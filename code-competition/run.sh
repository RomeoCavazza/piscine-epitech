#!/usr/bin/env bash
set -euo pipefail

# run.sh: crée un venv, installe deps, exécute.
# Sur NixOS: on peut lancer via nix-shell si dispo, sinon on tente python3 direct.

USE_CUDA="${USE_CUDA:-1}"

if command -v nix-shell >/dev/null 2>&1; then
  echo "[INFO] nix-shell détecté: exécution dans un environnement Nix avec python/pip."
  nix-shell -p python3 python3Packages.pip python3Packages.virtualenv \
    --run "bash -lc '
      set -euo pipefail
      python3 -m venv .venv
      source .venv/bin/activate
      python -m pip install --upgrade pip wheel
      python -m pip install numpy numba
      echo \"[INFO] USE_CUDA=${USE_CUDA}\"
      USE_CUDA=${USE_CUDA} python god_tier_cuda.py
    '"
else
  echo "[WARN] nix-shell non trouvé, utilisation du python système."
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip wheel
  python -m pip install numpy numba
  echo "[INFO] USE_CUDA=${USE_CUDA}"
  USE_CUDA="${USE_CUDA}" python god_tier_cuda.py
fi
