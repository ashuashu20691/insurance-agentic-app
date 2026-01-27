"""
LangGraph State Definition for Claims Processing Workflow
Supports both simple workflow and supervisor-based multi-agent workflow
"""
from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime


class ClaimState(TypedDict, total=False):
    """Base claim state for simple workflow (backward compatible)"""
    # Input fields
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
    
    # Validation Agent outputs
    validation_status: str  # VALID, INVALID
    validation_results: Dict[str, Any]
    validation_reason: str
    
    # Approval Agent outputs
    approval_status: str  # APPROVED, DENIED, NEEDS_REVIEW
    approval_reason: str
    payout_amount: float
    deductible: float
    processing_days: int
    fraud_score: float
    fraud_flags: List[str]
    
    # API response data
    damage_assessment: Dict[str, Any]
    policy_details: Dict[str, Any]
    fraud_assessment: Dict[str, Any]
    
    # Workflow metadata
    current_step: str
    error: Optional[str]
    completed_at: Optional[str]


class SupervisorClaimState(ClaimState, total=False):
    """
    Extended state for supervisor-based multi-agent workflow.
    Includes supervisor decision fields and workflow tracking.
    """
    # Supervisor Agent fields
    supervisor_decision: Literal["document_analyzer", "validation", "fraud_investigation", "approval", "human_review", "complete"]
    supervisor_reasoning: str
    supervisor_priority: Literal["low", "medium", "high", "critical"]
    
    # Complexity analysis
    complexity_analysis: Dict[str, Any]
    
    # Document Analyzer Agent outputs
    document_analysis: Dict[str, Any]
    document_issues: List[str]
    
    # Image fraud detection from API (vector store)
    image_fraud_check: Dict[str, Any]
    
    # Fraud Investigation Agent outputs
    fraud_investigation: Dict[str, Any]
    
    # Human Review fields
    human_review_required: bool
    human_review_reason: str
    human_review_decision: str
    human_reviewer_notes: str
    
    # Workflow tracking
    workflow_history: List[Dict[str, Any]]
    agents_invoked: List[str]
    total_processing_time_ms: int


class ChatState(TypedDict, total=False):
    """State for chatbot interactions"""
    chat_id: str
    claim_id: Optional[str]
    customer_id: Optional[str]
    messages: List[Dict[str, str]]
    current_question: str
    context: Dict[str, Any]
    sources: List[str]
