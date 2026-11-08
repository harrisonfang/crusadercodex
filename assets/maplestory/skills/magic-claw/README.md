# Magic Claw impact

These five frames come from the Magic Claw hit effect (skill 2001005, `hit/0`) in **Global MapleStory v83**, archived by MapleStory.IO. The original artwork belongs to Nexon / Wizet. [WZ tree](https://maplestory.io/api/wz/GMS/83/Skill/200.img/skill/2001005/hit/0)

The fetcher decoded each numbered Canvas node’s base64 PNG and read its origin and delay. The impact frames last 120, 90, 120, 90, and 150 ms in the source data. The shared source manifest records the WZ path and checksum for each frame. [Magic Claw source manifest](../../../../dev/maplestory/sources/magic_claw.json)

To regenerate the PNGs and frame metadata, run this command from the repository root.

```sh
python3 dev/maplestory/common/fetch_wz_sprites.py dev/maplestory/sources/magic_claw.json
```
