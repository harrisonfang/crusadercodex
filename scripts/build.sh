#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
rm -rf dist
mkdir dist
cp web/index.html web/styles.css dist/
cp -R assets dist/assets
