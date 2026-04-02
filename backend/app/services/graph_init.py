"""
Graph initialization service.
Loads schema and seed data into Neo4j.
Idempotent — safe to run multiple times.
"""

import os
import logging
from app.db import get_driver

logger = logging.getLogger(__name__)

GRAPH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "graph")


def _read_cypher_file(filename: str) -> list[str]:
    """Read a .cypher file and split into individual statements."""
    filepath = os.path.join(GRAPH_DIR, filename)

    # Also check parent directories for Docker volume mounts
    if not os.path.exists(filepath):
        filepath = os.path.join("/app", "graph", filename)
    if not os.path.exists(filepath):
        # Try relative to project root
        filepath = os.path.join(os.getcwd(), "graph", filename)

    if not os.path.exists(filepath):
        logger.warning(f"Cypher file not found: {filename}")
        return []

    with open(filepath, "r") as f:
        content = f.read()

    # Split by semicolons, filter empty/comment-only statements
    statements = []
    for stmt in content.split(";"):
        cleaned = stmt.strip()
        # Remove comment-only lines
        lines = [l for l in cleaned.split("\n") if l.strip() and not l.strip().startswith("//")]
        if lines:
            statements.append(cleaned)

    return statements


def init_schema():
    """Load graph schema (constraints + indexes)."""
    logger.info("Loading graph schema...")
    statements = _read_cypher_file("schema.cypher")

    driver = get_driver()
    success = 0
    skipped = 0

    with driver.session(database="neo4j") as session:
        for stmt in statements:
            try:
                session.run(stmt)
                success += 1
            except Exception as e:
                if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                    skipped += 1
                else:
                    logger.error(f"Schema error: {e}")

    logger.info(f"Schema loaded: {success} created, {skipped} already existed")
    return {"created": success, "skipped": skipped}


def init_seed_data():
    """Load seed data into graph."""
    logger.info("Loading seed data...")
    statements = _read_cypher_file("seed.cypher")

    driver = get_driver()
    success = 0
    errors = 0

    with driver.session(database="neo4j") as session:
        for stmt in statements:
            try:
                session.run(stmt)
                success += 1
            except Exception as e:
                logger.error(f"Seed data error: {e}")
                errors += 1

    logger.info(f"Seed data loaded: {success} statements, {errors} errors")
    return {"success": success, "errors": errors}


def init_graph():
    """Full graph initialization: schema + seed data."""
    schema_result = init_schema()
    seed_result = init_seed_data()
    return {
        "schema": schema_result,
        "seed_data": seed_result,
    }


def get_graph_stats():
    """Get node/relationship counts from the graph."""
    driver = get_driver()
    with driver.session(database="neo4j") as session:
        # Node counts
        result = session.run("MATCH (n) RETURN labels(n)[0] as label, count(n) as count ORDER BY label")
        nodes = {record["label"]: record["count"] for record in result}

        # Relationship counts
        result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY type")
        rels = {record["type"]: record["count"] for record in result}

    return {"nodes": nodes, "relationships": rels}
