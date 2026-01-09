# Insurance Claims Processing System - Architecture v2.0

## Executive Summary

This document describes the architecture of a **Supervisor-Based Multi-Agent System** for processing insurance claims. The system uses **LangGraph** for agent orchestration, **Oracle 23ai** for data and vector storage, and **OCI GenAI** for LLM capabilities.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           INSURANCE CLAIMS PROCESSING SYSTEM                             │
│                                                                                          │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│   │   📝 Submit     │    │   🔍 Track      │    │   💬 AI         │    │ 🏗️ System   │ │
│   │     Claim       │    │     Claim       │    │   Assistant     │    │ Architecture│ │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘    └──────┬──────┘ │
│            │                      │                      │                    │         │
│            └──────────────────────┴──────────────────────┴────────────────────┘         │
│                                          │                                               │
│                              ┌───────────┴───────────┐                                  │
│                              │   STREAMLIT WEB UI    │                                  │
│                              │      (Port 8501)      │                                  │
│                              └───────────┬───────────┘                                  │
│                                          │ HTTP/REST                                    │
│                              ┌───────────┴───────────┐                                  │
│                              │   FASTAPI BACKEND     │                                  │
│                              │      (Port 8000)      │                                  │
│                              └───────────┬───────────┘                                  │
│                                          │                                               │
│   ┌──────────────────────────────────────┴──────────────────────────────────────┐       │
│   │                    SUPERVISOR-BASED MULTI-AGENT SYSTEM                       │       │
│   │                                                                              │       │
│   │    ┌─────────────────────────────────────────────────────────────────┐      │       │
│   │    │                    🎯 SUPERVISOR AGENT                          │      │       │
│   │    │         Central Coordinator & Intelligent Router                │      │       │
│   │    └─────────────────────────────┬───────────────────────────────────┘      │       │
│   │                                  │                                           │       │
│   │    ┌─────────┬─────────┬─────────┼─────────┬─────────┬─────────┐           │       │
│   │    │         │         │         │         │         │         │           │       │
│   │    ▼         ▼         ▼         ▼         ▼         ▼         ▼           │       │
│   │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │       │
│   │ │ 📄   │ │  ✓   │ │  🔍  │ │  ✅  │ │  👤  │ │  💬  │ │      │            │       │
│   │ │ DOC  │ │VALID │ │FRAUD │ │APPRO-│ │HUMAN │ │CHAT- │ │ ...  │            │       │
│   │ │ANALYZ│ │ATION │ │INVEST│ │ VAL  │ │REVIEW│ │ BOT  │ │      │            │       │
│   │ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘            │       │
│   │                                                                              │       │
│   └──────────────────────────────────────────────────────────────────────────────┘       │
│                                          │                                               │
│   ┌──────────────────────────────────────┴──────────────────────────────────────┐       │
│   │                           EXTERNAL INTEGRATIONS                              │       │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │       │
│   │  │Car Damage│ │  Fraud   │ │  Policy  │ │ Payment  │ │ Document │          │       │
│   │  │   API    │ │Scoring   │ │Management│ │   API    │ │   API    │          │       │
│   │  │(Arya.ai) │ │(Fraud.ai)│ │(Vertafore│ │          │ │          │          │       │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │       │
│   └──────────────────────────────────────────────────────────────────────────────┘       │
│                                          │                                               │
│   ┌──────────────────────────────────────┴──────────────────────────────────────┐       │
│   │                              DATA LAYER                                      │       │
│   │  ┌────────────────────────────────────────────────────────────────────┐     │       │
│   │  │                    ORACLE AUTONOMOUS DATABASE 23ai                  │     │       │
│   │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │     │       │
│   │  │  │  Claims  │ │ Policies │ │   Chat   │ │  Policy  │ │  Damage  │ │     │       │
│   │  │  │  Table   │ │  Table   │ │ History  │ │ Vectors  │ │  Images  │ │     │       │
│   │  │  │          │ │          │ │          │ │(384-dim) │ │(512-dim) │ │     │       │
│   │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │     │       │
│   │  └────────────────────────────────────────────────────────────────────┘     │       │
│   └──────────────────────────────────────────────────────────────────────────────┘       │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Supervisor-Based Multi-Agent Architecture

### Why Supervisor Pattern?

The **Supervisor Pattern** provides:
- **Intelligent Routing**: Claims are routed to appropriate agents based on complexity
- **Conditional Execution**: Not all agents run for every claim
- **Human-in-the-Loop**: Automatic escalation for edge cases
- **Scalability**: Easy to add new specialized agents
- **Observability**: Full workflow history tracking

### Workflow Diagram

```
                                ┌─────────────────┐
                                │   📥 NEW CLAIM  │
                                └────────┬────────┘
                                         │
                                         ▼
                    ┌────────────────────────────────────────┐
                    │         🎯 SUPERVISOR AGENT            │
                    │                                        │
                    │  • Analyzes claim complexity           │
                    │  • Determines routing strategy         │
                    │  • Coordinates agent execution         │
                    │  • Handles escalation decisions        │
                    └────────────────────┬───────────────────┘
                                         │
                              ┌──────────┴──────────┐
                              │    SMART ROUTER     │
                              └──────────┬──────────┘
                                         │
         ┌───────────────┬───────────────┼───────────────┬───────────────┐
         │               │               │               │               │
         ▼               ▼               ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │   📄    │    │   ✓     │    │   🔍    │    │   ✅    │    │   👤    │
    │  DOC    │    │ VALID-  │    │  FRAUD  │    │APPROVAL │    │ HUMAN   │
    │ANALYZER │    │ ATION   │    │  INVEST │    │  AGENT  │    │ REVIEW  │
    │         │    │ AGENT   │    │  AGENT  │    │         │    │         │
    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │               │               │
         └───────────────┴───────────────┴───────────────┴───────────────┘
                                         │
                              ┌──────────┴──────────┐
                              │  Back to Supervisor │
                              │   for next routing  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │   ✅ COMPLETE   │
                                └─────────────────┘
```

---

## Agent Specifications

### 1. 🎯 Supervisor Agent

**File:** `agents/supervisor_agent.py`

**Role:** Central Coordinator

**Responsibilities:**
- Analyze incoming claims and determine complexity
- Route claims to appropriate specialized agents
- Coordinate parallel agent execution when possible
- Handle human-in-the-loop for edge cases
- Make final decisions on claim routing

**Complexity Factors Analyzed:**
| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Claim Amount | < $5K | $5K - $50K | > $50K |
| Photos | 0-2 | 3-5 | > 5 |
| Claim Type | Standard | - | total_loss, theft |
| Filing Delay | < 10 days | 10-20 days | > 20 days |
| Fraud Score | < 0.4 | 0.4 - 0.7 | > 0.7 |

**Priority Levels:**
- `LOW`: complexity_score < 2
- `MEDIUM`: complexity_score 2-3
- `HIGH`: complexity_score 4-5
- `CRITICAL`: complexity_score >= 6

---

### 2. 📄 Document Analyzer Agent

**File:** `agents/document_analyzer_agent.py`

**Role:** Document Expert

**Responsibilities:**
- Analyze damage photos using Car Damage API
- Check for duplicate/fraudulent images via CLIP embeddings
- Assess document quality and completeness
- Extract key information from uploaded documents

**Outputs:**
```python
{
    "photos_analyzed": int,
    "damage_detected": List[str],
    "duplicate_images": List[str],
    "quality_score": int,  # 0-100
    "estimated_repair_cost": float
}
```

---

### 3. ✓ Validation Agent

**File:** `agents/validation_agent.py`

**Role:** Eligibility Checker

**Validation Checks:**
1. **Filing Timeline**: Claim filed within 30 days of incident
2. **Policy Active**: Policy was active on incident date
3. **Coverage Match**: Claim type matches policy coverage
4. **Required Documents**: Photos, incident report, repair estimate
5. **Damage Estimate**: Reasonable amount vs coverage limit

**Outputs:**
- `validation_status`: VALID | INVALID
- `validation_results`: Detailed check results
- `validation_reason`: Human-readable explanation

---

### 4. 🔍 Fraud Investigation Agent

**File:** `agents/fraud_investigation_agent.py`

**Role:** Risk Analyst

**Triggered When:**
- Claim amount > $30,000
- Fraud score > 0.5
- High-complexity claim types
- Multiple risk indicators

**Analysis Performed:**
- Comprehensive fraud scoring via Fraud API
- Pattern analysis across historical claims
- Repair shop reputation check
- Customer claim history analysis
- Image fraud detection (duplicate images)

**Recommendations:**
| Fraud Score | Recommendation |
|-------------|----------------|
| > 0.8 | DENY - High fraud probability |
| 0.6 - 0.8 | ESCALATE - Requires human review |
| 0.4 - 0.6 | APPROVE_WITH_MONITORING |
| < 0.4 | APPROVE - Low fraud risk |

---

### 5. ✅ Approval Agent

**File:** `agents/approval_agent.py`

**Role:** Decision Maker

**Decision Logic:**
```
IF fraud_score > 0.7:
    status = NEEDS_REVIEW (manual)
ELIF fraud_score 0.4-0.7:
    status = APPROVED (with monitoring)
ELSE:
    status = APPROVED (auto)
```

**Payout Calculation:**
```
payout = damage_amount - deductible
payout = min(payout, coverage_limit)
```

**Processing Time:**
| Fraud Score | Processing Days |
|-------------|-----------------|
| < 0.2 | 2 days |
| 0.2 - 0.5 | 5 days |
| > 0.5 | 10 days |

---

### 6. 👤 Human Review Handler

**File:** `agents/supervisor_workflow.py` (human_review_node)

**Role:** Escalation Handler

**Triggered When:**
- Very high fraud score (> 0.8)
- Approval status = NEEDS_REVIEW
- Critical priority claims
- Edge cases requiring judgment

**Actions:**
- Flag claim for manual review
- Prepare case summary for reviewers
- In production: integrate with ticketing system

---

### 7. 💬 Chatbot Agent

**File:** `agents/chatbot_agent.py`

**Role:** Customer Support

**Features:**
- RAG-powered answers using Oracle Vector Store
- Claim-specific context when claim ID provided
- Policy document search
- Direct data lookups for common questions

**Capabilities:**
- Coverage questions
- Deductible inquiries
- Payout information
- Appeal process guidance
- Rental coverage details

---

## Routing Logic

### Decision Tree

```
                              ┌─────────────────┐
                              │  NEW CLAIM      │
                              └────────┬────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         │    Has damage photos?     │
                         └─────────────┬─────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                   YES                                    NO
                    │                                      │
                    ▼                                      ▼
        ┌───────────────────┐                  ┌───────────────────┐
        │ DOCUMENT ANALYZER │                  │    VALIDATION     │
        └─────────┬─────────┘                  └─────────┬─────────┘
                  │                                      │
                  ▼                                      │
        ┌───────────────────┐                           │
        │    VALIDATION     │◄──────────────────────────┘
        └─────────┬─────────┘
                  │
         ┌────────┴────────┐
         │ Validation OK?  │
         └────────┬────────┘
                  │
        ┌─────────┴─────────┐
       YES                  NO
        │                   │
        ▼                   ▼
┌───────────────┐    ┌─────────────┐
│ High Risk?    │    │   DENIED    │
│ Amount>$30K?  │    │   (END)     │
│ Fraud>0.5?    │    └─────────────┘
└───────┬───────┘
        │
   ┌────┴────┐
  YES       NO
   │         │
   ▼         ▼
┌──────────┐ ┌──────────┐
│  FRAUD   │ │ APPROVAL │
│  INVEST  │ │  AGENT   │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            │
┌──────────┐      │
│ Score    │      │
│ > 0.8?   │      │
└────┬─────┘      │
     │            │
┌────┴────┐       │
YES      NO       │
│         │       │
▼         ▼       │
┌──────┐ ┌────────┴───────┐
│HUMAN │ │    APPROVAL    │
│REVIEW│ │     AGENT      │
└──┬───┘ └────────┬───────┘
   │              │
   │         ┌────┴────┐
   │         │ NEEDS   │
   │         │ REVIEW? │
   │         └────┬────┘
   │              │
   │         ┌────┴────┐
   │        YES       NO
   │         │         │
   │         ▼         ▼
   │    ┌──────────┐ ┌─────────┐
   └───►│  HUMAN   │ │   END   │
        │  REVIEW  │ │         │
        └────┬─────┘ └─────────┘
             │
             ▼
        ┌─────────┐
        │   END   │
        └─────────┘
```

---

## State Management

### SupervisorClaimState

```python
class SupervisorClaimState(TypedDict):
    # Input Fields
    claim_id: str
    policy_id: str
    customer_id: str
    incident_date: str
    claim_date: str
    claim_type: str
    damage_description: str
    repair_shop: str
    estimated_damage_amount: float
    damage_photos: List[str]
    incident_report: str
    repair_estimate: str
    
    # Supervisor Fields
    supervisor_decision: str  # next agent to invoke
    supervisor_reasoning: str
    supervisor_priority: str  # low | medium | high | critical
    complexity_analysis: Dict[str, Any]
    
    # Agent Outputs
    document_analysis: Dict[str, Any]
    validation_status: str
    validation_results: Dict[str, Any]
    fraud_investigation: Dict[str, Any]
    approval_status: str
    payout_amount: float
    fraud_score: float
    
    # Workflow Tracking
    workflow_history: List[Dict[str, Any]]
    human_review_required: bool
    current_step: str
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | Web UI with 4 tabs |
| **Backend** | FastAPI | REST API |
| **Agent Framework** | LangGraph | Multi-agent orchestration |
| **LLM Framework** | LangChain | LLM integration |
| **LLM** | OCI GenAI (Cohere Command-A) | Chatbot responses |
| **Database** | Oracle Autonomous 23ai | Data storage |
| **Text Vectors** | Oracle VECTOR(384) | RAG for chatbot |
| **Image Vectors** | Oracle VECTOR(512) | Fraud detection |
| **Text Embeddings** | Sentence-BERT (MiniLM) | Document embeddings |
| **Image Embeddings** | CLIP (ViT-B/32) | Image embeddings |

---

## API Endpoints

### Claims
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/submit-claim` | Submit new claim (JSON) |
| POST | `/submit-claim-with-images` | Submit with image uploads |
| GET | `/claim/{id}` | Get claim details |
| GET | `/claims` | List all claims |

### Workflow
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workflow/agents` | Get agent information |
| GET | `/workflow/architecture` | Get workflow diagram |
| GET | `/workflow/stats` | Get processing statistics |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send message to chatbot |
| GET | `/chat-history/{id}` | Get chat history |

### Images
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/claim/{id}/images` | Get claim images |
| GET | `/image/{id}` | Get image data |
| POST | `/check-image-fraud` | Check for duplicate images |

---

## UI Components

### Tab 1: Submit Claim
- Policy selection
- Date inputs (incident, filing)
- Claim type selection
- Damage description
- Photo upload with CLIP vectorization
- Real-time processing results
- Workflow history display

### Tab 2: Track Claim
- Claim ID search
- Status cards (validation, approval)
- Financial summary
- Fraud analysis with progress bar
- Workflow visualization
- Image gallery

### Tab 3: AI Assistant
- RAG-powered chatbot
- Claim context linking
- Quick question buttons
- Chat history

### Tab 4: System Architecture
- Workflow diagram
- Agent cards with descriptions
- Routing logic explanation
- Technology stack
- Live statistics
- API integrations

---

## Security

- **Database**: mTLS with wallet-based authentication
- **API**: Environment variables for secrets
- **Validation**: Pydantic models for all inputs
- **CORS**: Configurable middleware

---

## Deployment

### Local Development
```bash
# Terminal 1: API
./venv/bin/python run_api.py

# Terminal 2: UI
./venv/bin/python run_ui.py
```

### Production (OCI)
```bash
# Background processes
nohup ./venv/bin/python run_api.py > api.log 2>&1 &
nohup ./venv/bin/python run_ui.py > ui.log 2>&1 &
```

---

**Document Version:** 2.0  
**Last Updated:** January 2026  
**Architecture:** Supervisor-Based Multi-Agent System with LangGraph
