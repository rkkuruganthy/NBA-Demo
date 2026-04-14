"""
Temporal Intelligence Service.
Detects behavioral drift, confidence decay, and decision patterns over time.
Uses Cypher traversals to analyze how graph state evolves across evaluations.
"""

import logging
from datetime import datetime, timedelta
from app.db import execute_query

logger = logging.getLogger(__name__)


def detect_behavioral_drift(customer_id: str) -> dict:
    """
    Detect behavioral drift by comparing a customer's decision history.
    Identifies trends: rising utilization, widening care gaps, escalating wire amounts.
    """
    # Get decision history for this customer
    results = execute_query("""
        MATCH (d:Decision)-[:ABOUT]->(p {id: $id})
        MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        RETURN d.id AS decision_id,
               d.action AS action,
               d.confidence AS confidence,
               d.created_at AS created_at,
               dc.trigger_event AS trigger_event,
               dc.utilization_at_time AS utilization,
               dc.risk_at_time AS risk_score
        ORDER BY d.created_at ASC
    """, {"id": customer_id})

    if len(results) < 2:
        return {
            "customer_id": customer_id,
            "has_drift": False,
            "message": "Insufficient decision history for drift detection (need 2+ evaluations)",
            "decisions_analyzed": len(results),
        }

    # Analyze trends
    utilizations = [r["utilization"] for r in results if r["utilization"] is not None]
    risk_scores = [r["risk_score"] for r in results if r["risk_score"] is not None]
    confidences = [r["confidence"] for r in results if r["confidence"] is not None]

    drift_signals = []

    # Rising utilization trend
    if len(utilizations) >= 2:
        util_trend = utilizations[-1] - utilizations[0]
        if util_trend > 0.15:
            drift_signals.append({
                "signal": "RISING_UTILIZATION",
                "severity": "HIGH" if util_trend > 0.30 else "MEDIUM",
                "details": f"Utilization rose from {utilizations[0]*100:.0f}% to {utilizations[-1]*100:.0f}% across {len(utilizations)} evaluations",
                "delta": round(util_trend, 3),
            })

    # Escalating risk
    if len(risk_scores) >= 2:
        risk_trend = risk_scores[-1] - risk_scores[0]
        if risk_trend > 0.1:
            drift_signals.append({
                "signal": "ESCALATING_RISK",
                "severity": "HIGH" if risk_trend > 0.25 else "MEDIUM",
                "details": f"Risk score climbed from {risk_scores[0]:.2f} to {risk_scores[-1]:.2f}",
                "delta": round(risk_trend, 3),
            })

    # Decision pattern shift (e.g., went from APPROVE to DECLINE)
    actions = [r["action"] for r in results]
    if len(set(actions)) > 1:
        last_action = actions[-1]
        prev_action = actions[-2]
        if prev_action == "APPROVE" and last_action in ["DECLINE", "ESCALATE_FOR_REVIEW"]:
            drift_signals.append({
                "signal": "DETERIORATING_DECISIONS",
                "severity": "HIGH",
                "details": f"Decision shifted from {prev_action} → {last_action}",
            })

    # Confidence decay
    if len(confidences) >= 2 and confidences[-1] < confidences[0] - 0.15:
        drift_signals.append({
            "signal": "CONFIDENCE_DECAY",
            "severity": "MEDIUM",
            "details": f"Confidence dropped from {confidences[0]:.2f} to {confidences[-1]:.2f}",
            "delta": round(confidences[-1] - confidences[0], 3),
        })

    return {
        "customer_id": customer_id,
        "has_drift": len(drift_signals) > 0,
        "drift_signals": drift_signals,
        "decisions_analyzed": len(results),
        "timeline": [
            {
                "decision_id": r["decision_id"],
                "action": r["action"],
                "confidence": r["confidence"],
                "utilization": r["utilization"],
                "risk_score": r["risk_score"],
                "trigger_event": r["trigger_event"],
                "created_at": str(r["created_at"]) if r["created_at"] else None,
            }
            for r in results
        ],
    }


def get_decision_timeline(customer_id: str) -> dict:
    """
    Get the full decision timeline for a customer, including
    all linked context, policies, and outcomes.
    """
    results = execute_query("""
        MATCH (d:Decision)-[:ABOUT]->(p {id: $id})
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        OPTIONAL MATCH (d)-[:APPLIED_POLICY]->(pol:Policy)
        OPTIONAL MATCH (d)-[:RESULTED_IN]->(o:Outcome)
        OPTIONAL MATCH (d)-[:HAS_STEP]->(ns:NegotiationStep)
        RETURN d.id AS decision_id,
               d.action AS action,
               d.confidence AS confidence,
               d.status AS status,
               d.reasoning AS reasoning,
               d.created_at AS created_at,
               dc.trigger_event AS trigger_event,
               dc.utilization_at_time AS utilization,
               dc.risk_at_time AS risk,
               collect(DISTINCT pol.name) AS policies,
               o.actual_result AS outcome,
               count(DISTINCT ns) AS negotiation_steps
        ORDER BY d.created_at DESC
    """, {"id": customer_id})

    return {
        "customer_id": customer_id,
        "total_decisions": len(results),
        "timeline": [
            {
                "decision_id": r["decision_id"],
                "action": r["action"],
                "confidence": r["confidence"],
                "status": r["status"],
                "reasoning": r["reasoning"],
                "trigger_event": r["trigger_event"],
                "utilization": r["utilization"],
                "risk_score": r["risk"],
                "policies_applied": r["policies"],
                "outcome": r["outcome"],
                "negotiation_steps": r["negotiation_steps"],
                "created_at": str(r["created_at"]) if r["created_at"] else None,
            }
            for r in results
        ],
    }


def calculate_decision_decay(decision_id: str, half_life_days: int = 30) -> dict:
    """
    Calculate confidence decay for an open decision based on time elapsed.
    Older decisions with PENDING status should have decaying confidence.

    Uses exponential decay: decayed_confidence = original * 0.5^(days/half_life)
    """
    results = execute_query("""
        MATCH (d:Decision {id: $id})
        RETURN d.confidence AS confidence,
               d.status AS status,
               d.created_at AS created_at,
               d.action AS action
    """, {"id": decision_id})

    if not results:
        return {"error": f"Decision {decision_id} not found"}

    r = results[0]
    if r["status"] in ["COMPLETED", "CLOSED"]:
        return {
            "decision_id": decision_id,
            "status": r["status"],
            "original_confidence": r["confidence"],
            "decayed_confidence": r["confidence"],
            "decay_applied": False,
            "message": "Decision is finalized — no decay applied.",
        }

    # Calculate decay
    created = r["created_at"]
    if created:
        try:
            if hasattr(created, 'to_native'):
                created_dt = created.to_native()
            else:
                created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            days_elapsed = (datetime.utcnow() - created_dt.replace(tzinfo=None)).days
        except Exception:
            days_elapsed = 0
    else:
        days_elapsed = 0

    original = r["confidence"] or 0.5
    decay_factor = 0.5 ** (days_elapsed / half_life_days)
    decayed = round(original * decay_factor, 3)

    return {
        "decision_id": decision_id,
        "status": r["status"],
        "action": r["action"],
        "original_confidence": original,
        "decayed_confidence": decayed,
        "days_elapsed": days_elapsed,
        "half_life_days": half_life_days,
        "decay_factor": round(decay_factor, 3),
        "decay_applied": True,
        "recommendation": "Re-evaluate" if decayed < 0.5 else "Still valid",
    }
