"""
Document Management API (Mock implementation)
Retrieves policy documents for RAG
"""
from typing import Dict, Any, List

class DocumentManagementAPI:
    """Mock Document Management API for RAG"""
    
    # Sample policy documents for RAG
    POLICY_DOCUMENTS = {
        "general_coverage": """
INSURANCE POLICY COVERAGE GUIDE

COMPREHENSIVE COVERAGE:
Comprehensive coverage protects your vehicle against damage from events other than collision. 
This includes theft, vandalism, fire, natural disasters, falling objects, and animal strikes.
Coverage limit applies per incident. Deductible must be paid before coverage kicks in.

COLLISION COVERAGE:
Collision coverage pays for damage to your vehicle resulting from a collision with another 
vehicle or object, regardless of fault. This includes single-vehicle accidents.
Coverage is subject to your policy's deductible and coverage limits.

LIABILITY COVERAGE:
Liability coverage pays for bodily injury and property damage you cause to others in an accident.
This does not cover damage to your own vehicle. Required by law in most states.
Split limits apply: per person / per accident / property damage.
        """,
        
        "claims_process": """
CLAIMS FILING PROCESS

1. REPORT THE INCIDENT: Contact us within 30 days of the incident to file a claim.
2. PROVIDE DOCUMENTATION: Submit damage photos, incident report, and repair estimate.
3. CLAIM REVIEW: Our team will review your claim within 2-5 business days.
4. DAMAGE ASSESSMENT: We may send an adjuster or use photo-based assessment.
5. APPROVAL/DENIAL: You will receive a decision with explanation.
6. PAYMENT: Approved claims are paid within 5-10 business days after approval.

REQUIRED DOCUMENTS:
- Clear photos of all damage (minimum 4 photos from different angles)
- Police report (if applicable)
- Repair estimate from licensed repair shop
- Proof of ownership
        """,
        
        "deductibles": """
UNDERSTANDING YOUR DEDUCTIBLE

Your deductible is the amount you pay out-of-pocket before insurance coverage begins.

DEDUCTIBLE OPTIONS:
- $250 deductible: Lower out-of-pocket, higher premium
- $500 deductible: Standard option, balanced cost
- $1,000 deductible: Higher out-of-pocket, lower premium

HOW IT WORKS:
If your repair costs $5,000 and your deductible is $500:
- You pay: $500
- Insurance pays: $4,500

DEDUCTIBLE WAIVERS:
Some policies include deductible waivers for specific situations like windshield repair.
        """,
        
        "appeal_process": """
APPEAL PROCESS FOR DENIED CLAIMS

If your claim is denied, you have the right to appeal the decision.

STEPS TO APPEAL:
1. Review the denial letter carefully to understand the reason.
2. Gather additional documentation that supports your claim.
3. Submit a written appeal within 60 days of denial.
4. Include: Claim number, policy number, reason for appeal, supporting documents.
5. Appeals are reviewed within 30 days.

APPEAL CONTACT:
Email: appeals@insurance.com
Phone: 1-800-APPEALS
Mail: Claims Appeal Department, PO Box 12345

You may also contact your state's insurance commissioner if you believe the denial was unfair.
        """,
        
        "rental_coverage": """
RENTAL CAR COVERAGE

RENTAL REIMBURSEMENT RIDER:
If you have the rental reimbursement rider on your policy, we will pay for a rental car 
while your vehicle is being repaired due to a covered claim.

COVERAGE LIMITS:
- Daily limit: $30-$50 per day (depending on your policy)
- Maximum days: 30 days per claim
- Total maximum: $900-$1,500 per claim

HOW TO USE:
1. Rent from any major rental company
2. Keep all receipts
3. Submit receipts with your claim for reimbursement

NOTE: Rental coverage only applies if you have this rider on your policy.
Check your declarations page or contact us to verify your coverage.
        """,
        
        "payment_timeline": """
PAYMENT TIMELINE

PROCESSING TIMES:
- Low-risk claims (fraud score < 0.2): 2 business days
- Standard claims (fraud score 0.2-0.5): 5 business days  
- Complex claims (fraud score > 0.5): 10 business days
- Claims requiring investigation: 15-30 business days

PAYMENT METHODS:
- Direct deposit (ACH): Fastest option, 1-2 days after processing
- Check by mail: 5-7 days after processing

TRACKING YOUR PAYMENT:
Log into your account or contact customer service to track payment status.
        """
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def get_policy_documents(self, policy_id: str = None) -> List[Dict[str, Any]]:
        """
        Get policy documents for RAG indexing
        
        Args:
            policy_id: Optional policy ID for specific documents
            
        Returns:
            List of document dicts with id, title, content
        """
        documents = []
        for doc_id, content in self.POLICY_DOCUMENTS.items():
            documents.append({
                "id": doc_id,
                "title": doc_id.replace("_", " ").title(),
                "content": content.strip(),
                "policy_id": policy_id
            })
        return documents
    
    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Simple keyword search in documents"""
        results = []
        query_lower = query.lower()
        
        for doc_id, content in self.POLICY_DOCUMENTS.items():
            if query_lower in content.lower():
                results.append({
                    "id": doc_id,
                    "title": doc_id.replace("_", " ").title(),
                    "content": content.strip(),
                    "relevance": content.lower().count(query_lower)
                })
        
        return sorted(results, key=lambda x: x["relevance"], reverse=True)
