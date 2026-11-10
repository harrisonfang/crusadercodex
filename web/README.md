# Website

Static HTML, CSS, and JavaScript display the book at its original 499 × 370 size.
Small windows scroll. Home opens *Crusader Codex* at chapter 1, page 1. Choose
one of the nine tabs or use the Up/Down arrows, Home, or End to select a chapter.
Set opens *Set List* and hides the chapter tabs. Both sections have empty pages
and a disabled Back button until there are items to open.

The banners and bookmarks use original GMS v102 artwork. The [v102 Home screenshot](https://mapleglobalnews.wordpress.com/2011/10/28/gms-v-102-rise-of-fellowship/)
and [in-game Set List](https://www.youtube.com/watch?v=MHhzQ4DmX6Q&t=186s) show their placement.
See the [regular card grid and pagination](https://www.youtube.com/watch?v=_E1hfM1feEo&t=51s),
[opening an individual card](https://www.youtube.com/watch?v=b1LbOydoJwQ&t=555s),
and [switching between Home and Set](https://www.youtube.com/watch?v=TKOcsxXUON4&t=2s)
for navigation in later GMS recordings.

The build writes the site to `dist/`. It includes the game UI artwork and each finished pet's `pets/<game>/<pet>/spritesheet.png`.

Run these commands from the repository root to preview the site.

```sh
sh web/build.sh
python3 -m http.server 8000 --directory dist
```
