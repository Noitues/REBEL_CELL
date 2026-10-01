# Round 5: s_c_screen_data (SCREENS & DATA)

Each slice is a small CRT running its program. Every tile is built the same way, and only
the screen texture changes:

1. **Per-slice bezel.** A dark plastic frame about 8.5 px wide, inset 1.6 px from the wedge
   edges. Screen corners are rounded (r 9–11 px). A top-left key light and an outer lip
   catch-light shade it. A hairline in the program colour runs around the screen, and a
   **power LED** sits at the outer corner.
2. **Polar UV.** `x = arc length from the midline`, `y = r_out - rho`. Rows of text, charts
   and scanlines bend into arcs that follow the rim. Wedges of 2, 3 and 5 ticks re-crop the
   same texture without stretching it.
3. **Barrel bulge.** `uv = c + (uv - c) * (1 - 0.055 * |n|²)` hints at the CRT curvature.
4. **Phosphor glow.** The texture plus two blurred copies (5 px × 0.55 and 14 px × 0.35).
5. **Scanlines.** `0.70 + 0.30 * cos(2π * y / 3px)`, along arcs.
6. **Edge vignette.** Driven by the screen's distance to the bezel.
7. **Read plate.** A gaussian ellipse darkens the screen by 62% where the icon sits.
8. **Glass glint.** A soft band at the top-left of the screen.
9. **Icon block.** A white glyph about 38% of the chord at 0.6 of the radius, with a dark
   outline and drop shadow. A Bahnschrift Bold Condensed value with a dark stroke sits
   under it. On 60° and wider wedges the value moves beside the glyph. The block is rotated
   with the slice (outward = up). NULL shows only the glyph, at 1.3×.

## Programs

| Program | Glyph | Screen texture | Shader behaviour (24-frame loop) |
|---|---|---|---|
| EXPLOIT | tilted dagger | Scrolling hex dump (address + 8 bytes); one injected `JMP 0xDEAD ;inj` line on a pink-red bar | 16-line scroll per loop; the bar pulses 4× per loop; at each peak the whole screen washes red-pink |
| ZERO-DAY | 12-point burst | 2 px white noise that resolves into a skull | resolves over 0–55%, holds, then tears back at 80%; RGB split + band offsets, strongest while unresolved |
| FIREWALL | shield with brick cut-outs | `[#]` brick wall in staggered rows over the outer 58%; empty lane below | 4 red packets rise from the hub side and bounce off the wall; struck bricks flash white with a spark line |
| SANDBOX | window-in-window | 6 nested terminal windows (title bar, 3 dots, `$ run ./boxN`) recursing to a core dot | breathing: the recursion step and brightness follow a sine; the core swells |
| PROXY | double chevron | Network map of 9 nodes on dim edges | dashed route marches toward the target; reroutes 3× per loop; the abandoned node shows a fading red X |
| PATCH | bandage | `PATCH v3.x` segmented progress bar plus a `+`/`-` diff (green adds, red removals) | bar fills over 0–80%; diff lines appear as it fills; the full bar blinks |
| VIRUS | spiked capsid | 6 px block grid of dim healthy bits | infection grows from 2 seeds with a jittered, glowing front; per-frame datamosh smears blocks sideways; purge flash at loop end |
| TROJAN | gift box with bow | `free_gift.exe` smiley | scripted flicker (frames 11–22) into an angry payload face plus `PAYLOAD` garbage; RGB split on flicker frames |
| NULL | slashed zero | Dead near-black CRT | only faint scanlines and a collapsed-beam dot + line afterimage near the hub, slowly pulsing |

### Enemy theme: Meridian dashboard (`theme = "corp"`)
All slices use one material:
- slate glass `#0F1115` with a 10 px grid;
- a graphite bezel and an orange hairline and LED (`#FF8A1F`);
- a uniform `MRD-0n` header.

Each type gets its own orange widget:

| Type | Widget |
|---|---|
| ATTACK | bar chart |
| CRITICAL | KPI % |
| DEFEND | compliance checklist |
| SHIELD | coverage gauge |
| EVADE | line chart |
| HEAL | SLA bar |
| AFFLICT | heatmap |
| DEPLOY | pie |
| MISS | NO DATA |

Colour never tells the types apart. Only the glyph, a 3 px accent strip and a header pip
use the type colour. The animation is sterile: bars grow, checks tick, the gauge breathes,
the pie rotates. The hub is a "COMPLIANCE MONITOR" card with the Meridian hex mark. The
outer ring is brushed graphite with orange ticks.

## Godot 4.7 build
- **Mesh.** One `ArrayMesh` wedge per slice (a polygon fan or ring strip), built from
  `start_tick` and `ticks`. Feed polar data via UV: `UV.x = angle offset from mid (rad)`,
  `UV.y = rho` in px (or normalised). The fragment computes
  `tx = W/2 + rho*ang` and `ty = r_out - rho`, which is exactly `render_slice()` in
  `scripts/slicelib.py`.
- **One shared `canvas_item` shader** (`slice_crt.gdshader`) with per-slice
  `ShaderMaterial` instances (or instance uniforms):
  - geometry: `span`, `r_in`, `r_out`, `bezel_w`, `gap`;
  - colour: `program_color`, `bezel_color`, `hairline_color`;
  - `program_id` (int), `time_offset` (de-syncs slices), `plate_strength`, `tex_gain`,
    `glyph_scale`.
- **Screen content.** Two routes:
  - (a) **Procedural, in-shader**: noise/resolve, brick grid, block infection, dashed path,
    progress fill and scanlines are all cheap math. Branch on `program_id`.
  - (b) **Atlas**: text-heavy screens (hex dump, diff, terminal windows, dashboard widgets)
    go into a `screen_atlas.png` with one 256×256 cell per program × theme. The shader
    scrolls or flicker-masks UVs. The EXPLOIT scroll is a `fract(uv.y + TIME*k)`;
    TROJAN switches between two atlas cells on a 24-step flicker table.
- **Glow.** Sample a pre-blurred mip (`textureLod(atlas, uv, 2.5)`) and add it, or rely on
  the `WorldEnvironment` glow with HDR 2D on.
- **Icons stay crisp.** The glyph + value is a separate `Control`/`Sprite2D` child per
  slice, outside the screen shader: an SDF glyph atlas with a dark outline and a `Label`
  with an outline. It is rotated to the slice mid-angle and placed at
  `r_in + 0.6*(r_out - r_in)`. The darkening plate is computed in the screen shader from
  the same anchor.
- **LOD.** Below about r = 120, set `tex_gain` 0.55, `plate_strength` 0.85, `glyph_scale` 1.45
  (see `small_and_grey.png`).
- **Determinism.** The shader only reads `TIME + time_offset` and does not affect game
  state. The noise seeds in the scripts are fixed.

## Files
- `programs_sheet.png`: all 9 programs, the EXPLOIT 2-tick and 5-tick variants, and 2 Meridian tiles.
- `wheel_player.png`: 9 programs on 30 ticks, with pointer, hub, bezel and HP arc.
- `wheel_enemy.png`: the Meridian compliance-monitor wheel plus the full dashboard skin family.
- `shader_fx.gif` (2.2 MB, 24 frames at 12 fps): all 9 programs plus Meridian EXPLOIT.
  `shader_fx_strip.png` shows 8 time samples each.
- `small_and_grey.png`: r = 60 straight downscale versus LOD, and the hero wheel in greyscale.
- `scripts/`:
  - `slicelib.py`: slice renderer, glyphs, bezel and post-processing;
  - `programs.py`: screen textures;
  - `wheel.py`: wheel assembly;
  - `make_all.py [sheet|player|enemy|small|gif|all]`.

## Verdict
- **Strongest.** ZERO-DAY (the skull resolving out of noise reads instantly and feels rare),
  EXPLOIT (the scrolling dump with an injected bar is the most "program"-like), and
  FIREWALL (the bricks made of characters show the concept best).
- **Weakest.** SANDBOX's breathing is too subtle at small sizes. NULL is deliberately dead
  but nearly blank (its afterimage dot sits near the hub so the plate does not hide it).
  VIRUS's colour field can overpower its neighbours, so keep its gain lower.
- **r = 60.** With the straight downscale, values read but glyphs blur together. With the
  LOD pass (bigger glyph, calmer texture, stronger plate), both the glyph and the value
  read. Greyscale holds because the white-with-dark-outline icon block carries the
  contrast.
- **Favourite.** ZERO-DAY, with EXPLOIT's injected-line flash a close second.
