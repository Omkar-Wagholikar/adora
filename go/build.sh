#!/usr/bin/env bash
set -euo pipefail

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Output directory for built artifacts
OUTDIR="../brags/bin"
mkdir -p "$OUTDIR"

# The module has no cgo (no `import "C"`, all deps are pure Go), so this
# doesn't need to be enabled -- and disabling it lets GOOS/GOARCH below
# cross-compile a fully static binary without a matching C cross-toolchain,
# which is what makes building for macOS/Windows from a single Linux
# runner possible.
export CGO_ENABLED=0

EXT=""
if [ "${GOOS:-}" = "windows" ]; then
  EXT=".exe"
fi

echo "Building Go binary for ${GOOS:-$(go env GOOS)}/${GOARCH:-$(go env GOARCH)}..."

cp -r ./static "$OUTDIR/static"
cp -r ./pythonFiles "$OUTDIR/pythonFiles"
go build -o "$OUTDIR/server_executable$EXT" "./main.go"
echo "Build complete: $OUTDIR/server_executable$EXT"
