# REBEL_CELL — Vertical Slice Milestones

Goal: prove the core loop is fun with one class (Breaker), one corporation (Solace) and a
10-Site City Grid before building more content. Work one milestone at a time. A milestone
is done only when **every** acceptance criterion passes and all tests are green headless.

Placeholder art is expected until M4 (see `STYLE_GUIDE.md` §7).

---

## M0 — Foundation
**Build**
- Project structure per `TECH_SPEC.md` §2; move provided schemas to `scripts/data/`.
- Install GUT 9.x; add one passing test per test folder.
- Autoloads: `SignalBus`, `ContentRegistry`, `RngService`, `SaveService` (skeleton),
  `RunManager` (skeleton).
- `content/config/campaign_config.tres` with every value from GDD §11 and the config
  groups in `CampaignConfigData`.
- `tools/validate_content.gd`: loads all content and prints every `validate()` error.
- Input map for GDD §9.5 bindings.

**Acceptance**
- [ ] `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit` exits 0.
- [ ] `tools/schema_smoke_test.gd` and `tools/validate_content.gd` exit 0.
- [ ] `RngService` streams: same seed → same sequences; streams are independent (test).
- [ ] `ContentRegistry` resolves every content id; duplicate ids fail validation.

## M1 — Combat Core
**Build**
- `wheel_math`, state classes, `CombatResolver`, turn state machine, effect interpreter
  (effect types used by Appendix A), preview, rewind with checkpoints.
- Content: Breaker (wheel, Hub Core, starting deck), slice types, Collections Agent (with
  satellite), Compliance Officer (Hub resistance), Dosage Dispenser (DOSE).
- A functional (ugly is fine) combat scene: two wheels, hand, preview readouts, targeting,
  nudge, end turn, rewind, log.

**Acceptance**
- [ ] Wheel math matches GDD §2.3 for all 30 ticks, flipped and unflipped (table test).
- [ ] Precision tiers: offsets 0/±1/±2 → Perfect/Good/Partial; no Miss tier exists.
- [ ] Resistance absorbs nudges and spins tick-for-tick; Flip and Respin are blocked while
      resistance > 0; passive resistance restores each player turn; Hub Breach disables
      Hub resistance for one turn.
- [ ] Resolution order: defensive → offensive → statuses, simultaneous on both sides.
- [ ] Pointer rule and satellite bodyguard work; Pierce ignores satellites and block.
- [ ] Breaker Perfect hook resolves the slice twice; Inner Ring ×2/Pierce apply.
- [ ] CORRUPTED, OVERCLOCKED, ENCRYPTED behave per GDD §2.9.
- [ ] **Preview equals actual** for 500 random seeded turns.
- [ ] **Rewind** restores exactly and cannot cross a checkpoint; checkpoints survive
      save/load.
- [ ] **Determinism:** replaying a recorded fight from its seed gives an identical state
      hash.
- [ ] A full fight against each of the three enemies is playable in the scene.

## M2 — Netrun Loop
**Build**
- Map generator (TECH_SPEC §6), map scene, node types, Terminal events (5 placeholder
  events), Mainframe shop, rewards (cards 1-of-3, elite Firmware 1-of-2, Rack Daemon 1-of-3,
  asset drops), Heat per node, Server Rack banking, death and completion flow.
- Content: all Appendix A.2 cards, A.3 normal + elite enemies, A.4 Firmware & Daemons,
  A.5 assets.
- Run save/resume.

**Acceptance**
- [ ] 1,000 seeds generate valid maps (reachability + guarantees); same seed = same map.
- [ ] Banking: Schematics and assets bank on Rack capture; death loses only unbanked items;
      death adds 10 + tier Heat.
- [ ] Completion: Cycles convert 10:1; operative keeps deck/Firmware/Daemons; Rank +1.
- [ ] Every card, Firmware and Daemon in the slice has at least one unit test.
- [ ] Quit mid-run (including mid-combat) and resume to the identical state.
- [ ] A Tier 1 netrun is completable in roughly 12–18 minutes of play.

## M3 — Campaign & Raids
**Build**
- HQ scene (roster, recruit, station, spend), City Grid scene with the A.6 Grid, Site
  selection with rank gating, claiming and 3 node types (Relay, Firewall Relay,
  Safehouse), Heat meter with threshold events/modifiers, Armory, raid setup +
  projection + playout, node loss states, repair, Rank 1 Inner Ring, Exploits (3) with
  placeholder story beats, Renewal Engine boss with phases, win/loss flow.

**Acceptance**
- [ ] Threshold events fire once only; modifiers switch off when Heat drops below.
- [ ] Raid projection equals the real raid result (golden tests for 5 layouts).
- [ ] Disabled/Seized rules, cascade (50%), step cap and home-server loss per GDD §7.
- [ ] Deployed assets persist and can be repositioned; Armory cap 6 enforced.
- [ ] Beating the Renewal Engine with 3 Exploits wins the campaign; home integrity 0 loses
      it; profile records update.
- [ ] Campaign save/load round-trip is exact.

## M4 — Look, Feel & Accessibility
**Build**
- Three-worlds visual baseline per `STYLE_GUIDE.md`: cyberdeck HQ, wireframe Grid and
  arena (glow shader, grid floor), zine UI kit (cards, HUD, notes, stamps), jack-in
  transition, precision feedback, Heat feedback, ratchet/tick audio and placeholder
  music by context, accessibility settings.

**Acceptance**
- [ ] Combat, Grid and HQ screens match the approved mockups' layout and style rules.
- [ ] Reduce-effects toggle disables scanlines, flicker and chromatic effects everywhere.
- [ ] Flash limiter: never more than 3 flashes per second (automated check on the event
      stream).
- [ ] Every slice type and status is distinguishable without colour.
- [ ] Full keyboard play is possible for combat.
- [ ] 60 fps at 1080p on a mid-range PC.

---

## M5 — Vertical Completion (added 2026-09-24)

The designer asked for every vertical-slice gap to be fixed and the project analysis rerun
until clean (`GAP_ANALYSIS.md`, pass log). Decisions are the implementer's, logged in
`DECISIONS.md`.

**Acceptance**
- [x] Every `RuleModifierType` in the ICE ladder and the Heat thresholds changes play, each
      with a test (combat, netrun, campaign, raids).
- [x] Every effect type and slice type resolves (no "not implemented" path is reachable).
- [x] All seven node types, node upgrades, Profile unlocks, a second home-server variant,
      netrun boosts, and every raid trigger source exist and are tested.
- [x] The combat UI plays every card in the pool from the keyboard (slice and direction
      pickers, respin, inspect, odds for random effects).
- [x] Solace has 30-40 Sites, six written story paths, DISPATCH briefings for every Site,
      subtitles, a codex and a text export for translation.
- [x] Title, save slots, pause, options (display, audio, key rebinding, language),
      tutorial, achievements, CI and export presets.
- [x] A seeded bot campaign wins at ICE 0 and ICE 5 within ±20% of GDD 11.8 pacing
      (`tools/simulate_campaign.gd`).
- [x] Tests, schema smoke test and content validation green.

## M6 — Class Roster (added 2026-09-24, horizontal loop)

Ghost, Rigger and Botnet from GDD 5.2 plus one alternative per class (GDD 3.4), with
recruitment gated by Profile unlocks. Decisions are the implementer's, logged in
`DECISIONS.md`.

**Acceptance**
- [x] Ghost, Rigger and Botnet: wheel, Hub Core and Mk2, Rank 1 ring, Rank 3 options,
      starting deck, two exclusive cards, station bonus and barks.
- [x] Four alternatives (Wrecker, Phantom, Overclocker, Hivemind): same deck, new core.
- [x] Recruitment by class; class unlocks (80 Schematics, alternatives 60); the new
      campaign picks the starting crew's class.
- [x] Botnet drones persist between the fights of a netrun and survive save/load.
- [x] PARASITE status; station hold, regen and turrets in raids.
- [x] A seeded bot campaign wins at ICE 0 with every class (`tools/simulate_campaign.gd
      -- 8 0 class=<id>`).
- [x] Tests, schema smoke test and content validation green.

## M7 — Pools and Solace Depth (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Shared cards 60, Firmware 18, Daemons 24, defense assets 8, shop slices 12.
- [x] Solace netruns can roll 40 Terminal events; every choice resolves.
- [x] Every shared card plays with preview == result; new Firmware, Daemon hooks and
      assets are tested.
- [x] Seeded bot campaigns still win at ICE 0 and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M8 — Corporation Selection and Meridian Freight Systems (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Corporations are Profile unlocks; the new-campaign panel picks the target and its ICE
      ladder; a locked corporation cannot be started.
- [x] Meridian Freight Systems: 32-Site Grid, 6 enemies, 2 elites, mini-boss, phased boss,
      3 Exploits, threats and 8 raids, 6 story paths, 20 events, DISPATCH briefings and
      corporate voice, colour.
- [x] Heat-threshold raids resolve to the corporation's own raid.
- [x] Seeded bot campaigns against Meridian win at ICE 0 (every base class) and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M9 — Halcyon Civic (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Halcyon Civic: 32-Site Grid, 6 enemies, 2 elites, mini-boss, phased boss, Exploits,
      threats and 8 raids, 6 story paths, 20 events, briefings, corporate voice, colour.
- [x] Citations (PARASITE on your wheel) and the Civic Core hub are tested.
- [x] Seeded bot campaigns against Halcyon win at ICE 0 and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M10 — Orbital Commons (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Orbital Commons: 32-Site Grid, 6 enemies, 2 elites, mini-boss, phased boss, Exploits,
      threats and 8 raids, 6 story paths (one foreshadows REBEL_CELL), 20 events, briefings,
      corporate voice, colour.
- [x] Solar Flares (OVERCLOCK on your wheel) and the Commons Array hub are tested.
- [x] Seeded bot campaigns against Orbital Commons win at ICE 0 and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M11 — REBEL_CELL (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] REBEL_CELL opens free once every other corporation is cleared at ICE 10; own ladder.
- [x] Built from the profile: Mirror elites (your classes' wheels and Daemons), Site names
      (your node types), Mirror raid threats (your assets); deterministic; rebuilt from the
      saved snapshot on resume; the loaded template is never modified.
- [x] DISPATCH reveal: six story paths and DISPATCH as the final boss.
- [x] "Final final" achievement.
- [x] Seeded bot campaigns can win REBEL_CELL at ICE 0 and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M12 — Polish and Reach (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Five home-server variants, each a Profile unlock after the standard one.
- [x] Every combat action has a controller button (cards and pickers: D-pad focus + A);
      every panel, modal and the combat hand (also after a card play) holds focus, and the
      start panel's ICE and seed have buttons, so pad-only play works; Tab and Space keep
      their keyboard meanings; rebinding keys keeps the pad button. (Checked headless;
      confirm on real hardware; modal focus traps and 1.6 text-scale fit fixed in H14, the
      pause menu's Options size and hotkeys behind it in H15.)
- [x] Share codes replay the same campaign; a daily run seeds from the date.
- [x] Assist mode: extra free nudge and HP, no ICE records or achievements.
- [x] Skins: done in M14 (ART-12 12s: v2 / cobalt / graphite, Options > Display).
- [x] Tests, schema smoke test and content validation green.

## M13 — Art pass v1 (art-pass branch, superseded in part)

Presentation only, governed by ART_BIBLE v1.0 (now `docs/ART_BIBLE_v1.md`); plan in
`docs/art_history/ART_PLAN_M13.md`; DECISIONS "M13 art pass (art-pass branch, superseded in part)".
Built on branch `art-pass` (from `8ddfa86`), **never merged**: W1–W10 + WF + W9F, 1414 tests green
there. Tags: `art-m13-final` = `f80f393` (the last M13 code state) and `art-concepts-r43` =
`9a62cec` (concept rounds 1–43, ART_BIBLE v2, the reintegration plan). The concept direction
superseded its zine / neon / cyberdeck look; its direction-agnostic infrastructure is ported by
M14 ART-0 (salvage S1–S5), the rest is re-implemented from ART_BIBLE v2 (DECISIONS 2026-10-05 "Designer rulings: art reintegration, pause point 0", rulings 2 and 4).

Done on `art-pass` (summary of its acceptance box): W1 tokens, type scale, MSDF, Plex body face ·
W10 visual QA harness and lint · W2 component library · W4 cards · W6 VFX tiers and shader library
· W9 accessibility settings (text scale 2.0, colour-blind, high contrast, reduce motion, resolve
speed, glyph sets) · W3 wheels and combat · W5 characters · W7 city · W8 screens (8a–8d) · W9F
final accessibility sweep; tests, schema smoke test and content validation green on the branch.

## M14 — Art direction v2 (added 2026-10-05)

Port the art pass onto main (DECISIONS 2026-10-05 "Designer rulings: art reintegration, pause point 0"): ruling 1 puts M14 first, ruling 2 ports and never merges.
Visual source of truth: `docs/ART_BIBLE.md` (v2) with `docs/art_reference/`; plan:
`docs/ART_REINTEGRATION_PLAN.md` §4 (loop shape §4.1: batch → audit ART-Rn → fix batch until
CLEAN → designer review). ANIM motion behaviour is kept and restyled (MotionSkip, holds, reduce
effects = end state, `ui_motion.tres` entries).

**Acceptance (M14):** the look and most of the feel of the art pass are present by the end of the
milestone (ruling 2), or M14 has failed.

**Shape (designer, 2026-10-05, "Designer ruling: M14 regrouped"):** ART-0, then four groups, then the
final sweep. Inside a group its batches are built **in parallel** (one agent area each, at most 4–5
agents); ~~the group gets **one** audit round (vertical / horizontal / naive) and its fix rounds until
CLEAN, then **one** designer review. The next group's brief may be written while the previous group is
in audit. Check cadence ("Designer ruling: check cadence for M14"): fast checks per hand-back and merge;
the full suite ×3 once per group, in isolation, before its audit.~~ **Superseded** (DECISIONS 2026-10-05,
"one full run, one audit at the end"): each group ends with **one** full-suite run in isolation (two more
runs only after a failure, to tell flaky from real) and the designer review; there are **no per-group
audits**: the single vertical / horizontal / naive audit loop runs once, after ART-12, over all of M14.
- **Group 1 — Foundations:** ART-1 (everything else builds on its kit and the render spike).
- **Group 2 — Combat:** ART-2 wheel stack, ART-3 cards and FX, ART-4 HUD.
- **Group 3 — City:** ART-5 unified city, ART-6 raid, ART-7 netrun, ART-8 HQ runs (ART-5's city model
  and render tech land first inside the group; 6–8 build on it).
- **Group 4 — Screens:** ART-9 shop / rewards / events / dialogue / portraits, ART-10 menus / title /
  settings, ART-11 campaign lost and dossier.
- **Final:** ART-12 sweep, then the one M14 audit loop to CLEAN, "M14 complete".

Every batch also meets the common acceptance (plan §4.1): 3 checks green (one full-suite run per
group, never only the fast tier); new tests in `tests/test_manifest.json`; layout tests at 1.0 / 1.6 / 2.0; reduce
effects = end state; headless never waits; motion values in `ui_motion.tres` with a lab demo; no
colour or size literals (tokens); the runtime lint clean; a GAP_ANALYSIS ART-n row; the perf
budget met in a windowed profile (plan §5.2). Boxes are ticked only as the orchestrator merges.

**ART-0 — Rulings, landing, salvage** (`docs/handoff/art_0/ART_0_BATCH.md`)
- [x] A1–A6 docs landing (bible v2 + v1, plan, `docs/art_reference/`, art history, GDD 9, this box).
- [x] B1–B4 names pass part 1 (raid words, Mainframe, Customs Seal) and the saves folder.
- [x] C accessibility settings, D visual QA harness and lint, E tokens / type machinery and VFX
      tiers, F kit behaviour; B part 2 names D2–D8, D11–D12 after the §3.1 rulings.
- [x] The full suite is green with the ported M13 tests; the QA harness runs on main's screens.
- [x] Timeline `17_art0` (the baseline before the new look) with a README row.
- [x] ~~Audit round ART-R0 to CLEAN.~~ Superseded: one M14 audit after ART-12 (DECISIONS "one full run, one audit at the end").

### Group 1 — Foundations
- [ ] Group 1 merged with fast checks green; designer review (non-blocking; full suite deferred to after ART-12, DECISIONS "groups in parallel, fast checks only").

**ART-1 — Foundations** (palette v2, faces incl. Courier Prime, theme, the material kit, glyph
pipeline, the render spike)
- [x] Kit sheet capture vs `round3_overlay/combined_v2`, `round33_ui_chrome/ui_kit.png` and
      `typography.png`.
- [x] Every shader has a `reduce_effects` uniform and a VfxTier (`test_art1_material_kit`).
- [x] Lint rule: no UI node's rect over a pencil stroke (PencilLint, in the runtime lint).
- [x] Render spike for the unified city, **fidelity first** (ruling 7): the technique that
      reproduces the reference images most faithfully is chosen, then an optimisation round brings
      it inside the plan §5.2 budget (the budget is a gate, not a reason to change the look).

### Group 2 — Combat
- [ ] Group 2 merged with fast checks green; designer review (non-blocking; full suite deferred to after ART-12, DECISIONS "groups in parallel, fast checks only").

**ART-2 — Combat wheel stack**
- [ ] The worst-case clutter fixture renders legibly at 1.0 and 1.6.
- [ ] Preview == result still holds.
- [x] Wheel draw time is within budget (3.8 ms mean vs 4 ms, 2A).

**ART-3 — Cards and FX**
- [x] Every FX has an entry in `ui_motion.tres`, a lab demo and its reduce-effects end state.
- [x] Flash limiter (≤ 3/s) test (`test_the_flash_limiter_holds_local_fx_flashes_to_three_a_second`).
- [x] The D16 origin rule tested (`test_d16_origin_rule`).

**ART-4 — HUD**
- [x] GDD 2.10 holds: chip == resolve for all enemies × seeds (the H23/H24 sweeps re-used).
- [ ] Pad reachability.
- [x] Fits at 2.0 (`test_the_hud_fits_at_every_text_size`).

### Group 3 — City
- [ ] Group 3 merged with fast checks green; designer review (non-blocking; full suite deferred to after ART-12, DECISIONS "groups in parallel, fast checks only").

**ART-5 — Unified city model and motion**
- [ ] Each corporation's Grid capture vs the reference.
- [x] Motion layers pause under reduce motion (`test_the_pause_and_reduce_rules`).
- [x] LOD switches at the configured zooms (`test_the_car_lod_swaps_at_the_configured_zooms`).
- [ ] 60 fps at 1080p on the target PC, and the Deck tier.
- [x] Logic-side tests headless (projection, picking, label placement); render verified windowed.

**ART-6 — Raid**
- [ ] The raid verdict sweep still matches `raid_verdict`.
- [ ] Reading holds never shortened at 2x / 4x (R7 C4).
- [ ] Every changing state has a capture.
- [ ] DOWN is the Site markers' white bolt over a greyed marker at every zoom; no amber dashed
      socket (ruling 11).

**ART-7 — Netrun**
- [ ] The route sweeps for every corporation still pass (labels, you-are-here, fits).
- [ ] The transition skips with one press (STYLE_GUIDE 5.1).

**ART-8 — HQ runs**
- [ ] Each corporation's HQ run is playable and captured; the boss backdrop matches the city
      model (D17).

### Group 4 — Screens
- [ ] Group 4 merged with fast checks green; designer review (non-blocking; full suite deferred to after ART-12, DECISIONS "groups in parallel, fast checks only").

**ART-9 — Shop, rewards, events, dialogue, portraits**
- [x] The shop and event sweeps (affordability, outcome rows == deltas) still hold (4A ported `test_horizontal_pass20/23/24_screens` and kept their behaviour; confirm in the full run).

**ART-10 — Menus, title, settings** (plan §4.2 names references, no acceptance line; these are
its items)
- [x] Title option A with the verbs (D10) and SIMULATE; the abandon dialog; Options on the v2 kit
      (incl. `heat_glitch`, always-show nodes), each captured vs `round33_ui_chrome/title_screen.png`,
      `title_screen_alt_simulate.png`, `abandon_dialog.png`.
- [x] Codex, stats, achievements, pause, campaign slots and the new-campaign picker on the v2 kit;
      corp paper in Courier Prime.

**ART-11 — Campaign lost and dossier** (no acceptance line in the plan; these are its items)
- [x] Campaign lost = A, ransomware lock; the campaign summary as a corporate dossier with the
      audit report; campaign won in the same language.
- [x] Run end (FLATLINED / JACKED OUT / HOME FELL) restyled.

### Final

**ART-12 — Final sweep**
- [ ] The full QA matrix (all screens × 1.0 / 1.6 / 2.0 × mouse / pad × reduce effects × high
      contrast × greyscale × colour-blind).
- [ ] A perf profile on the target PC and the Deck tier.
- [x] Skins (the M12 box: procedural palette skins on the v2 tokens). ART-12 12s: v2 / cobalt / graphite,
      Options > Display picker, `test_art12_skins`; DECISIONS "Art direction — ART-12 12s skins".
- [ ] **One full-suite run** in isolation (the only one in M14), then **the M14 audit** (the only one): vertical / horizontal / naive over every ART-0…12 change, fix
      rounds until CLEAN (nothing deferred, P3s included); "M14 complete" logged in DECISIONS.

*Left unticked by ART-12 12b, and why:* the four "Group n merged" boxes (they wait for the full-suite run and
the designer review); ART-2 clutter fixture at 1.0 / 1.6 and "preview == result still holds" (confirm in the full
run; no named test here); ART-4 pad reachability; ART-5 per-corporation Grid captures vs reference and 60 fps /
Deck tier (12p); ART-6 verdict sweep, reading holds at 2x / 4x, a capture for every changing state and the DOWN
bolt line (3A captured it; the playout capture is for 12q); ART-7 route sweeps and the one-press skip; ART-8
per-corporation HQ run captures and D17 check; ART-12 QA matrix, perf, full suite and audit.

**After ART-12** (rulings 1, 8, 9; nothing deferred)
- [ ] **R7 re-evaluation:** every ANIM-R7 finding (`docs/handoff/anim_r7/`) re-checked against the
      ported screens, then the ones still valid fixed (batches A–E re-cut), incl. the overkill
      wording "→ N LEFT" (ruling 9).
- [ ] **G1–G16 re-evaluation with the designer** (plan §3.2, ruling 8); approved ones become
      G-passes.
- [ ] **Horizontal list re-evaluation.**
- [ ] Then H25+ and the Queued passes below.

## Queued passes (designer, 2026-09-27)

Order: finish the Animation pass review loop (ANIM-R1…, until an audit is clean), then the
horizontal review loop (pass 25+), then these passes, each with its own review loop. See
DECISIONS "Designer rulings on the open questions".
Order changed 2026-10-05 (DECISIONS 2026-10-05 "Designer rulings: art reintegration, pause point 0", ruling 1): M14 first, then the
R7, G1–G16 and horizontal re-evaluations, then H25+ and these passes (see M14 above).

- [ ] **Rulings and balance**: rewards up slightly for pacing (sim-tuned); a small Rigger
      buff at ICE 0; an extra Schematics payout at the final Rack; a soft enrage for boss
      stalls; more Schematics sinks (boosts, unlocks); balance simulation logged.
- [ ] **Corporation unlocks**: beat Solace → Meridian; Halcyon bought with Schematics;
      REBEL_CELL after ICE X on every other corporation; Orbital's rule decided in the
      pass; profile, title and HQ show each rule; tests.
- [ ] **Card upgrades**: design (how, where, what changes, price), content for every card,
      shop and viewer support, balance lever in config, tests, simulation.
- [ ] **Slice rearranging**: the player rearranges wheel slices at any time outside combat
      (HQ and in a run), with drag and drop and pad/keys, rules and tests.
- [ ] **Daily run modifiers**: a config table of modifiers (corporation, ICE rules,
      starting deck/wheel twists, boosts...), the day's pick from the date seed, shown on
      the start screen, and a test that each modifier works.
- [x] **Skins** (M12's open box): a skin system with procedural palette skins now; art later.
      (Done in ART-12 12s.)

