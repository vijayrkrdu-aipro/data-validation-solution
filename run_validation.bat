@echo off
REM Data Validation Solution - Windows Batch Runner
REM This script runs the data validation tool with timestamped output

echo ========================================
echo Data Validation Solution
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Generate timestamp for output file
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%%dt:~12,2%"

REM Set paths
set "CONFIG_FILE=examples\validation_template.xlsx"
set "CONNECTIONS_FILE=config\connections.yaml"
set "OUTPUT_FILE=output\validation_report_%timestamp%.csv"

REM Check if config files exist
if not exist "%CONFIG_FILE%" (
    echo ERROR: Validation config file not found: %CONFIG_FILE%
    echo Please create the Excel configuration file first
    pause
    exit /b 1
)

if not exist "%CONNECTIONS_FILE%" (
    echo ERROR: Connections config file not found: %CONNECTIONS_FILE%
    echo Please create the connections.yaml file first
    echo You can copy from config\connections_template.yaml
    pause
    exit /b 1
)

echo Running validation...
echo Config: %CONFIG_FILE%
echo Connections: %CONNECTIONS_FILE%
echo Output: %OUTPUT_FILE%
echo.

REM Run the validation
python -m src.main --config "%CONFIG_FILE%" --connections "%CONNECTIONS_FILE%" --output "%OUTPUT_FILE%"

REM Check exit code
if errorlevel 1 (
    echo.
    echo ========================================
    echo Validation completed with errors
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Validation completed successfully
    echo ========================================
)

echo.
echo Press any key to exit...
pause >nul
