#!/usr/bin/env bash
# scripts/publish.sh — Build wheels for all targets and publish to PyPI
#
# Prerequisites:
#   pip install maturin twine
#   Set MATURIN_PYPI_TOKEN or have ~/.pypirc configured.
#
# Usage:
#   ./scripts/publish.sh               # publish to PyPI
#   ./scripts/publish.sh --test        # publish to TestPyPI first
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"

TEST_MODE=false
for arg in "$@"; do
    [[ "$arg" == "--test" ]] && TEST_MODE=true
done

cd "$PROJECT_ROOT"

echo "🚀  Publishing grapx to PyPI..."

if ! command -v maturin &>/dev/null; then
    pip install "maturin>=1.5,<2.0"
fi
if ! command -v twine &>/dev/null; then
    pip install twine
fi

# Clean previous builds
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Build source distribution
echo "Building sdist..."
maturin sdist --out "$DIST_DIR"

# Build wheel for current platform
echo "Building wheel for current platform..."
maturin build --release --out "$DIST_DIR"

echo ""
echo "Built artefacts:"
ls -lh "$DIST_DIR"

if $TEST_MODE; then
    echo ""
    echo "Uploading to TestPyPI..."
    twine upload --repository testpypi "$DIST_DIR"/*
    echo ""
    echo "✓  Published to TestPyPI."
    echo "   Verify: pip install --index-url https://test.pypi.org/simple/ grapx"
else
    echo ""
    echo "Uploading to PyPI..."
    twine upload "$DIST_DIR"/*
    echo ""
    echo "✓  Published to PyPI."
    echo "   Install: pip install grapx"
fi
