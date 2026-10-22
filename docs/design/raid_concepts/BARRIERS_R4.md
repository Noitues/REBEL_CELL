# Round 4: the critic-R3 barriers, challenged

The user's direction (2026-10-22) is to challenge any barrier to a high critic score. Every row below is a **designer
decision**. None of it is in `scripts/`. Measurements come from `tools/raid_concepts/rule_metrics_r4.py` and
`payout_r4.py`, which build on the round-3 package (fixed routes, home not a corridor, weakest tie, ICE blocks, 3-of-5
draft).

| # | Barrier (critic R3) | Round-4 answer | Measured / shown |
|---|---|---|---|
| 1 | D27: a clean defense gains +5 Heat, pulling the next raid closer | **Raids do not move Heat.** The reward is Schematics only. | G4 aftermath: "51 = 51" |
| 2 | D27: any damage pays nothing, so a better losing plan earns nothing more | **Graded payout:** +4 salvage per threat killed, +6 if CLEAN. Each plan shows **net = payout − patch**. | The best plan in each draft now spreads from +10 to −6. Top three: +10 clean, +9 clean, +4 not clean. |
| 3 | SCUFFED counts as clean, so the patch can exceed the payout | Clean keeps its meaning (home untouched, nothing DOWN or TAKEN), but the stamp carries the net, so a costly clean shows a red net. A TAKEN node also costs its full install (it was free before). | `net_box` on the stamp |
| 4 | D26: 20–40 s step-locked playout, but only 4 steps | **Pace by beat:** about 1 s per shot or hit, plus a 2 s kill-cam per kill, capped at 40 s. The plan-1 raid is 9 beats, 15 s. A replay is offered afterwards (watch only). | G4 resolution: beat track and clock |
| 5 | D28: the verdict is only CELL HOLDS / BREACHED | **Three tiers: CLEAN / HOLDS / BREACHED**, each stamped with its net. Node marks are unchanged (DOWN, TAKEN, plus SCUFFED). | G4 aftermath |
| 6 | Cobalt routes are dim on navy | Keep cobalt (the ruling stands), and add a **white core line**. | every G4 route |
| 7 | Cascade damage is drawn nowhere | **Cut the cascade** (`no_cascade`). It changes no clean plan: 4.83 % clean before and after, cheapest clean per draft identical. It only produced undrawn damage. | rule_metrics_r4 |
| 8 | Crew ×1.5 is hidden | No rule change. Placed pieces print their **effective** number, with a chevron badge on the crew's node. | G4 planning, forecast |
| 9 | Turret, Sentry and Railgun are all crosshairs | Three silhouettes: crosshair, twin barrels, long beam. Art-pass owns the final icons. | G4 cards, plan rows |
| 10 | Content scale is brute-forceable | Tested a conditional threat: the Auditor **hunts the node holding the most pieces**. It barely changes anything (clean 4.83 > 4.57 %, the same cheapest plans), so it is **dropped**. Depth comes instead from #2 and #13. A real conditional threat is open: see below. | rule_metrics_r4 |
| 11 | The draft is blind | Each card previews its **best single placement** against this raid ("nodes lost 2, struck, 1"). | G4 draft |
| 12 | C7: the raid always lands on return, so timing is never a decision | The dial counts **netruns**, with a hex inside it, the same unit as the netrun map. Making timing a decision is still open (see below). | G4 netrun, warning |
| 13 | (new) Depth across raids | Plans now differ in what they **leave for the next raid**. Plan 1 (net +10) scuffs RELAY, so the next raid loses 3. Plan 2 (net +9) leaves RELAY untouched, so the next raid loses 2. Each plan row shows a "next raid" line. | G4 forecast, next raid |

Two further items came from the same R3 list:
- **The countdown unit.** The netrun map and HQ use the same unit, so the "map nodes vs netruns" confusion is gone.
- **The raid record.** One shield per raid survived, with a teal check when it was clean, kept on the campaign map.

## Still open (designer decisions, not yet tried)
- **A conditional threat that changes placement.** The first try (most pieces) was inert, because the cheap clean plans
  already kill it. Content already has stronger candidates, with no new mechanic needed:
  - the mirror threats (`informant`, `loyalist`, `purger`: "replaced by mirrors of your assets"), which make the draft
    shape the raid;
  - the link sealers (`customs_agent`, `signal_jammer`, `tow_truck`), which change routes mid-raid. These conflict with
    fixed routes unless the seal is drawn at the warning.

  These are the round-5 candidates if decision depth stays below 8.
- **Timing as a choice.** For example, return early to face the raid before a 4th threat joins at the next Heat tier,
  or run one more netrun for loot.
