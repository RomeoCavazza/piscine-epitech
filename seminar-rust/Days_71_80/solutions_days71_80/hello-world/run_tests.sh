#!/usr/bin/env bash
# Hello World - Automated Test Suite
# Runs all backend tests with optional coverage reporting

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "Hello World - Test Suite"
echo "========================="
echo ""

# Backend tests
echo "[1/2] Backend Tests (Rust)"
echo "--------------------------"
cd "$BACKEND_DIR"

if ! cargo test --quiet 2>&1 | grep -E "test result|running"; then
    echo "Error: Backend tests failed"
    exit 1
fi

TOTAL_TESTS=$(cargo test --quiet 2>&1 | grep "test result" | awk '{sum+=$4} END {print sum}')
echo ""
echo "Result: $TOTAL_TESTS tests passed"
echo ""

# Coverage (optional)
if command -v cargo-llvm-cov &> /dev/null; then
    echo "[2/2] Coverage Report"
    echo "---------------------"
    cargo llvm-cov --quiet --summary-only 2>&1 | tail -3
    echo ""
elif command -v cargo-tarpaulin &> /dev/null; then
    echo "[2/2] Coverage Report"
    echo "---------------------"
    cargo tarpaulin --skip-clean --quiet --out Stdout 2>&1 | grep -E "coverage|lines covered"
    echo ""
else
    echo "[2/2] Coverage: Not available"
    echo "Install: nix-shell or cargo install cargo-llvm-cov"
    echo ""
fi

echo "========================="
echo "Test suite completed"
echo ""
