"""
Insurance Chatbot Agent
Answers customer questions using RAG with Oracle 23ai Vector Store
"""
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_core.messages import HumanMessage, SystemMessage
from sentence_transformers import SentenceTransformer

from config import config
from external_apis import DocumentManagementAPI
from database import get_claim, get_policy
from database.vector_store import OracleVectorStore

class InsuranceChatbotAgent:
    """Chatbot agent using Oracle 23ai Vector Store for RAG"""
    
    def __init__(self):
        self.doc_api = DocumentManagementAPI()
        self.llm = self._init_llm()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = OracleVectorStore(self.embedding_model)
        self._init_vector_store()
    
    def _init_llm(self):
        """Initialize OCI GenAI LLM"""
        return ChatOCIGenAI(
            model_id=config.OCI_MODEL_ID,
            service_endpoint=config.OCI_SERVICE_ENDPOINT,
            compartment_id=config.OCI_COMPARTMENT_ID,
            auth_type="API_KEY",
            model_kwargs={"temperature": 0, "max_tokens": 500}
        )
    
    def _init_vector_store(self):
        """Initialize vector store with policy documents"""
        # Check if documents already loaded
        if self.vector_store.get_document_count() > 0:
            print(f"Vector store already has {self.vector_store.get_document_count()} documents")
            return
        
        print("Loading policy documents into Oracle Vector Store...")
        documents = self.doc_api.get_policy_documents()
        
        # Split documents into chunks
        chunks = []
        for doc in documents:
            content = doc["content"]
            # Simple chunking by paragraphs
            paragraphs = content.split("\n\n")
            for i, para in enumerate(paragraphs):
                if para.strip():
                    chunks.append({
                        "id": f"{doc['id']}_{i}",
                        "title": doc["title"],
                        "content": para.strip(),
                        "metadata": {"source": doc["id"], "chunk": i}
                    })
        
        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Store in Oracle Vector Store
        self.vector_store.add_documents(chunks, embeddings)
        print(f"Loaded {len(chunks)} document chunks into Oracle Vector Store")
    
    def answer_question(self, question: str, claim_id: Optional[str] = None) -> Dict[str, Any]:
        """Answer a customer question using RAG with Oracle Vector Store"""
        # Try to extract claim_id from the question if not provided
        if not claim_id:
            import re
            claim_match = re.search(r'CLM-[A-Z0-9]{8}', question.upper())
            if claim_match:
                claim_id = claim_match.group(0)
                print(f"[Chatbot] Extracted claim_id from question: {claim_id}")
        
        # Get claim and policy context if available
        claim_context = ""
        if claim_id:
            claim = get_claim(claim_id)
            if claim:
                claim_context = self._build_claim_context(claim)
        
        # Check for specific question types with direct data lookups
        question_lower = question.lower()
        
        if claim_id:
            if "deductible" in question_lower:
                return self._answer_deductible(claim_id)
            elif any(word in question_lower for word in ["payout", "payment amount", "breakdown", "how much", "calculate", "approved amount"]):
                return self._answer_payout(claim_id)
            elif "when" in question_lower and ("paid" in question_lower or "payment" in question_lower or "process" in question_lower):
                return self._answer_processing_time(claim_id)
            elif "status" in question_lower:
                return self._answer_status(claim_id)
            elif any(word in question_lower for word in ["risk", "risky", "fraud", "why flagged", "why high", "suspicious", "duplicate"]):
                return self._answer_fraud_risk(claim_id)
        
        # RAG search using Oracle Vector Store
        query_embedding = self.embedding_model.encode(question).tolist()
        relevant_docs = self.vector_store.similarity_search(query_embedding, k=3)
        rag_context = "\n\n".join([doc["content"] for doc in relevant_docs])
        
        # Build prompt
        system_prompt = """You are a helpful insurance customer service assistant. 
Answer questions based on the provided policy information and claim data.
Be concise, accurate, and helpful. If you don't have enough information to answer, say so.
Always be empathetic and professional."""
        
        user_prompt = f"""Context from policy documents:
{rag_context}

{claim_context}

Customer Question: {question}

Please provide a helpful answer based on the above information."""
        
        # Get LLM response
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.llm.invoke(messages)
            answer = response.content
        except Exception as e:
            # Fallback to simple response if LLM fails
            print(f"LLM error: {e}")
            answer = self._fallback_answer(question, rag_context, claim_context)
        
        return {
            "answer": answer,
            "sources": [doc["title"] for doc in relevant_docs],
            "claim_id": claim_id
        }
    
    def _build_claim_context(self, claim: Dict) -> str:
        """Build context string from claim data"""
        return f"""
Current Claim Information:
- Claim ID: {claim.get('claim_id')}
- Status: {claim.get('approval_status', 'PENDING')}
- Validation: {claim.get('validation_status', 'PENDING')}
- Claim Type: {claim.get('claim_type')}
- Estimated Damage: ${claim.get('estimated_damage_amount', 0):,.2f}
- Payout Amount: ${claim.get('payout_amount', 0):,.2f}
- Deductible: ${claim.get('deductible', 0):,.2f}
- Processing Days: {claim.get('processing_time_days', 'TBD')}
- Fraud Score: {claim.get('fraud_score', 'N/A')}
"""
    
    def _answer_deductible(self, claim_id: str) -> Dict[str, Any]:
        """Answer deductible question"""
        claim = get_claim(claim_id)
        if claim and claim.get("deductible"):
            deductible = claim['deductible']
            if isinstance(deductible, (int, float)):
                return {
                    "answer": f"Your deductible for this claim is ${deductible:,.2f}. This is the amount you'll pay out-of-pocket before your insurance coverage kicks in.",
                    "sources": ["Claim Data"],
                    "claim_id": claim_id
                }
        return {
            "answer": "I couldn't find deductible information for this claim. Please contact customer service for details.",
            "sources": [],
            "claim_id": claim_id
        }
    
    def _answer_payout(self, claim_id: str) -> Dict[str, Any]:
        """Answer payout amount question with detailed breakdown"""
        claim = get_claim(claim_id)
        if claim:
            status = claim.get("approval_status", "PENDING")
            if status == "APPROVED" or status == "NEEDS_REVIEW":
                payout = claim.get('payout_amount', 0)
                deductible = claim.get('deductible', 0)
                estimated_damage = claim.get('estimated_damage_amount', 0)
                
                # Get policy details for coverage limit
                policy_id = claim.get('policy_id')
                policy = get_policy(policy_id) if policy_id else None
                coverage_limit = policy.get('coverage_limit', 50000) if policy else 50000
                
                # Calculate the breakdown
                damage_after_deductible = max(0, estimated_damage - deductible)
                capped_at_limit = min(damage_after_deductible, coverage_limit)
                
                breakdown = f"""Here's the detailed payout breakdown for claim {claim_id}:

📊 **Payout Calculation:**
┌─────────────────────────────────────────┐
│ Estimated Damage Amount:    ${estimated_damage:>10,.2f} │
│ Less: Deductible:          -${deductible:>10,.2f} │
├─────────────────────────────────────────┤
│ Subtotal:                   ${damage_after_deductible:>10,.2f} │
│ Coverage Limit:             ${coverage_limit:>10,.2f} │
├─────────────────────────────────────────┤
│ **Final Payout Amount:**    ${payout:>10,.2f} │
└─────────────────────────────────────────┘

💡 **How it's calculated:**
1. We start with the estimated damage: ${estimated_damage:,.2f}
2. Subtract your deductible: ${deductible:,.2f}
3. The result (${damage_after_deductible:,.2f}) is checked against your coverage limit (${coverage_limit:,.2f})
4. Your approved payout is: **${payout:,.2f}**

✅ Status: {status}"""
                
                return {
                    "answer": breakdown,
                    "sources": ["Claim Data", "Policy Coverage"],
                    "claim_id": claim_id
                }
            elif status == "DENIED":
                reason = claim.get('approval_reason', 'Not specified')
                return {
                    "answer": f"Unfortunately, your claim was denied. Reason: {reason}. You may appeal this decision within 60 days.",
                    "sources": ["Claim Data"],
                    "claim_id": claim_id
                }
            else:
                return {
                    "answer": f"Your claim is currently {status}. The payout amount will be determined once the claim is fully processed.",
                    "sources": ["Claim Data"],
                    "claim_id": claim_id
                }
        return {
            "answer": "I couldn't find this claim. Please verify your claim ID.",
            "sources": [],
            "claim_id": claim_id
        }
    
    def _answer_processing_time(self, claim_id: str) -> Dict[str, Any]:
        """Answer processing time question"""
        claim = get_claim(claim_id)
        if claim and claim.get("processing_time_days"):
            days = claim["processing_time_days"]
            return {
                "answer": f"Your claim is estimated to be processed within {days} business days. Once approved, payment will be issued via direct deposit within 1-2 additional business days.",
                "sources": ["Claim Data", "Payment Timeline"],
                "claim_id": claim_id
            }
        return {
            "answer": "Processing time hasn't been determined yet. Standard claims typically take 2-10 business days depending on complexity.",
            "sources": ["Payment Timeline"],
            "claim_id": claim_id
        }
    
    def _answer_status(self, claim_id: str) -> Dict[str, Any]:
        """Answer claim status question"""
        claim = get_claim(claim_id)
        if claim:
            validation = claim.get('validation_status', 'PENDING')
            approval = claim.get('approval_status', 'PENDING')
            reason = claim.get('approval_reason') or claim.get('validation_reason') or 'Processing'
            return {
                "answer": f"Your claim {claim_id} status:\n- Validation: {validation}\n- Approval: {approval}\n- Reason: {reason}",
                "sources": ["Claim Data"],
                "claim_id": claim_id
            }
        return {
            "answer": "I couldn't find this claim. Please verify your claim ID.",
            "sources": [],
            "claim_id": claim_id
        }
    
    def _answer_fraud_risk(self, claim_id: str) -> Dict[str, Any]:
        """Answer fraud risk question with detailed explanation"""
        claim = get_claim(claim_id)
        if not claim:
            return {
                "answer": "I couldn't find this claim. Please verify your claim ID.",
                "sources": [],
                "claim_id": claim_id
            }
        
        fraud_score = claim.get('fraud_score', 0)
        fraud_flags = claim.get('fraud_flags', [])
        approval_reason = claim.get('approval_reason', '')
        estimated_amount = claim.get('estimated_damage_amount', 0)
        claim_type = claim.get('claim_type', 'unknown')
        
        # Parse fraud flags if it's a string
        if isinstance(fraud_flags, str):
            try:
                import json
                fraud_flags = json.loads(fraud_flags)
            except:
                fraud_flags = []
        
        # Determine risk level
        if fraud_score >= 0.8:
            risk_level = "🔴 HIGH RISK"
            risk_emoji = "🚨"
        elif fraud_score >= 0.5:
            risk_level = "🟡 MODERATE RISK"
            risk_emoji = "⚠️"
        else:
            risk_level = "🟢 LOW RISK"
            risk_emoji = "✅"
        
        # Build detailed explanation
        explanation = f"""**Fraud Risk Analysis for Claim {claim_id}**

{risk_emoji} **Risk Level:** {risk_level}
📊 **Fraud Score:** {fraud_score:.2f} (scale: 0.0 - 1.0)

"""
        
        # Add risk factors
        risk_factors = []
        
        # Check for duplicate image flag
        if fraud_flags:
            if "DUPLICATE_IMAGE_DETECTED" in fraud_flags or "DUPLICATE_IMAGE_FRAUD" in fraud_flags:
                risk_factors.append("🖼️ **DUPLICATE IMAGE DETECTED** - The same or very similar image was found in another claim. This is a major fraud indicator.")
            for flag in fraud_flags:
                if flag not in ["DUPLICATE_IMAGE_DETECTED", "DUPLICATE_IMAGE_FRAUD"]:
                    risk_factors.append(f"⚠️ {flag}")
        
        # Check claim amount
        if estimated_amount > 30000:
            risk_factors.append(f"💰 **High Claim Amount** - ${estimated_amount:,.2f} exceeds typical claim values")
        
        # Check approval reason for fraud indicators
        if "fraud" in approval_reason.lower():
            risk_factors.append(f"📋 **Approval Note:** {approval_reason}")
        
        # Add risk factors to explanation
        if risk_factors:
            explanation += "**🔍 Risk Factors Detected:**\n"
            for factor in risk_factors:
                explanation += f"• {factor}\n"
            explanation += "\n"
        else:
            if fraud_score >= 0.5:
                explanation += "**🔍 Risk Factors:**\n"
                explanation += "• Multiple automated checks flagged potential concerns\n"
                explanation += "• Claim patterns matched known fraud indicators\n\n"
            else:
                explanation += "**✅ No significant risk factors detected.**\n\n"
        
        # Add recommendation
        if fraud_score >= 0.8:
            explanation += """**📌 What This Means:**
This claim has been flagged for manual review due to high fraud risk indicators. 
A claims specialist will review the details before final approval.

If you believe this is an error, please contact our fraud investigation team with any additional documentation."""
        elif fraud_score >= 0.5:
            explanation += """**📌 What This Means:**
This claim has moderate risk indicators and may require additional verification.
Processing may take longer than usual while we verify the claim details."""
        else:
            explanation += """**📌 What This Means:**
This claim passed our automated fraud checks with no significant concerns.
Standard processing times apply."""
        
        return {
            "answer": explanation,
            "sources": ["Fraud Analysis", "Claim Data"],
            "claim_id": claim_id
        }
    
    def _fallback_answer(self, question: str, rag_context: str, claim_context: str) -> str:
        """Provide fallback answer when LLM is unavailable"""
        question_lower = question.lower()
        
        if "cover" in question_lower:
            return "Your policy coverage depends on your specific plan. Comprehensive coverage includes collision, theft, and natural disasters. Please check your policy documents or contact us for specific coverage details."
        elif "appeal" in question_lower:
            return "You can appeal a denied claim within 60 days. Submit a written appeal with your claim number, policy number, and any supporting documentation to our appeals department."
        elif "rental" in question_lower:
            return "Rental car coverage is available if you have the rental reimbursement rider on your policy. Coverage typically includes $30-50 per day for up to 30 days."
        else:
            return "I'd be happy to help with your question. For specific policy details, please contact our customer service team or check your policy documents."
