# Change plan 2: from PT-002 + PT-003b tester findings (designer go 2026-10-15)

The designer assumes PT-003 complete and says to start all the listed changes.
- **Lanes:** Batch API and lower models where they fit (memory route-cheapest-first).
- **Scope:** the deferred tier stays deferred.
- **The route map redesign is its own development pass.** The designer picked V3, a dynamic side-view cutaway that also
  covers the HQ. The art-pass session hands over the full package in one go, so plan 2 does **not** touch the route /
  HQ map views; their findings (PB-PT-003b C5, the heal markers) go to that pass.

Evidence:
- `docs/playtest/claude/PB-PT-002/_FINDINGS.md`
- `docs/playtest/claude/PB-PT-003b/_FINDINGS.md`
- `docs/playtest/claude/steps/PT-003_steps.md`

Rules: preview = result (rule 6); no tick marks; captures per group for the art-pass session; suite-rule tests before
hand-back (D18).

## Wave A: combat input (P1s; the top tester time sink in both batches)
| Slice | Items | Lane |
|---|---|---|
| A-INPUT (combat) | **Cancel / unstage:** Esc cancels an aim or staged card before it opens pause; right-click and Z are reliable; a visible cancel control on the staged card; clicks aren't swallowed while aiming (PT-003b B2, PT-002 C4). **Card-select → enemy-wheel click responds at once** (PT-003b B3). Selection must not jump to the neighbouring card (B4). SEND IT stall during an escalation (B7, + PT-002 B8): reproduce first. | fix-visual Sonnet |
| A-RULES (rules) | **UNDO after the turn-start spin** (PT-003b B1 / D7): cards staged after the turn's spin checkpoint must be undoable back to that checkpoint. That is not crossing it, so it's a fix, not a rule change. **Preview readouts changing with no input change** (B5): a preview = result violation; reproduce and fix. Restored-fight disagreement after CONTINUE (B6): check the save round trip. | fix-rules (OPUS-BECAUSE: checkpoint / RNG determinism and preview = result are the core's hardest invariants) |
| A-HAND (combat) | Card text clipped / garbled ("Blockev while th…", Fine Tune); overlapping hand hit areas; the raised card covers the deck and discard counters (PT-003b C2, PT-002 C6). Resting cards stay small (earlier ruling); faces must fit. | fix-visual Sonnet |

## Wave B: teaching and words
| Slice | Items | Lane |
|---|---|---|
| B-TEACH (screens + combat) | **Tutorial:** short step text, NEXT reads as live (PT-002 C9, PT-003b B8). It teaches the nudge, FREE NUDGE, Q / E / W, the RAM debt chip and the precision tags (PT-003b C1 / C3, PT-002 C2 / C3); testers still don't aim for Perfects (D1). Teach aiming for a Perfect as the core skill. | fix-visual Sonnet |
| B-CODEX (content text) | Codex entries for nudge, free nudge, tick, RAM / RAM debt, Null, Corrupted, Resist, Blocked / Guard, Heat thresholds, Cycles (PT-003b C3: 214 entries, none for "nudge"; PB-010 C10). Codex search if cheap. | Batch API Haiku drafts the entries (US English, from the GDD); fix-mechanical Sonnet applies them + strings |
| B-MENU (screens) | Abandon Run separated from Resume and Quit, with a confirm (PT-003b C6, PT-002 C5). Keyboard path gaps: loot / firmware picks, JACK IN, START DEFENSE, BACK, raid Continue, Market recruit (PT-002 C8), skipping the route view (redesign). | fix-visual Sonnet |

## Wave C: campaign clarity (no map views)
| Slice | Items | Lane |
|---|---|---|
| C-SCREENS (screens + city panels) | **Unlock currency** named, with balance and how to earn it (PT-003b C7). **Loot / Firmware pick confirmation:** say what was taken, and never hide an option behind the loot sheet (C8). **Heat words:** tutorial and banking text in plain English; thresholds stated where Heat shows; the +11 on arrival shown before acting (C4; W3-GRID did the Site files). | fix-visual Sonnet |

## Wave D: balance evidence (designer rulings before any tuning; CP-002 ruling 6)
| Slice | Items | Lane |
|---|---|---|
| D-SIM (rules, analysis only) | Free heuristic sweeps (`state_agent.py --strategist heuristic`) plus parameter variants in config copies. Measure: HP attrition with no heal (D2), fight length 9–16 turns and enemy HP (D3), the Schematics economy (D6), flatline Heat driving raids (D5). Output: `docs/handoff/plan2/BALANCE_OPTIONS.md`, 2–3 options per issue with sim numbers, for rulings. No content change. | fix-mechanical Sonnet (runs the sims) |

## Wave E: content design pass (D1; concepts and rulings before any build)
| Slice | Items | Lane |
|---|---|---|
| E-CONCEPT | The Genome Core is "easy but boring / tediously long". Concepts for enemies, bosses, events and raids: what they do, distinctive mechanics, and how fights end faster. Output `docs/handoff/plan2/CONTENT_CONCEPTS.md` with options and recommended picks, for rulings. | Plan agent (read-only) drafts; the orchestrator writes the file |

## Wave F: upkeep
| Slice | Items | Lane |
|---|---|---|
| F-RULE5 | The rule-5 remainder: the files W5 excluded, plus kit files with 12+ R5 lines (W5 RESULT). `const_edits` kind. | Batch API **Sonnet** (Haiku's edits didn't apply in W5); fix-mechanical applies them |
| F-PROCESS | Adopt D15–D20 (gate reports PT-002 / PT-003): one Godot process parse-checks all changed files; precommit always runs the suite-rule tests; parity picks a session with paired turns; briefs name the batch lane; batch edits use `const_edits`; no slice is DONE without its sheet. | fix-mechanical Sonnet |
| Routes | Re-record the playtest routes after the route redesign lands; recording now would break again. Testers start at the title until then. | — |

## G1–G16
Re-evaluation running (Explore, read-only) → `docs/handoff/plan2/G_REEVAL.md`. Startable items join the waves above;
the rest go to the designer as questions.

## Order and gate
- **Now:** A-INPUT, A-RULES, A-HAND, F-RULE5, F-PROCESS (5 worktrees). E-CONCEPT runs read-only in parallel.
- **Then:** B-TEACH, B-CODEX, B-MENU, C-SCREENS, D-SIM, and the startable G items.
- **Gate:** PT-004 (full suite once, the scripted steps runner via the Batch API, and a Claude screen batch when the
  machine allows).
