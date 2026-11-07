# Scripts

Run `sh scripts/build.sh` from the repository root to assemble the website in `dist/`.
The script starts with an empty output directory, copies the website and its
`assets/gms-v102/` UI artwork, and publishes each pet's final sprite sheet at
`assets/pets/<pet-id>/spritesheet.png`. When the site uses a new artwork directory,
add its path to the build script. Pet manifests and source frames stay in the repository.
