{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Rust toolchain complète
    rustc
    cargo
    rustfmt
    clippy
    rust-analyzer
    
    # LLVM tools pour coverage
    llvm_18
    llvmPackages_18.bintools
    llvmPackages_18.libllvm
    
    # Database tools
    postgresql
    
    # Node.js pour frontend
    nodejs_20
    
    # System tools essentiels
    openssl
    openssl.dev
    pkg-config
    gcc
    gnumake
    cmake
    zlib
    zlib.dev
    curl
    git
    
    # Test et coverage tools
    cargo-nextest  # Fast test runner
    cargo-watch    # Auto-recompile on save
    cargo-tarpaulin # Coverage tool
  ];

  # Variables d'environnement pour coverage
  LLVM_COV = "${pkgs.llvmPackages_18.bintools}/bin/llvm-cov";
  LLVM_PROFDATA = "${pkgs.llvmPackages_18.bintools}/bin/llvm-profdata";
  
  # Variables pour compilation
  PKG_CONFIG_PATH = "${pkgs.openssl.dev}/lib/pkgconfig:${pkgs.zlib.dev}/lib/pkgconfig";
  OPENSSL_DIR = "${pkgs.openssl.dev}";
  OPENSSL_LIB_DIR = "${pkgs.openssl.out}/lib";
  OPENSSL_INCLUDE_DIR = "${pkgs.openssl.dev}/include";

  shellHook = ''
    echo "Hello World - Development Environment"
    echo "Rust $(rustc --version | cut -d' ' -f2) | Node $(node --version) | LLVM $(llvm-config --version)"
    echo ""
    echo "Available tools: cargo test, cargo tarpaulin, cargo llvm-cov"
    echo "Run './run_tests.sh' for full test suite"
    echo ""
  '';
}
