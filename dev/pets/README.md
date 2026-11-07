# Authoring a sprite pet

The [MapleStory Slime recipe](recipes/maplestory-slime/recipe.json) is a complete worked example: original PNGs and game metadata go in, and two install files come out. The compiler handles **Codex sprite format v1**. The repository's website build copies `assets/`; the authoring source under `dev/` is browsable on GitHub, and the generated preview runs locally.

## Reproduce the shipped slime

From the repository root, use Python 3.11 or newer (reviewed on 3.12). Set up the environment once:

```sh
python3 -m venv dev/pets/.venv
. dev/pets/.venv/bin/activate
python -m pip install -r dev/pets/requirements.txt
```

The pinned Pillow dependency is the only package. Once installed, the following commands work offline. The two `cmp` commands print nothing on a byte-for-byte match:

```sh
python dev/pets/tools/build_source_preview.py dev/pets/recipes/maplestory-slime/recipe.json
python -m unittest discover -s dev/pets/tools
cmp dev/pets/build/maplestory-slime/pet.json assets/pets/maplestory-slime/pet.json
cmp dev/pets/build/maplestory-slime/spritesheet.png assets/pets/maplestory-slime/spritesheet.png
```

Open `dev/pets/build/maplestory-slime/source-preview.html` in a browser. All nine animations play independently at the app's frame timings. Pause and step one row to inspect a repeated pose, switch its source sprite, or check which pixels cross a cell boundary. Reset restores that row's recipe. Edits in the browser are temporary: record accepted changes in the recipe and rerun the command. The generated `preview.html` in the same folder plays the **finished atlas**; use it to see exactly what will ship. For a build without the source comparison, run `python dev/pets/tools/build_pet.py dev/pets/recipes/maplestory-slime/recipe.json`.

## Start another pet

1. **Collect originals and identify the version.** Pick the game, region/build, and character ID. Prefer transparent native-resolution frames with placement origins and source frame delays. For MapleStory, copy [fetch-slime.json](recipes/maplestory-slime/fetch-slime.json), set the WZ paths and output directory, and run `python dev/pets/tools/fetch_wz_sprites.py path/to/fetch.json` (requires network and `curl`). [fetch-effects.json](recipes/maplestory-slime/fetch-effects.json) demonstrates a second source for overlays. The fetcher writes the lossless frames, their checksums, and an `animations.json` manifest. Keep the selected frames and manifest with the recipe; leave the raw HTTP cache in the build folder. If a source does not specify a delay, keep it unknown. For another game, use its own extractor and follow the same [source manifest layout](recipes/maplestory-slime/sources/slime/animations.json).
2. **Create a recipe.** Copy the example to `dev/pets/recipes/<pet-id>/recipe.json`. Set the stable `pet.id`, name, description, output directory, and source manifest paths. Paths resolve relative to the containing JSON file. In each layer, put the sprite's original origin on a fixed anchor, then use integer scaling and nearest-neighbor sampling. Centering each tightly cropped frame separately can erase the game's bounce.
3. **Map source poses onto the runtime slots.** The [timing profile](timing-profile.json) lists the fixed hold of every slot. V1 is an eight-column, nine-row atlas of 192 × 208 px cells. The required counts, top to bottom, are **6, 8, 8, 4, 5, 8, 6, 6, 6**. There are 57 used slots; the 15 remaining cells must stay transparent. V2 additionally requires 16 pointer-look poses and is outside this compiler's scope. Number source sprites from **1** when discussing choices; the recipe's selectors start at **0**. Surface any repeated or omitted sprites during review. For example, this slime has seven move sprites: its eight-slot directional run repeats sprite 1, while its five-slot jump uses only 1, 4, 5, 6, 7.
4. **Match the feel of the original loop.** Preserve cyclic pose order and compare **time visible**, not slot counts. Add consecutive holds for the same sprite, including across the last-to-first boundary. On each bounce, first preserve the uniquely longest pose, then the other duration rankings if possible. Compare candidates that tie by minimizing the sum of squared differences in per-pose time shares. Show shares and signed percentage-point differences against the source, and flag unavoidable ties. For slime's standing sprites 1, 2, 3 the source holds are 200, 300, 250 ms: sprite 2 should read longest. Choosing idle **3, 3, 1, 1, 2, 2** gives holds of 2,340, 1,500, and 2,760 ms for poses 3, 1, and 2 respectively.
5. **Compose effects and check their boundaries.** Layers draw back to front. Use `null` to hide a layer on a slot. For translation, set the curve's start time, duration, and displacement; the compiler samples at the actual slot start times and rounds to pixels. The slime's bronze meso uses `ballistic` for gravity; its hit pose uses `exponential-stop` for knockback, while the Magic Claw layer stays fixed. Inspect the per-frame positions and velocities in `build-report.json`. Cropping fails the build by default. If a particular effect should clip, opt in on **that layer** and inspect the highlighted pixels in the source preview. For this slime the approved claw glow overhangs by up to five pixels on either side.
6. **Review and publish the two files.** Inspect all nine states at 1×, check the loop boundary and the finished atlas, then copy **only** `pet.json` and `spritesheet.png` into `assets/pets/<pet-id>/`. Run `sh scripts/build.sh` and verify those files under `dist/assets/pets/<pet-id>/`. Commit the recipe and inputs under `dev/pets/`; keep generated reports, comparison HTML and scratch work out of `assets/` and out of Git.

For a portable ZIP, archive the folder containing the two files. Use `<pet-id>-v<design-revision>.zip` for the download name; `spriteVersionNumber` in the manifest identifies the separate Codex atlas format. For example, from `assets/pets/`, `zip -X maplestory-slime-v12.zip maplestory-slime/pet.json maplestory-slime/spritesheet.png` would package a hypothetical twelfth revision.

See the [slime source notes](recipes/maplestory-slime/SOURCES.md) for the exact GMS v83 art and Monster Book text, ownership, and commands to fetch fresh copies without overwriting the checked-in inputs.
