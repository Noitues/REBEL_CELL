# W3 — Wheels and combat presentation (branch `art/w3-combat`)

ART_BIBLE §6.1, §6.2, §3.5, §7.1, §8, §10, §11 Combat, §12. Presentation only: no rule,
content value, balance or save format changed; preview still equals the result (tested).
W5 (characters), W4 (cards) and W7 (city) are merged in and wired.

## Images

| File | What it shows |
|---|---|
| `before_after/<combo>/<screen>.jpg` | W10 baseline (left) next to W3 (right) for `combat_start`, `hover`, `aiming`, `resolving`, `after`, `refused`, `boss_p2`, `boss_p3`, `victory`, `defeat`, at `1.0_mouse`, `1.6_pad`, `2.0_mouse` and `1.0_mouse` greyscale (40 sheets). |
| `classes_bezels.jpg` | The eight classes' wheels at turn 1 (bezel ornament, hub pattern, Polaroid inset with the class glyph badge), colour over greyscale. |
| `enemy_bezels.jpg` | One enemy per corporation plus a boss: notched corp bezels with their patterns, W5 hologram busts above, the boss at 120% with its taped nameplate, phase pips and hologram behind; colour over greyscale. |
| `strips/resolve_1x.jpg`, `resolve_2x.jpg`, `resolve_instant.jpg` | One SEND IT at each resolve speed, frames every 0.25 s of real time. |
| `strips/boss_intro.jpg` | The boss's T4 name slam over the hologram's reveal. |
| `strips/phase_change.jpg` | A phase: the hub clears for PHASE 2 (held by the stamp rule), the burst, the new needles drawing on. |
| `strips/hp_drain.jpg` | The two-stage HP drain (fill, then the white lag), the colour stepping to amber and red. |

Reproduce: `tools/visual_qa/capture_pack.py` (screens above), `before_after.py` (sheets),
`tools/design_lab/bezel_lab.tscn` (`--enemies` for the corp sheet), and
`tools/design_lab/w3_strips.tscn --mode=resolve|boss_intro|phase|hp_drain` with `make_strip.py`.

## What changed (files)

- New: `scripts/ui/kit/wheel_bezel.gd` (bezel, ornament, hub pattern, glyph and inset painters, all as testable geometry), `hub_queue.gd` (one stamp per hub), `boss_intro.gd` (T4 sting); `tools/design_lab/bezel_lab.*`, `w3_strips.*`; `tests/unit/test_art_w3_wheels.gd` (40 tests, fast).
- `scripts/ui/wheel_view.gd`: ownership bezels, class identity, HP arc (§3.5 colours, hatched ghost, two-stage drain, heartbeat, 30% dim), HP under the arc and every needle, boss scale/nameplate/pips/hologram seam, hub clear, net line, NEXT TURN plate, tag rules (one row, radius + 66, arrows clear), rim tick marks, respin settle, needle draw-on, T2 hit flash/shake, StatIcon status marks, high contrast, tokens and type.
- `scripts/ui/combat_scene.gd`: forecast split and net line, net numbers (colour, "7 − 4", capped), hub stamp queue, boss intro, resolve speed / instant / fast-forward, turn-start sequencing, drag preview and aim origin, W4 hover, W6 hit shapes and phase pattern, W7 context, dev pickers to kit, tokens.
- `heat_poster.gd` (Heat colour, caption floor, body-face consequence, tokens), `ram_bar.gd`, `outcome_row.gd`, `spinner_view.gd`, `spinner_mini.gd`, `forecast_stamp.gd`: tokens and steps.
- `motion_skip.gd`: `resolve_fast_forward` is never a press (W9's exemption).
- `ui_motion.tres` (+ REQUIRED_IDS, lab DEMOS): `bezel_ambient` T0, `hp_heartbeat` T1, `needle_draw` T2, `boss_intro` T4, `hub_clear` T1, `wheel_respin_settle` T1.
- Tests updated where a rule changed on purpose (each marked "art pass W3"): pass20/23/24 (no YOU TAKE chip; net line), anim_r2 (one number per hit), anim_r4/r5 (status glyph as a StatIcon id), anim_r4_city (caption floor on the small poster), vfx_tiers (phase burst pattern), pass24_screens (NEXT TURN key); the combat layout tests now check up to `Settings.TEXT_SCALE_MAX`.
- `tools/visual_qa/lint_baseline.json`: every W3 file at 0. `assets/text/strings.csv`: 5 rows appended.

## ART_BIBLE §14 checklist (combat)

| Item | Result |
|---|---|
| §3 tokens / §4 steps / §5 spacing | **Pass**: static lint 0 in all W3 files (tested). Ring geometry (bezel width, notch depth…) are named px constants: hardware, not type. |
| Materials not mixed | **Pass**: wheel hardware, PAPER tags / stickers / nameplate / Polaroid, GLASS status line; the paper bezel stickers are hardware decoration. |
| Focal order / one primary | **Pass**: tags → wheels → hand → SEND IT; tags are the brightest paper; one verb. |
| Six component states | n/a (no new control); dev pickers now kit components. |
| 1.0 / 1.6 / 2.0: no clip, overlap, < 12 px | **Pass** for the wheels (tested 1.0 / 1.6 / 2.0: ≥ 70% radius, no layout violation, no key hint on a tag). Gaps: see below (top bar, Polaroid caption). |
| Contrast §3.7 | **Pass**: values outlined on the bezel, HP outlined; high contrast 7:1 (tested). |
| Greyscale | **Pass**: operative = light torn stickers + smooth rim, enemy = teeth + corp pattern; eight class ornaments differ by shape (tested pairwise). |
| Pad | **Pass**: hints follow the tag rule; fast-forward on the right stick; no mouse wording added. |
| Motion / VFX tiers | **Pass**: every new entry tiered; no full-screen flash below T4 (boss intro is T4, skippable, cross-fade under reduce effects); T0 ornaments and T1 heartbeat static under reduce effects. |
| No leftovers | **Pass**: skip clears intro, hub queue, clock, needle draw. |
| Review stills | **Pass** (this folder). |

## Decisions (one line each)

1. §6.1: bezel = a 26 px ring outside the slices; slice values sit on it with an ink outline so they read on paper and metal.
2. §6.1: the enemy portrait hangs between the needles' reach and the tag (sized to that room, 30 px up to W5's bust size); a boss's portrait rides on its nameplate there.
3. §6.1: HP number under the arc for every wheel (not only multi-needle bosses): one layout, never under a needle.
4. §3.5/§12: the HP number stays `heading` (30 px) past text scale 1.0; wheel lettering follows the text scale up to 1.3 (`WHEEL_TEXT_MAX`), then yields so the wheels keep ≥ 70% at 1.6 and 2.0 (every word is also in a tooltip at full size).
5. §6.2: the tag's HP-loss chips (YOU TAKE / TAKES) and the operative's BLOCKED chip leave the tags; the loss shows on the HP arc's ghost and NEXT plate, and the operative's once as the net line.
6. §6.2: chips at `body` (15), not `label` (18): one row at 1.0 must hold the damage chips in a ~470 px tag.
7. §11: the NEXT plate reads "NEXT TURN 56" (HP after SEND IT); the bible's "−56" read as a separator, since a −56 change would contradict the NEXT value.
8. §11: "≤ 12% of the screen" measured as area (the Polaroid and poster are ~2% each).
9. §10: resolve speed runs the engine clock (Engine.time_scale) during the replay, so W6's sprites, tweens and timers all scale and one hit still flies at a time; the schedule stays in 1× seconds.
10. §10 rule 4: the turn start plays forecast fade → respins → redeal (the redeal waits for the spins).
11. Critique 3.4: partly guarded hits show one amber number with "7 − 4" beside it; fully guarded hits keep the "0" equation, moved off the HP number.
12. §6.1: hub stamps queue in HubQueue (BannerQueue's contract for effect-layer sprites); numbers keep their time and stamps wait for them.
13. §7.4: the replay's status stamp on a slice pops without a font glyph (CombatFxLayer draws text); the slice's StatIcon mark shows it.
14. Dev fight picker: TilePicker + Stepper, shown only when the combat scene runs on its own.
15. §3.5: Heat COOL on the paper wanted poster is INK (TEXT_MID on paper is ~1.4:1); warm bands get an INK outline there.
17. Review fix (§4.3 rule 4, §6.1): the hub lays out rows inside its text circle: Polaroid inset, then the name, the hub core, the status words and the extra lines. Every rect is disjoint, which is tested for the 8 classes and a boss with BLOCK, SHIELD and a phase line at 1.0, 1.6 and 2.0, at combat and lab sizes. A row that has no room steps down to `caption`; after that it folds into the hub's tooltip in this order: extra lines, inset shrink, core line, inset, status words, name. The inner ring's segment names now sit on the ring's band (tangential; the first 3 letters when the full name would bow off the band), never among the hub's words, with the full names in the tooltip.
16. `OutcomeRow` amounts: GAIN/HARM darkened for ink on paper (≥ 4.5:1, tested) until W1 adds paper inks.

## Couldn't do / known gaps

- The Polaroid's caption is cut at 2.0 ("BREAKE") — `polaroid.gd` is W5's.
- The DISPATCH box "We lost o" in the defeat captures is the subtitle still typing when the frame is taken (same in the baseline), not a clip.
- On very small wheels (three stacked enemies, the bezel lab's cells), a hub without room at `caption` folds its core line and inset, and on the smallest its name too, into the hub's tooltip. `classes_bezels.jpg` shows that: its cells are smaller than any combat wheel. In live combat at 1.0 the operative's hub shows inset → BREAKER → Breaker Core, and at 1.6 and 2.0 the name.
- The top bar at 2.0 is W8's.
- The RESPIN sticker's lettering is W2's `StickerButton._fit`; in combat it fits at 1.6 and 2.0 in the captures (it grows large at 2.0).

## Bible rules I'd question

- §6.2 "chip text in `label`" and "one row at 1.0" pull against each other; `body` chips suggested.
- §11 "NEXT TURN −56": a minus reads as a change; suggest "NEXT TURN 56" or "−4 → 56".
- §12 wheels ≥ 70% with every size × text scale: the arena's height is fixed, so the wheel's own lettering has to stop growing somewhere; the bible could say so.
