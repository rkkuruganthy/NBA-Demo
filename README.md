# 🧠 NBA Context Engine — Next Best Action Decision Intelligence

> **A production-grade, graph-powered Decision Intelligence platform** that replaces hardcoded rule engines with real-time Cypher graph traversals across 10,000+ entities in Financial Services, AML/Fraud, Healthcare, Insurance Claims, and Automotive E-Commerce.

---

## 🎯 What Is This?

The **NBA Context Engine** is a full-stack demonstration of how enterprise decision-making can be transformed from opaque, siloed "black box" systems into **transparent, auditable, graph-driven intelligence** — purpose-built for CIO and executive audiences.

Unlike traditional NBA (Next Best Action) engines that pull from flat APIs and lose decision context immediately, this system:

1. **Persists every decision as a node** in a Neo4j knowledge graph
2. **Traverses actual graph relationships** (not hardcoded rules) to extract features
3. **Provides a full audit trail** — every decision links back to the policies, context, and graph features that produced it
4. **Supports interactive negotiation** — customers can Accept, Counter, or Decline recommendations
5. **Uses AI synthesis** (GPT-4o-mini) strictly as a translator — the LLM **never** makes the decision
6. **Synthesizes omnichannel signals** — web, mobile, and physical touchpoints are unified in the graph to produce high-precision interventions
7. **Works offline** — includes a local narrative builder that generates structured explanations when OpenAI is unreachable

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    NBA Context Engine                              │
│                                                                    │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   Next.js    │    │    FastAPI        │    │    Neo4j 5.26    │  │
│  │   Frontend   │◄──►│    Backend        │◄──►│    Knowledge     │  │
│  │   (Port 3002)│    │    (Port 8001)    │    │    Graph         │  │
│  └─────────────┘    └──────────────────┘    └──────────────────┘  │
│       │                     │                        │             │
│       │              ┌──────┴──────┐          ┌──────┴──────┐     │
│       │              │ Policy      │          │ 56,308+     │     │
│       │              │ Engine      │          │ Nodes       │     │
│       │              │ (5 Cypher   │          │ 10,006      │     │
│       │              │  Extractors)│          │ Users       │     │
│       │              └──────┬──────┘          └─────────────┘     │
│       │              ┌──────┴──────┐                               │
│       │              │ LLM         │                               │
│       │              │ Synthesizer │                               │
│       │              │ (GPT-4o /   │                               │
│       │              │  Offline)   │                               │
│       │              └─────────────┘                               │
│       │                                                            │
│  ┌────┴────────────────────────────────────────────────────────┐   │
│  │  Context Explorer UI                                        │   │
│  │  • Interactive Graph Visualization (Neo4j NVL)              │   │
│  │  • Real-time Decision Trace & Engine Log                    │   │
│  │  • Negotiation Loop (Accept / Counter / Decline)            │   │
│  │  • Searchable 10K User Population                           │   │
│  │  • Omnichannel Node Types (Session, Device, Calculator,     │   │
│  │    PhysicalVisit, BrowsedVehicle, Dealership, Valuation)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Graph Database** | Neo4j 5.26 Community + APOC | Knowledge graph persistence, Cypher-based feature extraction |
| **Backend Engine** | Python 3.12 / FastAPI | Deterministic policy engine, decision orchestration, REST API |
| **Frontend UI** | Next.js 16 / React 19 | Context Explorer, Graph Visualization, Negotiation UI |
| **Graph Visualization** | @neo4j-nvl/react 1.1 | Canvas-based interactive graph rendering |
| **Styling** | TailwindCSS 4 | Responsive dark-mode UI with glassmorphism design |
| **AI Narrative** | OpenAI GPT-4o-mini | Decision explanation synthesis (translator only, not decider) |
| **Offline Fallback** | Local Narrative Builder | Structured explanations when OpenAI is unavailable |
| **Orchestration** | Docker Compose | Full-stack container orchestration |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (optional — for AI narrative synthesis; falls back to local builder)

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
| `nba-neo4j` | 7474 (browser) / 7687 (bolt) | Neo4j 5.26 Knowledge Graph |
| `nba-backend` | 8001 | FastAPI Decision Engine |
| `nba-frontend` | 3002 | Next.js Explorer UI |

### 3. Initialize the Graph
```bash
# Initialize schema + seed data
curl -X POST http://localhost:8001/graph/init
```

### 4. Seed the Population (10,000 Users)
```bash
docker exec -it nba-backend python seed_10k_population.py
```

This creates **56,308+ nodes** across 5 industries:
- **3,502 Financial** users (Affluent / Mass Market / Subprime)
- **3,002 AML** users (Clean / Suspicious / Confirmed Fraud Ring)
- **3,502 Healthcare** patients (Compliant / At Risk / Critical)
- **2,000 E-Commerce** visitors (Anonymous Browsing & Conversion paths)
- **25 Historical E-Commerce Cohorts** (powers population-based confidence scoring)
- **10 Hero profiles** for curated demo scenarios (including omnichannel personas)
- **17+ deterministic policies** across Credit, Fraud, Clinical, Claims, and MarTech families

### 5. Open the Explorer
Navigate to **http://localhost:3002/explorer**

---

## 📊 Five Industry Scenarios

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

### 🛡️ Insurance Claims — Underwriting & Fraud
| Graph Path | Feature Extracted | Decision Logic |
|---|---|---|
| `Person → Claim → Provider` | `is_duplicate_claim`, `provider_risk_score` | Duplicate claim within 30 days → DENY + SIU referral |
| `Claim → DiagnosisCode` | `claim_amount`, `is_emergency` | $50K+ from high-risk provider → ESCALATE |
| `Claim → PreAuthorization` | `has_preauthorization` | Emergency OON → Override approve |

### 🛒 Auto E-Commerce — Omnichannel Intent-to-Lease Conversion (MarTech)

This is the **flagship demonstration** of omnichannel decision intelligence. The engine synthesizes signals from three distinct channels to produce high-precision conversion interventions.

| Graph Path | Feature Extracted | Decision Logic |
|---|---|---|
| `Session → BrowsedVehicle` (Web) | `view_count` | Quantifies digital browsing intensity |
| `Session → FinancingCalculator` (Mobile) | `used_calculator`, `term_months` | Confirms financing intent from mobile device |
| `Person → PhysicalVisit → Dealership` (Physical) | `test_drive_count`, `duration_min` | **The "Closing Fact"** — proves physical engagement |
| `Person → OwnedVehicle → Valuation` | `max_trade_in_equity` | > $5k equity → TRADE-IN VOUCHER |
| `BrowsedVehicle → Dealership` | `min_inventory_stock` | < 3 units → DYNAMIC SCARCITY ALERT |

#### E-Commerce Policy Rules (Priority Order)

| Priority | Policy | Trigger Condition | Action |
|----------|--------|-------------------|--------|
| 1 | **POL-MAR-01** Omnichannel Abandonment Recovery | 4+ views + calculator + 1+ test drives | SMS with Locked APR (98% confidence) |
| 2 | **POL-MAR-02** Trade-In Equity Leverage | 4+ views + $5K+ equity | Trade-In Counter-Offer |
| 3 | **POL-MAR-03** Dynamic Scarcity Alert | 2+ views + < 3 units in stock | FOMO Notification |
| 4 | **POL-MAR-04** Omnichannel Accelerator | 1+ test drive + 1+ views | VIP Showroom Invite |

#### Hero Demo: "The Sad User" (Robert Vance — `CUST-ECOM-SAD`)

```
Web:      4 views of Audi A4 (20 minutes browsing)
Mobile:   72-month financing calculator at 4.99% APR
Physical: 90-minute test drive at Central Audi Manhattan
Result:   ❌ No purchase recorded

→ Engine fires POL-MAR-01 → "Send Conversion SMS" at 98% confidence
→ Narrative cites test drive as the "closing fact" bridging digital-physical gap
```

---

## 🔑 Key Features

### Graph-Traversal Policy Engine
Every decision is made by querying actual Neo4j relationships — **zero hardcoded customer IDs**. Five Cypher-based feature extractors (Financial, AML, Healthcare, Insurance, E-Commerce) traverse distinct graph topologies, extract quantitative signals, and apply deterministic rules.

### Omnichannel Signal Synthesis
The E-Commerce vertical demonstrated a critical capability: synthesizing **web browsing history**, **mobile app engagement** (financing calculator), and **physical dealership visits** (test drives) into a single decisioning context. The graph traversal path `Person → Device → Session → BrowsedVehicle` + `Person → PhysicalVisit → Dealership` produces a unified intent score that no single channel could generate alone.

### Population-Based Confidence Scoring
Confidence scores are blended from two sources:
- **Rule-based confidence** (70% weight) — derived from the specific features extracted
- **Population historical data** (30% weight) — derived from how similar decisions performed across the 10K population

For E-Commerce, this includes a custom `calculate_ecommerce_conversion_rate()` function that queries historical `ABANDONED_SESSION` decisions to provide data-driven signal blending.

### Interactive Negotiation Loop
Full lifecycle support: `EVALUATE → COUNTER-OFFER → ACCEPT/DECLINE`. Each negotiation step is persisted as a `NegotiationStep` node in the graph with a complete audit trail.

### AI Narrative Synthesis (LLM as Translator, Not Decider)
After the deterministic engine makes the decision, we pass the full graph context to GPT-4o-mini to generate a human-readable explanation. The LLM **never influences** the actual decision. Four specialized personas are used:
- **Credit Analyst** — for financial decisions
- **AML Fraud Investigator** — for fraud detection
- **Clinical Care Coordinator** — for healthcare
- **Automotive E-Commerce Strategist** — for abandoned sessions

### Offline Narrative Fallback
When OpenAI is unavailable (no internet, missing API key, timeout), the system falls back to **`_build_local_narrative()`** — a structured, template-based narrative builder that produces the same format as the LLM, including graph path descriptions, feature bullet points, and policy citations. **No internet required for the core demo.**

### Decision Reasoning on Graph Nodes
Every Decision node stores:
- `reasoning` — Human-readable explanation of why the decision was made
- `graph_features` — Exact feature values extracted from the graph (including `view_count`, `used_calculator`, `test_drive_count`, `max_trade_in_equity`)
- `policies_applied` — Which policy rules fired
- `decision_type` — The trigger event type
- `ranked_actions` — JSON-serialized ranked alternatives with revenue impact estimates

### Searchable User Explorer
Browse and search across all users with industry filters (💳 Financial, 🚨 AML, 🏥 Healthcare, 🛡️ Insurance, 🛒 E-Commerce) and real-time Neo4j-backed search.

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
│   │       │                            #   5 extractors: Financial, AML, Healthcare,
│   │       │                            #   Insurance, E-Commerce
│   │       │                            #   Population-based confidence blending
│   │       ├── decision_service.py      # Orchestrates evaluation + persistence
│   │       │                            #   Feature whitelist for graph node properties
│   │       ├── llm_service.py           # AI narrative synthesis (GPT-4o-mini)
│   │       │                            #   4 specialized personas + offline fallback
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
│   │       │                            #   Interactive tooltips, node coloring
│   │       │                            #   by type, legend overlay
│   │       └── Sidebar.tsx              # Navigation sidebar
│   └── Dockerfile
├── graph/
│   ├── schema.cypher                    # ★ Full graph schema (constraints + indexes)
│   │                                    #   Supports all 5 verticals + E-Commerce nodes
│   └── seed.cypher                      # ★ Hero profiles + 25 historical E-Commerce
│                                        #   cohorts for population confidence scoring
├── docker-compose.yml                   # Full stack orchestration (3 services)
├── ARTICLE.md                           # Thought leadership article content
├── NBA-Demo-Technical-Doc.html          # CIO-ready technical presentation
└── ARCHITECTURE.md                      # Architecture documentation
```

---

## 🔄 Graph Schema (Node Types)

| Node Label | Purpose | Relationships |
|---|---|---|
| `Person` / `Patient` | Customer entity | `OWNS`, `LOGGED_IN_FROM`, `TOOK_TEST_DRIVE`, `INITIATED_SESSION` |
| `Account` | Financial account | `MADE_PURCHASE`, `INITIATED` |
| `Device` | Login device | `INITIATED` (→ Session) |
| `Session` | E-Commerce browsing session | `VIEWED`, `ENGAGED_WITH`, `PURCHASED` |
| `BrowsedVehicle` | Vehicle listing | `LOCATED_AT` (→ Dealership) |
| `FinancingCalculator` | Finance tool engagement | — |
| `PhysicalVisit` | Dealership test drive | `AT_LOCATION` (→ Dealership) |
| `Dealership` | Physical location | — |
| `OwnedVehicle` | Trade-in vehicle | `VALUED_AT` (→ Valuation) |
| `Valuation` | Trade-in equity assessment | — |
| `Decision` | Engine output | `ABOUT`, `HAS_CONTEXT`, `APPLIED_POLICY` |
| `DecisionContext` | Trigger context | — |
| `Policy` | Business rules | — |
| `NegotiationStep` | Counter-offer lifecycle | — |
| `Fraudster` / `Threat` | AML threat actors | `LOGGED_IN_FROM` (shared device) |
| `InsurancePolicy` / `Claim` | Insurance vertical | `FILED_CLAIM`, `SUBMITTED_TO`, `HAS_PREAUTH` |

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
| **Omnichannel** | Single-channel attribution | Graph bridges Web + Mobile + Physical |
| **Offline Support** | Requires API connectivity | Local narrative builder for air-gapped demos |

---

## 🌐 Internet Requirements

| Feature | Internet Required? | Notes |
|---|---|---|
| Core UI & Graph Visualization | ❌ No | Runs locally via Docker |
| Policy Engine & Decision Logic | ❌ No | Deterministic, graph-traversal only |
| Decision Persistence (Neo4j) | ❌ No | Local containerized database |
| AI Narrative (GPT-4o-mini) | ✅ Yes | Falls back to local builder when offline |
| Google Fonts (Inter, Roboto) | ✅ Yes | Browser defaults used when offline |

> **Demo Tip:** The platform is fully functional offline. The AI narrative section will use the local builder, which produces structured, professional explanations citing the same graph features and policies.

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

# Insurance — Claims review
curl -X POST http://localhost:8001/cases/evaluate \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"INS-04100","trigger_event":"CLAIMS_REVIEW"}'

# Auto E-Commerce — Omnichannel Abandoned Session (Hero Demo)
curl -X POST http://localhost:8001/cases/evaluate \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST-ECOM-SAD","trigger_event":"ABANDONED_SESSION"}'

# Initialize graph (schema + seed data)
curl -X POST http://localhost:8001/graph/init

# Population count
curl http://localhost:8001/customers/count

# Search users
curl "http://localhost:8001/customers?search=Sarah&industry=financial&limit=10"
```

---

## 🎯 Demo Walkthrough: Auto E-Commerce "Sad User"

This is the recommended flow for executive demonstrations:

1. **Open Explorer** → Navigate to `http://localhost:3002/explorer`
2. **Search for "Robert Vance"** → Select the customer
3. **View the Graph** → Observe the omnichannel topology:
   - 🟣 **Person** node (Robert Vance)
   - 🔵 **Session** node → 4 web views of Audi A4
   - ⚪ **Device** node → Mobile (iOS)
   - 📱 **FinancingCalculator** → 72-month at 4.99%
   - 🏢 **PhysicalVisit** → 90-min test drive at Central Audi Manhattan
4. **Trigger Evaluation** → Select `ABANDONED_SESSION` → Click "Evaluate"
5. **Observe the Decision**:
   - Action: **Send Conversion SMS** with locked APR
   - Confidence: **98%** (Omnichannel proof from 3 channels)
   - Policy: **POL-MAR-01** (Omnichannel Abandonment Recovery)
6. **Read the Narrative** → The AI (or local builder) cites the test drive as the "closing fact"
7. **Key Talking Point**: *"The system KNOWS they took a test drive because of the graph relationship, not because an AI guessed. The AI only explains what the data already proved."*

---

## 📄 License

Proprietary — Viztral Technologies. For demonstration purposes only.
