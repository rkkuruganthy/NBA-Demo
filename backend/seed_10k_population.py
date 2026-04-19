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

        # Healthcare Sad Path (High-Risk Escalation) — Robert Jones
        session.run("""
            MERGE (p:Patient {id: 'CUST-MED-SAD', name: 'Robert Jones', age: 68, risk_tier: 'High'})
            MERGE (ctx:Context {id: 'MED-S-CTX', risk_score: 0.88, sdoh_food_desert: true, sdoh_transportation_risk: 'high', zip_code: '90001'})
            MERGE (p)-[:HAS_CONTEXT]->(ctx)
            
            // IoT Device Data
            MERGE (dev:Device {id: 'DEV-CPAP-RJ', type: 'Medical', name: 'ResMed CPAP'})
            MERGE (p)-[:OWNS_DEVICE]->(dev)
            MERGE (tel:Telemetry {id: 'TEL-RJ-01', metric: 'Adherence', value: '42%', status: 'Non-Compliant'})
            MERGE (dev)-[:RECORDED]->(tel)
            
            // Omnichannel Intent (Patient Portal)
            MERGE (sess:Session {id: 'SESS-MED-RJ', platform: 'Patient Portal', date: '2026-04-18'})
            MERGE (symp:SymptomSearch {id: 'SYMP-RJ-01', term: 'shortness of breath worsening'})
            MERGE (p)-[:INITIATED_SESSION]->(sess)
            MERGE (sess)-[:SEARCHED_SYMPTOM]->(symp)
            
            // Clinical Pipeline
            MERGE (enc:Encounter {id: 'MED-S-ENC', type: 'Inpatient Stay', department: 'Cardiology', date: '2026-03-01'})
            MERGE (p)-[:HAD_ENCOUNTER]->(enc)
            MERGE (diag:Diagnosis {id: 'MED-S-DIAG', code: 'I50.9', name: 'Heart Failure, Unspecified'})
            MERGE (enc)-[:RESULTED_IN]->(diag)
            MERGE (rx:Prescription {id: 'MED-S-RX', medication: 'Entresto 97/103mg', status: 'Unfulfilled'})
            MERGE (diag)-[:TREATMENT_PLAN]->(rx)
            MERGE (gap:CareGap:Threat {id: 'MED-S-GAP', type: 'Missed Cardiology Rx', duration_days: 14})
            MERGE (rx)-[:HAS_CARE_GAP]->(gap)
        """)

        # Healthcare Happy Path (Cleared / Compliant) — Mary Poppins
        session.run("""
            MERGE (p:Patient {id: 'CUST-MED-HAPPY', name: 'Mary Poppins', age: 52, risk_tier: 'Low'})
            MERGE (ctx:Context {id: 'MED-H-CTX', risk_score: 0.1, sdoh_food_desert: false, zip_code: '90210'})
            MERGE (p)-[:HAS_CONTEXT]->(ctx)
            
            // IoT Device Data
            MERGE (dev:Device {id: 'DEV-WATCH-MP', type: 'Wearable', name: 'Apple Watch Series 9'})
            MERGE (p)-[:OWNS_DEVICE]->(dev)
            MERGE (tel:Telemetry {id: 'TEL-MP-01', metric: 'ECG', value: 'Normal Sinus Rhythm', status: 'Healthy'})
            MERGE (dev)-[:RECORDED]->(tel)
            
            // Clinical Pipeline & Pharmacy Node
            MERGE (enc:Encounter {id: 'MED-H-ENC', type: 'Annual Physical', department: 'Primary Care', date: '2026-03-15'})
            MERGE (p)-[:HAD_ENCOUNTER]->(enc)
            MERGE (diag:Diagnosis {id: 'MED-H-DIAG', code: 'Z00.00', name: 'General Adult Exam'})
            MERGE (enc)-[:RESULTED_IN]->(diag)
            MERGE (rx:Prescription {id: 'MED-H-RX', medication: 'Lisinopril 10mg', status: 'Active'})
            MERGE (diag)-[:TREATMENT_PLAN]->(rx)
            
            MERGE (pharm:Pharmacy {id: 'PHARM-CVS-01', name: 'CVS Pharmacy #412'})
            MERGE (rx)-[:FULFILLED_AT {date: '2026-03-16'}]->(pharm)
        """)


        # E-Commerce Sad Path (High Intent Abandonment) — Robert Vance
        # Full omnichannel graph: Person → Session → Device → BrowsedVehicle → Calculator → PhysicalVisit → Dealership
        session.run("""
            MERGE (pe2:Person {id: 'CUST-ECOM-SAD', name: 'Robert Vance', segment: 'premium',
              risk_score: 0.1, churn_risk: 0.8, customer_value: 55000,
              credit_score: 790, months_active: 48, email: 'robert.vance@example.com'})

            MERGE (ctx_ecom:Context {id: 'CTX-ECOM-01', risk_score: 0.1, months_active: 48, inquiries: 0})
            MERGE (pe2)-[:HAS_CONTEXT]->(ctx_ecom)

            MERGE (v1:BrowsedVehicle {vin: 'VIN-A4-001', make: 'Audi', model: 'A4', year: 2026, price: 42000})
            MERGE (v2:BrowsedVehicle {vin: 'VIN-Q5-002', make: 'Audi', model: 'Q5', year: 2026, price: 55000})

            MERGE (dlr1:Dealership {id: 'DLR-NY-01', name: 'Central Audi Manhattan', location: 'New York, NY'})
            MERGE (v1)-[:LOCATED_AT {stock: 2}]->(dlr1)
            MERGE (v2)-[:LOCATED_AT {stock: 5}]->(dlr1)

            MERGE (sess1:Session {id: 'SESS-ECOM-SAD', is_authenticated: true, start_time: datetime('2026-04-14T14:00:00Z')})
            MERGE (pe2)-[:INITIATED_SESSION]->(sess1)
            MERGE (sess1)-[:VIEWED {count: 4, duration_sec: 1200}]->(v1)

            MERGE (dev1:Device {id: 'DEV-IPHONE-15', type: 'Mobile', os: 'iOS'})
            MERGE (pe2)-[:LOGGED_IN_FROM]->(dev1)
            MERGE (dev1)-[:INITIATED]->(sess1)

            MERGE (calc1:FinancingCalculator {id: 'CALC-72MO', term_months: 72, interest_rate: 4.99})
            MERGE (sess1)-[:ENGAGED_WITH]->(calc1)

            MERGE (visit1:PhysicalVisit {id: 'VISIT-NY-001', date: datetime('2026-04-14T15:30:00Z'), duration_min: 90, activity: 'Test Drive'})
            MERGE (pe2)-[:TOOK_TEST_DRIVE]->(visit1)
            MERGE (visit1)-[:AT_LOCATION]->(dlr1)
        """)

        # E-Commerce Happy Path (Low Intent / Purchased) — John Miller
        session.run("""
            MERGE (pe1:Person {id: 'CUST-ECOM-HAPPY', name: 'John Miller', segment: 'standard',
              risk_score: 0.2, churn_risk: 0.1, customer_value: 32000,
              credit_score: 720, months_active: 24, email: 'john.m@example.com'})
            MERGE (sess2:Session {id: 'SESS-ECOM-HAPPY', is_authenticated: true})
            MERGE (pe1)-[:INITIATED_SESSION]->(sess2)
            MERGE (v2:BrowsedVehicle {vin: 'VIN-Q5-002', make: 'Audi', model: 'Q5', year: 2026, price: 55000})
            MERGE (sess2)-[:VIEWED]->(v2)
            MERGE (sess2)-[:PURCHASED {date: datetime('2026-04-10T11:00:00Z')}]->(v2)
        """)

        # ============================================
        # PHASE 5: E-COMMERCE USERS (2,000)
        # ============================================
        print("Seeding E-Commerce visitors (2,000)...")
        ecom_users = []
        for i in range(1, 2001):
            views = random.choice([1, 1, 2, 3, 4, 5, 6])
            engaged_calc = random.random() < (0.2 * views)
            make = random.choice(['Sedan', 'SUV', 'Truck', 'Coupe'])
            price = random.randint(22000, 85000)
            ecom_users.append({
                "pid": rand_id("ECOM", i),
                "dev_id": rand_id("EDEV", i),
                "sess_id": rand_id("ESESS", i),
                "vin": rand_id("EVIN", i),
                "make": make,
                "price": price,
                "views": views,
                "engaged_calc": engaged_calc,
                "term": random.choice([36, 48, 60, 72]) if engaged_calc else None
            })
        
        for start in range(0, len(ecom_users), BATCH):
            batch = ecom_users[start:start + BATCH]
            session.run("""
                UNWIND $batch AS u
                CREATE (p:Person {id: u.pid, name: 'Anonymous', segment: 'Unknown'})
                CREATE (dev:Device {id: u.dev_id, type: 'Mobile'})
                CREATE (sess:Session {id: u.sess_id, is_authenticated: false})
                CREATE (dev)-[:INITIATED]->(sess)
                CREATE (v:BrowsedVehicle {vin: u.vin, make: u.make, price: u.price, model_year: 2026})
                WITH u, sess, v
                UNWIND range(1, u.views) AS view_idx
                CREATE (sess)-[:VIEWED]->(v)
            """, {"batch": batch})
            
            calc_batch = [u for u in batch if u["engaged_calc"]]
            if calc_batch:
                session.run("""
                    UNWIND $batch AS u
                    MATCH (sess:Session {id: u.sess_id})
                    CREATE (calc:FinancingCalculator {id: u.sess_id + '-CALC', term_months: u.term, estimated_apr: 4.5})
                    CREATE (sess)-[:ENGAGED_WITH]->(calc)
                """, {"batch": calc_batch})
            print(f"  E-commerce batch {start}-{start+len(batch)} created")

        # ============================================
        # PHASE 6: POLICIES
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
            CREATE (:Policy {id: 'POL-MAR-01', name: 'High-Intent Financed Abandonment', description: 'Trigger proactive SMS rate lock if user views vehicle 4+ times and checks 72-month financing.', family: 'MarTech'})
        """)

        # ============================================
        # PHASE 7: HISTORICAL E-COMMERCE COHORTS (Precedents)
        # ============================================
        print("Seeding historical ECOM cohorts from seed.cypher...")
        try:
            with open('graph/seed.cypher', 'r') as f:
                content = f.read()
            header = "// ============================================================\n// E-COMMERCE POPULATION SEED"
            if header in content:
                ecom_block = content.split(header)[1]
                statements = [s.strip() for s in ecom_block.split(';')]
                success_count = 0
                for stmt in statements:
                    if not stmt: continue
                    clean_lines = [line for line in stmt.split('\n') if not line.strip().startswith('//')]
                    clean_stmt = '\n'.join(clean_lines).strip()
                    if clean_stmt:
                        try:
                            # Use consume() to execute fully and catch errors without aborting loop
                            session.run(clean_stmt).consume()
                            success_count += 1
                        except Exception as e:
                            # Ignored (typically "Node already exists" from duplicate Policies)
                            pass
                print(f"Successfully loaded {success_count} historical ECOM cohort blocks.")
            else:
                print("Could not locate ECOM cohort block in seed.cypher.")
        except Exception as e:
            print(f"Failed to load historical ECOM cohorts file: {e}")

        # ============================================
        # PHASE 8: HISTORICAL HEALTHCARE COHORTS
        # ============================================
        print("Seeding historical Healthcare cohorts...")
        
        # 1. 5 High-Risk Escalations (POL-MED-01)
        session.run("""
            UNWIND range(1, 5) AS i
            MERGE (pol:Policy {id: 'POL-MED-01'})
            MERGE (p:Patient {id: 'CUST-MED-HI-' + toString(i), name: 'HighRisk Patient ' + toString(i), age: 60+i, risk_tier: 'High'})
            
            MERGE (ctx:Context {id: 'CTX-MED-HI-' + toString(i), risk_score: 0.8 + (i*0.02), sdoh_transportation_risk: 'high'})
            MERGE (p)-[:HAS_CONTEXT]->(ctx)
            
            MERGE (dev:Device {id: 'DEV-CPAP-HI-' + toString(i), type: 'Medical'})
            MERGE (tel:Telemetry {id: 'TEL-HI-' + toString(i), metric: 'Adherence', value: toString(30 + i*5) + '%', status: 'Non-Compliant'})
            MERGE (p)-[:OWNS_DEVICE]->(dev)
            MERGE (dev)-[:RECORDED]->(tel)
            
            MERGE (sess:Session {id: 'SESS-HI-' + toString(i), platform: 'Patient Portal'})
            MERGE (symp:SymptomSearch {id: 'SYMP-HI-' + toString(i), term: 'chest pain'})
            MERGE (p)-[:INITIATED_SESSION]->(sess)
            MERGE (sess)-[:SEARCHED_SYMPTOM]->(symp)
            
            MERGE (dc:Decision {id: 'DEC-MED-HI-' + toString(i), action: 'TRIGGER_CLINICAL_INTERVENTION', 
                               confidence: 0.95, status: 'COMPLETED', 
                               outcome: CASE WHEN i < 4 THEN 'AVOIDED_ER' ELSE 'ADMITTED_TO_ER' END,
                               created_at: datetime('2026-04-01T08:00:00Z'), decision_type: 'CARE_GAP_REVIEW'})
            MERGE (dx:DecisionContext {id: 'DCX-MED-HI-' + toString(i), trigger_event: 'CARE_GAP_REVIEW', 
                                      risk_at_time: 0.8 + (i*0.02), notes: 'Intervened due to missing Rx and chest pain search'})
            
            MERGE (dc)-[:HAS_CONTEXT]->(dx)
            MERGE (dc)-[:ABOUT]->(p)
            MERGE (dc)-[:APPLIED_POLICY]->(pol)
        """)

        # 2. 5 Chronic Monitoring Calls (POL-MED-02)
        session.run("""
            UNWIND range(1, 5) AS i
            MERGE (pol:Policy {id: 'POL-MED-02'})
            MERGE (p:Patient {id: 'CUST-MED-CH-' + toString(i), name: 'Chronic Patient ' + toString(i), age: 50+i, risk_tier: 'Medium'})
            
            MERGE (ctx:Context {id: 'CTX-MED-CH-' + toString(i), risk_score: 0.5 + (i*0.02)})
            MERGE (p)-[:HAS_CONTEXT]->(ctx)
            
            MERGE (dev:Device {id: 'DEV-WATCH-CH-' + toString(i), type: 'Wearable'})
            MERGE (tel:Telemetry {id: 'TEL-CH-' + toString(i), metric: 'HRV', status: 'Irregular'})
            MERGE (p)-[:OWNS_DEVICE]->(dev)
            MERGE (dev)-[:RECORDED]->(tel)
            
            MERGE (gap:CareGap:Threat {id: 'MED-CH-GAP-' + toString(i), type: 'Missing Lab Results', duration_days: 5})
            MERGE (p)-[:HAS_CARE_GAP]->(gap)
            
            MERGE (dc:Decision {id: 'DEC-MED-CH-' + toString(i), action: 'SCHEDULE_FOLLOW_UP', 
                               confidence: 0.85, status: 'COMPLETED', outcome: 'ADHERENT',
                               created_at: datetime('2026-04-10T11:00:00Z'), decision_type: 'CARE_GAP_REVIEW'})
            MERGE (dx:DecisionContext {id: 'DCX-MED-CH-' + toString(i), trigger_event: 'CARE_GAP_REVIEW', 
                                      risk_at_time: 0.5 + (i*0.02), notes: 'Follow-up scheduled due to Apple watch irregularity'})
            
            MERGE (dc)-[:HAS_CONTEXT]->(dx)
            MERGE (dc)-[:ABOUT]->(p)
            MERGE (dc)-[:APPLIED_POLICY]->(pol)
        """)

        # 3. 15 Compliant Clearances (POL-MED-03)
        session.run("""
            UNWIND range(1, 15) AS i
            MERGE (pol:Policy {id: 'POL-MED-03'})
            MERGE (p:Patient {id: 'CUST-MED-LO-' + toString(i), name: 'LowRisk Patient ' + toString(i), age: 30+i, risk_tier: 'Low'})
            
            MERGE (ctx:Context {id: 'CTX-MED-LO-' + toString(i), risk_score: 0.1})
            MERGE (p)-[:HAS_CONTEXT]->(ctx)
            
            MERGE (pharm:Pharmacy {id: 'PHARM-MED-LO-' + toString(i), name: 'CVS'})
            MERGE (rx:Prescription {id: 'RX-LO-' + toString(i), status: 'Active'})
            MERGE (rx)-[:FULFILLED_AT]->(pharm)
            MERGE (p)-[:HAS_PRESCRIPTION]->(rx)
            
            MERGE (dc:Decision {id: 'DEC-MED-LO-' + toString(i), action: 'CLEAR_PATIENT', 
                               confidence: 0.99, status: 'COMPLETED', outcome: 'COMPLIANT',
                               created_at: datetime('2026-04-15T09:00:00Z'), decision_type: 'CARE_GAP_REVIEW'})
            MERGE (dx:DecisionContext {id: 'DCX-MED-LO-' + toString(i), trigger_event: 'CARE_GAP_REVIEW', 
                                      risk_at_time: 0.1, notes: 'Automated clearance via IoT and Pharmacy data'})
            
            MERGE (dc)-[:HAS_CONTEXT]->(dx)
            MERGE (dc)-[:ABOUT]->(p)
            MERGE (dc)-[:APPLIED_POLICY]->(pol)
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
