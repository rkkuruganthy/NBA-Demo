from fastapi import APIRouter, HTTPException
from neo4j import GraphDatabase
from app.db import get_driver
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/explorer", tags=["explorer"])

class Node(BaseModel):
    id: str
    labels: List[str]
    properties: Dict[str, Any]

class Relationship(BaseModel):
    id: str
    type: str
    startNode: str
    endNode: str
    properties: Dict[str, Any]

class GraphData(BaseModel):
    nodes: List[Node]
    relationships: List[Relationship]

def serialize_props(props):
    result = {}
    for k, v in dict(props).items():
        if hasattr(v, "iso_format"):
            result[k] = v.iso_format()
        else:
            result[k] = v
    return result

@router.get("/customer/{customer_id}", response_model=GraphData)
async def get_customer_graph(customer_id: str):
    """
    Returns the graph data (nodes and relationships) surrounding a specific customer,
    including their accounts, recent decisions, contexts, applied policies, and precedent cases.
    """
    driver = get_driver()
    
    query = """
    MATCH path = (root {id: $customer_id})-[*1..5]-()
    UNWIND nodes(path) AS n
    UNWIND relationships(path) AS r
    RETURN collect(DISTINCT n) AS nodes, collect(DISTINCT r) AS rels
    """
    
    records, _, _ = driver.execute_query(query, customer_id=customer_id)
    
    if not records:
        return {"nodes": [], "relationships": []}
        
    record = records[0]
    neo4j_nodes = record["nodes"]
    neo4j_rels = record["rels"]
    
    nodes = []
    for n in neo4j_nodes:
        if n is None: continue
        
        # Determine the best ID field to use for the visual graph
        node_id = n.get("id") or n.get("decision_id") or str(n.element_id)
        
        nodes.append({
            "id": node_id,
            "labels": list(n.labels),
            "properties": serialize_props(n)
        })
        
    relationships = []
    for r in neo4j_rels:
        if r is None: continue
        
        # Get start/end node visual IDs
        start_id = r.start_node.get("id") or r.start_node.get("decision_id") or str(r.start_node.element_id)
        end_id = r.end_node.get("id") or r.end_node.get("decision_id") or str(r.end_node.element_id)
        
        relationships.append({
            "id": str(r.element_id),
            "type": r.type,
            "startNode": start_id,
            "endNode": end_id,
            "properties": serialize_props(r)
        })
        
    return {"nodes": nodes, "relationships": relationships}
