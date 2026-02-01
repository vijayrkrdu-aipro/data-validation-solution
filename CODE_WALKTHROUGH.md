# Code Walkthrough

A simplified guide to understanding the Data Validation Solution codebase.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Core Components](#core-components)
3. [File-by-File Breakdown](#file-by-file-breakdown)
4. [Configuration Files](#configuration-files)
5. [How It All Works Together](#how-it-all-works-together)

---

## Project Overview

This solution validates data between databases by:
1. Reading validation rules from an Excel file (vertical layout)
2. Loading credentials from host-specific `.env` files
3. Connecting to source and target databases
4. Running aggregate SQL queries (COUNT, SUM, etc.)
5. Comparing results and reporting pass/fail

**Architecture Pattern:** Connector Pattern + Factory Pattern
- Each database type has its own connector
- Validator creates the right connector based on database type
- All connectors share the same interface (BaseConnector)

---

## Core Components

```
Main Flow:
main.py → ConfigParser → EnvManager → Validator → QueryBuilder → Connectors → Results
           (reads Excel)   (loads creds) (orchestrates) (builds SQL)   (executes)   (CSV)
```

---

## File-by-File Breakdown

### 1. src/main.py
**Purpose:** Entry point for the CLI application

#### Key Functions:

**`parse_arguments()`**
- Reads command-line arguments
- Parameters:
  - `--config`: Path to Excel file with validations (required)
  - `--output`: Where to save CSV results (optional, auto-generated if not provided)
  - `--sheet`: Excel sheet name (default: "Validations")
  - `--verbose`: Enable detailed logging

**`generate_output_path(custom_path)`**
- Creates output filename with timestamp
- Example: `validation_report_20240115_143022.csv`

**`save_results_to_csv(results, output_path)`**
- Converts validation results to DataFrame
- Saves as CSV file

**`print_summary(results)`**
- Prints summary table to console
- Shows: Total, Passed, Failed, Errors
- Lists failed validations and errors

**`main()`**
- Orchestrates everything:
  1. Parse command-line arguments
  2. Load and parse validations from Excel
  3. Initialize Validator
  4. Run each validation
  5. Save results to CSV
  6. Print summary
  7. Exit with appropriate code (0 = success, 1 = failures/errors)

---

### 2. src/config_parser.py
**Purpose:** Reads and parses the Excel validation configuration file (vertical layout)

#### Classes:

**`ValidationConfig` (dataclass)**
- Stores a single validation rule
- Fields:
  - `validation_id`: Unique ID (e.g., "VAL001")
  - `validation_name`: Descriptive name
  - **Source details:**
    - `source_type`: Database type (SQLServer, Oracle, Netezza, Snowflake, CSV)
    - `source_host`: Host identifier (used to lookup .env file)
    - `source_port`: Port number
    - `source_database/schema/table/column`: Where to query
    - `source_column_expression`: Custom SQL expression for source column
    - `source_filter`: WHERE clause for source
  - **Target details:** (same structure as source)
  - **Validation rules:**
    - `rule_type`: What aggregate to use (COUNT_STAR, SUM, AVG, etc.)
    - `threshold_type`: EXACT, PERCENTAGE, or ABSOLUTE
    - `threshold_value`: The tolerance (0 for exact, 0.01 for 1%, etc.)
    - `enabled`: TRUE/FALSE to enable/disable (default: TRUE)

**`ConfigParser`**
- Reads Excel file with vertical layout and converts to ValidationConfig objects
- Vertical layout: First column = field names, subsequent columns = validations

#### Key Methods:

**`__init__(excel_path, sheet_name='Validations')`**
- Parameters:
  - `excel_path`: Path to Excel file
  - `sheet_name`: Which sheet has validations (default: "Validations")

**`parse()`**
- Main method that does all the work
- Returns: List of ValidationConfig objects
- Steps:
  1. Reads Excel file with pandas (no header)
  2. Creates mapping of field names to row indices
  3. Parses each column (each column = one validation)
  4. Returns list of ValidationConfig objects

**`_parse_column(df, col_idx, field_map)`**
- Converts one Excel column to ValidationConfig object
- Handles missing values gracefully
- Validates threshold_type is valid
- Helper function `get_value()` extracts values from specific fields

---

### 3. src/env_manager.py
**Purpose:** Manages host-specific credentials from `.env` files

#### Class: `EnvManager`

**`__init__(env_dir=None)`**
- Initializes environment manager
- Parameters:
  - `env_dir`: Directory containing .env files (default: project root)
- Creates credentials cache for performance

**`get_credentials(hostname)`**
- Loads credentials for a specific hostname
- Looks for `.env.{hostname}` file
- Returns: Dictionary with credentials (HOSTNAME, USERNAME, PASSWORD, etc.)
- Validates required fields are present
- Caches results for performance
- Raises ConfigurationException if file not found or invalid

**`clear_cache()`**
- Clears the credentials cache

---

### 4. src/query_builder.py
**Purpose:** Builds SQL queries for different aggregate functions

#### Class: `QueryBuilder`

**`build_query(...)`** (static method)
- Builds SQL query based on rule type
- Parameters:
  - `dialect`: Database dialect (sqlserver, oracle, netezza, snowflake)
  - `database/schema/table`: Target location
  - `column`: Column name (if applicable)
  - `rule_type`: Type of aggregate (COUNT_STAR, SUM, AVG, etc.)
  - `custom_expression`: Custom SQL expression (for CUSTOM rule type)
  - `filter_clause`: WHERE condition
- Returns: Complete SQL query string

**Supported Rule Types:**
- `COUNT_STAR`: `SELECT COUNT(*) FROM table WHERE filter`
- `COUNT_COLUMN`: `SELECT COUNT(column) FROM table WHERE filter`
- `SUM`: `SELECT SUM(column) FROM table WHERE filter`
- `AVG`: `SELECT AVG(column) FROM table WHERE filter`
- `MIN`: `SELECT MIN(column) FROM table WHERE filter`
- `MAX`: `SELECT MAX(column) FROM table WHERE filter`
- `COUNT_DISTINCT`: `SELECT COUNT(DISTINCT column) FROM table WHERE filter`
- `COUNT_NULL`: `SELECT SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) FROM table WHERE filter`
- `COUNT_NOT_NULL`: `SELECT COUNT(column) FROM table WHERE filter`
- `CUSTOM`: Uses custom_expression directly

**Helper methods:**
- `_build_table_name()`: Constructs fully qualified table name
- `_validate_identifiers()`: Prevents SQL injection

---

### 5. src/validator.py
**Purpose:** Core validation engine that runs validations

#### Classes:

**`ValidationResult` (dataclass)**
- Stores results of a single validation
- Fields:
  - `validation_id`, `validation_name`
  - `status`: PASS, FAIL, or ERROR
  - `source_value`, `target_value`: Actual values returned
  - `difference`: target_value - source_value
  - `percentage_diff`: Percentage difference
  - `source_details`, `target_details`: Connection and table info
  - `rule_type`, `threshold_type`, `threshold_value`
  - `execution_timestamp`
  - `error_message`: Error details (if status is ERROR)
  - `source_query`, `target_query`: SQL queries executed

**`Validator`**
- Executes validations and compares results

#### Key Methods:

**`__init__(env_dir=None)`**
- Initializes validator with EnvManager
- Parameters:
  - `env_dir`: Directory containing .env files

**`_create_connector(db_type, host_identifier, port, database, schema=None)`**
- Creates a connector instance for a specific database
- Loads credentials from `.env.{host_identifier}` file
- Returns: Appropriate connector instance (SQLServerConnector, OracleConnector, etc.)
- Priority: .env file values override Excel values

**`validate(config)`**
- Executes a single validation
- Parameters:
  - `config`: ValidationConfig object
- Returns: ValidationResult object
- Steps:
  1. Create source and target connectors
  2. Build SQL queries using QueryBuilder
  3. Execute queries
  4. Compare results based on threshold
  5. Return ValidationResult

**`_check_threshold(source_value, target_value, threshold_type, threshold_value)`** (static)
- Determines if values pass the threshold criteria
- Returns: 'PASS' or 'FAIL'
- Logic:
  - `EXACT`: abs(target - source) <= threshold_value
  - `PERCENTAGE`: abs((target - source) / source) <= threshold_value
  - `ABSOLUTE`: abs(target - source) <= threshold_value

**Helper methods:**
- `_build_details()`: Formats connection details string
- `_to_numeric()`: Converts values to numeric for comparison

---

### 6. src/connectors/base_connector.py
**Purpose:** Abstract base class for all database connectors

#### Class: `BaseConnector`

**Abstract methods (must be implemented by subclasses):**
- `connect()`: Establish database connection
- `disconnect()`: Close database connection
- `execute_query(sql)`: Execute SQL and return single result
- `test_connection()`: Test if connection works
- `get_dialect()`: Return database dialect name

**Context manager support:**
- `__enter__()`: Opens connection
- `__exit__()`: Closes connection automatically
- Allows `with connector as conn:` syntax

---

### 7. src/connectors/sqlserver_connector.py
**Purpose:** SQL Server database connector

#### Class: `SQLServerConnector`

**`connect()`**
- Uses pyodbc to connect to SQL Server
- Connection string format:
  - `DRIVER={ODBC Driver 17 for SQL Server};SERVER=host,port;DATABASE=db;UID=user;PWD=pass`
  - For Windows Authentication: Empty UID and PWD uses Trusted_Connection

**`execute_query(sql)`**
- Executes query and returns first row, first column
- Uses cursor with fetchone()

**`get_dialect()`**
- Returns: 'sqlserver'

---

### 8. src/connectors/oracle_connector.py
**Purpose:** Oracle database connector (using pyodbc)

#### Class: `OracleConnector`

**`connect()`**
- Uses pyodbc with Oracle ODBC driver
- Connection string format:
  - `Driver={Oracle in OraClient12Home1};DBQ=host:port/service_name;UID=user;PWD=pass`
- Supports both SERVICE_NAME and SID

**`execute_query(sql)`**
- Executes query and returns first value

**`get_dialect()`**
- Returns: 'oracle'

---

### 9. src/connectors/netezza_connector.py
**Purpose:** IBM Netezza database connector

#### Class: `NetezzaConnector`

**`connect()`**
- Uses nzpy to connect to Netezza
- Connection parameters: host, port, database, user, password

**`execute_query(sql)`**
- Executes query and returns first value

**`get_dialect()`**
- Returns: 'netezza'

---

### 10. src/connectors/snowflake_connector.py
**Purpose:** Snowflake data warehouse connector

#### Class: `SnowflakeConnector`

**`connect()`**
- Uses snowflake-connector-python
- Connection parameters: account, user, password, database, warehouse, schema, role

**`execute_query(sql)`**
- Executes query and returns first value

**`get_dialect()`**
- Returns: 'snowflake'

---

### 11. src/connectors/csv_connector.py
**Purpose:** CSV file connector (for validating CSV files)

#### Class: `CSVConnector`

**`connect()`**
- Uses pandas to read CSV file
- Stores DataFrame in memory

**`execute_query(sql)`**
- Parses SQL to extract:
  - Aggregate function (COUNT, SUM, etc.)
  - Column name
  - Filter condition
- Applies filter to DataFrame
- Executes aggregate function on pandas DataFrame
- Returns result

**`get_dialect()`**
- Returns: 'csv'

---

### 12. src/utils/logger.py
**Purpose:** Centralized logging configuration

#### Functions:

**`setup_logger(level=logging.INFO)`**
- Configures logging with console and file handlers
- Format: `[TIMESTAMP] [LEVEL] message`
- File: `validation.log`

**`logger`**
- Global logger instance
- Use: `logger.info()`, `logger.error()`, etc.

---

### 13. src/utils/exceptions.py
**Purpose:** Custom exception classes

#### Classes:

**`ValidationException`**
- Base exception for validation errors

**`ConfigurationException`**
- Raised when configuration is invalid

**`ConnectionException`**
- Raised when database connection fails

**`QueryException`**
- Raised when SQL query fails

---

## Configuration Files

### Excel Configuration (Vertical Layout)

```
Field Name               | Validation 1        | Validation 2
-------------------------|---------------------|---------------------
Validation Name          | Daily Order Count   | Total Sales
Validation_id            | VAL001              | VAL002
Source Type              | SQLServer           | Netezza
Source Host Name         | p8054               | nz-db-ut
Source Port              | 3085                | 5480
Source Database Name     | OrderDB             | SalesDB
Source Schema Name       | dbo                 | sales
Source Table Name        | Orders              | Transactions
Source Column Name       |                     | Amount
Source Column Expression |                     |
Source Filter            | date >= '2024-01-01'|
Target Type              | Snowflake           | Snowflake
Target Host Name         | snowflake-prod      | snowflake-prod
...                      | ...                 | ...
```

### .env Files (Host-Specific Credentials)

**Format:** `.env.{hostname}`

**Example:** `.env.p8054`
```env
HOSTNAME=p8054.company.com
USERNAME=sql_user
PASSWORD=sql_password
PORT=3085
DATABASE=BDM Archive
```

**Required Fields:**
- HOSTNAME, USERNAME, PASSWORD

**Optional Fields:**
- PORT, DATABASE, SCHEMA, DRIVER
- Oracle: SERVICE_NAME or SID
- Snowflake: ACCOUNT, WAREHOUSE, ROLE

---

## How It All Works Together

### Execution Flow:

1. **User runs command:**
   ```bash
   python -m src.main --config validations.xlsx
   ```

2. **main.py parses arguments**
   - Validates config file exists
   - Sets up logging

3. **ConfigParser reads Excel**
   - Loads vertical layout Excel file
   - Maps field names to row indices
   - Parses each column into ValidationConfig object
   - Returns list of validations

4. **Validator initializes**
   - Creates EnvManager for credential management

5. **For each validation:**
   - **EnvManager loads credentials**
     - Reads `.env.{source_host}` file
     - Reads `.env.{target_host}` file
     - Validates required fields present

   - **Validator creates connectors**
     - Creates source connector (e.g., SQLServerConnector)
     - Creates target connector (e.g., SnowflakeConnector)
     - Passes credentials from .env files

   - **QueryBuilder builds SQL**
     - Generates SQL based on rule_type
     - Applies filters
     - Returns query string

   - **Connectors execute queries**
     - Opens database connections
     - Executes SQL queries
     - Returns single aggregate value
     - Closes connections

   - **Validator compares results**
     - Checks if values match within threshold
     - Creates ValidationResult (PASS/FAIL/ERROR)

   - **Validator returns result**
     - Result added to results list

6. **main.py saves results**
   - Converts results to pandas DataFrame
   - Saves to CSV file

7. **main.py prints summary**
   - Shows total, passed, failed, errors
   - Lists failed validations

8. **Program exits**
   - Exit code 0 if all passed
   - Exit code 1 if any failures or errors

---

## Example Execution

### Input (Excel):
```
Source: SQLServer @ p8054:3085 / OrderDB.dbo.Orders
Target: Snowflake @ snowflake-prod / ANALYTICS.PUBLIC.ORDERS
Rule: COUNT_STAR
Filter: order_date >= '2024-01-01'
Threshold: EXACT (0)
```

### .env Files:
**`.env.p8054`**
```env
HOSTNAME=p8054.company.com
USERNAME=sql_user
PASSWORD=sql_password
PORT=3085
```

**`.env.snowflake-prod`**
```env
HOSTNAME=xy12345.us-east-1.snowflakecomputing.com
USERNAME=snow_user
PASSWORD=snow_password
ACCOUNT=xy12345.us-east-1
WAREHOUSE=COMPUTE_WH
```

### Generated SQL:
**Source Query:**
```sql
SELECT COUNT(*) FROM OrderDB.dbo.Orders
WHERE order_date >= '2024-01-01'
```

**Target Query:**
```sql
SELECT COUNT(*) FROM ANALYTICS.PUBLIC.ORDERS
WHERE ORDER_DATE >= '2024-01-01'
```

### Execution:
```
1. Load credentials from .env.p8054 and .env.snowflake-prod
2. Create SQLServerConnector with p8054 credentials
3. Create SnowflakeConnector with snowflake-prod credentials
4. Execute source query → Result: 1500
5. Execute target query → Result: 1500
6. Compare: 1500 == 1500 → PASS
7. Save result to CSV
```

### Output (CSV):
```csv
validation_id,validation_name,status,source_value,target_value,difference,percentage_diff,...
VAL001,Daily Order Count,PASS,1500,1500,0,0.0,...
```

---

## Key Design Decisions

1. **Vertical Excel Layout**: More natural for defining multiple validations side-by-side
2. **Host-Specific .env Files**: Supports multiple instances and environments cleanly
3. **Connector Pattern**: Easy to add new database types
4. **Context Managers**: Automatic connection cleanup
5. **Aggregate-Only Queries**: Fast, scalable validation without row-by-row comparison
6. **Single Value Return**: All queries return one aggregate value for simple comparison
7. **CSV Output**: Easy to share, import into Excel, or load into BI tools

---

## Adding a New Database Type

To add support for a new database (e.g., PostgreSQL):

1. **Create connector:** `src/connectors/postgres_connector.py`
   ```python
   class PostgresConnector(BaseConnector):
       def connect(self): ...
       def execute_query(self, sql): ...
       def get_dialect(self): return 'postgres'
   ```

2. **Update Validator:** Add to CONNECTOR_MAP
   ```python
   CONNECTOR_MAP = {
       ...
       'postgres': PostgresConnector,
       'postgresql': PostgresConnector,
   }
   ```

3. **Create .env template:** `.env.example-postgres`

4. **Update documentation:** Add to README.md and CREDENTIALS_GUIDE.md

That's it! The rest of the system will automatically work with the new database type.

---

## Questions?

For more details, see:
- [README.md](README.md) - Setup and usage instructions
- [CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md) - Detailed credential management guide
