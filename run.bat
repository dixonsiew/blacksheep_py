call .venv\Scripts\activate.bat
@REM python server.py
uvicorn server:app --reload --port 8000