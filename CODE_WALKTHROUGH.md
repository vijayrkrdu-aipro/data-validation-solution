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
1. Reading validation rules from an Excel file
2. Connecting to source and target databases
3. Running aggregate SQL queries (COUNT, SUM, etc.)
4. Comparing results and reporting pass/fail

**Architecture Pattern:** Connector Pattern + Factory Pattern
- Each database type has its own connector
- ConnectionManager creates the right connector based on type
- All connectors share the same interface (BaseConnector)

---

## Core Components

```
Main Flow:
main.py → ConfigParser → ConnectionManager → QueryBuilder → Validator → Results
           (reads Excel)   (creates connectors)  (builds SQL)   (compares)  (CSV)
```

---

## File-by-File Breakdown

### 1. src/main.py
**Purpose:** Entry point for the CLI application

#### Key Functions:

**`parse_arguments()`**
- Reads command-line arguments
- Parameters:
  - `--config`: Path to Excel file with validations
  - `--connections`: Path to YAML file with database connections
  - `--output`: Where to save CSV results (optional)
  - `--test-connections`: Just test connections, don't validate
  - `--verbose`: Enable detailed logging

**`test_connections(connection_manager)`**
- Tests all database connections before running validations
- Prints a nice table showing which connections work

**`generate_output_path(custom_path)`**
- Creates output filename with timestamp
- Example: `validation_report_20240115_143022.csv`

**`save_results_to_csv(results, output_path)`**
- Converts validation results to DataFrame
- Saves as CSV file

**`print_summary(results)`**
- Prints summary table to console
- Shows: Total, Passed, Failed, Errors

**`main()`**
- Orchestrates everything:
  1. Load connections from YAML
  2. Parse validations from Excel
  3. Run each validation
  4. Save results to CSV
  5. Print summary

---

### 2. src/config_parser.py
**Purpose:** Reads and parses the Excel validation configuration file

#### Classes:

**`ValidationConfig` (dataclass)**
- Stores a single validation rule
- Fields:
  - `validation_id`: Unique ID (e.g., "VAL001")
  - `validation_name`: Descriptive name
  - `source_connection`: Which connection to use for source
  - `source_database/schema/table/column`: Where to query
  - `source_filter`: WHERE clause for source
  - `target_*`: Same but for target database
  - `rule_type`: What aggregate to use (COUNT_STAR, SUM, etc.)
  - `custom_expression`: For CUSTOM rule types
  - `threshold_type`: EXACT, PERCENTAGE, or ABSOLUTE
  - `threshold_value`: The tolerance (0 for exact, 0.01 for 1%, etc.)
  - `enabled`: TRUE/FALSE to enable/disable

**`ConfigParser`**
- Reads Excel file and converts rows to ValidationConfig objects

#### Key Methods:

**`__init__(excel_path, sheet_name='Validations')`**
- Parameters:
  - `excel_path`: Path to Excel file
  - `sheet_name`: Which sheet has validations (default: "Validations")

**`parse()`**
- Main method that does all the work
- Returns: List of ValidationConfig objects
- Steps:
  1. Reads Excel file with pandas
  2. Validates required columns exist
  3. Parses each row
  4. Skips disabled validations
  5. Returns list of enabled validations

**`_parse_row(row, row_idx)`**
- Converts one Excel row to ValidationConfig object
- Handles missing values (NaN) gracefully
- Validates threshold_type is valid

**Helper methods:**
- `_get_string_value()`: Gets string from Excel, handles NaN
- `_get_float_value()`: Gets number from Excel, handles NaN
- `_get_bool_value()`: Gets TRUE/FALSE from Excel, handles various formats

---

### 3. src/connection_manager.py
**Purpose:** Manages database connections from YAML config

#### Class: `ConnectionManager`

**`__init__(config_path)`**
- Loads YAML file with database connections
- Loads .env file for environment variables
- Parameters:
  - `config_path`: Path to connections.yaml

**`_load_config()`**
- Reads YAML file
- Validates 'connections' key exists
- Stores connections in memory

**`_resolve_env_vars(value)`**
- Replaces `${VAR_NAME}` with actual environment variable values
- Example: `${SQLSERVER_USER}` becomes `"john_doe"`
- Works recursively for nested dictionaries

**`get_connector(connection_name)`**
- Returns the right connector for a connection name
- Steps:
  1. Finds connection config in YAML
  2. Resolves environment variables
  3. Determines connector type (sqlserver, oracle, etc.)
  4. Creates and returns appropriate connector instance

**`test_connection(connection_name)`**
- Tests if a specific connection works
- Returns: True if successful, False otherwise

**`test_all_connections()`**
- Tests all configured connections
- Returns: Dictionary mapping connection names to True/False

#### Connector Map:
```python
CONNECTOR_MAP = {
    'sqlserver': SQLServerConnector,
    'oracle': OracleConnector,
    'netezza': NetezzaConnector,
    'snowflake': SnowflakeConnector,
    'csv': CSVConnector
}
```

---

### 4. src/query_builder.py
**Purpose:** Builds SQL queries for aggregate validations

#### Class: `QueryBuilder`

**Static Class** - All methods are `@staticmethod`, no need to create an instance

**Rule Type Mapping:**
```python
RULE_TYPES = {
    'COUNT_STAR': 'COUNT(*)',
    'COUNT_COLUMN': 'COUNT({column})',
    'SUM': 'SUM({column})',
    'AVG': 'AVG({column})',
    'MIN': 'MIN({column})',
    'MAX': 'MAX({column})',
    'COUNT_DISTINCT': 'COUNT(DISTINCT {column})',
    'COUNT_NULL': 'SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END)',
    'COUNT_NOT_NULL': 'SUM(CASE WHEN {column} IS NOT NULL THEN 1 ELSE 0 END)'
}
```

#### Key Methods:

**`build_query(dialect, database, schema, table, column, rule_type, custom_expression, filter_clause)`**
- Builds a complete SQL query
- Parameters:
  - `dialect`: Database type (sqlserver, oracle, etc.)
  - `database`: Database name (optional)
  - `schema`: Schema name (optional)
  - `table`: Table name (required)
  - `column`: Column name (needed for most rules)
  - `rule_type`: Type of aggregate
  - `custom_expression`: Custom SQL (if rule_type=CUSTOM)
  - `filter_clause`: WHERE clause without "WHERE" keyword
- Returns: Complete SQL query string
- Example output: `SELECT COUNT(*) FROM dbo.Orders WHERE order_date >= '2024-01-01'`

**`_build_table_reference(dialect, database, schema, table)`**
- Builds the table reference part based on database type
- Examples:
  - SQL Server: `[database].[schema].[table]`
  - Oracle: `schema.table`
  - Snowflake: `database.schema.table`

**`validate_rule_type(rule_type)`**
- Checks if a rule type is valid
- Returns: True/False

---

### 5. src/validator.py
**Purpose:** Core validation engine that runs validations and compares results

#### Classes:

**`ValidationResult` (dataclass)**
- Stores the result of one validation
- Fields:
  - `validation_id`, `validation_name`: From config
  - `status`: PASS, FAIL, or ERROR
  - `source_value`: Value from source query
  - `target_value`: Value from target query
  - `difference`: target_value - source_value
  - `percentage_diff`: Percentage difference
  - `source_details`: Connection and table info
  - `target_details`: Connection and table info
  - `execution_timestamp`: When it ran
  - `error_message`: Error details (if status=ERROR)
  - `source_query`, `target_query`: SQL queries executed

**`Validator`**
- Executes validations and compares results

#### Key Methods:

**`__init__(connection_manager)`**
- Parameters:
  - `connection_manager`: ConnectionManager instance to get database connections

**`validate(config)`**
- Main validation method
- Parameters:
  - `config`: ValidationConfig object with validation details
- Returns: ValidationResult object
- Steps:
  1. Get source and target connectors
  2. Build SQL queries for both
  3. Execute queries
  4. Compare results
  5. Determine PASS/FAIL based on threshold
  6. Return ValidationResult

**`_build_details(connection, database, schema, table)`**
- Creates a details string
- Example: `"sqlserver_prod:OrderDB.dbo.Orders"`

**`_to_numeric(value)`**
- Converts value to float for comparison
- Handles None gracefully

**`_check_threshold(source_value, target_value, threshold_type, threshold_value)`**
- Determines if validation passes
- Logic:
  - **EXACT**: `abs(target - source) <= threshold_value`
  - **PERCENTAGE**: `abs((target - source) / source) <= threshold_value`
  - **ABSOLUTE**: `abs(target - source) <= threshold_value`
- Returns: "PASS" or "FAIL"

---

### 6. Connectors (src/connectors/)

All connectors inherit from `BaseConnector` and implement the same interface.

#### Base Connector (base_connector.py)

**`BaseConnector` (Abstract Base Class)**
- Defines the interface all connectors must implement

**Abstract Methods** (must be implemented by each connector):
- `connect()`: Establish database connection
- `disconnect()`: Close database connection
- `execute_query(sql)`: Run SQL and return result
- `test_connection()`: Test if connection works
- `get_dialect()`: Return database type name

**Context Manager Support:**
```python
with connector as conn:
    result = conn.execute_query("SELECT COUNT(*) FROM table")
# Automatically connects and disconnects
```

#### SQL Server Connector (sqlserver_connector.py)

**`SQLServerConnector`**
- Uses `pyodbc` library
- Default driver: `{ODBC Driver 17 for SQL Server}`

**`connect()`**
- Builds connection string from config
- Supports:
  - Individual parameters (host, port, database, username, password)
  - Windows Authentication (no username/password)
  - Custom connection string
- Sets timeout to 30 seconds

**`execute_query(sql)`**
- Executes query using cursor
- Returns first column of first row
- Handles NULL values

#### Oracle Connector (oracle_connector.py)

**`OracleConnector`**
- Uses `pyodbc` with Oracle ODBC driver
- Default driver: `{Oracle in OraClient12Home1}`

**`connect()`**
- Supports both `service_name` and `sid`
- Connection string format: `Driver={driver};DBQ=host:port/service;UID=user;PWD=pass;`

**`test_connection()`**
- Uses Oracle-specific query: `SELECT 1 FROM DUAL`

#### Netezza Connector (netezza_connector.py)

**`NetezzaConnector`**
- Uses `nzpy` library
- Default port: 5480

**`connect()`**
- Parameters:
  - `securityLevel`: Security level (default: 0)
  - `logLevel`: Logging level (default: 0)

#### Snowflake Connector (snowflake_connector.py)

**`SnowflakeConnector`**
- Uses `snowflake-connector-python`

**`connect()`**
- Required parameters:
  - `account`: Snowflake account ID
  - `username`, `password`
- Optional parameters:
  - `database`, `schema`, `warehouse`, `role`

#### CSV Connector (csv_connector.py)

**`CSVConnector`**
- Uses `pandas` to load CSV into memory
- Uses `pandasql` library for SQL queries on DataFrames

**`connect()`**
- Loads CSV file with pandas
- Parameters:
  - `file_path`: Path to CSV file
  - `encoding`: File encoding (default: utf-8)
  - `delimiter`: Column separator (default: ,)

**`execute_query(sql)`**
- Uses pandasql to run SQL on DataFrame
- The DataFrame is referenced as "data" in SQL
- Example: `SELECT COUNT(*) FROM data WHERE age > 18`

---

### 7. Utilities (src/utils/)

#### Exceptions (exceptions.py)

Custom exception hierarchy:
- `ValidationException`: Base exception
  - `ConnectionException`: Connection errors
  - `ConfigurationException`: Config file errors
  - `QueryExecutionException`: SQL execution errors
  - `InvalidRuleTypeException`: Invalid rule type

#### Logger (logger.py)

**`setup_logger(name, level)`**
- Creates a logger with console output
- Parameters:
  - `name`: Logger name (default: "data_validator")
  - `level`: Logging level (default: INFO)
- Format: `2024-01-15 14:30:22 - INFO - Message here`

**Default logger instance:**
```python
from src.utils.logger import logger
logger.info("This is an info message")
logger.error("This is an error message")
```

---

## Configuration Files

### 1. connections.yaml

**Purpose:** Defines database connections

**Structure:**
```yaml
connections:
  connection_name:      # Used in Excel config
    type: sqlserver     # Connector type
    host: server.com    # Database server
    port: 1433          # Port number
    database: MyDB      # Database name
    username: ${VAR}    # Can use env variables
    password: ${VAR}    # Can use env variables
```

**Supported Types:**
- `sqlserver` or `mssql`
- `oracle`
- `netezza` or `nz`
- `snowflake`
- `csv`

**Environment Variables:**
- Use `${VAR_NAME}` syntax
- Resolved from `.env` file or system environment

### 2. Excel Validation Config

**Sheet Name:** "Validations"

**Required Columns:**
- `validation_id`: Unique identifier
- `validation_name`: Description
- `source_connection`: Connection name from YAML
- `source_table`: Table name
- `target_connection`: Connection name from YAML
- `target_table`: Table name
- `rule_type`: Aggregate type
- `threshold_type`: EXACT/PERCENTAGE/ABSOLUTE
- `threshold_value`: Tolerance value

**Optional Columns:**
- `source_database/schema/column/filter`
- `target_database/schema/column/filter`
- `custom_expression`: For CUSTOM rule type
- `enabled`: TRUE/FALSE

**Example Row:**
```
VAL001 | Order Count | sqlserver_prod | NULL | dbo | Orders | NULL | date>='2024-01-01' |
snowflake_cloud | ANALYTICS | PUBLIC | ORDERS | NULL | DATE>='2024-01-01' |
COUNT_STAR | NULL | EXACT | 0 | TRUE
```

### 3. .env File

**Purpose:** Store sensitive credentials

**Format:**
```
SQLSERVER_USER=john_doe
SQLSERVER_PASS=secret123
ORACLE_USER=oracle_user
ORACLE_PASS=oracle_pass
```

**Security:**
- Ignored by Git (.gitignore)
- Never commit to repository
- Use .env.template as template

---

## How It All Works Together

### Execution Flow:

```
1. User runs: python -m src.main --config validations.xlsx --connections connections.yaml

2. main.py:
   - Parses command-line arguments
   - Creates ConnectionManager with connections.yaml
   - Creates ConfigParser with validations.xlsx

3. ConnectionManager:
   - Loads connections.yaml
   - Loads .env file
   - Stores connection configs in memory

4. ConfigParser:
   - Reads Excel file
   - Converts each row to ValidationConfig object
   - Returns list of validations

5. For each validation:

   a. Validator.validate(config):
      - Gets source connector from ConnectionManager
      - Gets target connector from ConnectionManager

   b. For source:
      - QueryBuilder builds SQL query
      - Source connector executes query
      - Returns single value (e.g., 1500)

   c. For target:
      - QueryBuilder builds SQL query
      - Target connector executes query
      - Returns single value (e.g., 1500)

   d. Comparison:
      - Calculates difference: 1500 - 1500 = 0
      - Checks threshold: EXACT with value 0
      - Result: PASS

   e. Returns ValidationResult object

6. All results collected

7. Save to CSV:
   - Converts results to DataFrame
   - Saves to output/validation_report_TIMESTAMP.csv

8. Print summary to console
```

### Example Execution:

**Input (Excel):**
```
VAL001 | Daily Orders | sqlserver_prod | dbo | Orders | COUNT_STAR | EXACT | 0
```

**What Happens:**
1. ConnectionManager gets SQLServerConnector for "sqlserver_prod"
2. QueryBuilder creates: `SELECT COUNT(*) FROM [OrderDB].[dbo].[Orders]`
3. SQLServerConnector executes query → Result: 1500
4. ConnectionManager gets SnowflakeConnector for target
5. QueryBuilder creates: `SELECT COUNT(*) FROM ANALYTICS.PUBLIC.ORDERS`
6. SnowflakeConnector executes query → Result: 1500
7. Validator compares: 1500 vs 1500 with EXACT threshold
8. Result: PASS

**Output (CSV):**
```csv
validation_id,validation_name,status,source_value,target_value,difference,...
VAL001,Daily Orders,PASS,1500,1500,0,...
```

---

## Quick Reference

### Adding a New Validation:

1. Open `examples/validation_template.xlsx`
2. Add a new row with:
   - Unique validation_id
   - Source and target details
   - Rule type
   - Threshold settings
3. Save and run

### Adding a New Database Connection:

1. Open `config/connections.yaml`
2. Add new connection under `connections:`
3. Add credentials to `.env` file
4. Test: `python -m src.main --connections config/connections.yaml --test-connections`

### Understanding a Validation Result:

- **PASS**: Values match within threshold
- **FAIL**: Values differ more than threshold
- **ERROR**: Connection or query failed

### Threshold Examples:

- `EXACT, 0`: Must match exactly
- `PERCENTAGE, 0.01`: Allow 1% difference
- `ABSOLUTE, 100`: Allow difference of 100

---

## Common Questions

**Q: Where are credentials stored?**
A: In `.env` file, referenced in `connections.yaml` using `${VAR_NAME}`

**Q: How do I disable a validation?**
A: Set `enabled = FALSE` in Excel

**Q: Can I validate between different database types?**
A: Yes! Source can be SQL Server, target can be Snowflake, etc.

**Q: What if a query fails?**
A: Status = ERROR, error message in CSV output, validation continues

**Q: How do I add a custom SQL expression?**
A: Set `rule_type = CUSTOM`, put SQL in `custom_expression` column

---

This walkthrough covers all the essential components. Each file is designed to do one thing well, making the system modular and easy to understand!
