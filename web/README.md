# Website

Static HTML, CSS, and JavaScript displaying the book at its original 499 × 370 size.
The nine right-side tabs select a chapter; its pages remain blank. Use the mouse,
Up/Down arrow keys, Home, or End. Chapter and page state stays in memory.
Small windows scroll instead of resizing the artwork.

To preview from the repository root:

```sh
sh scripts/build.sh
python3 -m http.server 8000 --directory dist
```
