@echo off
title Medaille SUPER PAPA
cd /d "%~dp0"

echo ============================================
echo   Medaille SUPER PAPA - lancement...
echo ============================================
echo.

REM Verifie que Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Installe-le depuis https://www.python.org/downloads/
    echo et coche "Add Python to PATH" pendant l'installation.
    echo.
    pause
    exit /b
)

REM Installe Pillow si necessaire (silencieux)
python -m pip install --quiet --disable-pip-version-check pillow

REM Lance l'application (fenetre)
python "%~dp0medaille_app.py"
