# Round 21: raid UI (the world half is in `round21_raid_world/`)

Locked from round 20 and kept as they were:
- red grease-pencil raid routes;
- the DOWN wipe;
- the CELL HOLDS sticker;
- panel option E, "by fiction" (network = CRT terminal, work order = intercepted memo under glass, intel = holo).

## Files
| File | What |
|---|---|
| `raid_setup_night.png` | Setup with the round 21 rules: denser holo intel with the decrypted Halcyon mark, the parked ICE LOCK card and its pencil targeting arrow resolving into a yellow circle on the Vault, and speed/skip below START DEFENSE. |
| `speed_position.png` | Speed/skip below START DEFENSE (**picked**) vs above the work order. |
| `intel_decrypt.png` | Holo intel DECRYPTED (normal) vs NOT DECRYPTED (proposal: a Heat consequence). |
| `node_health.png` + `node_health.gif` | Health v2: the outline and icon stay lit; only the inner fill drains, north to south. The red diegetic numbers are brightened. |
| `path_rules.png` | Grease-pencil path rules in 6 frames (from gifs 09 and 16). |
| `raid_report.png` | The raid report as Halcyon's own **after-action report** (work-order paper family) with the Cell's grease pencil on it. |
| `interactions_gifs/` | All 27 gifs re-encoded (saturation kept), the listed ones redone, plus `index.md` and `index.jpg`. |
| `contact_sheet.jpg`, `scripts/` | |

Rebuild:
1. `python scripts/run_blender.py`
2. `blender -b --factory-startup --python scripts/vehicles.py -- <abs>/scratch/bl sprites`
3. `python scripts/screens21.py`

`screens21.py` is the round 20 builder with the round 21 blocks swapped in. `ui21.py` and `netdecal21.py` hold the new parts.

## Changes
**Panels (E).**
- The holo is less transparent: a denser fill, a near-opaque scrim (0.88) behind it, and stronger scanlines.
- The intel holo carries the **Halcyon mark** (a halo over the civic pyramid). It is cracked by a red fracture and stamped **DECRYPTED**, with "decrypted by the Cell // key 7F-A2", so the panel reads as hacked enemy data.
- The **NOT-decrypted** variant shows garbled rows, route letters as "?", the mark intact under an **ENCRYPTED** stamp, and a lock. On the map the routes would be withheld, with only the entry Sites circled.
- *Proposal for the GDD:* e.g. "Heat 75+: threat intel encrypted". GDD 4.3 has no such modifier today.
- The work-order paper is unchanged.

**Speed/skip.** Same terminal strip in both positions. We pick **below START DEFENSE**:
- START lifts a little and the strip sits under it, greyed out during setup.
- In the playout START peels away and the strip stays in the same spot, so the "go" controls stay together.

**Node health v2** (`netdecal21.health_pad`):
- The **outline** (frame + pins) keeps its active colour throughout. The **icon** (glyph + inner square) stays fully lit.
- Only the inner **lit fill** (a soft colour fill plus the integrity track) drains from the north point to the south point.
- The drained part shows a faint hatch in the active colour, and a thin bright line marks the drain front.
- At 0 the socket switches to the disabled amber with the dashed outline.
- Low-health numbers are a brighter red, `(255, 128, 112)`. Yellow is unchanged.

**Path rules** (grease pencil):
- **SOLID** red = the active route. **DASHED** = a what-if.
- Setup, while dragging or hovering a DECOY over a node: the part of the active route that would disappear is **scribbled through** (a tight zigzag), and the new route is drawn **dashed**.
- Placed: the scribbled part is **erased** (cloth wipe) and the new route is drawn **solid**.
- Raid: the lure never re-routes on its own. The route shown after setup is exactly what happens; only if the decoy is **destroyed** does the decoy leg erase and the original route redraw solid (gif 16).
- This is true to `raid_resolver`: `_decoy_site` only counts decoys on active nodes. **Assumption to confirm:** the code does not visibly damage assets themselves, so "decoy destroyed" equals its node going down.

**Card drag model** (gifs 01–03, 06):
1. The sticker peels off the tray and **parks** in a dashed sticker parking slot.
2. A **yellow pencil arrow** draws from the parked card to the cursor.
3. Near a node it resolves into a **yellow circle** (valid: white socket frame, green forecast ring, IF PLACED terminal) or a **red pencil X** (invalid: red socket, NO SLOT terminal, then the card returns to the tray).

Swap: the placed unit's sticker peels **off its node**, flies to the slot, then the arrow targets the new node.

**Gifs.**
- **Palette fix for all gifs:** one shared 255-colour palette built from five spread frames, with Floyd-Steinberg dithering and a fallback ladder to stay ≤ 2 MB. Saturation now holds; the round 20 gifs used one mid frame's palette at 128 colours with no dither.
- **Redone:**
  - 01, 02, 03 and 06: the drag model.
  - 07: palette only.
  - 09: the decoy in setup.
  - 10: the frozen link. It keeps the round 19 frozen trace, plus the **slice FROZEN overlay** recipe in screen space: cold tint, crust grown from the edge, crystal ridges at the crust front, white cracks and twinkling glints.
  - 12: INCOMING with letter spacing. Pencil tracking went from 0.20 to 0.45, which applies to all pencil words.
  - 15: the threat encased in that frost.
  - 16: the decoy destroyed and the route reverting.
  - 22: a **binary-bit explosion** at CORE (flash, shock ring, 0/1 bits blasting out and falling).
  - 24: the corp report.
  - 26: **BREACHED** as a double-pass heavy wax word with an underline, a red bit-explosion and a red flash.

**Raid report.** An intercepted Halcyon **AFTER-ACTION REPORT**: letterhead with the mark, rule line, the operation line, a values table, a redacted footer, and a **CLASSIFIED** stamp. The Cell's pencil:
- circles what we gained / they lost: "THEY LOST 6" and "OURS! +12" (the Schematics);
- writes **RIP** next to the reclaimed Site and on the lost node on the map;
- ticks HOME INTACT.

CELL HOLDS slaps on top. The Heat line is on the paper ("52 > 52 no change"); a lost raid would read +5.

## Weakest / open
- **Gif 16:** the decoy explosion and the route revert happen while the unit waits on the proxy, which is true to the stop-at-live-node rule but reads a little static.
- **Halcyon mark:** it is drawn here; the world agent's corp emblems should replace it.
- **For the designer:**
  - Approve NOT-decrypted as a Heat rule (GDD).
  - Confirm that "decoy destroyed" = its node disabled, or ask for asset damage in the resolver.
