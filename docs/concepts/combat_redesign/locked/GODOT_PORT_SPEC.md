# Godot port spec: the locked combat screen (roadmap step 8)

**Status: DRAFT, not posted.** Art-pass draft, rebuilt 2026-11-04 on the rebuilt board (`final/` gate 1 of 2026-11-04, the effects rebuild of 2026-11-03, room grade rb2-1). It is not signed off by the designer and has not been sent to build. The mailbox draft is `MAILBOX_DRAFT.md` (also DRAFT, not posted).

**Generated tables.** Every table and appendix that carries a number sits between a pair of `gen:` markers (HTML comments, `gen:<name> begin` and `gen:<name> end`, invisible when rendered) and is written by `port/src/port_spec.py` from the data files (`port/*.json`, `backdrop/grade.json`, `backdrop/checks.json`, `final/checks.json`). No number inside a marker is typed by hand; change the data and re-run, never edit the block.

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
  - **corp skins per the `docs/ART_BIBLE.md` 2.4 designer-ruling note (DR-6):** the corp theme is told by material; the corp hue appears only on the rim, the bezel lip, the crest and the cell edges; the cell fills are neutral slate with a low-chroma tint; every corp hue ink keeps ΔE 15 or more (dE76 in the checks) from Cell lime, GAIN, FOCUS and HARM. One gunmetal clock (the schedule band) is the same on every corp; SCHEDULE orange is on the live step only. The silver THIS TURN tape is retired;
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
| File | What it is |
|---|---|
| `port/fx_timings.json` | 32 effects (T 1, M 8, P 3, D 7, H 7, L 3, C 2, S 1) merged from `effects/timings_CDHL.json` and `timings_MPST.json`; cap 600 ms with 0 per-effect overrides; the resolve beat 3800 ms against 4000 (section 8, Appendix A). Version port-2. |
| `port/skin_tables.json` | Tokens, marks, slice inks, card types, cell fills, the time grade, the gunmetal clock and the three skins with their material layers read from the generator source (sections 3, 4.3, 4.4, 7, Appendix B). Version port-2. |
| `port/cards_atlas.json`, `port/cards_proof.jpg` | The card atlas baked from the module that renders `final/card_sheet.jpg`: cell rects, every text anchor logged from the real draw call, the rules-bar quads, the state recipes; the proof shows art | worded | liner per card at the in-hand size (sections 4.8, 6.2, Appendix D). Version port-2. |
| `port/src/` | `norm_timings.py`, `skin_tables.py`, `bake_cards.py` make the three data files; `port_spec.py` writes every table and appendix of this spec from them (and from `backdrop/grade.json`, `backdrop/checks.json`, `final/checks.json`). Re-run all four after any change upstream; a hand edit inside a `gen:` block is overwritten. |
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
| Slice type BURST (big dots, slice ink in section 3) | role GUN with `shots >= 2`: `burst`, `railgun` | Same rule as `WavesSpinner._slice_color` today. Confirm. |
| TURRET (Ben-Day bullseye, slice ink in section 3) | role GUN with `shots == 1`: `turret` | Confirm. |
| SHIELD (scales, blue slice ink, section 3) | role SHIELD: `shield`, `bulwark`, `thorn` | Confirm. Thorn and bulwark share the texture and differ by glyph. |
| REPAIR (plus tiles, slice ink in section 3) | role REPAIR: `repair` | ok |
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
| 5 | Unit cells: neutral slate kind fill plus skin material plus enamel outline | shader plus code (4.3, 4.5) | `UnitCellLayer` | `WavesSpinner._draw_unit` |
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

<!-- gen:tokens begin -->
| Token | Hex | L* | Meaning |
|---|---|---|---|
| `player_pink (CELL_PINK)` | #FF3DA8 | 59.4 | Player-owned: tower halo, guns, resolve marks, D effects, the lifted-card print |
| `toner (ink)` | #15121A | 6.0 | Key lines, hatch keyline (card_render INK, logged from the rules text) |
| `sheet (paper)` | #F2EEE4 | 94.2 | Copier paper, card bone |
| `white` | #FBFAF4 | 98.2 | Glyph white (card titles, logged) |
| `harm` | #FF4433 | 57.7 | Red hatch = the enemy hits you |
| `harm_up (HOT)` | #FF6452 | 62.5 | Threat chevrons and arcs, HOT |
| `harm_cold` | #D9877C | 64.6 | COLD threat marks (lifted; `f1_board`) |
| `harm_far` | #96767A | 52.8 | FAR threat marks (lifted) |
| `hot_core` | #FFEAE0 | 94.1 | The HOT outline core |
| `soak` | #3A7EF3 | 54.3 | Blue hatch = soaked |
| `gain` | #7BE07B | 81.3 | Gains, the clear wash |
| `net_cyan` | #5CE1FF | 83.6 | RAM coin only (and the NO RAM word) |
| `trace_violet` | #A03CFF | 49.4 | Trace only (card tab, Trace pips, S glitch) |
| `boss_gold` | #D69A1A | 67.6 | Ward and boss (re-picked 2026-11-03; was #FFC428) |
| `boss_gold_hi` | #F0BE46 | 79.5 | Boss gold highlight |
| `resist_gold` | #FFD24D | 86.0 | Stars (rb_tokens) |
| `plan_yellow` | #FFE200 | 89.7 | Hover and plan pencil (preview form only) |
| `plan_badge` | | | The twist badge: plan_yellow x 0.86 |
| `focus_lime` | #D4FF00 | 94.1 | Hover focus corners |
| `amber (CRT_AMBER)` | #FFB000 | 77.5 | HOLD plates, Adjuster arc, Heat |
| `schedule` | #FF8C1A | 69.5 | The clock's LIVE step only: live cell edge, its chevrons, the rings-step and Hold motion (4.4); and the W6 climax ticket's three hazard ticks (VISUAL_PLAN F) |
| `clock_fill` | #6E7580 | 49.0 | Gunmetal clock: engraved band and cells (4.4); the same on every corp |
| `clock_light` | #969EAA | 64.8 | Gunmetal clock: lip and groove light |
| `clock_groove` | #282C34 | 17.9 | Gunmetal clock: groove, Hold glyph body |
| `enamel` | #D9E1EA | 89.2 | Enemy cell outline, HOT (COLD / FAR in the time grade below) |
| `cream_hp` | #DBD1B7 | 84.0 | Enemy HP ticks on the board |
| `cream_faded` | #FFF4D6 | 96.3 | HP ticks of hover-faded units only (p2b) |
| `k_type` | #CBD2DB | 83.9 | K type: sector digits, ring tags, W tags, ticket glyphs, nowords tallies (no glow) |
| `token_glyph` | #C8CED8 | 82.6 | Unit glyph in its token frame |
| `hit_paper` | #DED8CA | 86.5 | Gun hit star fill, tracer highlight, bit white-hot |
| `steel_hi` | #C4CBD8 | 81.5 | The armour rail's top edge on enemy HP trays |
| `text_hi / best_neutral` | #F2F6FF | 96.8 | BEST LINE chip and selected option chips (type), filled star; never plan_yellow |
| `text_mid` | #AFC0D6 | 77.1 | BEST LINE chip edge, HUD mid text |
| `p_stock` | #F6C8DE | 85.1 | FX-P plate stock and break shards (review 3.10: the FX-P plate on its own stock, a pink-tinted paper, not the card bone PAPER #F2EEE4) |
| `slice_burst` | fill #F06EAE / texture ink #9E2A66 | 63.9 | Slice ink (`rb_tokens` SLICE_INK / SLICE_TEX) |
| `slice_shield` | fill #5E9BE0 / texture ink #234E8C | 62.7 | Slice ink (`rb_tokens` SLICE_INK / SLICE_TEX) |
| `slice_turret` | fill #AEB24E / texture ink #5A5E1A | 70.4 | Slice ink (`rb_tokens` SLICE_INK / SLICE_TEX) |
| `slice_repair` | fill #3FB59A / texture ink #1D6656 | 66.9 | Slice ink (`rb_tokens` SLICE_INK / SLICE_TEX) |
| `card_tower` | #006E66 (dark #00403B, text #FBFAF4) | 41.4 | Card type plate (`card_render.TYPES`) |
| `card_wave` | #B4AAFF (dark #5E50C4, text #15121A) | 73.3 | Card type plate (`card_render.TYPES`) |

Retired, never drawn: the silver THIS TURN tape (`tape_lo` / `tape_hi`), the O-29 slice inks, BOSS_GOLD #FFC428. Targets the tokens are held to (`port/skin_tables.json` `targets`): `cell_ratio_min` 3.0, `clock_L` [45.0, 55.0], `slice_ink_L` [60.0, 72.0], `cap_min_px` 16.0, `de_min` 15.0, `order_margin` 1.0, `room_mean_L` [28.0, 34.0], `e_mark_L` 84.0, `k_type_L` 84.0, `mark_margin` 1.0, `ring_val` [1.0, 0.8, 0.62], `cell_tint_max_chroma` 8.0, `review_room_box` [1200, 450, 1800, 800].
<!-- gen:tokens end -->

**Time grade function** (`gramlib.grade`, used for every graded mark). For COLD and FAR, the threat red is overridden by the lifted colours.

<!-- gen:time_grade begin -->
Function: gramlib.grade: g = lum + (c - lum) * sat (lum Rec709 on 0-255), out = bed + (g - bed) * val; f1_board.grade2 replaces the threat red by the lifted COLD_CHEV / FAR_CHEV. bed #070912, sat [1.0, 0.45, 0.25], val [1.0, 0.7, 0.5] (HOT, COLD, FAR).

| Mark | HOT | COLD | FAR |
|---|---|---|---|
| `harm` | #FF6452 (L* 62.5) | #D9877C (L* 64.6) | #96767A (L* 52.8) |
| `enamel` | #D9E1EA (L* 89.2) | #9DA0A5 (L* 65.8) | #73757A (L* 49.2) |
| `k_type` | #CBD2DB (L* 83.9) | #93959B (L* 61.7) | #6B6D73 (L* 46.0) |
| `cream_hp` | #DBD1B7 (L* 84.0) | #989590 (L* 61.8) | #6D6D6E (L* 46.1) |

Bake these into the resource as three colours per mark; never compute them per frame.
<!-- gen:time_grade end -->

---

## 4. Element families

Each family lists: **S** (shader), **T** (texture or sprite), **C** (code-drawn), and **N** (the node it maps onto).

### 4.1 Room backdrop and grade (rb2-1)
- **Which room:** `docs/ART_BIBLE.md` 3.14 (designer ruling DR-9): Site and HQ-run fights show the cutaway room; the boss fight keeps the perspective close-up. The skin picks the room (`bd_grade.CORP_ROOM`, below).
- **T, recommended:** bake each graded room offline with `D:/rc_scratch/combat_redesign/locked/corp/src/bd_grade.py` (`room_grade()`, rb2-1) and the parameters in `backdrop/grade.json`: one PNG per room in Appendix C (the `shop_meridian` corp variant included), at 1920x1080, `res://assets/backdrops/combat_v3/room_<name>_graded.png`. Bake the board scrim into the same image, because the board centre is fixed.
  - Keep the bare rooms (`combat_backdrop/v3_1/room_<n>_bare.png`) as well. T5 crossfades bare to graded (section 10).
  - Runtime cost: one texture.
- **S, for rooms not yet baked and for tuning:** `shaders/combat/room_grade.gdshader`, a canvas_item shader on the room TextureRect. It runs on sRGB-encoded values; in Godot 4 canvas textures arrive as sRGB, so no conversion is needed. It runs the grade.json steps below, in order, with the uniforms below. The hull is a signed-distance texture baked once from `hull_poly`; the blur ramp and the local tone's blurred luma are mip LOD taps (the room texture needs mipmaps). The step6-1 shader and its room squint bars in the 2026-11-02 draft are retired with step6-1; rb2-1 is gated by the room L* (section 13.3).

<!-- gen:room begin -->
Grade version **rb2-1**. Skin to room (`bd_grade.CORP_ROOM`): neutral → bio, solace → bio, meridian → shop.

Steps, in order (`backdrop/grade.json` `order`, verbatim):

- 1 focus hull m: polygon hull_poly (the cutaway box: walls + floor slab), m = 1 - smoothstep(-pf0, pf1, sdf) (sdf in px, + outside); d = the ellipse distance (cx, cy, rx, ry) for the vignette, spill and tone reach
- 2 blur ramp: hull_blur -> mid_blur -> city_blur, smoothsteps on the sdf from -pf0 to pf1 + blur_reach (one ramp, no cross-fade)
- 2b corp light (only when hue_amt > 0): w = window(hue_lo - hue_f .. hue_lo, hue_hi .. hue_hi + hue_f) * smoothstep(.10, .30, S); rotate the pixel about the grey axis by (hue_to - hue) * hue_amt * w, Rec709 luma kept
- 3 chroma: lerp to Rec709 luma; k = chroma * (1 - (1 - neon_chroma) * neon) * (1 - (1 - pink_chroma) * pink) * (m + city_chroma * (1 - m))
- 4 contrast: c = pivot + (c - pivot) * contrast
- 5 value: * (hull_value * m + city_value * (1 - m))
- 5b local tone: x = gaussian(luma, tone_blur); target = tone_lo + (tone_hi - tone_lo) * (1 - exp(-x / tone_s)); g = clamp(target / x, 0, tone_gmax); g = 1 + (g - 1) * (m + tone_out * (1 - m) * (1 - smoothstep(tone_d0, tone_d1, d))); rgb *= g
- 6 shoulder on luma above knee toward ceil: l2 = knee + (ceil - knee) * (1 - exp(-(l - knee) / (ceil - knee))); rgb *= l2 / l
- 7 haze: h = haze * m + haze_out * (1 - m); colour = mix(spill_rgb, haze_rgb, smoothstep(sp0, sp1, d)); rgb = rgb * (1 - h) + colour * h
- 8 vignette: * (1 - vignette * smoothstep(v0, v1, d)) * (1 - board_falloff * (1 - smoothstep(bx0, bx1, x)))
- then the board scrim (unchanged): 6 px blur weighted 1 - smoothstep(300, 520, r), and SCRIM #02030A at 0.55 * (1 - smoothstep(330, 560, r)), r from (536, 540)

Measured on the graded rooms (`backdrop/checks.json`, L* of the room region, after the grade):

| Plate | Room | Skin | mean L* | p95 L* | passes |
|---|---|---|---|---|---|
| `p1_bio` | bio | neutral | 32.0 | 38.1 | yes |
| `p1_srv` | srv | neutral | 32.5 | 38.1 | yes |
| `p1_gh` | gh | neutral | 31.9 | 38.1 | yes |
| `p1_rec` | rec | neutral | 32.3 | 38.1 | yes |
| `p1_lobby` | lobby | neutral | 32.2 | 38.1 | yes |
| `p1_event` | event | neutral | 31.8 | 38.1 | yes |
| `p1_shop` | shop | neutral | 32.2 | 38.1 | yes |
| `p1_bio_solace` | bio | solace | 32.0 | 38.1 | yes |
| `p1_shop_meridian` | shop_meridian | meridian | 32.2 | 38.1 | yes |

Targets: room_mean: L* 28-34 (rb_checks room region); room_p95: +1 <= ring-NOW occupied glass p95 of the plate; pink: room pink share < 0.1 %; rb_checks: a-e pass on every plate.

Shader path uniforms (`shaders/combat/room_grade.gdshader`), defaults = the `bio` room; every room's values are in Appendix C:
```glsl
shader_type canvas_item;
uniform float cx = 1500;
uniform float cy = 600;
uniform float rx = 330;
uniform float ry = 270;
uniform float f0 = 0.85;
uniform float f1 = 1.55;
uniform sampler2D hull_sdf;   // hull_poly [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]] baked once to a signed distance texture (px, + outside)
uniform float pf0 = 10;
uniform float pf1 = 3;
uniform float hull_blur = 0.4;
uniform float mid_blur = 1.6;
uniform float city_blur = 4;
uniform float blur_reach = 40;
uniform float neon_chroma = 0.8;
uniform float city_chroma = 0.3;
uniform float pivot = 0.16;
uniform float hull_value = 0.8;
uniform float city_value = 0.6;
uniform float tone_lo = 0.17;
uniform float tone_hi = 0.38;
uniform float tone_s = 0.09;
uniform float tone_blur = 14;
uniform float tone_gmax = 3.5;
uniform float tone_out = 0.45;
uniform float tone_d0 = 1.5;
uniform float tone_d1 = 2.6;
uniform float knee = 0.24;
uniform float ceil_ = 0.3502;   // grade.json "ceil"
uniform float haze = 0.05;
uniform float haze_out = 0.5;
uniform vec3 haze_rgb = vec3(0.0784, 0.0706, 0.1333);   // [20, 18, 34] / 255
uniform float sp0 = 1;
uniform float sp1 = 2.6;
uniform float vignette = 0.1;
uniform float v0 = 0.9;
uniform float v1 = 2.6;
uniform float board_falloff = 0.08;
uniform float bx0 = 700;
uniform float bx1 = 1250;
uniform float chroma = 0.876;
uniform float contrast = 1.12;
uniform float pink_chroma = 0.55;
uniform vec3 spill_rgb = vec3(0.3020, 0.4157, 0.2667);   // [77, 106, 68] / 255
uniform float hue_lo = 0.0;   // not set on bio (step off); set on shop_meridian
uniform float hue_hi = 0.0;   // not set on bio (step off); set on shop_meridian
uniform float hue_f = 0.0;   // not set on bio (step off); set on shop_meridian
uniform float hue_to = 0.0;   // not set on bio (step off); set on shop_meridian
uniform float hue_amt = 0.0;   // not set on bio (step off); set on shop_meridian
uniform float grade_mix = 1.0;   // T5: 0 = bare room, 1 = graded
```
<!-- gen:room end -->

- **N:** `CombatBackdrop` keeps choosing the room (`BackdropCatalog.place_for`). The art pass adds the `room_<n>` → graded-texture lookup and the per-room uniforms, read from a `RoomGradeData` resource array that mirrors `grade.json` (Appendix C).
- **Test hook:** with the shader on `room_bio_bare.png`, the mean absolute error against the baked PNG is at most 3/255, allowing for the mip blur. The room L* gate and the data test are in 13.3 ("room grade").

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
- **Cell fill (unit cells), DR-6:** the cell fill is the same neutral slate on every skin: one kind wash per unit kind and ring, at the ring value, and the empty fill per ring. The skin only adds its material over it (low chroma; `targets.cell_tint_max_chroma`). There is no per-skin push: `kind_gain` is retired (1.0 on every ring of every skin), and so is the `CorpKindWash` compute step. The fills are constants in `CombatLookData`:

<!-- gen:cells begin -->
Every skin draws the same cell fill (`kind_gain` 1.0 on every ring of every skin; `retired_skin_fields.kind_gain`: every skin is 1.0 on every ring (rb_patch._skins): the cell fill is the neutral slate kind wash at the ring value, the skin only adds its material, so no per-skin Lab push is baked). The skin adds its material over it (section 7, Appendix B).

| Fill | ring NOW | ring +1 | ring +2 |
|---|---|---|---|
| occupied, Packet | #506D83 (L* 44.6) | #4E5F6C (L* 39.4) | #495259 (L* 34.3) |
| occupied, Worm | #666594 (L* 44.6) | #5C5B74 (L* 39.6) | #50505E (L* 34.5) |
| occupied, Jammer | #38717F (L* 44.5) | #42626B (L* 39.5) | #435459 (L* 34.5) |
| occupied, Payload | #6E6774 (L* 44.6) | #605C63 (L* 39.7) | #535054 (L* 34.4) |
| occupied, Ring | #5D6984 (L* 44.4) | #565D6C (L* 39.4) | #4D5159 (L* 34.4) |
| empty | #243043 (L* 19.6) | #1B2535 (L* 14.5) | #161E2B (L* 11.1) |

Targets: occupied L* [44.5, 39.5, 34.5], empty L* [19.5, 14.5, 11.0] per ring. Other cell numbers: `occ_grad` [0.8, 1.14], `screen_lift` 1.1, `screen_inset` 6.0, `skin_unit_k` 0.3, `skin_empty_k` 0.8, `pip_h` 9.5, `empty_edge_mix` 0.3, `hot_core_w` 3.2, `kind_ramp` [0.0, 0.0, 0.0], `empty_base` "#263246", `dying` {"chev_dim": 0.55, "hatch_pitch": 8.5, "hatch_w": 1.6, "hatch_alpha": 150, "edge_w": 2.0, "inset": 3.0}, `adjuster` {"seg": 16.0, "gap": 1.6, "clear": 5.0, "track_h": 12.0}.

With the skin material composited (`skin_tables.py`, the material layers over the fill on a 2x canvas) and on the plates:

| Skin | occupied mean L* (NOW / +1 / +2) | empty mean L* | data: luminance ratio occupied / empty, lowest ring (the check-a measure) | plate: ring NOW occupied L* | plate: lowest ratio |
|---|---|---|---|---|---|
| neutral | 43.1 / 38.6 / 33.9 | 22.7 / 19.1 / 16.8 | 3.54 | 42.9-43.1 | 3.17 |
| solace | 43.1 / 38.5 / 33.9 | 22.1 / 18.4 / 15.7 | 3.73 | 43.0-43.3 | 3.32 |
| meridian | 42.3 / 37.8 / 33.1 | 20.5 / 16.9 / 14.5 | 4.08 | 42.7-42.9 | 4.12 |
<!-- gen:cells end -->

- **T (bake once per corp with PIL; corp-specific vector pieces):**
  - the rim strip;
  - 6 crests;
  - the token frame and disc frame;
  - the ticket 9-patch.

  See section 6.3.
- **C:** each cell's edge line (`cell_detail`) is drawn in the skin's hue ink as its `cell_detail` method lists it (Appendix B): the cell edge is one of the four places the corp hue may appear (DR-6).
- **N:** `CorpRingLayer` and `UnitCellLayer` replace `_draw_rings` and the fill and outline in `_draw_unit`. `WavesSpinner._band()` geometry gives way to section 2's radii.
- **Never touched by a skin:** the clock (4.4), HP, hatch, HOT/COLD/FAR, outlines, PLAN yellow, focus lime and pink.

### 4.4 Schedule band: the gunmetal clock, the live step, HOLD plates (time grammar)
- **C:** flat colours, drawn directly. **One gunmetal clock on every corp** (DR-6 note, `docs/ART_BIBLE.md` 2.4): the engraved band and its cells in gunmetal, the lip and groove light, the groove; **SCHEDULE orange only on the live step** (its cell edge, a soft glow under it, its chevrons) and in the clock's own motion (rings step, Hold). The silver THIS TURN tape of the 2026-11-02 draft and its remap table are retired; no clock colour is a skin field. Colours and draw calls, read from `rb_patch.py`:

<!-- gen:clock begin -->
| Part | Colour |
|---|---|
| `gun_fill` | #6E7580 (L* 49.0) |
| `gun_light` | #969EAA (L* 64.8) |
| `gun_groove` | #282C34 (L* 17.9) |
| `schedule` | #FF8C1A (L* 69.5) |

Band text 23 px, label tracks [1.0, 0.96, 0.92, 0.88], label to digit margin 2.0 px.

Draw calls, read from the generator source (`skin_tables.py`):

| Function | Source | Layers |
|---|---|---|
| `engraved` | `rb_patch.py:467` | `{"op": "poly", "fill": "#6E7580", "outline": "#0C0A16", "width": 3.2}` |
| `groove` | `rb_patch.py:471` | `{"op": "for", "target": "rr, col, w", "values": [[380.4, "#282C34", 1.4], [379.2, "#969EAA", 1.0], [361.4, "#282C34", 1.4], [362.6, "#969EAA", 1.0]]}`; `{"op": "line", "colour": null, "width": "w"}` |
| `live_cell` | `rb_patch.py:476` | `{"op": "glow", "args": "L.glow(lambda d: d.polygon([(x * k, y * k) for x, y in p], fill=SCHED + (255,)), blur=4, strength=0.30)"}`; `{"op": "poly", "outline": "#FF8C1A", "width": 2.2}` |
| `chevrons` | `rb_patch.py:513` | `{"op": "line", "colour": "#0C0A16", "width": 5.6}`; `{"op": "line", "colour": "#FF8C1A", "width": 3.0}` |
| `hold_glyph` | `rb_patch.py:525` | `{"op": "ellipse", "fill": "#282C34", "outline": "#0C0A16", "width": 3.0}`; `{"op": "ellipse", "fill": "#282C34", "outline": null, "width": 1.8}` |
<!-- gen:clock end -->

- HOLD plates and the Adjuster arc keep amber (`CRT_AMBER`). On Meridian a black gap of at least 2 px separates them from the rim rust; the bezel inner lip is black (section 7, Appendix B `bezel`).
- Digits draw on their own layer above everything on the board. Each digit **punches a hole** of boss r + 2.6 px in the band/plate layer and the label layer: draw the digit's disc with `BLEND_MODE_SUB` alpha, or use a stencil-like mask Control. Digit 0 sits at -4.5°.
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
- **N:** `TowerView` replaces `_draw_tower`. During a spin (`fx_spin`), the whole `TowerView` rotates; the baked lit edges rotate with it for the turn phase of `fx_spin` (Appendix A), which is accepted. At rest it snaps to the 6 baked sector sprites.

### 4.7 Guns (player pink marker)
- **C:** Line2D ribbons in `player_pink` with an ink key (a second, wider Line2D underneath) and xerox grain (5.4).
- Opacity: full at decide, 0.58 as the p2 preview, full at resolve. On p2b they are dimmed by `DIM_K` 0.38.
- **N:** a new `GunLayer` under the landing arcs. Data comes from the `fire` events of the previewed END TURN.

### 4.8 Hand and cards (WPAP)
- **T:** a card art atlas baked from `card_render` (the module that renders `final/card_sheet.jpg`) with every text call emptied and the pink rules bar left out (6.2): the plates, tabs, facets, icons and drops stay; the words and the bar go.
  - A second atlas holds the PLAYED liner frames (torn outline plus ghost glyph), also without words. The slot is upright, never fanned (2026-11-03 stage 2, review 2.3).
- **C, Labels over the art** (fonts already in `assets/fonts/`), and the rules bar drawn from the rules Label's width:

<!-- gen:cards begin -->
Logged from the real `text()` calls while each card is drawn (`bake_cards.py`; per-card values in Appendix D). Coordinates are card design px (the card is 176 x 250; cell px = (design + 18) x 2).

| Text | Font, size, tracking, rotation, colour | Anchor (design px, centre of the cap height) | Cards |
|---|---|---|---|
| mult | Anton-Regular 30 px, track 0.5, rot -3°, #FBFAF4 | (139, 107) | Nudge, Spin2, Spin3 |
| title | Anton-Regular 38 px, track 1, rot -2°, #FBFAF4 | (87.5, 144.5) | Nudge, Spin2, Spin3, Brace, Strike, Pull, Shove, Twist, Hold, Trigger |
| type_word | Anton-Regular 19 px, track 2.2, rot -1.2°, #FBFAF4 | (85.5, 174.4) | Nudge, Spin2, Spin3, Brace, Strike |
| cost | Anton-Regular 27 px, track 0, rot 0°, #15121A | (21.5, 22.2) | all |
| played_name | ShareTechMono-Regular 21 px, track 1, rot 0°, #96948D | (88, 157) | all |
| played_word | ShareTechMono-Regular 21 px, track 1, rot 0°, #B3B0A9 | (88, 183) | all |
| title | Anton-Regular 34.25 px, track 1, rot -2°, #FBFAF4 | (87.5, 144.5) | Firewall |
| type_word | Anton-Regular 19 px, track 2.2, rot -1.2°, #15121A | (85.5, 174.4) | Firewall, Pull, Shove, Twist, Hold, Trigger |
| trace | Anton-Regular 21 px, track 0, rot 0°, #FBFAF4 | (133, 17.6) | Firewall, Pull, Shove, Trigger |
| rules | IBMPlexSansCondensed-Medium 21 px, track 0, rot -0.8°, #15121A; never shrunk; wider than 124 px wraps to two lines (a text wider than fit_w wraps at the word break giving the narrowest longest line (card_render.rules_lines)) | one line (80, 206); two lines (80, 200) and (80, 221.5) | all |
| rules bar | #FF3DA8 quad under the last line, from the label width; drawn by Godot, not in the art atlas | y band below the last line: one line [11.5, 18.5], two lines [13.0, 20.0] (quads per card in Appendix D) | all |

The title's plate, keyline and drop, the type plate and the tab plates are art (in the atlas); their drawing code is in Appendix D, verbatim. Hand scale 1.1: the card is 193.6 px wide on screen.
<!-- gen:cards end -->

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
- **Unaffordable** (`card_render._unaffordable` and `unaffordable_marks`; the cost badge keeps its colour, it is the reason, so pass its rect as an exclusion uniform):

<!-- gen:unaffordable begin -->
- Dim glass, `card_render._unaffordable` (`corp/src/card_render.py:1022`), verbatim:
  ```python
  def _unaffordable(im):
      """dim glass: value x0.5, chroma x0.4, two flat glass planes.  draw_card then lays unaffordable_marks() on top at full value
      (cost badge, padlock, NO RAM tab), so the state is told by a glyph and a word, not only by the dim."""
      a = np.asarray(im).astype(np.float32)
      rgb, al = a[..., :3], a[..., 3:]
      g = rgb.mean(-1, keepdims=True)
      rgb = (g + (rgb - g) * 0.40) * 0.55 + np.array([8, 6, 14], np.float32) * 0.45
      H, W = al.shape[:2]
      y, x = np.mgrid[0:H, 0:W].astype(np.float32)
      u = (x + y * 0.55) / W
      gl = ((u > 0.42) & (u < 0.62)).astype(np.float32) * 0.10 + ((u > 0.70) & (u < 0.76)).astype(np.float32) * 0.08
      rgb = rgb + gl[..., None] * (255 - rgb)
      return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), 'RGBA')
  ```
- Over the glass at full value (`unaffordable_marks`, `corp/src/card_render.py:809`): the "NO RAM" tab (design rect x 32-92.5, y 10-30, visible from x 42.5; word centre x 67.2; Anton 17 px, track -0.5, in #5CE1FF; measured cap 16.1 px at the hand scale, fits the tab: True), the cost badge redrawn (centre [21.0, 21.0]), and the padlock (`lock_glyph`, `corp/src/card_render.py:783`). nowords keeps the badge and the padlock only. These are sprites on the card, not shader work.
<!-- gen:unaffordable end -->

### 5.6 `offset_print.gdshader` (drop shadows and halos, by silhouette offset)
- Samples the alpha at `UV - offset / size`, blurred by mip LOD.
- Used for:
  - the tower drop: (3, 5), blur 7, alpha 0.55, #08060E;
  - the lifted-card shadow;
  - the D-family ink keys.
- The pink scissor halo of the tower is **baked** (6.1). It is not this shader.

### 5.7 `glitch_s.gdshader` (S family: `fx_trace_add`)
- One band of rows per step (`rows[i] = (y, h, shift)`; 4-7 px tall since the 2026-11-03 rebuild, `effects/NOTES_MPST.md` 2.10; the 2026-11-02 draft had 3 bands per step) shifts by ±6 px.
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

### 6.2 Card atlas (baked in this pass from the new card sheet's module)
- **Bake:** `port/src/bake_cards.py` imports `corp/src/card_render.py` read-only (the module `final_cards.py` renders `final/card_sheet.jpg` with) and wraps four of its calls for the bake only: `text` (returns an empty mask in the art pass and logs every call: text, anchor, size, font, tracking, rotation, and the colour of the paint that follows), `rules_lines` and `poly` (to catch the rules bar), and `Cv.paint` (skips the one pink bar paint after the rules layout in the art pass). Nothing in `card_render` is edited; the `bake_art_only` flag the 2026-11-02 draft asked for is not needed. It draws `draw_card(name, 2 x CW, state)` for the 11 cards in `card_render.ORDER`, in the normal, played and unaffordable states.
- **Result** (atlases in scratch, `D:/rc_scratch/combat_redesign/locked/port_rb/work/`; `port/cards_atlas.json` and `port/cards_proof.jpg` beside this spec):

<!-- gen:atlas begin -->
| File | Size | md5 | Opaque px | What |
|---|---|---|---|---|
| `cards_art_atlas.png` | 1696 x 1716 | `77250b4c0d4d006b9cbb87959eda875c` | 2105609 | normal state, art only: every word and the rules bar left out |
| `cards_ref_atlas.png` | 1696 x 1716 | `57f8431fd7bd068814521f9cf3393267` | 2105422 | the same with words and bar: what the Labels plus the bar must reproduce |
| `cards_liner_atlas.png` | 1696 x 1716 | `f1748b8fba783add5c009f471a553276` | 1860256 | the played-slot liner, art only (Godot labels the name and PLAYED) |

4 x 3 cells of **424 x 572** (the card 352 px wide = 2x design, plus 36 px margin each side), in `card_render.ORDER`. Sources: `corp/src/card_render.py` md5 `7603fd56141bb72dffd0bba9ab3c8058`, `final/card_sheet.jpg` md5 `87a5a6da7d076291a3fe8b481e80e200`. On screen at 1.1 the card is 193.6 px wide, so the atlas is 1.82x screen.

Note: cards/src_snapshot/card_render.py md5 b8a435c4aa055c85d45f4c42c8ac10ae is the card session's older snapshot (before the stage-2 NO RAM and rules-wrap change); the atlas follows corp/src.
<!-- gen:atlas end -->

- **Looked at** (`cards_proof.jpg`, at the in-hand size): every art card keeps its type plate, title plate, cost hex, Trace tab, multiplier plate, owner triangles, icon and facets with no words and no rules bar; the worded card matches `final/card_sheet.jpg`; the liner keeps its torn rim and ghost glyph with no words.
- **Also bake** `cards_nowords_atlas.png` only if a no-words mode ships (`state='nowords'`).
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
| `fx_p_plate.png` | 9-patch, sized at the bake from the plate | P shield plate on the **P stock** (`p_stock`, section 3: its own pink-tinted paper, never the card bone PAPER), ink key, rivet heads; the clamp brackets and the P-stock sparks are cut from the same stock (`effects/NOTES_MPST.md` 2.10, 3.10). The bone plate #F1EAD6 of the 2026-11-02 draft is retired. |
| `fx_brace_stamp.png` | sized at the bake from the stamp | P brace stamp (it slams to its final size; `effects/NOTES_MPST.md` 2.10) |

There is **no C-family sprite**: the corp shutter slab and its lips are retired. C is one vector scan line in the skin's `c_scan_ink` with an ink key, code-drawn (8.4, section 7).

Starbursts, tracers, speed lines, ribbons and arrows are **C**: Polygon2D or Line2D with width curves, keyed in ink.

---

## 7. Corp skin data format (Godot Resource)

`scripts/data/combat_corp_skin.gd`. It is read-only at runtime (rule 3), and every value is data (rule 5).
```gdscript
class_name CombatCorpSkin
extends Resource
## One corporation's enemy-layer look on the combat board: its material, plus the corp hue on the rim, the bezel lip, the crest
## and the cell edges only (docs/ART_BIBLE.md 2.4, designer ruling DR-6). Game marks are NOT here: the clock, HP, hatch,
## HOT/COLD/FAR, outlines, the cell fills, PLAN yellow, focus lime and player pink live in CombatLookData.

enum CellMaterial { ENAMEL_LINES, MEMBRANE, RIBS }

@export var id: StringName = &"neutral"
## The graded room this corp's fights use (backdrop/grade.json corp_room, GODOT_PORT_SPEC 4.1).
@export var room: StringName = &"bio"
## Cell, bezel, annulus and arcframe materials: ShaderMaterials on corp_ring.gdshader, uniforms filled per corp (Appendix B).
@export var cell_material: ShaderMaterial
@export var bezel_material: ShaderMaterial
@export var annulus_material: ShaderMaterial
@export var arcframe_material: ShaderMaterial
@export var material_kind: CellMaterial = CellMaterial.ENAMEL_LINES
## The skin palette (rb_patch._skins) and its hue inks: the only colours a skin draws.
@export var pal: Dictionary = {}
@export var inks: Dictionary = {}
## C family (the corp acting): the ink of its one scan line (fxk_lib.CORP_ENAMEL).
@export var c_scan_ink: Color = Color.WHITE
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
## Transitions (T5/T6 bits FX): no skin field (review 3.12): each bit reads the colour of its source from the board
## (section 10, "Bit colour"; ART_BIBLE 1.2).
## Meridian's stencilled numbers on empty cells (hook exists, art not drawn yet).
@export var empty_marks: bool = false

## Error codes of a bad value (empty when valid).
func validate() -> PackedStringArray:
	var e := PackedStringArray()
	if crest_count < 0: e.append("corp_skin: crest_count")
	if room == &"": e.append("corp_skin: room")
	return e
```

Retired fields of the 2026-11-02 draft, not ported: `kind_gain`, `cell_edge` / `cell_edge_w` / `frame` / `frame_groove` as typed colours (the cell edge and the frames are now the method layers of Appendix B, read into the materials and the 6.3 bakes), `shutter_slab`, `shutter_lip`, `shutter_lip_shape`, `motion_tint`, and the hazard paint (reasons below, generated).

**Per corp** (generated from `port/skin_tables.json`; the material layers of every method are in Appendix B):

<!-- gen:skins begin -->
| Skin | Class | Room | `kind_gain` | Hue inks (rim, lip, crest, cell edges) | C scan line ink | Material means, occupied L* (NOW / +1 / +2) |
|---|---|---|---|---|---|---|
| neutral | `lw_skin.NeutralSkin` | bio | [1.0, 1.0, 1.0] | (none) | #D9E1EA (L* 89.2) (key #748090 (L* 53.1)) | 43.1 / 38.6 / 33.9 |
| solace | `cs_skin.Solace` | bio | [1.0, 1.0, 1.0] | leaf #96FF46 (L* 91.0), leaf_deep #4FA83A (L* 61.6), porcelain #B8DCCC (L* 84.9) | #B8DCCC (L* 84.9) (key #507868 (L* 47.2)) | 43.1 / 38.5 / 33.9 |
| meridian | `cs_skin.Meridian` | shop | [1.0, 1.0, 1.0] | rust #B0602C (L* 49.2), rust_hi #D88A4E (L* 64.4), barcode #2A2A2E (L* 17.2) | #D88A4E (L* 64.4) (key #78401E (L* 33.5)) | 42.3 / 37.8 / 33.1 |

Palettes (`pal`), as installed by `rb_patch._skins()`:

| Skin | accent | bed | edge | glass | glass_hi | hazard_a | hazard_b | ink | line | nucleus | oxide | paint | pale | panel | panel_hi | porcelain | porcelain_d | primary | rivet | secondary | steel | steel_d | strand_a | strand_b |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutral | #96A2B2 | #090B0F |  |  |  |  |  | #08090C | #BCC8D6 |  |  |  |  | #283240 | #6E7C8E |  |  |  |  |  | #748090 | #46505E |  |  |
| solace |  | #06120D | #96FF46 | #2C3634 | #96AAA0 |  |  |  |  | #96AAA0 |  |  | #ECF8E2 |  |  | #B8DCCC | #96B096 | #96FF46 |  | #FF4696 |  |  | #96FF46 | #4FA83A |
| meridian |  | #0E0B09 | #B0602C |  |  | #B0602C | #140F0C |  |  |  | #383430 | #ECD6B2 |  |  |  |  |  | #B0602C | #281E18 | #FF2E28 | #463E38 |  |  |  |

Retired skin fields (never port them):

- `kind_gain`: every skin is 1.0 on every ring (rb_patch._skins): the cell fill is the neutral slate kind wash at the ring value, the skin only adds its material, so no per-skin Lab push is baked
- `shutter_slab`: C family is one 1.6 px scan line in c_scan_ink (fxk_lib.CORP_ENAMEL), no slab and no lip
- `shutter_lip`: as shutter_slab
- `shutter_lip_shape`: as shutter_slab
- `motion_tint`: M print echoes are retired (effects/NOTES_MPST.md 2.10); the corp hue in motion is only the wave_enter scan line
- `bits_rings`: T5 / T6 bits read the colour of their source from the board (ART_BIBLE 1.2, review 3.12)
- `bits_accent`: as bits_rings
- `hazard_paint`: Meridian HAZ_DESAT is 0: the rim stripes and the outer lip are container rust (SKIN_INKS meridian rust), off SCHEDULE

**The three `.tres` files** (`content/combat/skins/<id>.tres`), generated; the ShaderMaterials and textures are filled from Appendix B and section 6.3:
```
# content/combat/skins/neutral.tres   (lw_skin.NeutralSkin; room bio)
[gd_resource type="Resource" script_class="CombatCorpSkin" load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/data/combat_corp_skin.gd" id="1"]
[resource]
script = ExtResource("1")
id = &"neutral"
material_kind = 0   # ENAMEL_LINES
room = &"bio"
c_scan_ink = Color(0.8510, 0.8824, 0.9176, 1.0000)   # #D9E1EA
pal = {&"bed": Color(0.0353, 0.0431, 0.0588, 1.0000), &"panel": Color(0.1569, 0.1961, 0.2510, 1.0000), &"panel_hi": Color(0.4314, 0.4863, 0.5569, 1.0000), &"steel": Color(0.4549, 0.5020, 0.5647, 1.0000), &"steel_d": Color(0.2745, 0.3137, 0.3686, 1.0000), &"line": Color(0.7373, 0.7843, 0.8392, 1.0000), &"ink": Color(0.0314, 0.0353, 0.0471, 1.0000), &"accent": Color(0.5882, 0.6353, 0.6980, 1.0000)}
# + cell_material / bezel_material / annulus_material / arcframe_material (ShaderMaterial sub-resources, Appendix B)
# + rim: degree ticks on steel; crest: dark roundel with pale ring and bar (section 6.3 textures)

# content/combat/skins/solace.tres   (cs_skin.Solace; room bio)
[gd_resource type="Resource" script_class="CombatCorpSkin" load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/data/combat_corp_skin.gd" id="1"]
[resource]
script = ExtResource("1")
id = &"solace"
material_kind = 1   # MEMBRANE
room = &"bio"
c_scan_ink = Color(0.7216, 0.8627, 0.8000, 1.0000)   # #B8DCCC
inks = {&"leaf": Color(0.5882, 1.0000, 0.2745, 1.0000), &"leaf_deep": Color(0.3098, 0.6588, 0.2275, 1.0000), &"porcelain": Color(0.7216, 0.8627, 0.8000, 1.0000)}
pal = {&"primary": Color(0.5882, 1.0000, 0.2745, 1.0000), &"secondary": Color(1.0000, 0.2745, 0.5882, 1.0000), &"glass": Color(0.1725, 0.2118, 0.2039, 1.0000), &"glass_hi": Color(0.5882, 0.6667, 0.6275, 1.0000), &"bed": Color(0.0235, 0.0706, 0.0510, 1.0000), &"edge": Color(0.5882, 1.0000, 0.2745, 1.0000), &"porcelain": Color(0.7216, 0.8627, 0.8000, 1.0000), &"porcelain_d": Color(0.5882, 0.6902, 0.5882, 1.0000), &"strand_a": Color(0.5882, 1.0000, 0.2745, 1.0000), &"strand_b": Color(0.3098, 0.6588, 0.2275, 1.0000), &"nucleus": Color(0.5882, 0.6667, 0.6275, 1.0000), &"pale": Color(0.9255, 0.9725, 0.8863, 1.0000)}
# + cell_material / bezel_material / annulus_material / arcframe_material (ShaderMaterial sub-resources, Appendix B)
# + rim_texture (helix turns), crest (porcelain roundel, lime helix S), token_frame (porcelain ring, lime dot at 12), ticket (chamfered lab slide) (section 6.3 textures)

# content/combat/skins/meridian.tres   (cs_skin.Meridian; room shop)
[gd_resource type="Resource" script_class="CombatCorpSkin" load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/data/combat_corp_skin.gd" id="1"]
[resource]
script = ExtResource("1")
id = &"meridian"
material_kind = 2   # RIBS
room = &"shop"
c_scan_ink = Color(0.8471, 0.5412, 0.3059, 1.0000)   # #D88A4E
inks = {&"rust": Color(0.6902, 0.3765, 0.1725, 1.0000), &"rust_hi": Color(0.8471, 0.5412, 0.3059, 1.0000), &"barcode": Color(0.1647, 0.1647, 0.1804, 1.0000)}
pal = {&"primary": Color(0.6902, 0.3765, 0.1725, 1.0000), &"secondary": Color(1.0000, 0.1804, 0.1569, 1.0000), &"steel": Color(0.2745, 0.2431, 0.2196, 1.0000), &"oxide": Color(0.2196, 0.2039, 0.1882, 1.0000), &"edge": Color(0.6902, 0.3765, 0.1725, 1.0000), &"bed": Color(0.0549, 0.0431, 0.0353, 1.0000), &"paint": Color(0.9255, 0.8392, 0.6980, 1.0000), &"hazard_a": Color(0.6902, 0.3765, 0.1725, 1.0000), &"hazard_b": Color(0.0784, 0.0588, 0.0471, 1.0000), &"rivet": Color(0.1569, 0.1176, 0.0941, 1.0000)}
empty_marks = true   # stencilled container numbers on empty cells: hook only, art not drawn
# + cell_material / bezel_material / annulus_material / arcframe_material (ShaderMaterial sub-resources, Appendix B)
# + rim: stripes in container rust, crest crane-A, token_frame steel octagon with 4 corner castings, ticket square-cut shipping tag with barcode (section 6.3 textures)

```
<!-- gen:skins end -->

- **Selecting the skin.** The fight's corp (`WavesState.node` / netrun site → corporation id) picks `content/combat/skins/<id>.tres`. Neutral is the fallback. Meridian stays hibernated in the slice (A-112): a palette proof that the swap works.
- **Swapping at runtime:** set the four ShaderMaterials, swap the five textures and the room. The game marks and the cell fills do not change.
- **The clock is not a skin field.** `CombatLookData` holds the clock colours (4.4). A test asserts that no skin colour equals a game-mark token, and that every hue ink keeps dE76 15 or more from Cell lime, GAIN, FOCUS and HARM (section 13).

---

## 8. Effect timings as data

### 8.1 Resources
<!-- gen:fx_counts begin -->
`port/fx_timings.json` holds **32 effects**: T 1, M 8, P 3, D 7, H 7, L 3, C 2, S 1.

- Cap: every total, every phase end and every reduce form at most **600 ms**; per-effect overrides: 0. Tier: T2 for every effect (VfxTier T2 outcome, max 0.6 s; REVIEW_RESPONSE 2.11).
- Layer: every effect draws under the HUD and the hand (f1_render.SPLIT below / above); only fx_hp_through, fx_refund, fx_trace_add may draw above the HUD (review 1.6).
- Frames: 60 fps. Loudness: damage > kill > block > state (gain ranks with state), measured as peak over the 60 fps frames of sum(L*/100) over the pixels where the frame differs (dE76 > 5) from both the frame without the effect and the settled frame (the transient); unit full-value px.

| Effect | Family | Kind | Layer | Total ms (O-30 → now) | Reduce ms | Flashes/s full / reduce |
|---|---|---|---|---|---|---|
| `fx_commit` | T | state | board | 760 → **600** | 600 | 0 / 0 |
| `fx_hold` | M | state | board | 700 → **560** | 520 | 0 / 0 |
| `fx_pull` | M | state | board | 600 → **500** | 520 | 1 / 0 |
| `fx_rings_step` | M | state | board | 900 → **600** | 520 | 1 / 0 |
| `fx_shove` | M | state | board | 580 → **500** | 520 | 1 / 0 |
| `fx_shove_bump` | M | state | board | 540 → **480** | 480 | 1 / 1 |
| `fx_spin` | M | state | board | 820 → **600** | 520 | 1 / 1 |
| `fx_twist` | M | state | board | 660 → **540** | 520 | 1 / 0 |
| `fx_wave_enter` | M | state | board | 760 → **600** | 600 | 0 / 0 |
| `fx_brace_block` | P | block | board | 1060 → **600** | 600 | 1 / 1 |
| `fx_shield_block` | P | block | board | 920 → **600** | 600 | 1 / 1 |
| `fx_soak_take` | P | block | board | 960 → **600** | 600 | 1 / 1 |
| `fx_firewall_burn` | D | damage | board | 1000 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_gun_hit` | D | damage | board | 600 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_kill` | D | kill | board | 600 → **600** | in `reduce_motion` (one still per effect) | 0 / 0 |
| `fx_ricochet` | D | block | board | 500 → **500** | in `reduce_motion` (one still per effect) | 1 / 1 |
| `fx_ricochet_gold` | D | block | board | 500 → **500** | in `reduce_motion` (one still per effect) | 1 / 1 |
| `fx_strike` | D | damage | board | 700 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_trigger_hit` | D | damage | board | 900 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_hit_land` | H | damage | board | 700 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_hit_land_adjuster` | H | damage | board | 700 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_hit_land_worm` | H | damage | board | 700 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_hp_through` | H | damage | hud | 1150 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_shield_break` | H | damage | board | 700 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_slice_break` | H | damage | board | 650 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_slice_crack` | H | damage | board | 500 → **500** | in `reduce_motion` (one still per effect) | 2 / 0 |
| `fx_clear` | L | gain | board | 800 → **400** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_refund` | L | gain | hud | 900 → **600** | in `reduce_motion` (one still per effect) | 1 / 1 |
| `fx_repair_mend` | L | gain | board | 900 → **600** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_grow` | C | state | board | 650 → **400** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_ward_on` | C | state | board | 750 → **400** | in `reduce_motion` (one still per effect) | 1 / 0 |
| `fx_trace_add` | S | state | hud | 400 → **400** | 400 | 2 / 0 |
<!-- gen:fx_counts end -->

Each entry has: `id`, `family`, `title`, `kind` (damage, kill, block, state, gain: the loudness tier), `skins`, `total_ms`, `phases[{name, start_ms, end_ms, ease, ease_raw}]`, `reduce_phases` (MPST: timed phases; CDHL: empty, the reduce form is the timed `reduce_motion` text), `keyframes_ms`, `reduce_motion`, `layer` (`board` or `hud`), `source`, `max_flashes_per_s` (full) and `reduce_max_flashes_per_s`, the O-30 total (`total_ms_o30`), and the transient loudness per skin. Import it into Resources:
```gdscript
class_name CombatFxPhase extends Resource
@export var name: StringName
@export var start_ms: int
@export var end_ms: int
@export var ease: StringName        # LINEAR, IN_QUAD, IN_CUBIC, OUT_CUBIC, IN_OUT_CUBIC, OUT_BACK, IN_OUT_SINE, STEP, HOLD

class_name CombatFxTiming extends Resource
@export var id: StringName
@export var family: StringName      # M P C D H L S T
@export var kind: StringName        # damage kill block state gain (8.4 loudness order)
@export var layer: StringName = &"board"   # board: under the HUD and the hand; hud: only the three HUD-row effects (section 1)
@export var total_ms: int
@export var phases: Array[CombatFxPhase] = []
@export var reduce_phases: Array[CombatFxPhase] = []   # MPST from the data; CDHL authored from the reduce_motion text
@export var tier: int = 2            # VfxTier T2 (outcome, max 0.6 s) for every effect; no override
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

Raw ease strings in the data (generated):

<!-- gen:eases begin -->
Every raw ease string in the data, the code it maps to, and where it is used. A raw string with more than the code (an overshoot value, a step quantum, a wobble, gravity, a stagger, a width curve) needs a sampled Curve built from the string.

| Raw (source) | Code | Effects |
|---|---|---|
| `-` | `HOLD` | `fx_brace_block`, `fx_commit`, `fx_shield_block`, `fx_shove_bump`, `fx_soak_take`, `fx_trace_add`, `fx_wave_enter` |
| `ease-in cubic` | `IN_CUBIC` | `fx_hit_land` |
| `ease-in-out cubic` | `IN_OUT_CUBIC` | `fx_grow`, `fx_kill`, `fx_refund`, `fx_repair_mend`, `fx_shield_break`, `fx_slice_break`, `fx_ward_on` |
| `ease-in-out cubic, 20 ms stagger` | `IN_OUT_CUBIC` | `fx_hp_through` |
| `easeInOutCubic` | `IN_OUT_CUBIC` | `fx_commit`, `fx_hold`, `fx_pull`, `fx_rings_step`, `fx_shove`, `fx_spin`, `fx_twist`, `fx_wave_enter` |
| `sine` | `IN_OUT_SINE` | `fx_clear`, `fx_ricochet`, `fx_strike` |
| `sine in/out` | `IN_OUT_SINE` | `fx_gun_hit` |
| `sine, once` | `IN_OUT_SINE` | `fx_hit_land_adjuster`, `fx_hp_through` |
| `easeInQuad` | `IN_QUAD` | `fx_brace_block`, `fx_shield_block`, `fx_shove_bump`, `fx_soak_take` |
| (no ease given in the source; norm_timings reads it as LINEAR) | `LINEAR` | `fx_firewall_burn`, `fx_gun_hit`, `fx_hit_land`, `fx_hit_land_adjuster`, `fx_hit_land_worm`, `fx_kill`, `fx_repair_mend`, `fx_ricochet_gold`, `fx_shield_break`, `fx_slice_break`, `fx_slice_crack`, `fx_strike`, `fx_trigger_hit` |
| `linear` | `LINEAR` | `fx_brace_block`, `fx_clear`, `fx_firewall_burn`, `fx_gun_hit`, `fx_hold`, `fx_hp_through`, `fx_kill`, `fx_pull`, `fx_ricochet`, `fx_ricochet_gold`, `fx_rings_step`, `fx_shield_block`, `fx_shove`, `fx_shove_bump`, `fx_slice_break`, `fx_slice_crack`, `fx_soak_take`, `fx_spin`, `fx_strike`, `fx_twist` |
| `linear (front to back)` | `LINEAR` | `fx_trigger_hit` |
| `ease-out back` | `OUT_BACK` | `fx_clear`, `fx_hit_land_worm`, `fx_kill`, `fx_strike` |
| `ease-out back (overshoot)` | `OUT_BACK` | `fx_gun_hit`, `fx_refund` |
| `ease-out back (strong)` | `OUT_BACK` | `fx_slice_break` |
| `easeOutBack 2.0` | `OUT_BACK` | `fx_brace_block`, `fx_shield_block` |
| `easeOutBack 2.2` | `OUT_BACK` | `fx_brace_block`, `fx_hold` |
| `ease-out cubic` | `OUT_CUBIC` | `fx_gun_hit`, `fx_hit_land`, `fx_hp_through`, `fx_kill`, `fx_refund`, `fx_ricochet`, `fx_ricochet_gold`, `fx_shield_break`, `fx_slice_crack`, `fx_strike`, `fx_ward_on` |
| `ease-out cubic + gravity` | `OUT_CUBIC` | `fx_shield_break` |
| `ease-out cubic rise, sine width` | `OUT_CUBIC` | `fx_repair_mend` |
| `easeOutCubic` | `OUT_CUBIC` | `fx_brace_block`, `fx_commit`, `fx_hold`, `fx_pull`, `fx_rings_step`, `fx_shove`, `fx_shove_bump`, `fx_soak_take`, `fx_spin`, `fx_twist`, `fx_wave_enter` |
| `easeOutCubic + 2 deg wobble` | `OUT_CUBIC` | `fx_shove_bump` |
| `step` | `STEP` | `fx_trace_add` |
| `step (2 frames)` | `STEP` | `fx_hit_land` |
| `step (2 frames, 55 % on the token)` | `STEP` | `fx_kill` |
| `step (4 frames, 40 % on the new mark)` | `STEP` | `fx_grow` |
| `step (4 frames, 50 % on the lozenge)` | `STEP` | `fx_ward_on` |
| `step 27 ms / easeOutCubic` | `STEP` | `fx_wave_enter` |
| `step 33 ms` | `STEP` | `fx_trace_add` |
<!-- gen:eases end -->

### 8.2 Runtime rules
- **Slot:** `WavesFxOverlay`, **under the HUD and the hand** (z 12.5, section 1; `docs/ART_BIBLE.md` 6.4; review 1.6). Only `fx_hp_through`, `fx_refund` and `fx_trace_add` (they land on HUD rows) use the second slot above the HUD (z 14). No effect draws above the hand.
- **Length:** every effect is VfxTier T2, 0.6 s or less, with no per-effect override (`docs/ART_BIBLE.md` 5.3; REVIEW_RESPONSE 2.11). The importer asserts it (13.1).
- **The resolve beat** (review 2.11) plays its effects as **concurrent tracks** in the HUD chain order, each at its own timing, and lasts under 4 s; **any input skips it**: the frame dissolves to the settled frame. The flash meter was run on the whole beat (full and reduce), not only per effect. Every flash also goes through `FlashLimiter.request()` (3 per second, `Settings.flash_limiter`). The beat as rendered (`effects/resolve_beat.gif`, `timings_MPST.json` `resolve_beat`):

<!-- gen:beat begin -->
**3800 ms against a 4000 ms limit** (skin neutral). Skip: any input: the frame dissolves (easeInOutCubic) to the settled frame in skip_ms; no on-screen word (open question for the designer); 200 ms. Order: concurrent tracks in the HUD chain order (SEND IT, 1 TWIST, 2 TRIGGER, 4 GUNS, 3 BRACE + 5 LANDS, 6 RINGS STEP, W4 enters); every effect at its own designer's timing, each <= 600 ms.

| Track | Effect | Family | Start ms | Length ms | End ms | What |
|---|---|---|---|---|---|---|
| commit | `fx_commit` | T | 0 | 600 | 600 | SEND IT: pencil burns into paint |
| twist | `fx_twist` | M | 420 | 540 | 960 | 1 TWIST: ring +1 turns one sector |
| trace_add | `fx_trace_add` | S | 600 | 400 | 1000 | 2 TRIGGER: Trace 3 -> 4 |
| trigger_hit | `fx_trigger_hit` | D | 760 | 600 | 1360 | 2 TRIGGER: hits Packet 1 (s3, s4) |
| kill_p1 | `fx_kill` | D | 1000 | 600 | 1600 | 2 TRIGGER: Packet 1 dies |
| refund | `fx_refund` | L | 1100 | 600 | 1700 | 2 TRIGGER: refund, RAM 2 -> 3 |
| gun_hit | `fx_gun_hit` | D | 1300 | 600 | 1900 | 4 GUNS: s0 shot 1 on Worm 2 |
| gun_adj | `fx_gun_hit` | D | 1360 | 600 | 1960 | 4 GUNS: s2 TURRET on the Adjuster |
| ricochet_gold | `fx_ricochet_gold` | D | 1420 | 500 | 1920 | 4 GUNS: s4 2 shots warded (Packet 6) |
| kill | `fx_kill` | D | 1560 | 600 | 2160 | 4 GUNS: s0 shot 2, Worm 2 dies |
| shield_block | `fx_shield_block` | P | 1900 | 600 | 2500 | 5 LANDS: Worm 3 on s1 SHIELD, absorbed 2 |
| brace_block | `fx_brace_block` | P | 1900 | 600 | 2500 | 3 BRACE / 5 LANDS: Worm 3 on s2, braced 3 |
| soak_take | `fx_soak_take` | P | 1930 | 600 | 2530 | 5 LANDS: s1 soaked 1 (under the plate) |
| clear | `fx_clear` | L | 2400 | 400 | 2800 | 5 LANDS: THROUGH 0 |
| settle | `(none)` | - | 2640 | 200 | 2840 | board hand-off: ring NOW clears |
| rings_step | `fx_rings_step` | M | 2800 | 600 | 3400 | 6 RINGS STEP |
| wave_enter | `fx_wave_enter` | M | 3200 | 600 | 3800 | 6 W4 enters |

Flash over the whole beat: `{"full": {"whole_frame": 0, "track_boxes": 1, "tiles": {"240": 2, "120": 2, "60": 3}, "beat": 3, "skips": 3, "passes": true}, "reduce": {"whole_frame": 0, "track_boxes": 0, "tiles": {"240": 1, "120": 2, "60": 2}, "beat": 2, "skips": 2, "passes": true}}`.

**Not to ship:** ring +1 drawn one sector back from SEND IT until Twist turns it (f2 holds ring +1 where Twist leaves it): a RULES question (REVIEW_RESPONSE "Shove bump, Twist render"); the strip and the GIF caption say so.
Kill colour: {"kill_p1": {"token": [624.7571906056955, 769.4300789255503], "radius_px": 90, "settled_frame_px": {"GAIN": 56, "FOCUS": 0, "LIME": 0, "CELL_PINK": 588}, "peak_added_px": {"GAIN": 0, "FOCUS": 0, "LIME": 0, "CELL_PINK": 2044}}, "kill": {"token": [292.9291279553569, 502.1509423702948], "radius_px": 90, "settled_frame_px": {"GAIN": 68, "FOCUS": 0, "LIME": 0, "CELL_PINK": 400}, "peak_added_px": {"GAIN": 0, "FOCUS": 0, "LIME": 0, "CELL_PINK": 1456}}}.
Gif: {"width": 640, "height": 360, "caption_px": 20, "fps": 30.0, "frames": 136, "bytes": 1017714}.
<!-- gen:beat end -->

- **Reduce motion:** when `Settings.reduce_motion` is set, play `reduce_phases` (MPST) or the timed `reduce_motion` text (CDHL). Every reduce form drops travel, overshoot, sparks and glitch steps; state changes become short dissolves (each effect's length in Appendix A).

- **Determinism:** effects are views. Their random bits (shards, sparks, glitch rows, the bits FX) use a local `RandomNumberGenerator` seeded from `hash(effect_id, unit_id, sector)`. That keeps headless captures stable. Never use the global `randf` (rule 2 in spirit).
- **The post-state comes from the game.** An effect ends on the next `WavesState` drawn by the board, never on a painted end frame. Examples: the grow chevron, the empty cell after a kill, the ward. That is the same rule the art followed (real generator renders as post-states).

### 8.3 Event to effect map (game-v2 event types)
These are the types found in `scripts/core/waves_*.gd`. Rows marked *infer* come from the played action, not an event.

| Source | Effect(s) |
|---|---|
| play `Spin2`, `Spin3`, `Nudge` (*infer*) | `fx_spin` (turn = amount x 60°, plus a 3° settle) |
| play `Twist` | `fx_twist` |
| play `Pull` / `Shove` (blocked) | `fx_pull` / `fx_shove` (`fx_shove_bump`; it draws no HP change; the HP rule is a RULES question, open, section 14) |
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

### 8.4 Family looks (what each draws; must keep; `effects/NOTES_MPST.md` and `NOTES_CDHL.md`, rebuild 2026-11-03)
- **M motion:**
  - **no print echoes** (retired in the rebuild: on the shared loudness meter the echo copies were the loudest light of every motion effect);
  - the arrow is one solid line, never dashed: a 3 px core with a 2.5 px ink casing and an 11 px open head. On spin, twist, shove, rings step and Hold it is a stub (`ARROW_STUB`) that runs ahead of the mover and is eaten when the mover arrives; pull and the bump keep their short whole arrow;
  - colour by owner (VISUAL_PLAN E, R51): cards (spin, twist, pull, shove, bump, the commit ping) are CELL_PINK; the clock (rings step, Hold's slide) is SCHEDULE and the Hold stamp is the clock's gunmetal; the wave feed is neutral ENAMEL; the corp hue moves only as the `fx_wave_enter` scan line that draws the new cell edges (DR-6). Yellow never appears in resolve.
- **P protect:** everything on the **P stock** (`p_stock`, section 3), never the card bone PAPER. The shield plate is small, on the trim band; the brace is four clamp brackets on the wedge corners and a small stamp that slams to size; the sparks are P stock. The flat wedge tint and the SOAK wash are retired; SOAK stays a mark (the soak funnel, DR-5). No starburst, no red, no glow.
- **S system:** the glitch shader (5.7), one glitch band per 33 ms step.
- **T commit:**
  - pencil yellow becomes pink along each mark in route order, with a narrow white-hot burn edge: a Line2D gradient whose offset is tweened along a per-mark distance-along-path;
  - then a pink ping at the route end.
- **C corp:** one clean vector scan line with an ink key, in the skin's own `c_scan_ink` (section 7), then one flat 4-frame flash on the new mark only. BOSS_GOLD for the ward. No slab, no texture, no trail; never pink and never the clock's colours.
- **D damage:** the player-owned comic hit frame: a painted pink tracer (a tapered ribbon with an ink key), an ink-keylined CELL_PINK starburst with a white core, converging white speed lines cut at the tower rim, and flat vector shards. Kills are in the cause colour. No Ben-Day.
- **H harm:**
  - misregistered red print: the X-only halftone flood (5.8; crossed marks, never round dots);
  - black krackle with a red 2 px offset (sprites);
  - the red stencil X;
  - slice-wide, with the icon seat (r 37) clear except on shield_break and slice_break; the broken shield is the P-stock plate in shards.
- **L life:** the only soft glow, with additive blend and small radius:
  - brush strokes, plus signs, a painted check, four-point sparkles;
  - GAIN on dark; mint with an ink key on the green REPAIR wedge;
  - the RAM coin in NET_CYAN. L ranks with the state changes.
- **No family** draws dashed or dotted lines (trails are one continuous tapered ribbon), uses the needle, or adds cross-hatch (an effect resolves hatch into a gone socket or a dark pip). Pink stays the player's; gold is the boss's.
- **Loudness order** (review 2.10), measured on 60 fps frames, every skin:

<!-- gen:loudness begin -->
Rule: damage > kill > block > state (gain ranks with state). Two meters, one per designer set (same metric):

| Set | Skin | Passes | Tier boundaries (quietest of the louder kind > loudest of the quieter kind) |
|---|---|---|---|
| cdhl | neutral | yes | damage 2816.8 (`fx_hit_land`) > kill 1813.2 (`fx_kill`); kill 1813.2 (`fx_kill`) > block 1393.4 (`fx_shield_block`); block 885.2 (`fx_ricochet_gold`) > state 699.9 (`fx_repair_mend`) |
| cdhl | solace | yes | damage 2816.8 (`fx_hit_land`) > kill 1816.4 (`fx_kill`); kill 1816.4 (`fx_kill`) > block 1393.4 (`fx_shield_block`); block 885.6 (`fx_ricochet_gold`) > state 699.9 (`fx_repair_mend`) |
| cdhl | meridian | yes | damage 2816.8 (`fx_hit_land`) > kill 1812.5 (`fx_kill`); kill 1812.5 (`fx_kill`) > block 1393.4 (`fx_shield_block`); block 885.4 (`fx_ricochet_gold`) > state 699.9 (`fx_repair_mend`) |
| mpst | neutral | yes | damage 2816.8 (`fx_hit_land`) > kill 1813.2 (`fx_kill`); kill 1813.2 (`fx_kill`) > block 1676.8 (`fx_brace_block`); block 841.0 (`fx_soak_take`) > state 761.3 (`fx_hold`) |
| mpst | solace | yes | damage 2816.8 (`fx_hit_land`) > kill 1816.4 (`fx_kill`); kill 1816.4 (`fx_kill`) > block 1678.2 (`fx_brace_block`); block 841.0 (`fx_soak_take`) > state 768.0 (`fx_hold`) |
| mpst | meridian | yes | damage 2816.8 (`fx_hit_land`) > kill 1812.5 (`fx_kill`); kill 1812.5 (`fx_kill`) > block 1677.6 (`fx_brace_block`); block 841.0 (`fx_soak_take`) > state 761.4 (`fx_hold`) |
<!-- gen:loudness end -->

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
| Re-top | Digits, labels, tags, badges, tickets, the clock's band and the label plates draw back on top of the hover marks (with the dim applied where they fall outside the lit mask) |

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
| `WavesSpinner._draw_unit`, `_draw_pips`, `_draw_chevrons`, `_draw_barrier` | `UnitCellLayer` + `BoardMarkLayer` | Cell fills from `CombatLookData` (4.3) |
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
   - `RoomGradeData` (Appendix C);
   - their tests (13.1, 13.3);
   - schema smoke updated, and a DECISIONS entry for the new data classes (rule 8).
2. **Layout:** `WavesFight` goes full screen at 1080p plate coordinates × 2/3. `WavesSpinner` becomes a facade with empty child layers. Hit-test parity tests pass on the new radii.
3. **Room:** graded room textures plus the shader fallback.
4. **Corp rings:** the `corp_ring` shader for neutral, then Solace and Meridian; rim, crests, token frames and tickets; the neutral cell fills.
5. **Schedule band:** the gunmetal clock, the live step, HOLD plates, digits with punched holes.
6. **Tower:** the sheet bake (6.1), `TowerView`, the hatch shader, HP ring, pips, brace and soak.
7. **Board marks:** the time grammar, landing arcs, chevrons, tags, tickets, and the arrowed outline helper. Add the draw log, the draw asserts and the collision test here.
8. **Hand and cards:** the atlas (6.2), Labels and the rules bar, the `card_state` shader, the fan layout and the r 455 assert.
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
| `test_combat_look_data.gd` | `CombatLookData.validate()` is empty. Every token equals section 3, the HOT/COLD/FAR colours equal `port/skin_tables.json` `time_grade`, the clock colours equal 4.4 and the cell fills equal 4.3 (golden, within 1/255). |
| `test_combat_corp_skin.gd` | All 3 skins pass `validate()`. **No skin colour equals a game-mark token** (the clock, harm, harm_up, soak, pink, plan_yellow, focus_lime, the enamel grades, the cell fills). No retired field exists (section 7). The `.tres` values equal section 7 (golden). |
| `test_combat_fx_timings.gd` | All effects of `port/fx_timings.json` load. Every phase has `0 <= start <= end <= total_ms`; every total, phase end and reduce phase is at most the cap; no per-effect override; `tier` is T2 for every effect; only the three HUD-layer effects have `layer = hud`. `max_flashes_per_s <= 3`. `FlashLimiter.stream_is_safe(flash_events)` holds for each effect and for the sequenced resolve beat of the E10-like golden fight, and the sequenced beat ends before its limit. |
| `test_waves_board_hit.gd` | `hit_test` and `sector_at` on the new radii match the old semantics (unit, slice, cell, Adjuster orbit) on fixture states |
| `test_waves_board_draw_asserts.gd` | From the draw log, for fixture states (`tests/fixtures/waves_golden`): chevrons solid/hollow = `hit` / growth; diamonds per sector = HP through; k dots = turns ahead; soak and clamp marks; hatch cause colours; pips match HP. The generator ran 63/63, 49/49 and 24/24 on its plates. |
| `test_waves_board_collisions.gd` | Mark rects (digits, labels, tags, badges, tickets, hover leader) do not overlap each other or the occluders (the clock's band, HOLD and +N plates, hand). Badge vs band = 0. Hand min radius ≥ 455. The leader may cross the band once. |
| `test_waves_no_dashes.gd` | A grep of `scripts/ui/waves*` and `shaders/combat/` finds no `draw_dashed_line` and no dotted helpers. The draw log has 0 dash entries. |
| `test_waves_preview_equals_result.gd` | Already present in spirit (`WavesFight.preview_mismatches` must stay 0). Extend it to hover ghosts: the ghost state equals the session's plan state. |
| `test_waves_hover_dim.gd` | With a lit mask, a dimmed pixel equals `(g + (c - g) * 0.45) * 0.40` within 2/255 (shader run through a SubViewport in headless with a dummy renderer; skip if no renderer). Hand modulate 0.70, UI modulate 0.62. |

### 13.2 Capture checks (windowed, through `python tools/run_windowed.py --log <file> -- <godot args>`, never a bare windowed godot)
- **Plate parity:** capture p1, p2, p2b and p3 on the neutral skin, and p1 and p2b on Solace (and Meridian as the proof), at 1920x1080, from a fixture that reproduces `state_e10.json`. Use these metrics; pixel identity is not expected:
  - squint (1/16 box downscale, 1 px blur, Rec709, loud above 0.38): mean, p95 and loud share within ±10 % of `final/checks.json`;
  - the pixel halves of the 13.3 checks (a cell contrast, b value order, c cap height on the frame, e hand clearance, the dot-run finder), against the thresholds there;
  - the tower-zone loud share and the pink share in the enemy zone r 214-500 are **reported, not gated** (13.3; open questions 5 and 7 in section 14). The 2026-11-02 bars (tower zone at most 50 %, pink at most 0.3 %) are not met by the rebuilt board and wait for the designer.
- **Room:** the room region mean L* and p95 per 13.3 ("room grade"). The step6-1 room squint bars are retired with step6-1.
- **Effects:** per effect, and for the whole resolve beat, record 60 fps frames and run the art's flash method (`effects/NOTES_CDHL.md`, `NOTES_MPST.md`; the Python meter is `fx_cdhl/src/fxk_lib.flash_check`). The bar is at most 3 flashes per second, and both reduce-motion and full motion must pass. Run the transient loudness meter too: the order in 8.4 must hold on every skin.
- **Hover:** h01-h11 against `hover/checks.json`; lit/dim luma ratio 1.20-1.86 (from the 2026-11-02 hover set; see section 14, item 9).

### 13.3 The art's checks and their GUT equivalents (generated)

<!-- gen:checks begin -->
Every check the art ran on the published plates, its rule (as `final/checks.json` states it), what it measured, and its GUT-test equivalent. A pixel-level check stays a capture check (13.2); its data-level half is the GUT test.

| Check | Rule | Threshold | Measured on the plates | GUT equivalent |
|---|---|---|---|---|
| rb a: cell contrast | glass mean luminance occupied / the BRIGHTEST single empty cell of the same ring (each skin-probe cell and each empty cell on the plate) >= 3.0, per ring and per covered sector; live and dying units gated (dimmed = hover dim, ghosts: reported); marks, token disc, HP tray and tracers cut out.  The Adjuster HP track: 0 px under its diamond plate or the guns layer | ratio >= 3.0 | all 15 plates pass; ring NOW occupied L* 42.7-43.3; lowest ratio per skin 3.17, 3.32, 4.12 | `test_waves_cell_contrast.gd`: for each skin and ring, the composited occupied fill over the brightest empty fill (section 4.3 data) >= `cell_ratio_min` |
| rb b: value order | p95 L* per family region; A.1 chain SEND IT > T HOT marks > P tower > P hand (rest) > E cells occupied (glass) > E cells empty (glass); K below the tower, K median in L* 45-55; token discs below HOT marks; every E / K / T / N mark class (HP ticks, Adjuster HP and plate, badges, sector digits, ring tags, bezel labels, tickets, token discs, COLD, FAR, plan): p99 at least 1 under the HOT p95, and every E / K mark p95 at least 1 under the tower p95; room (x >= 1100, y >= 420, r > 505, UI / hand / hover tag and the UI scrim slabs cut out) mean L* 28-34 with its p95 below the ring-NOW occupied glass p95 (live cells; L* 40 when no ring-NOW cell is live) | chain holds, margin 1.0 L* | 0 failures on 15 plates; ring NOW glass p95 reference L* 40.0-51.8 | `test_combat_look_values.gd`: clock fill L* in `clock_L`, slice inks in `slice_ink_L`, K type and CREAM_HP at `e_mark_L` / `k_type_L` ± `mark_margin`, cell tint chroma <= `cell_tint_max_chroma`; the pixel order itself is a capture check (13.2) |
| rb c: cap height | cap height (font H box x px) of every text draw >= 16 px at 1080p; card text at the hand scale; the parked hover tag text is reported, not gated; any text drawn outside the hooked drawers fails the check | >= 16 px | 1296 text draws, 0 fail; smallest cap 16.1 px | `test_waves_text_caps.gd`: every Label in the combat scene (instanced headless): font cap height of "H" x the node's scale at 1080p >= `cap_min_px` (card Labels at the hand scale) |
| rb d: palette dE76 | dE76 >= 15: token pairs; slice inks, card type plates, skin hue inks vs the tokens they sit next to; HOT / COLD marks vs the measured cell colours | >= 15 | 178-233 pairs per plate; lowest dE76 17.3 | `test_combat_palette_de.gd`: the same pair groups computed in Lab from `CombatLookData`, the skins' inks and the card types >= `de_min` |
| rb e: hand clearance | hand pixels under SEND IT / UNDO: 0; lifted card over a sibling card cost hex or rules line: 0 px | 0 px | hand under SEND IT / UNDO 0 / 0 px; lifted card over a sibling's cost hex / rules 0 / 0 px (9 pairs measured) | `test_waves_hand_layout.gd`: card rects (fan, lift, slot-0 shift) against the SEND IT / UNDO rects and each sibling's cost-hex and rules rects: 0 overlap |
| stage 2: hand margin, ticket glyphs | 2.7: hand bottom (alpha >= 128) at least 12 px above y = 1080; 2.14: every kind glyph on the three wave tickets has an ink height of 16 px or more and p90 L* within 4 of the K type value (L* 84, the same full value on every ticket; time is on the ticket edge and pips) | as the rule | hand margin 12-15 px; ticket glyph ink height 23-25 px, p90 L* 86.3-87.8 | `test_waves_hand_layout.gd` (lowest card pixel vs y 1080); `test_combat_look_values.gd` (ticket glyph colour = `k_type` on every ticket, glyph size from the ticket layout) |
| hand vs board | no hand pixel (alpha >= 128) inside wheel radius 455 of the board centre (536, 540), and 0 px over any board mark, tape or plate | as the rule | min hand radius 457.7 px; 0 px inside | `test_waves_board_collisions.gd` (hand min radius) |
| draw asserts | game-mark asserts from the draw log | all pass | 744 / 744 | `test_waves_board_draw_asserts.gd` |
| mark collisions, occlusion | marks x marks; marks x occluders | 0 px | 0 px; 0 px | `test_waves_board_collisions.gd` |
| dash and dot audit | dashed_line_calls / dotted_mark_calls count draw calls; pixel_dot_runs (O-30) finds, on the rendered pixels, chains of 5 or more small spots (/DoG/ > 14, area 3-70 px) with even spacing (CV <= 0.18, 3.5-16 px), same size and colour and a smooth path, after dropping 2-D halftone fields; params in dot_audit.py | 0 | dashed calls 0, dotted calls 0, pixel dot runs 0 | `test_waves_no_dashes.gd` (source grep and draw log); the pixel dot-run finder is a capture check |
| card type plates | type word vs its plate | TOWER >= 4.5, WAVE >= 4.5 | TOWER 5.87:1, WAVE 8.94:1 | `test_combat_palette_de.gd` (WCAG ratio from the card type colours) |
| effects | cap, overrides, layer, beat, flashes | <= 600 ms; 0 overrides; HUD layer only fx_hp_through, fx_refund, fx_trace_add; beat < 4000 ms; <= 3 flashes/s | longest 600 ms; 0 overrides; beat 3800 ms; flash {"full": {"whole_frame": 0, "track_boxes": 1, "tiles": {"240": 2, "120": 2, "60": 3}, "beat": 3, "skips": 3, "passes": true}, "reduce": {"whole_frame": 0, "track_boxes": 0, "tiles": {"240": 1, "120": 2, "60": 2}, "beat": 2, "skips": 2, "passes": true}} | `test_combat_fx_timings.gd`: 32 effects load; every total, phase end and reduce phase <= `cap_ms`; no override; only the three HUD-layer effects ask for the HUD slot; the sequenced beat ends before `limit_ms`; `FlashLimiter.stream_is_safe` on each effect and on the beat |
| effect loudness order | damage > kill > block > state (gain ranks with state) | order holds | 6 of 6 meters pass | capture check (13.2): the transient meter on 60 fps captures |
| room grade | L* 28-34 (rb_checks room region) | L* [28.0, 34.0] | mean L* 31.8-32.5, p95 L* 38.1-38.1 on 9 rooms; all pass: True | `test_room_grade_data.gd`: `RoomGradeData` equals `backdrop/grade.json` (version, every room, every parameter); the L* gate is a capture check |
| squint, tower zone (reported, not gated) | loud share (0-1) of the tower zone r <= 212; target < 0.50 (O-29 fix 9) is NOT met on p1 / p2 / p3: see final/NOTES.md "2026-11-04 gate 1"; reported, not gated | reported | loud share 57.0-68.7 % over 15 plates | capture check, reported only (open question, section 14) |
| corp: pink in the enemy zone, clock match (reported) | pink share in r 214-500; the clock pixels equal across skins | reported | pink 1.39-1.39 %; clock match 97.0-100.0 % | capture check, reported |

All-pass flags (`final/checks.json` `all_pass`): `draw_asserts` True, `collisions` True, `occlusion` True, `hand` True, `dashes` True, `pixel_dot_runs` True, `rb_a_cell_contrast` True, `rb_b_value_order` True, `rb_c_cap_height` True, `rb_d_palette` True, `rb_e_hand` True, `stage2_hand_margin` True, `stage2_tickets` True.
<!-- gen:checks end -->

---

## 14. Open questions and risks

Rulings already made are not open: DR-1..DR-10 (`VISUAL_PLAN.md`), the `docs/ART_BIBLE.md` 2.4 and 3.14 notes, and the art-pass calls of `REVIEW_RESPONSE.md` (tower loudness by value order, card colours, corp skin, effect layer, effect lengths, movement arrows) are part of this spec.

**Open, for the designer (or the GDD):**
1. **Names (0.2):** Jammer vs `glitch`, `halo`, Firewall vs `scorch`, the Hold card vs the SET dial, and the `bug` card have no settled art mapping. The designer or build must answer before those cells, cards and effects are wired.
2. **Shove bump HP (RULES, REVIEW_RESPONSE S3):** round 2 said both units lose a tick; E10 has no such rule, so `fx_shove_bump` draws no HP change. The GDD or game-v2's rule decides.
3. **Twist render (RULES, REVIEW_RESPONSE S3):** the resolve beat draws ring +1 one sector back from SEND IT until Twist turns it (`resolve_beat.not_to_ship`, 8.2). Not a shipping reference for ring +1 during the Twist track until the designer rules.
4. **D4 scope:** "not until this board passes" (AD review section 5; REVIEW_RESPONSE). What D4 then covers is open.
5. **Tower squint vs ink value (VISUAL_PLAN A.1):** the tower-zone loud share is over the O-29 fix 9 target of 50 % on p1, p2 and p3 (13.3); the value order (rb b) holds. Which one governs the tower is the designer's call; until then it is reported, not gated.
6. **Skip word:** the resolve-beat skip has no on-screen word (`effects/NOTES_MPST.md`, Not done 2).
7. **Pink in the enemy zone:** measured on the rebuilt board above the 2026-11-02 bar of 0.3 % (13.3). Reported, not gated, until the bar is restated for the rebuilt board.

**Not done (known defects, not leftovers):**

8. **Thin 1 px ring and band lines** peak at L* 95-100 and are not gated (`final/NOTES.md`, "2026-11-04 gate 1", Not done).
9. **Hover (section 9)** carries the 2026-11-02 hover numbers. The `hover/` set is being rebuilt in another session; section 9 is not regenerated from it here.
10. **P stock is not a token in `corp/src/rb_tokens.py`.** It lives in `fxk_lib.P_STOCK` and the MPST constants (one value, two sources) until its owner adds it.
11. **The beat's pre-state:** Packet 1 is never seen alive (p2 already draws it trigger-dead), and the Adjuster shot has no HP-tick change (`effects/NOTES_MPST.md`, Not done 3 and 4).
12. **Latent effects** with no E10 source were drawn on stand-in marks: strike, the steel ricochet, firewall_burn, the hit_land Adjuster variant and repair_mend. Check them against real game numbers once wired.
13. **`corp/src` is order-dependent:** rendering Solace or Meridian p3 after p1_clean in one process drew a wrong TWIST glyph. Each bake runs one plate per process (6) until it is fixed.
14. **Documents that still disagree** (other owners' files, not edited here): `VISUAL_PLAN.md` B still lists L8 dotted, and G still gives the M echoes, the P plate "over the wedge's outer 40 percent" and white block sparks; `cards/src_snapshot/card_render.py` is older than `corp/src/card_render.py` (6.2).

**Risks:**

15. **Baked lit edges rotate during a spin** (4.6). Accepted for the turn. If it reads wrong, bake 12 rotation steps or move the highlight into a shader.
16. **Meridian** stays hibernated (A-112). Its skin ships as a proof only. The stencilled numbers are not drawn.
17. **The tower sheet bake (6.1)** is specified but was not run in this pass.
18. **Game-v2 has moved** past `b09f9b9d`. Re-read the waves views at build's head before starting.

---

## Appendix A. Effect timings (generated from `port/fx_timings.json`)

<!-- gen:fx_appendix begin -->
| id | fam | kind | layer | total ms | phases (name start-end ease) | reduce ms | reduce motion | flashes/s full / reduce |
|---|---|---|---|---|---|---|---|---|
| `fx_commit` | T | state | board | 600 | SEND IT press, hold 0-60 HOLD; burn front runs the marks 60-400 IN_OUT_CUBIC; ping at the route end 400-520 OUT_CUBIC; board, HUD and hand step preview to resolve 400-600 IN_OUT_CUBIC | 600 | No burn front and no ping: the marks cross-fade yellow to pink over 300 ms, then the board, the HUD and the hand step to resolve over 300 ms. | 0 / 0 |
| `fx_hold` | M | state | board | 560 | stamp slams 0-100 OUT_BACK; stamp hands over to the printed HOLD glyph 100-200 LINEAR; band turns over, arrow stub runs the slot 100-420 IN_OUT_CUBIC; arrow fades 420-560 LINEAR | 520 | No stamp slam and no wipe: the arrow appears (100 ms) and the band dissolves to the new schedule over 300 ms; the arrow fades (120 ms). | 0 / 0 |
| `fx_pull` | M | state | board | 500 | anticipate: arrow draws 0-90 OUT_CUBIC; slide 59 px 90-400 IN_OUT_CUBIC; settle back 2 px, arrow fades 400-500 OUT_CUBIC | 520 | The arrow appears (100 ms), the cell dissolves from ring +2 to ring +1 over 300 ms, the arrow fades (120 ms). | 1 / 0 |
| `fx_rings_step` | M | state | board | 600 | anticipate: tape arrow draws 0-100 OUT_CUBIC; spiral: -57 px, +120 deg 100-480 IN_OUT_CUBIC; settle: arrow fades 480-600 LINEAR | 520 | No spiral: the arrow stub appears (100 ms), every cell dissolves from its old place to its new one over 300 ms, the arrow fades (120 ms). | 1 / 0 |
| `fx_shove` | M | state | board | 500 | anticipate: arrow draws 0-90 OUT_CUBIC; slide 62 deg 90-400 IN_OUT_CUBIC; settle back 2 deg, arrow fades 400-500 OUT_CUBIC | 520 | The arrow stub appears (100 ms), the cell dissolves into the next sector over 300 ms, the arrow fades (120 ms). | 1 / 0 |
| `fx_shove_bump` | M | state | board | 480 | anticipate: arrow draws 0-90 OUT_CUBIC; slide toward the edge 90-200 IN_QUAD; contact: bump line, starbursts, shards 200-320 OUT_CUBIC; spring back 200-380 OUT_CUBIC; arrow and bump line fade 380-480 LINEAR | 480 | No slide and no starbursts: the arrow and the bump line on the shared edge appear for 380 ms and fade; the cell never moves. | 1 / 1 |
| `fx_spin` | M | state | board | 600 | anticipate: arrow draws, gun preview fades 0-100 OUT_CUBIC; turn 183 deg 100-500 IN_OUT_CUBIC; settle back 3 deg, arrow gone 500-600 OUT_CUBIC | 520 | No sweep: the arrow stub appears whole (100 ms), the tower dissolves from 0 to 180 deg over 300 ms (easeInOut), the arrow fades (120 ms). Icons and hub as in full motion. | 1 / 1 |
| `fx_twist` | M | state | board | 540 | anticipate: arrows draw 0-90 OUT_CUBIC; turn 61.5 deg 90-430 IN_OUT_CUBIC; settle back 1.5 deg, arrows fade 430-540 OUT_CUBIC | 520 | The arrow stubs appear whole (100 ms), the ring dissolves from 0 to 60 deg over 300 ms, the arrows fade (120 ms). | 1 / 0 |
| `fx_wave_enter` | M | state | board | 600 | feed arrow lights, ticket lifts 0-80 STEP; ticket rides into the entry 80-360 IN_OUT_CUBIC; cells scan in, glyphs drop 300-480 OUT_CUBIC; queue moves up one slot 360-540 IN_OUT_CUBIC; settled 540-600 HOLD | 600 | No travel: the W4 ticket fades out, the new cells fade in with their outlines and glyphs, and W5 / W6 cross-fade one slot right, all over 300 ms. | 0 / 0 |
| `fx_brace_block` | P | block | board | 600 | lane draws in 0-80 OUT_CUBIC; clamp brackets close (1.12 to 1.0) 60-180 OUT_BACK; chevrons run the lane 80-260 IN_QUAD; chevrons crumple on the bar 260-330 LINEAR; stamp slams on the arc glyph (1.2 to 1.0) 330-400 OUT_BACK; hold 400-460 HOLD; clamp, bar, lane and stamp lift off (the printed glyph stays) 460-600 LINEAR | 600 | No closing or crumple motion: lane, clamp, bar, the crumpled chevrons and the stamp appear over 300 ms with no hard shadow and dissolve over 300 ms (measured 1 flash per s, as full motion; with a 200 ms appear it counted 2); the board's own brace glyph and brace edge stay. | 1 / 1 |
| `fx_shield_block` | P | block | board | 600 | chevrons arrive 0-160 IN_QUAD; plate slams (1.2 to 1.0) 110-170 OUT_BACK; impact: stop dead, sparks 160-280 LINEAR; hold 280-440 HOLD; plate lifts off 440-600 LINEAR | 600 | No slam and no sparks: the plate, its ticks and the two chevrons stopped at the plate edge appear over 150 ms (linear), hold 100 ms, and dissolve over 350 ms (linear); no hard shadow in reduce motion. Measured: this form counts 1 flash per s, as full motion (the 0-200 / 300-600 form counted 2). | 1 / 1 |
| `fx_soak_take` | P | block | board | 600 | overflow chevron arrives 0-120 IN_QUAD; funnel draws in 80-220 OUT_CUBIC; chevron shrinks into the mouth 220-320 LINEAR; pip fills 300-420 OUT_CUBIC; hold, flow scrolls 420-470 LINEAR; funnel and pip fill lift off 470-600 LINEAR | 600 | No travel: the funnel and the filled pip appear over 200 ms with the flow chevrons still, hold, and dissolve over 300 ms. The overflow chevron is not shown. | 1 / 1 |
| `fx_firewall_burn` | D | damage | board | 600 | ring0 0-160 LINEAR; ring1 60-220 LINEAR; ring2 120-280 LINEAR; ticks 220-220 LINEAR; embers 380-600 LINEAR | in `reduce_motion` (one still per effect) | All three bands appear at full height at once, no flicker, hold 300 ms, fade 200 ms. | 1 / 0 |
| `fx_gun_hit` | D | damage | board | 600 | tracer 0-80 OUT_CUBIC; burst 80-140 OUT_BACK; speed_lines 80-300 IN_OUT_SINE; shards 100-420 OUT_CUBIC; tick 140-230 LINEAR; out 300-520 LINEAR | in `reduce_motion` (one still per effect) | Tracer and burst appear at full size for 300 ms, then fade 200 ms; no speed lines, no shards; the tick goes gone on the same frame. | 1 / 0 |
| `fx_kill` | D | kill | board | 600 | flare 17-50 STEP; burst 34-100 OUT_BACK; speed_lines 34-240 LINEAR; shards 50-460 OUT_CUBIC; empty 160-380 IN_OUT_CUBIC; out 300-520 LINEAR | in `reduce_motion` (one still per effect) | No flare: a 30 % pink-tint disc holds on the token for 200 ms while the burst shows; the cell empties with a 220 ms fade. | 0 / 0 |
| `fx_ricochet` | D | block | board | 500 | tracer 0-80 OUT_CUBIC; glint 80-200 IN_OUT_SINE; sparks 80-380 OUT_CUBIC; out 220-380 LINEAR | in `reduce_motion` (one still per effect) | Tracer and glint shown still for 300 ms; no sparks. | 1 / 1 |
| `fx_ricochet_gold` | D | block | board | 500 | tracer 0-80 OUT_CUBIC; streak 80-280 OUT_CUBIC; ring 80-200 LINEAR; out 240-460 LINEAR | in `reduce_motion` (one still per effect) | Tracer and the full streak shown still for 300 ms. | 1 / 1 |
| `fx_strike` | D | damage | board | 600 | slash 0-90 OUT_CUBIC; burst 90-150 OUT_BACK; speed_lines 90-300 IN_OUT_SINE; shards 100-420 OUT_CUBIC; ticks 150-240 LINEAR; out 340-560 LINEAR | in `reduce_motion` (one still per effect) | Slash and burst shown full at once for 300 ms, fade 200 ms; no speed lines or shards. | 1 / 0 |
| `fx_trigger_hit` | D | damage | board | 600 | ignite 0-240 LINEAR; burst_s3 120-460 LINEAR; burst_s4 240-580 LINEAR; route_out 420-600 LINEAR | in `reduce_motion` (one still per effect) | Route shown painted at once; the two bursts appear together for 300 ms, no speed lines. | 1 / 0 |
| `fx_hit_land` | H | damage | board | 600 | chevrons 0-80 IN_CUBIC; frame_flash 80-114 STEP; flood 80-200 OUT_CUBIC; krackle 100-440 LINEAR; flood_out 300-560 LINEAR; pip 200-200 LINEAR | in `reduce_motion` (one still per effect) | No chevron travel or krackle: the flood holds at 80 % density for 300 ms and fades; the pip goes dark on the same frame. | 1 / 0 |
| `fx_hit_land_adjuster` | H | damage | board | 600 | as_parent 0-600 LINEAR; gold_flash 80-170 IN_OUT_SINE | in `reduce_motion` (one still per effect) | As the parent; the gold rim shows as a thin outline, no flash. | 1 / 0 |
| `fx_hit_land_worm` | H | damage | board | 600 | as_parent 0-600 LINEAR; hook 140-200 OUT_BACK | in `reduce_motion` (one still per effect) | As the parent; the hook appears without overshoot. | 1 / 0 |
| `fx_hp_through` | H | damage | hud | 600 | lift 0-140 OUT_CUBIC; flight 60-460 IN_OUT_CUBIC; slap 400-520 IN_OUT_SINE; dark 440-580 LINEAR | in `reduce_motion` (one still per effect) | No flight: the six hatched segments go dark in a 200 ms fade, no slap. | 1 / 0 |
| `fx_shield_break` | H | damage | board | 600 | load 0-90 OUT_CUBIC; crack 20-90 LINEAR; split 100-100 LINEAR; shards 100-460 OUT_CUBIC; flood 110-260 OUT_CUBIC; krackle 110-500 LINEAR; dark 160-420 IN_OUT_CUBIC; pips 260-260 LINEAR | in `reduce_motion` (one still per effect) | No shard flight or krackle: the plate shows split in place (shards offset 55 %) for 300 ms; flood at 70 %; the wedge darkens in one 300 ms fade. | 1 / 0 |
| `fx_slice_break` | H | damage | board | 600 | flood 0-360 LINEAR; frame_flash 30-64 LINEAR; stamp 100-170 OUT_BACK; blackout 130-400 IN_OUT_CUBIC; halftone 170-450 LINEAR; pips 220-220 LINEAR | in `reduce_motion` (one still per effect) | No flood or overshoot: black-out, X and halftone fade in together over 300 ms. | 1 / 0 |
| `fx_slice_crack` | H | damage | board | 500 | flood 0-420 LINEAR; frame_flash 30-64 LINEAR; crack 50-220 OUT_CUBIC; tip 50-260 LINEAR; krackle 40-400 LINEAR; pip 180-180 LINEAR | in `reduce_motion` (one still per effect) | No flood pulse or tip spark: the crack draws in 150 ms linear. | 2 / 0 |
| `fx_clear` | L | gain | board | 400 | check 0-100 OUT_BACK; glow 100-360 LINEAR; sparkles 100-360 IN_OUT_SINE | in `reduce_motion` (one still per effect) | No stamp, glow or sparkles: the check shows at once. | 1 / 0 |
| `fx_refund` | L | gain | hud | 600 | pop 0-90 OUT_BACK; flight 90-400 IN_OUT_CUBIC; light 400-600 OUT_CUBIC | in `reduce_motion` (one still per effect) | No flight: the coin fades at the refund mark (150 ms) and the RAM slot and tab show at once. | 1 / 1 |
| `fx_repair_mend` | L | gain | board | 600 | strokes 0-450 OUT_CUBIC; plus 80-560 LINEAR; pip_fill 260-400 IN_OUT_CUBIC; glow_out 380-600 LINEAR | in `reduce_motion` (one still per effect) | No strokes or glow: two static plus signs and the pip fills over 200 ms. | 1 / 0 |
| `fx_grow` | C | state | board | 400 | scan 0-133 IN_OUT_CUBIC; flash 133-200 STEP | in `reduce_motion` (one still per effect) | No scan or flash: the hollow chevron fades in over 200 ms (ease-in-out). | 1 / 0 |
| `fx_ward_on` | C | state | board | 400 | scan 0-133 IN_OUT_CUBIC; flash 133-200 STEP; ping 133-360 OUT_CUBIC | in `reduce_motion` (one still per effect) | No scan, flash or ping: the lozenge fades in over 200 ms. | 1 / 0 |
| `fx_trace_add` | S | state | hud | 400 | card glitch, 5 steps 0-166 STEP; pip pops, 3 steps; row glitch 166-266 STEP; settled 266-400 HOLD | 400 | No glitch bands: the fourth pip simply lights at 166 ms (one step, no scale). | 2 / 0 |

Phases with equal start and end are instant events at that time. Sources (md5): `timings_CDHL.json` `5da1a6d8434d70deab3be1a59c9b01bf`, `timings_MPST.json` `97367232db0a00269675b9e7392ce9ed`.
<!-- gen:fx_appendix end -->

## Appendix B. Corp skin material layers (generated from `port/skin_tables.json`)

<!-- gen:skin_appendix begin -->
Each material method of each skin, read from the generator source by `skin_tables.py` (AST of the method body: `acc.add`, `L.line` / `poly` / `ellipse` / `rect` / `glow`, and `for` loops over literal tables). `colour` is the evaluated value, `colour_expr` the source expression where it is not a constant. These are the layers `corp_ring.gdshader` and the 6.3 bakes reproduce.

**neutral** (`lw_skin.NeutralSkin`)
```
cell  lw_skin.py:20
    {"op": "add", "line": 23, "colour": "#283240", "alpha": "0.30"}
    {"op": "add", "line": 25, "colour": "#6E7C8E", "alpha": "(1 - sstep(0.0, 0.45, np.abs(((TH + 5) % 10) - 5) * RHO * 0.01745)) * 0.07"}
    {"op": "add", "line": 26, "colour": "#6E7C8E", "alpha": "(1 - sstep(0.0, 0.5, np.abs(((RHO - 214) % 9.5) - 4.75) - 4.25)) * 0.05"}
    {"op": "add", "line": 27, "colour": "#EBF2FA", "alpha": "np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 2 * 0.05"}
bezel  lw_skin.py:30
    {"op": "add", "line": 34, "colour": "#161B22", "alpha": "1.0"}
    {"op": "add", "line": 35, "colour": "#283240", "alpha": "0.45 + 0.25 * np.sin(np.pi * u)"}
    {"op": "add", "line": 36, "colour": "#DCE6F2", "alpha": "(0.5 + 0.5 * np.cos(2 * np.pi * RHO / 2.4)) * 0.035"}
    {"op": "add", "line": 37, "colour": "#FFFFFF", "alpha": "np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 3 * np.exp(-((u - 0.2) / 0.12) ** 2) * 0.10"}
    {"op": "add", "line": 39, "colour": "#BCC8D6", "alpha": "np.clip(lip, 0, 1) * 0.55"}
annulus  lw_skin.py:42
    {"op": "add", "line": 45, "colour": "#080B10", "alpha": "0.55"}
    {"op": "add", "line": 46, "colour": "#6E7C8E", "alpha": "(1 - sstep(0.0, 0.6, np.abs(((RHO - 424) % 8.0) - 4.0) - 3.6)) * 0.06"}
arcframe  lw_skin.py:60
    {"op": "add", "line": 63, "colour": "#1A212A", "alpha": "0.55"}
    {"op": "add", "line": 64, "colour": "#6E7C8E", "alpha": "(1 - sstep(0.0, 0.5, np.abs(((RHO - 200) % 5.0) - 2.5) - 2.2)) * 0.05"}
rim  lw_skin.py:49
    {"op": "add", "line": 54, "colour": "#748090", "alpha": "1.0", "colour_expr": "np.array(P['steel'], np.float32)[None, None] * k[..., None]"}
    {"op": "add", "line": 57, "colour": "#08090C", "alpha": "tick.astype(np.float32) * 0.55"}
rim_vector  lw_skin.py:68
    {"op": "line", "line": 70, "colour": "#0A0C10", "width": 1.6}
    {"op": "call", "line": 73, "call": "self.crest"}
crest  lw_skin.py:75
    {"op": "ellipse", "line": 79, "fill": "#08090C"}
    {"op": "ellipse", "line": 80, "fill": "#1E242E"}
    {"op": "ellipse", "line": 81, "outline": "#BCC8D6", "width": 1.3}
    {"op": "rect", "line": 82, "fill": "#BCC8D6"}
cell_detail  lw_skin.py:84
    {"op": "line", "line": 86, "colour": "#6D747E@120", "width": 1.0}
token_frame  lw_skin.py:88
    {"op": "ellipse", "line": 90, "fill": "#08090C"}
    {"op": "ellipse", "line": 91, "fill": "#525C68"}
    {"op": "ellipse", "line": 92, "outline": "#9AA5B1", "width": 1.0}
    {"op": "ellipse", "line": 93, "fill": "#08090C"}
disc_frame  lw_skin.py:95
    {"op": "ellipse", "line": 97, "fill": "#08090C"}
    {"op": "ellipse", "line": 98, "fill": "#525C68"}
    {"op": "ellipse", "line": 99, "fill": "#08090C"}
ticket  lw_skin.py:101
    {"op": "poly", "line": 105, "fill": "#1A2029@255"}
    {"op": "line", "line": 106, "colour": "#08090C", "width": 4.2}
    {"op": "line", "line": 107, "colour": ["#BCC8D6", "#737C88"], "width": 1.6}
```

**solace** (`cs_skin.Solace`)
```
cell  rb_patch.py:747
    {"op": "add", "line": 751, "colour": "#2C3634", "alpha": "0.30"}
    {"op": "add", "line": 753, "colour": "#96AAA0", "alpha": "(1 - sstep(0.0, 1.5, f2 - f1)) * 0.12"}
    {"op": "add", "line": 757, "colour": "#D2E1DA", "alpha": "(1 - sstep(0.0, 0.9, np.abs(g1 - rr))) * keep * 0.14"}
    {"op": "add", "line": 758, "colour": "#DCEBE4", "alpha": "np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 2 * 0.05"}
bezel  rb_patch.py:762
    {"op": "add", "line": 765, "colour": "#141A1A", "alpha": "1.0"}
    {"op": "add", "line": 766, "colour": "#2C3634", "alpha": "0.35 + 0.25 * np.sin(np.pi * u)"}
    {"op": "add", "line": 768, "colour": "#788C84", "alpha": "(1 - sstep(0.0, 1.4, f2 - f1)) * 0.10"}
    {"op": "add", "line": 770, "colour": "#4FA83A", "alpha": "np.clip(lip, 0, 1) * 0.85"}
annulus  rb_patch.py:774
    {"op": "add", "line": 776, "colour": "#0A0E0E", "alpha": "0.55"}
    {"op": "add", "line": 778, "colour": "#6E827A", "alpha": "(1 - sstep(0.0, 1.4, f2 - f1)) * 0.08"}
arcframe  rb_patch.py:782
    {"op": "add", "line": 784, "colour": "#161C1C", "alpha": "0.55"}
rim  cs_skin.py:220
    {"op": "add", "line": 225, "colour": "#B8DCCC", "alpha": "1.0", "colour_expr": "np.array(P['porcelain'], np.float32)[None, None] * k[..., None]"}
rim_vector  cs_skin.py:278
    {"op": "call", "line": 279, "call": "self.helix"}
    {"op": "call", "line": 282, "call": "self.crest"}
crest  cs_skin.py:284
    {"op": "ellipse", "line": 288, "fill": "#0A1812"}
    {"op": "ellipse", "line": 289, "fill": "#B8DCCC"}
    {"op": "ellipse", "line": 290, "outline": "#96B096", "width": 0.9}
    {"op": "line", "line": 293, "colour": "#4FA83A", "width": 1.7}
    {"op": "line", "line": 294, "colour": "#96FF46", "width": 1.9}
    {"op": "line", "line": 297, "colour": "#FFFFFF", "width": 0.9}
cell_detail  rb_patch.py:788
    {"op": "line", "line": 790, "colour": ["#459234@200", "#306527@130"], "width": 1.3}
token_frame  rb_patch.py:793
    {"op": "ellipse", "line": 796, "fill": "#080E0C"}
    {"op": "ellipse", "line": 797, "fill": "#606C68"}
    {"op": "line", "line": 798, "colour": "#96A29E", "width": 1.6}
    {"op": "ellipse", "line": 799, "fill": "#080E0C"}
    {"op": "ellipse", "line": 800, "fill": "#96FF46", "outline": "#080E0C", "width": 0.8}
disc_frame  rb_patch.py:803
    {"op": "ellipse", "line": 805, "fill": "#080E0C"}
    {"op": "ellipse", "line": 806, "fill": "#606C68"}
    {"op": "ellipse", "line": 807, "fill": "#080E0C"}
ticket  rb_patch.py:810
    {"op": "poly", "line": 813, "fill": "#1E2424@255"}
    {"op": "line", "line": 814, "colour": "#080E0C", "width": 4.4}
    {"op": "line", "line": 815, "colour": ["#96FF46", "#4FA83A"], "width": 1.8}
    {"op": "call", "line": 816, "call": "self.crest"}
```

**meridian** (`cs_skin.Meridian`)
```
cell  rb_patch.py:825
    {"op": "add", "line": 828, "colour": "#383430", "alpha": "0.30"}
    {"op": "call", "line": 829, "call": "self._rib"}
    {"op": "add", "line": 830, "colour": "#100E0C", "alpha": "(1 - rib) ** 2 * 0.16"}
    {"op": "add", "line": 831, "colour": "#C8C4BE", "alpha": "rib ** 3 * 0.07"}
bezel  rb_patch.py:835
    {"op": "add", "line": 838, "colour": "#1E1E20", "alpha": "1.0"}
    {"op": "add", "line": 839, "colour": "#464648", "alpha": "0.30 + 0.2 * np.sin(np.pi * u)"}
    {"op": "add", "line": 840, "colour": "#100E0C", "alpha": "(1 - self._rib(RHO, TH, 5.0)) ** 2 * 0.12"}
    {"op": "call", "line": 840, "call": "self._rib"}
    {"op": "add", "line": 843, "colour": "#0E0C0B", "alpha": "np.maximum(lip_in, lip_out) * 0.95"}
    {"op": "add", "line": 845, "colour": "#B0602C", "alpha": "lip_out * 0.90"}
annulus  rb_patch.py:849
    {"op": "add", "line": 851, "colour": "#121110", "alpha": "0.55"}
    {"op": "add", "line": 852, "colour": "#0E0C0A", "alpha": "(1 - self._rib(RHO, TH, 7.0)) ** 2 * 0.12"}
    {"op": "call", "line": 852, "call": "self._rib"}
arcframe  rb_patch.py:856
    {"op": "add", "line": 858, "colour": "#1E1C1A", "alpha": "0.55"}
rim  rb_patch.py:862
    {"op": "add", "line": 865, "colour": "#0E0C0B", "alpha": "1.0"}
    {"op": "add", "line": 869, "colour": "#B0602C", "alpha": "stripe * 0.94", "colour_expr": "np.array(MR['rust'], np.float32)[None, None] * k[..., None]"}
rim_vector  cs_skin.py:433
    {"op": "line", "line": 436, "colour": "#0A0807", "width": 1.6}
    {"op": "call", "line": 439, "call": "self.crest"}
crest  cs_skin.py:441
    {"op": "rect", "line": 445, "fill": "#0A0807"}
    {"op": "rect", "line": 446, "fill": "#1E1814"}
    {"op": "line", "line": 449, "colour": "#B0602C", "width": 1.9}
    {"op": "line", "line": 450, "colour": "#B0602C", "width": 1.5}
    {"op": "line", "line": 452, "colour": "#B0602C", "width": 1.6}
    {"op": "line", "line": 453, "colour": "#F0E6D6", "width": 0.9}
    {"op": "ellipse", "line": 454, "outline": "#F0E6D6", "width": 0.9}
    {"op": "for", "line": 455, "target": "(rx, ry)", "values": [[-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0], [1.0, 1.0]]}
    {"op": "ellipse", "line": 456, "fill": "#968C82"}
cell_detail  rb_patch.py:873
    {"op": "line", "line": 875, "colour": ["#A05728@200", "#66381B@130"], "width": 1.3}
    {"op": "call", "line": 882, "call": "self._rivet"}
token_frame  rb_patch.py:885
    {"op": "poly", "line": 888, "fill": "#0A0807"}
    {"op": "poly", "line": 889, "fill": "#5C5C60"}
    {"op": "line", "line": 891, "colour": "#96969C", "width": 1.5}
    {"op": "line", "line": 892, "colour": "#323236", "width": 1.5}
    {"op": "ellipse", "line": 893, "fill": "#0A0807"}
    {"op": "rect", "line": 897, "fill": "#B0602C", "outline": "#0A0807", "width": 0.8}
disc_frame  rb_patch.py:900
    {"op": "poly", "line": 903, "fill": "#0A0807"}
    {"op": "poly", "line": 904, "fill": "#5C5C60"}
    {"op": "ellipse", "line": 905, "fill": "#0A0807"}
ticket  rb_patch.py:908
    {"op": "poly", "line": 911, "fill": "#222122@255"}
    {"op": "line", "line": 912, "colour": "#0A0807", "width": 4.4}
    {"op": "line", "line": 913, "colour": ["#D88A4E", "#B0602C"], "width": 1.8}
    {"op": "call", "line": 915, "call": "self._rivet"}
```
<!-- gen:skin_appendix end -->

## Appendix C. Room grade parameters (generated from `backdrop/grade.json`)

<!-- gen:room_appendix begin -->
`backdrop/grade.json` version rb2-1. One row per parameter, one column per room.

| Parameter | bio | srv | gh | rec | lobby | event | shop | shop_meridian |
|---|---|---|---|---|---|---|---|---|
| `cx` | 1500.0 | 1500.0 | 1500.0 | 1500.0 | 1500.0 | 1500.0 | 1500.0 | 1500.0 |
| `cy` | 600.0 | 600.0 | 600.0 | 600.0 | 600.0 | 600.0 | 600.0 | 600.0 |
| `rx` | 330.0 | 330.0 | 330.0 | 330.0 | 330.0 | 330.0 | 330.0 | 330.0 |
| `ry` | 270.0 | 270.0 | 270.0 | 270.0 | 270.0 | 270.0 | 270.0 | 270.0 |
| `f0` | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| `f1` | 1.55 | 1.55 | 1.55 | 1.55 | 1.55 | 1.55 | 1.55 | 1.55 |
| `pf0` | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 | 10.0 |
| `pf1` | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| `hull_blur` | 0.4 | 0.4 | 0.4 | 0.4 | 0.4 | 0.4 | 0.4 | 0.4 |
| `mid_blur` | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 |
| `city_blur` | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 |
| `blur_reach` | 40.0 | 40.0 | 40.0 | 40.0 | 40.0 | 40.0 | 40.0 | 40.0 |
| `neon_chroma` | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | 0.9 |
| `city_chroma` | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 |
| `pivot` | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 |
| `hull_value` | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 |
| `city_value` | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 |
| `tone_lo` | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 |
| `tone_hi` | 0.38 | 0.38 | 0.38 | 0.38 | 0.38 | 0.38 | 0.38 | 0.38 |
| `tone_s` | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 | 0.09 |
| `tone_blur` | 14.0 | 14.0 | 14.0 | 14.0 | 14.0 | 14.0 | 14.0 | 14.0 |
| `tone_gmax` | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 | 3.5 |
| `tone_out` | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 | 0.45 |
| `tone_d0` | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 |
| `tone_d1` | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 |
| `knee` | 0.24 | 0.24 | 0.24 | 0.24 | 0.24 | 0.24 | 0.24 | 0.24 |
| `ceil` | 0.3502 | 0.35 | 0.3519 | 0.3547 | 0.3493 | 0.3496 | 0.3523 | 0.3518 |
| `haze` | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |
| `haze_out` | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| `haze_rgb` | [20, 18, 34] | [20, 18, 34] | [20, 18, 34] | [20, 18, 34] | [20, 18, 34] | [20, 18, 34] | [20, 18, 34] | [20, 18, 34] |
| `sp0` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| `sp1` | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 |
| `vignette` | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| `v0` | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 |
| `v1` | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 | 2.6 |
| `board_falloff` | 0.08 | 0.08 | 0.08 | 0.08 | 0.08 | 0.08 | 0.08 | 0.08 |
| `bx0` | 700.0 | 700.0 | 700.0 | 700.0 | 700.0 | 700.0 | 700.0 | 700.0 |
| `bx1` | 1250.0 | 1250.0 | 1250.0 | 1250.0 | 1250.0 | 1250.0 | 1250.0 | 1250.0 |
| `chroma` | 0.876 | 0.814 | 0.891 | 0.941 | 0.849 | 0.836 | 0.826 | 1.05 |
| `contrast` | 1.12 | 1.12 | 1.12 | 1.12 | 1.12 | 1.24 | 1.12 | 1.12 |
| `pink_chroma` | 0.55 | 0.55 | 0.55 | 0.55 | 0.55 | 0.42 | 0.55 | 0.55 |
| `spill_rgb` | [77, 106, 68] | [65, 107, 85] | [88, 103, 61] | [94, 101, 69] | [69, 109, 59] | [88, 101, 81] | [84, 104, 68] | [106, 97, 70] |
| `hue_lo` | null | null | null | null | null | null | null | 88.0 |
| `hue_hi` | null | null | null | null | null | null | null | 162.0 |
| `hue_f` | null | null | null | null | null | null | null | 14.0 |
| `hue_to` | null | null | null | null | null | null | null | 20.0 |
| `hue_amt` | null | null | null | null | null | null | null | 0.88 |

Hull polygons (plate px):

- `bio`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `srv`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `gh`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `rec`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `lobby`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `event`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `shop`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
- `shop_meridian`: [[1195, 488], [1465, 338], [1792, 523], [1792, 672], [1512, 808], [1195, 632]]
<!-- gen:room_appendix end -->

## Appendix D. Card text anchors and drawing code (generated from `port/cards_atlas.json` and `card_render.py`)

<!-- gen:card_appendix begin -->
| Card | Type | Cost | Trace | Mult | Text draws (role "text" @ design x, y) | Rules bar quad (design px) |
|---|---|---|---|---|---|---|
| Nudge | TOWER | 1 | 0 | 1 | mult "×1" @ 139, 107; title "NUDGE" @ 87.5, 144.5; type_word "TOWER" @ 85.5, 174.4; rules "Turn the" @ 80, 200; rules "tower 1" @ 80, 221.5; cost "1" @ 21.5, 22.2 | (42.875, 236.5) (119.125, 234.5) (117.125, 239.5) (40.875, 241.5) |
| Spin2 | TOWER | 1 | 0 | 2 | mult "×2" @ 139, 107; title "SPIN 2" @ 87.5, 144.5; type_word "TOWER" @ 85.5, 174.4; rules "Turn the" @ 80, 200; rules "tower 2" @ 80, 221.5; cost "1" @ 21.5, 22.2 | (42.875, 236.5) (119.125, 234.5) (117.125, 239.5) (40.875, 241.5) |
| Spin3 | TOWER | 1 | 0 | 3 | mult "×3" @ 139, 107; title "SPIN 3" @ 87.5, 144.5; type_word "TOWER" @ 85.5, 174.4; rules "Turn the" @ 80, 200; rules "tower 3" @ 80, 221.5; cost "1" @ 21.5, 22.2 | (42.875, 236.5) (119.125, 234.5) (117.125, 239.5) (40.875, 241.5) |
| Brace | TOWER | 1 | 0 |  | title "BRACE" @ 87.5, 144.5; type_word "TOWER" @ 85.5, 174.4; rules "Block a slice" @ 80, 206; cost "1" @ 21.5, 22.2 | (21.812, 219.5) (140.188, 217.5) (138.188, 222.5) (19.812, 224.5) |
| Strike | TOWER | 1 | 0 |  | title "STRIKE" @ 87.5, 144.5; type_word "TOWER" @ 85.5, 174.4; rules "Hit a unit for 2" @ 80, 206; cost "1" @ 21.5, 22.2 | (14.062, 219.5) (147.938, 217.5) (145.938, 222.5) (12.062, 224.5) |
| Firewall | WAVE | 2 | 2 |  | title "FIREWALL" @ 87.5, 144.5; type_word "WAVE" @ 85.5, 174.4; rules "Burn 2 units" @ 80, 206; cost "2" @ 21.5, 22.2; trace "+2" @ 133, 17.6 | (23.25, 219.5) (138.75, 217.5) (136.75, 222.5) (21.25, 224.5) |
| Pull | WAVE | 0 | 1 |  | title "PULL" @ 87.5, 144.5; type_word "WAVE" @ 85.5, 174.4; rules "Pull a unit in" @ 80, 206; cost "0" @ 21.5, 22.2; trace "+1" @ 133, 17.6 | (22, 219.5) (140, 217.5) (138, 222.5) (20, 224.5) |
| Shove | WAVE | 2 | 2 |  | title "SHOVE" @ 87.5, 144.5; type_word "WAVE" @ 85.5, 174.4; rules "Slide a unit 1" @ 80, 206; cost "2" @ 21.5, 22.2; trace "+2" @ 133, 17.6 | (19.5, 219.5) (142.5, 217.5) (140.5, 222.5) (17.5, 224.5) |
| Twist | WAVE | 0 | 0 |  | title "TWIST" @ 87.5, 144.5; type_word "WAVE" @ 85.5, 174.4; rules "Turn one" @ 80, 200; rules "ring 1" @ 80, 221.5; cost "0" @ 21.5, 22.2 | (51.25, 236.5) (110.75, 234.5) (108.75, 239.5) (49.25, 241.5) |
| Hold | WAVE | 0 | 0 |  | title "HOLD" @ 87.5, 144.5; type_word "WAVE" @ 85.5, 174.4; rules "Pause" @ 80, 200; rules "the wave" @ 80, 221.5; cost "0" @ 21.5, 22.2 | (36.625, 236.5) (125.375, 234.5) (123.375, 239.5) (34.625, 241.5) |
| Trigger | WAVE | 1 | 1 |  | title "TRIGGER" @ 87.5, 144.5; type_word "WAVE" @ 85.5, 174.4; rules "Resolve a unit" @ 80, 206; cost "1" @ 21.5, 22.2; trace "+1" @ 133, 17.6 | (14.938, 219.5) (147.062, 217.5) (145.062, 222.5) (12.938, 224.5) |

Played liner text (every card): played_name "NUDGE" @ 88, 157, ShareTechMono-Regular 21 px, track 1, rot 0°, #96948D; played_word "PLAYED" @ 88, 183, ShareTechMono-Regular 21 px, track 1, rot 0°, #B3B0A9.
Liner art numbers: {"tear": 1.7, "rim": 2.2, "fill": ["#15121A", 0.86], "paper_v": 0.62, "word_px": 21.0, "word_v": [0.62, 0.74]}.

Card text plates, verbatim from `corp/src/card_render.py` `render_base` (md5 `7603fd56141bb72dffd0bba9ab3c8058`):

Line 932:
```python
    # ---------------- title: a slanted ink plate, white title, black keyline, hard offset drop
    tb = poly(cv, [(0, 130), (CW, 124), (CW, 160), (0, 166)]) * cm
    cv.paint(extrude(cv, tb, 0, 3.0) * (1 - tb) * cm, hx('78105C'))
    cv.paint(tb, INK)
    cv.paint(poly(cv, [(0, 130), (CW, 124), (CW, 127), (0, 133)]) * cm, T['col'])   # type colour runs the top edge of the plate
    nm = spec['nm']
    px = _fit_title(nm)
    if nowords:
        cv.paint(poly(cv, [(30, 140), (CW - 30, 136), (CW - 30, 152), (30, 156)]) * cm, WHITE)
    else:
        m = text(cv, nm, 87.5, 144.5, px, ANTON, 1.0, 0.0, -2.0)
        cv.paint(shift(cv, m, 2.6, 3.0), PINK)
        cv.paint(grow(cv, m, 1.4), INK)      # the keyline: INK on the ink plate, white fill inside it
        cv.paint(m, WHITE)
```

Line 946:
```python
    # ---------------- type plate (the colour behind WAVE / TOWER)
    tw = 92 if fam == 'TOWER' else 80
    ty = 174.0
    pl = poly(cv, [(88 - tw / 2 - 5, ty - 11), (88 + tw / 2 + 5, ty - 12.5), (88 + tw / 2 - 3, ty + 11), (88 - tw / 2 - 11, ty + 12.5)])
    cv.paint(extrude(cv, grow(cv, pl, 1.6), 2.2, 2.8), INK)
    cv.paint(grow(cv, pl, 1.6), INK)
    cv.paint(pl, T['col'])
    cv.paint(poly(cv, [(88 - tw / 2 - 11, ty + 12.5), (88 + tw / 2 - 3, ty + 11), (88 + tw / 2 - 4, ty + 6), (88 - tw / 2 - 10, ty + 7.5)]), T['dk'], 0.0)
    if nowords:
        cv.paint(poly(cv, [(88 - tw / 2 + 6, ty - 3), (88 + tw / 2 - 8, ty - 4), (88 + tw / 2 - 8, ty + 4), (88 - tw / 2 + 6, ty + 5)]), INK)
    else:
        m = text(cv, fam, 85.5, ty + 0.4, 19, ANTON, 2.2, 0.0, -1.2)
        cv.paint(m, T['text'])
```

Line 959:
```python
    # ---------------- rules text (2026-11-03 stage 2: never shrunk below the 16 px cap floor; a long line wraps to two, rules_lines())
    lines = rules_lines(spec['txt'])
    cxr = RULES_CX
    for li, (s_, ly, wt) in enumerate(lines):
        last = li == len(lines) - 1
        if nowords:
            cv.paint(poly(cv, [(cxr - wt / 2, ly - 4), (cxr + wt / 2, ly - 5), (cxr + wt / 2, ly + 5), (cxr - wt / 2, ly + 6)]) * cm, INK)
            continue
        if last:
            b0, b1 = RULES_BAR[len(lines) - 1]
            bar = poly(cv, [(cxr - wt / 2 - 4, ly + b0 + 2.0), (cxr + wt / 2 + 6, ly + b0), (cxr + wt / 2 + 4, ly + b1 - 2.0), (cxr - wt / 2 - 6, ly + b1)])
            cv.paint(bar * cm, PINK)
        m = text(cv, s_, cxr, ly, RULES_PX, PLEX, 0.0, 0.0, -0.8)
        cv.paint(m, INK)
```

Line 979:
```python
    # ---------------- cost badge: cyan hexagon (RAM)
    cost_badge(cv, spec, nowords)
```

Line 981:
```python
    # ---------------- loud tab (+N Trace): violet eye plate, top right
    if spec['loud']:
        lx, ly2 = CW - 54, 17
        bxp = poly(cv, [(lx - 21, ly2 - 12), (lx + 18, ly2 - 14), (lx + 22, ly2 + 12), (lx - 18, ly2 + 14)])
        cv.paint(extrude(cv, grow(cv, bxp, 2.4), 2.2, 2.8), INK)
        cv.paint(grow(cv, bxp, 2.4), INK)
        cv.paint(bxp, TRACE_VIOLET)
        e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
        cv.paint(e2, WHITE)
        cv.paint(circle(cv, lx - 9, ly2, 2.9), INK)
        if nowords:
            for q in range(int(spec['loud'])):
                cv.paint(stroke(cv, [(lx + 6 + q * 7, ly2 - 7), (lx + 7 + q * 7, ly2 + 8)], 3.0), WHITE)
        else:
            cv.paint(text(cv, '+' + str(spec['loud']), lx + 11, ly2 + 0.6, 21, ANTON), WHITE)
```

`_liner`, `corp/src/card_render.py:1048`:
```python
def _liner(R, nowords, spec):
    cv = Cv(R)
    seed = sum(ord(c) for c in spec['name'])
    rect_ = [(3, 3), (CW - 3, 3), (CW - 3, CH - 3), (3, CH - 3)]
    torn = poly(cv, jag(cv, rect_, LINER_TEAR, seed, n=5))
    body =np.clip(1.0 - grow(cv, 1.0 - torn, LINER_RIM), 0, 1)          # the torn shape shrunk by the rim width
    cv.paint(torn, LINER_FILL[0], LINER_FILL[1])
    paper = np.array([0xF2, 0xEE, 0xE4], np.float32) / 255.0
    rim = np.clip(torn - body, 0, 1)
    cv.paint(rim, paper * LINER_PAPER_V)
    fib = np.clip(body - np.clip(1.0 - grow(cv, 1.0 - body, 1.0), 0, 1), 0, 1)                  # fibre edge just inside the tear
    cv.paint(fib * (halftone(cv, np.full_like(fib, 0.35), 2.6, 30) > 0.5), paper * LINER_PAPER_V, 0.55)
    gm = glyph(cv, spec['g'], 54, CW / 2, CH / 2 - 14)
    cv.paint(gm, paper * 0.46)
    if not nowords:
        # O-29 fix 4 kept: the played slot keeps the card name above PLAYED, mono small caps
        cv.paint(text(cv, spec['nm'], CW / 2, CH / 2 + 32, LINER_WORD_PX, MONO, 1.0), paper * LINER_WORD_V[0])
        cv.paint(text(cv, 'PLAYED', CW / 2, CH / 2 + 58, LINER_WORD_PX, MONO, 1.0), paper * LINER_WORD_V[1])
    return cv.img()
```

`draw_card`, `corp/src/card_render.py:1069` (the state switch; the hover print and drop offsets of 5.5 are read from it):
```python
def draw_card(card, size, state='normal'):
    spec = _spec(card)
    if isinstance(state, str):
        state = dict(mode=state)
    mode = state.get('mode', 'normal')
    nowords = bool(state.get('nowords')) or mode == 'nowords'
    w = size[0] if isinstance(size, (tuple, list)) else size
    s = w / CW
    ss = 3 if s <= 1.5 else 2
    R = s * ss
    ck = (spec['name'], nowords, round(R, 3), json.dumps({k: spec[k] for k in ('cost', 'loud', 'txt', 'nm', 'fam')}))
    if mode == 'played':
        im = _liner(R, nowords, spec)
    else:
        if ck not in _BASE:
            if len(_BASE) > 40:
                _BASE.clear()
            _BASE[ck] = render_base(spec, nowords, R).img()
        im = _BASE[ck].copy()
        if mode == 'hover':
            # pink misregistered print behind the lifted card (silhouette incl. its drop), hard longer drop under it
            a = np.asarray(im)[..., 3].astype(np.float32) / 255.0
            sil = (a > 0.5).astype(np.float32)
            pk = ndi.shift(sil, (6 * R, -9 * R), order=0)
            sh = ndi.shift(sil, (11 * R, 7 * R), order=0)
            H, W = sil.shape
            base = np.zeros((H, W, 4), np.float32)
            base[..., :3] = np.array([8, 6, 14])
            base[..., 3] = sh * 0.55 * 255
            pkl = np.zeros((H, W, 4), np.float32); pkl[..., :3] = np.array([255, 61, 168]); pkl[..., 3] = pk * 255
            comp = Image.fromarray(base.astype(np.uint8), 'RGBA')
            comp.alpha_composite(Image.fromarray(pkl.astype(np.uint8), 'RGBA'))
            comp.alpha_composite(im)
            im = comp
        elif mode == 'unaffordable':
            im = _unaffordable(im)
            im.alpha_composite(unaffordable_marks(R, spec, nowords))
        elif state.get('dim'):
            im = _post_dim(im, float(state['dim']))
    out_w = int(round((CW + 2 * MARGIN) * s)); out_h = int(round((CH + 2 * MARGIN) * s))
    if mode == 'played':
        im = im.resize((out_w, out_h), Image.LANCZOS)
    else:
        im = im.resize((out_w, out_h), Image.LANCZOS)
    if not isinstance(size, (tuple, list)):
        pass
    return im
```
<!-- gen:card_appendix end -->
