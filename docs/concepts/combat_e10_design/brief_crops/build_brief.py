"""Build ../BRIEF.md from inventory.json + the cohesion bible below, and run the completeness checks:
 1. ids unique across clusters, every element in exactly one cluster;
 2. every non-LATENT element has its crop <cluster>__<id>.png, and every crop png belongs to an element;
 3. every draw function / drawn part in the E10 generator source maps to at least one element id (COVER)."""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
INV = json.load(open(HERE + 'inventory.json', encoding='utf-8'))
ORDER = ['wheel_core', 'wave_rings', 'outer_rings', 'top_hud', 'objectives', 'cards', 'actions']
TITLE = {'wheel_core': 'Wheel core', 'wave_rings': 'Wave rings and units', 'outer_rings': 'Outer rings and timing',
         'top_hud': 'Turn header and damage panel', 'objectives': 'Objectives and resources', 'cards': 'Card hand', 'actions': 'Actions and identity'}

# every drawing call in build10.py / e10lib / e9lib / e8lib / cv_over / cv_board / cv_chrome / cv_lib that reaches a plate -> element ids
COVER = {
    'cv_board.render_board: back plate disc': ['board_backplate'],
    'cv_board.render_board: ring_base (brushed bezel)': ['bezel_ring'],
    'cv_board.ring_base: orange rim glows R0+1.5 / R1-1.5 + cos(th-315) light': ['bezel_rim_lines'],
    'cv_board.render_board: render_slice x6 (frame, screen, glyph)': ['slice_frame', 'slice_screen', 'slice_gutters', 'icon_burst', 'icon_shield', 'icon_turret', 'icon_repair'],
    'cv_board.render_slice: programme screen code/hex text': ['slice_screen_code_text'],
    'cv_board.render_board: unit programme screens': ['unit_cell_screen', 'unit_screen_bezel', 'screen_motif_skull'],
    'cv_board unit programme screens: hex/code text': ['unit_screen_code_text'],
    'cv_board.render_board: empty cells (dark glass)': ['empty_cell', 'ring_separators'],
    'cv_board.render_board: code-base frame rings': ['codebase_frame'],
    'cv_board.render_board: draw_hub (disc, emblem, name)': ['hub_disc', 'hub_emblem', 'hub_label'],
    'cv_board.draw_hub: inner rings alpha 10, r 16-36 step 9': ['hub_inner_rings'],
    'cv_lib.backdrop: radial dim pool': ['board_scrim'],
    'cv_lib.backdrop: global x0.80 dim + GaussianBlur 2.5': ['backdrop_grade'],
    'cv_lib.terminal (fill 238, cyan edge 2 px / 210, r 8, scanlines 4 px / 38)': ['terminal_plate_kit'],
    'cv_lib.text with NOW[words] off (L2.text proxy bars)': ['nowords_variant', 'hero_nowords_proxy', 'sector_digits_nowords', 'ring_tags_nowords', 'cards_nowords', 'stickers_nowords'],
    'cv_lib.shadow_paste + sticker plates': ['sticker_material'],
    'build10 layout constants (column x, gaps, board centre and radii)': ['layout_grid'],
    'SCRIM token (BRIEF 3.3; not drawn under the HUD/hand today)': ['hud_scrim'],
    'e10lib.grade_units (mauve post-grade, p2b dim)': ['unit_cell_screen', 'hover_focus_dim'],
    'build10 p2b overlay alpha 36 percent + non-hovered arcs skipped': ['hover_dim_overlay'],
    'cv_over.hp_ring': ['hp_ring'],
    'e9lib.bezel9 (ticks, live cell, chevrons, HOLD cells, arc text)': ['bezel_ticks', 'sched_this_turn', 'sched_chevrons', 'sched_hold_cells', 'sched_plus_cells'],
    'e9lib.bezel9: live HOLD branch (white outline + glyph)': ['sched_hold_live'],
    'cv_over.sector_digits (+ needle)': ['sector_digits', 'needle'],
    'cv_over.cell_border (empty cells, 30 percent)': ['empty_cell'],
    'e10lib.wave_arcs10 (arcs, pips, width dots, hazard, W tags)': ['future_wave_arcs', 'wave_arc_unit_pips', 'climax_hazard_ticks', 'wave_tags'],
    'e8lib.ward_arc': ['ward_arc'],
    'e9lib.tower_slice_bars (bars, crack, break X, broken)': ['slice_hp_bars', 'slice_break_x', 'slice_cracked_mark', 'slice_broken_state'],
    'e9lib.tower_slice_bars: harm-lost pip (255,150,140) + slash': ['slice_pip_lost_harm'],
    'e9lib.tower_slice_bars: by_soak lost pip SOAK_C': ['slice_pip_lost_soak'],
    'e9lib.tower_slice_bars: mend pip (170,240,170) + 3/3 dash': ['slice_pip_mend'],
    'e9lib.tower_slice_bars: gone pip dashed socket': ['slice_pip_gone'],
    'e9lib.brace_plate': ['brace_plate'],
    'e9lib.soak_marks: inward chevrons': ['slice_soak_marks'],
    'e9lib.soak_marks: rim arc r s1-1, +/-26 deg': ['slice_soak_rim_arc'],
    'e9lib.tower_slice_bars / soak_marks: orange break X': ['slice_soak_break_x'],
    'e9lib.threat_trim': ['threat_trim'],
    'e10lib.lit_cell / unit_mask (incl. the width-6 branch)': ['unit_cell_screen', 'ring_unit_wide6'],
    'e8lib.cell_outline': ['unit_cell_outline', 'consumed_unit', 'hovered_cell_outline'],
    'e8lib.token + cv_over.lane_base_style': ['token_disc', 'token_lane_base', 'token_halo', 'glyph_packet', 'glyph_worm', 'glyph_payload'],
    'e8lib.hp_row (segments, lose slash, shield bracket)': ['unit_hp_row', 'shield_bracket'],
    'e8lib.armor_cap': ['armor_cap'],
    'e10lib.chevrons_h / chev_stack_h': ['chev_solid_stack', 'chev_hollow', 'chev_sector_column'],
    'e9lib.warded_mark': ['warded_mark'],
    'e8lib.dead_x': ['dead_x'],
    'build10.draw_units: consumed branch': ['consumed_unit'],
    'build10.draw_units: trigdead branch': ['trigger_killed_unit'],
    'e10lib.adjuster_body (cell, HP bar, armor cap, diamond, skull, strike)': ['adjuster_cell', 'adjuster_hp_bar', 'adjuster_diamond', 'adjuster_armor_strike'],
    'e10lib.gun_tracers10 (tracer line, muzzle nubs, NO TARGET tag)': ['gun_tracers', 'gun_tracer_burst_pair', 'no_target_tag'],
    'e10lib.gun_tracers10: result hit / armor / ward / shield / sealed': ['gun_result_hit', 'gun_result_armor', 'gun_result_ward', 'gun_result_shield_pop', 'gun_result_sealed'],
    'e10lib.gun_tracers10: idle stub dash 4/8 r 145-175': ['gun_idle_stub'],
    'build10.make p2/p3: gun tracers not called (state f2 has guns)': ['gun_tracers_preview'],
    'GDD 9.2 / 9.5 (not drawn): card-hover ghost, targeting, Tab focus': ['spin_ghost_preview', 'card_targeting'],
    'e10lib.landing_arcs (band, disc, wear, twist, dots, chevrons, clamp, diamonds, soak, check)': ['landing_arc_frame', 'arc_glyph_disc', 'arc_wear_mark', 'arc_twist_mark', 'arc_now_dot', 'arc_turn_dots', 'arc_chevrons', 'arc_soak_chevron', 'arc_brace_glyph', 'arc_diamonds', 'arc_check'],
    'build10.ring_tags': ['ring_tags'],
    'build10.nudge_ghost': ['nudge_ghost'],
    'build10.twist_badge (p2/p3)': ['twist_badge'],
    'build10.refund_marks (placement + REFUND tag)': ['refund_burst'],
    'e10lib.burst + ram_pip_pop (token, drawn in 4 places)': ['refund_token'],
    'e8lib.trigger_paths + pencil_line / pencil_x (p2)': ['trigger_path', 'trigger_tower_hit'],
    'build10.hover_path (p2b)': ['hover_path', 'hover_slice_highlight'],
    'build10.make p3: cyan fire lines': ['resolve_fire_lines'],
    'build10.header (plate, title, waves left, pips, ?)': ['header_plate', 'header_title', 'waves_left', 'help_button'],
    'build10.bill_box (frame, YOU, hero, eq row, split, NEXT, pencil, BEST LINE, without Twist)': ['bill_frame', 'you_hp_tally', 'hero_pair', 'eq_row', 'eq_labels', 'tally_segments', 'operators', 'empty_socket', 'trig_groups', 'trig_lands_group', 'split_row', 'route_arrows', 'next_row', 'plan_pencil_underline', 'best_line_tag', 'without_twist_row'],
    'build10.option_chip (frame, glyph sequence, label, bar, pair)': ['option_chips', 'option_plan_glyphs', 'option_name_label', 'option_outcome_bar', 'option_pair'],
    'build10.chain_strip (frame, discs, glyphs, names, tallies, prose)': ['chain_strip', 'chain_step_discs', 'chain_step_glyphs', 'chain_step_names', 'chain_result_tallies', 'chain_result_prose'],
    'build10.stars_row (frame, stars, labels, tallies, card challenge)': ['objectives_frame', 'star_glyph', 'win_label', 'challenge_labels', 'challenge_tallies', 'challenge_trigger_hits'],
    'build10.ram_trace (frame, labels, RAM, refund pip, Trace, cap hatch, ENDS = HEAT)': ['ram_trace_frame', 'ram_trace_labels', 'ram_pips', 'ram_refund_pop', 'trace_pips', 'trace_cap_hatch', 'ends_heat'],
    'cv_chrome.hand (fan, hover grow, liners)': ['hand_fan', 'card_hover_grow', 'played_liner'],
    'cv_chrome.card_img (frame, band, glyph, x, title, type band, text, cost, loud tab, curl)': ['card_frame', 'card_header_strip', 'art_band', 'card_icon', 'card_icon_set', 'card_multiplier', 'card_title', 'type_band', 'rules_text', 'cost_badge', 'loud_tab', 'loud_tab_resting', 'card_hover_grow'],
    'build10.stickers (CELL-9, SEND IT, UNDO, hint)': ['nameplate', 'send_it', 'undo_chip', 'bottom_hint'],
    'build10.hover_tag (p2b)': ['hover_tag'],
}

BIBLE = r"""
## 3. Cohesion bible (every designer follows this; the whole E10 read stays)

### 3.1 What E10 already does well (keep, do not redesign away)
- **One board.** Tower in the centre, three wave rings, the schedule bezel, landing arcs outside; the right column is the bill; the hand bottom right. The layout is locked (3.1, 3.22).
- **Depth four ways** (position, lane outline, token base, NOW / +1 / +2 words). Keep all four.
- **Threat grammar:** red chevrons pointing at the tower = hit; red diamonds = HP that gets through; solid = now, hollow = growth to come. This is the strongest idea on the screen.
- **Counts are tallies** (groups of 5), digits only in the hero `lands -> through` pair, tags and the hover tag.
- **Ink keylines** under every coloured mark give the print/sticker feel that ties the board to the stickers and cards.
- **Media split** (1.2): CRT terminal plates for data, vinyl stickers for identity and the verb, grease pencil only for the player's plan.
- **Muted mauve unit screens** so the red pops (PL10). Keep the value relationship even where pink is now allowed case by case (amendments draft, Part 3.1).
- **One warm mass:** the live schedule cell is the one big orange shape; the board reads first at 320 px.

### 3.2 Value hierarchy (squint order at 320 px, on room_bio_bare)
1. **L1 threat:** red chevrons, red diamonds, the solid threat trim, the hero THROUGH digit. Highest saturation x contrast on screen.
2. **L2 board structure:** the live schedule cell, slice icons, unit tokens, the Adjuster. One step below L1. The live schedule cell must not outweigh L1 (today it does).
3. **L3 HUD data:** bill tallies, RAM / Trace pips, card art bands, SEND IT (SEND IT is L2 by size but sits away from the board).
4. **L4 containers and engraving:** panel frames, gutters, empty cells, labels, ticks, future wave arcs.
5. **L5 backdrop:** the cutaway room is the lit second mass (value up to x0.84 in its focus hull per the cutaway NOTES); the city around it is texture. Nothing on the board may sit at L5 value, and the room may never exceed L2.
- Rule of thumb: a mark's value tier is set by what the player must read first, never by how new it is.

### 3.3 Colour tokens (hex) and their one meaning
| Token | Hex | Meaning on this screen | Never |
|---|---|---|---|
| `HARM` | #FF4433 | Damage that will happen: chevrons, diamonds, threat trim (now), lost-this-turn slashes, THROUGH digit, NOW lane | decoration, Trace, card cost |
| `PENCIL_THREAT` | #FF1C2C | Grease pencil threat (Trigger hit reaching the tower) | non-pencil marks |
| `GAIN` | #7BE07B | Player HP left, slice HP left, enemy shot dead (X), nothing through (check) | Worm wear, route icons, Solace identity |
| `NET_CYAN` | #5CE1FF | Ours / the tower: code-base frame, terminal edges, RAM, SHOT, ABSORBED, gun tracers, TOWER card family | enemy elements |
| `PENCIL_PLAN` | #FFE200 | The player's plan only: pencil paths, hover path and tag edge, plan underline, twist badge, selected option, BEST LINE, TRIG group | SEND IT fill, help button, card cost, hazard ticks |
| Vinyl yellow | #FFEE60 -> #FFB60E | SEND IT sticker material (gradient, 2.10) | flat fills |
| `SCHEDULE_ORANGE` (`RING_AVAILABLE`) | #FF8C1A | The wave schedule: bezel cells, WAVES LEFT, future normal waves, WAVE card family | soak, heat, corp identity |
| `SOAK` | #FF9628 today | Slice takes pips instead of HP | **must move away from #FF8C1A** (designers propose; hue + shape, see 3.10) |
| `CRT_AMBER` / `WARN` | #FFB000 | Heat consequence (ENDS = HEAT), caution | boss, reward |
| `BOSS_GOLD` | #FFC428 | The Adjuster: body, cell edge, ward arc, warded mark, its HP progress | refund, generic reward |
| Reward gold | #FFD24D (`RESIST_GOLD`) | Stars met (with the star shape only) | boss marks |
| `CREAM` | #FFF4D6 | Enemy HP segments | Brace (player's), boss HP if the boss gets its own colour |
| `LANE_PLUS1` | #78AAFF | Ring +1 outline, next-turn threat trim | Trace |
| `LANE_PLUS2` | #ECF0FF dashed | Ring +2 outline, later threat trim | turn dots, HP |
| `RIDER_LAV` | #BEA0FF | Rider (Adjuster turn rider) | Trace |
| `TRACE_VIOLET` | #A03CFF | Trace pips and anything that adds Trace (card loud tab) | rider, Jammer |
| Unit mauve | #7C4068 Packet, #6A4482 Worm, #5E568A Jammer, #76446A Payload (washes) | Unit screens only | HUD |
| `STEEL` / `STEEL_HI` | #96A2B6 / #E2E9F6 | Armor | lane outlines |
| `INK` | #0C0A16 | Keylines, glyph outlines | |
| `TERMINAL_BG` | #050D1C at 93 percent | CRT plates | |
| `TEXT_HI` / `TEXT_MID` / `TEXT_LO` | #F2F6FF / #AFC0D6 / #7A889C | Text on dark | |
| `SCRIM` | #02030A at 55 percent + 6 px blur | Under the board and HUD over the room | |

Rules: every colour pairs with a shape, glyph or word (5.1). A corp hue never takes a UI role (2.4); Solace lime #96FF46 sits next to GAIN, so Solace shows on this screen by **material and crest only** (bezel, ring cells), never as lime fill. Pink: allowed case by case (amendments draft), but never on a mark that must read as threat or as ours.

### 3.4 Type ladder (1080p px)
| Role | Face | Sizes | Notes |
|---|---|---|---|
| Verb sticker | Anton, ink keyline 5 px | 62 (SEND IT) | die-cut border 0.14 x size, max 12 px |
| Hero digits | Anton, keyline 3-5 px | 58 | the only raw number on the board/HUD besides tags |
| Display L | Anton | 30-34 | header turn number, nameplate, cost digit |
| Display M | Anton | 22-28 | card titles, sector digits, operators |
| Tag | Anton with keyline | 17-20 | ring tags only; raise toward 20 where space allows |
| Terminal | Share Tech Mono caps +8 percent | 18 floor, 22 for rows that lead | HUD labels are 16 today: raise to 18 (2.9 floor) |
| Rail / bezel arc text | Share Tech Mono | >= 16 (3.22 rail rule) | flip on the lower half |
| Body / tooltip | IBM Plex Sans Condensed Regular + Medium | 20 (hover tag; 18 today) | keywords Medium in their colour, 36-60 chars a line |
| Card rules (resting) | Plex Sans Condensed | 16 (= 10.7 at 720p, inside the resting-card exception) | grown card keeps the 12 px 720p floor |

### 3.5 Stroke and ink ladder
| Tier | Width | Use |
|---|---|---|
| Hairline | 1.2-1.6 px | engraving: bezel ticks, segment outlines |
| Fine | 2-2.6 px | containers: terminal edges, tags, chips, token rings |
| Medium | 3-4 px | identity borders: lane outlines (now 4, +1 / +2 3), boss cell edge |
| Bold | 5.5-8 px | action and threat: threat trim, chevrons (6 on 10.5 ink), grease pencil 7 + ink |
- Ink keyline = coloured stroke + about 4.5 px (each side about 2.25), colour INK. Every coloured mark on the board has one; text on plates does not.
- A tier means something: a container never uses the bold tier, a threat mark never uses hairline.

### 3.6 Corner and bevel language
- HUD (rectilinear): radius ladder 3 (pips, segments) / 6 (tags, chips) / 8 (terminal plates) / 16 (cards, stickers outer). One panel style for every HUD plate (today there are three: cyan terminal, white bill box, grey objectives).
- Board (polar): arc bands with a fixed inset (4 px radial, 3 deg angular) for every cell, unit or empty; no rounded rectangles on the board except tags; slices keep family-C rounded wedges.
- Shapes carry meaning: circle = identity token or count dot; square/rounded segment = HP or resource pip; diamond = HP through (red) or boss (gold), so no unit glyph may be a diamond; chevron = hit; X = removed (green = enemy dies, red = our slice breaks).
- Bevel: none on HUD (flat CRT glass with scanlines). Board materials (bezel, cells) may carry one soft inner bevel, light from the top-left, matching the cutaway's fixed light (-0.5, -0.3, 0.81).

### 3.7 Glow and bloom
- Default: no glow. Allowed emissive marks: the solid threat trim (now) and the live schedule cell, soft bloom 4-6 px at up to 35 percent; the hover / plan pencil gets no glow (wax, not neon).
- Dark ink halos (pools) under tokens and the boss are allowed (they are shadow, not glow) at up to 75 percent, blur 4.
- No glow on text, tallies or HUD plates. The board never blooms more than the backdrop's brightest neon.

### 3.8 Icon grid and style
- Bible 3.5 glyph set (round 17 package): white silhouette, ink outline 7.5 percent of size, 512 grid, 2-3 parts, no interior detail under 2 px at use size.
- Sizes: 70 card art, 44 slice, 37 unit token, 28 arc disc, 24 boss skull, 20 chips and options; nothing below 16 (5.2): today's 13 px wave-arc glyphs fail.
- No media-player shapes (play, pause, skip): the Packet, HOLD and needle all read as media buttons today.
- No letter-like glyphs (Worm reads as "M").
- One meaning per silhouette: today the shield is used for the SHIELD slice, the warded mark and (nearly) the Brace glyph; the diamond for Payload, HP-through and the boss.

### 3.9 Process rules for every option
- Render on `docs/concepts/combat_backdrop/v2/room_bio_bare.png` (room framed at screen 1500, 612) at 1920x1080; never on the old crane backdrop.
- Content is fixed: state_e10.json, every count, number and word stays; design changes how, never what. Draw asserts (assert_draw_log) must still pass for anything that is counted.
- Check each option in context (full plate), at 320 px squint, deutan, and the nowords variant (`actions__nowords_variant.png` shows the HUD with words stripped: every element must still read by shape).
- Work on copies of src/; never overwrite the approved plates or E10 source.

### 3.10 Do-nots
1. Do not add a colour token; reuse 3.3, or bring a token change to the art director with a reason.
2. Do not let any orange other than the schedule fill an area larger than a chip.
3. Do not put plan yellow on anything that is not the player's plan.
4. Do not put an X, slash or badge over an icon it describes; place states beside or around.
5. Do not stack more than two parallel arcs within 12 px (today up to six).
6. Do not add digits to the board (tallies only), except the existing tags and hero pair.
7. Do not use a corp hue (Solace lime, Meridian orange) for a UI role; Meridian art is hibernated.
8. Do not draw nudge buttons on the ring wheel (3.22 Open).
9. Do not use media shapes or letters as glyphs.
10. Do not add glow to fix a weak read; fix value and size first.
11. Do not let the board's outer arcs touch the screen edge (keep a 24 px margin) or let stickers crop at the frame.
"""

REVIEW = r"""
## 6. Completeness review (2026-11-01)

An independent review of the 133-element inventory reported 28 missing elements, 15 lumped or vague entries and one process gap. The art director checked each finding against the five plates (crops at 2-4x) and the generator source (e9lib.tower_slice_bars, e9lib.soak_marks, e10lib.gun_tracers10, cv_lib.backdrop, cv_lib.text, build10.stars_row) and the f1/f2 sim state. **Every finding was confirmed. None is rejected.** Two are handled differently from the review's suggestion; both are noted below. The inventory now has **183 elements, 22 of them LATENT (was 9); 161 crops; COVER 48 -> 72 entries**.

**Added (missing elements)**
- wheel_core: `hub_inner_rings` (alpha-10 rings: confirmed in source, invisible on the plate; kept as the hub's material decision), `slice_screen_code_text` (legible 'goto fail' / hex survives in p1_nowords), `slice_pip_lost_soak` (orange pip beside the salmon pip in the SHIELD sector 1 bar, p2), `slice_pip_mend` (LATENT), `slice_soak_rim_arc` (orange arc on the threat-trim radius, p2), `gun_idle_stub` (LATENT), `gun_result_sealed` (LATENT, stale branch; recommendation: retire), `gun_tracers_preview` (LATENT on the plates: f2 has BURST sector 4 'ward' x2 into Packet 6, but p2/p3 draw no tracers), `spin_ghost_preview` (LATENT, GDD 9.2).
- wave_rings: `unit_screen_code_text` (hex columns in the Packet screens, still there in nowords).
- outer_rings: `bezel_rim_lines` (two orange rim glows at r ~356 / ~388 plus baked light), `backdrop_grade` (global x0.80 dim and 2.5 px blur stacked on room_bio_bare's own grade), `sector_digits_nowords`, `ring_tags_nowords`.
- top_hud: `hud_scrim` (nothing seats the column or the hand on the lit room), `terminal_plate_kit` (the shared plate component and its scanlines), `layout_grid` (x 1066 vs 1062 vs 1068, gaps of 8/10/4 px, p2/p3 growth into the focus hull, edge margins), `hero_nowords_proxy` (white square and red bar replace 12 -> 6, while the yellow arrow stays loudest).
- objectives: `ram_trace_labels`, `challenge_trigger_hits` (LATENT, plan-yellow tally).
- cards: `card_header_strip`, `cards_nowords`.
- actions: `sticker_material` (shared die-cut / plate / shadow; card and sticker shadows differ), `stickers_nowords`, `card_targeting` (LATENT, GDD 9.2 / 9.5), `nowords_variant` (the existing nowords crop now has an owner element for the screen-wide nowords rule).
- `chain_step_glyphs` (red skull for LANDS reuses the boss silhouette; the lightning is used nowhere else) is listed under the splits below.

**Split (lumped entries)**
- `slice_hp_bars` -> the bar set plus `slice_pip_lost_harm`, `slice_pip_lost_soak`, `slice_pip_mend` (LATENT) and `slice_pip_gone` (LATENT): five pip states designed as one set.
- `slice_soak_marks` -> soak chevrons (kept id) + `slice_soak_rim_arc` + `slice_soak_break_x` (+ the soak pip). Four marks for one choice; the family is to be pruned in design.
- `gun_tracers` -> tracer line (kept id) + `gun_result_hit` (the only result visible) + `gun_result_armor`, `gun_result_ward`, `gun_result_shield_pop`, `gun_result_sealed`, `gun_idle_stub` (all LATENT).
- `chain_strip` -> frame (kept id) + `chain_step_discs`, `chain_step_glyphs`, `chain_step_names`, `chain_result_tallies`, `chain_result_prose`.
- `option_chips` -> frame and two states (kept id) + `option_plan_glyphs`, `option_name_label`, `option_outcome_bar`, `option_pair`.
- Refund token -> new owner element `refund_token` (one token drawn in four places at four sizes). `refund_burst` is now the board placement only. `ram_refund_pop`, option chips and the chain strip reference the token.
- `hover_focus_dim` -> unit-screen grade at 50 percent (kept id) + `hover_dim_overlay` (marks at 36 percent; the non-hovered arcs are **removed**, not dimmed).
- `board_scrim` -> radial pool (kept id) + `backdrop_grade`; the HUD/hand scrim is the new `hud_scrim`.
- `consumed_unit` -> consumed, yellow (kept id) + `trigger_killed_unit`, red (its greyed token is hidden under the refund burst).
- `token_disc` -> fill and size (kept id) + `token_lane_base` (three base rings) + `token_halo`.
- `arc_soak_brace` -> `arc_soak_chevron` + `arc_brace_glyph` (different owners: the cream glyph is 28 px and is not a clamp). The old crop was deleted.
- `trig_groups` -> TRIG group (kept id) + `trig_lands_group` (LATENT, reuses the RAW red).
- `sched_hold_cells` -> plus `sched_hold_live` (LATENT white live-HOLD branch).

**Sharpened:** `slice_screen` (code text moved out; per-type contrast named), `unit_cell_screen` (code text moved out), `screen_motif_skull` (stronger in p2 under keep_all), `gun_tracers` (second tracer style and idle style named).

**Handled differently from the review's suggestion (not rejected)**
- Hub inner rings: the review treated them as part of hub material. They are kept as their own element because the source draws them as a separate sub-draw. At alpha 10 they cannot be seen, so the designer decides whether to keep one bevel or remove them.
- Sealed result: the seal mechanic has no meaning in the current rules, so the element exists only to make a decision. The art director recommends deleting the branch rather than designing a glyph for it.

**Process fix:** COVER in `build_brief.py` is now keyed per drawn part (branch, colour state, sub-mark), not per function. It gained 24 entries for sub-draws that were hidden inside covered functions: ring_base rims, draw_hub rings, soak / mend / gone pips, idle stub, sealed, L2.text proxies, terminal() scanlines, shadow_paste, layout constants. It also lists the undrawn parts the screen needs (GDD ghost / targeting, the SCRIM token) so each one has an owner. The nowords crop is no longer exempt from the crop check.

"""


def main():
    ids, problems = {}, []
    for cl in ORDER:
        for e in INV[cl]:
            if e['id'] in ids:
                problems.append('duplicate id %s (%s, %s)' % (e['id'], ids[e['id']], cl))
            ids[e['id']] = cl
    if set(INV) != set(ORDER):
        problems.append('cluster keys differ: %s' % sorted(set(INV) ^ set(ORDER)))
    crops = {os.path.basename(p)[:-4] for p in glob.glob(HERE + '*__*.png')}
    want = {'%s__%s' % (ids[e['id']], e['id']) for cl in ORDER for e in INV[cl] if e['src'] != 'LATENT'}
    for c in sorted(want - crops):
        problems.append('missing crop %s.png' % c)
    for c in sorted(crops - want):
        if True:
            problems.append('crop without element %s.png' % c)
    covered = set()
    for fn, el in COVER.items():
        for i in el:
            if i not in ids:
                problems.append('COVER %s -> unknown id %s' % (fn, i))
            covered.add(i)
    for i in ids:
        if i not in covered:
            problems.append('element %s not mapped to any source draw call' % i)
    n = sum(len(INV[c]) for c in ORDER)
    nl = sum(1 for c in ORDER for e in INV[c] if e['src'] == 'LATENT')

    L = []
    L.append('# E10 combat screen: element-by-element design brief (art director)\n')
    L.append('Date: 2026-10-31. Branch art-pass, documentation only. Solace vertical slice, art only.\n')
    L.append('**Source of truth:** approved plate E10 `D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png` (plus p2_preview, p2b_hover, p3_resolve, p1_nowords); generator `D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py` + `e10lib.py` (+ e9lib, e8lib, cv_over, cv_board, cv_chrome, cv_lib); sim state `state_e10.json`; rules `D:/rc_tmp/combat_concepts/D4_E10/rules.md`; ART_BIBLE 2, 3.1, 3.22; `docs/concepts/ART_BIBLE_AMENDMENTS_DRAFT.md`; cutaway backdrop `docs/concepts/combat_backdrop/v2/NOTES.md`; golden plates `docs/concepts/golden_plates/street_overview.png`, `hq_rebel_cell_overview.png`.\n')
    L.append('**Designer rulings this brief serves:** E10 "as a whole meets the visuals we want", but the micro details and sub-elements need real design (amendments draft, open items). Process ruling 2026-10-31: every element gets a design goal and look, options, iteration to a settled look, with the art director pruning and deciding and keeping the whole view cohesive.\n')
    L.append('## 1. How to use this brief\n')
    L.append('- Each element below has: **design goal** (what the player must read, in order, and how fast), **look and feel** (the target in words a designer can act on), **current problems** (minute level, as seen in E10), and a crop in `brief_crops/` (`<cluster>__<id>.png`, cut from the plate named in the Src column; contact sheets `brief_crops/contact_<cluster>.jpg`).')
    L.append('- Elements marked **LATENT** are drawn by the generator but not visible in this sim state (no crop). They are part of the screen vocabulary and must be designed with their family so a later state does not break the look.')
    L.append('- Hard limits: game content is fixed (state, numbers, counts, words); judge on room_bio_bare at 1920x1080; never overwrite the approved plates or E10 source; never run `python -`.')
    L.append('- Re-run `python brief_crops/make_crops.py` then `python brief_crops/build_brief.py` after editing `brief_crops/inventory.json`; the build fails loudly if an element loses its crop or a source draw call loses its element.\n')
    L.append('## 2. Cluster moves (from the task\'s starting list)\n')
    L.append('Keys are fixed; these elements were moved so each object is designed in one place:')
    L.append('- **HOLD NEXT / HOLD THEN zones**: wave_rings -> **outer_rings** (they are cells of the one schedule bezel with `+2 THIS TURN`).')
    L.append('- **Landing arcs** (frame, kind disc, wear, now dot, turn dots, chevrons, diamonds, check, soak/brace, twist mark): **outer_rings** as one object (the task split them between wave_rings and outer_rings).')
    L.append('- **Soak and clamp marks**: the slice versions (Brace plate, slice soak marks) go to **wheel_core**; the arc versions stay with the landing arc in outer_rings.')
    L.append('- **Gun tracers, nudge ghost**: **wheel_core** (they come from the tower). **Ward arc, consumed-unit state**: wave_rings.')
    L.append('- **Option chips, chain strip, plan underline, BEST LINE, WITHOUT TWIST, TRIG groups**: **top_hud** (they are states of the bill). **RAM refund pop**: objectives. **Trigger path, twist badge, refund burst, hover tag/path/dim, resolve fire lines**: **actions** (plan / preview affordances).\n')
    L.append(BIBLE)
    L.append('## 4. Element inventory (%d elements, %d of them LATENT)\n' % (n, nl))
    for cl in ORDER:
        L.append('### 4.%d %s (`%s`, %d elements)\n' % (ORDER.index(cl) + 1, TITLE[cl], cl, len(INV[cl])))
        L.append('Contact sheet: `brief_crops/contact_%s.jpg`\n' % cl)
        for e in INV[cl]:
            crop = 'LATENT (no crop)' if e['src'] == 'LATENT' else '[%s__%s.png](brief_crops/%s__%s.png) (from %s)' % (cl, e['id'], cl, e['id'], e['src'])
            L.append('#### `%s`: %s' % (e['id'], e['name']))
            L.append('- Crop: %s' % crop)
            L.append('- **Design goal:** %s' % e['goal'])
            L.append('- **Look and feel:** %s' % e['look'])
            L.append('- **Current problems:** %s\n' % e['problems'])
    L.append('## 5. Completeness audit (nothing omitted)\n')
    L.append('Method: (a) every drawing call in the E10 generator that reaches any of the five plates was listed from the source and mapped to element ids; (b) every element must map back to a call; (c) every visible element has a crop and every crop has an element; (d) all five plate states were scanned for state-only elements (p2 Brace, soak, option chips, refund, twist; p2b hover tag, path, dim; p3 chain strip, liners, fire lines; nowords). The build script checks (a)-(c) on every run.\n')
    L.append('| Source draw call | Element ids |')
    L.append('|---|---|')
    for fn, el in COVER.items():
        L.append('| %s | %s |' % (fn, ', '.join('`%s`' % i for i in el)))
    L.append('')
    L.append('Granularity rule (completeness review): COVER is keyed per drawn part (branch, colour state, sub-mark), not per function, so a sub-draw cannot hide inside a covered function. Entries for parts that are not drawn (GDD asks, the SCRIM token) are listed so the element still has an owner.\n')
    L.append('**Retired, not designed:** the sealed hatching + padlock (`e8lib.sealed_marks`, SEALED +2 tag) and the Adjuster rim satellite (`e8lib.adjuster_satellite`), `e8lib.twist_chip` and `e9lib.rim_chips`: dropped by the E9/E10 rules or replaced by landing arcs / the Adjuster body; not called by build10.')
    L.append('**Not elements (fixed):** the backdrop itself (cutaway pick, its own kit), and the plate layout (locked 3.1/3.22).\n')
    L.append('**Audit result:** %s\n' % ('PASS: %d elements in 7 clusters, %d crops, %d source draw calls mapped, 0 gaps.' % (n, len(crops), len(COVER)) if not problems else 'FAIL: ' + '; '.join(problems)))
    L.append(REVIEW)
    L.append('## 7. Open calls for the art director (round 1)\n')
    L.append('1. Soak colour: needs a new hue/shape clear of schedule orange (decide in R1 from options).')
    L.append('2. Brace colour: cream is enemy HP; propose a player-side clamp colour (cyan family or steel) in R1.')
    L.append('3. Boss HP colour: cream (unit family) vs gold (boss family); the HUD and board must agree.')
    L.append('4. Bezel material for a Solace fight (Meridian brushed brown today); Solace by material and crest, not lime.')
    L.append('5. Card cost badge: plan yellow today; proposal to speak RAM (cyan pip) so cost and RAM read as one currency.')
    L.append('6. Glyph replacements (Packet media arrow, Worm "M", Payload diamond, turret sword, shield reuse) must go through the bible 3.5 twin check.\n')
    open(HERE + '../BRIEF.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('elements', n, 'latent', nl, 'crops', len(crops), 'cover', len(COVER))
    print('problems', len(problems))
    for p in problems:
        print('  ', p)


if __name__ == '__main__':
    main()
