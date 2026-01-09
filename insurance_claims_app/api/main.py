"""
FastAPI Backend for Insurance Claims Processing
Supervisor-Based Multi-Agent System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_database, seed_sample_policies,
    create_claim, get_claim, update_claim, get_all_claims,
    get_policy, get_all_policies,
    save_chat_message, get_chat_history,
    ImageVectorStore
)
# Import both legacy and supervisor workflows
from agents import process_claim, InsuranceChatbotAgent
from agents.supervisor_workflow import process_claim_with_supervisor
from agents.supervisor_agent import ClaimsSupervisorAgent

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Claims Processing API",
    description="Supervisor-based multi-agent system for processing insurance claims",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot and supervisor (lazy loading)
_chatbot = None
_image_store = None
_supervisor = None

def get_chatbot():
    global _chatbot
    if _chatbot is None:
        _chatbot = InsuranceChatbotAgent()
    return _chatbot

def get_image_store():
    global _image_store
    if _image_store is None:
        _image_store = ImageVectorStore()
    return _image_store

def get_supervisor():
    global _supervisor
    if _supervisor is None:
        _supervisor = ClaimsSupervisorAgent()
    return _supervisor

# Pydantic models
class ClaimSubmission(BaseModel):
    policy_id: str = Field(..., description="Policy ID")
    incident_date: str = Field(..., description="Date of incident (ISO format)")
    claim_date: str = Field(..., description="Date claim is filed (ISO format)")
    claim_type: str = Field(..., description="Type: collision, comprehensive, liability")
    damage_description: str = Field(..., description="Description of damage")
    repair_shop: Optional[str] = Field(None, description="Repair shop name")
    estimated_damage_amount: float = Field(..., description="Estimated damage amount")
    damage_photos: Optional[List[str]] = Field(default=[], description="List of photo paths/URLs")
    incident_report: Optional[str] = Field(None, description="Incident report text")
    repair_estimate: Optional[str] = Field(None, description="Repair estimate document")

class ChatMessage(BaseModel):
    claim_id: Optional[str] = Field(None, description="Claim ID for context")
    message: str = Field(..., description="Customer message")

class ClaimResponse(BaseModel):
    claim_id: str
    validation_status: str
    validation_reason: str
    approval_status: str
    approval_reason: str
    payout_amount: float
    deductible: float
    processing_days: int
    fraud_score: Optional[float]
    # Supervisor workflow fields
    supervisor_priority: Optional[str] = None
    workflow_history: Optional[List[Dict[str, Any]]] = None
    human_review_required: Optional[bool] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    claim_id: Optional[str]

# Startup event
@app.on_event("startup")
async def startup_event():
    init_database()
    seed_sample_policies()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Submit claim
@app.post("/submit-claim", response_model=ClaimResponse)
async def submit_claim(claim: ClaimSubmission):
    """Submit a new insurance claim and process through supervisor workflow"""
    try:
        # Get customer_id from policy
        policy = get_policy(claim.policy_id)
        customer_id = policy.get("customer_id", "UNKNOWN") if policy else "UNKNOWN"
        
        # Create claim in database
        claim_data = claim.model_dump()
        claim_data["customer_id"] = customer_id
        claim_id = create_claim(claim_data)
        claim_data["claim_id"] = claim_id
        
        # Process through SUPERVISOR workflow (new multi-agent system)
        result = process_claim_with_supervisor(claim_data)
        
        # Update claim in database with results
        update_claim(claim_id, {
            "validation_status": result.get("validation_status"),
            "validation_reason": result.get("validation_reason"),
            "approval_status": result.get("approval_status"),
            "approval_reason": result.get("approval_reason"),
            "payout_amount": result.get("payout_amount", 0),
            "deductible": result.get("deductible", 0),
            "processing_time_days": result.get("processing_days", 0),
            "fraud_score": result.get("fraud_score")
        })
        
        return ClaimResponse(
            claim_id=claim_id,
            validation_status=result.get("validation_status", "PENDING"),
            validation_reason=result.get("validation_reason", ""),
            approval_status=result.get("approval_status", "PENDING"),
            approval_reason=result.get("approval_reason", ""),
            payout_amount=result.get("payout_amount", 0),
            deductible=result.get("deductible", 0),
            processing_days=result.get("processing_days", 0),
            fraud_score=result.get("fraud_score"),
            supervisor_priority=result.get("supervisor_priority"),
            workflow_history=result.get("workflow_history"),
            human_review_required=result.get("human_review_required", False)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Submit claim with images (multipart form)
@app.post("/submit-claim-with-images", response_model=ClaimResponse)
async def submit_claim_with_images(
    policy_id: str = Form(...),
    incident_date: str = Form(...),
    claim_date: str = Form(...),
    claim_type: str = Form(...),
    damage_description: str = Form(...),
    estimated_damage_amount: float = Form(...),
    repair_shop: Optional[str] = Form(None),
    incident_report: Optional[str] = Form(None),
    repair_estimate: Optional[str] = Form(None),
    damage_photos: List[UploadFile] = File(default=[])
):
    """Submit a new insurance claim with actual image uploads for vectorization"""
    try:
        # Get customer_id from policy
        policy = get_policy(policy_id)
        customer_id = policy.get("customer_id", "UNKNOWN") if policy else "UNKNOWN"
        
        # Prepare photo list for claim data
        photo_names = [photo.filename for photo in damage_photos] if damage_photos else []
        
        # Create claim in database
        claim_data = {
            "policy_id": policy_id,
            "incident_date": incident_date,
            "claim_date": claim_date,
            "claim_type": claim_type,
            "damage_description": damage_description,
            "estimated_damage_amount": estimated_damage_amount,
            "repair_shop": repair_shop or "Unknown",
            "incident_report": incident_report,
            "repair_estimate": repair_estimate,
            "damage_photos": photo_names,
            "customer_id": customer_id
        }
        
        claim_id = create_claim(claim_data)
        claim_data["claim_id"] = claim_id
        
        # Process images through ImageVectorStore
        image_fraud_check = {"is_potential_duplicate": False, "fraud_risk": "LOW"}
        if damage_photos:
            image_store = get_image_store()
            images_to_store = []
            
            for photo in damage_photos:
                image_bytes = await photo.read()
                images_to_store.append((photo.filename, image_bytes))
                
                # Check for duplicate images (fraud detection)
                if len(image_bytes) > 0:
                    fraud_check = image_store.check_for_duplicate_images(image_bytes)
                    if fraud_check["is_potential_duplicate"]:
                        image_fraud_check = fraud_check
                        print(f"⚠️ Potential duplicate image detected! Similar to claims: {fraud_check['similar_claims']}")
            
            # Store all images with embeddings
            if images_to_store:
                image_ids = image_store.add_images_batch(claim_id, images_to_store, claim_type)
                print(f"✅ Stored {len(image_ids)} images for claim {claim_id}")
        
        # Add image fraud info to claim data for workflow
        claim_data["image_fraud_check"] = image_fraud_check
        
        # Process through SUPERVISOR workflow (new multi-agent system)
        result = process_claim_with_supervisor(claim_data)
        
        # Adjust fraud score if duplicate images detected
        fraud_score = result.get("fraud_score", 0)
        if image_fraud_check.get("is_potential_duplicate"):
            fraud_score = max(fraud_score, 0.8)  # Boost fraud score for duplicate images
            result["fraud_flags"] = result.get("fraud_flags", []) + ["DUPLICATE_IMAGE_DETECTED"]
        
        # Update claim in database with results
        update_claim(claim_id, {
            "validation_status": result.get("validation_status"),
            "validation_reason": result.get("validation_reason"),
            "approval_status": result.get("approval_status"),
            "approval_reason": result.get("approval_reason"),
            "payout_amount": result.get("payout_amount", 0),
            "deductible": result.get("deductible", 0),
            "processing_time_days": result.get("processing_days", 0),
            "fraud_score": fraud_score
        })
        
        return ClaimResponse(
            claim_id=claim_id,
            validation_status=result.get("validation_status", "PENDING"),
            validation_reason=result.get("validation_reason", ""),
            approval_status=result.get("approval_status", "PENDING"),
            approval_reason=result.get("approval_reason", ""),
            payout_amount=result.get("payout_amount", 0),
            deductible=result.get("deductible", 0),
            processing_days=result.get("processing_days", 0),
            fraud_score=fraud_score,
            supervisor_priority=result.get("supervisor_priority"),
            workflow_history=result.get("workflow_history"),
            human_review_required=result.get("human_review_required", False)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Get claim status
@app.get("/claim/{claim_id}")
async def get_claim_status(claim_id: str):
    """Get status and details of a claim"""
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Convert non-serializable types
    result = {}
    for key, value in claim.items():
        if isinstance(value, bytes):
            result[key] = None  # Skip binary data
        elif hasattr(value, 'isoformat'):  # datetime objects
            result[key] = value.isoformat()
        else:
            result[key] = value
    
    return result

# List all claims
@app.get("/claims")
async def list_claims():
    """List all claims"""
    return get_all_claims()

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Send a message to the insurance chatbot"""
    try:
        chatbot = get_chatbot()
        response = chatbot.answer_question(message.message, message.claim_id)
        
        # Save chat history only if claim exists
        if message.claim_id:
            claim = get_claim(message.claim_id)
            if claim:
                try:
                    save_chat_message(message.claim_id, message.message, response["answer"])
                except Exception as e:
                    print(f"Warning: Could not save chat history: {e}")
        
        return ChatResponse(
            answer=response["answer"],
            sources=response.get("sources", []),
            claim_id=message.claim_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get chat history
@app.get("/chat-history/{claim_id}")
async def get_claim_chat_history(claim_id: str):
    """Get chat history for a claim"""
    return get_chat_history(claim_id)

# Get policy
@app.get("/policy/{policy_id}")
async def get_policy_details(policy_id: str):
    """Get policy details"""
    policy = get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

# List policies
@app.get("/policies")
async def list_policies():
    """List all policies"""
    return get_all_policies()

# Get claim images
@app.get("/claim/{claim_id}/images")
async def get_claim_images(claim_id: str):
    """Get all images for a claim"""
    try:
        image_store = get_image_store()
        images = image_store.get_claim_images(claim_id)
        return {"claim_id": claim_id, "images": images, "count": len(images)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get image data
@app.get("/image/{image_id}")
async def get_image(image_id: str):
    """Get raw image data by ID"""
    try:
        image_store = get_image_store()
        image_data = image_store.get_image_data(image_id)
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_data, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Find similar images (fraud detection)
@app.post("/check-image-fraud")
async def check_image_fraud(image: UploadFile = File(...)):
    """Check if an uploaded image is similar to existing images (fraud detection)"""
    try:
        image_bytes = await image.read()
        image_store = get_image_store()
        result = image_store.check_for_duplicate_images(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get image store stats
@app.get("/image-store/stats")
async def get_image_store_stats():
    """Get statistics about the image vector store"""
    try:
        image_store = get_image_store()
        count = image_store.get_image_count()
        return {"total_images": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== SUPERVISOR WORKFLOW ENDPOINTS ==============

@app.get("/workflow/agents")
async def get_workflow_agents():
    """Get information about all agents in the supervisor workflow"""
    return {
        "supervisor": {
            "name": "Supervisor Agent",
            "description": "Central coordinator that orchestrates all specialized agents",
            "responsibilities": [
                "Analyze claim complexity",
                "Route claims to appropriate agents",
                "Coordinate parallel execution",
                "Handle human-in-the-loop escalation"
            ]
        },
        "document_analyzer": {
            "name": "Document Analyzer Agent",
            "description": "Analyzes uploaded documents and damage photos",
            "responsibilities": [
                "Analyze damage photos using AI",
                "Check for duplicate/fraudulent images",
                "Assess document quality and completeness"
            ]
        },
        "validation": {
            "name": "Validation Agent",
            "description": "Validates claim eligibility",
            "responsibilities": [
                "Check filing timeline (30-day limit)",
                "Verify policy active status",
                "Match coverage type",
                "Verify required documents",
                "Validate damage estimate"
            ]
        },
        "fraud_investigation": {
            "name": "Fraud Investigation Agent",
            "description": "Deep fraud analysis for suspicious claims",
            "responsibilities": [
                "Comprehensive fraud scoring",
                "Pattern analysis across claims",
                "Repair shop reputation check",
                "Customer history analysis"
            ]
        },
        "approval": {
            "name": "Approval Agent",
            "description": "Makes final approval decisions",
            "responsibilities": [
                "Process approval decision",
                "Calculate payout amount",
                "Determine processing timeline"
            ]
        },
        "human_review": {
            "name": "Human Review Handler",
            "description": "Escalates complex cases for human review",
            "responsibilities": [
                "Flag claims requiring manual review",
                "Prepare case summary for reviewers"
            ]
        }
    }

@app.get("/workflow/architecture")
async def get_workflow_architecture():
    """Get the supervisor workflow architecture diagram"""
    return {
        "type": "supervisor_based_multi_agent",
        "version": "2.0",
        "description": "Hierarchical multi-agent system with central supervisor coordination",
        "flow": """
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
              ┌────►│ SUPERVISOR  │◄────┐
              │     └──────┬──────┘     │
              │            │            │
              │     ┌──────┴──────┐     │
              │     │   ROUTER    │     │
              │     └──────┬──────┘     │
              │            │            │
        ┌─────┴─────┬──────┼──────┬─────┴─────┐
        │           │      │      │           │
        ▼           ▼      ▼      ▼           ▼
    ┌───────┐  ┌────────┐ ┌────┐ ┌──────┐ ┌───────┐
    │DOC    │  │VALIDATE│ │FRAUD│ │APPROVE│ │HUMAN │
    │ANALYZE│  │        │ │INV  │ │       │ │REVIEW│
    └───┬───┘  └───┬────┘ └──┬──┘ └───┬───┘ └───┬───┘
        │          │         │        │         │
        └──────────┴─────────┴────────┴─────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    END      │
                    └─────────────┘
        """,
        "routing_logic": {
            "started": "If photos present → document_analyzer, else → validation",
            "document_analysis_complete": "→ validation",
            "validation_complete": {
                "INVALID": "→ complete (denied)",
                "VALID + high_complexity": "→ fraud_investigation",
                "VALID + low_complexity": "→ approval"
            },
            "fraud_investigation_complete": {
                "fraud_score > 0.8": "→ human_review",
                "fraud_score <= 0.8": "→ approval"
            },
            "approval_complete": {
                "NEEDS_REVIEW": "→ human_review",
                "APPROVED/DENIED": "→ complete"
            }
        }
    }

@app.get("/workflow/stats")
async def get_workflow_stats():
    """Get statistics about workflow processing"""
    try:
        claims = get_all_claims()
        
        stats = {
            "total_claims": len(claims),
            "by_status": {
                "APPROVED": 0,
                "DENIED": 0,
                "NEEDS_REVIEW": 0,
                "PENDING": 0
            },
            "by_priority": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "average_fraud_score": 0,
            "human_review_required": 0
        }
        
        total_fraud_score = 0
        fraud_count = 0
        
        for claim in claims:
            status = claim.get("approval_status", "PENDING")
            if status in stats["by_status"]:
                stats["by_status"][status] += 1
            else:
                stats["by_status"]["PENDING"] += 1
            
            if claim.get("fraud_score"):
                total_fraud_score += claim["fraud_score"]
                fraud_count += 1
        
        if fraud_count > 0:
            stats["average_fraud_score"] = round(total_fraud_score / fraud_count, 3)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
