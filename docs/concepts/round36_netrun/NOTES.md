# Round 36: netrun follow-ups (node states, Heat B, rules, node backdrops, zoom transitions)

Locked from round 35:
- **HQ** is the overhead **compound**. Unique HQ mechanics come in a later pass.
- **Heat** is **option B**: darker orange, the city reacts, lights circle.

The unified city/raid/run building pass belongs to another agent, so this round leaves the city kit alone.

All work is in `docs/concepts/round36_netrun/`. Nothing is committed and `scratch/` is cleared.

## Files

| File | Point | What it shows |
|---|---|---|
| `city_states_a.png` | 1, 2a, 4 | **Option A.** Nodes keep their normal icon colours. The Meridian crest is corp orange, Heat-objective Sites carry a flame, and the T3 Exploit Sites carry a gold key. The state is an **outline circle**: white = unavailable, **orange = selectable** (the path colour), **lime = visited** (its line colour). The Cell's own nodes stay lime raid pads. |
| `city_states_b.png` | 2b | **Option B.** The round 35 scheme (state-coloured pads), with the white wash on not-yet icons cut from 55 % to **20 %**, and cleared Sites greyscale. |
| `transit_states_a.png` / `transit_states_b.png` | 2 | The same two options on the run map. In A, the stickers keep full colour and the rings carry the state. Nodes that can't be reached any more get a dim grey ring: **the run never goes back**. B uses the light wash. |
| `city_heat_b.png` + `city_heat_b.gif` (2.3 MB) | 3 | **Heat B, darker orange (#CE5412).** See below. |
| `node_backdrop.png` + `.gif` (1.0 MB) | 5 | **A dressed room as a node's backdrop.** See below. |
| `zoom_a_wheel.gif` … `zoom_e_terminal.gif` (0.9–1.8 MB each) + `zoom_compare.png` | 6 | Five mixed-media city-to-link transitions. See below. |

**Every city view also has:**
- the **AT LARGE** stamp beside the operative's name on the dossier (point 1);
- the target chip relabelled **CENTRAL SERVER // EXPLOITS 0 / 3** (point 4);
- a **PATROL** affordance on a cleared Site (point 4): a circular-arrows mark, a CLEARED chip and a `PATROL [P]` terminal button reading "loot, Heat, Rank; no objective" (GDD 3.3).

### `city_heat_b` in detail
- **City-wide:** searchlight sweeps (the locked H1 language) and a dark-orange edge haze.
- **Per node:** circling red/blue police lights on a dark-orange ring centred on each **node that Heat has made harder**.
  - Each has a searchlight locked onto it and an effect chip: `HEAT: +1 ELITE`, `HEAT: SHOP STOCK -1`, `HEAT: +1 RESISTANCE`.
  - These are the GDD 4.3 Minor complications and Major modifiers, placed on the Site they affect.
- **The number:** the Heat strip is gone. The number lives on the dossier as a `HEAT 52: HUNTED` stamp. The GIF loops the circling lights and the sweeps.

### `node_backdrop` in detail
- From the compound, the operative enters a Terminal node and the camera cuts to that node's close-up: a dressed container room from the climb set (the desk and screen-wall Terminal room).
- That close-up is the backdrop behind the node's screen. The event shown is the real `ev_mer_manifest_glitch` (title, text, three choices with outcome chips).
- An inset shows the compound with the entered node ringed. The GIF plays it: compound > ring > zoom > cut > room > event.

### The five transitions in detail
- **A, wheel lens:** a spinner slaps onto the link and spins. Its hub opens onto the transit view, and the ring flies past the camera.
- **B, sticker peel:** the city map peels back from the corner like a sticker. The run is printed underneath.
- **C, pencil dive:** the pencil rings the chosen Site and the camera dives through the ring.
- **D, CRT channel change:** the map collapses to a scanline, then a dot. The link's channel opens with an "CH 15 DEPOT 15" on-screen label.
- **E, terminal jack-in:** the Cell's terminal types the connection. Binary rain falls along the link, washes the map away, and thins onto the transit view.

## Recommendations
- **Node states: option A.** It fixes the washed-out look at the source: icons always read in their real colours, and the state is a single ring whose colour matches its link (orange path, orange ring; lime line, lime ring). It also costs one shader parameter instead of a colour treatment per sticker. Option B is the fallback if rings feel busy at city zoom.
- **Transition: A, the wheel lens.** It uses the game's core object, so moving from map to run reads as "the Cell's wheel takes you there", and it is clean at under 1 s. Its hub radius is a single shader uniform (a circular reveal) over the two views. The runner-up is **D, CRT**, the cheapest to build and the cleanest. B (peel) is the most charming but covers half the screen with the backing for a beat.

## Rules applied (point 4)
- **Exploits.** The T3 key nodes *are* the Exploits. The Central Server needs 3, so the chip reads EXPLOITS 0 / 3.
  - **Open:** GDD 4.1 says Exploits sit on **T2** Sites. Either the GDD changes to T3, or the key plates move to T2. This needs a DECISIONS entry.
- **Run map.** Past nodes are never revisited. Unreachable nodes keep a dim grey ring (A) or a greyscale sticker (B) for context, and can't be selected.
- **City map.** Cleared Sites can be patrolled (GDD 3.3), as shown on the grey or lime cleared Site.

## Godot notes
- **Option A ring:** one `ring_color` parameter on the node sticker scene (white / orange / lime / dim grey), with the glow on selectable only. Icons are never tinted.
- **Heat B node marker:**
  - two additive point sprites orbiting the node (red and blue, about 1.1 s per turn);
  - a dark-orange ring decal;
  - a `SpotLight` cone sprite aimed at the node;
  - an effect chip from the complication's content id.
  - City-wide sweeps are the existing H1 searchlights.
- **Node backdrop:** each compound node references a room preset (kind × dressing variant). Entering renders or loads that preset as the event or combat backdrop, matching the round 30 rule that the combat backdrop is the zoomed-in place you fight in.
- **Wheel lens:** the player wheel scene, scaled and spun by a tween. A circular `reveal_radius` uniform on the transit view's `SubViewport` texture follows the hub, and Skip snaps to the end.

## Build (from `scripts/`)
1. Blender 5.2 headless:
   - `r32_scene.py -- tower ../scratch/bl room` (the room close-up, new this round);
   - `iso_scene.py -- ../scratch/bl transit`;
   - `compound_scene.py -- ../scratch/bl 0`.
2. `finish.py` for `tower_room`, `iso_transit` and `compound_f00`, written as `scratch/fin/tower_room.png`, `iso_transit.png` and `compound_full.png`.
3. `python states36.py all`, `python backdrop36.py`, `python zoom36.py all`.

All randomness is seeded.
