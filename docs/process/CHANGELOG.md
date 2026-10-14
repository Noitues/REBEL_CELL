# Process changelog

One line per accepted process change, newest first: date, gate or checkpoint that proposed it,
what changed, why (the retrospective row that justified it). The process docs are edited in the
same commit; nothing changes silently.

- 2026-10-13 · designer, chat ("batch calls or lower sub-agents for pre-commit?") · precommit costs no tokens, so the saving is fewer runs and no Sonnet agent idling on them: `QUICK=1` mode in `tools/precommit.sh` (parse + only the changed test scripts) for agent commits and hand-backs; the orchestrator runs ONE full diff-selected precommit per wave batch as a background shell (no model in the loop); failures triage to the batch lane (expectation / lint fixes) or a Sonnet agent only when Godot iteration is needed.
- 2026-10-13 · designer, chat ("strayed from the batch API and lower models") · **Route cheapest first** before every spawn: (1) Batch API lane, Haiku low by default, for patch-shaped work that needs no Godot run to produce (test expectation updates, renames, string / literal sweeps, docstrings, lint fixes, unit-test drafts, text audits); the orchestrator applies the patches and runs one precommit; (2) code-cleanup (Haiku) for one diff; (3) fix-mechanical / fix-visual (Sonnet medium) only when Godot runs, captures or iteration are needed; (4) Opus only with OPUS-BECAUSE. Every brief / report names the lane; gate reports count batch tokens (D12).
- 2026-10-13 · designer, chat ("can we run anything in parallel / precommit every time / faster") · (1) merges within a wave are committed without the per-merge hook (`--no-verify`); after the last slice of the wave merges, ONE `bash tools/precommit.sh --base <pre-wave sha>` runs on the combined tree before any push (both sides already passed precommit on their branches); (2) precommit runs tests at `-j 4` by default (`JOBS`; measured 7.3 min vs 10-15 at -j 2); (3) the next step starts while the previous group is in art review. Gates unchanged (full suite once in isolation).
- 2026-10-12 · designer, chat · Claude playtesters (doc 05): black-box `playtester` agent (Sonnet medium, pinned), `tools/playtest/blackbox.py` / `roll_testers.py` / `aggregate.py`, persona × focus × quirk roster, `guard_playtester.py` hook, feedback template `CLAUDE_PLAYTEST_FEEDBACK.md`.
- 2026-10-12 · designer ("more efficiency") · Agent routing hook (`tools/hooks/guard_agents.py`): pinned
  types only, Opus needs `OPUS-BECAUSE:`, no Fable sub-agents, effort capped at the pin, briefs ≤ 4 000
  chars, ≤ 5 agent worktrees; fix-visual re-pinned to Sonnet medium, fix-rules / auditor to Opus medium;
  project default model Opus 5.5 at effort medium · why: the M14 session spawned every sub-agent on Opus
  high from the generic type and ran the orchestrator on Fable; usage climbed with no batch work.

- 2026-10-11 · designer, chat · Retrospective + replan block added to every gate report
  (`templates/GATE_REPORT.md`, doc 04 §5, doc 01 §6); light replan at ordinary gates, full at
  milestone completion or after a second failed gate · why: the process had no step that forced a
  comparison between waves or announced the next milestone.
- 2026-10-11 · CP-001 follow-ups · reading-rule hook, pinned agent models and effort, DECISIONS
  archived by month, hourly report retired, worktrees cleaned, art reviews per group.
- 2026-10-11 · CP-001 · rule 6 scoped to rule-bearing code; full suite once per gate, never ×3;
  Batch API lane on; playtest gates per group.
- 2026-10-10 · process redesign · docs/process 00–04, diff-based checks, batch lane, cleanup
  sub-agent, STATE handoffs, checkpoint batches, playtest protocol.
