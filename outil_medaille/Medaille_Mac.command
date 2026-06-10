#!/bin/bash
# Double-clic sur Mac. (Au 1er lancement : clic droit > Ouvrir, pour autoriser.)
cd "$(dirname "$0")"

echo "============================================"
echo "  Medaille SUPER PAPA - lancement..."
echo "============================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERREUR] Python 3 n'est pas installe."
    echo "Installe-le depuis https://www.python.org/downloads/"
    read -r -p "Appuie sur Entree pour fermer."
    exit 1
fi

python3 -m pip install --quiet pillow
python3 medaille_app.py
