# Objectifs pédagogiques — Days 71–80

## Objectifs généraux

À l'issue de ce séminaire, l'étudiant doit être capable de :
- Écrire du code Rust idiomatique et sûr
- Comprendre et appliquer les concepts d'ownership, borrowing, et lifetimes
- Développer une application web full-stack en Rust
- Intégrer une base de données relationnelle
- Déployer une application Rust conteneurisée

---

## Days 71-75 : Fondamentaux Rust (Bootstrap)

### Day 71 : Introduction à Rust
**Concepts**
- Installation de Rust (rustup, cargo)
- Syntaxe de base : variables, types primitifs, fonctions
- Ownership basics : move semantics
- Pattern matching simple

**Exercices**
- Hello World et premiers programmes
- Manipulation de variables et types
- Fonctions avec ownership

**Acquis**
- [ ] Configurer l'environnement Rust
- [ ] Comprendre le système d'ownership de base
- [ ] Écrire des fonctions simples

### Day 72 : Ownership, Borrowing & Lifetimes
**Concepts**
- References (&T, &mut T)
- Borrowing rules (une seule référence mutable OU plusieurs immutables)
- Lifetimes explicites
- Slices

**Exercices**
- Manipulation de références
- Gestion de la durée de vie des données
- Travail avec des slices

**Acquis**
- [ ] Maîtriser les règles de borrowing
- [ ] Comprendre les lifetimes
- [ ] Utiliser les références correctement

### Day 73 : Structs, Enums & Traits
**Concepts**
- Définition de structs et méthodes
- Enums et pattern matching avancé
- Traits (interfaces) et implémentations
- Generics de base

**Exercices**
- Créer des structures de données
- Implémenter des traits standards (Display, Debug, Clone)
- Pattern matching complexe

**Acquis**
- [ ] Structurer du code avec structs et enums
- [ ] Implémenter et utiliser des traits
- [ ] Comprendre le polymorphisme en Rust

### Day 74 : Error Handling & Collections
**Concepts**
- Result<T, E> et Option<T>
- Opérateur ? pour la propagation d'erreurs
- Vec, HashMap, HashSet
- Iterators et closures

**Exercices**
- Gestion d'erreurs robuste
- Manipulation de collections
- Programmation fonctionnelle avec iterators

**Acquis**
- [ ] Gérer les erreurs proprement
- [ ] Utiliser les collections standard
- [ ] Chaîner des opérations avec iterators

### Day 75 : Modules, Crates & Testing
**Concepts**
- Organisation du code en modules
- Utilisation de crates externes (Cargo.toml)
- Tests unitaires avec #[test]
- Documentation avec ///

**Exercices**
- Structurer un projet multi-modules
- Intégrer des dépendances externes
- Écrire des tests complets

**Acquis**
- [ ] Organiser un projet Rust proprement
- [ ] Gérer les dépendances avec Cargo
- [ ] Tester du code Rust

---

## Days 76-80 : Application Full-Stack (Hello World)

### Day 76 : Setup Backend & Routing
**Concepts**
- Framework web (Actix-web/Rocket)
- Routing et handlers
- Middleware et état partagé
- Gestion JSON (serde)

**Tâches**
- Initialiser le projet backend
- Créer les routes API
- Implémenter les handlers de base
- Parser/serializer JSON

**Acquis**
- [ ] Configurer un serveur web Rust
- [ ] Créer une API REST
- [ ] Manipuler JSON

### Day 77 : Database Integration
**Concepts**
- ORM Rust (Diesel/SeaORM)
- Migrations de base de données
- Requêtes SQL type-safe
- Connection pooling

**Tâches**
- Connecter PostgreSQL
- Créer le schéma (migrations)
- Implémenter les modèles
- CRUD operations

**Acquis**
- [ ] Intégrer PostgreSQL avec Rust
- [ ] Écrire des requêtes type-safe
- [ ] Gérer les migrations

### Day 78 : Frontend avec WASM
**Concepts**
- Compilation Rust vers WebAssembly
- Framework frontend (Yew/Leptos)
- Composants et props
- Communication avec le backend

**Tâches**
- Setup du projet frontend
- Créer les composants
- Appels API (fetch)
- State management

**Acquis**
- [ ] Compiler Rust en WASM
- [ ] Créer une UI interactive
- [ ] Intégrer frontend/backend

### Day 79 : Tests & Documentation
**Concepts**
- Tests d'intégration
- Mocking (Mockito)
- Code coverage
- Documentation technique

**Tâches**
- Tests unitaires backend
- Tests d'intégration API
- Tests frontend
- Documenter l'architecture

**Acquis**
- [ ] Écrire des tests complets
- [ ] Atteindre une bonne couverture
- [ ] Documenter le projet

### Day 80 : Containerization & Deployment
**Concepts**
- Multi-stage Docker builds
- docker-compose pour orchestration
- Optimisation de la taille d'image
- Configuration de production

**Tâches**
- Dockerfile pour backend
- Dockerfile pour frontend
- docker-compose.yml complet
- Déploiement et tests

**Acquis**
- [ ] Conteneuriser l'application
- [ ] Orchestrer les services
- [ ] Déployer en production

---

## Critères d'évaluation

### Bootstrap (40%)
- Tous les exercices complétés et fonctionnels
- Code Rust idiomatique (utilisation correcte de l'ownership)
- Tests passants
- Documentation des fonctions principales

### Hello World Full-Stack (60%)
- API REST fonctionnelle avec tous les endpoints
- Base de données correctement intégrée
- Frontend opérationnel et responsive
- Tests unitaires et d'intégration passants (>70% coverage)
- Déploiement Docker fonctionnel
- Documentation technique complète (README, architecture)

## Compétences transversales

- **Sécurité** : code memory-safe, pas de data races
- **Performance** : optimisation des requêtes, async/await
- **Maintenabilité** : code modulaire, bien testé, documenté
- **DevOps** : containerization, orchestration, CI/CD ready
