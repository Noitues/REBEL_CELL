# Round 41: multi-drone docking, the parasite pop-up, and the full wheel stack

Builds on round 40 (untouched). The blended dock, the replace animation and parasite option A are kept as agreed. The other agents' locked layers are redrawn in their agreed form for the combined mock:
- tier V2 strong;
- state overlay with the badge plus ×N tab and rule tag (outer clockwise corner);
- firmware socket at r = 168 (round 34);
- inner-ring texture extension and sub-needle (rounds 39 and 40).

## Files
| File | What it shows |
|---|---|
| `multi_drone.png` | Two drones on one slice (hangar): Botnet and Care Swarm at r = 220, the pair under the needle, and r = 60. |
| `parasite_popup.gif` | 25 frames, about 3.6 MB. The steps: 1. attached while the needle is elsewhere; 2. a 35-tick spin where it crosses the needle mid-spin and stays attached; 3. the wheel settles with the needle on it and it pops up beyond the tip; 4. the in-line sub-slice fires (PATCH 6 heals the boss); 5. on the next spin it drops back to attached. |
| `parasite_drones.png` | A parasite plus 1 or 2 drones on one slice, both attached and popped. Also the whole wheel at r = 220 and r = 60, and the rules. |
| `wheel_stack_combined.png` | The worst case. The whole wheel at r = 220, the slice enlarged, r = 60, the z-order, the radial zones of one slice drawn to scale, and the conflicts with their rules. |
| `scripts/` | `stack41.py` holds `dock_multi`, `put_drones`, the parasite states and the per-slice layers; `make41.py multi`, `popup`, `pdrones` and `combined` build the outputs. Also patched: `sat3.parasite2(radii=)`, `d4corp` (per-slot tier) and `tiles` (player tier colours). |

## 1. Two drones on one slice
- **One blended dock:** one rim band over the slice, plus a neck and collar per drone.
- **Placement:** the pair sits at the slice centre ±14°, so the collars clear each other and the needle blade passes between them. A single drone stays centred.
- **Replacing on a full hangar:** the targeted drone is replaced (default: the older one). It returns to the core as green bits.
- **Still open:** how damage works with two drones on one slice.

## 2. Parasite pop-up
- **Attached state:** a thin band hugging the frame over its slice (r RA + 6 to RA + 48), glyphs only. It stays like this while the needle is elsewhere, and during any spin, even when it crosses the needle.
- **Popped state:** once the wheel settles with the needle on its slice, it tweens out to option A. That means beyond the needle tip, at full depth, with glyphs and values. The sub-slice in line with the tick fires.
- **On the next spin** it drops back to attached.

## 3. Parasite plus drones
- **Radial order:** frame, then parasite, then drones. Drones dock beyond the parasite with a 26-unit gap, and their necks pass under it.
- **When it pops,** the drones move out with it, tweened together.
- **Bodyguard is unchanged:** a pointer attack on the slice hits a drone first.
- **The parasite is not a satellite.** It is never hit and never guards.

## 4. The full stack: z-order, bottom to top
1. slice screen
2. ring texture extension
3. tier inset
4. state overlay wash
5. firmware socket
6. sub-needle
7. **read block**
8. state badge + ×N tab + rule tag
9. frame + telemetry
10. dock lobes
11. parasite
12. drones
13. needle blades
14. card-preview ghosts

## Radial zones (master units, player wheel)
| Element | Radius |
|---|---|
| Hub + inner ring | < 127 |
| Sub-needle | 122 – 152 |
| Ring extension | 132 – 182 |
| Firmware socket | 142 – 194 |
| Read block | 230 – 306 |
| Badge | 300 – 352 |
| Frame | 360 – 414 |
| Needle | 336 – 510 |
| Parasite (attached) | 420 – 462 |
| Parasite (popped) | 526 – 616 |
| Drones | 642 – 884 |

## Conflicts and proposed rules
1. **Ghost blade vs a popped parasite or drones.** While a card is hovered, popped parasites on other slices drop back to attached. Ghosts draw on top of everything.
2. **Sub-needle vs firmware socket.** The sub-needle's tip stops at the slice lip (r 152). The socket sits at r 168. They always have a gap between them and never overlap.
3. **State overlay vs read block.** The wash stays at 45 % or less, and the read block is always re-stamped on top.
4. **Drones vs needle.**
   - A pair flanks the blade at ±14°.
   - A single drone on the needle's slice sits centred, beyond the blade top or the parasite. It is never under the blade.
5. **Headroom.** A popped parasite plus drones needs about 470 master units above the rim (about 290 px at r = 220).
   - When that happens on the top slice, the forecast tag shifts sideways.
   - Alternatively, the wheel scales down 10 %.
   - This is an open question for the designer.
6. **At r = 60** only colour, glyphs and the parasite and drone silhouettes survive. All values move to the forecast chip.
7. **Tier III gold border vs ring extension.** Both are warm, so the extension (hatch) is drawn at 120 alpha under the inset line. Tier always wins at the screen edge.

## Weakest parts
- **The worst case is tall.** It is legible at r = 220 but crowds anything placed above the wheel.
- **The sub-needle and firmware socket are small** next to the tier III border at sheet scale.

---

# Combat fit check: `combat_worst_case.png` and `combat_typical.png`

Both screens use the locked round 31 layout:
- player wheel at (481, 490), r = 220;
- boss (The Manifest) at (1438, 520), r = 236;
- the round 31 backdrop and HUD, with the HUD drawn on top as in the game.

Each HUD panel that hides wheel content is outlined in red with the share of its area covered. The off-screen figure is the share of the wheel extras (everything outside the frames) that falls past the screen edge. Both come from `scripts/combat41.py worst|typical`.

**Worst case.** Both wheels carry, on every slice:
- 2 drones (12 per wheel);
- a parasite (attached, and popped on the needle slice);
- a status with a ×N tab (×2 to ×5).

The player also has tiers I to III, the inner ring with extensions on every slice, firmware sockets on every slice and a sub-needle. The boss is at tier III. Bosses have no inner ring or firmware, so those are player-only.

**Typical.** The player has 1 drone, 1 firmware chip and 1 status. The boss has 1 drone, 1 status and 1 parasite (attached).

## Verdict
**Typical fits.** 0 % is off-screen and no HUD panel hides anything. The one issue: the boss's single drone sits at the screen's right edge, and its pointer tab clips.

**Worst case does not fit.**

| Measure | Result |
|---|---|
| Wheel extras off-screen | 6 % |
| Nudge buttons hidden | 71 % |
| CELL-9 sticker hidden | 69 % |
| Player HP + NEXT hidden | 66 % |
| Boss HP + NEXT hidden | 57 % |
| Both forecast tags hidden | 50 % |
| Buttons + SEND IT hidden | 40 % |
| Hand hidden | 21 % |
| Status bar hidden | 17 % |

What clips or becomes unreadable:
- **Between the wheels**, the two drone halos interleave, so you can't tell which wheel a drone belongs to.
- **The popped parasite on the boss** covers the boss nameplate banner.
- **At the top**, drones run off-screen. On the player wheel, the drones above the needle also collide with the forecast tag.
- **Slice values stay readable**, because the read block is always on top. But 6 status badges, ×N tabs and firmware chips per wheel turn the rim into noise.
- **Drone values (3/5)** at this scale are about 14 px. They are readable one at a time, but not as a set of 24.

## Mitigations (proposed, in priority order)
1. **Collapse drones into a count badge past one per slice, or past four per wheel.**
   - A slice with 2 drones shows one drone plus a "×2" pip.
   - When a wheel has more than 4 drones, the rest collapse into a single docked "DRONES ×8" pod at the rim's free side.
   - Hovering a slice expands its drones.
2. **Hide the parasite until it's relevant.** Show only a 6-unit-thin tinted rim stripe (no glyphs) while the needle is elsewhere. Pop it up when the needle settles on it, or when a card preview lands there. This is the same rule as round 41 §2, made stricter.
3. **Scale rule: the wheel extras budget.** Measure the radius of the extras. Past 1.6 × R_OUT, scale the whole wheel group down, to a minimum of 0.8 × r. Also slide the forecast tag and HP/NEXT plate outward along the wheel's free diagonal.
4. **Status: one corner badge per slice, with the highest stack shown.** Show the full list on hover and in the forecast chip. Hide ×N tabs at r < 150.
5. **Firmware: show the chip only on the slice under the needle and on hover.** The other slices get a 3-pin LED dot.
6. **Ownership tint.** Each drone collar is tinted with its owner's frame colour, so interleaved drones still read as player or boss.
7. **Hard limits** (an open question for the designer): no more than 2 drones per slice, and no more than 6 drones and 2 parasites per wheel.

These open questions should go into `DECISIONS.md` under "Open questions for the designer".

---

# v2: drones collapsed, inner ring, re-test (`_v2` files)

## Files
| File | What it shows |
|---|---|
| `drones_v2.png` | Drones collapsed and hovered, each with and without a parasite, plus the locked inner ring with its texture extension. |
| `combat_typical_v2.png` | The typical case. |
| `combat_worst_case_v2.png` | The worst case, with the drones on slice 3 hovered. |
| `combat_worst_case_spin.gif` | 16 frames, 3.8 MB: both wheels spin, settle, and the parasite under each needle pops up. |

Scripts: `stack42.py` (v2 drones and the locked inner ring), `ringlock.py` (a verbatim copy of the round 39/40 `ring2.py` ring functions, rebanded to the D4 hub, 100–127) and `combat42.py worst | typical | sheet | frame k | gif`.

## Changes
1. **Drones are smaller and sit closer to the wheel.** They are 0.22 of the host, down from 0.30.
   - With no parasite, the drone has a short stem and sits at RA + 30.
   - With a parasite, there is no stem and the drone sits directly on the parasite's outer edge.
2. **Drones are collapsed by default.** Each slice's drones become one thin band, 34 units deep, with one tile per drone. Each tile shows the drone's current effect (glyph and value) and its HP pips.
   - Hovering the slice, or aiming a card at a drone, blooms the band into the full mini-wheels, each with its needle.
3. **The inner ring now uses the locked round 39/40 look:**
   - per-segment textures, machined lips, grooves and bolts, and glyph plates;
   - each segment's texture extends into its aligned outer slice. Strength is raised to 1.7 so it shows at combat scale.
4. **Re-test.** Same worst case as before: 2 drones, a parasite and a status ×N on every slice of both wheels, with the inner ring populated.

## Verdict: the worst case now fits
| Measure | v1 | v2 |
|---|---|---|
| Off-screen | 6 % | **0 %** |
| Player forecast hidden | 50 % | 23 % |
| Boss forecast hidden | 50 % | 18 % |
| Name sticker hidden | 69 % | 11 % |
| Boss HP hidden | 57 % | 5 % |
| Nudge Q | 71 % | 0 % |
| Player HP, hand, SEND IT, status bar | 17–66 % | 0 % |

**The typical case** is 0 % off-screen and hides nothing, apart from 2 % of the name sticker.

## Still clipping or crowded
- **Nudge E is 81 % covered**, but only while the slice next to it is hovered: the bloomed drones sit on the button. Suggested fixes:
  - bloom away from HUD controls, by mirroring the drones to the slice's other side;
  - or temporarily nudge the button outward.
- **The popped parasites reach the top forecast tags** (18–23 %). Suggested fix: the tags gain 30 px of top margin, or slide sideways when a parasite pops on the top slice.
- **Six status badges with ×N tabs per wheel are still busy.** The rule "one badge per slice, full list on hover" still applies.
- **The drone band tiles are small at r = 220**, about 14 px values. That is acceptable because hovering shows full size, and the forecast chip carries the numbers.

---

# v3: HUD rework (`combat_worst_case_v3.png`, `combat_typical_v3.png`, `combat_worst_case_spin_v3.gif`)

Script: `scripts/combat43.py worst | typical | frame k | gif`.

## Changes
1. **Nudge buttons sit above each wheel.** They keep roughly their old lateral positions and swap sides: anticlockwise (CCW) on the left, clockwise (CW) on the right.
   - Player buttons: (192, 190) [Q] and (770, 190) [E].
   - Boss buttons: (1150, 215) and (1726, 215), with no key labels yet. Assigning keys is an open question.
   - All four clear the popped parasites and the hovered drones.
2. **The CELL-9 // BREAKER sticker moves to just above the RAM readout,** at (24, 846).
3. **The forecast tags and NEXT plates are removed.** Instead, each HP value gets **result chips**: what this turn does if SEND IT is pressed now.
   - Player: "♥ −14".
   - Boss: "♥ −8" and "shield +4".
   - **Hovering a chip shows a breakdown tooltip** (shown on the boss's −8 chip): YOU: ZERO-DAY 12 (GOOD), − its SHIELD 4, = −8 HP (340 → 332); IT: EXPLOIT 14 (PERFECT), −14 HP to you; Priority Routing: +4 SHIELD.
4. **The boss HP readout moves right,** centred at x = 1500, so it clears the HEAVY SPIN card.

## Overlap check (v3)
**Worst case:** 0 % off-screen, and no HUD element is covered by wheel content. I measured every kept panel, the sticker, all four nudge buttons and both HP readouts with their chips.

**Typical case:** 0 % off-screen, no overlaps.

**Remaining note:** the hover tooltip appears over the bottom of the boss wheel. That is acceptable because it is transient.

**The spin GIF was re-made as v3** because the HUD changed: 16 frames, 3.8 MB.

---

# v4: nudge alignment, boss nudge keys, forecast format (`*_v4` files, `scripts/combat44.py`)

1. **Nudge alignment.** All four nudge buttons sit on one line at y = 216: player at x 192 / 770, boss at x 1150 / 1748. I lowered them from y 200 because the popped parasite's turn pips grazed the boss CW button.
2. **Boss nudge keys:** [A] for CCW and [D] for CW. These are proposed keys; confirm they don't clash with other bindings.
3. **Forecast beside each HP**, in this order:
   1. **final damage** (red, boxed);
   2. **absorbed** (blue, "(N shield)", no box);
   3. **shield gained** (green "+N shield");
   4. **other losses** (red "−N icon", for example RAM; none happen on this screen);
   5. **status icons** with ×N.

   Hovering the final-damage chip keeps the breakdown tooltip.

## Values used (from the screen)
| Case | Player | Boss |
|---|---|---|
| Typical | −14 | −8, (4 shield), +4 shield |
| Worst | −21 (EXPLOIT 14 × 1.5), OVERCLOCKED ×2 | −14 (ZERO-DAY 12 × 1.5 = 18, minus 4 absorbed), (4 shield), +4 shield, OVERCLOCKED ×2 |

In the worst case, both resolving slices carry OVERCLOCKED ×2 (×1.5).

## Overlap check (v4)
- **Worst case:** 0 % off-screen, no overlaps.
- **Typical case:** 0 % off-screen, no overlaps.

**The spin GIF was re-made as v4** (16 frames, 3.5 MB). Its forecast chips show the pre-spin values on every frame. In the game they would update when the wheel settles.
