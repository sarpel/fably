@echo off

echo Starting Enhanced Fably Web Interface...

REM Check if virtual environment exists
if not exist "..\..\venv\" (
    echo Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call ..\..\venv\Scripts\activate.bat

REM Install/update requirements
pip install -r requirements.txt

REM Launch the enhanced app
echo Launching on http://localhost:7860
python enhanced_app.py

pause
