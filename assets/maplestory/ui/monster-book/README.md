# Monster Book

The open book, chapter tabs and buttons come from Global MapleStory v102, under `UI/UIWindow2.img/MonsterBook`. The original artwork belongs to Nexon and Wizet. [MapleStory.IO ZIP export](https://maplestory.io/api/wz/export/GMS/102/UI/UIWindow2.img/MonsterBook)

| Repository path | Original WZ path under MonsterBook |
| --- | --- |
| `background.png` | `backgrnd` |
| `right-tabs/<index>/<state>/<frame>.png` | `RightTab/<index>/<state>/<frame>` |
| `left-tabs/home/<state>/<frame>.png` | `LeftTab/0/<state>/<frame>` |
| `left-tabs/set/<state>/<frame>.png` | `LeftTab/1/<state>/<frame>` |
| `page-info/book-info-0.png` | `pageInfo/bookInfo0` |
| `page-info/set-info-0.png` | `pageInfo/setInfo0` |
| `back/<state>/<frame>.png` | `UpTab/<state>/<frame>` |

The [Crusader Codex](page-info/book-info-0-banner.png) and [Set List](page-info/set-info-0-banner.png) banners sit beside their source overlays in `page-info/` with a `-banner` suffix. Each is a 171 × 28 pixel crop starting at (9, 0) from the top left of its source.

The repository calls the WZ state `mouseOver` **hover**. Other state names and all frame indices follow the archive. The background is a transparent 499 × 370 PNG. The chapter tabs use indices 0 through 8, displayed as chapters 1 through 9. [Original background](https://maplestory.io/api/wz/img/GMS/102/UI/UIWindow2.img/MonsterBook/backgrnd)
