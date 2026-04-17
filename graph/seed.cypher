// ============================================================
// NBA Context Graph — Seed Data
// Realistic financial services demo data
// ============================================================

// --- Communities ---
MERGE (c1:Community {id: 'COM-001', name: 'Premium Banking', description: 'High-value personal banking customers'})
MERGE (c2:Community {id: 'COM-002', name: 'Small Business', description: 'Small business account holders'})
MERGE (c3:Community {id: 'COM-003', name: 'Young Professionals', description: 'Early-career professionals with growth potential'});

// --- Policies ---
MERGE (pol1:Policy {id: 'POL-001', name: 'Credit Limit Increase - Standard', family: 'credit_limit',
  description: 'Standard criteria for credit limit increases',
  min_months_active: 12, min_payment_score: 0.7, max_utilization_pct: 80, min_credit_score: 650})

MERGE (pol2:Policy {id: 'POL-002', name: 'High Risk Decline', family: 'risk_management',
  description: 'Decline threshold for high-risk indicators',
  max_days_past_due: 60, max_utilization_pct: 85, min_payment_score: 0.4})

MERGE (pol3:Policy {id: 'POL-003', name: 'Retention Offer Eligibility', family: 'retention',
  description: 'Criteria for retention offer eligibility',
  min_customer_value: 5000, min_months_active: 24, max_churn_risk: 0.7})

MERGE (pol4:Policy {id: 'POL-004', name: 'Escalation Threshold', family: 'escalation',
  description: 'When to escalate for manual review',
  ambiguity_threshold: 0.3, value_threshold: 10000})

MERGE (pol5:Policy {id: 'POL-005', name: 'Documentation Requirements', family: 'compliance',
  description: 'When additional documentation is required',
  income_verification_threshold: 50000, limit_increase_pct: 50});

// --- Persons ---
MERGE (p1:Person {id: 'PER-001', name: 'Sarah Chen', segment: 'premium',
  risk_score: 0.15, churn_risk: 0.08, customer_value: 28500,
  credit_score: 780, months_active: 72, email: 'sarah.chen@example.com'})

MERGE (p2:Person {id: 'PER-002', name: 'Marcus Williams', segment: 'standard',
  risk_score: 0.55, churn_risk: 0.42, customer_value: 8200,
  credit_score: 680, months_active: 36, email: 'marcus.w@example.com'})

MERGE (p3:Person {id: 'PER-003', name: 'Elena Rodriguez', segment: 'premium',
  risk_score: 0.25, churn_risk: 0.65, customer_value: 19800,
  credit_score: 740, months_active: 48, email: 'elena.r@example.com'})

MERGE (p4:Person {id: 'PER-004', name: 'James Park', segment: 'standard',
  risk_score: 0.78, churn_risk: 0.30, customer_value: 4500,
  credit_score: 590, months_active: 18, email: 'j.park@example.com'})

MERGE (p5:Person {id: 'PER-005', name: 'Aisha Patel', segment: 'business',
  risk_score: 0.35, churn_risk: 0.22, customer_value: 42000,
  credit_score: 720, months_active: 60, email: 'aisha.p@example.com'})

MERGE (p6:Person {id: 'PER-006', name: 'David Kim', segment: 'young_professional',
  risk_score: 0.20, churn_risk: 0.15, customer_value: 6200,
  credit_score: 710, months_active: 14, email: 'david.k@example.com'})

MERGE (p7:Person {id: 'PER-007', name: 'Linda Foster', segment: 'premium',
  risk_score: 0.10, churn_risk: 0.05, customer_value: 55000,
  credit_score: 810, months_active: 120, email: 'linda.f@example.com'})

MERGE (p8:Person {id: 'PER-008', name: 'Roberto Silva', segment: 'standard',
  risk_score: 0.62, churn_risk: 0.71, customer_value: 7800,
  credit_score: 640, months_active: 30, email: 'r.silva@example.com'});

// --- Accounts ---
MERGE (a1:Account {id: 'ACC-001', type: 'platinum_card', credit_limit: 25000,
  current_balance: 8750, utilization_pct: 35.0, payment_score: 0.95,
  days_past_due: 0, monthly_spend_avg: 3200})

MERGE (a2:Account {id: 'ACC-002', type: 'gold_card', credit_limit: 10000,
  current_balance: 8700, utilization_pct: 87.0, payment_score: 0.55,
  days_past_due: 45, monthly_spend_avg: 1800})

MERGE (a3:Account {id: 'ACC-003', type: 'platinum_card', credit_limit: 20000,
  current_balance: 14000, utilization_pct: 70.0, payment_score: 0.82,
  days_past_due: 0, monthly_spend_avg: 4500})

MERGE (a4:Account {id: 'ACC-004', type: 'standard_card', credit_limit: 5000,
  current_balance: 4600, utilization_pct: 92.0, payment_score: 0.35,
  days_past_due: 75, monthly_spend_avg: 900})

MERGE (a5:Account {id: 'ACC-005', type: 'business_card', credit_limit: 50000,
  current_balance: 22000, utilization_pct: 44.0, payment_score: 0.88,
  days_past_due: 0, monthly_spend_avg: 8500})

MERGE (a6:Account {id: 'ACC-006', type: 'standard_card', credit_limit: 8000,
  current_balance: 2400, utilization_pct: 30.0, payment_score: 0.90,
  days_past_due: 0, monthly_spend_avg: 1200})

MERGE (a7:Account {id: 'ACC-007', type: 'platinum_card', credit_limit: 50000,
  current_balance: 12000, utilization_pct: 24.0, payment_score: 0.98,
  days_past_due: 0, monthly_spend_avg: 6800})

MERGE (a8:Account {id: 'ACC-008', type: 'gold_card', credit_limit: 12000,
  current_balance: 10200, utilization_pct: 85.0, payment_score: 0.50,
  days_past_due: 30, monthly_spend_avg: 1500});

// --- Ownership Relationships ---
MATCH (p1:Person {id: 'PER-001'}), (a1:Account {id: 'ACC-001'}) MERGE (p1)-[:OWNS]->(a1);
MATCH (p2:Person {id: 'PER-002'}), (a2:Account {id: 'ACC-002'}) MERGE (p2)-[:OWNS]->(a2);
MATCH (p3:Person {id: 'PER-003'}), (a3:Account {id: 'ACC-003'}) MERGE (p3)-[:OWNS]->(a3);
MATCH (p4:Person {id: 'PER-004'}), (a4:Account {id: 'ACC-004'}) MERGE (p4)-[:OWNS]->(a4);
MATCH (p5:Person {id: 'PER-005'}), (a5:Account {id: 'ACC-005'}) MERGE (p5)-[:OWNS]->(a5);
MATCH (p6:Person {id: 'PER-006'}), (a6:Account {id: 'ACC-006'}) MERGE (p6)-[:OWNS]->(a6);
MATCH (p7:Person {id: 'PER-007'}), (a7:Account {id: 'ACC-007'}) MERGE (p7)-[:OWNS]->(a7);
MATCH (p8:Person {id: 'PER-008'}), (a8:Account {id: 'ACC-008'}) MERGE (p8)-[:OWNS]->(a8);

// --- Community Memberships ---
MATCH (p1:Person {id: 'PER-001'}), (c1:Community {id: 'COM-001'}) MERGE (p1)-[:MEMBER_OF]->(c1);
MATCH (p3:Person {id: 'PER-003'}), (c1:Community {id: 'COM-001'}) MERGE (p3)-[:MEMBER_OF]->(c1);
MATCH (p7:Person {id: 'PER-007'}), (c1:Community {id: 'COM-001'}) MERGE (p7)-[:MEMBER_OF]->(c1);
MATCH (p5:Person {id: 'PER-005'}), (c2:Community {id: 'COM-002'}) MERGE (p5)-[:MEMBER_OF]->(c2);
MATCH (p6:Person {id: 'PER-006'}), (c3:Community {id: 'COM-003'}) MERGE (p6)-[:MEMBER_OF]->(c3);

// --- Historical Decisions ---

// Decision 1: Sarah Chen — Approved credit increase (past)
MERGE (d1:Decision {id: 'DEC-001', action: 'APPROVE', confidence: 0.94,
  status: 'COMPLETED', created_at: datetime('2025-11-15T10:30:00Z'),
  analyst_id: 'analyst_01', outcome: 'POSITIVE'})
MERGE (dc1:DecisionContext {id: 'DCX-001', trigger_event: 'CREDIT_LIMIT_REVIEW',
  utilization_at_time: 40.0, risk_at_time: 0.12, notes: 'Annual review - excellent payment history'})
WITH d1, dc1
MATCH (p1:Person {id: 'PER-001'}), (a1:Account {id: 'ACC-001'}), (pol1:Policy {id: 'POL-001'})
MERGE (d1)-[:ABOUT]->(p1)
MERGE (d1)-[:ABOUT]->(a1)
MERGE (d1)-[:HAS_CONTEXT]->(dc1)
MERGE (d1)-[:APPLIED_POLICY]->(pol1);

// Decision 2: Marcus Williams — Escalated (past)
MERGE (d2:Decision {id: 'DEC-002', action: 'ESCALATE_FOR_REVIEW', confidence: 0.68,
  status: 'COMPLETED', created_at: datetime('2025-12-03T14:15:00Z'),
  analyst_id: 'analyst_02', outcome: 'NEUTRAL'})
MERGE (dc2:DecisionContext {id: 'DCX-002', trigger_event: 'PAYMENT_DELINQUENCY',
  utilization_at_time: 82.0, risk_at_time: 0.50, notes: 'Mixed signals - high utilization but recovering payments'})
MERGE (esc1:Escalation {id: 'ESC-001', reason: 'Ambiguous risk profile', target_reviewer: 'risk_manager_01',
  urgency: 'MEDIUM', status: 'RESOLVED', created_at: datetime('2025-12-03T14:15:00Z')})
WITH d2, dc2, esc1
MATCH (p2:Person {id: 'PER-002'}), (a2:Account {id: 'ACC-002'}), (pol2:Policy {id: 'POL-002'}), (pol4:Policy {id: 'POL-004'})
MERGE (d2)-[:ABOUT]->(p2)
MERGE (d2)-[:ABOUT]->(a2)
MERGE (d2)-[:HAS_CONTEXT]->(dc2)
MERGE (d2)-[:APPLIED_POLICY]->(pol2)
MERGE (d2)-[:APPLIED_POLICY]->(pol4)
MERGE (d2)-[:TRIGGERED]->(esc1);

// Decision 3: Elena Rodriguez — Retention offer (past)
MERGE (d3:Decision {id: 'DEC-003', action: 'OFFER_RETENTION', confidence: 0.86,
  status: 'COMPLETED', created_at: datetime('2026-01-10T09:45:00Z'),
  analyst_id: 'analyst_01', outcome: 'POSITIVE'})
MERGE (dc3:DecisionContext {id: 'DCX-003', trigger_event: 'CHURN_SIGNAL',
  utilization_at_time: 65.0, risk_at_time: 0.22, notes: 'Competitor offer detected, high-value customer'})
WITH d3, dc3
MATCH (p3:Person {id: 'PER-003'}), (a3:Account {id: 'ACC-003'}), (pol3:Policy {id: 'POL-003'})
MERGE (d3)-[:ABOUT]->(p3)
MERGE (d3)-[:ABOUT]->(a3)
MERGE (d3)-[:HAS_CONTEXT]->(dc3)
MERGE (d3)-[:APPLIED_POLICY]->(pol3);

// Decision 4: James Park — Declined (past)
MERGE (d4:Decision {id: 'DEC-004', action: 'DECLINE', confidence: 0.92,
  status: 'COMPLETED', created_at: datetime('2026-01-22T16:00:00Z'),
  analyst_id: 'analyst_03', outcome: 'EXPECTED'})
MERGE (dc4:DecisionContext {id: 'DCX-004', trigger_event: 'CREDIT_LIMIT_REQUEST',
  utilization_at_time: 90.0, risk_at_time: 0.75, notes: 'High utilization, severely delinquent'})
WITH d4, dc4
MATCH (p4:Person {id: 'PER-004'}), (a4:Account {id: 'ACC-004'}), (pol2:Policy {id: 'POL-002'})
MERGE (d4)-[:ABOUT]->(p4)
MERGE (d4)-[:ABOUT]->(a4)
MERGE (d4)-[:HAS_CONTEXT]->(dc4)
MERGE (d4)-[:APPLIED_POLICY]->(pol2);

// Decision 5: Aisha Patel — Approved with documentation request (past)
MERGE (d5:Decision {id: 'DEC-005', action: 'APPROVE', confidence: 0.82,
  status: 'COMPLETED', created_at: datetime('2026-02-05T11:30:00Z'),
  analyst_id: 'analyst_01', outcome: 'POSITIVE'})
MERGE (dc5:DecisionContext {id: 'DCX-005', trigger_event: 'CREDIT_LIMIT_REVIEW',
  utilization_at_time: 48.0, risk_at_time: 0.30, notes: 'Business growth, needed higher limit'})
MERGE (exc1:Exception {id: 'EXC-001', type: 'POLICY_OVERRIDE',
  rationale: 'Strong business growth trajectory justifies higher limit despite moderate risk',
  approved_by: 'risk_manager_01'})
WITH d5, dc5, exc1
MATCH (p5:Person {id: 'PER-005'}), (a5:Account {id: 'ACC-005'}), (pol1:Policy {id: 'POL-001'}), (pol5:Policy {id: 'POL-005'})
MERGE (d5)-[:ABOUT]->(p5)
MERGE (d5)-[:ABOUT]->(a5)
MERGE (d5)-[:HAS_CONTEXT]->(dc5)
MERGE (d5)-[:APPLIED_POLICY]->(pol1)
MERGE (d5)-[:APPLIED_POLICY]->(pol5)
MERGE (d5)-[:GRANTED_EXCEPTION]->(exc1);

// Decision 6: Linda Foster — Approved (past, premium)
MERGE (d6:Decision {id: 'DEC-006', action: 'APPROVE', confidence: 0.97,
  status: 'COMPLETED', created_at: datetime('2026-02-20T08:00:00Z'),
  analyst_id: 'analyst_02', outcome: 'POSITIVE'})
MERGE (dc6:DecisionContext {id: 'DCX-006', trigger_event: 'CREDIT_LIMIT_REVIEW',
  utilization_at_time: 22.0, risk_at_time: 0.08, notes: 'Exemplary customer, routine increase'})
WITH d6, dc6
MATCH (p7:Person {id: 'PER-007'}), (a7:Account {id: 'ACC-007'}), (pol1:Policy {id: 'POL-001'})
MERGE (d6)-[:ABOUT]->(p7)
MERGE (d6)-[:ABOUT]->(a7)
MERGE (d6)-[:HAS_CONTEXT]->(dc6)
MERGE (d6)-[:APPLIED_POLICY]->(pol1);

// --- Precedent Relationships ---
// Decision 6 (Linda approve) is precedent for Decision 1 (Sarah approve) — similar profile
MATCH (d1:Decision {id: 'DEC-001'}), (d6:Decision {id: 'DEC-006'})
MERGE (d6)-[:PRECEDENT_FOR]->(d1);

// Decision 4 (James decline) influenced Decision 2 (Marcus escalate) — similar risk
MATCH (d2:Decision {id: 'DEC-002'}), (d4:Decision {id: 'DEC-004'})
MERGE (d4)-[:INFLUENCED]->(d2);

// Decision 3 (Elena retention) is precedent for future retention cases
// (will be linked dynamically by the engine)

// --- Person 9: E-Commerce Happy Path ---
MERGE (pe1:Person {id: 'CUST-ECOM-HAPPY', name: 'John Miller', segment: 'standard',
  risk_score: 0.2, churn_risk: 0.1, customer_value: 32000,
  credit_score: 720, months_active: 24, email: 'john.m@example.com'})

// --- Person 10: E-Commerce Sad Path (Omnichannel Abandonment) ---
MERGE (pe2:Person {id: 'CUST-ECOM-SAD', name: 'Robert Vance', segment: 'premium',
  risk_score: 0.1, churn_risk: 0.8, customer_value: 55000,
  credit_score: 790, months_active: 48, email: 'robert.vance@example.com'})

// --- E-Commerce Context ---
MERGE (ctx_ecom:Context {id: 'CTX-ECOM-01', risk_score: 0.1, months_active: 48, inquiries: 0})
MERGE (pe2)-[:HAS_CONTEXT]->(ctx_ecom)

// --- Vehicles ---
MERGE (v1:BrowsedVehicle {vin: 'VIN-A4-001', make: 'Audi', model: 'A4', year: 2026, price: 42000})
MERGE (v2:BrowsedVehicle {vin: 'VIN-Q5-002', make: 'Audi', model: 'Q5', year: 2026, price: 55000})

// --- Dealerships ---
MERGE (dlr1:Dealership {id: 'DLR-NY-01', name: 'Central Audi Manhattan', location: 'New York, NY'})
MERGE (v1)-[:LOCATED_AT {stock: 2}]->(dlr1)
MERGE (v2)-[:LOCATED_AT {stock: 5}]->(dlr1)

// --- Omnichannel Facts for Robert Vance (Sad Path) ---

// 1. Web History (4 views of the A4)
MERGE (sess1:Session {id: 'SESS-ECOM-SAD', is_authenticated: true, start_time: datetime('2026-04-14T14:00:00Z')})
MERGE (pe2)-[:INITIATED_SESSION]->(sess1)
MERGE (sess1)-[:VIEWED {count: 4, duration_sec: 1200}]->(v1)

// 2. Mobile Device & Calculator usage
MERGE (dev1:Device {id: 'DEV-IPHONE-15', type: 'Mobile', os: 'iOS'})
MERGE (pe2)-[:LOGGED_IN_FROM]->(dev1)
MERGE (dev1)-[:INITIATED]->(sess1)
MERGE (calc1:FinancingCalculator {id: 'CALC-72MO', term_months: 72, interest_rate: 4.99})
MERGE (sess1)-[:ENGAGED_WITH]->(calc1)

// 3. Physical Visit (The "Closing Fact")
MERGE (visit1:PhysicalVisit {id: 'VISIT-NY-001', date: datetime('2026-04-14T15:30:00Z'), duration_min: 90, activity: 'Test Drive'})
MERGE (pe2)-[:TOOK_TEST_DRIVE]->(visit1)
MERGE (visit1)-[:AT_LOCATION]->(dlr1)

// --- Happy Path (John Miller) ---
MERGE (sess2:Session {id: 'SESS-ECOM-HAPPY', is_authenticated: true})
MERGE (pe1)-[:INITIATED_SESSION]->(sess2)
MERGE (sess2)-[:VIEWED]->(v2)
MERGE (sess2)-[:PURCHASED {date: datetime('2026-04-10T11:00:00Z')}]->(v2);

// ============================================================
// E-COMMERCE POPULATION SEED
// 25 historical abandoned-session cohorts — powers NBA confidence blending
// 5 cohorts × 5 sessions: OFFER_SMS · OFFER_TRADE_IN · SCARCITY_ALERT
//                          VIP_SHOWROOM_INVITE · APPROVE (bounce)
// ============================================================

// --- MarTech Policy Nodes ---
MERGE (:Policy {id: 'POL-MAR-01', name: 'Omnichannel Abandonment Recovery', family: 'MarTech',
  description: 'Trigger SMS with locked APR when web + mobile + physical intent confirmed'})
MERGE (:Policy {id: 'POL-MAR-02', name: 'Trade-In Equity Leverage', family: 'MarTech',
  description: 'Convert trade-in equity into monthly payment counter-offer'})
MERGE (:Policy {id: 'POL-MAR-03', name: 'Dynamic Scarcity Alert', family: 'MarTech',
  description: 'Trigger FOMO notification when local inventory falls below 3 units'})
MERGE (:Policy {id: 'POL-MAR-04', name: 'Omnichannel Accelerator', family: 'MarTech',
  description: 'VIP showroom invite for test-drive leads who abandoned digitally'});

// --- Additional Vehicles (normal inventory) ---
MERGE (vb1:BrowsedVehicle {vin: 'VIN-BMWX5-001', make: 'BMW',      model: 'X5',       year: 2026, price: 65000})
MERGE (vb2:BrowsedVehicle {vin: 'VIN-BMW3S-001', make: 'BMW',      model: '3 Series',  year: 2025, price: 45000})
MERGE (vb3:BrowsedVehicle {vin: 'VIN-CAMRY-001', make: 'Toyota',   model: 'Camry',     year: 2026, price: 28000})
MERGE (vb4:BrowsedVehicle {vin: 'VIN-CRV-001',   make: 'Honda',    model: 'CR-V',      year: 2026, price: 35000})
MERGE (vb5:BrowsedVehicle {vin: 'VIN-MERCC-001', make: 'Mercedes', model: 'C-Class',   year: 2026, price: 48000})
// Scarcity-only VINs: isolated low-stock vehicles so normal-stock sessions are unaffected
MERGE (vs1:BrowsedVehicle {vin: 'VIN-SCAR-B1', make: 'BMW',      model: 'X5',      year: 2026, price: 65000})
MERGE (vs2:BrowsedVehicle {vin: 'VIN-SCAR-A1', make: 'Audi',     model: 'Q5',      year: 2026, price: 55000})
MERGE (vs3:BrowsedVehicle {vin: 'VIN-SCAR-B2', make: 'BMW',      model: 'X5',      year: 2026, price: 65000})
MERGE (vs4:BrowsedVehicle {vin: 'VIN-SCAR-M1', make: 'Mercedes', model: 'C-Class', year: 2026, price: 48000})
MERGE (vs5:BrowsedVehicle {vin: 'VIN-SCAR-A2', make: 'Audi',     model: 'A4',      year: 2026, price: 42000})
// --- Additional Dealerships ---
MERGE (dla:Dealership  {id: 'DLR-LA-01',  name: 'Beverly Hills BMW',     location: 'Los Angeles, CA'})
MERGE (dchi:Dealership {id: 'DLR-CHI-01', name: 'Chicago Toyota',         location: 'Chicago, IL'})
MERGE (dmia:Dealership {id: 'DLR-MIA-01', name: 'South Beach Mercedes',   location: 'Miami, FL'})
MERGE (dny:Dealership  {id: 'DLR-NY-01',  name: 'Central Audi Manhattan', location: 'New York, NY'})
// Normal inventory stock
MERGE (vb1)-[:LOCATED_AT {stock: 6}]->(dla)
MERGE (vb2)-[:LOCATED_AT {stock: 8}]->(dla)
MERGE (vb3)-[:LOCATED_AT {stock: 12}]->(dchi)
MERGE (vb4)-[:LOCATED_AT {stock: 10}]->(dchi)
MERGE (vb5)-[:LOCATED_AT {stock: 7}]->(dmia)
// Scarcity stock (1–2 units)
MERGE (vs1)-[:LOCATED_AT {stock: 1}]->(dla)
MERGE (vs2)-[:LOCATED_AT {stock: 2}]->(dny)
MERGE (vs3)-[:LOCATED_AT {stock: 1}]->(dla)
MERGE (vs4)-[:LOCATED_AT {stock: 2}]->(dmia)
MERGE (vs5)-[:LOCATED_AT {stock: 1}]->(dny);

// ── COHORT 1: OFFER_SMS — High-Intent Omnichannel (4 CONVERTED, 1 CHURNED) ──
// Pattern: 4+ views + financing calculator + 1+ physical test drive
MERGE (pm01:Policy {id: 'POL-MAR-01'})
MERGE (dla1:Dealership {id: 'DLR-LA-01'})
MERGE (dny1:Dealership {id: 'DLR-NY-01'})
MERGE (dchi1:Dealership {id: 'DLR-CHI-01'})

// HI-01 Emma Wilson — premium, BMW X5, 5 views, 60mo calc, 1 test drive → CONVERTED
MERGE (p_hi1:Person {id: 'CUST-ABN-HI-01', name: 'Emma Wilson', segment: 'premium',
  risk_score: 0.12, churn_risk: 0.75, customer_value: 48000, credit_score: 765, months_active: 36, email: 'emma.w@example.com'})
MERGE (dv_hi1:Device {id: 'DEV-ABN-HI-01', type: 'Mobile', os: 'iOS'})
MERGE (ss_hi1:Session {id: 'SESS-ABN-HI-01', is_authenticated: true, start_time: datetime('2026-01-10T11:00:00Z')})
MERGE (p_hi1)-[:LOGGED_IN_FROM]->(dv_hi1)
MERGE (dv_hi1)-[:INITIATED]->(ss_hi1)
MERGE (vh_hi1:BrowsedVehicle {vin: 'VIN-BMWX5-001'})
MERGE (ss_hi1)-[:VIEWED {count: 5, duration_sec: 1800}]->(vh_hi1)
MERGE (ca_hi1:FinancingCalculator {id: 'CALC-ABN-HI-01', term_months: 60, interest_rate: 3.99})
MERGE (ss_hi1)-[:ENGAGED_WITH]->(ca_hi1)
MERGE (vi_hi1:PhysicalVisit {id: 'VISIT-ABN-HI-01', date: datetime('2026-01-10T14:30:00Z'), duration_min: 80, activity: 'Test Drive'})
MERGE (p_hi1)-[:TOOK_TEST_DRIVE]->(vi_hi1)
MERGE (vi_hi1)-[:AT_LOCATION]->(dla1)
MERGE (dc_hi1:Decision {id: 'DEC-ABN-HI-01', action: 'OFFER_SMS', confidence: 0.98,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-01-11T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_hi1:DecisionContext {id: 'DCX-ABN-HI-01', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.12, notes: 'SMS with locked 3.99% APR — responded within 4h'})
MERGE (dc_hi1)-[:HAS_CONTEXT]->(dx_hi1)
MERGE (dc_hi1)-[:ABOUT]->(p_hi1)
MERGE (dc_hi1)-[:APPLIED_POLICY]->(pm01)

// HI-02 Carlos Mendez — standard, BMW X5, 4 views, 48mo calc, 1 test drive → CONVERTED
MERGE (p_hi2:Person {id: 'CUST-ABN-HI-02', name: 'Carlos Mendez', segment: 'standard',
  risk_score: 0.22, churn_risk: 0.68, customer_value: 31000, credit_score: 700, months_active: 24, email: 'carlos.m@example.com'})
MERGE (dv_hi2:Device {id: 'DEV-ABN-HI-02', type: 'Mobile', os: 'Android'})
MERGE (ss_hi2:Session {id: 'SESS-ABN-HI-02', is_authenticated: true, start_time: datetime('2026-01-18T15:00:00Z')})
MERGE (p_hi2)-[:LOGGED_IN_FROM]->(dv_hi2)
MERGE (dv_hi2)-[:INITIATED]->(ss_hi2)
MERGE (ss_hi2)-[:VIEWED {count: 4, duration_sec: 1400}]->(vh_hi1)
MERGE (ca_hi2:FinancingCalculator {id: 'CALC-ABN-HI-02', term_months: 48, interest_rate: 4.49})
MERGE (ss_hi2)-[:ENGAGED_WITH]->(ca_hi2)
MERGE (vi_hi2:PhysicalVisit {id: 'VISIT-ABN-HI-02', date: datetime('2026-01-18T17:00:00Z'), duration_min: 60, activity: 'Test Drive'})
MERGE (p_hi2)-[:TOOK_TEST_DRIVE]->(vi_hi2)
MERGE (vi_hi2)-[:AT_LOCATION]->(dla1)
MERGE (dc_hi2:Decision {id: 'DEC-ABN-HI-02', action: 'OFFER_SMS', confidence: 0.98,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-01-19T08:30:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_hi2:DecisionContext {id: 'DCX-ABN-HI-02', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.22, notes: 'SMS converted same-day purchase'})
MERGE (dc_hi2)-[:HAS_CONTEXT]->(dx_hi2)
MERGE (dc_hi2)-[:ABOUT]->(p_hi2)
MERGE (dc_hi2)-[:APPLIED_POLICY]->(pm01)

// HI-03 Priya Sharma — premium, Audi Q5, 6 views, 72mo calc, 2 test drives → CONVERTED
MERGE (p_hi3:Person {id: 'CUST-ABN-HI-03', name: 'Priya Sharma', segment: 'premium',
  risk_score: 0.10, churn_risk: 0.82, customer_value: 62000, credit_score: 790, months_active: 60, email: 'priya.s@example.com'})
MERGE (dv_hi3:Device {id: 'DEV-ABN-HI-03', type: 'Desktop', os: 'macOS'})
MERGE (ss_hi3:Session {id: 'SESS-ABN-HI-03', is_authenticated: true, start_time: datetime('2026-01-25T10:00:00Z')})
MERGE (p_hi3)-[:LOGGED_IN_FROM]->(dv_hi3)
MERGE (dv_hi3)-[:INITIATED]->(ss_hi3)
MERGE (vh_hi3:BrowsedVehicle {vin: 'VIN-Q5-002'})
MERGE (ss_hi3)-[:VIEWED {count: 6, duration_sec: 2400}]->(vh_hi3)
MERGE (ca_hi3:FinancingCalculator {id: 'CALC-ABN-HI-03', term_months: 72, interest_rate: 3.79})
MERGE (ss_hi3)-[:ENGAGED_WITH]->(ca_hi3)
MERGE (vi_hi3a:PhysicalVisit {id: 'VISIT-ABN-HI-03A', date: datetime('2026-01-20T13:00:00Z'), duration_min: 90, activity: 'Test Drive'})
MERGE (vi_hi3b:PhysicalVisit {id: 'VISIT-ABN-HI-03B', date: datetime('2026-01-25T11:00:00Z'), duration_min: 70, activity: 'Test Drive'})
MERGE (p_hi3)-[:TOOK_TEST_DRIVE]->(vi_hi3a)
MERGE (vi_hi3a)-[:AT_LOCATION]->(dny1)
MERGE (p_hi3)-[:TOOK_TEST_DRIVE]->(vi_hi3b)
MERGE (vi_hi3b)-[:AT_LOCATION]->(dny1)
MERGE (dc_hi3:Decision {id: 'DEC-ABN-HI-03', action: 'OFFER_SMS', confidence: 0.98,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-01-26T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_hi3:DecisionContext {id: 'DCX-ABN-HI-03', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.10, notes: '2 test drives — SMS lock-in offer triggered purchase'})
MERGE (dc_hi3)-[:HAS_CONTEXT]->(dx_hi3)
MERGE (dc_hi3)-[:ABOUT]->(p_hi3)
MERGE (dc_hi3)-[:APPLIED_POLICY]->(pm01)

// HI-04 Tyler Brooks — standard, Toyota Camry, 4 views, 60mo calc, 1 test drive → CONVERTED
MERGE (p_hi4:Person {id: 'CUST-ABN-HI-04', name: 'Tyler Brooks', segment: 'standard',
  risk_score: 0.28, churn_risk: 0.60, customer_value: 22000, credit_score: 685, months_active: 18, email: 'tyler.b@example.com'})
MERGE (dv_hi4:Device {id: 'DEV-ABN-HI-04', type: 'Mobile', os: 'iOS'})
MERGE (ss_hi4:Session {id: 'SESS-ABN-HI-04', is_authenticated: true, start_time: datetime('2026-02-03T16:00:00Z')})
MERGE (p_hi4)-[:LOGGED_IN_FROM]->(dv_hi4)
MERGE (dv_hi4)-[:INITIATED]->(ss_hi4)
MERGE (vh_hi4:BrowsedVehicle {vin: 'VIN-CAMRY-001'})
MERGE (ss_hi4)-[:VIEWED {count: 4, duration_sec: 1200}]->(vh_hi4)
MERGE (ca_hi4:FinancingCalculator {id: 'CALC-ABN-HI-04', term_months: 60, interest_rate: 4.99})
MERGE (ss_hi4)-[:ENGAGED_WITH]->(ca_hi4)
MERGE (vi_hi4:PhysicalVisit {id: 'VISIT-ABN-HI-04', date: datetime('2026-02-03T18:00:00Z'), duration_min: 55, activity: 'Test Drive'})
MERGE (p_hi4)-[:TOOK_TEST_DRIVE]->(vi_hi4)
MERGE (vi_hi4)-[:AT_LOCATION]->(dchi1)
MERGE (dc_hi4:Decision {id: 'DEC-ABN-HI-04', action: 'OFFER_SMS', confidence: 0.98,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-04T08:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_hi4:DecisionContext {id: 'DCX-ABN-HI-04', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.28, notes: 'SMS offer accepted next morning'})
MERGE (dc_hi4)-[:HAS_CONTEXT]->(dx_hi4)
MERGE (dc_hi4)-[:ABOUT]->(p_hi4)
MERGE (dc_hi4)-[:APPLIED_POLICY]->(pm01)

// HI-05 Natalie Greene — premium, BMW X5, 5 views, 72mo calc, 1 test drive → CHURNED
MERGE (p_hi5:Person {id: 'CUST-ABN-HI-05', name: 'Natalie Greene', segment: 'premium',
  risk_score: 0.15, churn_risk: 0.90, customer_value: 41000, credit_score: 750, months_active: 42, email: 'natalie.g@example.com'})
MERGE (dv_hi5:Device {id: 'DEV-ABN-HI-05', type: 'Mobile', os: 'iOS'})
MERGE (ss_hi5:Session {id: 'SESS-ABN-HI-05', is_authenticated: true, start_time: datetime('2026-02-10T12:00:00Z')})
MERGE (p_hi5)-[:LOGGED_IN_FROM]->(dv_hi5)
MERGE (dv_hi5)-[:INITIATED]->(ss_hi5)
MERGE (ss_hi5)-[:VIEWED {count: 5, duration_sec: 1600}]->(vh_hi1)
MERGE (ca_hi5:FinancingCalculator {id: 'CALC-ABN-HI-05', term_months: 72, interest_rate: 4.99})
MERGE (ss_hi5)-[:ENGAGED_WITH]->(ca_hi5)
MERGE (vi_hi5:PhysicalVisit {id: 'VISIT-ABN-HI-05', date: datetime('2026-02-10T15:00:00Z'), duration_min: 65, activity: 'Test Drive'})
MERGE (p_hi5)-[:TOOK_TEST_DRIVE]->(vi_hi5)
MERGE (vi_hi5)-[:AT_LOCATION]->(dla1)
MERGE (dc_hi5:Decision {id: 'DEC-ABN-HI-05', action: 'OFFER_SMS', confidence: 0.98,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-02-11T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_hi5:DecisionContext {id: 'DCX-ABN-HI-05', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.15, notes: 'SMS sent — no response, purchased competitor vehicle'})
MERGE (dc_hi5)-[:HAS_CONTEXT]->(dx_hi5)
MERGE (dc_hi5)-[:ABOUT]->(p_hi5)
MERGE (dc_hi5)-[:APPLIED_POLICY]->(pm01);

// ── COHORT 2: OFFER_TRADE_IN — Trade-In Equity Leverage (4 CONVERTED, 1 CHURNED) ──
// Pattern: 4+ views + owned vehicle equity > $5,000 + no test drive (Rule 1 cannot fire)
MERGE (pm02:Policy {id: 'POL-MAR-02'})
MERGE (dla2:Dealership {id: 'DLR-LA-01'})
MERGE (dny2:Dealership {id: 'DLR-NY-01'})
MERGE (dmia2:Dealership {id: 'DLR-MIA-01'})
MERGE (dchi2:Dealership {id: 'DLR-CHI-01'})

// TI-01 Victor Chang — premium, BMW X5, 5 views, trade-in $12,000 → CONVERTED
MERGE (p_ti1:Person {id: 'CUST-ABN-TI-01', name: 'Victor Chang', segment: 'premium',
  risk_score: 0.14, churn_risk: 0.72, customer_value: 54000, credit_score: 775, months_active: 48, email: 'victor.c@example.com'})
MERGE (ov_ti1:OwnedVehicle {vin: 'OWN-ABN-TI-01', make: 'BMW', model: '5 Series', year: 2021})
MERGE (val_ti1:Valuation {id: 'VAL-ABN-TI-01', amount: 12000, assessed_at: datetime('2026-02-01T10:00:00Z')})
MERGE (p_ti1)-[:OWNS]->(ov_ti1)
MERGE (ov_ti1)-[:VALUED_AT]->(val_ti1)
MERGE (dv_ti1:Device {id: 'DEV-ABN-TI-01', type: 'Desktop', os: 'Windows'})
MERGE (ss_ti1:Session {id: 'SESS-ABN-TI-01', is_authenticated: true, start_time: datetime('2026-02-01T14:00:00Z')})
MERGE (p_ti1)-[:LOGGED_IN_FROM]->(dv_ti1)
MERGE (dv_ti1)-[:INITIATED]->(ss_ti1)
MERGE (vh_ti1:BrowsedVehicle {vin: 'VIN-BMWX5-001'})
MERGE (ss_ti1)-[:VIEWED {count: 5, duration_sec: 1900}]->(vh_ti1)
MERGE (dc_ti1:Decision {id: 'DEC-ABN-TI-01', action: 'OFFER_TRADE_IN', confidence: 0.95,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-02T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_ti1:DecisionContext {id: 'DCX-ABN-TI-01', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.14, notes: 'Trade-in offer $299/mo closed deal within 48h'})
MERGE (dc_ti1)-[:HAS_CONTEXT]->(dx_ti1)
MERGE (dc_ti1)-[:ABOUT]->(p_ti1)
MERGE (dc_ti1)-[:APPLIED_POLICY]->(pm02)

// TI-02 Sandra O'Brien — standard, Audi A4, 4 views, trade-in $8,500 → CONVERTED
MERGE (p_ti2:Person {id: 'CUST-ABN-TI-02', name: "Sandra O'Brien", segment: 'standard',
  risk_score: 0.25, churn_risk: 0.65, customer_value: 27000, credit_score: 710, months_active: 30, email: 'sandra.ob@example.com'})
MERGE (ov_ti2:OwnedVehicle {vin: 'OWN-ABN-TI-02', make: 'Honda', model: 'Civic', year: 2020})
MERGE (val_ti2:Valuation {id: 'VAL-ABN-TI-02', amount: 8500, assessed_at: datetime('2026-02-08T10:00:00Z')})
MERGE (p_ti2)-[:OWNS]->(ov_ti2)
MERGE (ov_ti2)-[:VALUED_AT]->(val_ti2)
MERGE (dv_ti2:Device {id: 'DEV-ABN-TI-02', type: 'Mobile', os: 'iOS'})
MERGE (ss_ti2:Session {id: 'SESS-ABN-TI-02', is_authenticated: true, start_time: datetime('2026-02-08T11:00:00Z')})
MERGE (p_ti2)-[:LOGGED_IN_FROM]->(dv_ti2)
MERGE (dv_ti2)-[:INITIATED]->(ss_ti2)
MERGE (vh_ti2:BrowsedVehicle {vin: 'VIN-A4-001'})
MERGE (ss_ti2)-[:VIEWED {count: 4, duration_sec: 1300}]->(vh_ti2)
MERGE (dc_ti2:Decision {id: 'DEC-ABN-TI-02', action: 'OFFER_TRADE_IN', confidence: 0.95,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-09T08:30:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_ti2:DecisionContext {id: 'DCX-ABN-TI-02', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.25, notes: 'Trade-in SMS with payment breakdown converted'})
MERGE (dc_ti2)-[:HAS_CONTEXT]->(dx_ti2)
MERGE (dc_ti2)-[:ABOUT]->(p_ti2)
MERGE (dc_ti2)-[:APPLIED_POLICY]->(pm02)

// TI-03 Marcus Brown — premium, Mercedes C-Class, 6 views, trade-in $15,000 → CONVERTED
MERGE (p_ti3:Person {id: 'CUST-ABN-TI-03', name: 'Marcus Brown', segment: 'premium',
  risk_score: 0.11, churn_risk: 0.78, customer_value: 71000, credit_score: 800, months_active: 72, email: 'marcus.br@example.com'})
MERGE (ov_ti3:OwnedVehicle {vin: 'OWN-ABN-TI-03', make: 'Mercedes', model: 'E-Class', year: 2019})
MERGE (val_ti3:Valuation {id: 'VAL-ABN-TI-03', amount: 15000, assessed_at: datetime('2026-02-15T10:00:00Z')})
MERGE (p_ti3)-[:OWNS]->(ov_ti3)
MERGE (ov_ti3)-[:VALUED_AT]->(val_ti3)
MERGE (dv_ti3:Device {id: 'DEV-ABN-TI-03', type: 'Desktop', os: 'macOS'})
MERGE (ss_ti3:Session {id: 'SESS-ABN-TI-03', is_authenticated: true, start_time: datetime('2026-02-15T13:00:00Z')})
MERGE (p_ti3)-[:LOGGED_IN_FROM]->(dv_ti3)
MERGE (dv_ti3)-[:INITIATED]->(ss_ti3)
MERGE (vh_ti3:BrowsedVehicle {vin: 'VIN-MERCC-001'})
MERGE (ss_ti3)-[:VIEWED {count: 6, duration_sec: 2600}]->(vh_ti3)
MERGE (dc_ti3:Decision {id: 'DEC-ABN-TI-03', action: 'OFFER_TRADE_IN', confidence: 0.95,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-16T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_ti3:DecisionContext {id: 'DCX-ABN-TI-03', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.11, notes: '$15k equity — trade-in offer converted in 24h'})
MERGE (dc_ti3)-[:HAS_CONTEXT]->(dx_ti3)
MERGE (dc_ti3)-[:ABOUT]->(p_ti3)
MERGE (dc_ti3)-[:APPLIED_POLICY]->(pm02)

// TI-04 Lisa Park — standard, Honda CR-V, 4 views, trade-in $7,200 → CONVERTED
MERGE (p_ti4:Person {id: 'CUST-ABN-TI-04', name: 'Lisa Park', segment: 'standard',
  risk_score: 0.30, churn_risk: 0.55, customer_value: 19000, credit_score: 695, months_active: 20, email: 'lisa.pk@example.com'})
MERGE (ov_ti4:OwnedVehicle {vin: 'OWN-ABN-TI-04', make: 'Toyota', model: 'Corolla', year: 2019})
MERGE (val_ti4:Valuation {id: 'VAL-ABN-TI-04', amount: 7200, assessed_at: datetime('2026-02-22T10:00:00Z')})
MERGE (p_ti4)-[:OWNS]->(ov_ti4)
MERGE (ov_ti4)-[:VALUED_AT]->(val_ti4)
MERGE (dv_ti4:Device {id: 'DEV-ABN-TI-04', type: 'Mobile', os: 'Android'})
MERGE (ss_ti4:Session {id: 'SESS-ABN-TI-04', is_authenticated: true, start_time: datetime('2026-02-22T16:00:00Z')})
MERGE (p_ti4)-[:LOGGED_IN_FROM]->(dv_ti4)
MERGE (dv_ti4)-[:INITIATED]->(ss_ti4)
MERGE (vh_ti4:BrowsedVehicle {vin: 'VIN-CRV-001'})
MERGE (ss_ti4)-[:VIEWED {count: 4, duration_sec: 1350}]->(vh_ti4)
MERGE (dc_ti4:Decision {id: 'DEC-ABN-TI-04', action: 'OFFER_TRADE_IN', confidence: 0.95,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-23T08:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_ti4:DecisionContext {id: 'DCX-ABN-TI-04', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.30, notes: 'Trade-in equity closed price gap — converted'})
MERGE (dc_ti4)-[:HAS_CONTEXT]->(dx_ti4)
MERGE (dc_ti4)-[:ABOUT]->(p_ti4)
MERGE (dc_ti4)-[:APPLIED_POLICY]->(pm02)

// TI-05 Kevin Patel — premium, BMW 3 Series, 5 views, trade-in $9,800 → CHURNED
MERGE (p_ti5:Person {id: 'CUST-ABN-TI-05', name: 'Kevin Patel', segment: 'premium',
  risk_score: 0.18, churn_risk: 0.88, customer_value: 38000, credit_score: 740, months_active: 54, email: 'kevin.pt@example.com'})
MERGE (ov_ti5:OwnedVehicle {vin: 'OWN-ABN-TI-05', make: 'Audi', model: 'A3', year: 2020})
MERGE (val_ti5:Valuation {id: 'VAL-ABN-TI-05', amount: 9800, assessed_at: datetime('2026-03-01T10:00:00Z')})
MERGE (p_ti5)-[:OWNS]->(ov_ti5)
MERGE (ov_ti5)-[:VALUED_AT]->(val_ti5)
MERGE (dv_ti5:Device {id: 'DEV-ABN-TI-05', type: 'Mobile', os: 'iOS'})
MERGE (ss_ti5:Session {id: 'SESS-ABN-TI-05', is_authenticated: true, start_time: datetime('2026-03-01T12:00:00Z')})
MERGE (p_ti5)-[:LOGGED_IN_FROM]->(dv_ti5)
MERGE (dv_ti5)-[:INITIATED]->(ss_ti5)
MERGE (vh_ti5:BrowsedVehicle {vin: 'VIN-BMW3S-001'})
MERGE (ss_ti5)-[:VIEWED {count: 5, duration_sec: 1700}]->(vh_ti5)
MERGE (dc_ti5:Decision {id: 'DEC-ABN-TI-05', action: 'OFFER_TRADE_IN', confidence: 0.95,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-02T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_ti5:DecisionContext {id: 'DCX-ABN-TI-05', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.18, notes: 'Trade-in offer sent — customer leased competitor vehicle'})
MERGE (dc_ti5)-[:HAS_CONTEXT]->(dx_ti5)
MERGE (dc_ti5)-[:ABOUT]->(p_ti5)
MERGE (dc_ti5)-[:APPLIED_POLICY]->(pm02);

// ── COHORT 3: SCARCITY_ALERT — Low Inventory (3 CONVERTED, 2 CHURNED) ──
// Pattern: 2+ views + dealership stock < 3 + no test drive + no trade-in equity > $5k
MERGE (pm03:Policy {id: 'POL-MAR-03'})
MERGE (dla3:Dealership {id: 'DLR-LA-01'})
MERGE (dny3:Dealership {id: 'DLR-NY-01'})
MERGE (dmia3:Dealership {id: 'DLR-MIA-01'})

// SC-01 Jessica Torres — standard, BMW X5 (stock=1), 3 views → CONVERTED
MERGE (p_sc1:Person {id: 'CUST-ABN-SC-01', name: 'Jessica Torres', segment: 'standard',
  risk_score: 0.26, churn_risk: 0.70, customer_value: 24000, credit_score: 695, months_active: 22, email: 'jessica.t@example.com'})
MERGE (dv_sc1:Device {id: 'DEV-ABN-SC-01', type: 'Mobile', os: 'iOS'})
MERGE (ss_sc1:Session {id: 'SESS-ABN-SC-01', is_authenticated: true, start_time: datetime('2026-02-05T10:00:00Z')})
MERGE (p_sc1)-[:LOGGED_IN_FROM]->(dv_sc1)
MERGE (dv_sc1)-[:INITIATED]->(ss_sc1)
MERGE (vh_sc1:BrowsedVehicle {vin: 'VIN-SCAR-B1'})
MERGE (ss_sc1)-[:VIEWED {count: 3, duration_sec: 900}]->(vh_sc1)
MERGE (dc_sc1:Decision {id: 'DEC-ABN-SC-01', action: 'SCARCITY_ALERT', confidence: 0.88,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-05T14:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_sc1:DecisionContext {id: 'DCX-ABN-SC-01', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.26, notes: '"Only 1 left" alert — booked appointment same day'})
MERGE (dc_sc1)-[:HAS_CONTEXT]->(dx_sc1)
MERGE (dc_sc1)-[:ABOUT]->(p_sc1)
MERGE (dc_sc1)-[:APPLIED_POLICY]->(pm03)

// SC-02 Brian Kim — standard, Audi Q5 (stock=2), 2 views → CONVERTED
MERGE (p_sc2:Person {id: 'CUST-ABN-SC-02', name: 'Brian Kim', segment: 'standard',
  risk_score: 0.32, churn_risk: 0.62, customer_value: 18000, credit_score: 680, months_active: 15, email: 'brian.k@example.com'})
MERGE (dv_sc2:Device {id: 'DEV-ABN-SC-02', type: 'Mobile', os: 'Android'})
MERGE (ss_sc2:Session {id: 'SESS-ABN-SC-02', is_authenticated: true, start_time: datetime('2026-02-12T15:00:00Z')})
MERGE (p_sc2)-[:LOGGED_IN_FROM]->(dv_sc2)
MERGE (dv_sc2)-[:INITIATED]->(ss_sc2)
MERGE (vh_sc2:BrowsedVehicle {vin: 'VIN-SCAR-A1'})
MERGE (ss_sc2)-[:VIEWED {count: 2, duration_sec: 700}]->(vh_sc2)
MERGE (dc_sc2:Decision {id: 'DEC-ABN-SC-02', action: 'SCARCITY_ALERT', confidence: 0.88,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-12T18:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_sc2:DecisionContext {id: 'DCX-ABN-SC-02', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.32, notes: 'Scarcity push notification — purchased within 24h'})
MERGE (dc_sc2)-[:HAS_CONTEXT]->(dx_sc2)
MERGE (dc_sc2)-[:ABOUT]->(p_sc2)
MERGE (dc_sc2)-[:APPLIED_POLICY]->(pm03)

// SC-03 Alicia Chen — premium, BMW X5 (stock=1), 4 views, no trade-in → CONVERTED
MERGE (p_sc3:Person {id: 'CUST-ABN-SC-03', name: 'Alicia Chen', segment: 'premium',
  risk_score: 0.13, churn_risk: 0.76, customer_value: 52000, credit_score: 760, months_active: 40, email: 'alicia.c@example.com'})
MERGE (dv_sc3:Device {id: 'DEV-ABN-SC-03', type: 'Desktop', os: 'macOS'})
MERGE (ss_sc3:Session {id: 'SESS-ABN-SC-03', is_authenticated: true, start_time: datetime('2026-02-20T11:00:00Z')})
MERGE (p_sc3)-[:LOGGED_IN_FROM]->(dv_sc3)
MERGE (dv_sc3)-[:INITIATED]->(ss_sc3)
MERGE (vh_sc3:BrowsedVehicle {vin: 'VIN-SCAR-B2'})
MERGE (ss_sc3)-[:VIEWED {count: 4, duration_sec: 1500}]->(vh_sc3)
MERGE (dc_sc3:Decision {id: 'DEC-ABN-SC-03', action: 'SCARCITY_ALERT', confidence: 0.88,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-20T16:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_sc3:DecisionContext {id: 'DCX-ABN-SC-03', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.13, notes: 'Final unit urgency — premium buyer converted'})
MERGE (dc_sc3)-[:HAS_CONTEXT]->(dx_sc3)
MERGE (dc_sc3)-[:ABOUT]->(p_sc3)
MERGE (dc_sc3)-[:APPLIED_POLICY]->(pm03)

// SC-04 Derek Walsh — standard, Mercedes C-Class (stock=2), 3 views → CHURNED
MERGE (p_sc4:Person {id: 'CUST-ABN-SC-04', name: 'Derek Walsh', segment: 'standard',
  risk_score: 0.35, churn_risk: 0.58, customer_value: 16000, credit_score: 670, months_active: 12, email: 'derek.w@example.com'})
MERGE (dv_sc4:Device {id: 'DEV-ABN-SC-04', type: 'Mobile', os: 'Android'})
MERGE (ss_sc4:Session {id: 'SESS-ABN-SC-04', is_authenticated: false, start_time: datetime('2026-03-05T14:00:00Z')})
MERGE (p_sc4)-[:LOGGED_IN_FROM]->(dv_sc4)
MERGE (dv_sc4)-[:INITIATED]->(ss_sc4)
MERGE (vh_sc4:BrowsedVehicle {vin: 'VIN-SCAR-M1'})
MERGE (ss_sc4)-[:VIEWED {count: 3, duration_sec: 800}]->(vh_sc4)
MERGE (dc_sc4:Decision {id: 'DEC-ABN-SC-04', action: 'SCARCITY_ALERT', confidence: 0.88,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-05T17:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_sc4:DecisionContext {id: 'DCX-ABN-SC-04', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.35, notes: 'Scarcity alert sent — price sensitivity, no conversion'})
MERGE (dc_sc4)-[:HAS_CONTEXT]->(dx_sc4)
MERGE (dc_sc4)-[:ABOUT]->(p_sc4)
MERGE (dc_sc4)-[:APPLIED_POLICY]->(pm03)

// SC-05 Samantha Lee — standard, Audi A4 (stock=1), 2 views → CHURNED
MERGE (p_sc5:Person {id: 'CUST-ABN-SC-05', name: 'Samantha Lee', segment: 'standard',
  risk_score: 0.38, churn_risk: 0.64, customer_value: 14000, credit_score: 660, months_active: 10, email: 'samantha.l@example.com'})
MERGE (dv_sc5:Device {id: 'DEV-ABN-SC-05', type: 'Mobile', os: 'iOS'})
MERGE (ss_sc5:Session {id: 'SESS-ABN-SC-05', is_authenticated: false, start_time: datetime('2026-03-10T16:00:00Z')})
MERGE (p_sc5)-[:LOGGED_IN_FROM]->(dv_sc5)
MERGE (dv_sc5)-[:INITIATED]->(ss_sc5)
MERGE (vh_sc5:BrowsedVehicle {vin: 'VIN-SCAR-A2'})
MERGE (ss_sc5)-[:VIEWED {count: 2, duration_sec: 600}]->(vh_sc5)
MERGE (dc_sc5:Decision {id: 'DEC-ABN-SC-05', action: 'SCARCITY_ALERT', confidence: 0.88,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-10T19:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_sc5:DecisionContext {id: 'DCX-ABN-SC-05', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.38, notes: 'Low-intent visitor — scarcity alert insufficient to convert'})
MERGE (dc_sc5)-[:HAS_CONTEXT]->(dx_sc5)
MERGE (dc_sc5)-[:ABOUT]->(p_sc5)
MERGE (dc_sc5)-[:APPLIED_POLICY]->(pm03);

// ── COHORT 4: VIP_SHOWROOM_INVITE — Physical-Digital Bridge (4 CONVERTED, 1 CHURNED) ──
// Pattern: 1+ test drive + 1–3 views (views < 4 prevents Rule 1 from firing) + no calculator
MERGE (pm04:Policy {id: 'POL-MAR-04'})
MERGE (dla4:Dealership {id: 'DLR-LA-01'})
MERGE (dny4:Dealership {id: 'DLR-NY-01'})
MERGE (dchi4:Dealership {id: 'DLR-CHI-01'})
MERGE (dmia4:Dealership {id: 'DLR-MIA-01'})

// VIP-01 Nathan Ford — premium, BMW X5, 2 views, 1 test drive → CONVERTED
MERGE (p_vip1:Person {id: 'CUST-ABN-VIP-01', name: 'Nathan Ford', segment: 'premium',
  risk_score: 0.16, churn_risk: 0.73, customer_value: 46000, credit_score: 758, months_active: 44, email: 'nathan.f@example.com'})
MERGE (dv_vip1:Device {id: 'DEV-ABN-VIP-01', type: 'Mobile', os: 'iOS'})
MERGE (ss_vip1:Session {id: 'SESS-ABN-VIP-01', is_authenticated: true, start_time: datetime('2026-02-14T10:00:00Z')})
MERGE (p_vip1)-[:LOGGED_IN_FROM]->(dv_vip1)
MERGE (dv_vip1)-[:INITIATED]->(ss_vip1)
MERGE (vh_vip1:BrowsedVehicle {vin: 'VIN-BMWX5-001'})
MERGE (ss_vip1)-[:VIEWED {count: 2, duration_sec: 800}]->(vh_vip1)
MERGE (vi_vip1:PhysicalVisit {id: 'VISIT-ABN-VIP-01', date: datetime('2026-02-14T13:00:00Z'), duration_min: 85, activity: 'Test Drive'})
MERGE (p_vip1)-[:TOOK_TEST_DRIVE]->(vi_vip1)
MERGE (vi_vip1)-[:AT_LOCATION]->(dla4)
MERGE (dc_vip1:Decision {id: 'DEC-ABN-VIP-01', action: 'VIP_SHOWROOM_INVITE', confidence: 0.94,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-15T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_vip1:DecisionContext {id: 'DCX-ABN-VIP-01', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.16, notes: 'VIP $500 closing invite accepted — purchased same week'})
MERGE (dc_vip1)-[:HAS_CONTEXT]->(dx_vip1)
MERGE (dc_vip1)-[:ABOUT]->(p_vip1)
MERGE (dc_vip1)-[:APPLIED_POLICY]->(pm04)

// VIP-02 Diana Ross — standard, Toyota Camry, 1 view, 1 test drive → CONVERTED
MERGE (p_vip2:Person {id: 'CUST-ABN-VIP-02', name: 'Diana Ross', segment: 'standard',
  risk_score: 0.29, churn_risk: 0.58, customer_value: 20000, credit_score: 692, months_active: 19, email: 'diana.r@example.com'})
MERGE (dv_vip2:Device {id: 'DEV-ABN-VIP-02', type: 'Mobile', os: 'Android'})
MERGE (ss_vip2:Session {id: 'SESS-ABN-VIP-02', is_authenticated: true, start_time: datetime('2026-02-20T15:00:00Z')})
MERGE (p_vip2)-[:LOGGED_IN_FROM]->(dv_vip2)
MERGE (dv_vip2)-[:INITIATED]->(ss_vip2)
MERGE (vh_vip2:BrowsedVehicle {vin: 'VIN-CAMRY-001'})
MERGE (ss_vip2)-[:VIEWED {count: 1, duration_sec: 400}]->(vh_vip2)
MERGE (vi_vip2:PhysicalVisit {id: 'VISIT-ABN-VIP-02', date: datetime('2026-02-20T11:00:00Z'), duration_min: 50, activity: 'Test Drive'})
MERGE (p_vip2)-[:TOOK_TEST_DRIVE]->(vi_vip2)
MERGE (vi_vip2)-[:AT_LOCATION]->(dchi4)
MERGE (dc_vip2:Decision {id: 'DEC-ABN-VIP-02', action: 'VIP_SHOWROOM_INVITE', confidence: 0.94,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-21T08:30:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_vip2:DecisionContext {id: 'DCX-ABN-VIP-02', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.29, notes: 'Test drive completed — VIP invite bridged to close'})
MERGE (dc_vip2)-[:HAS_CONTEXT]->(dx_vip2)
MERGE (dc_vip2)-[:ABOUT]->(p_vip2)
MERGE (dc_vip2)-[:APPLIED_POLICY]->(pm04)

// VIP-03 George Martin — premium, Audi Q5, 3 views, 2 test drives → CONVERTED
MERGE (p_vip3:Person {id: 'CUST-ABN-VIP-03', name: 'George Martin', segment: 'premium',
  risk_score: 0.11, churn_risk: 0.80, customer_value: 59000, credit_score: 782, months_active: 55, email: 'george.m@example.com'})
MERGE (dv_vip3:Device {id: 'DEV-ABN-VIP-03', type: 'Desktop', os: 'Windows'})
MERGE (ss_vip3:Session {id: 'SESS-ABN-VIP-03', is_authenticated: true, start_time: datetime('2026-03-02T10:00:00Z')})
MERGE (p_vip3)-[:LOGGED_IN_FROM]->(dv_vip3)
MERGE (dv_vip3)-[:INITIATED]->(ss_vip3)
MERGE (vh_vip3:BrowsedVehicle {vin: 'VIN-Q5-002'})
MERGE (ss_vip3)-[:VIEWED {count: 3, duration_sec: 1100}]->(vh_vip3)
MERGE (vi_vip3a:PhysicalVisit {id: 'VISIT-ABN-VIP-03A', date: datetime('2026-02-25T14:00:00Z'), duration_min: 75, activity: 'Test Drive'})
MERGE (vi_vip3b:PhysicalVisit {id: 'VISIT-ABN-VIP-03B', date: datetime('2026-03-02T11:00:00Z'), duration_min: 80, activity: 'Test Drive'})
MERGE (p_vip3)-[:TOOK_TEST_DRIVE]->(vi_vip3a)
MERGE (vi_vip3a)-[:AT_LOCATION]->(dny4)
MERGE (p_vip3)-[:TOOK_TEST_DRIVE]->(vi_vip3b)
MERGE (vi_vip3b)-[:AT_LOCATION]->(dny4)
MERGE (dc_vip3:Decision {id: 'DEC-ABN-VIP-03', action: 'VIP_SHOWROOM_INVITE', confidence: 0.94,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-03-03T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_vip3:DecisionContext {id: 'DCX-ABN-VIP-03', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.11, notes: '2 test drives — closing incentive sealed deal'})
MERGE (dc_vip3)-[:HAS_CONTEXT]->(dx_vip3)
MERGE (dc_vip3)-[:ABOUT]->(p_vip3)
MERGE (dc_vip3)-[:APPLIED_POLICY]->(pm04)

// VIP-04 Hannah White — standard, Honda CR-V, 2 views, 1 test drive → CONVERTED
MERGE (p_vip4:Person {id: 'CUST-ABN-VIP-04', name: 'Hannah White', segment: 'standard',
  risk_score: 0.27, churn_risk: 0.61, customer_value: 21000, credit_score: 698, months_active: 21, email: 'hannah.w@example.com'})
MERGE (dv_vip4:Device {id: 'DEV-ABN-VIP-04', type: 'Mobile', os: 'iOS'})
MERGE (ss_vip4:Session {id: 'SESS-ABN-VIP-04', is_authenticated: true, start_time: datetime('2026-03-08T14:00:00Z')})
MERGE (p_vip4)-[:LOGGED_IN_FROM]->(dv_vip4)
MERGE (dv_vip4)-[:INITIATED]->(ss_vip4)
MERGE (vh_vip4:BrowsedVehicle {vin: 'VIN-CRV-001'})
MERGE (ss_vip4)-[:VIEWED {count: 2, duration_sec: 650}]->(vh_vip4)
MERGE (vi_vip4:PhysicalVisit {id: 'VISIT-ABN-VIP-04', date: datetime('2026-03-08T11:00:00Z'), duration_min: 60, activity: 'Test Drive'})
MERGE (p_vip4)-[:TOOK_TEST_DRIVE]->(vi_vip4)
MERGE (vi_vip4)-[:AT_LOCATION]->(dchi4)
MERGE (dc_vip4:Decision {id: 'DEC-ABN-VIP-04', action: 'VIP_SHOWROOM_INVITE', confidence: 0.94,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-03-09T08:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_vip4:DecisionContext {id: 'DCX-ABN-VIP-04', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.27, notes: 'VIP invite returned customer to dealership — closed'})
MERGE (dc_vip4)-[:HAS_CONTEXT]->(dx_vip4)
MERGE (dc_vip4)-[:ABOUT]->(p_vip4)
MERGE (dc_vip4)-[:APPLIED_POLICY]->(pm04)

// VIP-05 Patrick Quinn — standard, BMW 3 Series, 3 views, 1 test drive → CHURNED
MERGE (p_vip5:Person {id: 'CUST-ABN-VIP-05', name: 'Patrick Quinn', segment: 'standard',
  risk_score: 0.33, churn_risk: 0.67, customer_value: 17000, credit_score: 672, months_active: 14, email: 'patrick.q@example.com'})
MERGE (dv_vip5:Device {id: 'DEV-ABN-VIP-05', type: 'Mobile', os: 'Android'})
MERGE (ss_vip5:Session {id: 'SESS-ABN-VIP-05', is_authenticated: true, start_time: datetime('2026-03-15T13:00:00Z')})
MERGE (p_vip5)-[:LOGGED_IN_FROM]->(dv_vip5)
MERGE (dv_vip5)-[:INITIATED]->(ss_vip5)
MERGE (vh_vip5:BrowsedVehicle {vin: 'VIN-BMW3S-001'})
MERGE (ss_vip5)-[:VIEWED {count: 3, duration_sec: 950}]->(vh_vip5)
MERGE (vi_vip5:PhysicalVisit {id: 'VISIT-ABN-VIP-05', date: datetime('2026-03-14T16:00:00Z'), duration_min: 45, activity: 'Test Drive'})
MERGE (p_vip5)-[:TOOK_TEST_DRIVE]->(vi_vip5)
MERGE (vi_vip5)-[:AT_LOCATION]->(dla4)
MERGE (dc_vip5:Decision {id: 'DEC-ABN-VIP-05', action: 'VIP_SHOWROOM_INVITE', confidence: 0.94,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-16T09:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_vip5:DecisionContext {id: 'DCX-ABN-VIP-05', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.33, notes: 'Invite declined — budget constraints cited'})
MERGE (dc_vip5)-[:HAS_CONTEXT]->(dx_vip5)
MERGE (dc_vip5)-[:ABOUT]->(p_vip5)
MERGE (dc_vip5)-[:APPLIED_POLICY]->(pm04);

// ── COHORT 5: APPROVE / Bounce — Low Intent (1 CONVERTED, 4 CHURNED) ──
// Pattern: 1–2 views + no calculator + no test drive + no trade-in > $5k + normal inventory
// All rules miss → default APPROVE with 0.50 confidence (treated as unqualified bounce)

// LO-01 Amy Johnson — standard, Toyota Camry, 1 view → CONVERTED (organic)
MERGE (p_lo1:Person {id: 'CUST-ABN-LO-01', name: 'Amy Johnson', segment: 'standard',
  risk_score: 0.30, churn_risk: 0.50, customer_value: 15000, credit_score: 675, months_active: 16, email: 'amy.j@example.com'})
MERGE (dv_lo1:Device {id: 'DEV-ABN-LO-01', type: 'Mobile', os: 'iOS'})
MERGE (ss_lo1:Session {id: 'SESS-ABN-LO-01', is_authenticated: false, start_time: datetime('2026-02-18T10:00:00Z')})
MERGE (p_lo1)-[:LOGGED_IN_FROM]->(dv_lo1)
MERGE (dv_lo1)-[:INITIATED]->(ss_lo1)
MERGE (vh_lo1:BrowsedVehicle {vin: 'VIN-CAMRY-001'})
MERGE (ss_lo1)-[:VIEWED {count: 1, duration_sec: 180}]->(vh_lo1)
MERGE (dc_lo1:Decision {id: 'DEC-ABN-LO-01', action: 'APPROVE', confidence: 0.50,
  status: 'COMPLETED', outcome: 'CONVERTED', created_at: datetime('2026-02-18T12:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_lo1:DecisionContext {id: 'DCX-ABN-LO-01', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.30, notes: 'Low-intent session — walked in organically next day'})
MERGE (dc_lo1)-[:HAS_CONTEXT]->(dx_lo1)
MERGE (dc_lo1)-[:ABOUT]->(p_lo1)

// LO-02 Chris Davis — standard, Honda CR-V, 2 views → CHURNED
MERGE (p_lo2:Person {id: 'CUST-ABN-LO-02', name: 'Chris Davis', segment: 'standard',
  risk_score: 0.36, churn_risk: 0.55, customer_value: 13000, credit_score: 665, months_active: 13, email: 'chris.d@example.com'})
MERGE (dv_lo2:Device {id: 'DEV-ABN-LO-02', type: 'Mobile', os: 'Android'})
MERGE (ss_lo2:Session {id: 'SESS-ABN-LO-02', is_authenticated: false, start_time: datetime('2026-02-25T14:00:00Z')})
MERGE (p_lo2)-[:LOGGED_IN_FROM]->(dv_lo2)
MERGE (dv_lo2)-[:INITIATED]->(ss_lo2)
MERGE (vh_lo2:BrowsedVehicle {vin: 'VIN-CRV-001'})
MERGE (ss_lo2)-[:VIEWED {count: 2, duration_sec: 300}]->(vh_lo2)
MERGE (dc_lo2:Decision {id: 'DEC-ABN-LO-02', action: 'APPROVE', confidence: 0.50,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-02-25T16:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_lo2:DecisionContext {id: 'DCX-ABN-LO-02', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.36, notes: 'Bounce session — no re-engagement signal'})
MERGE (dc_lo2)-[:HAS_CONTEXT]->(dx_lo2)
MERGE (dc_lo2)-[:ABOUT]->(p_lo2)

// LO-03 Michelle Lopez — standard, Audi A4, 1 view → CHURNED
MERGE (p_lo3:Person {id: 'CUST-ABN-LO-03', name: 'Michelle Lopez', segment: 'standard',
  risk_score: 0.40, churn_risk: 0.60, customer_value: 12000, credit_score: 658, months_active: 11, email: 'michelle.l@example.com'})
MERGE (dv_lo3:Device {id: 'DEV-ABN-LO-03', type: 'Desktop', os: 'Windows'})
MERGE (ss_lo3:Session {id: 'SESS-ABN-LO-03', is_authenticated: false, start_time: datetime('2026-03-04T11:00:00Z')})
MERGE (p_lo3)-[:LOGGED_IN_FROM]->(dv_lo3)
MERGE (dv_lo3)-[:INITIATED]->(ss_lo3)
MERGE (vh_lo3:BrowsedVehicle {vin: 'VIN-A4-001'})
MERGE (ss_lo3)-[:VIEWED {count: 1, duration_sec: 150}]->(vh_lo3)
MERGE (dc_lo3:Decision {id: 'DEC-ABN-LO-03', action: 'APPROVE', confidence: 0.50,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-04T13:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_lo3:DecisionContext {id: 'DCX-ABN-LO-03', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.40, notes: 'Single page view — no intent signal detected'})
MERGE (dc_lo3)-[:HAS_CONTEXT]->(dx_lo3)
MERGE (dc_lo3)-[:ABOUT]->(p_lo3)

// LO-04 Ryan Murphy — standard, BMW 3 Series, 2 views → CHURNED
MERGE (p_lo4:Person {id: 'CUST-ABN-LO-04', name: 'Ryan Murphy', segment: 'standard',
  risk_score: 0.37, churn_risk: 0.57, customer_value: 11000, credit_score: 662, months_active: 9, email: 'ryan.m@example.com'})
MERGE (dv_lo4:Device {id: 'DEV-ABN-LO-04', type: 'Mobile', os: 'iOS'})
MERGE (ss_lo4:Session {id: 'SESS-ABN-LO-04', is_authenticated: false, start_time: datetime('2026-03-11T16:00:00Z')})
MERGE (p_lo4)-[:LOGGED_IN_FROM]->(dv_lo4)
MERGE (dv_lo4)-[:INITIATED]->(ss_lo4)
MERGE (vh_lo4:BrowsedVehicle {vin: 'VIN-BMW3S-001'})
MERGE (ss_lo4)-[:VIEWED {count: 2, duration_sec: 250}]->(vh_lo4)
MERGE (dc_lo4:Decision {id: 'DEC-ABN-LO-04', action: 'APPROVE', confidence: 0.50,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-11T18:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_lo4:DecisionContext {id: 'DCX-ABN-LO-04', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.37, notes: 'Quick browse — price-checking, no conversion'})
MERGE (dc_lo4)-[:HAS_CONTEXT]->(dx_lo4)
MERGE (dc_lo4)-[:ABOUT]->(p_lo4)

// LO-05 Stephanie Hall — standard, Toyota Camry, 1 view → CHURNED
MERGE (p_lo5:Person {id: 'CUST-ABN-LO-05', name: 'Stephanie Hall', segment: 'standard',
  risk_score: 0.42, churn_risk: 0.63, customer_value: 10000, credit_score: 650, months_active: 8, email: 'stephanie.h@example.com'})
MERGE (dv_lo5:Device {id: 'DEV-ABN-LO-05', type: 'Mobile', os: 'Android'})
MERGE (ss_lo5:Session {id: 'SESS-ABN-LO-05', is_authenticated: false, start_time: datetime('2026-03-18T09:00:00Z')})
MERGE (p_lo5)-[:LOGGED_IN_FROM]->(dv_lo5)
MERGE (dv_lo5)-[:INITIATED]->(ss_lo5)
MERGE (ss_lo5)-[:VIEWED {count: 1, duration_sec: 120}]->(vh_lo1)
MERGE (dc_lo5:Decision {id: 'DEC-ABN-LO-05', action: 'APPROVE', confidence: 0.50,
  status: 'COMPLETED', outcome: 'CHURNED', created_at: datetime('2026-03-18T11:00:00Z'), decision_type: 'ABANDONED_SESSION'})
MERGE (dx_lo5:DecisionContext {id: 'DCX-ABN-LO-05', trigger_event: 'ABANDONED_SESSION',
  utilization_at_time: 0, risk_at_time: 0.42, notes: 'Minimal engagement — treated as unqualified bounce'})
MERGE (dc_lo5)-[:HAS_CONTEXT]->(dx_lo5)
MERGE (dc_lo5)-[:ABOUT]->(p_lo5);
