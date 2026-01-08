"""
Claims Validation Agent
Validates claim eligibility based on policy and claim details
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from external_apis import PolicyManagementAPI
from .state import ClaimState

class ClaimsValidationAgent:
    """Agent that validates insurance claims for eligibility"""
    
    def __init__(self):
        self.policy_api = PolicyManagementAPI(config.POLICY_API_KEY)
    
    def validate_claim(self, state: ClaimState) -> ClaimState:
        """
        Validate a claim and return updated state
        
        Checks:
        1. Claim filed within 30 days of incident
        2. Policy was active on incident date
        3. Claim type matches policy coverage
        4. All required documents submitted
        5. Damage estimate is reasonable
        """
        validation_results = {}
        all_valid = True
        reasons = []
        
        # 1. Check filing timeline (within 30 days)
        timeline_check = self._check_filing_timeline(
            state.get("incident_date"),
            state.get("claim_date")
        )
        validation_results["filing_timeline"] = timeline_check
        if timeline_check["status"] != "PASS":
            all_valid = False
            reasons.append(timeline_check["reason"])
        
        # 2. Check policy active on incident date
        policy_check = self._check_policy_active(
            state.get("policy_id"),
            state.get("incident_date")
        )
        validation_results["policy_active"] = policy_check
        if policy_check["status"] != "PASS":
            all_valid = False
            reasons.append(policy_check["reason"])
        
        # Store policy details in state
        policy_details = policy_check.get("policy_details", {})
        
        # 3. Check coverage type match
        coverage_check = self._check_coverage_match(
            state.get("policy_id"),
            state.get("claim_type"),
            state.get("incident_date")
        )
        validation_results["coverage_match"] = coverage_check
        if coverage_check["status"] != "PASS":
            all_valid = False
            reasons.append(coverage_check["reason"])
        
        # 4. Check required documents
        docs_check = self._check_required_documents(
            state.get("damage_photos", []),
            state.get("incident_report"),
            state.get("repair_estimate")
        )
        validation_results["documents"] = docs_check
        if docs_check["status"] != "PASS":
            all_valid = False
            reasons.append(docs_check["reason"])
        
        # 5. Check damage estimate reasonableness
        estimate_check = self._check_damage_estimate(
            state.get("estimated_damage_amount", 0),
            policy_details.get("coverage_limit", 50000)
        )
        validation_results["damage_estimate"] = estimate_check
        if estimate_check["status"] != "PASS":
            all_valid = False
            reasons.append(estimate_check["reason"])
        
        # Update state
        state["validation_status"] = "VALID" if all_valid else "INVALID"
        state["validation_results"] = validation_results
        state["validation_reason"] = "; ".join(reasons) if reasons else "All validation checks passed"
        state["policy_details"] = policy_details
        state["current_step"] = "validation_complete"
        
        return state
    
    def _check_filing_timeline(self, incident_date: str, claim_date: str) -> Dict[str, Any]:
        """Check if claim was filed within 30 days of incident"""
        try:
            incident_dt = datetime.fromisoformat(incident_date)
            claim_dt = datetime.fromisoformat(claim_date)
            
            days_diff = (claim_dt - incident_dt).days
            
            if days_diff <= config.CLAIM_FILING_DAYS_LIMIT:
                return {
                    "status": "PASS",
                    "reason": f"Claim filed {days_diff} days after incident (within {config.CLAIM_FILING_DAYS_LIMIT} day limit)"
                }
            else:
                return {
                    "status": "FAIL",
                    "reason": f"Claim filed {days_diff} days after incident (exceeds {config.CLAIM_FILING_DAYS_LIMIT} day limit)"
                }
        except Exception as e:
            return {
                "status": "FAIL",
                "reason": f"Invalid date format: {str(e)}"
            }
    
    def _check_policy_active(self, policy_id: str, incident_date: str) -> Dict[str, Any]:
        """Check if policy was active on incident date"""
        policy = self.policy_api.get_policy_details(policy_id)
        
        if not policy:
            return {
                "status": "FAIL",
                "reason": f"Policy {policy_id} not found",
                "policy_details": {}
            }
        
        if not policy.get("is_active"):
            return {
                "status": "FAIL",
                "reason": f"Policy {policy_id} is not active",
                "policy_details": policy
            }
        
        # Check date range if available
        if policy.get("start_date") and policy.get("end_date"):
            try:
                incident_dt = datetime.fromisoformat(incident_date)
                start_dt = datetime.fromisoformat(policy["start_date"])
                end_dt = datetime.fromisoformat(policy["end_date"])
                
                if not (start_dt <= incident_dt <= end_dt):
                    return {
                        "status": "FAIL",
                        "reason": f"Incident date {incident_date} is outside policy period ({policy['start_date']} to {policy['end_date']})",
                        "policy_details": policy
                    }
            except:
                pass
        
        return {
            "status": "PASS",
            "reason": "Policy was active on incident date",
            "policy_details": policy
        }
    
    def _check_coverage_match(self, policy_id: str, claim_type: str, incident_date: str) -> Dict[str, Any]:
        """Check if claim type matches policy coverage"""
        coverage = self.policy_api.check_coverage(policy_id, claim_type, incident_date)
        
        if coverage.get("is_covered"):
            return {
                "status": "PASS",
                "reason": f"Claim type '{claim_type}' is covered under policy type '{coverage.get('policy_type')}'"
            }
        else:
            return {
                "status": "FAIL",
                "reason": coverage.get("reason", f"Claim type '{claim_type}' is not covered")
            }
    
    def _check_required_documents(self, photos: list, incident_report: str, repair_estimate: str) -> Dict[str, Any]:
        """Check if all required documents are submitted"""
        missing = []
        
        if not photos or len(photos) == 0:
            missing.append("damage photos")
        
        if not incident_report:
            missing.append("incident report")
        
        if not repair_estimate:
            missing.append("repair estimate")
        
        if missing:
            return {
                "status": "FAIL",
                "reason": f"Missing required documents: {', '.join(missing)}"
            }
        
        return {
            "status": "PASS",
            "reason": "All required documents submitted"
        }
    
    def _check_damage_estimate(self, estimated_amount: float, coverage_limit: float) -> Dict[str, Any]:
        """Check if damage estimate is reasonable"""
        if estimated_amount <= 0:
            return {
                "status": "FAIL",
                "reason": "Damage estimate must be greater than zero"
            }
        
        if estimated_amount > coverage_limit * 1.5:
            return {
                "status": "FAIL",
                "reason": f"Damage estimate ${estimated_amount:,.2f} significantly exceeds coverage limit ${coverage_limit:,.2f}"
            }
        
        return {
            "status": "PASS",
            "reason": f"Damage estimate ${estimated_amount:,.2f} is within reasonable range"
        }
