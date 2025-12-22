#!/usr/bin/env python3
"""
Algorithme d'optimisation CUDA pour le problème d'antennes 5G
Utilise CUDA pour accélérer les calculs de distance et de clustering
"""

import json
import math
import numpy as np
from typing import List, Dict, Tuple, Set, Optional
from score_function import getSolutionScore

# Tentative d'import CUDA
CUDA_AVAILABLE = False
cuda = None

try:
    from numba import cuda as numba_cuda
    cuda = numba_cuda
    CUDA_AVAILABLE = True
    print("✓ Numba CUDA disponible")
except ImportError:
    try:
        import cupy as cp
        CUDA_AVAILABLE = True
        print("✓ CuPy disponible")
    except ImportError:
        print("⚠ CUDA non disponible, utilisation du CPU optimisé avec NumPy")

ANTENNA_TYPES = {
    'Nano': {'range': 50, 'capacity': 200, 'cost_on_building': 5_000, 'cost_off_building': 6_000},
    'Spot': {'range': 100, 'capacity': 800, 'cost_on_building': 15_000, 'cost_off_building': 20_000},
    'Density': {'range': 150, 'capacity': 5_000, 'cost_on_building': 30_000, 'cost_off_building': 50_000},
    'MaxRange': {'range': 400, 'capacity': 3_500, 'cost_on_building': 40_000, 'cost_off_building': 50_000}
}


# Définir les kernels CUDA si disponible
if CUDA_AVAILABLE and cuda is not None:
    @cuda.jit
    def compute_distances_kernel(buildings_x, buildings_y, antenna_x, antenna_y, range_limit, result):
        """Kernel CUDA pour calculer les distances entre une antenne et tous les bâtiments."""
        idx = cuda.grid(1)
        if idx < buildings_x.shape[0]:
            dx = buildings_x[idx] - antenna_x
            dy = buildings_y[idx] - antenna_y
            dist = math.sqrt(dx * dx + dy * dy)
            result[idx] = dist <= range_limit
    
    @cuda.jit
    def compute_all_distances_kernel(buildings_x, buildings_y, result_matrix):
        """Kernel CUDA pour calculer toutes les distances entre bâtiments."""
        i, j = cuda.grid(2)
        if i < buildings_x.shape[0] and j < buildings_x.shape[0]:
            dx = buildings_x[i] - buildings_x[j]
            dy = buildings_y[i] - buildings_y[j]
            result_matrix[i, j] = math.sqrt(dx * dx + dy * dy)


def compute_distance_matrix_cuda(buildings_x: np.ndarray, buildings_y: np.ndarray) -> np.ndarray:
    """
    Calcule la matrice de distances entre tous les bâtiments en utilisant CUDA.
    """
    n = buildings_x.shape[0]
    
    if not CUDA_AVAILABLE or cuda is None:
        # Fallback CPU avec vectorisation NumPy optimisée
        x_diff = buildings_x[:, np.newaxis] - buildings_x[np.newaxis, :]
        y_diff = buildings_y[:, np.newaxis] - buildings_y[np.newaxis, :]
        return np.sqrt(x_diff ** 2 + y_diff ** 2)
    
    try:
        # Allouer sur GPU
        d_buildings_x = cuda.to_device(buildings_x.astype(np.float32))
        d_buildings_y = cuda.to_device(buildings_y.astype(np.float32))
        d_result = cuda.device_array((n, n), dtype=np.float32)
        
        # Configuration des threads (16x16 par bloc)
        threads_per_block = (16, 16)
        blocks_per_grid_x = (n + threads_per_block[0] - 1) // threads_per_block[0]
        blocks_per_grid_y = (n + threads_per_block[1] - 1) // threads_per_block[1]
        blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)
        
        # Lancer le kernel
        compute_all_distances_kernel[blocks_per_grid, threads_per_block](
            d_buildings_x, d_buildings_y, d_result
        )
        
        # Copier le résultat
        return d_result.copy_to_host()
    except Exception as e:
        print(f"⚠ Erreur CUDA, fallback CPU: {e}")
        # Fallback CPU
        x_diff = buildings_x[:, np.newaxis] - buildings_x[np.newaxis, :]
        y_diff = buildings_y[:, np.newaxis] - buildings_y[np.newaxis, :]
        return np.sqrt(x_diff ** 2 + y_diff ** 2)


def euclidean_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_max_population(building: Dict) -> int:
    """Retourne la population maximale d'un bâtiment sur les 3 périodes."""
    return max(
        building['populationPeakHours'],
        building['populationOffPeakHours'],
        building['populationNight']
    )


def check_capacity(cluster: List[Dict], capacity: int) -> bool:
    """
    Vérifie que le cluster respecte la capacité pour toutes les périodes.
    """
    total_peak = sum(b['populationPeakHours'] for b in cluster)
    total_off_peak = sum(b['populationOffPeakHours'] for b in cluster)
    total_night = sum(b['populationNight'] for b in cluster)
    max_load = max(total_peak, total_off_peak, total_night)
    return max_load <= capacity


def get_antenna_cost(antenna_type: str, x: int, y: int, building_positions: Set[Tuple[int, int]]) -> int:
    """Calcule le coût d'une antenne selon son placement."""
    spec = ANTENNA_TYPES[antenna_type]
    is_on_building = (x, y) in building_positions
    return spec['cost_on_building'] if is_on_building else spec['cost_off_building']


def find_optimal_cluster_optimized(building: Dict, remaining: List[Dict], 
                                   antenna_type: str, building_positions: Set[Tuple[int, int]],
                                   distance_matrix: Optional[np.ndarray] = None,
                                   building_indices: Optional[Dict[int, int]] = None) -> Tuple[List[Dict], Tuple[int, int], float]:
    """
    Trouve le cluster optimal pour un bâtiment avec un type d'antenne donné.
    Utilise la matrice de distance pré-calculée si disponible.
    """
    spec = ANTENNA_TYPES[antenna_type]
    range_limit = spec['range']
    capacity = spec['capacity']
    
    # Commencer avec le bâtiment seul
    best_cluster = [building]
    best_pos = (building['x'], building['y'])
    best_cost_per_building = float('inf')
    
    # Essayer différentes positions : sur le bâtiment et autour
    positions_to_try = [(building['x'], building['y'])]
    
    # Pour MaxRange, essayer plus de positions pour optimiser
    step = 20 if antenna_type == 'MaxRange' else 10
    radius = 100 if antenna_type == 'MaxRange' else 50
    
    for dx in range(-radius, radius + 1, step):
        for dy in range(-radius, radius + 1, step):
            if dx == 0 and dy == 0:
                continue
            new_x = building['x'] + dx
            new_y = building['y'] + dy
            if new_x >= 0 and new_y >= 0:
                positions_to_try.append((new_x, new_y))
    
    # Utiliser la matrice de distance si disponible pour accélérer
    if distance_matrix is not None and building_indices is not None:
        building_idx = building_indices.get(building['id'])
        if building_idx is not None:
            # Utiliser la matrice pour trouver rapidement les bâtiments proches
            remaining_indices = [building_indices.get(b['id']) for b in remaining 
                               if b['id'] != building['id'] and building_indices.get(b['id']) is not None]
            
            if len(remaining_indices) > 0:
                # Pour chaque position, utiliser la matrice pour filtrer rapidement
                for pos_x, pos_y in positions_to_try[:50]:  # Limiter pour performance
                    dist_to_building = euclidean_distance(pos_x, pos_y, building['x'], building['y'])
                    if dist_to_building > range_limit:
                        continue
                    
                    cluster = [building]
                    
                    # Calculer les distances depuis cette position
                    candidates = []
                    for other in remaining:
                        if other['id'] == building['id']:
                            continue
                        distance = euclidean_distance(pos_x, pos_y, other['x'], other['y'])
                        if distance <= range_limit:
                            candidates.append((other, distance))
                    
                    candidates.sort(key=lambda x: x[1])
                    
                    for other, dist in candidates:
                        test_cluster = cluster + [other]
                        if check_capacity(test_cluster, capacity):
                            cluster = test_cluster
                    
                    if check_capacity(cluster, capacity):
                        cost = get_antenna_cost(antenna_type, pos_x, pos_y, building_positions)
                        cost_per_building = cost / len(cluster)
                        
                        if len(cluster) > len(best_cluster) or (len(cluster) == len(best_cluster) and cost_per_building < best_cost_per_building):
                            best_cluster = cluster
                            best_pos = (pos_x, pos_y)
                            best_cost_per_building = cost_per_building
                    
                    if len(best_cluster) > 5:  # Bon cluster trouvé, arrêter
                        break
    
    # Si pas de bonne solution avec matrice, utiliser méthode classique
    if len(best_cluster) == 1:
        for pos_x, pos_y in positions_to_try:
            dist_to_building = euclidean_distance(pos_x, pos_y, building['x'], building['y'])
            if dist_to_building > range_limit:
                continue
            
            cluster = [building]
            candidates = []
            
            for other in remaining:
                if other['id'] == building['id']:
                    continue
                distance = euclidean_distance(pos_x, pos_y, other['x'], other['y'])
                if distance <= range_limit:
                    candidates.append((other, distance))
            
            candidates.sort(key=lambda x: x[1])
            
            for other, dist in candidates:
                test_cluster = cluster + [other]
                if check_capacity(test_cluster, capacity):
                    cluster = test_cluster
            
            if check_capacity(cluster, capacity):
                cost = get_antenna_cost(antenna_type, pos_x, pos_y, building_positions)
                cost_per_building = cost / len(cluster)
                
                if len(cluster) > len(best_cluster) or (len(cluster) == len(best_cluster) and cost_per_building < best_cost_per_building):
                    best_cluster = cluster
                    best_pos = (pos_x, pos_y)
                    best_cost_per_building = cost_per_building
    
    return best_cluster, best_pos, best_cost_per_building


def solve_suburbia_cuda(dataset: Dict) -> Dict:
    """
    Optimisation CUDA pour Suburbia (fichier 3) - Objectif: 28 431 000€
    Utilise CUDA pour accélérer les calculs de distance et de clustering.
    """
    buildings = dataset['buildings'].copy()
    building_map = {b['id']: b for b in buildings}
    building_positions = {(b['x'], b['y']) for b in buildings}
    
    # Calculer pop max pour chaque bâtiment
    for building in buildings:
        building['max_pop'] = get_max_population(building)
    
    antennas = []
    covered = set()
    
    # Trier par population décroissante
    buildings.sort(key=lambda b: b['max_pop'], reverse=True)
    
    # Pré-calculer la matrice de distances avec CUDA si disponible
    distance_matrix = None
    building_indices = None
    
    if len(buildings) > 100:
        print("Calcul de la matrice de distances...")
        building_indices = {b['id']: i for i, b in enumerate(buildings)}
        buildings_x = np.array([b['x'] for b in buildings], dtype=np.float32)
        buildings_y = np.array([b['y'] for b in buildings], dtype=np.float32)
        
        distance_matrix = compute_distance_matrix_cuda(buildings_x, buildings_y)
        print(f"✓ Matrice de distances calculée ({distance_matrix.shape[0]}x{distance_matrix.shape[1]})")
    
    # Phase 1: Traiter les bâtiments nécessitant Density (pop > 3500)
    for building in buildings:
        if building['id'] in covered:
            continue
        
        if building['max_pop'] > 3500:
            antennas.append({
                'type': 'Density',
                'x': building['x'],
                'y': building['y'],
                'buildings': [building['id']]
            })
            covered.add(building['id'])
    
    # Phase 2: MaxRange agressif avec optimisation de position
    remaining = [b for b in buildings if b['id'] not in covered]
    remaining.sort(key=lambda b: b['max_pop'], reverse=True)
    
    print(f"Traitement de {len(remaining)} bâtiments restants...")
    
    for i, building in enumerate(remaining):
        if building['id'] in covered:
            continue
        
        if (i + 1) % 200 == 0:
            print(f"  Progression: {i+1}/{len(remaining)} bâtiments traités, {len(antennas)} antennes créées")
        
        # Essayer MaxRange avec optimisation de position
        cluster, pos, cost_per_building = find_optimal_cluster_optimized(
            building, [b for b in remaining if b['id'] not in covered],
            'MaxRange', building_positions, distance_matrix, building_indices
        )
        
        # Utiliser MaxRange si rentable
        if len(cluster) >= 2 or cost_per_building < 25000:
            antennas.append({
                'type': 'MaxRange',
                'x': pos[0],
                'y': pos[1],
                'buildings': [b['id'] for b in cluster]
            })
            covered.update(b['id'] for b in cluster)
            continue
        
        # Phase 3: Essayer de connecter à une antenne existante
        connected = False
        for antenna in antennas:
            antenna_spec = ANTENNA_TYPES[antenna['type']]
            
            dist = euclidean_distance(
                antenna['x'], antenna['y'],
                building['x'], building['y']
            )
            if dist > antenna_spec['range']:
                continue
            
            cluster_buildings = [building_map[bid] for bid in antenna['buildings']] + [building]
            if check_capacity(cluster_buildings, antenna_spec['capacity']):
                antenna['buildings'].append(building['id'])
                covered.add(building['id'])
                connected = True
                break
        
        # Phase 4: Essayer Spot avec optimisation
        if not connected:
            cluster, pos, cost_per_building = find_optimal_cluster_optimized(
                building, [b for b in remaining if b['id'] not in covered],
                'Spot', building_positions, distance_matrix, building_indices
            )
            
            if len(cluster) >= 2 or cost_per_building < 20000:
                antennas.append({
                    'type': 'Spot',
                    'x': pos[0],
                    'y': pos[1],
                    'buildings': [b['id'] for b in cluster]
                })
                covered.update(b['id'] for b in cluster)
                continue
        
        # Phase 5: Fallback - utiliser le type minimal nécessaire
        if not connected:
            for antenna_type in ['Nano', 'Spot', 'Density']:
                spec = ANTENNA_TYPES[antenna_type]
                if building['max_pop'] <= spec['capacity']:
                    cost = get_antenna_cost(antenna_type, building['x'], building['y'], building_positions)
                    antennas.append({
                        'type': antenna_type,
                        'x': building['x'],
                        'y': building['y'],
                        'buildings': [building['id']]
                    })
                    covered.add(building['id'])
                    break
    
    print(f"✓ Solution générée avec {len(antennas)} antennes")
    return {'antennas': antennas}


if __name__ == "__main__":
    import sys
    
    dataset_name = sys.argv[1] if len(sys.argv) > 1 else "3_suburbia"
    
    with open(f'./datasets/{dataset_name}.json', 'r') as f:
        dataset = json.load(f)
    
    solution = solve_suburbia_cuda(dataset)
    cost, isValid, msg = getSolutionScore(
        json.dumps(solution),
        json.dumps(dataset)
    )
    
    print(f"\nCoût: {cost:,}€")
    print(f"Valide: {isValid}")
    if not isValid:
        print(f"Message: {msg}")
    
    if isValid:
        file_num = dataset_name.split('_')[0]
        output_file = f'./solutions/solution_{file_num}.json'
        with open(output_file, 'w') as f:
            json.dump(solution, f, indent=2)
        print(f"Solution sauvegardée: {output_file}")
