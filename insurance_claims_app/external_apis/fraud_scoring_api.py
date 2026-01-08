"""
Fraud Scoring API (Mock implementation - simulates Fraud.ai)
Scores fraud risk for insurance claims
"""
import random
from typing import Dict, Any, List

class FraudScoringAPI:
    """Mock Fraud Scoring API similar to Fraud.ai"""
    
    FRAUD_INDICATORS = [
        "multiple_claims_short_period",
        "high_value_claim_new_policy",
        "inconsistent_damage_description",
        "suspicious_repair_shop",
        "claim_filed_immediately_after_policy_start",
        "previous_fraud_history",
        "mismatched_vehicle_info",
        "staged_accident_pattern",
        "inflated_repair_estimate",
        "missing_documentation"
    ]
    
    RISK_LEVELS = {
        (0.0, 0.2): "LOW",
        (0.2, 0.4): "MODERATE_LOW",
        (0.4, 0.7): "MODERATE_HIGH",
        (0.7, 1.0): "HIGH"
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def score_claim(
        self,
        claim_amount: float,
        repair_shop: str,
        claimant_id: str,
        vehicle_age: int,
        damage_type: str
    ) -> Dict[str, Any]:
        """
        Score fraud risk for a claim
        
        Args:
            claim_amount: Total claim amount
            repair_shop: Name of repair shop
            claimant_id: Customer/claimant ID
            vehicle_age: Age of vehicle in years
            damage_type: Type of damage (collision, comprehensive, liability)
            
        Returns:
            Dict with fraud_score, fraud_indicators, risk_level
        """
        # Mock scoring logic
        base_score = 0.15
        indicators = []
        
        # High claim amount increases risk
        if claim_amount > 15000:
            base_score += 0.15
            indicators.append("high_value_claim")
        elif claim_amount > 8000:
            base_score += 0.08
        
        # Old vehicle with high claim is suspicious
        if vehicle_age > 10 and claim_amount > 10000:
            base_score += 0.2
            indicators.append("high_claim_old_vehicle")
        
        # Unknown repair shops are riskier
        known_shops = ["certified_auto", "dealer_service", "national_chain"]
        if repair_shop and not any(shop in repair_shop.lower() for shop in known_shops):
            base_score += 0.1
            indicators.append("unverified_repair_shop")
        
        # Add some randomness for simulation
        base_score += random.uniform(-0.1, 0.15)
        
        # Clamp score between 0 and 1
        fraud_score = max(0.0, min(1.0, base_score))
        
        # Determine risk level
        risk_level = "LOW"
        for (low, high), level in self.RISK_LEVELS.items():
            if low <= fraud_score < high:
                risk_level = level
                break
        
        # Add random indicators for high scores
        if fraud_score > 0.5:
            additional = random.sample(self.FRAUD_INDICATORS, min(2, len(self.FRAUD_INDICATORS)))
            indicators.extend([i for i in additional if i not in indicators])
        
        return {
            "fraud_score": round(fraud_score, 3),
            "fraud_indicators": indicators,
            "risk_level": risk_level,
            "recommendation": self._get_recommendation(fraud_score),
            "confidence": round(random.uniform(0.75, 0.95), 2)
        }
    
    def _get_recommendation(self, score: float) -> str:
        if score < 0.2:
            return "AUTO_APPROVE"
        elif score < 0.4:
            return "APPROVE_WITH_MONITORING"
        elif score < 0.7:
            return "MANUAL_REVIEW_RECOMMENDED"
        else:
            return "INVESTIGATION_REQUIRED"
