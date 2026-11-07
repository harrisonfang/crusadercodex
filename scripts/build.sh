#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
rm -rf dist
mkdir -p dist/assets
cp web/*.html web/*.css web/*.js dist/

for ui in assets/gms-v102 assets/*/ui; do
  [ -d "$ui" ] || continue
  mkdir -p "dist/${ui%/*}"
  cp -R "$ui" "dist/$ui"
done

for sheet in assets/pets/*/spritesheet.png assets/pets/*/*/spritesheet.png; do
  [ -f "$sheet" ] || continue
  mkdir -p "dist/${sheet%/*}"
  cp "$sheet" "dist/$sheet"
done
