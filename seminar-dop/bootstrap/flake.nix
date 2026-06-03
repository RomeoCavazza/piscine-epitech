{
  description = "Epitech Seminar DOP - Bernstein (Kubernetes)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            minikube
            kubectl
            k9s
            kubernetes-helm
          ];
 
          shellHook = ''
            # Clean terminal and print a professional header
            echo -e "\033[1;36m"
            cat << "EOF"
  ____  _____ ____  _   _ ____ _____ _____ ___ _   _ 
 | __ )| ____|  _ \| \ | / ___|_   _| ____|_ _| \ | |
 |  _ \|  _| | |_) |  \| \___ \ | | |  _|  | ||  \| |
 | |_) | |___|  _ <| |\  |___) || | | |___ | || |\  |
 |____/|_____|_| \_\_| \_|____/ |_| |_____|___|_| \_|
                                                     
   Epitech DevOps Seminar - Symphony of Containers   
EOF
            echo -e "\033[0m"

            # Check environment status
            echo -e "\033[1;33m--- ENVIRONMENT STATUS ---\033[0m"
            
            # Helper function to check package
            check_tool() {
              if command -v $1 >/dev/null 2>&1; then
                version=""
                if [ "$1" = "minikube" ]; then
                  version=$(minikube version --short 2>/dev/null || minikube version 2>/dev/null | head -n 1)
                elif [ "$1" = "kubectl" ]; then
                  version=$(kubectl version --client --short 2>/dev/null || kubectl version --client 2>/dev/null | head -n 1)
                else
                  version=$($1 --version 2>/dev/null | head -n 1 || $1 version 2>/dev/null | head -n 1)
                fi
                echo -e "  \033[0;32m✓\033[0m \033[1m$1\033[0m: $version"
              else
                echo -e "  \033[0;31m✗ $1\033[0m (not installed)"
              fi
            }

            check_tool minikube
            check_tool kubectl
            check_tool k9s
            check_tool helm

            echo ""
            echo -e "\033[1;33m--- DOCKER ENGINE STATUS ---\033[0m"
            if docker info >/dev/null 2>&1; then
              echo -e "  \033[0;32m✓\033[0m Docker daemon is running"
            else
              echo -e "  \033[0;31m✗\033[0m Docker daemon is NOT running or user not in docker group."
              echo -e "    Please run: \033[1msudo systemctl start docker\033[0m or check user groups."
            fi

            # Define useful Kubernetes developer aliases
            alias k="kubectl"
            alias kgp="kubectl get pods"
            alias kgs="kubectl get services"
            alias kgd="kubectl get deployments"
            alias kd="kubectl describe"
            alias kl="kubectl logs"
            alias kexec="kubectl exec -it"

            echo ""
            echo -e "\033[1;33m--- HANDY ALIASES ACTIVATED ---\033[0m"
            echo -e "  \033[1mk\033[0m     -> kubectl"
            echo -e "  \033[1mkgp\033[0m   -> kubectl get pods"
            echo -e "  \033[1mkgs\033[0m   -> kubectl get services"
            echo -e "  \033[1mkd\033[0m    -> kubectl describe"
            echo -e "  \033[1mkl\033[0m    -> kubectl logs"
            echo -e "  \033[1mk9s\033[0m   -> Launch Kubernetes TUI dashboard"
            
            echo ""
            echo -e "\033[1;35mQUICK START:\033[0m"
            echo -e "  1. Start cluster: \033[1;32mminikube start --driver=docker\033[0m"
            echo -e "  2. Deploy pod:    \033[1;32mkubectl apply -f hello-world.pod.yaml\033[0m"
            echo -e "  3. Check status:  \033[1;32mkgp\033[0m or run \033[1;32mk9s\033[0m"
            echo ""
          '';
        };
      });
}
