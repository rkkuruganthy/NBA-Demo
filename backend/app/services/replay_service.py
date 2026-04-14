"""
Decision Replay & What-If Analysis Service.
Re-runs decisions against current or altered graph state for comparison.
"""

import logging
from app.db import execute_query
from app.services.policy_engine import (
    extract_financial_features,
    extract_aml_features,
    extract_healthcare_features,
    extract_insurance_features,
    evaluate_case,
)
from app.models.case import TriggerEvent

logger = logging.getLogger(__name__)


def replay_decision(decision_id: str) -> dict:
    """
    Re-run a past decision against the CURRENT graph state.
    Returns comparison: original_result vs replayed_result with delta analysis.
    """
    # Fetch original decision
    results = execute_query("""
        MATCH (d:Decision {id: $id})-[:ABOUT]->(p)
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        OPTIONAL MATCH (p)-[:OWNS]->(a:Account)
        RETURN d.action AS original_action,
               d.confidence AS original_confidence,
               d.reasoning AS original_reasoning,
               d.graph_features AS original_features,
               d.policies_applied AS original_policies,
               d.created_at AS original_timestamp,
               p.id AS customer_id,
               p.name AS customer_name,
               p.segment AS segment,
               dc.trigger_event AS trigger_event,
               a.id AS account_id
    """, {"id": decision_id})

    if not results:
        return {"error": f"Decision {decision_id} not found"}

    r = results[0]
    customer_id = r["customer_id"]
    trigger_event = r["trigger_event"]

    # Determine current features based on trigger type
    if "CREDIT_LIMIT" in trigger_event:
        current_features = extract_financial_features(customer_id)
    elif "FRAUD" in trigger_event:
        current_features = extract_aml_features(customer_id)
    elif "CARE_GAP" in trigger_event:
        current_features = extract_healthcare_features(customer_id)
    elif "CLAIMS" in trigger_event:
        current_features = extract_insurance_features(customer_id)
    else:
        current_features = {}

    # Re-run the evaluation
    from app.services.decision_service import get_customer, get_account, get_policies
    customer = get_customer(customer_id)
    account = get_account(r["account_id"]) if r["account_id"] else {}
    policies = get_policies()

    try:
        trigger = TriggerEvent(trigger_event)
    except ValueError:
        return {"error": f"Unknown trigger event: {trigger_event}"}

    if not customer:
        return {"error": f"Customer {customer_id} no longer exists in graph"}

    customer["customer_id"] = customer_id
    eval_result = evaluate_case(customer, account or {}, trigger, policies)

    # Build comparison
    action_changed = eval_result.action.value != r["original_action"]
    confidence_delta = round((eval_result.confidence - (r["original_confidence"] or 0)), 3)

    return {
        "decision_id": decision_id,
        "customer_id": customer_id,
        "customer_name": r["customer_name"],
        "trigger_event": trigger_event,
        "original": {
            "action": r["original_action"],
            "confidence": r["original_confidence"],
            "reasoning": r["original_reasoning"],
            "features": r["original_features"],
            "policies": r["original_policies"],
            "timestamp": str(r["original_timestamp"]) if r["original_timestamp"] else None,
        },
        "replayed": {
            "action": eval_result.action.value,
            "confidence": round(eval_result.confidence, 3),
            "reasoning": "\n".join(f"• {f}" for f in eval_result.explanation_inputs.get("factors", [])),
            "features": eval_result.explanation_inputs.get("graph_features", {}),
            "policies": [p.policy_name for p in eval_result.applied_policies],
        },
        "delta": {
            "action_changed": action_changed,
            "confidence_delta": confidence_delta,
            "drift_detected": action_changed or abs(confidence_delta) > 0.1,
        },
    }


def what_if_analysis(decision_id: str, overrides: dict) -> dict:
    """
    Re-run a decision with user-altered parameters.
    E.g., "What if utilization was 50% instead of 92%?"

    overrides example: {"utilization_pct": 0.50, "dpd": 0, "credit_score": 720}
    """
    # Fetch original decision context
    results = execute_query("""
        MATCH (d:Decision {id: $id})-[:ABOUT]->(p)
        OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
        OPTIONAL MATCH (p)-[:OWNS]->(a:Account)
        RETURN d.action AS original_action,
               d.confidence AS original_confidence,
               p.id AS customer_id,
               p AS customer,
               a AS account,
               dc.trigger_event AS trigger_event
    """, {"id": decision_id})

    if not results:
        return {"error": f"Decision {decision_id} not found"}

    r = results[0]
    customer = dict(r["customer"]) if r["customer"] else {}
    account = dict(r["account"]) if r["account"] else {}

    # Apply overrides
    for key, value in overrides.items():
        if key in account:
            account[key] = value
        elif key in customer:
            customer[key] = value

    customer["customer_id"] = r["customer_id"]

    try:
        trigger = TriggerEvent(r["trigger_event"])
    except ValueError:
        return {"error": f"Unknown trigger event: {r['trigger_event']}"}

    from app.services.decision_service import get_policies
    policies = get_policies()
    eval_result = evaluate_case(customer, account, trigger, policies)

    return {
        "decision_id": decision_id,
        "scenario": "what_if",
        "overrides_applied": overrides,
        "original": {
            "action": r["original_action"],
            "confidence": r["original_confidence"],
        },
        "what_if_result": {
            "action": eval_result.action.value,
            "confidence": round(eval_result.confidence, 3),
            "factors": eval_result.explanation_inputs.get("factors", []),
            "policies": [p.policy_name for p in eval_result.applied_policies],
        },
        "delta": {
            "action_changed": eval_result.action.value != r["original_action"],
            "confidence_delta": round(eval_result.confidence - (r["original_confidence"] or 0), 3),
        },
    }
