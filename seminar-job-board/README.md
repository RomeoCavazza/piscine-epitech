# Séminaire Job Board (Days 21–30)

Ce séminaire couvre le développement d'une plateforme de recrutement complète avec base de données, API REST et interface utilisateur. Contrairement aux autres séminaires, il s'agit d'un projet unifié sur 2 semaines avec une seule consigne globale.

## 🎯 Objectif du projet

Développer une **plateforme de recrutement** complète comprenant :
- 🗄️ **Base de données** pour stocker les offres d'emploi
- 🌐 **Interface web** (front-end) avec JavaScript pour afficher les offres et page d'administration
- 🔌 **API REST** (back-end) pour permettre aux utilisateurs de postuler et gérer la DB (admin)

## 📋 Étapes de développement

### Étapes 01-03 : Fondations
- **Step 01** → Création de la base de données SQL (tables pour annonces, entreprises, personnes, candidatures)
- **Step 02** → Page HTML/CSS initiale avec affichage des offres d'emploi
- **Step 03** → Affichage dynamique des détails d'annonce (sans rechargement de page)

### Étapes 04-06 : API et interactions
- **Step 04** → Création de l'API REST avec opérations CRUD et respect des verbes HTTP
- **Step 05** → Système de candidature avec formulaire et sauvegarde en base
- **Step 06** → Mécanisme d'authentification (connexion/inscription)

### Étapes 07-08 : Administration et finalisation
- **Step 07** → Page d'administration pour gérer la base de données (accès admin uniquement)
- **Step 08** → Amélioration du design et finalisation

## 🛠️ Technologies utilisées

**Backend :**
- PHP avec API REST
- MySQL (Railway)
- Authentification JWT

**Frontend :**
- HTML5 sémantique
- CSS3 moderne et responsive
- JavaScript ES6+ (modules)
- API REST avec fetch()

## 📁 Structure du projet

```
seminar-job-board/
├── consignes_day21-30.pdf    # Consignes complètes du projet
├── README.md                 # Ce fichier
└── DAY_21_30/               # Implémentation du projet
    ├── back/                # Backend PHP
    │   ├── api/            # Endpoints API
    │   └── data/           # Schéma SQL
    └── front/              # Frontend
        ├── web/            # Pages HTML
        └── assets/         # CSS + JavaScript
```

## 🚀 Installation et utilisation

Voir le [README détaillé](DAY_21_30/README.md) pour les instructions d'installation et de configuration.

## 🔗 Liens utiles

- [Consignes complètes](consignes_day21-30.pdf)
- [Implémentation détaillée](DAY_21_30/README.md)
- [Code source](DAY_21_30/)
