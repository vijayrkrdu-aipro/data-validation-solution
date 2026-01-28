"""
Script to create Excel validation template with examples.
"""

import pandas as pd
import os

# Define the columns
columns = [
    'validation_id',
    'validation_name',
    'source_connection',
    'source_database',
    'source_schema',
    'source_table',
    'source_column',
    'source_filter',
    'target_connection',
    'target_database',
    'target_schema',
    'target_table',
    'target_column',
    'target_filter',
    'rule_type',
    'custom_expression',
    'threshold_type',
    'threshold_value',
    'enabled'
]

# Create example validations
data = [
    # Example 1: COUNT(*) validation with exact match
    {
        'validation_id': 'VAL001',
        'validation_name': 'Daily Order Count - Exact Match',
        'source_connection': 'sqlserver_prod',
        'source_database': 'OrderDB',
        'source_schema': 'dbo',
        'source_table': 'Orders',
        'source_column': None,
        'source_filter': "order_date >= '2024-01-01' AND order_date < '2024-02-01'",
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'PUBLIC',
        'target_table': 'ORDERS_FACT',
        'target_column': None,
        'target_filter': "ORDER_DATE >= '2024-01-01' AND ORDER_DATE < '2024-02-01'",
        'rule_type': 'COUNT_STAR',
        'custom_expression': None,
        'threshold_type': 'EXACT',
        'threshold_value': 0,
        'enabled': True
    },

    # Example 2: SUM validation with percentage threshold
    {
        'validation_id': 'VAL002',
        'validation_name': 'Total Sales Amount - 1% Tolerance',
        'source_connection': 'oracle_dwh',
        'source_database': None,
        'source_schema': 'SALES',
        'source_table': 'TRANSACTIONS',
        'source_column': 'AMOUNT',
        'source_filter': "TRANSACTION_DATE >= TO_DATE('2024-01-01', 'YYYY-MM-DD')",
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'SALES',
        'target_table': 'TRANSACTIONS',
        'target_column': 'AMOUNT',
        'target_filter': "TRANSACTION_DATE >= '2024-01-01'",
        'rule_type': 'SUM',
        'custom_expression': None,
        'threshold_type': 'PERCENTAGE',
        'threshold_value': 0.01,  # 1%
        'enabled': True
    },

    # Example 3: COUNT(column) validation
    {
        'validation_id': 'VAL003',
        'validation_name': 'Count of Valid Customer IDs',
        'source_connection': 'netezza_analytics',
        'source_database': 'PRODUCTION',
        'source_schema': 'CUSTOMER',
        'source_table': 'CUSTOMER_MASTER',
        'source_column': 'CUSTOMER_ID',
        'source_filter': None,
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'CUSTOMER',
        'target_table': 'CUSTOMER_DIM',
        'target_column': 'CUSTOMER_ID',
        'target_filter': None,
        'rule_type': 'COUNT_COLUMN',
        'custom_expression': None,
        'threshold_type': 'EXACT',
        'threshold_value': 0,
        'enabled': True
    },

    # Example 4: COUNT_DISTINCT validation
    {
        'validation_id': 'VAL004',
        'validation_name': 'Distinct Product Count',
        'source_connection': 'sqlserver_prod',
        'source_database': 'ProductDB',
        'source_schema': 'dbo',
        'source_table': 'Products',
        'source_column': 'ProductID',
        'source_filter': "IsActive = 1",
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'PRODUCT',
        'target_table': 'PRODUCT_DIM',
        'target_column': 'PRODUCT_ID',
        'target_filter': "IS_ACTIVE = TRUE",
        'rule_type': 'COUNT_DISTINCT',
        'custom_expression': None,
        'threshold_type': 'EXACT',
        'threshold_value': 0,
        'enabled': True
    },

    # Example 5: AVG validation with absolute threshold
    {
        'validation_id': 'VAL005',
        'validation_name': 'Average Order Value',
        'source_connection': 'oracle_dwh',
        'source_database': None,
        'source_schema': 'SALES',
        'source_table': 'ORDERS',
        'source_column': 'ORDER_TOTAL',
        'source_filter': None,
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'SALES',
        'target_table': 'ORDERS',
        'target_column': 'ORDER_TOTAL',
        'target_filter': None,
        'rule_type': 'AVG',
        'custom_expression': None,
        'threshold_type': 'ABSOLUTE',
        'threshold_value': 5.0,  # Allow $5 difference
        'enabled': True
    },

    # Example 6: COUNT_NULL validation
    {
        'validation_id': 'VAL006',
        'validation_name': 'Null Email Count',
        'source_connection': 'sqlserver_prod',
        'source_database': 'CustomerDB',
        'source_schema': 'dbo',
        'source_table': 'Customers',
        'source_column': 'Email',
        'source_filter': None,
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'CUSTOMER',
        'target_table': 'CUSTOMERS',
        'target_column': 'EMAIL',
        'target_filter': None,
        'rule_type': 'COUNT_NULL',
        'custom_expression': None,
        'threshold_type': 'EXACT',
        'threshold_value': 0,
        'enabled': True
    },

    # Example 7: CUSTOM expression
    {
        'validation_id': 'VAL007',
        'validation_name': 'Custom Aggregate - Total Revenue by Region',
        'source_connection': 'oracle_dwh',
        'source_database': None,
        'source_schema': 'SALES',
        'source_table': 'REVENUE',
        'source_column': None,
        'source_filter': "REGION = 'WEST'",
        'target_connection': 'snowflake_cloud',
        'target_database': 'ANALYTICS',
        'target_schema': 'SALES',
        'target_table': 'REVENUE_FACT',
        'target_column': None,
        'target_filter': "REGION = 'WEST'",
        'rule_type': 'CUSTOM',
        'custom_expression': "SUM(REVENUE * QUANTITY)",
        'threshold_type': 'PERCENTAGE',
        'threshold_value': 0.02,  # 2%
        'enabled': True
    },

    # Example 8: CSV to Database validation
    {
        'validation_id': 'VAL008',
        'validation_name': 'CSV File Row Count',
        'source_connection': 'csv_source',
        'source_database': None,
        'source_schema': None,
        'source_table': 'data',  # For CSV, this is ignored but required
        'source_column': None,
        'source_filter': None,
        'target_connection': 'sqlserver_prod',
        'target_database': 'StagingDB',
        'target_schema': 'dbo',
        'target_table': 'StagingData',
        'target_column': None,
        'target_filter': None,
        'rule_type': 'COUNT_STAR',
        'custom_expression': None,
        'threshold_type': 'EXACT',
        'threshold_value': 0,
        'enabled': True
    },

    # Example 9: Disabled validation (will be skipped)
    {
        'validation_id': 'VAL009',
        'validation_name': 'DISABLED - Example Validation',
        'source_connection': 'sqlserver_prod',
        'source_database': 'TestDB',
        'source_schema': 'dbo',
        'source_table': 'TestTable',
        'source_column': None,
        'source_filter': None,
        'target_connection': 'snowflake_cloud',
        'target_database': 'TEST',
        'target_schema': 'PUBLIC',
        'target_table': 'TEST_TABLE',
        'target_column': None,
        'target_filter': None,
        'rule_type': 'COUNT_STAR',
        'custom_expression': None,
        'threshold_type': 'EXACT',
        'threshold_value': 0,
        'enabled': False
    }
]

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), 'examples')
os.makedirs(output_dir, exist_ok=True)

# Save to Excel
output_path = os.path.join(output_dir, 'validation_template.xlsx')
df.to_excel(output_path, sheet_name='Validations', index=False)

print(f"Excel template created successfully: {output_path}")
print(f"Total validations: {len(data)}")
print(f"Enabled validations: {sum(1 for v in data if v['enabled'])}")
