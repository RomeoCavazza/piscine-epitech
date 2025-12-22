{
  description = "Environnement Python HPC pour Challenge (CUDA + Numba)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            cudaSupport = true;
          };
        };

        # CORRECTION ICI : On retire 'cudatoolkit' de cette liste
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          numpy
          pandas
          numba
          scikit-learn
          # cudatoolkit a été retiré ici, car ce n'est pas un module Python !
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          name = "cuda-challenge-env";

          # Il est bien présent ici (c'est correct)
          buildInputs = with pkgs; [
            pythonEnv
            cudatoolkit 
            linuxPackages.nvidia_x11
            nvtopPackages.nvidia
          ];

          shellHook = ''
            export CUDA_PATH=${pkgs.cudatoolkit}
            export LD_LIBRARY_PATH=${pkgs.linuxPackages.nvidia_x11}/lib:${pkgs.ncurses5}/lib:${pkgs.libz}/lib:${pkgs.cudatoolkit}/lib:$LD_LIBRARY_PATH
            export NUMBAPRO_NVVM=${pkgs.cudatoolkit}/nvvm/lib64/libnvvm.so
            export NUMBAPRO_LIBDEVICE=${pkgs.cudatoolkit}/nvvm/libdevice

            clear
            echo "🚀 Environnement HPC prêt pour le Challenge !"
            echo "---------------------------------------------"
            echo "🐍 Python : $(python --version)"
            # Petite sécurité au cas où nvidia-smi n'est pas dans le PATH par défaut
            echo "🔌 GPU    : $(${pkgs.linuxPackages.nvidia_x11}/bin/nvidia-smi --query-gpu=name --format=csv,noheader || echo 'GPU détecté mais nvidia-smi silencieux')"
            echo "---------------------------------------------"
            echo "💡 Astuce : Tape 'nvtop' pour voir l'usage GPU en temps réel."
          '';
        };
      }
    );
}