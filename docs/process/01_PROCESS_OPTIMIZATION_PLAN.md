# 01 — Process optimization plan (waste, context budget, handoffs)

Written 2026-10-10 from the M14 / ANIM-R7 process as it ran (CLAUDE.md, TEST_SUITE.md, the
handoffs under `docs/handoff/`, the agent rule blocks, the memory notes). Status: **in force** since the
CP-001 rulings of 2026-10-11 (1A 2A 3A 4A; the designer added "never run ×3 tests"); the items marked
*(CLAUDE.md change)* are applied in CLAUDE.md.

## 1. What the process costs today, and where the waste is

| # | Observed practice (M14 / ANIM) | Cost | Replacement |
|---|---|---|---|
| W1 | Every fix agent runs the **full suite ×3** before hand-back (25 min each; 9–15 agents in parallel on one PC) | ~6 CPU-hours per batch wave, Godot windows contending, and each agent reads three logs into its context | Hand-back = `tools/precommit.sh --base main` (parse check + diff-selected tests, 1–3 min). The orchestrator runs the full suite **once per gate** in isolation; never ×3 (CP-001.2). |
| W2 | Agents told to "read CLAUDE.md, STYLE_GUIDE §5, ANIMATION_HANDOFF, TEST_SUITE, the DECISIONS entries..." and then `Read` whole files; DECISIONS.md is 11 406 lines | 40–80 k tokens of context per agent before any work | Agents get a **brief + slice**: the area's rules file (`docs/process/agent_rules/`) and `tools/batch/context_slice.py` output for their files. DECISIONS is read through its digest (batch task `decisions_digest`) or `grep -n` on a topic, never whole. |
| W3 | Rule block pasted verbatim into every agent prompt, re-edited per round (sha, round tag, temp folder) | Every prompt a unique prefix: no cache reuse, and drift between agents | One stable rules file per area under `docs/process/agent_rules/`, referenced by path. The variable part (sha, items, temp folder) is a 10-line footer. |
| W4 | Hourly progress report with a Gantt widget, re-derived from agent messages | 5–15 k tokens per hour of orchestrator context, no durable record | `docs/handoff/STATE.md` updated at each merge (one table). A report is produced only at a gate or on request, from that file. |
| W5 | "Every rule gets a test" applied to everything: view glue, lab demos, getters, `to_dict` round trips; 1 233+ tests, 193 scripts, 10–12 min single-process | Suite time grows with every batch; agents write tests to satisfy the rule, not to catch bugs | *(CLAUDE.md change)* Rule 6 scoped to **rule-bearing code**: `scripts/core/`, `scripts/state/`, resolvers, save, RNG, content validation, layout rules at 1.0/1.6/2.0, reduce-effects = end state. View glue and tooling are covered by one integration flow test per screen and by the Human Playtest gate (doc 04). |
| W6 | Three-auditor rounds (vertical / horizontal / naive) repeated per fix round, each auditor re-reading the codebase | 3 large sessions per round, 7 rounds in ANIM | One audit per milestone (already ruled for M14). The **horizontal** half (rule compliance over every file) moves to the Batch API (`lint_report`, `text_audit`) at 50 % price with no chat context. Vertical and naive stay interactive but read the batch report first. |
| W7 | Full logs piped into context (`tail -n 40`, `cat gut.log`, capture frames read one by one) | The largest single context sink after W2 | Hard reading rules in §3: logs are grepped for `=` lines, `FAIL`, `ERROR` only; captures as contact sheets (`tools/visual_qa/contact_sheet.py`), never frame by frame. |
| W8 | 92 worktrees left under `.claude/worktrees/` (~100 MB each), `%TEMP%` runs left behind | Disk filled twice; a full disk lost a whole test run | Hand-back deletes the agent's `%TEMP%` folder; the orchestrator removes merged worktrees at the gate (`git worktree remove`). `run_tests.py` already warns under 5 GB. |
| W9 | Handoffs written by hand at the end, when the context was already full (M14_RESUME: 90 lines written at 90 %+) | Late handoffs lose the reasoning; the next session re-derives it | A **State Handoff Document** at a hard threshold (§4), from a template, in under 5 minutes. |
| W10 | Designer questions asked one at a time as they come up, or buried in reports | Interrupt loops; some questions answered twice, some never | Checkpoint batches (doc 02 §5): BLOCKING questions only when nothing else can proceed; everything else waits for the next gate. |

Expected effect (measured against the ANIM-R6 round, where numbers exist): per fix wave, test
CPU time 6 h → under 1 h; agent context at start 60 k → under 15 k tokens; orchestrator context
per wave about halved (no log dumps, no hourly Gantt). Verification: `docs/handoff/STATE.md`
keeps a "cost" row per wave (test minutes, agent count, handoffs) so the next plan has data.

## 2. Testing policy (diff-based between gates, full at gates)

```
edit ──► tools/precommit.sh (staged)         seconds–minutes   parse check, smoke/validate only if touched,
                                                                 diff-selected tests (fast tier if nothing maps)
hand-back ──► tools/precommit.sh --base main 1–3 min           same, over the whole branch
merge wave ──► checks_fast.sh                 ~2 min            import + fast tier + smoke + validate (unchanged)
GATE ──► python tools/run_tests.py -j 4       ~5 min, isolated   the full suite, ONCE; ×3 only after a red run
         + smoke + validate + windowed bake/motion checks where rendering changed
```

- **Diff-based selection** is `tools/select_tests.py` (TEST_SUITE.md gets a row): changed
  test → itself; changed script → every test naming its `class_name`, basename or `res://`
  path; `scripts/core` / `scripts/state` → plus the rule guards and the integrity check;
  `content/` → plus the content guards; a change to a hub class that fans out to more than half
  the scripts → the fast tier instead (the full suite catches the rest at the gate). Nothing
  mapped → the fast tier, never "no tests".
- **Pre-commit** is `tools/precommit.sh` (install: `printf 'bash tools/precommit.sh\n' > .git/hooks/pre-commit`).
  Its parse step uses Godot's `--check-only` per changed file (seconds), so a typo never reaches a
  test run.
- **Gates** are the only place the full suite runs: a User-Ready Gate (doc 04), the end of a
  milestone group, and before any push of `main` (the push gate stays as it is: parse the
  `import=0 fast=0 smoke=0 validate=0` lines from a file, never chain a push after a grep).
- **Flakiness** is handled by the runner's rerun-alone (`ORDER-DEPENDENT` / `fails alone too`),
  never by running the suite three times (CP-001.2): investigate the rerun-alone verdict, fix, run once more.
- *(CLAUDE.md change)* Rule 6 wording proposed: "Every **rule** gets a test (core, state,
  resolvers, save, RNG, content, layout at 1.0/1.6/2.0, reduce effects = end state). View glue,
  labs and tools are covered by one flow test per screen and by the playtest gate; don't write
  tests for getters, setters or data round trips without logic."
- *(CLAUDE.md change)* "Run all three before declaring any task done, with the full suite"
  stays true **for a gate**. Between gates, done = pre-commit green + hand-back checks green.

## 3. Context budgeting rules (every session, every agent)

**Reading rules** (these are what keep a session under budget; break one and the handoff
comes sooner):
1. Never `cat` or `Read` a test log, a Godot log, a capture folder or DECISIONS.md whole.
   Logs: `grep -E "^(import|fast|smoke|validate|tests|parse)=|FAIL|ERROR|ORDER-DEPENDENT|ALONE"`.
   The runner's last three lines are the verdict. DECISIONS: `grep -n "<topic>"` then `sed -n a,bp`.
2. Source files: `tools/batch/context_slice.py <file>` first (signatures + `##` docs, ~5 % of
   the file); `--full` only for the file being edited; `--diff main` for review.
3. Captures: contact sheet or one crop per finding, read once, then deleted.
4. Agent reports come back in the fixed `RESULT` block (doc 02 §3), ≤ 40 lines. An agent that
   returns more is asked for the block, not read.
5. No re-reading: a file read in this session and not changed since is not read again.

**Budgets** (tokens of the session's context window, as the harness shows them):

| Role | Starting brief | Working ceiling | Hard handoff |
|---|---|---|---|
| Orchestrator (this session) | CLAUDE.md + memory index + `docs/handoff/STATE.md` + doc 00 (≈ 12 k) | 60 % | **65 %**, or the start of a merge wave if the previous wave ended above 50 % |
| Fix / port agent (worktree) | area rules file + brief footer + slices (≤ 15 k) | 55 % | 60 %: write the State Handoff, commit, report `HANDOFF` status; the orchestrator respawns from the branch |
| Auditor (vertical / naive) | rules + the batch lint report + screen list (≤ 10 k) | 60 % | 65 % |
| Cleanup sub-agent (doc 03) | the diff or file only | n/a (single pass) | never: one file, one answer |
| Batch worker (API) | cached rules (~1 k) + one file | n/a | n/a |

The threshold is checked: at every merge, at every agent report, and before any step that reads
more than 2 k tokens (a full-suite verdict, a review sheet). Reaching it is not a failure; it is
the trigger for §4. The orchestrator also hands off **before** a gate's full-suite run when above
50 %, so the gate verdict lands in a fresh session.

## 4. Handoff protocol (State Handoff Document)

Trigger: a budget line in §3, the designer saying pause, a planned interruption, or the end of a
gate. The `/handoff` skill may draft it; the file is `docs/handoff/STATE.md`
(template `docs/process/templates/STATE_HANDOFF.md`), committed on the branch the work is on.

```
# STATE — <area or ORCHESTRATOR> — <ISO date time local>
Session: <id>   Branch/commit: <branch> @ <sha> (pushed: yes/no)   Context at handoff: <n> %
## Current goal            one paragraph: the milestone item and its acceptance line
## Modified files delta    `git diff --stat <base>..HEAD` summarised + uncommitted files, one line each: path — what and why
## Checks                  last precommit / checks_fast / full-suite verdicts with the sha they ran on
## Open items              numbered, each with: what's left, the file(s), the next command
## Decisions taken         rulings applied or defaults chosen since the last STATE, with the DECISIONS anchor
## Questions pending       the CHECKPOINT ids waiting for the designer, and the default in force meanwhile
## Next three actions      exact commands or agent briefs, in order
## Gotchas                 only new ones (the standing ones live in memory and agent_rules)
```

Rules: ≤ 120 lines; no narrative history (DECISIONS and git hold it); every path exists; every
claim about checks names the sha. A new session starts with: CLAUDE.md, the memory index,
`docs/process/00_README.md`, `docs/handoff/STATE.md`, then only what STATE's next action needs.
Old handoffs (`M14_RESUME.md`, `.claude/HANDOFF.md`) stay as history; STATE.md is the live one.

## 5. Sub-agent context slices (what an agent receives, and nothing more)

| Agent kind | Receives | Never receives |
|---|---|---|
| Fix / port (visual or rules) | its area rules file; the brief footer (items, sha, temp tag); `context_slice.py --deps` of its files; the concept image paths for its screens | the full tree, DECISIONS.md whole, other areas' briefs, old audit reports |
| Cleanup (doc 03) | one `git diff` or one file | anything else; it does not inspect unaffected modules |
| Auditor | the batch `lint_report` digest, the screen list with capture commands, the acceptance lines | the implementation briefs |
| Batch worker | the cached rules block + one file (+ its diff, + referenced signatures when the spec says `deps`) | the tree |

Briefs name files by path and let the agent slice them; they do not inline source.
