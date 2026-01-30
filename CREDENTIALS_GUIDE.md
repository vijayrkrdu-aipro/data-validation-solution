# Credentials Management Guide

## Overview

The Data Validation Solution uses **host-specific `.env` files** to manage credentials for multiple database instances across different environments.

## How It Works

### 1. Excel Configuration

In your validation Excel file, you specify a **host identifier** in the "Source Host Name" or "Target Host Name" field:

```
Source Host Name: nz-prod-01
Source Port: 5480
Source Database Name: PRODUCTION
```

### 2. Environment File Lookup

The program looks for a file named `.env.{host_identifier}` in the project root:

```
.env.nz-prod-01
```

### 3. Credential Loading

The `.env.nz-prod-01` file contains the actual connection details:

```env
HOSTNAME=nz-prod-01.company.com
PORT=5480
USERNAME=prod_user
PASSWORD=prod_password
DATABASE=PRODUCTION
```

## File Naming Convention

**Pattern:** `.env.{host-identifier}`

**Examples:**
- Excel has `p8054` → Look for `.env.p8054`
- Excel has `nz-db-ut` → Look for `.env.nz-db-ut`
- Excel has `oracle-prod` → Look for `.env.oracle-prod`
- Excel has `snowflake-analytics` → Look for `.env.snowflake-analytics`

## Environment File Format

### Required Fields (All Databases)

```env
HOSTNAME=full.hostname.com
USERNAME=database_user
PASSWORD=database_password
```

### Optional Fields (Override Excel Values)

```env
PORT=5480
DATABASE=my_database
SCHEMA=my_schema
```

If not provided in `.env` file, values from Excel are used.

## Database-Specific Fields

### SQL Server

```env
# .env.p8054
HOSTNAME=p8054.company.com
USERNAME=sql_user
PASSWORD=sql_password
PORT=3085
DATABASE=BDM Archive

# Optional: Specify ODBC driver
DRIVER={ODBC Driver 17 for SQL Server}
```

**Windows Authentication:**
To use Windows Authentication, provide empty credentials:
```env
HOSTNAME=localhost
USERNAME=
PASSWORD=
```

### Oracle

```env
# .env.oracle-prod
HOSTNAME=oracle-prod.company.com
USERNAME=oracle_user
PASSWORD=oracle_password
PORT=1521

# Required: Either SERVICE_NAME or SID
SERVICE_NAME=ORCL
# OR
# SID=ORCL

# Optional: ODBC driver
DRIVER={Oracle in OraClient12Home1}
```

### Netezza

```env
# .env.nz-db-ut
HOSTNAME=nz-db-ut.company.com
USERNAME=nz_user
PASSWORD=nz_password
PORT=5480
DATABASE=cidpr
SCHEMA=stgprd
```

### Snowflake

```env
# .env.snowflake-prod
HOSTNAME=xy12345.us-east-1.snowflakecomputing.com
USERNAME=snowflake_user
PASSWORD=snowflake_password

# Snowflake-specific (required)
ACCOUNT=xy12345.us-east-1

# Optional
DATABASE=ANALYTICS
SCHEMA=PUBLIC
WAREHOUSE=COMPUTE_WH
ROLE=SYSADMIN
```

## Multiple Environments Example

### Development Environment

**Excel:**
```
Source Host Name: nz-dev
```

**.env.nz-dev:**
```env
HOSTNAME=nz-dev-01.company.com
USERNAME=dev_user
PASSWORD=dev_pass
PORT=5480
DATABASE=DEV_DB
```

### Production Environment

**Excel:**
```
Source Host Name: nz-prod
```

**.env.nz-prod:**
```env
HOSTNAME=nz-prod-01.company.com
USERNAME=prod_user
PASSWORD=prod_pass
PORT=5480
DATABASE=PROD_DB
```

## Multiple Instances of Same Database Type

You can have multiple SQL Server, Oracle, Netezza, or Snowflake instances:

```
.env.sqlserver-finance
.env.sqlserver-sales
.env.sqlserver-hr

.env.oracle-erp
.env.oracle-warehouse
.env.oracle-analytics

.env.nz-dev
.env.nz-test
.env.nz-prod-01
.env.nz-prod-02
```

## Security Best Practices

### 1. Never Commit Credentials

The `.gitignore` file excludes all `.env.*` files (except examples):

```gitignore
.env.*
!.env.example-*
```

### 2. Use Strong Passwords

Generate strong, unique passwords for each environment.

### 3. Restrict File Permissions

On production servers, restrict access to `.env` files:

```bash
chmod 600 .env.*
```

### 4. Rotate Credentials Regularly

Update passwords periodically and update the `.env` files.

### 5. Separate Dev/Prod Credentials

Never use production credentials in development environments.

## Setup Procedure

### Step 1: Identify Your Hosts

List all database hosts you need to connect to:
```
p8054 (SQL Server - Finance)
nz-db-ut (Netezza - Test)
nz-prod-01 (Netezza - Production)
oracle-dwh (Oracle - Data Warehouse)
```

### Step 2: Create .env Files

For each host, create a `.env.{host}` file:

```bash
# Copy from examples
cp .env.example-sqlserver .env.p8054
cp .env.example-netezza .env.nz-db-ut
cp .env.example-oracle .env.oracle-dwh
```

### Step 3: Fill in Credentials

Edit each file with actual credentials:

```bash
# Edit with your preferred editor
nano .env.p8054
nano .env.nz-db-ut
nano .env.oracle-dwh
```

### Step 4: Test Connection

Use a simple validation to test:

```bash
python -m src.main --config test_validation.xlsx
```

## Troubleshooting

### Error: "Credentials file not found"

**Problem:**
```
ConfigurationException: Credentials file not found: .env.nz-prod-01
```

**Solution:**
Create the missing `.env.nz-prod-01` file with credentials.

### Error: "Missing required fields"

**Problem:**
```
Missing required fields in .env.nz-prod: USERNAME, PASSWORD
```

**Solution:**
Ensure your `.env` file has HOSTNAME, USERNAME, and PASSWORD fields.

### Wrong Database/Schema

**Problem:**
Connecting to wrong database or schema.

**Solution:**
Check priority:
1. `.env` file values override Excel values
2. If not in `.env`, Excel values are used
3. Add DATABASE and SCHEMA to `.env` file if needed

### Oracle: SERVICE_NAME vs SID

**Problem:**
Oracle connection fails.

**Solution:**
Ensure you have either SERVICE_NAME or SID in your `.env.oracle-*` file:

```env
# Use one of these
SERVICE_NAME=ORCL
# OR
SID=ORCL
```

### Snowflake: ACCOUNT Required

**Problem:**
Snowflake connection fails.

**Solution:**
Snowflake requires ACCOUNT field:

```env
HOSTNAME=xy12345.us-east-1.snowflakecomputing.com
ACCOUNT=xy12345.us-east-1
```

## Example: Complete Setup

### Excel Configuration

| Field | Value |
|-------|-------|
| Source Host Name | nz-db-ut |
| Source Port | 5480 |
| Source Database Name | cidpr |
| Source Schema Name | stgprd |
| Target Host Name | p8054 |
| Target Port | 3085 |
| Target Database Name | BDM Archive |

### .env.nz-db-ut

```env
HOSTNAME=nz-db-ut.internal.company.com
USERNAME=validation_user
PASSWORD=secure_nz_password
PORT=5480
DATABASE=cidpr
```

### .env.p8054

```env
HOSTNAME=p8054.internal.company.com
USERNAME=sql_validation_user
PASSWORD=secure_sql_password
PORT=3085
DATABASE=BDM Archive
```

### Result

The program will:
1. Read "nz-db-ut" from Excel
2. Load `.env.nz-db-ut`
3. Connect to `nz-db-ut.internal.company.com:5480`
4. Read "p8054" from Excel
5. Load `.env.p8054`
6. Connect to `p8054.internal.company.com:3085`

## Migration from Old Format

If you were using the old `connections.yaml` format:

### Old Format (connections.yaml)
```yaml
connections:
  nz_prod:
    type: netezza
    host: nz-prod.com
    port: 5480
    username: ${NZ_USER}
    password: ${NZ_PASS}
```

### New Format

**Excel:**
```
Source Host Name: nz-prod
```

**.env.nz-prod:**
```env
HOSTNAME=nz-prod.com
USERNAME=nz_user
PASSWORD=nz_password
PORT=5480
```

## Summary

✅ One `.env` file per host identifier
✅ Host identifier in Excel matches `.env` filename
✅ Supports multiple instances of same database type
✅ Supports multiple environments (dev, test, prod)
✅ Credentials never in Excel or code
✅ .env files never committed to Git

For questions or issues, refer to README.md or raise an issue in the repository.
