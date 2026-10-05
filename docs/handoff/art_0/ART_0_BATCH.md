# ART-0 — Rulings, docs landing, names, salvage (M14 — Art direction v2)

Plan: `docs/ART_REINTEGRATION_PLAN.md` §1–§3 (on tag `art-concepts-r43`; landed on main by area A).
Rulings: DECISIONS "2026-10-05 — Designer rulings: art reintegration, pause point 0" (applied; GDD
3.3 / 4.2 / 6.3 / 7.x / 8.4b already updated). Every agent reads `process/agent_common_rules.txt` first.

Sources: tag `art-concepts-r43` = `9a62cec` (concepts, ART_BIBLE v2, plan); tag `art-m13-final` =
`f80f393` (M13 code, ART_BIBLE v1). Read-only checkout: `.claude/worktrees/art-pass`.

ART-0 is the baseline before the new look: no restyling here. Every later batch (ART-1…12) cites
ART_BIBLE v2 sections and `docs/art_reference/` images, which area A lands.

## Wave 1 (parallel)

### A — Docs landing (ART-0a). Docs only; no code, no tests change.
Owns: `docs/art_reference/**` (new), `docs/art_history/**` (new), `docs/ART_BIBLE.md`, `docs/ART_BIBLE_v1.md`,
`docs/ART_REINTEGRATION_PLAN.md`, `docs/ART_REINTEGRATION_PROMPT.md`, `docs/concepts/DIRECTION_REVIEW.md`,
`docs/concepts/GDD_ART_COVERAGE.md` (+ `docs/concepts/.gdignore`), `docs/GDD.md` §9 only, `docs/MILESTONES.md`,
`docs/STYLE_GUIDE.md` (pointer lines only), DECISIONS (append).
1. `git checkout art-concepts-r43 -- docs/ART_BIBLE.md docs/ART_BIBLE_v1.md docs/ART_REINTEGRATION_PLAN.md
   docs/ART_REINTEGRATION_PROMPT.md docs/concepts/DIRECTION_REVIEW.md docs/concepts/GDD_ART_COVERAGE.md
   docs/concepts/.gdignore`. Add a banner to the plan: "Rulings applied: DECISIONS 2026-10-05 pause point 0" and
   strike/annotate the §1 items those rulings changed (1, 5, 6.2, 6.5, 6.6, 7, 9, Appendix C 12) — do not rewrite
   history, annotate.
   - Accept: the files are on main; `git diff art-concepts-r43 -- <those files>` shows only the banner/annotations.
2. **Curated `docs/art_reference/`** (ruling 3), target 30–60 MB, hard cap 80 MB. For every element ART_BIBLE v2
   Appendix A names a latest locked image for, copy that image (and the motion GIF where the lock is a motion) into
   `docs/art_reference/<area>/` (areas: foundations, wheel, cards_fx, hud, city, raid, netrun, hq, shop_events,
   portraits, menus, campaign_end, glyphs, fonts). Include `round17_slice_system/glyphs/` (59 PNGs + `index.txt`) and
   the Courier Prime fonts with their OFL. Exclude `__pycache__`, `*.pyc`, scripts, rejected and superseded
   variants, the EVOLUTION video/PDF. Large PNGs above 2 MB: keep the original only if Appendix A names it as the
   final; otherwise a downscaled 1600-px-wide copy is fine (say which in the README).
   - `docs/art_reference/README.md`: one row per image: file, the DIRECTION_REVIEW round + lock it shows, the
     ART_BIBLE v2 section, the original path `art-concepts-r43:<path>`, and the ART-n batch that implements it.
   - `docs/art_reference/.gdignore`.
   - Accept: `du -sh docs/art_reference` ≤ 80 MB; every Appendix A row resolves to a README row (or is listed in the
     README "not copied, why" table); a script in your scratchpad confirms each README path exists.
3. `docs/art_history/ART_PLAN_M13.md` = art-pass `docs/ART_PLAN.md` with a superseded banner (M13, ART_BIBLE v1.0,
   superseded in part by the concept direction; ported in part per the reintegration plan). Bring art-pass's M13
   DECISIONS entries (the "Art pass …" / W1–W10 / WF / W9F entries) over **verbatim** into main's DECISIONS under
   one heading "M13 art pass (art-pass branch, superseded in part)", placed after main's newest entries.
   - Accept: every M13 DECISIONS heading on art-pass appears once on main.
   - Careful: `tests/unit/test_horizontal_pass24_city.gd` reads DECISIONS and fails if it contains
     "GRID_FITS_MAX (<n-1>)" for main's `hq_scene.gd` GRID_FITS_MAX. If a verbatim M13 entry carries another
     number, annotate it (e.g. "GRID_FITS_MAX on art-pass was …") rather than breaking the test, and say so.
     Run the full suite: DECISIONS is read by tests.
4. **GDD §9 rewrite** (ruling 4) around ART_BIBLE v2: 9.1 visual baseline (cel-shaded low-poly city with ink lines,
   CRT screens with white glyphs, vinyl stickers for everything that never changes, grease pencil for plans
   (yellow routes / red threats), light spill), citing DECISIONS 2026-10-05 ruling 4; 9.2 combat readability
   (sticker and pencil layer rules, "no UI ever covers grease pencil", status overlay = the status with corner badge
   only for ×N / multiplier tags per ruling 10); 9.3 raids & grid (DOWN = white bolt over a greyed marker at every
   zoom, ruling 11); 9.4 Heat feedback ("the city reacts"; screen glitch only as an off-by-default Options extra).
   Keep 9.5 / 9.6 except where v2 contradicts them. Update GDD "Changes since" and the "Locked design decisions"
   line "Visual baseline: three worlds" in DECISIONS → mark superseded, pointing at the ruling (never delete).
   - Accept: no GDD line still describes wireframe / zine / spray as the baseline; every changed paragraph cites
     the ruling.
5. **MILESTONES**: add an "M13 — Art pass v1 (art-pass branch, superseded in part)" box (summary + tags) and
   "M14 — Art direction v2" listing ART-0…ART-12 with their acceptance lines from plan §4.2 as unticked boxes,
   adjusted for the rulings: ART-1 render spike = fidelity first then an optimisation round (ruling 7); ART-6 DOWN
   uses the white bolt (ruling 11); after ART-12: "R7 re-evaluation" (ANIM-R7 findings re-checked against the
   ported screens, then fixed), "G1–G16 re-evaluation with the designer", "Horizontal list re-evaluation", then
   H25+ and the Queued passes. M14 acceptance headline: "the look and most of the feel of the art pass are present
   (ruling 2)". Tick ART-0 lines only as the orchestrator merges them (leave unticked).
6. STYLE_GUIDE: a short pointer at the top: ART_BIBLE v2 is the visual source of truth from M14; §5 (motion rulings)
   stays binding.
DECISIONS entry "Art direction — ART-0 docs landing" (what was copied, sizes, what was left on the tag and why).

### B — Names pass, part 1, and the saves folder (ART-0n + S0)
Owns: content ids/strings/file names for the renamed things, `assets/text/strings.csv` (re-export),
`scripts/core/**` and `scripts/state/**` renames, `scripts/autoload/save_service.gd`, `.gitignore`, the tests that
name the old words. Other agents' files: smallest rename-only edits (say which).
Order per rename (CLAUDE.md): DECISIONS (already logged) → GDD (done for 3.3/4.2/6.3/7.x/8.4b; finish any line still
using the old word) → content and strings → code → tests. Internal names follow the display names (ruling 5): enums,
ids, constants, file and class names, signal names, test names. No aliases, no migrations.
1. **Raid words** (ruling 6.2): Seized → TAKEN (`taken`), Disabled (node loss state) → DOWN (`down`), Holds → HOLDS
   (raid result "CELL HOLDS"), home server falling → BREACHED. Only the node-loss / raid meaning: "disabled" as a
   UI-control word or Hub-Breach "disabled 1 turn" stays.
   - Accept: a test sweeps `strings.csv` English and every `content/**/*.tres` text field and fails on the old raid
     words in that meaning (an allow-list for the unrelated meanings); seeded raid replay / verdict tests still
     pass with the new names.
2. **Modem → Mainframe** (ruling 6.5): node type, ids, file and class names, strings, codex, tutorial, GDD lines
   left. The GDD 11.7 heading "Mainframe Gate" collides; until the designer rules on D5, write it as
   "Mainframe Gate (name pending, D5)" in the GDD only and log it in your report.
   - Accept: `grep -rni modem scripts content scenes tests tools assets/text` returns nothing (or only the
     allow-listed history comments in DECISIONS-referencing comments); the same sweep test covers it.
3. **Priority Routing → Customs Seal** (`customs_seal`, ruling 6.1); rules unchanged.
   - Accept: the Manifest still gains 4 shield per turn unless breached (existing test, renamed).
4. **Saves folder (S0, ruling 5):** saves and replays go to a project folder git ignores.
   - `SaveService` (and the replay writer) write to `<project>/saves/` (profiles, campaign slots) and
     `<project>/saves/replays/` when running from source (`OS.has_feature("editor")` or not `template`); an
     exported build keeps `user://saves`. The folder gets a `.gdignore` written at creation so Godot never imports it.
   - Replays: when a combat ends, write the inputs the engine already records (setup id, seed, action list,
     result hash) as JSON to `saves/replays/` (source runs only; never in tests unless a test asks; GUT runs keep
     their per-pid folders). Path and on/off in config (no magic strings in code paths).
   - `.gitignore`: add `/saves/`.
   - `SAVE_VERSION` bumped; drop the migrations table content (no compatibility); an old-version file is refused
     through the existing "can't load" path with no crash.
   - Accept: tests for the path choice (source vs export), replay file round-trip (reload, replay, same result hash),
     old-version refusal; `git status` stays clean after a full suite run.
DECISIONS entry "Art direction — ART-0 names pass, part 1 + saves folder". Part 2 (D2–D8, D11–D12 after the designer
rules on them) comes to you by SendMessage.

### C — Salvage S1: accessibility settings (ART-0b S1)
Owns: `scripts/autoload/settings.gd`, `scripts/ui/settings_panel.gd` (behaviour only), the S1 tests.
From `art-m13-final` (W9s / W9F: `tests/**/test_w9_accessibility_settings.gd`, `settings.gd`, `settings_panel.gd`):
port text scale to 2.0, colour-blind modes, high contrast, reduce motion (distinct from reduce effects, as M13
had it), resolve speed, pad glyph sets, `city_quality`. Panel styling is NOT ported (ART-10 restyles the panel); add
the rows to main's current panel. Every layout test that main runs at 1.6 runs at 2.0 too (M13 W9F removed
`LayoutScales` in favour of every layout test at 2.0: port that approach; fix whatever breaks at 2.0 on main's
screens or list it per screen in your report with the smallest fix you applied).
- Accept: ported behaviour tests green; each setting round-trips through settings.json; defaults equal main's
  behaviour; every layout test passes at 1.0, 1.6 and 2.0; Settings restored after tests.

### D — Salvage S2: visual QA harness and lint (ART-0b S2)
Owns: `tools/visual_qa/**` (new), the review-pack tooling, runtime / static lint scripts and their tests.
From `art-m13-final` W10 / W9F: port the visual QA harness (screen matrix, review-pack contact sheets, static and
runtime lint: on-screen sizes, modals, scroll clipping, literal colours/sizes), re-pointed at **main's** screens and
scenes (main has ANIM views the harness has never seen). Baseline images are re-captured, not ported. The harness
must run only through `tools/run_windowed.py` for windowed captures and keep captures out of git (write under %TEMP%
or a git-ignored folder; review packs land later in `docs/art_review/ART-n/` with `.gdignore`).
- Accept: the harness runs on main's screens (all screens main has) × text scale 1.0 / 1.6 / 2.0 × mouse / pad ×
  reduce effects (+ greyscale, high contrast once C lands — gate those axes on the setting existing) and writes a
  contact sheet; the static lint runs headless as a test with a baseline file of today's violations (count recorded
  in DECISIONS, to be driven to zero by ART-1…12); you captured and READ one small contact sheet.

### E — Salvage S3 + S4: tokens / type machinery and VFX tiers (ART-0b S3, S4)
Owns: `scripts/ui/palette.gd`, `scripts/ui/ui_theme.gd` (mechanism), `assets/fonts/` (new faces only), VfxTier
(new), shader `reduce_effects` uniforms, their tests.
- S3: port the M13 W1 semantic-token mechanism (names, lookups, tests), type steps, tracking, MSDF switches and the
  Plex font with its licence. Values stay main's for now (ART-1 sets the v2 palette and faces). No view restyle.
- S4: port `VfxTier` ("no full-screen flash below T4"), the `reduce_effects` shader uniforms and
  `test_vfx_tiers.gd`. Zine-specific shaders are not ported.
- Accept: ported tests green; main's screens look unchanged (one windowed capture of combat and the Grid, read,
  compared with a capture from main before your change); every existing shader that animates has the uniform.

## Wave 2 (after C and E merge)

### F — Salvage S5: kit behaviour (ART-0b S5)
Component states, focus brackets (round 31: 3 px at 7 px offset, ART_BIBLE v2 Appendix C #15), `PadGlyph`,
`UiTip.for_input`, the `PageTransition` modal API (`open_modal` / `after_modals`), `UiWrap.whole_words`, `FitScroll`
guards, `PaperInk` high contrast. Behaviour and tests only; zine skins are not ported (ART-4 / ART-10 restyle).
- Accept: ported tests green; pad reachability unchanged or better on every screen; MotionSkip still owns the
  one-press skip.

### B part 2 — Names D2–D8, D11–D12 (after the designer's §3.1 rulings)

## File-ownership matrix (wave 1)
| Path | Owner |
|---|---|
| docs/** except DECISIONS append | A (B may touch GDD lines naming the renamed words) |
| assets/text/strings.csv | B (others append rows; union-merge + re-export) |
| content/** | B |
| scripts/core/**, scripts/state/** | B |
| scripts/autoload/save_service.gd, .gitignore | B |
| scripts/autoload/settings.gd, scripts/ui/settings_panel.gd | C |
| tools/visual_qa/**, lint tools | D |
| scripts/ui/palette.gd, scripts/ui/ui_theme.gd, assets/fonts/**, shaders | E |
| other scripts/ui/** | rename-only edits by B; layout-at-2.0 fixes by C; smallest change, reported |
| tests/test_manifest.json, DECISIONS | everyone (union) |

## Batch acceptance (ART-0)
- [ ] A1–A6, B1–B4, C, D, E, F, B part 2 merged one at a time, each followed by checks_fast.sh green, pushed; (full suite deferred to after ART-12).
- [ ] Full suite green with the ported M13 tests; the QA harness runs on main's screens.
- [ ] Timeline `17_art0` (the baseline before the new look) with a README row.
- [ ] GAP_ANALYSIS row, test count, DECISIONS per area.
