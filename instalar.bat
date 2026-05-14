@echo off
:: ─────────────────────────────────────────────────────
::  PoP Monitor — Instalador automático (Windows)
::  Uso: duplo clique em instalar.bat
:: ─────────────────────────────────────────────────────

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║         PoP Monitor — Instalacao automatica          ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python nao encontrado.
    echo   Baixe em: https://python.org/downloads
    echo   Marque "Add Python to PATH" durante a instalacao!
    pause
    exit /b 1
)
echo OK Python encontrado.

:: Cria o venv
echo Criando ambiente virtual...
python -m venv .venv

:: Ativa e instala
echo Instalando dependencias...
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo OK Dependencias instaladas.

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║           PoP Monitor — Instalado!                   ║
echo ║  Acesse:  http://localhost:5050                      ║
echo ║  Pressione Ctrl+C para encerrar                      ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Abre o navegador e inicia a API
start http://localhost:5050
python pop_monitor_api.py
pause
