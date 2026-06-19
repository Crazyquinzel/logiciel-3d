@echo off
title Etui briquet - Personnalisation
cd /d "%~dp0"
echo ============================================================
echo   Etui briquet flamme - Personnalisation
echo ============================================================
echo.
python --version >nul 2>&1 || (echo [ERREUR] Installe Python depuis python.org ^(coche "Add to PATH"^). & pause & exit /b)
echo Installation des dependances (la 1re fois c'est LONG : build123d ~200 Mo)...
python -m pip install --quiet --disable-pip-version-check build123d bd_warehouse trimesh numpy pillow
echo Lancement...
python "%~dp0perso_app.py"
