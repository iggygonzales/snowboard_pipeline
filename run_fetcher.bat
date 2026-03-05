@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline"
call "C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline\venv\Scripts\activate.bat"
"C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline\venv\Scripts\python.exe" -m ingestion.noaa_fetcher >> "C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline\logs\fetcher.log" 2>&1
cd "C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline\transforms\snow_transforms"
"C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline\transforms\venv\Scripts\dbt.exe" run >> "C:\Users\migue\OneDrive\Documents\NEU Projects\snowboard_pipeline\logs\fetcher.log" 2>&1
