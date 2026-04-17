"""
Precedent retrieval service.
Finds similar historical decisions from Neo4j based on profile similarity.
"""

import logging
from app.db import execute_query
from app.models.case import PrecedentCase

logger = logging.getLogger(__name__)


def find_precedents(
    segment: str,
    utilization: float,
    risk_score: float,
    trigger_event: str,
    limit: int = 5,
) -> list[PrecedentCase]:
    """
    Find similar historical decisions.

    Similarity is computed based on:
    - Same customer segment (weight: 0.3)
    - Utilization within ±15% (weight: 0.25)
    - Risk score within ±0.2 (weight: 0.25)
    - Same trigger event (weight: 0.2)
    """
    try:
        results = execute_query("""
            MATCH (d:Decision)-[:ABOUT]->(p:Person)
            OPTIONAL MATCH (d)-[:ABOUT]->(a:Account)
            MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
            WHERE d.status IN ['COMPLETED', 'PENDING', 'CLOSED']

            // Compute similarity components
            WITH d, p, a, dc,
                 CASE WHEN p.segment = $segment THEN 0.3 ELSE 0.0 END AS seg_score,
                 CASE WHEN dc.utilization_at_time IS NOT NULL AND abs(dc.utilization_at_time - $utilization) <= 15 THEN
                      0.25 * (1 - abs(dc.utilization_at_time - $utilization) / 15)
                 ELSE 0.0 END AS util_score,
                 CASE WHEN abs(dc.risk_at_time - $risk_score) <= 0.2 THEN
                      0.25 * (1 - abs(dc.risk_at_time - $risk_score) / 0.2)
                 ELSE 0.0 END AS risk_sim_score,
                 CASE WHEN dc.trigger_event = $trigger_event THEN 0.2 ELSE 0.0 END AS trigger_score

            WITH d, p, dc,
                 round((seg_score + util_score + risk_sim_score + trigger_score) * 100) / 100 AS similarity

            WHERE similarity > 0.2

            RETURN d.id AS decision_id,
                   d.action AS action,
                   d.confidence AS confidence,
                   d.outcome AS outcome,
                   similarity,
                   p.segment AS customer_segment,
                   dc.trigger_event AS trigger_event,
                   toString(d.created_at) AS created_at

            ORDER BY similarity DESC
            LIMIT $limit
        """, {
            "segment": segment,
            "utilization": utilization,
            "risk_score": risk_score,
            "trigger_event": trigger_event,
            "limit": limit,
        })

        precedents = []
        for r in results:
            precedents.append(PrecedentCase(
                decision_id=r["decision_id"],
                action=r["action"],
                confidence=r["confidence"],
                outcome=r.get("outcome"),
                similarity_score=r["similarity"],
                customer_segment=r["customer_segment"],
                trigger_event=r["trigger_event"],
                created_at=r.get("created_at"),
            ))

        logger.info(f"Found {len(precedents)} precedent cases")
        return precedents

    except Exception as e:
        logger.error(f"Precedent retrieval failed: {e}")
        return []


def get_decision_trace(decision_id: str) -> dict | None:
    """
    Get the full decision trace — the chain of evaluation steps,
    policies applied, and any precedent relationships.
    """
    try:
        results = execute_query("""
            MATCH (d:Decision {id: $id})
            OPTIONAL MATCH (d)-[:HAS_CONTEXT]->(dc:DecisionContext)
            OPTIONAL MATCH (d)-[:APPLIED_POLICY]->(pol:Policy)
            OPTIONAL MATCH (d)-[:GRANTED_EXCEPTION]->(exc:Exception)
            OPTIONAL MATCH (d)-[:TRIGGERED]->(esc:Escalation)
            OPTIONAL MATCH (d)-[:PRECEDENT_FOR]->(pd:Decision)
            OPTIONAL MATCH (id:Decision)-[:INFLUENCED]->(d)
            OPTIONAL MATCH (d)-[:ABOUT]->(p:Person)
            OPTIONAL MATCH (d)-[:ABOUT]->(a:Account)

            RETURN d, dc, p, a,
                   collect(DISTINCT pol) AS policies,
                   collect(DISTINCT exc) AS exceptions,
                   collect(DISTINCT esc) AS escalations,
                   collect(DISTINCT pd.id) AS precedent_for,
                   collect(DISTINCT id.id) AS influenced_by
        """, {"id": decision_id})

        if not results:
            return None

        r = results[0]
        decision = dict(r["d"])

        trace = {
            "decision_id": decision.get("id"),
            "action": decision.get("action"),
            "confidence": decision.get("confidence"),
            "status": decision.get("status"),
            "created_at": str(decision.get("created_at", "")),
            "context": dict(r["dc"]) if r.get("dc") else None,
            "customer": dict(r["p"]) if r.get("p") else None,
            "account": dict(r["a"]) if r.get("a") else None,
            "policies": [dict(p) for p in r.get("policies", []) if p],
            "exceptions": [dict(e) for e in r.get("exceptions", []) if e],
            "escalations": [dict(e) for e in r.get("escalations", []) if e],
            "precedent_for": r.get("precedent_for", []),
            "influenced_by": r.get("influenced_by", []),
        }

        return trace

    except Exception as e:
        logger.error(f"Decision trace retrieval failed: {e}")
        return None
