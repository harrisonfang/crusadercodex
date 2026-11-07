# Authoring a sprite pet

The shared v1 compiler and preview tools live in `dev/common/`. Each pet has a recipe under `dev/<game>/<pet>/`. Original game frames and their metadata live under `assets/<game>/<category>/<asset-name>/`, where each asset README records its game version and download source. The [MapleStory Slime recipe](maplestory/slime/recipe.json) builds the two [install files](../assets/pets/) from these originals.

## Reproduce the shipped slime

From the repository root, use Python 3.11 or newer (reviewed on 3.12). Set up the environment once:

```sh
python3 -m venv dev/.venv
. dev/.venv/bin/activate
python -m pip install -r dev/common/requirements.txt
```

With Pillow installed, both commands run offline. The test suite finds the released bundle by its manifest ID, rebuilds from the recipe, and compares the manifest and every RGBA pixel.

```sh
python dev/common/build_source_preview.py dev/maplestory/slime/recipe.json
python -m unittest discover -s dev/common
```

Open `dev/maplestory/slime/build/source-preview.html` in a browser. All nine animations play independently at the app's frame timings. Pause and step one row to inspect a repeated pose, switch its source sprite, or check which pixels cross a cell boundary. Reset restores that row's recipe. Edits in the browser are temporary: record accepted changes in the recipe and rerun the command. The generated `preview.html` in the same folder plays the **finished atlas**; use it to see exactly what will ship. For a build without the source comparison, run `python dev/common/build_pet.py dev/maplestory/slime/recipe.json`.

## Start another pet

1. **Collect originals and record their provenance.** Choose a character, region and game build. For MapleStory, copy the [slime fetch config](maplestory/slime/fetch-slime.json), set its WZ animation paths and destination asset directory, then run `python dev/common/fetch_wz_sprites.py path/to/fetch.json` with network access and `curl`. Put each asset in its own folder, such as `assets/maplestory/mobs/slime/`, `assets/maplestory/items/meso/` or `assets/maplestory/skills/magic-claw/`. Use the fetch config’s animation keys for the directories immediately above the numbered PNGs (for example, `hit/0.png` or `bronze/0.png`). Record the version and archive URL in the asset README. The [slime manifest](../assets/maplestory/mobs/slime/animations.json) shows how to represent native PNGs, original placement origins, delays and checksums for this or another game. Keep an unspecified delay as `null`.
2. **Create a recipe.** Copy the example to `dev/<game>/<pet>/recipe.json`. Set the stable `pet.id`, name, description, output directory, and source manifest paths. Paths resolve relative to the containing JSON file. In each layer, put the sprite's original origin on a fixed anchor, then use integer scaling and nearest-neighbor sampling. Centering each tightly cropped frame separately can erase the game's bounce.
3. **Map source poses onto the runtime slots.** The [timing profile](common/timing-profile.json) lists the fixed hold of every slot. V1 is an eight-column, nine-row atlas of 192 × 208 px cells. The required counts, top to bottom, are **6, 8, 8, 4, 5, 8, 6, 6, 6**. There are 57 used slots; the 15 remaining cells must stay transparent. V2 additionally requires 16 pointer-look poses and is outside this compiler's scope. Number source sprites from **1** when discussing choices; the recipe's selectors start at **0**. Surface any repeated or omitted sprites during review. For example, this slime has seven move sprites: its eight-slot directional run repeats sprite 1, while its five-slot jump uses only 1, 4, 5, 6, 7.
4. **Match the feel of the original loop.** Preserve cyclic pose order and compare **time visible**, not slot counts. Add consecutive holds for the same sprite, including across the last-to-first boundary. On each bounce, first preserve the uniquely longest pose, then the other duration rankings if possible. Compare candidates that tie by minimizing the sum of squared differences in per-pose time shares. Show shares and signed percentage-point differences against the source, and flag unavoidable ties. For slime's standing sprites 1, 2, 3 the source holds are 200, 300, 250 ms: sprite 2 should read longest. Choosing idle **3, 3, 1, 1, 2, 2** gives holds of 2,340, 1,500, and 2,760 ms for poses 3, 1, and 2 respectively.
5. **Compose effects and check their boundaries.** Layers draw back to front. Use `null` to hide a layer on a slot. For translation, set the curve's start time, duration, and displacement; the compiler samples at the actual slot start times and rounds to pixels. The slime's bronze meso uses `ballistic` for gravity; its hit pose uses `exponential-stop` for knockback, while the Magic Claw layer stays fixed. Inspect the per-frame positions and velocities in `build-report.json`. Cropping fails the build by default. If a particular effect should clip, opt in on **that layer** and inspect the highlighted pixels in the source preview. For this slime the approved claw glow overhangs by up to five pixels on either side.
6. **Review the install files and the website build.** Inspect all nine states at 1×, the loop boundary, and the finished atlas. Copy `pet.json` and `spritesheet.png` into `assets/pets/<game>/<pet>/` so they can be installed together from the repository. Run `sh scripts/build.sh` and compare the deployed sheet at its matching path under `dist/` with the reviewed sheet. Each pet contributes that single file to the website. The generated authoring previews and reports stay in `dev/<game>/<pet>/build/`.

To make a portable ZIP, stage `pet.json` and `spritesheet.png` together under a folder named for the manifest’s stable ID, such as `maplestory-slime/`. Name the archive `<pet-id>-v<design-revision>.zip`. For example, a twelfth design revision would be `maplestory-slime-v12.zip` containing `maplestory-slime/pet.json` and `maplestory-slime/spritesheet.png`. The manifest’s `spriteVersionNumber` identifies the Codex atlas format.

See the [slime source notes](maplestory/slime/SOURCES.md) for the exact GMS v83 art and Monster Book text, ownership, and commands to fetch fresh copies without overwriting the checked-in inputs.
