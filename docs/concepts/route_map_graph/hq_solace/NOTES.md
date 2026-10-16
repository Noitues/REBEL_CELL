# HQ netrun: Solace Biosystems, "the ladder" (2026-10-15, redesigned)

The Solace HQ run in the approved route-map look (AAA-2 r3) with the designer's HQ lighting rule. **Redesigned the same
day** after the designer's review of the first version (a ribbon double helix with pods, "looks like a dangerous roller
coaster"): the landmark is now two twisting towers joined by a glazed bow-tie skybridge on every floor, and the
route is a LADDER that starts at the bottom and winds up. A second note (v3) made each strand a smooth swept TUBE with
oval portholes in rows (an aircraft fuselage), skinnier and taller. Archived: the v1 ribbon helix in
`D:\rc_scratch\hq_solace\v1_helix\`, the v2 stacked-box towers in `D:\rc_scratch\hq_solace\v2_boxes\`. Nothing is committed; Cycles HIP in the shared GPU queue; Eevee for previews.

## Files

| File | What it is |
|---|---|
| `H_overview.png` | OVERVIEW: the twin towers twisting round each other, a lit bow-tie bridge on every floor (the DNA rungs), the green atrium slots drawing each tower's helix, the crown with THE GENOME CORE (TARGET) and the pink halo, the plaza podium; the city dark behind. |
| `H_decision.png` | DECISION on tower B, route floor 3 (building floor 6), after crossing at floor 2: option UP (tower B, floor 8) or ACROSS (the floor-6 bridge to tower A). Floors above route floor 5 are UNREAD. |
| `H_hover.png` | The same, hovering ACROSS: the power cut, the branch, the rule note. |
| `H_mechanic_states.png` | The sheet: UP / ACROSS options, CURRENT, READ, UNREAD, WALKED; three shots (ground floor, mid-climb after a crossing, the top); the SEQUENCE dial; the rule cards. |
| `H_reveal.mp4` / `.gif` | 6.5 s HQ beat: from the plaza looking up the gap between the towers (the bridges stack overhead like rungs), the camera rises up the gap, turning with the twist, then pulls out to the OVERVIEW. |
| `plates/`, `scripts/` | Plates without UI; everything to rebuild. |

## 1. Layout rules (`scripts/hq_graph.py`; numbers in `hq_preset "compound"`)

| Element | Rule |
|---|---|
| Strands | Two smooth swept TUBES (radius 9, a shared-vertex 40-segment mesh, smooth shaded, glossy porcelain) following the helix: centre 30 BU out at azimuth theta(z) = 90 + 11 z / 12.5 (11 degrees a floor), tower B opposite. 19 floors of 12.5 BU (~240 BU). |
| A floor | A row of 12 OVAL portholes round the tube (half axes 1.7 x 2.9, lit from inside, seeded tints, a few dark) with a thin frame ring each; a downlight ring under the row; a pale-mint light seam rises up the tube's outer side (the light inside the tower; mint, never the route lime). |
| Bridges | Every floor: a glazed BOW-TIE walkway between the tubes' inner sides (13 BU wide where it meets a tube, 4 BU at the waist), lit walls and floor; the route floors' bridges are brighter. |
| Rooms | Route floors 2, 4 .. 16 on both towers (A1..A8, B1..B8): a cutaway room set into the tube's FRONT (normal theta + 90), the tube's skin opened round it. Both towers' rooms of a floor face the same way, so a decision frames the current room, the room UP and the room ACROSS. |
| Links | UP: a stair up the outer edge of the front face (turning with the floors); ACROSS: along the bridge's front edge (the waist); the last floor climbs to the crown. |
| Crown / server | The top floor is a crown joining the towers; THE GENOME CORE sits open in its middle (GDD 11.7; the TARGET). |
| Base | A rectangular plaza podium with steps and the SOLACE name; the clinic gate (start) on the plaza. |

## 2. Preset variant
r3 look; `PRESET["hq"]`: porcelain white, Solace leaf #96FF46 (the atrium slots, window tints, the podium edge), pink
#FF4696 (the crown halo), clinic white (bands, bridges, the ground spots); the city darker (win_k 0.16, less neon) and
the fog halo toned down per the review. Solace lime stays in the 3D, never on a link or ring (bible 2.4).

## 3. The mechanic: GDD vs proposal

| What | Source | Status |
|---|---|---|
| Solace's Central Server = THE GENOME CORE | GDD 11.7 | **Real.** GDD 8.3 / App. A call the final server / boss "the Renewal Engine" (flagged, Q1). |
| The twin towers, the bridge per floor, the ladder (UP or ACROSS each floor) | Designer brief (2026-10-15 redesign) | **Proposal** (not in the GDD). Replaces round 43's three crossovers: every floor is a crossover now. |
| The strands are semi-random node sets | Round 43 decision | Kept: each tower's rooms draw from a seeded deck (preset `seed`, `deck`). |
| The READ rule: 2 route floors ahead are read on both towers, higher rooms UNREAD (kind hidden) | This round | **Proposal** (preset `mech.read_ahead`). With a crossing every floor, reading ahead is what makes UP vs ACROSS a choice. |
| No spinning walkways | Bible Appendix C #10 (round 43 over round 42) | Kept: the twist is architecture, not motion. |
| Visual language: UP / ACROSS chips on options, the '?' disc + UNREAD chip, frosted dim unread rooms in 3D, THE SEQUENCE dial (the ladder ahead) | This round | **Design-language proposal**; state colours unchanged. |

## 4. Camera beats
| Beat | Rule |
|---|---|
| DECISION | The ORBIT-AND-RISE: the azimuth faces the options' floor front (it turns 11 degrees a floor, so the camera orbits as the run climbs), pitch 12-26 by height, the framing solver over the current room + UP + ACROSS. |
| OVERVIEW | Yaw 99 (the front of the middle route floors), pitch 20, lens 34: both towers whole. |
| REVEAL | Up the gap between the towers, then the pull-out. |

## 5. Godot 4.7 mapping
| Element | Godot | Perf |
|---|---|---|
| Strands | Each tube one generated mesh (a `@tool` sweep along the helix, ~20 k tris); the portholes an instanced oval quad + frame (MultiMesh, ~450) with a per-instance lit / tint; the light seam an emissive ribbon. | 3-4 draws. |
| Bridges | One bow-tie mesh instanced 19x; route bridges a brighter instance uniform. | 1 draw. |
| Rooms | Room scenes on the route floors' fronts (16). | Lights: visible rooms only. |
| Downlights / ground spots | Emissive slab-edge strips + ~8 `SpotLight3D` ground spots (shadows off) + ~20 downlight spots (could be baked). | The downlight spots are the cost: bake or drop to emissive. |
| Read rule | A frosted-glass decal + dimmed room light per unread room (state uniform). | Free. |

## 6. Value checks and render log

| Still (2560 x 1440, 64 spp) | median | < 0.10 | > 0.85 | landmark / local background |
|---|---|---|---|---|
| H_overview | 0.071 | 62 % | 0.6 % | 0.369 / 0.046 = 8.0 |
| H_decision | 0.047 | 64 % | 1.8 % | 0.328 / 0.025 = 13 |

The landmark rule (1.5-2x) is far exceeded and the frame median is BELOW the r3 target (0.14): after the review asked
for a dark night city behind the tower, the city windows and the halo fills were cut and the towers' own light carries
the frame. The towers read at 320 px (`scratch/thumb_H_overview.png`). Fix for a next pass (light, not exposure): raise
the city ring's window strength (preset `city.win_k` 0.16 -> ~0.3) and give the plaza podium its own warm wash, which
lifts the median without bringing back the magenta wash.

Render log (Cycles HIP, shared queue): stills 294 s for three (with the build), sheet shots 72 s, the reveal 156 frames
at 960 x 540 in 949 s (~6 s a frame), compose 122 + 59 + 234 s, encode 19 s.

## 7. Gaps for the tools step
- The route floors are a preset list (every other floor); the overview yaw is a preset number (the front of the middle floors).
- Pane patterns are seeded, not authored; the SOLACE lettering position is a number.
- The reveal path is a hand-set rise + pull-out.

## 8. Open questions for the designer
1. The server's name: THE GENOME CORE (11.7) or the Renewal Engine (8.3)?
2. Read ahead: 2 route floors (here), 1, or "read a floor when you stand on its bridge"?
3. Should a crossing cost something (e.g. the bridge holds an encounter) so UP vs ACROSS is not free?
4. Route floors every other floor (8 a tower): fewer, taller climbs?
