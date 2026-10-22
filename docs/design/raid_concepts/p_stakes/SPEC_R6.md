# P: Stakes (round 6)

**What will you give up?** Code: `tools/raid_concepts/concept_p6_stakes.py`; the measurement is `pareto_harness.py`.
Every rule is a **designer decision**.

## Rules
- **Every node has a job, drawn on it:**

  | Node | Job |
  |---|---|
  | Vault | +3 Schematics per netrun |
  | Relay | one more branch on each netrun map |
  | Safehouse | where the crew stations (lost: no crew next raid) |
  | Firewall | home's built-in gun (lost: no gun next raid) |
  | Proxy | intel: while it holds, the next raid is telegraphed one netrun earlier |

  A DOWN or TAKEN node loses its job until it is repaired or reclaimed.
- **Survivors rejoin.** Threats that survive the raid fall back to their corp site and join the next raid, so kills
  deny reinforcements.
- **The forecast shows the front.** It does not fold outcomes into one score. It shows the plans that no other plan
  beats on every count at once: home, each job, survivors, patch. Each card shows:
  - the pieces;
  - the jobs it gives up (struck);
  - who comes back;
  - the patch.
- **Draft and combat** are the round-5 package (3 of 5, crew). Execution is hands-off.

## Measured depth
On 10 seeded raids, the front holds 4.7 plans on average, with 3.9 distinct "what you give up" sets. 60 % of raids
have 3 or more such sets.

## Raid shown (scenario 7)
The roster: Collector from C1; Bailiff and Enforcer from C2. Its front has 8 plans. Four are shown:

| Plan | Gives up | Survivors | Patch |
|---|---|---|---|
| 1 | nothing | 0 | 19 |
| 2 | Proxy (intel) | 0 | 10 |
| 3 | Safehouse + Proxy | 0 | 0 |
| 4 | Vault (income) | 2 return | 14 |

Plan 2 is the one played.

## Frames
1. Warning with the jobs.
2. Planning.
3. The front.
4. Resolution.
5. Aftermath (jobs lost, who falls back).
6. Next raid: the dial starts one netrun later because the Proxy fell. An inset shows plan 4's survivors.
