# Data Validation Solution

A configuration-driven data load validation solution in Python that validates data between databases (SQL Server, Oracle, Netezza, Snowflake) and CSV files using aggregate-level comparisons.

## Features

- **Database Agnostic**: Supports SQL Server, Oracle, Netezza, Snowflake, and CSV files as both source and target
- **Configuration-Driven**: Define validations in Excel, connections in YAML
- **Aggregate Validations**: COUNT, SUM, AVG, MIN, MAX, COUNT_DISTINCT, COUNT_NULL, COUNT_NOT_NULL, and custom expressions
- **Flexible Thresholds**: Exact match, percentage tolerance, or absolute difference
- **Filter Support**: Apply WHERE clauses to both source and target queries
- **CSV Output**: Detailed validation results with pass/fail status
- **Error Handling**: Graceful handling of connection and query errors
- **Easy to Use**: Windows batch file for quick execution

## Requirements

- Python 3.8 or higher
- Database drivers (installed via requirements.txt)
- Access to source and target databases

## Installation

### 1. Clone or Download the Project

```bash
cd C:\Users\conco\Documents\Projects\data-validation-solution
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Connections

Copy the connection template and customize it:

```bash
copy config\connections_template.yaml config\connections.yaml
```

Edit `config\connections.yaml` with your actual database credentials.

### 5. Create Validation Configuration

Run the Excel template generator:

```bash
python create_excel_template.py
```

This creates `examples\validation_template.xlsx` with sample validations. Customize it for your needs.

## Configuration

### Connections Configuration (YAML)

The `config\connections.yaml` file defines database connections:

```yaml
connections:
  sqlserver_prod:
    type: sqlserver
    host: server.domain.com
    port: 1433
    database: ProductionDB
    username: ${SQLSERVER_USER}  # Environment variable
    password: ${SQLSERVER_PASS}

  oracle_dwh:
    type: oracle
    host: oracle.domain.com
    port: 1521
    username: ${ORACLE_USER}
    password: ${ORACLE_PASS}
    service_name: ORCL

  snowflake_cloud:
    type: snowflake
    account: xy12345.us-east-1
    username: ${SNOW_USER}
    password: ${SNOW_PASS}
    database: PROD_DB
    warehouse: COMPUTE_WH
```

**Supported Connection Types:**
- `sqlserver` or `mssql` - Microsoft SQL Server
- `oracle` - Oracle Database
- `netezza` or `nz` - IBM Netezza
- `snowflake` - Snowflake Data Warehouse
- `csv` - CSV Files

**Environment Variables:**
Create a `.env` file in the project root for sensitive credentials:

```
SQLSERVER_USER=myuser
SQLSERVER_PASS=mypassword
ORACLE_USER=oracleuser
ORACLE_PASS=oraclepass
```

### Validation Configuration (Excel)

The Excel file (`examples\validation_template.xlsx`) contains validation rules with these columns:

| Column | Required | Description |
|--------|----------|-------------|
| validation_id | Yes | Unique identifier (e.g., VAL001) |
| validation_name | Yes | Descriptive name |
| source_connection | Yes | Connection name from YAML |
| source_database | No | Database name (can override YAML) |
| source_schema | No | Schema name |
| source_table | Yes | Table name |
| source_column | Conditional | Column name (required for column-specific rules) |
| source_filter | No | WHERE clause (without 'WHERE' keyword) |
| target_connection | Yes | Connection name from YAML |
| target_database | No | Database name |
| target_schema | No | Schema name |
| target_table | Yes | Table name |
| target_column | Conditional | Column name |
| target_filter | No | WHERE clause |
| rule_type | Yes | See Rule Types below |
| custom_expression | Conditional | SQL expression (for CUSTOM rule type) |
| threshold_type | Yes | EXACT, PERCENTAGE, or ABSOLUTE |
| threshold_value | Yes | Threshold value (0 for exact, 0.01 for 1%, etc.) |
| enabled | No | TRUE/FALSE (default: TRUE) |

**Rule Types:**
- `COUNT_STAR` - COUNT(*) - total row count
- `COUNT_COLUMN` - COUNT(column) - non-null count
- `SUM` - SUM(column) - sum of values
- `AVG` - AVG(column) - average value
- `MIN` - MIN(column) - minimum value
- `MAX` - MAX(column) - maximum value
- `COUNT_DISTINCT` - COUNT(DISTINCT column) - unique values
- `COUNT_NULL` - Count of NULL values
- `COUNT_NOT_NULL` - Count of non-NULL values
- `CUSTOM` - Custom SQL expression (use custom_expression column)

**Threshold Types:**
- `EXACT` - Values must match exactly (within threshold_value)
- `PERCENTAGE` - Allow percentage difference (e.g., 0.01 = 1%)
- `ABSOLUTE` - Allow absolute difference (e.g., 100 = allow difference of 100)

## Usage

### Option 1: Windows Batch File (Easiest)

Double-click `run_validation.bat` or run from command prompt:

```bash
run_validation.bat
```

### Option 2: Command Line

```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml
```

### Option 3: Custom Output Path

```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml --output reports\my_report.csv
```

### Option 4: Test Connections Only

```bash
python -m src.main --connections config\connections.yaml --test-connections
```

### Option 5: Verbose Logging

```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml --verbose
```

## Output

The tool generates a CSV report with these columns:

- `validation_id` - Validation identifier
- `validation_name` - Validation description
- `status` - PASS, FAIL, or ERROR
- `source_value` - Value from source
- `target_value` - Value from target
- `difference` - target_value - source_value
- `percentage_diff` - Percentage difference
- `source_details` - Source connection and table
- `target_details` - Target connection and table
- `rule_type` - Type of validation
- `threshold_type` - Threshold type used
- `threshold_value` - Threshold value
- `execution_timestamp` - When validation ran
- `error_message` - Error details (if status is ERROR)

### Console Output

The tool also prints a summary to the console:

```
============================================================
VALIDATION SUMMARY
============================================================
Total Validations: 8
✓ Passed:          6 (75.0%)
✗ Failed:          1 (12.5%)
⚠ Errors:          1 (12.5%)
============================================================
```

## Examples

### Example 1: Count Validation with Exact Match

```excel
validation_id: VAL001
validation_name: Daily Order Count
source_connection: sqlserver_prod
source_schema: dbo
source_table: Orders
source_filter: order_date = '2024-01-15'
target_connection: snowflake_cloud
target_schema: PUBLIC
target_table: ORDERS
target_filter: ORDER_DATE = '2024-01-15'
rule_type: COUNT_STAR
threshold_type: EXACT
threshold_value: 0
```

### Example 2: Sum Validation with Percentage Threshold

```excel
validation_id: VAL002
validation_name: Total Sales Amount
source_connection: oracle_dwh
source_schema: SALES
source_table: TRANSACTIONS
source_column: AMOUNT
target_connection: snowflake_cloud
target_table: TRANSACTIONS
target_column: AMOUNT
rule_type: SUM
threshold_type: PERCENTAGE
threshold_value: 0.01  # Allow 1% difference
```

### Example 3: Custom Expression

```excel
validation_id: VAL003
validation_name: Weighted Revenue
source_connection: sqlserver_prod
source_table: Sales
rule_type: CUSTOM
custom_expression: SUM(Price * Quantity * Discount)
threshold_type: PERCENTAGE
threshold_value: 0.02  # Allow 2% difference
```

## Project Structure

```
data-validation-solution/
├── config/
│   ├── connections.yaml          # Your database connections
│   └── connections_template.yaml # Template with examples
├── src/
│   ├── main.py                   # CLI entry point
│   ├── config_parser.py          # Excel parser
│   ├── connection_manager.py     # Connection management
│   ├── query_builder.py          # SQL query generation
│   ├── validator.py              # Validation engine
│   ├── connectors/
│   │   ├── base_connector.py
│   │   ├── sqlserver_connector.py
│   │   ├── oracle_connector.py
│   │   ├── netezza_connector.py
│   │   ├── snowflake_connector.py
│   │   └── csv_connector.py
│   └── utils/
│       ├── logger.py
│       └── exceptions.py
├── output/                       # Generated reports
├── examples/
│   └── validation_template.xlsx  # Excel template
├── requirements.txt
├── create_excel_template.py      # Script to generate Excel template
├── run_validation.bat            # Windows batch runner
└── README.md
```

## Troubleshooting

### Python Not Found

Install Python 3.8+ from [python.org](https://www.python.org/downloads/) and ensure it's in your PATH.

### Database Driver Issues

**SQL Server:**
- Install ODBC Driver 17 or 18 for SQL Server
- Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Oracle:**
- Install Oracle Instant Client
- Download from: https://www.oracle.com/database/technologies/instant-client.html

**Netezza:**
- `nzpy` should work out of the box
- For ODBC, install Netezza ODBC drivers

**Snowflake:**
- The `snowflake-connector-python` package is sufficient

### Connection Errors

1. Verify database credentials in `config\connections.yaml`
2. Check network connectivity to database servers
3. Ensure firewall allows connections to database ports
4. Use `--test-connections` flag to diagnose connection issues

### Excel Template Not Found

Run `python create_excel_template.py` to generate the template.

## Advanced Usage

### Filtering Validations

To run only specific validations, edit the Excel file and set `enabled = FALSE` for validations you want to skip.

### Parallel Source and Target

The solution supports any combination of source and target, including:
- SQL Server → SQL Server
- Oracle → Oracle
- CSV → Snowflake
- Snowflake → SQL Server

### Custom SQL Expressions

For complex validations, use `rule_type = CUSTOM` and provide the full aggregate expression in `custom_expression`:

```
CUSTOM: SUM(CASE WHEN status = 'ACTIVE' THEN amount ELSE 0 END)
```

## Future Enhancements

- Parallel execution of validations
- Database storage of validation results
- Email/Slack notifications
- Web UI for configuration
- REST API
- Scheduling capability
- Support for joins and complex queries

## Support

For issues or questions, please contact your development team or create an issue in the project repository.

## License

Internal use only.
