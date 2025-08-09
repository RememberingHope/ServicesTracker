@echo off
echo ============================================
echo Starting SPED Services Analytics Dashboard
echo ============================================
echo.
echo This will launch the Streamlit dashboard in your browser.
echo Make sure you have run the Services Aggregator first
echo to import data from email.
echo.
echo Press Ctrl+C in this window to stop the dashboard.
echo.
echo Starting dashboard...
echo.

REM Launch Streamlit dashboard
streamlit run Services_Dashboard.py --server.port 8501 --server.headless true

pause