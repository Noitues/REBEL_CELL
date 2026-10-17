<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__launch_pad; status ok; tokens in 5027 cache-write 0 cache-read 32585 out 1931; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/launch_pad

**Verdict:** FIX

## Issues

1. **BLOCKER, R11 / §2 table.** The 6-tick slices are mapped "W W G G W W" with "no Perfect". R11's default for size 6 is W W G G W W, so that part is consistent. The Fuel Shield and Shim 5 rows (5 ticks) correctly give W G P G W. But the Shim 8 and Launch rows call the profile "narrow-tier", and the Solar Flare row says "G G G G is the default W G G W", which contradicts itself. The R11 size-4 default is W G G W. The Flare row must state that map.

2. **BLOCKER, R13 / §2 vs §9.** The draft says the second Sandbox is replaced by a Launch slice. Today's layout isn't shown, but the new layout has exactly one defensive slice plus a Null. R13's SANDBOX name is for the evade rule. "Fuel Shield (SANDBOX type, enemy shield)" is the SHIELD in R13 naming. Rename the slice to SHIELD, which is a lingering effect with a cap.

3. **BLOCKER, R2 arithmetic / §4.** The budget is dpt × 3.5 − sustain × 3.5. T1: 9 × 3.5 = 31.5, minus 1.8 = 29.7. That is fine. But the sustain figures are inconsistent with §3. §3 gives 0.5 per turn at T1, and 0.5 × 3.5 = 1.75, which is fine. At T4, §3 says 0.8 per turn, so the deduction is 2.8, correct. At T3, 2.4 is unsupported, because §3 gives no T3 sustain figure. The deeper issue is that the 8 % shield on 30 HP is 2.4, not "≈ 4", and 5 at T4 should be 4.8. The T1 shield "≈ 4 (46→ band 28-36, shield ≈ 3)" is garbled, and the 46 is a T3 value. Recompute the sustain.

4. **MAJOR, §3 intake.** The drone is described as "turns 2-4, average ≈ 1.5", while the Launch Drone has a 5 HP mini-wheel (Shim 3 / Defrag 3), so 3 damage on only half its slices gives ≈ 1.5 at best. The text then multiplies it by 2.2 at T4 as "3.3". Per R2, flat enemy amounts scale by the tier damage factor, so that is fine, but the T1 total of 6.3 uses 4.8 + 1.5. T4 is 4.8 × 2.2 = 10.6 plus 3.3, which makes 13.9. Correct, but the drone's damage presumably also goes to the player only when the drone's slice is hit. Say so.

5. **MAJOR, N13 / §2 and §8.** "dock_slot = the Launch slice's neighbour" is also described as "Shim 5 at the clockwise side", which makes the guarded slice a weak Shim, not Launch. This undermines the bodyguard question: the dangerous slice stays unguarded. Also, `max_active` and `every_n` are asserted as fields. Check whether they exist; if not, tag them NEW: spawn cadence. The §8 fallback for N13 is "none needed", yet REPLACE is a new rule.

6. **MAJOR, §10 vs R1 pass criteria.** The prediction is T4 88 %, below the ≥ 90 % target at T3, and §10 admits "T3 ≈ 92 %" with only a tuning hint. Pre-tune the Launch slice now.

7. **NIT, §7.** "Spend one nudge to push the enemy needle to Null" conflicts with the claim that the Fuel Shield is the only sustain. Also, the counterplay lists "Cleanse", which does not fit a normal-fight deck.

## Concrete fixes

- Flare row: `Solar Flare | 4 | APPLY_STATUS OVERCLOCKED, 1 random non-NULL slice of yours | n/a | W G G W`.
- Rename: "Fuel Shield" → "SHIELD slice, PERCENT 8 % max HP, enemy shield cap 15 (Q9 open)".
- Sustain recompute: shield 2.4 / 2.9 / 3.7 / 4.8 at T1–T4. Expected 0.4 / 0.5 / 0.6 / 0.8 per turn. Deductions at 3.5 turns: 1.4 / 1.8 / 2.2 / 2.8.
- HP: T1 30 (31.5 − 1.4), T2 36 (38.5 − 1.8 = 36.7), T3 47 (49 − 2.2 = 46.8, rounded), T4 60 (63 − 2.8 = 60.2).
- Dock the drone on the **Launch** slice itself, so the question is real: "dock_slot = Launch".
- Launch damage: 10 instead of 12.
- Tag cadence and `max_active` as "NEW: spawn cadence (data field) — fallback: today's `spawns` every 2 turns".

## Keep

The one question (steer around the guarded slice or kill the drone) is clear and ties to R12. The single-phase design, no enrage and the intake math structure are sound. Keeping T3 near today's 46 HP is a sensible reference point.

## Q:

Q: Does the drone's damage land only when its slice is under the pointer?
Q: Should `max_active` 1 with REPLACE ever trigger in a 3-4 turn fight, given launches on turns 2 and 4?
Q: Is the enemy shield cap shared with the player's `shield_cap` of 15?
