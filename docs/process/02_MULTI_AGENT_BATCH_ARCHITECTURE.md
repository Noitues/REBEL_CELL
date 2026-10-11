# 02 — Multi-agent and Batch API architecture

Three execution lanes. The orchestrator decides the lane per task with the routing table in §2
and never does batch work interactively.

```
                 ┌────────────────────────────────────────────────────────────────┐
  designer ◄────►│ ORCHESTRATOR (interactive, this session)                       │
  (checkpoints,  │  plans, briefs, merges, gates, writes STATE.md, reads reports    │
   playtests)    └───┬──────────────────────┬──────────────────────┬──────────────┘
                     │ Agent tool            │ Agent tool            │ .jsonl files
                     ▼                       ▼                       ▼
           ┌──────────────────┐  ┌─────────────────────┐  ┌────────────────────────────┐
           │ FIX / PORT agents│  │ CLEANUP sub-agent    │  │ BATCH lane (Message Batches)│
           │ Opus/Sonnet,     │  │ Haiku, effort low,   │  │ Haiku/Sonnet, 50 % price,   │
           │ worktree each,   │  │ one diff in, one     │  │ no chat context, ≤ 24 h     │
           │ real-time        │  │ patch out            │  │ make → submit → ingest      │
           └──────────────────┘  └─────────────────────┘  └────────────────────────────┘
```

## 1. Lane rules: real-time vs batch

| Property | Real-time (Agent tool, interactive) | Batch (Message Batches API) |
|---|---|---|
| Needs Godot, a merge, a window, a capture, a designer answer | yes → real-time | never |
| Depends on the result of another step in the same hour | yes → real-time | no |
| Same instruction over many files, result is a patch or a report per file | avoid | **yes** |
| Judgement about look, feel, rules, or the GDD | real-time (Opus) | only `decisions_digest` |
| Price | full | 50 % of input and output; plus prompt-cache reads on the shared prefix |
| Latency | minutes | usually < 1 h, up to 24 h; results kept 29 days |
| Context cost to the orchestrator | the agent's report | one `INGEST_REPORT.md` |

Decision rule: **if it can be expressed as "for each file, do X, return a patch or a list", it is
batch.** If it needs the tree, a run, or a person, it is real-time. Batch results are applied on a
`batch/<name>` branch and go through the same hand-back checks as an agent branch.

## 2. Task routing table

| Task | Lane | Model / effort | Spec kind | Notes |
|---|---|---|---|---|
| `##` docstrings on public API | batch | Haiku 5.5 / low | `docstrings` | per file |
| Lint, dead code, typing, formatting, comment cleanup | batch (bulk) or cleanup sub-agent (one diff) | Haiku 5.5 / low | `cleanup` | doc 03 |
| Rule-compliance report over an area (the "horizontal" audit) | batch | Haiku 5.5 / low | `lint_report` | no patch; the auditor reads the digest |
| Player-facing text audit (literals, rules-English) | batch | Haiku 5.5 / low | `text_audit` | |
| Unit tests for new core classes | batch | Sonnet 5.5 / medium | `unit_tests` | the orchestrator adds manifest tiers and runs them |
| Mechanical refactor / rename across N files | batch | Haiku 5.5 (rename) or Sonnet 5.5 (refactor) | `rename`, `refactor` | the declaration is changed first, interactively |
| DECISIONS.md digest per milestone (for agent briefs) | batch | Sonnet 5.5 / medium | `decisions_digest` | |
| Port a screen to the art direction; fix a rule bug; anything with Godot | real-time | Opus 5.5 (visual/rules), Sonnet 5.5 (mechanical) | — | worktree agent |
| Merge, checks, push, gate, playtest list, checkpoints | real-time | orchestrator | — | never delegated |
| Visual review / approval | real-time | art-direction session, then designer | — | memory: art-pass-session-reviews-batches |

Model ids are the current ones (`claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`); the
`claude-3-5-sonnet-20241022` id in the task brief is retired. Haiku 5.5 and Sonnet 5.5 think by
default, so every batch line sets `output_config.effort` (low for mechanical work, medium for tests
and refactors); thinking tokens count against `max_tokens`, hence the per-kind defaults in
`tools/batch/make_batch.py`.

## 3. Real-time agents: brief shape and report shape

**Brief** (what the Agent prompt contains, in this order; nothing else):
1. `Read docs/process/agent_rules/<area>.md first.` (stable; one file per area: `combat`,
   `city`, `screens`, `rules`, `audit`.)
2. Footer, ≤ 12 lines: base sha, round tag (`ART-3 B6`), temp folder tag, the items verbatim
   (or the path to the batch brief), the files it owns, the hand-back command.
3. Slices on demand: the agent runs `python tools/batch/context_slice.py --deps <its files>`.

**Report** (the agent's final message; the orchestrator reads only this):
```
RESULT <round tag> <area>
status: DONE | HANDOFF | BLOCKED
commit: <sha> on <branch>
checks: precommit=<0/1> fast=<0/1> smoke=<0/1> validate=<0/1> (sha <sha>)
items: <n> done / <n> listed
- <item id>: done — <test name or capture path>
- <item id>: differs — <one line why>
notes: <≤ 5 lines: files touched outside the area, NEEDS lines, questions as Q:>
```

Agent cap and machine rules stay as in memory (one Godot window each, never `python -`, own
PIDs only, batch Godot launches, `run_windowed.py` for anything that draws). "Remote" isolation
runs locally here and counts toward the cap.

## 4. Batch API pipeline

### 4.1 Files

```
tools/batch/make_batch.py        spec.json ──► batches/<name>.jsonl + <name>.manifest.json
tools/batch/submit_batch.py      .jsonl ──► batch id (.batch_id) ──► <name>.results.jsonl
tools/batch/ingest_results.py    results ──► batches/<name>_out/{<id>.patch,<id>.notes.md,INGEST_REPORT.md} [+ commits on batch/<name>]
tools/batch/prompts/_common_rules.md   the cached system block (project rules, style, the RC envelope)
tools/batch/prompts/<kind>.md          the task block appended to it (docstrings, cleanup, lint_report, ...)
tools/batch/specs/*.json               example specs
tools/batch/context_slice.py           signatures / diff / deps for any file (also used by briefs)
```
`batches/` is a working folder (add to `.gitignore`; the `_out/INGEST_REPORT.md` of a batch that
changed code is copied next to its DECISIONS entry when it matters).

### 4.2 JSONL payload schema (one request per line)

```json
{"custom_id": "docstrings_core-003-campaign_rules",
 "params": {
   "model": "claude-haiku-5-5",
   "max_tokens": 8000,
   "system": [{"type": "text", "text": "<_common_rules.md + <kind>.md, byte-identical on every line>",
               "cache_control": {"type": "ephemeral"}}],
   "messages": [{"role": "user", "content": "<file path=...>...</file>\n<diff base=main>...</diff>\n<signatures class=...>...</signatures>\n<instructions>...</instructions>\nWork on <path> only. Answer in the RC envelope."}],
   "output_config": {"effort": "low"}}}
```
- `custom_id`: `<batch name>-<nnn>-<file stem>`, `[A-Za-z0-9_-]`, ≤ 64 chars, unique in the
  batch; the manifest maps it back to the file. Results come back in any order: **always key by
  `custom_id`**.
- Limits: 100 000 requests or 256 MB per batch. One file per request keeps every request under
  the model's context and makes a failed request cheap to retry.
- `max_tokens` is per kind (thinking counts). A result with `stop_reason: max_tokens` is marked
  `truncated` by the ingester and lands in the retry file with a note to raise it.
- The payload holds only what the request needs. Nothing about the machine, no paths outside the
  repo, no credentials.

### 4.3 Prompt caching across the batch

- The system prompt is **one block, byte-identical on every line**, with the breakpoint on it:
  the project rules + the task text (~1 k tokens; ~1.1 k with the test kind). Everything that
  varies (file, diff, deps, instructions) is in the user turn after the breakpoint.
- `make_batch.py` writes JSON with `sort_keys=True` so no line differs by key order.
- Caching inside a batch works when requests with the same prefix are processed close together;
  it is not guaranteed and the prefix must exceed the model's minimum cacheable length (model
  dependent). The ingest report prints `cache read: <n> (<pct>% of input)`: if it is 0 on a
  large batch, the prefix is too short for that model — move the per-kind text into the shared
  block or accept the uncached price (still 50 % off).
- Caches are model-scoped: a batch uses one model. Two kinds on two models are two batches.

### 4.4 Submitting

```bash
pip install anthropic              # once; credentials: ANTHROPIC_API_KEY or `ant auth login`
python tools/batch/make_batch.py tools/batch/specs/docstrings_core.json
python tools/batch/submit_batch.py batches/docstrings_core.jsonl          # prints the batch id; returns at once
python tools/batch/submit_batch.py --status msgbatch_...                  # later
python tools/batch/submit_batch.py --fetch msgbatch_... --out batches/docstrings_core.results.jsonl
```
`--wait` polls every 60 s and writes the results when the batch ends; the orchestrator does not
sit on it — submit, carry on, fetch at the next natural pause (a merge, a gate). The batch id is
saved next to the payload (`<name>.batch_id`) and in `STATE.md` under Open items.

### 4.5 Ingestion protocol (orchestrator)

1. `python tools/batch/ingest_results.py batches/<name>.results.jsonl` → read **only**
   `batches/<name>_out/INGEST_REPORT.md` (one row per request: status, `git apply --check`,
   cache, tokens, summary; then the notes). Never read the results file.
2. Rows `ok` + check `ok` → `--apply --branch batch/<name>`: each patch becomes one commit
   ("batch <name>: <summary>"). Rows `skip` are done. Rows `FAIL` on check: the file moved since
   the payload was built → rebuild those lines only (`make_batch` on a spec listing them) and
   resubmit; or hand the patch to the cleanup sub-agent with the current file.
3. Rows `errored` / `expired` / `truncated` → `<name>.retry.jsonl` is ready to submit; fix
   `invalid_request` lines first (the report says which).
4. `RC_NOTES` findings (`- path:line ...`, `- NEEDS: ...`, `- Q: ...`) → each becomes a line in
   the current slice's item list or a checkpoint question; nothing is dropped (memory:
   nothing-deferred).
5. The branch goes through the normal hand-back: `bash tools/precommit.sh --base main`, then a
   merge wave with `checks_fast.sh`, then the gate. New test files from `unit_tests` get their
   manifest tier before the checks (the integrity test enforces it).
6. STATE.md: the batch moves from Open items to Decisions taken with the report path, the token
   totals and the applied count (the cost row).

### 4.6 Failure handling

| Result | Cause | Action |
|---|---|---|
| `errored` / `invalid_request` | malformed line (bad model id, max_tokens, custom_id) | fix the line, resubmit the retry file |
| `errored` other | server side | resubmit unchanged |
| `expired` | batch ran past 24 h | resubmit unchanged |
| `refusal` stop reason | classifier declined (rare on code) | reword the user turn or do it interactively; never loop |
| `no-envelope` | the model ignored the format | the prompt is unclear for that file; do it interactively, fix the prompt file |
| marker drift (`<<<RC_NOTES>`, `_END` closers) | Sonnet on long outputs (seen on the first digest batch) | the ingester parses tolerantly and keeps the longer block; the rules block now spells out the six marker lines |
| many "ok / confirm / no finding" lines in a report | Haiku at low effort lists what passes | `tools/batch/lint_digest.py` drops them; the lint prompt says violations only; a report is a **lead list** until a Sonnet verify pass or an auditor confirms it |
| patch check FAIL | file changed after the payload was built, or the model paraphrased context lines | rebuild from the current file; if it repeats, the file is too large for one request — split by `<instructions>` |

## 5. Human-in-the-loop: checkpoints

Three classes, decided when the question appears:

| Class | When asked | Where |
|---|---|---|
| **BLOCKING** | nothing in the current wave can proceed under any default, or an action is destructive / outward-facing | one question, now, in chat, with the default proposed |
| **GATE** | everything else that needs the designer | collected in `docs/handoff/CHECKPOINT_PENDING.md`; asked as one batch at the next User-Ready Gate or milestone group end |
| **FYI** | a default the orchestrator may take (small tuning, presentation per the art bible, process) | logged in DECISIONS as a default; listed in the checkpoint batch under "defaults taken" for veto, not for an answer |

Checkpoint format (`docs/process/templates/CHECKPOINT.md`): numbered items, each with a one-line
context, lettered options with the **recommended one first and marked**, the default that applies
if unanswered, and what it blocks. The designer answers with a numbered list (`1A 2C 3: free text`),
which is how rulings have been given so far; the orchestrator logs each in DECISIONS with the
checkpoint id (`CP-007.3`) and updates the GDD line it supersedes.

Rules: at most one checkpoint batch per gate; ≤ 10 items (split by area otherwise); nothing
re-asked that DECISIONS already rules on (grep first); an unanswered item keeps its default and
reappears once, flagged "second ask", then becomes a logged default.

## 6. Sequence of a typical slice under this process

```
1. Orchestrator writes the brief footer; spawns fix agents (worktrees); submits any batch work
   the slice makes mechanical (docstrings/tests for new classes) in the same minute.
2. Agents work on slices; hand back RESULT blocks after `precommit.sh --base main`.
3. Orchestrator merges one branch at a time: checks_fast.sh, union-resolve as today.
4. Batch results fetched at the merge pause; ingested on batch/<name>; merged like an agent branch.
5. Gate: full suite once in isolation, smoke, validate, windowed checks for rendering; push gate.
6. Playtest list (doc 04) to the designer with the checkpoint batch; STATE.md updated; handoff if over 50 %.
7. Playtest feedback ingested → findings → next slice's items (nothing deferred).
```
