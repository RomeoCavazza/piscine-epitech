#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU Distance + Greedy + Bandit Improver (3..6 in parallel)

Print format (simple):
  "<k> <cost> <improved>"
Where improved is 1 if final_cost < start_cost, else 0.

Env vars:
  USE_CUDA=1              (default 1)
  TIME_BUDGET_SEC=10      (default 10 seconds per dataset for 3..6)
  SEED=42                 (default 42)
  MAX_WORKERS=2           (default 2; set 4 if your GPU can handle it)
"""

from __future__ import annotations

import json
import os
import time
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set

import numpy as np

# -----------------------------
# Antenna specification
# -----------------------------

ANTENNA_TYPES: Dict[int, Dict[str, int | str]] = {
    0: {"name": "Nano",     "range": 50,  "capacity": 200,  "cost_on": 5000,  "cost_off": 6000},
    1: {"name": "Spot",     "range": 100, "capacity": 800,  "cost_on": 15000, "cost_off": 20000},
    2: {"name": "Density",  "range": 150, "capacity": 5000, "cost_on": 30000, "cost_off": 50000},
    3: {"name": "MaxRange", "range": 400, "capacity": 3500, "cost_on": 40000, "cost_off": 50000},
}
NAME_TO_TYPE = {v["name"]: k for k, v in ANTENNA_TYPES.items()}

def ant_range_sq(t: int) -> int:
    r = int(ANTENNA_TYPES[t]["range"])
    return r * r

def ant_capacity(t: int) -> int:
    return int(ANTENNA_TYPES[t]["capacity"])

def ant_cost(t: int, ax: int, ay: int, building_coords: Set[Tuple[int, int]]) -> int:
    on_building = (ax, ay) in building_coords
    return int(ANTENNA_TYPES[t]["cost_on"] if on_building else ANTENNA_TYPES[t]["cost_off"])


# -----------------------------
# Optional CUDA
# -----------------------------

CUDA_AVAILABLE = False
try:
    from numba import cuda

    @cuda.jit
    def dist_sq_matrix_kernel(bx, by, out_dist_sq):
        i, j = cuda.grid(2)
        n = bx.size
        if i < n and j < n:
            dx = bx[i] - bx[j]
            dy = by[i] - by[j]
            out_dist_sq[i, j] = dx * dx + dy * dy

    CUDA_AVAILABLE = True
except Exception:
    CUDA_AVAILABLE = False


# -----------------------------
# Data structures
# -----------------------------

@dataclass(frozen=True)
class Building:
    id: int
    x: int
    y: int
    p_max: int

@dataclass
class Antenna:
    t: int
    site: int
    buildings: List[int]

    def clone(self) -> "Antenna":
        return Antenna(self.t, self.site, list(self.buildings))

@dataclass
class Solution:
    antennas: List[Antenna]

    def clone(self) -> "Solution":
        return Solution([a.clone() for a in self.antennas])


# -----------------------------
# Evaluator (strict)
# -----------------------------

class Evaluator:
    def __init__(self, buildings: List[Building], dist_sq: np.ndarray):
        self.buildings = buildings
        self.n = len(buildings)
        self.dist_sq = dist_sq
        self.coords = {(b.x, b.y) for b in buildings}

    def cost(self, sol: Solution) -> int:
        total = 0
        for a in sol.antennas:
            bs = self.buildings[a.site]
            total += ant_cost(a.t, bs.x, bs.y, self.coords)
        return total

    def validate(self, sol: Solution) -> Tuple[bool, str]:
        if sol is None or sol.antennas is None:
            return False, "solution is None"

        n = self.n
        seen = np.zeros(n, dtype=np.int32)

        for ai, a in enumerate(sol.antennas):
            if a.t not in ANTENNA_TYPES:
                return False, f"antenna[{ai}] invalid type {a.t}"
            if a.site < 0 or a.site >= n:
                return False, f"antenna[{ai}] invalid site index {a.site}"
            if not a.buildings:
                return False, f"antenna[{ai}] has no buildings"

            r2 = ant_range_sq(a.t)
            cap = ant_capacity(a.t)
            load = 0

            for bi in a.buildings:
                if bi < 0 or bi >= n:
                    return False, f"antenna[{ai}] invalid building index {bi}"
                seen[bi] += 1
                if int(self.dist_sq[a.site, bi]) > r2:
                    return False, f"antenna[{ai}] building {bi} out of range"
                load += self.buildings[bi].p_max

            if load > cap:
                return False, f"antenna[{ai}] capacity exceeded ({load} > {cap})"

        bad = np.where(seen != 1)[0]
        if bad.size:
            i = int(bad[0])
            return False, f"building index {i} appears {int(seen[i])} times (must be exactly 1)"

        return True, "ok"


# -----------------------------
# GPU distance precompute
# -----------------------------

def compute_dist_sq_matrix(bx: np.ndarray, by: np.ndarray, use_cuda: bool) -> np.ndarray:
    n = bx.size
    if not use_cuda or not CUDA_AVAILABLE:
        dx = bx.astype(np.int64)[:, None] - bx.astype(np.int64)[None, :]
        dy = by.astype(np.int64)[:, None] - by.astype(np.int64)[None, :]
        return (dx * dx + dy * dy).astype(np.int32)

    d_bx = cuda.to_device(bx)
    d_by = cuda.to_device(by)
    d_out = cuda.device_array((n, n), dtype=np.int32)

    threads = (16, 16)
    blocks = ((n + threads[0] - 1) // threads[0], (n + threads[1] - 1) // threads[1])
    dist_sq_matrix_kernel[blocks, threads](d_bx, d_by, d_out)
    cuda.synchronize()
    return d_out.copy_to_host()


# -----------------------------
# Neighbor lists
# -----------------------------

def build_neighbors(dist_sq: np.ndarray, r2: int) -> List[np.ndarray]:
    n = dist_sq.shape[0]
    neighbors: List[np.ndarray] = []
    for s in range(n):
        idx = np.where(dist_sq[s] <= r2)[0]
        idx = idx[np.argsort(dist_sq[s, idx], kind="mergesort")]
        neighbors.append(idx.astype(np.int32))
    return neighbors


# -----------------------------
# Greedy constructor
# -----------------------------

def greedy_construct(buildings: List[Building], dist_sq: np.ndarray, neighbors_by_type: Dict[int, List[np.ndarray]]) -> Solution:
    n = len(buildings)
    p = np.array([b.p_max for b in buildings], dtype=np.int32)
    assigned = np.full(n, -1, dtype=np.int32)

    order = np.argsort(-p)
    antennas: List[Antenna] = []
    coords = {(b.x, b.y) for b in buildings}

    def load_of(a: Antenna) -> int:
        return int(sum(p[bi] for bi in a.buildings))

    for bi in order:
        bi = int(bi)
        if assigned[bi] != -1:
            continue

        # reuse existing
        placed = False
        for ai, a in enumerate(antennas):
            if int(dist_sq[a.site, bi]) > ant_range_sq(a.t):
                continue
            if load_of(a) + int(p[bi]) > ant_capacity(a.t):
                continue
            a.buildings.append(bi)
            assigned[bi] = ai
            placed = True
            break
        if placed:
            continue

        # new antenna at building bi
        pop = int(p[bi])
        feasible = [t for t in range(4) if ant_capacity(t) >= pop] or [2]
        site_b = buildings[bi]

        best_t = feasible[0]
        best_eff = -1.0
        best_c = 10**18
        for t in feasible:
            c = ant_cost(t, site_b.x, site_b.y, coords)
            eff = ant_capacity(t) / float(c)
            if eff > best_eff or (eff == best_eff and c < best_c):
                best_eff, best_c, best_t = eff, c, t

        a = Antenna(int(best_t), bi, [bi])
        antennas.append(a)
        assigned[bi] = len(antennas) - 1

        cap = ant_capacity(a.t)
        load = pop
        neigh = neighbors_by_type[a.t][a.site]
        for bj in neigh:
            bj = int(bj)
            if assigned[bj] != -1:
                continue
            pj = int(p[bj])
            if load + pj > cap:
                continue
            a.buildings.append(bj)
            assigned[bj] = assigned[bi]
            load += pj

    # safety: leftovers
    for bi in range(n):
        if assigned[bi] == -1:
            pop = int(p[bi])
            feasible = [t for t in range(4) if ant_capacity(t) >= pop] or [2]
            b = buildings[bi]
            tbest = min(feasible, key=lambda t: ant_cost(t, b.x, b.y, coords))
            antennas.append(Antenna(int(tbest), bi, [bi]))
            assigned[bi] = len(antennas) - 1

    return Solution(antennas)


# -----------------------------
# Bandit + mutations
# -----------------------------

class Bandit:
    def __init__(self, ops: List[str], rng: random.Random):
        self.ops = ops
        self.rng = rng
        self.count = {op: 0 for op in ops}
        self.value = {op: 0.0 for op in ops}

    def select(self) -> str:
        total = sum(self.count.values()) + 1
        scores = []
        for op in self.ops:
            c = self.count[op]
            bonus = math.sqrt(math.log(total) / (c + 1.0))
            scores.append(self.value[op] + 0.25 * bonus)

        m = max(scores)
        exps = [math.exp(s - m) for s in scores]
        z = sum(exps)
        r = self.rng.random() * z
        acc = 0.0
        for op, e in zip(self.ops, exps):
            acc += e
            if acc >= r:
                return op
        return self.ops[-1]

    def update(self, op: str, reward: float) -> None:
        self.count[op] += 1
        n = self.count[op]
        self.value[op] += (reward - self.value[op]) / float(n)


class Improver:
    def __init__(self, buildings: List[Building], dist_sq: np.ndarray, neighbors_by_type: Dict[int, List[np.ndarray]], seed: int = 42):
        self.buildings = buildings
        self.n = len(buildings)
        self.dist_sq = dist_sq
        self.neighbors_by_type = neighbors_by_type
        self.eval = Evaluator(buildings, dist_sq)
        self.rng = random.Random(seed)
        self.coords = {(b.x, b.y) for b in buildings}

        self.ops = [
            "downgrade_type",
            "recenter_site_to_member",
            "move_one_building",
            "swap_two_buildings",
            "remove_antenna_and_repair",
        ]
        self.bandit = Bandit(self.ops, self.rng)

    def _load(self, a: Antenna) -> int:
        return sum(self.buildings[i].p_max for i in a.buildings)

    def _in_range(self, a: Antenna, bi: int) -> bool:
        return int(self.dist_sq[a.site, bi]) <= ant_range_sq(a.t)

    def _repair_exact_cover(self, sol: Solution) -> Optional[Solution]:
        n = self.n
        owner = np.full(n, -1, dtype=np.int32)

        # remove duplicates
        for ai, a in enumerate(sol.antennas):
            new_list = []
            for bi in a.buildings:
                if owner[bi] == -1:
                    owner[bi] = ai
                    new_list.append(bi)
            a.buildings = new_list

        sol.antennas = [a for a in sol.antennas if a.buildings]

        owner[:] = -1
        for ai, a in enumerate(sol.antennas):
            for bi in a.buildings:
                owner[bi] = ai

        missing = np.where(owner == -1)[0].tolist()
        if not missing:
            ok, _ = self.eval.validate(sol)
            return sol if ok else None

        # insert into existing
        for bi in missing[:]:
            bi = int(bi)
            inserted = False
            for a in sol.antennas:
                if not self._in_range(a, bi):
                    continue
                if self._load(a) + self.buildings[bi].p_max <= ant_capacity(a.t):
                    a.buildings.append(bi)
                    inserted = True
                    break
            if inserted:
                missing.remove(bi)

        # create new antennas
        for bi in missing:
            bi = int(bi)
            b = self.buildings[bi]
            pop = b.p_max
            feasible = [t for t in range(4) if ant_capacity(t) >= pop] or [2]
            tbest = min(feasible, key=lambda t: ant_cost(t, b.x, b.y, self.coords))
            sol.antennas.append(Antenna(int(tbest), bi, [bi]))

        ok, _ = self.eval.validate(sol)
        return sol if ok else None

    # operators
    def op_downgrade_type(self, sol: Solution) -> Optional[Solution]:
        if not sol.antennas:
            return None
        a = self.rng.choice(sol.antennas)
        load = self._load(a)
        best_t = a.t
        best_c = None

        candidates = [0, 1, 2, 3]
        self.rng.shuffle(candidates)

        for t in candidates:
            if ant_capacity(t) < load:
                continue
            old_t = a.t
            a.t = t
            if not all(self._in_range(a, bi) for bi in a.buildings):
                a.t = old_t
                continue
            site_b = self.buildings[a.site]
            c = ant_cost(a.t, site_b.x, site_b.y, self.coords)
            if best_c is None or c < best_c:
                best_c = c
                best_t = t

        a.t = best_t
        return sol

    def op_recenter_site_to_member(self, sol: Solution) -> Optional[Solution]:
        if not sol.antennas:
            return None
        a = self.rng.choice(sol.antennas)
        if len(a.buildings) <= 1:
            return None
        new_site = int(self.rng.choice(a.buildings))
        old_site = a.site
        a.site = new_site
        if not all(self._in_range(a, bi) for bi in a.buildings):
            a.site = old_site
            return None
        return sol

    def op_move_one_building(self, sol: Solution) -> Optional[Solution]:
        if len(sol.antennas) < 2:
            return None
        src = self.rng.choice(sol.antennas)
        if len(src.buildings) <= 1:
            return None
        dst = self.rng.choice(sol.antennas)
        if dst is src:
            return None

        bi = int(self.rng.choice(src.buildings))
        if not self._in_range(dst, bi):
            return None
        if self._load(dst) + self.buildings[bi].p_max > ant_capacity(dst.t):
            return None

        src.buildings.remove(bi)
        dst.buildings.append(bi)
        if not src.buildings:
            return None
        return sol

    def op_swap_two_buildings(self, sol: Solution) -> Optional[Solution]:
        if len(sol.antennas) < 2:
            return None
        a1 = self.rng.choice(sol.antennas)
        a2 = self.rng.choice(sol.antennas)
        if a1 is a2 or not a1.buildings or not a2.buildings:
            return None
        b1 = int(self.rng.choice(a1.buildings))
        b2 = int(self.rng.choice(a2.buildings))
        if b1 == b2:
            return None
        if not self._in_range(a1, b2) or not self._in_range(a2, b1):
            return None

        load1 = self._load(a1) - self.buildings[b1].p_max + self.buildings[b2].p_max
        load2 = self._load(a2) - self.buildings[b2].p_max + self.buildings[b1].p_max
        if load1 > ant_capacity(a1.t) or load2 > ant_capacity(a2.t):
            return None

        i1 = a1.buildings.index(b1)
        i2 = a2.buildings.index(b2)
        a1.buildings[i1] = b2
        a2.buildings[i2] = b1
        return sol

    def op_remove_antenna_and_repair(self, sol: Solution) -> Optional[Solution]:
        if len(sol.antennas) <= 1:
            return None
        idx = self.rng.randrange(len(sol.antennas))
        sol.antennas.pop(idx)
        return self._repair_exact_cover(sol)

    def improve(self, sol: Solution, time_budget_sec: float) -> Solution:
        best = sol.clone()
        ok, _ = self.eval.validate(best)
        if not ok:
            repaired = self._repair_exact_cover(best.clone())
            if repaired is None:
                return sol
            best = repaired

        best_cost = self.eval.cost(best)
        t_end = time.time() + time_budget_sec

        while time.time() < t_end:
            op = self.bandit.select()
            cand = best.clone()

            changed = None
            if op == "downgrade_type":
                changed = self.op_downgrade_type(cand)
            elif op == "recenter_site_to_member":
                changed = self.op_recenter_site_to_member(cand)
            elif op == "move_one_building":
                changed = self.op_move_one_building(cand)
            elif op == "swap_two_buildings":
                changed = self.op_swap_two_buildings(cand)
            elif op == "remove_antenna_and_repair":
                changed = self.op_remove_antenna_and_repair(cand)

            if changed is None:
                self.bandit.update(op, -1.0)
                continue

            ok, _ = self.eval.validate(changed)
            if not ok:
                self.bandit.update(op, -2.0)
                continue

            c_cost = self.eval.cost(changed)
            delta = best_cost - c_cost
            if delta > 0:
                best = changed
                best_cost = c_cost
                self.bandit.update(op, float(delta))
            else:
                self.bandit.update(op, -0.25)

        return best


# -----------------------------
# I/O helpers
# -----------------------------

def load_dataset(path: str) -> Tuple[List[Building], np.ndarray, np.ndarray]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    buildings_raw = data["buildings"]
    buildings: List[Building] = []

    bx = np.empty(len(buildings_raw), dtype=np.int32)
    by = np.empty(len(buildings_raw), dtype=np.int32)

    for i, b in enumerate(buildings_raw):
        p_max = int(max(b["populationPeakHours"], b["populationOffPeakHours"], b["populationNight"]))
        buildings.append(Building(int(b["id"]), int(b["x"]), int(b["y"]), p_max))
        bx[i] = int(b["x"])
        by[i] = int(b["y"])

    return buildings, bx, by


def solution_to_json(sol: Solution, buildings: List[Building]) -> dict:
    out = {"antennas": []}
    for a in sol.antennas:
        site_b = buildings[a.site]
        out["antennas"].append({
            "type": str(ANTENNA_TYPES[a.t]["name"]),
            "x": int(site_b.x),
            "y": int(site_b.y),
            "buildings": sorted(int(buildings[bi].id) for bi in a.buildings),
        })
    return out


def json_to_solution(obj: dict, buildings: List[Building]) -> Optional[Solution]:
    id_to_idx = {b.id: i for i, b in enumerate(buildings)}
    coord_to_idx = {(b.x, b.y): i for i, b in enumerate(buildings)}

    ants = []
    for a in obj.get("antennas", []):
        tname = a.get("type")
        if tname not in NAME_TO_TYPE:
            return None
        t = NAME_TO_TYPE[tname]
        x = int(a.get("x"))
        y = int(a.get("y"))
        if (x, y) not in coord_to_idx:
            return None
        site = coord_to_idx[(x, y)]
        b_ids = a.get("buildings", [])
        b_idx = []
        for bid in b_ids:
            bid = int(bid)
            if bid not in id_to_idx:
                return None
            b_idx.append(int(id_to_idx[bid]))
        if not b_idx:
            return None
        ants.append(Antenna(int(t), int(site), b_idx))

    if not ants:
        return None
    return Solution(ants)


def try_load_solution(path: str, buildings: List[Building], evaluator: Evaluator) -> Optional[Solution]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        sol = json_to_solution(obj, buildings)
        if sol is None:
            return None
        ok, _ = evaluator.validate(sol)
        return sol if ok else None
    except Exception:
        return None


# -----------------------------
# Worker for dataset (parallel 3..6)
# -----------------------------

def solve_one_dataset(name: str, k: int, use_cuda: bool, time_budget: float, seed: int) -> Tuple[int, int, int]:
    """
    Returns: (k, final_cost, improved_flag)
    improved_flag = 1 if final_cost < start_cost else 0
    """
    in_path = f"./datasets/{name}.json"
    out_path = f"./solutions/solution_{k}.json"

    if not os.path.exists(in_path):
        return (k, 0, 0)

    buildings, bx, by = load_dataset(in_path)
    dist_sq = compute_dist_sq_matrix(bx, by, use_cuda=use_cuda)
    evaluator = Evaluator(buildings, dist_sq)
    neighbors_by_type = {t: build_neighbors(dist_sq, ant_range_sq(t)) for t in range(4)}

    greedy_sol = greedy_construct(buildings, dist_sq, neighbors_by_type)
    ok, _ = evaluator.validate(greedy_sol)
    if not ok:
        return (k, 0, 0)
    greedy_cost = evaluator.cost(greedy_sol)

    # start solution = best(valid existing, greedy)
    best = try_load_solution(out_path, buildings, evaluator)
    if best is None:
        start = greedy_sol
        start_cost = greedy_cost
    else:
        existing_cost = evaluator.cost(best)
        if greedy_cost < existing_cost:
            start = greedy_sol
            start_cost = greedy_cost
        else:
            start = best
            start_cost = existing_cost

    final = start
    final_cost = start_cost

    if time_budget > 0:
        improver = Improver(buildings, dist_sq, neighbors_by_type, seed=seed + k * 1000)
        cand = improver.improve(start, time_budget_sec=time_budget)
        ok, _ = evaluator.validate(cand)
        if ok:
            c_cost = evaluator.cost(cand)
            if c_cost < final_cost:
                final = cand
                final_cost = c_cost

    improved = 1 if final_cost < start_cost else 0

    ok, _ = evaluator.validate(final)
    if not ok:
        return (k, 0, 0)

    os.makedirs("./solutions", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(solution_to_json(final, buildings), f, indent=2, ensure_ascii=False)

    return (k, int(final_cost), int(improved))


# -----------------------------
# Main
# -----------------------------

def main():
    use_cuda = os.environ.get("USE_CUDA", "1").strip() != "0"
    time_budget = float(os.environ.get("TIME_BUDGET_SEC", "10"))
    seed = int(os.environ.get("SEED", "42"))
    max_workers = int(os.environ.get("MAX_WORKERS", "2"))

    os.makedirs("./solutions", exist_ok=True)

    # datasets 1..2 sequential (print in same simple format: improved always 0)
    for name, k in [("1_peaceful_village", 1), ("2_small_town", 2)]:
        kk, cost, imp = solve_one_dataset(name, k, use_cuda, time_budget=0.0, seed=seed)
        print(f"{kk} {cost} {imp}", flush=True)

    # datasets 3..6 parallel
    jobs = [("3_suburbia", 3), ("4_epitech", 4), ("5_isogrid", 5), ("6_manhattan", 6)]
    from concurrent.futures import ProcessPoolExecutor, as_completed

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(solve_one_dataset, name, k, use_cuda, time_budget, seed) for name, k in jobs]
        for fut in as_completed(futs):
            k, cost, improved = fut.result()
            # simple print
            print(f"{k} {cost} {improved}", flush=True)


if __name__ == "__main__":
    main()
