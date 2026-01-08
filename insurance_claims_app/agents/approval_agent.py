"""
Claims Approval Agent
Makes approval decisions and calculates payouts using external APIs
"""
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from external_apis import CarDamageAPI, FraudScoringAPI, PolicyManagementAPI
from .state import ClaimState

class ClaimsApprovalAgent:
    """Agent that approves/denies claims and calculates payouts"""
    
    def __init__(self):
        self.damage_api = CarDamageAPI(config.ARYA_API_KEY)
        self.fraud_api = FraudScoringAPI(config.FRAUD_API_KEY)
        self.policy_api = PolicyManagementAPI(config.POLICY_API_KEY)
    
    def process_approval(self, state: ClaimState) -> ClaimState:
        """
        Process claim approval decision
        
        Steps:
        1. Check validation status (if INVALID -> DENIED)
        2. Call Car Damage Detection API
        3. Call Fraud Scoring API
        4. Get policy coverage details
        5. Make approval decision
        6. Calculate payout
        """
        # If validation failed, deny immediately
        if state.get("validation_status") == "INVALID":
            state["approval_status"] = "DENIED"
            state["approval_reason"] = f"Validation failed: {state.get('validation_reason', 'Unknown reason')}"
            state["payout_amount"] = 0
            state["processing_days"] = 0
            state["current_step"] = "approval_complete"
            return state
        
        # 1. Get damage assessment from Car Damage API
        damage_assessment = self.damage_api.analyze_damage(
            photos=state.get("damage_photos", []),
            estimated_amount=state.get("estimated_damage_amount")
        )
        state["damage_assessment"] = damage_assessment
        
        # 2. Get fraud score
        fraud_assessment = self.fraud_api.score_claim(
            claim_amount=state.get("estimated_damage_amount", 0),
            repair_shop=state.get("repair_shop", ""),
            claimant_id=state.get("customer_id", ""),
            vehicle_age=5,  # Default, would come from vehicle data
            damage_type=state.get("claim_type", "collision")
        )
        state["fraud_assessment"] = fraud_assessment
        state["fraud_score"] = fraud_assessment["fraud_score"]
        state["fraud_flags"] = fraud_assessment.get("fraud_indicators", [])
        
        # 3. Get policy details (may already be in state from validation)
        policy_details = state.get("policy_details")
        if not policy_details:
            policy_details = self.policy_api.get_policy_details(state.get("policy_id"))
            state["policy_details"] = policy_details
        
        if not policy_details:
            state["approval_status"] = "DENIED"
            state["approval_reason"] = "Policy not found"
            state["payout_amount"] = 0
            state["processing_days"] = 0
            state["current_step"] = "approval_complete"
            return state
        
        # 4. Make approval decision based on fraud score
        fraud_score = fraud_assessment["fraud_score"]
        approval_status, approval_reason = self._make_decision(fraud_score, fraud_assessment)
        
        state["approval_status"] = approval_status
        state["approval_reason"] = approval_reason
        
        # 5. Calculate payout if approved
        if approval_status in ["APPROVED", "NEEDS_REVIEW"]:
            payout = self._calculate_payout(
                damage_amount=damage_assessment["total_estimated_repair_cost"],
                deductible=policy_details["deductible"],
                coverage_limit=policy_details["coverage_limit"]
            )
            state["payout_amount"] = payout
            state["deductible"] = policy_details["deductible"]
        else:
            state["payout_amount"] = 0
            state["deductible"] = policy_details["deductible"]
        
        # 6. Set processing days based on fraud score
        state["processing_days"] = self._get_processing_days(fraud_score)
        state["current_step"] = "approval_complete"
        
        return state
    
    def _make_decision(self, fraud_score: float, fraud_assessment: Dict) -> tuple:
        """Make approval decision based on fraud score"""
        if fraud_score > config.FRAUD_SCORE_HIGH:
            return (
                "NEEDS_REVIEW",
                f"High fraud risk detected (score: {fraud_score:.2f}). Manual review required. Indicators: {', '.join(fraud_assessment.get('fraud_indicators', []))}"
            )
        elif fraud_score > config.FRAUD_SCORE_MEDIUM:
            return (
                "APPROVED",
                f"Approved with monitoring flag. Moderate fraud risk (score: {fraud_score:.2f})"
            )
        else:
            return (
                "APPROVED",
                f"Auto-approved. Low fraud risk (score: {fraud_score:.2f})"
            )
    
    def _calculate_payout(self, damage_amount: float, deductible: float, coverage_limit: float) -> float:
        """Calculate payout amount"""
        payout = damage_amount - deductible
        payout = max(0, payout)  # Can't be negative
        payout = min(payout, coverage_limit)  # Cap at coverage limit
        return round(payout, 2)
    
    def _get_processing_days(self, fraud_score: float) -> int:
        """Determine processing days based on fraud score"""
        if fraud_score < config.FRAUD_SCORE_LOW:
            return 2
        elif fraud_score < 0.5:
            return 5
        else:
            return 10
