# E — COUNTDOWN + ALLOCATION, round 2 (current; replaces the SPEC.md rules where they differ)

## Rules (one function, `outcome()` in `tools/raid_concepts/concept_e2_countdown.py`)
- **Notch** = the strike on a node. The attackers causing it sit on the notch as silhouettes:

  | Node | Notch | Attackers |
  |---|---|---|
  | Home | 15 | Collector ×3 |
  | Firewall | 5 | Collector, passing |
  | Relay | 5 | Collector, passing |
  | Vault | 9 | Auditor ×3 |
  | Proxy | 30 | Enforcer ×3, Auditor passing |

- **Fill** = Firewall gun 3, turret 6, ICE 5, each crew-hour 2.
- **Shortfall** = notch − fill:

  | Shortfall | Result |
  |---|---|
  | 0 or less | HOLDS, untouched |
  | below integrity | SCUFFED, by the shortfall |
  | at least integrity | DOWN |
  | at least 2 × integrity | TAKEN |

  Home loses the shortfall; 0 = BREACHED.
- **Allocation is split** over the two HQ visits of the countdown, 3 crew-hours each, so the netrun in between counts.
- **Hard calls** are icon cards:
  - **Evacuate a node:** it is TAKEN, and half its install cost is refunded (Proxy +5).
  - **Go dark:** +1 netrun on the countdown, +4 Heat, +3 crew-hours.

## Presentation
- **The when.** A big top-centre dial (netruns left) and a hatched front at the map edge that moves in after each netrun.
- **Outcome tags** on every node are live from the warning onward.
- **Two plans compared:**
  - plan 1: everything into Proxy, 2 hours on home → home −11, nothing lost;
  - plan 2: shield home, evacuate Proxy → home 0, Proxy TAKEN with +5 refund.
- **The strike is watchable.** The front crosses the map node by node, one beat per node (5 beats, about 4 s each). On each
  beat the attackers slam the gauge and the shortfall lands as a number.
- **The aftermath** shows the stamp with loss icons, the patch cost, and the next strike at Heat 75.

## Rule changes (each a designer decision)
1. The raid is announced N netruns ahead.
2. Crew-hours and gauge fill replace reach and targeting.
3. The hard calls.
4. A node-by-node sweep replaces the step playout.
