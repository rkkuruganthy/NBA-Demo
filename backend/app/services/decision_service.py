"""
Decision service — evaluates cases and persists decisions to Neo4j.
"""

import uuid
import logging
import json
from datetime import datetime
from app.db import execute_query, execute_write
from app.models.case import (
    CaseEvaluationRequest,
    RecommendationResponse,
    TriggerEvent,
)
from app.services.policy_engine import evaluate_case
from app.services.precedent_service import find_precedents
from app.services.llm_service import synthesize_decision_narrative

logger = logging.getLogger(__name__)


def get_customer(customer_id: str) -> dict | None:
    """Fetch customer from Neo4j."""
    results = execute_query(
        "MATCH (p {id: $id}) RETURN p",
        {"id": customer_id},
    )
    if results:
        return dict(results[0]["p"])
    return None


def get_account(account_id: str) -> dict | None:
    """Fetch account from Neo4j."""
    results = execute_query(
        "MATCH (a:Account {id: $id}) RETURN a",
        {"id": account_id},
    )
    if results:
        return dict(results[0]["a"])
    return None


def get_policies() -> list[dict]:
    """Fetch all active policies from Neo4j."""
    results = execute_query("MATCH (p:Policy) RETURN p")
    return [dict(r["p"]) for r in results]


def evaluate(request: CaseEvaluationRequest) -> RecommendationResponse:
    """
    Evaluate a case end-to-end:
    1. Fetch customer + account from graph
    2. Run deterministic policy engine
    3. Find precedent cases
    4. Persist decision to graph
    5. Return structured recommendation
    """
    # 1. Fetch data
    customer = get_customer(request.customer_id)
    if not customer:
        raise ValueError(f"Customer {request.customer_id} not found")
    # Ensure customer_id is always present for policy engine matching
    customer["customer_id"] = request.customer_id

    # Try to find account: use provided ID first, then auto-discover from graph
    account = {}
    if request.account_id:
        account = get_account(request.account_id) or {}
    if not account:
        # Auto-discover account from graph relationship
        acc_results = execute_query(
            "MATCH (p {id: $id})-[:OWNS]->(a:Account) RETURN a LIMIT 1",
            {"id": request.customer_id}
        )
        if acc_results:
            account = dict(acc_results[0]["a"])

    policies = get_policies()

    # 2. Run policy engine (deterministic — no LLM)
    eval_result = evaluate_case(
        customer=customer,
        account=account,
        trigger_event=request.trigger_event,
        policies=policies,
    )

    # 3. Find precedent cases
    precedents = find_precedents(
        segment=customer.get("segment", ""),
        utilization=account.get("utilization_pct", 0),
        risk_score=customer.get("risk_score", 0.5),
        trigger_event=request.trigger_event.value,
    )

    # 4. Generate decision ID and persist
    decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
    context_id = f"DCX-{uuid.uuid4().hex[:8].upper()}"

    _persist_decision(
        decision_id=decision_id,
        context_id=context_id,
        request=request,
        eval_result=eval_result,
        customer=customer,
        account=account,
    )

    # 5. Build response
    
    # 5b. Generate AI Narrative with full graph traversal context
    ai_narrative = synthesize_decision_narrative(
        customer=customer,
        account=account,
        rules=eval_result.applied_policies,
        result=eval_result.action.value,
        trigger=request.trigger_event.value,
        graph_features=eval_result.explanation_inputs.get("graph_features", {}),
        factors=eval_result.explanation_inputs.get("factors", []),
        counter_offer=eval_result.counter_offer,
        ranked_actions=eval_result.ranked_actions,
    )
    
    return RecommendationResponse(
        decision_id=decision_id,
        recommended_action=eval_result.action,
        confidence=round(eval_result.confidence, 2),
        requires_human_review=eval_result.requires_human_review,
        applied_policies=eval_result.applied_policies,
        precedent_cases=precedents,
        explanation_inputs=eval_result.explanation_inputs,
        customer_summary={
            "id": customer.get("id"),
            "name": customer.get("name"),
            "segment": customer.get("segment"),
            "risk_score": customer.get("risk_score"),
            "churn_risk": customer.get("churn_risk"),
            "customer_value": customer.get("customer_value"),
            "credit_score": customer.get("credit_score"),
        },
        account_summary={
            "id": account.get("id"),
            "type": account.get("type"),
            "credit_limit": account.get("credit_limit"),
            "utilization_pct": account.get("utilization_pct"),
            "payment_score": account.get("payment_score"),
            "days_past_due": account.get("days_past_due"),
        },
        ai_narrative=ai_narrative,
        counter_offer=eval_result.counter_offer,
        ranked_actions=eval_result.ranked_actions,
    )


def _persist_decision(
    decision_id: str,
    context_id: str,
    request: CaseEvaluationRequest,
    eval_result,
    customer: dict,
    account: dict,
):
    """Persist decision + context + relationships to Neo4j."""
    now = datetime.utcnow().isoformat()

    # Build a human-readable reasoning summary for the Decision node
    factors = eval_result.explanation_inputs.get("factors", [])
    graph_features = eval_result.explanation_inputs.get("graph_features", {})
    policy_names = [p.policy_name for p in eval_result.applied_policies]
    
    reasoning_summary = "\n".join(f"• {f}" for f in factors)
    policies_str = ", ".join(policy_names) if policy_names else "No specific policy matched"
    
    # Build graph feature summary
    feature_parts = []
    for k, v in graph_features.items():
        if k in ["utilization", "dpd", "credit_score", "wire_amount", "care_gap_days", 
                  "shared_with_threat", "has_travel_intent", "is_high_risk_jurisdiction",
                  "is_critical_diagnosis", "rx_status", "diag_name", "risk_score",
                  "view_count", "used_calculator", "test_drive_count", "max_trade_in_equity"]:
            feature_parts.append(f"{k}: {v}")
    features_str = " | ".join(feature_parts) if feature_parts else "N/A"

    # Create Decision + DecisionContext nodes
    execute_write("""
        CREATE (d:Decision {
            id: $decision_id,
            action: $action,
            confidence: $confidence,
            status: 'PENDING',
            created_at: datetime($created_at),
            requires_human_review: $requires_human_review,
            reasoning: $reasoning,
            policies_applied: $policies_applied,
            graph_features: $graph_features_str,
            decision_type: $trigger_event,
            ranked_actions: $ranked_actions_json
        })
        CREATE (dc:DecisionContext {
            id: $context_id,
            trigger_event: $trigger_event,
            utilization_at_time: $utilization,
            risk_at_time: $risk_score,
            notes: $notes
        })
        MERGE (d)-[:HAS_CONTEXT]->(dc)
    """, {
        "decision_id": decision_id,
        "action": eval_result.action.value,
        "confidence": eval_result.confidence,
        "created_at": now,
        "requires_human_review": eval_result.requires_human_review,
        "reasoning": reasoning_summary,
        "policies_applied": policies_str,
        "graph_features_str": features_str,
        "context_id": context_id,
        "trigger_event": request.trigger_event.value,
        "utilization": account.get("utilization_pct", 0),
        "risk_score": customer.get("risk_score", 0),
        "notes": request.notes or "",
        "ranked_actions_json": json.dumps([ra.model_dump() for ra in eval_result.ranked_actions]) if eval_result.ranked_actions else "[]"
    })

    # Link to Person/Patient
    execute_write("""
        MATCH (d:Decision {id: $decision_id})
        MATCH (p {id: $customer_id})
        MERGE (d)-[:ABOUT]->(p)
    """, {
        "decision_id": decision_id,
        "customer_id": request.customer_id,
    })

    # Link to Account (if applicable — Healthcare has no Account)
    if request.account_id:
        execute_write("""
            MATCH (d:Decision {id: $decision_id})
            MATCH (a:Account {id: $account_id})
            MERGE (d)-[:ABOUT]->(a)
        """, {
            "decision_id": decision_id,
            "account_id": request.account_id,
        })

    # Link to applied policies
    for policy in eval_result.applied_policies:
        execute_write("""
            MATCH (d:Decision {id: $decision_id})
            MATCH (pol:Policy {id: $policy_id})
            MERGE (d)-[:APPLIED_POLICY]->(pol)
        """, {
            "decision_id": decision_id,
            "policy_id": policy.policy_id,
        })

    logger.info(f"Decision {decision_id} persisted to graph")


def get_decision(decision_id: str) -> dict | None:
    """Fetch a decision with its context from Neo4j."""
    results = execute_query("""
        MATCH (d:Decision {id: $id})
        OPTIONAL MATCH (d)-[:ABOUT]->(p:Person)
        OPTIONAL MATCH (d)-[:ABOUT]->(a:Account)
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        OPTIONAL MATCH (d)-[:APPLIED_POLICY]->(pol:Policy)
        RETURN d, p, a, dc, collect(pol.name) as policies
    """, {"id": decision_id})

    if not results:
        return None

    r = results[0]
    decision = dict(r["d"])
    return {
        "decision_id": decision.get("id"),
        "action": decision.get("action"),
        "confidence": decision.get("confidence"),
        "status": decision.get("status"),
        "created_at": str(decision.get("created_at", "")),
        "customer": dict(r["p"]) if r.get("p") else None,
        "account": dict(r["a"]) if r.get("a") else None,
        "context": dict(r["dc"]) if r.get("dc") else None,
        "applied_policies": r.get("policies", []),
    }


def get_all_decisions(limit: int = 20) -> list[dict]:
    """Fetch recent decisions."""
    results = execute_query("""
        MATCH (d:Decision)
        OPTIONAL MATCH (d)-[:ABOUT]->(p:Person)
        OPTIONAL MATCH (d)-[:ABOUT]->(a:Account)
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        RETURN d, p.name as customer_name, p.id as customer_id,
               a.id as account_id, dc.trigger_event as trigger_event
        ORDER BY d.created_at DESC
        LIMIT $limit
    """, {"limit": limit})

    decisions = []
    for r in results:
        d = dict(r["d"])
        decisions.append({
            "decision_id": d.get("id"),
            "customer_name": r.get("customer_name"),
            "customer_id": r.get("customer_id"),
            "account_id": r.get("account_id"),
            "action": d.get("action"),
            "confidence": d.get("confidence"),
            "status": d.get("status"),
            "trigger_event": r.get("trigger_event"),
            "created_at": str(d.get("created_at", "")),
        })

    return decisions
