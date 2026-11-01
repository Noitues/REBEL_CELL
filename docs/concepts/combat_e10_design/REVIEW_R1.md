# E10 design, round 1: art director review

Date: 2026-11-01. Reviewed: every R1 sheet set and all seven favourite plates (wheel_core, wave_rings, outer_rings, top_hud, objectives, cards, actions), on room_bio_bare at 1920x1080. The picks are shown side by side in `r1/cohesion_board.jpg` (script: `D:/rc_scratch/e10_design/ad_r1/cohesion_board.py`). The cohesion bible changes are in BRIEF.md 3.3, 3.11 and 7.

**Overall:** the seven favourite sets mostly agree with each other, and E10's overall read survives in every one. Round 1 found real wins: the Solace teal bezel, the HP grammar, shape per resource, fixed-thirds threat trim, frosted scrim and the sharp room. It also found six real clashes between clusters:
1. **Currency shape.** RAM is a coin in objectives, but a square in the card cost and the refund token.
2. **Twin glyphs.** Spin, Jammer, Ring unit and the hub crest are all broken rings.
3. **Media and letter reads.** The twin bullets read as pause, and the crossed bandage reads as an X.
4. **HOLD glyph.** It is a ring with a bar (a no-entry sign) on the bezel and an hourglass on the card.
5. **Soak hue.** Soak still shows orange in the HUD.
6. **Content breaks.** Four favourites drop or move game information: the xN digit, the NO TARGET words, the W5 angle and the extra SLICES KEPT tally. Each one is overruled below.

Two clusters left whole states unrendered: wheel_core has 10 elements with no options. Those come first in round 2.

Verdict key: **KEEP** = settled, polish only; **PICK** = option chosen, R2 iterates on it; **MERGE** = parts of two options; **REDO** = no option works, new options in R2; **OVERRULE** = the designer's favourite is replaced; **NEW** = no R1 options, R2 must render three; **RETIRE** = not designed.

---

## 1. Cross-cluster rulings (these win over any cluster favourite)

| # | Clash | Ruling |
|---|---|---|
| X1 | RAM shape: objectives coin vs card cost square tab vs refund token square pip | **RAM = cyan coin everywhere**: a NET_CYAN disc, ink keyline, inner ring hairline at INK 60 percent. RAM pip 24 px; card cost 34 px with an Anton 24 INK digit (0 = dark socket coin, cyan 2 px ring, TEXT_MID digit); refund token = coin plus a 3 px INK plus; RAM refund pop = cyan ray ticks around the coin, inside the pip gap. |
| X2 | Shape per resource | Coin = RAM, **square r3 = Trace** (card loud tab becomes a 26 px violet square with white eye and +N), **flame = Heat**. Nothing else may use these three silhouettes. The Firewall card glyph becomes a brick wall only, so the flame stays Heat's alone. |
| X3 | SOAK token (open call 1) | **SOAK = indigo #6A6CFF + chevron notch**, darker than LANE_PLUS1 #78AAFF. It always comes with the notch shape (pip), the notch chevron (marks) or the funnel (HUD destination). LANE_PLUS1 stays an outline/trim colour only and never fills a pip. Every soak mark on every cluster changes now (top_hud SOAK label, split row, plan glyph, slice, arc). R2 must pass a deutan and tritan check of SOAK against LANE_PLUS1 and TRACE_VIOLET at 320 px. |
| X4 | Brace colour (open call 2) | **Brace = NET_CYAN + the card's clamp-plate silhouette** (card_icon_set A) everywhere: slice brace_plate, arc_brace_glyph, chain glyph, option plan glyph. Cream stays enemy HP only. |
| X5 | Boss HP colour (open call 3) | **BOSS_GOLD**: the board bar (adjuster_hp_bar A) and the HUD tally (challenge_tallies A) agree. |
| X6 | Bezel material (open call 4) | **Solace teal enamel** (bezel_ring A). The value stays below the L2 cells; no lime. |
| X7 | Card cost colour (open call 5) | Cyan RAM coin (X1). Plan yellow leaves the cost badge. |
| X8 | Glyph twins | **One glyph master library** for every cluster: white silhouette, 7.5 percent ink, 512 grid, 2-3 parts. Assignments: Spin = arrow ring cut into N steps (card A); **Breaker crest = cracked ring** (hub, nameplate, nowords sticker); **Jammer = relay pylon with broken arcs** (not a ring); **Ring unit = interlocked chain links**; **HOLD = hourglass** on the card, bezel HOLD cells and plan glyphs (ring-with-bar and pause both retired); Twist = open circular arrow (card A) on the card, twist badge, arc twist mark and chain; Packet = cube; Payload = bomb; Worm = tapered hook body with a head bulge and eye (one bend, never an S). R2 runs the bible 3.5 twin check on the whole library at 16/20/28/37/44/70 px on one sheet. |
| X9 | Media and letter reads | Twin bullets read as pause: burst and turret bullets **tilt 35 deg** toward the slice rim, staggered 4 px, with 2 streaks behind. Crossed bandages read as the removed-X: repair = **one strip** (icon_repair C) at 20 deg. The needle may never be a symmetric rhombus (that is the HP-through diamond). |
| X10 | HP grammar | One set for slice bars, unit HP rows, the HP ring, the YOU tally and the arc wear mark: **rounded segment r3; kept = GAIN (slice/player) or CREAM (enemy) / BOSS_GOLD (Adjuster); lost now = HARM solid + white 2 px slash + ink; lost to soak = SOAK + ink chevron notch; mend = GAIN 2 px outline + plus; gone = dark socket + 1.4 px hairline (solid, not dashed).** The top_hud empty socket uses the gone pip, not a ring (circle = count dot). The arc wear mark loses its salmon and uses HARM. |
| X11 | Dashes | Dashed = later / growth (+2 lane, hollow chevrons, +2 trim, NEXT ghost). Cyan dash = gun tracer only. No mend or state outline may be dashed. |
| X12 | Code text on screens | **None anywhere on the board.** slice_screen_code_text is dropped to match units. Screen texture comes only from one shared phosphor mesh (3 px pitch, max 8 percent value lift), used by both slice screens and unit CRT bowls. |
| X13 | Gutters | **One continuous 8 px INK spoke** from the hub edge through the slices, HP ring, code-base ring, wave rings and bezel, on the six sector boundaries. Interior hairlines in wide cells are 1.4 px at 30 percent. |
| X14 | Ground | One grade owner, outer_rings: backdrop_grade C (room hull sharp, city 2 px blur and x0.85) + board_scrim B (frosted pool) + hud_scrim A (two soft slabs). **The room focus hull never blurs.** The actions favourite plate blurred the whole room; that is rejected. |
| X15 | Plate kit and sticker material | One terminal kit (terminal_plate_kit A: 93 percent fill, cyan 2 px, r8, 4 px scanlines at alpha 20; hero plate 3 px; selected plan yellow 3 px) on every HUD plate, including UNDO and the hover tag. One sticker material (sticker_material A) on SEND IT, nameplate and **card frames** (card_frame A, not B). One shadow for all stickers and cards: (4,8), blur 8, k 0.5; a grown card (8,16) blur 14. |
| X16 | Type | Labels are mono 18 everywhere (22 for a row that leads). Display Anton is reserved for the header, hero pair, titles, sector digits and stickers. The objectives WIN label goes back to mono 22 gold: Anton 28 there is overruled. |
| X17 | Content | Overruled because they change WHAT is shown: card_multiplier B (drops the xN digit; B lives in nowords only), no_target_tag B (drops the words; B's bar cap lives in nowords only, without the barred circle), future_wave_arcs B as drawn (moves W5's angle; the tape must keep true angles), and challenge_tallies B/C (add a SLICES KEPT display). |
| X18 | HUD height budget | Column x 1072..1896, 8 px gaps. Bottom of the stack: p1 <= y 384, p2/p3 no more than 12 px below E10's p2/p3 bottoms. The objectives (+10 px) and bill growth are paid for out of the chain strip and option chip padding. |
| X19 | Focus | Keyboard focus = lime corner brackets (bible 2.10), one drawing (actions owns it), on every focusable thing: help, UNDO, SEND IT, cards, cells, slices. |

---

## 2. Element list review (the user's request: nothing omitted)

All seven designers checked their lists against the generator. I re-checked their findings against the E10 source. `cv_over.slice_badges` is defined but never called. `cv_over.bezel` (the 'WAVE TURNS' caption) is called only by build8, not build10. `e8lib.token_pos` exists. Results:

**Added to the inventory (now owned; R2 renders them):**
| Element | Cluster | Why |
|---|---|---|
| `glyph_jammer` | wave_rings | Jammer token glyph had no owner (added in R1) |
| `glyph_ring` | wave_rings | Ring unit glyph had no owner (added in R1) |
| `gun_muzzle_beads` (renamed from gun_tracer_burst_pair, now covers 1 and 2 beads) | wheel_core | TURRET single muzzle had no owner |
| `token_placement` | wave_rings | Rule: token at the start cap of a unit, the same rule for widths 1/2/3/6 (today 58 px CCW of the first axis) |
| `kind_colour_set` | wave_rings (bible token table) | Per-kind wash set incl. the unseen Jammer and Ring washes; shared with arc_glyph_disc |
| `adjuster_cell_underlay` | wave_rings (inside adjuster_cell) | E10 paints an empty cell, a dim orange outline and boss programme art under the gold glass. R2 draws the Adjuster cell **instead of** the empty cell (no double paint) |
| `unit_gone_state` | wave_rings (inside dead_x) | Cell and chevron dim for a shot-dead unit |
| `ring_tag_no_wave` (LATENT) | outer_rings | rings_wave = -1 drops the W part |
| `landing_arc_full_circle` (LATENT) | outer_rings | width-6 Ring arc, untested |
| `row_tags` | top_hud (inside eq_labels) | SPLIT / NEXT / LANDS / THROUGH labels, now explicit |
| `card_unaffordable` (LATENT) | cards | RAM below cost |
| `card_committed` (LATENT) | cards | card chosen in the plan before SEND IT |
| `card_exhaust_keyword` (LATENT) | cards | GDD A.1 exhaust / Starting Bug, third rules line |
| `card_key_hint` (LATENT) | cards | GDD 9.5 number key per card |
| `send_it_states` (LATENT) | actions | hover, focus, pressed, disabled |
| `focus_brackets` | actions | one shared keyboard-focus mark (X19) |
| `adjuster_as_target` (LATENT) | actions (inside card_targeting) | targeting view on the boss |

**Moved:** `trigger_tower_hit` goes wheel_core -> **actions** (one pencil family with trigger_path; actions already drew the branch). The tower back plate and the 160-165 px gap before the ring cells belong to **outer_rings board_backplate** (ring_base inner disc r~230), not to slice_gutters. The UNDO plate belongs to **actions undo_chip**; top_hud draws no UNDO. The twist badge anchor on the ring tag belongs to **actions twist_badge**, re-anchored to whatever ring_tags A settles.

**Retired (confirmed not drawn by build10):** `gun_result_sealed` (the seal mechanic is gone), `cv_over.slice_badges` (p3 BLOCKED / HOLDS badges), the `cv_over.bezel` 'WAVE TURNS' caption, the ring-with-bar HOLD glyph, the pause glyph.

**Not added (it would be new information):** draw/discard pile counters (GDD has piles; E10 shows none). This is a game-content question for the designer, not art.

**Still with no R1 options (round 2 does these first):** wheel_core `gun_idle_stub`, `gun_tracers_preview`, `brace_plate`, `slice_soak_marks`, `slice_soak_rim_arc`, `slice_cracked_mark`, `slice_broken_state`, `spin_ghost_preview`, plus `trigger_tower_hit` (now actions). `gun_result_shield_pop` needs two new shapes, because its three R1 options share one. `nowords_variant` (actions) has one table sheet and no per-option crops: R2 renders a full nowords plate of the picks.

Inventory after this review: 183 + 17 added - 1 retired element (gun_result_sealed); BRIEF section 8 lists the changes.

---

## 3. Per element: verdict, kept option, direction

### 3.1 wheel_core
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| hub_disc | PICK | A | Near-black glass, NET_CYAN rim 2.6 px, ink halo 4 px at 60 percent. Drop B and C. |
| hub_inner_rings | PICK | A | One bevel arc, light top-left (matches the cutaway light), 1.4 px, +12 / -12 value. |
| hub_label | PICK | A | Anton 17 white + 2 px ink, 6 px under the crest. Keep it (the nameplate is far away). |
| hub_emblem | PICK | A | Cracked ring = **Breaker crest** (X8), NET_CYAN engraved, 22 px; the same drawing goes to the nameplate and the nowords sticker. |
| slice_frame | PICK | A | Type-colour edge 2.2 px, ink outside, r9 even, 8 px gutters (X13). |
| slice_screen | PICK | A | Phosphor mesh 3 px (X12); value capped so the icon stays the brightest thing in the wedge; no rainbow halo. |
| slice_screen_code_text | OVERRULE | none | Removed (X12). |
| slice_gutters | PICK | B | 8 px INK strip continues through the HP ring and code-base frame (X13). Drop C's spoke engraving. |
| icon_burst | PICK + fix | A | Twin bullets tilted 35 deg outward, staggered 4 px, 2 streaks each (X9). 44 px. B and C pruned. |
| icon_shield | KEEP E10 | current | Keep the E10 split heater: the warded mark is now a lozenge and Brace a clamp, so the shield silhouette is the SHIELD slice's alone. A (face), B (circle = token) and C (reads as a letter) are pruned. |
| icon_turret | PICK + fix | A | Single bullet, the same 35 deg tilt and streak as burst. |
| icon_repair | OVERRULE | C | One wide strip with pad and perforations at 20 deg (A and B read as the X). |
| slice_hp_bars | PICK | A | The X10 set; equal length on all six; capsule 7 px tall, gap 3 px. |
| slice_pip_lost_harm | PICK | A | HARM + 2 px white slash + ink. |
| slice_pip_lost_soak | PICK | A | SOAK #6A6CFF + ink chevron notch 4 px (X3). |
| slice_pip_mend | PICK | A | GAIN 2 px outline + plus, LATENT. |
| slice_pip_gone | PICK | A | Dark socket + 1.4 px hairline, solid. |
| slice_break_x | PICK | A | Heavy HARM corner X at the wedge's outer corner (beside the icon, never over it), 6 px + ink, plus a 45 deg hatch dim at 35 percent. |
| slice_soak_break_x | PICK | A | Same geometry in SOAK. |
| threat_trim | PICK | A | Fixed thirds: now (HARM, bold 6 px, 35 percent bloom), next (LANE_PLUS1 4 px), later (LANE_PLUS2 dashed 3 px). |
| hp_ring | PICK | A | 6 px segments in groups of 5, X10 states. |
| codebase_frame | PICK | A | One NET_CYAN ring 2 px at the HP ring outer edge, ink outside; broken only by the 8 px spokes. |
| nudge_ghost | PICK | A (removed) | Removed per 3.22 Open and do-not 8. |
| gun_tracers | PICK | A | NET_CYAN dash 12/6, 3 px + ink, ends at the target cell centre. |
| gun_result_hit | PICK | A | White 8-point spark 18 px + ink. |
| gun_result_armor | PICK | A | STEEL chevron ricochet + ink, LATENT. |
| gun_result_ward | PICK | A | BOSS_GOLD chevron ricochet. Also draw the sim's real p2/p3 ward shots (gun_tracers_preview). |
| gun_result_shield_pop | REDO | A shape kept as one candidate | Two new shapes: a cyan ring that breaks in 4 arcs, and a hex shard burst. All 22 px, dark core. |
| gun_tracer_burst_pair -> gun_muzzle_beads | PICK | A | Muzzle beads 6 px NET_CYAN + ink: 2 for BURST, 1 for TURRET. |
| gun_result_sealed | RETIRE | - | Delete the branch. |
| gun_idle_stub | NEW | - | Three options; it should read as "gun with no shot this turn": cyan stub 1.4 px at 40 percent. |
| gun_tracers_preview | NEW | - | Draw f2's BURST sector 4 ward x2 in p2/p3 with the A tracer at 55 percent (matches resolve_fire_lines). |
| brace_plate | NEW | - | Cyan clamp-plate silhouette (X4) across the slice rim, 2 rivets, ink; three sizes/placements. |
| slice_soak_marks | NEW | - | Inward SOAK chevrons; prune the family to at most two marks per soaking slice (pip + one mark). |
| slice_soak_rim_arc | NEW | - | Option C of the three must be "removed" (the trim slot already speaks); do-not 5 (no more than two parallel arcs in 12 px). |
| slice_cracked_mark | NEW | - | Crack in the frame, not over the icon (do-not 4). |
| slice_broken_state | NEW | - | Slice dim + break X result; it must read differently from break_x (preview vs done). |
| spin_ghost_preview | NEW | - | GDD 9.2 card-hover ghost: the tower rotated by N, at 38 percent, with Spin's arrow ring as the only new mark. |

### 3.2 wave_rings
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| empty_cell | PICK | A | Void tint, one 1.4 px lane hairline at 30 percent, no orange edge. |
| ring_separators | PICK | B | 8 px INK gutters aligned with the slice spokes (X13); wide-cell interior hairlines 1.4 px at 30 percent. |
| unit_cell_screen | PICK | C | CRT bowl (dark inner edge to lit outer edge) on the shared 3 px mesh (X12); mauve values stay (PL10). |
| unit_screen_bezel | PICK | A (removed) | Removed. |
| unit_screen_code_text | PICK | A (none) | None. |
| unit_cell_outline | PICK | A | Ink-sheathed, drawn last; now 4 px HARM, +1 3 px LANE_PLUS1, +2 3 px LANE_PLUS2 dash 12/8. Pick together with hp row and armor (shared radial layout). |
| token_disc | PICK | A | 54 px, kind colour at 26 percent. |
| token_lane_base | PICK | A | Rim ring 4/3/3; +2 six long dashes. |
| token_halo | PICK | A | Tight INK pool 1.5 px, blur 4, 75 percent. |
| glyph_packet | PICK | A | Cube, 37 px. Twin check vs Brace plate. |
| glyph_worm | PICK + fix | B | One bend, head bulge + eye dot, taper to the tail; must not read as S or M at 28 px. |
| glyph_payload | PICK | A | Bomb with fuse; fuse 2 px min at 28 px. |
| glyph_jammer | OVERRULE | B | Relay pylon with broken broadcast arcs (A twins Spin and the crest). |
| glyph_ring | OVERRULE | C | Interlocked chain links (B twins Spin and the tower). |
| unit_hp_row | PICK | A | X10 set, CREAM kept; capacity tray on the sector axis. |
| chev_solid_stack | PICK | A | Stem-less V, HARM 6 px on 10.5 ink. |
| chev_hollow | PICK | B | Dashed V (X11). |
| chev_sector_column | PICK | A | Baseline tick per unit stack, 1.4 px. |
| armor_cap | PICK | B | Armour tiles + steel cap on the token, STEEL / STEEL_HI. |
| warded_mark | PICK | A | Gold lozenge with skull; skull 16 px min; placed beside the token. |
| dead_x | PICK | A | GAIN X badge beside the token (not over), cell and chevrons dimmed to 38 percent (= unit_gone_state). |
| adjuster_cell | PICK | A | Brass gradient glass, 3 px BOSS_GOLD edge; replaces the empty cell (no underlay). |
| adjuster_diamond | PICK | A | 72 px double edge, white skull 24 px. |
| adjuster_hp_bar | PICK | A | BOSS_GOLD pips in groups of 5 (X5). |
| ward_arc | PICK | A | BOSS_GOLD strip in the ring-NOW inner gutter, 3 px. |
| consumed_unit | PICK | A | Ghost 40 percent, PENCIL_PLAN 3 px outline (it is the plan's result), Trigger stamp from the glyph library. |
| trigger_killed_unit | PICK | A | Ghost + small GAIN X; the red dashed outline goes wax (pencil style, matches trigger_path); keep the token visible clear of the pencil X end cap. |
| screen_motif_skull | PICK | A | None. |
| shield_bracket | PICK | A | NET_CYAN under-bar 3 px below the shielded pips. |
| adjuster_armor_strike | PICK | A | Unit chevron grammar on the boss cell + steel cap. |
| ring_unit_wide6 | PICK | A | Seamed band, end caps, token at the start cap (token_placement). |
| token_placement | NEW | - | Write the rule and show widths 1/2/3/6. |
| kind_colour_set | NEW | - | One table, all six kinds incl. Jammer and Ring; deutan sheet. |

### 3.3 outer_rings
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| board_scrim | PICK | B | Frosted pool, 6 px blur + SCRIM 55 percent, fading before the room hull (X14). |
| backdrop_grade | PICK | C | Room sharp, city blurred 2 px and x0.85; the only grade pass. |
| board_backplate | PICK | B | Plate to the bezel + lane annulus with a gutter; owns the tower back plate and the 160-165 px gap. |
| bezel_ring | PICK | A | Solace teal enamel, circumferential grain, top-left bevel (X6). |
| bezel_rim_lines | PICK | A | Ink edges + one top-left hairline in the bezel colour; no orange glow. |
| bezel_ticks | PICK | A | Incised ticks, ink + pale lip, 1.4 px. |
| sector_digits | PICK | A | Casting boss at r392, Anton 24. Check lane 0 (r410) clearance; 6 px min. |
| sector_digits_nowords | PICK | A | Zero ring + tallies 1-5. |
| needle | PICK + fix | A | Pointer 10 x 26 px, white + ink, with an 8 px stem into the band; never a symmetric rhombus (X9). |
| sched_this_turn | PICK | A | Arrow-end cell, value lowered under L1 (it must not outweigh the threat), INK text 19 with a drawn plus; bloom 4 px at 30 percent max. |
| sched_chevrons | PICK | A | Fine pale chevrons, 26 px pitch. |
| sched_hold_cells | PICK + fix | A | Dark glass, orange outline, 18 px pale text, **hourglass glyph** (X8). |
| sched_hold_live | PICK | B | Dark glass, 4 px orange rule, hatch, hourglass. |
| sched_plus_cells | PICK | A | Ember fill, bright edge, arrow end. |
| ring_tags | PICK | A | Pennants, Anton 20, drawn plus; add the LATENT ring_tag_no_wave; leave an anchor for the twist badge. |
| ring_tags_nowords | PICK | A | Swatch + wave tally. |
| landing_arc_frame | PICK | A | Capsule, round start cap, arrow end; render the LATENT full-circle width-6 arc. |
| arc_glyph_disc | PICK | A | 27 px exact board token + lane base ring; glyphs from the master library. |
| arc_wear_mark | PICK + fix | A | X10 lost pip in HARM (not salmon). |
| arc_now_dot | PICK | A | 18 px HARM dot, white 2 px ring. |
| arc_turn_dots | PICK | A | Dots in an ink pill slot. |
| arc_chevrons | PICK | A | Body grammar at 22x10; inward-pointing everywhere (accepted). |
| arc_diamonds | PICK | A | Bigger; later turns darker (not hollow, which is chevron grammar). |
| arc_check | PICK | B | GAIN check in the empty diamond slot. |
| arc_soak_chevron | PICK | A | Soak capsule pip in SOAK (X3). |
| arc_brace_glyph | MERGE | A colour + card A shape | Cyan, the card's clamp-plate silhouette at 22 px (X4). |
| arc_twist_mark | PICK | A | Quiet 21 px ink disc, thin PENCIL_PLAN ring, Twist glyph from the library. |
| future_wave_arcs | MERGE | B tape + A weight, true angles | Two rings of tape, each wave at its **true angular extent** (X17). An overlapping wave steps to the second ring; a third overlap uses a 2 px hairline at 60 percent; 24 px screen margin. |
| wave_arc_unit_pips | PICK | A | 27 px token disc, boundary bar ticks. |
| climax_hazard_ticks | PICK | A | CRT_AMBER / INK tape (caution meaning). |
| wave_tags | PICK | B | Anton 20 keylined on the tape, no box; nowords = tally. |

### 3.4 top_hud
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| header_plate | PICK | A | Flush with the bill edge, 56 px, kit edge, 20 px padding. |
| header_title | PICK | A | Small TURN + keylined Anton 44 digit, hairline cyan divider, mode Anton 26. The nowords header hides the digit as E10 did (fix). |
| waves_left | PICK | B | Label in an orange-edged chip (chip-sized orange only); pips as bezel-cell wedges; the climax pip stays HARM. |
| help_button | PICK | A | 30 px kit chip, cyan hairline, drawn white ?; focus via focus_brackets. |
| bill_frame | PICK | A | Kit at hero weight 3 px cyan r8 (replaces the white box); inner rows are flat insets. |
| terminal_plate_kit | PICK | A | X15. |
| hud_scrim | PICK | A | Two soft SCRIM slabs (column, hand), 24 px feather, no blur over the room hull. |
| layout_grid | PICK | A | X18; remove the magenta guides from the plates. |
| you_hp_tally | PICK | A | X10, YOU inline. |
| hero_pair | PICK | A | Anton 58, 4 px keyline, labels on the digit edges, **neutral TEXT_HI arrow** (plan yellow off). |
| hero_nowords_proxy | PICK | A | Hero-size grouped segments 12 white, neutral arrow, 6 HARM. |
| eq_row | PICK | A | Identical columns, operators centred in equal gutters. |
| eq_labels | PICK | A | Mono 18 +8 percent, TEXT_MID, centred; owns row_tags (SPLIT, NEXT, LANDS, THROUGH). |
| tally_segments | PICK | A | One size system 7x15 r3, group gap 16, RAW at 62 percent value. |
| operators | PICK | A | Vector bars + ink on the tally centreline. |
| empty_socket | OVERRULE | gone pip | X10 gone pip (C's ring = count dot; A's dashes = later). |
| trig_groups | PICK | A | Secondary size 7x12, PENCIL_PLAN (the TRIG group is the plan). |
| trig_lands_group | PICK + fix | A | HARM segments (not PENCIL_THREAT: a tally is not pencil) with a white pierce tick; LATENT mock is OK. |
| split_row | PICK | A | One baseline; soak destination funnel outlined in SOAK, label SOAK in TEXT_MID (orange gone). |
| route_arrows | PICK | A | Bold arrows; destination icons match the board (hub ring cyan, slice funnel SOAK, HP segment GAIN). |
| next_row | PICK | A | Icon-led groups, ghost at 60 percent. |
| plan_pencil_underline | PICK | A | Wax stroke exactly under the HP width, 7 px + ink. |
| best_line_tag | PICK | A | Dark chip with plan-yellow hairline. |
| without_twist_row | PICK | A | Hollow bad case, PENCIL_PLAN arrow, solid result. |
| option_chips | PICK | A | Kit chips, selected = PENCIL_PLAN 3 px. |
| option_plan_glyphs | PICK | A | 24 px library glyphs; soak token SOAK, refund token = coin + plus. |
| option_name_label | PICK | A | Mono 18; BEST in plan yellow. |
| option_outcome_bar | PICK | A | Fixed order, group gaps, empty slots as gone pips. |
| option_pair | PICK | A | Hero grammar small; the arrow is neutral. |
| chain_strip | PICK | A | Kit table, hairline dividers; padding pays for X18. |
| chain_step_discs | PICK | A | Plain mono numerals. |
| chain_step_glyphs | OVERRULE | A | White library silhouettes (B's coloured glyphs break the one glyph style); the LANDS skull is replaced by the HARM chevron glyph (the skull is the boss's). |
| chain_step_names | PICK | A | Mono 18 TEXT_MID. |
| chain_result_tallies | PICK | A | Fixed start column. |
| chain_result_prose | PICK | A | Mono 18, own column. |

### 3.5 objectives
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| objectives_frame | PICK | A | Twin kit plate, 48 px. |
| star_glyph | PICK | A | Sticker star, ink in all states; open = white outline, met = reward gold #FFD24D, failed = dark + HARM slash beside the star (do-not 4: offset the slash off the star body). |
| win_label | OVERRULE | A | Mono 22 reward gold, +10 percent tracking (X16). |
| challenge_labels | PICK | A | Inline flow, mono 18, equal gaps. |
| challenge_tallies | PICK | A | X10 capsules, groups of 5; Adjuster BOSS_GOLD, Trace violet; **no SLICES KEPT tally** (X17). |
| challenge_trigger_hits | PICK | A | Cream pips, 8 sockets in groups of 5, LATENT. |
| ram_trace_frame | PICK | B | Kit plate with two hairline dividers (bays), 54 px. |
| ram_trace_labels | PICK | A | Inline mono 18, 12 px gap. |
| ram_pips | PICK | B | RAM coin 24 px (X1); spent = hollow ring 2 px cyan at 50 percent. |
| trace_pips | PICK | A | Square 22 r3 violet + ink; unlit = near-black socket, faint violet hairline. |
| trace_cap_hatch | PICK | B | White padlock + ink on the cap pip (the retired seal padlock is gone, so there is no twin). |
| ends_heat | PICK | C | CRT_AMBER flame pips 22 px (X2). |
| ram_refund_pop | PICK | A | Cyan ray ticks inside the pip gap + ink plus on the coin. |

### 3.6 cards
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| hand_fan | PICK | A | Shingle arc, 5 deg/card, ends drop 15 px, clears SEND IT and the lit floor. |
| card_frame | OVERRULE | A | 12 px white die-cut, 3 px ink, r16/r10, shared shadow (X15); B's kiss-cut hairline is pruned (stickers do not have it). |
| card_header_strip | PICK | A | 30 px cap strip, cost left, loud tab right, 12 px safe margin. |
| cost_badge | MERGE | B -> coin | RAM coin 34 px with INK Anton 24 digit (X1). |
| art_band | PICK | A | Mid value, 6 px sine scan, no moire. |
| card_icon | PICK | A | 66 px white glyph, 7.5 percent ink, centred. |
| card_icon_set | PICK | A | This set seeds the glyph master library (X8); Hold = hourglass, Firewall = brick wall only, Brace = clamp plate. |
| card_multiplier | OVERRULE | A | Anton xN locked to the icon; B cuts only in nowords (X17). |
| card_title | PICK | A | Anton 28 + 2.2 px ink, autofit 22. |
| type_band | PICK | A | Compact family chip + hairline rule. |
| rules_text | PICK | A | Verb Medium white, rest Regular TEXT_MID, 12 px margin. |
| loud_tab | MERGE | A -> square | 26 px TRACE_VIOLET square r3 + ink, white eye, +N (X2). |
| loud_tab_resting | PICK | A | Right header, visible at rest. |
| card_hover_grow | PICK | A | Page curl, 1.22x, grown shadow (8,16). |
| played_liner | PICK | A | Dim glass, dashed kiss-cut edge (= later/empty), ghost glyph, PLAYED 19 + ink. |
| cards_nowords | PICK | A | RAM coins, redacted bars, cut-arrow Spin (B multiplier). |
| card_unaffordable / card_committed / card_exhaust_keyword / card_key_hint | NEW (LATENT) | - | Three options each, in the deck strip. |

### 3.7 actions
| Element | Verdict | Kept | R2 direction |
|---|---|---|---|
| send_it | PICK | A | One-line vinyl yellow gradient, 9 px die-cut, inside the 24 px margin. |
| undo_chip | PICK | A | Tab tucked under the sticker top edge, kit material, word 22 + Z keycap; locked = grey tick. |
| nameplate | PICK | A | Corner label, two lines + Breaker crest (= hub emblem drawing). |
| sticker_material | PICK | A | X15. |
| stickers_nowords | PICK | A | Arrow-through-ring verb, undo arc, crest + 9 tally. |
| bottom_hint | PICK | A | Mono 18 under the stack, block cursor. |
| card_targeting | PICK | A | White hairline corner ticks; focus via focus_brackets; add the Adjuster view. |
| hover_tag | OVERRULE | A | Bottom-left callout, PENCIL_PLAN leader, Plex 20, <= 41 chars/line, kit plate (B covers the HOLD NEXT/THEN bezel). |
| hover_path | PICK | A | Wax pencil 7 px + ink, open arrowhead. |
| hover_slice_highlight | PICK | A | Yellow rim arc in the trim slot, the hovered trim removed (do-not 5). |
| hover_focus_dim | PICK | A | Non-hovered unit screens at 38 percent. |
| hover_dim_overlay | PICK | A | Marks and arcs at one value, 38 percent; check do-not 5 where arcs remain. |
| hovered_cell_outline | PICK | A | Lime corner brackets (= focus_brackets drawing). |
| trigger_path | PICK | A | Wax line from the Payload edge, hand-drawn X on the target. |
| trigger_tower_hit | NEW (moved in) | - | PENCIL_THREAT wax line to the slice rim + chevron stack; three options. |
| twist_badge | PICK | A | Pill the height of the tag, library Twist glyph + chevron, anchored to ring_tags A. |
| refund_burst | PICK | A | Token on the cell's open stretch, REFUND mono 18 tag. |
| refund_token | MERGE | A -> coin | Coin + plus; pale cyan star at board size, halo at row/chip, coin only at the strip. |
| resolve_fire_lines | PICK | A | gun_tracers A at 55 percent with result marks. |
| no_target_tag | OVERRULE | A | Terminal tag across the slice rim, never over a cell, words kept (X17). |
| nowords_variant | PICK | A | Glyph or tally for every word and digit; R2 renders a full nowords plate of all picks. |
| send_it_states / focus_brackets | NEW | - | Three options each. |

---

## 4. Round 2 instructions (all clusters)
1. Build the **glyph master library** first (cards owns `kglyph`; wave_rings and wheel_core import it). One twin-check sheet.
2. Apply X1-X19 in each cluster's harness; re-render the favourites as **one integrated plate set** (p1, p2, p2b, p3, nowords) from one assembler, so the first R2 review is of the whole screen, not seven partial plates.
3. Render every NEW element with three options before polishing the picks.
4. Every sheet: CURRENT, PICK, two variants of the pick (size or weight steps), at 2x in situ + 320 px squint + deutan.
5. Hard rules are unchanged: no `python -`, work on copies, state and content fixed, room_bio_bare at 1920x1080.
