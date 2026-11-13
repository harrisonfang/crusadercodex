# Website

Static HTML, CSS, and JavaScript displaying the book at its original 499 × 370 size.
The nine right-side tabs select a chapter; its pages remain blank. Use the mouse,
Up/Down arrow keys, Home, or End. Chapter and page state stays in memory.
Small windows scroll instead of resizing the artwork.

The build writes the site to `dist/`. It includes the game UI artwork and each finished pet's `pets/<game>/<pet>/spritesheet.png`.

Run these commands from the repository root to preview the site.

```sh
sh web/build.sh
python3 -m http.server 8000 --directory dist
```

See [Crusader Codex navigation](codex-behavior.md) for the original game's bookmarks, cards and Sets, and which behaviors the pet gallery keeps.
