#!/usr/bin/env bash
# scripts/build.sh — Build grapx Rust extension in release mode
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔨  Building grapx (release mode)..."
cd "$PROJECT_ROOT"

if ! command -v maturin &>/dev/null; then
    echo "Installing maturin..."
    pip install "maturin>=1.5,<2.0"
fi

maturin develop --release

echo ""
echo "✓  Build complete. The Rust extension is installed."
