# Round 37: hidden nodes, calm Heat B, the mixed jack-in transition

Locked from round 36:
- node outlines, option A;
- the node backdrop;
- Heat B.

**Exploits are back on T2** (GDD 4.1). The gold key plates now sit on three T2 Sites, and the target chip reads CENTRAL SERVER // EXPLOITS 0 / 3.

Nothing is committed and `scratch/` is cleared.

## Files

| File | What it shows |
|---|---|
| `city_default.png` | **Default.** Only the Cell's nodes, the selectable next Sites (orange rings), visited and cleared Sites (lime, with PATROL) and the TARGET are drawn. Hidden nodes take their links with them. |
| `city_node_hover.png` | **Node hover.** The cursor rests on empty map. The hidden node under it fades in (white ring) with a tooltip: tier, Exploit if any, and "not yet available: claim a neighbour first". |
| `city_legend_hover.png` | **Legend hover.** The cursor rests on the map legend strip, which reads "HOVER HERE: SHOW ALL NODES". Every node and link fades in, and the strip turns lime ("SHOWING ALL NODES"). |
| `city_visibility.gif` (1.7 MB) | Default, then the cursor travels to a hidden node, then on to the legend, where all nodes show. |
| `city_heat_calm.png` / `.gif` (2.7 MB) | **Heat B calmed.** See below. |
| `transition_mix.gif` (1.2 MB, about 4.4 s) | Terminal connect, then the window despawns, then the wheel spins up, then the wheel-lens zoom. See below. |
| `transition_storyboard.png` | The 7 beats with their start times. |

All three city stills also show the **Options > Map** toggle "Always show all nodes", drawn off.

### Calm Heat B (`city_heat_calm`)
- **City-wide:** two slow searchlight sweeps (12 frames at 220 ms per loop, about 2.6 s), at lower intensity.
- **Per node:** each hardened node has one soft circling light (alternating red and blue) on a thin dark-orange ring, plus its effect chip (`HEAT: +1 ELITE`, `HEAT: +1 RESISTANCE`).
- **Placement:** only selectable nodes carry markers, so they are visible by default.
- **The number:** the Heat value stays on the dossier stamp.

### The mixed transition (`transition_mix.gif`)
0. **JACK IN** is pressed.
1. The Cell's terminal types `jack --from RELAY_4 --to DEPOT_15`, routing, and the handshake.
2. **CONNECTED.** Binary rain falls only along the chosen link.
3. The terminal window despawns as a CRT collapse: it squashes to a line, then a dot.
4. The operative's wheel slaps onto the link and spins up (motion blur).
5. **Wheel lens.** The hub opens onto the transit view, and the ring flies past the camera while spinning.
6. The run.

## Rules and build notes
- **Visibility rule (view-only, no game state).** A node is drawn if any of these hold:
  - it is owned or visited;
  - it is selectable (unowned across a border link);
  - it is the target;
  - `always_show_nodes` is on;
  - the legend is hovered;
  - it is the node under the cursor (pick radius about 40 px, 0.15 s fade).

  Hidden nodes still exist for panning, hit tests and raids.
- **Settings:** add `always_show_nodes: bool = false` under Map. It is UI state only; no schema change.
- **Transition:**
  - one `AnimationPlayer` track per beat;
  - the terminal is the existing CRT panel, with a squash tween to despawn;
  - the wheel is the operative's real wheel scene;
  - the lens is a `reveal_radius` uniform on the transit `SubViewport` texture.
  - **Skip** snaps to beat 6. After the first few runs, beats 1–3 can shorten to about 0.6 s, as a setting.

## Build (from `scripts/`)
1. `blender -b --factory-startup --python iso_scene.py -- ../scratch/bl transit`
2. `python finish.py ../scratch/bl iso_transit ../scratch/fin/iso_transit.png`
3. `python r37.py all`

All randomness is seeded.
