"""
Supervisor Agent for Insurance Claims Processing
Central coordinator that orchestrates specialized agents using LangGraph
"""
from typing import Dict, Any, List, Literal, Optional
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field

from config import config


class SupervisorDecision(BaseModel):
    """Structured output for supervisor routing decisions"""
    next_agent: Literal["document_analyzer", "validation", "fraud_investigation", "approval", "human_review", "complete"]
    reasoning: str
    priority: Literal["low", "medium", "high", "critical"]
    parallel_agents: List[str] = Field(default_factory=list)


class ClaimsSupervisorAgent:
    """
    Supervisor Agent that orchestrates the claims processing workflow.
    
    Responsibilities:
    1. Analyze incoming claims and determine complexity
    2. Route claims to appropriate specialized agents
    3. Coordinate parallel agent execution when possible
    4. Handle human-in-the-loop for edge cases
    5. Make final decisions on claim routing
    """
    
    def __init__(self):
        self.llm = self._init_llm()
        self.agent_capabilities = {
            "document_analyzer": "Analyzes uploaded documents, photos, and extracts key information. Use for claims with images or complex documents.",
            "validation": "Validates claim eligibility - checks policy status, filing timeline, coverage match, required documents.",
            "fraud_investigation": "Deep fraud analysis for suspicious claims. Use when fraud score > 0.5 or multiple fraud indicators present.",
            "approval": "Makes final approval decision and calculates payout. Use after validation passes.",
            "human_review": "Escalates to human reviewer for complex edge cases requiring manual judgment.",
            "complete": "Marks the workflow as complete. Use when all processing is done."
        }
    
    def _init_llm(self):
        """Initialize OCI GenAI LLM for supervisor reasoning"""
        return ChatOCIGenAI(
            model_id=config.OCI_MODEL_ID,
            service_endpoint=config.OCI_SERVICE_ENDPOINT,
            compartment_id=config.OCI_COMPARTMENT_ID,
            auth_type="API_KEY",
            model_kwargs={"temperature": 0, "max_tokens": 500}
        )
    
    def analyze_claim_complexity(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze claim complexity to determine routing strategy.
        
        Factors considered:
        - Claim amount (high amounts = more scrutiny)
        - Number of damage photos
        - Claim type
        - Customer history (if available)
        - Time since incident
        """
        complexity_score = 0
        complexity_factors = []
        
        # Factor 1: Claim amount
        amount = state.get("estimated_damage_amount", 0)
        if amount > 50000:
            complexity_score += 3
            complexity_factors.append(f"High claim amount: ${amount:,.2f}")
        elif amount > 20000:
            complexity_score += 2
            complexity_factors.append(f"Moderate claim amount: ${amount:,.2f}")
        elif amount > 5000:
            complexity_score += 1
        
        # Factor 2: Number of photos (more photos = potentially more damage)
        photos = state.get("damage_photos", [])
        if len(photos) > 5:
            complexity_score += 2
            complexity_factors.append(f"Multiple damage photos: {len(photos)}")
        elif len(photos) > 2:
            complexity_score += 1
        
        # Factor 3: Claim type
        claim_type = state.get("claim_type", "").lower()
        high_complexity_types = ["total_loss", "theft", "vandalism", "fire"]
        if claim_type in high_complexity_types:
            complexity_score += 2
            complexity_factors.append(f"High-complexity claim type: {claim_type}")
        
        # Factor 4: Time since incident
        try:
            incident_date = datetime.fromisoformat(state.get("incident_date", ""))
            claim_date = datetime.fromisoformat(state.get("claim_date", ""))
            days_diff = (claim_date - incident_date).days
            if days_diff > 20:  # Close to 30-day limit
                complexity_score += 1
                complexity_factors.append(f"Late filing: {days_diff} days after incident")
        except:
            pass
        
        # Factor 5: Existing fraud indicators
        fraud_score = state.get("fraud_score", 0)
        if fraud_score > 0.7:
            complexity_score += 3
            complexity_factors.append(f"High fraud risk: {fraud_score:.2f}")
        elif fraud_score > 0.4:
            complexity_score += 2
            complexity_factors.append(f"Moderate fraud risk: {fraud_score:.2f}")
        
        # Factor 6: Image fraud detection (duplicate images)
        image_fraud_check = state.get("image_fraud_check", {})
        if image_fraud_check.get("is_potential_duplicate"):
            complexity_score += 4  # High weight for duplicate images
            similar_claims = image_fraud_check.get("similar_claims", [])
            similarity = image_fraud_check.get("highest_similarity", 0)
            complexity_factors.append(
                f"DUPLICATE IMAGE: {similarity:.2%} match with claims {similar_claims}"
            )
        
        # Determine priority level
        if complexity_score >= 6:
            priority = "critical"
        elif complexity_score >= 4:
            priority = "high"
        elif complexity_score >= 2:
            priority = "medium"
        else:
            priority = "low"
        
        return {
            "complexity_score": complexity_score,
            "complexity_factors": complexity_factors,
            "priority": priority
        }
    
    def determine_next_agent(self, state: Dict[str, Any]) -> SupervisorDecision:
        """
        Determine which agent should process the claim next.
        Uses LLM reasoning combined with rule-based logic.
        """
        current_step = state.get("current_step", "started")
        validation_status = state.get("validation_status")
        approval_status = state.get("approval_status")
        fraud_score = state.get("fraud_score", 0)
        
        # Rule-based routing for clear cases
        if current_step == "started":
            # New claim - check if we need document analysis first
            photos = state.get("damage_photos", [])
            if photos and len(photos) > 0:
                return SupervisorDecision(
                    next_agent="document_analyzer",
                    reasoning="New claim with damage photos - analyzing documents first",
                    priority="medium",
                    parallel_agents=[]
                )
            else:
                return SupervisorDecision(
                    next_agent="validation",
                    reasoning="New claim without photos - proceeding to validation",
                    priority="medium",
                    parallel_agents=[]
                )
        
        if current_step == "document_analysis_complete":
            return SupervisorDecision(
                next_agent="validation",
                reasoning="Document analysis complete - proceeding to validation",
                priority=state.get("supervisor_priority", "medium"),
                parallel_agents=[]
            )
        
        if current_step == "validation_complete":
            if validation_status == "INVALID":
                return SupervisorDecision(
                    next_agent="complete",
                    reasoning=f"Validation failed: {state.get('validation_reason', 'Unknown')}",
                    priority="low",
                    parallel_agents=[]
                )
            
            # Analyze complexity for valid claims
            complexity = self.analyze_claim_complexity(state)
            
            # Check if fraud investigation is needed based on:
            # 1. High complexity (priority high or critical)
            # 2. High claim amount (> $30,000)
            # 3. High-risk claim types
            # 4. Existing fraud score > 0.5
            # 5. Duplicate images detected (image fraud)
            amount = state.get("estimated_damage_amount", 0)
            claim_type = state.get("claim_type", "").lower()
            high_risk_types = ["total_loss", "theft", "vandalism", "fire"]
            
            # Check for image fraud from API
            image_fraud_check = state.get("image_fraud_check", {})
            has_duplicate_images = image_fraud_check.get("is_potential_duplicate", False)
            
            needs_fraud_investigation = (
                complexity["priority"] in ["high", "critical"] or
                fraud_score > 0.5 or
                amount > 30000 or
                claim_type in high_risk_types or
                has_duplicate_images  # Always investigate if duplicate images detected
            )
            
            if needs_fraud_investigation:
                # Build detailed reasoning
                reasons = []
                if complexity["priority"] in ["high", "critical"]:
                    reasons.append(f"Priority: {complexity['priority']}")
                if fraud_score > 0.5:
                    reasons.append(f"Fraud score: {fraud_score:.2f}")
                if amount > 30000:
                    reasons.append(f"High amount: ${amount:,.2f}")
                if claim_type in high_risk_types:
                    reasons.append(f"High-risk type: {claim_type}")
                if has_duplicate_images:
                    similar_claims = image_fraud_check.get("similar_claims", [])
                    similarity = image_fraud_check.get("highest_similarity", 0)
                    reasons.append(f"DUPLICATE IMAGE DETECTED (similarity: {similarity:.2%}, found in claims: {similar_claims})")
                
                return SupervisorDecision(
                    next_agent="fraud_investigation",
                    reasoning=f"Fraud investigation required. {'; '.join(reasons)}. Factors: {', '.join(complexity['complexity_factors']) if complexity['complexity_factors'] else 'Multiple risk indicators'}",
                    priority="critical" if has_duplicate_images else complexity["priority"],
                    parallel_agents=[]
                )
            else:
                return SupervisorDecision(
                    next_agent="approval",
                    reasoning="Validation passed, low complexity - proceeding to approval",
                    priority=complexity["priority"],
                    parallel_agents=[]
                )
        
        if current_step == "fraud_investigation_complete":
            fraud_score = state.get("fraud_score", 0)
            if fraud_score > 0.8:
                return SupervisorDecision(
                    next_agent="human_review",
                    reasoning=f"Very high fraud score ({fraud_score:.2f}) - requires human review",
                    priority="critical",
                    parallel_agents=[]
                )
            else:
                return SupervisorDecision(
                    next_agent="approval",
                    reasoning="Fraud investigation complete - proceeding to approval",
                    priority="high",
                    parallel_agents=[]
                )
        
        if current_step == "approval_complete":
            if approval_status == "NEEDS_REVIEW":
                return SupervisorDecision(
                    next_agent="human_review",
                    reasoning=f"Approval flagged for review: {state.get('approval_reason', 'Unknown')}",
                    priority="high",
                    parallel_agents=[]
                )
            else:
                return SupervisorDecision(
                    next_agent="complete",
                    reasoning=f"Claim processing complete. Status: {approval_status}",
                    priority="low",
                    parallel_agents=[]
                )
        
        if current_step == "human_review_complete":
            return SupervisorDecision(
                next_agent="complete",
                reasoning="Human review complete - workflow finished",
                priority="low",
                parallel_agents=[]
            )
        
        # Default: complete
        return SupervisorDecision(
            next_agent="complete",
            reasoning="No further processing needed",
            priority="low",
            parallel_agents=[]
        )
    
    def supervise(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main supervisor function - analyzes state and determines next action.
        
        Returns updated state with supervisor decision.
        """
        # Analyze complexity
        complexity = self.analyze_claim_complexity(state)
        
        # Determine next agent
        decision = self.determine_next_agent(state)
        
        # Update state with supervisor decision
        state["supervisor_decision"] = decision.next_agent
        state["supervisor_reasoning"] = decision.reasoning
        state["supervisor_priority"] = decision.priority
        state["complexity_analysis"] = complexity
        state["current_step"] = "supervisor_routed"
        
        return state
    
    def get_workflow_summary(self, state: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the workflow execution"""
        summary_parts = [
            f"Claim ID: {state.get('claim_id', 'N/A')}",
            f"Policy ID: {state.get('policy_id', 'N/A')}",
            f"Claim Type: {state.get('claim_type', 'N/A')}",
            f"Amount: ${state.get('estimated_damage_amount', 0):,.2f}",
            "",
            "Processing Steps:",
        ]
        
        # Add validation info
        if state.get("validation_status"):
            summary_parts.append(f"  • Validation: {state['validation_status']}")
            if state.get("validation_reason"):
                summary_parts.append(f"    Reason: {state['validation_reason']}")
        
        # Add fraud info
        if state.get("fraud_score") is not None:
            summary_parts.append(f"  • Fraud Score: {state['fraud_score']:.2f}")
            if state.get("fraud_flags"):
                summary_parts.append(f"    Flags: {', '.join(state['fraud_flags'])}")
        
        # Add approval info
        if state.get("approval_status"):
            summary_parts.append(f"  • Approval: {state['approval_status']}")
            if state.get("approval_reason"):
                summary_parts.append(f"    Reason: {state['approval_reason']}")
            if state.get("payout_amount"):
                summary_parts.append(f"    Payout: ${state['payout_amount']:,.2f}")
        
        # Add complexity analysis
        if state.get("complexity_analysis"):
            ca = state["complexity_analysis"]
            summary_parts.append(f"  • Priority: {ca.get('priority', 'N/A').upper()}")
            if ca.get("complexity_factors"):
                summary_parts.append(f"    Factors: {', '.join(ca['complexity_factors'])}")
        
        return "\n".join(summary_parts)
