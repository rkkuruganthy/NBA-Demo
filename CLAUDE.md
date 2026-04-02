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
4. Define: objective, files to change, acceptance criteria, verification steps, boundaries.
5. Implement only approved scope.
6. Verify.
7. Summarize changes + risks.
8. Update state docs.

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
