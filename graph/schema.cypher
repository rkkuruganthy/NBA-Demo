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
