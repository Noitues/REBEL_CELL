# G2: the hybrid "Infected Tide" (C's board and paths + D's deck infection) and the blind critic's fixes

**Decision (2026-10-25, from G1 plus a blind critic):**

| Design | Blind critic | Note |
|---|---|---|
| D Carrier Deck | 35 | Best Fit (9) and C (8). Its 3×3 lattice breaks the designer's path rule |
| C Bloom Tide | 33 | Best N (a visible front), but the front is decorative: never decisive, and the late dose is unused |
| B Three Wards | 32 | |
| A Contagion Sweep | 30 | Broken |

P-target is the strongest path lever: least locked at PLAN, most relevance.

**So G2 builds one hybrid and compares it against G1's C-target and D-lattice rows.** Extend
tools/raid_concepts/sweep_g1.py with new variants. Keep the old variants reproducible.

## H: the Infected Tide (main variant)
- **Board:** the real Solace graph, with raid lines on paths from the Genome Core to HOME (the designer's rule), using
  P-target: the candidates are the paths through the most owned Sites. Street hunter.
- **The infection lives in the defense deck (from D):**
  - Each Site lost (TAKEN) adds an INFECTED card tied to that Site. It replaces the plain wound; the score cost stays.
  - INFECTED cards are dead draws in raid hands.
  - In a netrun, each INFECTED card drawn costs 2 bank (abstraction, as in D).
- **Spread (critic fix 3):** at each raid, the infection spreads by +1 INFECTED card only if a Site was lost since the
  last raid, and only if no DOSE is spent.
- **Doses:** every 3rd netrun banks one DOSE card. Spending one at DECAY removes 1 INFECTED card, or blocks the spread.
- **Visible front (from C):**
  - The "front" is derived, not a separate timer: the Sites tied to INFECTED cards plus their TAKEN neighbors.
  - Record its size for the board view.
  - The bloom-front campaign timer of C is dropped (G1: never decisive).
- **Second route chosen after the response (critic fix 1, also backlog R15):**
  - Sealed B is no longer fixed at leg generation. After the response, the corp picks B from the two remaining
    candidates by a rule the player can read: it prefers the route with the most owned, unblocked Sites.
  - Its preference is telegraphed at REVEAL A as "B leans route X".
  - A response that moves or places a sentry, or a JAM, can flip that preference.
  - The forecast shows the lean.
  - The planner evaluates responses against the corp's actual pick.
- **Lose:** HOME 0 (BREACHED), or CITY LOST when INFECTED cards outnumber healthy cards.
- **Win proxy (critic fix 3):** 3 exploits held, plus a PURGE: one raid survived with 0 INFECTED cards while holding the
  3 exploit Sites. Report both the win rate and the purge rate.
- **Show the infection change on forecast rows:** compute per outcome the INFECTED cards it would add, and include
  that in the planner score.
- **Keep from G1:** PATCH HOME at between (+1 pip for 8 bank). Tune it so that the 24-netrun skilled loss is at most
  15 %. If 24 netruns needs it, add escalating raid tiers.

## Variants to run (12 and 24 netruns; 200 campaigns per claim policy per length; skilled vs careless)
| Variant | Description |
|---|---|
| H | as above |
| H-noB | H, but sealed B stays fixed at generation (isolates fix 1) |
| H-nospread | H, but INFECTED is added only on TAKEN, with no spread |
| C-target and D-lattice | rerun unchanged, for reference |

## Metrics
- All G1 metrics, plus:
  - **b_flip_rate:** how often the response changed the corp's B pick;
  - **response_decides,** which the lab measured at 0.53 (the target);
  - **infected_per_campaign**, the purge rate and the city-lost rate.
- **Targets:** skilled loss ≤ 15 % and careless loss ≥ 50 % at both lengths; locked_at_plan ≤ 0.5;
  response_decides ≥ 0.4.

## Outputs
- **Code:** the new variants in sweep_g1.py, with seeded replay `--check` passing.
- **docs/design/raid_concepts/G2_RESULTS.md:**
  - the table;
  - the assumed numbers;
  - a blind rule sheet for H, at most 25 lines, player-facing and without concept names;
  - your read.
- **Do not touch:** scripts/, content/, GDD.md or DECISIONS.md. No commits.
