#!/usr/bin/env bash
# Copy the fairland-modbus device library into the integration.
#
# The integration bundles its own copy of the library, so it installs
# without waiting for a release on PyPI. Run this after a change in
# hardes-bv/python-fairland-modbus to pick it up.
#
# Usage: scripts/vendor_fairland_modbus.sh [git URL or path] [ref]
set -euo pipefail

SOURCE="${1:-https://github.com/hardes-bv/python-fairland-modbus.git}"
REF="${2:-main}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$ROOT_DIR/custom_components/fairland_modbus/vendor"
CLONE_DIR="$(mktemp -d)"
trap 'rm -rf "$CLONE_DIR"' EXIT

git clone -q "$SOURCE" "$CLONE_DIR"
git -C "$CLONE_DIR" checkout -q "$REF"
COMMIT="$(git -C "$CLONE_DIR" rev-parse HEAD)"

rm -rf "$VENDOR_DIR/fairland_modbus"
mkdir -p "$VENDOR_DIR"
cp -R "$CLONE_DIR/src/fairland_modbus" "$VENDOR_DIR/fairland_modbus"
find "$VENDOR_DIR/fairland_modbus" -name "__pycache__" -type d -prune -exec rm -rf {} +
cp "$CLONE_DIR/LICENSE" "$VENDOR_DIR/fairland_modbus/LICENSE"
printf '"""A bundled copy of the fairland-modbus device library."""\n' > "$VENDOR_DIR/__init__.py"
printf '%s\n' "$COMMIT" > "$VENDOR_DIR/fairland_modbus/VENDORED_COMMIT"

echo "Vendored fairland-modbus at $COMMIT"
