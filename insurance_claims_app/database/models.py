"""
Oracle Database Models and Connection Management
"""
import oracledb
from typing import Optional
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Connection pool
_pool: Optional[oracledb.ConnectionPool] = None

def get_connection_pool() -> oracledb.ConnectionPool:
    """Get or create the Oracle connection pool"""
    global _pool
    
    if _pool is None:
        # Check if using wallet (for Autonomous Database)
        if config.ORACLE_WALLET_LOCATION:
            pool_params = {
                "user": config.ORACLE_USER,
                "password": config.ORACLE_PASSWORD,
                "dsn": config.ORACLE_DSN,
                "min": 2,
                "max": 10,
                "increment": 1,
                "config_dir": config.ORACLE_WALLET_LOCATION,
                "wallet_location": config.ORACLE_WALLET_LOCATION
            }
            if config.ORACLE_WALLET_PASSWORD:
                pool_params["wallet_password"] = config.ORACLE_WALLET_PASSWORD
            _pool = oracledb.create_pool(**pool_params)
        else:
            _pool = oracledb.create_pool(
                user=config.ORACLE_USER,
                password=config.ORACLE_PASSWORD,
                dsn=config.ORACLE_DSN,
                min=2,
                max=10,
                increment=1
            )
    
    return _pool

def get_connection() -> oracledb.Connection:
    """Get a connection from the pool"""
    pool = get_connection_pool()
    return pool.acquire()

def release_connection(conn: oracledb.Connection):
    """Release connection back to pool"""
    pool = get_connection_pool()
    pool.release(conn)

def init_database():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Claims table
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE claims (
                    claim_id VARCHAR2(50) PRIMARY KEY,
                    policy_id VARCHAR2(50) NOT NULL,
                    customer_id VARCHAR2(50) NOT NULL,
                    incident_date TIMESTAMP NOT NULL,
                    claim_date TIMESTAMP NOT NULL,
                    claim_type VARCHAR2(20) NOT NULL CHECK(claim_type IN (''collision'', ''comprehensive'', ''liability'')),
                    damage_description CLOB,
                    repair_shop VARCHAR2(200),
                    estimated_damage_amount NUMBER(12,2),
                    validation_status VARCHAR2(20) CHECK(validation_status IN (''VALID'', ''INVALID'', ''PENDING'')),
                    validation_reason CLOB,
                    validation_results CLOB,
                    fraud_score NUMBER(5,3),
                    fraud_flags CLOB,
                    approval_status VARCHAR2(20) CHECK(approval_status IN (''APPROVED'', ''DENIED'', ''NEEDS_REVIEW'', ''PENDING'')),
                    approval_reason CLOB,
                    payout_amount NUMBER(12,2),
                    deductible NUMBER(12,2),
                    processing_time_days NUMBER(5),
                    damage_photos CLOB,
                    incident_report CLOB,
                    repair_estimate CLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)
    
    # Policies table
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE policies (
                    policy_id VARCHAR2(50) PRIMARY KEY,
                    customer_id VARCHAR2(50) NOT NULL,
                    coverage_type VARCHAR2(50) NOT NULL,
                    coverage_limit NUMBER(12,2) NOT NULL,
                    deductible NUMBER(12,2) NOT NULL,
                    is_active NUMBER(1) DEFAULT 1,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    riders CLOB,
                    policy_document BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)
    
    # Chat history table
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE chat_history (
                    chat_id VARCHAR2(50) PRIMARY KEY,
                    claim_id VARCHAR2(50),
                    customer_message CLOB NOT NULL,
                    bot_response CLOB NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_chat_claim FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
                )
            ';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)
    
    conn.commit()
    release_connection(conn)

def seed_sample_policies():
    """Seed sample policies into database"""
    import json
    
    conn = get_connection()
    cursor = conn.cursor()
    
    sample_policies = [
        {
            "policy_id": "POL-001",
            "customer_id": "CUST-001",
            "coverage_type": "comprehensive",
            "coverage_limit": 50000.0,
            "deductible": 500.0,
            "is_active": 1,
            "start_date": "2025-01-01",
            "end_date": "2027-01-01",
            "riders": json.dumps(["rental_car", "roadside_assistance"]),
            "policy_document": b"Comprehensive Auto Insurance Policy..."
        },
        {
            "policy_id": "POL-002",
            "customer_id": "CUST-002",
            "coverage_type": "collision",
            "coverage_limit": 30000.0,
            "deductible": 1000.0,
            "is_active": 1,
            "start_date": "2025-06-01",
            "end_date": "2027-06-01",
            "riders": json.dumps([]),
            "policy_document": b"Collision Auto Insurance Policy..."
        },
        {
            "policy_id": "POL-003",
            "customer_id": "CUST-003",
            "coverage_type": "liability",
            "coverage_limit": 100000.0,
            "deductible": 250.0,
            "is_active": 0,
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "riders": json.dumps(["rental_car"]),
            "policy_document": b"Liability Auto Insurance Policy..."
        }
    ]
    
    for policy in sample_policies:
        try:
            # Check if policy exists
            cursor.execute("SELECT COUNT(*) FROM policies WHERE policy_id = :1", [policy["policy_id"]])
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO policies 
                    (policy_id, customer_id, coverage_type, coverage_limit, deductible, 
                     is_active, start_date, end_date, riders, policy_document)
                    VALUES (:1, :2, :3, :4, :5, :6, TO_TIMESTAMP(:7, 'YYYY-MM-DD'), 
                            TO_TIMESTAMP(:8, 'YYYY-MM-DD'), :9, :10)
                """, [
                    policy["policy_id"], policy["customer_id"], policy["coverage_type"],
                    policy["coverage_limit"], policy["deductible"], policy["is_active"],
                    policy["start_date"], policy["end_date"], policy["riders"], 
                    policy["policy_document"]
                ])
        except oracledb.IntegrityError:
            pass
    
    conn.commit()
    release_connection(conn)
