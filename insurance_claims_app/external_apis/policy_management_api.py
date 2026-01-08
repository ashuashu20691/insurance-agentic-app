"""
Policy Management API (Mock implementation - simulates Vertafore)
Retrieves policy information and coverage details
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _get_policy_from_db(policy_id: str):
    """Lazy import to avoid circular dependency"""
    from database import get_policy
    return get_policy(policy_id)

class PolicyManagementAPI:
    """Mock Policy Management API similar to Vertafore"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def get_policy_details(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get policy details from database
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Dict with policy details or None if not found
        """
        policy = _get_policy_from_db(policy_id)
        
        if not policy:
            return None
        
        # Parse riders JSON
        riders = []
        if policy.get("riders"):
            try:
                riders = json.loads(policy["riders"])
            except:
                riders = []
        
        return {
            "policy_id": policy["policy_id"],
            "customer_id": policy["customer_id"],
            "coverage_type": policy["coverage_type"],
            "coverage_limit": policy["coverage_limit"],
            "deductible": policy["deductible"],
            "is_active": bool(policy["is_active"]),
            "start_date": policy.get("start_date"),
            "end_date": policy.get("end_date"),
            "riders": riders,
            "endorsements": self._get_endorsements(policy["coverage_type"])
        }
    
    def check_coverage(self, policy_id: str, claim_type: str, incident_date: str) -> Dict[str, Any]:
        """
        Check if policy covers the claim type on incident date
        
        Args:
            policy_id: Policy identifier
            claim_type: Type of claim (collision, comprehensive, liability)
            incident_date: Date of incident
            
        Returns:
            Dict with coverage status and details
        """
        policy = self.get_policy_details(policy_id)
        
        if not policy:
            return {
                "is_covered": False,
                "reason": "Policy not found",
                "coverage_limit": 0,
                "deductible": 0
            }
        
        # Check if policy was active on incident date
        incident_dt = datetime.fromisoformat(incident_date) if isinstance(incident_date, str) else incident_date
        
        policy_active = policy["is_active"]
        if policy.get("start_date") and policy.get("end_date"):
            start = policy["start_date"] if isinstance(policy["start_date"], datetime) else datetime.fromisoformat(str(policy["start_date"]))
            end = policy["end_date"] if isinstance(policy["end_date"], datetime) else datetime.fromisoformat(str(policy["end_date"]))
            policy_active = start <= incident_dt <= end
        
        # Check coverage type match
        coverage_matches = self._check_coverage_match(policy["coverage_type"], claim_type)
        
        is_covered = policy_active and coverage_matches
        
        reason = "Covered" if is_covered else ""
        if not policy_active:
            reason = "Policy was not active on incident date"
        elif not coverage_matches:
            reason = f"Policy type '{policy['coverage_type']}' does not cover '{claim_type}' claims"
        
        return {
            "is_covered": is_covered,
            "reason": reason,
            "coverage_limit": policy["coverage_limit"] if is_covered else 0,
            "deductible": policy["deductible"],
            "policy_type": policy["coverage_type"],
            "riders": policy.get("riders", [])
        }
    
    def _check_coverage_match(self, policy_type: str, claim_type: str) -> bool:
        """Check if policy type covers the claim type"""
        coverage_map = {
            "comprehensive": ["collision", "comprehensive", "liability"],
            "collision": ["collision"],
            "liability": ["liability"]
        }
        return claim_type in coverage_map.get(policy_type, [])
    
    def _get_endorsements(self, coverage_type: str) -> list:
        """Get standard endorsements for coverage type"""
        endorsements = {
            "comprehensive": ["glass_coverage", "rental_reimbursement", "gap_coverage"],
            "collision": ["rental_reimbursement"],
            "liability": ["medical_payments"]
        }
        return endorsements.get(coverage_type, [])
