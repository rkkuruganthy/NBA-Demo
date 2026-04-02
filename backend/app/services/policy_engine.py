"""
Graph-Traversal Policy Engine.
Evaluates decisions by querying actual Neo4j relationships, NOT hardcoded customer IDs.
Rules-based — LLM MUST NOT influence action selection.
"""

import logging
from typing import Optional
from app.models.case import (
    RecommendedAction,
    AppliedPolicy,
    TriggerEvent,
    CounterOffer,
    RankedAction,
)
from app.db import execute_query

logger = logging.getLogger(__name__)


class PolicyEvaluationResult:
    """Result of running all policies against a case."""

    def __init__(self):
        self.action: RecommendedAction = RecommendedAction.ESCALATE_FOR_REVIEW
        self.confidence: float = 0.5
        self.requires_human_review: bool = True
        self.applied_policies: list[AppliedPolicy] = []
        self.explanation_inputs: dict = {}
        self.counter_offer: Optional[CounterOffer] = None
        self.ranked_actions: list[RankedAction] = []


# ──────────────────────────────────────────────────
# GRAPH FEATURE EXTRACTORS (Cypher-based)
# ──────────────────────────────────────────────────

def extract_financial_features(customer_id: str) -> dict:
    """Extract features from the Financial graph topology via Cypher."""
    result = execute_query("""
        MATCH (p:Person {id: $id})-[:OWNS]->(a:Account)
        OPTIONAL MATCH (p)-[:HAS_CONTEXT]->(ctx:Context)
        OPTIONAL MATCH (a)-[:MADE_PURCHASE]->(t:Transaction)
        OPTIONAL MATCH (t)-[:INDICATES]->(e:Entity)
        RETURN a.utilization_pct AS utilization,
               a.dpd AS dpd,
               a.current_limit AS current_limit,
               p.credit_score AS credit_score,
               p.segment AS segment,
               ctx.risk_score AS risk_score,
               ctx.months_active AS months_active,
               ctx.recent_inquiries AS inquiries,
               count(DISTINCT t) AS tx_count,
               avg(t.amount) AS avg_tx_amount,
               collect(DISTINCT e.type) AS intent_markers
    """, {"id": customer_id})

    if not result:
        return {}

    r = result[0]
    intent_markers = [m for m in (r.get("intent_markers") or []) if m is not None]
    return {
        "utilization": r.get("utilization") or 0,
        "dpd": r.get("dpd") or 0,
        "current_limit": r.get("current_limit") or 0,
        "credit_score": r.get("credit_score") or 0,
        "segment": r.get("segment") or "Unknown",
        "risk_score": r.get("risk_score") or 0.5,
        "months_active": r.get("months_active") or 0,
        "inquiries": r.get("inquiries") or 0,
        "tx_count": r.get("tx_count") or 0,
        "avg_tx_amount": r.get("avg_tx_amount") or 0,
        "intent_markers": intent_markers,
        "has_travel_intent": "Travel Indicator" in intent_markers,
        "has_luxury_intent": "Luxury Indicator" in intent_markers,
    }


def extract_aml_features(customer_id: str) -> dict:
    """Extract features from the AML graph topology via Cypher."""
    result = execute_query("""
        MATCH (p:Person {id: $id})
        OPTIONAL MATCH (p)-[:HAS_CONTEXT]->(ctx:Context)
        OPTIONAL MATCH (p)-[:LOGGED_IN_FROM]->(d:Device)
        OPTIONAL MATCH (threat:Fraudster)-[:LOGGED_IN_FROM]->(d)
        OPTIONAL MATCH (p)-[:OWNS]->(a:Account)-[:INITIATED]->(t:Transaction)-[:DESTINATION]->(dest:Entity)
        RETURN d.ip AS device_ip,
               d.type AS device_type,
               threat IS NOT NULL AS shared_with_threat,
               threat.name AS threat_name,
               ctx.risk_score AS risk_score,
               t.amount AS wire_amount,
               dest.name AS dest_name,
               dest.jurisdiction AS dest_jurisdiction,
               count(DISTINCT threat) AS threat_count
    """, {"id": customer_id})

    if not result:
        return {}

    r = result[0]
    dest_jurisdiction = r.get("dest_jurisdiction") or "Domestic"
    high_risk_jurisdictions = {"Cayman Islands", "Panama", "Cyprus", "Malta", "British Virgin Islands"}
    return {
        "device_ip": r.get("device_ip") or "unknown",
        "device_type": r.get("device_type") or "unknown",
        "shared_with_threat": bool(r.get("shared_with_threat")),
        "threat_name": r.get("threat_name") or None,
        "threat_count": r.get("threat_count") or 0,
        "risk_score": r.get("risk_score") or 0.5,
        "wire_amount": r.get("wire_amount") or 0,
        "dest_name": r.get("dest_name") or "Unknown",
        "dest_jurisdiction": dest_jurisdiction,
        "is_high_risk_jurisdiction": dest_jurisdiction in high_risk_jurisdictions,
    }


def extract_healthcare_features(patient_id: str) -> dict:
    """Extract features from the Healthcare graph topology via Cypher."""
    result = execute_query("""
        MATCH (p:Patient {id: $id})
        OPTIONAL MATCH (p)-[:HAS_CONTEXT]->(ctx:Context)
        OPTIONAL MATCH (p)-[:HAD_ENCOUNTER]->(enc:Encounter)-[:RESULTED_IN]->(diag:Diagnosis)
        OPTIONAL MATCH (diag)-[:TREATMENT_PLAN]->(rx:Prescription)
        OPTIONAL MATCH (rx)-[:HAS_CARE_GAP]->(gap)
        RETURN p.age AS age,
               p.risk_tier AS risk_tier,
               ctx.risk_score AS risk_score,
               enc.type AS encounter_type,
               enc.department AS department,
               diag.code AS diag_code,
               diag.name AS diag_name,
               rx.medication AS medication,
               rx.status AS rx_status,
               gap IS NOT NULL AS has_care_gap,
               gap.duration_days AS care_gap_days
    """, {"id": patient_id})

    if not result:
        return {}

    r = result[0]
    diag_code = r.get("diag_code") or ""
    critical_codes = {"I50.9", "I21.9", "J96.01"}
    chronic_codes = {"E11.9", "I10", "J44.1"}
    return {
        "age": r.get("age") or 0,
        "risk_tier": r.get("risk_tier") or "Low",
        "risk_score": r.get("risk_score") or 0.1,
        "encounter_type": r.get("encounter_type") or "Unknown",
        "department": r.get("department") or "Unknown",
        "diag_code": diag_code,
        "diag_name": r.get("diag_name") or "Unknown",
        "medication": r.get("medication") or "None",
        "rx_status": r.get("rx_status") or "Unknown",
        "has_care_gap": bool(r.get("has_care_gap")),
        "care_gap_days": r.get("care_gap_days") or 0,
        "is_critical_diagnosis": diag_code in critical_codes,
        "is_chronic_diagnosis": diag_code in chronic_codes,
    }


# ──────────────────────────────────────────────────
# POPULATION-BASED CONFIDENCE SCORING
# ──────────────────────────────────────────────────

def calculate_population_confidence(segment: str, proposed_action: str) -> float:
    """Calculate confidence by comparing against similar decisions in the population."""
    result = execute_query("""
        MATCH (d:Decision)-[:ABOUT]->(p)
        WHERE p.segment = $segment OR p.risk_tier = $segment
        WITH count(d) AS total,
             sum(CASE WHEN d.action = $action THEN 1 ELSE 0 END) AS matching
        RETURN total, matching
    """, {"segment": segment, "action": proposed_action})

    if result and result[0]["total"] > 0:
        base_confidence = result[0]["matching"] / result[0]["total"]
        # Blend with rule-based confidence (70% rule, 30% population)
        return base_confidence
    return 0.0  # No historical data yet


# ──────────────────────────────────────────────────
# MAIN EVALUATION FUNCTION
# ──────────────────────────────────────────────────

def evaluate_case(
    customer: dict,
    account: dict,
    trigger_event: TriggerEvent,
    policies: list[dict],
) -> PolicyEvaluationResult:
    """
    Evaluate a case by traversing the actual graph topology.
    No hardcoded customer IDs — rules operate on extracted features.
    """
    result = PolicyEvaluationResult()
    customer_id = customer.get("customer_id", customer.get("id", ""))

    explanation = {
        "risk_score": customer.get("risk_score", 0.5),
        "utilization_pct": account.get("utilization_pct", 0),
        "trigger": trigger_event.value,
        "customer_id": customer_id,
        "factors": [],
        "graph_features": {},
    }

    # ==========================================
    # SCENARIO 1: FINANCIAL CREDIT LIMIT
    # ==========================================
    if trigger_event in [TriggerEvent.CREDIT_LIMIT_REQUEST, TriggerEvent.CREDIT_LIMIT_REVIEW]:
        features = extract_financial_features(customer_id)
        if not features:
            explanation["factors"].append("No financial graph topology found for this entity.")
            result.explanation_inputs = explanation
            return result

        explanation["graph_features"] = features
        util = features["utilization"]
        dpd = features["dpd"]
        credit_score = features["credit_score"]
        has_travel = features["has_travel_intent"]
        segment = features["segment"]
        risk_score = features["risk_score"]
        current_limit = features["current_limit"]
        months_active = features["months_active"]

        # Rule 1: Hard decline if DPD > 30
        if dpd > 30:
            result.action = RecommendedAction.DECLINE
            result.confidence = 0.99
            result.requires_human_review = False
            explanation["factors"].append(f"Hard decline: {dpd} DPD exceeds 30-day policy limit.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-CLI-03", policy_name="Subprime Hard Decline",
                family="Credit", matched=True,
                details=f"Account has {dpd} days past due — exceeds absolute limit."
            ))
            result.ranked_actions = [
                RankedAction(rank=1, action="HARD DECLINE", confidence=0.99,
                             description=f"Decline due to {dpd} DPD. No counter-offer possible.",
                             revenue_impact="-$0"),
                RankedAction(rank=2, action="OFFER FINANCIAL COUNSELING", confidence=0.45,
                             description="Decline CLI but offer enrollment in financial wellness program.",
                             revenue_impact="+$500/year (retention)"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 2: High util + travel intent + 0 DPD → APPROVE
        if util > 0.70 and has_travel and dpd == 0:
            result.action = RecommendedAction.APPROVE
            result.confidence = min(0.70 + (credit_score - 650) / 500, 0.98)
            result.requires_human_review = False
            explanation["factors"].append(f"High utilization ({util*100:.0f}%) with Travel Indicator and 0 DPD — strong upgrade signal.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-CLI-01", policy_name="Travel Intent CLI Auto-Approve",
                family="Credit", matched=True,
                details=f"Approving: {util*100:.0f}% utilization + {features['intent_markers']} intent + clean payment history."
            ))
            increase_amount = min(current_limit * 0.5, 10000)
            result.ranked_actions = [
                RankedAction(rank=1, action=f"APPROVE ${increase_amount:,.0f} INCREASE", confidence=result.confidence,
                             description=f"Full approval based on travel intent, {credit_score} credit score, and {months_active}-month tenure.",
                             revenue_impact=f"+${increase_amount * 0.08:,.0f}/year interest"),
                RankedAction(rank=2, action="APPROVE + CARD UPGRADE", confidence=result.confidence * 0.92,
                             description="Approve CLI and offer upgrade to premium card with travel benefits.",
                             revenue_impact="+$3,500/year"),
                RankedAction(rank=3, action="APPROVE + TRAVEL INSURANCE", confidence=result.confidence * 0.85,
                             description="Approve CLI with cross-sell travel insurance bundle.",
                             revenue_impact="+$89 one-time"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 3: High util + DPD > 0 + no positive intent → DECLINE with counter
        if util > 0.80 and dpd > 0:
            result.action = RecommendedAction.DECLINE
            result.confidence = min(0.80 + dpd / 100, 0.98)
            result.requires_human_review = False
            explanation["factors"].append(f"High utilization ({util*100:.0f}%) and {dpd} DPD with no positive intent markers.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-CLI-02", policy_name="Standard Utilization Stop",
                family="Credit", matched=True,
                details=f"Declined: {util*100:.0f}% utilization + {dpd} DPD. Risk score: {risk_score:.2f}."
            ))
            counter_amount = max(min(current_limit * 0.2, 2000), 500)
            result.counter_offer = CounterOffer(
                suggested_value=f"${counter_amount:,.0f} Conditional Increase (instead of full request)",
                original_request=f"Credit Limit Increase on ${current_limit:,.0f} limit",
                rationale=f"Full increase denied due to {util*100:.0f}% utilization and {dpd} DPD. Smaller ${counter_amount:,.0f} increase available with conditions.",
                conditions=[
                    f"Clear current past-due balance ({dpd} DPD) within 30 days",
                    "Maintain 0 DPD for 60 consecutive days",
                    f"Utilization must drop below 80% before increase activates",
                    "Auto-review scheduled at day 90"
                ]
            )
            result.ranked_actions = [
                RankedAction(rank=1, action="DECLINE FULL REQUEST", confidence=result.confidence,
                             description=f"Decline: {util*100:.0f}% util + {dpd} DPD indicates default risk.",
                             revenue_impact="-$0"),
                RankedAction(rank=2, action=f"COUNTER: ${counter_amount:,.0f} CONDITIONAL", confidence=0.72,
                             description=f"Smaller increase contingent on clearing DPD and maintaining utilization below 80%.",
                             revenue_impact=f"+${counter_amount * 0.08:,.0f}/year"),
                RankedAction(rank=3, action="OFFER FINANCIAL COUNSELING", confidence=0.60,
                             description="Decline CLI but offer free financial wellness program enrollment.",
                             revenue_impact="+$500/year (retention)"),
                RankedAction(rank=4, action="DECLINE + RETENTION CALL", confidence=0.55,
                             description="Hard decline with proactive retention specialist outreach.",
                             revenue_impact="+$800/year (retention)"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 4: Low utilization + 0 DPD → APPROVE
        if util < 0.50 and dpd == 0 and credit_score >= 700:
            result.action = RecommendedAction.APPROVE
            result.confidence = min(0.75 + (credit_score - 700) / 400, 0.95)
            result.requires_human_review = False
            explanation["factors"].append(f"Healthy profile: {util*100:.0f}% utilization, {credit_score} credit score, {dpd} DPD.")
            result.ranked_actions = [
                RankedAction(rank=1, action="APPROVE STANDARD INCREASE", confidence=result.confidence,
                             description=f"Low-risk approval: {credit_score} credit score with {util*100:.0f}% utilization.",
                             revenue_impact=f"+${current_limit * 0.03:,.0f}/year"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 5: Medium risk — escalate for human review
        result.action = RecommendedAction.ESCALATE_FOR_REVIEW
        result.confidence = 0.60
        result.requires_human_review = True
        explanation["factors"].append(f"Mixed signals: {util*100:.0f}% util, {dpd} DPD, {credit_score} score. Manual review recommended.")
        result.ranked_actions = [
            RankedAction(rank=1, action="ESCALATE FOR REVIEW", confidence=0.60,
                         description="Profile doesn't clearly match approve or decline rules. Analyst review needed.",
                         revenue_impact="$0"),
            RankedAction(rank=2, action="CONDITIONAL APPROVE (SMALL)", confidence=0.50,
                         description=f"Approve small increase (${min(current_limit * 0.10, 1000):,.0f}) with monitoring.",
                         revenue_impact=f"+${min(current_limit * 0.01, 100):,.0f}/year"),
        ]
        result.explanation_inputs = explanation
        return result

    # ==========================================
    # SCENARIO 2: AML FRAUD DETECTION
    # ==========================================
    if trigger_event == TriggerEvent.FRAUD_DETECTION:
        features = extract_aml_features(customer_id)
        if not features:
            explanation["factors"].append("No AML graph topology found for this entity.")
            result.explanation_inputs = explanation
            return result

        explanation["graph_features"] = features
        shared = features["shared_with_threat"]
        high_risk_dest = features["is_high_risk_jurisdiction"]
        wire_amount = features["wire_amount"]
        dest_name = features["dest_name"]
        threat_name = features["threat_name"]
        risk_score = features["risk_score"]

        # Rule 1: Shared device with Fraudster → BLOCK
        if shared and high_risk_dest:
            result.action = RecommendedAction.DECLINE
            result.confidence = 0.99
            result.requires_human_review = False
            explanation["factors"].append(f"Device shared with {threat_name}. Wire to {dest_name} ({features['dest_jurisdiction']}) — 2-hop threat path confirmed.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-AML-01", policy_name="Shared Identity Device Threat",
                family="Fraud", matched=True,
                details=f"Immediate block: device IP {features['device_ip']} linked to {threat_name}."
            ))
            result.counter_offer = CounterOffer(
                suggested_value="Release hold after Enhanced Due Diligence (EDD)",
                original_request=f"${wire_amount:,.2f} Wire Transfer to {dest_name}",
                rationale=f"Wire blocked due to shared device with {threat_name}. Source-of-funds documentation and verification required for partial release.",
                conditions=[
                    "Submit source-of-funds documentation within 48 hours",
                    "Complete enhanced identity verification (video KYC)",
                    f"Wire amount reduced to ${min(wire_amount * 0.3, 5000):,.0f} maximum pending investigation"
                ]
            )
            result.ranked_actions = [
                RankedAction(rank=1, action="BLOCK + FILE SAR", confidence=0.99,
                             description=f"Block ${wire_amount:,.2f} wire and file Suspicious Activity Report with FinCEN.",
                             revenue_impact=f"-${wire_amount:,.2f} blocked"),
                RankedAction(rank=2, action="HOLD + ENHANCED VERIFICATION", confidence=0.75,
                             description="72-hour hold with enhanced due diligence request.",
                             revenue_impact="-$0 (pending)"),
                RankedAction(rank=3, action="ESCALATE TO BSA OFFICER", confidence=0.60,
                             description="Route to BSA/AML Compliance Officer for manual determination.",
                             revenue_impact="-$0 (pending)")
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 2: Shared device but domestic destination → ESCALATE
        if shared and not high_risk_dest:
            result.action = RecommendedAction.ESCALATE_FOR_REVIEW
            result.confidence = 0.80
            result.requires_human_review = True
            explanation["factors"].append(f"Device shared with THREAT node but wire is Domestic to {dest_name}. Elevated risk — manual review.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-AML-01", policy_name="Shared Identity Device Threat",
                family="Fraud", matched=True,
                details=f"Shared device but domestic destination mitigates risk. Escalating."
            ))
            result.ranked_actions = [
                RankedAction(rank=1, action="ESCALATE FOR REVIEW", confidence=0.80,
                             description="Shared device detected but domestic destination reduces threat level.",
                             revenue_impact="$0"),
                RankedAction(rank=2, action="APPROVE WITH MONITORING", confidence=0.55,
                             description="Allow wire but add 30-day enhanced transaction monitoring.",
                             revenue_impact=f"+${wire_amount * 0.001:,.2f} fee"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 3: High-risk destination but no threat device → ESCALATE
        if high_risk_dest and wire_amount > 5000:
            result.action = RecommendedAction.ESCALATE_FOR_REVIEW
            result.confidence = 0.70
            result.requires_human_review = True
            explanation["factors"].append(f"Wire of ${wire_amount:,.2f} to {features['dest_jurisdiction']} — high-risk jurisdiction. No device threat detected.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-AML-02", policy_name="High-Risk Jurisdiction Structuring",
                family="Fraud", matched=True,
                details=f"Wire to high-risk jurisdiction exceeds $5,000 threshold."
            ))
            result.ranked_actions = [
                RankedAction(rank=1, action="ESCALATE FOR REVIEW", confidence=0.70,
                             description=f"${wire_amount:,.2f} to {features['dest_jurisdiction']} exceeds threshold.",
                             revenue_impact="$0"),
                RankedAction(rank=2, action="APPROVE WITH SOURCE-OF-FUNDS", confidence=0.50,
                             description="Approve if customer provides source-of-funds documentation.",
                             revenue_impact=f"+${wire_amount * 0.005:,.2f} wire fee"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 4: Clean profile → APPROVE
        result.action = RecommendedAction.APPROVE
        result.confidence = min(0.80 + (1.0 - risk_score) * 0.15, 0.95)
        result.requires_human_review = False
        explanation["factors"].append(f"Clean device, Domestic wire (${wire_amount:,.2f} to {dest_name}). No threat indicators.")
        result.applied_policies.append(AppliedPolicy(
            policy_id="POL-AML-03", policy_name="Clean Domestic Wire",
            family="Fraud", matched=True,
            details=f"No shared devices, domestic jurisdiction, clean transaction profile."
        ))
        result.ranked_actions = [
            RankedAction(rank=1, action="APPROVE", confidence=result.confidence,
                         description=f"Clear ${wire_amount:,.2f} wire to {dest_name}. No AML risk.",
                         revenue_impact=f"+${wire_amount * 0.001:,.2f} wire fee"),
            RankedAction(rank=2, action="APPROVE + FLAG FOR MONITORING", confidence=result.confidence * 0.85,
                         description="Approve but add to enhanced transaction monitoring for 30 days.",
                         revenue_impact=f"+${wire_amount * 0.001:,.2f} wire fee"),
        ]
        result.explanation_inputs = explanation
        return result

    # ==========================================
    # SCENARIO 3: HEALTHCARE CARE GAP
    # ==========================================
    if trigger_event == TriggerEvent.CARE_GAP_REVIEW:
        features = extract_healthcare_features(customer_id)
        if not features:
            explanation["factors"].append("No healthcare graph topology found for this entity.")
            result.explanation_inputs = explanation
            return result

        explanation["graph_features"] = features
        has_gap = features["has_care_gap"]
        gap_days = features["care_gap_days"]
        is_critical = features["is_critical_diagnosis"]
        is_chronic = features["is_chronic_diagnosis"]
        risk_tier = features["risk_tier"]
        rx_status = features["rx_status"]
        medication = features["medication"]
        diag_name = features["diag_name"]
        age = features["age"]
        department = features["department"]

        # Rule 1: Critical diagnosis + care gap > 7 days → URGENT INTERVENTION
        if is_critical and has_gap and gap_days > 7:
            result.action = RecommendedAction.ESCALATE_FOR_REVIEW
            result.confidence = min(0.85 + gap_days / 100, 0.99)
            result.requires_human_review = True
            explanation["factors"].append(f"CRITICAL: {diag_name} patient missed {medication} refill for {gap_days} days.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-MED-01", policy_name="High-Risk Med Non-Adherence",
                family="Clinical", matched=True,
                details=f"Critical diagnosis ({diag_name}) + {gap_days}-day care gap on {medication}. Immediate intervention required."
            ))
            result.counter_offer = CounterOffer(
                suggested_value="Telehealth Check-in (before in-person intervention)",
                original_request="Immediate In-Person Clinical Intervention",
                rationale=f"Patient ({age}y, {risk_tier} Risk) has missed {medication} for {gap_days} days. Telehealth can assess barriers before costlier in-person visit.",
                conditions=[
                    "Schedule telehealth within 24 hours",
                    "If patient confirms medication access issues, auto-trigger pharmacy outreach",
                    f"If patient unreachable within 48 hours, escalate to in-person {department} visit"
                ]
            )
            result.ranked_actions = [
                RankedAction(rank=1, action="URGENT IN-PERSON INTERVENTION", confidence=result.confidence,
                             description=f"{diag_name} medication non-adherence ({gap_days} days). Dispatch care coordinator.",
                             revenue_impact=f"Cost: $450/visit"),
                RankedAction(rank=2, action="TELEHEALTH CHECK-IN FIRST", confidence=result.confidence * 0.87,
                             description="Assess adherence barriers via telehealth before dispatching in-person.",
                             revenue_impact="Cost: $85/call"),
                RankedAction(rank=3, action="PHARMACY OUTREACH", confidence=result.confidence * 0.75,
                             description=f"Contact pharmacy to confirm {medication} availability and auto-deliver.",
                             revenue_impact="Cost: $15/outreach"),
                RankedAction(rank=4, action=f"REFER TO {department.upper()}", confidence=result.confidence * 0.60,
                             description=f"Refer to {department} for medication review — current regimen may need adjustment.",
                             revenue_impact="Cost: $250/consult"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 2: Chronic diagnosis + care gap 3-7 days → SCHEDULE FOLLOW-UP
        if (is_chronic or is_critical) and has_gap and 3 <= gap_days <= 7:
            result.action = RecommendedAction.ESCALATE_FOR_REVIEW
            result.confidence = 0.75
            result.requires_human_review = True
            explanation["factors"].append(f"Chronic condition ({diag_name}) with {gap_days}-day care gap on {medication}.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-MED-02", policy_name="Chronic Condition Monitoring",
                family="Clinical", matched=True,
                details=f"Care gap of {gap_days} days on {medication} for {diag_name}. Follow-up recommended."
            ))
            result.ranked_actions = [
                RankedAction(rank=1, action="SCHEDULE FOLLOW-UP CALL", confidence=0.75,
                             description=f"{gap_days}-day gap on {medication}. Schedule clinical follow-up within 72 hours.",
                             revenue_impact="Cost: $45/call"),
                RankedAction(rank=2, action="PHARMACY OUTREACH", confidence=0.65,
                             description="Automated pharmacy notification to check Rx availability.",
                             revenue_impact="Cost: $15/outreach"),
                RankedAction(rank=3, action="PATIENT PORTAL REMINDER", confidence=0.50,
                             description="Send automated reminder via patient portal and mobile app.",
                             revenue_impact="Cost: $0"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 3: Care gap < 3 days → Monitor
        if has_gap and gap_days < 3:
            result.action = RecommendedAction.APPROVE
            result.confidence = 0.80
            result.requires_human_review = False
            explanation["factors"].append(f"Minor care gap ({gap_days} days) on {medication}. Within acceptable window.")
            result.ranked_actions = [
                RankedAction(rank=1, action="MONITOR - NO ACTION", confidence=0.80,
                             description=f"{gap_days}-day gap is within acceptable refill window. Continue monitoring.",
                             revenue_impact="$0"),
            ]
            result.explanation_inputs = explanation
            return result

        # Rule 4: No care gap, compliant → APPROVE
        if not has_gap and rx_status in ["Fulfilled", "Active"]:
            result.action = RecommendedAction.APPROVE
            result.confidence = 0.98
            result.requires_human_review = False
            explanation["factors"].append(f"Patient compliant: {diag_name} — {medication} status: {rx_status}. No care gaps detected.")
            result.applied_policies.append(AppliedPolicy(
                policy_id="POL-MED-03", policy_name="Compliant Patient Clearance",
                family="Clinical", matched=True,
                details=f"No care gaps. {rx_status} prescription for {medication}."
            ))
            result.ranked_actions = [
                RankedAction(rank=1, action="APPROVE - COMPLIANT", confidence=0.98,
                             description=f"Fully compliant. {encounter_type(features)} completed. Continue standard monitoring.",
                             revenue_impact="$0"),
                RankedAction(rank=2, action="SCHEDULE PREVENTIVE SCREENING", confidence=0.55,
                             description=f"Proactively schedule age-appropriate preventive screenings for {age}y patient.",
                             revenue_impact="Revenue: +$320/screening"),
            ]
            result.explanation_inputs = explanation
            return result

        # Fallback for healthcare
        result.action = RecommendedAction.ESCALATE_FOR_REVIEW
        result.confidence = 0.55
        result.requires_human_review = True
        explanation["factors"].append(f"Mixed clinical signals: {diag_name}, Rx: {rx_status}, Gap: {gap_days}d. Review needed.")
        result.explanation_inputs = explanation
        return result

    # ─── Fallback for unrecognized triggers ──────────
    result.action = RecommendedAction.ESCALATE_FOR_REVIEW
    result.confidence = 0.50
    result.requires_human_review = True
    explanation["factors"].append("No deterministic rule matched the trigger event and graph topology.")
    result.explanation_inputs = explanation
    return result


def encounter_type(features: dict) -> str:
    """Helper to format encounter type."""
    return features.get("encounter_type", "Visit")
