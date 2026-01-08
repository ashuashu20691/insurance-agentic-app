#!/usr/bin/env python3
"""
Test Oracle Database Connection - Autonomous Database with Wallet
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config

print("="*60)
print("Testing Oracle Autonomous Database Connection")
print("="*60)

print(f"\nConnection Details:")
print(f"  User: {config.ORACLE_USER}")
print(f"  DSN: {config.ORACLE_DSN}")
print(f"  Password: {'*' * len(config.ORACLE_PASSWORD)}")
print(f"  Wallet: {config.ORACLE_WALLET_LOCATION or 'Not using wallet'}")

try:
    import oracledb
    
    # Use thin mode (no Oracle Client needed)
    oracledb.init_oracle_client()
    
except Exception as e:
    print(f"Note: Oracle Client not available, using thin mode: {e}")

try:
    import oracledb
    print("\n✓ oracledb module imported successfully")
    
    # Test connection using thin mode with wallet
    print("\nAttempting to connect (thin mode with mTLS)...")
    
    # Read the connection string from tnsnames.ora
    tns_path = os.path.join(config.ORACLE_WALLET_LOCATION, "tnsnames.ora")
    
    # For thin mode with Autonomous Database, we need to construct the connection
    # using the wallet's PEM certificates
    
    conn = oracledb.connect(
        user=config.ORACLE_USER,
        password=config.ORACLE_PASSWORD,
        dsn=config.ORACLE_DSN,
        config_dir=config.ORACLE_WALLET_LOCATION,
        wallet_location=config.ORACLE_WALLET_LOCATION,
        wallet_password=config.ORACLE_WALLET_PASSWORD
    )
    
    print("✓ Connection successful!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT 'Hello from Oracle ADB!' as message, SYSDATE as current_time FROM DUAL")
    row = cursor.fetchone()
    
    print(f"\nTest Query Result:")
    print(f"  Message: {row[0]}")
    print(f"  Server Time: {row[1]}")
    
    # Get database info
    cursor.execute("SELECT SYS_CONTEXT('USERENV', 'DB_NAME') FROM DUAL")
    db_name = cursor.fetchone()[0]
    print(f"  Database: {db_name}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Database connection test PASSED!")
    print("="*60)
    
except oracledb.Error as e:
    error, = e.args
    print(f"\n❌ Oracle Error: {error.message}")
    if hasattr(error, 'code'):
        print(f"   Error Code: {error.code}")
    print("\nTroubleshooting:")
    print("  1. Verify ADMIN password for Autonomous Database")
    print("  2. Check wallet password (used when downloading wallet)")
    print("  3. Ensure network can reach Oracle Cloud")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
