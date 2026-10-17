<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__breaker; status ok; tokens in 4224 cache-write 0 cache-read 32585 out 2078; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: breaker

## 1. Current
"The node's assets +50% damage" (a DEAL_DAMAGE effect with multiplier 1.5, trigger 12 = ON_RAID_START). It is meaningful (Breaker = damage) but generic: it buffs every asset on the node uniformly, so it is a flat stat bump with no decisions, and its Rank scaling reaches 2.0× with no cost. It overlaps with any future "turret damage" bonus.

## 2. Proposed: BREAKER "Breach Charge" (burst, not a flat buff)
**Raid terms:** The node has a **charge** that stores the Breaker's first strike. The first time a threat enters the node (or starts a step on it), the node's assets fire a **Breach volley**: each asset on the node (including the built-in turret) deals its normal damage **plus a one-time bonus, as Pierce** (ignores threat armor/ICE-Lock shielding). It re-arms after **N steps** with no threat on the node (cooldown), so it rewards a node placed at a chokepoint where threats arrive in sequence, not a node that is constantly occupied.

| Rank | Bonus damage per asset (Pierce, one volley) | Re-arm (steps empty) | Node also |
|---|---|---|---|
| 0 | +4 | 4 | n/a |
| 1 | +6 | 3 | n/a |
| 2 | +8 | 3 | the volley also hits the **next** threat in range (2 targets) |
| 3 | +10 | 2 | 2 targets, and a threat killed by the volley pays 1 Schematic |

Total damage is deterministic. The raid preview already shows projected outcomes (GDD 7.1); the volley is a visible line "BREACH +6 PIERCE" in the node's projection.

**Non-raid terms:** while stationed, the Breaker's **Compiler-style kick**: netruns launched from the adjacent Sites start with the first Overflow slice Pierce-tagged for the first combat only (Rank 2+). Optional; cut this if the designer wants raid-only. Default: **raid-only**, to keep one clean identity.

**Reading on the grid:** the node shows a small red "charge" pip (a vinyl sticker, ART_BIBLE style) that is full when armed and greyed with a countdown number while recharging. The hover card lists "BREACH VOLLEY +N PIERCE · re-arm N". The defense-asset ring on the node flashes once when it fires in the playout.

## 3. Family
| Class | Bonus | Relation |
|---|---|---|
| **Breaker** (base) | **Breach Charge:** one burst volley with Pierce on first contact, re-arms when empty | The opening-strike specialist |
| **Wrecker** (alt) | **Wrecking Ball:** same trigger, but the volley deals **splash**: the bonus hits every threat on the node and 1 adjacent hop, and the bonus is smaller per target. Re-arm is 1 step longer at every Rank | Trades precision for a heavier, wider hit (mirrors "trade spin control for heavier Perfect") |

Wrecker numbers: Rank 0-3 bonus +3 / +5 / +7 / +9 per asset to all threats in 1 hop; re-arm 5 / 4 / 4 / 3. Same-family feel: both are burst-on-contact; one is single/double-target pierce, the other is area.

## 4. Fit
- **Defense trio:** the Breaker's bonus is offence-only. It does not give BLOCK/SHIELD/SANDBOX to the node, leaving Rigger's regen (a "node SHIELD-like" sustain), Ghost's hold (delay) and Phantom (SANDBOX-like dodge) their lanes. Pierce here is the asset-side analogue of the combat rule (ignores BLOCK/SHIELD, not SANDBOX): it ignores threat armor but not a threat's decoy bodyguard or an ICE Lock.
- **Other classes:** Botnet = free turret per raid (adds a body), Ghost = delay, Rigger = repair, Breaker = first-contact burst. No overlap. Phantom, Overclocker and Hivemind keep their own identities (dodge/delay variant, RAM-economy, swarm).
- **Dominant stacking:** Breach Charge is per node and re-arms only when the node is empty, so stacking Breakers on different nodes gives multiple bursts but not sustained DPS. Stacking two on one node is blocked (one stationed operative per Safehouse slot, and a node's bonus doesn't stack with a same-class one). It never helps against a continuous stream, so it doesn't make Ghost's delay unnecessary; delay plus burst is the intended combo, not a dominant one.

## 5. Data
- Trigger: ON_RAID_START arms the charge; firing needs a new **"on threat enters node"** trigger and a **re-arm cooldown** state on the node.
- EffectData: DEAL_DAMAGE with `pierce = true` (raid-side), `amount` per Rank via `station_bonus_multiplier` or per-rank values, `targets_count` (1/2), `rearm_steps`.
- Not a data-only change: **NEW: raid node-trigger hooks (on_threat_enter, cooldown state, pierce for asset damage)**, size M. The raid sim is deterministic, so it needs only the node's cooldown in its state; the preview projection must include the volley.
- Data-only fallback: keep ON_RAID_START and apply "+X Pierce damage to the first asset shot at each threat", approximated as a flat Pierce modifier on node assets (a single multiplier plus a pierce flag), size S.

## 6. Q:
1. Should the Rank 3 Schematic payout be allowed, or does it break the Schematics sink (R4 ultimatum) economy?
2. Pierce on asset damage: does it also bypass a threat's own ICE-Lock hold, or only armor and shield?
3. Should the raid-only identity stay, or does the designer want a netrun-side perk from stationing (the optional Rank 2+ kick)?
