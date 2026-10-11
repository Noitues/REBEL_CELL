# REBEL_CELL development process (2026-10-10 redesign)

Read this page, then `docs/handoff/STATE.md`. The four documents below are the process; CLAUDE.md
stays the rulebook for the code.

| Doc | What it decides | Read when |
|---|---|---|
| [01 Process optimization plan](01_PROCESS_OPTIMIZATION_PLAN.md) | waste cuts, diff-based testing, context budgets, the State Handoff Document | every session start; before any test run |
| [02 Multi-agent and Batch API architecture](02_MULTI_AGENT_BATCH_ARCHITECTURE.md) | real-time vs batch routing, briefs and reports, the `.jsonl` pipeline, ingestion, checkpoints | before spawning an agent or starting bulk work |
| [03 Code Review & Cleanup sub-agent](03_CODE_CLEANUP_AGENT.md) | the Haiku cleanup agent, its prompt, how to apply its patch | at every hand-back with a diff over ~50 lines |
| [04 Playtest protocol](04_PLAYTEST_PROTOCOL.md) | User-Ready Gates, the Human Playtest Task List, the feedback schema and its ingestion | at every gate |

## Tooling added with the process

| Tool | Does |
|---|---|
| `tools/precommit.sh [--base main]` | parse check of changed `.gd`, smoke/validate only when touched, diff-selected tests |
| `tools/select_tests.py` | maps a diff to test scripts and runs them (`--list` to see why) |
| `tools/run_tests.py --select A --select B` | the runner's `--select` is now repeatable |
| `tools/batch/context_slice.py` | signatures / diff / dependency signatures of files, for briefs and batch payloads |
| `tools/batch/make_batch.py spec.json` | spec → `batches/<name>.jsonl` (+ manifest), cached shared system prompt |
| `tools/batch/submit_batch.py` | submit / status / fetch results (`pip install anthropic`) |
| `tools/batch/ingest_results.py` | results → patches, `git apply --check`, `INGEST_REPORT.md`, retry file, optional commits on `batch/<name>` |
| `tools/playtest/make_playtest.py` | a prefilled Human Playtest Task List for a gate |
| `.claude/agents/code-cleanup.md` | the cleanup sub-agent (Haiku, effort low, no tools) |
| `docs/process/agent_rules/*.md` | stable per-area rules files that briefs reference instead of pasting |
| `docs/process/templates/` | STATE_HANDOFF, CHECKPOINT, PLAYTEST, GATE_REPORT (verdict, retrospective, replan) |
| `docs/process/CHANGELOG.md` | every accepted process change, one line, newest first |
| `docs/handoff/STATE.md`, `docs/handoff/CHECKPOINT_PENDING.md` | the live handoff and the pending designer questions |

## The loop in one screen

```
brief (rules file + footer) ──► agents in worktrees ──► RESULT block ──► precommit --base main
                │                                                            │
                └─► batch .jsonl (docstrings / tests / lint / rename) ──► INGEST_REPORT ─┘
                                                                             ▼
                                   merge wave: checks_fast.sh, one branch at a time
                                                                             ▼
                        GATE: full suite once (isolated) + smoke + validate + windowed checks + push gate
                                                                             ▼
          Gate report (retrospective → replan) + playtest list PT-nnn + checkpoint CP-nnn ──► designer ──► feedback ingested
                                                                             ▼
                                   STATE.md updated; handoff if context > 50 %; next slice
```

Standing machine rules (memory: godot-runtime-on-this-machine) still apply everywhere: never
`python -`, never pipe Godot output, windowed runs only via `tools/run_windowed.py` from a
worktree, kill only own PIDs, import after merging class_names.
