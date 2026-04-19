@echo off
echo Starting Corporate Smart Messenger...
cd /d "%~dp0"
python -m streamlit run frontend/app.py
pause
