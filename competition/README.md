# Competition — 5G Antenna Optimization

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Algorithms](https://img.shields.io/badge/Algorithms-FF6B6B?logo=algorithm&logoColor=white)
![Optimization](https://img.shields.io/badge/Optimization-4ECDC4?logo=optimization&logoColor=white)

Compétition d'optimisation algorithmique : placement optimal d'antennes 5G pour couvrir une ville tout en minimisant les coûts.

## 📋 Description

Défi algorithmique consistant à placer des antennes 5G pour couvrir tous les bâtiments d'une ville, en tenant compte de :

- **Variations de population** : les bâtiments ont des populations différentes selon les périodes (heures pleines, heures creuses, nuit)
- **Contraintes de capacité** : chaque antenne a une capacité maximale et une portée limitée
- **Optimisation des coûts** : minimiser le coût total d'installation (placement sur bâtiment vs hors bâtiment)

## 📁 Structure

```text
competition/
├── README.md              # Ce fichier
├── question.md            # Énoncé détaillé du problème
├── scoreboard.md          # Meilleurs scores par ville
├── score_function.py      # Fonction de calcul du score
├── starter_kit.py         # Kit de démarrage
├── shell.nix              # Environnement Nix (optionnel)
├── datasets/              # Jeux de données
│   ├── 1_peaceful_village.json
│   ├── 2_small_town.json
│   ├── 3_suburbia.json
│   ├── 4_epitech.json
│   ├── 5_isogrid.json
│   └── 6_manhattan.json
└── solutions/             # Solutions optimisées
    ├── solution_peaceful_village.json
    ├── solution_small_town.json
    ├── solution_suburbia.json
    ├── solution_epitech.json
    ├── solution_isogrid.json
    └── solution_manhattan.json
```

## 🎯 Objectifs

- **Optimisation algorithmique** : développer des algorithmes efficaces pour le placement d'antennes
- **Gestion de contraintes** : respecter les contraintes de portée et de capacité
- **Minimisation des coûts** : trouver la solution la moins coûteuse pour chaque ville
- **Analyse de complexité** : comprendre les trade-offs entre différentes approches

## 🧠 Notions clés

- **Algorithmes gloutons** : placement itératif d'antennes

- **Clustering** : regroupement de bâtiments pour optimiser la couverture
- **Distance euclidienne** : calcul de portée des antennes
- **Gestion de capacité** : allocation de population aux antennes
- **Optimisation combinatoire** : exploration de l'espace des solutions

## 🚀 Utilisation

### Vérification d'une solution

```bash
python3 score_function.py datasets/1_peaceful_village.json solutions/solution_peaceful_village.json
```

### Développement

Consultez `question.md` pour l'énoncé complet et `starter_kit.py` pour un exemple de structure.

## 📊 Meilleurs scores

Consultez `scoreboard.md` pour les meilleurs scores actuels par ville.

## 🔗 Ressources

- [Énoncé complet](question.md)
- [Scoreboard](scoreboard.md)
- [Fonction de score](score_function.py)
