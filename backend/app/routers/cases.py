"""
Cases API router — case evaluation, retrieval, negotiation, replay, and what-if.
"""

from fastapi import APIRouter, HTTPException
from app.models.case import (
    CaseEvaluationRequest, RecommendationResponse, CaseResponse,
    NegotiationRequest, NegotiationStepResponse, CounterOffer,
)
from app.services.decision_service import evaluate, get_decision, get_all_decisions
from app.db import execute_write, execute_query
import uuid
from datetime import datetime

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/evaluate", response_model=RecommendationResponse)
async def evaluate_case(request: CaseEvaluationRequest):
    """
    Evaluate a case and generate a Next Best Action recommendation.

    The recommendation is determined by deterministic policy rules — no LLM is used
    for action selection. The response includes:
    - recommended action (APPROVE, DECLINE, ESCALATE, RETENTION, DOCUMENTS)
    - confidence score
    - applied policies with explanations
    - similar historical precedents
    - counter-offer (if applicable)
    - ranked alternative actions
    """
    try:
        result = evaluate(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/{decision_id}/negotiate", response_model=NegotiationStepResponse)
async def negotiate_decision(decision_id: str, request: NegotiationRequest):
    """
    Handle a negotiation step: customer/analyst accepts, counters, or declines.
    Each step is persisted as a NegotiationStep node in the graph.
    """
    # Verify the decision exists
    decision = get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    # Count existing negotiation steps
    step_count_result = execute_query("""
        MATCH (d:Decision {id: $decision_id})-[:HAS_STEP]->(s:NegotiationStep)
        RETURN count(s) as step_count
    """, {"decision_id": decision_id})
    step_number = (step_count_result[0]["step_count"] if step_count_result else 0) + 1

    now = datetime.utcnow().isoformat()
    step_id = f"NEG-{uuid.uuid4().hex[:8].upper()}"

    response_upper = request.response.upper()

    if response_upper == "ACCEPT":
        # Customer accepted the offer/counter-offer
        engine_action = "FINALIZED_APPROVED"
        engine_confidence = 1.0
        message = "Decision accepted. The recommendation has been finalized and applied."
        is_final = True
        counter_offer = None

        # Update the decision status
        execute_write("""
            MATCH (d:Decision {id: $decision_id})
            SET d.status = 'COMPLETED', d.final_action = 'ACCEPTED'
        """, {"decision_id": decision_id})

    elif response_upper == "DECLINE":
        # Customer declined everything
        engine_action = "CLOSED_DECLINED"
        engine_confidence = 1.0
        message = f"Decision declined by customer. Reason: {request.reason or 'No reason provided'}. Case closed."
        is_final = True
        counter_offer = None

        execute_write("""
            MATCH (d:Decision {id: $decision_id})
            SET d.status = 'CLOSED', d.final_action = 'DECLINED'
        """, {"decision_id": decision_id})

    elif response_upper == "COUNTER":
        # Customer made a counter-proposal — engine re-evaluates
        counter_value = request.counter_value or "unspecified"

        # Deterministic re-evaluation based on the counter
        eval_result = _evaluate_counter(decision, counter_value, step_number)
        engine_action = eval_result["action"]
        engine_confidence = eval_result["confidence"]
        message = eval_result["message"]
        is_final = eval_result["is_final"]
        counter_offer = eval_result.get("counter_offer")

        if is_final:
            execute_write("""
                MATCH (d:Decision {id: $decision_id})
                SET d.status = 'COMPLETED', d.final_action = $action
            """, {"decision_id": decision_id, "action": engine_action})

    else:
        raise HTTPException(status_code=400, detail="Response must be ACCEPT, COUNTER, or DECLINE")

    # Persist the negotiation step as a graph node
    execute_write("""
        MATCH (d:Decision {id: $decision_id})
        CREATE (s:NegotiationStep {
            id: $step_id,
            step_number: $step_number,
            customer_response: $customer_response,
            counter_value: $counter_value,
            engine_action: $engine_action,
            engine_confidence: $engine_confidence,
            message: $message,
            is_final: $is_final,
            created_at: datetime($now)
        })
        MERGE (d)-[:HAS_STEP]->(s)
    """, {
        "decision_id": decision_id,
        "step_id": step_id,
        "step_number": step_number,
        "customer_response": response_upper,
        "counter_value": request.counter_value or "",
        "engine_action": engine_action,
        "engine_confidence": engine_confidence,
        "message": message,
        "is_final": is_final,
        "now": now,
    })

    return NegotiationStepResponse(
        step_number=step_number,
        customer_response=response_upper,
        engine_action=engine_action,
        engine_confidence=engine_confidence,
        message=message,
        counter_offer=counter_offer,
        is_final=is_final,
    )


def _evaluate_counter(decision: dict, counter_value: str, step_number: int) -> dict:
    """
    Deterministic re-evaluation of a customer counter-proposal.
    Uses step_number to limit negotiation rounds (max 3).
    """
    trigger = decision.get("context", {}).get("trigger_event", "")

    if step_number >= 3:
        # Final round — no more negotiation allowed
        return {
            "action": "FINAL_OFFER",
            "confidence": 0.90,
            "message": f"Maximum negotiation rounds reached. Our final offer stands. Counter-proposal of '{counter_value}' noted but cannot be processed further. Please accept or decline.",
            "is_final": False,
            "counter_offer": None,
        }

    if "CREDIT_LIMIT" in trigger:
        # Financial CLI counter-offer logic
        try:
            amount = float(counter_value.replace("$", "").replace(",", ""))
        except (ValueError, AttributeError):
            amount = 0

        if amount <= 1500:
            return {
                "action": "COUNTER_APPROVED",
                "confidence": 0.85,
                "message": f"Counter-proposal of ${amount:,.0f} is within acceptable risk parameters. Approved with standard conditions.",
                "is_final": True,
            }
        elif amount <= 3000:
            return {
                "action": "COUNTER_CONDITIONAL",
                "confidence": 0.68,
                "message": f"Counter-proposal of ${amount:,.0f} requires additional conditions. We can approve ${amount:,.0f} if you clear your past-due balance within 30 days.",
                "is_final": False,
                "counter_offer": CounterOffer(
                    suggested_value=f"${amount:,.0f} with conditions",
                    original_request=f"${amount:,.0f} counter-proposal",
                    rationale=f"The ${amount:,.0f} amount is within conditional approval range but requires DPD clearance first.",
                    conditions=[
                        "Clear past-due balance within 30 days",
                        "Maintain 0 DPD for 45 consecutive days",
                        f"Increase activates automatically after conditions met"
                    ]
                ),
            }
        else:
            return {
                "action": "COUNTER_DECLINED",
                "confidence": 0.95,
                "message": f"Counter-proposal of ${amount:,.0f} exceeds maximum allowable increase for your risk profile. Our best offer remains $1,000 conditional.",
                "is_final": False,
                "counter_offer": CounterOffer(
                    suggested_value="$1,000 Conditional (final offer)",
                    original_request=f"${amount:,.0f} counter-proposal",
                    rationale="Amount exceeds policy limits for current risk profile. Maximum conditional offer is $1,000.",
                    conditions=[
                        "Clear past-due balance within 30 days",
                        "Maintain 0 DPD for 60 consecutive days",
                    ]
                ),
            }

    elif "FRAUD" in trigger:
        return {
            "action": "COUNTER_PARTIAL_RELEASE",
            "confidence": 0.65,
            "message": f"Counter-proposal noted: '{counter_value}'. We can release a partial hold of $2,500 (of $9,500) pending enhanced verification completion.",
            "is_final": False,
            "counter_offer": CounterOffer(
                suggested_value="$2,500 partial release",
                original_request=counter_value,
                rationale="Full release requires completed EDD. Partial release is available for amounts under $3,000.",
                conditions=[
                    "Enhanced identity verification must be completed",
                    "Source-of-funds documentation required within 48 hours",
                    "Remaining $7,000 held pending investigation conclusion"
                ]
            ),
        }

    elif "CARE_GAP" in trigger:
        return {
            "action": "COUNTER_CARE_PLAN",
            "confidence": 0.78,
            "message": f"Alternative care plan noted: '{counter_value}'. We recommend scheduling both a telehealth check-in AND pharmacy outreach as a combined approach.",
            "is_final": False,
            "counter_offer": CounterOffer(
                suggested_value="Combined: Telehealth + Pharmacy Outreach",
                original_request=counter_value,
                rationale="Combining telehealth assessment with pharmacy outreach addresses both adherence barriers and medication access issues simultaneously.",
                conditions=[
                    "Telehealth scheduled within 24 hours",
                    "Pharmacy outreach initiated immediately",
                    "If no response in 48 hours, auto-escalate to in-person home visit"
                ]
            ),
        }

    # Generic fallback
    return {
        "action": "COUNTER_NOTED",
        "confidence": 0.50,
        "message": f"Counter-proposal '{counter_value}' has been noted and sent for manual review.",
        "is_final": False,
    }


@router.get("/{decision_id}")
async def get_case(decision_id: str):
    """Fetch a stored case and its decision details."""
    result = get_decision(decision_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return result


@router.get("/")
async def list_cases(limit: int = 20):
    """List recent cases."""
    return get_all_decisions(limit=limit)


@router.post("/{decision_id}/replay")
async def replay_case(decision_id: str):
    """
    Replay a past decision against the CURRENT graph state.
    Returns comparison: original vs replayed result with delta analysis.
    """
    from app.services.replay_service import replay_decision
    result = replay_decision(decision_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/{decision_id}/what-if")
async def what_if_case(decision_id: str, overrides: dict):
    """
    Re-run a decision with altered parameters.
    E.g., "What if utilization was 50% instead of 92%?"
    """
    from app.services.replay_service import what_if_analysis
    result = what_if_analysis(decision_id, overrides)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
