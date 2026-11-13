# Crusader Codex: a guide to the original book

The pet gallery uses **Global MapleStory (GMS) v102** artwork. The v102 client data identifies the cards, colors and sets. For interactions, the references below distinguish the 2011 launch guide from recordings and screenshots of other builds.

## What could a player see?

The [launch guide][guide] describes the eight numbered bookmarks as shortcuts to monster level groups. Their colors also appear behind the portraits. These are the published monster level bands, not confirmed player levels for unlocking each tab.

| Bookmark | Monster level | Bookmark | Monster level |
| --- | --- | --- | --- |
| 1 · Red | 1–15 | 5 · Sky blue | 61–75 |
| 2 · Orange | 16–30 | 6 · Blue | 76–90 |
| 3 · Lime | 31–45 | 7 · Purple | 91–105 |
| 4 · Green | 46–60 | 8 · Black | 106+ |

The ninth bookmark has a [skull](../assets/maplestory/ui/monster-book/right-tabs/8/normal/0.png) in place of a number. It is for **Master Monsters and bosses**. According to the [v100 release notes][notes], it appears after the player picks up their first card from that group.

**A missing bookmark and a gray portrait mean different things.** A [level-10 Jett](https://www.youtube.com/watch?v=b1LbOydoJwQ&t=199s) has just the red bookmark, but can browse gray portraits among its 36 entries. A [level-200 test-server character](https://www.youtube.com/watch?v=9W59sS9-ilU&t=8s) has all nine bookmarks with only two cards collected. This is consistent with the numbered chapters opening as the character levels; the exact unlock rule is unverified. Within an available chapter, a gray portrait means the player hasn't picked up that card. It still opens to the monster’s name, picture and location. Collecting one copy colors the portrait and reveals information such as stats and drops. [Launch notes][notes]

## How did the bookmarks and arrows work?

Home returns to the counts on the left and the first 25 red cards on the right. The [v102 Home screenshot](https://mapleglobalnews.wordpress.com/2011/10/28/gms-v-102-rise-of-fellowship/) shows a search box directly above the grid.

The arrows turn through one continuous catalog. In the [January 2012 recording at 0:21–0:30][paging], choosing tab 2 opens a spread with **11 red, 36 orange and 3 lime cards**. Only tabs 2 and 3 extend. On the next spread, lime continues and green begins; only tab 4 extends. The footage fits bookmarks marking **where chapters start**: two can point to the same spread, and cards from the preceding chapter can remain visible. The recording’s exact patch is unknown.

Opening [Ribbon Pig’s card](https://www.youtube.com/watch?v=b1LbOydoJwQ&t=555s) shows the detail spread with Back enabled; Back is gray on Home. The [2018 Roid report][roid] shows **tabs 3–6 extended after manual selection**. The separate search/world-click screenshot shows only tab 1 extended. Neither shows the preceding spread, the transition from typing a query, or where Back returns after a search.

## What were Sets for?

Sets are named checklists, usually regional. A card belongs to one bookmark category but can count toward several sets. The v102 [Perion roster][perion] includes [Stump (red)][stump], Wild Boar (orange), Skeledog (lime), [Mummy Dog (green)][mummy] and Stumpy (gold). The same Snail card counts toward both [Victoria Island Friends][friends] and [Harmless Critters][critters].

Completing the first set unlocked [Set List](https://www.youtube.com/watch?v=MHhzQ4DmX6Q&t=186s), which hides the chapter bookmarks. [Set Details](https://forums.maplestory.nexon.net/discussion/15760/merge-monster-book-into-monster-collection) shows the roster, completion count, score and effect. A player could choose one completed set’s effect and switch it later. Completing more sets also raised the total score toward Codex stats and medals. [Launch notes][notes] · [v100 player report](https://mapleglobalnews.wordpress.com/2011/08/11/v100-age-of-triumph/)

## What we’re keeping for the pet gallery

| Area | Website decision |
| --- | --- |
| Access | All nine bookmarks are available immediately; there is no character level or card ownership to track. The blank gallery currently extends one chosen bookmark. How populated spreads should highlight chapters remains open. |
| Home, Set and Back | The [navigation change](https://github.com/harrisonfang/crusadercodex/pull/5) returns Home to chapter 1, page 1 and opens Set List without a collection requirement. Set hides the right bookmarks. Both sections keep Back disabled while there are no items to open. |
| Card details | A later change will use the detail spread for pet animation previews. Familiar naming and summoning are outside the gallery’s scope. Search behavior and Set contents are still open design choices. |

[guide]: https://msupdate.wordpress.com/2011/08/16/gms-maintenance-acornstory-the-crusader-codex/
[notes]: https://www.southperry.net/showthread.php?mode=threaded&pid=778914&tid=45712
[paging]: https://www.youtube.com/watch?v=PxDcbFKpN40&t=21s
[roid]: https://forums.maplestory.nexon.net/discussion/21004/crusader-codex-monsters-not-displaying-loot
[perion]: https://maplestory.io/api/wz/GMS/102/Etc/MonsterBookSet.img/setList/7/cardList
[stump]: https://maplestory.io/api/wz/img/GMS/102/Item/Consume/0238.img/02380003/info/iconRaw
[mummy]: https://maplestory.io/api/wz/img/GMS/102/Item/Consume/0238.img/02383005/info/iconRaw
[friends]: https://maplestory.io/api/wz/GMS/102/Etc/MonsterBookSet.img/setList/0/cardList/0
[critters]: https://maplestory.io/api/wz/GMS/102/Etc/MonsterBookSet.img/setList/100/cardList/0
