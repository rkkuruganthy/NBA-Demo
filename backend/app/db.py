from neo4j import GraphDatabase
from contextlib import asynccontextmanager
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Global driver instance
_driver = None


def get_driver():
    """Get or create the Neo4j driver singleton."""
    global _driver
    if _driver is None:
        settings = get_settings()
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
        logger.info(f"Neo4j driver created for {settings.neo4j_uri}")
    return _driver


def close_driver():
    """Close the Neo4j driver."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")


def verify_connectivity():
    """Verify Neo4j connectivity. Returns True if connected."""
    try:
        driver = get_driver()
        driver.verify_connectivity()
        return True
    except Exception as e:
        logger.error(f"Neo4j connectivity check failed: {e}")
        return False


def execute_query(query: str, parameters: dict = None, database: str = "neo4j"):
    """Execute a Cypher query and return results."""
    driver = get_driver()
    with driver.session(database=database) as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def execute_write(query: str, parameters: dict = None, database: str = "neo4j"):
    """Execute a write Cypher query within a transaction."""
    driver = get_driver()
    with driver.session(database=database) as session:
        result = session.execute_write(
            lambda tx: list(tx.run(query, parameters or {}))
        )
        return [record.data() for record in result]
