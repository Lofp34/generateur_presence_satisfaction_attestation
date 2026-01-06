# Spécification technique — Générateur de questionnaires de satisfaction

## 1. Contexte et objectif
Créer une application dérivée du générateur de feuilles de présence permettant de produire des questionnaires de satisfaction personnalisés pour des formations. L’outil doit proposer une expérience identique côté ligne de commande et via une interface web, tout en restant extensible (nouvelles questions, formats additionnels).

## 2. Livrables
- Script Python (CLI) : `generateur_questionnaires.py`.
- Application Streamlit : `streamlit_questionnaire.py`.
- Module commun : `questionnaire_core.py` (logique métier).
- Gabarit de questionnaire d’exemple (JSON ou YAML) fourni par l’utilisateur.
- Dossier de sortie contenant les PDF générés (`questionnaires_satisfaction/`).
- Tests unitaires pour le module métier.

## 3. Cas d’usage cibles
1. Un formateur veut générer un questionnaire papier personnalisé par formation.
2. Une équipe souhaite produire plusieurs questionnaires pour différents groupes et exporter tous les PDF d’un coup.
3. Un utilisateur final désire rapidement lancer le processus via le navigateur sans manipuler la console.

## 4. Entrées & paramètres
- **Métadonnées formation** : société cliente, intitulé formation, dates, lieu, animateur.
- **Participants** : liste de noms (séparés par virgules côté CLI, liste multiligne côté UI).
- **Gabarit questionnaire** (fournit les questions et l’organisation en sections) :
  ```jsonc
  {
    "title": "Questionnaire de satisfaction",
    "sections": [
      {
        "name": "Organisation",
        "questions": [
          {"type": "likert", "label": "Qualité de l’organisation générale", "scale": 5},
          {"type": "text", "label": "Suggestions pour améliorer l’organisation"}
        ]
      }
    ]
  }
  ```
  - Champs requis : `title`, `sections[].name`, `sections[].questions[]`.
  - Types de questions pris en charge : `likert` (échelle 1..N), `checkbox`, `radio`, `text`, `textarea`.
- **Options** (facultatif) : logo entreprise, texte d’introduction, texte de conclusion, langue.

## 5. Sorties attendues
- Un PDF par participant structuré ainsi :
  1. En-tête (logo, société, formation, participant, date).
  2. Introduction (texte libre).
  3. Sections de questions : tableau ou zone dédiée selon le type.
  4. Zone de commentaires libres (optionnelle).
  5. Pied de page avec pagination et données de contact.
- Zip export (Streamlit) regroupant tous les PDF générés.
- Journal minimal en console ou UI (succès/erreurs).

## 6. Fonctionnalités principales
- **CLI** :
  - Invite les champs formation + liste participants.
  - Lit le gabarit via chemin de fichier (par défaut `questionnaire_template.json`).
  - Génère les PDF individuellement, affiche un récapitulatif en console.
- **Interface Streamlit** :
  - Formulaire avec les mêmes champs.
  - Upload du gabarit (fichier JSON/YAML) ou utilisation du modèle par défaut.
  - Prévisualisation d’une page (optionnel si faisable rapidement).
  - Bouton “Générer” + “Télécharger le ZIP”.
- **Gestion des templates** :
  - Chargement JSON/YAML (utiliser `pyyaml` en option).
  - Validation structurée (champ manquant ⇒ erreur claire).
- **Personnalisation PDF** :
  - Typographie cohérente (ReportLab).
  - Rendu adapté selon question type :
    - `likert` : table avec colonnes numérotées, cases vides pour cocher.
    - `checkbox` / `radio` : cases vides + libellés.
    - `text` / `textarea` : zone encadrée pour réponse manuscrite.
  - Respect des marges A4 + possibilité multi-pages.

## 7. Architecture recommandée
```
project_root/
│
├─ questionnaire_core.py      # Fonctions noyau (chargement template, génération PDF)
├─ generateur_questionnaires.py
├─ streamlit_questionnaire.py
├─ templates/
│   └─ questionnaire_template.json
├─ questionnaires_satisfaction/  # sortie PDF
└─ tests/
    └─ test_questionnaire_core.py
```

- `questionnaire_core.py`
  - `load_template(path: str) -> QuestionnaireTemplate`
  - `render_questionnaire(data: QuestionnaireData, template: QuestionnaireTemplate, output_dir: str) -> Path`
  - `QuestionnaireTemplate`, `QuestionDefinition` (dataclasses).
- `generateur_questionnaires.py`
  - Parsing CLI (`argparse`), collecte inputs, appels à `render_questionnaire`.
  - Gestion erreurs (`try/except` + messages utilisateurs).
- `streamlit_questionnaire.py`
  - UI Streamlit, upload template, spinner, Zip en mémoire (`io.BytesIO` + `zipfile`).
- Commons : constantes (marges, styles), utilitaires (génération nom de fichier sécurisé).

## 8. Technologies & dépendances
- Python 3.10+ recommandé.
- `reportlab` pour PDF.
- `streamlit` pour UI web.
- `pyyaml` (optionnel) pour support YAML.
- `dataclasses`, `typing` (stdlib).

## 9. Gestion des erreurs & validations
- Template invalide : affichage des champs manquants / types erronés.
- Liste participants vide : blocage avec message.
- Dossier de sortie inaccessible : proposer alternative ou création automatique.
- Logging minimal (module `logging`) pour traçabilité.

## 10. Tests
- Tests unitaires du module core :
  - Chargement template valide/ invalide.
  - Génération PDF (tester que le fichier existe et taille > 0).
  - Rendu des différents types de questions.
- Tests manuels :
  - CLI : flux complet.
  - Streamlit : génération + téléchargement ZIP.

## 11. Roadmap d’implémentation
1. Définir format définitif du template (basé sur l’exemple fourni).
2. Implémenter `questionnaire_core.py` (charge + rendu PDF).
3. Ajouter script CLI.
4. Ajouter app Streamlit.
5. Mettre en place tests automatisés.
6. Documenter dans README (nouvelle section “Questionnaire de satisfaction”).

## 12. Extension futures
- Export CSV des réponses (si saisie numérique planifiée).
- Support multilingue complet (strings externalisées).
- Génération de formulaires interactifs (PDF AcroForm).
- Intégration stockage cloud (upload ZIP directement).

