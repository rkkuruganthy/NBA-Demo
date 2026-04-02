"""
Seed 10K realistic multi-hop users across Financial, AML, and Healthcare industries.
Each user gets a full graph topology (4-7 hops) for real graph-traversal decisioning.
Preserves the 6 Hero profiles as curated demo anchors.
"""

import os
import random
import string
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# --- Distributions ---
FIRST_NAMES = ["James","Mary","Robert","Patricia","John","Jennifer","Michael","Linda","David","Elizabeth",
    "William","Barbara","Richard","Susan","Joseph","Jessica","Thomas","Sarah","Christopher","Karen",
    "Daniel","Lisa","Matthew","Nancy","Anthony","Betty","Mark","Margaret","Donald","Sandra",
    "Steven","Ashley","Andrew","Dorothy","Paul","Kimberly","Joshua","Emily","Kenneth","Donna",
    "Kevin","Michelle","Brian","Carol","George","Amanda","Timothy","Melissa","Ronald","Deborah",
    "Edward","Stephanie","Jason","Rebecca","Jeffrey","Sharon","Ryan","Laura","Jacob","Cynthia",
    "Gary","Kathleen","Nicholas","Amy","Eric","Angela","Jonathan","Shirley","Stephen","Anna",
    "Larry","Brenda","Justin","Pamela","Scott","Emma","Brandon","Nicole","Benjamin","Helen"]
LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts"]
MERCHANTS_TRAVEL = ["Delta Airlines","United Airlines","Marriott","Hilton Hotels","Airbnb","Expedia","Hertz","Southwest"]
MERCHANTS_LUXURY = ["Nordstrom","Saks Fifth Avenue","Tiffany","Louis Vuitton","Apple Store","Tesla"]
MERCHANTS_ESSENTIAL = ["Walmart","Target","Costco","Kroger","CVS Pharmacy","Home Depot","Amazon"]
MERCHANTS_RISKY = ["Local Casino","Draft Kings","PokerStars","Bet365","Cash Advance Co","Payday Loans"]
DEPARTMENTS = ["Primary Care","Cardiology","Endocrinology","Pulmonology","Oncology","Neurology","Orthopedics"]
DIAGNOSES_ROUTINE = [("Z00.00","General Adult Exam"),("Z01.10","Routine ECG"),("Z12.31","Screening Mammogram")]
DIAGNOSES_CHRONIC = [("E11.9","Type 2 Diabetes"),("I10","Essential Hypertension"),("J44.1","COPD with Exacerbation")]
DIAGNOSES_CRITICAL = [("I50.9","Heart Failure, Unspecified"),("I21.9","Acute MI"),("J96.01","Acute Respiratory Failure")]
MEDS_ROUTINE = ["Lisinopril 10mg","Metformin 500mg","Atorvastatin 20mg","Omeprazole 20mg"]
MEDS_CRITICAL = ["Entresto 97/103mg","Eliquis 5mg","Warfarin 5mg","Insulin Glargine"]
JURISDICTIONS_SAFE = ["Domestic","Domestic","Domestic","EU-Regulated","Canada","UK"]
JURISDICTIONS_RISKY = ["Cayman Islands","Panama","Cyprus","Malta","British Virgin Islands"]
OFFSHORE_ENTITIES = ["Cayman Offshore LLC","Panama Holdings SA","Cyprus Investments Ltd","Malta Capital Group","BVI Trust Corp"]
DOMESTIC_ENTITIES = ["Vance Refrigeration","Smith & Co Legal","Johnson Hardware","Local Coffee Shop","City Utilities"]


def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def rand_id(prefix, i):
    return f"{prefix}-{i:05d}"


def seed_all():
    with driver.session() as session:
        print("Wiping all existing data...")
        session.run("MATCH (n) DETACH DELETE n")

        # Create indexes for performance
        print("Creating indexes...")
        for label in ["Person","Patient","Account","Device","Transaction","Entity","Policy","Decision","Context"]:
            try:
                session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.id)")
            except Exception:
                pass

        # ============================================
        # PHASE 1: FINANCIAL USERS (3,500)
        # ============================================
        print("Seeding Financial users (3,500)...")
        fin_users = []

        # Affluent (1,200)
        for i in range(1, 1201):
            fin_users.append({
                "pid": rand_id("FIN", i), "name": rand_name(), "segment": "Affluent",
                "credit_score": random.randint(750, 850),
                "acc_id": rand_id("FACC", i), "acc_type": "Credit Card",
                "limit": random.choice([15000, 20000, 25000, 30000, 50000]),
                "util": round(random.uniform(0.10, 0.60), 2), "dpd": 0,
                "risk": round(random.uniform(0.02, 0.20), 2),
                "months_active": random.randint(24, 120),
                "inquiries": random.randint(0, 2),
                "merchant_pool": "travel_luxury",
            })

        # Mass Market (1,500)
        for i in range(1201, 2701):
            dpd = random.choices([0, 0, 0, 5, 10, 15], weights=[50, 20, 10, 10, 5, 5])[0]
            fin_users.append({
                "pid": rand_id("FIN", i), "name": rand_name(), "segment": "Mass Market",
                "credit_score": random.randint(650, 749),
                "acc_id": rand_id("FACC", i), "acc_type": "Credit Card",
                "limit": random.choice([3000, 5000, 7500, 10000]),
                "util": round(random.uniform(0.40, 0.85), 2), "dpd": dpd,
                "risk": round(random.uniform(0.15, 0.50), 2),
                "months_active": random.randint(6, 48),
                "inquiries": random.randint(0, 4),
                "merchant_pool": "essential",
            })

        # Subprime (800)
        for i in range(2701, 3501):
            fin_users.append({
                "pid": rand_id("FIN", i), "name": rand_name(), "segment": "Subprime",
                "credit_score": random.randint(550, 649),
                "acc_id": rand_id("FACC", i), "acc_type": "Credit Card",
                "limit": random.choice([1000, 2000, 3000, 5000]),
                "util": round(random.uniform(0.80, 0.98), 2),
                "dpd": random.choice([15, 30, 45, 60, 90]),
                "risk": round(random.uniform(0.50, 0.95), 2),
                "months_active": random.randint(3, 24),
                "inquiries": random.randint(3, 8),
                "merchant_pool": "risky",
            })

        # Batch insert financial users
        BATCH = 500
        for start in range(0, len(fin_users), BATCH):
            batch = fin_users[start:start + BATCH]
            session.run("""
                UNWIND $batch AS u
                CREATE (p:Person {id: u.pid, name: u.name, segment: u.segment, credit_score: u.credit_score})
                CREATE (a:Account {id: u.acc_id, type: u.acc_type, current_limit: u.limit,
                                   utilization_pct: u.util, dpd: u.dpd})
                CREATE (ctx:Context {id: u.pid + '-CTX', risk_score: u.risk,
                                     months_active: u.months_active, recent_inquiries: u.inquiries})
                CREATE (p)-[:OWNS]->(a)
                CREATE (p)-[:HAS_CONTEXT]->(ctx)
            """, {"batch": batch})
            print(f"  Financial batch {start}-{start+len(batch)} created")

        # Add transactions & intent markers for financial users
        print("  Adding financial transactions...")
        for u in fin_users:
            pool = u["merchant_pool"]
            if pool == "travel_luxury":
                merchants = random.sample(MERCHANTS_TRAVEL + MERCHANTS_LUXURY, min(3, len(MERCHANTS_TRAVEL)))
                has_intent = True
            elif pool == "essential":
                merchants = random.sample(MERCHANTS_ESSENTIAL, 2)
                has_intent = random.random() < 0.15  # 15% chance of travel intent
                if has_intent:
                    merchants.append(random.choice(MERCHANTS_TRAVEL))
            else:
                merchants = random.sample(MERCHANTS_RISKY + MERCHANTS_ESSENTIAL[:2], 2)
                has_intent = False

            tx_params = []
            for m in merchants:
                tx_params.append({
                    "tx_id": f"TX-{u['pid']}-{m[:3].upper()}",
                    "amount": round(random.uniform(100, u["limit"] * 0.3), 2),
                    "merchant": m,
                    "status": random.choice(["CLEARED", "CLEARED", "PENDING"]),
                })

            session.run("""
                MATCH (a:Account {id: $acc_id})
                UNWIND $txs AS tx
                CREATE (t:Transaction {id: tx.tx_id, amount: tx.amount, merchant: tx.merchant, status: tx.status})
                CREATE (a)-[:MADE_PURCHASE]->(t)
            """, {"acc_id": u["acc_id"], "txs": tx_params})

            if has_intent:
                intent_type = "Travel Indicator" if any(m in MERCHANTS_TRAVEL for m in merchants) else "Luxury Indicator"
                session.run("""
                    MATCH (a:Account {id: $acc_id})-[:MADE_PURCHASE]->(t:Transaction)
                    WITH t LIMIT 1
                    MERGE (e:Entity {type: $intent_type, confidence: $conf})
                    CREATE (t)-[:INDICATES]->(e)
                """, {"acc_id": u["acc_id"], "intent_type": intent_type,
                      "conf": round(random.uniform(0.70, 0.98), 2)})

        # ============================================
        # PHASE 2: AML USERS (3,000)
        # ============================================
        print("Seeding AML users (3,000)...")
        aml_users = []

        # Clean (2,400)
        for i in range(1, 2401):
            aml_users.append({
                "pid": rand_id("AML", i), "name": rand_name(), "segment": "Mass Market",
                "credit_score": random.randint(650, 800),
                "acc_id": rand_id("AACC", i),
                "risk": round(random.uniform(0.01, 0.15), 2),
                "device_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
                "device_type": random.choice(["Desktop", "Mobile", "Tablet"]),
                "wire_amount": round(random.uniform(100, 5000), 2),
                "dest_name": random.choice(DOMESTIC_ENTITIES),
                "dest_jurisdiction": random.choice(JURISDICTIONS_SAFE),
                "is_threat": False,
            })

        # Suspicious (400)
        for i in range(2401, 2801):
            aml_users.append({
                "pid": rand_id("AML", i), "name": rand_name(), "segment": "Mass Market",
                "credit_score": random.randint(600, 720),
                "acc_id": rand_id("AACC", i),
                "risk": round(random.uniform(0.15, 0.50), 2),
                "device_ip": f"192.168.{random.randint(100,110)}.{random.randint(1,50)}",
                "device_type": "Mobile",
                "wire_amount": round(random.uniform(5000, 9999), 2),
                "dest_name": random.choice(OFFSHORE_ENTITIES),
                "dest_jurisdiction": random.choice(JURISDICTIONS_RISKY),
                "is_threat": True,
            })

        # Confirmed Ring (200)
        for i in range(2801, 3001):
            aml_users.append({
                "pid": rand_id("AML", i), "name": rand_name(), "segment": "Mass Market",
                "credit_score": random.randint(550, 650),
                "acc_id": rand_id("AACC", i),
                "risk": round(random.uniform(0.50, 0.95), 2),
                "device_ip": f"192.168.104.{random.randint(1,30)}",
                "device_type": "Mobile",
                "wire_amount": round(random.uniform(8000, 50000), 2),
                "dest_name": random.choice(OFFSHORE_ENTITIES),
                "dest_jurisdiction": random.choice(JURISDICTIONS_RISKY),
                "is_threat": True,
            })

        # Batch insert AML users
        for start in range(0, len(aml_users), BATCH):
            batch = aml_users[start:start + BATCH]
            session.run("""
                UNWIND $batch AS u
                CREATE (p:Person {id: u.pid, name: u.name, segment: u.segment, credit_score: u.credit_score})
                CREATE (a:Account {id: u.acc_id, type: 'Checking', current_limit: 0, utilization_pct: 0, dpd: 0})
                CREATE (ctx:Context {id: u.pid + '-CTX', risk_score: u.risk})
                CREATE (d:Device {id: u.pid + '-DEV', ip: u.device_ip, type: u.device_type})
                CREATE (t:Transaction {id: u.pid + '-WIRE', amount: u.wire_amount, type: 'Wire Transfer', status: 'PENDING'})
                CREATE (dest:Entity {id: u.pid + '-DEST', name: u.dest_name, jurisdiction: u.dest_jurisdiction})
                CREATE (p)-[:OWNS]->(a)
                CREATE (p)-[:HAS_CONTEXT]->(ctx)
                CREATE (p)-[:LOGGED_IN_FROM]->(d)
                CREATE (a)-[:INITIATED]->(t)
                CREATE (t)-[:DESTINATION]->(dest)
            """, {"batch": batch})
            print(f"  AML batch {start}-{start+len(batch)} created")

        # Add Fraudster/Threat nodes for suspicious + confirmed ring users
        print("  Adding fraud threat connections...")
        threat_ips = set()
        for u in aml_users:
            if u["is_threat"]:
                threat_ips.add(u["device_ip"])

        # Create shared Fraudster nodes per IP cluster
        for ip in threat_ips:
            session.run("""
                MATCH (d:Device {ip: $ip})
                MERGE (f:Fraudster:Threat {name: 'Syndicate-' + $ip, risk_level: 'CRITICAL', ip: $ip})
                MERGE (f)-[:LOGGED_IN_FROM]->(d)
            """, {"ip": ip})

        # ============================================
        # PHASE 3: HEALTHCARE USERS (3,500)
        # ============================================
        print("Seeding Healthcare users (3,500)...")
        med_users = []

        # Compliant (2,000)
        for i in range(1, 2001):
            med_users.append({
                "pid": rand_id("MED", i), "name": rand_name(),
                "age": random.randint(25, 75), "risk_tier": "Low",
                "risk": round(random.uniform(0.02, 0.20), 2),
                "enc_type": random.choice(["Annual Physical", "Routine Checkup", "Preventive Screening"]),
                "department": "Primary Care",
                "diag": random.choice(DIAGNOSES_ROUTINE),
                "med": random.choice(MEDS_ROUTINE), "rx_status": "Fulfilled",
                "has_gap": False, "gap_days": 0,
            })

        # At Risk (1,000)
        for i in range(2001, 3001):
            med_users.append({
                "pid": rand_id("MED", i), "name": rand_name(),
                "age": random.randint(45, 80), "risk_tier": "Medium",
                "risk": round(random.uniform(0.30, 0.65), 2),
                "enc_type": random.choice(["Outpatient Visit", "Follow-up", "Lab Review"]),
                "department": random.choice(DEPARTMENTS),
                "diag": random.choice(DIAGNOSES_CHRONIC),
                "med": random.choice(MEDS_ROUTINE + MEDS_CRITICAL),
                "rx_status": random.choice(["Active", "Overdue"]),
                "has_gap": True, "gap_days": random.randint(3, 14),
            })

        # Critical (500)
        for i in range(3001, 3501):
            med_users.append({
                "pid": rand_id("MED", i), "name": rand_name(),
                "age": random.randint(55, 90), "risk_tier": "High",
                "risk": round(random.uniform(0.65, 0.98), 2),
                "enc_type": random.choice(["Inpatient Stay", "ER Visit", "ICU Admission"]),
                "department": random.choice(["Cardiology", "Pulmonology", "Neurology"]),
                "diag": random.choice(DIAGNOSES_CRITICAL),
                "med": random.choice(MEDS_CRITICAL),
                "rx_status": random.choice(["Active", "Missed"]),
                "has_gap": True, "gap_days": random.randint(14, 45),
            })

        # Batch insert healthcare users
        for start in range(0, len(med_users), BATCH):
            batch = med_users[start:start + BATCH]
            # Flatten diagnosis tuples for Neo4j
            for u in batch:
                u["diag_code"] = u["diag"][0]
                u["diag_name"] = u["diag"][1]

            session.run("""
                UNWIND $batch AS u
                CREATE (p:Patient {id: u.pid, name: u.name, age: u.age, risk_tier: u.risk_tier})
                CREATE (ctx:Context {id: u.pid + '-CTX', risk_score: u.risk})
                CREATE (enc:Encounter {id: u.pid + '-ENC', type: u.enc_type, department: u.department})
                CREATE (diag:Diagnosis {id: u.pid + '-DIAG', code: u.diag_code, name: u.diag_name})
                CREATE (rx:Prescription {id: u.pid + '-RX', medication: u.med, status: u.rx_status})
                CREATE (p)-[:HAS_CONTEXT]->(ctx)
                CREATE (p)-[:HAD_ENCOUNTER]->(enc)
                CREATE (enc)-[:RESULTED_IN]->(diag)
                CREATE (diag)-[:TREATMENT_PLAN]->(rx)
            """, {"batch": batch})
            print(f"  Healthcare batch {start}-{start+len(batch)} created")

        # Add care gaps for at-risk and critical patients
        print("  Adding care gaps...")
        gap_users = [u for u in med_users if u["has_gap"]]
        for start in range(0, len(gap_users), BATCH):
            batch = gap_users[start:start + BATCH]
            session.run("""
                UNWIND $batch AS u
                MATCH (rx:Prescription {id: u.pid + '-RX'})
                CREATE (gap:Entity:Threat {id: u.pid + '-GAP', type: 'Missed Fulfillment', duration_days: u.gap_days})
                CREATE (rx)-[:HAS_CARE_GAP]->(gap)
            """, {"batch": batch})

        # ============================================
        # PHASE 4: HERO PROFILES (6 curated anchors)
        # ============================================
        print("Seeding 6 Hero profiles...")

        # Financial Happy Path
        session.run("""
            CREATE (p:Person {id: 'CUST-CLI-HAPPY', name: 'John Carter', segment: 'Affluent', credit_score: 790})
            CREATE (a:Account {id: 'ACC-CLI-H', type: 'Credit Card', current_limit: 15000, utilization_pct: 0.85, dpd: 0})
            CREATE (p)-[:OWNS]->(a)
            CREATE (ctx:Context {id: 'CLI-H-CTX', risk_score: 0.1, recent_inquiries: 1, months_active: 48})
            CREATE (p)-[:HAS_CONTEXT]->(ctx)
            CREATE (t1:Transaction {id: 'TX-CLI-H-1', amount: 4500, merchant: 'Delta Airlines', status: 'CLEARED'})
            CREATE (t2:Transaction {id: 'TX-CLI-H-2', amount: 1200, merchant: 'Marriott Tokyo', status: 'PENDING'})
            CREATE (a)-[:MADE_PURCHASE]->(t1)
            CREATE (a)-[:MADE_PURCHASE]->(t2)
            CREATE (intent:Entity {id: 'CLI-H-INTENT', type: 'Travel Indicator', confidence: 0.95})
            CREATE (t1)-[:INDICATES]->(intent)
            CREATE (t2)-[:INDICATES]->(intent)
        """)

        # Financial Sad Path
        session.run("""
            CREATE (p:Person {id: 'CUST-CLI-SAD', name: 'Sarah Connor', segment: 'Subprime', credit_score: 610})
            CREATE (a:Account {id: 'ACC-CLI-S', type: 'Credit Card', current_limit: 5000, utilization_pct: 0.92, dpd: 15})
            CREATE (p)-[:OWNS]->(a)
            CREATE (ctx:Context {id: 'CLI-S-CTX', risk_score: 0.8, recent_inquiries: 5, months_active: 12})
            CREATE (p)-[:HAS_CONTEXT]->(ctx)
            CREATE (t:Transaction {id: 'TX-CLI-S-1', amount: 800, merchant: 'Local Casino', status: 'CLEARED'})
            CREATE (a)-[:MADE_PURCHASE]->(t)
        """)

        # AML Sad Path
        session.run("""
            CREATE (p:Person {id: 'CUST-AML-SAD', name: 'Alice Smith', segment: 'Mass Market', credit_score: 680})
            CREATE (a:Account {id: 'ACC-AML-S', type: 'Checking', current_limit: 0, utilization_pct: 0, dpd: 0})
            CREATE (p)-[:OWNS]->(a)
            CREATE (ctx:Context {id: 'AML-S-CTX', risk_score: 0.2})
            CREATE (p)-[:HAS_CONTEXT]->(ctx)
            CREATE (dev:Device {id: 'AML-S-DEV', ip: '192.168.104.22', type: 'Mobile'})
            CREATE (p)-[:LOGGED_IN_FROM]->(dev)
            CREATE (bad:Fraudster:Threat {name: 'Known Syndicate Node', risk_level: 'CRITICAL', ip: '192.168.104.22'})
            CREATE (bad)-[:LOGGED_IN_FROM]->(dev)
            CREATE (t:Transaction {id: 'AML-S-WIRE', amount: 9500, type: 'Wire Transfer', status: 'PENDING'})
            CREATE (dest:Entity {id: 'AML-S-DEST', name: 'Cayman Offshore LLC', jurisdiction: 'Cayman Islands'})
            CREATE (a)-[:INITIATED]->(t)
            CREATE (t)-[:DESTINATION]->(dest)
        """)

        # AML Happy Path
        session.run("""
            CREATE (p:Person {id: 'CUST-AML-HAPPY', name: 'Bob Vance', segment: 'Mass Market', credit_score: 720})
            CREATE (a:Account {id: 'ACC-AML-H', type: 'Checking', current_limit: 0, utilization_pct: 0, dpd: 0})
            CREATE (p)-[:OWNS]->(a)
            CREATE (ctx:Context {id: 'AML-H-CTX', risk_score: 0.05})
            CREATE (p)-[:HAS_CONTEXT]->(ctx)
            CREATE (dev:Device {id: 'AML-H-DEV', ip: '10.0.1.5', type: 'Desktop'})
            CREATE (p)-[:LOGGED_IN_FROM]->(dev)
            CREATE (t:Transaction {id: 'AML-H-WIRE', amount: 1500, type: 'Wire Transfer', status: 'PENDING'})
            CREATE (dest:Entity {id: 'AML-H-DEST', name: 'Vance Refrigeration', jurisdiction: 'Domestic'})
            CREATE (a)-[:INITIATED]->(t)
            CREATE (t)-[:DESTINATION]->(dest)
        """)

        # Healthcare Sad Path
        session.run("""
            CREATE (p:Patient {id: 'CUST-MED-SAD', name: 'Robert Jones', age: 68, risk_tier: 'High'})
            CREATE (ctx:Context {id: 'MED-S-CTX', risk_score: 0.88})
            CREATE (p)-[:HAS_CONTEXT]->(ctx)
            CREATE (enc:Encounter {id: 'MED-S-ENC', type: 'Inpatient Stay', department: 'Cardiology', date: '2026-03-01'})
            CREATE (p)-[:HAD_ENCOUNTER]->(enc)
            CREATE (diag:Diagnosis {id: 'MED-S-DIAG', code: 'I50.9', name: 'Heart Failure, Unspecified'})
            CREATE (enc)-[:RESULTED_IN]->(diag)
            CREATE (rx:Prescription {id: 'MED-S-RX', medication: 'Entresto 97/103mg', status: 'Active'})
            CREATE (diag)-[:TREATMENT_PLAN]->(rx)
            CREATE (gap:Entity:Threat {id: 'MED-S-GAP', type: 'Missed Fulfillment', duration_days: 14})
            CREATE (rx)-[:HAS_CARE_GAP]->(gap)
        """)

        # Healthcare Happy Path
        session.run("""
            CREATE (p:Patient {id: 'CUST-MED-HAPPY', name: 'Mary Poppins', age: 52, risk_tier: 'Low'})
            CREATE (ctx:Context {id: 'MED-H-CTX', risk_score: 0.1})
            CREATE (p)-[:HAS_CONTEXT]->(ctx)
            CREATE (enc:Encounter {id: 'MED-H-ENC', type: 'Annual Physical', department: 'Primary Care', date: '2026-03-15'})
            CREATE (p)-[:HAD_ENCOUNTER]->(enc)
            CREATE (diag:Diagnosis {id: 'MED-H-DIAG', code: 'Z00.00', name: 'General Adult Exam'})
            CREATE (enc)-[:RESULTED_IN]->(diag)
            CREATE (rx:Prescription {id: 'MED-H-RX', medication: 'Lisinopril 10mg', status: 'Fulfilled'})
            CREATE (diag)-[:TREATMENT_PLAN]->(rx)
        """)

        # ============================================
        # PHASE 5: POLICIES
        # ============================================
        print("Seeding policies...")
        session.run("""
            CREATE (:Policy {id: 'POL-CLI-01', name: 'Travel Intent CLI Auto-Approve', description: 'Approve CLI if utilization > 80% with Travel Indicator and 0 DPD.', family: 'Credit'})
            CREATE (:Policy {id: 'POL-CLI-02', name: 'Standard Utilization Stop', description: 'Decline CLI if util > 80% without intent markers and DPD > 0.', family: 'Credit'})
            CREATE (:Policy {id: 'POL-CLI-03', name: 'Subprime Hard Decline', description: 'Decline CLI if DPD > 30 days regardless of other factors.', family: 'Credit'})
            CREATE (:Policy {id: 'POL-AML-01', name: 'Shared Identity Device Threat', description: 'Block if device IP is shared with known Fraudster node.', family: 'Fraud'})
            CREATE (:Policy {id: 'POL-AML-02', name: 'High-Risk Jurisdiction Structuring', description: 'Escalate if wire goes to high-risk jurisdiction.', family: 'Fraud'})
            CREATE (:Policy {id: 'POL-AML-03', name: 'Clean Domestic Wire', description: 'Approve domestic wires with no threat indicators.', family: 'Fraud'})
            CREATE (:Policy {id: 'POL-MED-01', name: 'High-Risk Med Non-Adherence', description: 'Trigger Clinical Intervention if care gap > 7 days for critical diagnosis.', family: 'Clinical'})
            CREATE (:Policy {id: 'POL-MED-02', name: 'Chronic Condition Monitoring', description: 'Schedule follow-up if chronic condition with care gap 3-7 days.', family: 'Clinical'})
            CREATE (:Policy {id: 'POL-MED-03', name: 'Compliant Patient Clearance', description: 'Clear patient if prescriptions fulfilled and no care gaps.', family: 'Clinical'})
        """)

        # Verify counts
        print("\n=== Verification ===")
        result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC")
        for r in result:
            print(f"  {r['label']}: {r['cnt']}")

        total = session.run("MATCH (n) RETURN count(n) AS total").single()["total"]
        print(f"\n  TOTAL NODES: {total}")
        print("Seeding complete!")


if __name__ == "__main__":
    seed_all()
