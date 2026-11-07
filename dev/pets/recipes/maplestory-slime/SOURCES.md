# MapleStory Slime sources

The source PNGs are lossless WZ canvases from Global MapleStory v83. MapleStory.IO hosts the client archive. The original art belongs to Nexon / Wizet.

| Source | WZ animation |
| --- | --- |
| Slime (monster 210100) | [stand, move, jump, hit1 and die1](https://maplestory.io/api/wz/GMS/83/Mob/0210100.img) |
| Bronze meso | [Item/Special/0900.img/09000000/iconRaw](https://maplestory.io/api/wz/GMS/83/Item/Special/0900.img/09000000/iconRaw) |
| Magic Claw (skill 2001005) | [Skill/200.img/skill/2001005/hit/0](https://maplestory.io/api/wz/GMS/83/Skill/200.img/skill/2001005/hit/0) |
| Pet description | [First sentence of the English Monster Book episode for monster 210100](https://maplestory.io/api/wz/GMS/83/String/MonsterBook.img/210100/episode) |

The [slime](sources/slime/animations.json) and [effect](sources/effects/animations.json) manifests record the WZ path, pixel dimensions, origin, game delay and PNG SHA-256 of each frame. A null delay means that the client resource omits that property. The original single jump pose is available for preview. The released jumping row uses five movement poses.

The checked-in frames support an offline rebuild. To retrieve fresh copies and full WZ properties for comparison, run these commands from the repository root (requires Python and `curl`):

```sh
python3 dev/pets/tools/fetch_wz_sprites.py dev/pets/recipes/maplestory-slime/fetch-slime.json
python3 dev/pets/tools/fetch_wz_sprites.py dev/pets/recipes/maplestory-slime/fetch-effects.json
```

The fetcher writes PNGs, metadata and cached API responses under `dev/pets/build/fetched/maplestory-slime/`. The base URL and each frame's WZ path identify its source. To repeat the network requests, pass `--refresh`.
