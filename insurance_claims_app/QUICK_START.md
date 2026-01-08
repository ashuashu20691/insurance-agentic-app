# Quick Start Guide

## Current Status

✅ Application built and ready to test
⚠️ Oracle database account expired - needs password reset

## Fix Database Issue

The testuser account has expired. Run this command to fix it:

```bash
sqlplus sys/YourSysPassword@140.238.167.101:1521/FREEPDB1 as sysdba
```

Then execute:
```sql
ALTER USER testuser IDENTIFIED BY Password123 ACCOUNT UNLOCK;
ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;
EXIT;
```

## Test the System

Once the password is reset:

```bash
cd insurance_claims_app

# Test database connection
./venv/bin/python test_db_connection.py

# Run complete system test
./venv/bin/python test_complete_system.py
```

## Install All Dependencies

```bash
./venv/bin/pip install -r requirements.txt
```

This will install:
- LangChain & LangGraph (multi-agent framework)
- OCI SDK (for GenAI)
- FastAPI & Uvicorn (backend API)
- Streamlit (frontend UI)
- ChromaDB (vector store for RAG)
- Sentence Transformers (embeddings)

## Run the Application

### Terminal 1: Start API Server
```bash
./venv/bin/python run_api.py
```
API will be at: http://localhost:8000

### Terminal 2: Start Streamlit UI
```bash
./venv/bin/python run_ui.py
```
UI will be at: http://localhost:8501

## Test Scenarios

The system includes 3 sample policies:
- **POL-001**: Comprehensive ($50K limit, $500 deductible) - Active
- **POL-002**: Collision ($30K limit, $1000 deductible) - Active  
- **POL-003**: Liability ($100K limit, $250 deductible) - Inactive

### Test Case 1: Valid Claim (Should Approve)
- Policy: POL-001
- Incident Date: 5 days ago
- Claim Type: collision
- Damage: $5,000
- Expected: APPROVED with payout ~$4,500

### Test Case 2: Late Filing (Should Deny)
- Policy: POL-001
- Incident Date: 45 days ago
- Expected: INVALID - filed too late

### Test Case 3: Inactive Policy (Should Deny)
- Policy: POL-003
- Expected: INVALID - policy not active

## Architecture

```
Streamlit UI (Port 8501)
    ↓
FastAPI Backend (Port 8000)
    ↓
LangGraph Workflow
    ├── Validation Agent → Approval Agent
    └── Chatbot Agent (RAG)
    ↓
External APIs (Mock)
    ├── Car Damage Detection
    ├── Fraud Scoring
    └── Policy Management
    ↓
Oracle Database (140.238.167.101:1521)
```

## Features

### 1. Claims Validation Agent
- Checks filing timeline (30 days)
- Verifies policy active status
- Validates coverage match
- Ensures documents submitted
- Validates damage estimate

### 2. Claims Approval Agent
- Calls Car Damage API for assessment
- Calls Fraud Scoring API (0-1 scale)
- Makes approval decision:
  - Fraud > 0.7 → NEEDS_REVIEW
  - Fraud 0.4-0.7 → APPROVED (monitored)
  - Fraud < 0.4 → AUTO_APPROVED
- Calculates payout: damage - deductible (capped at limit)
- Sets processing time: 2-10 days based on fraud score

### 3. Insurance Chatbot Agent
- RAG from policy documents
- Answers questions about:
  - Policy coverage
  - Deductibles
  - Payout amounts
  - Processing times
  - Appeal process
  - Rental car coverage

## API Endpoints

- `GET /health` - Health check
- `POST /submit-claim` - Submit new claim
- `GET /claim/{claim_id}` - Get claim status
- `GET /claims` - List all claims
- `POST /chat` - Chat with bot
- `GET /policies` - List policies

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
./venv/bin/python test_db_connection.py

# Check Oracle is running
tnsping 140.238.167.101:1521/FREEPDB1
```

### Missing Dependencies
```bash
# Install all at once
./venv/bin/pip install -r requirements.txt

# Or install individually
./venv/bin/pip install langchain langgraph oci fastapi streamlit
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

## Next Steps

1. ✅ Fix Oracle password
2. ✅ Run test_complete_system.py
3. ✅ Install all dependencies
4. ✅ Start API server
5. ✅ Start UI
6. ✅ Submit test claims
7. ✅ Test chatbot
