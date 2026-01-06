# Attestations automatiques

Application minimale pour charger une convention PDF (format unique) et generer automatiquement une attestation PDF.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer le serveur

```bash
uvicorn app.main:app --reload
```

Ouvrir `http://127.0.0.1:8000` et deposer une convention PDF. Si plusieurs participants sont detectes, un fichier `attestations.zip` est telecharge.

## Utiliser la ligne de commande

```bash
python3 -m app.cli Convention_SLS_202511191_Mon_coach_brico_2025-1.pdf --output certificats_output/attestation.pdf
```

## Configuration

- `config/convention_patterns.json` : regles d'extraction (labels et regex).
- `config/attestation_layout.json` : positions des champs dans le template `certificat_de_realisation_281225.pdf`.

Si un champ obligatoire est manquant, l'application retourne une erreur explicite. Ajuste les patterns/labels si besoin.
