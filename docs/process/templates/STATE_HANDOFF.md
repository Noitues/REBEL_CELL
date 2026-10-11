# STATE — <ORCHESTRATOR | area> — <YYYY-MM-DD HH:MM local>

| | |
|---|---|
| Session | <id> (previous: <id>) |
| Branch / commit | <branch> @ <sha> (pushed: yes/no) |
| Context at handoff | <n> % of the window |
| Reason | threshold / designer pause / gate / end of wave |

## Current goal
<One paragraph: the milestone item (MILESTONES.md anchor) and its acceptance line verbatim.>

## Modified files delta (vs <base sha>)
<`git diff --stat <base>..HEAD` summarised in words, then one line per file that matters:>
- `path` — what changed and why (DECISIONS anchor if ruled)
Uncommitted: <none | list with "stage" / "never stage" (project.godot is the designer's)>

## Checks (sha they ran on)
- precommit: parse=<> tests=<> @ <sha>
- checks_fast: import=<> fast=<> smoke=<> validate=<> @ <sha>
- full suite: <n> tests, <n> failing (<time>) @ <sha> | not run since <sha>
- windowed: <bake_smoke / motion lab / capture> @ <sha> | n/a

## Open items
1. <what's left> — files: <paths> — next: `<command or brief>`
2. ...
Batches in flight: <name> <batch id> submitted <time> | none

## Decisions taken since the last STATE
- <ruling applied or default chosen> — DECISIONS "<entry title>"

## Questions pending (designer)
- CP-<nnn>.<k> <topic> — default in force: <value>

## Next three actions
1. `<exact command>` or Agent brief: <area>, footer at <path>
2. ...
3. ...

## Gotchas (new this session only)
- <one line each; standing ones live in memory and docs/process/agent_rules/common.md>

## Cost row (for the plan's measurement)
wave <tag>: agents <n>, test minutes <n>, batches <n> (<tokens in/out>, cache <pct>), handoffs <n>
