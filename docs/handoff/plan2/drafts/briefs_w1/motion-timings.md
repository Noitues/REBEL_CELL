<!-- W1 brief via Message Batches, claude-sonnet-5-5, batch msgbatch_01XJNbnNCPMUUX88XP2A5B47, custom_id brief__motiontimings; status ok; tokens in 8846 cache-write 0 cache-read 33457 out 1695; cost $0.021. DRAFT brief: not yet dispatched. -->
<!-- shortened by a second pass (compress), cost $0.010 -->

# MOTION-TIMINGS: inline motion timings to ui_motion.tres

- **Goal**
  - Move inline motion timings (`dur * 0.2`-style fractions, fade spans) out of `combat_fx_layer` and `wheel_view` into `content/config/ui_motion.tres`. Each moved value gets a `REQUIRED_IDS` entry and a lab demo.
  - Behavior unchanged: with reduce effects on, the end state is identical. Only combat-view motion in these two files. No new motion, no retuning.
- **Base / tag**: `<BASE_SHA>` / `<TEMP_TAG>`
- **Agent type and lane**: fix-mechanical, Sonnet. No Opus: no RNG, save format, damage order or determinism contract.
- **Depends on**: none

## Read first
- `docs/process/agent_rules/common.md` (ui_motion rule: REQUIRED_IDS plus lab demo) and `docs/process/agent_rules/fix-mechanical.md`.
- DECISIONS: `grep -n "RULE5b" docs/DECISIONS.md docs/decisions/`, `grep -n "reduce effects" docs/DECISIONS.md`, `grep -n "ui_motion" docs/DECISIONS.md`.
- Ruling Q19: the preview "?" rule. Don't change it.
- `python tools/batch/context_slice.py --deps scripts/ui/combat_fx_layer.gd` (same for `wheel_view`).
- Before editing, write `docs/handoff/MOTION_TIMINGS_INVENTORY.md`: one row per inline timing with file:line, current expression, proposed id, value, and base it scales from (e.g. `dur`).

## Files
- `scripts/ui/combat_fx_layer.gd` (edit)
- `scripts/ui/wheel_view.gd` (edit)
- `content/config/ui_motion.tres` (add entries only)
- `REQUIRED_IDS` list and lab demo; find with `grep -rn REQUIRED_IDS scripts tests`, don't invent paths.
- `docs/handoff/MOTION_TIMINGS_INVENTORY.md` (new)

## Acceptance
1. Zero inline numeric timing literals remain in `combat_fx_layer.gd` and `wheel_view.gd`. A grep for `\* 0\.\d` and tween-duration literals returns nothing, except 0 and 1 identity cases.
2. Every moved timing is a `ui_motion.tres` entry. Fractions are stored as fractions of the base duration, so the computed duration equals the old expression exactly.
3. Each new id is in `REQUIRED_IDS`. A test fails if an id is missing from the `.tres`.
4. Each new id has a lab demo entry, and the lab opens headless without error.
5. Under reduce effects, the end state (final positions, alphas, visible flags) of every moved tween matches the pre-change capture. Record before/after values in the report.
6. With reduce effects off, each computed duration is within 1 ms of the old value, checked by a test on the inventory rows.
7. No new strings and no new numbers beyond the moved ones.

## Tests
- `tests/test_ui_motion_ids.gd` (extend if it exists, else new). Tier `fast`. Add to `tests/test_manifest.json`.
- Duration-equivalence test over the inventory rows. Tier `fast`.
- Reduce-effects end-state test using MotionSkip registration. Restore every Settings value changed. Bounded waits only.
- No test plan file exists. Use `QUICK=1` as in common.md.

## Not in scope
- `city_map_overlay` R5 lines (about 12 remain; F-RULE5 remainder).
- Retiming, easing changes, new animations, any core or rule change.
- Gamepad and text scales other than 1.0.
- Captures: only if a visual change appears. Expected none; say so in the report.

## Conflicts
- `wheel_view` and `combat_fx_layer` may be touched by N11 and N14. Rebase on main before the final commit.
- `ui_motion.tres` is shared: append entries only.
- Per REPLAN C.2, nothing else is shared with the `netrun_session` or `netrun_scene` rows.

## Report
End with the RESULT envelope from `docs/process/agent_rules/common.md` (round tag `MOTION-TIMINGS`, area `ui`).

Q: Should the inventory also cover timings in other combat views (e.g. `ram_bar`, HUD chips), or only these two files?
Q: Does the lab demo need one demo per id, or may related ids share one demo entry?

## Added 2026-10-19 (NA-26)
- `route_target_pulse`: CityMapOverlay must honor the motion switch (it is back in AWAITING_FIX). `CityMapOverlay.hover_out` and motion lab `_staying_node` are now dead: remove them.
