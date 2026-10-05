# M14 resume — orchestrator handoff (paused Mon 2026-10-05 ~16:00, resume 18:01)

You are the **orchestrator** for REBEL_CELL M14 (Art direction v2 port from `art-pass`). You coordinate agents;
you do not write batch code. You merge, check, push, report and keep the docs true. Clone: `D:\Godot\rebel_cell`
(branch main). Memory index loads automatically (`C:\Users\noitu\.claude\projects\D--Godot-rebel-cell\memory\`).

## Read first (fast)
1. `CLAUDE.md`; memory notes (art-pass-branch, push-gate, cloud-agents-run-locally, godot runtime, workflow).
2. DECISIONS 2026-10-05 entries at the top of "Implementation decisions" (all designer rulings; newest first).
3. This file, then each agent's `docs/handoff/m14_resume/<area>.md` (written at pause; on its branch until merged).
4. Briefs: `docs/handoff/art_0..art_4/ART_*_BATCH.md`, `docs/handoff/art_12/ART_12_BATCH.md`,
   `docs/handoff/art_0/CARRY_OVER.md` (cross-batch items), `docs/handoff/m14_audit/` (stored audit reports for the
   final audit), `docs/handoff/art_1/city_spike_report.md`.

## Standing designer rulings (binding)
- Port, never merge art-pass. **The art pass design is correct** (presentation follows ART_BIBLE v2 / locked
  concepts without asking; log it). **Reuse the art pass's assets — never redraw them** (run the concept's own
  generator scripts on tag `art-concepts-r43` or slice the approved images; procedural only where none exists).
- Mechanics the rules lack (G1–G16) are NOT built; re-evaluated after M14 (`docs/G_REEVALUATION.md`).
- ANIM-R7 paused until after M14 (`docs/R7_REEVALUATION_PREP.md`).
- **Checks:** fast checks only (`checks_fast.sh`) at hand-back and merge. **No full suite and no audit until after
  ART-12**; then one full run in isolation + one audit loop (vertical / horizontal / naive) to CLEAN.
- **Push gate:** push main ONLY via `SP=$TEMP/rc_orch bash docs/handoff/art_2/process/merge_push.sh` (pushes only
  if import/fast/smoke/validate are all 0). Never chain `git push` after a grep.
- Merging: `git merge --no-ff <branch>`; DECISIONS / strings.csv / ui_motion_data.gd / motion_lab.gd union
  (scratch `union.py` pattern: keep both hunks); **ui_motion.tres with the three-way
  `docs/handoff/art_2/process/merge_tres.py BASE OURS THEIRS OUT`** (BASE = `git show $(git merge-base HEAD
  MERGE_HEAD):<f>`); test_manifest.json with `merge_manifest.py`; after strings.csv run
  `godot --headless --path . -s tools/export_text.gd` then import; strip "# Conflicts:" from MERGE_MSG; watch for
  semantic clashes (duplicate members across subclass/parent — happened with RouteOverlay/CityMapOverlay).
- Agents: Opus for visual / rules work, **Sonnet for mechanical tasks**; ~9 at once; one Godot window each;
  batch Godot launches; never `python -` (if one hangs, kill only that PID — allowed for our own agents' strays,
  but never kill on an agent's request after the classifier denied it: surface to the designer).
- Groups overlap; designer reviews are non-blocking; GitHub CI is manual-only during M14 (sharded workflow ready).
- Keep %TEMP% clear: delete `rebel_cell_tests_*` older than 30 min and finished agents' `%TEMP%\<tag>\` folders.
- Hourly report to the designer: progress table, Gantt (show_widget, style of `m14_art_gantt_complete_mon_1540`),
  critical-path review with applied moves, finish estimate. Scheduled jobs only fire when the session is idle —
  produce the report yourself at a merge when an hour has passed.

## State at pause
main = **c66e427** (pushed). Fast tier 939 tests green. Merged: ART-0 (+ audit fixes), Group 1 (1A palette/faces/
theme, 1B material kit, 1C glyphs, 1D city spike → real-time 3D), Group 2 (2A wheels, 2B arena, 2C cards/FX,
2D HUD), 3B netrun 2D, 4B portraits/dialogue, 4D campaign end, 5a city model + Grid on 3D (+ buildings fix +
landmarks placed), 5b landmarks, 5c city motion, 5d Grid markers/key, 8p HQ compounds, CI sharding, docs sync.

## Agents paused (resume each from its branch + its m14_resume file)
Respawn each as a NEW agent (isolation: worktree), told to: `git merge <its old branch>` first (or check out its
work), read `docs/handoff/m14_resume/<area>.md` from that branch, then continue its brief. Old worktrees stay at
`.claude/worktrees/agent-<id>/` (branch `worktree-agent-<id>`).
| Area | Brief | Old branch | Notes |
|---|---|---|---|
| 3A raid 2D presentation (ART-6) | art_3 3A | worktree-agent-a0855db0bb959add2 | re-exporting vehicle icons etc. from concept scripts (reuse ruling); then 6w raid on the city |
| 4A shop, rewards, events, deck viewer (ART-9) | art_4 4A | worktree-agent-ae1eaaa9153075336 | concept asset exports in progress |
| 4C title, menus, settings, HQ screen (ART-10) | art_4 4C | worktree-agent-a0cb90b54d201c218 | build abandon dialog on 2D's HudDialogPanel |
| 5e city integration (critical path) | art_3 wave 2b | worktree-agent-a6251886202f8044b | landmarks placed by 5a already; Site glbs, motion+markers on live Grid, crest reveal, TARGET, ×2 spread, roof props export, day-look API, reduce motion 40 % |
| 7w netrun on the city | art_3 wave 2b | worktree-agent-a22a15b76e7966ef8 | merge main for the buildings fix |
| 8w HQ runs on city + canyon + Central Server + D17 swap | art_3 wave 2b | worktree-agent-af369f8f018afa386 | 8p compounds are its |
| Asset parity: combat + foundations | (rules + DECISIONS reuse ruling) | worktree-agent-ab68662e2190e33b2 | inventory `docs/handoff/m14_asset_parity/combat.md` |
| Asset parity: city + screens | same | worktree-agent-a70306033acfdedd2 | also fixes test_anim_r6_rules MotionSkip registration (rubber_stamp, route_overlay) |
| 12s skins (ART-12) | art_12 | worktree-agent-a00c6982b0b32d285 | |
### Checkpoints at pause (all 9 answered; each wrote `docs/handoff/m14_resume/<area>.md` on its branch)
| Area | Final commit | Must do first on resume |
|---|---|---|
| 3A | 34a8f0c | wire the BREACHED bit burst (6484926, not imported); DECISIONS source table; also take 4C's P3 "raid setup SAVED stamp almost invisible"; then hand back → 6w raid on the city |
| 4A | 6f610d1 | re-run own scripts (2.0 wedge overlap rework untested), re-export strings, fast checks, hand back |
| 4C | f65bd36 | fix the title verbs column overlapping MORE by ~2 px at 2.0 (`test_art10_menus`); re-capture crops (taken before the concept-art switch) |
| 5e | 6e1793a | reduce motion: the view reports zero ambience under reduce motion, so 40 % traffic never shows — fix per its notes; wire Cell reveal / DISPATCH fist / Site landmarks; then motion on the live Grid, markers, ×2 spread, TARGET, roof-props export |
| 7w | 1f5cc3e | merge main (buildings fix); its Solace capture showed flat blocks — re-check after merge; 1080p frame time |
| 8w | 1e61251 | compound validator fails for the DISPATCH canyon (two rooftop slot pairs 18 px / 1 px apart, min 50) — fix `hq_compound_spec.py`; then Godot seams, HQ-run page, Central Server gate, D17 swap |
| parity combat | f4b4081 | nothing imported/compiled/run yet: import, fix, test; evade token + drone sticker not drawn yet; inventory doc + DECISIONS |
| parity city/screens | 19fc530 | import + campaign-end tests; billboards and 3D car/chopper/drone models; inventory doc; strings re-export ("Gold key") |
| 12s skins | 994a126 | test_art12_skins 7/9 last run (one test reads the wrong panel); re-export strings (dropped verdigris); captures; DECISIONS |
Known red on main's full tier (fixed on branches, land with them): test_anim_r6_rules (rubber_stamp / route_overlay
— parity city/screens fixed it; 1B's inline tween in vinyl_sticker.gd and Group 2's `p * 2.0` in fx_draw.gd still
need a fix — give to parity combat), test_anim_r2_combat (fx_draw.gd).

### Calls to make on resume (orchestrator, under the standing rulings; log each in DECISIONS)
- 5e ×2 Site spread pushes many Sites out of their corp's territory (Meridian 24/32, Halcyon 26/32, Rebel_Cell
  17/32): default — aim each corp's layout into its own territory (presentation only; verify sweeps).
- 5e: keep 5d's markers drawn by the Grid overlay (already correct, tested) instead of moving them to
  SiteMarkerLayer — accept. Grid stays night (no day rule); DISPATCH's fist shows in the REBEL_CELL campaign — accept.
- parity: Exploit marker = the v4 script's single gold key (approved art wins over the bible's "keyring"); corp
  seals use the round 6 emblems the seal script builds — accept (art pass is correct). Card kinds: violet "other"
  cards drawn as SYSTEM — log as an open question; WEAK sticker amber per concept — accept.
- 8w: keycards carry baked English text (concept generator) — log a translation open question; Central Server name
  "DISPATCH" vs concept "DISPATCH CORE" — follow the concept (art pass is correct), rename the display string.
- 3A: the Compiler Rack has no concept glyph (uses picto_ram) — add to the post-M14 glyph concept slice.
Branches that had no commits at pause still need the resume file; if an agent never answered, read its
worktree's `git status` / log and brief the new agent from that.

## Next after resume (critical path)
5e → **6w raid on the city** (start when 3A hands back; brief in art_3 wave 2b) → 12q QA matrix + 12p perf (this PC,
both city_quality tiers; no real Deck needed) + 12b bookkeeping (timelines 18–21, GAP_ANALYSIS rows, MILESTONES
ticks, STYLE_GUIDE/ART_BIBLE updates) → one full-suite run in isolation → the M14 audit (stored reports as input)
→ fixes to CLEAN → re-enable CI triggers (fix the order-dependent pass-20 test first) → "M14 complete".
Estimate at pause: Tuesday ~22:00 (range to Wednesday morning). After M14: R7 re-eval + fixes, G1–G16 review,
horizontal re-eval, glyph + crest concept slices, H25+, Queued passes.

## Open designer questions logged (not blocking)
2D: A/D boss nudge keys; run-results row; tutorial run bar. 2A: tier I screen gain. 4D: ballpoint face. 5c/5d/5b/
1B/1D items under DECISIONS "Open questions for the designer". Apply the standing rulings before asking.
