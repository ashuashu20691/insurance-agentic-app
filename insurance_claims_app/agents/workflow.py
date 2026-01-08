"""
LangGraph Workflow for Claims Processing
Orchestrates validation and approval agents
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .state import ClaimState
from .validation_agent import ClaimsValidationAgent
from .approval_agent import ClaimsApprovalAgent

# Initialize agents
validation_agent = ClaimsValidationAgent()
approval_agent = ClaimsApprovalAgent()

def validation_node(state: ClaimState) -> ClaimState:
    """Node that runs the validation agent"""
    return validation_agent.validate_claim(state)

def approval_node(state: ClaimState) -> ClaimState:
    """Node that runs the approval agent"""
    return approval_agent.process_approval(state)

def build_claims_workflow() -> StateGraph:
    """Build and return the claims processing workflow graph"""
    
    # Create the graph
    workflow = StateGraph(ClaimState)
    
    # Add nodes
    workflow.add_node("validation_agent", validation_node)
    workflow.add_node("approval_agent", approval_node)
    
    # Set entry point
    workflow.set_entry_point("validation_agent")
    
    # Add edges
    workflow.add_edge("validation_agent", "approval_agent")
    workflow.add_edge("approval_agent", END)
    
    return workflow

def get_compiled_workflow():
    """Get the compiled workflow ready for execution"""
    workflow = build_claims_workflow()
    return workflow.compile()

def process_claim(claim_data: Dict[str, Any]) -> ClaimState:
    """
    Process a claim through the entire workflow
    
    Args:
        claim_data: Dictionary with claim information
        
    Returns:
        Final state with validation and approval results
    """
    # Initialize state from claim data
    initial_state: ClaimState = {
        "claim_id": claim_data.get("claim_id", ""),
        "policy_id": claim_data.get("policy_id", ""),
        "customer_id": claim_data.get("customer_id", ""),
        "incident_date": claim_data.get("incident_date", ""),
        "claim_date": claim_data.get("claim_date", ""),
        "claim_type": claim_data.get("claim_type", ""),
        "damage_description": claim_data.get("damage_description", ""),
        "repair_shop": claim_data.get("repair_shop", ""),
        "estimated_damage_amount": claim_data.get("estimated_damage_amount", 0),
        "damage_photos": claim_data.get("damage_photos", []),
        "incident_report": claim_data.get("incident_report", ""),
        "repair_estimate": claim_data.get("repair_estimate", ""),
        "current_step": "started"
    }
    
    # Get compiled workflow and run
    app = get_compiled_workflow()
    final_state = app.invoke(initial_state)
    
    return final_state
