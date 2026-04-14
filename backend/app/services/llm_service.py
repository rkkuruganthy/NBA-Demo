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

def synthesize_decision_narrative(
    customer: dict,
    account: dict,
    rules: list,
    result: str,
    trigger: str,
    graph_features: dict = None,
    factors: list = None,
    counter_offer = None,
    ranked_actions: list = None,
) -> str:
    """
    Takes the deterministic graph outputs — including traversed features, 
    conditions checked, and policy matches — and uses an LLM to synthesize 
    a detailed professional narrative for the Analyst.
    """
    if not client:
        return "AI Narrative unavailable due to missing API Key."

    # Build comprehensive context from Graph traversal results
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
    
    # Graph features extracted via Cypher traversal
    if gf:
        context_parts.append("\nGRAPH FEATURES EXTRACTED (via Cypher traversal of actual Neo4j relationships):")
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
        }
        for k, v in gf.items():
            label = feature_map.get(k, k)
            if v is not None and v != "" and v != [] and k not in ["current_limit"]:
                if isinstance(v, float):
                    context_parts.append(f"  ✓ {label}: {v:.2f}")
                elif isinstance(v, list):
                    context_parts.append(f"  ✓ {label}: {', '.join(str(x) for x in v)}")
                else:
                    context_parts.append(f"  ✓ {label}: {v}")
    
    # Factors / conditions checked
    if factors:
        context_parts.append("\nCONDITIONS EVALUATED BY RULES ENGINE:")
        for i, f in enumerate(factors, 1):
            context_parts.append(f"  {i}. {f}")
    
    # Policies triggered
    if rules:
        context_parts.append(f"\nPOLICIES TRIGGERED: {', '.join([p.policy_name for p in rules])}")
        for p in rules:
            context_parts.append(f"  → {p.policy_name}: {p.details}")
    else:
        context_parts.append("\nPOLICIES TRIGGERED: None (no specific policy rule was matched)")
    
    # Counter-offer if exists
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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Graph Context:\n{context}"}
            ],
            temperature=0.1,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI Synthesis Error: {str(e)}")
        return f"AI Interpretation temporarily unavailable. (Deterministic Rules executed successfully: {result})"
