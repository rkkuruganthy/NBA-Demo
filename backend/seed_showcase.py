import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def seed_showcase_graphs():
    with driver.session() as session:
        print("Wiping all existing data...")
        session.run("MATCH (n) DETACH DELETE n")

        print("Seeding Showcase Graph 1: Financial CLI (Decisioning)")
        cli_cypher = """
        // 1. Core Profile (Happy Path)
        CREATE (p:Person {id: 'CUST-CLI-HAPPY', name: 'John Carter', segment: 'Affluent', credit_score: 790})
        CREATE (a:Account {id: 'ACC-CLI-H', type: 'Credit Card', current_limit: 15000, utilization_pct: 0.85, dpd: 0})
        CREATE (p)-[:OWNS]->(a)
        
        // 2. Temporal Context
        CREATE (ctx:Context {risk_score: 0.1, recent_inquiries: 1, months_active: 48, timestamp: datetime()})
        CREATE (p)-[:HAS_CONTEXT]->(ctx)
        
        // 3. Transactions & Intent
        CREATE (t1:Transaction {amount: 4500, merchant: 'Delta Airlines', status: 'CLEARED'})
        CREATE (t2:Transaction {amount: 1200, merchant: 'Marriott Tokyo', status: 'PENDING'})
        CREATE (a)-[:MADE_PURCHASE]->(t1)
        CREATE (a)-[:MADE_PURCHASE]->(t2)
        CREATE (intent:Entity {type: 'Travel Indicator', confidence: 0.95})
        CREATE (t1)-[:INDICATES]->(intent)
        CREATE (t2)-[:INDICATES]->(intent)

        // 4. Sad Path Profile
        CREATE (p2:Person {id: 'CUST-CLI-SAD', name: 'Sarah Connor', segment: 'Mass Market', credit_score: 610})
        CREATE (a2:Account {id: 'ACC-CLI-S', type: 'Credit Card', current_limit: 5000, utilization_pct: 0.92, dpd: 15})
        CREATE (p2)-[:OWNS]->(a2)
        CREATE (ctx2:Context {risk_score: 0.8, recent_inquiries: 5, months_active: 12, timestamp: datetime()})
        CREATE (p2)-[:HAS_CONTEXT]->(ctx2)
        CREATE (t3:Transaction {amount: 800, merchant: 'Local Casino', status: 'CLEARED'})
        CREATE (a2)-[:MADE_PURCHASE]->(t3)
        """
        session.run(cli_cypher)

        print("Seeding Showcase Graph 2: AML Fraud Ring (Security)")
        aml_cypher = """
        // 1. The Seemingly Clean Profile (Sad Path)
        CREATE (p:Person {id: 'CUST-AML-SAD', name: 'Alice Smith', segment: 'Mass Market', credit_score: 680})
        CREATE (a:Account {id: 'ACC-AML-S', type: 'Checking', current_limit: 0, utilization_pct: 0, dpd: 0})
        CREATE (p)-[:OWNS]->(a)
        CREATE (ctx:Context {risk_score: 0.2, timestamp: datetime()})
        CREATE (p)-[:HAS_CONTEXT]->(ctx)

        // 2. The Hidden Threat Path
        CREATE (dev:Device {ip: '192.168.104.22', type: 'Mobile', last_seen: datetime()})
        CREATE (p)-[:LOGGED_IN_FROM]->(dev)
        
        CREATE (bad:Fraudster:Threat {name: 'Known Syndicate Node', risk_level: 'CRITICAL'})
        CREATE (bad)-[:LOGGED_IN_FROM]->(dev)
        
        // 3. The Suspicious Action
        CREATE (t:Transaction {amount: 9500, type: 'Wire Transfer', status: 'PENDING'})
        CREATE (dest:Entity {name: 'Cayman Offshore LLC', jurisdiction: 'High Risk'})
        CREATE (a)-[:INITIATED]->(t)
        CREATE (t)-[:DESTINATION]->(dest)

        // 4. Happy Path Profile
        CREATE (p2:Person {id: 'CUST-AML-HAPPY', name: 'Bob Vance', segment: 'Mass Market', credit_score: 720})
        CREATE (a2:Account {id: 'ACC-AML-H', type: 'Checking', current_limit: 0, utilization_pct: 0, dpd: 0})
        CREATE (p2)-[:OWNS]->(a2)
        CREATE (ctx2:Context {risk_score: 0.05, timestamp: datetime()})
        CREATE (p2)-[:HAS_CONTEXT]->(ctx2)
        CREATE (dev2:Device {ip: '10.0.1.5', type: 'Desktop', last_seen: datetime()})
        CREATE (p2)-[:LOGGED_IN_FROM]->(dev2)
        CREATE (t2:Transaction {amount: 1500, type: 'Wire Transfer', status: 'PENDING'})
        CREATE (dest2:Entity {name: 'Vance Refrigeration', jurisdiction: 'Domestic'})
        CREATE (a2)-[:INITIATED]->(t2)
        CREATE (t2)-[:DESTINATION]->(dest2)
        """
        session.run(aml_cypher)

        print("Seeding Showcase Graph 3: Clinical Care Gap (Healthcare)")
        med_cypher = """
        // 1. The Patient Profile (Sad Path)
        CREATE (p:Patient {id: 'CUST-MED-SAD', name: 'Robert Jones', age: 68, risk_tier: 'High'})
        CREATE (ctx:Context {risk_score: 0.88, timestamp: datetime()})
        CREATE (p)-[:HAS_CONTEXT]->(ctx)
        
        // 2. The Clinical Journey
        CREATE (enc:Encounter {type: 'Inpatient Stay', department: 'Cardiology', date: '2026-03-01'})
        CREATE (p)-[:HAD_ENCOUNTER]->(enc)
        
        CREATE (diag:Diagnosis {code: 'I50.9', name: 'Heart Failure, Unspecified'})
        CREATE (enc)-[:RESULTED_IN]->(diag)
        
        CREATE (rx:Prescription {medication: 'Entresto 97/103mg', status: 'Active'})
        CREATE (diag)-[:TREATMENT_PLAN]->(rx)
        
        // 3. The Care Gap (The trigger)
        CREATE (gap:Entity:Threat {type: 'Missed Fulfillment', duration_days: 14})
        CREATE (rx)-[:HAS_CARE_GAP]->(gap)

        // 4. Happy Path Profile
        CREATE (p2:Patient {id: 'CUST-MED-HAPPY', name: 'Mary Poppins', age: 52, risk_tier: 'Low'})
        CREATE (ctx2:Context {risk_score: 0.1, timestamp: datetime()})
        CREATE (p2)-[:HAS_CONTEXT]->(ctx2)
        CREATE (enc2:Encounter {type: 'Annual Physical', department: 'Primary Care', date: '2026-03-15'})
        CREATE (p2)-[:HAD_ENCOUNTER]->(enc2)
        CREATE (diag2:Diagnosis {code: 'Z00.00', name: 'General Adult Exam'})
        CREATE (enc2)-[:RESULTED_IN]->(diag2)
        CREATE (rx2:Prescription {medication: 'Lisinopril 10mg', status: 'Fulfilled'})
        CREATE (diag2)-[:TREATMENT_PLAN]->(rx2)
        """
        session.run(med_cypher)

        print("Seeding Showcase Graph 4: Auto E-Commerce (MarTech)")
        ecom_cypher = """
        // 1. E-Commerce Anonymous Browser (Sad Path - High Intent)
        CREATE (dev1:Device {id: 'DEV-ECOM-SAD', ip: '192.168.1.10', type: 'Mobile', last_seen: datetime()})
        CREATE (sess1:Session {id: 'SESS-ECOM-SAD', is_authenticated: false})
        CREATE (p1:Person {id: 'CUST-ECOM-SAD', name: 'Anonymous', segment: 'Mass Market'})
        CREATE (dev1)-[:INITIATED]->(sess1)
        CREATE (p1)-[:LOGGED_IN_FROM]->(dev1)
        CREATE (v1:BrowsedVehicle {vin: 'VIN-SAD-01', make: 'Sedan', price: 28000, model_year: 2026})
        CREATE (sess1)-[:VIEWED {timestamp: datetime()}]->(v1)
        CREATE (sess1)-[:VIEWED {timestamp: datetime()}]->(v1)
        CREATE (sess1)-[:VIEWED {timestamp: datetime()}]->(v1)
        CREATE (sess1)-[:VIEWED {timestamp: datetime()}]->(v1)
        CREATE (calc:FinancingCalculator {id: 'CALC-SAD-01', term_months: 72, estimated_apr: 4.5})
        CREATE (sess1)-[:ENGAGED_WITH]->(calc)
        
        // COMPLEX VECTORS FOR CUST-ECOM-SAD
        // Vector 1: Trade-in Equity (Capability)
        CREATE (old_car:OwnedVehicle {vin: 'VIN-OLD-99', make: 'Compact', model_year: 2018})
        CREATE (val:Valuation {amount: 6500, source: 'KBB', date: datetime()})
        CREATE (p1)-[:OWNS]->(old_car)
        CREATE (old_car)-[:VALUED_AT]->(val)
        
        // Vector 2: Dynamic Supply / Scarcity (FOMO)
        CREATE (dealership:Dealership {id: 'DLR-01', name: 'Downtown Auto Mall', zipcode: '78701'})
        CREATE (v1)-[:LOCATED_AT {stock: 2}]->(dealership)
        
        // Vector 3: Omnichannel Attribution (Physical bridging)
        CREATE (visit:PhysicalVisit {date: 'Yesterday', duration_minutes: 45})
        CREATE (p1)-[:TOOK_TEST_DRIVE]->(visit)
        CREATE (visit)-[:TESTED]->(v1)

        // 2. E-Commerce Buyer (Happy Path - Converted Sale)
        CREATE (dev2:Device {id: 'DEV-ECOM-HAPPY', ip: '10.0.5.22', type: 'Desktop', last_seen: datetime()})
        CREATE (sess2:Session {id: 'SESS-ECOM-HAPPY', is_authenticated: false})
        CREATE (p2:Person {id: 'CUST-ECOM-HAPPY', name: 'Anonymous', segment: 'Affluent'})
        CREATE (p2)-[:LOGGED_IN_FROM]->(dev2)
        CREATE (dev2)-[:INITIATED]->(sess2)
        CREATE (v2:BrowsedVehicle {vin: 'VIN-HAPPY-01', make: 'Luxury SUV', price: 75000, model_year: 2026})
        CREATE (sess2)-[:VIEWED {timestamp: datetime()}]->(v2)
        CREATE (sess2)-[:PURCHASED {amount: 75000, method: 'Cash', date: datetime()}]->(v2)
        
        // Vector 4: Collaborative Filtering (Lookalikes)
        CREATE (p1)-[:LOOKALIKE_OF {score: 0.92}]->(p2)
        """
        session.run(ecom_cypher)

        print("Seeding Multi-Industry Policies...")
        policy_cypher = """
        // Financial Policies
        CREATE (:Policy {id: 'POL-CLI-01', name: 'Travel Intent CLI Auto-Approve', description: 'Approve CLI if utilization > 80% with Travel Indicator and 0 DPD.', family: 'Credit'})
        CREATE (:Policy {id: 'POL-CLI-02', name: 'Standard Utilization Stop', description: 'Decline CLI if util > 80% without intent markers.', family: 'Credit'})
        
        // AML Policies
        CREATE (:Policy {id: 'POL-AML-01', name: 'Shared Identity Device Threat', description: 'Immediate block if device IP is shared with known Fraudster node.', family: 'Fraud'})
        CREATE (:Policy {id: 'POL-AML-02', name: 'High-Risk Jurisdiction Structuring', description: 'Escalate if wire transfer <10k goes to High Risk entity.', family: 'Fraud'})
        
        // Healthcare Policies
        CREATE (:Policy {id: 'POL-MED-01', name: 'High-Risk Med Non-Adherence', description: 'Trigger Clinical Intervention if Heart Failure medication gap > 7 days.', family: 'Clinical'})

        // MarTech E-Commerce Policies
        CREATE (:Policy {id: 'POL-MAR-01', name: 'High-Intent Financed Abandonment', description: 'Trigger proactive SMS rate lock if user views vehicle 4+ times and checks 72-month financing.', family: 'MarTech'})
        CREATE (:Policy {id: 'POL-MAR-02', name: 'Trade-In Equity Leverage', description: 'Trigger positive equity voucher if Valuation > $5k and user is abandoning.', family: 'MarTech'})
        CREATE (:Policy {id: 'POL-MAR-03', name: 'Dynamic Scarcity Alert', description: 'Trigger urgency notification if local dealership stock is < 3.', family: 'MarTech'})
        CREATE (:Policy {id: 'POL-MAR-04', name: 'Omnichannel Accelerator', description: 'Provide VIP showroom invite if user test-drove recently but did not purchase.', family: 'MarTech'})
        """
        session.run(policy_cypher)

        print("Showcase Seeding Complete!")

if __name__ == "__main__":
    seed_showcase_graphs()
