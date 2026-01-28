@echo off
REM Quick Setup Script for Data Validation Solution
REM This script automates the initial setup process

echo ========================================
echo Data Validation Solution - Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo WARNING: Failed to activate virtual environment
    echo You may need to run: Set-ExecutionPolicy RemoteSigned
)
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

echo Step 4: Creating configuration files...

REM Create .env file if it doesn't exist
if exist .env (
    echo .env file already exists, skipping...
) else (
    copy .env.template .env
    echo Created .env file - PLEASE EDIT THIS FILE WITH YOUR CREDENTIALS
)

REM Create connections.yaml if it doesn't exist
if exist config\connections.yaml (
    echo connections.yaml already exists, skipping...
) else (
    copy config\connections_template.yaml config\connections.yaml
    echo Created config\connections.yaml - PLEASE EDIT THIS FILE WITH YOUR DATABASE DETAILS
)
echo.

echo Step 5: Generating Excel validation template...
python create_excel_template.py
if errorlevel 1 (
    echo ERROR: Failed to generate Excel template
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Edit .env file with your database credentials
echo 2. Edit config\connections.yaml with your database connection details
echo 3. Edit examples\validation_template.xlsx with your validation rules
echo 4. Test connections: python -m src.main --connections config\connections.yaml --test-connections
echo 5. Run validations: run_validation.bat
echo.
echo For detailed instructions, see SETUP.md
echo.
pause
