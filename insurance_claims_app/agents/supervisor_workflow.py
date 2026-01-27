"""
Supervisor-Based Multi-Agent Workflow for Claims Processing
Uses LangGraph with a central Supervisor Agent orchestrating specialized agents
"""
from typing import Dict, Any, Literal, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .state import SupervisorClaimState
from .supervisor_agent import ClaimsSupervisorAgent
from .document_analyzer_agent import DocumentAnalyzerAgent
from .validation_agent import ClaimsValidationAgent
from .fraud_investigation_agent import FraudInvestigationAgent
from .approval_agent import ClaimsApprovalAgent


# Initialize all agents
supervisor = ClaimsSupervisorAgent()
document_analyzer = DocumentAnalyzerAgent()
validation_agent = ClaimsValidationAgent()
fraud_agent = FraudInvestigationAgent()
approval_agent = ClaimsApprovalAgent()


def supervisor_node(state: SupervisorClaimState) -> SupervisorClaimState:
    """
    Supervisor node - analyzes state and determines next agent.
    This is the central coordinator of the workflow.
    """
    # Track workflow history
    workflow_history = state.get("workflow_history", [])
    workflow_history.append({
        "step": "supervisor",
        "current_step": state.get("current_step", "started"),
        "action": "analyzing"
    })
    state["workflow_history"] = workflow_history
    
    # Run supervisor analysis
    state = supervisor.supervise(state)
    
    # Update history with decision
    workflow_history.append({
        "step": "supervisor",
        "decision": state.get("supervisor_decision"),
        "reasoning": state.get("supervisor_reasoning")
    })
    state["workflow_history"] = workflow_history
    
    return state


def document_analyzer_node(state: SupervisorClaimState) -> SupervisorClaimState:
    """Document analysis node"""
    workflow_history = state.get("workflow_history", [])
    workflow_history.append({"step": "document_analyzer", "action": "analyzing documents"})
    state["workflow_history"] = workflow_history
    
    return document_analyzer.analyze_documents(state)


def validation_node(state: SupervisorClaimState) -> SupervisorClaimState:
    """Validation node"""
    workflow_history = state.get("workflow_history", [])
    workflow_history.append({"step": "validation", "action": "validating claim"})
    state["workflow_history"] = workflow_history
    
    return validation_agent.validate_claim(state)


def fraud_investigation_node(state: SupervisorClaimState) -> SupervisorClaimState:
    """Fraud investigation node"""
    workflow_history = state.get("workflow_history", [])
    workflow_history.append({"step": "fraud_investigation", "action": "investigating fraud"})
    state["workflow_history"] = workflow_history
    
    return fraud_agent.investigate(state)


def approval_node(state: SupervisorClaimState) -> SupervisorClaimState:
    """Approval node"""
    workflow_history = state.get("workflow_history", [])
    workflow_history.append({"step": "approval", "action": "processing approval"})
    state["workflow_history"] = workflow_history
    
    return approval_agent.process_approval(state)


def human_review_node(state: SupervisorClaimState) -> SupervisorClaimState:
    """
    Human review node - marks claim for human review.
    In production, this would integrate with a ticketing system.
    """
    workflow_history = state.get("workflow_history", [])
    workflow_history.append({"step": "human_review", "action": "escalated to human"})
    state["workflow_history"] = workflow_history
    
    state["human_review_required"] = True
    state["human_review_reason"] = state.get("supervisor_reasoning", "Requires manual review")
    state["current_step"] = "human_review_complete"
    
    # For demo purposes, we'll auto-approve with monitoring
    # In production, this would pause and wait for human input
    if state.get("approval_status") is None:
        state["approval_status"] = "NEEDS_REVIEW"
        state["approval_reason"] = f"Escalated for human review: {state.get('supervisor_reasoning', 'High complexity')}"
    
    return state


def route_from_supervisor(state: SupervisorClaimState) -> Literal["document_analyzer", "validation", "fraud_investigation", "approval", "human_review", "complete"]:
    """
    Routing function - determines next node based on supervisor decision.
    """
    decision = state.get("supervisor_decision", "complete")
    
    # Map decision to node names
    valid_routes = ["document_analyzer", "validation", "fraud_investigation", "approval", "human_review", "complete"]
    
    if decision in valid_routes:
        return decision
    
    return "complete"


def build_supervisor_workflow() -> StateGraph:
    """
    Build the supervisor-based multi-agent workflow.
    
    Architecture:
    
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
    """
    
    # Create the graph with supervisor state
    workflow = StateGraph(SupervisorClaimState)
    
    # Add all nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("document_analyzer", document_analyzer_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("fraud_investigation", fraud_investigation_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("human_review", human_review_node)
    
    # Set entry point - always start with supervisor
    workflow.set_entry_point("supervisor")
    
    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "document_analyzer": "document_analyzer",
            "validation": "validation",
            "fraud_investigation": "fraud_investigation",
            "approval": "approval",
            "human_review": "human_review",
            "complete": END
        }
    )
    
    # All agent nodes route back to supervisor for next decision
    workflow.add_edge("document_analyzer", "supervisor")
    workflow.add_edge("validation", "supervisor")
    workflow.add_edge("fraud_investigation", "supervisor")
    workflow.add_edge("approval", "supervisor")
    workflow.add_edge("human_review", "supervisor")
    
    return workflow


def get_compiled_supervisor_workflow(with_memory: bool = False):
    """
    Get the compiled supervisor workflow ready for execution.
    
    Args:
        with_memory: If True, adds checkpointing for state persistence
    """
    workflow = build_supervisor_workflow()
    
    if with_memory:
        checkpointer = MemorySaver()
        return workflow.compile(checkpointer=checkpointer)
    
    return workflow.compile()


def process_claim_with_supervisor(claim_data: Dict[str, Any], with_memory: bool = False) -> SupervisorClaimState:
    """
    Process a claim through the supervisor-based workflow.
    
    Args:
        claim_data: Dictionary with claim information
        with_memory: If True, enables state persistence
        
    Returns:
        Final state with all processing results
    """
    # Initialize state from claim data
    initial_state: SupervisorClaimState = {
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
        "current_step": "started",
        "workflow_history": [],
        # Include image fraud check from API if available
        "image_fraud_check": claim_data.get("image_fraud_check", {})
    }
    
    # Get compiled workflow and run
    app = get_compiled_supervisor_workflow(with_memory=with_memory)
    
    if with_memory:
        # Run with thread_id for state persistence
        config = {"configurable": {"thread_id": claim_data.get("claim_id", "default")}}
        final_state = app.invoke(initial_state, config)
    else:
        final_state = app.invoke(initial_state)
    
    return final_state


# Backward compatibility - keep the old function name working
def process_claim(claim_data: Dict[str, Any]) -> SupervisorClaimState:
    """
    Process a claim through the workflow (backward compatible).
    Uses the new supervisor-based workflow.
    """
    return process_claim_with_supervisor(claim_data)
