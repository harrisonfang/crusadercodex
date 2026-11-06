#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
rm -rf dist
mkdir dist
cp web/*.html web/*.css web/*.js dist/
cp -R assets dist/assets
