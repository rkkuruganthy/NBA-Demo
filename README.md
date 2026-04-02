# 🧠 NBA Context Engine — Next Best Action Decision Intelligence

> **A production-grade, graph-powered Decision Intelligence platform** that replaces hardcoded rule engines with real-time Cypher graph traversals across 10,000+ entities in Financial Services, AML/Fraud, and Healthcare.

---

## 🎯 What Is This?

The **NBA Context Engine** is a full-stack demonstration of how enterprise decision-making can be transformed from opaque, siloed "black box" systems into **transparent, auditable, graph-driven intelligence** — purpose-built for CIO and executive audiences.

Unlike traditional NBA (Next Best Action) engines that pull from flat APIs and lose decision context immediately, this system:

1. **Persists every decision as a node** in a Neo4j knowledge graph
2. **Traverses actual graph relationships** (not hardcoded rules) to extract features
3. **Provides a full audit trail** — every decision links back to the policies, context, and graph features that produced it
4. **Supports interactive negotiation** — customers can Accept, Counter, or Decline recommendations
5. **Uses AI synthesis** (GPT-4o-mini) strictly as a translator — the LLM **never** makes the decision

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    NBA Context Engine                              │
│                                                                    │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   Next.js    │    │    FastAPI        │    │    Neo4j 5.x     │  │
│  │   Frontend   │◄──►│    Backend        │◄──►│    Knowledge     │  │
│  │   (Port 3002)│    │    (Port 8001)    │    │    Graph         │  │
│  └─────────────┘    └──────────────────┘    └──────────────────┘  │
│       │                     │                        │             │
│       │              ┌──────┴──────┐          ┌──────┴──────┐     │
│       │              │ Policy      │          │ 56,308      │     │
│       │              │ Engine      │          │ Nodes       │     │
│       │              │ (Cypher     │          │ 10,006      │     │
│       │              │  Traversal) │          │ Users       │     │
│       │              └──────┬──────┘          └─────────────┘     │
│       │              ┌──────┴──────┐                               │
│       │              │ LLM         │                               │
│       │              │ Synthesizer │                               │
│       │              │ (GPT-4o)    │                               │
│       │              └─────────────┘                               │
│       │                                                            │
│  ┌────┴────────────────────────────────────────────────────────┐   │
│  │  Context Explorer UI                                        │   │
│  │  • Interactive Graph Visualization (Neo4j NVL)              │   │
│  │  • Real-time Decision Trace & Engine Log                    │   │
│  │  • Negotiation Loop (Accept / Counter / Decline)            │   │
│  │  • Searchable 10K User Population                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (optional — for AI narrative synthesis)

### 1. Clone & Configure
```bash
git clone <repo-url>
cd NBA-Demo
cp .env.example .env
# (Optional) Add your OpenAI API key to .env
```

### 2. Start Services
```bash
docker compose up -d
```

This spins up:
| Service | Port | Description |
|---------|------|-------------|
| `nba-neo4j` | 7474 (browser) / 7687 (bolt) | Neo4j 5.x Knowledge Graph |
| `nba-backend` | 8001 | FastAPI Decision Engine |
| `nba-frontend` | 3002 | Next.js Explorer UI |

### 3. Seed the Population (10,000 Users)
```bash
docker exec -it nba-backend python seed_10k_population.py
```

This creates **56,308 nodes** across 3 industries:
- **3,502 Financial** users (Affluent / Mass Market / Subprime)
- **3,002 AML** users (Clean / Suspicious / Confirmed Fraud Ring)
- **3,502 Healthcare** patients (Compliant / At Risk / Critical)
- **6 Hero profiles** for curated demo scenarios
- **9 deterministic policies**

### 4. Open the Explorer
Navigate to **http://localhost:3002/explorer**

---

## 📊 Three Industry Scenarios

### 💳 Financial Services — Credit Limit Increase
| Graph Path | Feature Extracted | Decision Logic |
|---|---|---|
| `Person → Account` | `utilization_pct`, `dpd` | High util + 0 DPD + travel intent → APPROVE |
| `Account → Transaction → Entity` | `intent_markers` | 30+ DPD → Hard DECLINE |
| `Person → Context` | `risk_score`, `credit_score` | Mixed signals → ESCALATE with counter-offer |

### 🚨 AML / Fraud Detection — Suspicious Wire Transfer
| Graph Path | Feature Extracted | Decision Logic |
|---|---|---|
| `Person → Device ← Fraudster` | `shared_with_threat` | Shared device + high-risk jurisdiction → BLOCK + SAR |
| `Account → Transaction → Destination` | `dest_jurisdiction`, `wire_amount` | $5K+ to high-risk country → ESCALATE |
| `Person → Context` | `risk_score` | Clean profile, domestic wire → APPROVE |

### 🏥 Healthcare — Care Gap Review
| Graph Path | Feature Extracted | Decision Logic |
|---|---|---|
| `Patient → Encounter → Diagnosis` | `diag_code`, `is_critical` | Critical diagnosis + 7+ day gap → URGENT INTERVENTION |
| `Diagnosis → Prescription → CareGap` | `care_gap_days`, `rx_status` | Chronic + 3-7 day gap → Schedule follow-up |
| `Patient → Context` | `risk_tier` | Compliant, fulfilled Rx → APPROVE (monitor) |

---

## 🔑 Key Features

### Graph-Traversal Policy Engine
Every decision is made by querying actual Neo4j relationships — **zero hardcoded customer IDs**. The engine runs Cypher queries to extract features, then applies deterministic rules on those features.

### Interactive Negotiation Loop
Full lifecycle support: `EVALUATE → COUNTER-OFFER → ACCEPT/DECLINE`. Each negotiation step is persisted as a `NegotiationStep` node in the graph with a complete audit trail.

### Population-Based Confidence Scoring
Confidence scores factor in how similar decisions were made across the 10K population — providing data-driven intelligence rather than arbitrary thresholds.

### AI Narrative Synthesis (LLM as Translator, Not Decider)
After the deterministic engine makes the decision, we pass the full graph context to GPT-4o-mini to generate a human-readable explanation. The LLM **never influences** the actual decision.

### Decision Reasoning on Graph Nodes
Every Decision node stores:
- `reasoning` — Human-readable explanation of why the decision was made
- `graph_features` — Exact feature values extracted from the graph
- `policies_applied` — Which policy rules fired
- `decision_type` — The trigger event type

### Searchable User Explorer
Browse and search across all 10,000+ users with industry filters (💳 Financial, 🚨 AML, 🏥 Healthcare) and real-time Neo4j-backed search.

---

## 📁 Project Structure

```
NBA-Demo/
├── backend/
│   ├── main.py                          # FastAPI app + /customers endpoints
│   ├── app/
│   │   ├── db.py                        # Neo4j connection pool
│   │   ├── config.py                    # Environment configuration
│   │   ├── models/
│   │   │   └── case.py                  # Pydantic models (Request/Response/Negotiation)
│   │   ├── routers/
│   │   │   ├── cases.py                 # /cases/evaluate + /negotiate endpoints
│   │   │   ├── decisions.py             # Decision CRUD
│   │   │   └── explorer.py             # /explorer/customer/{id} graph data
│   │   └── services/
│   │       ├── policy_engine.py         # ★ Graph-traversal Cypher feature extraction
│   │       ├── decision_service.py      # Orchestrates evaluation + persistence
│   │       ├── llm_service.py           # AI narrative synthesis (GPT-4o-mini)
│   │       ├── precedent_service.py     # Historical precedent matching
│   │       └── graph_init.py            # Graph schema initialization
│   ├── seed_10k_population.py           # ★ 10K realistic user seeding script
│   ├── seed_showcase.py                 # Hero profile seeding
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── explorer/page.tsx        # ★ Main Context Explorer (search + evaluation)
│   │   │   ├── dashboard/page.tsx       # Dashboard overview
│   │   │   ├── decisions/page.tsx       # Decision history
│   │   │   ├── policies/page.tsx        # Policy management
│   │   │   └── cases/                   # Case detail views
│   │   └── components/
│   │       ├── GraphView.tsx            # ★ Neo4j NVL graph visualization
│   │       └── Sidebar.tsx              # Navigation sidebar
│   └── Dockerfile
├── docker-compose.yml                   # Full stack orchestration
├── NBA-Demo-Technical-Doc.html          # CIO-ready technical presentation
└── ARCHITECTURE.md                      # Architecture documentation
```

---

## 🛡️ Why This Matters for Regulated Industries

| Challenge | Traditional NBA | Context Graph Engine |
|---|---|---|
| **Audit Trail** | Decision output only ("The What") | Full graph trace ("The What + The Why") |
| **State Preservation** | Lost after API response | Permanently embedded in graph |
| **Explainability** | Black box | Click any Decision node → see exact reasoning |
| **Scalability** | Hardcoded rules per customer | 10K+ users, same engine |
| **AI Safety** | LLM makes decisions | LLM only translates; engine decides |
| **Negotiation** | One-shot decision | Multi-round counter-offer lifecycle |

---

## 🧪 API Testing

```bash
# Financial — Affluent customer with travel intent
curl -X POST http://localhost:8001/cases/evaluate \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"FIN-00050","trigger_event":"CREDIT_LIMIT_REVIEW"}'

# AML — Suspicious wire transfer
curl -X POST http://localhost:8001/cases/evaluate \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"AML-02500","trigger_event":"FRAUD_DETECTION"}'

# Healthcare — Critical care gap
curl -X POST http://localhost:8001/cases/evaluate \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"MED-03200","trigger_event":"CARE_GAP_REVIEW"}'

# Population count
curl http://localhost:8001/customers/count

# Search users
curl "http://localhost:8001/customers?search=Sarah&industry=financial&limit=10"
```

---

## 📄 License

Proprietary — Viztral Technologies. For demonstration purposes only.
