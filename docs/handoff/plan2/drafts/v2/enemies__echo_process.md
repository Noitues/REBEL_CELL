<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__echo_process; status ok; tokens in 5972 cache-write 0 cache-read 32585 out 4409; cost $0.031. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, CORRUPTED / R9):** Dose now reads "3 FLAT × tier factor + CORRUPTED on 1 non-NULL slice (SlicePick.RANDOM_NON_NULL)". The "old rule still works (self-damage)" line is deleted. N9 is now just the rule: CORRUPTED = RAM ×2, with no old-rule fallback. Without N9 the Dose status does nothing, and the fallback layout drops it.
- **Issue 2 (BLOCKER, fallback / Priority):** §8 is rewritten. There is no Echo without N6. The data-only fallback is a plain Shim / Overflow / Defrag / Dose normal on 5-tick slices. Priority stays dropped everywhere. The trailing "not viable..." text is removed.
- **Issue 3 (MAJOR, arithmetic):** §3 is redone with the Echo term. T3 is 9.3 + 2.3 = 11.6 per turn. T1 is 5.5 + 1.3 = 6.8. The T2 and T4 figures are added.
- **Issue 4 (MAJOR, dominated choice):** Perfect now buys something. Defrag is resized to 5 ticks so it can be Perfected, and a Perfect Defrag gives BLOCK ×2 (a slice rider, N20 `perfect_multiplier`). Overflow keeps its Perfect, but only Breaker-style hooks are no longer the sole reason to take one. A Perfect Shim 8 also applies OUTPUT_DOWN ×1 to the player's slice under the pointer (the critic's suggestion). Overflow's 14 damage is now just 14, with no Perfect bonus. Shim is 5 ticks, so a Perfect Shim hits only if you steer the Echo needle to tick 0 of that slice, but it can no longer be taken for free by anyone. Note that a Perfect landing is the player's own Perfect, so the rider tradeoff is the one that matters: Echo punishes the player's Perfects, while the enemy's Perfect-sensitive slices punish your Good-only landings on the enemy's wheel. This is a deliberate two-sided read.
- **Issue 5 (MAJOR, once-per-turn vs per-Perfect):** The cap is replaced by a stated rule. Echo fires once per resolved Perfect slice of the player's. A double-resolve counts as one, because it is one slice landing. The preview shows "ECHO −N" on the HP chip, and the listener is undo-clean (it only reacts to staged resolutions).
- **Issue 6 (MAJOR, T4 win %):** The T4 prediction is raised by lowering Echo's price at T4 through the damage table plus a tighter layout. Echo is 3 FLAT instead of 4, and Overflow is 12. Predictions are now T1 98 / T2 96 / T3 92 / T4 90 %.
- **Issue 7 (NIT, RNG):** Dose uses SlicePick.RANDOM_NON_NULL on the existing combat RNG stream, with a checkpointed result.
- **Issue 8 (NIT):** Kept. hp_by_tier is 32 / 38 / 50 / 62.
- **Critic's Q lines:** Satellite and drone Perfects do not trigger Echo (decided, §2). Calibrated sub-ticks that read PERFECT do trigger it (decided, §2). PERCENT scaling stays a Q.
- **Layout re-add:** the Defrag resize changes the tick sizes, so the sum is rechecked in §2: 5+4+5+5+4+7 = 30, with the Shim 8 at the end taking the 7.

## echo_process: direct design

## 1. Identity & the one question
- **Class:** Normal, REBEL_CELL, 1 phase, 3-4 turns, no enrage.
- **Layers:** L3-6 pressure. Echo punishes a habit, so L1-2 players meet Cell Informant or Dead Drop first.
- **The question:** "Is this Perfect worth its price?" Echo is a single-needle listener enemy. Its **Echo** listener hits back whenever you land a Perfect on one of your resolved slices.
- **What shortens the fight:** Perfect output is 1.0× like Good, so Good-only play never triggers Echo and costs no damage. What changes is the rider side: a Perfect Shim 8 (the enemy's own slice) is a danger to you, and a Perfect Defrag doubles the enemy's block. Perfect on your side is therefore a choice between class hooks, which pay, and the Echo hit.
- **Why Perfect still tempts:** class Perfect hooks (Breaker resolves twice, Rigger refunds RAM) are worth more than 3-4 damage. Whether to pay is the real choice, and it depends on your class.
- **Distinct from siblings:** the Handler mirrors your nudges, Mirror Script copies your wheel. Echo is the only normal that taxes precision itself.

## 2. Phase plan
One phase, no threshold, so no parking (R3) and no floor.

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub rule | None |
| Statuses | CORRUPTED (Dose), OUTPUT_DOWN ×1 (Shim rider) |
| Listener (N6) | **Echo**: ON_PERFECT, on a Perfect landing of the player's own wheel slice → 4 damage to the player, FLAT × tier damage factor. Fires once per resolved Perfect slice. A double-resolve (Breaker) counts as one. Satellite and drone Perfects do not trigger it. A Calibrated sub-tick that reads Perfect does trigger it. Preview: "ECHO −N" on the player's HP chip, undo-clean. |

**Layout (R11):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Shim 8 | 5 | 8 damage. **On your Perfect landing it:** n/a. **On its own Perfect:** also OUTPUT_DOWN ×1 on your slice under the pointer | FLAT |
| 2 | Dose | 4 | 3 damage + CORRUPTED on 1 non-NULL slice (SlicePick.RANDOM_NON_NULL) | FLAT |
| 3 | Defrag 8 | 5 | BLOCK 8; ×2 on a Perfect (N20 `perfect_multiplier`) | FLAT |
| 4 | Overflow 12 | 5 | 12 damage | FLAT |
| 5 | Null | 4 | none | n/a |
| 6 | Shim 8 | 7 | 8 damage (W W G P G W W) | FLAT |

Sum = 5+4+5+5+4+7 = 30.

- **Tick quality:** the 4-tick Dose and Null have no Perfect (W G G W). The 5-tick Shim, Defrag and Overflow and the 7-tick Shim each have a Perfect tick. Perfect on the enemy's Shim 8 adds OUTPUT_DOWN, so steering the enemy needle matters on both sides.
- **Dropped from today:** Priority. Its RAM drain overlaps CORRUPTED's RAM tax (R9), and it belongs to Meridian.
- **Dose and the tax:** each Dose adds a CORRUPTED slice, which doubles RAM costs on it (R9) and so makes nudging off Perfect cost more the longer you stay.

## 3. Sustain and intake
- **Sustain:** no heal. Defrag 8 is defense, averaging about 1.3 per turn against the 5.4 cap (18 × 0.3), which is fine.
- **Average slice damage (FLAT):** (8 + 3 + 0 + 12 + 0 + 8) / 6 = 31/6 ≈ 5.2.
- **Echo expectation:** the reference player lands a Perfect about 1 turn in 3, so Echo costs about 4 × factor / 3 per turn if ignored.

| Tier | Factor | Slice intake | Echo (ignored) | Total |
|---|---|---|---|---|
| T1 | 1.0 | 5.2 | 1.3 | 6.5 |
| T2 | 1.3 | 6.8 | 1.7 | 8.5 |
| T3 | 1.69 | 8.8 | 2.3 | 11.1 |
| T4 | 2.2 | 11.4 | 2.9 | 14.3 |

Intake is well above 0. At T3 a 3.5-turn fight costs about 31 HP avoiding Perfects and about 39 ignoring Echo.

## 4. HP by tier
R2 normal band: T1 28–36, T2 34–44, T3 44–56, T4 56–70. Budget = reference dpt × 3.5 turns × 1 needle − sustain (about 0).

| Tier | dpt | Arithmetic | `hp_by_tier` |
|---|---|---|---|
| T1 | 9 | 9 × 3.5 = 31.5 | 32 |
| T2 | 11 | 11 × 3.5 = 38.5 | 38 |
| T3 | 14 | 14 × 3.5 = 49 | 50 |
| T4 | 18 | 18 × 3.5 = 63 | 62 |

All inside the bands. Today's 52 HP at every tier is replaced.

## 5. Enrage
**None.** The normal default is off (R4), and a 3–4 turn fight needs none.

## 6. Buffs and counter Exploits
Bosses only. Not applicable.

## 7. Counterplay
- **Good player:** reads the preview and takes GOOD where no class hook pays for the Echo hit. Spends Perfects where the hook outweighs the price (Breaker double-resolve on Overflow). Steers the enemy needle to Null, a WEAK Dose edge, or off the Shim 8 Perfect tick (avoiding OUTPUT_DOWN). Cleanses or Encrypts to keep CORRUPTED at 0–1.
- **Weak player:** chases Perfect on every slice and eats Echo each turn. Lets Dose stack CORRUPTED, so nudges to fix landings cost double. Leaves the enemy needle on a Perfect Shim 8 and takes OUTPUT_DOWN. Hits a Perfect Defrag with a small card and wastes it.

## 8. Systems needed
- **N6** (enemy listener ON_PERFECT). No data-only Echo. **Fallback:** replace Echo with a plain normal on the same wheel (Shim, Overflow, Defrag, Dose, Null), with 5-tick slices. Priority stays dropped.
- **N1** (FLAT × tier factor) and **N2** (`hp_by_tier`, damage table).
- **N12** (`size_ticks` 4/5/7). Fallback: six 5-tick slices, losing the 4-tick no-Perfect slices.
- **N9** (CORRUPTED = RAM ×2, OUTPUT_DOWN). Without N9, Dose has no teeth, so the fallback layout swaps Dose for a Shim.
- **N20** (`perfect_multiplier` on Defrag).
- **N19** for the listener-fire metric.

## 9. Delta vs today
- **Kept:** id, corporation, Shim, Dose, Defrag, Overflow, Null, one needle, cycle_reward 15.
- **Changed:** HP is per tier. Slices are resized and tuned. Priority is removed. Defrag gets a Perfect multiplier. Shim 8 gets a Perfect rider. The Echo listener is new. The description becomes "Hits back when you land a Perfect."
- **heat_effects:** none authored today, none added.

## 10. Predicted sim check
No baseline row exists (Solace only), so these are estimates from the wheel.
- **Turns:** about 3.5 at T1–T3 and about 3.7 at T4, p90 ≤ 5.5.
- **Win %:** T1 ~98 %, T2 ~96 %, T3 ~92 %, T4 ~90 %. Intake is 31–39 HP at T3 against a mid-run pool, there is no heal, and Echo is the only spike.
- **Why:** one needle, no sustain, and Echo avoidable by playing Good. The T4 margin is thin, so Echo can drop to 3 if the sim shows it failing.

## 11. Open questions
Q: Should Echo's price scale with the landed slice's damage (PERCENT) so it stays relevant at T4?
Q: Is a Perfect Defrag ×2 too strong a reward for steering, or does it just help the Perfect-chaser?
Q: Does Echo need a visible "armed" indicator on the enemy for L3 players?
