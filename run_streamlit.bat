@echo off
REM Script to run Streamlit app for testing the API (Windows)

echo 🚀 Starting Streamlit UI for Azure GenAI API Tester
echo.

REM Check if API_URL is set, otherwise use default
if "%API_URL%"=="" (
    set API_URL=http://localhost:8000
    echo Using default API URL: %API_URL%
    echo Set API_URL environment variable to use a different URL
) else (
    echo Using API URL: %API_URL%
)

echo.
echo 📝 Make sure your FastAPI server is running on %API_URL%
echo    Start it with: uvicorn api.main:app --reload
echo.
echo 🌐 Opening Streamlit app...
echo.

REM Run Streamlit
streamlit run streamlit_app.py

pause

