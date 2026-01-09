"""
Test script for the Supervisor-Based Multi-Agent Workflow
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from agents.supervisor_workflow import process_claim_with_supervisor
from agents.supervisor_agent import ClaimsSupervisorAgent

def test_supervisor_workflow():
    """Test the supervisor workflow with a sample claim"""
    
    print("=" * 60)
    print("TESTING SUPERVISOR-BASED MULTI-AGENT WORKFLOW")
    print("=" * 60)
    
    # Create a test claim
    test_claim = {
        "claim_id": "TEST-SUP-001",
        "policy_id": "POL-001",
        "customer_id": "CUST-001",
        "incident_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "collision",
        "damage_description": "Front bumper damage from rear-end collision at traffic light",
        "repair_shop": "Certified Auto Body Shop",
        "estimated_damage_amount": 8500.00,
        "damage_photos": ["photo1.jpg", "photo2.jpg"],
        "incident_report": "Police report #12345 filed at scene",
        "repair_estimate": "Estimate from certified shop: $8,500"
    }
    
    print("\n📋 Test Claim Details:")
    print(f"   Claim ID: {test_claim['claim_id']}")
    print(f"   Policy ID: {test_claim['policy_id']}")
    print(f"   Claim Type: {test_claim['claim_type']}")
    print(f"   Amount: ${test_claim['estimated_damage_amount']:,.2f}")
    print(f"   Photos: {len(test_claim['damage_photos'])}")
    
    print("\n🚀 Processing claim through supervisor workflow...")
    print("-" * 60)
    
    # Process the claim
    result = process_claim_with_supervisor(test_claim)
    
    print("\n✅ WORKFLOW COMPLETE")
    print("=" * 60)
    
    # Print results
    print("\n📊 RESULTS:")
    print(f"   Validation Status: {result.get('validation_status', 'N/A')}")
    print(f"   Validation Reason: {result.get('validation_reason', 'N/A')}")
    print(f"   Approval Status: {result.get('approval_status', 'N/A')}")
    print(f"   Approval Reason: {result.get('approval_reason', 'N/A')}")
    print(f"   Payout Amount: ${result.get('payout_amount', 0):,.2f}")
    print(f"   Fraud Score: {result.get('fraud_score', 'N/A')}")
    print(f"   Processing Days: {result.get('processing_days', 'N/A')}")
    
    print("\n🎯 SUPERVISOR ANALYSIS:")
    print(f"   Priority: {result.get('supervisor_priority', 'N/A')}")
    print(f"   Human Review Required: {result.get('human_review_required', False)}")
    
    if result.get('complexity_analysis'):
        ca = result['complexity_analysis']
        print(f"   Complexity Score: {ca.get('complexity_score', 'N/A')}")
        if ca.get('complexity_factors'):
            print(f"   Complexity Factors: {', '.join(ca['complexity_factors'])}")
    
    print("\n📜 WORKFLOW HISTORY:")
    for i, step in enumerate(result.get('workflow_history', []), 1):
        step_name = step.get('step', 'unknown')
        action = step.get('action', step.get('decision', 'N/A'))
        print(f"   {i}. {step_name}: {action}")
    
    print("\n" + "=" * 60)
    return result


def test_high_risk_claim():
    """Test with a high-risk claim that should trigger fraud investigation"""
    
    print("\n" + "=" * 60)
    print("TESTING HIGH-RISK CLAIM (Should trigger fraud investigation)")
    print("=" * 60)
    
    high_risk_claim = {
        "claim_id": "TEST-SUP-002",
        "policy_id": "POL-001",
        "customer_id": "CUST-002",
        "incident_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "collision",  # Valid claim type
        "damage_description": "Major collision damage - vehicle severely damaged",
        "repair_shop": "Quick Fix Auto",  # Suspicious shop name
        "estimated_damage_amount": 55000.00,  # High amount - triggers fraud investigation
        "damage_photos": ["p1.jpg", "p2.jpg", "p3.jpg", "p4.jpg", "p5.jpg", "p6.jpg"],  # Many photos
        "incident_report": "Police report filed at scene",
        "repair_estimate": "Major repair assessment: $55,000"
    }
    
    print(f"\n📋 High-Risk Claim: ${high_risk_claim['estimated_damage_amount']:,.2f} - {high_risk_claim['claim_type']}")
    
    result = process_claim_with_supervisor(high_risk_claim)
    
    print("\n📊 RESULTS:")
    print(f"   Validation Status: {result.get('validation_status', 'N/A')}")
    print(f"   Validation Reason: {result.get('validation_reason', 'N/A')}")
    print(f"   Priority: {result.get('supervisor_priority', 'N/A')}")
    print(f"   Fraud Score: {result.get('fraud_score', 'N/A')}")
    print(f"   Approval Status: {result.get('approval_status', 'N/A')}")
    print(f"   Human Review Required: {result.get('human_review_required', False)}")
    
    # Check if fraud investigation was triggered
    workflow_steps = [s.get('step') for s in result.get('workflow_history', [])]
    print(f"\n📜 Workflow Steps: {workflow_steps}")
    
    if 'fraud_investigation' in workflow_steps:
        print("   ✅ Fraud Investigation was triggered (as expected)")
    else:
        print("   ⚠️ Fraud Investigation was NOT triggered")
    
    return result


if __name__ == "__main__":
    # Test basic workflow
    result1 = test_supervisor_workflow()
    
    # Test high-risk claim
    result2 = test_high_risk_claim()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
