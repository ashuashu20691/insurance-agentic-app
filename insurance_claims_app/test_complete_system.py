#!/usr/bin/env python3
"""
Complete System Test - Tests all components without requiring full dependencies
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("INSURANCE CLAIMS PROCESSING - COMPLETE SYSTEM TEST")
print("="*70)

# Test 1: Configuration
print("\n[1/6] Testing Configuration...")
try:
    from config import config
    print(f"  ✓ Config loaded")
    print(f"    - Oracle User: {config.ORACLE_USER}")
    print(f"    - Oracle DSN: {config.ORACLE_DSN}")
    print(f"    - OCI Model: {config.OCI_MODEL_ID}")
except Exception as e:
    print(f"  ✗ Config error: {e}")
    sys.exit(1)

# Test 2: Database Connection
print("\n[2/6] Testing Database Connection...")
try:
    import oracledb
    
    connect_params = {
        "user": config.ORACLE_USER,
        "password": config.ORACLE_PASSWORD,
        "dsn": config.ORACLE_DSN,
    }
    
    # Add wallet params if using Autonomous Database
    if config.ORACLE_WALLET_LOCATION:
        connect_params["config_dir"] = config.ORACLE_WALLET_LOCATION
        connect_params["wallet_location"] = config.ORACLE_WALLET_LOCATION
        if config.ORACLE_WALLET_PASSWORD:
            connect_params["wallet_password"] = config.ORACLE_WALLET_PASSWORD
    
    conn = oracledb.connect(**connect_params)
    cursor = conn.cursor()
    cursor.execute("SELECT 'OK' FROM DUAL")
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f"  ✓ Database connection successful")
except Exception as e:
    print(f"  ✗ Database connection failed: {e}")
    print("\n  Check your .env configuration and wallet settings")
    sys.exit(1)

# Test 3: Initialize Database
print("\n[3/6] Initializing Database Tables...")
try:
    from database import init_database, seed_sample_policies
    init_database()
    print(f"  ✓ Tables created")
    seed_sample_policies()
    print(f"  ✓ Sample policies seeded")
except Exception as e:
    print(f"  ✗ Database initialization error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test External APIs
print("\n[4/6] Testing External APIs (Mock)...")
try:
    from external_apis import CarDamageAPI, FraudScoringAPI, PolicyManagementAPI
    
    # Test Car Damage API
    damage_api = CarDamageAPI()
    damage_result = damage_api.analyze_damage(["photo1.jpg", "photo2.jpg"], 5000.0)
    print(f"  ✓ Car Damage API: ${damage_result['total_estimated_repair_cost']:,.2f}")
    
    # Test Fraud API
    fraud_api = FraudScoringAPI()
    fraud_result = fraud_api.score_claim(5000.0, "Test Shop", "CUST-001", 5, "collision")
    print(f"  ✓ Fraud Scoring API: {fraud_result['fraud_score']:.3f} ({fraud_result['risk_level']})")
    
    # Test Policy API
    policy_api = PolicyManagementAPI()
    policy = policy_api.get_policy_details("POL-001")
    print(f"  ✓ Policy Management API: {policy['coverage_type']} - ${policy['coverage_limit']:,.2f}")
    
except Exception as e:
    print(f"  ✗ External API error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test Workflow (without LLM)
print("\n[5/6] Testing Claims Processing Workflow...")
try:
    from datetime import datetime, timedelta
    from database import create_claim, get_claim
    from agents.validation_agent import ClaimsValidationAgent
    from agents.approval_agent import ClaimsApprovalAgent
    from agents.state import ClaimState
    
    # Create test claim
    claim_data = {
        "policy_id": "POL-001",
        "customer_id": "CUST-001",
        "incident_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "claim_date": datetime.now().isoformat(),
        "claim_type": "collision",
        "damage_description": "Front bumper damage from collision",
        "repair_shop": "Certified Auto Body",
        "estimated_damage_amount": 5000.0,
        "damage_photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg"],
        "incident_report": "Rear-ended at traffic light",
        "repair_estimate": "Bumper replacement: $4500, Labor: $500"
    }
    
    claim_id = create_claim(claim_data)
    print(f"  ✓ Claim created: {claim_id}")
    
    # Test validation agent
    validation_agent = ClaimsValidationAgent()
    state: ClaimState = {
        "claim_id": claim_id,
        **claim_data
    }
    state = validation_agent.validate_claim(state)
    print(f"  ✓ Validation: {state['validation_status']}")
    
    # Test approval agent
    approval_agent = ClaimsApprovalAgent()
    state = approval_agent.process_approval(state)
    print(f"  ✓ Approval: {state['approval_status']}")
    print(f"    - Payout: ${state.get('payout_amount', 0):,.2f}")
    print(f"    - Fraud Score: {state.get('fraud_score', 0):.3f}")
    print(f"    - Processing Days: {state.get('processing_days', 0)}")
    
    # Update claim in database
    from database import update_claim
    update_claim(claim_id, {
        "validation_status": state["validation_status"],
        "validation_reason": state["validation_reason"],
        "approval_status": state["approval_status"],
        "approval_reason": state["approval_reason"],
        "payout_amount": state.get("payout_amount", 0),
        "deductible": state.get("deductible", 0),
        "processing_time_days": state.get("processing_days", 0),
        "fraud_score": state.get("fraud_score")
    })
    
    # Verify in database
    saved_claim = get_claim(claim_id)
    print(f"  ✓ Claim saved to database")
    
except Exception as e:
    print(f"  ✗ Workflow error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test Database CRUD
print("\n[6/6] Testing Database CRUD Operations...")
try:
    from database import get_all_claims, get_all_policies
    
    claims = get_all_claims()
    print(f"  ✓ Retrieved {len(claims)} claims")
    
    policies = get_all_policies()
    print(f"  ✓ Retrieved {len(policies)} policies")
    
    for policy in policies:
        print(f"    - {policy['policy_id']}: {policy['coverage_type']} (${policy['coverage_limit']:,.2f})")
    
except Exception as e:
    print(f"  ✗ CRUD error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\nNext Steps:")
print("  1. Install remaining dependencies: ./venv/bin/pip install -r requirements.txt")
print("  2. Start API server: ./venv/bin/python run_api.py")
print("  3. Start UI: ./venv/bin/python run_ui.py")
print("  4. Access UI at: http://localhost:8501")
print("="*70)
