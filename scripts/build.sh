#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
rm -rf dist
mkdir -p dist/assets
cp web/*.html web/*.css web/*.js dist/

cp -R assets/gms-v102 dist/assets/

for sheet in assets/pets/*/spritesheet.png; do
  [ -f "$sheet" ] || continue
  mkdir -p "dist/${sheet%/*}"
  cp "$sheet" "dist/$sheet"
done
