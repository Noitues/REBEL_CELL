# Process changelog

One line per accepted process change, newest first: date, gate or checkpoint that proposed it,
what changed, why (the retrospective row that justified it). The process docs are edited in the
same commit; nothing changes silently.

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
