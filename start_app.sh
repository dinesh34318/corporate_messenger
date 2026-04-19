#!/bin/bash
echo "Starting Corporate Smart Messenger..."
cd "$(dirname "$0")"
python -m streamlit run frontend/app.py
