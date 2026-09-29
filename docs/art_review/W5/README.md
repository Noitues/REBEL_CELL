# W5 Characters: class silhouettes, expressions, enemy busts, boss hologram, dossier

Branch `art/w5-characters` (from `art-pass`). ART_BIBLE §7.1, §7.2, §6.1, §3.6, §12. Presentation only: no rule, content value, save format or public signal changed.

## Images

| File | What it shows |
|---|---|
| `classes.png` | The eight classes (columns) x four expressions in NEON BUST, then one row each in XEROX ZINE, WIRE SCAN and MUGSHOT, then two rows of per-operative variation (op_3, op_4). Rendered by `tools/design_lab/portrait_concepts.tscn -- --sheet=classes` (windowed through `run_windowed.py`). |
| `classes_grey.png` | The same sheet in greyscale: every class reads by silhouette and prop alone. |
| `enemies.png` | Every corp: agents, machines and bosses as NEON busts in the corp hue with the corp pattern on the body, then two `Hologram` busts per corp. |
| `bosses.png` | The five bosses as `Hologram` (Mode.BOSS): full brightness (top) and at `BOSS_DIM` as they sit behind their wheel (bottom). Each has the corp pattern halo. |
| `boss_hologram.png` | The boss hologram at 40% of 720 px (288 px) behind a stand-in 120% wheel, dimmed: the slice values stay readable. The wheel is a stand-in; W3 places the real one. |
| `boss_intro_strip.png` | `Hologram.play_intro()`: the T4 reveal at 0, 0.2 … 1.0, then the reduce-effects cross-fade at 25/50/75/100%. |
| `before_after/<screen>_<combo>.jpg` | W10 harness captures of `hq`, `hq_crew`, `combat_start`, `combat_boss_p2` at 1.0 mouse and 1.6 pad: the W10 baseline (`art-pass/docs/art_review/W10/baseline/full`) left, this branch right. |
| `concepts/` | Q6 pixel-art concepts (64 px x6): 8 classes x 4 expressions, an agent and a machine per corp, the five bosses, and `contact_sheet.png`. Concepts only, never shipped. |

## What changed (files)

- `scripts/ui/kit/portrait_art.gd`
  - `CLASS_IDS` and a head-and-shoulders silhouette + prop per class (§7.1 table); `shapes()` (was `_shapes`), `silhouette_polygons`, `silhouette_mask`, `mask_difference`, `draw_silhouette`.
  - Per-operative variation: `hair` (4), `visor` (3) and a shade of `Palette.class_accent` (±7%); the old shared `OPERATIVE_TINTS` (critique 69–76: "three tints") is gone.
  - `enum Expr { NEUTRAL, HURT, TRIUMPHANT, FLATLINED }` (`Expression` is a native class name); `draw_operative(..., expression = NEUTRAL)`, `operative_subject(..., expression)`, `with_expression`.
  - Enemies: `enemy_subject` carries `corp` and `pattern`; every look fills the body with the `CorpPattern`; bosses get sloped shoulders and a pattern halo (`boss_halo`); `enemy_data_subject(EnemyData)`.
  - 16 literal colours → tokens (0 left); text under 12 px removed (WIRE "THREAT: MAX", the MUGSHOT height numbers and "MOST WANTED"; the placard name shows only when it fits at `caption`). Polygons clip to the portrait rect.
- `scripts/ui/kit/polaroid.gd`: `expression` + `set_expression(e)`; caption in handwriting at `label`, stepping down to fit, never under `caption`; low-HP glitch bars in `HARM`; `image_rect()`, `caption_font_size()`.
- `scripts/ui/kit/hologram.gd` (new, `Hologram`): enemy/boss hologram Control (see API below).
- `scripts/ui/kit/crew_card.gd`: class accent stripe, silhouette glyph + class tag, rank as the Polaroid caption, stat fields, HP strip on `Palette.hp_color`, FLATLINED stamp in `HARM` (posting stamps in ink), flatlined portrait when dead, high contrast, all sizes from `UiTheme` steps/spacing; `set_stats`, `stat_field`, `text_labels`, `text_color`.
- `scripts/ui/kit/stat_field.gd` (new, `StatField`): StatIcon + number.
- `content/config/ui_motion.tres`, `scripts/data/ui_motion_data.gd`, `tools/design_lab/motion_lab.gd`: `hologram_idle` (T0, 4 s, 0.08), `hologram_intro` (T4, 1.4 s), `hologram_intro_fade` (T4, 0.4 s) and their lab demo.
- `assets/text/strings.csv`: `RANK %d`, `R%d`, `// %s` appended.
- `tools/design_lab/portrait_concepts.gd`: the W5 sheets (`--sheet=classes|enemies|boss|intro`).
- `tools/art_concepts/character_concepts.py` (new), `docs/art_briefs/characters/**` (24 briefs + index).
- Tests: `tests/unit/test_art_w5_characters.gd` (new, fast, 18 tests); `test_horizontal_pass20_screens.gd` (`_shapes` → `shapes`); `test_anim_r1_campaign.gd` (finds the HP field instead of an "HP …" sentence). `tools/visual_qa/lint_baseline.json` lowered: crew_card, polaroid, portrait_art now 0.

## Measurements
- Closest class silhouettes (mask XOR / union, 48x48): rigger/botnet 0.142; the test floor is 0.12. Every sampled operative's silhouette stays nearest its own class, and its tint nearest its own accent.
- Runtime lint on the after captures (`hq`, `hq_crew`, `combat_start`, `combat_boss_p2` at 1.0 mouse and 1.6 pad): **0** `crew_card` findings (baseline on the same screens: 12 font at 1.0, 12 font at 1.6 plus 2 overlap). The dossier labels are now §4.2 steps (name `label`, class and numbers `caption`), INK opaque (was 75%).

## ART_BIBLE §14 checklist (what W5 touched)

| Item | Result |
|---|---|
| Only §3 tokens, §4 steps, §5 spacing | Pass: 0 literal colours or sizes in portrait_art, polaroid, crew_card, hologram, stat_field (static lint). Drawing proportions in the painters are shape geometry, not tokens. |
| Materials not mixed | Pass: Polaroid and dossier are PAPER; the hologram is net light (crt_overlay, never on paper). |
| Focal order / one primary | n/a (components; the HQ's order is W8b's). |
| Six component states | Partial: the dossier keeps hover (Polaroid tilt) and focus via its orders; no new interactive states. |
| 1.0 / 1.6 / 2.0: no clip, overlap, text < 12 px | Pass for the dossier (test at all three; lint 0 at 1.0/1.6). Polaroid caption never under `caption`. |
| Contrast §3.7 | Pass: dossier text INK on NOTE_PAPER > 4.5:1; high contrast TEXT_HI on black > 7:1 (tested). |
| Greyscale | Pass: `classes_grey.png`; corp patterns on every enemy body and boss halo. |
| Pad | Pass (1.6 pad captures); nothing mouse-only added. |
| Motion / tiers | Pass: idle T0 (≥ 3 s period), intro T4 ≤ 2.5 s, reduce effects static + cross-fade (tested). |
| No placeholder / leftovers | Pass. |
| Review stills | Pass (this folder). |

## Decisions
1. §7.1: the per-operative tint is the class accent lightened or darkened by 7% (`SHADE_STEP`); 12% let a dark Overclocker sit nearer Breaker's pink.
2. §7.1: the silhouette test compares 48x48 masks; floor 0.12 (closest pair measures 0.142).
3. §7.1: the expression enum is `PortraitArt.Expr` (Godot has a native `Expression` class).
4. §7.1/§3.3: "hurt" adds two `HARM` scratches (damage taken, paired with a crack shape); "flatlined" drops every colour to grey and adds a one-blip flat line; "triumphant" raises a fist that breaks the frame edge.
5. Critique 08: the dossier's Polaroid caption is the rank ("RANK 0", "R0" when compact); the class moved to a tag with a silhouette glyph; compact shows the class name without "//".
6. §4.1: Polaroid captions are handwriting at `label` stepping to `body`, then `caption` only if nothing else fits (handwriting "never under 16 px" can't hold on a 60 px compact Polaroid).
7. §12: dossier stats are `StatField`s (HP, CARDS, DAEMON StatIcons); `CrewCard.set_operative` reads the operative's deck and Daemons from `RunManager.campaign` (read only), so `hq_scene.gd` needn't change; the detail sentence stays as a fallback for callers that never name an operative.
8. §3.3: the FLATLINED dossier stamp is `HARM`; a posting stamp ("ON <SITE>") is ink; low-HP Polaroid glitch bars are `HARM` (were `CELL_PINK`).
9. §7.2: enemy portraits and holograms carry the corp pattern on the body; bosses also on a halo ring, since all five bosses share the crown.
10. §7.2/§8: `Hologram` uses W6's `crt_overlay` (scan 0.18, roll 0.12, flicker 0.02, roll period = `hologram_idle`), plus its own drifting scanlines and a 0.08 shimmer; all static under reduce effects.
11. §7.2: boss hologram dim `BOSS_DIM` = 0.5.
12. §4.3: text under 12 px was removed from the WIRE and MUGSHOT looks instead of enlarged (it didn't fit a 96 px portrait).
13. Corp-less enemies (`botnet_drone`, `seed_drone`, the two "Mirror" templates) get no brief of their own (README of the briefs says why).

## Couldn't do / known gaps
- The hologram isn't on screen in combat yet: W3 places `Hologram` above enemy wheels and behind the boss wheel. `combat_boss_p2` therefore shows only the new operative Polaroid.
- The runtime-lint contrast findings the baseline listed on `hq_loadout_*`, `hq_pause` and `hq_black_market` are dossier labels under an opaque modal or scrolled out of the page's clip: lint false positives, not re-captured here.
- The painted art itself (briefs only).
- W8d's FLATLINED screen isn't built; it uses `Polaroid.set_expression(PortraitArt.Expr.FLATLINED)`.

## Bible rules I'd question
- §4.1 "handwriting never under 16 px" can't hold for the compact dossier Polaroid (60 px wide); suggest "caption floor, 16 px where the frame allows".
