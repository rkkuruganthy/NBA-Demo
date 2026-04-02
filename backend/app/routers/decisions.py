"""
Decisions API router — traces, precedents, and analyst actions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.precedent_service import get_decision_trace, find_precedents
from app.services.decision_service import get_decision
from app.db import execute_write, execute_query
import uuid
from datetime import datetime

router = APIRouter(prefix="/decisions", tags=["Decisions"])


# --- Action Models ---

class ApprovalRequest(BaseModel):
    analyst_id: str = Field(..., examples=["analyst_01"])
    notes: Optional[str] = None


class OverrideRequest(BaseModel):
    analyst_id: str = Field(..., examples=["analyst_01"])
    new_action: str = Field(..., examples=["APPROVE"])
    rationale: str = Field(..., min_length=10, description="Required rationale for override")


class EscalationRequest(BaseModel):
    analyst_id: str = Field(..., examples=["analyst_01"])
    reason: str = Field(..., min_length=10)
    target_reviewer: str = Field(..., examples=["risk_manager_01"])
    urgency: str = Field("MEDIUM", examples=["LOW", "MEDIUM", "HIGH"])


class OutcomeRequest(BaseModel):
    actual_result: str = Field(..., examples=["POSITIVE", "NEGATIVE", "NEUTRAL"])
    revenue_impact: Optional[float] = None
    customer_retained: Optional[bool] = None
    notes: Optional[str] = None


# --- Endpoints ---

@router.get("/{decision_id}/trace")
async def decision_trace(decision_id: str):
    """Return the full decision trace including policies, context, and relationships."""
    trace = get_decision_trace(decision_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return trace


@router.get("/{decision_id}/precedents")
async def decision_precedents(decision_id: str):
    """Find similar prior decisions for a given decision."""
    decision = get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    customer = decision.get("customer", {})
    context = decision.get("context", {})

    precedents = find_precedents(
        segment=customer.get("segment", ""),
        utilization=context.get("utilization_at_time", 0),
        risk_score=context.get("risk_at_time", 0.5),
        trigger_event=context.get("trigger_event", ""),
    )

    return {"decision_id": decision_id, "precedents": precedents}


@router.post("/{decision_id}/approve")
async def approve_decision(decision_id: str, request: ApprovalRequest):
    """Approve a recommendation."""
    execute_write("""
        MATCH (d:Decision {id: $id})
        SET d.status = 'COMPLETED',
            d.analyst_id = $analyst_id,
            d.approved_at = datetime($now),
            d.approval_notes = $notes
    """, {
        "id": decision_id,
        "analyst_id": request.analyst_id,
        "now": datetime.utcnow().isoformat(),
        "notes": request.notes or "",
    })
    return {"status": "approved", "decision_id": decision_id}


@router.post("/{decision_id}/override")
async def override_decision(decision_id: str, request: OverrideRequest):
    """Override a recommendation with rationale."""
    exc_id = f"EXC-{uuid.uuid4().hex[:8].upper()}"

    execute_write("""
        MATCH (d:Decision {id: $id})
        SET d.status = 'OVERRIDDEN',
            d.analyst_id = $analyst_id,
            d.original_action = d.action,
            d.action = $new_action,
            d.overridden_at = datetime($now)
        CREATE (exc:Exception {
            id: $exc_id,
            type: 'ANALYST_OVERRIDE',
            rationale: $rationale,
            approved_by: $analyst_id
        })
        MERGE (d)-[:GRANTED_EXCEPTION]->(exc)
    """, {
        "id": decision_id,
        "analyst_id": request.analyst_id,
        "new_action": request.new_action,
        "now": datetime.utcnow().isoformat(),
        "exc_id": exc_id,
        "rationale": request.rationale,
    })
    return {"status": "overridden", "decision_id": decision_id, "new_action": request.new_action}


@router.post("/{decision_id}/escalate")
async def escalate_decision(decision_id: str, request: EscalationRequest):
    """Escalate a decision for review."""
    esc_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"

    execute_write("""
        MATCH (d:Decision {id: $id})
        SET d.status = 'ESCALATED',
            d.analyst_id = $analyst_id,
            d.escalated_at = datetime($now)
        CREATE (esc:Escalation {
            id: $esc_id,
            reason: $reason,
            target_reviewer: $target_reviewer,
            urgency: $urgency,
            status: 'PENDING',
            created_at: datetime($now)
        })
        MERGE (d)-[:TRIGGERED]->(esc)
    """, {
        "id": decision_id,
        "analyst_id": request.analyst_id,
        "now": datetime.utcnow().isoformat(),
        "esc_id": esc_id,
        "reason": request.reason,
        "target_reviewer": request.target_reviewer,
        "urgency": request.urgency,
    })
    return {"status": "escalated", "decision_id": decision_id, "escalation_id": esc_id}


@router.post("/{decision_id}/outcome")
async def record_outcome(decision_id: str, request: OutcomeRequest):
    """Record the actual business outcome for a decision."""
    execute_write("""
        MATCH (d:Decision {id: $id})
        SET d.outcome = $result,
            d.revenue_impact = $revenue,
            d.customer_retained = $retained,
            d.outcome_notes = $notes,
            d.outcome_recorded_at = datetime($now)
    """, {
        "id": decision_id,
        "result": request.actual_result,
        "revenue": request.revenue_impact,
        "retained": request.customer_retained,
        "notes": request.notes or "",
        "now": datetime.utcnow().isoformat(),
    })
    return {"status": "outcome_recorded", "decision_id": decision_id}


@router.get("/")
async def list_decisions(limit: int = 20):
    """List all decisions."""
    results = execute_query("""
        MATCH (d:Decision)
        OPTIONAL MATCH (d)-[:ABOUT]->(p:Person)
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        RETURN d, p.name as customer_name, p.id as customer_id,
               dc.trigger_event as trigger_event
        ORDER BY d.created_at DESC
        LIMIT $limit
    """, {"limit": limit})

    return [
        {
            "decision_id": dict(r["d"]).get("id"),
            "customer_name": r.get("customer_name"),
            "customer_id": r.get("customer_id"),
            "action": dict(r["d"]).get("action"),
            "confidence": dict(r["d"]).get("confidence"),
            "status": dict(r["d"]).get("status"),
            "trigger_event": r.get("trigger_event"),
            "created_at": str(dict(r["d"]).get("created_at", "")),
        }
        for r in results
    ]
