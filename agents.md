# Agents du projet

Ce projet expose plusieurs « agents » (points d’entrée) permettant de générer les feuilles de présence selon le contexte d’utilisation. Utilisez la section correspondant à votre scénario.

## Agent terminal : `lancer.sh`
- **Rôle** : automatise l’activation du virtualenv, la vérification des dépendances et l’exécution du script principal.
- **Quand l’utiliser** : usage local ponctuel ou récurrent depuis un terminal macOS/Linux.
- **Commande** :
  ```bash
  ./lancer.sh
  ```
  > Rendez-le exécutable une fois avec `chmod +x lancer.sh`.

## Agent CLI direct : `generateur_feuilles.py`
- **Rôle** : script Python interactif posant les questions en console et générant les PDF.
- **Quand l’utiliser** : intégration dans une automatisation existante ou exécution sur un poste sans Bash.
- **Commande type** :
  ```bash
  source venv/bin/activate          # venv\Scripts\activate sur Windows
  python generateur_feuilles.py
  ```

## Agent web : `streamlit_app.py`
- **Rôle** : interface graphique simple accessible via navigateur pour saisir les informations et télécharger un ZIP.
- **Quand l’utiliser** : démonstrations, collecte d’informations à distance, accompagnement utilisateur.
- **Commande** :
  ```bash
  source venv/bin/activate
  streamlit run streamlit_app.py
  ```
  Une fois lancée, ouvrez le lien proposé (généralement `http://localhost:8501`) et utilisez le formulaire.

## Bonnes pratiques
- Toujours activer l’environnement virtuel avant d’utiliser un agent Python (`source venv/bin/activate`).
- Vérifier que le dossier `feuilles_présence/` est accessible en lecture/écriture pour permettre la création des PDF.
- Personnaliser les agents en conservant la fonction `create_presence_sheet` comme point central de génération.

## Ajouter un nouvel agent
1. Importez la fonction `create_presence_sheet` depuis `generateur_feuilles.py`.
2. Collectez les données nécessaires (société, académiciens, durée, lieu, formation).
3. Parcourez la liste des académiciens et appelez `create_presence_sheet` pour chacun.
4. Documentez la nouvelle méthode dans ce fichier afin de garder une vision à jour des points d’entrée disponibles.
