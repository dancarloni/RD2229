#!/usr/bin/env bash
set -euo pipefail

# Script di setup locale per RD2229
# Uso: ./run-local.sh [TARGET_DIR]

TARGET_DIR=${1:-"RD2229-local"}

echo "Clonazione repository in: ${TARGET_DIR}"
git clone https://github.com/dancarloni/RD2229.git "${TARGET_DIR}"

cd "${TARGET_DIR}"

echo "Creazione virtualenv .venv"
python3 -m venv .venv
echo "Attiva con: source .venv/bin/activate"

echo "Installazione dipendenze (se presente requirements.txt)"
source .venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

echo "Setup completato. Esempi utili:
- Entrare nella cartella: cd ${TARGET_DIR}
- Attivare venv: source .venv/bin/activate
- Eseguire test: pytest -q
- Aprire in VS Code: code ."

echo -e "Se vuoi lavorare completamente offline e rimuovere l'origin remoto:
  git remote remove origin
" 

echo "Fine."
