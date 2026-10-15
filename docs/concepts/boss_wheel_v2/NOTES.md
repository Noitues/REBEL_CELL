# Boss Wheel v2: a design system for boss wheels

Concept round in the art-pass worktree. Nothing here is game content, and nothing is committed.

Test cases:
- **Aurelian Concord**: the Roman corp. Boss THE ROSTRUM, hub THE GRAND STAND.
- **Tethys Deep**: the Atlantis corp. Boss THE BLACK SMOKER, hub THE VENT CAP.

The two finals follow the designer's direct briefs:
- Roman: "the wheel IS the arena pit, seen from above".
- Atlantis: "the octopus IS the wheel".

Both are built on one template. Three earlier directions per corp (A/B/C) are kept as explorations.

## Files

| File | What it is |
|---|---|
| `system.png` | The template: the real layers of both finals in an exploded stack, plus the slot list. |
| `roman_wheel_final.png`, `atlantis_wheel_final.png` | Top: a full combat frame using the round 41 v4 composition, next to the player wheel. Bottom: combat size, a 2x close-up, and the needle at rest, on a hit and on a whiff. |
| `roman_wheel_A/B/C.png`, `atlantis_wheel_A/B/C.png` | The exploration directions. Each shows combat size, a 2x close-up and the three needle states. |
| `roman_phases.png`, `atlantis_phases.png` | Phases 1, 2 and 3, plus damage cracks at 10 % HP. |
| `roman_anim.mp4` / `.gif`, `atlantis_anim.mp4` / `.gif` | About 6.5 s at 24 fps: idle, spin, land, the figures act, the needle reacts, the phase 2 change. The mp4 is 1920x1080, encoded by Blender's FFmpeg through the VSE. The gif is 960x540 at 12 fps (every second frame), to keep its size down. |
| `roman_boss_emblem.png`, `atlantis_boss_emblem.png` | Each emblem at 512, 256, 128, 64, 32 and 16 px, on paper and in greyscale, matched to its final. |
| `readability_test.png` | Each final at combat size three ways: full, values only, and 2 px blur in greyscale. Also the reduce-effects end states. |
| `compare_v1_v2.jpg` | The mainline build's boss wheel (from W2R2_GROUP), the round 41 concept (THE MANIFEST), and both v2 finals, all at one size. |
| `scripts/` | Covered under "How to run" below. |

## Picks

| Corp | Primary (designer brief) | Alternate kept | Why |
|---|---|---|---|
| Aurelian | **D, THE ARENA PIT** | **B, MOSAIC** | Designer: keep pushing the tiled fresco. It now has a gilded border on every panel and fresco cracks. |
| Tethys | **D, THE OCTOPUS IS THE WHEEL** | **B, KRAKEN** (portholes) | The approved octopus. B is its strongest variant: values read best of all six and the porthole blank is unmistakable. C BIOLUME is the non-octopus alternate. |

**Why D wins, Aurelian.**
- It is the only option where the boss *is* the wheel: the HQ (the turning colosseum), the house rule (VERDICT, the thumb) and the needle (the box) tell one story.
- Its two rings map to real rules: outer slices are the chariots, the inner ring is the fighters.
- Type colour stays clean. Each chariot's plume and cloth are its slice colour (team colour = type).

**Why D wins, Tethys.**
- It changes the wheel's silhouette, so it reads at r = 60.
- The arms *are* the slice borders, so the art and the structure are the same object.
- The beak is a needle no other boss has.

## 1. The template (one system, named slots)

All of it is in `wheel_v2.py` (`compose`). A boss is a Direction object that fills the slots. Every slot is optional; the template supplies defaults.

| Slot (bottom to top) | Turns with the wheel? | Contents |
|---|---|---|
| `back_plate` | no (parallax depth 1.0) | The stage behind everything. It is seen through the blank window and around the rim. |
| `art_ring_under` | yes (lags 3 % in a spin) | Ring art behind the slices: the sand floor, or the octopus web. |
| `slice_scenes[]` | yes | One scene per slice, masked to its wedge. |
| `blank_window` | yes | The NULL slice (section 3). |
| `separators` | yes | Slice borders. The default is a dark spoke; Aurelian uses chalk lines; Tethys uses none, because its arms are the borders. |
| `rim_band` | yes | Colour = type: an 18-unit band per slice at the rim, r 334-352. |
| `plaque_zone` | yes | The art under each plaque, desaturated by 50 % and darkened by 40 % (feathered ellipse 160 x 84). |
| `bezel` + `threat_ring` + `hp_arc` | no | The locked D4 lens & rail frame in the corp material: 30 ticks, telemetry, readout rail, threat ring, HP arc and phase pips. |
| `inner_ring` (optional) | yes, independently | A boss inner ring under the round 45 rules (Aurelian). |
| `art_ring_over` | no, or self-rotating | Art over the rim: arches, gates, tentacles. It stays out of r < 318 except on the borders. |
| `plaques` | the position turns; the plaque stays upright | Value and glyph, **always on top of the art**. |
| `hub_portrait` | no | The boss portrait or emblem, animated. |
| `needle_rig` | no | The pointer actor. It carries `pointer_angle`, which is 0 (top) by default and 180 for the octopus beak. It also carries the precision latch and the value window. |
| `fx_idle`, `fx_land`, `fx_phase` | — | Motion layers. Each has a static reduce-effects end state (section 6). |

Per-boss options on the Direction:
- `pointer_angle`: the needle position. The rail and the telemetry gap follow it.
- `hp_span`: where the HP arc and phase pips sit. The default is the bottom; the octopus puts them at the top.
- `separators`, `inner_ring`, `slice_glass`, `blank_window`: overrides of the defaults.

**Radii** (master units: R_OUT = 352, combat r = 236 px, so S = 0.656):

| Element | Radius |
|---|---|
| Hub | 0-112, rim 128 |
| Slices | 130-352 |
| Rim band | 334-352 |
| Plaque centre | **290** (fixed for every boss) |
| Bezel | 352-398 |
| Threat ring | 402-426 |
| HP arc | 438-458 |
| Over-art | 318-510 |
| Rig and banner | up to 700 |

Every final keeps its extras within 1.45 x R_OUT, under the round 41 budget of 1.6.

## 2. Readability rules (non-negotiable)

- **Value plaque.**
  - Dark backing: #0A0810 at 92 %, with a 6-unit dark halo.
  - A type-colour cap bar on the outer edge.
  - The locked white glyph (round 17 atlas, 0.075 outline) and the value in Bahnschrift Bold Condensed.
  - Sizes: 60 master for the numeral (39 px at combat size, cap height about 27 px) and 46 master for the glyph (30 px).
  - Upright at every angle, at r = 290 on every boss.
  - Plaques sit above every art layer except the hub and needle. Those are kept out of the plaque radius.
- **Art under values** is desaturated and darkened in a feathered zone.
- **Colour = type** survives as the rim band. The octopus arms and the arena chalk never carry a type colour; the chariot plume does, as reinforcement only.
- **Slice figures are lit in the slice's type colour** (backlight, rim light, plume), so the type reads even when blurred.
- **The read test** (`readability_test.png`):
  - With the art removed, the plaques alone carry value and type.
  - Under 2 px blur in greyscale, glyph and number still separate.
  - The precision tags (the rail `SHIM 14 // PERFECT`, the PERFECT and GOOD word stickers, the latch) are unchanged from round 39.
- **The forecast slice** glows subtly: a type-colour edge pulsing at 1.6 s plus a 10 % wash.
  - It is compatible with the round 45 ghost wedge.
  - On the Aurelian final the inner ring's ghost wedge sits on the outer slice under the box, with the active modifier's mark at 24 %.

## 3. The blank (NULL) slice: rules check and the visual rule

**GDD 2.4 and 2.6:**
- NULL is a real outcome: "nothing (unless modified)". It is the only "miss".
- Rules refer to it by name:
  - Fault Tolerance: NULL deals 3 damage.
  - Zero Day: a Perfect on NULL resolves as a 3x OVERFLOW.
  - Cold Exit: finish without NULL resolving.
  - Stolen Intent.
  - CORRUPTED, and DOSE's "non-NULL" target rule.

So the blank slice:
- must stay a full slice, with its 5 ticks and precision tiers;
- must stay targetable for previews and ghosts;
- must read unmistakably as "nothing here".

**Visual rule:**
- Dark glass onto the art below: back_plate and art_ring_under at 35 % saturation and 42 % value.
- An inner shadow, a faint reflection streak, a thin empty grey outline inset 12 units, and a grey rim band.
- The plaque still shows the locked `1/0` glyph in grey, so the outcome stays explicit.

Per boss:
- Aurelian: an empty lane on the track, with one lost wheel.
- Tethys: the bare web between two arms.
- Kraken (B): an empty porthole.

**Open question for the designer:** when a Daemon modifies NULL (Fault Tolerance, Zero Day), the plaque shows the modified value. Should the window also gain an art hint?
- Proposed: the round 45 ghost-wedge pattern, using the Daemon family colour.

## 4. The needle rig

| Boss | Rig | Rest | Hit (a damaging landing) | Whiff / blocked / blank |
|---|---|---|---|---|
| Aurelian (A, D) | The emperor's box (pulvinar) on the wall at the top. The locked cream blade hangs from its ledge with the value window. His arm is the **VERDICT emoji hand**, the same drawing as the boss emblem, rooted at the box's right column. | Thumb sideways (deliberating) | Thumb down (0.3 s ease-out roll about the sleeve root) | Thumb up |
| Tethys (D) | **No external needle.** The head is fixed; the **beak points down at 6 o'clock**. Precision is read at the beak tip on the hub lip, where 30 notches turn with the wheel. The value window sits on the head above the beak. | Beak shut, eyes half-lidded | Beak snaps (open and shut in 0.3 s), eyes flare, the two tucked arms clench | Beak clacks empty, the two border arms recoil |
| Tethys (A) | An anglerfish lure on a stalk from the banner | Sway | Lure flares white-hot | Lure dims and droops |
| Tethys (B) | An arm tip coiled round the blade shank | Lazy coil | Squeezes, suckers flush red | Lets go and recoils upward |
| Tethys (C) | A diver's helmet on its air tether | Swing | Port flares red, bubbles burst | Port goes dark |
| Aurelian (B) | A gilt aquila standard; the vexillum carries the name | Wings level | Wings rise | Wings fold |

**The bottom needle, approved by the designer.**
- GDD 2.1 says the pointer is "a fixed marker (top of the wheel *by default*)".
- GDD 2.3 resolves `(rotation + pointer_tick) mod 30`.
- So `pointer_tick = 15` is legal for one boss, and it is now a `needle_rig` option (`pointer_angle`).

What follows from it:
- The readout rail moves to the bottom of the bezel and reads upright.
- The HP arc and phase pips move to the top (`hp_span`).
- Card-preview ghost chevrons start from the beak.
- Multi-pointer phases (Multiply) are an open question. Proposed: an extra pointer is an arm tip lifted over the rim at the new tick, holding a small hooked blade with the locked value window.

**Bottom needle vs the HUD.** In the round 41 v4 layout the boss HP number, its result chips and the breakdown tooltip sit just below the boss wheel, which is where the beak reads. The tooltip must open upward-left (or to the side) for this boss; the finals' combat frames are shown without the tooltip for that reason.

**Eight arms on a six-slice wheel.** Six arms are the borders. The two spares tuck round the head and cup the beak; they are the needle's "hands", and they clench on a hit. An eight-slice boss would use all eight arms as borders; five or fewer tuck the same way.

## 5. Slice figures and how they map to the rules

**Aurelian D: the arena pit.**

*Outer ring, the chariot track (r 246-352).*
- One tiny top-down quadriga per slice. Its driver's plume, cloak and bridles are the slice's type colour. The chariot's slice value is the plaque beside it.
- Chariots hold station in their slice and gallop in place while the track streams under them (ruts and dust), so a chariot always means its slice.
- On landing the chariot surges forward (an overtake) with a dust burst.
- The NULL slice is an empty lane with a lost wheel.

*Inner ring, the fighting floor (r 130-242).*
- A boss inner ring of 3 segments of 10 ticks, under the round 45 rules: the active segment under the box is raised and lit with a notch tick, the others dim to 72 %, and words appear on hover only.
- Segments (proposed):
  - LION (with a bestiarius) = **x2 DOUBLE**;
  - RETIARIUS (vs a secutor; the net) = **ANCHOR**;
  - MURMILLO (vs a thraex) = **PIERCE**.
- On landing, the active pair plays a finishing move (the lion pounces, the net is thrown).
- **Rules flag:** a boss inner ring is new. GDD 6.4 inner rings are a player system, and ART_BIBLE 3.3 says enemy hubs have none.
  - Open question: who can nudge the boss's inner ring, and does it respin each turn?
  - The default here: the player's nudges can target it like any ring, and it respins with the wheel.

*Hub.* The captives, the "innocent gladiators", huddle round a stake in a palisade pen: the stakes of the fight.

*Rim.* The arena wall is the D4 bezel in travertine. Four gates hold portcullises and braziers. The stands and crowd sit beyond the wall.

**Tethys D: the octopus.**
- Six arms radiate from the head and turn with the slice ring.
- Each slice is a water scene through the web: harpoon diver, anglerfish, pressure dome, ink-jetting octopus, stinging jellyfish.
- The membrane darkens each slice's edges.

**Tethys loadout change (flag for the corps agent):**
- The special slice is now **STING** (INFECT 3, the jellyfish). TIDE stays a HUD house rule, not a slice.
- **DETOUR** (an ink cloud, glyph only) replaces DEFRAG 14, to match the designer's harpoon / dome / sting / ink / diver list.

**Exploration directions A/B/C** use the same figure library in three render modes (`render2d.py`):
- backlit silhouettes lit in the type colour;
- mosaic tesserae;
- carved relief under a type-colour neon tube;
- emissive bioluminescent outline (the octopus C alternate).

**ART_BIBLE note.**
- 1.2 lists "illustrated identity icons on slices (rounds 8-9)" as rejected, and 3.4 makes slices CRT screens.
- The designer's v2 brief asks for illustrated scenes on boss wheels. Here they are limited to *boss* wheels, behind a locked read block, and the glyph is kept on every plaque.
- Log this in DECISIONS.md as a deliberate change (not done here: this round writes only in its own folder).

## 6. Animation list (timings, triggers, reduce-effects end state)

All motion values belong in `content/config/ui_motion.tres` with their VfxTier.

| Beat | Trigger | Timing | Motion | Reduce effects (end state) |
|---|---|---|---|---|
| Idle life | always | loops of 3 s or more (T0) | Chariots gallop and the track streams; fighters spar; captives tremble; crowd ripple; torches and braziers flicker; arms ripple (a sine travelling out at 0.55 Hz); the head breathes; eyes look; the forecast slice pulses (1.6 s) | Static frame; forecast edge steady at 70 % |
| Spin | respin or card spin | ease-out, 1.5 s for 2 turns | Rotational blur on the turning group (up to 26 samples, 40 deg); back plate shifts 6 units against the spin; art_ring_under lags 2.5 deg; arms trail up to 16 deg at the tips; plaques blur with the group | Step to the end rotation in one 120 ms tween, no blur |
| Land | wheel settles | 80 ms latch + 250 ms slice flash | Round 39 landings kept: PERFECT latch jaws (beak ring on the octopus), gold rail, word sticker 650 ms then bits; the landed slice lifts and gets a cream outline, others dim to 62 % | Rail recolour only; outline, no flash |
| Figure acts | land + 0.1 s | 0.7 s in, 0.4 s out (T2) | Chariot surges + dust, lion pounces, net thrown; harpoon fires, dome pulses, the jellyfish stings; the two border arms curl in to grab the slice | The figure holds its act pose, no particles |
| Needle reacts | land + 0.15 s | 0.3 s ease-out | Thumb down on a hit, up on a whiff or block; beak snaps; tucked arms clench | The pose is set at once |
| Phase change | HP crosses a pip | 120 ms hit-stop (3 frames), white flash on the wheel only (180 ms), art cross-fade 0.8-1.0 s | Round 3.16 v3 beats kept (pip rings, banner flips, `PHASE 2` temp label). Aurelian: the crowd fills, braziers light, gates lift, beasts walk in. Tethys: the eyes open wide, the skin flushes, the blue rings bioluminesce, more arms grip | Instant swap, no flash, no hit-stop |
| Damage cracks | HP below max | continuous (`dmg = 1 - HP/max`) | Cracks open on the bezel, the floor ring and the over-art (7-10 seeded cracks, ember glow) | Same (static) |

## 7. Phase rules (art)

| Phase | Aurelian (arena pit) | Tethys (octopus) |
|---|---|---|
| P1 | half-empty stands, 12 torches, gates shut | the arms lazy, lids half shut (0.5), mottled red-brown skin, blue rings dull |
| P2 (66 %) | the stands fill, 24 torches, braziers lit, the four gates open and lions walk in, blood on the sand | eyes fully open, skin flushes orange-red, blue rings glow (x0.9), second arm set wakes on the A/B variants |
| P3 (33 %) | fire on the tiers, the bust's eye turns red (A), embers | eyes turn red, skin crimson, rings blaze (x1.3) |

## 8. Godot 4.7 mapping and performance budget (per boss wheel)

**Node tree.**
- `BossWheel (Node2D)`
  - `BackPlate (Sprite2D)`
  - `Turning (Node2D, rotation)`
    - `UnderRing`
    - `Slices`: a `Polygon2D` wedge per slice, with a shared ShaderMaterial and a per-slice `scene_tex`. The scene is an upright sub-viewport or flipbook atlas; top-down figures rotate with the slice.
    - `Separators` and `RimBand` (one annulus shader)
  - `InnerRing (Node2D, own rotation)`
  - `Bezel` (baked sprite + telemetry shader)
  - `OverArt`
  - `Plaques` (`top_level` Controls, counter-rotated)
  - `Hub`
  - `NeedleRig` (`pointer_angle`)

**Shaders.**
- UV rotation per ring (one uniform).
- Rotational motion blur: N taps along the arc in the ring shader, only while `|angular velocity|` > 3 deg/frame.
- A scroll shader for the track ruts and dust and for caustics and marine snow.
- The plaque-zone desat/darken is a mask uniform in the slice shader.

**Figures.**
- Chariots, fighters and captives are `AnimatedSprite2D` flipbooks: 8-12 frames, 64-128 px.
- Octopus arms are a `Skeleton2D` chain per arm, about 8 bones driven by a sine and a trail term, or a `Line2D` with a width curve and a texture.
- The emoji hand is one sprite rotated about the sleeve root.
- The beak is two sprites.

**Budget per boss wheel at 1080p:**

| Item | Budget |
|---|---|
| Textures | 4 MB or less (BC7); figure atlases 2 x 2048^2 at most |
| Draw calls | 40 or fewer (6 wedges batched, 6 plaques, rig 4, hub 3, rings 4) |
| Arms | 6 Skeleton2D with 8 bones each, or 6 Line2D |
| Particles | 2 GPUParticles2D (dust, embers / bubbles), 300 or fewer |
| GPU time | under 1.0 ms on the target (blur taps only while spinning) |

**Determinism.** Every motion is presentation only. Figure acts key off the resolved landing (slot, tier) and never feed back into rules. Rotations come from the rules' rotation, so preview equals result.

## 9. Retrofitting the other bosses (same slots, same pipeline)

**The recipe for each corp:**
- one back_plate;
- one under-ring;
- a slice-figure set (one figure per program, lit in the type colour);
- one over-ring;
- one hub portrait;
- one needle rig with its hit/whiff poses;
- phase deltas.

Everything else (plaques, rim band, bezel, rail, ticks, HP arc, blank window) is shared.

| Corp / boss | back_plate | over-art | slice figures | hub | needle rig (hit / whiff) | phases |
|---|---|---|---|---|---|---|
| Meridian / THE MANIFEST | the container-wall fortress and rail yard | gantry crane arms over the rim, swinging containers | forklift ram (SHIM), container drop (OVERFLOW), container wall (DEFRAG), priority beacon (PRIORITY) | the express-arrow core (Priority Routing) | the crane hook on its cable (hook drops and clamps / swings empty) | P2 hazard lights + steam, P3 containers stack over the rim |
| Solace / RENEWAL ENGINE | the lit DNA helix | vines of cells budding over the rim | capsule dose (DOSE), mitosis (GROWTH), syringe | the renew loop (Auto-Renew) | a pipette dropper (drop falls / dries) | P2 the helix unwinds and glows pink, P3 cells divide across the slices |
| Halcyon (civic boss) | the seven-tier Civic Core | scanning-eye drones orbiting the rim | gavel (JUDGEMENT), citation receipt, siren dome | the EYE | the eye's scan beam (beam locks red / blinks shut) | P2 more drones, P3 the eye opens fully, violet floodlight |
| Orbital (station boss) | the silo crescent and dishes | satellite dishes turning on the rim | solar flare, drone, weight (anvil) | the ringed planet | a docking arm (latches / retracts) | P2 the dishes track, P3 the silo opens |

## 10. GDD and design questions (consolidated)

1. **NULL art hint when modified** (section 3).
2. **Multiply on the beak boss** (section 4).
3. **Boss inner ring** (Aurelian D): who nudges it, does it respin, and are x2 / ANCHOR / PIERCE the right picks for LION / RETIARIUS / MURMILLO.
4. **Chariots hold station** rather than lapping the track, so they keep meaning their slice (designer to confirm).
5. **Tethys loadout change** (STING and DETOUR) for the corps agent.
6. **Illustrated slices on boss wheels**: a deliberate exception to ART_BIBLE 1.2 / 3.4. Log it in DECISIONS.md.
7. **The defend rule** (the wall sits on the hub side) can't hold for upright scenes at every angle. Proposal: it applies to FX and card art only; slice scenes stay upright.

## How to run (Python 3.14 + Pillow + numpy; no GPU; nothing reads the clock; every random draw is seeded)

```
python scripts/r41cache.py                      # cache the round 41 player wheel + HUD plate (read-only import)
python scripts/sheets.py dir roman A|B|C        # direction sheets (same for atlantis)
python scripts/sheets.py phases roman D         # phases sheet
python scripts/sheets2.py final roman|atlantis  # finals (combat frame + sizes + needle)
python scripts/sheets2.py emblem roman|atlantis
python scripts/sheets2.py readability | compare | system
python scripts/anim.py frames roman D 0 155     # frames to D:/rc_scratch/boss_wheel_v2/frames_roman
python scripts/anim.py gif roman
blender -b --factory-startup -P scripts/encode_mp4.py -- D:/rc_scratch/boss_wheel_v2/frames_roman roman_anim.mp4 156
```

**Module map:**

| Module | Contents |
|---|---|
| `bw_kit` | paint kit |
| `shapes` | skeleton pen |
| `render2d` | render modes |
| `wheel_v2` | THE TEMPLATE |
| `roman`, `roman_bc`, `roman_d` | Aurelian directions A / B, C / final |
| `atlantis`, `atlantis_bc`, `atlantis_d` | Tethys directions A / B, C / final |
| `fig_roman`, `fig_atlantis` | figure library |
| `emoji_hand` | the VERDICT hand |
| `directions` | registry |
| `anim`, `encode_mp4` | reel |


---

# ROUND 3 (v3): every boss has its own MECHANIC

The v2 finals (`*_wheel_final.png`, `*_anim.*`) are kept as history.

## v3 files

| File | What it is |
|---|---|
| `roman_v3_final.png` | THE PANTHEON. Top: the full combat frame. Bottom: combat size, a 2x close-up, and the needle at rest, on a hit and on a whiff. |
| `roman_v3_mechanic.png` | The four god states (normal, ascendant, wrathful, ascendant + wrathful), a mid-fight wheel, the god table and the rules. Option C and Neptune are noted. |
| `roman_v3_anim.mp4` / `.gif` | The gilding moves onto a wrathful god, the spin, the landing (SHIM 24), a hit cracks Vulcan into wrath, then phase 2. |
| `roman_v3_boss_emblem.png` | The VERDICT hand in front of the apotheosis sunburst. |
| `atlantis_v3_final.png` | THE TANK. Top: the full combat frame. Bottom: combat size, a 2x close-up, and the tank at rest, migrating and landed. |
| `atlantis_v3_arms.png` | The arms go 2, 4, 6, 8 while the creature rises with them. Includes the reveal close-up, the curve and the sprint ruling. |
| `atlantis_v3_anim.mp4` / `.gif` | Idle, the fish migrate (the "spin"), six arms land, the reveal (arms 7 and 8 burst out, the cyber kraken climbs out), one more migration, then all eight arms land. |
| `atlantis_v3_boss_emblem.png` | The kraken climbing out of its tank: 8 arms, LED brow, plate. The v2 `atlantis_boss_emblem.png` was regenerated with 8 arms as well. |

## Roman v3: THE PANTHEON (fresco gods, approved)

**Look.**
- **Slices:** every slice is a tiled fresco bust: plaster, a halo in the slice type colour, a robe in the type colour, the god's attribute, and tesserae with grout.
- **Frame and bezel:** gilded borders, a gilt laurel bezel, the aureus-gold bezel.
- **Hub:** the emperor's apotheosis, a marble bust with a gilt laurel on a gold-rayed mosaic sky. The sky turns red in phase 2.
- **Needle:** kept as the royal box with the VERDICT emoji hand. The emperor still judges the gods.

**God to action, in real GDD vocabulary:**

| God | Normal | Wrathful (3 cracks) |
|---|---|---|
| Mars | SHIM 14 | SHIM 14 PIERCE (ignores block + shield, GDD 2.7 ruling) |
| Jupiter | OVERFLOW 24 | OVERFLOW 24 + CORRUPTED on your landed slice (GDD 2.9) |
| Minerva | DEFRAG 12 | counterattack: SHIM 12 |
| Mercury | **RESIST 2**: the boss gains spin resistance 2 until its next turn (GDD 2.5 resistance as a slice effect; glyph = the locked WEIGHT/RESIST alias). This replaces "extra nudge". | theft: -1 RAM per landing (Meridian drain precedent) |
| Vulcan | INFECT 3 (burn = CORRUPTED) | spreads: CORRUPTED on 2 of your slices |
| Pluto | NULL | the void bites: SHIM 6 |
| Neptune | SHIM 10 SWEEP. Seven gods but six slices, so Neptune replaces Mercury in phase 3; Mercury's cracks carry over. | n/a |

**The combined mechanic, ASCENDANT + OMENS.**
- **Ascendant:** one god is gilded and its slice resolves x2. The plaque shows the doubled value with a gold x2 tag, so preview = result.
- **Gilding movement:**
  - It moves one god clockwise at the start of every boss turn, in a fixed order. **No RNG**, so the telegraph (a dashed gold outline plus a NEXT tab) is always true.
  - It skips Pluto, and starts on the god opposite the needle.
  - Respin and Flip move the wheel, not the gilding: the gilding belongs to the god.
  - Phase 3: two gods ascend at once.
- **Omens:**
  - Each player hit that deals damage adds 1 crack to the god under the boss's needle that turn, at most 1 per god per turn.
  - Three omen pips sit on the rim band of each slice.
  - At 3 cracks the god turns WRATHFUL for the rest of the fight: a red tag on the plaque, red-glowing cracks, the flipped effect.
- **Ascendant + wrathful:** the wrathful effect is doubled. It is telegraphed hard:
  - gold leaf over the cracks;
  - the fresco bleeds light;
  - the emperor's thumb trembles (+-6 deg at 9 Hz).
  - Reduce effects: no bleed or glints; the thumb holds half-turned.
- **The risk choice:** you crack the god the boss lands on. Breaking a strong god while the gilding is far away is safe; breaking it as the gilding arrives makes the fight's worst slice.
- **Not chosen:** C, THE SENATE VOTE. It adds a second HUD layer; it would suit an elite better.

**GDD flags (Roman):**
- Resistance as a slice effect is new; today it is only a passive or hub trait (GDD 2.5).
- A slice changing type mid-fight: the preview must recompute, and rewind must not cross the crack (a crack is a state change set by resolution).
- Pluto turning hostile changes the only "miss" (Cold Exit, Fault Tolerance, Zero Day, Stolen Intent all reference NULL). Proposed: those effects keep treating Pluto as NULL until it is wrathful.

## Atlantis v3: THE TANK (designer rulings applied)

**The model.**
- The wheel is a fixed ring aquarium round a central tank. **Nothing turns.**
- **8 slots of 45 deg.** For this boss: 40 ticks of 9 deg, 5 per slot, so precision tiers keep their +-1 / +-2 meaning. This is a per-boss tick count; flag it against GDD 2.1, which locks 30 ticks / 6 slices.
- **The predators ARE the slices:**
  - SHARK SHIM 8
  - SWORDFISH OVERFLOW 14
  - JELLYFISH SWARM INFECT 2
  - THE WRECK SANDBOX 6 (the octopus hides)
  - MORAY SHIM 6
  - NAVAL MINE OVERFLOW 12
  - ELECTRIC EEL SHIM 5
  - SUBMARINE NULL (it passes; nothing)
- Barracuda, anglerfish and divers are ambient (the barracuda school sweeps during migration).
- **Spin = the fish move** (designer ruling).
  - The seeded spin result is the predator ring's new offset: same RngService stream, same determinism.
  - A spin of N ticks moves the fish N ticks round the tank.
  - The ring keeps its order and spacing, so the slice under a pointer is still (rotation + pointer_tick) mod ticks. Only the art moves.
  - Each fish swims with its own easing (sharks surge, mines drift late), but all of them land exactly on the result.
- **Nudge moves the fish** (designer ruling): one nudge shifts the ring one tick, exactly like nudging a wheel. Resistance still absorbs nudges.
  - Flip mirrors the fish order.
  - Arms cannot be nudged: they are pointers.
- **Plaques follow the predator**, because the value belongs to the predator. They ride the ring's slot positions at r = 290, so spacing never collapses mid-swim.
  - The 8 tank zones (open blue, kelp, reef, wreck site, sand flats, the vent, trench, coral) are fixed scenery and carry no rules.

**Pointers = arms.**
- Every arm that climbs out of the tank is a pointer, radiating outward. Its tip is lit in the type colour of the predator it grips; PERFECT adds a gold latch ring at the tip.
- Emergence order is fixed (top, bottom, right, left, then the diagonals). Empty sockets 1-8 on the tank wall show the arms still to come.
- Twin-pointer precedent (GDD 2.1, "several pointers, evenly spaced"; 2.11 Multiply) is extended to N = 2, 4, 6, 8.
- The HUD result chip sums all arms. The breakdown tooltip lists each arm's predator and tier.

**Curve:**

| HP | Arms |
|---|---|
| 100-75 % | 2 |
| 75-50 % | 4 |
| 50-25 % | 6 |
| < 25 % | 8 |

Phase pips sit on the HP arc at 75 / 50 / 25.

**8 arms = a deliberate SPRINT** (designer ruling). With all eight out, every slice resolves every turn. There is no damage scaling: the last quarter is a race to see who kills whom first. The 0.5x "tired arms" proposal is withdrawn; arms 5-8 only look paler.

**The escalating reveal:**

| Phase | What shows |
|---|---|
| P1 | The body is unseen: a shadow under the water, bubbles, a faint eye glint. |
| P2 | The eyes break the surface. |
| P3 | The mantle is out and the blue rings glow. |
| FINAL | The cybernetic kraken, the corporation's brain (details below). |

FINAL details:
- Bolted cranial plates, a TETHYS plate, an antenna beacon.
- An LED eye array across the brow.
- Cable tendons and steel bands down every arm.
- It climbs OUT of the tank: drawn 32 % bigger, over the rim.

The reveal beat:
1. Hit-stop, 3 frames.
2. The water boils white.
3. Arms 7 and 8 burst out (0.6 s).
4. The hardware lights up (0.8 s).

Reduce effects: the final art appears at once.

**Octopus or kraken?** An octopus silhouette (8 arms, bar pupils) reads best at r = 60. The fiction calls it the Kraken.

## v3 scripts

| Script | Builds |
|---|---|
| `fig_gods.py` | the god busts |
| `fresco.py` | fresco paint + tesserae |
| `roman_v3.py` | the Pantheon direction on the wheel_v2 template |
| `sheets3.py` | Roman final, mechanic, anim, emblem |
| `atlantis_v3.py` | the tank renderer: own compose, 8 slots, N pointers |
| `sheets_tank.py` | Atlantis final, arms, anim, emblem |

The Pantheon runs on the shared template. The tank needs its own compositor (8 slots, fixed frame, N pointers), but it reuses the plaque, kit and render modes. The section 1 template should grow `slot_count`, `tick_count` and `pointers[]` to cover it.
