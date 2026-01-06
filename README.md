# Générateur de Feuilles de Présence

## Description
Application Python permettant de générer automatiquement des feuilles de présence en PDF pour chaque académicien d’une formation. Le projet propose à la fois un script en ligne de commande et une interface web (Streamlit).

## Prérequis
- Python 3.x installé sur la machine
- `pip` disponible dans le PATH

### Utilisation de la version Terminal (CLI)

1. Ouvrez un terminal dans le dossier du projet.
2. Lancez le script directement :
   ```bash ./lancer.sh
   ```
   *Note : Si vous tapez `bash` puis `Entrée`, vous ouvrez une session interactive qui affiche un avertissement de macOS. Tapez directement `./lancer.sh` pour éviter cela.*
4. Répondez aux questions posées en console. Les PDF sont créés dans `feuilles_présence/`.

## Installation détaillée
Les dépendances sont pré-installées dans le dossier `venv/`. Si vous devez repartir de zéro :

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
> Pour réactiver ultérieurement l’environnement : `source venv/bin/activate` (macOS/Linux) ou `venv\Scripts\activate` (Windows).

## Utilisation
### Script `lancer.sh` (recommandé)
Automatise l’activation du virtualenv, l’installation des dépendances et l’exécution du générateur :
```bash
./lancer.sh
```

### Mode manuel (sans script)
```bash
source venv/bin/activate          # ou venv\Scripts\activate sur Windows
python generateur_feuilles.py
```
Saisissez ensuite :
1. Nom de la société cliente
2. Liste des académiciens (séparés par des virgules)
3. Durée de la formation
4. Lieu de formation
5. Nom de la formation

### Interface web (Streamlit)
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```
Ouvrez le lien local affiché (par défaut `http://localhost:8501`), remplissez le formulaire et cliquez sur **Générer les feuilles** puis **Télécharger le ZIP** pour récupérer toutes les feuilles.

## Résultat des feuilles PDF
Chaque fichier suit la structure suivante :
- En-tête : « Laurent-Serre-Développement »
- Informations générales : société, académicien, durée, lieu, formation
- Tableau de présence avec 16 lignes (8 demi-journées) et les colonnes : Date, Niveau, Durée (h), Horaires, Signature Stagiaire, Signature Formateur

Les fichiers sont déposés dans le dossier `feuilles_présence/`.

## Dépannage
- **Permission denied sur `lancer.sh`** : exécutez `chmod +x lancer.sh`.
- **Module introuvable (`reportlab`, `streamlit`)** : activez le virtualenv (`source venv/bin/activate`) puis `pip install -r requirements.txt`.
- **PDF manquants** : vérifiez que le dossier `feuilles_présence/` existe et que les noms d’académiciens ne contiennent pas uniquement des espaces.

## Structure du projet
- `generateur_feuilles.py` : script principal en ligne de commande.
- `streamlit_app.py` : interface web pour générer et télécharger un ZIP de feuilles.
- `lancer.sh` : script d’aide pour lancer l’outil côté terminal.
- `feuilles_présence/` : répertoire de sortie des PDF.
- `venv/` : environnement virtuel Python prêt à l’emploi.

## Support
Pour toute question ou problème, contactez Laurent Serre Développement.
