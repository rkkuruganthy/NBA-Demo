"""
Graph Analytics API router.
Population-level analytics, risk propagation, segment intelligence.
"""

from fastapi import APIRouter
from app.services.analytics_service import (
    get_population_analytics,
    get_risk_propagation,
    get_segment_intelligence,
    get_community_detection,
)

router = APIRouter(prefix="/analytics", tags=["Graph Analytics"])


@router.get("/population")
async def population_analytics():
    """
    Population-level analytics: decision distribution, segment confidence,
    graph topology metrics.
    """
    return get_population_analytics()


@router.get("/risk-propagation")
async def risk_propagation():
    """
    Detect fraud risk propagation through shared devices.
    Shows clusters of accounts connected to threat actors via 2-hop paths.
    """
    return get_risk_propagation()


@router.get("/segments")
async def segment_intelligence():
    """
    Segment-level intelligence: decision patterns grouped by customer segment
    with outcome tracking.
    """
    return get_segment_intelligence()


@router.get("/communities")
async def community_detection():
    """
    Identify behavioral communities: customer clusters based on
    utilization bands, payment status, and segment.
    """
    return get_community_detection()
