import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OCI GenAI
    OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID", "ocid1.compartment.oc1..aaaaaaaa5jnmxes5yog6ucgnrfttaeckgqewgvfkhaybd32km2lv25fghc4a")
    OCI_SERVICE_ENDPOINT = os.getenv("OCI_SERVICE_ENDPOINT", "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com")
    OCI_MODEL_ID = os.getenv("OCI_MODEL_ID", "cohere.command-a-03-2025")
    
    # External APIs
    ARYA_API_KEY = os.getenv("ARYA_API_KEY", "mock_arya_key")
    FRAUD_API_KEY = os.getenv("FRAUD_API_KEY", "mock_fraud_key")
    POLICY_API_KEY = os.getenv("POLICY_API_KEY", "mock_policy_key")
    
    # Oracle Database Configuration
    ORACLE_USER = os.getenv("ORACLE_USER", "insurance_user")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
    ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")
    ORACLE_WALLET_LOCATION = os.getenv("ORACLE_WALLET_LOCATION", "")
    ORACLE_WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD", "")
    
    # Validation thresholds
    CLAIM_FILING_DAYS_LIMIT = 30
    FRAUD_SCORE_HIGH = 0.7
    FRAUD_SCORE_MEDIUM = 0.4
    FRAUD_SCORE_LOW = 0.2

config = Config()
