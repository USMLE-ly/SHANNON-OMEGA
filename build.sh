#!/bin/sh
set -e
cd luxor-hub
rm -rf node_modules/.vite node_modules/.cache
NODE_OPTIONS="--max-old-space-size=2048" npm install --ignore-scripts=false
NODE_OPTIONS="--max-old-space-size=2048" npx vite build
mkdir -p ../dist
cp -r dist/. ../dist/
