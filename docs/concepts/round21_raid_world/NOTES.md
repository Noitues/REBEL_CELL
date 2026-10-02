# Round 21: raid world (class beacons, station bonus proposals, icons v3, corporate dossier)

Locked from round 20:
- building nodes **B uplink pad**;
- vehicle models + corp colours;
- campaign lost **A ransomware lock**;
- the **EXPOSED** spotlight effect (on the integration to-do).

The raid UI half is in `round21_raid_ui/`.

## Files
| File | What |
|---|---|
| `operators_r3.png` | R3 class beacon, all 8 classes. Each tile shows the idle frame, the class's station bonus (from the mapping below) and a line describing its idle loop. |
| `operator_classes.gif` | The 8 idle loops side by side, 16 frames. |
| `station_bonuses.png` | **PROPOSALS (GDD gap):** five bonus effects on the raid map, base vs levelled, plus the class → bonus mapping. |
| `bonus_damage.gif`, `bonus_slow.gif`, `bonus_sniper.gif`, `bonus_drones.gif`, `bonus_repair.gif` | One loop each, base (left) vs levelled up (right). Each is 2 MB or less. |
| `vehicle_icons_v3.png` | Icon shape = vehicle type, colour = corporation. Matrix of the 5 types × 5 corps, upgraded + HP, the 30 units at map scale, and the hover heading ring. |
| `vehicle_toggle_v2.png` | Close-up showing hover (dashed ring) and selected (solid ring), each with a heading arrow and a tag; the zoomed-out view with v3 icons; the VIEW terminal. |
| `campaign_dossier.png` | The campaign summary as the winning corporation's audit file. |
| `campaign_dossier_open.gif` | Short loop: the closed folder (PROCESSED) opens to the summary. |
| `contact_sheet.jpg`, `scripts/` | |

## 1. Class beacons (R3, locked)
- **The cone:** the beam opens upward from the Safehouse pad projector and ends at an elliptical cap ring under the emblem.
- **No light behind the icon:** the beam layer is cut by the emblem's dilated silhouette, and a soft dark plate sits behind the emblem. Inside the cone: rising bands and a bright rim.
- **The emblem:** a holo with scanlines, tinted with the class colour.
- **Safehouse mast:** removed under R3 so the beacon owns the roof. The round 20 lime mast stays on every other node.
- **Idles, one per class:**
  - Breaker: crowbar swing with a spark burst.
  - Wrecker: hammer slam with a shock ring on the roof.
  - Ghost: bobbing fade with glitch slices.
  - Phantom: a cyan afterimage splits off and snaps back.
  - Rigger: cable rings climb the cone.
  - Overclocker: the cone flutters fast and embers rise.
  - Botnet: drone dots orbit the emblem.
  - Hivemind: hex cells ripple outward.
- **Class colours and emblems:** from round 6. Phantom and Botnet are close (violet); the idles and emblems separate them.

## 2. Station bonuses: PROPOSALS, they need GDD decisions
| Class | Bonus | Base | Levelled up | Source |
|---|---|---|---|---|
| Breaker | **A damage aura** | Node assets +50% damage: pink ground aura, rising chevrons, boosted damage numbers | The aura runs down the links: adjacent nodes get it too | GDD §5.2 |
| Ghost | **B slow field** | 30 m field; units inside lose 1 step: inward ripples, afterimages, clock ticks | Periodically freezes the units inside for 1 step: ice flash, FROZEN glyph | GDD "delayed 1 step", widened to a radius |
| Rigger | **E field repair** | Integrity track refills after each wave: green spark spiral, +INT | Adjacent nodes repaired too | GDD §5.2 |
| Botnet | free asset per raid | (GDD, not drawn) | | GDD §5.2 |
| Wrecker | **C sniper** | Roof sniper locks the toughest unit in range: laser sight + charge ring, one heavy shot every 3 steps | The player drags the reticle and clicks to fire | new |
| Hivemind | **D drone operator** | Drones launch from the pad, orbit incoming units and chip them | Drones also hunt enemy drones and choppers. The chopper goes down, and its spotlight and EXPOSED go with it (the counter to the locked EXPOSED effect) | new |
| Phantom | F echo decoy (not drawn) | A phantom copy of the node pulls threats for 1 step (DECOY rule) | 2 copies | new |
| Overclocker | G overclock (not drawn) | Node assets fire twice, +1 Heat per raid | No Heat cost | new |

**Mapping logic:**
- The four base classes keep their GDD §5.2 bonuses.
- The alternates get the new ones, each a twist on its base class: Wrecker/Breaker = damage, Hivemind/Botnet = drones, Phantom/Ghost = deception, Overclocker/Rigger = tempo.
- "Levelled up" can hang off operative rank: GDD §5.3 already says "station bonuses scale with rank".
- Numbers (radius 30 m, sniper damage 14/18, cooldown 3 steps) are placeholders for config.

**The gifs:**
- Every gif is the same Halcyon wave closing on the Safehouse.
- The drones gif is at Heat 75 so a chopper spotlights the Safehouse.
- The other four gifs have no heat rigs so the effect reads.

## 3. Vehicles
**Heading:**
- Removed from the icon.
- Shown only on hover or selection, as an arrow riding a ring round the unit on the street: dashed ring = hover, solid ring = selected.
- The arrow is yellow, the same plan colour as the pencil.
- A CRT tag gives name, HP and target.

**Icons v3:** the shape is the vehicle type, shared by every corporation:
- FAST: chevron badge, glyph `>>`.
- HEAVY: chamfered block, glyph weight.
- SPECIAL: hexagon with its verb glyph (seal / dose / freeze / burn).
- LANDER: a pod pointing down, glyph drop.
- FLYING: winged diamond, glyph rotor. For choppers and drones once they are targetable, e.g. by the levelled drone operator.

Colour is the corporation only. Upgraded = two chevrons on top and a double rim; HP = the lit ring. Orbital's Lander is the only LANDER and has no SPECIAL.

## 4. Campaign summary = the corporate dossier
- **Framing:** an open manila folder on a lamp-lit desk.
- **Right panel:**
  - The typed AUDIT REPORT on Halcyon letterhead, with seal: subject, duration, status, activity, network at closure, and a typed heat graph with the raids in red.
  - Signed "A. Vance" in ballpoint.
  - A red CASE CLOSED stamp.
  - An annex underneath with the profile unlocks, as residual risk.
- **Left panel:**
  - Three taped polaroids: home server 0/50; the Safehouse beacon, captioned "whose?"; the network at the end.
  - A typed PERSONNEL sheet with emblem prints. The dead are struck through as DECEASED; survivors are AT LARGE.
- **Post-its:** the auditor's blue ballpoint, not the Cell's grease pencil:
  - MOST TROUBLESOME → BREAKER (replaces MVP);
  - "2 still at large";
  - "heat spiked after run 8, why weren't we told?";
  - "they'll be back, flag the PHANTOM".
- **Only our UI stays vinyl:** NEW CAMPAIGN / MAIN MENU are stickers on the desk.
- **The other corps:** the corp's letterhead, seal and stamp verb come from the round 20 ransomware styles, so each corporation gets its own dossier.

## GIF quantisation (saturation)
- A median-cut palette from a frame mosaic averages neon toward grey.
- Instead, `save_gif` uses 196 median-cut colours plus the key neon colours. These are the class colours, corp colours, Cell lime, harm red, amber and ice, each at 4 intensities and one pastel tint. No dither.

## Godot build notes
- **Beacon:**
  - A cone mesh (open top, additive, bands scroll in the shader) plus a cap ring quad.
  - The emblem is a Sprite3D billboard with the holo shader.
  - The beam is masked by the emblem's SDF, so nothing glows behind it.
  - The idle per class is an AnimationPlayer library keyed by class id. Parameters: bob, rotation, flutter, plus a particle emitter (sparks, embers, hex cells, drone dots).
- **Bonuses:**
  - Each is a node-attached effect scene with base/levelled variants: aura decal + link share, ground ring decal + freeze pulse, sniper (laser line + reticle; the levelled version takes mouse input in the raid view), drone swarm (PathFollow3D orbits + tracers), repair particles.
  - The visual reads the resolver's step events, so preview = result.
- **Heading ring:** a ground decal ring plus an arrow on hover/selection only. The tag is a CRT `PanelContainer`.
- **Icons:** an atlas of 5 shapes × verb glyphs, tinted per corp in the shader, plus an upgraded overlay and the HP ring.
- **Dossier:** a 2D scene. The paper textures are static art. Stats are typed into Labels (monospace, type-on), the polaroids are SubViewport captures of the end-state map, and the post-it texts are picked by rules (most kills / deaths / heat spikes).

## Rebuild
1. `python scripts/emblems20.py`
2. `python scripts/run_blender21.py` (4 jobs, about 3 min)
3. `blender -b --factory-startup --python scripts/vehicles20.py -- <abs>/scratch/bl`
4. `python scripts/screens21.py r3 r3gif bonuses bonusgifs icons toggle dossier dossiergif contact` (bonusgifs takes about 30 min)

Seeded throughout. Round 20 scripts were copied; the round 21 code is `screens21.py`, `icons21.py`, `dossier21.py` and `run_blender21.py`.

## Weak / open
- **Phantom vs Botnet:** the two violets are close at small size.
- **Slow field (base):** the afterimages are subtle at map zoom. The ripples carry the effect.
- **Sniper levelled:** player aim needs a GDD rule for when aim is allowed (setup only? live during the playout?).
- **Dossier, closed state:** the post-it edges peek past the cover in the first gif frames.
