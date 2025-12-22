{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:

pkgs.mkShell {
  name = "god-tier-blackwell-final";

  packages = with pkgs; [
    cudatoolkit
    (python311.withPackages (ps: with ps; [
      numpy
      scipy
      pycuda
      tqdm
      colorama
    ]))
  ];

  shellHook = ''
    # --- CONFIGURATION BLACKWELL (RTX 5070 Ti) ---

    # 1. Nettoyage
    unset LD_LIBRARY_PATH

    # 2. On pointe vers le driver SYSTÈME (Kernel 590) pour l'exécution
    export LD_LIBRARY_PATH=/run/opengl-driver/lib:/run/opengl-driver/lib64:${pkgs.cudatoolkit}/lib

    # 3. On pointe vers le toolkit NIX pour la compilation (NVCC)
    export CUDA_HOME=${pkgs.cudatoolkit}

    # 4. Variables Numba (Minimalistes et Performantes)
    # On laisse Numba détecter l'architecture (Compute Capability 10.x pour Blackwell)
    export NUMBAPRO_NVVM=${pkgs.cudatoolkit}/nvvm/lib64/libnvvm.so
    export NUMBAPRO_LIBDEVICE=${pkgs.cudatoolkit}/nvvm/libdevice

    echo "🚀 BLACKWELL ENGINE READY."
    echo "   Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"
    echo "   CUDA:   $(nvidia-smi --query-gpu=compute_cap --format=csv,noheader) (Architecture)"
  '';
}