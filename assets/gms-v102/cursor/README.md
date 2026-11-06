# Cursor

Original PNGs from GMS v102 `UI/Basic.img/Cursor`, with their numbered paths intact.
`frames.json` preserves each frame's origin (pointer hotspot) and animation delay.

- `0`: idle glove.
- `1`: clickable hover, two frames at 500 ms each.
- `12`: mouse button held down, a single pressed-glove frame.

[Original asset archive](https://maplestory.io/api/wz/export/GMS/102/UI/Basic.img/Cursor)
· [Frame metadata](https://maplestory.io/api/wz/GMS/102/UI/Basic.img/Cursor)
· [Cursor-state reference](https://github.com/ryantpayton/MapleStory-Client/blob/master/IO/Cursor.h)

The website swaps ordinary PNG cursor frames with their original hotspots; it does
not rely on browser support for animated cursor files. Reduced motion freezes the
hover animation, while press/release feedback remains available.
