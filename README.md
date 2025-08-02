# Backend Django - Déchets KO

API REST Django pour l'application de gestion des déchets.

## Installation

1. **Créer un environnement virtuel :**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

3. **Configuration :**
```bash
cp .env.example .env
# Modifier les variables dans .env si nécessaire
```

4. **Migrations de base de données :**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **supprimer les données :**
```bash
python manage.py clean_data
```

6. **Peupler avec des données de test et créer un superutilisateur :**
```bash
python manage.py populate_data
```

7. **Lancer le serveur :**
```bash
python manage.py runserver
```

## API Endpoints

### Authentification
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `GET /api/auth/profile/` - Profil utilisateur
- `POST /api/auth/register/` - Inscription

### Gestion des déchets
- `GET /api/teams/` - Liste des équipes
- `GET /api/collection-points/` - Points de collecte
- `GET /api/trucks/` - Camions
- `GET /api/reports/` - Signalements
- `GET /api/schedules/` - Plannings
- `GET /api/incidents/` - Incidents
- `GET /api/statistics/` - Statistiques
- `GET /api/users/` - utilisateurs

### Actions spéciales
- `PATCH /api/collection-points/{id}/update_status/` - Changer statut point
- `PATCH /api/trucks/{id}/update_status/` - Changer statut camion
- `PATCH /api/trucks/{id}/update_location/` - Mettre à jour position
- `PATCH /api/reports/{id}/assign/` - Assigner signalement
- `PATCH /api/reports/{id}/resolve/` - Résoudre signalement
- `PATCH /api/incidents/{id}/resolve/` - Résoudre incident

## Comptes de test

Après `python manage.py populate_data` :


## Administration

Interface admin Django : http://localhost:8000/admin/

## Structure du projet

```
dko-back/
├── dechets_ko/          # Configuration Django
├── accounts/            # Gestion utilisateurs
├── waste_management/    # Gestion des déchets
├── requirements.txt     # Dépendances
└── manage.py           # Script Django
```
