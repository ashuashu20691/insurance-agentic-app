"""
LangGraph State Definition for Claims Processing Workflow
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime

class ClaimState(TypedDict, total=False):
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
