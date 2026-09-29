# REBEL_CELL — Art Plan

**Status:** draft for approval (2026-09-28). **Owner:** art direction (orchestrator).
**Governing doc:** `docs/ART_BIBLE.md` v1.0. Every item below cites a bible section. This is a
**presentation-only** pass: no rules, content values, balance or save formats change.

Backlog sources: `docs/VISUAL_CRITIQUE.md` (review pack aa51ad2) and
`docs/VISUAL_IMPROVEMENT.md`. The critique was re-audited against the current code on
2026-09-28 (table in §6): of its 28 finding groups, 1 is fixed, 11 are partly fixed and 16 are open.

---

## 0. Branch model and preconditions

**Designer ruling (2026-09-28):** the whole art effort lives on its own long-lived branch,
**`art-pass`**, merged into `main` at a later date chosen by the designer.
- `art-pass` forks from `8ddfa86` (the last clean commit on `main`; ANIM-R5 combat merged).
  It is checked out in the worktree `.claude/worktrees/art-pass`.
- Each workstream branches from `art-pass` as `art/w<n>-<slug>` in its own worktree. After review, it merges back into `art-pass`, never into `main`.
- `main` is not touched by this effort. That includes the in-progress ANIM-R5 netrun merge on the main checkout.

| # | Item | Why | Who |
|---|---|---|---|
| P0.1 | `art-pass` must stay mergeable with `main`. Once `main` finishes its ANIM-R5 netrun merge (MERGE_HEAD `1c749d2`) and the ANIM-R5 city branch (`worktree-agent-abd00f2f43e698125`), sync `main` into `art-pass` **only when the designer asks**. Until then, the art work avoids depending on those branches. | Those branches touch files the art pass owns (`netrun_scene.gd`, `subtitle_strip.gd`, `hud_stats.gd`, `zine_panel.gd`, `neon_city.gd`, `city_bake_cache.gd`, `pause_menu.gd`, `ui_motion.tres`). Syncing before W7/W8 start keeps conflicts small. | Designer decides when; orchestrator merges. |
| P0.2 | Known overlap: the city branch fixes blank bakes and prebakes pages (its P1/P2), sizes the pause menu to fit (its P4) and keeps labels clear (its P8). W7 and W8b **must not rebuild these**. If the sync hasn't happened when they start, they leave those paths alone and note the gap. | Avoids duplicate work and merge conflicts. | Orchestrator, in the W7/W8 briefs. |
| P0.3 | Merge order relative to the MILESTONES "Queued passes" is decided at merge time (Q-A in §5). | CLAUDE.md: one milestone at a time. | Designer. |
| P0.4 | Full suite, schema smoke test and content validation green on `art-pass` at `8ddfa86` + docs. This is the **art baseline**. | Regression reference for W10 diffs. | Orchestrator. |

---

## 1. Baseline facts (inventory, 2026-09-28)

These facts drive the plan.

- **Palette:** no §3.3 semantic tokens exist yet (`HARM`, `GAIN`, `PROTECT`, `WARN`, `FOCUS`, `DISABLED`, `TEXT_*`, `SCRIM`). Meridian, Halcyon and Orbital are literals inside `corp_color()`, and Orbital is still #DDE3FF. There are 163 literal colour lines in `scripts/ui/**` (worst files: `ui_theme` 24, `neon_city` 23, `city_map_overlay` 23, `portrait_art` 16, `zine_card` 9). `wheel_view.gd:205` hard-codes HP green.
- **Type:** `UiTheme.BASE_SIZE 15` scales, but HotButton is a fixed 22. There are 3 literal size overrides and about 143 `draw_string` calls with per-file size constants, many under 12 (`HUB_FONT_SIZE 10`, `HUB_MIN_FONT_SIZE 8`, `BANNER_FONT_FLOOR 8`, `ICON_ROW_MIN_FONT 8`, `buy_button MIN_FONT 8`). No global 12 px lint exists. MSDF is **off** on all three fonts. IBM Plex is not in the repo.
- **Components:** there are two toast components (`toast.gd`, and `toast_note.gd` with 2 styles). There are no focus brackets (the theme uses a 2 px acid ring), no custom toggle, slider, stepper or picker (stock CheckButton, HSlider and OptionButton), and no secondary or danger button. `PadPrompts` prints letters.
- **Combat:** the combat wheel is `scripts/ui/wheel_view.gd` (3,023 lines); `kit/spinner_view.gd` is the loadout viewer. Neither has bezels, ownership, boss scaling or class hubs. The full-screen `Fx.flash` is still called for Perfect (`combat_scene.gd:1387`) and boss phase (`:1357`).
- **Shaders:** `city_lights`, `city_live`, `city_sketch`, `influence_reveal`, `crt_panel`, `distortion`, `jack_cover`, `scanline`, `zine_paper`, plus `glow` (unused). None has a `reduce_effects` uniform; scripts zero their strengths instead.
- **Settings:** `text_scale` is clamped to 0.8–1.6 (the bible requires 2.0). There are no colour-blind, high-contrast, reduce-motion, resolve-speed or glyph-set settings.
- **Capture:** there is **no review-pack harness** in the repo. `tools/playtest/storyboard.gd` covers 15 shots with `--scale`, `--pad` and `--scramble`, but has no greyscale or reduce-effects mode and misses about 60% of screens. Other tools: `motion_lab` + `frame_strip.py` for motion, and `run_windowed.py` for quiet windowed runs (worktree only).
- **VFX:** `UiMotionEntryData` has no `tier` field. `FlashLimiter` exists (3/s) but `Fx.flash` doesn't check reduce effects.
- **Art:** `PortraitArt` has 5 kinds and 5 operative tints, with no class silhouettes. `ZineCard` has no illustration window and no rarity stock, and truncates with "…". `assets/` holds only fonts and text, so the logo and graffiti are live text.

---

## 2. Workstreams

**Ownership rule:** a file has exactly one owner at a time (see the matrix in §3). A workstream that needs a change in another's file asks the orchestrator, who either sequences it or grants a named, one-off edit.

Every brief uses the template in `docs/ART_ORCHESTRATOR_PROMPT.md`, plus these standing lines:
- Presentation only. Never change rules, content values, save formats, or public APIs and signals (wrap and extend them).
- CLAUDE.md rules apply: static typing, no magic numbers (tokens and `.tres`), and every rule gets a test.
- Windowed runs go only through `python tools/run_windowed.py` from the agent's worktree. Never pipe Godot output, and never `taskkill` by image name.
- Run `godot --headless --path . --import` after adding any `class_name`.
- Done means: the full suite (`python tools/run_tests.py -j 4`), the schema smoke test and content validation are green; the ART_BIBLE §14 checklist passes for every touched screen; and captures are in `docs/timeline/<ws>/`.
- One commit per acceptance item, with the item in the message, on the workstream's own branch `art/w<n>-<slug>` (forked from `art-pass`). Only the orchestrator merges into `art-pass`. Nothing goes to `main`, and never force-push.

### W1 — Foundation: tokens, type, spacing
- **Bible:** §3 (all), §4, §5.1, §15 (the STYLE_GUIDE pointer).
- **Owns:** `scripts/ui/kit/palette.gd`, `scripts/ui/kit/ui_theme.gd`, `assets/fonts/**` (+ `.import`), and the STYLE_GUIDE §2/§3 text.
- **Scope:**
  1. Add the §3.3 semantic tokens, and constants for all five corps (§3.6). Orbital becomes #7FA8FF.
  2. Add corp pattern ids (enum + painter hooks) for the helix-dot, container-stripe, civic-ring, star-dot and scan-glitch patterns. Painters live here as `CorpPattern` (new kit file owned by W1).
  3. `hp_color(frac)` and `heat_color(band)` helpers (§3.5).
  4. Type scale constants `caption`–`hero` plus `UiTheme.font_px(step)` = `roundi(step * text_scale)`. HotButton becomes scaled. Add spacing tokens (§5.1).
  5. MSDF on for all faces (§4.1, §13).
  6. The Plex body face and a `BodyText` theme type, **only if Q3 is approved**.
  7. A contrast helper `Palette.contrast(a, b)` for W10's lint.
  8. Update STYLE_GUIDE §2/§3/§5 to point at the bible (§15).
- **Doesn't:** migrate call sites in views. W1 adds tokens and APIs; each owning workstream migrates its own files.
- **Closes:** part of critique #23 (Orbital hue, patterns), and supplies the APIs for #4 (HP scale) and #15 (type scale).
- **Tests:** the token values, `font_px` scaling at 0.8/1.0/1.6/2.0, and no scaled size under 12 at 1.0.

### W10 — Visual QA automation (the gate)
- **Bible:** §13 "Automated visual checks", §14.
- **Owns:** `tools/visual_qa/**` (new), `tools/playtest/storyboard.gd`, `tests/unit/test_visual_lint*.gd` (new), and `docs/timeline/qa/**`.
- **Scope:**
  1. Extend the storyboard into a **review-pack harness** covering every screen in §11 (title, slots, new campaign, HQ + Black Market + crew + loadout DECK/SPINNER, pause, Grid, raid setup/playout/interlude, route, combat states incl. boss phases, loot, Modem, event, codex, options, stats, FLATLINED, campaign WON/LOST).
  2. Axes: text scale 1.0/1.6/2.0 × mouse/pad × reduce effects on/off, plus greyscale and deutan post filters (a screen-space shader in the harness only), plus scramble.
  3. Output a contact sheet per run, and a pixel diff against the previous build.
  4. **Lint** (a headless GUT test over instantiated screens), which flags:
     - Label, Button or RichTextLabel font size not from UiTheme;
     - effective px < 12 at 1.0;
     - overlapping visible text Controls;
     - clipped text (visible lines < lines, or `…` present);
     - contrast < 4.5:1 against the panel token.
     - Also a static grep lint for literal `Color(`/hex and literal font sizes in `scripts/ui/**`, with a shrinking allowlist (a baseline count that may only go down).
- **Runs:** first against the art baseline (P0.4), which gives the "before" stills. After that, on every workstream branch before review.
- **Review folders:** each workstream writes its before/after stills, strips, contact sheets and a `README.md` (changes, the §14 checklist, decisions, gaps) to `docs/art_review/W<n>/` (designer ruling 2026-09-28).
- **Closes:** the §13 harness and the lint (VISUAL_IMPROVEMENT §11 capture and lint).

### W2 — Component library
- **Bible:** §6 (the states table), §6.4–§6.8, §10 budgets for T1.
- **Owns:** new kit files `focus_brackets.gd`, `zine_toggle.gd`, `zine_slider.gd`, `stepper.gd`, `tile_picker.gd`, `glass_button.gd` (primary/secondary/tertiary/danger), `toast.gd` (the unified one), `ui_tip.gd`, `focus_tip.gd`, `zine_stamp.gd`, `confirm_dialog.gd`, `pad_prompts.gd`, plus the pad glyph painter `pad_glyph.gd` (new).
- **Scope:**
  1. All six states for every component (§6).
  2. `FocusBrackets`: 4 corners, 2 px, 4 px offset, 1.03 scale; replaces the acid ring theme-wide via UiTheme hooks from W1.
  3. The unified sticky toast (§6.7). `toast_note.gd` becomes a thin wrapper that forwards to it; the public API is kept.
  4. The tooltip width 26–36 columns and input-aware wording helper (§6.8).
  5. Stamp hold time 0.6 s + 0.05 s/char (§6.6) and a per-region banner queue.
  6. Drawn face-button glyphs (Xbox/PS/Switch/Deck, all procedural; no third-party glyph art) (§12).
  7. A `DISABLED` treatment with a lock or reason.
- **Doesn't:** replace call sites in screens (W8 does). It ships each component with a lab page in `tools/design_lab/components_lab.tscn` (new, owned by W2).
- **Closes:** critique #11 (one toast), #22 (glyphs, focus), part of #8 (disabled style) and part of #16 (the widgets exist).

### W4 — Cards
- **Bible:** §6.3, §7.3, §2 (PAPER).
- **Owns:** `zine_card.gd`, `deck_view.gd`, `inspect_popup.gd` (card detail), `drag_ghost.gd`, `shaders/foil.gdshader` (new, built with W6's uniform convention), `scripts/ui/kit/card_art.gd` (new procedural illustration stand-in), and `docs/art_briefs/cards/**`.
- **Scope:**
  1. The frame: cost gem, Anton title, a 60% illustration window, the effect band and body rules text.
  2. Rarity by stock (photocopy, glossy, foil).
  3. No "…" at any scale (the card grows, or text steps down once).
  4. The detail view shows the art and never repeats the face.
  5. A procedural 2-colour halftone stand-in per card, deterministic from the card id and effect type, wired so `CardData.illustration` swaps in final art.
  6. **One art brief per card.** The scale (unique vs ~30 bases) waits on **Q1**; until then, briefs are written per effect family.
- **Hand-off to W3:** hover lift and scale, and preview persistence through the drag, live in `combat_scene.gd` (W3). W4 supplies the card-side API.
- **Closes:** critique #25, part of #19 (deck truncation), and screens `54`/`55`.

### W5 — Characters
- **Bible:** §7.1, §7.2.
- **Owns:** `portrait_art.gd`, `polaroid.gd`, `crew_card.gd` (dossier stripe), and `docs/art_briefs/characters/**`.
- **Scope:**
  1. Eight class silhouettes and props as procedural head-and-shoulders painters (§7.1 table), with a class accent token per class added through W1.
  2. Four expressions (neutral, hurt, triumphant, flatlined) as procedural variants.
  3. Enemy busts and holograms in corp hue and pattern, and a boss hologram painter at 40% screen height (§7.2).
  4. A painted-final art brief per class, enemy family and boss.
  5. The Polaroid caption shouldn't repeat the name.
- **Blocked on:** **Q2** (class accents). The silhouette work can start on the proposals behind one token table, so a ruling only changes values.
- **Closes:** critique `08/14/15`, the portrait half of `69–76`, and the boss presence part of #6.

### W6 — VFX and shader library
- **Bible:** §8, §13 (shader library), §12 (reduce effects).
- **Owns:** `shaders/**` (except the foil file W4 creates), `scripts/autoload/fx.gd`, `scripts/ui/fx/**` (incl. `flash_limiter.gd`), `combat_fx_layer.gd`, `raid_fx_layer.gd`, `scripts/data/ui_motion_entry_data.gd` (**schema change: add `tier`**; logged, smoke test updated), and the `tier` values in `content/config/ui_motion.tres`.
- **Scope:**
  1. Shader library conventions: a shared include, a `reduce_effects` uniform on each.
  2. New shaders: `glass_blur`, `paper_burn`, `glitch_dissolve`, `marker_stroke`, `halftone`, and `crt_overlay` (refactored from `crt_panel`/`scanline`).
  3. The tier field on every motion entry, and an FX layer that enforces coverage, alpha and duration per tier.
  4. `Fx.flash` refuses full-screen below T4 and honours reduce effects.
  5. Replace the Perfect and phase flashes with wheel-local T3 effects. W6 supplies `CombatFx.wheel_burst(wheel, kind)`; W3 changes the two call sites.
  6. Per-slice hit VFX shapes (crit shatter, attack slash, shield hex, evade smear, afflict glitch, heal plus-signs, miss static).
  7. Delete the unused `glow.gdshader` only if nothing references it (verify first).
- **Closes:** critique #1 (flashes, with W3), VFX parts of `gifs/02`, `gifs/25` and `gifs/16`, and VISUAL_IMPROVEMENT §7.

### W3 — Wheels and combat presentation
- **Bible:** §6.1, §6.2, §3.5, §8, §10 (resolve budget), §11 Combat.
- **Owns:** `scripts/ui/wheel_view.gd`, `kit/spinner_view.gd`, `kit/spinner_mini.gd`, `resolve_beats.gd`, `forecast_stamp.gd`, `forecast_ticks.gd`, `outcome_row.gd`, `ram_bar.gd`, `heat_poster.gd` (combat use), and `scripts/ui/combat_scene.gd`.
- **Scope:**
  1. Bezel ownership: the operative's stickered bezel with a pink rim and Polaroid inset; the enemy's corp-hue machined bezel with its pattern and a notched edge.
  2. Class bezel ornaments and hub patterns and glyphs (§7.1).
  3. The HP arc at ≥10 px on the §3.5 scale, with a ghost segment, a two-stage drain and a heartbeat below 25%.
  4. The boss at 120% with a nameplate and phase pips; HP moves outside the needle sweep.
  5. A single-stamp hub queue.
  6. Forecast split: this wheel's own chips, plus a net line under the operative's HP; the "YOU TAKE" chip leaves the operative's tag. One chip row with "+N MORE"; tags stay at radius + 66.
  7. Net damage numbers anchored above the hub, with overkill shown as capped.
  8. The card preview persists through the mouse drag, and the aim line starts at the card centre.
  9. A resolve speed setting (1×/2×/instant) with hold to fast-forward, and respin overshoot. The setting's storage goes through W9's settings slice; see the sequencing note.
  10. Switch the two flash call sites to W6's API.
  11. NEXT plate wording, and the LAST TURN row at `caption` or larger.
  12. Migrate these files to W1 tokens and type.
- **Closes:** critique #1 (call sites), #2, #3, #4, #5, #6, #7, #27, `1.6/10–12` (wheels stay ≥70%), and the combat part of #15.

### W7 — City
- **Bible:** §9 (all), §2 (CITY), §10.6.
- **Owns:** `neon_city.gd`, `city_bake_cache.gd`, `city_layout.gd`, `city_influence.gd`, `influence_spread.gd`, `wireframe_background.gd`, `cyberdeck_background.gd`, and the city shaders (`city_*`, `influence_reveal`). W6 has already landed the library conventions by then.
- **Scope:**
  1. Lighting: per-ink glow, haze bands, wet-street reflections, rim light.
  2. Per-context LUT grade.
  3. T0 life: aircraft, drones, billboards in corp hue and pattern, window toggles.
  4. Heat reactivity per §9.3.
  5. Territory as spray tags and a `CELL_TURF` hatch, with light leaking into the haze (replacing the khaki).
  6. A campaign-progress grade.
  7. Map dim 40% + blur (§9.5).
  8. Silhouette pre-render, then a fade to the bake. Never flat blocks (§9.4).
  9. All of it stops under reduce effects.
- **Depends on:** P0.2 (the city branch prebakes).
- **Closes:** critique #14, #23 (the city side of the corp hues), the Heat-on-map note in `19/20`, `gifs/16` khaki, and VISUAL_IMPROVEMENT §2.

### W8 — Screens (four sub-waves)
- **Bible:** §5.2–§5.4, §11 blueprints, §10 (rules 4–6).
- **Owns (per wave):**
  - **8a:** `title_scene.gd`, `settings_panel.gd`, `codex.gd`, `pause_menu.gd`, stats page.
  - **8b:** `hq_scene.gd`, `grid_map_view.gd`, `city_map_overlay.gd`, `map_legend.gd`, `route_legend.gd`, `netrun_map_view.gd`, `raid_playout_panel.gd`, `raid_verdict.gd`, `loadout_view.gd`, `hud_bar.gd`, `hud_stats.gd`, `subtitle_strip.gd`, `page_transition.gd`.
  - **8c:** `netrun_scene.gd` (loot, Modem, events, interlude), `buy_button.gd`, `modem_sign.gd`, `daemon_*`.
  - **8d:** the run-end and campaign-end views.
- **Baked vector art (SVG, authored by the agent):** the logo, the MODEM / CYBER SHOP sign, NEVER SLEEP / TRUST NO ONE, sticker badges and landmark glyphs. They live in `assets/art/**` (new), with translated subtitles where §4.3.5 requires them.
- **Wave scope:**
  - **8a:** Title (§11), case-file slots with a danger Delete, Options (tabs, toggles beside labels, slider value, live preview), Codex zine spread, Stats badges, pause sized to content with a copy-code button, and the modal/page slide rules (§10).
  - **8b:** HQ with a DECK frame (**Q4**), 3-column crew, grouped Black Market with locks, the fixed-width loadout modal with the rank-3 ring swap visibly filled, Grid one-primary and chips in rows, raid LIVE/RESULT and disabled Continue, 28 px asset markers, route "you are here" on a node, legends that never jump, and a fixed site card height.
  - **8c:** Loot modal at 70% width, Modem slot tiles, microchips at `body` and a single Cycles readout, events sized to text with the speaker once and no subtitle repeat, and native dropdowns replaced by W2 pickers and steppers.
  - **8d:** FLATLINED (T4), and distinct WON and LOST templates.
- **Closes:** critique #8–#10, #13, #16–#21, #24, #26, #28, the screen part of #15, and "embarrass in a trailer" items 2 and 5–6.

### W9 — Accessibility and pad
- **Bible:** §12, §5.4, §3.7.
- **Owns:** `scripts/autoload/settings.gd` (new settings only; **save-format additive**, with defaults for old files, so this counts as a settings-file addition, not a save change), `ui_focus.gd`, `jack_input_gate.gd`, the colour-blind remap table (new, in `content/config/`), and high-contrast theme variants in UiTheme (a named, one-off W1 file grant).
- **Scope:**
  1. `text_scale` range 0.8 → **2.0**, with layouts verified at 2.0 through W10.
  2. Deutan, protan and tritan remaps of corp and semantic hues.
  3. High contrast (opaque panels, 7:1).
  4. Reduce motion (separate from reduce effects).
  5. Resolve speed storage, which W3 consumes.
  6. The glyph-set switch, which W2 draws.
  7. Steam Deck default 1.2.
  8. Input-aware wording audit: "click" and "drag" under pad (`netrun_scene.gd:3043` etc., coordinated with the W8 owner).
- **Timing:** the settings slice lands early, right after W1, because W2 and W3 consume it. The final sweep runs after W8.
- **Closes:** critique #22 (wording), `1.6` section items, and §5 "what breaks" (with W8).

---

## 3. File ownership matrix (conflict hot spots)

| File | Owner | Others need | Resolution |
|---|---|---|---|
| `palette.gd`, `ui_theme.gd` | W1 | W2, W9 (high contrast) | W1 lands first. Later edits go through one-off grants, merged by the orchestrator in order. |
| `combat_scene.gd` | W3 | W6 (flash calls), W4 (drag preview), W9 (wording) | W3 makes all edits using the others' APIs. |
| `netrun_scene.gd`, `hq_scene.gd` | W8 (per wave) | W9 wording, W2 pickers | W8 applies them. |
| `ui_motion.tres` / `ui_motion_data.gd` | W6 (tier) | Everyone adds entries | Append-only. W6's schema change lands before W3 and W7. |
| `assets/text/strings.csv` | Any (append) | Everyone | Append-only rows. The orchestrator resolves merge order. |
| `tests/test_manifest.json` | Any (append) | Everyone | Same. |
| `docs/DECISIONS.md` | Orchestrator | Everyone | Agents write their entries in their report. The orchestrator appends them under "Art pass – W<n>". |

---

## 4. Schedule (at most 4 agents at once)

| Wave | Runs in parallel | Gate to next wave |
|---|---|---|
| 0 | P0.4 (orchestrator) | Green `art-pass` = art baseline |
| 1 | **W1**, **W10** | W1 merged; W10 baseline pack captured ("before") |
| 2 | **W2**, **W4**, **W6**, **W9-settings** | Each reviewed against §14 with W10 captures, then merged in order W6 → W2 → W9s → W4 |
| 3 | **W3**, **W5**, **W7** | W3 needs W2 + W6; W7 needs W6; W5 needs Q2 (or runs on proposals) |
| 4 | **W8a**, **W8b** (then **W8c**, **W8d**) | 8b needs W7; 8c needs W3/W4; 8d needs W5 and W7 |
| 5 | **W9 final sweep**, W10 full-matrix run | Everything passes at 1.0/1.6/2.0, mouse and pad, RE on/off and greyscale |

**Review per result:**
1. The W10 pack at 1.0 and 1.6, mouse and pad, plus greyscale, compared before and after.
2. The §14 checklist.
3. Any improvisation beyond the bible goes back with the cited rule.
4. Merge. Re-run the full suite and harness.
5. Record in DECISIONS, update this plan's progress, and add strips under `docs/timeline/`.
6. Report to you with before/after stills at each wave gate.

---

## 5. Questions and rulings (all answered 2026-09-28; see DECISIONS "Art pass (branch `art-pass`)")

| Id | Question | Blocks | Proposal |
|---|---|---|---|
| **Q-A** | When `art-pass` merges into `main`, where does it sit relative to the MILESTONES "Queued passes"? (Decided at merge time.) | Merge only | Log it as "M13 Art pass" at merge. It also covers M12's open Skins box ("deferred to art integration (M13)"). |
| **Q-B** | ~~Who resolves the in-progress `main` merge?~~ **Answered 2026-09-28:** the art pass works on its own `art-pass` branch and leaves `main` alone (§0). | — | — |
| **Q1** (§16.1) | Card illustration budget: unique per card, or ~30 tinted bases? | W4 brief scale | Start on the ~30 bases plus unique rares and class cards (briefs per effect family); upgrade later. **Ruled: agreed.** |
| **Q2** (§16.2) | Confirm the class accents in §7.1. | W5 final values, W3 bezels | Accept the §7.1 proposals for the procedural stand-ins. The painter can revise them via tokens. **Ruled: agreed.** |
| **Q3** (§16.3) | Body face: IBM Plex Sans Condensed (OFL)? This is also a **licence decision**, so it needs your OK. | W1 item 6, W8 Codex/events | Yes, Plex (OFL, same licence family as the current fonts). **Ruled: agreed.** |
| **Q4** (§16.4) | HQ: full DECK frame, or keep the window-over-city composition? | W8b HQ | The full DECK frame, per §11 HQ's focal order. **Ruled: agreed.** |
| **Q5** (new) | Text scale ceiling is 1.6 in `Settings`, but the bible says 2.0. OK to raise the setting's range (an additive settings change)? | W9 | Yes. **Ruled: agreed.** |
| **Q6** (new) | May agents author SVG vector art (logo, signs, badges) themselves, and may I generate *concept* images for the painted-art briefs if an image tool is available? (Nothing generated ships without your approval.) | W8, W4/W5 briefs | SVG yes. No image tool is connected in this session, so the briefs are text only. **Ruled:** SVG yes; concept images as script-drawn pixel art/vector under `docs/art_review/<W>/concepts/`, never shipped without approval. |

---

## 6. Coverage checklists

### 6.1 ART_BIBLE sections → workstreams

| § | Topic | Workstream(s) |
|---|---|---|
| 1 | North star | All (review lens) |
| 2 | Four materials | W8 (screens), W2 (components never mix), W4 (PAPER cards), W7 (CITY) |
| 3.1–3.4 | Colour principles, tokens, slice colours | W1; call-site migration by each owner |
| 3.5 | HP and Heat scales | W1 helpers; W3 (arc); W8b/W3 (Heat poster) |
| 3.6 | Corps: hue + pattern + landmark | W1 (tokens, patterns); W7 (districts); W3 (enemy bezel); W8b (map routes) |
| 3.7 | Contrast | W10 lint; W8/W9 fixes |
| 4 | Typography | W1 (scale, MSDF, Plex); W10 lint; owners migrate |
| 5.1 | Grid and spacing | W1 tokens; W8 layout |
| 5.2–5.4 | Page structure, panels, resolution | W8; W9 (Deck default, safe areas) |
| 6 (states) | Six component states | W2 |
| 6.1 | Wheels | W3 (+ W5 portraits) |
| 6.2 | Forecast tags | W3 |
| 6.3 | Cards | W4 (+ W3 for drag in combat) |
| 6.4–6.8 | Buttons, inputs, stamps, toasts, tooltips | W2; W8 adopts |
| 6.9 | Top bar tags | W8b (`hud_bar`, `hud_stats`) |
| 6.10 | Map elements | W8b (+ W7 dim) |
| 7.1–7.2 | Operatives, enemies, bosses | W5 (+ W3 bezels) |
| 7.3 | Card illustrations | W4 |
| 7.4 | Icons (redraw ☠ ⚡ ⌗ ✺ as StatIcons) | W2 (`stat_icon.gd` one-off grant) |
| 8 | VFX tiers | W6 (+ W3 call sites) |
| 9 | City | W7 |
| 10 | Motion principles and budgets | W6 (tier), W8 (page/modal rules), W3 (resolve speed) |
| 11 | Screen blueprints | W8a–d, W3 (combat) |
| 12 | Accessibility | W9 (+ W2 glyphs, W10 checks) |
| 13 | Technical art | W6 (shaders), W1 (MSDF), W10 (checks); canvas layer order: W8 |
| 14 | Definition of done | Orchestrator review, with W10 |
| 15 | Changes from STYLE_GUIDE | W1 edits STYLE_GUIDE pointers |
| 16 | Open questions | §5 above |

### 6.2 Critique findings → workstreams (status as audited 2026-09-28)

| # | Finding (VISUAL_CRITIQUE ref) | Status now | Workstream |
|---|---|---|---|
| 1 | Full-screen Perfect / P3 flashes (`gifs/02`, `gifs/25`) | Open | W6 + W3 |
| 2 | Preview lost on mouse drag; hover lift (`31`, strip 04) | Open | W3 (+ W4 API) |
| 3 | Net numbers, "42⁶42", overkill (`37`, `38`, `47`) | Partial | W3 |
| 4 | HP colour scale, ghost, top-bar mismatch (`47`, `49`, `50`) | Partial | W3 (+ W1 helper) |
| 5 | Forecast split: "YOU TAKE" on own tag (`35`) | Open | W3 |
| 6 | Boss framing, stacked hub stamps, needle over HP (`43–46`) | Partial | W3 + W5 |
| 7 | Ownership bezels; class identity pairs (`69–76`) | Open | W3 + W5 |
| 8 | Raid LIVE/RESULT, disabled Continue, end camera, numbers on labels (`22–26`) | Partial | W8b (+ W2 disabled) |
| 9 | Legend jump, site card height, shred reflow, event bar (`gifs/07`, `14`, `20`, `24`) | Open | W8b / W8c |
| 10 | Loot fly to CARDS, LOOT overlap, modal size (`48`, `61`, `gifs/23`) | Partial | W8c |
| 11 | One toast style (`gifs/08`, `13`) | Open | W2 |
| 12 | Typing speed / skip (`gifs/24`) | Fixed | — (verify in W10) |
| 13 | One slide direction; modal animation; modal before page (`gifs/21`, `22`) | Open | W8a (`page_transition`, menu motion) |
| 14 | Placeholder flat city (`gifs/18`, `23`) | Partial | P0.2 + W7 |
| 15 | < 12 px text; fixed labels at 1.6 (`1.6/01`, `14`) | Open | W1 + W10 lint + each owner |
| 16 | Native dropdowns (`03`, `28`, `52`, `gifs/09`) | Open | W2 widgets → W8 |
| 17 | Slots as cards; Delete glyph (`02`) | Open | W8a |
| 18 | Pause sized; raw code → copy (`10`, `40`) | Partial | P0.2 + W8a |
| 19 | Loadout width, "Accelera/tor", ring swap (`11–13`, `57–58`, `gifs/10`) | Open | W8b (+ W4 deck cards) |
| 20 | Codex, Options toggles/slider, Stats badges (`16–18`) | Open | W8a |
| 21 | FLATLINED staging; WON vs LOST (`51`, `62`, `63`) | Partial | W8d (+ W5, W7) |
| 22 | Prompt bar everywhere, glyphs, focus, pad wording (`1.6/*`) | Open | W2 + W9 + W8 |
| 23 | Corp hues/patterns; Heat never green (`21`, `64–68`) | Partial | W1 + W7 + W3/W8b (Heat poster) |
| 24 | Black Market grouping, icons, contrast (`06`, `09`, `scr/05`) | Open | W8b |
| 25 | Card illustrations / rarity stock (`54`) | Open | W4 |
| 26 | Baked logo and signature graffiti (`scr/*`) | Open | W8 (SVG) |
| 27 | Resolve speed; respin overshoot (`gifs/01`, `03`) | Open | W3 + W9 |
| 28 | Grid one primary; chips in rows; label overlap; you-are-here on node (`19`, `20`, `27`) | Partial | W8b |

Also tracked (from the audit and DECISIONS open questions):
- the Heat banner's 8 px floor (`heat_poster.gd:86`), W3/W8b;
- a toast over a bottom control for 3.5 s (DECISIONS:4130), W2;
- the densest Grid cluster touching at 1.6 (DECISIONS:4122), W8b;
- page city latency of 2–6.5 s, P0.2 then W7;
- Modem microchips at about 7 px, W8c;
- Dossier stats as sentences (`scr`), W8b.

VISUAL_IMPROVEMENT items that the bible does **not** adopt, and that this plan therefore doesn't schedule:
- a replacement mono face (the bible keeps Share Tech Mono);
- parallax, the day/night drift and the continuous camera beyond §10.6 (W7/W8 do §10.6 only);
- photo mode, key art and the trailer (marketing, §12 of that doc);
- audio sync (not an art bible topic).

They are listed here so none is silently lost. Raise them as a later pass if you want them.

---

## 7. Progress

| Wave | Workstream | Branch | State |
|---|---|---|---|
| 0 | Branch + baseline | `art-pass` | done: the baseline is green (1094 tests) at 8ddfa86 + docs |
| 1 | W1, W10 | `art/w1-foundation`, `art/w10-visual-qa` | **merged** into art-pass (1146 tests green); review folders W1/ and W10/ |
| 2 | W2, W4, W6, W9s | — | **all merged** |
| 3 | W3, W5, W7 | — | **all merged** (1290 tests green) |
| 4 | W8a–d | `art/w8d-campaign-end` | W8a, W8b, W8c and WF **merged** (1379 tests green); W8d running |
| 5 | W9 sweep, W10 full | `art/w9f-sweep` | W9F (final accessibility sweep + all handed-off items) running; W10 full-matrix run after W8d and W9F merge |
