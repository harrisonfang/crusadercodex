# MapleStory Slime sources

The pet combines 25 native-resolution PNGs from MapleStory.IO's archive of the **GMS v83** client. Original MapleStory artwork belongs to Nexon / Wizet. Each asset's README identifies its client version, WZ location, and retrieval method.

| Asset | Frames | Archive details |
| --- | ---: | --- |
| Green Slime, monster 210100 | 16 | [Slime source notes](../../assets/slime/README.md) |
| Bronze meso, item 09000000 | 4 | [Meso source notes](../../assets/meso/README.md) |
| Magic Claw impact, skill 2001005 | 5 | [Magic Claw source notes](../../assets/magic-claw/README.md) |

The description is the first sentence of the English [GMS v83 Monster Book entry](https://maplestory.io/api/wz/GMS/83/String/MonsterBook.img/210100/episode).

A fresh checkout contains all the source PNGs and metadata needed to compile the pet offline. To download them again from the archive, run the following commands from the repository root with Python and `curl`:

```sh
python3 dev/common/fetch_wz_sprites.py dev/maplestory-slime/fetch-slime.json
python3 dev/common/fetch_wz_sprites.py dev/maplestory-slime/fetch-meso.json
python3 dev/common/fetch_wz_sprites.py dev/maplestory-slime/fetch-magic-claw.json
```

Each command updates its directory under `assets/`. It writes the lossless numbered frames and a manifest with the source paths, original WZ properties, placement origins, delays, and PNG checksums. The three configurations share a URL-keyed cache at `dev/maplestory-slime/build/wz-cache/`. Pass `--refresh` to fetch the responses again.
