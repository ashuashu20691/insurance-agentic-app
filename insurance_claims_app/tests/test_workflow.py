#!/usr/bin/env python3
"""
Test script for the complete claims processing workflow
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from database import init_database, seed_sample_policies, create_claim, get_claim
from agents import process_claim

def test_valid_claim():
    """Test a valid claim that should be approved"""
    print("\n" + "="*60)
    print("TEST 1: Valid Claim (Should be APPROVED)")
    print("="*60)
    
    claim_data = {
        "policy_id": "POL-001",
        "customer_id": "CUST-001",
        "incident_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "collision",
        "damage_description": "Front bumper damage from rear-end collision",
        "repair_shop": "Certified Auto Body Shop",
        "estimated_damage_amount": 5000.0,
        "damage_photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg"],
        "incident_report": "Vehicle was rear-ended at traffic light",
        "repair_estimate": "Front bumper replacement: $4500, Labor: $500"
    }
    
    result = process_claim(claim_data)
    
    print(f"\nValidation Status: {result.get('validation_status')}")
    print(f"Validation Reason: {result.get('validation_reason')}")
    print(f"\nApproval Status: {result.get('approval_status')}")
    print(f"Approval Reason: {result.get('approval_reason')}")
    print(f"\nPayout Amount: ${result.get('payout_amount', 0):,.2f}")
    print(f"Deductible: ${result.get('deductible', 0):,.2f}")
    print(f"Processing Days: {result.get('processing_days')}")
    print(f"Fraud Score: {result.get('fraud_score', 'N/A')}")
    
    return result

def test_late_filing():
    """Test a claim filed too late (>30 days)"""
    print("\n" + "="*60)
    print("TEST 2: Late Filing (Should be INVALID/DENIED)")
    print("="*60)
    
    claim_data = {
        "policy_id": "POL-001",
        "customer_id": "CUST-001",
        "incident_date": (datetime.now() - timedelta(days=45)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "collision",
        "damage_description": "Side door damage",
        "repair_shop": "Local Auto Shop",
        "estimated_damage_amount": 3000.0,
        "damage_photos": ["photo1.jpg"],
        "incident_report": "Hit by another vehicle in parking lot",
        "repair_estimate": "Door replacement: $3000"
    }
    
    result = process_claim(claim_data)
    
    print(f"\nValidation Status: {result.get('validation_status')}")
    print(f"Validation Reason: {result.get('validation_reason')}")
    print(f"Approval Status: {result.get('approval_status')}")
    
    return result

def test_inactive_policy():
    """Test a claim with inactive policy"""
    print("\n" + "="*60)
    print("TEST 3: Inactive Policy (Should be INVALID/DENIED)")
    print("="*60)
    
    claim_data = {
        "policy_id": "POL-003",  # This policy is inactive
        "customer_id": "CUST-003",
        "incident_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "liability",
        "damage_description": "Property damage to third party",
        "repair_shop": "N/A",
        "estimated_damage_amount": 10000.0,
        "damage_photos": ["photo1.jpg"],
        "incident_report": "Accident caused damage to fence",
        "repair_estimate": "Fence repair: $10000"
    }
    
    result = process_claim(claim_data)
    
    print(f"\nValidation Status: {result.get('validation_status')}")
    print(f"Validation Reason: {result.get('validation_reason')}")
    print(f"Approval Status: {result.get('approval_status')}")
    
    return result

def test_coverage_mismatch():
    """Test a claim type not covered by policy"""
    print("\n" + "="*60)
    print("TEST 4: Coverage Mismatch (Should be INVALID/DENIED)")
    print("="*60)
    
    claim_data = {
        "policy_id": "POL-002",  # Collision only policy
        "customer_id": "CUST-002",
        "incident_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "comprehensive",  # Not covered by collision policy
        "damage_description": "Hail damage to vehicle",
        "repair_shop": "Auto Body Works",
        "estimated_damage_amount": 4000.0,
        "damage_photos": ["photo1.jpg", "photo2.jpg"],
        "incident_report": "Vehicle damaged during hailstorm",
        "repair_estimate": "Dent repair and paint: $4000"
    }
    
    result = process_claim(claim_data)
    
    print(f"\nValidation Status: {result.get('validation_status')}")
    print(f"Validation Reason: {result.get('validation_reason')}")
    print(f"Approval Status: {result.get('approval_status')}")
    
    return result

def test_missing_documents():
    """Test a claim with missing documents"""
    print("\n" + "="*60)
    print("TEST 5: Missing Documents (Should be INVALID/DENIED)")
    print("="*60)
    
    claim_data = {
        "policy_id": "POL-001",
        "customer_id": "CUST-001",
        "incident_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "collision",
        "damage_description": "Rear bumper damage",
        "repair_shop": "Quick Fix Auto",
        "estimated_damage_amount": 2000.0,
        "damage_photos": [],  # Missing photos
        "incident_report": "",  # Missing report
        "repair_estimate": ""  # Missing estimate
    }
    
    result = process_claim(claim_data)
    
    print(f"\nValidation Status: {result.get('validation_status')}")
    print(f"Validation Reason: {result.get('validation_reason')}")
    print(f"Approval Status: {result.get('approval_status')}")
    
    return result

def test_high_value_claim():
    """Test a high value claim (may trigger fraud flags)"""
    print("\n" + "="*60)
    print("TEST 6: High Value Claim (May need review)")
    print("="*60)
    
    claim_data = {
        "policy_id": "POL-001",
        "customer_id": "CUST-001",
        "incident_date": (datetime.now() - timedelta(days=3)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "comprehensive",
        "damage_description": "Total vehicle damage from flood",
        "repair_shop": "Unknown Auto Shop",
        "estimated_damage_amount": 35000.0,
        "damage_photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg", "photo4.jpg"],
        "incident_report": "Vehicle submerged in flash flood",
        "repair_estimate": "Total loss assessment: $35000"
    }
    
    result = process_claim(claim_data)
    
    print(f"\nValidation Status: {result.get('validation_status')}")
    print(f"Validation Reason: {result.get('validation_reason')}")
    print(f"\nApproval Status: {result.get('approval_status')}")
    print(f"Approval Reason: {result.get('approval_reason')}")
    print(f"\nPayout Amount: ${result.get('payout_amount', 0):,.2f}")
    print(f"Fraud Score: {result.get('fraud_score', 'N/A')}")
    print(f"Fraud Flags: {result.get('fraud_flags', [])}")
    
    return result

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("INSURANCE CLAIMS PROCESSING - WORKFLOW TESTS")
    print("="*60)
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    seed_sample_policies()
    print("Database ready with sample policies.")
    
    # Run tests
    results = []
    results.append(("Valid Claim", test_valid_claim()))
    results.append(("Late Filing", test_late_filing()))
    results.append(("Inactive Policy", test_inactive_policy()))
    results.append(("Coverage Mismatch", test_coverage_mismatch()))
    results.append(("Missing Documents", test_missing_documents()))
    results.append(("High Value Claim", test_high_value_claim()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, result in results:
        validation = result.get("validation_status", "N/A")
        approval = result.get("approval_status", "N/A")
        print(f"{name}: Validation={validation}, Approval={approval}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
