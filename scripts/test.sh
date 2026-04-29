#!/usr/bin/env bash
# scripts/test.sh — Build (debug) and run the full test suite
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧪  Running grapx test suite..."
cd "$PROJECT_ROOT"

# Ensure dependencies
if ! command -v maturin &>/dev/null; then
    pip install "maturin>=1.5,<2.0"
fi
pip install -q "pydantic>=2.0" pytest pytest-cov

# Build the extension (debug for fast iteration)
echo "Building Rust extension..."
maturin develop

echo ""
echo "Running tests..."
python -m pytest tests/ -v --tb=short "$@"
