# E10 design, round 2: art director decisions (final per element) and assembly instructions

Date: 2026-11-01. Branch art-pass, documentation only. Reviewed: all R2 sheets, crops and plates of the seven clusters on room_bio_bare at 1920x1080, checked against BRIEF.md, REVIEW_R1.md (X1-X19), the E10 source and `state_e10.json`.

Cohesion board of the finals: `r2/cohesion_board_final.jpg` (script `D:/rc_scratch/e10_design/ad_r2/cohesion_board.py`). It has a rough p1 composite (`r2/_ad_composite_p1_rough.jpg`) pasted by region from the seven R2 plates, a 320 px squint with its value map, seven cross-cluster family strips, and one tile per element (197 tiles; the other 4 inventory entries are retired or owned inside another element). The composite is a region paste, not the assembler. The cross-cluster resolutions in section 2 are not in it yet.

Status key: **FINAL** = settled, the assembler uses it as is. **FINAL+T** = settled with the exact tweak given. **LATENT** = settled, but it does not appear in any of the five sim states. **UNSETTLED** = see section 6.

---

## 1. Element list review (the user's request: nothing omitted)

**Method.** (a) The 183 ids in BRIEF section 4, with the section 8 changes (17 added, 1 renamed, 1 moved, 1 retired), were diffed by script against the R2 element ids every cluster delivered (`D:/rc_scratch/e10_design/ad_r2/diff_ids.py`, using `brief_ids.tsv`). (b) Each cluster's own omission report was checked. (c) Every E10 draw call in BRIEF section 5 was re-walked against the final owners. (d) The GDD combat-readability items (9.2, 9.5, 9.6) were re-read against the inventory. (e) `state_e10.json` was searched for which LATENT branches really occur in the five states.

**Diff result.** The inventory has 199 entries. Every one has an R2 deliverable or a recorded ruling, so nothing is missing:
| Cluster | Inventory | Delivered | Notes |
|---|---|---|---|
| wheel_core | 38 | 36 | `gun_result_sealed` retired; `slice_screen_code_text` = none (X12). Both are confirmed absent from the R2 code. |
| wave_rings | 35 | 33 | `adjuster_cell_underlay` is owned inside `adjuster_cell` (fixed: the boss cell replaces the empty cell); `unit_gone_state` is owned inside `dead_x`. |
| outer_rings | 33 | 35 | +2 found by the designer and **accepted**: `bezel_spokes` and `sched_track`. |
| top_hud | 36 | 36 | (row_tags included) |
| objectives | 13 | 13 | |
| cards | 20 | 20 | |
| actions | 24 | 24 | (includes the moved `trigger_tower_hit` and the 3 R1 additions) |

**The inventory is now 201 entries: 199 + bezel_spokes + sched_track.**

**New findings in R2, with a ruling for each:**
| # | Finding (source) | Ruling |
|---|---|---|
| F1 | `bezel_spokes`: the bezel segment of the X13 spoke had no owner (outer_rings) | **Added**, outer_rings `r2_ground.spoke_mask`. FINAL. |
| F2 | `sched_track`: the recessed channel under the schedule cells and the empty bezel stretch (outer_rings) | **Added**, FINAL (P, with the track). |
| F3 | Glyph masters exist in four places: cards `kglyph2`, wave_rings `wr2_glyphs` (_R), wheel_core `wc2_glyphs` (burst/turret/repair/crest), outer_rings `r2_glyphs.KIND_MASTER` (provisional), and the actions and top_hud copies of the R1 kglyph | **One master** (Y3 below): `kglyph2` is the library. The wave_rings unit masters and the wheel_core masks/crest are the source drawings that get registered into it. Nothing else may draw a glyph. |
| F4 | `resource_shape_set` (objectives): a specimen of coin / square r3 / flame at every use size | **Accepted as a rule, not a new drawing.** `obj2.coin_img`, `obj2.sq_img` and `obj2.flame_img` are the only drawings of the three silhouettes. The card cost, refund token, chip, chain and loud tab call them (Y4). |
| F5 | The trace_cap padlock is a new glyph (objectives) | It goes into `kglyph2` and the twin check (Y3). |
| F6 | The cards note says the SLICES KEPT row is "removed by the other clusters" | **Wrong; it stays.** SLICES KEPT is an E10 challenge label (an existing word). X17 forbade only an added SLICES KEPT *tally*. The assembler keeps the label with no tally. |
| F7 | No gun is idle in any state (all f1/f2 guns have shots; checked in `state_e10.json`) | `gun_idle_stub` and `no_target_tag` are **LATENT**. The wheel_core sheets showed them in a showcase p1, which is not content. |
| F8 | top_hud states to check: hero THROUGH 0, HP gone pips, soaked > 0, TRIG LANDS, waves_left < 6 | These are states of existing elements and are rendered in `r2/top_hud/states_latent.jpg`. No new ids. |
| F9 | actions (1): SEND IT has no key hint (GDD 9.5 Space = end turn), though UNDO shows Z | **Added as LATENT `send_it_key_hint`** (owner actions), on the precedent of `card_key_hint` (also GDD 9.5). It is not in the five plates. It has no options yet: UNSETTLED (6.3). |
| F10 | actions (2): right-click inspect (GDD 9.5) has no element | **Not added.** An inspect panel shows new information: game-content ruling needed. |
| F11 | actions (3): GDD 9.2 card-hover ghost exists only for Spin | **Added as LATENT `card_hover_ghosts`** (Brace, Twist, Pull, Shove, Firewall, Trigger). Owners: wheel_core for tower cards, wave_rings for ring cards. The grammar is fixed now (spin_ghost_preview A: ghosts at 55 percent in the source colour; the only new mark is the card's library glyph in PENCIL_PLAN). No options are rendered: UNSETTLED (6.3). |
| F12 | actions (4): no hover tag for the Adjuster or the slices | **Not added.** It would need new tag words: game-content ruling. |
| F13 | actions (5): the UNDO-locked cause (nothing to undo vs checkpoint after a random outcome) is not distinguished | **Not added.** Game-content ruling. |
| F14 | actions (6): GDD 9.6 reduce-effects toggle has no owner | **Added as `reduced_effects_state`** (owner top_hud `terminal_plate_kit`, with actions `bottom_hint`). Settled by rule: scanlines alpha 20 -> 0; block cursor static; the threat-trim and live-cell bloom off; the sign/neon flicker of the backdrop is not ours; the card hover curl keeps its pose but loses its animation. FINAL (rule). |
| F15 | actions (7): the focus target list misses option chips and ring tags | **Ruled:** `focus_brackets` A also goes on option chips (p2) and ring tags. FINAL. |
| F16 | actions (8): no held-card aim cursor while a card is dragged | **Added as LATENT `card_drag_aim`** (owner actions). It has no options: UNSETTLED (6.3). |
| F17 | actions (10): GDD 9.2 per-pointer intent labels, migrating-pointer flicker, orbit trail | **Not added.** Shifting Waves has units on rings, not pointers. No E10 state has a migrating or orbiting unit, and the mapping is a game-design question. Record it for the designer. |
| F18 | Pile counters | Still **not added** (new information). |
| F19 | The NEXT row "slice lost" count: E10 used a green pip, R2 uses the HARM lost-now slash (top_hud open item 2) | **Confirmed:** the HP-grammar lost pip (HARM + white slash) at the NEXT row's 60 percent ghost value. Same count. |
| F20 | Spin ghost cannot redraw tracers (targets after rotation are not in the state) | Accepted. Slices only, no tracer ghost. That is a content limit, not an omission. |

**Inventory after this review:** 201 entries + 4 LATENT additions (send_it_key_hint, card_hover_ghosts, card_drag_aim, reduced_effects_state) = **205**. Retired or not drawn: gun_result_sealed, slice_screen_code_text, slice_badges, the WAVE TURNS caption, the ring-with-bar HOLD, the pause glyph, nudge_ghost (removed, kept as an id).

---

## 2. Cross-cluster rulings, round 2 (these win over any cluster pick)

| # | Issue | Ruling |
|---|---|---|
| Y1 | **SOAK fails deutan vs TRACE_VIOLET** (dE 2.6-2.8; reported by outer_rings, top_hud and objectives) | **Token change: SOAK = #464EFF** (was #6A6CFF). top_hud measured it: deutan vs violet 16.6, tritan vs violet 36.8, deutan vs LANE_PLUS1 49.4, tritan vs LANE_PLUS1 27.9, all passing. It is darker than LANE_PLUS1 as X3 asked, and it keeps the notch, chevron and funnel. It changes in one place (Y2) and so reaches every soak mark: slice pip, soak break X, soak chevron, arc soak capsule, split row, funnel, plan glyph, tally. The assembler re-runs the check (5.6). If the notch does not read on dark glass at 320 px, the assembler reports it and does not change the token. |
| Y2 | One token table | The assembler writes `asm_tokens.py` (colours, stroke ladder, HP-grammar constants: r3, slash 2 px white, ink 4.4, gone hairline 1.4) and points every cluster module's colour constants at it. These are the BRIEF 3.3 values with SOAK = #464EFF and the wave_rings kind set (Y6). |
| Y3 | **Glyph master** | `D:/rc_scratch/e10_design/cards/src/kglyph2.py` is the only library. Register into it, replacing its own drawing when they differ: unit glyphs from `wave_rings/src/wr2_glyphs.py` (packet_R, worm_R, payload_R, jammer_R, ring_R); `crest` = `wheel_core/src/wc2_glyphs.py` WC2_CREST (the hub engraving and the actions nameplate already use it); new ids `burst` = WC2_BURST_B, `turret` = turret_a, `repair` = WC2_REPAIR_P (repair_c_plain), and `padlock` from `obj2.el_cap`. Everyone then imports from kglyph2: wheel_core (spin ghost KA_spin3 -> kglyph2 spin3, Brace), outer_rings (`r2_glyphs.KIND_MASTER` -> kglyph2), actions (`a2_kglyph`, `a2_glyphs.crest`), top_hud (`hud_glyphs`). Delete the copies from the assembly. Re-run `kglyph2.iou` twin check on the full set at 16/20/28/37/44/70 px. |
| Y4 | Resource shapes | `obj2.coin_img(d, state, plus)` is the RAM coin everywhere: RAM pip 24, card cost 34 (`kcard2.coin/cost_draw` must call it; the Anton 24 INK digit stays cards'), refund token (plus=True; `a2_kit.refund_token` sizes 44/30/26/20 call it), and the top_hud chip and chain refund. `obj2.sq_img` gives the Trace square and the card loud tab (26). `obj2.flame_img` gives Heat. |
| Y5 | One terminal kit and one focus mark | `top_hud/src/hud2.py P()` is the kit plate for header, bill, chips, chain, objectives, RAM, UNDO tab, hover tag, refund tag and the no-target tag (`obj2.kit_plate` and `a2_stick.kit_plate` delegate to it). `actions/src/a2_kit.py focus_brackets` (A) is the only focus drawing (top_hud `focus_brackets` mirror is deleted). |
| Y6 | Kind colour set | **Approved: wave_rings R** (Packet 137,63,108; Worm 95,59,122; Jammer 57,103,164; Payload 98,51,66; Ring 113,109,149; Adjuster gold; min dE 11.8 in all four vision modes). This changes the BRIEF 3.3 unit mauve row. The Jammer wash sits near LANE_PLUS1 in hue but at far lower value and only fills a screen, never an outline, so it passes. `arc_glyph_disc` reads `wave_rings/.../kind_colour_set.json`. |
| Y7 | Shield pop twins the crest | `gun_result_shield_pop` A (a cyan ring broken in 4 arcs) twins the cyan cracked-ring Breaker crest. **Final = B (hex shard burst).** |
| Y8 | Preview vs resolve tracers (wheel_core gun_tracers_preview vs actions resolve_fire_lines) | **One drawing:** `wc2.guns_preview('B')` (tracer 55 percent, result glyphs 100 percent: the result is the information) in p2 and in p3. `a2_plan.fire_lines` is not called. resolve_fire_lines = FINAL+T "same as gun_tracers_preview B". |
| Y9 | Wave-ring badge collision (wave_rings flag 3) | Warded lozenge and dead-X badge move **onto the token rim**: centre 31 px from the token centre, at 45 deg into the quadrant between the start cap and the outer radius (the side away from the chevron column). Warded size = V (30 px lozenge, 16 px skull); dead badge 26 px. Draw order: halo, disc, ring, badge, then glyph (so the glyph is never covered; assert that badge alpha over the glyph mask = 0, else step down 2 px). Chevrons are then never touched, and do-not 4 holds (beside the glyph, on the rim). |
| Y10 | Ground | `outer_rings r2_ground` grade('P') + scrim('P') + plate('P') is the only grade, + `hud2.scrim_layers` (two slabs). `a2_render.ground` is **not** used. |
| Y11 | Twist badge anchor | `a2_plan.twist_badge` takes its anchor from `outer_rings/src/r2_misc.py tag_anchor`, not from its own copy `a2_plan.ring_tags_p`. |
| Y12 | Hover drawing owned by actions but drawn in wave_rings cell code | wave_rings keeps the geometry (outline path, token position); actions decides the look. Disable the wave_rings yellow hover outline branch and call `a2_hover.hover_cell` (lime focus brackets). The non-hovered dim = `wr2_lib.tint` true composite at k 0.38 (actions value; the R1 RGBA overwrite bug stays fixed). The trigger-path pencil X end cap = `a_plan.trigger_path` A on the R2 token position. |
| Y13 | HUD budget | Use the objectives heights (objectives 48, RAM 50). p1 bottom = y384 (limit met); p2 = 518 (E10 506, +12, at the limit); p3 = 538 (E10 534, +4). Within X18, so top_hud absorbs nothing. Assert these three numbers. |
| Y14 | Nameplate vs wheel (GDD 9.2: zine never covers the wheels) | In the composite the nameplate's top-right corner sits at r~508 from the board centre (536,540), on the outer future-wave tape. **Tweak:** place the nameplate (die-cut, tilt and shadow included) so every point is at r >= 520 from (536,540): move it down to the 24 px bottom margin and left to the 24 px side margin, and scale it to 0.92 if it still intrudes. |
| Y15 | Spokes | One 8 px INK spoke at 30+60k deg: `wc2.spokes` (r44-162), then `wr2_cells.gutters` (r161-355), then `r2_ground.spoke_mask` (bezel). Assert pixel continuity at r160-164 and r353-357 on all six angles. |

---

## 3. Final per element

Source roots (all copies, R2): WC = `D:/rc_scratch/e10_design/wheel_core/src`, WR = `.../wave_rings/src`, OR = `.../outer_rings/src`, TH = `.../top_hud/src`, OB = `.../objectives/src`, CA = `.../cards/src`, AC = `.../actions/src`. The crops and sheets are in `docs/concepts/combat_e10_design/r2/<cluster>/`.

### 3.1 wheel_core (36 delivered + 2 retired)
The wheel_core PICKS keys in `WC/wc2_run.py` are not the sheet labels everywhere. The "PICKS key" column gives the value the assembler sets.

| Element | Final | Source | Why | Tweak / PICKS key |
|---|---|---|---|---|
| hub_disc | FINAL A | WC wc2.hub_factory(disc='A') | quiet lens one step under the slices; B's scanlines are HUD language | hub_disc='A' |
| hub_inner_rings | FINAL A | wc2.hub_factory(rings='A') | one bevel gives glass and no bullseye | hub_rings='A' |
| hub_label | FINAL A | wc2.hub_factory(label='A') | readable, secondary | hub_label='A' |
| hub_emblem | FINAL A | wc2._engraved + mask WC2_CREST | engraved crest stays in the lens material; B is the sticker form (nameplate/nowords) | crest='A'; mask from kglyph2 'crest' (Y3) |
| slice_frame | FINAL A | wc2.FRAME2['A'] | B's catch-light adds an arc next to the bars | frame='A' |
| slice_screen | FINAL A | wc2.tex_phosphor | X12; icon stays brightest | screen='A' |
| slice_screen_code_text | RETIRED (none) | — | X12 | nothing drawn |
| slice_gutters | FINAL B | wc2.spokes | X13 | continuity per Y15 |
| icon_burst | FINAL A | mask wc2_glyphs.burst_b (WC2_BURST_B) | parallel tilted twins read as shells; the V's bases merge at 16-20 px | burst='B' (the code key for sheet option A) |
| icon_turret | FINAL A | wc2_glyphs.turret_a | same family as burst | turret='A' |
| icon_shield | FINAL (E10) | wc2.icons2 -> wc_base.icons_cur | unique silhouette after R1 rulings | — |
| icon_repair | FINAL A | wc2_glyphs.repair_c_plain (WC2_REPAIR_P) | plain strip reads at 16 px; B's dots read as buttons | repair='P' |
| slice_hp_bars | FINAL A | wc2.bars2 + wc2.pip | X10 | bars='A' |
| slice_pip_lost_harm | FINAL A | wc2.pip(st='harm') | X10 | — |
| slice_pip_lost_soak | FINAL+T A | wc2.pip(st='soak') | X10 | SOAK #464EFF (Y1) |
| slice_pip_mend | LATENT A | wc2.pip(st='mend') | X10 | — |
| slice_pip_gone | LATENT A | wc2.pip(st='gone') | X10, same as the HUD socket | — |
| slice_break_x | FINAL A | wc2.break_x + wc2.hatch | X plus HARM hatch reads as "will break" at 320 px; B alone is too weak | brk='A' |
| slice_soak_break_x | FINAL B | wc2.break_x(soak=True) + notch | the notch at the crossing carries the soak meaning without hue (Y1 shows hue alone is fragile) | soakx='B' (render with the B branch; SOAK #464EFF) |
| threat_trim | FINAL A | wc2.trim2 | each third keeps its own ink, so the separation reads; B's shared rail reads as a fourth arc | trim='A' |
| hp_ring | FINAL A | wc2.hp_ring2 | no slivers at the spokes; B drops sockets (content) | the 6 deg turn is accepted (it changes no count) |
| codebase_frame | FINAL A | wc2.frame2 | B's echo hairline breaks do-not 5 | cfr='A' |
| nudge_ghost | FINAL removed | wc2_run.sel_for hook blank | 3.22, do-not 8 | — |
| gun_tracers | FINAL A | wc2.dash_line + wc2.guns2 | X11 | — |
| gun_result_hit | FINAL A | wc2.spark | | — |
| gun_result_armor | LATENT A | wc2.chevron_result | B's bar is clutter | — |
| gun_result_ward | FINAL A | wc2.chevron_result (BOSS_GOLD) | appears in p2/p3 | — |
| gun_result_shield_pop | LATENT **B** | wc2.pop_shards | Y7 (A twins the crest; C's rays twin the hit spark) | guns=dict(pop='shards', wall=False) |
| gun_muzzle_beads | FINAL A | wc2.muzzle | | — |
| gun_result_sealed | RETIRED | — | | branch gone |
| gun_idle_stub | LATENT+T A | wc2.idle_stub('A') | the open ring end says "nothing hit"; C has no end | alpha **60 percent** (not 40: invisible at 320 px), 1.4 px, r164-186 |
| gun_tracers_preview | FINAL **B** | wc2.guns_preview('B') | Y8: tracer 55 percent, result 100 percent | preview='B'; also used in p3 |
| brace_plate | FINAL **C** | wc2.brace_plate2('C') + kglyph2 brace | X4 asks for the clamp-plate silhouette; A/B are only a cyan arc, and the 20 px clamp glyph beside the icon makes it Brace, not "cyan trim" | brace='C'; Brace glyph from kglyph2 |
| slice_soak_marks | FINAL A | wc2.soak_mark2('A') | the chevron repeats the pip notch, so one shape; B's funnel is the HUD destination; C crowds the X | soakmark='A' |
| slice_soak_rim_arc | FINAL A (removed) | — | pip + one mark + X is enough; B recolours the frame edge (two meanings on one stroke) | soakrim='A' (none) |
| slice_cracked_mark | LATENT A | wc2.cracked2('A') | reads at 320 px; B's hairlines vanish; C reads as a render bug | cracked='A' |
| slice_broken_state | LATENT A | wc2.broken2('A') | the ghost icon keeps what was lost; it reads "done", not preview | broken='A' |
| spin_ghost_preview | LATENT+T A | wc2.spin_ghost('A') | the only grammar without overlap (B) or hiding the label (C) | Spin ring glyph = kglyph2 spin3 (Y3) |

### 3.2 wave_rings (33 delivered + 2 owned inside)
Source: WR, picks `wr2_picks.R2` (all 'R', 'A' where removed/none). Run module map: wr2_cells (empty_cell, gutters, interior_hairlines, screen), wr2_units (outline, halo, disc, ring, armor_cue, token, hp_row, shield_bracket, rails, armour_rails, stack/chevrons, warded, gone_overlay, dead_badge, ghost, wax_outline, draw_unit), wr2_boss (ward_arc, cell, hp_bar, diamond, armor_and_strike, adjuster), wr2_latent (wide6), wr2_glyphs, wr2_lib (rseg, mesh, tint, token_pos_r2, cell_layout, chev_params), wr2_sets.

| Element | Final | Function | Why / tweak |
|---|---|---|---|
| empty_cell | FINAL R | wr2_cells.empty_cell | the faint sheen gives glass, V is a hole |
| ring_separators | FINAL R | wr2_cells.gutters, interior_hairlines | X13; continuity per Y15 |
| unit_cell_screen | FINAL R | wr2_cells.screen + wr2_lib.mesh | X12; mauve ramp kept |
| unit_screen_bezel | FINAL removed | — | |
| unit_screen_code_text | FINAL none | — | |
| unit_cell_outline | FINAL R | wr2_units.outline (drawn last but under the token) | 4/3/3 and dash 12/8 per X11; V's sheath is too heavy |
| token_disc | FINAL R | wr2_units.disc | 26 percent keeps the glyph on top |
| token_lane_base | FINAL R | wr2_units.ring | |
| token_halo | FINAL R | wr2_units.halo | shadow, not keyline (3.7) |
| glyph_packet | FINAL R | wr2_glyphs packet_R -> kglyph2 | twin IoU vs Payload 0.55: accepted (cube vs round with fuse; read by eye at 28 px) |
| glyph_worm | FINAL R | worm_R | one-bend hook, no S/M |
| glyph_payload | FINAL R | payload_R | |
| glyph_jammer | FINAL+T R | jammer_R | arcs thin at 16-20 px: arc stroke min 2 px at 20 px (scale-aware min width in the mask), no other change |
| glyph_ring | FINAL R | ring_R | the over/under gaps say "links" |
| unit_hp_row | FINAL R | wr2_units.hp_row | X10 + tray |
| chev_solid_stack | FINAL R | wr2_units.stack/chevrons + wr2_lib.chev_params | compresses only for the 4-stack |
| chev_hollow | FINAL R | same | X11 |
| chev_sector_column | FINAL R | same | |
| armor_cap | FINAL R | wr2_units.armour_rails + armor_cue | the shared radial budget |
| warded_mark | FINAL+T V size, new place | wr2_units.warded | **Y9**: 30 px lozenge / 16 px skull on the token rim |
| dead_x | FINAL+T R | wr2_units.dead_badge + gone_overlay (owns unit_gone_state, veil via wr2_lib.tint) | **Y9**: 26 px badge on the token rim; veil 38 percent |
| adjuster_cell | FINAL R | wr2_boss.cell (owns adjuster_cell_underlay: drawn instead of the empty cell) | |
| adjuster_diamond | FINAL R | wr2_boss.diamond | V's core disc makes it a token |
| adjuster_hp_bar | FINAL R | wr2_boss.hp_bar | X5, groups of 5 |
| ward_arc | FINAL R | wr2_boss.ward_arc | 3 px stays container-tier |
| consumed_unit | FINAL R | wr2_units.ghost | |
| trigger_killed_unit | FINAL R | wr2_units.ghost + wax_outline (PENCIL_PLAN) | a Trigger kill is the plan's result, so yellow; it differs from consumed by GAIN X vs stamp and wax vs clean line |
| screen_motif_skull | FINAL none | — | |
| shield_bracket | FINAL R | wr2_units.shield_bracket | |
| adjuster_armor_strike | FINAL R | wr2_boss.armor_and_strike | |
| ring_unit_wide6 | LATENT R | wr2_latent | |
| token_placement | FINAL R (rule) | wr2_lib.token_pos_r2 | 38 px from the start cap on every ring and width |
| kind_colour_set | FINAL R | wr2_sets + `r2/wave_rings/kind_colour_set.json` | Y6 |

### 3.3 outer_rings (35)
Source: OR; variant letter 'P' throughout; assembler `r2_render.render_r2` is the reference for draw order.

| Element | Final | Function | Why / tweak |
|---|---|---|---|
| backdrop_grade | FINAL P | r2_ground.grade('P') | X14; the room hull stays sharp |
| board_scrim | FINAL P | r2_ground.scrim('P') | zero by r560, before the hull |
| board_backplate | FINAL P | r2_ground.plate('P') | it reads as the ink gutter under the core, which is fine |
| bezel_ring | FINAL P | r2_ground.bezel_layer('P') | the teal reads in situ (sheet) and stays under the cells; V is too close to cell value |
| bezel_rim_lines | FINAL P | inside bezel_layer | |
| bezel_ticks | FINAL P | r2_sched.ticks('P') | |
| bezel_spokes | FINAL (added) | r2_ground.spoke_mask | Y15 |
| sched_track | FINAL P (track) | r2_ground.bezel_layer | it gives the empty stretch a designed form; the 'NT' no-track variant was never rendered correctly and is not wanted |
| sector_digits | FINAL P | r2_sched.digits('P') | 6.0 px clear of lane 0 |
| sector_digits_nowords | FINAL P | r2_sched.nowords_code | |
| needle | FINAL P | r2_sched.needle('P') | X9 |
| sched_this_turn | FINAL P | r2_sched.live_cell/live_label | now under L1 (lum 120 vs 122): the squint confirms |
| sched_chevrons | FINAL P | r2_sched.chevrons | |
| sched_hold_cells | FINAL P | r2_sched.hold_cell/hold_glyph | hourglass = kglyph2 hold |
| sched_hold_live | LATENT P | r2_sched.hold_live | |
| sched_plus_cells | FINAL P | o_sched.plus_cell('A') | |
| ring_tags | FINAL P | r2_misc.ring_tags('P'), tag_anchor | anchor for Y11 |
| ring_tags_nowords | FINAL P | r2_misc.ring_tags (nowords) | |
| ring_tag_no_wave | LATENT P | r2_misc.ring_tags (rings_wave=-1) | |
| landing_arc_frame | FINAL P | r2_arcs.frame | 2.8 px = lane-style medium tier |
| landing_arc_full_circle | LATENT P | r2_render.render_full_circle, r2_arcs.full_circle_unit | |
| arc_glyph_disc | FINAL+T P | r2_arcs.disc | glyph from kglyph2 (Y3), wash from the kind set (Y6) |
| arc_wear_mark | FINAL P | r2_arcs.wear | X10 |
| arc_now_dot | FINAL P | | |
| arc_turn_dots | FINAL P | r2_arcs.turn_dots | |
| arc_chevrons | FINAL P | r2_arcs.chevrons | |
| arc_diamonds | FINAL P | r2_arcs.diamonds | |
| arc_check | FINAL P | r2_arcs.check_mark | |
| arc_soak_chevron | FINAL+T P | r2_arcs.soak_mark | SOAK #464EFF |
| arc_brace_glyph | FINAL P | r2_arcs.brace_mark | kglyph2 brace |
| arc_twist_mark | FINAL P | r2_arcs.twist_mark | kglyph2 twist |
| future_wave_arcs | FINAL P | r2_misc.fut_geom/draw_tape | true extents kept (X17) |
| wave_arc_unit_pips | FINAL P | r2_misc.unit_pips | glyphs from kglyph2 |
| climax_hazard_ticks | FINAL P | r2_misc.haz_ticks | |
| wave_tags | FINAL+T P | r2_misc.wave_tags | flag (f), tags overlap the neighbouring tape lines: give each tag a 3 px INK knockout under its glyphs so the tape breaks under the text |

### 3.4 top_hud (36)
Source: TH `hud2.py` (`render(beat, Vd)`), all 'A'.

| Element | Final | Function | Why / tweak |
|---|---|---|---|
| header_plate | FINAL A | el_header_plate | |
| header_title | FINAL A | el_header_title (nowords: digit() skips) | the divider is one hairline; B's wedge competes with the waves chip |
| waves_left | FINAL A | el_waves_left + wedge | only the label in a chip (do-not 2); B's fused chip is a large orange area |
| help_button | FINAL A | el_help + qmark; focus = a2_kit.focus_brackets (Y5) | |
| bill_frame | FINAL A | el_bill_frame + inset | |
| terminal_plate_kit | FINAL A | P() + _scan | Y5 master; reduced_effects_state F14 |
| hud_scrim | FINAL A | scrim_layers | Y10 |
| layout_grid | FINAL A | G dict + draw_hud | Y13 numbers |
| you_hp_tally | FINAL A | hp_tally | |
| hero_pair | FINAL A | hero_pair | |
| hero_nowords_proxy | FINAL A | hero_nw | |
| eq_row | FINAL A | el_eq_row | |
| eq_labels | FINAL A | tag() | |
| row_tags | FINAL A | rowtag() / tag() | B's cyan marker adds a fourth mark per row |
| tally_segments | FINAL+T A | seg/tally/tpos/twidth | soak kind = #464EFF |
| operators | FINAL A | opdraw | |
| empty_socket | FINAL A | seg(kind gone) | |
| trig_groups | FINAL A | trig_form | |
| trig_lands_group | LATENT A | trig_lands_form | tally grammar, not hit grammar (B) |
| split_row | FINAL+T A | el_split_row | funnel + SOAK #464EFF |
| route_arrows | FINAL A | route + dest_hub/dest_funnel/dest_hp | |
| next_row | FINAL A | el_next_row | slice lost = HARM slash pip at 60 percent (F19); B's dashes would compete with X11 tracer and +2 language |
| plan_pencil_underline | FINAL A | el_plan_underline + wax | |
| best_line_tag | FINAL A | el_best_tag | a tab hung on the bill edge (B) breaks the kit |
| without_twist_row | FINAL A | without_twist | the arrow keeps it a cause and effect; B's strike reads as "cancelled" |
| option_chips | FINAL A | option_chip | focus brackets on chips (F15) |
| option_plan_glyphs | FINAL+T A | chip_glyphs + coin | glyphs from kglyph2, coin = obj2.coin_img (Y4), soak funnel #464EFF |
| option_name_label | FINAL A | chip_name | |
| option_outcome_bar | FINAL A | chip_bar | |
| option_pair | FINAL A | chip_pair | |
| chain_strip | FINAL A | chain_strip | |
| chain_step_discs | FINAL A | (in chain_strip) | |
| chain_step_glyphs | FINAL A | chain_glyph | white silhouettes from kglyph2 |
| chain_step_names | FINAL A | (in chain_strip) | |
| chain_result_tallies | FINAL+T A | (in chain_strip) | refund coin = obj2.coin_img (Y4) |
| chain_result_prose | FINAL A | (in chain_strip) | |

UNDO plate: not drawn by top_hud (actions owns it). `objectives_row` and `ram_row` in hud2 are placeholders: replace them with obj2 (3.5).

### 3.5 objectives (13)
Source: OB `obj2.py`, `obj2.V[element]='A'` for all.

| Element | Final | Function | Why / tweak |
|---|---|---|---|
| objectives_frame | FINAL A | el_obj_frame + kit_plate (-> hud2.P, Y5) | B's gold bay makes a second WIN housing that the star already gives |
| star_glyph | FINAL A | star_tile / el_star / fail_mark | the slash is the X10 slash; B's pip beside a star reads as HP |
| win_label | FINAL A | el_win_label | X16 |
| challenge_labels | FINAL A | ch_label / objectives_row | SLICES KEPT label stays (F6) |
| challenge_tallies | FINAL A | el_tally (cap_pip, gone_pip) | B's lead marks repeat board shapes in the HUD |
| challenge_trigger_hits | LATENT A | trig_tally | the 4-challenge layout is UNSETTLED (6.2) |
| ram_trace_frame | FINAL A | el_res_frame (50 px) | Y13 |
| ram_trace_labels | FINAL A | el_res_label | |
| ram_pips | FINAL A | coin_img / draw_coin | Y4 master; A's dark spent socket reads clearly as spent |
| trace_pips | FINAL A | sq_img / draw_sq | inner hairline = same construction as the coin |
| trace_cap_hatch | FINAL A | el_cap | always white, so the cap reads before it is reached; padlock into kglyph2 (F5) |
| ends_heat | FINAL A | flame_img / draw_flame | single tongue is cleaner at 22 px |
| ram_refund_pop | FINAL A | pop_rays + coin_img(plus=True) | B's fan is lopsided |

### 3.6 cards (20)
Source: CA `kcard2.py` (card_hi assembly), `kscene2.py` (fan), `kglyph2.py` (master), `krun2.py`.

| Element | Final | Function | Why / tweak |
|---|---|---|---|
| card_icon_set | FINAL+T | kglyph2 | Y3 registrations; re-run the twin check |
| hand_fan | FINAL P | kscene2 | V drops into the lit floor |
| card_frame | FINAL P | frame_under/frame_over | X15; V's 4 px ink is heavier than the stickers |
| card_header_strip | FINAL P | hdr_draw | |
| cost_badge | FINAL+T P (34) | coin/cost_draw | the coin body comes from obj2.coin_img(34) (Y4); the digit stays |
| art_band | FINAL P | art_draw | V's glow breaks 3.7 |
| card_icon | FINAL P (66) | icon_draw | |
| card_multiplier | FINAL P | mult_draw | xN kept (X17) |
| card_title | FINAL P | title_draw | |
| type_band | FINAL P | type_draw | |
| rules_text | FINAL P | rules_draw | the measure stays clear of the shingle |
| loud_tab | FINAL+T P (26) | loud_draw | the square comes from obj2.sq_img(26) (Y4) |
| loud_tab_resting | FINAL P | loud_draw | |
| card_hover_grow | FINAL P | peel | |
| played_liner | FINAL P | liner_hi | V's family tint competes with live cards |
| cards_nowords | FINAL P | nw_draw | |
| card_unaffordable | LATENT A | lat_top | dim glass + dark socket coin says "missing RAM"; C's hatch is the slice-break language |
| card_committed | LATENT A | lat_top | the pencil ring matches "selected = PENCIL_PLAN" on option chips; B's tick reads as done |
| card_exhaust_keyword | LATENT A | lat_top | keywords live in the rules (3.4); B and C invent new chips |
| card_key_hint | LATENT A | lat_top | the same keycap language as UNDO [Z]; B is cut by the screen edge |

### 3.7 actions (24)
Source: AC `a2_stick.py`, `a2_hover.py`, `a2_plan.py`, `a2_tgt.py`, `a2_kit.py`, `a2_glyphs.py`; unchanged R1 reuse `a_kit.vinyl2/wax/tally`, `a_plan.trigger_path`, `a_hover.trim_hover`.

| Element | Final | Function | Why / tweak |
|---|---|---|---|
| send_it | FINAL R2 PICK | a2_stick.send_base / stack_layer | 62 inside the margin |
| undo_chip | FINAL R2 PICK | a2_stick.undo_tab (kit -> hud2.P) | |
| nameplate | FINAL+T R2 PICK | a2_stick.nameplate | crest from kglyph2; **Y14** placement r >= 520 |
| sticker_material | FINAL R2 PICK | a_kit.vinyl2 + stack_layer | |
| stickers_nowords | FINAL R2 PICK | a2_stick (nowords) | B's arrow-into-bar reads as "download" |
| bottom_hint | FINAL R2 PICK | a2_stick.hint_line | static cursor under reduced effects (F14) |
| card_targeting | LATENT R2 PICK | a2_tgt.cues | V's outline duplicates the lane outline |
| adjuster_as_target | LATENT R2 PICK | a2_tgt.adj_geom + cues | |
| hover_tag | FINAL R2 PICK (A: 5 lines x 33 chars) | a2_hover.hover_tag | A2 touches HOLD THEN; the text is reflowed only, with nothing dropped |
| hover_path | FINAL R2 PICK | a2_hover.hover_path | |
| hover_slice_highlight | FINAL R2 PICK | a2_hover.hover_slice + a_hover.trim_hover | |
| hover_focus_dim | FINAL R2 PICK (0.38) | dim via wr2_lib.tint (Y12) | |
| hover_dim_overlay | FINAL R2 PICK (0.38) | dim layer | |
| hovered_cell_outline | FINAL R2 PICK | a2_hover.hover_cell -> a2_kit.focus_brackets | |
| trigger_path | FINAL R2 PICK (A) | a_plan.trigger_path | |
| trigger_tower_hit | LATENT A | a2_plan.tower_hit(opt A) | the standard HARM chevrons tie it to the threat grammar; B pencils the hits (pencil is the plan), C splits the hit from the stack |
| twist_badge | FINAL+T R2 PICK | a2_plan.twist_badge | anchor from r2_misc.tag_anchor (Y11) |
| refund_burst | FINAL R2 PICK | a2_plan.refund_place | |
| refund_token | FINAL+T R2 PICK | a2_kit.refund_token | body = obj2.coin_img(plus=True) (Y4) |
| resolve_fire_lines | FINAL+T | = wc2.guns_preview('B') in p3 | Y8 |
| no_target_tag | **UNSETTLED** (placement) | a2_tgt.idle_gun | words and kit tag settled; placement open (6.1) |
| nowords_variant | FINAL+T R2 PICK | plate_p1_nowords / plate_p2b_nowords_hover | the nowords hover-tag slice rows each lead with that slice's 20 px icon from kglyph2 (burst/turret/shield/repair) before its tally |
| send_it_states | LATENT A (lift/sink) | a2_stick.send_state('A') | B's hover bloom breaks do-not 10; C's straighten reads as a bug |
| focus_brackets | FINAL A | a2_kit.focus_brackets(opt A) | Y5; targets include option chips and ring tags (F15) |

New LATENT ids from section 1: `reduced_effects_state` FINAL (rule F14); `send_it_key_hint`, `card_hover_ghosts`, `card_drag_aim` UNSETTLED (6.3).

---

## 4. Cohesion check (cohesion_board_final.jpg)

- **Squint, measured on the assembled p1 (fix pass R3; replaces the earlier composite claim).** Method: 1/16 BOX + 1 px blur, luminance, regions = hull cells of the room (outside the HUD column and hand zone, 976 cells) and the board disc r <= 520 (3323 cells); loud = cells > 0.38. Room lift was lowered from x0.84 to x0.57 and green/neon saturation pulled to 0.33 (r2_ground.room_relight). Room p95 / loud: bio 0.389 / 0.066, srv 0.396 / 0.073, gh 0.384 / 0.057 (targets <= 0.40 / <= 0.10, met on all three; approved E10 p1 room: 0.420 / 0.156). Board p95 / loud on p1: 0.302 / 0.003 (E10: 0.403 / 0.080). **The board is still not the first mass: its p95 is below the room's on every plate, and board loud is far under 0.05.** One value step was applied to the L1 threat marks (HARM_UP #FF6452: ring-cell chevrons, landing-arc diamonds and zigzag chevrons, the NOW W1 tag; the live schedule cell was left muted). It moved board p95 only from 0.299 to 0.302, because those marks are 3-6 px strokes that blur away at 1/16. The brightest board cells are the white tower icons (0.45) and the unit tokens; a second step would not change the ranking. This is open for the art director (see section 6, item 5). Whole-plate squint: mean 0.188, p95 0.375, loud 0.046 (E10: 0.260 / 0.451 / 0.134).
- **One family per meaning holds across clusters:** coin/square/flame, the HP grammar (slice, unit, ring, YOU, arc wear, boss), BOSS_GOLD, the pencil family (path, trigger, underline, twist, killed ghost) and the kit plate (header, bill, objectives, RAM, UNDO, hover tag) all match on the board. The SOAK family is consistent in shape; Y1 moves its hue in one place.
- **Seams the assembler must close** (visible in the composite because each cluster rendered on E10 neighbours): the wheel_core plate still shows the E10 M worm and arrow-packet tokens on the rings, and the wave_rings plate still shows E10 slice icons. These go away once one generator draws everything. Glyph masters (Y3) and the nameplate intrusion (Y14) are the two visible cross-cluster faults; both are ruled.
- **Do-not audit:** do-not 5 holds after slice_soak_rim_arc was removed and threat_trim A, codebase A and slice_frame A were kept. Do-not 2: the only big orange is the live cell (the waves chip is chip-sized). Do-not 3: plan yellow appears only on pencil, selected chips, BEST, TRIG, committed card, twist and hover. Do-not 11: the future tape outer edge is 511.4 (24 px margin), and the nameplate is fixed by Y14.

---

## 5. Assembly instructions (one assembler, one copy of the generator, all 5 E10 states)

### 5.1 Set up (copies only)
1. Create `D:/rc_scratch/e10_design/assembly_r2/src/` and `D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/assembly/` (outputs). Never write in the E10 source, the approved plates, any cluster folder, or D:/Godot/rebel_cell. Never run `python -`: write scripts and run them by path. No commits, no Blender, kill only your own PIDs.
2. Copy in this order (later copies overwrite earlier ones; the collision scan `D:/rc_scratch/e10_design/ad_r2/collide.py` found only these overlaps):
   1. E10 base: everything in `D:/rc_scratch/combat_polish/E7_waves/E10/src/*.py` (plus bb_lib and its path setup), and `state_e10.json` read in place.
   2. wheel_core: `WC/wc_*.py` (R1 base: wc_base, wc_tower, wc_glyphs ...), then `WC/wc2.py`, `wc2_glyphs.py`, `wc2_run.py`. Do **not** copy `wc2_kglyph.py`.
   3. wave_rings: `WR/wr_*.py` (R1 base), then `WR/wr2_*.py` (lib, cells, units, boss, latent, glyphs, sets, picks, state, config, base).
   4. outer_rings: `OR/o_*.py`, `OR/r2_*.py`, and **`OR/cv_board.py` (overrides E10's)**. Actions holds an identical copy. Check: render the wheel_core tower with it and pixel-diff the r<162 region against `r2/wheel_core/plate_picks_p1.png`. If it differs, keep E10's as `cv_board_e10.py` for wheel_core.
   5. top_hud: `TH/hud2.py`. Do **not** copy `hud_glyphs.py`. Do **not** copy objectives' `OB/hud2.py` (a stale copy).
   6. objectives: `OB/obj2.py`.
   7. cards: `CA/kglyph2.py` (with `crests15` on the path, as it imports it), `kcard2.py`, `kscene2.py`.
   8. actions: `AC/a_*.py` (R1 base), `AC/a2_kit.py`, `a2_stick.py`, `a2_hover.py`, `a2_plan.py`, `a2_tgt.py`, `a2_glyphs.py`. Do **not** copy `a2_kglyph.py` or `a2_render.py` (its ground is rejected, Y10). Its `render()` may be read for the beat logic.
3. Write `asm_tokens.py` (Y2) and `asm_glyphs.py`, which imports kglyph2, registers the Y3 masters (wr2_glyphs *_R, WC2_CREST, WC2_BURST_B, turret_a, WC2_REPAIR_P, obj2 padlock), and exposes `mask(id)`. Repoint every module that imported wc2_kglyph, a2_kglyph, hud_glyphs, r2_glyphs.KIND_MASTER or the R1 kglyph to `asm_glyphs`.
4. Repoint shared drawings: kit plate -> `hud2.P` (Y5); focus -> `a2_kit.focus_brackets`; coin/square/flame -> `obj2.coin_img/sq_img/flame_img` (Y4); soak colour and HP-grammar constants -> `asm_tokens` (Y1, Y2); kind washes -> `kind_colour_set.json` (Y6).

### 5.2 One assembler
Write `asm_r2.py` with `render(beat) -> Image` for beat in p1, p2, p2b, p3, nowords. Start from `build10.make(beat)` and replace each E10 draw call with the final function, keeping build10's z-order and its beat logic (which units are consumed, hovered, keep_all in p2 and so on). The E10 call to element map is BRIEF section 5. Layer order:
1. **Backdrop** `room_bio_bare.png` (room framed at 1500,612) -> `r2_ground.grade('P')` -> `r2_ground.scrim('P')` -> `hud2.scrim_layers` (Y10). Replaces cv_lib.backdrop.
2. **Board plate** `r2_ground.plate('P')`, then `r2_ground.bezel_layer('P')` (bezel, rim lines, track) and `spoke_mask`, then `r2_sched` (ticks, schedule: live cell, chevrons, hold cells/live, plus cells), then `r2_sched.digits` (or nowords_code) and `needle`.
3. **Ring cells** `wr2_cells.empty_cell` (not for the boss cell), `wr2_boss.cell` (instead of the empty cell), `wr2_cells.screen`, `gutters`, `interior_hairlines`, `wr2_boss.ward_arc`.
4. **Units** per unit, in `wr2_units.draw_unit` order: chevrons/stack, tray/armour rails, hp_row, shield_bracket, outline, halo, disc, ring, **badge (Y9)**, glyph (asm_glyphs), armor cue; boss: `wr2_boss.adjuster` (hp_bar, diamond, armor_and_strike); consumed/killed ghosts with `wax_outline`. p2b: the dim of non-hovered units = `wr2_lib.tint` k 0.38 (Y12).
5. **Tower** (`wc2_run.plate` layers with PICKS set to section 3.1's "PICKS key"): slice frames, screens, icons, bars and pips, break X / soak X, soak mark, brace plate (p2), threat trim, HP ring, code-base frame, spokes, hub. Then **guns**: `wc2.guns2` (p1), `wc2.guns_preview('B')` (p2, p3), muzzle beads; the idle stub only if a gun has no shot (none in these states).
6. **Landing arcs and outer** `r2_arcs` landing arcs (frame, disc, wear, now dot, turn dots, chevrons, diamonds, check, soak, brace, twist mark), `r2_misc.ring_tags` / `tag_anchor`, `fut_geom` + `draw_tape`, `unit_pips`, `haz_ticks`, `wave_tags` (with the 3 px knockout). p2b: non-hovered arcs at 0.38.
7. **Actions board overlays** p2: `a_plan.trigger_path`, `a2_plan.twist_badge` (Y11 anchor), `a2_plan.refund_place` + `a2_kit.refund_token`. p2b: `a2_hover.hover_slice`, `hover_path`, `hover_cell`, `hover_tag`. Targeting and focus are latent.
8. **HUD column** `hud2.render` header, bill, chips (p2), chain (p3), with `objectives_row`/`ram_row` replaced by `obj2` (objectives row 48, resources 50).
9. **Hand** `kscene2` fan + `kcard2.card_hi` (p3 played liners).
10. **Stickers** `a2_stick`: nameplate (Y14 placement), SEND IT, UNDO tab, bottom hint.
11. **nowords**: the same beat with NOW['words'] off; every cluster's nowords branch (sector tallies, ring tag swatches, hero proxy, cards_nowords, stickers_nowords, hub crest 34 px alone).

### 5.3 Overlap resolution (who wins)
- Ground: outer_rings + top_hud slabs only (Y10). Spokes: three owners, one line (Y15). Glyphs: asm_glyphs only (Y3). Coin/square/flame: obj2 (Y4). Kit plate: hud2.P; focus: a2_kit (Y5).
- Tracers in p3: wheel_core preview B; a2_plan.fire_lines off (Y8).
- Hover: wave_rings geometry, actions look (Y12). Twist badge: actions draws it, outer_rings anchors it (Y11). UNDO: actions only. trigger_tower_hit: actions only (latent).
- Tower back plate under the core: outer_rings draws it, wheel_core covers it. That is accepted; it reads as the 160-165 gutter.
- HUD heights: objectives' numbers (Y13).
- SLICES KEPT label stays with no tally (F6).
- Badges on the token rim (Y9) win over the chevron column.

### 5.4 Content guard (must pass for every beat)
Run the E10 `build10.draw_asserts(beat, f)` and the cluster draw logs (`checks10.py`) on the assembled render. Every count, number and word is unchanged from E10. No tracer or result is added beyond f1/f2 (p2/p3 now show the real BURST sector 4 ward x2 shots: that is existing state, previously undrawn). Hover tag text = the E10 text reflowed.

### 5.5 Outputs
`r2/assembly/r3_p1_decide.png`, `r3_p2_preview.png`, `r3_p2b_hover.png`, `r3_p3_resolve.png`, `r3_p1_nowords.png` (1920x1080), plus `r3_contact.jpg` (the five at half size with E10 beside each).

### 5.6 Checks to report (not to fix silently)
1. The SOAK #464EFF CVD table (normal/deutan/protan/tritan vs TRACE_VIOLET and LANE_PLUS1) and the notch read at 320 px.
2. The kglyph2 twin check at 16/20/28/37/44/70 with the registered masters.
3. Spoke continuity (Y15). HUD bottoms 384 / 518 / 538 (Y13). Nameplate r >= 520 (Y14). Badge-over-glyph alpha = 0 (Y9).
4. A 320 px squint and deutan/tritan simulation of p1 and p2b.
5. The hover tag (p2b) does not cover the hovered unit's own landing arc. If it does, report the overlap box. Do not move the tag.

---

## 6. Not settled (and why)

1. **no_target_tag placement** (LATENT; no state shows it, so it does not block the five plates). The words and the kit tag are settled. The R2 rim-tangent placement covers that sector's threat trim and HP-ring segment, which hides content while shown, and its rotated text reads poorly. E10's placement sits on a ring cell (ruled out in R1). Every free slot inside the slice is taken by the icon, bars and soak mark. R3 must render placements against a showcase idle gun: (a) an upright tag in the code-base gutter r162-170 with a leader to the stub, and (b) an upright tag at the stub's outer end with the cell it overlaps dimmed. The rule for any option: nothing that carries a count may be covered.
2. **Four-challenge objectives row** (challenge_trigger_hits, LATENT). The 4th group (about 265 px) does not fit the row's spare width (about 150 px). A 2x2 grid adds 36 px and breaks the p1 384 budget. This needs a designer ruling: either the challenge count is capped at 3 on this screen, or the budget gives 36 px back from the chain strip in that state.
3. **New elements with no options yet:** `send_it_key_hint` (F9), `card_hover_ghosts` (F11; the grammar is fixed, the renders are missing) and `card_drag_aim` (F16). Each needs three options in R3. None appears in the five plates.
4. **Designer content rulings** (not art, not added): right-click inspect (F10), Adjuster/slice hover tags (F12), the UNDO-locked cause (F13), pointer intent labels/flicker/trail (F17), pile counters (F18).
5. **Board mass vs room (R3 fix pass, open).** After the room fix the room is at p95 0.38-0.40 and the board at 0.30: the board is not the first squint mass, and one value step of the L1 threat marks does not change that. The AD must choose: (a) accept (the board reads by structure, not by value, and E10-style loud reds were the complaint), (b) lift the tower icons and unit tokens one step, or (c) lower the room one more step (x0.50).
