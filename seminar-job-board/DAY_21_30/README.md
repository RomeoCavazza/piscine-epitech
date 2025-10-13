# Job Board – T-WEB-501-PAR_16

Plateforme de recrutement en PHP/MySQL avec interface responsive.

**Groupe** : Jason · Philippe · Roméo  
**Stack** : HTML · CSS · JavaScript · PHP · MySQL (Railway)

---

## 🚀 Installation rapide

### 1. Cloner le projet
```bash
git clone [URL_DU_REPO]
cd seminar-job-board
```

### 2. Configuration de la base de données

#### Credentials Railway (à copier-coller) :
```
Host: shortline.proxy.rlwy.net
Port: 49721
User: root
Password: hWEscXrpOTfwjFQOBIdwZETXXyFLybmO
Database: jobboard
```

#### Connexion MySQL directe :
```bash
mysql --ssl --ssl-verify-server-cert=OFF \
  -h shortline.proxy.rlwy.net \
  -P 49721 \
  -u root -p \
  railway
# Password: hWEscXrpOTfwjFQOBIdwZETXXyFLybmO
```

#### Import du schéma :
```bash
mysql --ssl --ssl-verify-server-cert=OFF \
  -h shortline.proxy.rlwy.net \
  -P 49721 \
  -u root -p \
  jobboard < back/data/jobboard.sql
# Password: hWEscXrpOTfwjFQOBIdwZETXXyFLybmO
```

### 3. Configuration des variables d'environnement

```bash
# Créer le fichier .env
cp back/.env.example back/.env

# Éditer avec tes credentials
nano back/.env
```

**Contenu du fichier `.env`** :
```env
DB_HOST=shortline.proxy.rlwy.net
DB_USER=root
DB_PASS=hWEscXrpOTfwjFQOBIdwZETXXyFLybmO
DB_NAME=jobboard
DB_PORT=49721
```

### 4. Lancement du serveur

```bash
# Démarrer le serveur PHP
php -S localhost:8001

# Accéder à l'application
open http://localhost:8001/front/web/index.html
```

---

## 📁 Structure du projet

```
seminar-job-board/
├── back/
│   ├── api/              # APIs PHP (auth, users, jobs, applications)
│   │   ├── config.php    # Configuration DB + CORS
│   │   ├── auth.php      # Authentification
│   │   ├── users.php     # Gestion utilisateurs
│   │   ├── jobs.php      # Offres d'emploi
│   │   └── applications.php
│   ├── data/
│   │   └── jobboard.sql  # Schéma de base
│   └── .env             # Variables d'environnement (IGNORÉ par git)
└── front/
    ├── web/             # Pages HTML
    │   ├── index.html   # Page principale
    │   └── profile.html # Profil utilisateur
    └── assets/          # CSS + JavaScript modulaire
        ├── css/
        │   └── styles.css
        └── js/
            ├── config.js    # Configuration API
            ├── auth.js      # Authentification
            ├── jobs.js      # Gestion offres
            ├── profile.js   # Profil utilisateur
            └── ui.js        # Interface utilisateur
```