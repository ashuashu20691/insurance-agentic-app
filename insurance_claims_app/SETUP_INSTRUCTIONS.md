# Oracle Database Setup Instructions

## Issue: Account Expired

The testuser account has expired. You need to reset the password.

## Solution Options

### Option 1: Reset Password via SQL*Plus (Recommended)

```bash
# Connect as SYSDBA
sqlplus sys/YourSysPassword@140.238.167.101:1521/FREEPDB1 as sysdba

# Run these commands:
ALTER USER testuser IDENTIFIED BY Password123 ACCOUNT UNLOCK;
ALTER USER testuser QUOTA UNLIMITED ON USERS;
ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;
EXIT;
```

### Option 2: Use the SQL Script

```bash
sqlplus sys/YourSysPassword@140.238.167.101:1521/FREEPDB1 as sysdba @setup_oracle_user.sql
```

### Option 3: Create New User

If you want to create a fresh user:

```sql
-- Connect as SYSDBA
sqlplus sys/YourSysPassword@140.238.167.101:1521/FREEPDB1 as sysdba

-- Create user
CREATE USER insurance_user IDENTIFIED BY Password123;
GRANT CONNECT, RESOURCE TO insurance_user;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE TO insurance_user;
GRANT UNLIMITED TABLESPACE TO insurance_user;
ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;
EXIT;
```

Then update `.env`:
```
ORACLE_USER=insurance_user
ORACLE_PASSWORD=Password123
```

## After Password Reset

Once the password is reset, test the connection:

```bash
./venv/bin/python test_db_connection.py
```

## Initialize Database Tables

After successful connection, initialize the database:

```bash
./venv/bin/python -c "from database import init_database, seed_sample_policies; init_database(); seed_sample_policies(); print('Database initialized!')"
```

## Run Tests

```bash
./venv/bin/python tests/test_workflow.py
```

## Start the Application

```bash
# Terminal 1: Start API
./venv/bin/python run_api.py

# Terminal 2: Start UI (after installing all dependencies)
./venv/bin/pip install -r requirements.txt
./venv/bin/python run_ui.py
```
