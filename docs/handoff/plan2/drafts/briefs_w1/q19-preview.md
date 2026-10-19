<!-- W1 brief via Message Batches, claude-sonnet-5-5, batch msgbatch_01XJNbnNCPMUUX88XP2A5B47, custom_id brief__q19preview; status ok; tokens in 8880 cache-write 0 cache-read 33457 out 1313; cost $0.019. DRAFT brief: not yet dispatched. -->
<!-- shortened by a second pass (compress), cost $0.008 -->

# Q19-PREVIEW: preview '?' rule for nudges and card plays

- **Goal:** Preview shows the exact result of any nudge or card play. Random outcomes show "?". A respin shows its direction plus "?" over a ghosted needle. A compound play shows known parts exactly and only unknown parts as "?". Preview must equal the real result (CLAUDE.md rule 6).
- **Base / tag:** `<BASE_SHA>` / `<TEMP_TAG>`
- **Agent type and lane:** fix-rules (Sonnet) for the core forecast, then fix-visual for the chip. No Opus: no RNG, save-format, damage-order or determinism contract changes. The forecast draws no random numbers.
- **Depends on:** N6, N9 (sources of "?"). Until they land, the unknown-marker API is exercised by RESPIN and RANDOM_NON_NULL.

**Read first**
- DECISIONS 2026-10-18: Q19 (binding), Q31, Q36, Q37.
- `docs/process/agent_rules/common.md`; `docs/handoff/plan2/drafts/test_plans/n6.md` and `n9.md` if present; GDD 2.10.

**Files**
- `scripts/core/combat_resolver.gd`: forecast entry for a staged action.
- `scripts/core/effect_interpreter.gd`: dry-run path marking unknown parts instead of rolling.
- New `scripts/state/preview_result.gd`: known value and unknown flag per part.
- `scripts/ui/wheel/` (chip, ghost needle).
- `content/config/ui_motion.tres`: fade/ghost timing, with REQUIRED_IDS entry and lab demo.
- `tools/export_text.gd` and `strings.csv`: "?" tooltip text.

**Acceptance**
1. Every nudge, and every fully deterministic card, previews values identical to the executed result across 200 seeded states.
2. A random part (RESPIN landing, RANDOM_NON_NULL pick) shows "?" never a sampled value. Preview draws 0 numbers from any RngService stream (state before == after).
3. A respin preview shows direction and "?" over a ghosted needle, and does not move the needle.
4. A compound play (deterministic hit + random status target) shows exact damage and block, "?" only on the random part.
5. After execution, each known part equals its preview; the unknown part is resolved and shown.
6. A rewind past a checkpoint leaves no stale preview.
7. The chip's "?" has a TextDb tooltip key; no hard-coded strings or motion fractions (all in `ui_motion.tres`).
8. Preview never mutates state (state hash before == after).

**Tests**
- New `tests/test_preview_unknown.gd`, tier `fast`: preview == result, zero-draw check, compound case. Add to `tests/test_manifest.json`.
- A flow test for the chip with bounded waits.

**Not in scope:** rider chips and Heat chip (follow-up, do not decide), N6/N9 effect content, `city_map_overlay` R5 lines.

**Conflicts:** `combat_resolver.gd` and `effect_interpreter.gd` are shared with N6, N7 and N9. Land after N6 and N9, merging one at a time.

**Report:** the RESULT envelope from `docs/process/agent_rules/common.md`.

Q: Does a "?" chip show the possible range or the odds, or only "?" (the rulings say only "?")?
Q: How should a preview show a random part inside a listener reaction (N6)?
