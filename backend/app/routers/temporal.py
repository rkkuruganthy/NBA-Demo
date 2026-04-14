"""
Temporal Intelligence API router.
Behavioral drift detection, decision timelines, and confidence decay.
"""

from fastapi import APIRouter, HTTPException
from app.services.temporal_service import (
    detect_behavioral_drift,
    get_decision_timeline,
    calculate_decision_decay,
)

router = APIRouter(prefix="/temporal", tags=["Temporal Intelligence"])


@router.get("/{customer_id}/drift")
async def behavioral_drift(customer_id: str):
    """
    Detect behavioral drift for a customer across their decision history.
    Identifies trends: rising utilization, escalating risk, deteriorating decisions.
    """
    result = detect_behavioral_drift(customer_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/{customer_id}/timeline")
async def decision_timeline(customer_id: str):
    """
    Get the full decision timeline for a customer with trend analysis.
    Includes all linked context, policies, outcomes, and negotiation steps.
    """
    result = get_decision_timeline(customer_id)
    return result


@router.get("/decay/{decision_id}")
async def confidence_decay(decision_id: str, half_life_days: int = 30):
    """
    Calculate confidence decay for an open decision based on time elapsed.
    Uses exponential decay with configurable half-life.
    """
    result = calculate_decision_decay(decision_id, half_life_days)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
