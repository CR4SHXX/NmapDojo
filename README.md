# 🗺️ Nmap Dojo - Formation IA sur Nmap

Nmap Dojo est une application de formation interactive et alimentée par l'IA qui vous enseigne les commandes **nmap** à travers des scénarios de cybersécurité réalistes. Utilisant **Google Gemini** comme moteur d'IA, l'application génère des missions, valide vos commandes et fournit des explications détaillées.

## 🎯 Caractéristiques

- 🤖 **Génération de missions alimentées par l'IA** - Scénarios uniques et réalistes générés par Gemini
- 🎓 **Système d'apprentissage progressif** - Progression par niveaux et points d'expérience (XP)
- 💡 **Système d'indices intelligent** - Obtenez des indices sans spoiler les réponses
- ✅ **Validation de commandes en temps réel** - L'IA valide vos commandes nmap
- 🎮 **Interface moderne** - Thème sombre "hacker" avec terminal simulé
- 📊 **Suivi de la progression** - Sauvegarde automatique de votre progression

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

1. **Python 3.8+** installé sur votre système
2. **Une clé API Google Gemini** (gratuite)
3. **Une connexion internet** (pour l'API Gemini)

## 🚀 Installation et Lancement

### Étape 1 : Vérifier Python

```powershell
python --version
```

Vous devriez voir `Python 3.8` ou une version supérieure. Si Python n'est pas installé, téléchargez-le depuis [python.org](https://www.python.org/downloads/).

### Étape 2 : Obtenir une clé API Google Gemini

1. Allez sur [ai.google.dev](https://ai.google.dev/)
2. Cliquez sur **"Get API Key"** (Obtenir une clé API)
3. Créez un nouveau projet ou utilisez un projet existant
4. Générez une nouvelle clé API
5. Copiez la clé (vous en aurez besoin dans l'étape suivante)

### Étape 3 : Cloner ou télécharger le projet

```powershell
# Naviguer vers le dossier désiré
cd "C:\Users\votreNom\Desktop"

# Cloner le référentiel
git clone https://github.com/CR4SHXX/NmapDojo.git
cd NmapDojo
```

Ou téléchargez le fichier ZIP et décompressez-le.

### Étape 4 : Créer un environnement virtuel (optionnel mais recommandé)

```powershell
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Sur Windows :
.venv\Scripts\Activate.ps1

# Si vous avez une erreur de permission, exécutez :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Étape 5 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

Cela installera :
- **flet** - Framework UI moderne
- **google-generativeai** - SDK Google Gemini

### Étape 6 : Configurer la clé API

Ouvrez `config/settings.py` et remplacez la ligne :

```python
GEMINI_API_KEY = ""
```

Par :

```python
GEMINI_API_KEY = "votre_clé_api_ici"
```

*Remplacez `votre_clé_api_ici` par la clé API que vous avez copiée à l'étape 2.*

### Étape 7 : Lancer l'application

```powershell
python main.py
```

Une fenêtre de l'application Nmap Dojo s'ouvrira automatiquement.

## 🎮 Comment utiliser l'application

### Interface

- **Panneau gauche** (70%) : Terminal simulé Nmap
- **Panneau droit** (30%) : Contrôle de mission

### Commandes disponibles

```
nmap [flags] [cible]  - Exécuter une commande nmap
help                  - Afficher l'aide
clear                 - Effacer le terminal
status                - Afficher votre progression
```

### Système de progression

- 📈 **Missions** : Complétez les missions pour gagner XP
- 🎖️ **Niveaux** : 5 niveaux au total
  - **Niveaux 1-3** : Missions fondamentales
  - **Niveaux 4-5** : Missions avancées
- 💡 **Indices** : Vous avez 2 indices par mission
- ⭐ **Récompenses XP** :
  - 100 XP : Première tentative réussie
  - 50 XP : Avec 1 indice utilisé
  - 25 XP : Avec 2 indices utilisés

## 🔧 Dépannage

### Erreur : "ModuleNotFoundError: No module named 'flet'"

**Solution** : Réinstallez les dépendances

```powershell
pip install --upgrade -r requirements.txt
```

### Erreur : "API key was reported as leaked"

**Solution** : Votre clé API doit être changée. Générez une nouvelle clé sur [ai.google.dev](https://ai.google.dev/) et mettez-à-jour `config/settings.py`

### L'application ne se lance pas

**Solution** : Vérifiez que vous utilisez Python 3.8 ou supérieur

```powershell
python --version
```

### Impossible de générer une mission

- Vérifiez que votre clé API est valide
- Vérifiez votre connexion internet
- Les quotas API gratuits limités peuvent affecter l'utilisation excessive

## 📁 Structure du projet

```
NmapDojo/
├── main.py                  # Point d'entrée
├── requirements.txt         # Dépendances Python
├── README.md               # Documentation (ce fichier)
├── config/                 # Configuration
│   ├── constants.py        # Constantes (couleurs, XP, etc.)
│   └── settings.py         # Clé API et chemins
├── core/                   # Logique principale
│   ├── ai_service.py       # Intégration Google Gemini
│   ├── mission_generator.py # Génération de missions
│   ├── command_validator.py # Validation des commandes
│   └── progress_manager.py  # Gestion de la progression
├── ui/                     # Interface utilisateur
│   ├── app.py             # Application principale
│   └── components/        # Composants UI
├── models/                # Types et modèles de données
└── utils/                 # Utilitaires (logging, etc.)
```

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Suggérer des améliorations
- Soumettre des pull requests

## 📝 Licence

Ce projet est sous licence MIT. Consultez `LICENSE` pour plus de détails.

## 🔗 Ressources utiles

- [Documentation Nmap](https://nmap.org/book/man.html)
- [Google Gemini API](https://ai.google.dev/)
- [Flet Documentation](https://flet.dev/)
- [Python Official](https://www.python.org/)

## ❓ Questions ou problèmes ?

Consultez le fichier `dojo.log` pour voir les journaux d'erreurs détaillés.

---

**Bonne chance dans votre apprentissage de Nmap ! 🚀**

*Créé avec ❤️ pour la formation en cybersécurité*
