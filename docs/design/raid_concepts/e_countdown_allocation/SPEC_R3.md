# E: Countdown + Allocation (round 3)

Round 2's gauges under the package (`concept_e3_countdown.py`).

## The countdown
- The dial counts the netruns left: 2, then 1.
- There are two HQ visits.
- Each visit gives 3 crew-hours, at +2 fill each.

## Fixed routes set the notches
The cobalt line on each node's gauge is the strike that node will take:
- Collector C1 > RELAY > VAULT > HOME (VAULT is weaker than FW, R3);
- Auditor > VAULT;
- Enforcer > PROXY.

## Fill
The fill is the node's defense. Drafted pieces, 3 of 5:
- Turret 6.
- Sentry 6.
- ICE 5.
- Railgun 8 on the biggest shortfall within 2 hops.
- Decoy moves the Collector's home notch onto the decoy node.

## Outcome
shortfall = notch − fill.
- 0 or less → HOLDS.
- Less than integrity → SCUFFED.
- At least integrity → DOWN.
- At least twice integrity → TAKEN.

Clean as in C1. Of 60,480 plans, 1,864 are clean (3.1 %).

## Plans
- Bare: home −15, PROXY TAKEN, patch 34.
- **Plan 1** (ICE, Sentry and Railgun on HOME; crew-hours PROXY 4, HOME 2): **CLEAN**, patch 33. The Railgun backs PROXY,
  2 hops out.
- Plan 2 (ICE on RELAY, Decoy on PROXY, Railgun on FW; crew-hours PROXY 3, VAULT 3): PROXY is given up (TAKEN), patch 0.
  That is the sacrifice trade: no Heat, a netrun to reclaim, and a new entry point.

## Playout
Hands-off: a front crosses the map node by node, and each node is one beat.

## Fixed since round 2
- no letter multipliers or kill marks;
- no hard-call cards (the draft replaces them).

Code: `concept_e3_countdown.py`.
