# M14 "Art direction v2" — retrospective            2026-10-12 · main @ 19ad76a3

Scope: M14 from its first commit `c4b7251b` (2026-10-05) to gate PT-001 (`873a362e`, 2026-10-12). Facts were
gathered from git and the docs (sources in brackets); the PT-001 gate report has this wave's short retrospective.

## 1. What happened
| | |
|---|---|
| Calendar | 7 days, 4 active: 10-05 (562 commits), 10-06 (189), 10-07…10-10 none (spend limit hit 10-06 ~17:10), 10-11 (83), 10-12 (21) |
| Volume | 855 commits on main, 252 merges, 120 `worktree-agent-*` branches; repo +190k / −12k lines (scripts +64.5k, tests +27.5k, docs +49.6k incl. 679 images) |
| Tests | manifest 123 → 208 scripts; 2207 tests, 0 failing on the single full-suite run at the gate (528 s, `-j 4`) |
| Look | ART-0…ART-12 ported; parity audit (136 gap ids) closed; 12q QA matrix: 44 findings, all fixed; art-pass APPROVED both close-out groups |
| Perf | medians inside 8 ms on the target PC, both tiers (HQ idle 5.94 / 6.69 ms, combat 5.14 / 4.93 ms) |
| Estimate | ruled "about 1.5–2.5 weeks", then "within days" (10-05): finished in 7 calendar days, 4 of them working |

## 2. What went well
1. **Throughput with a green end state.** The whole v2 look landed in four working days, and the one full-suite run was green
   the first time (DECISIONS "M14 gate (PT-001)").
2. **Review loops converged when batched.** Group 2, the first group reviewed as one comparison sheet, needed 7 → 4 → 3 polish
   items over 3 rounds. The close-out group was APPROVED first time. Under per-slice review in group 1, every slice came back
   (2–4 rounds each).
3. **Performance work paid off.** 12p and the PERF slice took HQ idle from ~9.5 ms to ~6 ms and wheels + FX from 12 ms to
   3.1 ms; the gate run confirmed both on a quiet machine.
4. **The process corrected itself in the open.** CP-001, the reading hook, the DECISIONS archive, the batch lane and the
   agent-routing hook were each logged with the problem they answer (docs/process/CHANGELOG.md).
5. **Recovery tooling worked.** STATE.md and the resume files let three different orchestrator sessions pick the work up;
   the three-way `.tres` merge stopped silent reverts of tunings.

## 3. What hurt
1. **Spend.** The monthly API limit was hit on 10-06 and stopped work for four days. The 10-12 diagnosis: every sub-agent
   ran on Opus high, and the orchestrator on Fable. Fixed by the routing hook and re-pinning (Sonnet medium for visual work).
2. **Uncommitted work lost three times.** Three dirty worktrees were force-removed (ART-6 3A, PERF, BIG-TEXT), the spend-limit
   stop lost BIG-TEXT round b, and the ACCESS agent died with 101 files staged (recovered only because the files were still on disk).
3. **Red main blocked parallel agents.** There were seven fix-the-reds rounds (FIX-REDS ×4, RED-TIP, RED-SWEEP, B4 fixing
   B2's red), about 1 h of agents blocked by the commit hook, a stale class cache (~15 min) and shared-shard-directory crashes.
4. **First-pass art quality.** Every slice in group 1 came back, and TITLE-01 took four iterations. Each round re-ran agents
   with capture loops, which is where most of the time and spend went.
5. **Plan churn.** The audit policy changed four times on 10-05, rolling audits were started and then killed, and 92
   worktrees filled the disk twice. Neither estimate held.

## 4. Root causes (the few that explain most of §3)
- **Too much in flight at once on 10-05.** About 9 agents ran in parallel against a main that was itself changing every few
  minutes (172 merges that day). That produced the reds, the disk filling, the blocked hooks and the spend.
- **No commit discipline for agents.** Work lived uncommitted in worktrees until the agent finished, so every interruption
  (spend limit, crash, force removal) lost it.
- **Review per slice instead of per group.** Group 1's per-slice loops cost far more rounds than group 2's single sheet.
- **Expensive defaults.** Model choice was left to each spawn, so everything ran on the most expensive models.

## 5. Changes proposed (for CP-002; each a default the designer can veto)
Already proposed at PT-001: D6 (precommit re-imports when a `class_name` changes), D7 (agents stop their own background
runs and run one precommit at a time), D8 (a fresh shard directory per test run). New:
- **D9 — WIP commits.** Agents commit WIP on their own branch at least every ~30 min, or before any long run, so an
  interruption never loses work. The commit message is marked `WIP`; the hand-back squashes or rewords it.
- **D10 — Main must be green before a wave starts.** The orchestrator runs the fast tier on main before spawning a
  wave, and fixes any red first (the PT-001 retro note, made a rule).
- **D11 — One comparison sheet per group is the only review unit.** This is ruling 9 of 10-11, extended to every art
  pass, including the R7 animation work.
- **D12 — Spend guard.** The gate report records agents × model × effort for the wave. A wave that would run more than 5
  agents at once, or any Opus agent, needs a line saying why in its brief (OPUS-BECAUSE already does part of this).

## 6. Cleanup still owed (housekeeping, no rulings needed)
- About 100 merged `worktree-agent-*` branches can be deleted (deleting them in bulk was blocked by the permission check
  this session; the designer can allow it or run the command).
- 116 pack-A QA contact sheets exist only on branch `qa12q`; merge or drop them.
- Two leftover directories under `.claude/worktrees/` (not registered worktrees) can be deleted.
