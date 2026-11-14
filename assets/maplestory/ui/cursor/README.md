# Cursor

Original PNGs from GMS v102 `UI/Basic.img/Cursor`, with the archive frame indices for each state.
The [website cursor](../../../../web/cursor.js) applies each frame's original hotspot and animation delay.

- `default.png` comes from WZ frame `0/0`, the default glove.
- `pointer-0.png` and `pointer-1.png` come from WZ frames `1/0` and `1/1`, the clickable hover animation at 500 ms per frame.
- `pressed.png` comes from WZ frame `12/0`, shown while the mouse button is held down.

[Original asset archive](https://maplestory.io/api/wz/export/GMS/102/UI/Basic.img/Cursor)
· [Frame metadata](https://maplestory.io/api/wz/GMS/102/UI/Basic.img/Cursor)
· [Cursor-state reference](https://github.com/ryantpayton/MapleStory-Client/blob/master/IO/Cursor.h)

The website swaps ordinary PNG cursor frames with their original hotspots; it does
not rely on browser support for animated cursor files. Reduced motion freezes the
hover animation, while press/release feedback remains available.
