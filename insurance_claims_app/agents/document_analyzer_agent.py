"""
Document Analyzer Agent
Analyzes uploaded documents and images for claims processing
"""
from typing import Dict, Any, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from external_apis import CarDamageAPI
from .state import ClaimState


class DocumentAnalyzerAgent:
    """
    Agent that analyzes uploaded documents and damage photos.
    
    Responsibilities:
    1. Analyze damage photos using Car Damage API
    2. Extract information from uploaded documents
    3. Check for image fraud (duplicate images)
    4. Provide document quality assessment
    """
    
    def __init__(self):
        self.damage_api = CarDamageAPI(config.ARYA_API_KEY)
        self.image_vector_store = None  # Lazy load
    
    def _get_image_vector_store(self):
        """Lazy load image vector store"""
        if self.image_vector_store is None:
            try:
                from database.image_vector_store import ImageVectorStore
                self.image_vector_store = ImageVectorStore()
            except Exception as e:
                print(f"Warning: Could not initialize ImageVectorStore: {e}")
        return self.image_vector_store
    
    def analyze_documents(self, state: ClaimState) -> ClaimState:
        """
        Analyze all documents and photos in the claim.
        
        Returns updated state with document analysis results.
        """
        analysis_results = {
            "photos_analyzed": 0,
            "documents_analyzed": 0,
            "quality_score": 0,
            "issues": [],
            "damage_detected": [],
            "duplicate_images": [],
            "estimated_repair_cost": 0
        }
        
        # Analyze damage photos
        photos = state.get("damage_photos", [])
        if photos:
            photo_analysis = self._analyze_photos(photos, state.get("estimated_damage_amount", 0))
            analysis_results["photos_analyzed"] = len(photos)
            analysis_results["damage_detected"] = photo_analysis.get("damaged_parts", [])
            analysis_results["estimated_repair_cost"] = photo_analysis.get("total_estimated_repair_cost", 0)
            analysis_results["photo_confidence"] = photo_analysis.get("confidence_score", 0)
            
            # Store damage assessment in state
            state["damage_assessment"] = photo_analysis
        
        # Check for duplicate/fraudulent images
        duplicate_check = self._check_duplicate_images(photos, state.get("claim_id", ""))
        if duplicate_check.get("duplicates_found"):
            analysis_results["duplicate_images"] = duplicate_check.get("similar_claims", [])
            analysis_results["issues"].append("Potential duplicate images detected")
        
        # Analyze document quality
        quality_assessment = self._assess_document_quality(state)
        analysis_results["quality_score"] = quality_assessment["score"]
        analysis_results["issues"].extend(quality_assessment.get("issues", []))
        
        # Update state
        state["document_analysis"] = analysis_results
        state["current_step"] = "document_analysis_complete"
        
        # Flag if issues found
        if analysis_results["issues"]:
            state["document_issues"] = analysis_results["issues"]
        
        return state
    
    def _analyze_photos(self, photos: List[str], estimated_amount: float) -> Dict[str, Any]:
        """Analyze damage photos using Car Damage API"""
        return self.damage_api.analyze_damage(
            photos=photos,
            estimated_amount=estimated_amount
        )
    
    def _check_duplicate_images(self, photos: List[str], claim_id: str) -> Dict[str, Any]:
        """Check for duplicate images across claims using image vector store"""
        result = {
            "duplicates_found": False,
            "similar_claims": []
        }
        
        image_store = self._get_image_vector_store()
        if not image_store:
            return result
        
        try:
            # Check each photo for duplicates
            for photo in photos:
                # This would use actual image bytes in production
                # For now, we'll use the mock implementation
                image_bytes = photo.encode() if isinstance(photo, str) else photo
                similar = image_store.find_similar_images(
                    image_bytes=image_bytes,
                    exclude_claim_id=claim_id
                )
                
                if similar:
                    result["duplicates_found"] = True
                    for match in similar:
                        if match["claim_id"] not in result["similar_claims"]:
                            result["similar_claims"].append(match["claim_id"])
        except Exception as e:
            # Silently handle - this is optional functionality
            pass
        
        return result
    
    def _assess_document_quality(self, state: ClaimState) -> Dict[str, Any]:
        """Assess the quality and completeness of submitted documents"""
        score = 100
        issues = []
        
        # Check for required documents
        if not state.get("damage_photos") or len(state.get("damage_photos", [])) == 0:
            score -= 30
            issues.append("No damage photos provided")
        elif len(state.get("damage_photos", [])) < 2:
            score -= 10
            issues.append("Insufficient damage photos (recommend at least 2)")
        
        if not state.get("incident_report"):
            score -= 25
            issues.append("No incident report provided")
        
        if not state.get("repair_estimate"):
            score -= 20
            issues.append("No repair estimate provided")
        
        # Check damage description quality
        description = state.get("damage_description", "")
        if len(description) < 20:
            score -= 15
            issues.append("Damage description is too brief")
        
        return {
            "score": max(0, score),
            "issues": issues
        }
