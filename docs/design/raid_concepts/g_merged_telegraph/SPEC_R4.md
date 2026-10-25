# G: Merged Telegraph (round 4)

Round 3's G with the barriers challenged (see `../BARRIERS_R4.md`; every change is a **designer decision**). Its frames
are in `r4/`; the code is `tools/raid_concepts/concept_g4_merged.py`. Every number comes from `sim.py`, run with the
package plus `no_cascade`.

## Loop
1. **Netrun map.** The dial shows 2 netruns left, with a netrun hex inside it. The raid size for each Heat tier sits
   above the Heat bar. The raid record is kept on the campaign map.
2. **Warning.** Fixed cobalt routes with a white core, drawn end to end. Every tag has a drawn cause (there is no
   cascade). Row 0 shows the bare raid: net −36.
3. **Draft, 3 of 5.** Each card previews its best single placement: nodes lost, from 2.
4. **Planning.** Reach rings, the effective number on each placed piece, the crew chevron, and a what-if chip
   (lost 2 > 1, net −36 > −27).
5. **Forecast.** Three plan rows, each showing: the pieces, the clean check, net, home, nodes lost, the scuffed nodes,
   and the next raid's losses.

   | Plan | Pieces | Result | Net | Next raid lost |
   |---|---|---|---|---|
   | 1 | Turret + Railgun on RELAY (crew), ICE on PROXY | CLEAN, RELAY and PROXY scuffed | **+10** | 3 |
   | 2 | ICE on RELAY, Sentry + Railgun on PROXY (crew) | CLEAN, PROXY scuffed | **+9** | 2 |
   | 3 | Turret + Sentry + Railgun on RELAY (crew) | PROXY DOWN | +4 | — |

6. **Resolution.** Zero input. Pacing is one beat (about 1 s) per shot or hit, plus a 2 s kill-cam per kill. Plan 1 runs
   9 beats, 15 s. Shots are numbered, and the kill-cam shows the +4 salvage.
7. **Aftermath.** The CLEAN tier stamp with its net box: 3 kills × 4, +6 clean, −8 patch = **+10**. Heat stays 51.
   Each scuffed node is listed with its patch price, and the record gains a clean shield.
8. **Next raid (Heat 76) after plan 1, unpatched.** Scuffed RELAY draws the Enforcer: 3 lost. The inset shows the raid
   after plan 2: 2 lost.

## Payout and prices
- Salvage is 4 per kill; the clean bonus is 6.
- Patch: home and SCUFFED cost 1 per point, DOWN costs half the install, and TAKEN costs the full install.
