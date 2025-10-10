# Générateur de Feuilles de Présence

## Description
Ce programme génère automatiquement des feuilles de présence en PDF pour des formations. Il crée un document personnalisé pour chaque académicien avec toutes les informations nécessaires.

## Prérequis
- Python 3.x
- pip (gestionnaire de paquets Python)

## Installation

### Première utilisation

1. Les dépendances sont déjà installées dans l'environnement virtuel `venv/`

2. Si vous devez réinstaller :
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

### Méthode 1 : Script de lancement (recommandé)
```bash
./lancer.sh
```

### Méthode 2 : Manuelle
```bash
source venv/bin/activate
python generateur_feuilles.py
```

### Utilisation avec Streamlit (interface web)
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```
Ouvrez ensuite le lien local affiché par Streamlit (généralement `http://localhost:8501`). Remplissez le formulaire :
- Société cliente
- Académiciens (séparés par des virgules)
- Durée de la formation
- Lieu de formation
- Nom de la formation

Cliquez sur « Générer les feuilles » puis « Télécharger le ZIP » pour obtenir l’archive contenant tous les PDF.

## Fonctionnement

Le programme vous demandera :
1. **Nom de la société cliente** : Le nom de l'entreprise
2. **Nom des académiciens** : Les noms des stagiaires (séparés par des virgules)
3. **Durée de la formation** : Par exemple "8 jours"
4. **Lieu de formation** : L'adresse ou le lieu
5. **Nom de la formation** : Le titre de la formation

Le programme générera automatiquement un PDF pour chaque académicien dans le dossier `feuilles_présence/`.

## Structure du PDF généré

Chaque feuille de présence contient :
- En-tête avec le nom de l'entreprise (Laurent-Serre-Développement)
- Informations sur la formation (société, académicien, durée, lieu, formation)
- Tableau de présence avec 16 lignes (8 jours complets)
- Colonnes : Date, Niveau, Durée, Horaires, Signature Stagiaire, Signature Formateur

## Dossiers

- `feuilles_présence/` : Contient tous les PDFs générés
- `venv/` : Environnement virtuel Python (ignoré par git)

## Dépendances

- `reportlab` : Bibliothèque pour la génération de PDF
- `streamlit` : Interface web simple pour formulaires et téléchargements

## Support

Pour toute question ou problème, contactez Laurent Serre Développement.

