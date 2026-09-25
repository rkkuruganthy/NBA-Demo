import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

with open('graph/seed.cypher', 'r') as f:
    content = f.read()

# Grab the "E-COMMERCE POPULATION SEED" and everything after
header = "// ============================================================\n// E-COMMERCE POPULATION SEED"
if header in content:
    ecom_block = content.split(header)[1]
    
    # Split by semicolon
    statements = [s.strip() for s in ecom_block.split(';')]
    
    with driver.session() as session:
        print("Running historical ECOM cases from seed.cypher...")
        for stmt in statements:
            if stmt and not stmt.startswith('//'):
                try:
                    session.run(stmt)
                except Exception as e:
                    print(f"Error executing statement: {e}")
                    
        print("Done running historical ECOM cases.")
else:
    print("Could not find ECOM block in seed.cypher")
