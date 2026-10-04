# Round 38: hub cores, the breached hub, inner-ring segments

This round covers three gaps from the backlog (`GDD_ART_COVERAGE.md` §1.5 and §1.6): hub-core emblems, the Hub Breach state, and the inner-ring segment marks. Anchor had never been drawn before.

It is drawn in the locked D4 wheel (`round13_wheel_details/`), with the round 17 slices, glyph language and V2 tiers. Earlier rounds are not edited.

## Files
| File | What it shows |
|---|---|
| `hub_cores.png` | 8 class cores, base and Mk2, each in its D4 hub with the class's Rank 1 inner ring; 6 enemy hubs; and the BREACHED state: The Manifest at r = 220 online and breached, a 3-frame breach loop, r = 60 online and breached, and greyscale. Every emblem is shown at 64, 24 and 16 px, in colour and grey. |
| `hub_breach.gif` | The breach idle loop: 12 frames. |
| `inner_ring.png` | The 7 segment glyphs (64, 24, 16 px, grey, nearest 16 px twin); the Breaker ring on a wheel at r = 220 and r = 60, colour and grey, with a hub close-up; every Rank 1 ring; and a Rank 3 swap example (Anchor / Corrupt / Accelerator). |
| `scripts/` | `glyphs38.py` (emblems and segment glyphs), `hubkit.py` (D4 hub, ring, breach, wheel) and `make_hubs.py`. The rest is copied from round 17. |

Rebuild with `python scripts/make_hubs.py`.

## Real names (from content)
**Class cores** (`content/hub_cores/`). Each `*_mk2` is the Rank 2 "Upgraded Hub Core" (GDD 5.3). Accents are from ART_BIBLE 7.1.

| Class | Core id | Emblem | Passive (base / Mk2) |
|---|---|---|---|
| Breaker | `breaker_core` | crowbar prying a cracked plate | +1 / +2 spin; Perfect resolves twice (Mk2 also refunds RAM) |
| Wrecker | `wrecker_core` | sledgehammer with impact lines | no spin / +1 spin; Perfect again at 1.5× |
| Ghost | `ghost_core` | hood with mesh eyes | first 1 / 2 nudges ignore resistance |
| Phantom | `phantom_core` | mask with an after-image | 1 / 2 free nudges each turn |
| Rigger | `rig_core` | jack plug and cable | +1 / +2 max RAM |
| Overclocker | `overclock_core` | heat-sink chip with a bolt | +2 / +3 max RAM |
| Botnet | `swarm_core` | three linked drones | 3 / 4 drones that persist |
| Hivemind | `hive_core` | hex cell holding 4 nodes | 4 / 5 drones for the fight |

**Mk2.** It uses the same emblem, plus a second notched rim and an "MK2" tab on the bottom rim.

**Enemy hubs** (the `hub` sub-resource in `content/enemies/`):

| Hub | Enemy | Corporation | Emblem | Passive |
|---|---|---|---|---|
| Compliance Lock | Compliance Officer (elite) | Solace | rubber stamp | spin resistance 3 |
| Priority Routing | The Manifest | Meridian | express arrow overtaking two lanes | gains 4 shield each turn |
| Emergency Powers | The Civic Core | Halcyon | siren dome | heals 4 and blocks 4 each turn |
| Station Keeping | The Commons Array | Orbital | satellite | repairs 3 and shields 3 each turn |
| Auto-Renew | Renewal Engine | Solace | renew loop around a plus | heals 10 each turn |
| Root Access | DISPATCH | REBEL_CELL | terminal with a "#_" prompt | repairs 4 and shields 4 each turn |

The boss passives switch off while the hub is breached (GDD 2.8 and 8.4).

**Inner-ring segments** (`content/rings/segments/`):

| Segment | Glyph | Effect |
|---|---|---|
| x2 | "×2" | outer slice output doubled |
| Pierce | arrow through a brick slab | ignores block and shield |
| Corrupt | data block glitched into offset slabs | target's resolved slice becomes CORRUPTED |
| Anchor | anchor (**first drawing**) | on Perfect, your wheel skips its next respin |
| Accelerator | gear with speed lines | nudge cards next turn trigger twice |
| Echo | source block with two echo arcs | outer slice again at half output |
| blank | a dash | no modifier |

**Rank 1 rings** (`content/rings/`). Each alternate class uses its base class's ring.

| Ring | Segments |
|---|---|
| Breaker | ×2 / Pierce / – |
| Ghost | Pierce / ×2 / Echo |
| Rigger | Accelerator / ×2 / Echo |
| Botnet | Echo / Corrupt / ×2 |

## Rules
**Hub (D4).**
- A dark CRT disc (class or corp tint, scanlines, vignette) in a machined rim with an accent hairline.
- The emblem sits centred with an accent glow, with the core name and a short passive under it.
- Player hubs sit inside the inner ring.
- Enemy hubs have no ring: they fill the centre and carry a slow corp-colour chevron sweep that marks them hostile.
- At r = 60 the hub shows the emblem only.

**BREACHED** (Hub Breach 1 turn, Short Circuit 2 turns, Shatter). It covers enemy hubs only.
- The glass cracks from an impact point: white-hot cracks with a warm glow.
- The screen dims, with static and 2 tear bands that re-roll 12 times a loop.
- The emblem drops to 75 % with an RGB split.
- Sparks spit from the crack ends.
- The passive text is struck out in red.
- A red **BREACHED** plate and turn count sit at the top of the hub.
- At r = 60, a thick HARM ring around the hub carries the state, and it still reads in greyscale.

**Inner ring.**
- A band between the hub and the slices: master radius 84 to 124, against slices at 130 to 360.
- Three 120° segments, each with 10 tick marks and a 2° gap.
- Each segment glyph stands upright at the segment's centre.
- The segment under the pointer is lit: accent fill and bright edge. The others are dimmed to 72 %.
- The pointer has a small notch over the ring.
- At r = 60, the ring reads as lit and unlit bands; the glyphs are decorative there.

## 16 px check
Segment glyphs, nearest twin in the whole final set:

| Segment | Nearest twin | Score |
|---|---|---|
| ×2 | ZERO-DAY burst | 0.46 |
| Pierce | Priority Routing | 0.57 |
| Corrupt | Ghost Core | 0.66 |
| Anchor | POWER | 0.51 |
| Accelerator | FREE NUDGE | 0.63 |
| Echo | FLIP | 0.48 |
| blank | DOSE | 0.26 |

Corrupt and Accelerator are the closest. They are acceptable, because segments are only ever seen inside the ring.

## Godot notes
- **Emblems** join the round 17 glyph atlas as `hub_<core_id>` and `seg_<id>` entries. Export the PNGs the same way as `round17_slice_system/glyphs`.
- **Hub.** A `Control` with a CRT `ShaderMaterial`:
  - uniforms `accent`, `breached` (bool), `breach_t` (TIME) and `breach_seed`;
  - the crack lines as a baked texture per seed, revealed by `breached`;
  - an emblem `TextureRect` and two `Label`s;
  - an `MK2` tab `Panel` shown when the core id ends in `_mk2`.
- **Inner ring.** A `Node2D` that rotates independently of the outer ring (GDD 2.1), with three arc `Polygon2D`s, tick `Line2D`s and 3 upright glyph `Sprite2D`s that counter-rotate.
- **Data flow.** The lit segment comes from the forecast; views only read state.

## Weakest part
- **The segment glyphs are small at r = 220** (about 16 px).
- **Corrupt (0.66) is close to the Ghost Core emblem at 16 px.**
- **The enemy-hub chevron sweep reads like clock ticks.**
