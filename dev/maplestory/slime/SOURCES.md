# MapleStory Slime sources

The pet combines 25 native-resolution PNGs from MapleStory.IO's archive of the **GMS v83** client. Original MapleStory artwork belongs to Nexon / Wizet. Each asset's README identifies its client version, WZ location, and retrieval method.

| Asset | Frames | Archive details |
| --- | ---: | --- |
| Green Slime, monster 210100 | 16 | [Slime source notes](../../../assets/maplestory/mobs/slime/README.md) |
| Bronze meso, item 09000000 | 4 | [Meso source notes](../../../assets/maplestory/items/meso/README.md) |
| Magic Claw impact, skill 2001005 | 5 | [Magic Claw source notes](../../../assets/maplestory/skills/magic-claw/README.md) |

The archive ZIPs encode the WZ path as a flat, hyphenated filename. The source directories use readable asset and sequence names. Frame numbers match the original WZ indices. The three manifests record each frame’s full WZ path. [Slime](../sources/slime.json) · [Meso](../sources/meso.json) · [Magic Claw](../sources/magic_claw.json)

| ZIP member | Source PNG in this repository |
| --- | --- |
| `Mob-0210100.img-stand-0.png` | [maplestory/mobs/slime/stand/0.png](../../../assets/maplestory/mobs/slime/stand/0.png) |
| `Item-Special-0900.img-09000000-iconRaw-0.png` | [maplestory/items/meso/bronze/0.png](../../../assets/maplestory/items/meso/bronze/0.png) |
| `Skill-200.img-skill-2001005-hit-0-0.png` | [maplestory/skills/magic-claw/hit/0.png](../../../assets/maplestory/skills/magic-claw/hit/0.png) |

The description is the first sentence of the English [GMS v83 Monster Book entry](https://maplestory.io/api/wz/GMS/83/String/MonsterBook.img/210100/episode).

A fresh checkout contains all the source PNGs and metadata needed to compile the pet offline. To regenerate them, run these commands from the repository root with Python and `curl`.

```sh
python3 dev/maplestory/common/fetch_wz_sprites.py dev/maplestory/sources/slime.json
python3 dev/maplestory/common/fetch_wz_sprites.py dev/maplestory/sources/meso.json
python3 dev/maplestory/common/fetch_wz_sprites.py dev/maplestory/sources/magic_claw.json
```

Each command reads the archive paths from its manifest, writes the original numbered PNGs under `assets/maplestory/`, and updates that same manifest with frame origins, delays, WZ properties, and PNG checksums. All three use a URL-keyed cache at `dev/maplestory/sources/build/wz-cache/`. Pass `--refresh` to download the archive responses again.
