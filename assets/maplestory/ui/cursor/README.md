# Cursor

Original PNGs from GMS v102 `UI/Basic.img/Cursor`, with the archive frame indices for each state.
`frames.json` preserves each frame's origin (pointer hotspot) and animation delay.

- `idle/` comes from WZ state `0`, the idle glove.
- `pointer/` comes from WZ state `1`, two clickable hover frames at 500 ms each.
- `pressed/` comes from WZ state `12`, a single frame while the mouse button is held down.

[Original asset archive](https://maplestory.io/api/wz/export/GMS/102/UI/Basic.img/Cursor)
· [Frame metadata](https://maplestory.io/api/wz/GMS/102/UI/Basic.img/Cursor)
· [Cursor-state reference](https://github.com/ryantpayton/MapleStory-Client/blob/master/IO/Cursor.h)

The website swaps ordinary PNG cursor frames with their original hotspots; it does
not rely on browser support for animated cursor files. Reduced motion freezes the
hover animation, while press/release feedback remains available.
