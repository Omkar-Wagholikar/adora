#!/bin/bash
# go/build.sh

go build -o ../your_package/libgo.so -buildmode=c-shared main.go
