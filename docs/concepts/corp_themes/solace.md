DRAFT (Batch API, Sonnet, 2026-10-18; AD review pending)

# Solace Biosystems: campaign theme "THE BLOOM", art plan

Status: concept plan for the designer's 2026-10-18 ruling. Nothing here is built. I design art only. Every game value the art needs is listed as a read-only input and as a question at the end.

## 0. Shared rules (all four parts)

### Conflicts with the attached HQ draft

I followed the designer's ruling and the approved landmark notes. I did not follow the draft where they disagree.

| Draft says | Conflict | What this plan does |
|---|---|---|
| "The player is the infection climbing a treatment facility." | The ruling makes the virus a pursuer behind the operative. | The virus is the pursuer. The operative is not infected. |
| `tower_pressure` tints the portholes mint to amber. | The Bloom would also tint the portholes. Two tints on the same glass is unreadable. | I use the portholes for the Bloom only. If pressure stays, it needs another channel (Question 9). |
| `debts` shown as pink pips on the crown halo. | The pips use the Bloom's hue. | I assume the pips are not approved. See Question 9. |
| 9 rungs, crown on floor 27. | The approved art has 8 route floors on 27 floors. | The Bloom front is a continuous floor coordinate, so any rung count works. |

### Art inputs (read-only game state, nothing baked)

| Input | Type | Meaning for the art |
|---|---|---|
| `bloom_front` | float, route-layer units | The position of the infected edge. Rooms at or below it are INFECTED. |
| `bloom_gap` | float, layers | Distance from the front to the operative's current room. |
| `bloom_state` | enum | DORMANT, CREEPING, CLOSE, CATCHING, CAUGHT. |
| `raid_infection_pct` | 0 to 100 | Population infected, for raids. |

### Look (one family across all forms)

| Element | Rule |
|---|---|
| Hue | Solace pink `#FF4696`, used only as thin lit lines and the front edge. |
| Body | Dark plum, about `#24101C`, luma 0.03 to 0.05. It reads as necrosis, not as light. |
| Pattern | Diagonal 45° hatch plus vein lines, so the Bloom reads by pattern as well as by hue (colour-vision rule). |
| Front edge | Organic fingers that follow the surface direction. On the towers they follow the helix. It is never a flat water line. |
| Never | No lime, no mint, no kind colours, no state colours. No volumetric haze (the v3 plinth rule stands). The Bloom is an emissive/decal skin and ribbons only. |
| Glyph | SPORE: a ring with three notches. Chips: `INFECTED`, `FRONT -n` (the gap). |
| Easing | When the front advances, its edge slides over 10 frames (0.4 s, matching the occlusion rig). The view never waits for it. |

### Motion tempo (loops are 96 frames = 4 s at 24 fps)

| State | Pulse beats per loop | Period |
|---|---|---|
| CREEPING | 1 | 96 frames |
| CLOSE | 2 | 48 frames |
| CATCHING | 4 | 24 frames |

Vein scroll and spore motes also loop in 96 frames. Noise is seeded by node id, with no render-time RNG.

### Value rules (netrun median 0.14, landmark about 2x)

| Check | Rule |
|---|---|
| Frame median | A Bloom frame stays within ±0.01 of the same clean frame. |
| Body | Luma 0.07 or less. |
| Veins | Peak 0.30 or less in street netruns. In the HQ, 0.30 to 0.45. |
| Front hot edge | Peak 0.40 or less in street netruns (0.45 in the HQ). It covers 1.5% of the frame or less. |
| HQ ratio | The landmark/background ratio stays inside the accepted 2.2x to 2.8x from the notes. |

Every still gets measured: median, share under 0.10, share over 0.85, and the ratio.

### Occlusion rule (never hide route rooms)

1. **Layer order:** the Bloom draws under the route links, the room frames and the overlay glyphs.
2. **Keep-out:** each route room has a keep-out. In 3D it is the opening, the jamb, the frame ring and a 10% margin. In 2D it is the room's bounding box plus 10%. The Bloom is masked to zero inside it.
3. **Links:** the Bloom runs beside a link, never on it, with a keep-out of the link width plus 2 px each side.
4. **State colours:** the Bloom never recolours a room or link. INFECTED adds a plum wash behind the room and a pink hairline on the outer edge of the frame only.
5. **Camera rig:** buildings the rig flattens or ghosts carry the Bloom at their cut height and ghost opacity. They never show it above the cut.
6. **Overlay:** gauges sit outside the framing solver's target volume plus margin.

## A. Street netrun, light form

**Drawn:** the Bloom crawls along the route's links, then floods the facades around each infected room. Ahead of the front, everything is clean. It has no landmark and no tower.

| State | Look | Motion |
|---|---|---|
| DORMANT | Nothing drawn. A small SPORE glyph on the start room. | Static. |
| CREEPING | Beside-link tendrils and a plum wash on facades behind the front, with sparse veins. The front edge is a hairline. | 1 pulse per loop. |
| CLOSE | More veins, a brighter front edge, `FRONT -n` chip on the nearest clean room, and a bottom-edge band. | 2 pulses per loop. |
| CATCHING | Plum wash fills the lower third of the frame edge, with veins reaching the current room's keep-out. | 4 pulses per loop. |
| CAUGHT | One-shot, 24 frames. The current room's window floods pink-white, then goes to black. It then hands off to the existing death flow. | Once. |

**Overlay**

| Overlay | Look and place |
|---|---|
| TIDE gauge | A thin vertical strip at the screen edge. The route layers are ticks, the operative is a marker, and the plum fill rises to `bloom_front`. |
| Bottom-edge band | A 6% tall pink hair-line band. The front is usually below the camera frame, so the player needs a cue that does not rely on seeing it. |
| `INFECTED` chip | On rooms behind the front. |

**Frames to render (2560x1440):**

| Frame | Content |
|---|---|
| `S_clean` | Baseline, no Bloom, for diffing. |
| `S_creep` | CREEPING, front 3 layers behind. |
| `S_close` | CLOSE, front 1 layer behind. |
| `S_catch` | CATCHING. |
| `S_caught_strip` | CAUGHT, frames 0, 8, 16, 23. |
| `S_occl` | Bloom on buildings flattened and ghosted by the camera rig. |
| `S_states_sheet` | All states side by side with the glyph and chip set. |
| `S_loop_creep`, `S_loop_close`, `S_loop_catch` | 96 frames each, at 960x540. |

## B. HQ netrun, full form

**Kept from the approved landmark, unchanged:**
- The twin porcelain tubes with the full 360° twist over 27 floors, and the radius-40 spacing.
- Two windows per floor, with the inward window as the route node on route floors (every third floor).
- Bridges on route floors only, and the mint seam on the back band.
- The crown with THE GENOME CORE and its pink halo, the crisp plinth with no haze, and the existing cameras.

**Drawn:** a dark Bloom rises from the plinth up both strands as a skin layer. It follows the helix in one spiral band per tower. It sits at the same floor height on both towers because the front is one number.

| Part | Below the front (infected) | Above the front (clean) |
|---|---|---|
| Strand skin | Plum body, with pink veins following the twist. The leaf-green rim is damped to 30%. | Unchanged. |
| Windows | Non-node windows go from green-white lit to pink-dim, then dark. Per-instance `infect` value, 0 to 1. | Unchanged. |
| Node rooms (inward windows) | Kind colours stay. A plum wash is added behind the frame and a pink hairline on the frame ring's outer edge. | Unchanged. |
| Bridges | Pink hairlines on the glass edge only. The deck and interior light stay. | Unchanged. |
| Stair link (UP) | A 1.5 BU keep-out on the front band. The Bloom touches only the sides of the stair. | Unchanged. |
| Mint seam (back band) | Overtaken by the plum body. | Unchanged. |
| Plinth | Source point. Planter edge lights shift leaf-green to pink and the lobby trim takes a pink hairline. No haze and no beams. | n/a |
| Crown | Nothing until CATCHING. Then the halo brightens by 20% and pulses on the CATCHING beat. | n/a |

| State | Look |
|---|---|
| DORMANT | Plinth only: pink-edged planters. |
| CREEPING | A thin spiral Bloom on the lower floors. |
| CLOSE | The front is within the decision framing. The bottom-edge band and the `FRONT -n` chip appear. |
| CATCHING | The Bloom reaches the current room's floor. The 4-beat pulse runs, and spore motes (tiny emissive points) drift up. |
| CAUGHT | The current window floods pink-white and goes to black, as in the street form. In the overview shot the front reaches the crown. |

**Overlay:** the TIDE gauge is on the screen edge, outside the framing target volume. The overview camera shows the whole tower at once, so the band is visible there. The decision camera frames the current room, UP and ACROSS, so the front is usually out of frame. The bottom-edge band and the gauge carry the warning there.

**Value rules:** as in section 0. Veins are 0.30 to 0.45. The Bloom body is part of the landmark in the ratio, so the ratio stays inside 2.2x to 2.8x. The frame median stays within ±0.01 of the clean frame.

**Occlusion:**
- The Bloom is a skin shader applied outside the cutaway oval, jamb and frame ring, so it never covers a node opening.
- The v4 per-floor `built` flag and interior mapping are unaffected, because the Bloom is on the skin and window glass only.
- The camera rig's flatten and ghost rule applies to city blocks only. The Bloom does not appear on the city, except a pink hairline on the street ring at the plinth foot. Keep it crisp, no haze.

**Frames to render (2560x1440 unless noted):**

| Frame | Content |
|---|---|
| `H_bloom_overview_early` | Front at about 25%, operative at rung 4. |
| `H_bloom_overview_close` | Front 1 rung behind the operative. |
| `H_bloom_overview_catch` | Front at the crown. |
| `H_bloom_decision_far` | Decision, front out of frame, with the band and TIDE gauge. |
| `H_bloom_decision_close` | Decision, front visible at the bottom. |
| `H_bloom_hover_across` | Hover ACROSS with a Bloom-edged bridge. |
| `H_bloom_plaza` | Plinth source and lobby. |
| `H_bloom_window_detail` | Infected window, clean window, and an open node window, side by side. |
| `H_bloom_crown` | Halo reaction. |
| `H_bloom_caught_strip` | CAUGHT, frames 0, 8, 16, 23. |
| `H_bloom_states_sheet` | All states. |
| `H_bloom_loop_creep`, `_close`, `_catch` | 96 frames each, at 960x540. |

## C. Raid hook (city / raid map)

**Drawn:** a population gauge and a district hatch that grows with `raid_infection_pct`. The home-server nodes you defend are never recoloured.

| Element | Look | Place |
|---|---|---|
| Gauge | A wide strip labelled `POPULATION INFECTED nn%`. Plum fill with a pink front edge and the SPORE glyph at the leading end. The 100% end cap is marked `CITY LOST`. | Top of the map, outside the node area. 4% of the frame or less. |
| District fill | 45° hatch (2 px lines, 8 px pitch, pink at alpha 0.35) plus the plum wash. Hatch density follows the percent. | Under the node and link layers. |
| Spread edges | The hatch advances district by district from the Solace source, with fingers along streets. | Under the nodes. |

| Visual stage (art bands, not rules) | Look |
|---|---|
| 0 to 24 | Source district only. |
| 25 to 49 | A third of the map seeded. |
| 50 to 74 | Majority hatched. The gauge pulses 1 per loop. |
| 75 to 99 | Plum wash dominant. The gauge pulses 2 per loop. |
| 100 | The whole map floods plum, with the gauge cap lit. This is the Solace-wins frame. |

**Value rules:** hold the Grid's current median ±0.02 at every percent. The hatch alpha is 0.35 or less. Node frames and rings keep their colours. The Bloom adds no new ring or link colour.

**Occlusion:** layer order is map, district fill, links, home-server nodes, gauge and chips. The fill never covers a node's label or its ring.

**Frames to render:**

| Frame | Content |
|---|---|
| `R_00` | 0%, clean. |
| `R_22` | 22%. |
| `R_58` | 58%. |
| `R_91` | 91%. |
| `R_100_lost` | 100%. |
| `R_node_detail` | A home-server node under attack inside a hatched district. |
| `R_gauge_sheet` | Gauge at each stage, with glyphs. |
| `R_loop_gauge` | 96-frame gauge idle loop. |

## D. Grid (city map) layer

Recommendation: **no live Bloom on the Grid.** Raids already carry the percentage, so the Grid stays calm.

| Layer | Look |
|---|---|
| Solace turf mark (passive) | A faint plum stipple on Solace districts, with a SPORE corner tick on Solace-owned nodes. No new rings or links. |
| Raid-active node | The corner tick pulses on the CLOSE beat while a raid is live. |

**Occlusion:** the stipple draws under all nodes and links, and under the Grid's own labels.

**Frames:** `G_turf` (Grid with Solace turf), `G_turf_raid` (with a raid-active node), `G_turf_vs_others` (Solace stipple beside another corp's turf, to confirm it is distinct).

## Kit reuse vs new

| Reuse | New |
|---|---|
| Route links, room frames, node states | Bloom skin shader: world-height front, noise, mask |
| UNREAD frost decal and the `read_horizon` wipe, as the template for the front wipe | Beside-link tendril ribbon mesh |
| `visible_outline` and `room_shape` as keep-out masks | `infect` per-instance value on the window MultiMesh |
| Fresnel rim, porcelain materials, mint seam | SPORE glyph, `INFECTED` and `FRONT -n` chips |
| Camera rig occlusion state per instance | TIDE gauge, bottom-edge band |
| Crown pink halo | Raid percentage gauge and district hatch |
| Interior mapping and `built` flag | CAUGHT one-shot beat |

## Risks

| Risk | Mitigation |
|---|---|
| Pink Bloom collides with the crown's pink halo and any kind colour. Red (elite) is close. | Bloom pink only as thin lines. The crown halo stays at its approved size. Check against the kind sheet. |
| The Bloom is out of frame in decision shots, so the player gets no warning. | Bottom-edge band and TIDE gauge, which are outside the framing target volume. |
| A dark Bloom on a dark city reads as missing geometry. | Veins, hatch and spore glyphs, plus the `INFECTED` chip. |
| A flat band looks like rising water. | Organic fingers that follow the helix, and a hatch pattern. |
| The Bloom drifts the frame median off 0.14. | Median check within ±0.01 of the clean frame, on every still. |
| Frost and Bloom overlap. | They should not. Frost is ahead of the operative and the Bloom is behind. Confirm in Question 4. |
| Draft pressure tint and debts pips use the same glass and hue. | Question 9. |
| Raid end state mistaken for a generic game-over. | The `CITY LOST` cap and the Solace plum wash identify it. |

## Questions for the build session

1. Does the front advance by room, by time, or by turn? The art needs only `bloom_front`, but the gauge units depend on it.
2. Is the front a layer number (same on both HQ towers) or a path distance?
3. What are the CLOSE and CATCHING thresholds in layers? The art bands above are placeholders.
4. Can the operative be ahead of the read horizon and the Bloom at the same time? If so, do frost and Bloom ever coexist?
5. Do skipped branches behind the front count as INFECTED? Does the other tower's room on the same rung?
6. Does a crossing (ACROSS) change the gap? Does it cost time? The art does not depend on it.
7. Is `raid_infection_pct` a rising value with a known rate? May the art show a rate chip?
8. Is the raid on a 2D map or a 3D view? The Grid's current median is also needed to hold the value rule.
9. Are `tower_pressure` and `debts` from the HQ draft ruled in? If yes, they need another visual channel.
10. Does a lost raid ("Solace wins") end the campaign, or leave a permanent Grid scar? That decides whether Part D stays minimal.
11. Does CAUGHT hand off to the existing death flow, and what is the campaign-end text on `CITY LOST`?
12. Are the 4 s loop tempos (1, 2, 4 beats) acceptable for the pulse, or does the audio set its own pace?