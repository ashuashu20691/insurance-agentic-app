# Insurance Claims Processing Multi-Agent Application

A production-ready multi-agent system for processing insurance claims using LangGraph, OCI GenAI, FastAPI, Oracle Database, and Streamlit.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Submit Claim │  │ Track Claim  │  │   Chatbot    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  POST /submit-claim  │  GET /claim/{id}  │  POST /chat          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                            │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │ Validation Agent │ ───► │  Approval Agent  │ ───► END       │
│  └──────────────────┘      └──────────────────┘                │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │  Chatbot Agent   │ (RAG + LLM)                              │
│  └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External APIs (Mock)                         │
│  Car Damage API │ Fraud Scoring │ Policy Mgmt │ Payment API    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Oracle Database                             │
│        Claims  │  Policies  │  Chat History                    │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Three Specialized Agents

1. **Claims Validation Agent** - Validates claim eligibility
2. **Claims Approval Agent** - Makes approval decisions and calculates payouts
3. **Insurance Chatbot Agent** - Answers customer questions using RAG

### External API Integrations (Mock)

- Car Damage Detection API (Arya.ai style)
- Fraud Scoring API (Fraud.ai style)
- Policy Management API (Vertafore style)
- Payment Processing API
- Document Management API

## Installation

```bash
cd insurance_claims_app
pip install -r requirements.txt
```

## Oracle Database Setup

### Option 1: Oracle Free (Local)
```bash
# Pull and run Oracle Free container
docker run -d --name oracle-free \
  -p 1521:1521 \
  -e ORACLE_PASSWORD=YourPassword123 \
  container-registry.oracle.com/database/free:latest

# Create user
sqlplus sys/YourPassword123@localhost:1521/FREEPDB1 as sysdba
CREATE USER insurance_user IDENTIFIED BY your_password;
GRANT CONNECT, RESOURCE, UNLIMITED TABLESPACE TO insurance_user;
```

### Option 2: Oracle Autonomous Database (Cloud)
1. Create an Autonomous Database in OCI
2. Download the wallet
3. Set wallet path in environment variables

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
```
# OCI GenAI
OCI_COMPARTMENT_ID=your_compartment_id
OCI_SERVICE_ENDPOINT=https://inference.generativeai.us-chicago-1.oci.oraclecloud.com
OCI_MODEL_ID=cohere.command-a-03-2025

# Oracle Database
ORACLE_USER=insurance_user
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/FREEPDB1

# For Autonomous Database (optional)
ORACLE_WALLET_LOCATION=/path/to/wallet
ORACLE_WALLET_PASSWORD=wallet_password
```

## Running the Application

### 1. Start the API Server

```bash
python run_api.py
```

API will be available at http://localhost:8000

### 2. Start the Streamlit UI

```bash
python run_ui.py
```

UI will be available at http://localhost:8501

### 3. Run Tests

```bash
python tests/test_workflow.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/submit-claim` | POST | Submit new claim |
| `/claim/{claim_id}` | GET | Get claim status |
| `/claims` | GET | List all claims |
| `/chat` | POST | Send chatbot message |
| `/chat-history/{claim_id}` | GET | Get chat history |
| `/policy/{policy_id}` | GET | Get policy details |
| `/policies` | GET | List all policies |

## Database Schema (Oracle)

### Claims Table
```sql
CREATE TABLE claims (
    claim_id VARCHAR2(50) PRIMARY KEY,
    policy_id VARCHAR2(50) NOT NULL,
    customer_id VARCHAR2(50) NOT NULL,
    incident_date TIMESTAMP NOT NULL,
    claim_date TIMESTAMP NOT NULL,
    claim_type VARCHAR2(20) NOT NULL,
    damage_description CLOB,
    repair_shop VARCHAR2(200),
    estimated_damage_amount NUMBER(12,2),
    validation_status VARCHAR2(20),
    validation_reason CLOB,
    fraud_score NUMBER(5,3),
    approval_status VARCHAR2(20),
    payout_amount NUMBER(12,2),
    deductible NUMBER(12,2),
    processing_time_days NUMBER(5),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Policies Table
```sql
CREATE TABLE policies (
    policy_id VARCHAR2(50) PRIMARY KEY,
    customer_id VARCHAR2(50) NOT NULL,
    coverage_type VARCHAR2(50) NOT NULL,
    coverage_limit NUMBER(12,2) NOT NULL,
    deductible NUMBER(12,2) NOT NULL,
    is_active NUMBER(1) DEFAULT 1,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    riders CLOB,
    policy_document BLOB
);
```

## Sample Policies

| Policy ID | Type | Coverage Limit | Deductible | Status |
|-----------|------|----------------|------------|--------|
| POL-001 | Comprehensive | $50,000 | $500 | Active |
| POL-002 | Collision | $30,000 | $1,000 | Active |
| POL-003 | Liability | $100,000 | $250 | Inactive |

## Workflow Logic

### Validation Checks
1. Claim filed within 30 days of incident
2. Policy active on incident date
3. Claim type matches policy coverage
4. All required documents submitted
5. Damage estimate is reasonable

### Approval Decision
- Fraud score > 0.7 → NEEDS_REVIEW
- Fraud score 0.4-0.7 → APPROVED (with monitoring)
- Fraud score < 0.4 → AUTO_APPROVED

### Payout Calculation
```
payout = min(damage_amount - deductible, coverage_limit)
```

### Processing Time
- Fraud score < 0.2 → 2 days
- Fraud score < 0.5 → 5 days
- Fraud score > 0.5 → 10 days
