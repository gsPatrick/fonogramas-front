@echo off
echo ========================================================
echo       PROCESSO DE REINSTALACAO LIMPA DO SISTEMA
echo ========================================================
echo.
echo Pressione qualquer tecla para INICIAR...
pause >nul

echo.
echo [1/5] Parando processos Python...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
echo OK.
echo.

echo [2/5] Removendo instalacao antiga...
if exist "venv" (
    rmdir /s /q "venv"
    echo Pasta venv removida.
) else (
    echo Pasta venv nao existia.
)

echo Limpando caches...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo OK.
echo.

echo [3/5] Backup do banco de dados...
if exist "instance\fonogramas.db" (
    if not exist "instance\backups" mkdir "instance\backups"
    copy "instance\fonogramas.db" "instance\backups\fonogramas_backup_anterior.db" /Y >nul
    echo Backup salvo em: instance\backups\fonogramas_backup_anterior.db
) else (
    echo Nenhum banco de dados para salvar.
)
echo.

echo [4/5] Criando ambiente virtual (pode demorar)...
python -m venv venv
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao criar ambiente virtual!
    echo Verifique se o Python esta instalado.
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit
)
echo Ambiente criado.
echo.

echo [5/5] Instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias!
    echo Tente rodar novamente como administrador ou verifique a internet.
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit
)
echo Dependencias instaladas.
echo.

echo ========================================================
echo           REINSTALACAO CONCLUIDA!
echo ========================================================
echo.
echo Pressione qualquer tecla para INICIAR O SISTEMA...
pause >nul

echo Iniciando servidor...
python app.py
pause
