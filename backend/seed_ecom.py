import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

with open('graph/seed.cypher', 'r') as f:
    content = f.read()

header = "// ============================================================\n// E-COMMERCE POPULATION SEED"
ecom_block = content.split(header)[1]
statements = [s.strip() for s in ecom_block.split(';')]

with driver.session() as session:
    for i, stmt in enumerate(statements):
        clean_lines = [line for line in stmt.split('\n') if not line.strip().startswith('//')]
        clean_stmt = '\n'.join(clean_lines).strip()
        if clean_stmt:
            try:
                res = session.run(clean_stmt)
                info = res.consume().counters
                print(f"Stmt {i} -> Nodes created: {info.nodes_created}, Rels: {info.relationships_created}")
            except Exception as e:
                print(f"Stmt {i} failed: {e}")
driver.close()
