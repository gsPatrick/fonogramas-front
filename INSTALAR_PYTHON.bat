@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo       INSTALADOR AUTOMATICO DE PYTHON (3.11)
echo ========================================================
echo.

:: Verificar permises de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR.
    echo.
    echo Clique com o botao direito no arquivo e escolha:
    echo "Executar como administrador"
    echo.
    pause
    exit
)

echo [1/3] Verificando instalacoes antigas...
:: Tenta desinstalar verses antigas via WMIC (pode demorar)
echo Tentando limpar versoes conflitantes (Isso pode falhar se nao houver nenhuma, ignore erros)...
wmic product where "name like 'Python%%'" call uninstall /nointeractive >nul 2>&1

echo.
echo [2/3] Baixando Python 3.11...
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
set "INSTALLER_NAME=python_installer.exe"

powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER_NAME%'"
if not exist "%INSTALLER_NAME%" (
    echo [ERRO] Falha no download. Verifique sua internet.
    pause
    exit
)
echo Download concluido.
echo.

echo [3/3] Instalando (Isso pode levar alguns minutos)...
echo Por favor aguarde e NAO feche esta janela...
:: /quiet = sem interface
:: InstallAllUsers=1 = para todos os usuarios
:: PrependPath=1 = adicionar ao PATH (CRUCIAL)
"%INSTALLER_NAME%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %errorlevel% neq 0 (
    echo [ERRO] Falha na instalacao. Codigo de erro: %errorlevel%
    pause
) else (
    echo.
    echo ========================================================
    echo           PYTHON INSTALADO COM SUCESSO!
    echo ========================================================
    echo.
    echo Agora voce pode rodar o script 'REINSTALAR_DO_ZERO.bat'.
    echo.
)

:: Limpeza
del "%INSTALLER_NAME%" >nul 2>&1

pause
