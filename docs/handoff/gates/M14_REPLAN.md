# Full replan after M14            2026-10-12 · main @ 19ad76a3 · feeds CP-002

Drafted by a read-only planning agent from MILESTONES, GAP_ANALYSIS, `docs/R7_REEVALUATION_PREP.md`,
`docs/handoff/anim_r7/`, `docs/ART_REINTEGRATION_PLAN.md` and DECISIONS. Spot-checked by the orchestrator.
A **wave** is up to 5 parallel agent slices, then a merge; every gate has one playtest (PT) list plus a checkpoint (CP).

## 1. Where the project stands
- M5–M14 are complete. M14 closed at PT-001: 2207 / 0 failing, smoke and validate green, perf medians inside 8 ms.
- Still to do: the "After ART-12" list (R7, G1–G16, horizontal list, H25+), five Queued passes, and follow-ups F1 / F2.
- `docs/GAP_ANALYSIS.md` is stale: §1 says "after M12, 1700 tests", and its pass log ends at H24.
- Code cleanup of the gate scope (tag `m14-cleanup`) found the 163 changed files already clean apart from one type. It
  listed about 190 numeric literals outside consts (rule 5); see §3.

## 2. M0–M4 unticked boxes (33)
29 are done (each backed by a named test), 2 are superseded, 1 is partial and 1 is open. Three need their wording
amended.

| Box | Verdict | Evidence / note |
|---|---|---|
| M0 ×4 (GUT exit 0, smoke + validate, RNG streams, registry) | Done | PT-001 suite; `test_rng_service`, `test_content_registry` |
| M1 ×11 (wheel math, precision, resistance, order, pointer, Breaker, statuses, preview = actual, rewind, replay, fight vs each enemy) | Done | `test_wheel_math`, `test_resistance`, `test_resolution_order`, `test_breaker`, `test_statuses`, `test_rewind`, `tests/integration/test_combat_scene` |
| M1 precision box | Done, **reword** | "Partial" is now WEAK (ART-0 names) |
| M1 pointer box | Done, **reword** | Pierce ignores block and shield, **not** satellites (GDD l.139; `test_pierce_still_hits_the_bodyguard_satellite`) |
| M2 maps, banking, completion, quit/resume | Done | `test_map_generator`, the banking and completion tests, `test_quit_and_resume_*` |
| M2 "every card, Firmware and Daemon tested" | **Partial** | Cards are covered by sweeps (`test_pools`); Firmware and Daemons are hand-picked, with no per-id coverage check |
| M2 "tier 1 netrun takes 12–18 min" | **Open (human)** | Not machine-checkable; the simulator measures runs, not minutes |
| M3 ×6 (thresholds, raid projection, cascade, assets, win/lose, save) | Done | `test_heat_rules`, `test_raid_resolver`, campaign tests |
| M3 cascade box | Done, **reword** | Disabled / Seized are now DOWN / TAKEN (ruling 6.2) |
| M4 "screens match the approved mockups" | Superseded | ART_BIBLE v2 replaced the mockups; M14 parity audit approved |
| M4 reduce effects, flash limit, colour-free cues, keyboard combat | Done | shader reduce-effects tests, the flash-rate tests, the glyph / second-cue tests, `test_keyboard_combat` |
| M4 colour-free cues | Done, caveat | The raid hostile cue shows only with the colour-blind setting on (DECISIONS l.6589) |
| M4 "60 fps at 1080p, mid-range PC" | Superseded | Closed by the ART-5 perf box and the target-PC ruling |

## 3. Made obsolete or urgent by M14
**Obsolete**
- **R7 items in views M14 replaced:** A5?, A12b, B3, B4, B8a, B8c, C1–C3, C9c–e (forecast in R7_REEVALUATION_PREP).
  C8a still needs a real check: `neon_city.gd` and `heat_poster.gd` are still in use.
- **R7 C4**, reading holds cut at 2× / 4×: fixed in ART-6.
- **G10 raid zoom:** built as `RaidZoomFit`.
- **G13 HQ actions:** answered by HQ direction B.
- **G16 card type band:** partly built (WHEEL / HACK / SYSTEM).
- **Stale "Open questions for the designer"** (about 50 entries), already settled: the Steam Deck run, B4 b perf, the
  letterhead and CP-001.

**Urgent**
- **R7 E, rules text keys** (about 90 English strings in `scripts/core/`). Do this before G-passes add more core text.
- **R7 P1 tutorial bugs** A1 and A2 are still valid.
- **Overkill wording "→ N LEFT"** is still live (`scripts/ui/combat_scene.gd:3429`, `:4677`); ruling 9 is owed.
- **Pacing drift.** The last sim needed about 43–49 runs at ICE 5 against a 24-run target. Nothing has been measured
  since M14, and every G-pass needs a sim baseline.
- **F1 / F2** and the perf watch (HQ idle tier-1 p95 11–12 ms).
- **Rule 5 sweep.** The cleanup listed absolute pixel literals in about 15 kit files (`spinner_view`, `heat_poster`,
  `zine_card`, `hud_bar`, `wheel_view`, `daemon_tray`, …). Move them to consts or config in a mechanical slice.

## 4. Remaining work (sizes are rough)
| Item | Scope | Waves / gates | Depends on | Rulings first? |
|---|---|---|---|---|
| Housekeeping | M0–M4 ticks and rewording; a Firmware / Daemon per-id coverage test; sim baseline at ICE 0 / 5; rule-5 sweep; delete merged branches | rides wave 1 | — | CP-002 3, 9 |
| R7 re-audit | Re-run the 22 "Check" repros, confirm the 19 "Valid" items, re-cut batches A–E | 1 / 0 | CP-002 1 | — |
| R7 fixes A–D (+F1 / F2) | Combat / tutorial, netrun, city / raid / HQ, motion kit / runner | 1–2 / 1 (PT-002) | re-audit | ruling 9 |
| R7 E + card-pile flights | Core emits `text_key` + args; views format the text; replays stay identical | 1–2 / shares PT-002 | A–D | wording calls |
| G1–G16 ruling session | One prep sheet per G item (art reference, rule impact, size); the designer approves, rejects or defers each | 0 / CP-003 | — (parallel with R7) | yes, this is the ruling |
| Horizontal list refresh | Rewrite GAP_ANALYSIS §1 / §4 / §5; collect the ART "owed" items; triage the open questions | 1 doc slice | R7 re-audit | → CP-003 |
| H25 (+H26…) | Vertical, horizontal and two naive audits over the post-M14 game; fix until CLEAN | 3–4 / 1–2 | R7 merged | — |
| Q: Rulings & balance | Rewards, Rigger buff, final-Rack Schematics, soft enrage, sinks; tuned by sim | 1–2 / 1 | sim baseline | already ruled |
| Q: Corporation unlocks | Solace → Meridian; Halcyon for Schematics; REBEL_CELL after ICE X; Orbital TBD | 1 / 1 | balance | ICE X, Orbital |
| Q: Card upgrades (+G5) | Design doc, then content for every card, shop and viewer | 3–4 / 2 | G4 | design; merge with G5? |
| Q: Slice rearranging | Rearrange slices outside combat | 1–2 / 1 | G1, G2 | hub / ring rules |
| Q: Daily run modifiers | Config table of modifiers; date seed picks the day's one | 1 / 1 | last | approve the list |
| G-passes (G11 → G6 → G2 → G1 → G4 / G5 → G3 → G14 → G8 / G9 → G12 → G7; G15, G16 folded in) | per ART_REINTEGRATION_PLAN l.482 | 15–28 / ~10 | rulings, balance | yes, each |

**Total: about 30–45 waves and 12–18 gates.** R7 is 4–5 waves, not the ~2 first quoted in CP-002.

## 5. Recommended order
1. **Wave 1:** R7 re-audit (3 auditors), the housekeeping slice and the sim baseline. The GAP_ANALYSIS refresh goes to
   the batch lane. The designer holds the G1–G16 ruling session during this wave.
2. **Waves 2–4:** R7 A–D with F1 / F2, then E plus the card-pile flights, then gate PT-002.
3. **H25 as R7's closing audit loop**, then a gate.
4. **Rulings & balance**, then **Corporation unlocks**.
5. **The approved G-passes in plan order**, with Slice rearranging after G1 / G2 and Card upgrades merged with G4 / G5.
6. **Daily modifiers last.**

Why this order:
- R7 is the only finished and approved fix list, and its P1 tutorial bugs and the core-text conversion are things every
  later pass builds on.
- The G ruling session needs only designer time, so it costs no waves.
- Closing R7 with H25 saves a separate audit wave.
- Balance before G-passes gives each pass a tuned baseline.

Alternatives:
- **B, gameplay first:** rulings and G-passes first, R7 and H25 once at the end. This avoids polishing views G1–G4 will
  change, but the tutorial P1s and the English core text stay through many gates.
- **C, ship scope:** R7, H25 and the Queued passes only, plus small G items (G14, G6, G16). Content-complete in about 15–20
  waves, for outside playtests; most concept mechanics are dropped.

## 6. Questions for the designer
Items 1–7 are in CP-002. The rest wait for CP-003, the G ruling session:
- Should G5 and Card upgrades be one pass?
- Does Slice rearranging come before or after G1 / G2?
- Does G12 wait for a G11 playtest?
- Do per-fight backdrops, the glyph slice and the crest go to the art-pass session in parallel?
- Triage the ~50 open questions.
