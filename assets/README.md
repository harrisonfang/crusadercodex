# Book artwork

Original client artwork is kept separate from derived files and grouped by game version.

| File | Dimensions | Contents |
| --- | --- | --- |
| `originals/gms-v102/book.png` | 499 × 370 | Unmodified RGBA image with transparent space outside the book. |
| `resized/gms-v102/book@2x.png` | 998 × 740 | Exact nearest-neighbor 2× enlargement, including the alpha channel. |

Source: MapleStory.IO's community archive of GMS v.102, WZ node
`UI/UIWindow2.img/MonsterBook/backgrnd`.

- [Source metadata](https://maplestory.io/api/wz/GMS/102/UI/UIWindow2.img/MonsterBook/backgrnd)
- [Source image](https://maplestory.io/api/wz/img/GMS/102/UI/UIWindow2.img/MonsterBook/backgrnd)
- Original SHA-256: `4285346fed4209ac70386b143ba7be79e8d7ac167cbfc6d35306b9a5c126649f`

The source artwork belongs to its respective rights holders; it is not original project artwork.

To reproduce the 2× file from the repository root with Python and Pillow installed:

```python
from PIL import Image

with Image.open("assets/originals/gms-v102/book.png") as image:
    image.resize((998, 740), Image.Resampling.NEAREST).save(
        "assets/resized/gms-v102/book@2x.png"
    )
```
