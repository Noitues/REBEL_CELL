# REST / WORKSHOP / CACHE: icons, pages, legend (concept round, Solace list item 4, B-058)

Concept only: the designer picks, through art-pass, before anything is built. Art only: no rules, no new text. Nothing here is committed.
Sheet: `sheet.jpg` (2560 wide; rows A/B/C; columns icons 2x / 1x / legend size | 320 px squint + 4 px blur | REST page | WORKSHOP page | legend
strip). Big icons: `icon_sheet.jpg`. Frames below.

## Recommendation

**C "Slap-tag" for the icons** (the glyph is the sticker: white contour die-cut, ink keyline, saturated glyph, no disc field). It is the only
direction whose three icons differ from the five shipped kinds, and from each other, by outline: WORKSHOP wrench soft IoU 0.53 against the
nearest shipped kind at 16 px, REST house 0.75, CACHE bricks 0.70 (the 16 px rule asks < 0.68; the shipped four discs score 0.98 against each
other, so the family never met the rule on outline). Colour cannot carry these three (table below: CACHE teal vs FIGHT cyan is ΔE 13, 3 under
tritan; WORKSHOP gold vs RACK amber 27 / 11 deutan), so outline has to. **Page layout: A's** (the event page's window + RUN column) is the
safest sibling of the shipped pages; C's compact layout with the hero sticker is the alternative if the designer wants the page to carry the
big kind sticker. B is the richest page (the street kit's room as backdrop) but its icons only half-separate (0.69 to 0.82 IoU).

| Direction | How it reads at the squint (320 px / 4 px blur, on the busy street plate) |
|---|---|
| A Kit | Three more round discs: the new kinds separate from the old by hue only (violet, gold, teal) and the greyscale family strip shows no outline difference; fails the shape test (IoU 0.98 against FIGHT). Safest family fit, weakest read. |
| B Cutout | Pod (wide pill), cog and can-with-handle read as "not a disc" in the blur and in greyscale; the cog's teeth and the pod survive 17 px, the can reads as a block. Middle read (IoU 0.69 to 0.82). |
| C Slap-tag | House, wrench and brick stack are the only non-disc, non-field shapes on the strip; the wrench is unmistakable even blurred, the house and bricks read by their roof peak and staggered edge. Best read (IoU 0.53 to 0.75). Cost: it leaves the "dark field + accent ring" look of the five shipped stickers, so it sits beside them as a sibling, not a clone. |

## Sizes measured (not guessed)

- Route sticker art: 130 x 130 px (rack 128 x 134), `assets/netrun/route/node_*.png`. Measured on the shipped art: die-cut radius 61 (grey 1 px
  edge), white band 9, ink keyline 5, bright accent ring 4, then the dark field, a cream pictogram with an ink outline, two faint gloss streaks.
- The map draws it at `street_route.tres` `stickers.radius_px = 26` x k (k = height / 1080): the art is scaled to the die-cut,
  `cut = 26 - (3.2 + 2 + 2.4) + 2.4 = 20.8` px radius, so **41.6 px wide at 1080p (83 px at 2160p, "2x")**, with the state ring at radius 24.4. The
  min at 720p is 24 px radius (27.7 px art). (`NetrunMapView.NODE_RADIUS = 18` is the retired wireframe map; the live map is
  `StreetRouteOverlay`.)
- `RouteLegend`: swatch 22 px, sticker reach 11 px at k 0.5 -> **16.8 px art**, a 10.2 px dashed white ring, 12 px mono words. This is the
  smallest the icons must work at (the 16 px glyph rule, ART_BIBLE 5.2).
- Frames: `map/<dir>_map.png` (1920x1080 mock route, all eight kinds, walked / next / later states, number chips, the real operative token),
  `map/<dir>_squint_320.png` and `_grey.png`, `map/<dir>_blur4_strip.png` (Gaussian 4 px at 1:1, y 380-900), `legend/<dir>_legend_1x.png` and
  `_2x.png`, `icons/<dir>_<kind>.svg`, `_130.png`, `_512.png`.

## Silhouette and colour numbers (`scripts/metrics.py`)

Soft IoU of the alpha silhouette (max against a shipped kind / max against another new kind), 16 px and 42 px agree to 0.01:

| dir | REST | WORKSHOP | CACHE |
|---|---|---|---|
| A | 0.98 FIGHT / 1.00 | 0.98 FIGHT / 1.00 | 0.98 FIGHT / 1.00 |
| B | 0.69 FIGHT / 0.73 | 0.82 FIGHT / 0.71 | 0.74 FIGHT / 0.73 |
| C | 0.75 FIGHT / 0.70 | 0.53 FIGHT / 0.58 | 0.70 FIGHT / 0.70 |

ΔE76 of the accent colour (the street room glow colours from `street_route.tres rooms.colors`, so a sticker and its room are one colour) against
the nearest shipped accent, Machado 2009 severity 1 (linear RGB):

| kind | normal | protan | deutan | tritan |
|---|---|---|---|---|
| REST violet | 53 (SHOP) | 20 | 5 (SHOP) | 40 |
| WORKSHOP gold | 27 (RACK) | 14 | 11 | 27 |
| CACHE teal | 13 (FIGHT) | 10 | 8 | 3 (FIGHT) |

New against new: REST/WORKSHOP 32 under tritan, otherwise above 50. So colour alone fails for CACHE vs FIGHT (all vision types) and REST vs SHOP
under deutan: outline and pictogram must carry (ART_BIBLE 5.1). The colours are kept because the sticker must match its room; if the designer
wants more separation the CACHE ring should move off cyan (a lime-teal or a warm kraft), not the shape.

## The three directions

All three use the shipped sticker material (vinyl, white die-cut + ink keyline, gloss), the street room colours, and a pictogram taken from what the
street room's props already show (REST a bunk and a lit lamp, WORKSHOP a bench and tool rack, CACHE stacked boxes; `StreetRoomKit.PROPS`).
The icon never carries the state ring (the overlay draws it); the sticker stays full colour in every state (ART_BIBLE 4.6 option A).

- **A Kit.** The family as shipped. REST: crescent + star + a plus (rest + patch). WORKSHOP: a spanner and a small cog. CACHE: an ammo can with its
  lid thrown back and three cards showing (a stash, not a toolbox: the first draft with a handle read as a toolbox and clashed with WORKSHOP).
- **B Cutout.** The die-cut is the object. REST: a capsule pod (a wide pill) with a bunk and a moon. WORKSHOP: a cog with eight teeth around the
  spinner (six cells, one in the kind colour: "pick a slice, then the wheel slot it replaces"). CACHE: a flat ammo can with a handle bar and a
  brick wall inside with one brick pushed out (the loose-brick stash).
- **C Slap-tag.** The glyph is the sticker. REST: a safehouse (roof, chimney, arched lit door, a window, a moon on the roof). WORKSHOP: one big
  spanner. CACHE: two courses of bricks, the top right one pushed half out and the hole lit.

## Pages (the medium: CRT terminal, ART_BIBLE 1.2 "The Cell's own systems")

REST and WORKSHOP are the Cell's own menus: **CRT terminal** (navy glass, accent edge, Share Tech Mono, 3 px scanlines, hex dump, corner
brackets), tinted the kind colour the way the event page tints its window green (`round31_reward_event/event_screen.png`). Buttons are **vinyl
stickers** (the bible's job for verbs): PATCH / CONFIRM REWIRE / BUY pink, UNDO grey, LEAVE the holo sticker; rows are the event page's choice
stickers (white die-cut, yellow number tab, dark plate, Anton). The kind's title word is a vinyl sticker in the kind colour (the event page's
TERMINAL sticker). A RUN window (HP, CYCLES) sits right as on the event page. No paper, no holo, no pencil on A and B.

Elements drawn, all from `node_page.gd` (nothing added or removed): REST = RestHp, RestPatch (with its preview line), RestHint, six RestSlot*
(toggle rows, one picked, one second pick, one disabled, the `[firmware]` after-swap preview), RestConfirm, RestUndo, RestLeave. WORKSHOP = WorkshopCycles,
WorkshopHint, three WorkshopOffer*, six WorkshopSlot* (with the price), WorkshopBuy (`BUY  %d Cycles (%d left)`), WorkshopLeave. Strings are the
existing ones (`PATCH  +%d HP -> %d/%d`, `REWIRE: pick a wheel slot, ...`, `CONFIRM REWIRE`, `UNDO`, `LEAVE`, `Cycles: %d`, `Pick a slice, ...`, `BUY ...`);
the header reuses LOOT_STRIP's pattern (`NETRUN: SOLACE // REST 4 OF 7`). Sample numbers and slice / firmware names are placeholders from `content/`.
Slice glyphs are the round 17 glyph files (`picto_block`, `slice_*`, `placeholder_shield`) and are a guess per slice name, not the shipped mapping.

- **A (`pages/A_*_page.png`).** The event page's layout: wide kind-tinted window left, RUN right, title sticker and the icon stamped big under it.
- **B (`pages/B_*_page.png`).** The page is the room: the street kit's interior (`StreetRoomKit.PROPS`: back wall glow, floor, near-black props, the
  lit lamp, white window frame) behind a smaller console; rows are pods (REST) and a tool-roll of canvas pockets with stitching and a numbered strap
  (WORKSHOP offers) over pod rows with kraft price tags. The die-cut stands as the room's sign.
- **C (`pages/C_*_page.png`).** Compact terminal with flat rows, the contour sticker as the hero at left, and an **orange pencil** arrow for the
  plan (the swap CONFIRM would make; the buy BUY would make). Orange per the bible's netrun-plan ruling; it is a plan true to the rules and is
  dropped if the designer does not want pencil on a node page.

### CACHE: does the loot page need a variant? Yes, a small one, header art only (`cache/<dir>_cache_loot.png`)

CACHE uses the loot page today (title sticker says LOOT because `LOOT_SOURCES` has no CACHE entry, strip says `... // CACHE n OF N` through
`node_word`). The loot sheet, PAYOUT, cards and firmware drop stay as they are. What changes: the **kind sticker stamped on the title sticker** (so
the page names what paid out, as FIGHT WON / RACK BREACHED do), the strip word, and the loot-sheet header words (`LOOT SHEET // LOOT // PICK 1 OF 3`,
`CACHE 4/7`). No new text, no "stash" word: if the designer wants a stash title, that is a text decision. The strip stays NET_CYAN (teal would be
indistinguishable from it). Built on the real `round32_shop_reward/reward_screen_v2.png`; the leftover `(router)` in PAYOUT and the Duck card are the
old screenshot's and are not part of the proposal.

## RouteLegend (`legend/<dir>_legend_1x.png`, `_2x.png`)

The real strip layout (ORDER: FIGHT ELITE EVENT SHOP RACK **REST WORKSHOP CACHE** | walked next | HOVER: SHOW ALL LINKS), swatches drawn as
`RouteOverlay.draw_sticker` does (art at k 0.5, the dashed white "later" ring). At 17 px A's three rows are three look-alike discs; B's pod and cog
survive; C's house, wrench and bricks read. The words are the existing `SHORT` entries (REST, WORKSHOP, CACHE). `MEANINGS` tooltips stay build's
("placeholder text").

## Research (what each reference teaches)

Real world and genre references were searched on 2026-10-22; the URL is given where a page was read. Where a search returned only secondary
summaries that is said.

**REST / safehouse**
1. Nakagin Capsule Tower and capsule hotels (https://en.wikipedia.org/wiki/Nakagin_Capsule_Tower; https://www.designboom.com/architecture/kisho-kurokawa-nakagin-capsule-tower-building):
   a bed is a wide rounded module with a round window; the whole object is a pill. Taught B's pod silhouette and the porthole numbers.
2. First-aid kits and the red-cross rules (Australian Red Cross misuse note; ICRC information note on the emblem, via search): a red cross on white is
   a protected emblem, and civilians use a white cross on green. **Taught: no red cross anywhere**; the plus on A's moon is violet, and C's
   safehouse uses no cross at all. Also: field kits keep the marking on a removable patch, so the sign is a separate, simple shape.
3. Hobo / traveller signs, chalk or wax pencil on posts (https://99percentinvisible.org/article/unpacking-hobo-codes-the-pictographic-language-of-train-hopping-nomads/,
   https://people.howstuffworks.com/hobo-code.htm): marks are bold, one-stroke, legible at a glance; a roof/house mark means a place to rest. Taught C's
   safehouse as a roof shape and its thick-stroke construction. (Both sources note the code is thinly documented; used as a style, not as fact.)
4. Slay the Spire's campfire (https://slaythespire.wiki.gg/wiki/Map_Locations): rest is the one node whose icon is a warm light on a dark field; it
   is always the same silhouette. Taught: REST needs a "light in the dark" cue (the moon, the lit window).
5. Inscryption's campfire node (https://primagames.com/gaming/inscryption-map-symbols-act-1-guide): the rest node doubles as an upgrade node and
   still reads as a fire; one icon, two verbs. Taught that PATCH + REWIRE can share one rest icon.

**WORKSHOP / back-alley cyberware bench**
1. Akihabara Radio Center (https://www.lonelyplanet.com/points-of-interest/akihabara-radio-center/1308595; https://www.ageekinjapan.com/radio-center/): tiny
   door-less stalls where the clerk serves through a small opening, selling connectors, LEDs, switches. (The search found no repair-stall photos, so the
   bench itself comes from `StreetRoomKit.PROPS`.) Taught: a cramped stall, parts and tools as the identity, so the icon should be a tool, not a person.
2. Tool rolls and watchmaker benches (canvas rolls with many shallow pockets; e.g. https://instructables.com/Canvas-Tool-Roll): a tool roll is an array of
   narrow pockets, each holding one tool, stitched edge, a strap on top. Taught B's WORKSHOP offer pockets with stitching and a numbered strap.
3. Cyberpunk 2077 ripperdoc (https://cyberpunk2077.wiki.fextralife.com/The+Ripperdoc): the map marker for a ripperdoc is a pair of medical forceps, an
   instrument rather than a body part. Taught: pick one instrument as the mark (our spanner).
4. Slay the Spire's rest site (same wiki page): rest, smith (upgrade a card) and relic options live at the campfire, so a "modify" action does not need
   its own icon family. Taught: WORKSHOP must be told from REST by its tool, not by a shared fire/light cue.
5. The game's own wheel (round 17 glyphs, the six-slot spinner): WORKSHOP replaces a wheel slot, so B's cog hides the spinner inside it.

**CACHE / dead drop**
1. Geocache containers (https://www.geocaching.com/geocache/GC3AFBV; https://colemans.com/surplus-guide/post/best-geocache-containers): an ammo can is the
   standard container: a low wide box, a hinged lid, a latch, a folded handle, often camouflaged with rubble. Taught A's open can and B's flat can.
2. Camouflaged caches (a Pelican case glued with concrete chunks, found via the same search): the disguise is the stash's own wall; the giveaway is one
   piece that does not match. Taught the loose-brick idea (B inside, C as the whole glyph).
3. Loose-brick dead drops (the trope; no page cited, the search found no single authoritative one): one brick pulled from a wall. Taught C's staggered
   courses with one brick proud, and the lit hole.
4. Hobo marks again (99percentinvisible link above): a chalk mark says "something here". Taught the first C draft's chalk X; **dropped** because an X on a
   rounded rectangle read as an adhesive bandage (a heal sign, the wrong node) and an X collides with the cut-off ring's slash.
5. Inscryption's backpack node and Slay the Spire's chest (links above): a stash node is a container with its lid open, contents visible. Taught A's
   open can with cards showing.

**Route-map UI**
- Slay the Spire (https://slaythespire.wiki.gg/wiki/Map_Locations): seven node types, each its own silhouette, and a **legend you can hover to light every
  node of a type**: the model for our RouteLegend. Taught: type by silhouette first, and make the new three as separate as its chest, campfire and shop.
- FTL (https://ftl.fandom.com/wiki/Sectors): beacon colours mislead (green is not safe); labels, not colours, say what a beacon is. Taught: do not
  rely on hue (matches the ΔE numbers above).
- Inscryption (https://primagames.com/gaming/inscryption-map-symbols-act-1-guide): a node's symbol shows what you pick, not where it is. Taught the
  pictogram-as-verb (cards on the can, spinner in the cog).
- Monster Train and Into the Breach: searches returned no icon documentation (store pages and fan wikis only), so they are not cited for design
  claims. Into the Breach's reward chips (star, lightning, core: https://gameranx.com/features/id/141847/article/into-the-breach-10-tips-to-help-you-crush-the-vek-beginners-guide/)
  taught keeping rewards as tiny chips apart from the node icon, which our stickers already do.

## Open points for the designer (art only; no rules)

1. Pick a direction (recommended: C icons; page A or C).
2. CACHE's teal sits on FIGHT's cyan ring (ΔE 13, 3 tritan). Keep for the room match, or move the CACHE ring colour.
3. The bandage on a rounded rectangle is the HEAL glyph (`slice_patch`). C REST avoids it on purpose; if WORKSHOP/REST ever show the HEAL glyph on
   the page rows (Hotfix does here) that is the slice's glyph, not the node's.
4. Pencil on a node page (C): wanted or not.
5. The RUN window on node pages (A, B, C) follows the event page; the shipped placeholder page has none (the top HUD strip carries HP and Cycles).
6. Loot page: header art only, as shown, or a text change (a stash title) as a separate build / text decision.

## Medium mapping (ART_BIBLE 1.2)

| Thing | Medium | Why |
|---|---|---|
| Node icons on the map and in the legend swatches | Vinyl sticker | "node-type and route-node stickers ... things that never change" |
| REST / WORKSHOP page body, header, HP / Cycles / RUN | CRT terminal | "The Cell's own systems: menus, resources" |
| PATCH, CONFIRM REWIRE, BUY, UNDO, LEAVE, title words | Vinyl sticker | "buttons and verbs, screen titles" |
| HP, Cycles values (RUN window) | Bare Anton in the terminal | live values |
| Plan arrows (C only) | Grease pencil, orange (netrun plan) | "plans true to the rules" |
| Room backdrop (B only) | World (AAA-2 night room, flat stand-in here) | the street room kit's interior |
| Legend strip | CRT terminal with sticker swatches | as `RouteLegend` ships |

## Rebuild

Pillow and numpy only (no Blender, no GPU, no Godot). From `D:/rc_scratch/solace_v1/nodes/scripts/` (copy in `scripts/` here):
`python build_all.py` writes everything under `docs/concepts/solace_vertical/nodes/` (about 2 minutes). `python metrics.py` prints the IoU and ΔE tables.
`vec.py` is the icon kit: one shape list (`Doc`) renders to SVG and to PNG, so the SVG in `icons/` is the Godot import source (130 x 130 view box; polygons,
polylines, circles, clip paths; no gradients, no filters). `icons.py` holds the nine icons; `common.py` the state ring (a port of
`RouteOverlay.draw_state_ring`), the mock map and the legend; `pages.py` and `kit.py` the page mocks; `cache_page.py` the loot variant.
Inputs read (never written): `D:/rc_art/godot_look_bloom/assets/netrun/route/*.png`, `assets/fonts/`, the golden plate
`golden_plates/street_decision.png`, `round17_slice_system/glyphs/`, `round32_shop_reward/reward_screen_v2.png`.

## Honest limits

- The map backdrop is the street golden plate (the real street at night) dimmed 30 %; stickers, rings, chips and links are drawn by code, so
  glow, gloss sweep and the hover power cut are not shown.
- Sticker rings are ported from the overlay's constants, not captured from the engine; check once in Godot.
- The SVG icons are flat: the shipped art's soft shading is two streaks and a top tint, reproduced; the real PNGs have a few more pixels of bevel.
- 320 px is a harsh squint (a 42 px sticker is 7 px). It is the brief's test; the 4 px blur strip at 1:1 is the fairer one, and the legend is the
  real worst case (17 px).
