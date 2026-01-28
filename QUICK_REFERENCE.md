# Quick Reference Card

## Common Commands

### Setup
```bash
setup.bat                    # Run initial setup (one time)
```

### Run Validations
```bash
run_validation.bat           # Run all enabled validations
```

### Test Connections
```bash
python -m src.main --connections config\connections.yaml --test-connections
```

### Custom Output
```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml --output my_report.csv
```

### Verbose Mode
```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml --verbose
```

## Rule Types

| Rule Type | Description | Requires Column |
|-----------|-------------|-----------------|
| COUNT_STAR | COUNT(*) | No |
| COUNT_COLUMN | COUNT(column) | Yes |
| SUM | SUM(column) | Yes |
| AVG | AVG(column) | Yes |
| MIN | MIN(column) | Yes |
| MAX | MAX(column) | Yes |
| COUNT_DISTINCT | COUNT(DISTINCT column) | Yes |
| COUNT_NULL | Count NULL values | Yes |
| COUNT_NOT_NULL | Count non-NULL values | Yes |
| CUSTOM | Custom SQL expression | No (use custom_expression) |

## Threshold Types

| Type | Description | Example Value |
|------|-------------|---------------|
| EXACT | Values must match exactly | 0 |
| PERCENTAGE | Allow % difference | 0.01 (for 1%) |
| ABSOLUTE | Allow absolute difference | 100 |

## Database Types

| Type | Driver | Default Port |
|------|--------|--------------|
| sqlserver | pyodbc | 1433 |
| oracle | cx_Oracle | 1521 |
| netezza | nzpy | 5480 |
| snowflake | snowflake-connector | N/A |
| csv | pandas | N/A |

## Excel Column Quick Reference

**Required Columns:**
- validation_id
- validation_name
- source_connection
- source_table
- target_connection
- target_table
- rule_type
- threshold_type
- threshold_value

**Optional Columns:**
- source_database, source_schema, source_column, source_filter
- target_database, target_schema, target_column, target_filter
- custom_expression
- enabled

## Output CSV Columns

- validation_id, validation_name, status
- source_value, target_value
- difference, percentage_diff
- source_details, target_details
- rule_type, threshold_type, threshold_value
- execution_timestamp, error_message

## Status Values

- **PASS** - Validation succeeded
- **FAIL** - Values don't match within threshold
- **ERROR** - Connection or query error

## File Locations

```
config\connections.yaml       # Database connections
examples\validation_template.xlsx  # Validation rules
output\*.csv                 # Results
.env                        # Credentials (create from .env.template)
```

## Environment Variables

Referenced in connections.yaml using `${VAR_NAME}`:

```
${SQLSERVER_USER}
${SQLSERVER_PASS}
${ORACLE_USER}
${ORACLE_PASS}
${NZ_USER}
${NZ_PASS}
${SNOW_USER}
${SNOW_PASS}
```

## Filter Examples

### SQL Server
```
order_date >= '2024-01-01' AND status = 'ACTIVE'
```

### Oracle
```
TRANSACTION_DATE >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
```

### Snowflake
```
ORDER_DATE >= '2024-01-01' AND REGION = 'WEST'
```

## Custom Expression Examples

```sql
SUM(Price * Quantity)
SUM(CASE WHEN Status = 'ACTIVE' THEN Amount ELSE 0 END)
COUNT(DISTINCT CASE WHEN Age >= 18 THEN CustomerID END)
```

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Python not found | Install Python, add to PATH |
| Driver not found | Install database ODBC drivers |
| Connection failed | Check credentials, network, firewall |
| Excel not found | Run `python create_excel_template.py` |
| Permission denied | Run as Administrator |

## Support

- Full Documentation: [README.md](README.md)
- Setup Guide: [SETUP.md](SETUP.md)
- Excel Template: `examples\validation_template.xlsx`
