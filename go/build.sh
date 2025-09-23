#!/usr/bin/env bash
set -euo pipefail

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Output directory for built artifacts
OUTDIR="../brags/bin"
mkdir -p "$OUTDIR"

echo "Building Go shared library for Linux..."

# Enable cgo and build as shared object (.so)
# CGO_ENABLED=1 go build \
#   -buildmode=c-shared \
#   -o "$OUTDIR/libbrags.so" \
#   ./main.go
# echo "Build complete: $OUTDIR/libbrags.so"
# cp index.html "$OUTDIR/index.html"
cp -r ./static "$OUTDIR/static"
go build -o "$OUTDIR/server_executable" "./main.go"
echo "Build complete: $OUTDIR/server_executable"
