"""
Graph Analytics Overlay Service.
Population-level analytics: community detection, risk propagation, segment intelligence.
Uses Cypher-based analytics for article-ready insights.
"""

import logging
from app.db import execute_query

logger = logging.getLogger(__name__)


def get_population_analytics() -> dict:
    """Run population-level analytics across the entire graph."""

    # Decision distribution by action
    action_dist = execute_query("""
        MATCH (d:Decision)
        RETURN d.action AS action, count(d) AS count
        ORDER BY count DESC
    """)

    # Decision distribution by trigger event
    trigger_dist = execute_query("""
        MATCH (d:Decision)-[:HAS_CONTEXT]->(dc:DecisionContext)
        RETURN dc.trigger_event AS trigger_event, count(d) AS count
        ORDER BY count DESC
    """)

    # Average confidence by segment
    segment_conf = execute_query("""
        MATCH (d:Decision)-[:ABOUT]->(p)
        WHERE p.segment IS NOT NULL OR p.risk_tier IS NOT NULL
        RETURN coalesce(p.segment, p.risk_tier) AS segment,
               avg(d.confidence) AS avg_confidence,
               count(d) AS decision_count
        ORDER BY decision_count DESC
    """)

    # Node and relationship counts
    node_counts = execute_query("""
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """)

    rel_counts = execute_query("""
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY count DESC
    """)

    return {
        "decision_distribution": {r["action"]: r["count"] for r in action_dist},
        "trigger_distribution": {r["trigger_event"]: r["count"] for r in trigger_dist},
        "segment_confidence": [
            {
                "segment": r["segment"],
                "avg_confidence": round(r["avg_confidence"], 3) if r["avg_confidence"] else None,
                "decision_count": r["decision_count"],
            }
            for r in segment_conf
        ],
        "graph_topology": {
            "nodes": {r["label"]: r["count"] for r in node_counts},
            "relationships": {r["type"]: r["count"] for r in rel_counts},
        },
    }


def get_risk_propagation() -> dict:
    """
    Detect fraud risk propagation through shared devices.
    Identifies clusters of accounts connected to threat actors via 2-hop paths.
    """
    results = execute_query("""
        MATCH (threat:Fraudster)-[:LOGGED_IN_FROM]->(d:Device)<-[:LOGGED_IN_FROM]-(p:Person)
        WITH threat, d, collect(DISTINCT p.id) AS affected_persons,
             count(DISTINCT p) AS affected_count
        RETURN threat.name AS threat_actor,
               threat.id AS threat_id,
               d.ip AS shared_device_ip,
               d.type AS device_type,
               affected_count,
               affected_persons[0..5] AS sample_affected
        ORDER BY affected_count DESC
        LIMIT 20
    """)

    return {
        "risk_propagation_clusters": [
            {
                "threat_actor": r["threat_actor"],
                "threat_id": r["threat_id"],
                "shared_device": r["shared_device_ip"],
                "device_type": r["device_type"],
                "affected_persons": r["affected_count"],
                "sample_ids": r["sample_affected"],
            }
            for r in results
        ],
        "total_clusters": len(results),
    }


def get_segment_intelligence() -> dict:
    """
    Aggregate decision patterns by segment with outcome tracking.
    Provides segment-level intelligence for article visualizations.
    """
    results = execute_query("""
        MATCH (d:Decision)-[:ABOUT]->(p)
        WHERE p.segment IS NOT NULL OR p.risk_tier IS NOT NULL
        OPTIONAL MATCH (d)-[:RESULTED_IN]->(o:Outcome)
        WITH coalesce(p.segment, p.risk_tier) AS segment,
             d.action AS action,
             count(d) AS decisions,
             avg(d.confidence) AS avg_conf,
             sum(CASE WHEN o.actual_result = 'POSITIVE' THEN 1 ELSE 0 END) AS positive,
             sum(CASE WHEN o.actual_result = 'NEGATIVE' THEN 1 ELSE 0 END) AS negative
        RETURN segment, action, decisions, avg_conf, positive, negative
        ORDER BY segment, decisions DESC
    """)

    # Group by segment
    segments = {}
    for r in results:
        seg = r["segment"]
        if seg not in segments:
            segments[seg] = {"actions": [], "total_decisions": 0}
        segments[seg]["total_decisions"] += r["decisions"]
        segments[seg]["actions"].append({
            "action": r["action"],
            "count": r["decisions"],
            "avg_confidence": round(r["avg_conf"], 3) if r["avg_conf"] else None,
            "positive_outcomes": r["positive"],
            "negative_outcomes": r["negative"],
        })

    return {"segments": segments}


def get_community_detection() -> dict:
    """
    Identify customer clusters based on shared behavioral patterns.
    Groups customers who have similar decision outcomes and risk profiles.
    """
    results = execute_query("""
        MATCH (p:Person)-[:OWNS]->(a:Account)
        WITH p.segment AS segment,
             CASE
                 WHEN a.utilization_pct > 0.8 THEN 'high_utilization'
                 WHEN a.utilization_pct > 0.5 THEN 'medium_utilization'
                 ELSE 'low_utilization'
             END AS util_band,
             CASE
                 WHEN a.dpd > 30 THEN 'severe_delinquent'
                 WHEN a.dpd > 0 THEN 'minor_delinquent'
                 ELSE 'current'
             END AS payment_status,
             count(p) AS population
        RETURN segment, util_band, payment_status, population
        ORDER BY population DESC
    """)

    return {
        "behavioral_communities": [
            {
                "segment": r["segment"],
                "utilization_band": r["util_band"],
                "payment_status": r["payment_status"],
                "population": r["population"],
            }
            for r in results
        ],
    }
