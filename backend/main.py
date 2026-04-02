from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db import verify_connectivity, close_driver, execute_query
from app.routers import cases, decisions, explorer
from app.services.graph_init import init_graph, get_graph_stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    logger.info("🚀 NBA Backend starting up...")
    neo4j_ok = verify_connectivity()
    if neo4j_ok:
        logger.info("✅ Neo4j connection verified")
    else:
        logger.warning("⚠️  Neo4j not available — some features will be unavailable")
    yield
    logger.info("🛑 NBA Backend shutting down...")
    close_driver()


app = FastAPI(
    title="NBA Context Engine",
    description="Next Best Action recommendation engine for financial services",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cases.router)
app.include_router(decisions.router)
app.include_router(explorer.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    neo4j_ok = verify_connectivity()
    return {
        "status": "ok",
        "service": "nba-backend",
        "version": "0.1.0",
        "neo4j": "connected" if neo4j_ok else "disconnected",
    }


@app.post("/graph/init")
async def initialize_graph():
    """Initialize graph schema and load seed data."""
    try:
        result = init_graph()
        return {"status": "initialized", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph init failed: {str(e)}")


@app.get("/graph/stats")
async def graph_stats():
    """Get graph node and relationship counts."""
    try:
        return get_graph_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


@app.get("/customers")
async def list_customers(search: str = "", industry: str = "", limit: int = 50, offset: int = 0):
    """List customers/patients with search and pagination. Supports 10K+ users."""
    
    # Build dynamic query based on filters
    where_clauses = ["(p:Person OR p:Patient)"]
    params = {"limit": limit, "offset": offset}
    
    if search:
        where_clauses.append("(p.name CONTAINS $search OR p.id CONTAINS $search)")
        params["search"] = search
    
    if industry == "financial":
        where_clauses = ["p:Person"]
        where_clauses.append("p.id STARTS WITH 'FIN' OR p.id STARTS WITH 'CUST-CLI'")
    elif industry == "aml":
        where_clauses = ["p:Person"]
        where_clauses.append("p.id STARTS WITH 'AML' OR p.id STARTS WITH 'CUST-AML'")
    elif industry == "healthcare":
        where_clauses = ["p:Patient"]
    
    where_str = " AND ".join(f"({c})" for c in where_clauses)
    
    results = execute_query(f"""
        MATCH (p) WHERE {where_str}
        OPTIONAL MATCH (p)-[:OWNS]->(a:Account)
        OPTIONAL MATCH (p)-[:HAS_CONTEXT]->(ctx:Context)
        RETURN p, a, ctx, labels(p) AS node_labels
        ORDER BY p.name
        SKIP $offset LIMIT $limit
    """, params)
    
    customers = []
    for r in results:
        p = dict(r["p"]) if r["p"] else {}
        a = dict(r["a"]) if r["a"] else {}
        ctx = dict(r["ctx"]) if r.get("ctx") else {}
        node_labels = r.get("node_labels") or []
        customers.append({
            "customer_id": p.get("id", "Unknown"),
            "name": p.get("name", "Unknown"),
            "segment": p.get("segment", p.get("risk_tier", "Unknown")),
            "risk_score": ctx.get("risk_score", 0.0) or 0.0,
            "credit_score": p.get("credit_score", 0),
            "account_id": a.get("id"),
            "account_type": a.get("type", "Unknown"),
            "utilization_pct": a.get("utilization_pct", 0),
            "credit_limit": a.get("current_limit", a.get("credit_limit", 0)) or 0,
            "labels": node_labels,
        })
    return customers


@app.get("/customers/count")
async def customer_count():
    """Get total customer counts by industry."""
    results = execute_query("""
        MATCH (p) WHERE p:Person OR p:Patient
        RETURN 
            count(p) AS total,
            sum(CASE WHEN p:Patient THEN 1 ELSE 0 END) AS healthcare,
            sum(CASE WHEN p:Person AND (p.id STARTS WITH 'FIN' OR p.id STARTS WITH 'CUST-CLI') THEN 1 ELSE 0 END) AS financial,
            sum(CASE WHEN p:Person AND (p.id STARTS WITH 'AML' OR p.id STARTS WITH 'CUST-AML') THEN 1 ELSE 0 END) AS aml
    """)
    if results:
        r = results[0]
        return {"total": r["total"], "financial": r["financial"], "aml": r["aml"], "healthcare": r["healthcare"]}
    return {"total": 0, "financial": 0, "aml": 0, "healthcare": 0}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "NBA Context Engine",
        "version": "0.1.0",
        "docs": "/docs",
    }
