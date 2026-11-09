# Bronze meso

These four frames come from the bronze meso icon (item 09000000) in **Global MapleStory v83**, archived by MapleStory.IO. The original artwork belongs to Nexon / Wizet. [WZ tree](https://maplestory.io/api/wz/GMS/83/Item/Special/0900.img/09000000/iconRaw)

The fetcher decoded each numbered Canvas node’s base64 PNG and read its placement origin. The archive omits frame delays for this coin, so the shared source manifest records `delay_ms` as `null`. [Meso source manifest](../../../../dev/maplestory/common/sprites/meso.json)

To regenerate the PNGs and frame metadata, run this command from the repository root.

```sh
python3 dev/maplestory/common/sprites/fetch.py dev/maplestory/common/sprites/meso.json
```
