@echo off
echo ===================================================
echo      ESP32 AIoT Dashboard - Startup Script
echo ===================================================
echo.

echo [1/3] Starting Backend API (api.py) ...
start "" cmd.exe /k "title Backend API && python api.py"

echo [2/3] Starting Streamlit Dashboard (app.py) ...
start "" cmd.exe /k "title Streamlit Dashboard && python -m streamlit run app.py"

echo Waiting 3 seconds for backend initialization...
timeout /t 3 /nobreak > nul

echo [3/3] Starting Serial Bridge (serial_to_api.py) ...
start "" cmd.exe /k "title Serial Bridge && set PYTHONIOENCODING=utf-8&& set PYTHONUNBUFFERED=1&& python serial_to_api.py"

echo.
echo ===================================================
echo All services started in separate windows!
echo Please do not close the 3 black command windows.
echo Dashboard URL: http://localhost:8501
echo ===================================================
pause > nul
