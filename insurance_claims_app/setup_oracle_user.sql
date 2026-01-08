-- Oracle User Setup Script for Insurance Claims App
-- Run this as SYSDBA or ADMIN user

-- Connect as SYSDBA:
-- sqlplus sys/YourSysPassword@140.238.167.101:1521/FREEPDB1 as sysdba

-- Option 1: Reset existing user password
ALTER USER testuser IDENTIFIED BY Password123 ACCOUNT UNLOCK;
ALTER USER testuser QUOTA UNLIMITED ON USERS;

-- Option 2: Create new user (if testuser doesn't exist)
-- CREATE USER insurance_user IDENTIFIED BY Password123;
-- GRANT CONNECT, RESOURCE TO insurance_user;
-- GRANT CREATE SESSION TO insurance_user;
-- GRANT CREATE TABLE TO insurance_user;
-- GRANT CREATE VIEW TO insurance_user;
-- GRANT CREATE SEQUENCE TO insurance_user;
-- GRANT UNLIMITED TABLESPACE TO insurance_user;
-- ALTER USER insurance_user QUOTA UNLIMITED ON USERS;

-- Verify user
SELECT username, account_status, expiry_date, profile 
FROM dba_users 
WHERE username = 'TESTUSER';

-- Set password to never expire (optional, for development)
ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;

EXIT;
