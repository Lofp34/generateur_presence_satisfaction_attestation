# 📋 Générateur de Questionnaires de Satisfaction

Application Python pour générer automatiquement des questionnaires de satisfaction personnalisés au format PDF pour vos formations.

---

## 🎯 À quoi ça sert ?

Cette application génère des **questionnaires de satisfaction PDF personnalisés** pour chaque participant d'une formation. Chaque questionnaire contient :

- Les informations du participant (nom, prénom)
- Les détails de la formation (société, parcours, centre, dates)
- 4 sections d'évaluation avec grilles de notation
- Des zones de commentaires libres
- Optionnellement, votre logo en en-tête

---

## 🚀 Comment lancer l'application ?

### **Option 1 : Interface Web Streamlit** (Recommandé ✅)

C'est la méthode la plus simple et visuelle !

```bash
streamlit run streamlit_questionnaire.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

### **Option 2 : Ligne de commande**

Pour une utilisation en mode terminal :

```bash
python generateur_questionnaires.py
```

Vous serez guidé par des questions interactives.

---

## 📝 Utilisation de l'interface Streamlit

### 1. **Remplir le formulaire**

Une fois l'application lancée, remplissez les champs suivants :

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Société cliente** | Nom de l'entreprise | `ACME Corporation` |
| **Parcours de formation** | Intitulé de la formation | `Techniques de vente avancées` |
| **Centre d'entraînement** | Lieu de formation | `Centre de formation Paris` |
| **Date de début** | Date de début | `01/12/2025` |
| **Date de fin** | Date de fin | `15/12/2025` |
| **Participants** | Liste des participants (un par ligne ou séparés par des virgules) | `Alice Dupont`<br>`Bob Martin`<br>`Charlie Durand` |
| **Logo** (optionnel) | Fichier image (PNG, JPG, JPEG) | Votre logo d'entreprise |

### 2. **Générer les questionnaires**

- Cliquez sur le bouton **"Générer les questionnaires"**
- L'application crée un PDF pour chaque participant
- Un fichier ZIP est automatiquement créé avec tous les PDFs

### 3. **Télécharger les résultats**

- Cliquez sur **"Télécharger le ZIP"**
- Le fichier `questionnaires_satisfaction.zip` contient tous les questionnaires générés

---

## 📂 Structure des fichiers générés

Les PDFs sont sauvegardés dans :
```
generateur_questionnaire/questionnaires_satisfaction/
```

Nom des fichiers : `Questionnaire_<nom>_<formation>.pdf`

Exemple : `Questionnaire_dupont_techniques_de_vente_avancees.pdf`

---

## 🛠️ Installation et prérequis

### **Prérequis**

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### **Installation des dépendances**

Si c'est la première fois que vous lancez l'application ou après une longue période :

```bash
pip install -r requirements.txt
```

Les bibliothèques principales utilisées :
- **streamlit** : Interface web interactive
- **reportlab** : Génération de PDF

---

## 📋 Contenu du questionnaire généré

Chaque questionnaire PDF contient **4 sections d'évaluation** :

### **1ère partie : L'organisation de la formation**
- Accueil
- Respect des horaires
- Durée
- Logistique, prestations techniques

### **2ème partie : Le formateur**
- La maîtrise du contenu
- La qualité de l'écoute
- La clarté du message

### **3ème partie : L'animation**
- Les supports
- Les échanges
- La méthode pédagogique
- La durée et le rythme

### **4ème partie : Les objectifs de la formation**
- Objectifs perçus
- Adhésion aux objectifs
- Atteinte des objectifs

### **Conclusion**
- Satisfaction globale
- Note sur 10
- Suggestions

Chaque critère peut être évalué avec : `++`, `+`, `-`, `--`

---

## 💡 Astuces et conseils

### **Format des participants**

Vous pouvez saisir les participants de plusieurs façons :

```
Alice Dupont
Bob Martin
Charlie Durand
```

Ou avec des virgules :

```
Alice Dupont, Bob Martin, Charlie Durand
```

### **Logo**

- Formats acceptés : PNG, JPG, JPEG
- Le logo sera redimensionné automatiquement (max 4cm x 4cm)
- Il apparaîtra en haut de chaque questionnaire

### **Noms de fichiers**

Les noms de fichiers sont automatiquement nettoyés :
- Accents supprimés
- Espaces remplacés par des underscores
- Caractères spéciaux supprimés

---

## 🔧 Utilisation en ligne de commande (avancé)

### **Commande de base**

```bash
python generateur_questionnaires.py
```

### **Avec options**

```bash
python generateur_questionnaires.py --output-dir ./mes_questionnaires --logo ./mon_logo.png
```

**Options disponibles :**

| Option | Description | Défaut |
|--------|-------------|--------|
| `--output-dir` | Répertoire de sortie des PDFs | `generateur_questionnaire/questionnaires_satisfaction` |
| `--logo` | Chemin vers le logo | Aucun |

---

## 📞 Informations de contact

**SARL LAURENT SERRE**  
259 rue de la Lavande  
34130 Mauguio  
📞 06 14 94 40 60  
✉️ ls@laurentserre.com

---

## 🐛 Dépannage

### **Problème : "streamlit: command not found"**

**Solution :**
```bash
pip install streamlit
```

### **Problème : "No module named 'reportlab'"**

**Solution :**
```bash
pip install reportlab
```

### **Problème : L'application ne génère aucun PDF**

**Vérifications :**
- Tous les champs obligatoires sont remplis ?
- Au moins un participant est saisi ?
- Vous avez les droits d'écriture dans le dossier de sortie ?

### **Problème : Le logo n'apparaît pas**

**Vérifications :**
- Le fichier est bien au format PNG, JPG ou JPEG ?
- Le fichier n'est pas corrompu ?
- La taille du fichier est raisonnable (< 5 Mo) ?

---

## 📚 Structure du projet

```
generateur_questionnaire/
├── streamlit_questionnaire.py      # Interface web Streamlit
├── generateur_questionnaires.py    # Interface ligne de commande
├── questionnaire_core.py           # Logique de génération PDF
├── questionnaires_satisfaction/    # Dossier de sortie des PDFs
├── tests/                          # Tests unitaires
│   └── test_questionnaire_core.py
└── README.md                       # Ce fichier
```

---

## ✅ Checklist de démarrage rapide

1. ✅ Ouvrir un terminal dans le dossier du projet
2. ✅ Installer les dépendances : `pip install -r requirements.txt`
3. ✅ Lancer l'application : `streamlit run streamlit_questionnaire.py`
4. ✅ Remplir le formulaire dans le navigateur
5. ✅ Cliquer sur "Générer les questionnaires"
6. ✅ Télécharger le ZIP avec tous les PDFs

---

**Bon courage avec vos formations ! 🎓**
