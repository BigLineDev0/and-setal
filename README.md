# Signalement Citoyen

Projet de gestion des signalements citoyens.

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/BigLineDev0/and-setal.git
cd and-setal

git checkout develop
git pull origin develop

python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```
# 2. Configurer les variables d'environnement

- Créer le fichier .env :

```bash
cp .env.example .env
```

- Puis éditer pour renseigner les variables nécessaires au projet `.env` :

# 3. Lancer le serveur Django
python manage.py runserver

- Le backend est disponible sur : http://127.0.0.1:8000/
- Le documentation API est disponible sur : http://127.0.0.1:8000/api/docs