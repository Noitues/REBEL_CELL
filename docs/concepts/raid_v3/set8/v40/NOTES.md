# Raid set 8 AS FIRST DRAWN on the v40 sockets (superseded by ../NOTES.md, v42; kept for reference, 2026-11-15)

**DRAFT.** Concept plates only (PIL); the numbers are illustrative, not from the sim. Set 7 (direction C, low text, the
designer-approved look) is unchanged in `../` (`r3_*`); this folder only adds set 8.

v40 as built (game-v2 page v40-2; port `D:/rc_art/chain_click`: `docs/design/campaign_b/RAID_LOOK_MELD_PLAN.md` sections 3
and 4 option 2, `scripts/core/raid_dock.gd`, levers in `content/config/b_raid_config.tres`):
- the operative is a fixed **post** (the R3 class beacon) on its site and is never placed;
- each weapon is its own piece, docked on a **socket**: a road cell where two routes meet or one route turns, within
  `dockRadius` 3 of the post (`dockRadiusHq` 6 in the PURGE), filled up to `dockMin` 4 with the nearest plain road cells, at
  most `dockMax` 8 (`dockMaxHq` 12), one weapon per socket (`dockPerSocket` 1). The shot leaves from the socket.

**The sockets and posts on these plates are computed by the rules, not hand placed:** `src/dock_rules.py` is a line-by-line
port of `RaidDock.junctions / sockets_of / beacons` run on each plate's own routes (cell id = r * 7 + c, ties by id).

## Plates

| File | Shows |
|---|---|
| `r8_plan.png` | Set 7's Safehouse raid is, under v40 + stationing, the **PURGE** (Heat 100, the whole crew recalled to HQ). Posts by the rule: KAI on the Safehouse (c7), VEX e5, MOTH a7, RUNE e7 (the nearest legal cells to HQ, by id). Sockets: b1, b7, d6, d7 (the four turns of routes A and B; the same four for every post). KAI's SMG docked on d7, MOTH's jammer on b7; VEX's rail and RUNE's shotgun are not docked (their CREW cards curl). Forecast as set 7: A holds at the wall, B leaks 2. |
| `r8_place.png` | RUNE's shotgun card held (Takeover drag: it trails the pointer, its liner stays on RUNE's CREW slot). Free sockets b1 and d6 lit; the taken ones (b7, d7) carry the taken badge. Hovered d6: yellow pencil brackets (valid), the shotgun's reach hatched from d6, `+3` (b1 would give `+1`). Posts dim while a card is held. Forecast re-projects: B 2 → 0, core safe, 8/8. The work order unfolded (Tab held), as set 7. |
| `r8_shop.png` | Between rounds: all four docked; the SHOTGUN bought from the sheet merges onto RUNE's docked shotgun, which stays on d6 (pencil stars on its tag). Credits 7 → 4. |
| `r8_playback.png` | Tick 3/8. VEX's rail on b1 shoots the trooper held at the wall (b3) and kills one on b2; RUNE's shotgun (d6) and KAI's SMG (d7) hit the slowed bike on e6. Reach outlines are drawn from the sockets (rail 2, shotgun 1). Tallies sit beside the guns that made them. |
| `r8_site.png` | Site raid on B2 (Heat 25), round 1/3. KAI holds the post on B2 (its beacon rises from the site sticker); VEX supports from C2 on a7 (the pencil arrow from off map). Sockets: b4, b5, c6, b7. KAI's SMG on b5 (lane B), VEX's rail on b7 (lane C, reaches lane A). Who-defends card, EVACUATE chip, core 8, as set 7. |
| `r8_siteplace.png` | VEX's rail lifted off b7: VEX's dock radius (3) drawn as a dashed line in VEX's blue round its post; its free sockets b4, c6, b7 lit; b5 (KAI's SMG) taken. The pointer is on e6, 4 cells from VEX: refused, a red pencil circle struck through and the **too-far** badge; no arrow, no forecast change (the strip shows place + too far, then the unchanged forecast). |
| `r8_sheet.jpg` | All six. |

Aftermath: **unchanged** (`../r3_aftermath.png` stands). The report and the result panel do not show sockets; the CREW column
there shows kill tallies, not cards. If the designer wants it, the only change would be the docked tags on the dimmed map.

Words on screen are the same as set 7: the callsigns and SEND IT (6; 9 on the site plates). No new words; every refusal and
socket state is a glyph. Counts in `D:/rc_scratch/raid_v3/insp/d_counts.json`.

## What changed vs set 7
- Operatives are never dragged and never stand in the street: each is its class beacon on its post.
- New pieces: sockets (cyan corner brackets), docked weapons (the CREW gear tag on a role-colour pad), tethers, the dock
  radius (held, site raid), two refusal badges.
- The held thing is now a **weapon card**, not an operative.
- CREW (option B): the operative has no tick of its own (it is always posted); its weapon card is ticked with a small pencil
  socket mark when docked, and peels at the corner when it is not.
- The PURGE plates carry Heat 100 beside the folded order (set 7 had 25).
- The site raid's core numbers moved below lane C (KAI's post now stands where set 7 put them).

## Look calls (mine, not designer rulings)
- **Sockets are system marks (cyan), not pencil.** They are rule geometry like the grid, so they share the grid's cyan; four
  L-brackets at the cell's grid intersections, so they sit on the faint grid and never on the route line through the cell
  centre. Pencil stays the player's plan (routes, forecast, ticks).
- **Lit = brighter brackets + a light fill, drawn over the posts while a card is held.** Under the posts' cones a ground-only
  socket disappeared (d6 under RUNE's cone).
- **Hovered legal socket = its brackets redrawn in yellow pencil** instead of set 7's yellow circle. The circle covered the
  brackets exactly (a cell and the circle are the same size).
- **Posts dim to 42 % while a card is held**, so the sockets and the reach read through the cones.
- **The docked weapon is the same gear tag as its CREW card** (one identity for the piece, card = model), at 0.56, over a
  small pad in the owner's role colour. Tag colour does not change with owner; pad and tether carry that.
- **Tether = thin dashed pencil in the owner's role colour, faded to 82 %, drawn under the red route pencil**, bowed so it
  never runs along a route. Most are one cell long and mostly hidden by the tag; the long one (VEX's rail on b1, 4 cells)
  reads clearly.
- **Refusals are red badges (bible red = invalid):** *taken* = a socket with a dot in it, beside the taken socket; *too far*
  = an arrow crossing a dashed line, above the refused cell, which also gets a red struck circle. No words.
- **Dock radius = the Chebyshev square, dashed in the owner's colour**, shown only while that owner's card is held.
- **Posts on a sticker (the Safehouse, the site) rise from behind the sticker**, so the house's heart and "B2" stay readable
  and the cone reads as standing on the roof.
- **Undocked cards curl at the corner** (bible 2.10 focus curl: "pick me up"); docked cards lie flat with a tick + socket mark.

## Honest weak points
- **The PURGE cluster.** Four posts within two cells of the Safehouse (the rule puts them there) plus two tags and the
  Safehouse make the bottom-left busy; RUNE's cone on e7 stands over the d6 socket and the B route's corner.
- **The PURGE dock radius is not drawn.** `dockRadiusHq` 6 covers the whole 7 x 7 district from any post, so its outline is
  the district edge and says nothing; "too far" cannot happen in the PURGE here. It is shown on the site plates instead.
- **Tethers are mostly invisible** because the sockets nearest a post are one cell away and the tag covers the line. Owner is
  then carried by the pad colour alone (a thin ring under the tag). If ownership must read at a glance, the tag itself needs
  the role colour (a rim or a corner chip).
- **Too-far refusal is only shown as a hover.** A road cell beyond the radius is not a socket, so it has no mark at rest;
  the badge appears where the pointer is.
- The held-card arrow on `r8_place` is a short hook; the card trails close to the socket.
- Busy spots kept from set 7: the wall in playback (held unit, kill bits, tracers, tally) now also has VEX's tag on b1.
- Stills only; numbers are not from the sim; tags and pencil are hand placed (the sockets and posts are not).

## Questions for the designer (morning review)
1. **Sockets are route cells only.** In the code a "road" is a cell some corp route uses, so the sockets are the turns and
   meetings of *routes*, not every street intersection of the city. On the plate district that gives 4 sockets in the PURGE
   (b1, b7, d6, d7) and, in the site raid, *no* junctions at all (three straight lanes), so the four nearest plain lane cells
   fill in (b4, b5, c6, b7). Intended, or should open streets that no route uses also offer sockets?
2. **Four sockets for a crew of four in the PURGE** (this map): one gun per operative, a second weapon (a levelled slot,
   TWO-GUN) could never dock. Is the PURGE meant to have more sockets (a bigger "full network" map, `dockMin` per post)?
3. **Supporter and owner share one socket pool** (KAI on B2 and VEX on a7 both get b4, b5, c6, b7). PORT_SPEC mentions a
   possible lever for which sockets a supporter may use; until then, is first come first served right?
4. **Weapons dock on the lanes themselves.** The corp drives over its own guns' cells (no `dockHit` today). Should a docked
   gun read as *in* the street (as drawn) or beside it (the pad offset to the kerb)?
5. **Ownership at a glance:** pad + tether colour (as drawn), or also tint the tag?
6. **Heat on the PURGE plates** reads 100 (the PURGE trigger); confirm the corner should show it.

## Source / run
`src/raid_d.py` (the set 8 plates + sheet; imports `raid_c.py` for set 7's pieces) and `src/dock_rules.py` (the v40 rules on
the plate grid; `python dock_rules.py` prints posts and sockets). Run from `D:/rc_scratch/raid_v3/src/` (needs `city_hi/`):
`python raid_d.py [plan place shop playback site siteplace sheet]` → `set8/r8_*.png`, `set8/r8_sheet.jpg`. `crop8.py` crops a
plate for inspection.

## Build's answers (B-102, 2026-11-16)
- Sockets as route turns is v40 as ported. v42 (designer-ruled, running in the prototype) replaces sockets with **route
  slots**: every street cell within dockRadius is a slot, with one piece per slot, and barricades use the same slots.
  This set stays DRAFT until `dock_rules.py` is re-run against the v42 port (sha after SY4).
- A shared socket pool, first come first served, is fine.
- Docked guns are drawn in the street, as now.
