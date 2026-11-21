@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -c "import PyQt5.QtWidgets, reportlab" >nul 2>&1
if errorlevel 1 goto empacotado

".venv\Scripts\python.exe" -m estrutural
if errorlevel 1 pause
exit /b

:empacotado
if exist "dist\MS Estruturas\MS Estruturas.exe" (
    cmd.exe /d /c exit 0
    start "" "%~dp0dist\MS Estruturas\MS Estruturas.exe"
    if errorlevel 1 pause
    exit /b
)

echo Ambiente Python indisponivel e executavel empacotado ausente.
echo Siga as instrucoes de instalacao no README.md.
pause
exit /b 1
