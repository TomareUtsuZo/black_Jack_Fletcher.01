@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the tests with all arguments passed to this script
python run_tests.py %*

REM Deactivate virtual environment
deactivate 