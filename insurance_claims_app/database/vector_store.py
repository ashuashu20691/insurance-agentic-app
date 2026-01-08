"""
Oracle 23ai Vector Store for RAG
Uses Oracle's native VECTOR data type and similarity search
"""
import json
from typing import List, Dict, Any, Optional
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models import get_connection, release_connection

class OracleVectorStore:
    """Vector store using Oracle 23ai native vector capabilities"""
    
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model
        self._init_table()
    
    def _init_table(self):
        """Create vector store table if not exists"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create policy_documents table with VECTOR column
        cursor.execute("""
            BEGIN
                EXECUTE IMMEDIATE '
                    CREATE TABLE policy_documents (
                        doc_id VARCHAR2(100) PRIMARY KEY,
                        title VARCHAR2(500),
                        content CLOB,
                        embedding VECTOR(384, FLOAT32),
                        metadata CLOB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                    CREATE VECTOR INDEX policy_docs_vec_idx 
                    ON policy_documents(embedding)
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
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents with their embeddings to the vector store"""
        conn = get_connection()
        cursor = conn.cursor()
        
        for doc, embedding in zip(documents, embeddings):
            doc_id = doc.get("id", f"doc_{hash(doc['content'][:50])}")
            
            # Convert embedding to Oracle VECTOR format
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            
            try:
                # Check if document exists
                cursor.execute("SELECT COUNT(*) FROM policy_documents WHERE doc_id = :1", [doc_id])
                exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    cursor.execute("""
                        INSERT INTO policy_documents (doc_id, title, content, embedding, metadata)
                        VALUES (:1, :2, :3, TO_VECTOR(:4, 384, FLOAT32), :5)
                    """, [
                        doc_id,
                        doc.get("title", ""),
                        doc.get("content", ""),
                        embedding_str,
                        json.dumps(doc.get("metadata", {}))
                    ])
            except Exception as e:
                print(f"Error inserting document {doc_id}: {e}")
        
        conn.commit()
        release_connection(conn)
    
    def similarity_search(self, query_embedding: List[float], k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents using Oracle vector similarity"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Convert query embedding to Oracle VECTOR format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Use Oracle's VECTOR_DISTANCE function for similarity search
        cursor.execute("""
            SELECT doc_id, title, content, metadata,
                   VECTOR_DISTANCE(embedding, TO_VECTOR(:1, 384, FLOAT32), COSINE) as distance
            FROM policy_documents
            ORDER BY distance
            FETCH FIRST :2 ROWS ONLY
        """, [embedding_str, k])
        
        results = []
        for row in cursor.fetchall():
            content = row[2]
            if hasattr(content, 'read'):
                content = content.read()
            
            metadata = row[3]
            if hasattr(metadata, 'read'):
                metadata = metadata.read()
            
            results.append({
                "id": row[0],
                "title": row[1],
                "content": content,
                "metadata": json.loads(metadata) if metadata else {},
                "distance": row[4]
            })
        
        release_connection(conn)
        return results
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM policy_documents")
        count = cursor.fetchone()[0]
        release_connection(conn)
        return count
    
    def clear_documents(self):
        """Clear all documents from vector store"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM policy_documents")
        conn.commit()
        release_connection(conn)
