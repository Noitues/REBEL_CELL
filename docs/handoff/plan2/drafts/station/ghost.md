<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__ghost; status ok; tokens in 4090 cache-write 0 cache-read 32585 out 2121; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: ghost

## 1. Current
FREEZE amount 1 on ON_RAID_START (trigger 12 is ON_RAID_START): threats entering the node are held 1 step, scaled 1 / 1 / 2 / 2 steps by Rank. It is unique among the classes and fits the Ghost, but it is a plain delay with no counterplay and no readable tie to the Ghost's "strip defenses / slip resistance" identity. It is also redundant with the ICE Lock asset. Rank 0 and Rank 1 are identical.

## 2. Proposed station bonus: "Slip the Lock" (working name)
**Concept:** the Ghost does not delay threats. It strips their defenses and stops their routing from working on the stationed node. In raid terms, a threat that enters this node has its defensive stats stripped once.

**Raid effect (trigger: threat enters the node, deterministic, once per threat per node):**
- The threat loses its **shield/armor-equivalent** (a flat chunk of integrity-damage reduction) and its **node-damage bonus** (Heat- or Raid-strength-scaled output) for as long as it stays on this node.
- Strength per Rank, as a percent of the threat's current damage-per-step against the node, with a cap on the number of threats affected per wave:

| Rank | Threat damage on this node | Threats affected per wave | Entry delay |
|---|---|---|---|
| 0 | −20 % | 1 | 0 |
| 1 | −25 % | 2 | 0 |
| 2 | −30 % | 2 | 1 step (first affected threat only) |
| 3 | −40 % | 3 | 1 step (first affected threat only) |

The old multiplier 1.0 / 1.25 / 1.5 / 2.0 is replaced by these explicit rows. Rank scaling comes from the threshold table, not from multiplying a percent.

**Why the cap matters:** it makes the bonus a "mark the biggest threats" decision. Targeting is by HIGHEST_DAMAGE, so the order is deterministic and the setup phase can show exactly which threats are affected.

**Non-raid effect:** a stationed Ghost makes the node "quiet". On the node's netrun launch (Compiler-style bonus), the first Heat gained from a **Router** combat on a netrun launched next to it is reduced by 1 at Rank 2+. This is small, flavorful ("ghosting") and optional.

**Grid view read:** a thin pale-ring "veil" on the node. Affected incoming threats show a small struck-through damage number in the setup-phase preview (e.g. "6 → 4"). The Rank is shown as 1–3 pips. The node tooltip reads: "Ghost: threats here deal −25 %, first 2 threats."

## 3. Family

| Class | Role | Station bonus |
|---|---|---|
| **ghost** (base) | Strip | Weakens the damage of the first N threats on the node (above) |
| **phantom** (alt: dodges instead of slipping resistance) | Evade | **Phase-out:** the node negates the **first hit it would take each raid step-wave entirely** (the SANDBOX analogue). Rank 0: once per raid; Rank 1: once; Rank 2: twice; Rank 3: 3 times. It also forces that threat to skip the damage tick but still occupy the node. |

**Relation:** the phantom shares the Ghost's "don't fight the threat, undermine it" philosophy. The Ghost scales damage down on several threats, while the Phantom fully cancels a few hits. The Ghost is steady and the Phantom is spiky. Both tell the same story: this node is hard to pin down.

## 4. Fit with the defense trio and other classes
- **Ghost = BLOCK-like** (temporary, partial reduction, per wave). **Phantom = SANDBOX-like** (a whole negation). **Rigger** (node regains integrity) stays the SHIELD/heal analogue, and it feeds Overclocker. Botnet = offense (turret), Breaker = offense (+asset damage).
- No duplicates: the Ghost reduces the damage of threats, the Rigger heals integrity, the Botnet adds turret fire, the Breaker amplifies assets, and the Phantom cancels hits.
- **Stacking:** the effect applies per node and per threat. A threat's damage reduction from several Ghost nodes does not compound, because the reduction is taken from a threat's base damage only once per threat (highest value wins). A Ghost and a Phantom on the same node, if the node allows it, still gives only one station bonus per node. Breaker + Ghost is the strongest pairing at neighbouring nodes. That is fine, since it needs two Rank 3 operatives.

## 5. Data
The current data is `TriggeredEffectData(trigger=ON_RAID_START, FREEZE amount 1)`.
- **New fields needed:** a threat-entry trigger and an effect on a threat rather than on a wheel. The raid layer is a graph auto-battle, not combat, so none of N1–N20 covers this.
- **NEW: raid station hook** (small–medium): an `ON_THREAT_ENTER_NODE` trigger plus a `MODIFY_THREAT` effect (`damage_pct`, `max_targets`, `delay_steps`, `target_order = HIGHEST_DAMAGE`).
- **Rank rows:** a per-rank table on `RankRewardData` (e.g. `station_params` array), replacing the single `station_bonus_multiplier`.
- **Data-only fallback:** keep FREEZE and use per-rank amounts of 1 / 1 / 2 / 2 (what exists today), with the strip part dropped. That is poor, but it can ship now.
- The raid resolver is deterministic and sorts targets by damage then by id, so the preview equals the result.

## 6. Q:
- Q: Should the damage reduction also apply to threats **passing through** the node, or only to threats whose destination is the node?
- Q: Should the Phantom's negation apply per raid or per wave, given that R4 ultimatum waves add a second wave?
- Q: Is the optional non-raid Heat reduction too close to the Proxy Relay node (−1 Heat per netrun), and should it be dropped?
