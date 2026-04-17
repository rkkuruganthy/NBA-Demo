import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI Client
API_KEY = os.getenv("OPENAI_API_KEY")

try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None


# ---------------------------------------------------------------------------
# Local narrative builder — used when OpenAI is unreachable (offline demo)
# Produces the same style/structure as the LLM prompt without any API call.
# ---------------------------------------------------------------------------

def _build_local_narrative(
    customer: dict,
    account: dict,
    rules: list,
    result: str,
    trigger: str,
    graph_features: dict = None,
    factors: list = None,
    counter_offer=None,
    ranked_actions: list = None,
) -> str:
    gf = graph_features or {}

    # Graph path traversal description by trigger type
    path_map = {
        "ABANDONED_SESSION": (
            "Customer → Session → Engagement → Transaction — "
            "This path identified the customer's omnichannel interaction and abandonment behavior across web, mobile, and physical dealership touchpoints."
        ),
        "CREDIT_LINE_INCREASE": (
            "Customer → Account → Transaction — "
            "This path assessed credit utilization, payment history, and spending patterns to evaluate credit worthiness."
        ),
        "RETENTION_OFFER": (
            "Customer → Account → Transaction — "
            "This path evaluated engagement signals, churn indicators, and account health metrics to assess retention priority."
        ),
        "FRAUD_DETECTION": (
            "Customer → Device → IPAddress → Transaction — "
            "This path traced device and network relationships to identify anomalous access patterns and threat actor proximity."
        ),
        "CARE_GAP_REVIEW": (
            "Patient → Encounter → Prescription → Diagnosis — "
            "This path identified care gaps, prescription adherence, and critical diagnosis flags requiring clinical intervention."
        ),
        "WIRE_TRANSFER_REVIEW": (
            "Customer → Account → Transaction → Entity — "
            "This path traced the wire transfer destination to detect jurisdictional risk and threat actor linkage."
        ),
    }
    graph_path = path_map.get(
        trigger,
        f"Customer → Context → Decision — Standard evaluation path for {trigger.replace('_', ' ').title()}."
    )

    # Human-readable labels for graph features
    feature_map = {
        "view_count": "Web Browsing History (Views)",
        "used_calculator": "Mobile Finance Calculator (Engagement)",
        "test_drive_count": "Physical Dealership Visit (Test Drive)",
        "max_trade_in_equity": "Trade-In Equity (Owned Vehicle)",
        "inventory_stock": "Regional Inventory Stock Level",
        "utilization": "Credit Utilization",
        "dpd": "Days Past Due",
        "credit_score": "Credit Score",
        "has_travel_intent": "Travel Intent Detected",
        "has_luxury_intent": "Luxury Intent Detected",
        "risk_score": "Risk Score",
        "shared_with_threat": "Device Shared with Threat Actor",
        "is_high_risk_jurisdiction": "High-Risk Jurisdiction",
        "wire_amount": "Wire Transfer Amount",
        "has_care_gap": "Care Gap Detected",
        "care_gap_days": "Care Gap Duration (Days)",
        "is_critical_diagnosis": "Critical Diagnosis",
        "diag_name": "Diagnosis",
        "medication": "Prescribed Medication",
        "rx_status": "Prescription Status",
        "segment": "Customer Segment",
        "months_active": "Months Active",
        "tx_count": "Transaction Count",
        "is_authenticated": "Is Authenticated",
        "device_type": "Device Type",
        "has_purchased": "Has Purchased",
    }

    # Build feature bullet list from extracted graph features
    feature_bullets = []
    for k, v in gf.items():
        if v is None or v == "" or v == []:
            continue
        label = feature_map.get(k, k.replace("_", " ").title())
        if isinstance(v, bool):
            feature_bullets.append(f"**{label}**: {'True' if v else 'False'}")
        elif isinstance(v, float):
            feature_bullets.append(f"**{label}**: {v:.2f}")
        elif isinstance(v, list):
            feature_bullets.append(f"**{label}**: {', '.join(str(x) for x in v)}")
        else:
            feature_bullets.append(f"**{label}**: {v}")

    # Policy names
    policy_names = [p.policy_name for p in rules] if rules else []
    policy_str = (
        " and ".join(f"**{p}**" for p in policy_names)
        if policy_names
        else "no specific policy"
    )

    # Action description
    action_map = {
        "OFFER_SMS": "send an **SMS Offer**",
        "DEALER_CONCIERGE_CALL": "initiate a **Dealer Concierge Call**",
        "OFFER_TRADE_IN": "present an **Equity Trade-In Offer**",
        "APPROVE": "**Approve** the request",
        "DECLINE": "**Decline** the request",
        "ESCALATE": "**Escalate** for analyst review",
        "CREDIT_LINE_INCREASE": "proceed with a **Credit Line Increase**",
        "RETENTION_OFFER": "issue a **Retention Offer**",
        "FLAG_FOR_REVIEW": "**Flag for Review**",
        "ALERT_FRAUD": "raise a **Fraud Alert**",
        "SCHEDULE_OUTREACH": "**Schedule Clinical Outreach**",
    }
    action_desc = action_map.get(result, f"execute **{result}**")

    # Top conditions evaluated
    conditions_text = ""
    if factors:
        top = factors[:3]
        conditions_text = (
            " The rules engine evaluated the following conditions: "
            + " ".join(f"{i + 1}. {f}" for i, f in enumerate(top))
            + "."
        )

    customer_name = customer.get("name", "the customer")
    feature_text = (
        " – ".join(feature_bullets[:6]) if feature_bullets else "standard profile metrics"
    )

    # Account context line (if available)
    account_text = ""
    if account:
        acc_type = account.get("type", "")
        util = account.get("utilization_pct")
        if acc_type or util is not None:
            util_str = f", utilization at {int(util * 100)}%" if util is not None else ""
            account_text = f" Account context: {acc_type}{util_str}."

    # Counter-offer line (if generated)
    counter_text = ""
    if counter_offer:
        counter_text = (
            f" A counter-offer of **{counter_offer.suggested_value}** was generated"
            f" with rationale: {counter_offer.rationale}."
        )

    narrative = (
        f"The engine traversed the following paths in the Neo4j knowledge graph to reach its decision: "
        f"**Path Traversed**: {graph_path} "
        f"Key feature values extracted during the traversal included: {feature_text}."
        f"{account_text}"
        f"{conditions_text} "
        f"This triggered {policy_str} based on the evaluated conditions."
        f"{counter_text} "
        f"The final determination was to {action_desc} for {customer_name}. "
        f"The confidence in this decision is supported by the graph-extracted signals and matched policy conditions above."
    )

    return narrative


# ---------------------------------------------------------------------------
# Main entry point — tries OpenAI first, falls back to local narrative
# ---------------------------------------------------------------------------

def synthesize_decision_narrative(
    customer: dict,
    account: dict,
    rules: list,
    result: str,
    trigger: str,
    graph_features: dict = None,
    factors: list = None,
    counter_offer=None,
    ranked_actions: list = None,
) -> str:
    """
    Takes the deterministic graph outputs — including traversed features,
    conditions checked, and policy matches — and synthesizes a narrative.

    Uses OpenAI when available; falls back to a locally-generated narrative
    (same structure, no API call) when offline or the key is missing.
    """

    # Build shared context string for the OpenAI prompt
    gf = graph_features or {}

    context_parts = [
        f"CUSTOMER: {customer.get('name')} (ID: {customer.get('id', customer.get('customer_id'))})",
        f"  Segment: {customer.get('segment', 'Unknown')}",
        f"  Credit Score: {customer.get('credit_score', 'N/A')}",
    ]

    if account:
        context_parts.extend([
            f"ACCOUNT: {account.get('type', 'N/A')} (ID: {account.get('id', 'N/A')})",
            f"  Credit Limit: ${account.get('current_limit', 0):,.0f}" if account.get('current_limit') else "",
            f"  Utilization: {int(account.get('utilization_pct', 0) * 100)}%",
            f"  Days Past Due: {account.get('dpd', 0)}",
        ])

    context_parts.append(f"\nTRIGGER EVENT: {trigger}")
    context_parts.append(f"DETERMINISTIC ENGINE DECISION: {result}")

    feature_map = {
        "utilization": "Credit Utilization",
        "dpd": "Days Past Due",
        "credit_score": "Credit Score",
        "has_travel_intent": "Travel Intent Detected (Transaction→Entity path)",
        "has_luxury_intent": "Luxury Intent Detected",
        "intent_markers": "Intent Markers Found",
        "segment": "Customer Segment",
        "risk_score": "Risk Score",
        "months_active": "Months Active",
        "inquiries": "Recent Credit Inquiries",
        "tx_count": "Transaction Count",
        "shared_with_threat": "Device Shared with Threat Actor (2-hop path)",
        "threat_name": "Linked Threat Actor",
        "is_high_risk_jurisdiction": "High-Risk Jurisdiction Destination",
        "dest_jurisdiction": "Wire Destination Jurisdiction",
        "dest_name": "Wire Destination Entity",
        "wire_amount": "Wire Transfer Amount",
        "device_ip": "Login Device IP",
        "has_care_gap": "Care Gap Detected (Rx→CareGap path)",
        "care_gap_days": "Care Gap Duration (Days)",
        "is_critical_diagnosis": "Critical Diagnosis (ICD-10)",
        "is_chronic_diagnosis": "Chronic Diagnosis (ICD-10)",
        "diag_name": "Diagnosis",
        "diag_code": "ICD-10 Code",
        "medication": "Prescribed Medication",
        "rx_status": "Prescription Status",
        "risk_tier": "Patient Risk Tier",
        "age": "Patient Age",
        "department": "Treating Department",
        "view_count": "Web Browsing History (Views)",
        "used_calculator": "Mobile Finance Calculator (Engagement)",
        "test_drive_count": "Physical Dealership Visit (Test Drive)",
        "max_trade_in_equity": "Trade-In Equity (Owned Vehicle)",
        "inventory_stock": "Regional Inventory Stock Level",
    }

    if gf:
        context_parts.append("\nGRAPH FEATURES EXTRACTED (via Cypher traversal of actual Neo4j relationships):")
        for k, v in gf.items():
            label = feature_map.get(k, k)
            if v is not None and v != "" and v != [] and k not in ["current_limit"]:
                if isinstance(v, float):
                    context_parts.append(f"  ✓ {label}: {v:.2f}")
                elif isinstance(v, list):
                    context_parts.append(f"  ✓ {label}: {', '.join(str(x) for x in v)}")
                else:
                    context_parts.append(f"  ✓ {label}: {v}")

    if factors:
        context_parts.append("\nCONDITIONS EVALUATED BY RULES ENGINE:")
        for i, f in enumerate(factors, 1):
            context_parts.append(f"  {i}. {f}")

    if rules:
        context_parts.append(f"\nPOLICIES TRIGGERED: {', '.join([p.policy_name for p in rules])}")
        for p in rules:
            context_parts.append(f"  → {p.policy_name}: {p.details}")
    else:
        context_parts.append("\nPOLICIES TRIGGERED: None (no specific policy rule was matched)")

    if counter_offer:
        context_parts.append(f"\nCOUNTER-OFFER GENERATED: {counter_offer.suggested_value}")
        context_parts.append(f"  Rationale: {counter_offer.rationale}")
        if counter_offer.conditions:
            context_parts.append(f"  Conditions: {'; '.join(counter_offer.conditions)}")

    context = "\n".join(context_parts)

    persona = "expert Credit Analyst"
    if trigger == "FRAUD_DETECTION":
        persona = "expert AML Fraud Investigator / Cyber Security Analyst"
    elif trigger == "CARE_GAP_REVIEW":
        persona = "expert Clinical Care Coordinator / Medical Analyst"
    elif trigger == "ABANDONED_SESSION":
        persona = "expert Automotive E-Commerce Strategist / MarTech Analyst"

    system_prompt = (
        f"You are an {persona} assistant interpreting a mathematical Enterprise Context Graph for a human underwriter/analyst. "
        "A strict, deterministic Rules Engine has ALREADY made the final decision by traversing the Neo4j knowledge graph. "
        "You cannot change this decision. "
        "\n\nYour job is to synthesize a thorough, structured narrative explaining EXACTLY HOW the engine reached this decision. "
        "Include:\n"
        "1. What graph paths were traversed (e.g., 'The engine traversed Person→Account→Transaction→Entity to detect travel intent')\n"
        "2. What specific feature values were extracted and compared against thresholds\n"
        "3. Which policy rules fired and why\n"
        "4. The final determination and confidence rationale\n"
        "\nWrite 4-6 sentences. Use bullet points for key data points. "
        "Speak directly to the analyst (e.g., 'The engine traversed...', 'This triggered policy POL-CLI-02 because...'). "
        "Do NOT hallucinate data outside of the explicit context provided."
    )

    # Try OpenAI — fall back to local narrative on any failure (no internet, bad key, timeout)
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Graph Context:\n{context}"}
                ],
                temperature=0.1,
                max_tokens=400,
                timeout=8,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI unavailable, using local narrative: {e}")

    # Offline / no key / timeout — generate narrative from graph data directly
    return _build_local_narrative(
        customer=customer,
        account=account,
        rules=rules,
        result=result,
        trigger=trigger,
        graph_features=graph_features,
        factors=factors,
        counter_offer=counter_offer,
        ranked_actions=ranked_actions,
    )
