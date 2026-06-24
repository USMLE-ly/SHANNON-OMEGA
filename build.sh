#!/bin/sh
set -e
cd luxor-hub
rm -rf node_modules/.vite node_modules/.cache

NODE_OPTIONS="--max-old-space-size=768" npm install --ignore-scripts=false

if [ -f node_modules/@esbuild/linux-x64/bin/esbuild ]; then
  cp node_modules/@esbuild/linux-x64/bin/esbuild /tmp/esbuild-bin
  chmod +x /tmp/esbuild-bin
  export ESBUILD_BINARY_PATH=/tmp/esbuild-bin
fi

# GOMEMLIMIT caps Go binary at 350MB, GOGC=25 forces frequent GC
# Node limited to 768MB to leave room for Go
GOMEMLIMIT=350MiB GOGC=25 NODE_OPTIONS="--max-old-space-size=768" UV_THREADPOOL_SIZE=2 npx vite build

mkdir -p ../dist
cp -r dist/. ../dist/
