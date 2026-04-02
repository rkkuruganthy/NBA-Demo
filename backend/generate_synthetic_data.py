import os
import json
import random
from faker import Faker
from neo4j import GraphDatabase

# Initialize Faker
fake = Faker()

# Neo4j connection
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def generate_customers(num_records=1000):
    customers = []
    segments = ['Mass Market', 'Standard', 'Affluent', 'High Net Worth']
    
    for _ in range(num_records):
        # Determine Segment
        segment_choice = random.choices(segments, weights=[40, 30, 20, 10])[0]
        
        # Credit Score Generation (Bell curve around 680, bounded 300-850)
        base_score = int(random.gauss(680, 80))
        credit_score = max(300, min(850, base_score))
        
        # Adjust income based on segment
        if segment_choice == 'High Net Worth':
            income = random.randint(250000, 1000000)
            credit_score = max(700, credit_score)
        elif segment_choice == 'Affluent':
            income = random.randint(120000, 250000)
        elif segment_choice == 'Standard':
            income = random.randint(60000, 120000)
        else:
            income = random.randint(30000, 60000)
            
        # Behavior Profile (Risk)
        # Utilization (0 to 1.0)
        utilization = round(random.uniform(0, 1), 2)
        
        # Hard inquiries in last 6 months
        hard_inquiries = max(0, int(random.gauss(1, 2)))
        
        # Days Past Due
        dpd_choices = [0, 30, 60, 90]
        dpd = random.choices(dpd_choices, weights=[85, 10, 3, 2])[0]
        
        # Tenure
        months_active = random.randint(1, 120)
        
        # Debt to income ratio (0.1 to 0.7)
        dti = round(random.uniform(0.1, 0.7), 2)
        
        # Credit limits related to segment
        current_limit = random.randint(1000, 5000) * (segments.index(segment_choice) + 1)
        requested_limit_increase = random.randint(500, 10000)

        customer = {
            "customer_id": fake.uuid4(),
            "name": fake.name(),
            "segment": segment_choice,
            "annual_income": income,
            "credit_score": credit_score,
            "months_active": months_active,
            "dti": dti,
            "hard_inquiries_6m": hard_inquiries
        }
        
        account = {
            "account_id": fake.uuid4(),
            "account_type": "Credit Card",
            "current_limit": current_limit,
            "requested_cli": requested_limit_increase,
            "utilization_pct": utilization,
            "dpd": dpd
        }

        customers.append({"customer": customer, "account": account})
        
    return customers

def seed_database(customers):
    print(f"Seeding {len(customers)} records to Neo4j...")
    
    with driver.session() as session:
        # Clear existing non-policy nodes (leaving policies if they exist, or clear all and reseed)
        print("Clearing existing generic data...")
        session.run("MATCH (n:Person) DETACH DELETE n")
        session.run("MATCH (n:Account) DETACH DELETE n")
        session.run("MATCH (n:Context) DETACH DELETE n")
        session.run("MATCH (n:Decision) DETACH DELETE n")
        # Ensure rules/policies exist
        create_policies = """
        MERGE (p1:Policy {id: 'POL-001'}) SET p1.name = 'High Risk Decline', p1.description = 'Decline if Risk Score > 0.7', p1.severity = 'HIGH'
        MERGE (p2:Policy {id: 'POL-002'}) SET p2.name = 'Delinquency Hard Stop', p2.description = 'Decline if DPD > 30', p2.severity = 'HIGH'
        MERGE (p3:Policy {id: 'POL-003'}) SET p3.name = 'Premium Segmentation', p3.description = 'Auto-Approve for Premium > 0.8 Score', p3.severity = 'LOW'
        MERGE (p4:Policy {id: 'POL-004'}) SET p4.name = 'High Debt to Income', p4.description = 'Escalate if DTI > 0.5', p4.severity = 'MEDIUM'
        """
        session.run(create_policies)
        
        # Batch insert customers
        # For performance, we'll do an UNWIND
        cypher_query = """
        UNWIND $batch AS record
        
        // Create Customer
        CREATE (c:Person {
            id: record.customer.customer_id,
            name: record.customer.name,
            segment: record.customer.segment,
            credit_score: record.customer.credit_score,
            annual_income: record.customer.annual_income,
            months_active: record.customer.months_active,
            dti: record.customer.dti,
            hard_inquiries_6m: record.customer.hard_inquiries_6m
        })
        
        // Create Account
        CREATE (a:Account {
            id: record.account.account_id,
            type: record.account.account_type,
            current_limit: record.account.current_limit,
            requested_cli: record.account.requested_cli,
            utilization_pct: record.account.utilization_pct,
            dpd: record.account.dpd
        })
        
        // Create Risk Context Snapshot
        CREATE (ctx:Context {
            id: 'CTX-' + record.customer.customer_id,
            timestamp: datetime(),
            risk_score: CASE 
                WHEN record.account.dpd > 0 THEN 0.9 
                WHEN record.customer.dti > 0.5 THEN 0.7
                WHEN record.customer.credit_score < 600 THEN 0.8
                ELSE 0.2 END
        })
        
        // Merge Relationships
        CREATE (c)-[:OWNS]->(a)
        CREATE (c)-[:HAS_CONTEXT]->(ctx)
        """
        
        # Run in batches of 100
        batch_size = 100
        for i in range(0, len(customers), batch_size):
            batch = customers[i:i+batch_size]
            session.run(cypher_query, batch=batch)
            print(f"Inserted batch {i//batch_size + 1}")
            
    print("Database seeding complete!")

if __name__ == "__main__":
    fake_data = generate_customers(1000)
    seed_database(fake_data)
    driver.close()
