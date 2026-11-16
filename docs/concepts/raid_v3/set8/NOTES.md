# Raid set 8: set 7 on the v42 route slots ("street slots") (DRAFT for designer review, 2026-11-16)

**DRAFT.** Concept plates only (PIL); the numbers are illustrative, not from the sim. Set 7 (direction C, low text, the
designer-approved look) is unchanged in `../` (`r3_*`). Set 8 as first drawn on the v40 sockets is kept in `v40/` (plates,
sheet and its NOTES; `src/raid_d_v40.py` reproduces it).

v42 as built (port-campaign-b **6a99f5c0**, "port synced to prototype v42 (route slots, opening rule)"; read with `git show`
from `D:/rc_art/godot_look`): `scripts/core/raid_dock.gd`, `scripts/ui/raid/b_raid_place_model.gd`; the campaign's levers in
`content/config/b_campaign_config.tres` (copied onto the raid by `BCampaignRaid.dock_lv`): dockRule 1, **slotRule 1, slotShare 0**,
dockRadius 3, dockRadiusHq 6, dockMin 4, **dockMax 0 / dockMaxHq 0 = no cap**, dockPerSocket 1, dockSupSide 0.
- the operative is a fixed **post** (the R3 class beacon) on its site, never placed (unchanged from v40);
- each weapon is its own piece docked on a **street slot**: *every* street cell within dockRadius of the post (no
  intersection preference; dockMin still grows the radius when fewer than 4); **one piece per slot**: a weapon, or a street
  device (barricade, mine, tar, shock fence, gate, a BUILD wall, the FIREWALL's barricades). A slot holding a barricade refuses
  a weapon (`slot_piece`, "barricade here"); a weapon's slot refuses a device ("weapon here"). The shot leaves from the slot.
- "Street" in the code is still a cell some corp **route** uses (`RaidGrid`: `cl.road` comes from the paths only).
- The v42 **opening rule** (`core/takeover_opening.gd`, `takeover_setup.gd`) is the street *fight's* first-turn guard (a fixed
  enemy sequence must not open with a killing blow). It does not touch the raid dock, so nothing of it shows on these plates.

**The slots, posts and refusals on these plates are computed by the rules, not hand placed:** `src/dock_rules.py` now holds
a line-by-line port of v42 `RaidDock.sockets_of` (`slots_of`, incl. the dockSupSide branch, off in the campaign),
`slot_piece`, the map part of `why_dock` (`why42`, checks in the source's order) and the device side (`why_dev42`), next to
the v40 port (`sockets_of`, `why`, kept unchanged). `python dock_rules.py` prints both. `raid_d.py` asserts every drawn dock is
legal and every drawn refusal has the right code.

What v42 gives on the plate district:
- **PURGE** (radius 6 covers the district): all **13** route cells off the Safehouse are slots for every post (a1, b1-b7, d6-g6,
  d7); v40 had 4 sockets. The barricade on b4 holds its slot.
- **Site raid B2**: KAI (post on b6) gets b3 b4 b5 c6 d6 e6 b7 (7); VEX (supporter, a7) gets b4 b5 c6 d6 b7 (5); the shared pool
  is 7 (v40: 4). e6 and b3 are KAI's only.

## Plates

| File | Shows |
|---|---|
| `r8_plan.png` | PURGE at rest (Heat 100). Posts by the rule: KAI on the Safehouse (c7), VEX e5, MOTH a7, RUNE e7. The 13 street slots are faint dashed tiles inset in the street cells. KAI's SMG docked on d7, MOTH's jammer on b7; VEX's rail and RUNE's shotgun not docked (cards curl). Forecast as set 7: A holds at the wall, B leaks 2. |
| `r8_place.png` | RUNE's shotgun card held. The 10 slots it may take are lit (solid cyan tile, light fill, glow, over the dimmed posts): the whole street lights up. Refused, with a red badge beside: d7 and b7 (a weapon there: the *taken* badge, a slot tile with a dot) and b4 (the barricade there: B-104, the badge is the barricade's own small sticker (yellow vinyl, hazard band, block glyph) with a red no-mark on its corner). Hovered d6: its tile redrawn in yellow pencil, the shotgun's reach hatched from d6, `+3`; forecast B 2 → 0, 8/8. Work order unfolded (Tab held). |
| `r8_shop.png` | Between rounds: all four docked (VEX's rail on b1, RUNE's shotgun on d6); the SHOTGUN bought merges onto RUNE's docked one, which stays on d6. Credits 7 → 4. Slots at rest. |
| `r8_playback.png` | Tick 3/8. Shots leave the slots (rail b1, shotgun d6, SMG d7); reach outlines from the slots. **No slot marks in playback** (the map is locked; slots are a plan mark). |
| `r8_site.png` | Site raid on B2 (Heat 25), round 1/3. KAI's post on B2, VEX supporting from C2 on a7. The 7 shared slots at rest; KAI's SMG on b5 (lane B), VEX's rail on b7 (lane C). B-104: under VEX's docked rail, the supporter-share chip (VEX-blue ink pill: a pie with the 15 % slice filled, `15%`, a link = the gun stays VEX's); no word. |
| `r8_siteplace.png` | VEX's rail lifted off b7: VEX's dock radius (3) dashed in VEX's blue; its free slots b4, c6, d6, b7 lit; b5 (KAI's SMG) refused (*taken*: first come); b3 and e6 stay at rest (KAI's slots, beyond VEX). Pointer on e6: refused, red struck circle + the **too-far** badge; no forecast change. The share chip travels with the held card (bottom right). The radius is drawn because it limits something (b3, e6). |
| `r8_sheet.jpg` | All six. |
| `r8_devhere_key.png` | Check strip, not a plate: the five street devices' "device here" badges (BARRICADE, MINE, TAR, SHOCK fence, GATE) at plate size (top row) and x2, on the place plate's ground. |

Aftermath: unchanged (`../r3_aftermath.png` stands). Words on screen: the same as set 7 (6; 9 on the site plates); every
slot state and refusal is a glyph. Counts in `D:/rc_scratch/raid_v3/insp/d_counts.json`.

## What changed for v42 (vs set 8 on v40, `v40/`)
- **Sockets → street slots.** The cyan corner brackets at the grid intersections are gone; a slot is a **tile inset in the
  street cell** (0.13 cell clear of the grid line), so it reads as a place *in the street*, not a crossing.
- **Many more slots**: 13 in the PURGE, 7 in the site raid; the held state lights a run of street, not four points.
- **New refusal: device here** (red badge with the device's glyph), beside a slot a street device holds. *Taken* now draws a
  slot tile with a dot (was brackets with a dot).
- The per-socket gain notes (`+1` on the other free sockets) are dropped: with 10 free slots they were noise; only the hovered
  slot's gain shows (`+3`).
- CREW card dock mark: a pencil slot tile (diamond) beside the tick, was pencil brackets.
- Playback no longer shows slot marks.

## Look calls (mine, not designer rulings)
- **Rest = faint dashed cyan tile; held = solid bright tile + fill + glow, over the dimmed posts; hover = yellow pencil tile.**
  At rest the dashes sit on the route's red tint like painted bays, so the street reads as "dockable" without competing with the
  route pencil; it is subtle on purpose (crop the plan at 1:1 to see it).
- **Only the slots the held weapon may take now are lit**; refused ones keep the rest tile and get a badge beside; slots of
  another post outside the holder's radius stay at rest (siteplace b3, e6), which shows the radius without text.
- Kept from v40: guns drawn *in* the street on a role-colour pad (build B-102), tethers, posts dim to 42 % while a card is held,
  shared pool first come (B-102).
- **Dock radius rule (B-104 #3, computed, `radius_limits`):** a held weapon's radius is drawn only when some route cell is
  not among its post's slots. PURGE: every route cell is a slot for every post (radius 6), so **no ring on plan / place /
  shop** (the run prints `purge radius drawn: False`). Site: KAI's and VEX's radius 3 both leave route cells out, so the
  siteplace ring stays.
- **Supporter share (B-104 #4):** a chip, no word: pie + `15%` + link (dockSupPct 15: VEX's docked gun deals 15 %;
  dockSupKeep 1: it stays with VEX). On the docked gun's tag, and on the held card. Both levers PROVISIONAL; the player word
  is pending with the designer.
- **Device here (B-104 #5):** the badge is now the device's own small sticker (its vinyl colours, white glyph, die-cut
  edge) with a small red no-mark on the corner, not a red disc. TAR, SHOCK and GATE have no raid_icons glyph yet; their
  marks (puddle + drip, two posts + bolt, boom barrier) are drawn at badge size in `raid_d.py` only.

## Honest weak points
- **The PURGE place plate lights almost the whole route.** With every street cell a slot, "where can I put it" is answered
  by "anywhere on the street but three cells"; the lit run is strong and sits under the reach hatch and route pencil. Fine as
  an affordance, but the choice now lives in the forecast, and only the hovered slot shows a gain.
- **Rest slots are faint**; over the red route tint the dashes go whitish. Brighter competes with the route pencil.
- **Device-here stickers** (`r8_devhere_key.png`): barricade, mine and gate read at 1:1; TAR (purple puddle) and SHOCK
  (posts + bolt) are weak at 1:1 and need real glyphs. Only the barricade appears on a plate.
- **Share chip:** the 15 % slice is small at 1:1 (the pie reads as a dot); the chip sits close to the site's 8/8 and the
  yellow C2 arrow crosses it on `r8_site.png`.
- The *device side* of the exclusion (a held barricade/mine refused on a weapon's slot, "weapon here") is ported and tested in
  `dock_rules.py` but **not staged** on a plate.
- Kept from v40: the PURGE cluster at the Safehouse (four posts within two cells), tethers mostly hidden by the tags, the
  busy wall in playback.
- Stills only; numbers are not from the sim; tags and pencil are hand placed (slots, posts and refusal codes are not).

## Questions for the designer / build
1. **Player word "street slot"** (build proposal, NAME_MAP SY4b): the plates carry no word for it; fine to keep it word-free on
   the map and use "street slot" only in tooltips?
2. **Slots are still route cells only.** A street no route uses is not a slot (`cl.road` is set from the paths). Intended?
3. **PURGE: every route cell is a slot** (radius 6, no cap). Should the PURGE plate show the dock radius at all (it is the
   district edge), and is "the whole street lights" the intended read?
4. **Supporter share**: the campaign levers at 6a99f5c0 also set `dockSupPct` 15 and `dockSupKeep` 1 (VEX covering at 15 %,
   keeps its own guns; `RaidDock.sup_tag`). Set 8 does not show it (v40 had neither). Wanted on the site plates (a glyph on
   VEX's tag?), or a later pass?
5. **Device-here badge = the device's own glyph**, vs one generic "something here" glyph for all five street devices.
6. Should the at-rest slots show at all outside a held card (plan / shop / site), or only while a piece is held?

## Source / run
`src/raid_d.py` (the v42 plates + sheet; imports `raid_c.py` for set 7's pieces), `src/dock_rules.py` (v40 and v42 dock rules
on the plate grid; `python dock_rules.py` prints posts, sockets, slots and sample refusals), `src/raid_d_v40.py` (set 8 as
first drawn, writes `set8/v40/`). Run from `D:/rc_scratch/raid_v3/src/` (needs `city_hi/`):
`python raid_d.py [plan place shop playback site siteplace devkey sheet]` → `set8/r8_*.png`, `set8/r8_sheet.jpg` (`devkey`
writes `r8_devhere_key.png` from the place plate). `crop8.py` crops a
plate for inspection.

## Build's answers (B-102, 2026-11-16), as received on the v40 draft
- Sockets as route turns is v40 as ported. v42 replaces sockets with route slots (every street cell within dockRadius, one
  piece per slot, barricades use the same slots). **Done here, on 6a99f5c0.**
- A shared socket pool, first come first served, is fine. **Kept (siteplace: b5 refused, KAI's).**
- Docked guns are drawn in the street, as now. **Kept.**

## Build's answers (B-104, 2026-11-16), on the v42 set (build's numbering: 1 = the opening rule; 2-5 = questions 2-5 above)
1. **Opening rule:** fights only (Takeover street / boss fights); raids are untouched. **Nothing to draw (as assumed).**
2. **Route cells only:** yes, as the page builds it (bit-exact): the designer's words were "a weapon on the route paths
   with operatives in adjacent buildings", so the route path is the slot space. **Kept.**
3. **PURGE radius:** draw it only where it limits something; no ring when every route cell is in reach (art's call on the
   exact rule). **Done:** `radius_limits` (some route cell not among the post's slots); no ring on the PURGE plates, the
   site ring kept.
4. **Supporter share:** show it on the site plates (a supporter's gun deals 15 % and stays with its owner); the player word
   is pending with the designer ("covering at 15 %" for now); both levers PROVISIONAL. **Done:** pie + `15%` + link chip,
   no word, on `r8_site.png` and `r8_siteplace.png`.
5. **Device here:** each device's own small sticker (the player should see what blocks the slot); art's call on size.
   **Done:** device sticker + red no-mark, 2.5 x 2.1 badge radius (about 42 x 36 px at 1080p); all five in
   `r8_devhere_key.png`.
Still open from the list above: question 1 (the word "street slot", tooltips only?) and question 6 (rest slots outside a
held card).
