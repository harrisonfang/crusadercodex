#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
rm -rf _site
mkdir _site
cp web/index.html web/styles.css _site/
cp -R assets _site/assets
