"""
Oracle 23ai Image Vector Store
Uses CLIP model to vectorize damage photos for similarity search and fraud detection
"""
import json
import base64
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models import get_connection, release_connection

class ImageVectorStore:
    """Vector store for damage images using Oracle 23ai and CLIP embeddings"""
    
    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
        self._init_table()
    
    def _load_clip_model(self):
        """Lazy load CLIP model"""
        if self.clip_model is None:
            from transformers import CLIPProcessor, CLIPModel
            print("Loading CLIP model for image vectorization...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            print("CLIP model loaded successfully")
    
    def _init_table(self):
        """Create image vector store table if not exists"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create damage_images table with VECTOR column for CLIP embeddings (512 dimensions)
        cursor.execute("""
            BEGIN
                EXECUTE IMMEDIATE '
                    CREATE TABLE damage_images (
                        image_id VARCHAR2(100) PRIMARY KEY,
                        claim_id VARCHAR2(50),
                        image_name VARCHAR2(500),
                        image_data BLOB,
                        embedding VECTOR(512, FLOAT32),
                        damage_type VARCHAR2(100),
                        metadata CLOB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_damage_claim FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
                    )
                ';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN RAISE; END IF;
            END;
        """)
        
        # Create vector index for fast similarity search
        cursor.execute("""
            BEGIN
                EXECUTE IMMEDIATE '
                    CREATE VECTOR INDEX damage_images_vec_idx 
                    ON damage_images(embedding)
                    ORGANIZATION NEIGHBOR PARTITIONS
                    WITH DISTANCE COSINE
                ';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 AND SQLCODE != -1408 THEN RAISE; END IF;
            END;
        """)
        
        conn.commit()
        release_connection(conn)
    
    def get_image_embedding(self, image_bytes: bytes) -> List[float]:
        """Generate CLIP embedding for an image"""
        self._load_clip_model()
        
        from PIL import Image
        
        # Load image from bytes
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        
        # Process image and get embedding
        inputs = self.clip_processor(images=image, return_tensors="pt")
        image_features = self.clip_model.get_image_features(**inputs)
        
        # Normalize and convert to list
        embedding = image_features.detach().numpy()[0]
        embedding = embedding / (embedding ** 2).sum() ** 0.5  # L2 normalize
        
        return embedding.tolist()

    def add_image(self, claim_id: str, image_name: str, image_bytes: bytes, 
                  damage_type: str = None, metadata: dict = None) -> str:
        """
        Add a damage image with its CLIP embedding to the vector store
        
        Args:
            claim_id: The claim this image belongs to
            image_name: Original filename
            image_bytes: Raw image bytes
            damage_type: Type of damage (collision, comprehensive, etc.)
            metadata: Additional metadata
            
        Returns:
            image_id: Unique identifier for the stored image
        """
        import uuid
        import oracledb
        
        # Generate embedding
        embedding = self.get_image_embedding(image_bytes)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        
        # Generate unique image ID
        image_id = f"IMG-{uuid.uuid4().hex[:8].upper()}"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # For Oracle, BLOB must be the last bind variable to avoid ORA-24816
            # Use a different column order in the INSERT statement
            cursor.execute("""
                INSERT INTO damage_images 
                (image_id, claim_id, image_name, embedding, damage_type, metadata, image_data)
                VALUES (:1, :2, :3, TO_VECTOR(:4, 512, FLOAT32), :5, :6, :7)
            """, [
                image_id,
                claim_id,
                image_name,
                embedding_str,
                damage_type or "unknown",
                json.dumps(metadata or {}),
                image_bytes  # BLOB must be last
            ])
            conn.commit()
            print(f"Stored image {image_name} with ID {image_id} for claim {claim_id}")
        except Exception as e:
            print(f"Error storing image: {e}")
            raise
        finally:
            release_connection(conn)
        
        return image_id
    
    def add_images_batch(self, claim_id: str, images: List[Tuple[str, bytes]], 
                         damage_type: str = None) -> List[str]:
        """
        Add multiple images for a claim
        
        Args:
            claim_id: The claim these images belong to
            images: List of (filename, image_bytes) tuples
            damage_type: Type of damage
            
        Returns:
            List of image_ids
        """
        image_ids = []
        for image_name, image_bytes in images:
            try:
                image_id = self.add_image(claim_id, image_name, image_bytes, damage_type)
                image_ids.append(image_id)
            except Exception as e:
                print(f"Failed to add image {image_name}: {e}")
        return image_ids
    
    def find_similar_images(self, image_bytes: bytes, k: int = 5, 
                           exclude_claim_id: str = None) -> List[Dict[str, Any]]:
        """
        Find similar damage images (useful for fraud detection)
        
        Args:
            image_bytes: Query image bytes
            k: Number of similar images to return
            exclude_claim_id: Exclude images from this claim (to avoid self-matching)
            
        Returns:
            List of similar images with similarity scores
        """
        # Get embedding for query image
        query_embedding = self.get_image_embedding(image_bytes)
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build query with optional exclusion
        if exclude_claim_id:
            cursor.execute("""
                SELECT image_id, claim_id, image_name, damage_type, metadata,
                       VECTOR_DISTANCE(embedding, TO_VECTOR(:1, 512, FLOAT32), COSINE) as distance
                FROM damage_images
                WHERE claim_id != :2
                ORDER BY distance
                FETCH FIRST :3 ROWS ONLY
            """, [embedding_str, exclude_claim_id, k])
        else:
            cursor.execute("""
                SELECT image_id, claim_id, image_name, damage_type, metadata,
                       VECTOR_DISTANCE(embedding, TO_VECTOR(:1, 512, FLOAT32), COSINE) as distance
                FROM damage_images
                ORDER BY distance
                FETCH FIRST :2 ROWS ONLY
            """, [embedding_str, k])
        
        results = []
        for row in cursor.fetchall():
            metadata = row[4]
            if hasattr(metadata, 'read'):
                metadata = metadata.read()
            
            similarity = 1 - row[5]  # Convert distance to similarity
            
            results.append({
                "image_id": row[0],
                "claim_id": row[1],
                "image_name": row[2],
                "damage_type": row[3],
                "metadata": json.loads(metadata) if metadata else {},
                "similarity": round(similarity, 4),
                "is_potential_fraud": similarity > 0.85  # High similarity = potential fraud
            })
        
        release_connection(conn)
        return results
    
    def check_for_duplicate_images(self, image_bytes: bytes, 
                                   similarity_threshold: float = 0.85) -> Dict[str, Any]:
        """
        Check if an image is a potential duplicate (fraud indicator)
        
        Args:
            image_bytes: Image to check
            similarity_threshold: Threshold above which images are considered duplicates
                                 (0.85 = 85% similar, catches near-identical images)
            
        Returns:
            Dict with fraud analysis results
        """
        similar_images = self.find_similar_images(image_bytes, k=3)
        
        # Debug logging
        print(f"[ImageVectorStore] Checking for duplicates, found {len(similar_images)} similar images")
        for img in similar_images:
            print(f"  - Claim {img['claim_id']}: similarity={img['similarity']:.4f}")
        
        duplicates = [img for img in similar_images if img["similarity"] >= similarity_threshold]
        
        print(f"[ImageVectorStore] Duplicates above threshold ({similarity_threshold}): {len(duplicates)}")
        
        return {
            "is_potential_duplicate": len(duplicates) > 0,
            "duplicate_count": len(duplicates),
            "similar_claims": [img["claim_id"] for img in duplicates],
            "highest_similarity": max([img["similarity"] for img in similar_images]) if similar_images else 0,
            "fraud_risk": "HIGH" if len(duplicates) > 0 else "LOW",
            "details": duplicates
        }
    
    def get_claim_images(self, claim_id: str) -> List[Dict[str, Any]]:
        """Get all images for a claim"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT image_id, image_name, damage_type, metadata, created_at
            FROM damage_images
            WHERE claim_id = :1
            ORDER BY created_at
        """, [claim_id])
        
        results = []
        for row in cursor.fetchall():
            metadata = row[3]
            if hasattr(metadata, 'read'):
                metadata = metadata.read()
            
            created_at = row[4]
            if hasattr(created_at, 'isoformat'):
                created_at = created_at.isoformat()
            
            results.append({
                "image_id": row[0],
                "image_name": row[1],
                "damage_type": row[2],
                "metadata": json.loads(metadata) if metadata else {},
                "created_at": created_at
            })
        
        release_connection(conn)
        return results
    
    def get_image_data(self, image_id: str) -> Optional[bytes]:
        """Get raw image bytes by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT image_data FROM damage_images WHERE image_id = :1", [image_id])
        row = cursor.fetchone()
        
        release_connection(conn)
        
        if row and row[0]:
            data = row[0]
            if hasattr(data, 'read'):
                return data.read()
            return data
        return None
    
    def get_image_count(self) -> int:
        """Get total number of images in store"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM damage_images")
        count = cursor.fetchone()[0]
        release_connection(conn)
        return count
