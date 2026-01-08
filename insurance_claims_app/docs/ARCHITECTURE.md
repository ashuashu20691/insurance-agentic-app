# Insurance Claims Processing System - Architecture

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         STREAMLIT WEB UI (Port 8501)                             │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │  Submit Claim   │  │  Track Claim    │  │    Chatbot      │                  │    │
│  │  │     Page        │  │     Page        │  │     Page        │                  │    │
│  │  │                 │  │                 │  │                 │                  │    │
│  │  │ • Policy Select │  │ • Claim Search  │  │ • Chat Input    │                  │    │
│  │  │ • Date Inputs   │  │ • Status View   │  │ • Quick Q's     │                  │    │
│  │  │ • Photo Upload  │  │ • Payout Info   │  │ • History       │                  │    │
│  │  │ • Documents     │  │ • Fraud Score   │  │ • RAG Answers   │                  │    │
│  │  │ • Vectorization │  │ • View Images   │  │                 │                  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ HTTP/REST
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     API LAYER                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         FASTAPI BACKEND (Port 8000)                              │    │
│  │                                                                                   │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │    │
│  │  │POST          │ │GET           │ │POST          │ │GET           │            │    │
│  │  │/submit-claim │ │/claim/{id}   │ │/chat         │ │/policies     │            │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘            │    │
│  │                                                                                   │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │    │
│  │  │GET           │ │GET           │ │GET           │ │GET           │            │    │
│  │  │/claims       │ │/policy/{id}  │ │/chat-history │ │/health       │            │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘            │    │
│  │                                                                                   │    │
│  │  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐           │    │
│  │  │POST                │ │GET                 │ │POST               │           │    │
│  │  │/submit-claim-with- │ │/claim/{id}/images  │ │/check-image-fraud │           │    │
│  │  │images (multipart)  │ │                    │ │                   │           │    │
│  │  └────────────────────┘ └────────────────────┘ └────────────────────┘           │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
```

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              MULTI-AGENT ORCHESTRATION LAYER                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                            LANGGRAPH WORKFLOW ENGINE                             │    │
│  │                                                                                   │    │
│  │    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐              │    │
│  │    │   START     │         │             │         │             │              │    │
│  │    │   ────►     │────────►│ VALIDATION  │────────►│  APPROVAL   │────►END     │    │
│  │    │             │         │   AGENT     │         │   AGENT     │              │    │
│  │    └─────────────┘         └─────────────┘         └─────────────┘              │    │
│  │                                   │                       │                      │    │
│  │                                   │                       │                      │    │
│  │    ┌──────────────────────────────┴───────────────────────┴──────────────────┐  │    │
│  │    │                         CLAIM STATE OBJECT                               │  │    │
│  │    │  • claim_id, policy_id, customer_id, dates, claim_type                  │  │    │
│  │    │  • validation_status, validation_results, validation_reason             │  │    │
│  │    │  • approval_status, approval_reason, payout_amount, fraud_score         │  │    │
│  │    │  • damage_assessment, policy_details, fraud_assessment                  │  │    │
│  │    └─────────────────────────────────────────────────────────────────────────┘  │    │
│  │                                                                                   │    │
│  │    ┌─────────────────────────────────────────────────────────────────────────┐  │    │
│  │    │                    CHATBOT AGENT (Parallel/Independent)                  │  │    │
│  │    │                                                                          │  │    │
│  │    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │  │    │
│  │    │  │   RAG       │    │  OCI GenAI  │    │   Claim     │                  │  │    │
│  │    │  │  Search     │───►│   LLM       │◄───│   Context   │                  │  │    │
│  │    │  │ (ChromaDB)  │    │  (Cohere)   │    │   Lookup    │                  │  │    │
│  │    │  └─────────────┘    └─────────────┘    └─────────────┘                  │  │    │
│  │    └─────────────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
```

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT DETAIL LAYER                                          │
│                                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐  ┌────────────────────┐ │
│  │    VALIDATION AGENT        │  │     APPROVAL AGENT         │  │   CHATBOT AGENT    │ │
│  │                            │  │                            │  │                    │ │
│  │  Checks:                   │  │  Calls:                    │  │  Features:         │ │
│  │  ✓ Filing Timeline (30d)  │  │  • Car Damage API          │  │  • RAG Search      │ │
│  │  ✓ Policy Active Status   │  │  • Fraud Scoring API       │  │  • LLM Response    │ │
│  │  ✓ Coverage Type Match    │  │  • Policy Management API   │  │  • Claim Context   │ │
│  │  ✓ Required Documents     │  │                            │  │                    │ │
│  │  ✓ Damage Estimate        │  │  Decision Logic:           │  │  Answers:          │ │
│  │                            │  │  • fraud > 0.7 → REVIEW   │  │  • Coverage Q's    │ │
│  │  Returns:                  │  │  • fraud 0.4-0.7 → APPROVE│  │  • Deductible      │ │
│  │  • VALID / INVALID        │  │  • fraud < 0.4 → AUTO     │  │  • Payout Info     │ │
│  │  • Detailed Results       │  │                            │  │  • Appeal Process  │ │
│  │  • Failure Reasons        │  │  Calculates:               │  │  • Rental Coverage │ │
│  │                            │  │  • Payout Amount          │  │                    │ │
│  │                            │  │  • Processing Days        │  │                    │ │
│  └────────────────────────────┘  └────────────────────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
```

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            EXTERNAL INTEGRATION LAYER                                    │
│                                                                                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│  │  CAR DAMAGE     │ │  FRAUD SCORING  │ │    POLICY       │ │    PAYMENT      │       │
│  │  DETECTION API  │ │      API        │ │  MANAGEMENT API │ │      API        │       │
│  │  (Arya.ai)      │ │  (Fraud.ai)     │ │  (Vertafore)    │ │                 │       │
│  │                 │ │                 │ │                 │ │                 │       │
│  │  Input:         │ │  Input:         │ │  Input:         │ │  Input:         │       │
│  │  • Photos       │ │  • Claim Amount │ │  • Policy ID    │ │  • Claim ID     │       │
│  │  • Est. Amount  │ │  • Repair Shop  │ │                 │ │  • Payout Amt   │       │
│  │                 │ │  • Claimant ID  │ │  Output:        │ │                 │       │
│  │  Output:        │ │  • Vehicle Age  │ │  • Coverage     │ │  Output:        │       │
│  │  • Damaged Parts│ │  • Damage Type  │ │  • Limits       │ │  • Payment ID   │       │
│  │  • Repair Cost  │ │                 │ │  • Deductible   │ │  • Status       │       │
│  │  • Confidence   │ │  Output:        │ │  • Riders       │ │  • Date         │       │
│  │                 │ │  • Fraud Score  │ │  • Active Flag  │ │                 │       │
│  │                 │ │  • Indicators   │ │                 │ │                 │       │
│  │                 │ │  • Risk Level   │ │                 │ │                 │       │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         DOCUMENT MANAGEMENT API                                  │    │
│  │                                                                                   │    │
│  │  Provides Policy Documents for RAG:                                              │    │
│  │  • General Coverage Guide    • Claims Process    • Deductibles                  │    │
│  │  • Appeal Process            • Rental Coverage   • Payment Timeline             │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
```

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  AI/ML LAYER                                             │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │         OCI GENERATIVE AI           │  │       ORACLE 23ai VECTOR STORE       │   │
│  │                                     │  │                                          │   │
│  │  Model: cohere.command-a-03-2025   │  │  Native VECTOR data type support         │   │
│  │  Endpoint: us-chicago-1            │  │                                          │   │
│  │  Auth: API_KEY                     │  │  ┌─────────────────────────────────────┐ │   │
│  │                                     │  │  │  TEXT VECTOR STORE                 │ │   │
│  │  Used For:                         │  │  │  • VECTOR(384, FLOAT32)             │ │   │
│  │  • Chatbot Responses               │  │  │  • Policy Document Embeddings      │ │   │
│  │  • Policy Q&A                      │  │  │  • HuggingFace all-MiniLM-L6-v2    │ │   │
│  │  • Grounded Answers                │  │  │  • RAG similarity search           │ │   │
│  │                                     │  │  └─────────────────────────────────────┘ │   │
│  │                                     │  │                                          │   │
│  │                                     │  │  ┌─────────────────────────────────────┐ │   │
│  │                                     │  │  │  IMAGE VECTOR STORE                │ │   │
│  │                                     │  │  │  • VECTOR(512, FLOAT32)             │ │   │
│  │                                     │  │  │  • CLIP Model Embeddings           │ │   │
│  │                                     │  │  │  • Damage Photo Vectorization      │ │   │
│  │                                     │  │  │  • Fraud Detection via Similarity  │ │   │
│  │                                     │  │  └─────────────────────────────────────┘ │   │
│  └─────────────────────────────────────┘  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  DATA LAYER                                              │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    ORACLE AUTONOMOUS DATABASE (Cloud)                            │    │
│  │                    Region: ap-mumbai-1 | Service: insuranceapp_medium           │    │
│  │                                                                                   │    │
│  │  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐        │    │
│  │  │    CLAIMS TABLE     │ │   POLICIES TABLE    │ │  CHAT_HISTORY TABLE │        │    │
│  │  │                     │ │                     │ │                     │        │    │
│  │  │ • claim_id (PK)     │ │ • policy_id (PK)    │ │ • chat_id (PK)      │        │    │
│  │  │ • policy_id (FK)    │ │ • customer_id       │ │ • claim_id (FK)     │        │    │
│  │  │ • customer_id       │ │ • coverage_type     │ │ • customer_message  │        │    │
│  │  │ • incident_date     │ │ • coverage_limit    │ │ • bot_response      │        │    │
│  │  │ • claim_date        │ │ • deductible        │ │ • timestamp         │        │    │
│  │  │ • claim_type        │ │ • is_active         │ │                     │        │    │
│  │  │ • validation_status │ │ • start_date        │ └─────────────────────┘        │    │
│  │  │ • approval_status   │ │ • end_date          │                                │    │
│  │  │ • payout_amount     │ │ • riders (JSON)     │ ┌─────────────────────┐        │    │
│  │  │ • fraud_score       │ │ • policy_document   │ │  DAMAGE_IMAGES TABLE│        │    │
│  │  │ • processing_days   │ │                     │ │                     │        │    │
│  │  └─────────────────────┘ └─────────────────────┘ │ • image_id (PK)     │        │    │
│  │                                                  │ • claim_id (FK)     │        │    │
│  │  ┌─────────────────────┐ ┌─────────────────────┐ │ • image_name        │        │    │
│  │  │ POLICY_DOCUMENTS    │ │                     │ │ • image_data (BLOB) │        │    │
│  │  │ (Vector Store)      │ │                     │ │ • embedding         │        │    │
│  │  │                     │ │                     │ │   VECTOR(512,FLOAT32)│       │    │
│  │  │ • doc_id (PK)       │ │                     │ │ • damage_type       │        │    │
│  │  │ • content (CLOB)    │ │                     │ │ • metadata (CLOB)   │        │    │
│  │  │ • embedding         │ │                     │ └─────────────────────┘        │    │
│  │  │   VECTOR(384,FLOAT32)│ │                     │                                │    │
│  │  │ • metadata (CLOB)   │ │                     │                                │    │
│  │  └─────────────────────┘ └─────────────────────┘                                │    │
│  │                                                                                   │    │
│  │  Connection: mTLS with Wallet | Pool: 2-10 connections                          │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```


## Data Flow Diagrams

### 1. Claim Submission Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Streamlit│    │ FastAPI  │    │ LangGraph│    │  Oracle  │
│  Browser │    │    UI    │    │  Backend │    │ Workflow │    │    DB    │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │               │
     │ Fill Form     │               │               │               │
     │──────────────►│               │               │               │
     │               │               │               │               │
     │               │ POST /submit  │               │               │
     │               │──────────────►│               │               │
     │               │               │               │               │
     │               │               │ Create Claim  │               │
     │               │               │───────────────────────────────►
     │               │               │               │               │
     │               │               │ process_claim │               │
     │               │               │──────────────►│               │
     │               │               │               │               │
     │               │               │               │ Validation    │
     │               │               │               │───────────────►
     │               │               │               │◄──────────────│
     │               │               │               │               │
     │               │               │               │ Call APIs     │
     │               │               │               │──────┐        │
     │               │               │               │◄─────┘        │
     │               │               │               │               │
     │               │               │               │ Approval      │
     │               │               │               │───────────────►
     │               │               │               │◄──────────────│
     │               │               │               │               │
     │               │               │◄──────────────│               │
     │               │               │               │               │
     │               │               │ Update Claim  │               │
     │               │               │───────────────────────────────►
     │               │               │               │               │
     │               │◄──────────────│               │               │
     │               │  JSON Result  │               │               │
     │◄──────────────│               │               │               │
     │ Display Result│               │               │               │
     │               │               │               │               │
```


### 2. Chatbot Interaction Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Streamlit│    │ FastAPI  │    │ Chatbot  │    │ OCI      │
│  Browser │    │    UI    │    │  Backend │    │  Agent   │    │ GenAI    │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │               │
     │ Ask Question  │               │               │               │
     │──────────────►│               │               │               │
     │               │               │               │               │
     │               │ POST /chat    │               │               │
     │               │──────────────►│               │               │
     │               │               │               │               │
     │               │               │ answer_question               │
     │               │               │──────────────►│               │
     │               │               │               │               │
     │               │               │               │ RAG Search    │
     │               │               │               │──────┐        │
     │               │               │               │◄─────┘ChromaDB│
     │               │               │               │               │
     │               │               │               │ Get Claim Data│
     │               │               │               │──────┐        │
     │               │               │               │◄─────┘Oracle  │
     │               │               │               │               │
     │               │               │               │ LLM Request   │
     │               │               │               │──────────────►│
     │               │               │               │◄──────────────│
     │               │               │               │  Response     │
     │               │               │◄──────────────│               │
     │               │◄──────────────│               │               │
     │◄──────────────│               │               │               │
     │ Display Answer│               │               │               │
```

### 3. Image Vectorization & Fraud Detection Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Streamlit│    │ FastAPI  │    │  Image   │    │ Oracle   │
│  Browser │    │    UI    │    │  Backend │    │ VecStore │    │   23ai   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │               │
     │ Upload Photos │               │               │               │
     │──────────────►│               │               │               │
     │               │               │               │               │
     │               │ POST /submit- │               │               │
     │               │ claim-with-   │               │               │
     │               │ images        │               │               │
     │               │──────────────►│               │               │
     │               │               │               │               │
     │               │               │ For each image│               │
     │               │               │──────────────►│               │
     │               │               │               │               │
     │               │               │               │ Load CLIP     │
     │               │               │               │ Model         │
     │               │               │               │──────┐        │
     │               │               │               │◄─────┘        │
     │               │               │               │               │
     │               │               │               │ Generate      │
     │               │               │               │ 512-dim       │
     │               │               │               │ Embedding     │
     │               │               │               │──────┐        │
     │               │               │               │◄─────┘        │
     │               │               │               │               │
     │               │               │               │ Check for     │
     │               │               │               │ Duplicates    │
     │               │               │               │──────────────►│
     │               │               │               │◄──────────────│
     │               │               │               │ Similar imgs  │
     │               │               │               │               │
     │               │               │               │ Store Image + │
     │               │               │               │ Embedding     │
     │               │               │               │──────────────►│
     │               │               │               │◄──────────────│
     │               │               │               │               │
     │               │               │◄──────────────│               │
     │               │               │ Fraud Check   │               │
     │               │               │ Results       │               │
     │               │               │               │               │
     │               │               │ Continue to   │               │
     │               │               │ Workflow      │               │
     │               │◄──────────────│               │               │
     │◄──────────────│               │               │               │
     │ Display Result│               │               │               │
     │ (with fraud   │               │               │               │
     │  warning if   │               │               │               │
     │  duplicate)   │               │               │               │
```

### 4. Validation Agent Logic Flow

```
                              ┌─────────────────┐
                              │  CLAIM INPUT    │
                              │                 │
                              │ • policy_id     │
                              │ • incident_date │
                              │ • claim_date    │
                              │ • claim_type    │
                              │ • documents     │
                              │ • damage_amount │
                              └────────┬────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────┐
                    │     CHECK 1: FILING TIMELINE     │
                    │                                  │
                    │  (claim_date - incident_date)    │
                    │         <= 30 days?              │
                    └────────────────┬─────────────────┘
                                     │
                         ┌───────────┴───────────┐
                         │                       │
                        YES                      NO
                         │                       │
                         ▼                       ▼
              ┌──────────────────┐    ┌──────────────────┐
              │     PASS         │    │     FAIL         │
              └────────┬─────────┘    │ "Exceeds 30 day  │
                       │              │  filing limit"   │
                       ▼              └──────────────────┘
        ┌──────────────────────────────────┐
        │    CHECK 2: POLICY ACTIVE        │
        │                                  │
        │  Policy exists AND is_active?    │
        │  Incident date within policy     │
        │  start_date and end_date?        │
        └────────────────┬─────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │    CHECK 3: COVERAGE MATCH       │
        │                                  │
        │  claim_type covered by           │
        │  policy coverage_type?           │
        │                                  │
        │  comprehensive → all types       │
        │  collision → collision only      │
        │  liability → liability only      │
        └────────────────┬─────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │    CHECK 4: REQUIRED DOCUMENTS   │
        │                                  │
        │  • damage_photos (required)      │
        │  • incident_report (required)    │
        │  • repair_estimate (required)    │
        └────────────────┬─────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │    CHECK 5: DAMAGE ESTIMATE      │
        │                                  │
        │  estimated_amount > 0?           │
        │  estimated_amount <= 1.5x        │
        │  coverage_limit?                 │
        └────────────────┬─────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
         ALL PASS              ANY FAIL
              │                     │
              ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ validation_status│   │ validation_status│
    │    = "VALID"    │   │   = "INVALID"   │
    │                 │   │                 │
    │ → Continue to   │   │ → Claim DENIED  │
    │   Approval Agent│   │                 │
    └─────────────────┘   └─────────────────┘
```


### 5. Approval Agent Logic Flow

```
                              ┌─────────────────┐
                              │ VALIDATED CLAIM │
                              │                 │
                              │ validation_status│
                              │    = "VALID"    │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
                    ▼                                     ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │   CAR DAMAGE API      │           │   FRAUD SCORING API   │
        │                       │           │                       │
        │ Input: photos, amount │           │ Input: amount, shop,  │
        │                       │           │ claimant, vehicle_age │
        │ Output:               │           │                       │
        │ • damaged_parts       │           │ Output:               │
        │ • repair_cost         │           │ • fraud_score (0-1)   │
        │ • confidence          │           │ • fraud_indicators    │
        └───────────┬───────────┘           │ • risk_level          │
                    │                       └───────────┬───────────┘
                    │                                   │
                    └─────────────┬─────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   FRAUD SCORE DECISION  │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
           ▼                     ▼                     ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │ score > 0.7 │       │ 0.4 < score │       │ score < 0.4 │
    │             │       │   <= 0.7    │       │             │
    │ HIGH RISK   │       │ MEDIUM RISK │       │  LOW RISK   │
    └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
           │                     │                     │
           ▼                     ▼                     ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │NEEDS_REVIEW │       │  APPROVED   │       │  APPROVED   │
    │             │       │ (monitored) │       │ (auto)      │
    │Manual review│       │             │       │             │
    │required     │       │Flag for     │       │Standard     │
    │             │       │monitoring   │       │processing   │
    └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   CALCULATE PAYOUT      │
                    │                         │
                    │ payout = damage_amount  │
                    │        - deductible     │
                    │                         │
                    │ payout = min(payout,    │
                    │          coverage_limit)│
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  SET PROCESSING TIME    │
                    │                         │
                    │ score < 0.2 → 2 days    │
                    │ score < 0.5 → 5 days    │
                    │ score > 0.5 → 10 days   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      FINAL OUTPUT       │
                    │                         │
                    │ • approval_status       │
                    │ • approval_reason       │
                    │ • payout_amount         │
                    │ • deductible            │
                    │ • processing_days       │
                    │ • fraud_score           │
                    │ • fraud_flags           │
                    └─────────────────────────┘
```


## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              INSURANCE CLAIMS SYSTEM                                     │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              PRESENTATION TIER                                   │    │
│  │                                                                                   │    │
│  │   ui/                                                                            │    │
│  │   └── streamlit_app.py ─────────────────────────────────────────────────────┐   │    │
│  │       │                                                                      │   │    │
│  │       ├── Submit Claim Page ──► Form validation, file upload                │   │    │
│  │       ├── Track Claim Page ───► Status display, metrics                     │   │    │
│  │       └── Chatbot Page ───────► Chat interface, quick questions             │   │    │
│  │                                                                              │   │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                             │
│                                         │ HTTP                                        │
│                                         ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              APPLICATION TIER                                    │    │
│  │                                                                                   │    │
│  │   api/                                                                           │    │
│  │   └── main.py ──────────────────────────────────────────────────────────────┐   │    │
│  │       │                                                                      │   │    │
│  │       ├── /submit-claim ──► Create claim, run workflow, return results      │   │    │
│  │       ├── /claim/{id} ────► Get claim status and details                    │   │    │
│  │       ├── /chat ──────────► Process chatbot message                         │   │    │
│  │       └── /policies ──────► List available policies                         │   │    │
│  │                                                                              │   │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                             │
│                                         ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              BUSINESS LOGIC TIER                                 │    │
│  │                                                                                   │    │
│  │   agents/                                                                        │    │
│  │   ├── workflow.py ────────► LangGraph orchestration                             │    │
│  │   ├── state.py ───────────► ClaimState TypedDict                                │    │
│  │   ├── validation_agent.py ► 5 validation checks                                 │    │
│  │   ├── approval_agent.py ──► API calls, decision logic, payout calc             │    │
│  │   └── chatbot_agent.py ───► RAG search, LLM response, claim context            │    │
│  │                                                                                   │    │
│  │   external_apis/                                                                 │    │
│  │   ├── car_damage_api.py ──► Mock Arya.ai damage detection                       │    │
│  │   ├── fraud_scoring_api.py► Mock Fraud.ai risk scoring                          │    │
│  │   ├── policy_management_api.py ► Policy lookup from DB                          │    │
│  │   ├── payment_api.py ─────► Mock payment processing                             │    │
│  │   └── document_api.py ────► Policy documents for RAG                            │    │
│  │                                                                                   │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                             │
│                                         ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              DATA ACCESS TIER                                    │    │
│  │                                                                                   │    │
│  │   database/                                                                      │    │
│  │   ├── models.py ──────────► Connection pool, table creation, seeding            │    │
│  │   ├── crud.py ────────────► Create, Read, Update operations                     │    │
│  │   ├── vector_store.py ────► Text embeddings for RAG (384-dim)                   │    │
│  │   └── image_vector_store.py► CLIP image embeddings (512-dim)                    │    │
│  │                                                                                   │    │
│  │   config.py ──────────────► Environment variables, thresholds                   │    │
│  │                                                                                   │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                             │
│                                         ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              INFRASTRUCTURE TIER                                 │    │
│  │                                                                                   │    │
│  │   ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │    │
│  │   │  Oracle Autonomous  │  │    OCI GenAI        │  │     ChromaDB        │     │    │
│  │   │     Database        │  │                     │  │   (In-Memory)       │     │    │
│  │   │                     │  │  Cohere Command-A   │  │                     │     │    │
│  │   │  • Claims           │  │  • LLM Inference    │  │  • Vector Store     │     │    │
│  │   │  • Policies         │  │  • Chat Responses   │  │  • RAG Embeddings   │     │    │
│  │   │  • Chat History     │  │                     │  │                     │     │    │
│  │   │                     │  │  Region: Chicago    │  │  Model: MiniLM      │     │    │
│  │   │  Region: Mumbai     │  │                     │  │                     │     │    │
│  │   └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │    │
│  │                                                                                   │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```


## Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              TECHNOLOGY STACK                                            │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  FRONTEND                                                                        │    │
│  │  ┌─────────────┐                                                                 │    │
│  │  │  Streamlit  │  Python web framework for data apps                            │    │
│  │  │   v1.52     │  • Reactive UI components                                      │    │
│  │  │             │  • Session state management                                    │    │
│  │  │             │  • File upload handling                                        │    │
│  │  └─────────────┘                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  BACKEND                                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                              │    │
│  │  │  FastAPI    │  │  Pydantic   │  │  Uvicorn    │                              │    │
│  │  │   v0.109    │  │   v2.5      │  │   v0.27     │                              │    │
│  │  │             │  │             │  │             │                              │    │
│  │  │ REST API    │  │ Validation  │  │ ASGI Server │                              │    │
│  │  │ framework   │  │ & schemas   │  │             │                              │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                              │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  AI/ML FRAMEWORK                                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  ┌─────────────┐     │    │
│  │  │ LangChain   │  │  LangGraph  │  │ Oracle 23ai Vector  │  │ Sentence    │     │    │
│  │  │   v1.2      │  │   v1.0      │  │      Store          │  │ Transformers│     │    │
│  │  │             │  │             │  │                     │  │   v5.2      │     │    │
│  │  │ LLM         │  │ Multi-agent │  │ Native VECTOR type  │  │             │     │    │
│  │  │ framework   │  │ workflow    │  │ Similarity search   │  │ Embeddings  │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  └─────────────┘     │    │
│  │                                                                                   │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────────────┐  │    │
│  │  │ CLIP Model  │  │ Transformers│  │  Image Vectorization for Fraud Detection│  │    │
│  │  │ (OpenAI)    │  │  (HuggingFace)│  │                                         │  │    │
│  │  │             │  │             │  │  • 512-dim image embeddings             │  │    │
│  │  │ clip-vit-   │  │ Model loader│  │  • Cosine similarity search             │  │    │
│  │  │ base-patch32│  │ & inference │  │  • Duplicate image detection            │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  CLOUD SERVICES                                                                  │    │
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────────────────┐   │    │
│  │  │  Oracle Cloud (OCI)         │  │  Oracle Autonomous Database 23ai        │   │    │
│  │  │                             │  │                                         │   │    │
│  │  │  • Generative AI Service    │  │  • Serverless database                  │   │    │
│  │  │  • Cohere Command-A model   │  │  • Native VECTOR data type              │   │    │
│  │  │  • API Key authentication   │  │  • VECTOR_DISTANCE function             │   │    │
│  │  │  • Region: us-chicago-1     │  │  • Vector index for fast search         │   │    │
│  │  │                             │  │  • mTLS with wallet                     │   │    │
│  │  │                             │  │  • Region: ap-mumbai-1                  │   │    │
│  │  └─────────────────────────────┘  └─────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  DATABASE DRIVER                                                                 │    │
│  │  ┌─────────────┐                                                                 │    │
│  │  │  oracledb   │  Python driver for Oracle Database                             │    │
│  │  │   v2.0+     │  • Thin mode (no Oracle Client needed)                         │    │
│  │  │             │  • Connection pooling                                          │    │
│  │  │             │  • Wallet support for ADB                                      │    │
│  │  │             │  • Native VECTOR type support                                  │    │
│  │  └─────────────┘                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY LAYERS                                             │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  APPLICATION SECURITY                                                            │    │
│  │                                                                                   │    │
│  │  • Environment variables for secrets (.env file)                                │    │
│  │  • Pydantic validation on all API inputs                                        │    │
│  │  • CORS middleware configured                                                   │    │
│  │  • No hardcoded credentials                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  DATABASE SECURITY                                                               │    │
│  │                                                                                   │    │
│  │  • mTLS encryption (wallet-based)                                               │    │
│  │  • Connection pooling with min/max limits                                       │    │
│  │  • Parameterized queries (no SQL injection)                                     │    │
│  │  • Wallet password protection                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  API SECURITY                                                                    │    │
│  │                                                                                   │    │
│  │  • OCI API Key authentication for GenAI                                         │    │
│  │  • HTTPS for all external communications                                        │    │
│  │  • Rate limiting (configurable)                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DEPLOYMENT OPTIONS                                          │
│                                                                                          │
│  OPTION 1: Local Development                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                   │    │
│  │   ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────────┐   │    │
│  │   │  Streamlit  │     │  FastAPI    │     │  Oracle Autonomous Database     │   │    │
│  │   │  localhost  │────►│  localhost  │────►│  (Cloud - ap-mumbai-1)          │   │    │
│  │   │  :8501      │     │  :8000      │     │                                 │   │    │
│  │   └─────────────┘     └─────────────┘     └─────────────────────────────────┘   │    │
│  │                                                                                   │    │
│  │   Commands:                                                                      │    │
│  │   $ ./venv/bin/python run_api.py    # Terminal 1                                │    │
│  │   $ ./venv/bin/python run_ui.py     # Terminal 2                                │    │
│  │                                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  OPTION 2: Docker Deployment                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                   │    │
│  │   ┌─────────────────────────────────────────────────────────────────────────┐   │    │
│  │   │                        Docker Compose                                    │   │    │
│  │   │                                                                          │   │    │
│  │   │   ┌─────────────┐     ┌─────────────┐                                   │   │    │
│  │   │   │  streamlit  │     │   api       │                                   │   │    │
│  │   │   │  container  │────►│  container  │────► Oracle ADB (Cloud)           │   │    │
│  │   │   │  :8501      │     │  :8000      │                                   │   │    │
│  │   │   └─────────────┘     └─────────────┘                                   │   │    │
│  │   │                                                                          │   │    │
│  │   └─────────────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  OPTION 3: OCI Container Instances                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                   │    │
│  │   ┌─────────────────────────────────────────────────────────────────────────┐   │    │
│  │   │                    OCI Container Instances                               │   │    │
│  │   │                                                                          │   │    │
│  │   │   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │   │    │
│  │   │   │  Streamlit  │     │  FastAPI    │     │  Oracle ADB │               │   │    │
│  │   │   │  Instance   │────►│  Instance   │────►│  (Same VCN) │               │   │    │
│  │   │   └─────────────┘     └─────────────┘     └─────────────┘               │   │    │
│  │   │         │                                                                │   │    │
│  │   │         ▼                                                                │   │    │
│  │   │   ┌─────────────┐                                                        │   │    │
│  │   │   │ OCI Load    │                                                        │   │    │
│  │   │   │ Balancer    │◄──── Public Internet                                  │   │    │
│  │   │   └─────────────┘                                                        │   │    │
│  │   │                                                                          │   │    │
│  │   └─────────────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.1  
**Last Updated:** January 2026  
**System:** Insurance Claims Processing Multi-Agent Application  
**New in v1.1:** Image Vectorization with CLIP for fraud detection
