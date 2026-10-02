# Round 19: raid view after the designer review

Locked from round 18: **nodes and links on the street plane = option C, circuit inlay.** Round 18's option B (holo floor tiles) is parked for another feature. This round reworks the mediums, removes every tag, makes all tactical marks true to GDD 7, and pushes the world (detail, nodes in buildings, day, Heat, vehicles).

## Files
| File | What |
|---|---|
| `raid_setup_night.png` / `raid_setup_day.png` | Setup with the new medium rules. ICE LOCK is hovering over the Vault socket (the only sticker showing the sheen sweep). Day has no fog. |
| `raid_wave_night.png` | Wave in progress: live info in terminals, the inlay and floats. Pencil only marks static states (DOWN, INCOMING). |
| `interactions.md` + `interactions_sheet.png`, `_2`, `_3` | 29 interactions/states, each with its feedback and medium, plus one example crop each. |
| `panel_mediums.png` | Node summary / raid incoming / threat intel in three mediums: **A CRT terminal (recommended)**, B case file under glass, C projected holo. |
| `node_status_key.png` | No tags: type = socket glyph; status = frame colour + pattern; integrity = inner track; forecast = dashed ring; drag states; EXPOSED (proposal). |
| `live_info_options.png` | Three live mediums: **L1 street HUD**, **L2 the inlay is the gauge**, **L3 diegetic floats**, each with feed + speed controls. |
| `link_colour.png` | Lime `cell_turf` #D4FF00 vs round 18's cyan, same frame. **Lime is recommended and is used everywhere else.** |
| `world_detail.png` | Round 18 vs round 19 buildings: ~2.6 m triangulated facets, ledges, dark glass with a few lit panes, shopfronts, awnings, blade signs, AC units, pipes, water tanks, vents, railings. |
| `building_nodes.png` | Three ways a node lives in a building: **server room**, **rooftop dish**, **shopfront**. |
| `heat_levels_v2.png`, `heat_spotlights.gif` | Heat 25/50/75: more and stronger waves and routes; circling choppers whose spotlights wobble on nodes; drones with mini spots; strobes. |
| `threat_vehicles.png` | 5 corps × fast / heavy / special, base + upgraded, at 2.2× and at true map scale. |
| `contact_sheet.jpg`, `scripts/` | |

Rebuild:
1. `python scripts/run_blender.py`: 11 Blender 5.2 headless jobs, about 12 min.
2. `blender -b --factory-startup --python scripts/vehicles.py -- <abs>/scratch/bl`
3. `python scripts/screens19.py`

Everything is seeded.

## Medium rules applied
- **Stickers:** only the title, defence cards, START DEFENSE and the final result stamp (CELL HOLDS). The `sticker_lib19.build_sticker(gloss_k=…)` sheen is at 0.22 at rest. Exactly one sticker per frame shows the full sweep (gloss_k 1.0): that is the in-game slow occasional glint.
- **Pencil** (true to the rules): removed THEY WANT THE VAULT, FLAK HERE? and HOLD IT!.
  - Setup: route A/B/C circles at the entry sockets, plus the drag-hover arrow + circle.
  - Playout: only static states (DOWN, INCOMING, LOST, BREACHED, WAVE 2).
  - **Correction:** the brief's re-routing example (Flak Array) cannot happen. In `raid_resolver.gd` only `decoy_pull` assets (DECOY 3, HONEYPOT 5) change `_target_of`. The redirect preview therefore uses a DECOY on the Relay, and a gun shows no route change.
- **Panels:** we recommend **A CRT terminal**. It uses the same navy glass, cyan edge, mono, scanline and hex-ghost language as the combat C screens, it glows into the map, and it is easy to animate (type-on, cursor).
  - B (case file) is the most characterful, but opaque paper must stay off the map.
  - C (holo) is diegetic, but has the weakest contrast over neon.
- **No node tags.** All six node types and every state read from the socket itself (`node_status_key.png`):
  - **Type:** the glyph from round 17. Relay = all-targets arrows, Firewall = firewall, Vault = safe door, Proxy = fingerprint, Safehouse = key, CORE = pink hex. Once seized, the glyph becomes the corp citation glyph.
  - **Status:** frame colour + pattern (works without colour too):
    - Holds: solid green, pins lit.
    - Disabled: dashed amber, pins dark.
    - Seized: violet hatch.
    - Lost: burnt with embers.
  - **Integrity:** the inner square track, drained clockwise from the pin-1 notch. It turns amber below 2/3 and red below 1/3, and cracks grow as it drains.
  - **Forecast:** a dashed outer ring in the projected outcome colour (dashed = predicted, as in the glyph language).
  - Threat HP: lit segments of the red ring under each vehicle.
- **Live info:** never stickers.
  - We recommend **L2 + L3 together**: the inlay carries the state and floats carry the hits, with feed + speed in terminals.
  - L1 (numbers on the street) is the accessibility option, behind a toggle.

## World
- **Facets:** the round 18 4-triangle facets became a jittered ~2.6 m grid of triangles (edges kept straight so the ink stays clean). Tone spread is 0.72–1.24 instead of 0.86–1.12.
- **Facade detail:** on the faces the camera sees.
- **Nodes in buildings:** the socket on the street stays the tactical node, and the node's machine lives in the corner building behind it. Three parallel inlay traces form a **riser** from the socket across the curb and sidewalk into the building. Riser state follows the node (dim when disabled, dead when seized).
  1. **Server room** (Vault, Firewall): racks with LED columns behind a ground-floor glass front, with a glyph sign on the side.
  2. **Rooftop dish** (Relay, Proxy): the riser climbs the facade corner to a dish on the roof; glyph sign high on the facade.
  3. **Shopfront** (Safehouse): a half-open shutter under a glyph sign, with an awning and a lit window.
- **Day:** no fog patches at this zoom (`finish19`: fog = 0 by day); tilt-shift and haze stay.

## Heat (GDD 4.4 / 7: Heat scales raid strength; thresholds add waves and routes)
- **Band 1 (25+):** 1 route; one chopper circling at the edge with its light on the street; 3 drones, no spots.
- **Band 2 (50+):** stronger threats (+integrity), 2 routes, a chopper circling the Vault, drones with mini spots, corner strobes.
- **Band 3 (75+):** 2 waves, 3 routes, choppers on Vault / Proxy / Safehouse, a gunship over CORE, 14 drones.
- **Motion:** choppers fly real circular orbits (`heat_pose(t)`). Wide edge orbits carry some in and out of frame. The spotlight is a cone from the nose to the node with an imperfect wobble (two incommensurate sines, ±3 m). Drones orbit tighter, each with an overlapping mini spot. `heat_spotlights.gif` is 24 frames of that loop.
- **PROPOSAL, needs a GDD decision:** a node in a spotlight is **EXPOSED** (e.g. +25% damage taken that step). It is shown by white hazard ticks round the socket. Without that rule the spotlights stay pure atmosphere and should not track nodes (they would then sweep the streets only, as in band 1).

## Threat vehicles
Each corp has one silhouette family:
- **Meridian:** freight boxes, hazard stripes, amber beacons.
- **Solace:** white capsules, green helix stripe, misting arms.
- **Halcyon:** police wedges, violet rim, red/blue bars.
- **Orbital:** hover pods, fins, thruster glow, star-dot lights.
- **REBEL_CELL:** scrap mirrors with odd plates, ram bars and red spray tags.

Unit types follow the threat roles in the content: fast (2 edges a step), heavy (weakest node), special (seals / freezes a link, corrupts, drops in, burns). **Upgraded (+):** +10% size, armour plates, a second light, and roof rank chevrons (1–3).

At true map scale every unit is still told apart by corp colour and outline; the + chevrons need the 2.2× zoom (or a hover).

## Godot build notes (additions to round 18)
- **Ground shader:** `netdecal19.Net` is the prototype of the ground shader (world XZ per fragment).
  - The socket anatomy is driven per node by uniforms: status enum, integrity 0..1, forecast enum, flash enum, exposed bool, glyph atlas index.
  - Per link: state enum (ok / dim / dead / frozen / hot) and the packet phase.
  - Per threat: position, HP fraction and state, for the ring.
  - It must cover sidewalks (z ≤ 0.36) for the sockets and risers.
- **Risers:** a decal on the building facade (or a thin strip mesh) along `layout.riser_paths()`, sharing the link shader.
- **Panels:** CRT terminal = a `PanelContainer` with the C-screen shader (scanline + hex ghost) and type-on text.
- **Floats:** shards = a GPUParticles2D burst with a 0/1 glyph atlas; numbers = Label tweens.
- **Choppers:** PathFollow3D on a circle per chopper, plus a SpotLight3D with a jittered aim target, plus the cone mesh. Drones are the same at a smaller radius.
- **Sticker sheen:** a shader parameter swept by a tween every ~8–14 s, on one sticker at a time.

## Weakest / open
- **The wave frame is busy around the Vault:** a chopper spot, a DOWN mark and a bailiff all sit there.
- **True-scale vehicles:** the upgraded variants are hard to tell apart at true scale.
- **Node building signs:** the glyph signs are small at map zoom. The lit server room and the dish read; the shopfront reads least.
- **For the designer:**
  - Approve or drop EXPOSED.
  - Lime vs cyan.
  - Pick the panel medium (A recommended).
  - Pick the live-info mix (L2 + L3 recommended).
- Interaction tiles 16 (ice crystal ring), 17 (decoy lure lane) and 25 (escalation chopper) read weakly at tile size; they need a tighter crop or the motion.
