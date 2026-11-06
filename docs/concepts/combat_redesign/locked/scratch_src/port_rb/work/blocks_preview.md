#### files
| File | What it is |
|---|---|
| `port/fx_timings.json` | 32 effects (T 1, M 8, P 3, D 7, H 7, L 3, C 2, S 1) merged from `effects/timings_CDHL.json` and `timings_MPST.json`; cap 600 ms with 0 per-effect overrides; the resolve beat 3800 ms against 4000 (section 8, Appendix A). Version port-2. |
| `port/skin_tables.json` | Tokens, marks, slice inks, card types, cell fills, the time grade, the gunmetal clock and the three skins with their material layers read from the generator source (sections 3, 4.3, 4.4, 7, Appendix B). Version port-2. |
| `port/cards_atlas.json`, `port/cards_proof.jpg` | The card atlas baked from the module that renders `final/card_sheet.jpg`: cell rects, every text anchor logged from the real draw call, the rules-bar quads, the state recipes; the proof shows art | worded | liner per card at the in-hand size (sections 4.8, 6.2, Appendix D). Version port-2. |
| `port/src/` | `norm_timings.py`, `skin_tables.py`, `bake_cards.py` make the three data files; `port_spec.py` writes every table and appendix of this spec from them (and from `backdrop/grade.json`, `backdrop/checks.json`, `final/checks.json`). Re-run all four after any change upstream; a hand edit inside a `gen:` block is overwritten. |

#### tokens
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
| `schedule` | #FF8C1A | 69.5 | The clock's LIVE step only: live cell edge, its chevrons, the rings-step and Hold motion (4.4) |
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

#### time_grade
Function: gramlib.grade: g = lum + (c - lum) * sat (lum Rec709 on 0-255), out = bed + (g - bed) * val; f1_board.grade2 replaces the threat red by the lifted COLD_CHEV / FAR_CHEV. bed #070912, sat [1.0, 0.45, 0.25], val [1.0, 0.7, 0.5] (HOT, COLD, FAR).

| Mark | HOT | COLD | FAR |
|---|---|---|---|
| `harm` | #FF6452 (L* 62.5) | #D9877C (L* 64.6) | #96767A (L* 52.8) |
| `enamel` | #D9E1EA (L* 89.2) | #9DA0A5 (L* 65.8) | #73757A (L* 49.2) |
| `k_type` | #CBD2DB (L* 83.9) | #93959B (L* 61.7) | #6B6D73 (L* 46.0) |
| `cream_hp` | #DBD1B7 (L* 84.0) | #989590 (L* 61.8) | #6D6D6E (L* 46.1) |

Bake these into the resource as three colours per mark; never compute them per frame.

#### room
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

#### room_appendix
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

#### cells
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

#### clock
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

#### cards
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

#### unaffordable
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

#### atlas
| File | Size | md5 | Opaque px | What |
|---|---|---|---|---|
| `cards_art_atlas.png` | 1696 x 1716 | `77250b4c0d4d006b9cbb87959eda875c` | 2105609 | normal state, art only: every word and the rules bar left out |
| `cards_ref_atlas.png` | 1696 x 1716 | `57f8431fd7bd068814521f9cf3393267` | 2105422 | the same with words and bar: what the Labels plus the bar must reproduce |
| `cards_liner_atlas.png` | 1696 x 1716 | `f1748b8fba783add5c009f471a553276` | 1860256 | the played-slot liner, art only (Godot labels the name and PLAYED) |

4 x 3 cells of **424 x 572** (the card 352 px wide = 2x design, plus 36 px margin each side), in `card_render.ORDER`. Sources: `corp/src/card_render.py` md5 `7603fd56141bb72dffd0bba9ab3c8058`, `final/card_sheet.jpg` md5 `87a5a6da7d076291a3fe8b481e80e200`. On screen at 1.1 the card is 193.6 px wide, so the atlas is 1.82x screen.

Note: cards/src_snapshot/card_render.py md5 b8a435c4aa055c85d45f4c42c8ac10ae is the card session's older snapshot (before the stage-2 NO RAM and rules-wrap change); the atlas follows corp/src.

#### skins
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

```

#### skin_appendix
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

#### fx_counts
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
| `fx_firewall_burn` | D | damage | board | 1000 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_gun_hit` | D | damage | board | 600 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_kill` | D | kill | board | 600 → **600** | in the text (text (reduce_motion)) | 0 / 0 |
| `fx_ricochet` | D | block | board | 500 → **500** | in the text (text (reduce_motion)) | 1 / 1 |
| `fx_ricochet_gold` | D | block | board | 500 → **500** | in the text (text (reduce_motion)) | 1 / 1 |
| `fx_strike` | D | damage | board | 700 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_trigger_hit` | D | damage | board | 900 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_hit_land` | H | damage | board | 700 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_hit_land_adjuster` | H | damage | board | 700 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_hit_land_worm` | H | damage | board | 700 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_hp_through` | H | damage | hud | 1150 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_shield_break` | H | damage | board | 700 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_slice_break` | H | damage | board | 650 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_slice_crack` | H | damage | board | 500 → **500** | in the text (text (reduce_motion)) | 2 / 0 |
| `fx_clear` | L | gain | board | 800 → **400** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_refund` | L | gain | hud | 900 → **600** | in the text (text (reduce_motion)) | 1 / 1 |
| `fx_repair_mend` | L | gain | board | 900 → **600** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_grow` | C | state | board | 650 → **400** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_ward_on` | C | state | board | 750 → **400** | in the text (text (reduce_motion)) | 1 / 0 |
| `fx_trace_add` | S | state | hud | 400 → **400** | 400 | 2 / 0 |

#### beat
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

#### loudness
Rule: damage > kill > block > state (gain ranks with state). Two meters, one per designer set (same metric):

| Set | Skin | Passes | Tier boundaries (quietest of the louder kind > loudest of the quieter kind) |
|---|---|---|---|
| cdhl | neutral | yes | damage 2816.8 (`fx_hit_land`) > kill 1813.2 (`fx_kill`); kill 1813.2 (`fx_kill`) > block 1393.4 (`fx_shield_block`); block 885.2 (`fx_ricochet_gold`) > state 699.9 (`fx_repair_mend`) |
| cdhl | solace | yes | damage 2816.8 (`fx_hit_land`) > kill 1816.4 (`fx_kill`); kill 1816.4 (`fx_kill`) > block 1393.4 (`fx_shield_block`); block 885.6 (`fx_ricochet_gold`) > state 699.9 (`fx_repair_mend`) |
| cdhl | meridian | yes | damage 2816.8 (`fx_hit_land`) > kill 1812.5 (`fx_kill`); kill 1812.5 (`fx_kill`) > block 1393.4 (`fx_shield_block`); block 885.4 (`fx_ricochet_gold`) > state 699.9 (`fx_repair_mend`) |
| mpst | neutral | yes | damage 2816.8 (`fx_hit_land`) > kill 1813.2 (`fx_kill`); kill 1813.2 (`fx_kill`) > block 1676.8 (`fx_brace_block`); block 841.0 (`fx_soak_take`) > state 761.3 (`fx_hold`) |
| mpst | solace | yes | damage 2816.8 (`fx_hit_land`) > kill 1816.4 (`fx_kill`); kill 1816.4 (`fx_kill`) > block 1678.2 (`fx_brace_block`); block 841.0 (`fx_soak_take`) > state 768.0 (`fx_hold`) |
| mpst | meridian | yes | damage 2816.8 (`fx_hit_land`) > kill 1812.5 (`fx_kill`); kill 1812.5 (`fx_kill`) > block 1677.6 (`fx_brace_block`); block 841.0 (`fx_soak_take`) > state 761.4 (`fx_hold`) |

#### fx_appendix
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
| `fx_firewall_burn` | D | damage | board | 600 | ring0 0-160 LINEAR; ring1 60-220 LINEAR; ring2 120-280 LINEAR; ticks 220-220 LINEAR; embers 380-600 LINEAR | in the text (text (reduce_motion)) | All three bands appear at full height at once, no flicker, hold 300 ms, fade 200 ms. | 1 / 0 |
| `fx_gun_hit` | D | damage | board | 600 | tracer 0-80 OUT_CUBIC; burst 80-140 OUT_BACK; speed_lines 80-300 IN_OUT_SINE; shards 100-420 OUT_CUBIC; tick 140-230 LINEAR; out 300-520 LINEAR | in the text (text (reduce_motion)) | Tracer and burst appear at full size for 300 ms, then fade 200 ms; no speed lines, no shards; the tick goes gone on the same frame. | 1 / 0 |
| `fx_kill` | D | kill | board | 600 | flare 17-50 STEP; burst 34-100 OUT_BACK; speed_lines 34-240 LINEAR; shards 50-460 OUT_CUBIC; empty 160-380 IN_OUT_CUBIC; out 300-520 LINEAR | in the text (text (reduce_motion)) | No flare: a 30 % pink-tint disc holds on the token for 200 ms while the burst shows; the cell empties with a 220 ms fade. | 0 / 0 |
| `fx_ricochet` | D | block | board | 500 | tracer 0-80 OUT_CUBIC; glint 80-200 IN_OUT_SINE; sparks 80-380 OUT_CUBIC; out 220-380 LINEAR | in the text (text (reduce_motion)) | Tracer and glint shown still for 300 ms; no sparks. | 1 / 1 |
| `fx_ricochet_gold` | D | block | board | 500 | tracer 0-80 OUT_CUBIC; streak 80-280 OUT_CUBIC; ring 80-200 LINEAR; out 240-460 LINEAR | in the text (text (reduce_motion)) | Tracer and the full streak shown still for 300 ms. | 1 / 1 |
| `fx_strike` | D | damage | board | 600 | slash 0-90 OUT_CUBIC; burst 90-150 OUT_BACK; speed_lines 90-300 IN_OUT_SINE; shards 100-420 OUT_CUBIC; ticks 150-240 LINEAR; out 340-560 LINEAR | in the text (text (reduce_motion)) | Slash and burst shown full at once for 300 ms, fade 200 ms; no speed lines or shards. | 1 / 0 |
| `fx_trigger_hit` | D | damage | board | 600 | ignite 0-240 LINEAR; burst_s3 120-460 LINEAR; burst_s4 240-580 LINEAR; route_out 420-600 LINEAR | in the text (text (reduce_motion)) | Route shown painted at once; the two bursts appear together for 300 ms, no speed lines. | 1 / 0 |
| `fx_hit_land` | H | damage | board | 600 | chevrons 0-80 IN_CUBIC; frame_flash 80-114 STEP; flood 80-200 OUT_CUBIC; krackle 100-440 LINEAR; flood_out 300-560 LINEAR; pip 200-200 LINEAR | in the text (text (reduce_motion)) | No chevron travel or krackle: the flood holds at 80 % density for 300 ms and fades; the pip goes dark on the same frame. | 1 / 0 |
| `fx_hit_land_adjuster` | H | damage | board | 600 | as_parent 0-600 LINEAR; gold_flash 80-170 IN_OUT_SINE | in the text (text (reduce_motion)) | As the parent; the gold rim shows as a thin outline, no flash. | 1 / 0 |
| `fx_hit_land_worm` | H | damage | board | 600 | as_parent 0-600 LINEAR; hook 140-200 OUT_BACK | in the text (text (reduce_motion)) | As the parent; the hook appears without overshoot. | 1 / 0 |
| `fx_hp_through` | H | damage | hud | 600 | lift 0-140 OUT_CUBIC; flight 60-460 IN_OUT_CUBIC; slap 400-520 IN_OUT_SINE; dark 440-580 LINEAR | in the text (text (reduce_motion)) | No flight: the six hatched segments go dark in a 200 ms fade, no slap. | 1 / 0 |
| `fx_shield_break` | H | damage | board | 600 | load 0-90 OUT_CUBIC; crack 20-90 LINEAR; split 100-100 LINEAR; shards 100-460 OUT_CUBIC; flood 110-260 OUT_CUBIC; krackle 110-500 LINEAR; dark 160-420 IN_OUT_CUBIC; pips 260-260 LINEAR | in the text (text (reduce_motion)) | No shard flight or krackle: the plate shows split in place (shards offset 55 %) for 300 ms; flood at 70 %; the wedge darkens in one 300 ms fade. | 1 / 0 |
| `fx_slice_break` | H | damage | board | 600 | flood 0-360 LINEAR; frame_flash 30-64 LINEAR; stamp 100-170 OUT_BACK; blackout 130-400 IN_OUT_CUBIC; halftone 170-450 LINEAR; pips 220-220 LINEAR | in the text (text (reduce_motion)) | No flood or overshoot: black-out, X and halftone fade in together over 300 ms. | 1 / 0 |
| `fx_slice_crack` | H | damage | board | 500 | flood 0-420 LINEAR; frame_flash 30-64 LINEAR; crack 50-220 OUT_CUBIC; tip 50-260 LINEAR; krackle 40-400 LINEAR; pip 180-180 LINEAR | in the text (text (reduce_motion)) | No flood pulse or tip spark: the crack draws in 150 ms linear. | 2 / 0 |
| `fx_clear` | L | gain | board | 400 | check 0-100 OUT_BACK; glow 100-360 LINEAR; sparkles 100-360 IN_OUT_SINE | in the text (text (reduce_motion)) | No stamp, glow or sparkles: the check shows at once. | 1 / 0 |
| `fx_refund` | L | gain | hud | 600 | pop 0-90 OUT_BACK; flight 90-400 IN_OUT_CUBIC; light 400-600 OUT_CUBIC | in the text (text (reduce_motion)) | No flight: the coin fades at the refund mark (150 ms) and the RAM slot and tab show at once. | 1 / 1 |
| `fx_repair_mend` | L | gain | board | 600 | strokes 0-450 OUT_CUBIC; plus 80-560 LINEAR; pip_fill 260-400 IN_OUT_CUBIC; glow_out 380-600 LINEAR | in the text (text (reduce_motion)) | No strokes or glow: two static plus signs and the pip fills over 200 ms. | 1 / 0 |
| `fx_grow` | C | state | board | 400 | scan 0-133 IN_OUT_CUBIC; flash 133-200 STEP | in the text (text (reduce_motion)) | No scan or flash: the hollow chevron fades in over 200 ms (ease-in-out). | 1 / 0 |
| `fx_ward_on` | C | state | board | 400 | scan 0-133 IN_OUT_CUBIC; flash 133-200 STEP; ping 133-360 OUT_CUBIC | in the text (text (reduce_motion)) | No scan, flash or ping: the lozenge fades in over 200 ms. | 1 / 0 |
| `fx_trace_add` | S | state | hud | 400 | card glitch, 5 steps 0-166 STEP; pip pops, 3 steps; row glitch 166-266 STEP; settled 266-400 HOLD | 400 | No glitch bands: the fourth pip simply lights at 166 ms (one step, no scale). | 2 / 0 |

Phases with equal start and end are instant events at that time. Sources (md5): `timings_CDHL.json` `5da1a6d8434d70deab3be1a59c9b01bf`, `timings_MPST.json` `97367232db0a00269675b9e7392ce9ed`.

#### card_appendix
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

#### checks
Every check the art ran on the published plates, its rule (as `final/checks.json` states it), what it measured, and its GUT-test equivalent. A pixel-level check stays a capture check (13.2); its data-level half is the GUT test.

| Check | Rule | Threshold | Measured on the plates | GUT equivalent |
|---|---|---|---|---|
| rb a: cell contrast | glass mean luminance occupied / the BRIGHTEST single empty cell of the same ring (each skin-probe cell and each empty cell on the plate) >= 3.0, per ring and per covered sector; live and dying units gated (dimmed = hover dim, ghosts: reported); marks, token disc, HP tray and tracers cut out.  The Adjuster HP track: 0 px under its diamond plate or the guns layer | ratio >= 3.0 | all 15 plates pass; ring NOW occupied L* 42.7-43.3; lowest ratio per skin 3.17, 3.32, 4.12 | `test_waves_cell_contrast.gd`: for each skin and ring, the composited occupied fill over the brightest empty fill (section 4.3 data) >= `cell_ratio_min` |
| rb b: value order | p95 L* per family region; A.1 chain SEND IT > T HOT marks > P tower > P hand (rest) > E cells occupied (glass) > E cells empty (glass); K below the tower, K median in L* 45-55; token discs below HOT marks; every E / K / T / N mark class (HP ticks, Adjuster HP and plate, badges, sector digits, ring tags, bezel labels, tickets, token discs, COLD, FAR, plan): p99 at least 1 under the HOT p95, and every E / K mark p95 at least 1 under the tower p95; room (x >= 1100, y >= 420, r > 505, UI / hand / hover tag and the UI scrim slabs cut out) mean L* 28-34 with its p95 below the ring-NOW occupied glass p95 (live cells; L* 40 when no ring-NOW cell is live) | chain holds, margin 1.0 L* | 0 failures on 15 plates; ring NOW glass p95 reference L* 40.0-51.8 | `test_combat_look_values.gd`: clock fill L* in `clock_L`, slice inks in `slice_ink_L`, K type and CREAM_HP at `e_mark_L` / `k_type_L` ± `mark_margin`, cell tint chroma <= `cell_tint_max_chroma`; the pixel order itself is a capture check (13.2) |
| rb c: cap height | cap height (font H box x px) of every text draw >= 16 px at 1080p; card text at the hand scale; the parked hover tag text is reported, not gated; any text drawn outside the hooked drawers fails the check | >= 16 px | 1296 text draws, 0 fail; smallest cap 16.1 px | `test_waves_text_caps.gd`: every Label in the combat scene (instanced headless): font cap height of "H" x the node's scale at 1080p >= `cap_min_px` (card Labels at the hand scale) |
| rb d: palette dE76 | dE76 >= 15: token pairs; slice inks, card type plates, skin hue inks vs the tokens they sit next to; HOT / COLD marks vs the measured cell colours | >= 15 | 178-233 pairs per plate; lowest dE76 17.3 | `test_combat_palette_de.gd`: the same pair groups computed in Lab from `CombatLookData`, the skins' inks and the card types >= `de_min` |
| rb e: hand clearance | hand pixels under SEND IT / UNDO: 0; lifted card over a sibling card cost hex or rules line: 0 px | 0 px | hand under SEND IT / UNDO 0 / 0 px; lifted over a sibling's cost or rules 9 cases | `test_waves_hand_layout.gd`: card rects (fan, lift, slot-0 shift) against the SEND IT / UNDO rects and each sibling's cost-hex and rules rects: 0 overlap |
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

#### mailbox_numbers
- Effects: 32, every one at most 600 ms (T2) with 0 overrides, drawn under the HUD and the hand except `fx_hp_through`, `fx_refund`, `fx_trace_add`.
- Resolve beat: 3800 ms against 4000, skip on any input in 200 ms; loudness order damage > kill > block > state (gain ranks with state) holds on every skin.
- One gunmetal clock on every corp: fill #6E7580 (L* 49.0), lip #969EAA (L* 64.8), groove #282C34 (L* 17.9); SCHEDULE #FF8C1A on the live step only.
- Corp skins: material plus corp hue on the rim, lip, crest and cell edges; neutral slate cell fills, `kind_gain` 1.0 everywhere; rooms neutral bio, solace bio, meridian shop.
- Room grade rb2-1; graded room mean L* 31.8-32.5.
- Plate checks: draw_asserts, collisions, occlusion, hand, dashes, pixel_dot_runs, rb_a_cell_contrast, rb_b_value_order, rb_c_cap_height, rb_d_palette, rb_e_hand, stage2_hand_margin, stage2_tickets all true; pink in the enemy zone 1.39-1.39 % and the tower-zone squint 57.0-68.7 % are reported, not gated.
- Card atlas: `cards_art_atlas.png` 1696 x 1716, `cards_ref_atlas.png` 1696 x 1716, `cards_liner_atlas.png` 1696 x 1716.
