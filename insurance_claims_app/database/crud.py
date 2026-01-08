"""
Oracle Database CRUD Operations
"""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import oracledb
from .models import get_connection, release_connection

def _row_to_dict(cursor, row) -> Dict[str, Any]:
    """Convert Oracle row to dictionary, handling LOB and datetime types"""
    if row is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    result = {}
    for col, val in zip(columns, row):
        if val is None:
            result[col] = None
        elif hasattr(val, 'read'):  # LOB object
            result[col] = val.read()
        elif hasattr(val, 'isoformat'):  # datetime
            result[col] = val.isoformat()
        else:
            result[col] = val
    return result

# Claims CRUD
def create_claim(claim_data: Dict[str, Any]) -> str:
    """Create a new claim"""
    conn = get_connection()
    cursor = conn.cursor()
    
    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now()
    
    cursor.execute("""
        INSERT INTO claims (
            claim_id, policy_id, customer_id, incident_date, claim_date,
            claim_type, damage_description, repair_shop, estimated_damage_amount,
            validation_status, approval_status, damage_photos, incident_report,
            repair_estimate, created_at, updated_at
        ) VALUES (
            :1, :2, :3, TO_TIMESTAMP(:4, 'YYYY-MM-DD"T"HH24:MI:SS'), 
            TO_TIMESTAMP(:5, 'YYYY-MM-DD"T"HH24:MI:SS'),
            :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16
        )
    """, [
        claim_id,
        claim_data.get("policy_id"),
        claim_data.get("customer_id", ""),
        claim_data.get("incident_date", "")[:19],
        claim_data.get("claim_date", "")[:19],
        claim_data.get("claim_type"),
        claim_data.get("damage_description"),
        claim_data.get("repair_shop"),
        claim_data.get("estimated_damage_amount"),
        "PENDING",
        "PENDING",
        json.dumps(claim_data.get("damage_photos", [])),
        claim_data.get("incident_report"),
        claim_data.get("repair_estimate"),
        now,
        now
    ])
    
    conn.commit()
    release_connection(conn)
    return claim_id

def get_claim(claim_id: str) -> Optional[Dict[str, Any]]:
    """Get a claim by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM claims WHERE claim_id = :1", [claim_id])
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row)
    
    release_connection(conn)
    return result

def update_claim(claim_id: str, updates: Dict[str, Any]) -> bool:
    """Update a claim"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates["updated_at"] = datetime.now()
    
    # Build SET clause with bind variables
    set_parts = []
    values = []
    for i, (key, value) in enumerate(updates.items(), 1):
        set_parts.append(f"{key} = :{i}")
        values.append(value)
    
    values.append(claim_id)
    set_clause = ", ".join(set_parts)
    
    cursor.execute(
        f"UPDATE claims SET {set_clause} WHERE claim_id = :{len(values)}",
        values
    )
    
    conn.commit()
    affected = cursor.rowcount
    release_connection(conn)
    
    return affected > 0

def get_all_claims() -> List[Dict[str, Any]]:
    """Get all claims"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM claims ORDER BY created_at DESC")
    rows = cursor.fetchall()
    results = [_row_to_dict(cursor, row) for row in rows]
    
    release_connection(conn)
    return results

# Policies CRUD
def get_policy(policy_id: str) -> Optional[Dict[str, Any]]:
    """Get a policy by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM policies WHERE policy_id = :1", [policy_id])
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row)
    
    release_connection(conn)
    return result

def get_all_policies() -> List[Dict[str, Any]]:
    """Get all policies"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM policies")
    rows = cursor.fetchall()
    results = [_row_to_dict(cursor, row) for row in rows]
    
    release_connection(conn)
    return results

# Chat History CRUD
def save_chat_message(claim_id: str, customer_message: str, bot_response: str) -> str:
    """Save a chat message"""
    conn = get_connection()
    cursor = conn.cursor()
    
    chat_id = f"CHAT-{uuid.uuid4().hex[:8].upper()}"
    
    cursor.execute("""
        INSERT INTO chat_history (chat_id, claim_id, customer_message, bot_response, timestamp)
        VALUES (:1, :2, :3, :4, :5)
    """, [chat_id, claim_id, customer_message, bot_response, datetime.now()])
    
    conn.commit()
    release_connection(conn)
    return chat_id

def get_chat_history(claim_id: str) -> List[Dict[str, Any]]:
    """Get chat history for a claim"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM chat_history WHERE claim_id = :1 ORDER BY timestamp ASC
    """, [claim_id])
    
    rows = cursor.fetchall()
    results = [_row_to_dict(cursor, row) for row in rows]
    
    release_connection(conn)
    return results
