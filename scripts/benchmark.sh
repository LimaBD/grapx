#!/usr/bin/env bash
# scripts/benchmark.sh — Release build + run performance benchmark
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "⚡  Building grapx (release) and running benchmarks..."
cd "$PROJECT_ROOT"

if ! command -v maturin &>/dev/null; then
    pip install "maturin>=1.5,<2.0"
fi
pip install -q "pydantic>=2.0"

echo "Building optimised Rust extension..."
maturin develop --release

echo ""
python tests/bench.py
