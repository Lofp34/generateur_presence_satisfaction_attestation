#!/bin/bash

# Script de lancement du générateur de feuilles de présence

echo "=========================================="
echo " Générateur de Feuilles de Présence"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

echo "🔧 Préparation de l'environnement virtuel..."

# Vérifier que Python 3 est disponible
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 est requis mais introuvable dans le PATH."
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas encore
if [ ! -d "${VENV_DIR}" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création en cours..."
    python3 -m venv "${VENV_DIR}"
    echo "✅ Environnement virtuel créé"
    echo ""
fi

PYTHON_BIN="${VENV_DIR}/bin/python3"
if [ ! -x "${PYTHON_BIN}" ]; then
    PYTHON_BIN="${VENV_DIR}/bin/python"
fi

if [ ! -x "${PYTHON_BIN}" ]; then
    echo "❌ Impossible de localiser l'interpréteur Python dans ${VENV_DIR}."
    exit 1
fi

# Installer/Mettre à jour les dépendances avec le Python du venv
echo "📦 Vérification des dépendances..."
"${PYTHON_BIN}" -m pip install -q -r "${SCRIPT_DIR}/requirements.txt"

echo "✅ Prêt à générer les feuilles de présence"
echo ""
echo "=========================================="
echo ""

# Lancer le programme avec l'interpréteur du venv
"${PYTHON_BIN}" "${SCRIPT_DIR}/generateur_feuilles.py"
