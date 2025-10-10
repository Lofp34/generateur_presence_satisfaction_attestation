#!/bin/bash

# Script de lancement du générateur de feuilles de présence

echo "=========================================="
echo " Générateur de Feuilles de Présence"
echo "=========================================="
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création en cours..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
    echo ""
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer/Mettre à jour les dépendances
echo "📦 Vérification des dépendances..."
pip install -q -r requirements.txt

echo "✅ Prêt à générer les feuilles de présence"
echo ""
echo "=========================================="
echo ""

# Lancer le programme
python generateur_feuilles.py

# Désactiver l'environnement virtuel à la fin
deactivate

