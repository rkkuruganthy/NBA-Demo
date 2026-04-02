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
