# Quick Setup Guide

Follow these steps to get the Data Validation Solution up and running.

## Prerequisites

1. **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
2. **Database drivers** (will be installed automatically)
3. **Access credentials** for your databases

## Step-by-Step Setup

### Step 1: Verify Python Installation

Open Command Prompt and verify Python is installed:

```bash
python --version
```

You should see Python 3.8 or higher. If not, install Python and add it to your PATH.

### Step 2: Navigate to Project Directory

```bash
cd C:\Users\conco\Documents\Projects\data-validation-solution
```

### Step 3: Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including database connectors.

### Step 5: Create Environment File

Copy the environment template:

```bash
copy .env.template .env
```

Edit `.env` and add your database credentials:

```
SQLSERVER_USER=actual_username
SQLSERVER_PASS=actual_password
ORACLE_USER=actual_username
ORACLE_PASS=actual_password
# ... etc
```

### Step 6: Configure Connections

Copy the connections template:

```bash
copy config\connections_template.yaml config\connections.yaml
```

Edit `config\connections.yaml` and update with your actual database details:

```yaml
connections:
  sqlserver_prod:
    type: sqlserver
    host: your-server.domain.com
    port: 1433
    database: YourDatabase
    username: ${SQLSERVER_USER}
    password: ${SQLSERVER_PASS}

  # Add more connections as needed...
```

### Step 7: Generate Excel Template

Create the validation template:

```bash
python create_excel_template.py
```

This creates `examples\validation_template.xlsx` with sample validations.

### Step 8: Customize Validations

Open `examples\validation_template.xlsx` in Excel and:

1. Review the sample validations (VAL001 - VAL009)
2. Update them with your actual tables and columns
3. Add new validations as needed
4. Set `enabled = FALSE` for validations you don't want to run

### Step 9: Test Connections

Before running validations, test your database connections:

```bash
python -m src.main --connections config\connections.yaml --test-connections
```

You should see:

```
============================================================
CONNECTION TEST RESULTS
============================================================
✓ sqlserver_prod              PASS
✓ oracle_dwh                  PASS
...
```

If any connections fail, check your credentials and network access.

### Step 10: Run Validations

**Option A: Use the batch file (easiest)**

Double-click `run_validation.bat`

**Option B: Use command line**

```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml
```

### Step 11: Review Results

Check the output CSV file in the `output\` folder. The filename includes a timestamp:

```
output\validation_report_20240115_143022.csv
```

Open it in Excel to review:
- Which validations passed/failed
- Source and target values
- Differences and percentage differences
- Any error messages

## Common Issues

### Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart your command prompt

### Virtual Environment Activation Failed

**Error:** Running scripts is disabled on this system

**Solution:** Run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating the virtual environment again.

### Database Driver Missing

**Error:** `ODBC Driver 17 for SQL Server not found`

**Solution:** Download and install:
- SQL Server: [ODBC Driver 17/18](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Oracle: [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html)

### Connection Failed

**Error:** `Failed to connect to [database]`

**Solution:**
1. Verify credentials in `config\connections.yaml`
2. Check `.env` file has correct values
3. Ensure network access to database server
4. Check firewall settings
5. Verify database port is correct

### Excel File Not Found

**Error:** `Excel file not found: examples\validation_template.xlsx`

**Solution:** Run the template generator:

```bash
python create_excel_template.py
```

## Next Steps

1. **Customize Validations:** Edit the Excel template with your actual validation rules
2. **Schedule Execution:** Use Windows Task Scheduler to run `run_validation.bat` automatically
3. **Monitor Results:** Set up alerts for failed validations
4. **Expand Coverage:** Add more connection types and validation rules

## Need Help?

- Review the main [README.md](README.md) for detailed documentation
- Check the Excel template for examples (VAL001-VAL009)
- Review log output for error details
- Contact your development team for support

## Quick Reference

### Activate Virtual Environment
```bash
venv\Scripts\activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Run Validations
```bash
run_validation.bat
```

### Test Connections Only
```bash
python -m src.main --connections config\connections.yaml --test-connections
```

### Run with Verbose Logging
```bash
python -m src.main --config examples\validation_template.xlsx --connections config\connections.yaml --verbose
```

### Update Excel Template
```bash
python create_excel_template.py
```
