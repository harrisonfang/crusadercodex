# Crusader Codex

A collection of Codex pets and a static gallery inspired by MapleStory's Crusader Codex.

## Repository layout

```text
pets/                 Pet sprite sheets and related files (reserved for pet work)
assets/originals/     Unmodified artwork, grouped by source game version
assets/resized/       Derived artwork, grouped by source game version
web/                  Static HTML and CSS
scripts/              Development and packaging helpers
_site/                Generated website, ignored by Git
```

This first iteration displays only the empty book. No JavaScript, package manager,
or framework is required.

## Preview locally

From the repository root:

```sh
sh scripts/build.sh
python3 -m http.server 8000 --directory _site
```

Open <http://localhost:8000>. The build stages `web/` at the website root and copies
`assets/` alongside it. Relative URLs work both locally and at `/crusadercodex/`.
Re-run the build after editing source files.

## Book sizes

- **1×:** 499 × 370 CSS pixels; uses the original transparent PNG.
- **2×:** 998 × 740 CSS pixels; uses the nearest-neighbor enlargement when the
  viewport is at least 1030 × 772 CSS pixels, including a 16-pixel margin per side.
- Narrower or shorter windows use 1×. On screens too narrow for 1×, the page scrolls
  horizontally instead of shrinking the artwork. Short screens can scroll vertically.

The `<picture>` source and CSS media query share the same breakpoint. Image choice
depends on available space, not device pixel density. There are no intermediate sizes.
See [asset provenance and reproduction](assets/README.md).
