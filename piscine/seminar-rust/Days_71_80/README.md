# Days 71–80 — Notes

## Vue d'ensemble

Séminaire intensif de 10 jours consacré à l'apprentissage de Rust et au développement d'une application web full-stack moderne.

## Objectifs du séminaire

### Semaine 1 (Days 71-75) : Fondamentaux Rust
- Maîtriser la syntaxe de base de Rust
- Comprendre le système d'ownership et de borrowing
- Manipuler les types, traits, et pattern matching
- Gérer les erreurs avec Result et Option
- Bootstrap : exercices progressifs sur les concepts clés

### Semaine 2 (Days 76-80) : Application Full-Stack
- Développer une API REST avec un framework web Rust
- Intégrer PostgreSQL avec un ORM Rust
- Créer un frontend moderne (compilation WASM)
- Conteneuriser l'application avec Docker
- Implémenter tests unitaires et d'intégration

## Structure du projet

```
Days_71_80/
├── README.md (ce fichier)
├── OBJECTIVES.md (objectifs pédagogiques détaillés)
├── consignes_days71_80.pdf (sujet complet du projet)
└── solutions_days71_80/
    ├── bootstrap/ (exercices d'introduction)
    └── hello-world/ (projet full-stack complet)
```

## Technologies utilisées

- **Rust** : langage de programmation système
- **Cargo** : gestionnaire de dépendances et build system
- **Backend** : Actix-web ou Rocket
- **Frontend** : Yew, Leptos, ou Dioxus (compilation WASM)
- **Database** : PostgreSQL + Diesel/SeaORM
- **Testing** : built-in test framework, Mockito
- **Deployment** : Docker, docker-compose

## Points clés

### Sécurité mémoire
Rust garantit la sécurité mémoire au moment de la compilation grâce au système d'ownership, éliminant les bugs courants comme les use-after-free et les data races.

### Performance
Comparable au C/C++, Rust offre un contrôle bas niveau avec des abstractions zero-cost, idéal pour les applications critiques en performance.

### Écosystème moderne
Cargo simplifie la gestion des dépendances et le build. L'écosystème Rust propose des crates de qualité pour le web, les bases de données, et le testing.

## Ressources

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Actix Web Documentation](https://actix.rs/)
- [Diesel ORM Guide](https://diesel.rs/guides/)

## Livrables

✅ Bootstrap complété avec tous les exercices fonctionnels  
✅ Application Hello World full-stack opérationnelle  
✅ Tests unitaires et d'intégration passants  
✅ Documentation technique du projet  
✅ Conteneurisation Docker fonctionnelle
