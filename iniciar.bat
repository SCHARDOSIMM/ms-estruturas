@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Ambiente ausente. Siga as instrucoes de instalacao no README.md.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m estrutural
if errorlevel 1 pause
