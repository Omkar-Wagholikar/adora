set -euo pipefail

OUT_DIR="../brags/bin"
mkdir -p $OUT_DIR

# Linux (x86_64)
GOOS=linux GOARCH=amd64 go build -buildmode=c-shared -o $OUT_DIR/filewatcher_linux_amd64.so ./main.go

# macOS (x86_64)
GOOS=darwin GOARCH=amd64 go build -buildmode=c-shared -o $OUT_DIR/filewatcher_darwin_amd64.dylib ./main.go

# macOS (ARM M1/M2)
GOOS=darwin GOARCH=arm64 go build -buildmode=c-shared -o $OUT_DIR/filewatcher_darwin_arm64.dylib ./main.go

# Windows (x86_64)
GOOS=windows GOARCH=amd64 go build -buildmode=c-shared -o $OUT_DIR/filewatcher_windows_amd64.dll ./main.go

