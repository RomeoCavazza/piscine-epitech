# 🏆 Code Competition — 5G or not 5G ?

Compétition d'optimisation algorithmique : déploiement optimal d'un réseau d'antennes 5G pour couvrir une ville tout en minimisant les coûts d'installation.

## 📋 Description

Vous êtes recruté·e par un opérateur téléphonique qui souhaite déployer son réseau sur une nouvelle ville. Votre mission : installer des antennes pour couvrir tous les bâtiments de la zone, tout en minimisant les coûts d'installation.

**Défi** : La population des bâtiments varie selon l'heure de la journée (bureaux bondés en journée mais déserts la nuit, immeubles résidentiels pleins la nuit mais vides le jour). Les antennes doivent pouvoir gérer le pic de fréquentation.

## 🎯 Objectif

Minimiser le coût total d'installation des antennes tout en respectant les contraintes :
- Chaque bâtiment doit être couvert par exactement une antenne
- La distance entre l'antenne et le bâtiment ne doit pas dépasser la portée de l'antenne
- La capacité de l'antenne ne doit pas être dépassée (pic de population sur les 3 périodes)

## 📦 Structure

```text
code-competition/
├── README.md              # Ce fichier
├── question.md            # Règles détaillées de la compétition
├── starter_kit.py         # Solution naïve de départ
├── optimizer.py           # Algorithme d'optimisation avancé
├── score_function.py      # Fonction d'évaluation des solutions
├── datasets/              # Jeux de données (6 villes)
│   ├── 1_peaceful_village.json
│   ├── 2_small_town.json
│   ├── 3_suburbia.json
│   ├── 4_epitech.json
│   ├── 5_isogrid.json
│   └── 6_manhattan.json
└── solutions/             # Solutions générées
    ├── solution_1.json
    ├── solution_2.json
    ├── solution_3.json
    ├── solution_4.json
    ├── solution_5.json
    └── solution_6.json
```

## 🔧 Utilisation

### Solution naïve (starter_kit.py)

```bash
python3 starter_kit.py
```

Génère une solution basique : une antenne Density sur chaque bâtiment (très coûteux mais fonctionnel).

### Optimiseur avancé (optimizer.py)

```bash
# Optimiser un dataset spécifique
python3 optimizer.py 1_peaceful_village

# Optimiser tous les datasets
python3 optimizer.py all
```

L'optimiseur utilise plusieurs stratégies :
- **Solution optimale** pour les petits datasets (fichiers 1 et 2)
- **Algorithme glouton optimisé** avec clustering intelligent
- **Stratégie MaxRange** pour les zones dispersées (Manhattan)

## 📊 Types d'antennes

| Type | Portée | Capacité | Coût (sur bâtiment) | Coût (hors bâtiment) |
|------|--------|----------|---------------------|----------------------|
| **Nano** | 50 | 200 | 5 000 € | 6 000 € |
| **Spot** | 100 | 800 | 15 000 € | 20 000 € |
| **Density** | 150 | 5 000 | 30 000 € | 50 000 € |
| **MaxRange** | 400 | 3 500 | 40 000 € | 50 000 € |

## 📈 Score

Le score est égal au coût total de l'installation. Plus le coût est bas, meilleur est le score.

Pour chaque jeu de données, le meilleur joueur remporte 1 million de points. Les autres joueurs reçoivent un score proportionnel :

```
Score = 1 000 000 × (score_meilleur / score_joueur)
```

## 🚀 Stratégies d'optimisation

1. **Clustering intelligent** : Regrouper les bâtiments proches pour partager une antenne
2. **Placement optimal** : Placer les antennes sur les bâtiments pour réduire les coûts
3. **Sélection de type** : Choisir le type d'antenne le plus rentable selon la densité
4. **MaxRange pour zones dispersées** : Utiliser MaxRange pour couvrir de grandes zones avec peu d'antennes

## 📚 Ressources

- [question.md](question.md) : Règles complètes de la compétition
- [score_function.py](score_function.py) : Fonction d'évaluation utilisée par le serveur

## 🛠️ Technologies

- **Python 3** : Algorithmes d'optimisation, manipulation JSON
- **Algorithmes** : Glouton, clustering, recherche de solutions optimales





