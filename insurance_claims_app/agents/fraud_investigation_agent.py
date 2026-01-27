"""
Fraud Investigation Agent
Deep fraud analysis for suspicious claims
"""
from typing import Dict, Any, List
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from external_apis import FraudScoringAPI, PolicyManagementAPI
from .state import ClaimState


class FraudInvestigationAgent:
    """
    Agent that performs deep fraud investigation on suspicious claims.
    
    Responsibilities:
    1. Comprehensive fraud scoring
    2. Pattern analysis across historical claims
    3. Repair shop reputation check
    4. Customer claim history analysis
    5. Image fraud detection
    """
    
    def __init__(self):
        self.fraud_api = FraudScoringAPI(config.FRAUD_API_KEY)
        self.policy_api = PolicyManagementAPI(config.POLICY_API_KEY)
    
    def investigate(self, state: ClaimState) -> ClaimState:
        """
        Perform comprehensive fraud investigation.
        
        Returns updated state with fraud investigation results.
        """
        investigation_results = {
            "investigation_complete": True,
            "risk_factors": [],
            "mitigating_factors": [],
            "recommendation": "",
            "confidence": 0
        }
        
        # 1. Get base fraud score
        fraud_assessment = self._get_fraud_assessment(state)
        state["fraud_assessment"] = fraud_assessment
        state["fraud_score"] = fraud_assessment["fraud_score"]
        state["fraud_flags"] = fraud_assessment.get("fraud_indicators", [])
        
        # 2. Analyze claim patterns
        pattern_analysis = self._analyze_claim_patterns(state)
        investigation_results["pattern_analysis"] = pattern_analysis
        if pattern_analysis.get("suspicious_patterns"):
            investigation_results["risk_factors"].extend(pattern_analysis["suspicious_patterns"])
        
        # 3. Check repair shop reputation
        shop_check = self._check_repair_shop(state.get("repair_shop", ""))
        investigation_results["repair_shop_check"] = shop_check
        if shop_check.get("risk_level") == "high":
            investigation_results["risk_factors"].append(f"High-risk repair shop: {shop_check.get('reason', 'Unknown')}")
        elif shop_check.get("risk_level") == "low":
            investigation_results["mitigating_factors"].append("Reputable repair shop")
        
        # 4. Analyze customer history
        customer_analysis = self._analyze_customer_history(state.get("customer_id", ""))
        investigation_results["customer_analysis"] = customer_analysis
        if customer_analysis.get("risk_factors"):
            investigation_results["risk_factors"].extend(customer_analysis["risk_factors"])
        if customer_analysis.get("positive_factors"):
            investigation_results["mitigating_factors"].extend(customer_analysis["positive_factors"])
        
        # 5. Check for image fraud (if document analysis was done)
        if state.get("document_analysis", {}).get("duplicate_images"):
            investigation_results["risk_factors"].append("Duplicate images detected from other claims")
            state["fraud_score"] = min(1.0, state["fraud_score"] + 0.2)
        
        # 5b. Check for image fraud from API-level detection (image vector store)
        image_fraud_check = state.get("image_fraud_check", {})
        if image_fraud_check.get("is_potential_duplicate"):
            similar_claims = image_fraud_check.get("similar_claims", [])
            highest_similarity = image_fraud_check.get("highest_similarity", 0)
            investigation_results["risk_factors"].append(
                f"DUPLICATE IMAGE DETECTED: Same image found in claims {similar_claims} "
                f"(similarity: {highest_similarity:.2%})"
            )
            # Significantly boost fraud score for duplicate images
            state["fraud_score"] = min(1.0, state["fraud_score"] + 0.3)
            state["fraud_flags"] = state.get("fraud_flags", []) + ["DUPLICATE_IMAGE_FRAUD"]
        
        # 6. Calculate final recommendation
        final_score = state["fraud_score"]
        risk_count = len(investigation_results["risk_factors"])
        mitigating_count = len(investigation_results["mitigating_factors"])
        
        # Adjust score based on investigation
        if risk_count > mitigating_count:
            final_score = min(1.0, final_score + 0.1 * (risk_count - mitigating_count))
        elif mitigating_count > risk_count:
            final_score = max(0.0, final_score - 0.05 * (mitigating_count - risk_count))
        
        state["fraud_score"] = round(final_score, 3)
        
        # Determine recommendation
        if final_score > 0.8:
            investigation_results["recommendation"] = "DENY - High fraud probability"
            investigation_results["confidence"] = 0.9
        elif final_score > 0.6:
            investigation_results["recommendation"] = "ESCALATE - Requires human review"
            investigation_results["confidence"] = 0.7
        elif final_score > 0.4:
            investigation_results["recommendation"] = "APPROVE_WITH_MONITORING - Moderate risk"
            investigation_results["confidence"] = 0.75
        else:
            investigation_results["recommendation"] = "APPROVE - Low fraud risk"
            investigation_results["confidence"] = 0.85
        
        # Update state
        state["fraud_investigation"] = investigation_results
        state["current_step"] = "fraud_investigation_complete"
        
        return state
    
    def _get_fraud_assessment(self, state: ClaimState) -> Dict[str, Any]:
        """Get fraud assessment from Fraud Scoring API"""
        return self.fraud_api.score_claim(
            claim_amount=state.get("estimated_damage_amount", 0),
            repair_shop=state.get("repair_shop", ""),
            claimant_id=state.get("customer_id", ""),
            vehicle_age=5,  # Default, would come from vehicle data
            damage_type=state.get("claim_type", "collision")
        )
    
    def _analyze_claim_patterns(self, state: ClaimState) -> Dict[str, Any]:
        """Analyze patterns that might indicate fraud"""
        suspicious_patterns = []
        
        # Check claim timing
        try:
            incident_date = datetime.fromisoformat(state.get("incident_date", ""))
            claim_date = datetime.fromisoformat(state.get("claim_date", ""))
            
            # Claims filed very quickly might be pre-planned
            days_diff = (claim_date - incident_date).days
            if days_diff == 0:
                suspicious_patterns.append("Claim filed same day as incident")
            
            # Weekend incidents
            if incident_date.weekday() >= 5:
                suspicious_patterns.append("Incident occurred on weekend")
        except:
            pass
        
        # Check amount patterns
        amount = state.get("estimated_damage_amount", 0)
        
        # Round numbers are sometimes suspicious
        if amount > 1000 and amount % 1000 == 0:
            suspicious_patterns.append("Claim amount is a round number")
        
        # Very high amounts relative to typical claims
        if amount > 30000:
            suspicious_patterns.append("Claim amount significantly above average")
        
        return {
            "suspicious_patterns": suspicious_patterns,
            "pattern_count": len(suspicious_patterns)
        }
    
    def _check_repair_shop(self, repair_shop: str) -> Dict[str, Any]:
        """Check repair shop reputation"""
        if not repair_shop:
            return {"risk_level": "unknown", "reason": "No repair shop specified"}
        
        # Mock implementation - in production, would check against database
        # of known fraudulent or high-risk repair shops
        high_risk_keywords = ["quick", "fast", "cheap", "discount"]
        low_risk_keywords = ["certified", "authorized", "dealer", "oem"]
        
        shop_lower = repair_shop.lower()
        
        for keyword in high_risk_keywords:
            if keyword in shop_lower:
                return {
                    "risk_level": "high",
                    "reason": "Shop name contains high-risk keywords",
                    "shop_name": repair_shop
                }
        
        for keyword in low_risk_keywords:
            if keyword in shop_lower:
                return {
                    "risk_level": "low",
                    "reason": "Certified/authorized repair shop",
                    "shop_name": repair_shop
                }
        
        return {
            "risk_level": "medium",
            "reason": "Standard repair shop",
            "shop_name": repair_shop
        }
    
    def _analyze_customer_history(self, customer_id: str) -> Dict[str, Any]:
        """Analyze customer's claim history"""
        if not customer_id:
            return {"risk_factors": [], "positive_factors": []}
        
        risk_factors = []
        positive_factors = []
        
        # Mock implementation - in production, would query historical claims
        # For demo, we'll use customer_id patterns
        
        # Check if customer has filed multiple claims (mock)
        try:
            from database import get_claims_by_customer
            customer_claims = get_claims_by_customer(customer_id)
            
            if len(customer_claims) > 3:
                risk_factors.append(f"Customer has {len(customer_claims)} previous claims")
            elif len(customer_claims) == 0:
                positive_factors.append("First-time claimant")
            else:
                positive_factors.append(f"Customer has {len(customer_claims)} previous claims (normal)")
        except:
            # If we can't get history, note it
            pass
        
        return {
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "customer_id": customer_id
        }
