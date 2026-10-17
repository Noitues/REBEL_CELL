<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__rigger; status ok; tokens in 4036 cache-write 0 cache-read 32585 out 2204; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: rigger

1. **Current.** The node regains 5 integrity at ON_RAID_START... actually trigger 12 = ON_RAID_START in the enum (index 12), amount 5, HEAL on SELF. This is a flat heal that doesn't match the description ("after each wave and when the raid ends"). It is meaningful for Rigger's "sustain" identity, but it is not unique: a plain heal is generic, it ignores the RAM identity, and it ignores Rank except through the multiplier.

2. **Proposed station bonus: "Load Balancer" (the node banks a RAM-like charge and spends it to absorb damage).**

*Raid terms.* The stationed node has a **Buffer**: a pool of integrity that sits above the node's integrity and takes damage first. It refills between waves and carries over when unspent, which is the "runs hot on RAM / carry-over" idea (RAM carries over, max 12).
- At raid start the Buffer is B points (it counts as BLOCK-like and is not repaired by anything else).
- After each wave step 30 resolves (raid step ticks: "each wave"), the node gains +R Buffer, capped at C. Unspent Buffer carries into the next wave. Buffer left when the raid ends converts to integrity at 1:1 (the "Perfect pays for the next move" payoff), up to the node's missing integrity.
- Damage hits Buffer first. A node with Buffer > 0 cannot go DOWN on that step; the 50 % spread to neighbours is computed only from damage that exceeds Buffer.

| Rank | Start Buffer B | Gain per wave R | Cap C | End-of-raid conversion |
|---|---|---|---|---|
| 0 | 4 | 3 | 12 | 1:1 |
| 1 | 5 | 4 | 15 | 1:1 |
| 2 | 6 | 5 | 18 | 1:1 |
| 3 | 8 | 6 | 24 | 1:1 |

(These are ×1.0 / 1.25 / 1.5 / 2.0 on a base of 4 / 3 / 12 rounded, so the existing `station_bonus_multiplier` can drive them.)

*Non-raid terms.* A Rigger stationed at a node gives the node's next netrun launch +1 starting RAM (`starting_ram` +1 at Rank 0-1, +2 at Rank 2-3) for operatives who launch from adjacent Compiler Racks. Hmm: to stay unique and avoid overlap with Compiler Rack, I cut this. **No non-raid effect**; the bonus is raid-only, which keeps scope small.

*Reading on the grid.* The node shows a thin blue "charge bar" arc around its ring, segmented in 3-point pips. Pips fill during setup (showing projected start Buffer) and the raid playout drains them first. The setup preview shows the Buffer after every projected wave, consistent with the exact-projected-outcome rule. All numbers are deterministic, with no RNG.

3. **Family / alternates.**

| Class | Role | Station bonus |
|---|---|---|
| **Rigger** (base) | Charge that absorbs | Buffer: start B, +R per wave, end converts to integrity |
| **Overclocker** (alt: banks raw RAM instead of free nudges) | Same Buffer, spent aggressively | **Overcharge:** same pool, but the Buffer *starts at 0* and gains double R (2×); at the final wave any Buffer above half of cap is dealt as damage to threats on the node (1 per 2 Buffer). Higher variance: weaker early, a burst finish. Ranks use the same scaling. |

Overclocker keeps the "banks RAM" theme: it saves charge for a payoff instead of spending free nudges, while Rigger is steady. Both share the same pip bar, with the Overclocker's pips shown in orange to read as a variant.

4. **Fit with the trio and the other classes.**
- Buffer behaves like **SHIELD** (lingering, capped, carried across waves), not BLOCK (it doesn't expire) and not SANDBOX (it doesn't negate a whole attack). Its cap keeps it a lingering shield with its own cap, in line with `shield_cap` 15 at Rank 2-ish.
- Other classes: Breaker boosts asset damage (+50 %), Ghost delays threats (FREEZE), Botnet deploys a free turret per raid. None overlap: Rigger is the only pure defensive-pool bonus.
- Dominance check: if all are stationed, Buffer stacks only per node, not across nodes, so nothing compounds. One Rigger per node (the Safehouse slot is single). Rigger Buffer + Ghost delay is the strongest synergy (delay gives more waves to refill), which is acceptable; Botnet's turret kills threats faster, so Rigger's gain per wave matters less there. Cap C at Rank 3 (24) is below a typical node's 30 integrity, so it can't make a node unkillable on its own.

5. **Data.**
- Today: `TriggeredEffectData` (trigger ON_RAID_START, HEAL amount 5).
- Proposed needs: a new node-side pool plus two triggers (per-wave step and raid end).
  - Fields: `station_pool_start`, `station_pool_gain_per_wave`, `station_pool_cap`, `convert_on_end` (bool), and for the Overclocker `overflow_damage_ratio`.
  - **NEW: raid node Buffer** (a field on the raid-state node plus damage ordering in raid resolution, a pip bar in the grid view, preview support). Size **M**. It is not among N1-N20 (those cover combat and run layer only).
- **Data-only fallback:** keep the HEAL effect but add a wave trigger (needs a per-wave hook, small code) and raise it to a table of 5 / 6 / 8 / 10 per wave via the multiplier. This is size **S** and works today if the per-wave trigger exists; otherwise the current ON_RAID_START heal stays.

6. **Q:**
- Q: Should Buffer end-of-raid conversion be capped at missing integrity (proposed), or may it overheal the node?
- Q: Is "one operative per Safehouse slot" firm? Dual Riggers on adjacent nodes would double-stack the pool, so should I add an adjacency cap?
- Q: Is a per-wave trigger acceptable in raid resolution, or should the bonus resolve only at raid start and end?
