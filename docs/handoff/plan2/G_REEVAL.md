# G1–G16 re-evaluation (2026-10-15, main @ 547fd746)

**Sources:**
- `docs/ART_REINTEGRATION_PLAN.md` l.224–239 and the order at l.482–483;
- `docs/G_REEVALUATION.md`, the prep sheet written at ecf6e16, now partly stale.

**Rulings so far:**
- Ruling 8 (2026-10-05): the G items are re-evaluated after the art integration.
- CP-002 D13: G10 and G13 close as done; G16 keeps only its per-card field.
- Designer go 2026-10-15: start the items that still apply.

No item has been approved as a mechanic yet. Everything below that changes rules still needs a ruling.

| ID | What | On main now | Class |
|---|---|---|---|
| G1 | Inner-ring redesign: the sub-needle Accelerator, a hangar, double status, AOE, blank starting segments, ×2 moving to Firmware | Only the look is built (round 45 ring, Twin Pointer). The rule is still the old Accelerator (`effect_interpreter.gd:114,170`). | STILL APPLIES · L · combat · ruling |
| G2 | Satellites: an overwrite rule, can't be nudged, damage when several drones share a slice, ×N stacks | GDD l.141 says satellites can be nudged; one satellite and one status per slot. | STILL APPLIES · M · combat · ruling |
| G3 | Parasite ring (partial third ring, a boss mechanic) | Nothing built. | ABSORBED → E-CONCEPT |
| G4 | New slice types and states, and what SANDBOX is for | 9 types and 4 statuses (`rc.gd`). | STILL APPLIES · M · ruling; overlaps E-CONCEPT |
| G5 | Slice tiers I–III, corporation tiers | No tier field; the Card upgrades pass is still queued. | STILL APPLIES · M · ruling |
| G6 | More Exploits (one per boss buff), per-type badges, Breach against a one-pointer boss, VIRUS at random | **VIRUS at random is done** (`RANDOM_NON_NULL`); the rest is not. | Rest STILL APPLIES · M · ruling; waits for the E-CONCEPT bosses |
| G7 | Rim gates | Nothing built; no design yet. | STILL APPLIES · M · ruling (keep or drop) |
| G8 | Distinct station bonuses for the four alternate classes | Wrecker's bonus is the same as Breaker's (×1.5). | STILL APPLIES · M · ruling |
| G9 | Raid: EXPOSED nodes, Heat-scaled waves, decoys, intel, threat vehicle types | None of it is built. | ABSORBED → E-CONCEPT (raids) |
| G10 | Raid zoom fits the network | `raid_zoom_fit.gd` | DONE |
| G11 | Netrun rules: any owned node to any unowned node; transit and HQ climb; TAKEN / DOWN nodes de-power their links | The launch rule is done. Transit and climb go to the route redesign. **De-power is missing.** | De-power STILL APPLIES · S · ruling |
| G12 | Per-corporation HQ mechanics and the Sync Strike finale | Static compounds; the HQ run is one node. | ABSORBED → route redesign (HQ map) + E-CONCEPT (finale) |
| G13 | HQ actions without the HQ room | HQ direction B | DONE |
| G14 | Shop: the slice wheel sells the top 3 (top one at 80); a shop nudge upgrade; recycle-bin removal; **confirm before a Firmware replaces a socketed chip** | The bin look is built; prices are flat (100 / 150); a socketed chip is overwritten with no confirm (`netrun_session.gd:572`). | The confirm is **startable** (no rule change). Prices and nudges need a ruling. |
| G15 | Rack "flash": upgrade or swap a slice | `_capture_rack` only banks. | STILL APPLIES · S–M · ruling (with G5) |
| G16 | Card type band WHEEL / HACK / SYSTEM | The band is derived from what the card does; there is no per-card field. | Effectively DONE; close it or add the field (ruling) |

## Startable now
1. **G14 confirm:** before a Firmware goes into an occupied socket, a confirm names the chip it destroys. This joins
   plan 2's C-SCREENS slice.
2. **Bookkeeping:** this file. Refresh `docs/G_REEVALUATION.md` to current main.
3. **E-CONCEPT input:** G3, G4 (the enemy side), G6 (boss buffs), G9 and the G12 finale go to the content design pass
   as candidate mechanics.

## Questions for the designer
1. **G11:** should a DOWN or TAKEN node stop counting as territory for launching runs, with its links de-powered (as
   the round 42 markers show)? Small.
2. **G1:** which parts of the inner-ring redesign? Does slice rearranging come before or after G1 / G2?
3. **G2:** should satellites become un-nudgeable (overturning GDD 2.7)? Should a new satellite overwrite an occupied
   slice? Do you want ×N status stacks, shared as one model with G1 and G4?
4. **G4:** which new slice types and states? Is SANDBOX "block one attack", "block the next status", or today's
   shield?
5. **G5 + G15:** should slice tiers be one pass with Card upgrades? What are tiers called, given T1–T4 means Site tiers
   today? Should a Rack offer the flash as a rewards-list row?
6. **G6:** should new Exploits wait for the E-CONCEPT bosses? Breach against a one-pointer boss: never offered, or
   the boss starts stunned?
7. **G8:** own station bonuses for the four alternate classes, or keep them?
8. **G14:** sell the top 3 slices with the top one at 80, instead of the flat 100 (GDD 11.2)? Add a shop-wheel nudge
   upgrade?
9. **G7:** keep rim gates, or drop them?
10. **G16:** close it, or add a per-card type field?
11. **G12:** wait for the route redesign and a playtest, and send the finale to E-CONCEPT?
