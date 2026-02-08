# Séminaire Jenkins (Days 66–70)

![Jenkins](https://img.shields.io/badge/Jenkins-D24939?logo=jenkins&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-pipelines-blue)
![Groovy](https://img.shields.io/badge/Groovy-4298B8?logo=apachegroovy&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-000000?logo=yaml&logoColor=white)

Automatisation CI/CD avec Jenkins, Configuration as Code (JCasC) et Job DSL autour du projet **MY\_MARVIN**.

## Contenu

- Days 66–70 → Jenkins, JCasC et Job DSL : projet MY\_MARVIN ([README](Days_66_70/README.md))
  - **Configuration as Code** : configuration complète de Jenkins via un fichier `my_marvin.yml`
  - **Job DSL Groovy** : génération de jobs Jenkins via `job_dsl.groovy`
  - **Pipelines CI/CD** : compilation, tests (`make tests_run`), nettoyage, SCM polling

## Notions

- **Jenkins** : serveur d’intégration continue, jobs freestyle, dossiers (`cloudbees-folder`)
- **Configuration as Code (JCasC)** : description déclarative de l’instance Jenkins en YAML
- **Job DSL** : définition de jobs Jenkins en Groovy, factorisation de la configuration
- **Gestion des rôles** : plugin `role-strategy`, création de rôles globaux et attribution fine des droits
- **Sécurité** : pas de mots de passe en dur, utilisation exclusive des variables d’environnement
- **SCM & GitHub** : configuration des jobs pour suivre un dépôt GitHub, SCM polling, workspace cleanup

## Compétences

- Modéliser une configuration Jenkins complète en YAML (JCasC)
- Écrire des scripts Job DSL Groovy robustes et réutilisables
- Concevoir un pipeline CI qui compile, teste et nettoie automatiquement un projet
- Gérer les droits d’accès via des rôles (admin, pédagogie, assistants)
- Mettre en place une instance Jenkins reproductible et testable automatiquement
