@echo off
echo Activating AnkiQuest development environment...
call venv\Scripts\activate
echo.
echo ✅ Environment activated!
echo.
echo Available commands:
echo   pytest          - Run tests
echo   black .         - Format code
echo   ruff check .    - Lint code
echo.