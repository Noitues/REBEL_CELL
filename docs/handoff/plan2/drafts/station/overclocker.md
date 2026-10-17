<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__overclocker; status ok; tokens in 3992 cache-write 0 cache-read 32585 out 2261; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: overclocker

## 1. Current
The Overclocker has the Rigger's bonus, copied verbatim: HEAL 5 on ON_RAID_START (trigger 12, 5 integrity, Rank-scaled). Its text says "after each wave and when the raid ends", but the data only fires at raid start. It is not unique, and it has nothing to do with "banks raw RAM instead of free nudges".

## 2. Proposed station bonus: "Capacitor"
**Idea:** The Rigger's node repairs itself. The Overclocker's node *stores power* and spends it as a burst on the first big hit. Rigger = steady upkeep, Overclocker = banked surge. Both are the same kind of support: node-integrity sustain that only works on the node itself.

**Raid terms:**
- The node holds a **Charge** meter (cap 12, like RAM). It gains +2 Charge per raid step in which no threat is on the node, and +1 per threat arrival on the node.
- When a threat deals damage to the node, the node spends Charge to absorb damage 1:1 (a flat buffer, like a raid-scale SHIELD). The Charge refills only through the gain rules above, so it is not a heal.
- **Overclock discharge:** if the Charge is full (cap) when a wave starts, the node's assets fire at ×1.25 damage for that wave and the Charge resets to half. This is the "overclock" part and the reason to hold the Charge.

**Non-raid terms:** Between runs, a stationed Overclocker gives Compiler-style value: netruns launched from the adjacent node start with +1 RAM (a 7-RAM opening). Rank scales it. This is the "raw RAM" identity and it pays off outside raids.

**Numbers per Rank** (station_bonus_multiplier 1.0 / 1.25 / 1.5 / 2.0):

| Rank | Charge cap | Idle gain / step | Arrival gain | Discharge asset dmg | Start RAM bonus |
|---|---|---|---|---|---|
| 0 | 12 | +2 | +1 | ×1.25 | +1 |
| 1 | 15 | +2 | +1 | ×1.31 | +1 |
| 2 | 18 | +3 | +2 | ×1.38 | +2 |
| 3 | 24 | +4 | +2 | ×1.5 | +2 |

(Cap, gains and the Start RAM bonus are rounded from base × multiplier. The discharge bonus is 25 % × the multiplier, so ×1.25, ×1.31, ×1.38, ×1.50.)

Raid resolution is deterministic and the Charge follows fixed rules, so the setup-phase projection (HOLDS / DOWN / TAKEN) includes it exactly.

**Grid view:** a small segmented bar (battery pips) under the node's integrity bar, using the RAM colour. A full bar glows and pulses slowly. The hover card reads "Charge 8/12 · full = overclock wave".

## 3. Family
The Overclocker is the Rigger's alternate. Where the Rigger's node *repairs* between hits, the Overclocker's node *banks* power and releases it as a buffer and a damage surge. Both are node sustain, differently timed.

| Class | Station bonus | Role |
|---|---|---|
| Rigger | Repair: +5 integrity per wave and at raid end | Steady upkeep |
| **Overclocker** | Capacitor (above) | Banked buffer plus surge |

Other families, for non-overlap (one line each, not exhaustive): Botnet free turret per raid; Hivemind a persistent swarm of cheap decoys; Breaker +assets damage; Wrecker burst damage on the first hit only; Ghost threats held 1 step; Phantom a chance-free dodge, i.e. the first threat entering is rerouted.

## 4. Defense trio and the other classes
- **BLOCK/SHIELD/SANDBOX mapping:** Capacitor is a raid-level SHIELD (lingers, capped by Charge, refills slowly). It is not BLOCK (it does not expire each turn) and not SANDBOX (it negates nothing whole).
- **Not the same as the Rigger:** the Rigger heals integrity (recovery); the Overclocker prevents damage (a buffer) and boosts assets. They differ by timing, so they do not feel identical.
- **Stacking:** the Charge is per node, so a stationed Overclocker affects only its own node. Assets only get the surge when the Charge is full, which forces a trade-off (spend vs bank). With Breaker (+assets damage on the same node), the surge multiplies additively (+25 % and +50 % = ×1.75), not multiplicatively. With the Rigger on an adjacent node there is no stacking (one operative per Safehouse slot).
- **Cap on dominance:** the buffer absorbs at most the Charge cap per raid on a node (24 at Rank 3, below the ~30 integrity of a Firewall Relay), so it cannot make a node unkillable.

## 5. Data
- **Raid half:** needs a node-level meter and two raid-step hooks. This is a raid-resolver feature, not on the N1–N20 list. NEW: *node charge meter*, size M (raid resolver, node state, grid-view pip UI). Fallback, data-only: an ON_RAID_START effect that GAIN_SHIELDs the node for 6 / 8 / 9 / 12 (new EffectTarget CAMPAIGN-node use with amount_mode FLAT, N1 helps). This is a one-shot buffer with no surge, and it works through the existing trigger 12 with a different effect type.
- **Non-raid half:** a netrun-start RAM bonus from a stationed operative. It needs a trigger on the adjacent node, comparable to the Compiler Rack's bonus. If Compiler Rack's start-bonus plumbing can read operative station data it is S; otherwise NEW: *station start bonus*, size S. The fallback is to drop it.
- Fields: TriggeredEffectData (trigger ON_RAID_START plus the new step triggers), EffectData amount, and station_bonus_multiplier rank scaling, which already exists.

## 6. Q:
- Q: Should Charge persist between raids (a long-term bank) or reset at raid end? I assumed it resets, to keep raids independent.
- Q: Is the netrun-start +RAM acceptable next to Compiler Rack (a bonus card or Firmware), or does it overlap?
- Q: Is the per-step raid hook a worthwhile new system for one class, or should we take the data-only fallback (a one-shot node SHIELD)?
