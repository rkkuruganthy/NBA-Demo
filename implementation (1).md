# Next Best Action App with SEED + PAUL + Claude Code + Neo4j

## 1. Objective

Build a **Next Best Action (NBA)** application that moves from **idea → scoped plan → implementation → production-ready MVP** using:

- **SEED** for ideation and structured planning
- **PAUL** for disciplined implementation workflow
- **Claude Code** for planning and coding assistance
- **Antigravity** as the IDE / build environment
- **Neo4j** as the context graph and decision-trace store
- **FastAPI** for backend services
- **Next.js** for frontend UI
- **Docker Compose** for local setup

The first MVP use case is:

- **Credit line increase / retention / escalation recommendation**

---

## 2. Target Architecture

### Core components

1. **Frontend (Next.js)**
   - Analyst dashboard
   - Case intake screen
   - Recommendation panel
   - Decision trace view
   - Similar cases / precedents panel
   - Approval / override / escalation actions

2. **Backend (FastAPI)**
   - Case evaluation API
   - Policy evaluation service
   - Precedent lookup service
   - Decision trace persistence
   - Outcome capture service

3. **Neo4j Context Graph**
   - Customer / account / transaction / policy / decision graph
   - Similar decision retrieval
   - Decision traceability
   - Precedent relationships

4. **Claude Code + PAUL**
   - Plan and implement in controlled slices
   - Maintain project state and progress
   - Produce code with acceptance criteria discipline

5. **SEED**
   - Convert initial idea into strong product / engineering plan
   - Produce `PLANNING.md`

---

## 3. Recommended Repository Structure

```text
nba-context-app/
├── frontend/                    # Next.js UI
├── backend/                     # FastAPI services
├── graph/                       # Cypher schema, seed data, graph queries
├── docs/
│   ├── implementation.md
│   ├── planning.md
│   ├── architecture.md
│   ├── domain-model.md
│   ├── nba-scenarios.md
│   └── prompts.md
├── .paul/
├── .claude/
├── docker-compose.yml
├── README.md
└── .env.example
```

---

## 4. Environment Setup

### 4.1 Prerequisites

Install the following on your machine:

- Node.js 18+
- npm or pnpm
- Python 3.11+
- Docker Desktop
- Git
- Neo4j Browser access via Docker
- Claude Code CLI
- Antigravity IDE with Claude support enabled

### 4.2 Install Claude Code

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude
```

Authenticate when prompted.

### 4.3 Install SEED

```bash
npm i -g @chrisai/seed
```

### 4.4 Install PAUL

From inside the repo root:

```bash
npx paul-framework
```

### 4.5 Create the project folder

```bash
mkdir nba-context-app
cd nba-context-app
git init
mkdir frontend backend graph docs
```

---

## 5. Initial Project Bootstrap

Create these starter files:

### 5.1 `docker-compose.yml`

Services:
- `neo4j`
- `backend`
- `frontend`

### 5.2 `.env.example`

Suggested variables:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
BACKEND_PORT=8000
FRONTEND_PORT=3000
ANTHROPIC_API_KEY=your_key_here
```

### 5.3 Backend bootstrap

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn neo4j pydantic python-dotenv
```

### 5.4 Frontend bootstrap

```bash
cd ../frontend
npx create-next-app@latest .
```

Choose:
- TypeScript: Yes
- App Router: Yes
- ESLint: Yes
- Tailwind: Yes

---

## 6. Docker Setup Plan

Your local environment should support full development using Docker Compose.

### Services to define

#### Neo4j
- Image: `neo4j:latest`
- Expose ports:
  - `7474` for browser
  - `7687` for bolt
- Mount persistent volume
- Enable APOC if needed later

#### Backend
- Build from `backend/`
- Expose `8000`
- Load env variables
- Connect to Neo4j

#### Frontend
- Build from `frontend/`
- Expose `3000`
- Connect to backend API

---

## 7. Graph Model for MVP

### Nodes

```text
Person
Account
Transaction
Policy
Decision
DecisionContext
Exception
Escalation
Community
```

### Relationships

```text
(Person)-[:OWNS]->(Account)
(Decision)-[:ABOUT]->(Person)
(Decision)-[:ABOUT]->(Account)
(Decision)-[:APPLIED_POLICY]->(Policy)
(Decision)-[:HAS_CONTEXT]->(DecisionContext)
(Decision)-[:GRANTED_EXCEPTION]->(Exception)
(Decision)-[:TRIGGERED]->(Escalation)
(Decision)-[:PRECEDENT_FOR]->(Decision)
(Decision)-[:INFLUENCED]->(Decision)
(Decision)-[:CAUSED]->(Decision)
(Decision)-[:IN_COMMUNITY]->(Community)
```

### Key graph goals

- Persist decisions as first-class graph entities
- Store why a recommendation happened
- Link to policies used
- Link to prior similar decisions
- Support analyst override and outcome feedback

---

## 8. MVP Functional Scope

### Input signals

- Customer profile
- Account profile
- Payment / utilization indicators
- Trigger event
- Existing policy thresholds
- Prior historical decisions

### Outputs

- Recommended action
- Confidence score
- Applied policies
- Similar prior cases
- Explanation narrative
- Human review requirement

### Supported actions

- APPROVE
- DECLINE
- ESCALATE_FOR_REVIEW
- OFFER_RETENTION
- REQUEST_DOCUMENTS

---

## 9. Step-by-Step Implementation Plan

## Phase 0 — Planning with SEED

### Goal
Create a strong `PLANNING.md` before writing meaningful code.

### Steps

1. Open the repo in Antigravity.
2. Start Claude Code.
3. Run:

```text
/seed
```

4. Use the prompt in the next section.
5. Review generated plan.
6. Refine until you have:
   - personas
   - journeys
   - domain model
   - graph design
   - APIs
   - UI screens
   - phased roadmap
   - acceptance criteria

---

## Phase 1 — Foundation Scaffold

### Goal
Create the technical skeleton without business logic.

### Deliverables

- Next.js app scaffold
- FastAPI app scaffold
- Docker Compose
- Neo4j connectivity
- Health check APIs
- Base docs

### Steps

1. Initialize PAUL:

```text
/paul:init
```

2. Create the first implementation plan.
3. Let Claude implement only the skeleton.
4. Run locally and verify all services come up.
5. Update docs and unify state.

---

## Phase 2 — Graph Schema and Seed Data

### Goal
Implement graph schema and initial sample cases.

### Deliverables

- `graph/schema.cypher`
- `graph/seed.cypher`
- Graph constraints / indexes
- Backend graph connection service
- Sample people / accounts / decisions / policies

### Steps

1. Create Cypher schema.
2. Add indexes and constraints.
3. Load seed data.
4. Add backend script to initialize database.
5. Verify with Neo4j Browser.

---

## Phase 3 — Deterministic Recommendation Engine

### Goal
Create the first version of NBA evaluation using deterministic logic.

### Deliverables

- `POST /cases/evaluate`
- Rules-based policy evaluator
- Decision persistence in Neo4j
- Response payload with explanation inputs

### Suggested first rules

- High utilization + poor payment history → DECLINE
- High customer value + moderate risk → ESCALATE_FOR_REVIEW
- High churn risk + eligible profile → OFFER_RETENTION

### Steps

1. Define Pydantic request / response models.
2. Implement evaluation service.
3. Persist decision + context in graph.
4. Return structured response.

---

## Phase 4 — Precedent Retrieval

### Goal
Find similar historical decisions from Neo4j.

### Deliverables

- Similar case lookup query
- `GET /decisions/{id}/precedents`
- Link current decision to prior decisions

### Retrieval logic

Search prior decisions by:
- customer segment
- utilization range
- risk category
- trigger type
- same policy family
- similar outcome

---

## Phase 5 — Analyst UI

### Goal
Expose recommendations and explanations in a business-friendly UI.

### Screens

1. Case Intake
2. Recommendation Panel
3. Applied Policies
4. Similar Cases
5. Decision Trace Timeline
6. Approve / Override / Escalate controls

### Deliverables

- Form-driven intake page
- Recommendation detail card
- Precedent side panel
- Policy side panel
- Action buttons

---

## Phase 6 — Human in the Loop

### Goal
Allow analysts to approve, override, or escalate.

### Deliverables

- `POST /decisions/{id}/approve`
- `POST /decisions/{id}/override`
- `POST /decisions/{id}/escalate`
- Override rationale capture
- Escalation record

### Steps

1. Add analyst action APIs.
2. Update graph relationships.
3. Track rationale and timestamps.
4. Reflect in UI.

---

## Phase 7 — Outcome Capture and Learning Loop

### Goal
Capture actual outcomes and feed graph memory.

### Deliverables

- `POST /decisions/{id}/outcome`
- Outcome nodes / attributes
- Update precedent usefulness
- Historical reporting hooks

### Steps

1. Add outcome model.
2. Persist outcome to graph.
3. Link decision to result.
4. Use outcomes later for smarter retrieval.

---

## Phase 8 — AI Narrative Enrichment

### Goal
Use Claude only after deterministic evaluation is complete.

### Deliverables

- Analyst-friendly explanation narrative
- Override draft rationale suggestion
- Summary explanation for trace screen

### Rule
Do **not** let the LLM decide the action in v1.
Use the LLM only to enrich explanation from structured results.

---

## 10. Core API Design

### `POST /cases/evaluate`
Evaluate a case and generate recommendation.

### `GET /cases/{id}`
Fetch stored case and decision summary.

### `GET /decisions/{id}/trace`
Return full decision trace.

### `GET /decisions/{id}/precedents`
Return similar prior decisions.

### `POST /decisions/{id}/approve`
Approve the recommendation.

### `POST /decisions/{id}/override`
Override recommendation with rationale.

### `POST /decisions/{id}/escalate`
Escalate decision.

### `POST /decisions/{id}/outcome`
Capture final business outcome.

---

## 11. Prompt Pack for Claude Code

## 11.1 SEED ideation prompt

```text
/seed

I want to build a financial-services Next Best Action application using a context-graph architecture.

The system should:
- ingest customer, account, and event signals
- apply deterministic business and risk policies
- retrieve similar prior decisions from Neo4j
- recommend a next best action
- explain why the action is recommended
- support human approval, override, and escalation
- store the full decision trace for future precedent and learning

Preferred stack:
- Next.js frontend
- FastAPI backend
- Neo4j graph database
- Docker for local development
- Claude Code + PAUL for disciplined implementation

First MVP use case:
Credit line increase / retention / escalation recommendation

Please guide me through ideation and generate a strong PLANNING.md with:
- personas
- user journeys
- domain model
- graph schema
- APIs
- UI screens
- phased roadmap
- acceptance criteria
- non-functional requirements
```

---

## 11.2 SEED graduation prompt

```text
/seed launch
```

If needed, use:

```text
Graduate this project from ideation into implementation mode.
Initialize the project so it can be executed using PAUL.
Preserve the planning outputs and convert them into implementation-ready artifacts.
```

---

## 11.3 PAUL foundation planning prompt

```text
/paul:plan

Create the first implementation plan for the MVP foundation only.
Do not implement business logic yet.

Scope:
- repository scaffolding
- Docker Compose
- Neo4j connectivity
- FastAPI backend skeleton
- Next.js frontend shell
- environment configuration
- sample seed initialization hooks
- verification steps
- acceptance criteria
- boundaries
```

---

## 11.4 PAUL graph schema planning prompt

```text
/paul:plan

Create a plan for the graph schema and seed data.
Include:
- graph nodes and relationships
- constraints and indexes
- schema.cypher
- seed.cypher
- initialization script
- test verification steps

Use these entities:
- Person
- Account
- Transaction
- Policy
- Decision
- DecisionContext
- Exception
- Escalation
- Community
```

---

## 11.5 PAUL recommendation engine prompt

```text
/paul:plan

Create the MVP recommendation engine plan.
Inputs:
- customer profile
- account state
- trigger event
- policy data
- similar historical decisions

Outputs:
- recommended_action
- confidence
- explanation_inputs
- applied_policies
- precedent_cases
- requires_human_review

Use deterministic rules first.
Do not use the LLM to choose actions.
Use the LLM only later for narrative explanation.
```

---

## 11.6 PAUL UI prompt

```text
/paul:plan

Create the plan for the analyst UI.
Screens:
- case intake
- recommendation panel
- applied policies
- similar cases
- decision trace timeline
- approve / override / escalate actions

Include component structure, API integrations, and acceptance criteria.
```

---

## 11.7 Implementation execution prompt

```text
Read .paul project files first.
Do not start coding until you summarize the plan.
Implement only the smallest approved slice.
Do not expand scope.
After implementation:
- run tests
- verify acceptance criteria
- summarize what changed
- update state artifacts
```

---

## 11.8 Unify / close-out prompt

```text
Compare implemented work against the approved plan.
List:
- completed scope
- deferred items
- risks
- files changed
- next recommended slice
Then update SUMMARY.md and STATE.md.
```

---

## 12. Suggested Build Order

1. Planning with SEED
2. Graduate to PAUL
3. Repo scaffolding
4. Docker + Neo4j + backend + frontend
5. Graph schema
6. Seed data
7. Case evaluation endpoint
8. Deterministic policy engine
9. Precedent retrieval
10. UI panels
11. Human approval workflow
12. Outcome capture
13. AI narrative enrichment
14. Observability / auth / hardening

---

## 13. Recommended Acceptance Criteria by Milestone

### Milestone 1 — Foundation
- App boots locally with Docker
- Backend health endpoint works
- Frontend loads
- Neo4j accessible

### Milestone 2 — Graph
- Schema creates successfully
- Seed data loads successfully
- Sample queries return expected nodes and relationships

### Milestone 3 — Recommendation Engine
- Evaluate endpoint returns valid action
- Decision is persisted in graph
- Policies are linked to decision

### Milestone 4 — Precedents
- Prior similar decisions are returned
- Current decision links to precedent cases

### Milestone 5 — UI
- Analyst can submit case
- Recommendation displays correctly
- Trace and policy panels show meaningful data

### Milestone 6 — HITL
- Analyst can approve / override / escalate
- Rationale is persisted

### Milestone 7 — Outcome
- Final outcome can be stored
- Outcome becomes part of future context

---

## 14. What to Avoid in v1

Do not start with:

- pure LLM decisioning
- complex multi-agent autonomy
- many business scenarios at once
- advanced embeddings before graph basics work
- over-engineered microservices for MVP

Keep v1 focused on **one clear NBA scenario** and make it explainable.

---

## 15. Final Recommendation

Use this operating pattern:

- **SEED** → define the product and engineering plan
- **PAUL** → implement in strict slices
- **Neo4j** → store explainable decision context and precedent
- **Claude Code** → accelerate plan-driven delivery
- **Antigravity** → act as the daily implementation cockpit

This gives you a disciplined path from ideation to a production-shaped MVP without turning the build into uncontrolled vibe coding.


---

## 16. CLAUDE.md (Production-Ready Project Instructions)

Create a file at repo root: `CLAUDE.md`

```md
# CLAUDE.md

## Project
Financial-services Next Best Action (NBA) application.

Primary goal:
Recommend the next best action using deterministic rules, Neo4j context graph, and human-in-the-loop.

Initial MVP use case:
- credit line increase
- retention offer
- escalation for analyst review

Stack:
- Next.js (frontend)
- FastAPI (backend)
- Neo4j (graph)
- Docker Compose (local)

## Non-Negotiable Architecture Rules
1. Deterministic rules select the action.
2. Neo4j stores context, policies, precedents, audit trail.
3. LLM MUST NOT choose actions in v1.
4. LLM may only generate explanations after deterministic output.
5. Human approval/override/escalation is mandatory.
6. Do not introduce new frameworks without approval.

## Working Method (MANDATORY)
For every task:
1. Read docs + state files first.
2. Summarize understanding.
3. Propose smallest implementation slice.
4. Define:
   - objective
   - files to change
   - acceptance criteria
   - verification steps
   - boundaries
5. Implement only approved scope.
6. Verify.
7. Summarize changes + risks.
8. Update state docs.

## Files to Read First
- docs/implementation.md
- docs/planning.md
- docs/architecture.md
- docs/domain-model.md
- .paul/STATE.md
- .paul/SUMMARY.md

## Coding Rules
- TypeScript (frontend)
- Typed Pydantic models (backend)
- Small modular services
- No duplicated business rules
- Graph queries isolated in repository layer
- No placeholder logic without TODO

## API Rules
Each endpoint must include:
- request model
- response model
- validation
- error handling
- example payload

## Testing Rules
- Add/update tests for non-trivial changes
- Explicitly state what was verified

## Neo4j Rules
Graph must capture:
- why decision happened
- policies applied
- precedent decisions
- human actions (approve/override/escalate)
- final outcome

## UI Rules
Screens:
- case intake
- recommendation panel
- policies
- precedents
- decision trace
- approval actions

## Safety
- No destructive changes without explanation
- No secrets in code
- Confirm before schema reset

## Response Format (STRICT)
### Understanding
...
### Plan
...
### Files to Change
...
### Acceptance Criteria
...
### Implementation Notes
...
### Verification
...
### Risks / Follow-ups
...

## Key Principles
- Optimize for determinism and auditability
- Do not confuse decision logic with explanation logic
```

---

## 17. docs/prompts.md (Reusable Prompt Library)

Create file: `docs/prompts.md`

```md
# Prompt Library for Claude Code + PAUL

## 1. Planning a Slice

/paul:plan

Create the smallest coherent implementation plan.

Include:
- objective
- files to change
- acceptance criteria
- verification steps
- boundaries

Do NOT write code yet.

---

## 2. Implementing a Slice

Read project docs and PAUL state first.

Implement ONLY the approved slice.

Rules:
- do not expand scope
- keep changes minimal
- follow coding rules

After implementation:
- verify behavior
- list files changed
- summarize outcome

---

## 3. Code Review Prompt

Review the following code for:
- correctness
- adherence to architecture rules
- duplication of logic
- missing validation
- missing error handling
- test coverage gaps

Provide:
- issues
- suggested fixes
- risk level

---

## 4. Test Generation Prompt

Generate tests for the following module.

Include:
- happy path
- edge cases
- failure scenarios

Use realistic input data.

Do not mock unnecessarily.

---

## 5. Documentation Update Prompt

Update documentation for the recent change.

Include:
- what changed
- why it changed
- API changes (if any)
- example usage

Keep it concise and accurate.

---

## 6. Debugging Prompt

Analyze the issue:
- summarize problem
- identify root cause
- propose fix

Then:
- implement minimal fix
- verify resolution

---

## 7. Graph Query Prompt

Create a Cypher query for:
- retrieving similar decisions
- linking precedent cases

Ensure:
- efficient traversal
- indexed fields used
- readable structure

---

## 8. Strict Execution Guardrail Prompt

Before coding:
- restate scope
- confirm boundaries

During coding:
- do not add features outside scope

After coding:
- verify only scoped changes were made

---

## 9. Explanation Generation Prompt (LLM Safe Use)

Convert structured decision output into a clear explanation.

Input:
- recommended action
- applied policies
- precedent cases

Output:
- concise explanation
- analyst-friendly language

Do NOT change the decision.
```

---

## 18. Final Note

Adding `CLAUDE.md` + `docs/prompts.md` ensures:

- consistent Claude behavior
- controlled PAUL execution
- minimal scope creep
- strong architectural discipline

This is critical for building a **production-grade, explainable NBA system** rather than a loosely generated prototype.

