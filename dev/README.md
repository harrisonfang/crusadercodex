# Authoring a sprite pet

The shared v1 compiler and preview tools live in `dev/common/`. Original PNGs and their provenance READMEs live under `assets/<game>/<category>/<asset-name>/`. Each game keeps its source manifests in `dev/<game>/sources/`, where multiple pets can share them. The [MapleStory Slime recipe](maplestory/slime/recipe.json) selects and positions frames from three manifests to build the [install files](../assets/pets/).

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

## Collect a MapleStory asset

First check `dev/maplestory/sources/` for the asset. A new pet can reference `../sources/meso.json` in its recipe to reuse the checked-in coin frames and their placement origins.

For a new asset, create a source manifest. The bronze meso example below shows the fields needed for the first fetch. Its location is `dev/maplestory/sources/meso.json`. Use strings for the region and version, and give each sequence a name and its archive path.

```json
{
  "image_root": "../../../assets/maplestory/items/meso",
  "source": {"region": "GMS", "version": "83"},
  "animations": {
    "bronze": {"wz_path": "Item/Special/0900.img/09000000/iconRaw"}
  }
}
```

Run the MapleStory fetcher from the repository root with Python, `curl`, and network access.

```sh
python3 dev/maplestory/common/fetch_wz_sprites.py dev/maplestory/sources/meso.json
```

The fetcher resolves `image_root` relative to the manifest. It writes each numbered PNG under that root and fills in frame records in the same manifest. Each frame’s `file` is relative to `image_root`, so `bronze/0.png` resolves to `assets/maplestory/items/meso/bronze/0.png`. The records include original WZ origins, delays, dimensions, and PNG checksums. An absent game delay stays `null`. The fetcher caches archive responses in `dev/maplestory/sources/build/wz-cache/`. Pass `--refresh` to retrieve fresh responses. Record the game version and archive URL in the asset’s README. [Populated meso manifest](maplestory/sources/meso.json)

## Start another pet

1. **Collect originals and record their provenance.** Choose a character, region, and game build. Reuse existing source manifests or add one per asset. For a new game, keep its extractor in `dev/<game>/common/` and use the same source manifest format. [MapleStory example](#collect-a-maplestory-asset)
2. **Create a recipe.** Copy the example to `dev/<game>/<pet>/recipe.json`. Set the stable `pet.id`, name, description, output directory, and source manifest paths relative to the recipe. In each layer, put the sprite's original origin on a fixed anchor, then use integer scaling and nearest-neighbor sampling. Centering each tightly cropped frame separately can erase the game's bounce.
3. **Map source poses onto the runtime slots.** The [timing profile](common/timing_profile.json) lists the fixed hold of every slot. V1 is an eight-column, nine-row atlas of 192 × 208 px cells. The required counts, top to bottom, are **6, 8, 8, 4, 5, 8, 6, 6, 6**. There are 57 used slots; the 15 remaining cells must stay transparent. V2 additionally requires 16 pointer-look poses and is outside this compiler's scope. Number source sprites from **1** when discussing choices; the recipe's selectors start at **0**. Surface any repeated or omitted sprites during review. For example, this slime has seven move sprites: its eight-slot directional run repeats sprite 1, while its five-slot jump uses only 1, 4, 5, 6, 7.
4. **Match the feel of the original loop.** Preserve cyclic pose order and compare **time visible**, not slot counts. Add consecutive holds for the same sprite, including across the last-to-first boundary. On each bounce, first preserve the uniquely longest pose, then the other duration rankings if possible. Compare candidates that tie by minimizing the sum of squared differences in per-pose time shares. Show shares and signed percentage-point differences against the source, and flag unavoidable ties. For slime's standing sprites 1, 2, 3 the source holds are 200, 300, 250 ms: sprite 2 should read longest. Choosing idle **3, 3, 1, 1, 2, 2** gives holds of 2,340, 1,500, and 2,760 ms for poses 3, 1, and 2 respectively.
5. **Compose effects and check their boundaries.** Layers draw back to front. Use `null` to hide a layer on a slot. For translation, set the curve's start time, duration, and displacement; the compiler samples at the actual slot start times and rounds to pixels. The slime's bronze meso uses `ballistic` for gravity; its hit pose uses `exponential-stop` for knockback, while the Magic Claw layer stays fixed. Inspect the per-frame positions and velocities in `build_report.json`. Cropping fails the build by default. If a particular effect should clip, opt in on **that layer** and inspect the highlighted pixels in the source preview. For this slime the approved claw glow overhangs by up to five pixels on either side.
6. **Review the install files and the website build.** Inspect all nine states at 1×, the loop boundary, and the finished atlas. Place a new pet’s `pet.json` and `spritesheet.png` together in `pets/<game>/<pet>/` for release. Run `sh scripts/build.sh` and compare the deployed sheet under `dist/` with the reviewed sheet. Each pet contributes that single file to the website. The generated authoring previews and reports stay in `dev/<game>/<pet>/build/`.

To make a portable ZIP, stage `pet.json` and `spritesheet.png` together under a folder named for the manifest’s stable ID, such as `maplestory-slime/`. Name the archive `<pet-id>-v<design-revision>.zip`. For example, a twelfth design revision would be `maplestory-slime-v12.zip` containing `maplestory-slime/pet.json` and `maplestory-slime/spritesheet.png`. The manifest’s `spriteVersionNumber` identifies the Codex atlas format.

The slime source notes identify the GMS v83 art and Monster Book text, credit their owners, and list the commands to refresh the checked-in inputs. [Slime source notes](maplestory/slime/SOURCES.md)
