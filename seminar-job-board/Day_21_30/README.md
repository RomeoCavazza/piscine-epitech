# Days 21–30 — Notes

Ce projet couvre 10 jours de développement d'une plateforme de recrutement complète, intégrant toutes les compétences acquises lors des séminaires précédents.

- Consignes: [consignes_day21-30.pdf](consignes_day21-30.pdf)
- Solutions: [solutions_day21_30/](solutions_day21_30/)

## Objectifs

### Semaine 1 (Days 21-25) : Backend & Base de données
- **Day 21** : Conception de la base de données et schéma relationnel
- **Day 22** : Développement de l'API REST (authentification, utilisateurs)
- **Day 23** : Gestion des offres d'emploi et candidatures
- **Day 24** : Interface d'administration et modération
- **Day 25** : Tests et optimisation des performances

### Semaine 2 (Days 26-30) : Frontend & Intégration
- **Day 26** : Interface utilisateur et design responsive
- **Day 27** : Intégration JavaScript et API calls
- **Day 28** : Fonctionnalités avancées (recherche, filtres)
- **Day 29** : Tests d'intégration et debugging
- **Day 30** : Déploiement et documentation finale

## 🏗️ Architecture du projet

### Backend (PHP/MySQL)
```
back/
├── api/
│   ├── admin.php      # Endpoints administration
│   ├── applications.php # Gestion candidatures
│   ├── auth.php       # Authentification JWT/sessions
│   ├── config.php     # Configuration base de données
│   ├── jobs.php       # CRUD offres d'emploi
│   ├── recruteur.php  # Interface recruteur
│   └── users.php      # Gestion utilisateurs
└── data/
    └── database.sql   # Schéma complet avec données de test
```

### Frontend (HTML/CSS/JS)
```
front/
├── assets/
│   ├── css/
│   │   ├── admin.css    # Styles interface admin
│   │   ├── profile.css  # Styles profils utilisateurs
│   │   └── styles.css   # Styles principaux
│   └── js/
│       ├── admin.js     # Logique administration
│       ├── app.js       # Application principale
│       └── profile.js   # Gestion profils
└── web/
    ├── admin.html       # Dashboard administrateur
    ├── index.html       # Page d'accueil publique
    ├── login.html       # Connexion utilisateurs
    ├── my-profile.html  # Profil utilisateur connecté
    ├── recruteur.html   # Interface recruteur
    └── signup.html      # Inscription nouveaux utilisateurs
```

## Actions

### 🔐 Authentification & Sécurité
- Inscription avec validation email
- Connexion sécurisée avec sessions
- Gestion des rôles (candidat/recruteur/admin)
- Protection CSRF et validation des données

### 👥 Gestion des utilisateurs
- Profils candidats avec CV et compétences
- Profils recruteurs avec informations entreprise
- Modification des profils
- Système de notifications

### 💼 Gestion des offres
- Création d'offres par les recruteurs
- Recherche et filtrage avancé
- Catégorisation par secteur/métier
- Gestion des statuts (ouverte/fermée/expirée)

### 📝 Système de candidatures
- Application aux offres
- Suivi des candidatures
- Messagerie candidat/recruteur
- Notifications de statut

### ⚙️ Administration
- Dashboard avec statistiques
- Gestion des utilisateurs
- Modération des offres
- Rapports et analytics

## 🛠️ Technologies & Outils

### Backend
- **PHP 8+** : POO, namespaces, exceptions
- **MySQL 8+** : Requêtes complexes, index, contraintes
- **PDO** : Accès sécurisé à la base de données
- **JWT/Sessions** : Authentification et autorisation

### Frontend
- **HTML5** : Sémantique, accessibilité
- **CSS3** : Flexbox, Grid, animations, responsive
- **JavaScript ES6+** : Modules, async/await, fetch API
- **Bootstrap/Tailwind** : Framework CSS (optionnel)

### DevOps & Qualité
- **Git** : Versioning et collaboration
- **Composer** : Gestion des dépendances PHP
- **PHPUnit** : Tests unitaires
- **Docker** : Containerisation (bonus)

## 📚 Notions techniques approfondies

### Base de données
- **Modélisation relationnelle** : Tables, clés étrangères, contraintes
- **Requêtes SQL avancées** : JOINs, sous-requêtes, agrégations
- **Optimisation** : Index, requêtes préparées, cache
- **Sécurité** : Injection SQL, sanitisation

### API REST
- **Architecture REST** : Ressources, méthodes HTTP, codes de statut
- **Format JSON** : Sérialisation, validation
- **Documentation** : OpenAPI/Swagger
- **Versioning** : Gestion des versions d'API

### Sécurité web
- **OWASP Top 10** : Vulnérabilités courantes
- **Validation** : Côté client et serveur
- **Sanitisation** : Protection contre XSS, injection
- **Authentification** : Sessions, tokens, cookies sécurisés

## Leçons

### Techniques
- **Développement full-stack** : Intégration frontend/backend
- **Architecture logicielle** : Patterns MVC, séparation des responsabilités
- **Base de données** : Conception, optimisation, maintenance
- **API design** : Conception d'interfaces robustes

### Méthodologiques
- **Gestion de projet** : Planification, livrables, deadlines
- **Tests** : Unitaires, intégration, end-to-end
- **Documentation** : Code, API, déploiement
- **Debugging** : Outils, techniques, méthodologie

### Professionnelles
- **Travail d'équipe** : Collaboration, code review, communication
- **Standards** : Coding standards, conventions, bonnes pratiques
- **Déploiement** : Production, monitoring, maintenance
- **Évolutivité** : Scalabilité, performance, refactoring

## 📖 Ressources complémentaires

- [Documentation PHP](https://www.php.net/docs.php)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)

## 🚀 Prochaines étapes

Après ce séminaire, les étudiants seront capables de :
- Développer des applications web complètes
- Concevoir et implémenter des APIs REST
- Gérer des bases de données relationnelles
- Intégrer frontend et backend
- Déployer des applications en production
- Collaborer efficacement sur des projets complexes

---

*Ce projet représente l'aboutissement de la formation technique, combinant toutes les compétences acquises dans un contexte professionnel réaliste.*
