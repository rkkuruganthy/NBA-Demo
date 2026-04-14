// ============================================================
// NBA Context Graph — Schema
// Neo4j 5.x | APOC enabled
// ============================================================

// --- Constraints (uniqueness + existence) ---

CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT account_id IF NOT EXISTS
FOR (a:Account) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT transaction_id IF NOT EXISTS
FOR (t:Transaction) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT policy_id IF NOT EXISTS
FOR (pol:Policy) REQUIRE pol.id IS UNIQUE;

CREATE CONSTRAINT decision_id IF NOT EXISTS
FOR (d:Decision) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT decision_context_id IF NOT EXISTS
FOR (dc:DecisionContext) REQUIRE dc.id IS UNIQUE;

CREATE CONSTRAINT exception_id IF NOT EXISTS
FOR (e:Exception) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT escalation_id IF NOT EXISTS
FOR (esc:Escalation) REQUIRE esc.id IS UNIQUE;

CREATE CONSTRAINT community_id IF NOT EXISTS
FOR (c:Community) REQUIRE c.id IS UNIQUE;

// --- Outcome & Feedback Loop ---

CREATE CONSTRAINT outcome_id IF NOT EXISTS
FOR (o:Outcome) REQUIRE o.id IS UNIQUE;

// --- Insurance Vertical ---

CREATE CONSTRAINT insurance_policy_id IF NOT EXISTS
FOR (ip:InsurancePolicy) REQUIRE ip.id IS UNIQUE;

CREATE CONSTRAINT claim_id IF NOT EXISTS
FOR (cl:Claim) REQUIRE cl.id IS UNIQUE;

CREATE CONSTRAINT provider_id IF NOT EXISTS
FOR (pr:Provider) REQUIRE pr.id IS UNIQUE;

CREATE CONSTRAINT diagnosis_code_id IF NOT EXISTS
FOR (dc:DiagnosisCode) REQUIRE dc.code IS UNIQUE;

CREATE CONSTRAINT preauth_id IF NOT EXISTS
FOR (pa:PreAuthorization) REQUIRE pa.id IS UNIQUE;

// --- Indexes for query performance ---

CREATE INDEX person_segment IF NOT EXISTS
FOR (p:Person) ON (p.segment);

CREATE INDEX person_risk IF NOT EXISTS
FOR (p:Person) ON (p.risk_score);

CREATE INDEX account_utilization IF NOT EXISTS
FOR (a:Account) ON (a.utilization_pct);

CREATE INDEX decision_action IF NOT EXISTS
FOR (d:Decision) ON (d.action);

CREATE INDEX decision_status IF NOT EXISTS
FOR (d:Decision) ON (d.status);

CREATE INDEX decision_timestamp IF NOT EXISTS
FOR (d:Decision) ON (d.created_at);

CREATE INDEX policy_family IF NOT EXISTS
FOR (pol:Policy) ON (pol.family);

CREATE INDEX escalation_status IF NOT EXISTS
FOR (esc:Escalation) ON (esc.status);

// --- Insurance Indexes ---

CREATE INDEX claim_amount IF NOT EXISTS
FOR (cl:Claim) ON (cl.amount);

CREATE INDEX claim_submitted IF NOT EXISTS
FOR (cl:Claim) ON (cl.submitted_at);

CREATE INDEX provider_risk IF NOT EXISTS
FOR (pr:Provider) ON (pr.risk_score);

CREATE INDEX provider_network IF NOT EXISTS
FOR (pr:Provider) ON (pr.is_in_network);

// --- Outcome Indexes ---

CREATE INDEX outcome_result IF NOT EXISTS
FOR (o:Outcome) ON (o.actual_result);

CREATE INDEX outcome_recorded IF NOT EXISTS
FOR (o:Outcome) ON (o.recorded_at);

// --- E-Commerce Vertical ---

CREATE CONSTRAINT session_id IF NOT EXISTS
FOR (s:Session) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT device_id IF NOT EXISTS
FOR (d:Device) REQUIRE d.id IS UNIQUE;

CREATE INDEX browsed_vehicle_vin IF NOT EXISTS
FOR (bv:BrowsedVehicle) ON (bv.vin);

CREATE CONSTRAINT calc_id IF NOT EXISTS
FOR (fc:FinancingCalculator) REQUIRE fc.id IS UNIQUE;

CREATE CONSTRAINT dealership_id IF NOT EXISTS
FOR (d:Dealership) REQUIRE d.id IS UNIQUE;

CREATE INDEX owned_vehicle_vin IF NOT EXISTS
FOR (ov:OwnedVehicle) ON (ov.vin);

CREATE INDEX valuation_amount IF NOT EXISTS
FOR (val:Valuation) ON (val.amount);
