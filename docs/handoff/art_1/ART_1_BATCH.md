# Group 1 — ART-1 Foundations (M14 — Art direction v2)

Started 2026-10-05 in parallel with the tail of ART-0 (F kit behaviour, B3 names part 3), at the designer's
request. Every agent reads `process/agent_common_rules.txt` first (ART-0's rules re-targeted at ART-1).
Source of truth: `docs/ART_BIBLE.md` (v2) and `docs/art_reference/` (README maps each image to its lock).
Originals of every reference: `git show art-concepts-r43:docs/concepts/<path>`; the concept generator
scripts (Blender / PIL) are on the same tag under `docs/concepts/*/scripts/` and are the starting point
for shaders and assets (bible §6, plan §5.3).

**The goal is visual impact** (ruling 2: "the look and most of the feel of the art pass are present by the
end of M14, or we failed"). Each area captures its result windowed **next to its reference image** and
reads both. Accessibility, lint and budgets are guard rails, not the goal.

Cadence (DECISIONS 2026-10-05): fast checks per hand-back and merge; one full-suite run at the end of the
group; no audit until after ART-12; designer review after the group.

Carry-over from ART-0 (`docs/handoff/art_0/CARRY_OVER.md`) is folded in below and marked (CO).

## Wave 1 (now)

### 1A — Palette v2, typography, theme (bible §2.1–2.10, §6.4 theme, §5.6)
Owns: `scripts/ui/palette.gd` values, `scripts/ui/kit/ui_theme.gd` (type variations), `assets/fonts/**`,
`assets/fonts/README`, the theme tests. F (kit behaviour) is still porting focus brackets / PadGlyph /
modals / PaperInk into `scripts/ui/kit/`: don't edit those files; after F merges, `git merge main`.
1. Palette v2: brand/neutral/semantic tokens (§2.1–2.2), slice colours (§2.3), the five corp kits with
   round 18 values (§2.4; App. C #5), class accents round 22/38 (§2.5; App. C #4) (CO), Daemon trigger
   families (§2.6), rarity (§2.7), Heat colours for the five bands (§2.8 + DECISIONS "five Heat bands":
   PURGE gets its own token, HUNTED's look until art says otherwise), focus/state chrome colours (§2.10).
   - Accept: token table test (every §2 row has a token with the bible's value); contrast checks from
     E's `Palette.contrast` for text tokens on their panels; greyscale pairing rule (§5.1) noted per token.
2. Faces (§2.9): Anton (stickers, live numbers), Share Tech Mono (CRT), IBM Plex Sans Condensed
   (letterheads, body), Courier Prime (corp paper; copy from `docs/art_reference/fonts/` with its OFL),
   Permanent Marker only where §2.9 still allows it. README rows + licences.
   - **MSDF on** (`Palette.FONTS_MSDF`) (CO): retune the layouts it moves
     (`test_horizontal_pass21_screens` radio lines, `test_anim_r5_netrun` page split) and find and fix
     the signal-11 crash in `test_anim_r5_city` `test_your_nodes_never_ends_in_a_cut_row` seen with MSDF
     on. Accept: those three green with MSDF on; layout tests at 1.0/1.6/2.0 green.
3. Theme type variations (§6.4): `TerminalPanel`, `TerminalButton` (focus = F's brackets once merged),
   `HoloPanel`, `PaperPanel`, the live-number `LabelSettings` (Anton, 2 px outline #06060A, glow).
   Built in `UiTheme.build()`, high contrast (C's hook) still applied last.
   - Accept: a design-lab "type & chrome" sheet captured windowed vs
     `menus/round33_ui_chrome/typography.jpg` and `ui_kit.jpg`, both read; existing screens pick up
     palette v2 without layout breaks (fast tier + layout scripts at 2.0).

### 1B — The material kit (bible §1.2, §1.3, §6.3, §6.4; refs `foundations/round3_overlay/combined_v2/*`,
`foundations/round11_combat_target/*`, `hud/round22_combat_fx/send_it_sticker.jpg`)
Owns: new `shaders/kit/**`, new `scripts/ui/kit/materials/**` (one class per file), new
`tools/design_lab/kit_sheet.gd/.tscn`, their `ui_motion.tres` entries + REQUIRED_IDS + lab demos, tests.
Each material is a reusable component other groups apply; this group does not restyle screens.
1. **CRT terminal** panel shader + component (navy glass, cyan edge, 3 px scanlines @10 %, hex-dump 6 %,
   edge glow, type-on text, `>` caret; accent per use).
2. **Vinyl sticker**: die-cut white border, ink keyline, extrude, gloss 0.22 at rest with one slow sweep
   on one sticker at a time; **peel / slap / dissolve** motion; the "word over a system word" pattern
   (§1.3: SEND IT over `EXECUTE`). Runtime sticker for now (the per-locale baked atlas is ART-4/10).
3. **Grease pencil**: `Line2D` round caps, width 8–10, wax-grain texture + marker stroke shader, offset
   under-shadow, alpha 0.96, yellow `#FFE200` / red `#FF1C2C`, solid vs dashed, write-on and cloth-wipe
   by trimming points (never alpha), snapping helper to a given polyline.
   - **Lint rule** (D's runtime lint): no UI node's rect over a pencil stroke; and the layer order puts
     pencil above all UI (§6.4 layer order).
4. **Light spill**: additive spill sprite/shader for glowing elements onto surroundings (2D layer, plus
   the uniforms 1D needs for 3D).
5. **Decrypted holo** panel (§1.2: corp tint ~78 %, 4 px scanlines, slow bands, edge-only RGB split,
   scrim 0.88, cracked seal + DECRYPTED stamp slot) and **corp paper** panel (9-patch, Courier Prime
   fields, stamp slot).
6. **Binary bits** emitter: pooled `GPUParticles2D` with the 0/1 atlas (Share Tech Mono + outline),
   Bézier particle process shader routed around a wheel rim, `CPUParticles2D` fallback (≤ 44), arrival
   times precomputed for the view (never read back).
7. **Cel / toon + ink**: a 3-band toon ramp material and an ink-outline approach for 3D (coordinate with
   1D by message through the orchestrator's report; 1D owns the city, you own the shared material).
- Every material: `reduce_effects` reads E2's global, a VfxTier, a `ui_motion.tres` entry + lab demo for
  each motion, reduce effects = end state, headless never waits.
- Accept: `kit_sheet` captured windowed next to `round3_overlay/combined_v2/04_kit_sheet.jpg` and
  `05_lifecycle.jpg` (+ the round 11 pencil stills), both read and described in DECISIONS; tests for
  each component's states, the pencil lint rule, reduce effects end states.

### 1D — The unified-city render spike (bible §4.1, §6.1; plan §5.1–5.2; ruling 7 fidelity first)
Owns: new `tools/spike/city/**`, new `scripts/city3d/**` (prototype classes, one per file), their tests;
read-only use of `content/` layout data and `CityBakeCache`.
References: `city/round40_city_unified/three_views_v3.jpg`, `city/round39_city_unified/city_grid.jpg`,
`city/round40_city_unified/cars_lod.jpg`, `foundations/round2/r2_blend_EC_on_Cv2_day/city_day.jpg`,
`foundations/round6_city_restyle/views/*`, `city/round26_city_motion/*`. Generator scripts:
`art-concepts-r43:docs/concepts/round40_city_unified/scripts/` (and round 6 `city_export.gd`).
1. Build one real district (the game's own layout for one corporation, seeded) two ways:
   (a) real-time Godot 3D: Cv2 triangulated low-poly with tone jitter, 3-band toon, ink lines
   (inverted hull or post-process from depth/normal), light spill, haze, one orthographic `Camera3D`,
   MultiMesh building families, a traffic lane; (b) Blender-baked layered sprites with 2D motion.
2. **Fidelity first:** capture both windowed at the grid, raid and netrun zooms, next to the references;
   pick the one closest to the references. Then an **optimisation round** on the chosen one: frame time at
   1920×1080 on this PC and at the Deck tier (`city_quality`), draw calls, texture memory; budget plan §5.2
   (city ≤ 8 ms). The budget is a gate, not a reason to change the look.
3. Logic tested headless (projection, picking, LOD choice from config); render verified windowed only.
- Accept: `docs/handoff/art_1/city_spike_report.md` with the side-by-side captures (small crops,
  `.gdignore`d folder `docs/art_review/ART-1/`), the measured numbers, the recommendation and what ART-5
  needs; nothing in shipped screens changes yet.

## Wave 2 (after B3 merges)

### 1C — Glyph pipeline (bible §3.5, §5.2, §6.2; plan §5.3; refs `glyphs/*`, `wheel/round34_slice_names/*`)
Production atlas from `docs/art_reference/glyphs/` (58 PNGs + `index.txt`) into `assets/glyphs/`, renamed
to the program names (SHIM, OVERFLOW, DEFRAG, SANDBOX, DETOUR, HOTFIX, INFECT, TROJAN, NULL, PRIORITY,
WEIGHT, GROWTH, AIRMAIL …), placeholders excluded; MSDF/SDF 128 px cells, one CanvasItem shader (fill +
`#0C0A16` outline 0.075); an id → glyph table in content; a test that every slice type, status, pictogram,
hub, segment, Firmware, Daemon and Exploit has a glyph; the 16 px rule (§5.2) checked.

## File-ownership matrix
| Path | Owner |
|---|---|
| palette.gd, ui_theme.gd, assets/fonts/** | 1A |
| shaders/kit/**, scripts/ui/kit/materials/**, tools/design_lab/kit_sheet.* | 1B |
| tools/spike/city/**, scripts/city3d/**, docs/art_review/ART-1/ | 1D |
| assets/glyphs/**, glyph table content | 1C |
| scripts/ui/kit/* existing components | F (ART-0) until it merges; then smallest edits, reported |
| ui_motion.tres, REQUIRED_IDS, lab DEMOS, test_manifest.json, strings.csv, DECISIONS | everyone (union) |

## Group 1 acceptance
- [ ] 1A, 1B, 1D, 1C merged one at a time, each after checks_fast.sh green, pushed.
- [ ] Kit sheet capture vs `round3_overlay/combined_v2`, `ui_kit.jpg` and `typography.jpg`.
- [ ] Every shader has a `reduce_effects` (global) and a VfxTier.
- [ ] Lint rule: no UI node's rect over a pencil stroke.
- [ ] Render spike: fidelity-first choice, then optimised inside the budget; report with numbers.
- [ ] Timeline `18_art1` with a README row; before/after of the most visible screens.
- [ ] One full-suite run in isolation; designer review.
