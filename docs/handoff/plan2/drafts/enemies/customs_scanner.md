<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__customs_scanner; status ok; tokens in 16120 cache-write 0 cache-read 32007 out 3353; cost $0.036. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# customs_scanner: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. **Corporation:** Meridian.
- **Layers:** L1-2 teaching. It is the first enemy that teaches "read the landing tier on a hostile wheel."
- **The one question:** *"Which of the two needles carries the tariff?"* The scanner has two needles at uneven ticks, 0 and 11. A landing that is good for one needle is usually bad for the other. Its heavy slice (Seizure) is a **4-tick slice with no Perfect** (R11) next to a **3-tick Priority slice** that is easy to nudge across.
- **Shortening answer:** a 1-tick nudge or spin that parks the wide needle on Null / Scan and the narrow needle on a Good-only slice. This removes the Seizure and the RAM drain together. The fight then ends in 3 turns.
- A player who ignores it eats Seizure + Priority and loses 3 RAM per turn.

## 2. Phase plan (single phase, no threshold)

| Field | Value |
|---|---|
| Phase | 1 of 1, no parked floor (the last phase has no floor) |
| Needles | 2, ticks 0 and 11 (uneven, R10/R11) |
| Hub | none (no passive), so there is no Hub Breach target |
| Statuses / parasites | none |
| Listeners | none (data-only) |

**Layout** (sizes sum to 30):

| # | Slice | Size | Map | Effect |
|---|---|---|---|---|
| 1 | Scan | 5 | W G P G W | SHIM 6 FLAT (×dmg factor 1.0/1.3/1.69/2.2) |
| 2 | Priority | 3 | G P G | INFECT: drain 2 RAM on hit (was 3). 0 damage |
| 3 | Null | 4 | W G G W | nothing |
| 4 | Seizure | 4 | W G G W (no Perfect) | OVERFLOW 12 FLAT |
| 5 | Bulwark | 6 | W W G G W W | BLOCK 6 FLAT |
| 6 | Scan | 5 | W G P G W | SHIM 6 FLAT |
| 7 | Null | 3 | G P G | nothing |

Sizes: 5+3+4+4+6+5+3 = 30. Slice start ticks, centred on ticks 2 / 7 / 11 / 15 / 20 / 26 / 29 (rounded; the data sets cumulative boundaries). Needle 0 reads Scan (size 5, ticks −2…2), and needle 11 reads the Null/Seizure boundary (ticks 9-12 = Null, 13-16 = Seizure), so a rotation of ±2 ticks moves needle 2 onto Seizure. This is the "two needles, one hazard" geometry.

**The key geometry:** the needles are 11 ticks apart. Priority (3) and Seizure (4) sit 7-8 ticks apart. A single rotation can only hurt with one at a time. Most rotations give one needle a damaging slice and the other a harmless one.

- Both needles hit the target at its own pointer (pointer rule, GDD 2.7), so Seizure lands once, not twice, unless both needles read it. That is not possible with 4-tick slices 11 apart.
- Transition: none (one phase).

## 3. Sustain and intake
- **Sustain:** Bulwark BLOCK 6 FLAT, a single source. Block expires each turn, so it reduces the player's effective damage only on turns Bulwark is read. At T1 that is at most 6 per turn against a reference of 9 per turn: **67 %**. That is over the 30 % cap, so it must be rare: only one Bulwark slice of 6 on the wheel, read by one needle. Expected reads per turn: 2 needles × 6/30 = 0.4. Expected block ≈ 0.4 × 6 ≈ 2.4 per turn = **27 % of 9**. Under the cap on average. Bad luck may block 12, but the player can steer away.
- **Intake per turn at the reference player (T1, no steering):** expected per needle: Scan 5/30 × 6 = 1.0; Seizure 4/30 × 12 = 1.6; per needle 2.6, two needles **≈ 5.2 per turn** minus the player's own block. With Good-only landings accounted for, about 4-5. Above 0. Steered well: 0-3. RAM drain: Priority 3/30 × 2 × 2 needles ≈ 0.4 RAM per turn on average.

## 4. HP by tier (R2 normal band, 1 phase)
Budget = reference_dpt × 3.5 turns × needles hit, minus sustain × 3.5. The player's hit lands on the scanner's 2 needles. Needle count applies only to the player's attack if it lands on its pointers (pointer rule), so the budget is multiplied by 2 only on a Pointer attack that reads both. I use a conservative ×1.0 because Pointer hits only land twice when both needles sit on live slices.

| Tier | dpt | Raw (dpt × 3.5) | Sustain (2.4 × dmg factor × 3.5) | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 8.4 | **34** (band 28-36, +extra for 2 needles' ~10 %: 34) |
| T2 | 11 | 38.5 | 10.9 | **40** (band 34-44) |
| T3 | 14 | 49 | 14.2 | **50** (band 44-56) |
| T4 | 18 | 63 | 18.5 | **62** (band 56-70) |

I round up slightly above the pure arithmetic because players do not hit every turn. `hp_by_tier` = [34, 40, 50, 62]. Today's 50 HP is the T3 value; it is kept at T3 only.

## 5. Enrage
None. Normals have it off (R4). The fight is 3-4 turns, so it is not needed.

## 6. Buffs and counter Exploits
Not applicable (normals only).

## 7. Counterplay
- **Good player:** read both landings before committing. Use the free nudge to move the Seizure needle by ±1-2 to Null (4-tick slice, G/G centre). Use a spin card to drop Bulwark off both needles. Land Perfects on Scan 1 and 2 only when it is cheap; the Seizure 4-tick slice and Bulwark never give the scanner a Perfect, so only the Scan and Priority slices matter. Kill in 3 turns.
- **Weak player:** nudges only for their own wheel and ignores the scanner's. Eats Seizure 12 once or twice, loses 2 RAM per Priority hit and is slowly out of nudges. They still win, but at a high HP cost, which is the teaching moment.
- **Do not over-correct:** nudging Seizure off needle 2 can push Priority onto it. That is the secondary lesson: Priority is 3 ticks, so it can be steered onto by accident.

## 8. Systems needed
- **N12** (variable slice sizes, sub-tick map) for the 3-, 4- and 6-tick slices. **Fallback:** all 5-tick slices (6 slices: Scan, Priority, Null, Seizure, Bulwark, Scan) with a 0 / 15 needle pair.
- **N11** (pointers on any tick) for the 0 / 11 needles. **Fallback:** 0 / 10 or 0 / 15 (both legal under today's rule).
- **N1** (flat × tier damage factor) so the flat 6 / 12 amounts scale correctly. **Fallback:** current output_scale.
- **N2** (`hp_by_tier`). **Fallback:** a single hp with the multiplier.
- Everything else is existing (SHIM, OVERFLOW, DEFRAG→BLOCK, INFECT with DRAIN_RAM). No N6, N8, N10.

## 9. Delta vs today
- **Today:** one needle, 6 slices of 5: Shim 9, Priority, Defrag 6, Overflow 14, Shim 9, Null. 50 HP.
- **Changes:** a second needle at tick 11; slices resized (3-6 ticks); Overflow 14 → Seizure 12 on a Perfect-less slice; Shim 9 → 6 (two needles carry the total); Priority drain 3 → 2; Null slice split in two; `hp_by_tier` replaces the single hp.
- **Kept:** the Priority RAM-drain identity, Defrag as the one sustain source, `cycle_reward` 15, id and description.
- **heat_effects:** none authored today, so none to keep.

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only), so this is an estimate from the wheel.
- **Turns:** 3.5 at T1-T2, 3.8 at T3-T4 (about 1 more turn at low skill).
- **Win %:** T1 about 99 %, T2 98 %, T3 95 %, T4 92 %. Expected intake is about 5 per turn at T1 (about 17 per fight), and the player has 45-60 HP.
- **Why:** the 2 needles double the intake over today's single needle, but the HP drop from 50 to 34 at T1 shortens the fight by about 1.5 turns, so total damage taken stays similar.

Q: Should Seizure (no Perfect) be marked in the intent UI as "cannot be Perfected" so players learn the sub-tick map?
Q: Is 2 RAM drain per Priority hit too weak to matter now that RAM is banked to 12?
Q: Should the 0 / 11 needle gap be a Meridian-wide pattern, or reserved for this scanner?
