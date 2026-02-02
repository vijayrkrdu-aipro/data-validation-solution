"""
Script to create Excel validation template with horizontal layout.
Each ROW is one validation, field names are COLUMNS (standard Excel format).

IMPORTANT: The "Source Host Name" and "Target Host Name" fields should contain
SHORT IDENTIFIERS that match your .env file names, NOT full hostnames.

Example: If you have .env.p8054, use "p8054" as the Host Name in Excel.
The actual full hostname and port will be loaded from the .env file.

NOTE: Ports are loaded from .env files only (NOT in Excel).
"""

import pandas as pd
import os

# Column names (horizontal layout - each row is one validation)
# NO PORT FIELDS (ports come from .env files)
columns = [
    'Validation Name',
    'Validation_id',
    'Source Type',
    'Source Host Name',              # SHORT identifier for .env file lookup
    'Source Database Name',
    'Source Schema Name',
    'Source Table Name',
    'Source Column Name',
    'Source Column Expression',
    'Source Filter',
    'Target Type',
    'Target Host Name',              # SHORT identifier for .env file lookup
    'Target Database Name',
    'Target Schema Name',
    'Target Table Name',
    'Target Column Name',
    'Target Column Expression',
    'Target Filter',
    'Rule Type',
    'Threshold Type',
    'Threshold Value'
]

# Example validations (rows)
# Note: Host names are SHORT identifiers matching .env file names
# Port is loaded from .env file automatically
validations = [
    {
        'Validation Name': 'Daily Order Count',
        'Validation_id': 'VAL001',
        'Source Type': 'SQLServer',
        'Source Host Name': 'p8054',                    # matches .env.p8054
        'Source Database Name': 'OrderDB',
        'Source Schema Name': 'dbo',
        'Source Table Name': 'Orders',
        'Source Column Name': '',                        # empty for COUNT_STAR
        'Source Column Expression': '',
        'Source Filter': "order_date >= '2024-01-01'",
        'Target Type': 'Snowflake',
        'Target Host Name': 'snowflake-prod',           # matches .env.snowflake-prod
        'Target Database Name': 'ANALYTICS',
        'Target Schema Name': 'PUBLIC',
        'Target Table Name': 'ORDERS_FACT',
        'Target Column Name': '',
        'Target Column Expression': '',
        'Target Filter': "ORDER_DATE >= '2024-01-01'",
        'Rule Type': 'COUNT_STAR',
        'Threshold Type': 'EXACT',
        'Threshold Value': 0
    },
    {
        'Validation Name': 'Total Sales Amount',
        'Validation_id': 'VAL002',
        'Source Type': 'Oracle',
        'Source Host Name': 'oracle-dwh',               # matches .env.oracle-dwh
        'Source Database Name': 'SALES_DB',
        'Source Schema Name': 'SALES',
        'Source Table Name': 'TRANSACTIONS',
        'Source Column Name': 'AMOUNT',
        'Source Column Expression': '',
        'Source Filter': "TRANSACTION_DATE >= TO_DATE('2024-01-01', 'YYYY-MM-DD')",
        'Target Type': 'Snowflake',
        'Target Host Name': 'snowflake-prod',
        'Target Database Name': 'ANALYTICS',
        'Target Schema Name': 'SALES',
        'Target Table Name': 'TRANSACTIONS',
        'Target Column Name': 'AMOUNT',
        'Target Column Expression': '',
        'Target Filter': "TRANSACTION_DATE >= '2024-01-01'",
        'Rule Type': 'SUM',
        'Threshold Type': 'PERCENTAGE',
        'Threshold Value': 0.01  # 1% tolerance
    },
    {
        'Validation Name': 'Distinct Product Count',
        'Validation_id': 'VAL003',
        'Source Type': 'Netezza',
        'Source Host Name': 'nz-db-ut',                 # matches .env.nz-db-ut
        'Source Database Name': 'cidpr',
        'Source Schema Name': 'stgprd',
        'Source Table Name': 'PRODUCT_MASTER',
        'Source Column Name': 'PRODUCT_ID',
        'Source Column Expression': '',
        'Source Filter': 'IS_ACTIVE = TRUE',
        'Target Type': 'SQLServer',
        'Target Host Name': 'p8054',
        'Target Database Name': 'BDM Archive',
        'Target Schema Name': 'dbo',
        'Target Table Name': 'PRODUCT_DIM',
        'Target Column Name': 'PRODUCT_ID',
        'Target Column Expression': '',
        'Target Filter': 'IS_ACTIVE = 1',
        'Rule Type': 'COUNT_DISTINCT',
        'Threshold Type': 'EXACT',
        'Threshold Value': 0
    },
    {
        'Validation Name': 'Average Order Value',
        'Validation_id': 'VAL004',
        'Source Type': 'SQLServer',
        'Source Host Name': 'p8054',
        'Source Database Name': 'OrderDB',
        'Source Schema Name': 'dbo',
        'Source Table Name': 'Orders',
        'Source Column Name': 'ORDER_TOTAL',
        'Source Column Expression': '',
        'Source Filter': '',
        'Target Type': 'Netezza',
        'Target Host Name': 'nz-db-ut',
        'Target Database Name': 'cidpr',
        'Target Schema Name': 'stgprd',
        'Target Table Name': 'ORDERS',
        'Target Column Name': 'ORDER_TOTAL',
        'Target Column Expression': '',
        'Target Filter': '',
        'Rule Type': 'AVG',
        'Threshold Type': 'ABSOLUTE',
        'Threshold Value': 5.0  # Allow $5 difference
    },
    {
        'Validation Name': 'Custom Revenue Calculation',
        'Validation_id': 'VAL005',
        'Source Type': 'SQLServer',
        'Source Host Name': 'p8054',
        'Source Database Name': 'SalesDB',
        'Source Schema Name': 'dbo',
        'Source Table Name': 'Sales',
        'Source Column Name': '',
        'Source Column Expression': 'Price * Quantity',  # Custom expression
        'Source Filter': "REGION = 'WEST'",
        'Target Type': 'Netezza',
        'Target Host Name': 'nz-db-ut',
        'Target Database Name': 'cidpr',
        'Target Schema Name': 'stgprd',
        'Target Table Name': 'Sales_Fact',
        'Target Column Name': '',
        'Target Column Expression': 'Price * Quantity',
        'Target Filter': "REGION = 'WEST'",
        'Rule Type': 'SUM',
        'Threshold Type': 'PERCENTAGE',
        'Threshold Value': 0.02  # 2% tolerance
    }
]

# Create DataFrame with horizontal layout (standard Excel format)
# Columns are field names, rows are validations
df = pd.DataFrame(validations, columns=columns)

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), 'examples')
os.makedirs(output_dir, exist_ok=True)

# Save to Excel
output_path = os.path.join(output_dir, 'validation_template.xlsx')

# Write with standard headers (first row = column names)
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Validations', index=False)

print(f"[OK] Excel template created successfully: {output_path}")
print(f"[OK] Total validations: {len(validations)}")
print(f"\nLayout: Horizontal (standard Excel format)")
print(f"  - Row 1: Column headers (field names)")
print(f"  - Row 2+: Each row is one validation")
print(f"\nNOTE: Port numbers are NOT in the Excel template.")
print(f"      They will be loaded automatically from .env files.")
print(f"\n" + "="*60)
print("IMPORTANT: Host-Specific .env Files Required")
print("="*60)
print("\nBased on the template, you need to create these .env files:")
print("  - .env.p8054           (SQL Server)")
print("  - .env.oracle-dwh      (Oracle)")
print("  - .env.nz-db-ut        (Netezza)")
print("  - .env.snowflake-prod  (Snowflake)")
print(f"\nSee CREDENTIALS_GUIDE.md for detailed setup instructions.")
print(f"Use the .env.example-* files as templates.")
