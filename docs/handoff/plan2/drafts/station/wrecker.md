<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__wrecker; status ok; tokens in 3990 cache-write 0 cache-read 32585 out 2111; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: wrecker

## 1. Current
Wrecker's station bonus is a copy of the Breaker's: a DEAL_DAMAGE effect with multiplier 1.5 on trigger 12 (ON_RAID_START). It is neither unique nor meaningful. It has no distinct target, and its 1.5 is a literal that duplicates the rank multiplier. The Breaker's own bonus ("node's assets +50% damage") is the only version that makes sense.

## 2. Proposed station bonus: BREAKPOINT (Wrecker)
**Idea:** the Breaker makes assets hit harder all the time. The Wrecker wants one heavy blow, like its heavier Perfect. The Wrecker's node stores up its Perfect-sized hit and releases it on the first threat that arrives, which fits a Breaker alternate that trades control for a bigger single payoff.

**Raid terms:**
- **Trigger:** the first threat to enter the stationed node each wave (ON_RAID_START arms it, and it re-arms at the start of each later wave).
- **Effect:** the node deals one Wrecker Strike to that threat, ignoring its ICE Lock hold and any block. This is a flat integrity hit to the threat, separate from asset fire. Ignoring block/shield is the pierce rule from GDD 2.7.
- **Numbers:** damage = base 8 × station_bonus_multiplier.

| Rank | Multiplier | Strike damage | Waves armed |
|---|---|---|---|
| 0 | 1.0 | 8 | 1st wave only |
| 1 | 1.25 | 10 | 1st wave only |
| 2 | 1.5 | 12 | each wave |
| 3 | 2.0 | 16 | each wave |

- **Why "first wave only" at low rank:** it keeps the bonus modest early. It becomes sustained at Rank 2, matching Rank 2's Hub upgrade.
- **Determinism:** the target is the first threat in the node's arrival order, with ties broken by threat id. There is no randomness, so the setup-phase preview shows the exact result (GDD 7.1).

**Non-raid terms:** during a netrun launched from this node, the Wrecker has no station effect. The bonus is raid-only, like the Breaker's.

**Grid view:** the node shows a small cracked-hammer chip with the strike number ("8"). The chip is lit while the strike is armed and dims after it fires. The setup-phase projection draws a short line from the node to the incoming threat's entry edge, and the chip tooltip shows "Strike 8, first threat per wave."

## 3. Family
The Breaker is the base, and the Wrecker is its alternate. It keeps the Breaker's idea of "stationed operative boosts node offense" but spends it as one large burst on the first arrival, where the Breaker gives a steady damage boost to every asset shot. That mirrors the class difference: the Breaker spins freely and hits twice on a Perfect, while the Wrecker has less control and a heavier single Perfect.

| Class | Bonus | Rank 0 → 3 |
|---|---|---|
| Breaker (base) | Assets on the node +50% damage (all shots) | 1.0 → 2.0 × the +50% |
| Wrecker (alt) | Breakpoint: pierce strike on the first threat per wave | 8 → 16 |

Other families: the Ghost/Phantom, Rigger/Overclocker and Botnet/Hivemind bonuses are decided in their own passes. The Wrecker and the Breaker share only the "offense" lane and never the same effect.

## 4. Fit
- **Defense trio:** BLOCK, SHIELD and SANDBOX are player combat defenses and don't apply to raids. The Wrecker strike pierces a threat's block and shield, which is the only overlap. It does not bypass a SANDBOX-like negation, because threats have none. That keeps it consistent with R13, where pierce leaves SANDBOX untouched.
- **Versus the other classes:**
  - Ghost holds threats (delay).
  - Rigger repairs integrity (sustain).
  - Botnet adds a free turret (more assets).
  - Breaker multiplies asset damage.
  - Wrecker gives a single armed burst.
- No two share an effect.
- **Stacking:** a one-shot strike per wave per node is bounded. Stationing several Wreckers on different nodes gives one strike each. It never multiplies asset damage the way several Breakers would. A Wrecker plus a Ghost on the same node is a good combo, because the Ghost holds the first threat in place for the strike, which is the intended synergy and not a runaway.

## 5. Data
- **TriggeredEffectData:** trigger = ON_RAID_START (12), with a new `repeat_each_wave` boolean (or a `min_rank_for_repeat` int).
- **EffectData:** type = DEAL_DAMAGE, target = a threat. The existing target enum has no "first arriving threat" value, and neither it nor the pierce flag (which the effect would need) is read by the raid code today.
- **Rank scaling:** the amount is multiplied by the existing `station_bonus_multiplier`. The `multiplier = 1.5` literal is replaced with `amount = 8`.
- **Not data-only.** It needs a small raid-side hook: NEW: station strike (raid resolver trigger on first threat entry, pierce damage, a preview line, a grid chip). Size S–M. No N# applies, because the raid system is outside N1–N20 and falls under the raid design pass in section 6 of CONTENT_DESIGN_V2.
- **Fallback:** a data-only version is possible. Use the Breaker's multiplier effect at +75% damage to turrets and keep the flavour text. This is not unique enough, so it is not recommended.

## 6. Q
- Q: Should the strike also hit when a threat is already ICE-Locked on the node, or only on first entry? (Proposed: first entry only.)
- Q: Is "first wave only" at Ranks 0–1 too weak compared with the Breaker's continuous +50%?
- Q: Should the strike deal damage to threats only, or can it also remove a TAKEN-state pressure on the node?
