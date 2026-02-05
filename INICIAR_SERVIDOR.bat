@echo off
cd /d "%~dp0"

echo ========================================================
echo           INICIANDO SISTEMA FONOGRAMAS
echo ========================================================
echo.

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo Por favor, execute o arquivo REINSTALAR_DO_ZERO.bat primeiro.
    echo.
    pause
    exit
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Iniciando servidor...
echo Acesse no navegador: http://127.0.0.1:5001
echo.
python app.py

pause
