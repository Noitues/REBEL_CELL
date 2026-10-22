# G: Merged Telegraph (round 3)

**Base:** A's map telegraph, plus B's reach rings and next-raid frame, F's per-threat path rows, E's countdown on the
netrun map and D's per-threat strip. It runs under the RULES_PROPOSAL package (every item there is a **designer
decision**).

## Loop
1. **Netrun map.** The raid is announced while you play: a dial counts the map nodes left until home (C7: it always
   lands on the return). The cause is shown as Heat 51 > 50.
2. **Warning at HQ.** Each threat's fixed route is drawn end to end in cobalt (R1). Home is never a corridor (R2), and
   ties go through the weaker node (R3). Path rows per threat and outcome tags show the raid as it stands.
3. **Draft.** Take 3 of the 5 Armory pieces (R5).
4. **Planning.** Drag pieces onto nodes. Reach rings, a what-if count of nodes lost, dashed red cascade spills (C3) and
   a per-step strip for the selected threat all update live.
5. **Forecast.** Plan rows compare home loss, nodes lost, the CLEAN check and the patch price before you commit (C8).
6. **Resolution.** A hands-off autoplay of about 20–40 s with numbered shots (C6). Speed and skip are the only controls.
7. **Aftermath.** The verdict stamp (CELL HOLDS / BREACHED, D28) with loss icons, the CLEAN payout, and each scuffed node
   with its patch price (C2: 1 per point).
8. **Next raid.** An unpatched scuffed node becomes the weakest, and the next route bends toward it (R3 × C2).

## Rules shown (one each)
- **Clean:** home untouched and no node DOWN or TAKEN (C1). Clean gains Heat (D27).
- **ICE:** a held threat neither moves nor strikes (R4).
- **Price:** home loss + scuffed points + DOWN at half the install cost.

## Numbers (from sim.py under the package)

| Plan | Pieces | Result | Patch |
|---|---|---|---|
| Bare | none | home −5; VAULT and PROXY TAKEN | 13 |
| Railgun on RELAY | Railgun | home −5; PROXY TAKEN | 27 |
| **Plan 1** | Turret + Railgun on RELAY, ICE on PROXY, crew on RELAY | **CLEAN** | **8** |
| Plan 2 | Turret on RELAY, ICE + Decoy on FW, crew on RELAY | CLEAN | 38 |

In the next raid, if RELAY is left unpatched at 10 it draws the Enforcer: 3 nodes lost, against 2 if it is patched.

Frames: `r3/mockups` (8 moments), `r3/scrambled`. Code: `tools/raid_concepts/concept_g3_merged.py`.
