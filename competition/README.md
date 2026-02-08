# Code Competition — 5G or not 5G ?

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Algorithms](https://img.shields.io/badge/Algorithms-FF6B6B?logo=algorithm&logoColor=white)
![Optimization](https://img.shields.io/badge/Optimization-4ECDC4?logo=optimization&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-76B900?logo=nvidia&logoColor=white)

## Contexte

Compétition algorithmique d'optimisation : déploiement optimal d'un réseau d'antennes 5G pour couvrir une ville tout en minimisant les coûts d'installation.

## Problématique

Étant donné :
- Une carte de bâtiments avec leurs positions (x, y) et populations
- Un ensemble d'antennes 5G avec leurs coûts d'installation et portées
- Une contrainte de couverture minimale de la population

Objectif : **Minimiser le coût total** d'installation des antennes tout en garantissant que chaque bâtiment est couvert par au moins une antenne.

## Contraintes

- **Couverture** : Un bâtiment est couvert si la distance euclidienne à une antenne ≤ portée de l'antenne
- **Optimisation** : Trouver le placement optimal (nombre et positions) des antennes
- **Budget** : Chaque antenne a un coût d'installation variable selon sa portée

## Approche algorithmique

### Stratégies possibles

1. **Greedy (glouton)** : Placer itérativement l'antenne qui couvre le plus de bâtiments non couverts
2. **Clustering** : Regrouper les bâtiments proches et placer une antenne par cluster
3. **Optimisation locale** : Recherche locale avec perturbations pour échapper aux minima locaux
4. **Heuristiques avancées** : Algorithmes génétiques, recuit simulé, colonies de fourmis

### Solution implémentée

Le fichier [god_tier_cuda.py](god_tier_cuda.py) contient une solution optimisée utilisant :
- Clustering spatial des bâtiments
- Calcul de couverture vectorisé
- Optimisation greedy avec backtracking
- **Accélération GPU avec CUDA** pour les calculs de distance

## Technologies

- **Python 3.x** : langage principal
- **NumPy** : calculs vectorisés, distances euclidiennes
- **CUDA/CuPy** : accélération GPU pour les calculs massifs
- **Matplotlib** : visualisation des résultats (optionnel)

## Structure du code

```python
# Pseudo-code de la stratégie
1. Charger les données (bâtiments, antennes disponibles)
2. Calculer la matrice de distances bâtiments-positions possibles
3. Algorithme greedy optimisé :
   - Sélectionner l'antenne avec le meilleur ratio couverture/coût
   - Marquer les bâtiments couverts
   - Répéter jusqu'à couverture complète
4. Optimisation locale pour réduire le coût
5. Retourner la configuration optimale
```

## Métriques de performance

- **Coût total** : somme des coûts des antennes installées (à minimiser)
- **Couverture** : pourcentage de la population couverte (≥ 100%)
- **Temps d'exécution** : performance algorithmique
- **Mémoire** : efficacité du code

## Compétences développées

- **Algorithmique** : optimisation combinatoire, heuristiques
- **Structures de données** : graphes, arbres de recherche
- **Performance** : vectorisation, parallélisation GPU
- **Analyse de complexité** : compromis temps/mémoire
- **Modélisation** : transformation d'un problème métier en problème algorithmique

## Résultats

La solution implémentée permet de :
- ✅ Couvrir 100% des bâtiments
- ✅ Minimiser le coût d'installation
- ✅ Temps d'exécution optimisé avec CUDA
- ✅ Scalabilité sur grandes instances (milliers de bâtiments)

## Ressources

- [Introduction to Optimization Algorithms](https://en.wikipedia.org/wiki/Optimization_algorithm)
- [Greedy Algorithms](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [CUDA Python (CuPy)](https://cupy.dev/)
- [Facility Location Problem](https://en.wikipedia.org/wiki/Facility_location_problem)
