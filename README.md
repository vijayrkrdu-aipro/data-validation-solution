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

### 4. Configure Database Credentials

Create `.env` files for each database host. See [CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md) for details.

```bash
# Example: Copy templates and edit with your credentials
copy .env.example-sqlserver .env.p8054
copy .env.example-netezza .env.nz-db-ut
notepad .env.p8054  # Edit with your actual credentials
```

### 5. Create Validation Configuration

Run the Excel template generator:

```bash
python create_excel_template.py
```

This creates `examples\validation_template.xlsx` with sample validations. Customize it for your needs.

## Configuration

### Credentials Configuration (.env Files)

The solution uses **host-specific `.env` files** for managing credentials. For each database host in your Excel configuration, create a corresponding `.env.{hostname}` file.

**Example:** If your Excel has `Source Host Name: p8054`, create `.env.p8054`

See [CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md) for detailed setup instructions.

**Quick Start:**

1. Copy an example .env file:
```bash
copy .env.example-sqlserver .env.p8054
copy .env.example-netezza .env.nz-db-ut
```

2. Edit with your credentials:
```env
# .env.p8054
HOSTNAME=p8054.company.com
USERNAME=your_username
PASSWORD=your_password
PORT=3085
DATABASE=BDM Archive
```

**Supported Database Types:**
- `SQLServer` or `MSSQL` - Microsoft SQL Server
- `Oracle` - Oracle Database
- `Netezza` or `NZ` - IBM Netezza
- `Snowflake` - Snowflake Data Warehouse
- `CSV` - CSV Files

### Validation Configuration (Excel)

The Excel file uses a **vertical layout** where each column is a validation and rows are fields.

**Format:** The first column contains field names, and each subsequent column contains one validation.

| Field Name | Validation 1 | Validation 2 |
|-----------|--------------|--------------|
| Validation Name | Daily Order Count | Total Sales Amount |
| Validation_id | VAL001 | VAL002 |
| Source Type | SQLServer | Netezza |
| Source Host Name | p8054 | nz-db-ut |
| Source Port | 3085 | 5480 |
| Source Database Name | OrderDB | SalesDB |
| Source Schema Name | dbo | sales |
| Source Table Name | Orders | Transactions |
| Source Column Name | | Amount |
| Source Column Expression | | |
| Source Filter | order_date = '2024-01-15' | |
| Target Type | Snowflake | Snowflake |
| Target Host Name | snowflake-prod | snowflake-prod |
| ... | ... | ... |

**Required Fields:**
- Validation Name, Validation_id
- Source Type, Source Host Name, Source Port, Source Database Name, Source Table Name
- Target Type, Target Host Name, Target Port, Target Database Name, Target Table Name
- Rule Type

**Optional Fields:**
- Source/Target Schema Name, Column Name, Column Expression, Filter
- Threshold Type (default: EXACT), Threshold Value (default: 0)

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
python -m src.main --config examples\validation_template.xlsx
```

### Option 3: Custom Output Path

```bash
python -m src.main --config examples\validation_template.xlsx --output reports\my_report.csv
```

### Option 4: Use Your Own Excel File

To pass your own Excel file from anywhere on your computer:

```bash
python -m src.main --config "C:\Users\YourName\Documents\my_validations.xlsx"
```

Or with a custom output location:

```bash
python -m src.main --config "C:\path\to\your\validations.xlsx" --output "C:\path\to\output\report.csv"
```

### Option 5: Verbose Logging

```bash
python -m src.main --config examples\validation_template.xlsx --verbose
```

### Option 6: Different Sheet Name

If your Excel file has validations in a different sheet (default is "Validations"):

```bash
python -m src.main --config examples\validation_template.xlsx --sheet "MyValidations"
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

In your Excel file (vertical layout):

```
Field Name                    | Validation 1
------------------------------|---------------------------
Validation Name               | Daily Order Count
Validation_id                 | VAL001
Source Type                   | SQLServer
Source Host Name              | p8054
Source Port                   | 3085
Source Database Name          | OrderDB
Source Schema Name            | dbo
Source Table Name             | Orders
Source Filter                 | order_date = '2024-01-15'
Target Type                   | Snowflake
Target Host Name              | snowflake-prod
Target Database Name          | ANALYTICS
Target Schema Name            | PUBLIC
Target Table Name             | ORDERS
Target Filter                 | ORDER_DATE = '2024-01-15'
Rule Type                     | COUNT_STAR
Threshold Type                | EXACT
Threshold Value               | 0
```

Requires `.env.p8054` and `.env.snowflake-prod` files with credentials.

### Example 2: Sum Validation with Percentage Threshold

```
Field Name                    | Validation 2
------------------------------|---------------------------
Validation Name               | Total Sales Amount
Validation_id                 | VAL002
Source Type                   | Oracle
Source Host Name              | oracle-dwh
Source Database Name          | SALES_DB
Source Schema Name            | SALES
Source Table Name             | TRANSACTIONS
Source Column Name            | AMOUNT
Target Type                   | Snowflake
Target Host Name              | snowflake-prod
Target Table Name             | TRANSACTIONS
Target Column Name            | AMOUNT
Rule Type                     | SUM
Threshold Type                | PERCENTAGE
Threshold Value               | 0.01
```

### Example 3: Custom Expression

```
Field Name                    | Validation 3
------------------------------|---------------------------
Validation Name               | Weighted Revenue
Validation_id                 | VAL003
Source Type                   | SQLServer
Source Host Name              | p8054
Source Table Name             | Sales
Source Column Expression      | SUM(Price * Quantity * Discount)
Target Host Name              | snowflake-prod
Target Table Name             | Sales_Summary
Target Column Expression      | SUM(Price * Quantity * Discount)
Rule Type                     | CUSTOM
Threshold Type                | PERCENTAGE
Threshold Value               | 0.02
```

## Project Structure

```
data-validation-solution/
├── src/
│   ├── main.py                   # CLI entry point
│   ├── config_parser.py          # Excel parser
│   ├── env_manager.py            # Host-specific credential manager
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
├── .env.example-sqlserver        # SQL Server credential template
├── .env.example-oracle           # Oracle credential template
├── .env.example-netezza          # Netezza credential template
├── .env.example-snowflake        # Snowflake credential template
├── requirements.txt
├── create_excel_template.py      # Script to generate Excel template
├── run_validation.bat            # Windows batch runner
├── README.md
├── CREDENTIALS_GUIDE.md          # Detailed credentials setup guide
└── CODE_WALKTHROUGH.md           # Code documentation
```

## Troubleshooting

### Python Not Found

Install Python 3.8+ from [python.org](https://www.python.org/downloads/) and ensure it's in your PATH.

### Database Driver Issues

**SQL Server:**
- Install ODBC Driver 17 or 18 for SQL Server
- Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Oracle:**
- Install Oracle ODBC Driver (part of Oracle Instant Client)
- Download Oracle Instant Client with ODBC: https://www.oracle.com/database/technologies/instant-client.html
- After installing, configure the ODBC driver name in connections.yaml (e.g., `{Oracle in OraClient12Home1}`)
- Common driver names: `{Oracle in instantclient_19_8}`, `{Oracle in OraClient19Home1}`

**Netezza:**
- `nzpy` should work out of the box
- For ODBC, install Netezza ODBC drivers

**Snowflake:**
- The `snowflake-connector-python` package is sufficient

### Connection Errors

1. Verify `.env.{hostname}` files exist for each host in your Excel
2. Check database credentials in the `.env` files
3. Verify network connectivity to database servers
4. Ensure firewall allows connections to database ports
5. Check [CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md) for troubleshooting

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
