# Godot port spec: the locked combat screen (roadmap step 8)

**Status: DRAFT, not posted.** Art-pass draft, rebuilt 2026-11-04 on the rebuilt board (`final/` gate 1 of 2026-11-04, the effects rebuild of 2026-11-03, room grade rb2-1). It is not signed off by the designer and has not been sent to build. The mailbox draft is `MAILBOX_DRAFT.md` (also DRAFT, not posted).

**Generated tables.** Every table and appendix that carries a number sits between `<!-- gen:NAME begin -->` and `<!-- gen:NAME end -->` markers and is written by `port/src/port_spec.py` from the data files (`port/*.json`, `backdrop/grade.json`, `backdrop/checks.json`, `final/checks.json`). No number inside a marker is typed by hand; change the data and re-run, never edit the block.

**What it covers.** How to build the locked Shifting Waves combat board in Godot 4.7. The board is defined by:
- `final/`: plates, NOTES, `checks.json` and `src_snapshot/` (rebuild, gate 1 2026-11-04);
- `corp/NOTES.md`: the corp skins; the designer rulings DR-1..DR-10 in `VISUAL_PLAN.md`, and `docs/ART_BIBLE.md` 2.4 and 3.14 (the corp-skin and room notes);
- `effects/`: the effects and their timings (`timings_CDHL.json`, `timings_MPST.json`, rebuild 2026-11-03);
- `hover/`: 11 hover plates;
- `backdrop/`: the room grade;
- `transitions/`: T5 and T6.

Every element family is listed with:
- what is a shader, with its uniforms and maths;
- what is a texture or sprite sheet, and how it is baked from the PIL generator;
- what stays code-drawn;
- which current Godot node it lands on;
- the order of work and the test hooks.

**Fixed rules for the port:**
- No game number, word or rule changes.
- The designer rules below are part of the spec:
  - no dashed or dotted lines;
  - no needle;
  - cross-hatch means HP lost at this END TURN, and the hatch colour is the cause;
  - the arrowed outline is kept, and means movement only (DR-1);
  - HOT/COLD/FAR is the time grammar;
  - **corp skins per the `docs/ART_BIBLE.md` 2.4 designer-ruling note (DR-6):** the corp theme is told by material; the corp hue appears only on the rim, the bezel lip, the crest and the cell edges; the cell fills are neutral slate with a low-chroma tint; every corp hue ink keeps dE76 15 or more from Cell lime, GAIN, FOCUS and HARM. One gunmetal clock (the schedule band) is the same on every corp; SCHEDULE orange is on the live step only. The silver THIS TURN tape is retired;
  - pink belongs to the player;
  - no reserved fill colours (DR-5).
- Art-pass calls, part of the spec (REVIEW_RESPONSE, not designer rulings):
  - **effects draw under the HUD and the hand** (`docs/ART_BIBLE.md` 6.4 layer order; review 1.6); only `fx_hp_through`, `fx_refund` and `fx_trace_add`, which land on HUD rows, draw above it (section 1, z 14);
  - **every effect lasts 0.6 s or less** (VfxTier T2, `docs/ART_BIBLE.md` 5.3), with no per-effect override;
  - **the resolve beat lasts under 4 s**, plays its effects as concurrent tracks, and any input skips it (8.2);
  - the effect loudness order is damage > kill > block > state (8.4).
- **The room** is graded per `backdrop/grade.json` (rb2-1); Site and HQ-run fights show the cutaway room, the boss keeps the perspective close-up (`docs/ART_BIBLE.md` 3.14, DR-9). T5 / T6 show what DR-10 rules (section 10).

**Files beside this spec** (`port/`):

<!-- gen:files begin -->
<!-- gen:files end -->

---

## 0. Target code, and where it differs from the concept

### 0.1 Which Godot code this lands on
- **The brief named the wrong clones.** `godot_look_tide` and `godot_look_hqnet` hold the old two-spinner combat: `CombatScene`, 5655 lines, with `WheelView`, `WheelDisc` and `wheel_*.gdshader`. That is not the Shifting Waves screen these plates show.
- **The Shifting Waves fight is on game-v2.** I read it, read-only, in `D:/rc_art/godot_jackin`: branch `art/jackin-prewarm` on game-v2 `b09f9b9d`, 2026-10-30. Game-v2 has moved since (A-115 names `d98dcd78`), so build should re-check every path below against its head.

| Current file | Class | What it does today |
|---|---|---|
| `scripts/ui/waves_scene.gd` | `WavesScene` | The netrun's fight page. It hosts `WavesFight` "unrestyled". |
| `scripts/ui/waves/waves_fight.gd` | `WavesFight` | The controller. It owns or attaches a `WavesSession`, does preview, undo and rewind, maps input, and builds the views at `SIZE_PX` 1280x688. |
| `scripts/ui/waves/waves_spinner.gd` | `WavesSpinner` | The tower and its 3 rings, drawn immediately in `_draw()` from `WavesState`. Signals: `hovered`, `clicked`, `inspected`. Also `hit_test()` and `sector_at()`. |
| `scripts/ui/waves/waves_hand.gd` | `WavesHand` | One button per card. |
| `scripts/ui/waves/waves_hud.gd` | `WavesHud` | RAM, run HP, turn, stars and an info text. |
| `scripts/ui/waves/waves_step_strip.gd` | `WavesStepStrip` | The printed rotation and the SET dial. |
| `scripts/ui/waves/waves_lineup_strip.gd` | `WavesLineupStrip` | The wave lineup. |
| `scripts/data/waves_look_data.gd` + `content/config/waves_look.tres` | `WavesLookData` | Every placeholder colour and size. Its doc says the art pass "can replace this one resource". |
| `scripts/ui/fx/flash_limiter.gd`, `vfx_tier.gd`, `bit_path.gd`, `bits_seam.gd`; `shaders/kit/binary_bits.gdshader` + `bits_atlas.png` | | Existing FX kit, reused (sections 8 and 10) |
| `scripts/ui/arena/combat_backdrop.gd`, `backdrop_catalog.gd` | | Existing backdrop plumbing (section 4.1) |
| `Settings.reduce_motion`, `Settings.reduce_effects`, `Settings.flash_limiter` | | Existing switches. Every effect reads them. |

Design resolution: the project is 1280x720 with `canvas_items` stretch, and the plates are 1920x1080.
- All plate numbers in this spec are **plate px at 1080p**. Multiply by **2/3** for 720-design coordinates.
- Textures are baked at 2x plate scale or more, so they stay sharp at 1440p and 4K.

### 0.2 Name mapping: concept vs game data (open, do not guess)
The plates use the E10 concept names. Game-v2 content differs in places. **The port binds by game id.** The art follows the mapping below, and the rows marked OPEN need a designer or build answer before their art is wired.

| Concept (plates) | Game-v2 id | Status |
|---|---|---|
| Slice type BURST (big dots, magenta) | role GUN with `shots >= 2`: `burst`, `railgun` | Same rule as `WavesSpinner._slice_color` today. Confirm. |
| TURRET (Ben-Day bullseye, yellow) | role GUN with `shots == 1`: `turret` | Confirm. |
| SHIELD (scales, cobalt) | role SHIELD: `shield`, `bulwark`, `thorn` | Confirm. Thorn and bulwark share the texture and differ by glyph. |
| REPAIR (plus tiles, green) | role REPAIR: `repair` | ok |
| Units Packet, Worm, Payload, Adjuster | `packet`, `worm`, `payload`, `adjuster` | ok |
| Unit Jammer | `glitch`? (barrier 1, glitches) | **OPEN** |
| (no concept art) | `halo` (width 6) | **OPEN:** no plate shows it |
| Cards Nudge, Spin 2, Spin 3, Brace, Strike, Pull, Shove, Twist, Trigger | same ids | ok |
| Card Firewall ("Burn 2 units") | `scorch`? | **OPEN** |
| Card Hold ("Pause the wave") | no card; game-v2 has the SET dial (Q/W/E) | **OPEN:** the art has a Hold card and a HOLD THEN band plate |
| (no concept art) | card `bug` | **OPEN** |
| Card text ("Turn the tower 1" ...) | `WavesHand.card_text()` | The game's strings win. The art only sets fonts and plates. |

---

## 1. Screen stack (z-order) and node map

The order matches `f1_render._render`, the plate assembler, and the `extra` effect slot. Bottom to top. **2026-11-04 (gate 1):** the board effects slot is under the HUD and the hand (z 12.5); `f1_render.SPLIT` (`SPLIT['on'] = True`) returns the plate as two layers, `below` (z 0-12) and `above` (HUD, YOU strip, hand, stickers), for effects to be composited between them. The effect strips in `effects/` (rebuild 2026-11-03) are composited this way: below, then the effect, then the HUD and the hand. Their layer check counts 0 changed pixels on opaque HUD or hand pixels for every board-layer effect (`effects/NOTES_MPST.md` 1.6; `timings_CDHL.json` `px_on_hud_max`); only the three HUD-layer effects change HUD pixels.

| z | Layer | Kind | New node (proposed) | Replaces or extends |
|---|---|---|---|---|
| 0 | Room backdrop plus grade | texture plus optional post shader (4.1) | `CombatRoomLayer` (TextureRect) | `CombatBackdrop` / `BackdropCatalog` pick the room |
| 1 | Board scrim | baked into the graded room, or a shader (4.1) | (part of z0) | |
| 2 | Plate, bezel and enemy ring ground | corp skin shaders on ring meshes (4.3) | `CorpRingLayer` (Node2D with Polygon2D or MeshInstance2D bands) | `WavesSpinner._draw_rings` |
| 3 | Tower shadow and tower | baked sprites plus the hatch shader plus code-drawn marks (4.6) | `TowerView` (Node2D; rotates as one) | `WavesSpinner._draw_tower` |
| 4 | Schedule band, the gunmetal clock: engraved band, live step cell and chevrons, +N cells, HOLD plates | code-drawn flat gunmetal; SCHEDULE on the live step only (4.4) | `ScheduleBand` | `WavesStepStrip` drawing (the dial stays UI) |
| 5 | Unit cells: kind wash plus skin material plus enamel outline | shader plus code (4.3, 4.5) | `UnitCellLayer` | `WavesSpinner._draw_unit` |
| 6 | Future (+1/+2) marks, Adjuster ward arc | code | `BoardMarkLayer` (part 1) | |
| 7 | Units' marks: chevrons, pips, badges, glyph disc in token frame | code plus small sprites | `BoardMarkLayer` | `_draw_pips`, `_draw_chevrons`, `_draw_barrier` |
| 8 | Guns (player pink marker) | code (Line2D ribbons) | `GunLayer` | (new) |
| 9 | Landing arcs, lanes 436/453/470, diamonds, k dots | code | `BoardMarkLayer` (part 2) | `_draw_landings` |
| 10 | Band labels, ring tags, W4-W6 tickets | code plus corp ticket 9-patch | `BoardMarkLayer` (part 3) | `WavesLineupStrip` drawing |
| 11 | Sector digits, with holes punched in z4 and z10 | code | `BoardDigits` | |
| 12 | Hover: dim of the rest, hover path, cell, tag | dim post shader plus code (section 9) | `HoverDimLayer` plus `HoverMarkLayer` | `_draw_hover`, `_draw_targets` |
| 12.5 | **FX world layer (board effects)**, 2026-11-04: moved under the HUD (review 1.6, ART_BIBLE 6.4) | effects, section 8 | `WavesFxOverlay` | (new) |
| 13 | HUD (system cyan terminal) | Controls | `WavesHud` restyled | |
| 14 | FX HUD layer: only `fx_hp_through`, `fx_refund` and `fx_trace_add`, which land on HUD rows | effects, section 8 | `WavesFxOverlay` (second slot) | (new) |
| 15 | YOU strip, hand, SEND IT and UNDO, nameplate | atlas sprites plus Labels | `WavesHand` restyled, `SendItSticker` reused | |
| 16 | Lifted-card print, p2b hover tag box | shader plus code | (part of z15 and z12) | |
| 17 | Transitions T5/T6 | section 10 | `WavesTransitionFx` | `PageTransition` hook |

All of these are views. They read `WavesState`, `WavesForecast` and the session's previews, and emit signals up to `WavesFight`. None of them changes game state (rule 4). Keep `WavesSpinner` as the facade that owns `hit_test`, `sector_at` and the three signals, so `WavesFight` keeps working. Its `_draw()` body moves into the child layers above.

---

## 2. Geometry (plate px at 1080p, board centre C = (536, 540); angle 0 = 12 o'clock, clockwise)

| Element | Value | Source |
|---|---|---|
| Tower page (paper) / key ring / pink halo | r 189.2 / 192.0 / 197.2 (halo jagged ±1.5 px, segments 7-15 px) | `lw_tower` R_PAPER, R_KEY, R_HALO |
| Tower hub / HP ring / wedges / icon seat centre / pips | hub r 46; HP ring r 52-64; wedge r 71-177, half-angle 26°; icon at r 120 (48 px); pips at r 167 (8 px) | `xf_tower`, `f1_tower` |
| Icon seat: disc / paper ring / key ring / hatch clearance | r 28.6 / 31.0 / 33.6 / 37.0 | `lw_tower` SEAT_* |
| Ring 0 (NOW) / ring 1 (+1) / ring 2 (+2) | r 214-271 / 271-328 / 328-385 | final NOTES |
| Ring value per depth (glass) | 1.00 / 0.80 / 0.62 | `f1_board.VAL` |
| Schedule band | r 391-417; marks stay inside `BAND_EDGE` = 388 | `r2_misc` |
| Bezel lips | r 389.4 and 420.6 | `lw_skin` |
| Sector digits | r 386.5, boss r 14.3; angles -4.5, 60, 120, 180, 240, 300; hole = boss + 2.6 px | `r2_sched` |
| Landing lanes | r 436, 453, 470 | `f1_render` |
| Rim / crests | r 489-500; 6 crests at r 494.5, 30° + 60k | `lw_skin.rim_vector` |
| Hand | CARD_SCALE 1.10, step 168, left card centre x 1035, y 904, fan 4°, hover push 16, lift 1.10 at y 866 (slot-0 lift: fan +32 px, LIFT_CY 906). The p2 play lift sits 24 px left at y 812 and pushes 16. No hand pixel inside r 455, and the lowest hand pixel is at least 12 px above y 1080 (2026-11-03 stage 2, review 2.7; was x 1023, y 924). | `f1_hand`, `rb2_patch` |
| Card | design 176 x 250, chamfer 16, art band (8,8)-(168,126), icon centre (88,66); canvas margin 18 | `card_render` |
| Hover tag box | (1092, 404) | `a2_hover` |

**Rotation.** `WavesSpinner._ang()` already puts sector 0 at the top with angles running clockwise, matching the plates. Use the same convention, and ±30° per sector edge.

---

## 3. Colour tokens (`CombatLookData`)

Create one new Resource, `scripts/data/combat_look_data.gd`, stored at `content/config/combat_look.tres`. It replaces `WavesLookData` behind the flag `waves_art_on` (default false) until the designer signs off. Game-mark colours live **here, never in a corp skin** (section 7 asserts this).

| Token | Hex | Meaning |
|---|---|---|
| `player_pink` (CELL_PINK) | #FF3DA8 | Player-owned: tower halo, guns, resolve marks, D effects, the lifted-card print |
| `toner` (ink) | #15121A | Key lines, hatch keyline |
| `sheet` (paper) / `white` | #F2EEE4 / #FBFAF4 | Copier paper / glyph white |
| `harm` (enemy hit, hatch) | #FF4433 | Red hatch = the enemy hits you |
| `harm_up` (threat marks, HOT) | #FF6452 | Chevrons and arcs HOT |
| `harm_cold` / `harm_far` | #D9877C / #96767A | COLD / FAR threat marks (lifted; `f1_board`) |
| `enamel` HOT / COLD / FAR | #D9E1EA / #9DA0A5 / #73757A | Enemy cell outline, by time grade |
| `soak` | #3A7EF3 | Blue hatch = soaked |
| `gain` | #7BE07B | Gains, the clear wash |
| `net_cyan` | #5CE1FF | RAM coin only |
| `trace_violet` | #A03CFF | Trace only (card tab, Trace pips, S glitch) |
| `boss_gold` | #D69A1A (2026-11-03 re-pick; was #FFC428) | Ward and boss |
| `plan_yellow` | #FFE200 | Hover and plan pencil (preview form only) |
| `focus_lime` | #D4FF00 | Hover focus corners (2 px legal, 3.5 px aimed) |
| `amber` | #FFB000 | HOLD plates, Adjuster arc |
| `tape_lo` / `tape_hi` | #76808E / #E8EEF4 (drawn colours in 4.4) | Neutral THIS TURN tape, the same on every corp |
| Slice inks BURST / SHIELD / TURRET / REPAIR | fill #F06EAE / #5E9BE0 / #AEB24E / #3FB59A; texture ink #9E2A66 / #234E8C / #5A5E1A / #1D6656 (2026-11-04: the rebuild's L* 60-72 inks, TURRET moved off BOSS_GOLD by gate 1; the O-29 #FF3DA8 / #2A58F0 / #FFD21F / #4BD67E are retired) | `corp/src/rb_tokens.py` `SLICE_INK` / `SLICE_TEX` |
| `cream_hp` | #DBD1B7 (2026-11-04) | Enemy HP ticks on the board (CREAM at L* 84) |
| `k_type` | #CBD2DB (2026-11-04) | K type: sector digits, ring tags, W tags, ticket glyphs, nowords tallies (L* 84, no glow) |
| `hit_paper` | #DED8CA (2026-11-04) | Gun hit star fill and tracer highlight (was `white` #FBFAF4) |
| `plan_badge` | `plan_yellow` x 0.86 (2026-11-04) | The twist badge (its edge read L* 97 at full PLAN) |
| `steel_hi` | #C4CBD8 (2026-11-04; was #E2E9F6) | The armour rail's top edge on enemy HP trays |
| `cream_faded` | #FFF4D6 | HP ticks of hover-faded units only (p2b; faded to 38 % alpha they keep reading as one segment) |
| `best_neutral` | `TEXT_HI` #F2F6FF type, `TEXT_MID` #AFC0D6 edge, filled star (2026-11-04, review 3.8) | BEST LINE chip, best and selected option chips; never `plan_yellow` |
| Card type TOWER / WAVE | #006E66 (dark #00403B, text white) / #B4AAFF (dark #5E50C4, text ink); 2026-11-03 rebuild, dE76 >= 15 from every meaning token and slice ink | `card_render.TYPES` |

**Time grade function** (`gramlib.grade`, used for every graded mark). For COLD and FAR, the threat red is overridden by the lifted colours above.
- `k = 0` (HOT): the colour as is.
- `k = 1` (COLD): saturation 0.45, value 0.70.
- `k = 2` (FAR): saturation 0.25, value 0.50.
- Formula: `g = lum + (c - lum) * sat`, then `out = bed + (g - bed) * val`, with `bed` = #070912 and `lum` = Rec709.

Bake these into the resource as three colours per mark. Do not compute them per frame.

---

## 4. Element families

Each family lists: **S** (shader), **T** (texture or sprite), **C** (code-drawn), and **N** (the node it maps onto).

### 4.1 Room backdrop and grade (step 6; rb2-1 since 2026-11-03 stage 2)
- **2026-11-03 stage 2 (review 2.8):** the grade is now rb2-1 (`corp/src/bd_grade.py`; `backdrop/grade.json` version rb2-1, with every room plus the `shop_meridian` corp variant). The baked-texture path (T) below is still the recommendation. Bake with rb2-1, one PNG per room plus `room_shop_meridian_graded.png`. The skin picks the room: neutral and Solace use bio, Meridian uses the shop (`bd_grade.CORP_ROOM`). The shader below is the **step6-1** version. If the shader path is taken, it needs the rb2-1 steps from grade.json `order`:
  - the box hull: a polygon SDF texture baked once, `m = 1 - smoothstep(-pf0, pf1, sdf)`;
  - a three-tap blur ramp (LOD for 0.4 / 1.6 / 4 px) on that SDF;
  - the corp light hue pull;
  - `city_chroma`;
  - the local tone (gain from a blurred-luma mip, about 14 px, capped at `tone_gmax`, weighted by `m + tone_out * (1 - m) * reach`);
  - the spill haze (`haze` → `haze_out` by m; colour `spill_rgb` → `haze_rgb` by `smoothstep(sp0, sp1, d)`).
  The acceptance is per plate on the rendered frame: room region mean L* 28-34, and p95 at least 1 below the ring-NOW occupied glass p95 (L* 40 when no ring-NOW cell is live). The room region is x ≥ 1100, y ≥ 420, r > 505, with the UI, the hand, the hover tag and the UI scrim slabs (where they darken the room by 15 % or more) cut out. Measured on the 15 final plates: mean L* 31.2-32.2, p95 37.5-38.1.
- **T, recommended:** bake each graded room offline with `D:/rc_scratch/combat_redesign/locked/backdrop/src/bd_grade.py` and the parameters in `backdrop/grade.json`. That gives 7 PNGs at 1920x1080, `res://assets/backdrops/combat_v3/room_<bio|srv|gh|rec|lobby|event|shop>_graded.png`. Bake the board scrim into the same image, because the board centre is fixed.
  - Keep the bare rooms (`combat_backdrop/v3_1/room_<n>_bare.png`) as well. T5 crossfades bare to graded (section 10).
  - Runtime cost: one texture.
- **S, for rooms not yet baked and for tuning:** `shaders/combat/room_grade.gdshader`, a canvas_item shader on the room TextureRect. It runs on sRGB-encoded values; in Godot 4 canvas textures arrive as sRGB, so no conversion is needed.
  ```glsl
  shader_type canvas_item;
  uniform vec4 hull = vec4(1500.0, 600.0, 330.0, 270.0);   // cx, cy, rx, ry (plate px)
  uniform vec2 hull_f = vec2(0.85, 1.55);
  uniform float hull_blur_lod = 0.0;   // 0.4 px: no blur needed
  uniform float city_blur_lod = 2.6;   // ~4 px gaussian via mip LOD (texture needs mipmaps)
  uniform float chroma = 0.876;        // per room, grade.json
  uniform float neon_chroma = 0.8;
  uniform float pink_chroma = 0.55;    // event 0.42
  uniform float contrast = 1.12;       // event 1.24
  uniform float pivot = 0.16;
  uniform float hull_value = 0.466;    // per room
  uniform float city_value = 0.55;
  uniform float knee = 0.18;
  uniform float ceil_ = 0.30;          // event 0.32
  uniform float vignette = 0.30;
  uniform vec2 vig_d = vec2(0.9, 2.6);
  uniform float board_falloff = 0.30;
  uniform vec2 board_x = vec2(700.0, 1250.0);
  uniform float grade_mix = 1.0;       // T5: 0 = bare room, 1 = graded
  uniform vec2 plate_size = vec2(1920.0, 1080.0);
  vec3 rgb2hsv(vec3 c){ vec4 K=vec4(0.,-1./3.,2./3.,-1.); vec4 p=mix(vec4(c.bg,K.wz),vec4(c.gb,K.xy),step(c.b,c.g));
    vec4 q=mix(vec4(p.xyw,c.r),vec4(c.r,p.yzx),step(p.x,c.r)); float d=q.x-min(q.w,q.y); return vec3(abs(q.z+(q.w-q.y)/(6.*d+1e-10)),d/(q.x+1e-10),q.x); }
  void fragment(){
    vec2 px = UV * plate_size;
    float d = length((px - hull.xy) / hull.zw);
    float m = 1.0 - smoothstep(hull_f.x, hull_f.y, d);                       // 1 inside the hull
    vec3 c = mix(textureLod(TEXTURE, UV, city_blur_lod).rgb, textureLod(TEXTURE, UV, hull_blur_lod).rgb, m);
    vec3 src = c;
    vec3 hsv = rgb2hsv(c); float hue = hsv.x * 360.0;
    float neon = smoothstep(.35,.60,hsv.y) * smoothstep(.35,.65,hsv.z);
    float pink = smoothstep(296.,308.,hue) * (1. - smoothstep(345.,358.,hue)) * smoothstep(.18,.35,hsv.y);
    float k = chroma * (1. - (1. - neon_chroma) * neon) * (1. - (1. - pink_chroma) * pink);
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    c = l + (c - l) * k;                                                        // 3 chroma
    c = pivot + (c - pivot) * contrast;                                         // 4 contrast
    c *= hull_value * m + city_value * (1. - m);                                // 5 value
    l = max(dot(c, vec3(0.2126, 0.7152, 0.0722)), 1e-5);                        // 6 shoulder
    if (l > knee) { float l2 = knee + (ceil_ - knee) * (1. - exp(-(l - knee) / (ceil_ - knee))); c *= l2 / l; }
    c *= (1. - vignette * smoothstep(vig_d.x, vig_d.y, d)) * (1. - board_falloff * (1. - smoothstep(board_x.x, board_x.y, px.x)));  // 8
    COLOR = vec4(mix(src, clamp(c, 0., 1.), grade_mix), 1.0);
  }
  ```
  - The scrim runs after the grade: a 6 px frosted pool weighted `1 - smoothstep(300, 520, r)`, then SCRIM #02030A at `0.55 * (1 - smoothstep(330, 560, r))`, with r measured from (536, 540). In the shader version, sample the blurred pool at mip LOD 3.
  - Haze is 0 in every room, so it is dropped from the shader.
- **N:** `CombatBackdrop` keeps choosing the room (`BackdropCatalog.place_for`). The art pass adds the `room_<n>` → graded-texture lookup and the per-room uniforms, read from a `RoomGradeData` resource array that mirrors `grade.json`.
- **Test hook:** with the shader on `room_bio_bare.png`, the mean absolute error against the baked PNG is at most 3/255, allowing for the mip blur. The room squint (section 13) has mean 0.125-0.145, p95 at most 0.25, and 0 loud cells.

### 4.2 HUD (system layer)
- **C/N:** `WavesHud` and the bill restyle as the cyan terminal: TBG #050D1C, THI #F2F6FF, TMID #AFC0D6, TLO #7A889C, at G = px0 1072 to px1 1896.
- Not a shader job. The panels use the existing `crt_terminal.gdshader` and `ui_panel_shadows.gdshader` look if wanted.
- The HUD is the same on every corp skin.

### 4.3 Corp rings: the enemy layer (skin data, section 7)
- **S:** `shaders/combat/corp_ring.gdshader`, one canvas_item shader on the ring-band meshes (cells, bezel, annulus, arcframe). The vertex shader passes plate px; the fragment shader computes `rho` and `theta`, the same polar frame as `cs_skin.polar`.
  - The uniforms come from the skin's ShaderMaterials (section 7).
  - Each material function becomes "over" accumulation of `(colour, alpha)` layers, exactly as `cs_skin.Acc` does:
    ```glsl
    vec4 over(vec4 acc, vec3 col, float a){ float oa = a + acc.a * (1. - a); return vec4((col * a + acc.rgb * acc.a * (1. - a)) / max(oa, 1e-6), oa); }
    ```
  - Voronoi (Solace membranes and bubbles) uses an integer-hash jittered grid, 3x3 neighbourhood, F1 and F2, at `vor_pitch`. Pixel identity with SciPy's cKDTree is not required; matching the pitch and the contrast is.
  - Meridian ribs: `rib = 0.5 + 0.5 * cos(2π * radians(mod(theta + 30, 60)) * rmid / pitch)`, with `rmid = 214 + 57 * depth + 28.5`.
- **Kind wash (unit cells):**
  - The four unit-kind washes are the base colour under the cell material.
  - They are **baked per skin** from `kind_gain`: a Lab push away from the mean of the four kinds, applied before the material.
  - The exact results are in `port/skin_tables.json` (`kind_wash[skin][kind][ring]`).
  - Compute them once per skin swap in `CorpKindWash.compute(gains)` (pure, `RefCounted`), never per frame.
- **T (bake once per corp with PIL; corp-specific vector pieces):**
  - the rim strip;
  - 6 crests;
  - the token frame and disc frame;
  - the ticket 9-patch.

  See section 6.3.
- **C:** each cell's edge line (`cell_detail`) is a 1.0-1.3 px polyline in the skin's `cell_edge` colour at alpha 120-150.
- **N:** `CorpRingLayer` and `UnitCellLayer` replace `_draw_rings` and the fill and outline in `_draw_unit`. `WavesSpinner._band()` geometry gives way to section 2's radii.
- **Never touched by a skin:** the THIS TURN tape, HP, hatch, HOT/COLD/FAR, outlines, PLAN yellow, focus lime and pink.

### 4.4 Schedule band, THIS TURN tape, HOLD plates (time grammar)
- **C:** flat colours, drawn directly in silver.
  - The generator draws orange and remaps it (`lw_skin.NeutralTape.remap`): `colour = lo + (hi - lo) * clamp((v - 0.30) / 0.70)`, with lo #76808E (118,128,142), hi #E8EEF4 (232,238,244), and v the HSV value of the original orange.
  - Pre-computed values:

| Tape part | Generator orange | Silver (use this) |
|---|---|---|
| LIVE_FILL (inner panel, carries the ink text) | (200, 98, 22) | **#C5CCD5** |
| LIVE_EDGE (outer band) | (176, 84, 18) | **#B6BDC7** |
| SCHEDULE (full value) | (255, 140, 26) | **#E8EEF4** |
| LIVE_LIP | (255, 176, 80) | **none:** the edge is the solid ink keyline only (a 1 px lip broke into a dotted line once silvered) |

- HOLD plates and the Adjuster arc keep amber #FFB000. On Meridian a black gap of at least 2 px separates them from the hazard paint; the bezel inner lip is black (section 7).
- Digits draw on their own layer above everything on the board. Each digit **punches a hole** of boss r + 2.6 px in the tape/plate layer and the label layer: draw the digit's disc with `BLEND_MODE_SUB` alpha, or use a stencil-like mask Control. Digit 0 sits at -4.5°.
- **N:** `ScheduleBand` and `BoardDigits` take the printed rotation from `WavesStepStrip`'s data (this END TURN's step, next, the one after). The SET dial buttons stay a UI Control (section 0.2, Hold is OPEN).

### 4.5 Board game marks (time grammar, arcs, tickets), code-drawn
All of these are **C**, drawn immediately in `_draw()` the way `WavesSpinner` already does, using `draw_polyline` and `draw_colored_polygon`, **never** `draw_dashed_line` (a test greps for it, section 13). Hatch regions use the hatch shader (5.1) through a child CanvasItem.

| Mark | Spec |
|---|---|
| Enemy cell outline | Ink keyline (4.0, or 3.0 on ring 2) + 4.5 px, then the enamel line by grade: HOT 4.0 px with a soft glow (blur 4, 40 %); COLD 2.6; FAR 2.0. Solid at every depth. Marker: an end notch on HOT, 1 or 2 pips on COLD and FAR. One graphite enamel; no outline colours by kind. |
| Threat chevrons | `harm_up` HOT, `harm_cold`, `harm_far`. Solid = landing hit; hollow = growth (`land_hit` > `hit`). |
| Landing arcs | Bezel arc over the landing sectors on lanes 436/453/470. Red diamonds = HP through per sector. k dots = turns ahead. Soak and clamp marks. |
| Pending-loss hatch on enemy HP trays | **Pink** cross-hatch = our hits (shader 5.1, cause = `player_pink`); the cream ticks stay. |
| Ring tags (NOW W1, +1 W2, +2 W3) | Pulled inward until the corner clears r 388. |
| W4-W6 tickets | The corp `ticket` 9-patch plus a Jammer/Packet glyph row (`WavesLineupStrip` data). |
| Arrowed outline | **Movement only.** The yellow PLAN arrow in hover, pink at resolve. One shared `ArrowOutline.draw(ci, pts, col, w)` helper, also used by the M effects. |
| Badges (ward and others) | Never on the band: shrink or flip until the band overlap is 0 (draw assert, section 13). |
| Sector-3 chevron column and rim landing marks | As drawn on `final/grammar_check.jpg`. |

- **N:** `BoardMarkLayer` replaces `_draw_pips`, `_draw_chevrons`, `_draw_barrier`, `_draw_landings`, `_draw_trigger_path`, `_draw_scorch` and `_draw_orbit`.
- Keep a **draw log** (`Array[Dictionary]` of `{cls, rect, unit, sector}`) for the draw asserts and the collision test, the way the generator's `DASH_LOG`, `BADGE_LOG` and `ASSERT_LOG` work.

### 4.6 Tower: the player spinner (xerox spot inks, linocut key, scissor halo, Ben-Day on TURRET)
- **T:** bake the static art per slice type, from `lw_tower`. Section 6.1 has the sheet list.
  - The page, halo, key and paper, with the margin marks.
  - Each wedge body: key plate + paper sliver + off-register spot ink at FILL_K 0.84 + texture at TEX_K 0.90 + stencil highlight.
  - Each O-28 icon seat: the slice-ink disc (full ink), the paper scissor ring and the key ring.
  - Each slice icon glyph: white, with the key and the drop.
  - The hub starburst and paper disc, without the name.
- **S:**
  - the pending-loss hatch per slice (5.1, cause red or blue);
  - the drop shadow of the whole tower, as an offset silhouette (5.6; (3, 5) px, blur 7, alpha 0.55);
  - the xerox grain on code-drawn player marks (5.4).
- **C, game marks that change:**
  - the HP ring (r 52-64) and its states;
  - pips (r 167);
  - the brace plate (`draw_brace_plate`) and soak mark (`draw_soak_mark`);
  - the trim;
  - the name tile text "BREAKER": a Label in Anton 15.5 px, white, rotated -2°, on an ink tile 58 x 17 with a pink offset of (1.6, 1.8).
- **Pending loss** (`lw_tower.draw_break_state`): when `hp > 0` and `hp_after == 0`:
  - darken the wedge by toner at 0.26;
  - hatch it at 45° and 135°, pitch 6.4, line 1.6, with an ink keyline grown 0.85 at alpha 0.92, then the cause colour on top;
  - draw a 2.4 px edge in the cause colour;
  - draw a 7 px stencil X at (r 155, angle +17°);
  - keep the hatch outside r 37 round the icon, so the seat carries the type (O-28).
- **N:** `TowerView` replaces `_draw_tower`. During a spin (`fx_spin`), the whole `TowerView` rotates; the baked lit edges rotate with it for 680 ms, which is accepted. At rest it snaps to the 6 baked sector sprites.

### 4.7 Guns (player pink marker)
- **C:** Line2D ribbons in `player_pink` with an ink key (a second, wider Line2D underneath) and xerox grain (5.4).
- Opacity: full at decide, 0.58 as the p2 preview, full at resolve. On p2b they are dimmed by `DIM_K` 0.38.
- **N:** a new `GunLayer` under the landing arcs. Data comes from the `fire` events of the previewed END TURN.

### 4.8 Hand and cards (WPAP)
- **T:** a card art atlas baked from `card_render` with every text call removed (section 6.2, proven): the plates stay and the words go.
  - A second small atlas holds the PLAYED liner frames (outline plus glyph).
- **C, Labels over the art** (fonts already in `assets/fonts/`). Coordinates are card design px:

| Text | Font, size, style | Anchor (design px) | Rotation |
|---|---|---|---|
| Title | Anton 38 px, fit down to at least 30.5 px in 128 px; white fill; ink outline 1.4; pink shadow offset (2.6, 3.0) | (87.5, 144.5) | -2.0° |
| Type word | Anton 19 px, tracking 2.2, colour `TYPES.text` | (85.5, 174.4) | -1.2° |
| Rules | IBM Plex Sans Condensed Medium 21 px, never shrunk (2026-11-03 stage 2, check c: cap height 16.2 px at 1.10). One line if it is 124 px or narrower, else two lines broken at the word gap that gives the narrowest widest line ("Turn the / tower 3", "Turn one / ring 1", "Pause / the wave"); ink | one line (80, 206); two lines (80, 200) and (80, 221.5) | -0.8° |
| Rules underline | Pink skew bar under the last line, width = that line + 10 (draw it in Godot; the proof bake still has the generator's bar, see 6.2) | one line y +11.5..+18.5; two lines y +13..+20 below the last line | |
| Cost | Anton 27 px, ink, on the cyan hex | (21.5, 22.2) | |
| +Trace | Anton 21 px, white, on the violet tab | (CW-43, 17.6) | |
| Multiplier | Anton 30 px, `TYPES.text`, on the type-colour plate | (139, 107) | -3° |
| PLAYED liner | Share Tech Mono 21 px, tracking 1.0, `PAPER` at 62 % (name) and 74 % (PLAYED), on the torn dark liner (#15121A at 86 %, paper rim 2.2 px at 62 %, ghost glyph at 46 % centred (88, 111)); the slot is upright, never fanned (2026-11-03 stage 2, review 2.3) | (88, 157), (88, 183) | 0° |

- **S:** `card_state.gdshader` on the card sprite (5.5), covering normal, rest dim (`REST_V` 0.88), unaffordable, and the hover-lift print.
- **N:** `WavesHand` keeps its signals (`card_pressed`, `card_hovered`) and fixed slots. Its buttons become `TextureRect` (atlas region) + Labels, in the fan from section 2. The old `CardFace` sticker is not used for Waves cards.

### 4.9 SEND IT, UNDO, nameplate, YOU strip
- **T/C:** SEND IT is the paper sticker from the plates (`lw_ui`). Reuse `SendItSticker` with a paper-and-ink style, or bake the plate art and draw the words as Labels. UNDO and the hint line stay terminal (system family).
- The YOU strip is 15 HP blocks in 3 x 5, taped onto the HUD. Hatch: blue = soak, pink = us, red = enemy (5.1). Since 2026-11-03 stage 2 (review 3.14), the blocks are 13.6 x 22 px at a 16.4 px pitch, with an 8 px group gap. The hatch is two-direction at a 5.4 px pitch with 1.5 px lines (`rb2_patch` YOU_*).
- **Bill (2026-11-03 stage 2, review 1.5 / 3.7):** the game's numbers are Labels: Anton 24, or 22 on the NEXT row and the chain. Each is followed by a small pip tally sprite. The operators are Anton 40 Labels (−, +, =), centred on their ink. SPLIT reads ABSORBED + SOAK + YOU. The NEXT row is at 70 % value with COLD tallies (`gramlib.grade` k = 1). WITHOUT TWIST shows "a → b" as digits. Heat is the atlas Heat glyph (`ATLAS_BURN`) tinted `CRT_AMBER`. REFUND is a terminal tab under the refunded RAM coin. The waves-left count shows once, as the header chip.

---

## 5. Shaders (uniforms and maths)

All the maths is in plate px. Pass `plate_px = VERTEX` (local, in plate units) from `vertex()` as a varying. Antialiasing uses `fwidth`.

### 5.1 `pending_loss_hatch.gdshader` (the L7 grammar: HP lost at this END TURN)
Used on tower slices, enemy HP trays and the YOU strip. **The hatch colour is the cause:** red #FF4433 for an enemy hit, blue #3A7EF3 for a soak, pink #FF3DA8 for the player's hits. Effects never add hatch; they resolve it (section 8).
```glsl
shader_type canvas_item;
#include "res://shaders/combat/rc_print.gdshaderinc"
uniform vec4 cause : source_color = vec4(1.0, 0.267, 0.2, 1.0);
uniform vec4 ink : source_color = vec4(0.082, 0.071, 0.102, 1.0);
uniform float pitch = 6.4;        // tower; HP trays use the same
uniform float line_w = 1.6;
uniform float key_grow = 0.85;    // ink keyline each side of the line
uniform float key_alpha = 0.92;
uniform float darken = 0.26;      // toner veil under the hatch (tower only; 0 on trays)
uniform vec2 seat = vec2(-1e5);   // icon seat centre (plate px); hatch cleared inside seat_clear
uniform float seat_clear = 37.0;
varying vec2 p;
void vertex(){ p = VERTEX; }
void fragment(){
  float clear = clamp((distance(p, seat) - seat_clear) * 1.5, 0.0, 1.0);
  float k = hatch_cov(p, pitch, 0.5 * line_w + key_grow);
  float h = hatch_cov(p, pitch, 0.5 * line_w);
  vec4 c = vec4(ink.rgb, darken * clear);
  c = mix(c, vec4(ink.rgb, 1.0), k * key_alpha * clear);
  c = mix(c, vec4(cause.rgb, 1.0), h * clear);
  COLOR = vec4(c.rgb, c.a * COLOR.a);
}
```
`rc_print.gdshaderinc` (shared):
```glsl
float aa(float sd){ float w = max(fwidth(sd), 1e-4); return clamp(0.5 - sd / w, 0.0, 1.0); }   // sd < 0 inside
float line_dist(vec2 p, float deg, float pitch){ float a = radians(deg); float s = dot(p, vec2(-sin(a), cos(a)));
  return abs(mod(s + 0.5 * pitch, pitch) - 0.5 * pitch); }
float hatch_cov(vec2 p, float pitch, float half_w){ return max(aa(line_dist(p, 45.0, pitch) - half_w), aa(line_dist(p, 135.0, pitch) - half_w)); }
// Ben-Day halftone (card_render.halftone): dot area = coverage, radius capped at 0.72 of the cell
float benday(vec2 p, float pitch, float deg, float cov, vec2 o){ float a = radians(deg); vec2 q = p - o;
  vec2 uv = vec2(q.x * cos(a) + q.y * sin(a), -q.x * sin(a) + q.y * cos(a)) / pitch;
  float r = min(sqrt(clamp(cov, 0.0, 1.0) / PI), 0.72); return aa((length(fract(uv) - 0.5) - r) * pitch); }
// tower textures (xf_slices / lw_tower), in the wedge frame (u along the spoke, v across) unless noted
float tex_dots(vec2 uv){ float p = 10.0, r = 3.3; vec2 a = uv - p * round(uv / p); vec2 b = (uv - p*0.5) - p * round((uv - p*0.5) / p);
  return aa(min(length(a), length(b)) - r); }                                   // BURST
float tex_rings(vec2 q_from_icon){ float p = 9.0, w = 2.8; float d = length(q_from_icon);
  return aa(abs(mod(d + p * 0.5, p) - p * 0.5) - w * 0.5); }                    // TURRET Ben-Day bullseye
float tex_plus(vec2 uv){ float p = 20.0, hl = 6.6, ht = 2.1; float best = 99.0;
  for (int i = 0; i < 2; i++){ vec2 o = vec2(float(i)) * p * 0.5; vec2 x = (uv - o) - p * round((uv - o) / p);
    best = min(best, min(max(abs(x.x) - hl, abs(x.y) - ht), max(abs(x.x) - ht, abs(x.y) - hl))); } return aa(best); }  // REPAIR
// SHIELD scales (r 8.6, lw 1.9) are only baked (6.1); they are not needed at runtime.
// X-only halftone (H family): an X per staggered pitch cell, half-size = pitch * 0.5 * density
float x_halftone(vec2 p, float pitch, float dens, float w){ if (dens < 0.06) return 0.0;
  float row = round(p.y / pitch); float xo = 0.5 * pitch * mod(row, 2.0);        // odd rows offset half a pitch (fxk_lib.grid_X)
  vec2 c = vec2(round((p.x - xo) / pitch) * pitch + xo, row * pitch);
  vec2 d = abs(p - c); float s = pitch * 0.5 * clamp(dens, 0.0, 1.0);
  float diag = abs(d.x - d.y) * 0.7071; return aa(diag - 0.5 * w) * step(max(d.x, d.y), s); }
```

### 5.2 `hover_dim.gdshader` (section 9)
A full-board post over z0-z11. Its inputs are a screen texture and a lit mask, drawn white by the hover controller into a SubViewport at 1/2 resolution.
- Outside the lit mask: `rgb → (g + (rgb - g) * desat) * k`, with `g = 0.30 R + 0.59 G + 0.11 B`, `k` = 0.40 and `desat` = 0.45.
- The mask is blurred 1.1 px. In the shader, take 5 taps at LOD 0.5.
- Uniforms: `lit_mask : sampler2D`, `k = 0.40`, `desat = 0.45`, `on = 0..1` (tweened in 120 ms, ease-out).

### 5.3 `corp_ring.gdshader` (4.3)
- Uniforms: `material_kind` (0 ENAMEL_LINES, 1 MEMBRANE, 2 RIBS) plus the per-material parameters listed with the skins in section 7.
- One shader is used for the cell, bezel, annulus and arcframe parts. A `part` int selects the formula, a straight port of each `cs_skin` or `lw_skin` function.

### 5.4 `xerox_grain.gdshaderinc`: toner dropout and speckle (player marks drawn at runtime)
The baked art already carries its grain. This include is for code-drawn player marks: guns, resolve marks, hover pencil and D effects.
```glsl
uniform sampler2D grain_noise : filter_linear, repeat_enable;  // FastNoiseLite value noise, static (no TIME): 512 px tile
float dropout(vec2 p, float amount){ float n = texture(grain_noise, p / 512.0).r; float n2 = texture(grain_noise, p / 2560.0 + 0.37).r;
  return clamp((n - (1.0 - amount * 1.3)) * 9.0, 0.0, 1.0) * clamp(0.6 + n2, 0.4, 1.0); }
// ink alpha *= 1.0 - 0.85 * dropout(p, 0.07..0.11)     (xf_gfx.ink: grain 0.07 on marks, 0.11 on wedge fills)
float speck(vec2 p, float thr){ return step(thr, texture(grain_noise, p / (1.1 * 512.0) + 0.71).r); }   // toner_noise, thr 0.80-0.90
```
The grain is static: it must never animate, or it flickers.

### 5.5 `card_state.gdshader` (one material on every hand card)
- Uniforms: `mode` (0 normal, 1 hover, 2 unaffordable), `dim` (value multiplier; rest 0.88), `print_offset = vec2(-9, 6)` and `shadow_offset = vec2(7, 11)` in design px, scaled to the sprite.
- **Hover:**
  - a pink #FF3DA8 silhouette at `print_offset`;
  - a #08060E shadow at 55 % at `shadow_offset`;
  - both sampled from the sprite alpha at the offset UV, under the card.
- **Unaffordable** (`card_render._unaffordable`):
  - `g` = the mean of RGB;
  - `rgb = (g + (rgb - g) * 0.40) * 0.55 + (8, 6, 14) * 0.45`;
  - plus two glass bands on `u = (x + 0.55 y) / W`: 0.42-0.62 at +10 % toward white, and 0.70-0.76 at +8 %;
  - the cost badge keeps its colour (it is the reason), so pass its rect as an exclusion uniform;
  - over the glass, at full value (`card_render.unaffordable_marks`, 2026-11-03, AD review 3.3): a "NO RAM" tab running out from
    under the cost badge (ink plate #1C1830, design rect `NO_RAM_TAB` 32-91 x 10-30, visible from x 42.5; Anton 15.5 design px in
    #5CE1FF), the badge redrawn on top, and a padlock (scale 1.15) on the badge's lower-right edge, body centre +17.5, +21 design px
    from the badge centre. nowords keeps the badge and the padlock only. These are sprites on the card, not shader work.

### 5.6 `offset_print.gdshader` (drop shadows and halos, by silhouette offset)
- Samples the alpha at `UV - offset / size`, blurred by mip LOD.
- Used for:
  - the tower drop: (3, 5), blur 7, alpha 0.55, #08060E;
  - the lifted-card shadow;
  - the D-family ink keys.
- The pink scissor halo of the tower is **baked** (6.1). It is not this shader.

### 5.7 `glitch_s.gdshader` (S family: `fx_trace_add`)
- Bands of rows (`rows[i] = (y, h, shift)`, 3 bands per step) shift by ±6 px.
- R and B split by ±3 px.
- Tint `0.65 * c + 0.35 * #A03CFF`; every second row ×0.72 (scanlines).
- Steps of 33 ms, with new rows at every step (seeded per step, so no pixel flickers twice).
- Uniforms: `band_y[3]`, `band_h[3]`, `band_shift[3]` and `region`, set by the effect from a seeded `RandomNumberGenerator` (seed = effect id hash + step). This is a view, so the game `RngService` is not involved, but never use the global `randf`.

### 5.8 `x_flood.gdshader` (H family)
- `x_halftone(p, pitch 6.5, dens, w 1.5)` in `harm` red, with a misregistration offset of (1.6, 1.2) on the second plate.
- The density rolls in from `r_hi` to `front_r`: `dens * (0.55 + 0.45 * k)`.
- The icon seat stays clear (seat r + 3).
- Uniforms: `front_r`, `r_hi`, `dens`, `seat`, `center`.

### 5.9 Not shaders, on purpose
- **WPAP facets:** baked in the card art (32 % type colour, 28 % type dark, 25 % white glint, 0.7 px ink cut edges).
- **Spin arcs:** baked.
- **Pink halo:** baked.
- **Room scrim:** baked, with the shader as fallback.
- **Ben-Day on cards:** baked.

A runtime shader would only add cost for static art.

---

## 6. Textures and sprite sheets (baked from the PIL generator)

All bakes import the locked generator read-only from `D:/rc_scratch/combat_redesign/locked/corp/src`, one process per skin (the skin installs at import). They write to their own folder; they never write into `corp/work`. Import settings in Godot: **Lossless, mipmaps on, filter linear**.

### 6.1 Tower sheets (player layer, the same on every corp)

| File | Size | Layout | Bake |
|---|---|---|---|
| `tower_page.png` | 940 x 940 | Halo, key ring, paper disc and margin marks; centre (470, 470) | `lw_tower.page(cv, seed)` + `margin_marks` on `Cv(0, 0, 470, 470, S=6)`, downsampled to 2x |
| `tower_wedges.png` | 6 x 4 cells of 288 x 288 | Row = type (BURST, SHIELD, TURRET, REPAIR); column = sector 0-5. Each cell is the wedge body with its key, drop, spot ink, texture and highlight, cropped to the wedge bbox at 2x; the pivot offset goes in json. | `lw_tower.draw_wedge` per type and sector, on an empty canvas |
| `tower_seats.png` | 4 cells of 160 x 160 | O-28 seat per type (disc, paper ring, key, misprint) | `lw_tower.draw_seat` |
| `tower_icons.png` | 7 cells of 128 x 128 | Slice glyph per game slice kind (white, key, drop) | `lw_tower.draw_icon` with `icon_masks` |
| `tower_hub.png` | 256 x 256 | Starburst, key and paper disc with the bolt; no name tile text | `lw_tower.draw_hub(cv, name='')`, plus the empty tile |
| `tower_sheets.json` | | Cell rects, pivots (the tower centre in each cell), sector angles | |

- The baked wedges have no hatch, HP, pips, brace or soak. Those are game marks (4.6).
- The pending-loss X and edge are code; the hatch is the shader.
- **This bake is specified, not run in this pass.** The card bake below was run.

### 6.2 Card atlas (proof run in this pass)
- **Bake:** `port/src/bake_cards.py`. It monkeypatches `card_render.text` to return an empty mask, so every plate, tab, facet, icon and drop stays and every word goes. It calls `draw_card(name, 352, 'normal')` for the 11 cards in `card_render.ORDER`.
- **Result:**
  - `cards_art_atlas.png`, 1696 x 1716: 4 x 3 cells of **424 x 572** (the card is 352 wide, 2.0x design, plus a 36 px margin each side). It is in scratch, at `D:/rc_scratch/combat_redesign/locked/port/work/`.
  - `cards_ref_atlas.png`: the worded reference.
  - `port/cards_atlas.json`: cell rects, card fields and text anchors in cell px.
  - `port/cards_proof.jpg`.
  - About 1 min 47 s for both atlases.
- **Looked at** (`cards_proof.jpg`): every art card keeps its type plate, title plate, cost hex, Trace tab and multiplier plate with no words, and the icons and facets match the worded card exactly.
  - **One fix for the real bake:** the pink rules underline is drawn from the text width, so it stays in the art layer at the English width. Add a `bake_art_only` flag to `card_render.render_base` that skips that bar, and draw it in Godot from the label width (4.8).
- On screen at 1.10 the card is 193.6 px wide, so the atlas is about 1.8x screen: sharp at 1440p and mipmapped at 720p.
- **Also bake:**
  - `cards_liner_atlas.png`: the PLAYED frame and glyph per card (`_liner` without text), same cells.
  - `cards_nowords_atlas.png` only if a no-words mode ships (`state='nowords'`).
- **Game card ids:** the atlas key is the game id (`spin2` and so on). The open rows in 0.2 (Firewall/scorch, Hold, bug) need art before their cells exist.

### 6.3 Corp skin sheets (one set per corp: `neutral`, `solace`, `meridian`)

| File | Size | Bake |
|---|---|---|
| `corp_<id>_rim.png` | 6144 x 48: a polar strip, x = angle 0-360° clockwise from 12 o'clock, y = r 489 to 500 at 2x (plus 13 px of keyline padding). Drawn on a ring mesh with UV.x = theta / 360. Solace: 71 helix turns (integer, so it closes); Meridian: 311 hazard stripes; neutral: degree ticks. | Evaluate `skin.rim(X, Y, RHO, TH)` on a polar grid, then draw `rim_vector` without the crests. One numpy unwrap script. |
| `corp_<id>_crest.png` | 64 x 64 | `skin.crest(L, 32, 32, s=1.25 * 2)` |
| `corp_<id>_token_frame.png` | 96 x 96 (R 30 at 1x, at 2x) | `skin.token_frame` |
| `corp_<id>_disc_frame.png` | 48 x 48 | `skin.disc_frame` |
| `corp_<id>_ticket.png` | 96 x 64 plus 9-patch margins 8 / 8 / 8 / 8 | `skin.ticket(L, box, nearest=True)`; also a `_dim` variant (nearest=False). Meridian's barcode and rivets sit in the right and top margin cells. |

The cell, bezel, annulus and arcframe materials are **shaders** (5.3), not textures. They cover large polar areas, and the voronoi and ribs are cheap to compute.

### 6.4 Effect sprites

| File | Size | Use |
|---|---|---|
| `fx_krackle.png` | 4 cells of 256 x 256 | H krackle (black cracks with a red 2 px offset), rotated per slice |
| `fx_stencil_x.png` | 64 x 64 | H red stencil X |
| `fx_shards.png` | 8 cells of 48 x 48 | D flat shards (pink, paper, ink); H plate shards are cut at runtime from the plate polygon |
| `fx_plus_sparkle.png` | 2 cells of 48 x 48 | L plus sign and four-point sparkle (mint, GAIN) |
| `fx_check.png` | 96 x 96 | L clear check stamp |
| `fx_bone_plate.png` | 9-patch, 128 x 64 | P bone card #F1EAD6, 3.4 px ink key, pink double line, rivets |
| `fx_brace_stamp.png` | 128 x 64 | P brace stamp |
| `fx_shutter_<id>.png` | 9-patch, 64 x 64 | C corp shutter slab lip per corp (steel straight, porcelain lime round, stencil oxide notched) |

Starbursts, tracers, speed lines, ribbons and arrows are **C**: Polygon2D or Line2D with width curves, keyed in ink.

---

## 7. Corp skin data format (Godot Resource)

`scripts/data/combat_corp_skin.gd`. It is read-only at runtime (rule 3), and every value is data (rule 5).
```gdscript
class_name CombatCorpSkin
extends Resource
## One corporation's enemy-layer look on the combat board (colour + material, O-27). Game marks are NOT here:
## the THIS TURN tape, HP, hatch, HOT/COLD/FAR, outlines, PLAN yellow, focus lime and player pink live in CombatLookData.

enum CellMaterial { ENAMEL_LINES, MEMBRANE, RIBS }

@export var id: StringName = &"neutral"
## Cell, bezel, annulus and arcframe materials: ShaderMaterials on corp_ring.gdshader, uniforms filled per corp.
@export var cell_material: ShaderMaterial
@export var bezel_material: ShaderMaterial
@export var annulus_material: ShaderMaterial
@export var arcframe_material: ShaderMaterial
@export var material_kind: CellMaterial = CellMaterial.ENAMEL_LINES
## Unit-kind wash separation per ring (Lab push away from the four-kind mean, before the material). Baked once per swap.
@export var kind_gain: PackedFloat32Array = PackedFloat32Array([1.0, 1.0, 1.0])
## Vector pieces, baked from the PIL generator (GODOT_PORT_SPEC 6.3).
@export var rim_texture: Texture2D
@export var crest_texture: Texture2D
@export var crest_count: int = 6
@export var crest_angle0_deg: float = 30.0
@export var crest_radius: float = 494.5
@export var token_frame_texture: Texture2D
@export var disc_frame_texture: Texture2D
@export var ticket_style: StyleBoxTexture
@export var ticket_style_dim: StyleBoxTexture
## Code-drawn colours.
@export var cell_edge: Color = Color(0.4275, 0.4549, 0.4941, 0.47)   # cell_detail polyline
@export var cell_edge_w: float = 1.0
@export var frame: Color = Color(0.3216, 0.3608, 0.4078, 1)          # token / disc frame fill (fallback when no texture)
@export var frame_groove: Color = Color(0.0314, 0.0353, 0.0471, 1)   # the ink groove against the lane ring
## Effects: the C-family shutter slab and lip (corp acting), and the M-family "corp moves it" echo tint.
@export var shutter_slab: Color = Color(0.7373, 0.7843, 0.8392, 1)
@export var shutter_lip: Color = Color(0.7373, 0.7843, 0.8392, 1)
@export var shutter_lip_shape: StringName = &"straight"            # straight | round | notched
@export var motion_tint: Color = Color(0.3569, 0.3961, 0.4510, 1)   # graphite enamel on neutral
## Transitions (T5/T6 bits FX): no skin field. 2026-11-04 (review 3.12): bits_rings and bits_accent are retired; each bit reads
## the colour of its source from the board (section 10, "Bit colour"; ART_BIBLE 1.2).
## Meridian's stencilled numbers on empty cells (hook exists, art not drawn yet).
@export var empty_marks: bool = false

## Error codes of a bad value (empty when valid).
func validate() -> PackedStringArray:
	var e := PackedStringArray()
	if kind_gain.size() != 3: e.append("corp_skin: kind_gain needs 3 rings")
	for g in kind_gain:
		if g < 0.5 or g > 3.0: e.append("corp_skin: kind_gain range")
	if crest_count < 0: e.append("corp_skin: crest_count")
	return e
```

**`corp_ring.gdshader` uniforms per corp.** The cell part is shown; the bezel, annulus and arcframe parts follow the same `cs_skin` and `lw_skin` functions line by line.

| Uniform | Neutral | Solace | Meridian |
|---|---|---|---|
| `material_kind` | 0 ENAMEL_LINES | 1 MEMBRANE | 2 RIBS |
| `tint` / `tint_alpha` / `tint_ring_lift` | panel #283240 / 0.30 / 0 | glass #14462E / 0.40 / 0.06 (per ring fraction) | oxide #964C1A / 0.34 / 0 |
| Pattern A | index lines every 10°, panel_hi #6E7C8E at 0.07; rings every 9.5 px at 0.05 | membranes: voronoi pitch 30, `1 - ss(0, 1.5, F2 - F1)` glass_hi #60D26E at 0.13; wall `1 - ss(1.5, 4.2)` at 0.04 | ribs pitch 6.5 px: trough #140C08 `(1 - rib)^2 * 0.17`, ridge #FFCE96 `rib^3 * 0.075` |
| Pattern B | | nucleus `1 - ss(2.6, 4.0, F1)` #E278A0 at 0.34 on 1 cell in 5 (pink demoted to rose under glass); other cells glass_hi at 0.05 within F1 < 6.5 | scuffs: blurred noise `ss(1.2, 2.4, n)` #100A08 at 0.10 (static noise texture) |
| Pattern C | | bubbles: voronoi pitch 44, radius 3 + (id·131 mod 7), 1 in 3: ring pale #ECF8E2 at 0.16, spec white at 0.20 | |
| Gloss `cos(theta - 315)^2` | #EBF2FA at 0.05 | #DCFFDC at 0.07 | (none) |
| Bezel | base #161B22, panel at 0.45 + 0.25 sin(πu), brushed rings, lips in line #BCC8D6 at 0.55 | base #102E22, glass, membranes pitch 26 at 0.14, porcelain lips | base #221C18, steel #463E38, ribs pitch 5.0; **inner lip black #140F0C, no stripe** (the O-29 gap to amber); outer lip hazard stripes 283 per turn in hazard paint at 0.85 |
| Hazard paint | | | #E6903B = #FF8C1A with 25 % chroma cut toward its own luma (`HAZ_DESAT`) |
| Annulus / arcframe | #080B10 at 0.55 / #1A212A at 0.55 | #081A14 at 0.55 + membranes / #103024 at 0.55 + membranes pitch 18 | #1A1410 at 0.55 + ribs 7.0 / #28180E at 0.55 + ribs 5.0 |

**The three `.tres` files** (`content/combat/skins/<id>.tres`). Only the fields that differ from the defaults are shown:
```
# content/combat/skins/solace.tres
[gd_resource type="Resource" script_class="CombatCorpSkin" load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/data/combat_corp_skin.gd" id="1"]
[resource]
script = ExtResource("1")
id = &"solace"
material_kind = 1
kind_gain = PackedFloat32Array(2.4, 2.1, 2.0)
crest_count = 6
cell_edge = Color(0.3961, 0.6431, 0.3333, 0.59)          # mixc(edge #96EC78, (10,30,20), 0.35), alpha 150
cell_edge_w = 1.3
frame = Color(0.6902, 0.7608, 0.6706, 1)                 # porcelain glaze #B0C2AB
frame_groove = Color(0.0314, 0.0863, 0.0627, 1)          # #081610
shutter_slab = Color(0.8863, 0.9333, 0.8471, 1)          # porcelain #E2EED8
shutter_lip = Color(0.5882, 0.9255, 0.4706, 1)           # lime #96EC78
shutter_lip_shape = &"round"
motion_tint = Color(0.5882, 1.0, 0.2745, 1)              # Solace lime #96FF46 (the wave moves it)
# + cell_material / bezel_material / annulus_material / arcframe_material (ShaderMaterial sub-resources, uniforms per the table)
# + rim_texture (71 helix turns), crest (porcelain roundel, lime helix S), token_frame (porcelain ring, lime dot at 12), ticket (chamfered lab slide)
porcelain = Color(0.7216, 0.8627, 0.8, 1)               # 2026-11-04 (gate 1): celadon #B8DCCC, the board's porcelain ink (bezel lip, rim,
                                                         # crest roundel, token frames, tickets); was #E6EFE4, dE76 4.7 from PAPER.
# NOT YET CHANGED: shutter_slab above still carries the old porcelain #E2EED8 (dE76 under 15 from PAPER). It belongs to the effects
# (C family), which were not re-rendered in gate 1; it takes #B8DCCC when they are (locked/final/NOTES.md). The T5/T6 part is done:
# bits_accent is retired (2026-11-04), and the bits read the board, whose porcelain is already #B8DCCC.

# content/combat/skins/meridian.tres   (Meridian stays hibernated in the slice, A-112: a palette proof that the swap works)
id = &"meridian"
material_kind = 2
kind_gain = PackedFloat32Array(1.0, 1.1, 1.2)
cell_edge = Color(0.5882, 0.3373, 0.1098, 0.59)          # mixc(edge #E08028, (12,8,6), 0.35)
cell_edge_w = 1.3
frame = Color(0.6784, 0.3686, 0.0745, 1)                 # container octagon #AD5E13
frame_groove = Color(0.0392, 0.0314, 0.0275, 1)          # #0A0807
shutter_slab = Color(0.9255, 0.8392, 0.698, 1)           # stencil paint #ECD6B2
shutter_lip = Color(0.8784, 0.502, 0.1569, 1)            # oxide edge #E08028
shutter_lip_shape = &"notched"
motion_tint = Color(1.0, 0.549, 0.102, 1)                # Meridian orange #FF8C1A
empty_marks = true                                       # stencilled container numbers: hook only, art not drawn
# rim: 311 hazard stripes, crest crane-A, token_frame steel octagon with 4 corner castings, ticket square-cut shipping tag with barcode

# content/combat/skins/neutral.tres
id = &"neutral"
material_kind = 0
kind_gain = PackedFloat32Array(1.0, 1.0, 1.0)
cell_edge = Color(0.4275, 0.4549, 0.4941, 0.47)          # mixc(line #BCC8D6, (12,14,18), 0.45), alpha 120
frame = Color(0.3216, 0.3608, 0.4078, 1)                 # #525C68
shutter_slab = Color(0.7373, 0.7843, 0.8392, 1)          # steel (188,200,214)
shutter_lip_shape = &"straight"
# rim: degree ticks on steel #748090, crest: dark roundel with pale ring and bar
```
- **Selecting the skin.** The fight's corp (`WavesState.node` / netrun site → corporation id) picks `content/combat/skins/<id>.tres`. Neutral is the fallback.
- **Swapping at runtime:** set the four ShaderMaterials, rebuild the kind wash, and swap the five textures. The game marks do not change.
- **The tape is not a skin field.** `CombatLookData` holds the tape colours (4.4). A test asserts that no skin field equals any game-mark token (section 13).

---

## 8. Effect timings as data

### 8.1 Resources
`port/fx_timings.json` holds 32 effects:
- 13 M/P/S/T: M motion 8, P protect 3, S system 1, T commit 1;
- 19 C/D/H/L: C 2, D 7, H 7, L 3.

Each entry has: `id`, `family`, `title`, `skins`, `total_ms`, `phases[{name, start_ms, end_ms, ease, ease_raw}]`, `keyframes_ms`, `reduce_motion`, `source`, `max_flashes_per_s` (full) and `reduce_max_flashes_per_s`. Import it into Resources:
```gdscript
class_name CombatFxPhase extends Resource
@export var name: StringName
@export var start_ms: int
@export var end_ms: int
@export var ease: StringName        # LINEAR, IN_QUAD, IN_CUBIC, OUT_CUBIC, IN_OUT_CUBIC, OUT_BACK, IN_OUT_SINE, STEP, HOLD

class_name CombatFxTiming extends Resource
@export var id: StringName
@export var family: StringName      # M P C D H L S T
@export var total_ms: int
@export var phases: Array[CombatFxPhase] = []
@export var reduce_phases: Array[CombatFxPhase] = []   # authored from the reduce_motion text (8.3)
@export var tier: int = 2            # VfxTier: T1 feedback for P/S, T2 outcome for C/D/H/L/M, T3 for kill, rings_step and commit
@export var flash_events_ms: PackedInt32Array = PackedInt32Array()   # the frames counted as flashes, for FlashLimiter
```
Store them in `content/combat/fx/fx_timings.tres`, with one sub-resource per effect. A tool script, `tools/import_fx_timings.gd` (headless, build-side), turns the JSON into the `.tres` so the numbers are never retyped.

**Ease codes** map to a Godot Tween `(TRANS, EASE)` pair, or to a sampled curve:

| Code | Godot |
|---|---|
| `IN_OUT_CUBIC` | `TRANS_CUBIC`, `EASE_IN_OUT` |
| `OUT_CUBIC` | `TRANS_CUBIC`, `EASE_OUT` |
| `IN_CUBIC` | `TRANS_CUBIC`, `EASE_IN` |
| `IN_QUAD` | `TRANS_QUAD`, `EASE_IN` |
| `IN_OUT_SINE` | `TRANS_SINE`, `EASE_IN_OUT` |
| `OUT_BACK` | `TRANS_BACK`, `EASE_OUT`. The raw strings `easeOutBack 2.0` and `2.2` give the overshoot. Godot's back uses s = 1.70158, so for 2.0 and 2.2 sample `1 + (s + 1)(t - 1)^3 + s(t - 1)^2` in a Curve. |
| `STEP` | Hold the value, then jump. `ease_raw` "step 33 ms" or "step 40 ms" sets the quantum. |
| `HOLD` | Nothing moves (a hold phase) |
| `LINEAR` | `TRANS_LINEAR` |

Two raw strings carry extra motion and need a hand-built curve:
- `easeOutCubic + 2 deg wobble`;
- `step 40 ms / easeOutCubic`.

### 8.2 Runtime rules
- **Slot:** `WavesFxOverlay`, above the board and HUD and below the hand and UI. To draw above the hand, the effect asks for the top slot explicitly; no current effect does.
- **Sequencing on the resolve beat:**
  - Effects never overlap within one 100 ms window. They run in the VISUAL_PLAN G layer order: GUNS (`fire`), then LANDS (`land`, the H family), then RINGS STEP, then W4 enters.
  - The flash checks are per effect (at most 2 flashes per second on its own); the combined sequence was not measured. The sequencer therefore leaves at least 100 ms between the flash windows of consecutive effects.
  - Every flash also goes through `FlashLimiter.request()` (3 per second, `Settings.flash_limiter`).
- **Reduce motion:** when `Settings.reduce_motion` is set, play `reduce_phases`. Every reduce form drops echoes, travel, overshoot, sparks and glitch steps; state changes become 260-300 ms dissolves.
- **Determinism:** effects are views. Their random bits (shards, sparks, glitch rows, the bits FX) use a local `RandomNumberGenerator` seeded from `hash(effect_id, unit_id, sector)`. That keeps headless captures stable. Never use the global `randf` (rule 2 in spirit).
- **The post-state comes from the game.** An effect ends on the next `WavesState` drawn by the board, never on a painted end frame. Examples: the grow chevron, the empty cell after a kill, the ward. That is the same rule the art followed (real generator renders as post-states).

### 8.3 Event to effect map (game-v2 event types)
These are the types found in `scripts/core/waves_*.gd`. Rows marked *infer* come from the played action, not an event.

| Source | Effect(s) |
|---|---|
| play `Spin2`, `Spin3`, `Nudge` (*infer*) | `fx_spin` (turn = amount x 60°, plus a 3° settle) |
| play `Twist` | `fx_twist` |
| play `Pull` / `Shove` (blocked) | `fx_pull` / `fx_shove` (`fx_shove_bump`; its HP rule is OPEN, see effects NOTES_MPST caveat 2) |
| play `Brace` | `fx_brace_block` at resolve when the braced landing stops |
| play `Trigger` | `fx_trace_add` (Trace +N), then at resolve `trigger_unit` / `trigger_tower` → `fx_trigger_hit`, and a kill → `fx_kill` |
| play `Strike` | `fx_strike`, and a kill → `fx_kill` |
| `scorch` | `fx_firewall_burn` (pending the Firewall/scorch answer, 0.2) |
| `fire` (target id ≥ 0) | `fx_gun_hit`; a kill → `fx_kill`; armour → `fx_ricochet`; warded → `fx_ricochet_gold` |
| `land` (`blocked` > 0 on a SHIELD slice) | `fx_shield_block` |
| `land` (soaked > 0) | `fx_soak_take` |
| `land` (HP through) | `fx_hit_land` (`_worm` and `_adjuster` variants by kind); slice to 0 → `fx_slice_break`; slice cracked → `fx_slice_crack`; shield plate lost → `fx_shield_break`; run HP → `fx_hp_through` |
| `repair` | `fx_repair_mend` |
| `refund` | `fx_refund` |
| end_turn: schedule step | `fx_rings_step`; `fx_hold` when the step is held (SET 0, pending 0.2) |
| wave enters ring +2 | `fx_wave_enter` |
| unit `growth` +1 | `fx_grow` |
| ward on | `fx_ward_on` |
| unit leaves the landing arc with no HP lost | `fx_clear` |
| SEND IT / END TURN pressed | `fx_commit` |

The full table (phases, reduce motion, flashes) is in Appendix A. It is generated from `port/fx_timings.json`.

### 8.4 Family looks (what each draws; must keep)
- **M motion:**
  - print echoes at 26, 52 and 78 ms (9, 18 and 27 ms on the fast tower), tinted 25 % toward the mover's colour;
  - an echo shows only where it differs from the current frame;
  - movers: pink = a card at resolve, silver = the clock (at r 426, never on the tape), the corp colour = the wave.
  - In Godot: keep a ring buffer of the last 5 transforms and draw the moving layer's texture 3 extra times with modulate.
- **P protect:** the bone plate 9-patch, flat tints (pink 18 % for a block, SOAK 16 %), white spark ticks. No starburst, no red, no glow.
- **S system:** the glitch shader (5.7).
- **T commit:**
  - pencil yellow becomes pink along each mark in route order, white-hot 2 frames deep: a Line2D gradient whose offset is tweened along a per-mark distance-along-path;
  - then a pink ping at the route end.
- **C corp:** the flat shutter slab in the corp's frame colour with a hard 2 px lip (skin fields), and one 4-frame flat flash. Ward uses boss gold.
- **D damage:** a pink tapered ribbon tracer with an ink key, an ink-keyed pink starburst with a white core, converging white speed lines, and flat shards. No Ben-Day.
- **H harm:**
  - the X-halftone flood (5.8);
  - black krackle with a red 2 px offset (sprites);
  - the red stencil X;
  - slice-wide, with the icon seat (r 37) clear except on shield_break and slice_break.
- **L life:** the only soft glow, with additive blend and small radius:
  - brush ribbons, plus signs and sparkles;
  - mint #D6FFCE with an ink key on the green REPAIR wedge;
  - the RAM coin in NET_CYAN.
- **No family** draws dashed or dotted lines (trails are one continuous tapered ribbon), uses the needle, or adds cross-hatch.

---

## 9. Hover dimming (11 hover plates, `hover/`)

| Part | Value |
|---|---|
| Dim outside the lit mask | value x 0.40, chroma x 0.45 (5.2) |
| Dimmed unit layer, guns on p2b | alpha x `DIM_K` 0.38 |
| Hand not in play | modulate value 0.70 |
| UNDO, SEND IT, nameplate | modulate value 0.62 |
| Focus | Lime #D4FF00 corners only: 2 px for a legal target, 3.5 px for the aimed one. A corner slides up to 12° inward if it would touch a digit, label, tag, badge or ticket. |
| PLAN arrow | Yellow #FFE200 arrowed outline, movement only: tower turn, Shove, Pull, Trigger path, Twist ring, Hold step |
| Ghost | The sim's plan units, drawn by the board's own unit and arc code at 74 %, with a pencil outline; the origin is veiled. Never a shifted copy. |
| Pencil ring | On every number the plan changes: LANDS/THROUGH, the YOU pips that change, spent RAM coins, added TRACE pips (square) |
| Burst | Only on a hit that removes HP, beside the token, never on it |
| Lifted card | Lift 1.10 at y 866 with the pink print (5.5). Slot 0: the fan shifts right 32 px and the lift sits at 906, so no hand pixel enters r 455. |
| Re-top | Digits, labels, tags, badges, tickets, the tape and the label plates draw back on top of the hover marks (with the dim applied where they fall outside the lit mask) |

- **Lit mask:** the hover controller (in `WavesFight`, from the hovered card's legal actions and the session preview) draws the lit polygons into a SubViewport. The polygons are the target cells, the slices, the path and the landing sectors.
- **Tweens:** dim on in 120 ms (OUT_CUBIC) and off in 90 ms. The hover tag box sits at (1092, 404).
- **N:** this replaces `WavesSpinner._draw_hover` and `_draw_targets`. `WavesFight._on_card_hovered` and `_set_hover_action` already compute the preview (`previews_checked`); they feed `targets`, `focus_target`, the ghost state and the lit mask.

---

## 10. T5 / T6 bits FX (`transitions/`)

What T5 and T6 show is the designer's ruling DR-10 (`VISUAL_PLAN.md`, ART CALL 49 items 5 and 6). How a bit looks is ART_BIBLE 1.2 (LOCKED). Option A (O-25) is inked 0/1 glyph bits, each band behind a keyline head that reveals its ring. **2026-11-04 rebuild (review 1.7, 3.12): every value is at 1080p** (the earlier table was at the 960 px GIF scale and is retired). Board centre C = (536, 540); rim r 500. Source: `transitions/scripts/fx3.py`, `fx3lib.py`; the numbers are in `transitions/metrics.json`.

| Part | T5, room to combat (1.2 s) | T6, combat to netrun (0.8 s) |
|---|---|---|
| Room | Starts on the bare room (`room_<n>_bare.png`), which is T4's last frame. `grade_mix = smoothstep((t - 0.25) / 0.75)` takes it to the graded room with the board scrim (4.1) by 1.00 s. The HUD scrim slides down from 80 px above and fades in over 1.05-1.16 s (OUT_CUBIC) | The reverse: `grade_mix = 1 - smoothstep((t - 0.12) / 0.62)`, ending on the bare room as T4 left it. The HUD scrim moves up 48 px and fades over 0-0.20 s (IN_CUBIC) |
| Spinner (`tower` layer) | Flies in from 0.25 s over 0.30 s: scale 1.35 → 1.0 (OUT_CUBIC) with the storyboard's 4 % overshoot (`- 0.04 sin(π clamp((u - 0.55) / 0.45))`; the O-25 code had 1.4 %), rotation 7° → 0, alpha `clamp(u * 2.2)`. One 90 ms pink (#FF3DA8) keyline snap round the halo at 0.56 s: r 216 (+6 → 0 px), 10 px ink with a 4 px core, alpha 150 | Eaten from 0.26 s over 0.22 s (IN_OUT_CUBIC) by a pink keyline at r 200 (18 px ink, 9 px core), 0.9 rad long. The tower's drop shadow goes with the same sweep. Its 40 bits read the slice inks (Bit colour) |
| Ring reveal | 4 bands: ring NOW r < 271, ring +1 271-328, ring +2 328-385, frame band 385-508. Head path r 242 / 300 / 356 / 408; start 0.56 / 0.61 / 0.66 / 0.71 s; direction +, -, +, -; 0.28 s IN_OUT_CUBIC; the head runs 0 → TAU + 0.9 rad from PHI0 = -90° + 0.10 rad; reveal `clamp((head - delta - 0.35) / 0.5)`, where delta is the pixel's swept angle from PHI0. The head is a 16 px INK keyline with a 6.4 px core, 1 rad long, with a 6 px dot | Starts 0.22 / 0.16 / 0.10 / 0.04 s (frame band first), 0.26 s each; keep `1 - clamp((head - delta) / 0.5)`; the head is 0.9 rad long |
| Bits | 54 / 70 / 86 / 96 per band, plus 30 for the W4-W6 tickets (landing at 0.86-0.98 s). Each lands on a random point of its band (r 222-263 / 279-320 / 336-377 / 394-494) as the head passes its angle. It leaves the room 0.18 + 0.12 \|d\| / π s earlier, where d is the shorter angle round the rim. Size 16 → 28 px in flight (IN_OUT_CUBIC), alpha 0.85 (fade-in 30 ms); after landing 28 → 0 px while fading over 0.12 s | 40 spinner bits (r 40-186) plus the same band counts and the 30 ticket bits. Each leaves its point as the head passes and drains to the room over 0.22 + 0.12 \|d\| / π s; all are home by 0.70 s. Size 28 → 16 px; alpha 0.85, fading over the last 20 % |
| Bit look (ART_BIBLE 1.2) | Share Tech Mono `0`, `1`, `10` or `01` with a same-colour outline of 1/22 of the size. White-hot `HIT_PAPER` #DED8CA for the first 80 ms (smoothstep to the bit's colour). Flips 0 ↔ 1 every 70 ms. Tumbles at 200-600 °/s (either sign), settling to 0 as it lands | same; no settle |
| Bit colour (review 3.12) | Read once, at transition start, from the board at the bit's landing point. Over a 9 px disc of the layer it belongs to, take the pixel at the 90th percentile of C*ab, then hold its L* in 55-80 with a* and b* kept. Rings and frame band read the board without the tower and guns; ticket bits read the ticket layer; card bits read their card (start points only where C*ab ≥ 20). **No skin colour field:** the colour comes with the skin's board | Read at the bit's start point, the same way; spinner bits read the tower layer |
| Route (1.2: round the rim, never across a wheel face) | From a source point in the room (4 centres in the bio lab: (1420, 560), (1560, 610), (1330, 650), (1640, 660), jittered), in to an orbit at r 506-532, round the rim the shorter way, then straight in along the target's radius. Inside r 492 a bit moves only radially | The same path backwards |
| Keylines, ghosts, lock | A band's head keyline, its ghost and its lock arc take the median colour of its bits (Lab median, L* at least 60). Ghost: one solid 6 px INK line with a 2.4 px core round the head path, alpha 120, from 0.28 s `smoothstep((t - 0.28) / 0.2)`, gone as its band ends. Never dashed. Lock at 1.00 s ±45 ms: one 10 px arc per band (4 px core), alpha 150, closing 6 px → 0 (the 90 ms lock) | Head keylines in the band colour; the spinner's in pink |
| Guns | Arm `smoothstep((t - 0.98) / 0.12)` | Fade `1 - smoothstep(t / 0.12)` |
| HUD / cards / SEND IT | The HUD and YOU strip come from 80 px above at 1.05 s, the nameplate from 80 px left at 1.07 s, each over 0.11 s (OUT_CUBIC). Cards deal from 180 px below at 1.05 + 0.03 i s over 0.09 s, each with a trail of 9 of its own bits. SEND IT and UNDO come from 100 px below at 1.11 s over 0.09 s. Input opens at 1.20 s | HUD, nameplate and SEND IT move 60 % of the same offsets and fade over 0.20 s (IN_CUBIC, 20 ms stagger). Each card drops 80 px and fades over 0.20 s (20 ms stagger), shedding 26 of its own bits, which fall 280 px |
| Keylines | INK #0C0A16; no glow, no bloom | same |
| FAIL branch | | netrun_fail design A (O-26): the glitch-in of `transitions/netrun_fail/scripts/nf_trans.py` on the board (row offsets and chroma split, never brighter) 0-0.20 s, a hard cut at 0.20 s, the panel opens at 0.30 s, input at 0.60 s |

- **S:** `shaders/combat/ring_reveal.gdshader`, with uniforms `center`, `band_r[5]`, `band_head[4]` + `core_head`, `band_dir[5]` and `phi0`. It masks the CorpRingLayer, ScheduleBand and BoardMarkLayer during the transition.
- **Particles:** a CPU draw through the existing `BitPath` + `BitsSeam` with `bits_atlas.png` (Share Tech Mono) and `binary_bits.gdshader`; this is the easiest to keep deterministic. The bit layout (landing points, sources, glyphs, flip phase, spin) comes from a cosmetic `RngService` stream. Each bit's colour is read from the board's layer textures at transition start (`Image.get_pixel` over the 9 px disc, the percentile and the clamp as above), about 700 reads.
- **N:** `WavesTransitionFx`, started from `RunManager.go_to_waves_fight()` / `WavesScene._ready` (T5) and `leave_waves_fight()` (T6). The source points are per room, as data next to the room in `BackdropCatalog`.
- **Flash** (CIE L*, `transitions/metrics.json`, both skins). 0 whole-frame flashes in T5 and T6 (O-25 rel10 and WCAG 2.x). The worst 120 px tile is at 3 in any 1 s (rel10), which is the limit, and 0 by WCAG. Frame mean L* runs 27.7-39.5 in T5 and 24.2-39.5 in T6. No frame is brighter than the plate.
- **Godot cost:** low to medium (O-25).
- **Not checked:** the srv and gh rooms (the source points sit in the bio lab). The T4-reverse pull-out inside T6 is not composited yet (`transitions/NOTES.md`, Not done).

---

## 11. Current node and script → new mapping (summary)

| Current | Becomes | Notes |
|---|---|---|
| `WavesLookData` + `waves_look.tres` | `CombatLookData` + `combat_look.tres` (flag `waves_art_on`) | Placeholder look kept as the fallback until sign-off |
| `WavesSpinner._draw_rings` | `CorpRingLayer` (corp_ring shader, skin) | |
| `WavesSpinner._draw_unit`, `_draw_pips`, `_draw_chevrons`, `_draw_barrier` | `UnitCellLayer` + `BoardMarkLayer` | Kind wash from `CorpKindWash` |
| `WavesSpinner._draw_tower` | `TowerView` (sprites + hatch shader + marks) | Brace, soak and ghost slices as game marks |
| `WavesSpinner._draw_landings`, `_draw_trigger_path`, `_draw_scorch`, `_draw_orbit`, `_draw_ward_column` | `BoardMarkLayer` | |
| `WavesSpinner._draw_targets`, `_draw_hover` | `HoverDimLayer` + `HoverMarkLayer` | |
| `WavesSpinner` signals, `hit_test`, `sector_at` | Unchanged (facade) | Hit radii from section 2 |
| `WavesStepStrip` | `ScheduleBand` on the board + the SET dial Control | Hold is OPEN |
| `WavesLineupStrip` | Ring tags + W4-W6 tickets | |
| `WavesHand` | Atlas card sprites + Labels + `card_state` shader | Signals unchanged |
| `WavesHud` | Cyan terminal HUD, bill, YOU strip | |
| (none) | `GunLayer`, `WavesFxOverlay`, `WavesFxSequencer`, `WavesTransitionFx` | New views |
| `CombatBackdrop`, `BackdropCatalog` | + graded rooms + `room_grade` shader | |
| `FlashLimiter`, `VfxTier`, `Motion`, `Settings.reduce_motion` | Reused as they are | |
| `BitPath`, `BitsSeam`, `binary_bits.gdshader`, `bits_atlas.png` | Reused for T5/T6 | |
| `WavesFight` | Layout to full screen (drop `SIZE_PX` 1280x688); wires the hover lit mask and the sequencer | Logic unchanged |

---

## 12. Order of work

Each step ends green on the full suite, schema smoke and validate_content (CLAUDE.md).
1. **Data first:**
   - `CombatLookData`, `CombatCorpSkin` (3 `.tres`), and `CombatFxTiming` / `CombatFxPhase` with the JSON importer;
   - `CorpKindWash` (pure);
   - their tests (13.1);
   - schema smoke updated, and a DECISIONS entry for the new data classes (rule 8).
2. **Layout:** `WavesFight` goes full screen at 1080p plate coordinates × 2/3. `WavesSpinner` becomes a facade with empty child layers. Hit-test parity tests pass on the new radii.
3. **Room:** graded room textures plus the shader fallback.
4. **Corp rings:** the `corp_ring` shader for neutral, then Solace and Meridian; rim, crests, token frames and tickets; the kind wash.
5. **Schedule band:** silver tape, HOLD plates, digits with punched holes.
6. **Tower:** the sheet bake (6.1), `TowerView`, the hatch shader, HP ring, pips, brace and soak.
7. **Board marks:** the time grammar, landing arcs, chevrons, tags, tickets, and the arrowed outline helper. Add the draw log, the draw asserts and the collision test here.
8. **Hand and cards:** the atlas bake with `bake_art_only`, Labels, the `card_state` shader, the fan layout and the r 455 assert.
9. **HUD and YOU strip.**
10. **Hover:** the lit mask, the dim post, ghosts, pencil, the lifted card. The 11 hover states should match `hover/` plates h01-h11.
11. **Effects, in play-path order:**
    - T commit, M motion and P protect;
    - then D damage, H harm and L life;
    - then C corp and S system.

    The sequencer, FlashLimiter and reduce motion go in with the first family.
12. **T5 / T6.**
13. **Plate parity captures** (Movie Maker through `tools/run_windowed.py`) against `final/`, `hover/` and `backdrop/`, plus the squint metrics. The designer signs the look off before `waves_art_on` defaults to true.

Steps 3, 4 and 6 can run in parallel after step 2. Effects (11) need steps 4-8.

---

## 13. Test hooks

### 13.1 Unit tests (GUT, `tests/unit/`, each added to `tests/test_manifest.json` with its tier)

| Test script | Checks |
|---|---|
| `test_combat_look_data.gd` | `CombatLookData.validate()` is empty. The HOT/COLD/FAR colours equal `port/skin_tables.json` `time_grade`. The tape colours equal 4.4. |
| `test_combat_corp_skin.gd` | All 3 skins pass `validate()`. **No skin field equals a game-mark token** (tape, harm, harm_up, soak, pink, plan_yellow, focus_lime, enamel grades). Solace and Meridian `kind_gain` match 7. |
| `test_corp_kind_wash.gd` | `CorpKindWash.compute()` for each skin and ring equals `port/skin_tables.json` `kind_wash` to within 1/255 (golden). Min dE2000 per ring is at least the neutral value (6.8 / 4.3 / 2.3). |
| `test_combat_fx_timings.gd` | 32 effects load. Every phase has `0 <= start <= end <= total_ms`. Every effect has `reduce_phases`. `max_flashes_per_s <= 3`. `FlashLimiter.stream_is_safe(flash_events)` holds for each effect and for the sequenced resolve beat of the E10-like golden fight. |
| `test_waves_board_hit.gd` | `hit_test` and `sector_at` on the new radii match the old semantics (unit, slice, cell, Adjuster orbit) on fixture states |
| `test_waves_board_draw_asserts.gd` | From the draw log, for fixture states (`tests/fixtures/waves_golden`): chevrons solid/hollow = `hit` / growth; diamonds per sector = HP through; k dots = turns ahead; soak and clamp marks; hatch cause colours; pips match HP. The generator ran 63/63, 49/49 and 24/24 on its plates. |
| `test_waves_board_collisions.gd` | Mark rects (digits, labels, tags, badges, tickets, hover leader) do not overlap each other or the occluders (tape, HOLD and +N plates, hand). Badge vs band = 0. Hand min radius ≥ 455. The leader may cross the tape once. |
| `test_waves_no_dashes.gd` | A grep of `scripts/ui/waves*` and `shaders/combat/` finds no `draw_dashed_line` and no dotted helpers. The draw log has 0 dash entries. |
| `test_waves_preview_equals_result.gd` | Already present in spirit (`WavesFight.preview_mismatches` must stay 0). Extend it to hover ghosts: the ghost state equals the session's plan state. |
| `test_waves_hover_dim.gd` | With a lit mask, a dimmed pixel equals `(g + (c - g) * 0.45) * 0.40` within 2/255 (shader run through a SubViewport in headless with a dummy renderer; skip if no renderer). Hand modulate 0.70, UI modulate 0.62. |

### 13.2 Capture checks (windowed, through `python tools/run_windowed.py --log <file> -- <godot args>`, never a bare windowed godot)
- **Plate parity:** capture p1, p2, p2b and p3 on the neutral skin, and p1 and p2b on Solace (and Meridian as the proof), at 1920x1080, from a fixture that reproduces `state_e10.json`. Use these metrics; pixel identity is not expected:
  - squint (1/16 box downscale, 1 px blur, Rec709, loud above 0.38): mean, p95 and loud share within ±10 % of `final/checks.json`;
  - tower-zone loud share at most 50 % on p1 (p2/p3 are known at 57-58 %, a designer call);
  - pink share in the enemy zone r 214-500 at most 0.3 %.
- **Room:** room squint mean 0.125-0.145, p95 at most 0.25, loud 0; board/room ratio at least 1.55.
- **Effects:** per effect, record 60 fps frames and run the art's flash method. It is written up in `effects/NOTES_CDHL.md` and `NOTES_MPST.md`, and the Python meter is in `fx_cdhl/src/fxk_lib.flash_check`. The bar is at most 3 flashes per second, and both reduce-motion and full motion must pass.
- **Hover:** h01-h11 against `hover/checks.json`; lit/dim luma ratio 1.20-1.86.

---

## 14. Open questions and risks

1. **Names (0.2):** Jammer vs `glitch`, `halo`, Firewall vs `scorch`, the Hold card vs the SET dial, and the `bug` card have no settled art mapping. The designer or build must answer before those cells, cards and effects are wired.
2. **Shove bump HP:** round 2 said both units lose a tick. E10 has no such rule, so the effect draws no HP change (NOTES_MPST caveat 2). Game-v2's rule decides.
3. **Tower loudness on p2/p3:** 57.9 % and 57.5 %, against a 50 % target. A designer call (final NOTES).
4. **Latent effects** with no E10 source were drawn on stand-in marks: strike, the steel ricochet, firewall_burn, the hit_land Adjuster variant and repair_mend. Check them against real game numbers once wired.
5. **Combined resolve sequence:** never flash-measured as a whole. The sequencer spacing (8.2) plus `FlashLimiter` is the guard. Measure it in the capture check.
6. **Baked lit edges rotate during a spin** (4.6). This is accepted for the 680 ms turn. If it reads wrong, bake 12 rotation steps or move the highlight into a shader.
7. **Text in cards** is Godot Labels, so translation works. The proof bake shows that the art layer is word-free except for the pink underline, which is fixed with a flag (6.2).
8. **Meridian** stays hibernated (A-112). Its skin ships as a proof only. The stencilled numbers are not drawn.
9. **The tower sheet bake (6.1)** is specified but was not run in this pass.
10. **Game-v2 has moved** past `b09f9b9d`. Re-read the waves views at build's head before starting.

---

## Appendix A. Effect timings (generated from `port/fx_timings.json`)

| id | fam | total ms | phases (name start-end ease) | reduce motion | flashes/s full / reduce |
|---|---|---|---|---|---|
| `fx_hold` | M | 700 | stamp slams 0-140 OUT_BACK; band turns over 205 deg 140-560 IN_OUT_CUBIC; settle: stamp hands over to the pr 560-700 LINEAR | No stamp slam and no wipe: the arrow appears (100 ms) and the band dissolves to the new schedule over 260 ms. | 1 / 1 |
| `fx_pull` | M | 600 | anticipate: arrow draws 0-120 OUT_CUBIC; slide 59 px 120-480 IN_OUT_CUBIC; settle back 2 px 480-600 OUT_CUBIC | No echoes: arrow appears (100 ms), the cell dissolves from ring +2 to ring +1 over 260 ms, arrow fades. | 0 / 0 |
| `fx_rings_step` | M | 900 | anticipate: tape arrow draws, land 0-160 OUT_CUBIC; spiral: -57 px, +120 deg 160-760 IN_OUT_CUBIC; settle: arrow fades 760-900 LINEAR | No echoes, no spiral: the arrow appears (100 ms), every cell dissolves from its old place to its new one over 300 ms, the arrow fades. | 1 / 0 |
| `fx_shove` | M | 580 | anticipate: arrow draws 0-120 OUT_CUBIC; slide 62 deg 120-460 IN_OUT_CUBIC; settle back 2 deg 460-580 OUT_CUBIC | No echoes: arrow appears (100 ms), the cell dissolves into the next sector over 260 ms, arrow fades. | 1 / 0 |
| `fx_shove_bump` | M | 540 | anticipate: arrow draws 0-120 OUT_CUBIC; slide toward the edge 120-260 IN_QUAD; contact: bump line, starbursts, sh 260-400 OUT_CUBIC; spring back 260-440 OUT_CUBIC; arrow and bump line fade 440-540 LINEAR | No slide and no starbursts: the arrow and the white bump line on the shared edge appear for 440 ms and fade; the cell never moves. | 1 / 1 |
| `fx_spin` | M | 820 | anticipate: arrow draws, gun previ 0-140 OUT_CUBIC; turn 183 deg 140-680 IN_OUT_CUBIC; settle back 3 deg, arrow gone 680-820 OUT_CUBIC | No echoes, no arc sweep: the arrow appears whole (100 ms fade), the tower dissolves from 0 to 180 deg over 280 ms (easeInOut), the arrow fades out. Icons and hub as in full motion. | 1 / 1 |
| `fx_twist` | M | 660 | anticipate: arrows draw 0-120 OUT_CUBIC; turn 61.5 deg 120-540 IN_OUT_CUBIC; settle back 1.5 deg 540-660 OUT_CUBIC | No echoes: the arrows appear whole (100 ms), the ring dissolves from 0 to 60 deg over 260 ms, the arrows fade. | 1 / 0 |
| `fx_wave_enter` | M | 760 | feed arrow lights, ticket lifts 0-120 STEP; ticket rides into the entry 120-520 IN_OUT_CUBIC; cells scan in, glyphs drop 440-700 OUT_CUBIC; queue moves up one slot 560-760 IN_OUT_CUBIC | No travel and no echoes: the W4 ticket fades out, the new cells fade in with their outlines and glyphs, and W5 / W6 cross-fade one slot right, all over 300 ms. | 0 / 0 |
| `fx_brace_block` | P | 1060 | lane draws in 0-120 OUT_CUBIC; clamp closes (1.12 to 1.0) 80-240 OUT_BACK; chevrons run the lane 120-380 IN_QUAD; chevrons crumple on the bar 380-480 LINEAR; stamp slams on the arc 480-560 OUT_BACK; hold 560-900 HOLD; clamp, bar and lane lift off (stam 900-1060 LINEAR | No closing or crumple motion: lane, clamp, bar, the crumpled chevrons and the stamp fade in over 120 ms, hold, then everything but the stamp fades. | 1 / 2 |
| `fx_shield_block` | P | 920 | chevrons arrive 0-240 IN_QUAD; plate slams (1.25 to 1.0) 170-250 OUT_BACK; impact: stop dead, sparks 240-400 LINEAR; hold 400-760 HOLD; plate lifts off 760-920 LINEAR | No slam and no sparks: plate, tint, ticks and the two chevrons stopped at the plate edge fade in over 100 ms, hold, and fade out. | 1 / 2 |
| `fx_soak_take` | P | 960 | overflow chevron arrives 0-160 IN_QUAD; funnel draws in 120-300 OUT_CUBIC; chevron shrinks into the mouth 300-440 LINEAR; pip drains 440-600 OUT_CUBIC; hold, flow scrolls 600-800 LINEAR; funnel and wash lift off 800-960 LINEAR | No travel: funnel, wash and the filled pip fade in over 120 ms with the flow chevrons still, hold, fade out. The overflow chevron is not shown. | 0 / 1 |
| `fx_grow` | C | 650 | wipe 0-250 IN_OUT_CUBIC; flash 250-317 STEP; open 317-460 IN_OUT_CUBIC; ping 300-560 OUT_CUBIC | No shutter or ping: the hollow chevron fades in over 200 ms (ease-in-out). | 1 / 0 |
| `fx_ward_on` | C | 750 | pulse 0-220 IN_OUT_SINE; wipe 150-450 IN_OUT_CUBIC; flash 450-517 STEP; ping 470-700 OUT_CUBIC | No pulse, scan or flash: the lozenge fades in over 200 ms. | 2 / 0 |
| `fx_firewall_burn` | D | 1000 | ring0 0-200 LINEAR; ring1 130-330 LINEAR; ring2 260-460 LINEAR; ticks 330-330 LINEAR; embers 700-1000 LINEAR | All three bands appear at full height at once, no flicker, hold 500 ms, fade 300 ms. | 1 / 0 |
| `fx_gun_hit` | D | 600 | tracer 0-100 OUT_CUBIC; burst 100-170 OUT_BACK; speed_lines 100-280 IN_OUT_SINE; shards 120-460 OUT_CUBIC; tick 170-260 LINEAR; out 300-520 LINEAR | Tracer and burst appear at full size for 300 ms, then fade 200 ms; no speed lines, no shards; the tick goes gone on the same frame. | 1 / 0 |
| `fx_kill` | D | 600 | flare 17-50 STEP; burst 34-110 OUT_BACK; speed_lines 34-260 LINEAR; shards 60-560 OUT_CUBIC; empty 200-420 IN_OUT_CUBIC; out 330-560 LINEAR | No flare: a 25 % white tint holds on the cell for 200 ms while the burst shows; the cell empties with a 220 ms fade. | 1 / 0 |
| `fx_ricochet` | D | 500 | tracer 0-100 OUT_CUBIC; glint 100-220 IN_OUT_SINE; sparks 100-360 OUT_CUBIC; out 250-420 LINEAR | Tracer and glint shown still for 300 ms; no sparks. | 1 / 0 |
| `fx_ricochet_gold` | D | 500 | tracer 0-100 OUT_CUBIC; streak 100-320 OUT_CUBIC; ring 100-220 LINEAR; out 260-520 LINEAR | Tracer and the full streak shown still for 300 ms. | 1 / 1 |
| `fx_strike` | D | 700 | slash 0-120 OUT_CUBIC; burst 120-200 OUT_BACK; speed_lines 120-330 IN_OUT_SINE; shards 130-520 OUT_CUBIC; ticks 200-300 LINEAR; out 380-640 LINEAR | Slash and burst shown full at once for 300 ms, fade 200 ms; no speed lines or shards. | 1 / 1 |
| `fx_trigger_hit` | D | 900 | ignite 0-420 LINEAR; burst_s3 230-560 LINEAR; burst_s4 420-750 LINEAR; route_out 650-900 LINEAR | Route shown painted at once; the two bursts appear together for 300 ms, no speed lines. | 0 / 0 |
| `fx_hit_land` | H | 700 | chevrons 0-100 IN_CUBIC; frame_flash 100-134 STEP; flood 100-260 OUT_CUBIC; krackle 120-520 LINEAR; flood_out 330-620 LINEAR; pip 260-260 LINEAR | No chevron travel or krackle: the flood holds at 80 % density for 300 ms and fades; the pip goes dark on the same frame. | 1 / 1 |
| `fx_hit_land_adjuster` | H | 700 | as_parent 0-700 LINEAR; gold_flash 100-200 IN_OUT_SINE | As the parent; the gold rim shows as a thin outline, no flash. | 1 / 1 |
| `fx_hit_land_worm` | H | 700 | as_parent 0-700 LINEAR; hook 160-230 OUT_BACK | As the parent; the hook appears without overshoot. | 1 / 1 |
| `fx_hp_through` | H | 1150 | lift 0-220 OUT_CUBIC; flight 120-880 IN_OUT_CUBIC; slap 800-980 IN_OUT_SINE; dark 920-1100 LINEAR | No flight: the six hatched segments go dark in a 200 ms fade, no slap. | 0 / 0 |
| `fx_shield_break` | H | 700 | load 0-110 OUT_CUBIC; crack 20-110 LINEAR; split 120-120 LINEAR; shards 120-560 OUT_CUBIC; flood 130-300 OUT_CUBIC; krackle 130-600 LINEAR; dark 200-500 IN_OUT_CUBIC; pips 300-300 LINEAR | No shard flight or krackle: the plate shows split in place (shards offset 55 %) for 300 ms; flood at 70 %; the wedge darkens in one 300 ms fade. | 1 / 1 |
| `fx_slice_break` | H | 650 | flood 0-380 LINEAR; stamp 120-200 OUT_BACK; blackout 150-450 IN_OUT_CUBIC; halftone 200-500 LINEAR; pips 250-250 LINEAR | No flood or overshoot: black-out, X and halftone fade in together over 300 ms. | 0 / 0 |
| `fx_slice_crack` | H | 500 | flood 0-300 LINEAR; crack 60-260 OUT_CUBIC; tip 60-300 LINEAR; pip 200-200 LINEAR | No flood pulse or tip spark: the crack draws in 150 ms linear. | 2 / 0 |
| `fx_clear` | L | 800 | wash 0-240 IN_OUT_CUBIC; check 160-300 OUT_BACK; sparkles 300-680 IN_OUT_SINE; wash_settle 400-800 LINEAR | No sweep or sparkles: wash and check fade in over 200 ms. | 1 / 0 |
| `fx_refund` | L | 900 | pop 0-150 OUT_BACK; flight 150-650 IN_OUT_CUBIC; light 650-910 OUT_CUBIC | No flight: the coin fades at the refund mark (150 ms) and the RAM slot lights at once. | 0 / 1 |
| `fx_repair_mend` | L | 900 | strokes 0-645 OUT_CUBIC; plus 120-780 LINEAR; pip_fill 380-560 IN_OUT_CUBIC; glow_out 550-900 LINEAR | No strokes or glow: two static plus signs and the pip fills over 200 ms. | 1 / 0 |
| `fx_trace_add` | S | 400 | card glitch, 5 steps 0-166 STEP; pip pops, 3 steps; row glitch 166-266 STEP; settled 266-400 HOLD | No glitch bands: the fourth pip simply lights at 166 ms (one step, no scale). | 1 / 0 |
| `fx_commit` | T | 760 | SEND IT press, hold 0-80 HOLD; burn front runs the marks 80-560 IN_OUT_CUBIC; ping at the route end 560-700 OUT_CUBIC; board steps preview to resolve 560-760 IN_OUT_CUBIC | No burn front and no ping: the marks cross-fade yellow to pink over 300 ms, then the board steps to resolve over 300 ms. | 0 / 0 |

Notes:
- `fx_refund`'s light phase ends at 910, 10 ms past its 900 total; that is in the source data.
- Phases with equal start and end (`pip 260-260`, `split 120-120`) are instant events at that time.
