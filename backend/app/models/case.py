"""
Pydantic models for case evaluation and recommendations.
"""

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class TriggerEvent(str, Enum):
    CREDIT_LIMIT_REVIEW = "CREDIT_LIMIT_REVIEW"
    CREDIT_LIMIT_REQUEST = "CREDIT_LIMIT_REQUEST"
    PAYMENT_DELINQUENCY = "PAYMENT_DELINQUENCY"
    CHURN_SIGNAL = "CHURN_SIGNAL"
    ACCOUNT_REVIEW = "ACCOUNT_REVIEW"
    CUSTOMER_COMPLAINT = "CUSTOMER_COMPLAINT"
    FRAUD_DETECTION = "FRAUD_DETECTION"
    CARE_GAP_REVIEW = "CARE_GAP_REVIEW"


class RecommendedAction(str, Enum):
    APPROVE = "APPROVE"
    DECLINE = "DECLINE"
    ESCALATE_FOR_REVIEW = "ESCALATE_FOR_REVIEW"
    OFFER_RETENTION = "OFFER_RETENTION"
    REQUEST_DOCUMENTS = "REQUEST_DOCUMENTS"


class DecisionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    OVERRIDDEN = "OVERRIDDEN"
    ESCALATED = "ESCALATED"


class CaseEvaluationRequest(BaseModel):
    """Request to evaluate a case and generate an NBA recommendation."""
    customer_id: str = Field(..., description="Person ID", examples=["PER-001"])
    account_id: Optional[str] = Field(None, description="Account ID", examples=["ACC-001"])
    trigger_event: TriggerEvent = Field(..., description="What triggered this evaluation")
    notes: Optional[str] = Field(None, description="Analyst notes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "PER-002",
                    "account_id": "ACC-002",
                    "trigger_event": "CREDIT_LIMIT_REQUEST",
                    "notes": "Customer requested credit limit increase via phone"
                }
            ]
        }
    }


class AppliedPolicy(BaseModel):
    """A policy that was evaluated during recommendation."""
    policy_id: str
    policy_name: str
    family: str
    matched: bool = Field(..., description="Whether this policy's conditions were met")
    details: str = Field("", description="Why this policy matched or didn't")


class PrecedentCase(BaseModel):
    """A similar historical decision used as precedent."""
    decision_id: str
    action: str
    confidence: float
    outcome: Optional[str] = None
    similarity_score: float = Field(..., ge=0, le=1)
    customer_segment: str
    trigger_event: str
    created_at: Optional[str] = None


class CounterOffer(BaseModel):
    """A counter-offer proposed by the engine when a full approval isn't possible."""
    suggested_value: str = Field(..., description="The counter-offer value, e.g. '$2,500' or 'Telehealth check-in'")
    original_request: str = Field(..., description="What was originally requested, e.g. '$5,000 CLI'")
    rationale: str = Field(..., description="Why the counter is being proposed")
    conditions: list[str] = Field(default_factory=list, description="Conditions for the counter-offer")


class RankedAction(BaseModel):
    """One of several ranked alternative actions the engine recommends."""
    rank: int
    action: str
    confidence: float = Field(..., ge=0, le=1)
    description: str
    revenue_impact: Optional[str] = None


class NegotiationRequest(BaseModel):
    """A customer/analyst response to a decision — accept, counter, or decline."""
    response: str = Field(..., description="ACCEPT, COUNTER, or DECLINE")
    counter_value: Optional[str] = Field(None, description="New proposed value if response is COUNTER")
    reason: Optional[str] = Field(None, description="Reason for counter or decline")


class NegotiationStepResponse(BaseModel):
    """Response from a negotiation step."""
    step_number: int
    customer_response: str
    engine_action: str
    engine_confidence: float
    message: str
    counter_offer: Optional[CounterOffer] = None
    is_final: bool = Field(False, description="Whether this step closes the negotiation")


class RecommendationResponse(BaseModel):
    """Response from case evaluation with recommendation and explanation."""
    decision_id: str
    recommended_action: RecommendedAction
    confidence: float = Field(..., ge=0, le=1)
    requires_human_review: bool
    applied_policies: list[AppliedPolicy]
    precedent_cases: list[PrecedentCase] = []
    explanation_inputs: dict = Field(
        default_factory=dict,
        description="Structured data for narrative explanation generation"
    )
    customer_summary: dict = Field(default_factory=dict)
    account_summary: dict = Field(default_factory=dict)
    ai_narrative: Optional[str] = Field(None, description="LLM synthesized narrative of the decision")
    counter_offer: Optional[CounterOffer] = Field(None, description="Counter-offer if not a straight approve/decline")
    ranked_actions: list[RankedAction] = Field(default_factory=list, description="Ranked alternative actions")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CaseResponse(BaseModel):
    """Stored case with decision details."""
    decision_id: str
    customer_id: str
    account_id: str
    customer_name: str
    action: str
    confidence: float
    status: str
    trigger_event: str
    applied_policies: list[str] = []
    created_at: Optional[str] = None
    analyst_id: Optional[str] = None
    notes: Optional[str] = None

