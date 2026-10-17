<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__botnet; status ok; tokens in 4035 cache-write 32585 cache-read 0 out 2104; cost $0.055. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: botnet

## 1. Current
"One free turret on the node for each raid" is a TriggeredEffectData on ON_RAID_START, type 18 (DEPLOY_DRONE) with amount 1, deploying `station_deploy_asset` (the turret). It is meaningful but not unique. Rigger heals, Ghost freezes and Breaker multiplies assets, so a free asset is "more of what the Armory already gives". The Rank multiplier has no stated effect on the amount (1 × 1.25 rounds to 1), so Ranks 0-2 are identical in practice. Both the swarm identity and the Rank scaling are weak.

## 2. Proposed: "Swarm Garrison"
**Raid terms.** The stationed Botnet seeds drones on the node. At the start of each raid, the node gets a Drone Swarm: N cheap decoy-turrets (the free asset, one per drone). Each swarm drone has 1 integrity and fires 1 damage at the first threat in range. A drone that is destroyed absorbs the hit instead of the node, so the swarm is a sacrificial buffer. After each wave, one lost drone regrows (the Botnet's drones "ride the whole netrun").

| Rank | Drones at raid start | Dmg per drone | Regrow per wave |
|---|---|---|---|
| 0 | 2 | 1 | 0 |
| 1 | 2 | 2 | 1 |
| 2 | 3 | 2 | 1 |
| 3 | 4 | 2 | 2 |

The swarm total is 2 / 4 / 6 / 8 damage per step against threats on the node and 1 integrity per drone as soft HP. The amounts are explicit per Rank, not a rounded multiplier, so every Rank is felt. This is a placeholder pending the raid sim. The comparison point is the Firewall Relay turret at 3 damage.

**Drone rules.**
- Drones are not assets, so they don't use Armory slots and don't count against the 6-asset cap.
- A threat on the node damages drones first (each hit kills one drone, with no overflow to the node) and only then the node's integrity.
- Excess damage on a kill is lost, so many drones means many hits absorbed. That is the swarm identity: it punishes multi-hit threats least and big single hits most (a big hit still only kills one drone).

**Non-raid.** When the node is idle between raids, the stationed Botnet contributes +1 Schematic per completed netrun by a *neighbouring* operative (scrap-farming). It is optional; drop it if it muddies the read. I recommend dropping it, so the bonus stays raid-only like the other classes.

**Grid view.** The node shows a cluster of small pips around its ring, one per drone, in the Botnet's colour. They dim as drones die during the playout and refill between waves. The preview shows the projected outcome (HOLDS / DOWN / TAKEN) with the swarm included, since resolution is deterministic. The tooltip reads "Swarm: 3 drones x 2 dmg, regrow 1/wave".

## 3. Family
Botnet is the base class. Its family stays "many small bodies".

| Class | Bonus | Relation |
|---|---|---|
| botnet | Swarm Garrison: 2/2/3/4 drones, regrow per wave | base |
| hivemind | Hive Garrison: fewer starting drones (1/1/2/2) that never leave: they are not lost at 0, but go dormant and revive at the next wave start. Damage per drone is the same as Botnet's | alternate: the bigger swarm that "never leaves the fight" becomes a permanent but slower presence |

Hivemind's drones are less of a buffer and more of a guaranteed damage source: they absorb the first hit each wave only, but the damage never drops to zero. That keeps the same cluster-of-pips read with a different uptime pattern. Hivemind in combat has a bigger swarm, so on the node it trades starting count for persistence.

## 4. Fit
- **Defense trio:** the drone buffer behaves like BLOCK-per-wave (it expires or regrows) rather than SHIELD (lingering) or SANDBOX (negating a whole attack). Nothing here duplicates Rigger's heal or Ghost's freeze.
- **Other 7 classes:** Breaker multiplies asset damage, Ghost/Phantom delay or evade, Rigger/Overclocker restore integrity or bank RAM, Botnet/Hivemind add bodies. The Breaker multiplier applies to *assets*, not drones, so there is no multiplicative stacking. Rigger regen heals the node, not drones. If all are stationed on one node, the combined effect is bounded by the soft-HP-only drones and by the cap that drones can't be shielded.
- **Dominance guard:** swarm drones attack only threats on their own node, so stacking several Botnets on separate nodes is linear, not exponential.

## 5. Data
- Replace `fx_station` (DEPLOY_DRONE, amount 1) with: ON_RAID_START → DEPLOY_DRONE amount N, using explicit Rank-keyed values in `RankRewardData` (**new field** `station_params`, a per-Rank dictionary) instead of relying on `station_bonus_multiplier`.
- Needs a raid-side "node drone" entity (integrity 1, damage, regrow-per-wave). That is **NEW: raid swarm drone**, size M (raid sim, resolution order, preview, grid pips). There is no N# for it; it belongs to the raid design pass.
- **Data-only fallback:** keep DEPLOY_DRONE as a turret asset, deploy 2/2/3/4 turrets at 1 integrity each, with no regrow and drones sharing the Armory cap. This works today with `amount` set per Rank by hand.

## 6. Q:
- Q: Should drones count toward the raid asset cap, or live in their own pool (proposed: own pool)?
- Q: Does hivemind's "dormant, revive each wave" read clearly enough in the grid preview, or should it simply have more drones with no regrow?
- Q: Is the non-raid Schematic trickle worth keeping for a distinct campaign-layer identity?
