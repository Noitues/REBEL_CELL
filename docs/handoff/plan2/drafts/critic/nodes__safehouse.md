<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__nodes__safehouse; status ok; tokens in 5790 cache-write 0 cache-read 32585 out 1962; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: nodes/safehouse

**Verdict:** FIX

## Issues

1. **BLOCKER, internal contradiction (§2 Stationing vs §2 Slot rule / Level II).** "Stationing and recalling are free and instant between runs" versus "Rank 0 rookie … reduced bonus", while the table gives Rank 0 values that are not half of Rank 1. Breaker is 25 vs 50 (OK), but Ghost is 1/1 and Botnet is 1/1/…, so "half scale, rounded down" gives 0 and is false for them. The table and the rule disagree.
2. **BLOCKER, amount modes (R5/R2).** "`rank_scaling`… written as FLAT. Percent amounts read the target node's max integrity and are used only for repair", but the Rigger repair is listed as flat 3/5/7/10, and the Breaker's damage is a percent that is not a share of max HP. No `amount_mode` field is named, and the Breaker row mixes PERCENT with a FLAT claim.
3. **MAJOR, undefined stacking (§2 Slot rule).** "two stationed operatives of the same class stack at 50 %", but Level I has 1 slot and Level II is the only way to get 2. The cap "4 Level II Safehouses" is not otherwise reachable by the install curve, and the 2nd operative's bonus does not appear in the examples. The config key `second_slot_bonus_ratio` is not in §2 and conflicts with Q4.
4. **MAJOR, fabricated numbers vs GDD (§2 table).** The GDD 5.2 station bonus for Ghost is "Threats entering node delayed 1 step", with no Rank 0. Botnet's "persists at Rank 3" and "TURRET at Rank 2" are invented, and "free asset per raid" collides with Armory cap 6 (§8 admits it). The draft also says "No N# system is required" while it needs a new raid hook and the new effect type `GRANT_RAID_ASSET`, which it labels "NEW: station asset grant". The dependency is stated inconsistently, so tag it consistently.
5. **MAJOR, Example B arithmetic.** 3 × 1.6 = 4.8 is right, but Rank 2 Breaker is +60 % as the table says, and the "Total spent: 60" is 30 + 30 = 60, which is correct only if the 2nd Safehouse is 30. The draft's curve is [20, 30, 45, 65], so the 2nd is 30 and Level II is 30. Fine, but Example B says the Safehouse is "next to a Firewall Relay" and Level II range 1 boosts a second turret, while the Breaker bonus is listed as range 0 at Rank 0–2 and range 1 only at Rank 3. This contradicts the Level II +1 hop rule.
6. **MAJOR, raid interaction contradiction (§2).** "`raid_priority` stays 0" while the Safehouse has "integrity 20" and §2 says the bonus is lost on DOWN. The draft also says "Rigger regains integrity after each wave" for the node itself, with the node weak and not targeted. The Rigger bonus then barely triggers, and Example C protects a Vault Terminal, which is not the Safehouse's node (range 0 until Level II or Rank 3). Example C is inconsistent with range 0.
7. **NIT, template.** Section 3 has no RNG stream statement beyond "none". That is acceptable. §4 has no cancel path for the Level II upgrade.
8. **NIT,** "cannot die" for a stationed operative restates GDD 5.4 and is fine.

## Concrete fixes

- Replace the table with explicit values and drop "half scale":

| Class | Effect | R0 / R1 / R2 / R3 | Mode |
|---|---|---|---|
| Breaker | node assets damage | +25 / +50 / +60 / +75 | PERCENT of base asset damage |
| Ghost | entering threats delayed (steps) | 0 / 1 / 1 / 2 | FLAT |
| Rigger | integrity regained per wave | 3 / 5 / 7 / 10 | FLAT |
| Botnet | free TURRET (3 dmg) per raid, max 1 | n/a / 1 / 1 / 1 | FLAT |

- Fix the range rule: `bonus_range_hops` = 0 at Level I; Level II gives 1. Remove "1 at Rank 3". Rewrite Example C so the Rigger sits adjacent to a Level II Safehouse, or place the Rigger Safehouse on the Vault Terminal's Site.
- Slot rule: "A Level II Safehouse hosts 2 operatives. A second same-class operative contributes `second_slot_bonus_ratio` = 0.5 of its values (rounded down, minimum 0). Different classes stack fully."
- Systems line: "NEW: station bonus raid hook (M); NEW: station asset grant (S). Data-only fallback: Breaker, Ghost and Rigger as node `passive_effects`; Botnet is deferred."
- Add `amount_mode` to `StationBonusData.rank_scaling` entries.

## Keep

- The cost-versus-benefit framing and the Heat-neutral stationing: it is the real alternative to running.
- Class bonuses grounded in GDD 5.2, with alternates sharing a bonus family (G8).
- The 4-Safehouse cap and the install curve as the anti-degeneracy lever.

## Q:

- Q: Should Rank 0 rookies give any bonus at all, or only Rank 1 and up?
- Q: Does Level II range 1 apply to all four classes, including the Botnet's grant?
- Q: Does a stationed operative's Rank advance from raids survived?
