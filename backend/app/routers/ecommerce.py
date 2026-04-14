"""
E-Commerce API router — Handles identity resolution and anonymous session merging.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import execute_write, execute_query

router = APIRouter(prefix="/ecommerce", tags=["E-Commerce"])

class IdentityResolveRequest(BaseModel):
    user_id: str = Field(..., description="The known authenticated Person ID")
    device_id: str = Field(..., description="The anonymous Device ID from the browser")


@router.post("/resolve-identity")
async def resolve_identity(request: IdentityResolveRequest):
    """
    Perform Identity Resolution.
    Merges an anonymous browsing history with a known customer profile
    by linking the Device to the Person and marking associated Sessions as authenticated.
    """
    
    # Check if device and user exist
    user_check = execute_query(
        "MATCH (p:Person {id: $user_id}) RETURN p.name AS name", 
        {"user_id": request.user_id}
    )
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")
        
    dev_check = execute_query(
        "MATCH (d:Device {id: $device_id}) RETURN d.type AS type", 
        {"device_id": request.device_id}
    )
    if not dev_check:
        raise HTTPException(status_code=404, detail="Device not found")

    # Perform the graph identity merge
    result = execute_write("""
        MATCH (p:Person {id: $user_id})
        MATCH (d:Device {id: $device_id})
        
        // Explicitly link the person to the device
        MERGE (p)-[:LOGGED_IN_FROM]->(d)
        
        WITH p, d
        // Find all anonymous sessions initiated from this device
        MATCH (d)-[:INITIATED]->(s:Session)
        WHERE s.is_authenticated = false
        
        // Mark them as authenticated and optionally link to Person
        SET s.is_authenticated = true
        MERGE (p)-[:OWNS_SESSION]->(s)
        
        // Track the total vehicle view count now attributed to this person
        WITH p, count(DISTINCT s) AS merged_sessions
        OPTIONAL MATCH (p)-[:OWNS_SESSION]->(:Session)-[:VIEWED]->(v:BrowsedVehicle)
        
        RETURN p.name AS user_name,
               merged_sessions,
               count(v) AS total_vehicles_viewed
    """, {
        "user_id": request.user_id,
        "device_id": request.device_id
    })

    if not result:
        return {"status": "success", "message": "Identity resolved but no anonymous sessions existed."}

    r = result[0]
    return {
        "status": "success",
        "user_name": r.get("user_name"),
        "merged_sessions": r.get("merged_sessions"),
        "total_vehicles_viewed": r.get("total_vehicles_viewed"),
        "message": f"Successfully merged anonymous device {request.device_id} into user {request.user_id}"
    }
