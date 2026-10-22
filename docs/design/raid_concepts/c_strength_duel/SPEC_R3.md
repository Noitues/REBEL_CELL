# C: Strength Duel (round 3)

Round 2's banner duel under the package, using `tools/raid_concepts/c3_rules.py`. Each threat has a fixed declared path.
Each node gets a banner reading ATK : DEF, where ATK is strikes × damage along the paths that reach it: 1 strike on
each node passed and 3 on the target.

## Bonuses
- FW gun +3.
- Turret +8 on its node.
- Sentry +6 on its node.
- Railgun +8 on the biggest banner within 2 hops.
- Crew +3 on its node and each neighbor.
- ICE cancels the biggest single strike at its node.
- Decoy sends the Collector to the decoy node instead of home.

## Outcome
loss = ATK − DEF.
- 0 → HOLDS.
- Less than integrity → SCUFFED.
- At least integrity → DOWN.
- At least twice integrity → TAKEN.

Clean = home loss 0 and nothing DOWN or TAKEN. Of 12,960 plans, 127 are clean.

## Plans
- Bare: home −15, PROXY TAKEN, patch 34.
- Railgun on HOME only: PROXY DOWN instead of TAKEN.
- **Plan 1** (ICE on PROXY, Decoy on RELAY, Railgun on HOME, crew on VAULT): **CLEAN**, patch 28.
- Plan 2 (Turret + ICE on PROXY, Railgun on HOME, crew on SAFE): home −12, patch 33.

## Playout
Hands-off: the duels run one by one, biggest first, home last.

## Fixed since round 2
- clean is computed, not hard-coded;
- SCUFFED has its own corner mark;
- multipliers are drawn glyphs.

Code: `concept_c3_duel.py`.
