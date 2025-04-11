@echo off
echo Starting Waleed Smart WooCommerce...
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: Start the application
echo Starting the application...
python app.py

pause 