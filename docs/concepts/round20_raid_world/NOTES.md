# Round 20: raid world (rooftops, stationed operatives, corp livery + icons, heat live, campaign lost)

Builds on round 19 (street grid option C, lime `#D4FF00` Cell links, risers into node buildings). The raid UI half (panels, node health, interaction gifs) is in `round20_raid_ui/`.

## Files
| File | What |
|---|---|
| `building_nodes_v2.png` | Three rooftop indications (A crown inlay, B uplink pad, C mast + lit hatch) on Firewall Relay, Vault Terminal and Safehouse. The riser now also climbs the -x facade to the roof. **B is recommended.** |
| `operators.png` | Station flow: 1 empty slot, 2 drag-hover valid, 3 stationed, 4 adjacency share, 5 recall. Three ways to show a stationed operative: **R1 rooftop figure (recommended)**, R2 emblem decal, R3 class beacon. Class chips show the emblems, colours and station bonuses. |
| `operator_drop.gif` | 46 frames, 1.5 MB. Empty slot, drag a BREAKER card from the roster, the pad answers, drop, figure, bonus shared down the link to CORE, recall. |
| `threat_vehicles_v2.png` | 5 corps × fast / heavy / special, base and +, with the v2 livery. Each unit has its map icon beside it, plus the icon grammar and a map-scale models vs icons comparison. |
| `vehicle_toggle.png` | One mixed-corp wave: close-up with models, zoomed out with icons (close-up area outlined), zoomed out without the swap, and the VIEW toggle terminal. |
| `heat_levels_live.gif` | Heat 25 / 50 / 75 side by side, 20-frame loop, 2.9 MB. Choppers circle, beams wobble, drones carry mini spots, Halcyon convoys drive their routes, and Heat 75 shows WAVE 2 INCOMING. The heat meter is padlocked. |
| `campaign_lost.png` | **A ransomware lock (recommended)** and B carrier lost, with their key moments, plus A in the Meridian / Solace / Orbital / DISPATCH house styles. |
| `campaign_lost.gif` | Option A from hit to wipe, then option B. 640×360, 45 frames, 3.4 MB. |
| `campaign_summary.png` | The CELL DOWN summary page. |
| `contact_sheet.jpg`, `scripts/` | |

## Choices
**1. Rooftops: B, uplink pad.**
- The pad is a raised plate whose face is the street socket's twin: frame, pins, pin-1 notch and node glyph. A lime beacon mast stands at its corner, and a faint lime parapet edge runs along the two faces the camera sees.
- It says "this building is that node" with the same symbol, at any zoom, and stays calm.
- On a Safehouse the pad doubles as the station slot.
- A (crown inlay) is the loudest. With 6+ nodes it turns the skyline into a circuit board.
- C (mast + hatch) has the best silhouette but reads as "antenna". Its light shaft also fights the Heat spotlights.
- All three keep the round 19 riser into the machine and add a 3-trace climb up the -x facade onto the roof, with packets running. The climb dims or dies with the node like the street riser.

**2. Stationed operatives, true to GDD 3.2 / 5.4.**
- Only a Safehouse has a station slot, and the slot is its rooftop pad, so the drop target is the whole pad.
- States:
  - **Empty:** dashed ring and "+". Dashed means available.
  - **Hover, valid:** the frame and ring go white and the slot floods with the class colour.
  - **Stationed:** a solid class ring with ticks. The street socket gets class-colour corner brackets and an emblem chip, which is the boost indicator.
  - **Share:** class-colour chevrons run down the middle trace of the link to the adjacent node. That node gets dashed brackets and a hollow chip.
  - **Recall:** a class-colour beam goes up, the ring unwinds and the card flies back to the roster.
- Recommendation is **R1, a figure**: a low-poly operative with a class-colour visor, coat seam and foot ring. It is the only option that reads as a person.
- The roster card is a vinyl sticker (static UI object). Live feedback is decal and light, never sticker.
- Class colours and emblems come from round 6. GDD 5.2 only defines station bonuses for the 4 base classes, so the 4 alternative classes are marked "tbd".

**3. Corp colour.**
- Every unit carries its corp colour three ways:
  - an under-glow pool on the street, which also lights the asphalt through the spill pass;
  - a roof livery plate;
  - twin corp beacons.
- Palette:
  - Meridian: orange + amber.
  - Solace: lime-green `(0.42, 1, 0.16)`, deliberately greener than the Cell lime.
  - Halcyon: violet + amber light bars. The old red/blue light bars are gone.
  - Orbital: ice-white hulls + cyan.
  - REBEL_CELL: red.

**Icons:** one rule per channel, so each channel reads on its own and in greyscale:
- **Shape = corp:** crate, capsule, shield, finned diamond, scrap octagon.
- **Fill = corp colour.**
- **Glyph = role:** fast `>>`, heavy weight; specials have their own verb (seal, dose, freeze, drop, burn).
- **Crown = upgraded:** two white chevrons and a double rim.
- **Notch = heading.**
- **Ring = live HP.**

**4. Heat.**
- The heat level at raid start sets the raid and is padlocked; nothing escalates mid-raid.
- Band contents follow round 19 / GDD 4.3:
  - 25: 1 route, 3 threats, 1 sweeping chopper, 3 drones.
  - 50: 2 routes, + threats, a chopper on the Vault, 7 drones with spots, strobes.
  - 75: 3 routes, 2 waves, 3 choppers + gunship, 14 drones.
- EXPOSED ticks on spot-lit nodes are still the round 19 proposal.

**5. Campaign lost: A, ransomware lock.**
- It tells you who beat you, in their house style and with their verb: PROCESSED / RECLAIMED / TREATED / DE-ORBITED / OVERWRITTEN.
- Every node is padlocked and a countdown runs to the wipe, which cuts to the summary.
- The Cell's stickers are vinyl on the glass: they never glitch or tint, they curl and drop off. That is the last mixed-media beat.
- B (NO CARRIER) is purer but anonymous. Its half-peeled stickers on a dead screen are a nice beat, which A could borrow for its final frame.
- **Summary page:**
  - Operative cards with fates in grease pencil (red X for KIA, yellow MVP).
  - The network at the end on the burnt map, plus a tally.
  - Heat over the campaign as a CRT graph with the raids marked.
  - "TAKEN DOWN BY" with the corp seal and a PROCESSED sticker.
  - A run log.
  - Unlocks as stickers (class card, ICE record, home-server variant) and records.
  - NEW CAMPAIGN / MAIN MENU sticker buttons.

## Godot build notes
- **Roof:**
  - A node building gets a `roof_variant` and a pad mesh (B).
  - The pad face is a decal / quad that uses the street socket shader, with the same uniforms: status, glyph index and `slot_state`.
  - `slot_state` is an enum: empty, hover, stationed, recall, plus `class_colour` and `emblem_index`.
  - The facade climb is the riser shader on a strip mesh along `layout.climb_paths()`.
- **Station drag:**
  - Hit-test the pad's screen quad. Only a Safehouse pad is a valid target; any other node shows the round 19 invalid flash.
  - On drop, spawn the figure (a low-poly rig with a two-pose idle) and set the socket `boost` uniforms. The adjacency share is a `share_dir` + phase uniform on the link shader.
- **Vehicles:**
  - Livery = three emissive meshes per unit (glow pool, roof plate, beacons), using the corp palette from a resource.
  - Icons are a 30-entry atlas (shape × role × upgraded). The heading notch and HP ring are drawn in the icon shader.
  - Swap below 0.6× zoom, with 0.55 / 0.65 hysteresis and a 0.15 s crossfade. Hold [V] to show the models.
  - Icons are billboards at a fixed 26 px (1080p).
- **Heat:** the round 19 rigs (PathFollow3D orbits, SpotLight3D with jittered aim, drones). The band is read once at raid start.
- **Loss:**
  - A full-screen CanvasLayer: a corp theme resource (palette, motif texture, font, verb), a wipe shader (scan edge), padlock sprites on the node screen positions, and a Label for the countdown.
  - The stickers are separate TextureRects with a curl shader, then a fall tween.
  - B is a CRT-off shader (squash to a line, then a dot) and a terminal Label with type-on.

## Rebuild
1. `python scripts/emblems20.py` (writes `scratch/emblems`).
2. `python scripts/run_blender20.py` (Blender 5.2 headless; roofs, wave and 3 heat loops; about 5 min).
3. `blender -b --factory-startup --python scripts/vehicles20.py -- <abs>/scratch/bl`
4. `python scripts/screens20.py` (all sheets and gifs; about 15 min).

Everything is seeded. Round 19 scripts were copied, not edited:
- `district.py` became `district20.py`, which adds `roof=`, `op=`, `figtoggle`, `veh=mixed` and `cams=`.
- `vehicles.py` became `veh_models.py` + `vehicles20.py`.

## Weak / open
- **R1 figure:** it reads as blocky and dark on the dark pad. In game it needs a class-colour rim light.
- **Heat-loop icons:** at 17 px in the heat loop they are small.
- **Alt-class station bonuses** (Wrecker / Phantom / Overclocker / Hivemind): not in the GDD.
- **Stationing beyond the Safehouse:** the GDD has one slot per Safehouse. If the designer wants stationing on any node, the pad already exists on every node building under B.
- **Ransomware panel:** it covers the padlocked sockets. The locks read during the wipe, before the notice lands.
