#!/bin/bash
set -e
echo "[BUILD] Copying pre-built luxor-hub/dist/ to root dist/"
mkdir -p dist
cp -r luxor-hub/dist/. dist/
echo "[BUILD] dist ready"
