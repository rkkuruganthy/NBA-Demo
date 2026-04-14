"""
Outcome & Feedback Loop Service.
Tracks actual business outcomes and calibrates decision confidence.
Creates (:Outcome) nodes linked to (:Decision) for closed-loop intelligence.
"""

import uuid
import logging
from datetime import datetime
from app.db import execute_query, execute_write

logger = logging.getLogger(__name__)


def record_outcome(
    decision_id: str,
    actual_result: str,
    revenue_impact: float = None,
    customer_retained: bool = None,
    days_to_outcome: int = None,
    outcome_category: str = None,
    notes: str = None,
) -> dict:
    """
    Record the actual business outcome for a decision.
    Creates an (:Outcome) node and links it to the (:Decision) via [:RESULTED_IN].

    This closes the feedback loop, enabling:
    - Calibration of confidence scores (predicted vs actual)
    - Policy effectiveness measurement
    - Population-level outcome analytics
    """
    outcome_id = f"OUT-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    # Create Outcome node and link to Decision
    execute_write("""
        MATCH (d:Decision {id: $decision_id})
        CREATE (o:Outcome {
            id: $outcome_id,
            actual_result: $actual_result,
            revenue_impact: $revenue_impact,
            customer_retained: $customer_retained,
            days_to_outcome: $days_to_outcome,
            outcome_category: $outcome_category,
            notes: $notes,
            recorded_at: datetime($now)
        })
        MERGE (d)-[:RESULTED_IN]->(o)
        SET d.status = 'COMPLETED',
            d.outcome = $actual_result
    """, {
        "decision_id": decision_id,
        "outcome_id": outcome_id,
        "actual_result": actual_result,
        "revenue_impact": revenue_impact or 0.0,
        "customer_retained": customer_retained,
        "days_to_outcome": days_to_outcome or 0,
        "outcome_category": outcome_category or "UNCLASSIFIED",
        "notes": notes or "",
        "now": now,
    })

    logger.info(f"Outcome {outcome_id} recorded for Decision {decision_id}")

    return {
        "outcome_id": outcome_id,
        "decision_id": decision_id,
        "actual_result": actual_result,
        "status": "recorded",
    }


def get_calibration_metrics(trigger_event: str = None) -> dict:
    """
    Calculate calibration metrics: predicted confidence vs actual outcomes.

    Returns:
    - accuracy: % of decisions where action aligned with positive outcome
    - overconfidence_rate: % where confidence > 0.8 but outcome was negative
    - underconfidence_rate: % where confidence < 0.6 but outcome was positive
    - by_action: breakdown per action type
    """
    filter_clause = ""
    params = {}
    if trigger_event:
        filter_clause = "AND dc.trigger_event = $trigger_event"
        params["trigger_event"] = trigger_event

    results = execute_query(f"""
        MATCH (d:Decision)-[:RESULTED_IN]->(o:Outcome)
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        WHERE o.actual_result IS NOT NULL {filter_clause}
        RETURN d.action AS action,
               d.confidence AS predicted_confidence,
               o.actual_result AS actual_result,
               o.revenue_impact AS revenue_impact,
               dc.trigger_event AS trigger_event
    """, params)

    if not results:
        return {
            "total_decisions_with_outcomes": 0,
            "message": "No outcomes recorded yet. Record outcomes to enable calibration.",
        }

    total = len(results)
    positive_outcomes = {"POSITIVE", "APPROVE", "RESOLVED"}
    negative_outcomes = {"NEGATIVE", "DEFAULT", "FRAUD_CONFIRMED", "READMISSION"}

    correct = 0
    overconfident = 0
    underconfident = 0
    by_action = {}

    for r in results:
        action = r["action"]
        confidence = r["predicted_confidence"] or 0.5
        outcome = r["actual_result"]

        is_positive = outcome in positive_outcomes
        is_negative = outcome in negative_outcomes

        # Track per action
        if action not in by_action:
            by_action[action] = {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        by_action[action]["total"] += 1

        if is_positive:
            by_action[action]["positive"] += 1
            correct += 1
            if confidence < 0.6:
                underconfident += 1
        elif is_negative:
            by_action[action]["negative"] += 1
            if confidence > 0.8:
                overconfident += 1
        else:
            by_action[action]["neutral"] += 1

    return {
        "total_decisions_with_outcomes": total,
        "accuracy": round(correct / total, 3) if total > 0 else 0,
        "overconfidence_rate": round(overconfident / total, 3) if total > 0 else 0,
        "underconfidence_rate": round(underconfident / total, 3) if total > 0 else 0,
        "by_action": by_action,
    }


def get_policy_effectiveness() -> list[dict]:
    """
    Measure which policies led to positive vs negative outcomes.
    Enables data-driven policy refinement.
    """
    results = execute_query("""
        MATCH (d:Decision)-[:APPLIED_POLICY]->(pol:Policy)
        OPTIONAL MATCH (d)-[:RESULTED_IN]->(o:Outcome)
        WITH pol.id AS policy_id,
             pol.name AS policy_name,
             count(d) AS total_applications,
             sum(CASE WHEN o.actual_result IN ['POSITIVE', 'RESOLVED'] THEN 1 ELSE 0 END) AS positive,
             sum(CASE WHEN o.actual_result IN ['NEGATIVE', 'DEFAULT', 'FRAUD_CONFIRMED'] THEN 1 ELSE 0 END) AS negative,
             sum(CASE WHEN o IS NULL THEN 1 ELSE 0 END) AS pending_outcome,
             avg(d.confidence) AS avg_confidence
        RETURN policy_id, policy_name, total_applications,
               positive, negative, pending_outcome, avg_confidence
        ORDER BY total_applications DESC
    """)

    return [
        {
            "policy_id": r["policy_id"],
            "policy_name": r["policy_name"],
            "total_applications": r["total_applications"],
            "positive_outcomes": r["positive"],
            "negative_outcomes": r["negative"],
            "pending_outcomes": r["pending_outcome"],
            "effectiveness_rate": round(
                r["positive"] / (r["positive"] + r["negative"]), 3
            ) if (r["positive"] + r["negative"]) > 0 else None,
            "avg_confidence": round(r["avg_confidence"], 3) if r["avg_confidence"] else None,
        }
        for r in results
    ]
