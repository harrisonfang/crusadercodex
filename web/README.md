# Website

Static HTML, CSS, and JavaScript displaying the book at its original 499 × 370 size.
The nine right-side tabs select a chapter; its pages remain blank. Use the mouse,
Up/Down arrow keys, Home, or End. The gold Home bookmark returns to the opening
view, chapter 1, page 1. The keyboard Home key within the chapter tabs selects
the first chapter, following the tab-list keyboard convention.
Home remains selected while browsing chapters: it represents the catalog section.

Back uses the original disabled artwork on these blank browsing views. Game
references show it disabled on lists and enabled on details; there is no detail
view yet, so chapter changes do not create a Back history. View, chapter, and
page state stays in memory.
Small windows scroll instead of resizing the artwork.

Home's destination is documented in the [2011 Nexon guide repost](https://msupdate.wordpress.com/2011/08/16/gms-maintenance-acornstory-the-crusader-codex/).
The [2017 catalog screenshots](https://forums.maplestory.nexon.net/discussion/14064/crusader-codex-glitches-issues)
show Home selected during chapter browsing. A later video shows Back disabled on
a [paged list](https://www.youtube.com/watch?v=MHhzQ4DmX6Q&t=212s) and enabled on
[details](https://www.youtube.com/watch?v=MHhzQ4DmX6Q&t=252s). These later references'
exact patches and the result of a Back click are unverified; all artwork is v102.

The build writes the site to `dist/`. It includes the game UI artwork and each finished pet's `pets/<game>/<pet>/spritesheet.png`.

Run these commands from the repository root to preview the site.

```sh
sh web/build.sh
python3 -m http.server 8000 --directory dist
```
