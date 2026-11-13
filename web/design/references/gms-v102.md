# Global MapleStory v102: cards, bookmarks and sets

Historical evidence for the [pet gallery design](../README.md). The v102 client data identifies the cards, colors and sets. For interactions, the references below distinguish the 2011 launch guide from recordings and screenshots of other builds.

## What could a player see?

The [launch guide][guide] describes the eight numbered bookmarks as shortcuts to monster level groups. Their colors also appear behind the portraits. These are the published monster level bands, not confirmed player levels for unlocking each tab.

| Bookmark | Monster level | Bookmark | Monster level |
| --- | --- | --- | --- |
| 1 · Red | 1–15 | 5 · Sky blue | 61–75 |
| 2 · Orange | 16–30 | 6 · Blue | 76–90 |
| 3 · Lime | 31–45 | 7 · Purple | 91–105 |
| 4 · Green | 46–60 | 8 · Black | 106+ |

Treat these as a guide to the colors, not a formula for individual v102 cards. For example, the [green Mummy Dog card][mummy] points to a [monster record](https://maplestory.io/api/wz/GMS/102/Item/Consume/0238.img/02383005/info/mob) whose [v102 level is 32](https://maplestory.io/api/wz/GMS/102/Mob/4230126.img/info/level).

The ninth bookmark has a [skull](../../../assets/maplestory/ui/monster-book/right-tabs/8/normal/0.png) in place of a number. It is for **Master Monsters and bosses**. According to the [v100 release notes][notes], it appears after the player picks up their first card from that group.

**A missing bookmark and a gray portrait mean different things.** A [level-10 Jett](https://www.youtube.com/watch?v=b1LbOydoJwQ&t=199s) has just the red bookmark, but can browse gray portraits among its 36 entries. A [level-200 test-server character](https://www.youtube.com/watch?v=9W59sS9-ilU&t=8s) has all nine bookmarks with only two cards collected. This is consistent with the numbered chapters opening as the character levels; the exact unlock rule is unverified. Within an available chapter, a gray portrait means the player hasn't picked up that card. It still opens to the monster’s name, picture and location. Collecting one copy colors the portrait and reveals information such as stats and drops. [Launch notes][notes]

## How did the bookmarks and arrows work?

Home returns to the counts on the left and the first 25 red cards on the right. The [v102 Home screenshot](https://mapleglobalnews.wordpress.com/2011/10/28/gms-v-102-rise-of-fellowship/) shows a search box directly above the grid.

The arrows turn through one continuous catalog. In the [January 2012 recording at 0:21–0:30][paging], choosing tab 2 opens a spread with **11 red, 36 orange and 3 lime cards**. Only tabs 2 and 3 extend. On the next spread, lime continues and green begins; only tab 4 extends. The footage fits bookmarks marking **where chapters start**: two can point to the same spread, and cards from the preceding chapter can remain visible. The recording’s exact patch is unknown.

Opening [Ribbon Pig’s card](https://www.youtube.com/watch?v=b1LbOydoJwQ&t=555s) shows the detail spread with Back enabled; Back is gray on Home. In the [2018 Roid bug report][roid], searching for Roid (or double-clicking the monster in the world) opens details with tab 1 extended and missing drop information. Browsing to Roid manually opens details with tabs 3–6 extended and the drop list present. A reply attributes the difference to two Roid records. The details view may retain the preceding spread’s bookmarks; neither screenshot shows that spread, so it cannot tell us how many colors were visible there.

## What were Sets for?

Sets are named checklists, usually regional. In v102, picking up one orange [Wild Boar card][boar] ticks a box on **two lists**: [Perion][perion-boar] and [Harmless Critters][critters-boar]. Both slots reference card ID `2381022`. The card still has just one color and one place in the chapter catalog. Even without bosses, the [Perion roster][perion] spans multiple colors: [Stump (red)][stump], Wild Boar (orange), Skeledog (lime) and [Mummy Dog (green)][mummy].

Completing the first set unlocked [Set List](https://www.youtube.com/watch?v=MHhzQ4DmX6Q&t=186s), which hides the chapter bookmarks. [Set Details](https://forums.maplestory.nexon.net/discussion/15760/merge-monster-book-into-monster-collection) shows the roster, completion count, score and effect. A player could choose one completed set’s effect and switch it later. Completing more sets also raised the total score toward Codex stats and medals. [Launch notes][notes] · [v100 player report](https://mapleglobalnews.wordpress.com/2011/08/11/v100-age-of-triumph/)

[guide]: https://msupdate.wordpress.com/2011/08/16/gms-maintenance-acornstory-the-crusader-codex/
[notes]: https://www.southperry.net/showthread.php?mode=threaded&pid=778914&tid=45712
[paging]: https://www.youtube.com/watch?v=PxDcbFKpN40&t=21s
[roid]: https://forums.maplestory.nexon.net/discussion/21004/crusader-codex-monsters-not-displaying-loot
[perion]: https://maplestory.io/api/wz/GMS/102/Etc/MonsterBookSet.img/setList/7/cardList
[stump]: https://maplestory.io/api/wz/img/GMS/102/Item/Consume/0238.img/02380003/info/iconRaw
[mummy]: https://maplestory.io/api/wz/img/GMS/102/Item/Consume/0238.img/02383005/info/iconRaw
[boar]: https://maplestory.io/api/wz/GMS/102/String/Consume.img/2381022/name
[perion-boar]: https://maplestory.io/api/wz/GMS/102/Etc/MonsterBookSet.img/setList/7/cardList/6
[critters-boar]: https://maplestory.io/api/wz/GMS/102/Etc/MonsterBookSet.img/setList/100/cardList/13
