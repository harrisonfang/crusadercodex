# Slime

These 16 lossless frames come from Green Slime (monster 210100) in **Global MapleStory v83**, archived by MapleStory.IO. The original artwork belongs to Nexon / Wizet. [WZ tree](https://maplestory.io/api/wz/GMS/83/Mob/0210100.img)

The initial download used the archive's ZIP export. Each ZIP entry contains the WZ frame's PNG followed by archive text after the PNG end marker. The checked-in files use the PNG bytes from the corresponding WZ Canvas. All 16 match the PNG portion of the ZIP entries byte for byte. [Original ZIP](https://maplestory.io/api/wz/export/GMS/83/Mob/0210100.img)

The five sequences are `stand` (3 frames), `move` (7), `jump` (1), `hit1` (1), and `die1` (4). Each frame's dimensions, placement origin, game delay and checksum are in the [animation manifest](animations.json).

From the repository root, run:

```sh
python3 dev/common/fetch_wz_sprites.py dev/maplestory-slime/fetch-slime.json
```
