# Round 13: the slice system (glyphs, tiers, state overlays)

This round builds on round 11's Screens & Data slices (family C). Each slice is a live CRT screen in its own bezel, with an upright white glyph and value on a darkened read plate. The slice frames (pointer, hub, bezel, boss) are covered in `round13_wheel_details/`, not here.

The game names come from:
- `scripts/data/rc.gd`: `SliceType { ATTACK, CRIT, DEFEND, EVADE, SHIELD, DEPLOY, HEAL, AFFLICT, MISS }` and `Status { CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE }`;
- `docs/art_asset.md`: sections E2, E3 and E5, and the Appendix slices and cards.

Anything not in the game is labelled **placeholder (not in game)** on the sheets.

## Files
| File | What it shows |
|---|---|
| `glyph_set.png` | The full glyph pass, 66 cells, each at 64, 24 and 16 px, in colour and greyscale. Below them, the 16 px confusion fixes, old shape against new. |
| `tiers.png` | Tiers I, II and III. Hero tiles for EXPLOIT, every program at all three tiers, a mixed-tier wheel at r = 150, and r = 60 wheels in colour and greyscale. |
| `states.png` | Eight state overlays. Each is shown on 3 slice colours, on an r = 60 wheel (3 of its 6 slices carry the overlay), and in greyscale. |
| `states_fx.gif` | Each overlay's idle loop: 24 frames at 70 ms, 2.6 MB. |
| `contact_sheet.jpg` | All of the above. |
| `scripts/` | The scripts. See "Build" at the end. |

## 1. Glyph list
All glyphs share one language:
- one solid white silhouette with a few dark cut-outs;
- a dark rounded outline added by `slicelib.glyph_rgba`;
- strokes at least 40/512 of the box and cut-outs at least 24/512, so a stroke is still at least 1.25 px at 16 px;
- the outer silhouette alone must identify the glyph.

Attacks are pointed and aggressive. Defences are blocky and solid.

**Slice types: one program each.**

| Program | Type | Glyph |
|---|---|---|
| EXPLOIT | ATTACK | dagger |
| ZERO-DAY | CRIT | 12-point burst |
| FIREWALL | DEFEND | brick wall with three flame tongues (**new**) |
| SANDBOX | SHIELD | window inside a window |
| PROXY | EVADE | double chevron (approved) |
| PATCH | HEAL | bandage |
| VIRUS | AFFLICT | biohazard (approved) |
| TROJAN | DEPLOY | horse on a wheeled platform (**new**, from the designer's list; replaces the gift box) |
| NULL | MISS | tall slashed zero (**new**) |

**Corporation specials and other slice marks.**

| Slice | Owner and effect | Glyph |
|---|---|---|
| TARIFF | Meridian; drains RAM | receipt |
| CITATION | Halcyon; plants PARASITE | gavel on its block (**new**) |
| SOLAR FLARE | Orbital; overclocks, then corrupts | sun breaking the horizon (**new**) |
| DOSE | Solace; corrupts | capsule |
| INERTIA | adds +1 resistance | anvil (**new**) |
| DRONE | satellite | quad-rotor |

Drain variants such as `atk_7_drain` keep their type glyph and add the existing "−n RAM" chip.

**Placeholders (not in game).**

| Glyph | Shape |
|---|---|
| PHISHING | hook with a bait envelope |
| SHIELD | heater shield |
| ENCRYPT | password pill with `***` |
| RECON | magnifier |
| BURN | flame |
| BOMB | bomb |
| VAULT | steel safe door |
| KEY | key |
| SPOOF | fingerprint |
| STORM | cloud with a lightning bolt |

**Statuses.**

| Status | Mark | Effect |
|---|---|---|
| CORRUPTED | file split by a crack | hurts |
| PARASITE | tick | hurts; halves output |
| OVERCLOCKED | gauge pegged | helps, then hurts |
| ENCRYPTED | `***` over a field line | helps |
| CLEANSE | drop with a sparkle | action that removes CORRUPTED |
| PREDICTED | the status's own mark in a dashed badge | will happen |

Each mark sits in a badge whose shape says whether it helps, so the reading never depends on colour (art_asset Part I):

| Badge | Meaning |
|---|---|
| circle | helps you |
| diamond | hurts you |
| circle with a diamond notch | helps, then hurts |
| rounded square | neutral |
| dashed | predicted |

**Slice states (placeholders).**
- FROZEN: snowflake. The game's Freeze is wheel-level (the wheel skips its next respin).
- LOCKED: padlock.
- BURNING: the BURN flame.
- EMPOWERED: an up arrow on a bar.

**Card pictograms (E5).**
- Spin, clockwise and anticlockwise, plus "n+".
- Respin: a die.
- Nudge, and nudge on the inner ring.
- Free nudge: a price tag.
- Again: a rectangular repeat loop.
- Flip: a solid and a hollow triangle on either side of a dashed axis.
- Snap: a magnet.
- Ring lock: a ring with a padlock.
- Perfect: a diamond with a centre pip.
- Draw: two cards with a +.
- RAM: a memory chip.
- Freeze: the snowflake.
- Resistance: the anvil.
- Breach: a broken hub ring.
- Undock: a drone leaving its bay.
- Damage: the EXPLOIT glyph.
- Block: a plain brick wall.
- Shield points: the SHIELD glyph.
- Evade: the PROXY glyph.
- Heal: the PATCH glyph.
- All targets: three arrows fanning out.
- Take damage: a cracked heart.
- Exhaust: a card burning away.
- Target: a reticle.
- No damage: the round no-entry sign.
- HP: a heart.

Amounts sit at the bottom right of the mark.

### 16 px confusions fixed
Each pair is scored with the soft IoU of the two glyphs' 16 px coverage maps (`glyph_catalog.top_pairs`). The table gives the score before and after each fix.

| Pair | Before | After | Fix |
|---|---|---|---|
| CITATION ticket vs TARIFF receipt | 0.75 | 0.39 | CITATION becomes a gavel |
| FIREWALL (a shield with bricks) vs SHIELD | 0.74 | 0.48 | FIREWALL becomes a wall with flames |
| NULL (round slashed zero) vs the no-entry sign | 0.51 | 0.40 | NULL becomes tall and narrow; the no-entry sign stays round |
| SOLAR FLARE (rayed disc) vs ZERO-DAY burst | 0.47 | 0.46 | sun on the horizon, with rays on top only |

The SOLAR FLARE pair barely changes on the metric, because the metric scores blob overlap and misses that both old shapes were radial. By eye they were the worst pair, and the horizon shape fixes it.

Two more confusions were caught while drafting and fixed before the sheet:
- a RAM stick read as ENCRYPT's pill, so RAM became a chip;
- an INERTIA kettlebell read as LOCKED's padlock (0.67), so INERTIA became an anvil.

Some pairs are kept alike on purpose:
- SPIN clockwise and anticlockwise are a mirror pair, with a bigger arrowhead and the card text to tell them apart;
- BURN and BURNING share a mark;
- ENCRYPT and ENCRYPTED share a mark;
- HP and TAKE DAMAGE are both hearts, one cracked.

## 2. Tier rules (placeholder: no upgrade tier exists in SliceData)
The glyph and value block is identical at every tier: same size, same plate, same position. Only three things change:

| | Tier I: plain | Tier II: trimmed | Tier III: gilded |
|---|---|---|---|
| Bezel | matte dark, hairline dimmed | brushed steel, type-colour trim line, brighter corner brackets | gold, etched circuit trace with vias, holo rim whose hue walks around the wheel and drifts over time |
| Screen | 70 % gain, 30 % desaturated | 100 % gain | 122 % gain, a diagonal holo sweep and data sparks |
| Tier tab | 1 grey pip | 2 pips in the type colour | 3 pale gold pips |

The tier tab is a small dark plate notched into the top centre of the screen.

At r = 60 the tab is smaller than 2 px. There, the bezel material (dark, silver or gold) carries the tier, and it still reads in greyscale.

## 3. Overlay rules
- **Layer.** An overlay is its own layer. It sits above the screen and bezel and below the read block, so nothing can cover the value.
- **Read window.** Inside the read window, an ellipse fitted to the glyph and value block, every overlay thins to 35 % or less. Most effects drop to 0 % there.
- **Badge.** Every overlay puts its badge, upright, in the outer-right corner. States with a rule number also add a chip by the inner edge: OVERCLOCKED ×1.5, PARASITE ×0.5.
- **Loops.** All motion loops over t ∈ [0, 1). Noise is sampled on a circle (`loop_off`), or cross-faded, so the loop has no seam.

| State | In game? | Look | Idle loop |
|---|---|---|---|
| CORRUPTED | status | slabs displaced sideways with an RGB split, magenta and green macroblocks, grain, red bezel | 12 glitch states per loop; a tear line scans down |
| OVERCLOCKED | status | hot amber bezel, electric arcs along the bezel band, heat shimmer in the side lanes, ×1.5 chip | the arcs re-roll 8 times per loop; the heat pulses |
| ENCRYPTED | status | cyan hex cipher shell, bright rim, `*` marks along the outer band | a shimmer sweep crosses the shell; the cells churn; the `*` marks scroll |
| PARASITE | status | veins climbing from the hub side, the lower half drained of light, a sick-green inner bezel, ×0.5 chip | pulses travel down the veins to the hub |
| FROZEN | placeholder | cold glass tint, an ice crust grown in from the bezel, crystal ridges, cracks | the crust edge breathes; glints twinkle |
| LOCKED | placeholder | a roller shutter down to the value with a hazard edge, cage bars on either side of the value, a lock LED | a glint slides across the slats; the LED blinks |
| BURNING | placeholder | flames off the rim and along the bezel; the reserved BURN blotches char the screen, with ember rims | the flames rise; embers drift outward |
| EMPOWERED | placeholder | gold rim glow and a halo past the rim | chevrons climb both side lanes; a light band rises; the glow pulses |

## 4. Building it in Godot 4.7
**Glyph atlas.**
- Export each 512 mask from `glyphs13.py` / `slicelib.glyph_mask` as an SDF or MSDF atlas, one cell per glyph id, at 128 px.
- Draw the glyphs with a shared shader that does the white fill and dark outline: `smoothstep` on the distance, with the outline width as a uniform. One atlas then serves 16 px to 64 px with no per-size art.
- Simpler alternative: export SVGs and let Godot import them at 1×, 2× and 4×.

**Slice node.** Each slice is a `Control`, or a `Polygon2D` wedge, with a `ShaderMaterial`. It has:
- the screen texture: a SubViewport, or a baked flipbook per program;
- uniforms `slice_color`, `tier` (int 1 to 3), `time`, `span_deg`, `r_in`, `r_out`;
- in the shader:
  - `tier` picks the bezel material (matte, steel, or gold with holo);
  - `tier` sets the screen gain and saturation (0.70, 1.0, 1.22);
  - for `tier == 3` only, it adds the holo sweep;
  - it draws the tier-tab pips in the same pass.

The distance fields `e_tile`, `e_scr`, `u` and `v` in `slicekit.geom` port line for line to the fragment shader.

**Overlay layer.** Each slice has a sibling `ColorRect` with its own `ShaderMaterial`: one shader per state, or one uber-shader with `uniform int state`. It uses the same wedge uniforms, plus:
- `read_center`, `read_radii` for the read window;
- `seed`.

CORRUPTED needs `uniform sampler2D screen_tex : hint_screen_texture` to displace what is underneath. The others are pure procedural noise with `TIME`.

The flames and the EMPOWERED halo extend about 34 master px past the rim, so the overlay's rect is padded outward.

**Draw order per slice:** screen and bezel, then the overlay layer, then the read block (a glyph `TextureRect` and a value `Label`, upright and counter-rotated), then the badge and chip. Views only read state; the overlay is chosen from the slice's runtime status.

## Build
Run from `scripts/` (Pillow and numpy only):
1. `python make_glyphs.py`
2. `python make_tiers.py`, about 2 minutes
3. `python make_states.py`, about 6 minutes including the GIF
4. `python make_contact.py`

Renders are cached in `../scratch/`, which git ignores.

## Weakest part
- **Tier differences at hero size are clear, but II and III are close on the grid and at r = 60.** Steel against gold separates them; the pips do not.
- **The tier III circuit etch barely shows.** It needs a deeper or wider trace, or a glowing via, to read.
- **EMPOWERED's chevrons are modest** next to the stronger overlays.
- **On small wheels FROZEN and ENCRYPTED both read as "cool cyan glass".** Their badges and the white crust versus the hex grid separate them, but they share a temperature.
