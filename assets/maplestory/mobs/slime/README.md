# Slime

These 16 lossless frames come from Green Slime (monster 210100) in **Global MapleStory v83**, archived by MapleStory.IO. The original artwork belongs to Nexon / Wizet. [WZ tree](https://maplestory.io/api/wz/GMS/83/Mob/0210100.img)

The initial download used the archive's ZIP export. Each ZIP entry contains the WZ frame's PNG followed by archive text after the PNG end marker. The checked-in files use the PNG bytes from the corresponding WZ Canvas. All 16 match the PNG portion of the ZIP entries byte for byte. [Original ZIP](https://maplestory.io/api/wz/export/GMS/83/Mob/0210100.img)

The five sequences are `stand` (3 frames), `move` (7), `jump` (1), `hit1` (1), and `die1` (4). The shared source manifest records each frame’s dimensions, placement origin, game delay, and checksum. [Slime source manifest](../../../../dev/maplestory/sources/slime.json)

To regenerate the PNGs and frame metadata, run this command from the repository root.

```sh
python3 dev/maplestory/common/fetch_wz_sprites.py dev/maplestory/sources/slime.json
```
