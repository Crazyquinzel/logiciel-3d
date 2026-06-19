#!/bin/bash
cd "$(dirname "$0")"
echo "Etui briquet - Personnalisation"
command -v python3 >/dev/null 2>&1 || { echo "Installe Python 3 depuis python.org"; read -r -p "Entree pour fermer"; exit 1; }
echo "Installation des dependances (1re fois LONG : build123d ~200 Mo)..."
python3 -m pip install --quiet build123d bd_warehouse trimesh numpy pillow
python3 perso_app.py
