#!/usr/bin/env bash
# scripts/dev.sh — Install grapx in development mode (unoptimized, fast compile)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📦  Installing grapx in development mode..."
cd "$PROJECT_ROOT"

# Ensure maturin is available
if ! command -v maturin &>/dev/null; then
    echo "Installing maturin..."
    pip install "maturin>=1.5,<2.0"
fi

# Install pydantic (runtime dependency)
pip install "pydantic>=2.0"

# Build the Rust extension in-place (debug mode = fast compile)
maturin develop

echo ""
echo "✓  grapx is ready. Run 'import grapx' in Python."
