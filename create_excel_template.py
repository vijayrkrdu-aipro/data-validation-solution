"""
Script to create Excel validation template with vertical layout.
Each validation is a column, field names are in rows.
"""

import pandas as pd
import os

# Field names (rows)
fields = [
    'Validation Name',
    'Validation_id',
    'Source Type',
    'Source Host Name',
    'Source Port',
    'Source Database Name',
    'Source Schema Name',
    'Source Table Name',
    'Source Column Name',
    'Source Column Expression',
    'Source Filter',
    'Target Type',
    'Target Host Name',
    'Target Port',
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

# Example validations (columns)
validation1 = [
    'Daily Order Count',                    # Validation Name
    'VAL001',                               # Validation_id
    'SQLServer',                            # Source Type
    'sqlserver.example.com',                # Source Host Name
    1433,                                   # Source Port
    'OrderDB',                              # Source Database Name
    'dbo',                                  # Source Schema Name
    'Orders',                               # Source Table Name
    '',                                     # Source Column Name (empty for COUNT_STAR)
    '',                                     # Source Column Expression
    "order_date >= '2024-01-01'",          # Source Filter
    'Snowflake',                            # Target Type
    'xy12345.us-east-1.snowflakecomputing.com',  # Target Host Name
    443,                                    # Target Port
    'ANALYTICS',                            # Target Database Name
    'PUBLIC',                               # Target Schema Name
    'ORDERS_FACT',                          # Target Table Name
    '',                                     # Target Column Name
    '',                                     # Target Column Expression
    "ORDER_DATE >= '2024-01-01'",          # Target Filter
    'COUNT_STAR',                           # Rule Type
    'EXACT',                                # Threshold Type
    0                                       # Threshold Value
]

validation2 = [
    'Total Sales Amount',
    'VAL002',
    'Oracle',
    'oracle.example.com',
    1521,
    'SALES_DB',
    'SALES',
    'TRANSACTIONS',
    'AMOUNT',
    '',
    'TRANSACTION_DATE >= TO_DATE(\'2024-01-01\', \'YYYY-MM-DD\')',
    'Snowflake',
    'xy12345.us-east-1.snowflakecomputing.com',
    443,
    'ANALYTICS',
    'SALES',
    'TRANSACTIONS',
    'AMOUNT',
    '',
    "TRANSACTION_DATE >= '2024-01-01'",
    'SUM',
    'PERCENTAGE',
    0.01  # 1% tolerance
]

validation3 = [
    'Distinct Product Count',
    'VAL003',
    'Netezza',
    'nz-db-ut',
    5480,
    'PRODUCTION',
    'PRODUCT',
    'PRODUCT_MASTER',
    'PRODUCT_ID',
    '',
    'IS_ACTIVE = TRUE',
    'SQLServer',
    'p8054',
    3085,
    'BDM Archive',
    'dbo',
    'PRODUCT_DIM',
    'PRODUCT_ID',
    '',
    'IS_ACTIVE = 1',
    'COUNT_DISTINCT',
    'EXACT',
    0
]

validation4 = [
    'Average Order Value',
    'VAL004',
    'SQLServer',
    'p8054',
    3085,
    'OrderDB',
    'dbo',
    'Orders',
    'ORDER_TOTAL',
    '',
    '',
    'Snowflake',
    'xy12345.us-east-1.snowflakecomputing.com',
    443,
    'ANALYTICS',
    'SALES',
    'ORDERS',
    'ORDER_TOTAL',
    '',
    '',
    'AVG',
    'ABSOLUTE',
    5.0  # Allow $5 difference
]

validation5 = [
    'Custom Revenue Calculation',
    'VAL005',
    'SQLServer',
    'p8054',
    3085,
    'SalesDB',
    'dbo',
    'Sales',
    '',
    'Price * Quantity',  # Custom source expression
    "REGION = 'WEST'",
    'Netezza',
    'nz-db-ut',
    5480,
    'cidpr',
    'stgprd',
    'Sales_Fact',
    '',
    'Price * Quantity',  # Custom target expression
    "REGION = 'WEST'",
    'SUM',
    'PERCENTAGE',
    0.02  # 2% tolerance
]

# Create DataFrame with vertical layout
# First column is field names, subsequent columns are validations
data = {
    'Field': fields,
    'Validation 1': validation1,
    'Validation 2': validation2,
    'Validation 3': validation3,
    'Validation 4': validation4,
    'Validation 5': validation5
}

df = pd.DataFrame(data)

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), 'examples')
os.makedirs(output_dir, exist_ok=True)

# Save to Excel
output_path = os.path.join(output_dir, 'validation_template.xlsx')

# Write without headers (first column becomes the row labels)
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Validations', index=False, header=False)

print(f"Excel template created successfully: {output_path}")
print(f"Total validations: 5")
print(f"\nLayout: Vertical (rows are fields, columns are validations)")
print(f"Each validation is in a separate column")
