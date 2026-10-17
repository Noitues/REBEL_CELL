<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__handler_proxy; status ok; tokens in 15336 cache-write 0 cache-read 32007 out 2852; cost $0.033. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# handler_proxy: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, REBEL_CELL. Appears in L1-2 as a teaching enemy for the "unlock before you strike" lesson. At L5-6 it is a pressure check on whether you kept a nudge in reserve.
- **Concept:** DISPATCH's local relay. It answers to a leash it holds on *your* wheel, not its own: it plants a LEASH (an OUTPUT_DOWN stack) on the slice your own pointer will read, so your best landing is quietly taxed.
- **Question (single phase):** "Which of your slices is leashed, and do you pay to land elsewhere or take the tax and burst?"
- **Fast answer:** Spend the free nudge to move off the leashed slice, then SHIM it while its Sandbox is not turning. Its Resistance 2 means nudging *its* wheel is wasteful. Move *yours*.
- **Distinct from siblings:** Mirror Script, Echo Process and Cell Informant copy or replay you. Loyalty Test and Dead Drop are separate tests. The Proxy is the only normal built around a status on your wheel plus resistance.

## 2. Phase plan (single phase, no threshold, no floor)

| Item | Design |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | Resistance 2 (passive, restores each player turn). It stays: it makes its own wheel hard to steer, which pushes the player to steer *theirs*. |
| Statuses | OUTPUT_DOWN ×1 on your slice under your pointer (N8/N9) |
| Listeners | none |

**Layout (ticks sum 30; N12):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Leash | 5 | INFECT: OUTPUT_DOWN ×1 on your slice under your pointer (UNDER_POINTER), plus 3 FLAT damage |
| 2 | Shim | 5 | SHIM 8 FLAT |
| 3 | Defrag | 4 | BLOCK 6 FLAT |
| 4 | Overflow | 6 | OVERFLOW 14 FLAT. Its big slice, and a 6-tick WEAK-heavy slice (W W G G W W), so only 2 of 6 ticks are Perfect-quality. |
| 5 | Sandbox | 4 | SHIELD 5 FLAT (this is a defense slice, not sustain) |
| 6 | Null | 6 | nothing |

- Leash is the signature slice. Overflow is the threat, and its odd width makes the landing readable and steerable.
- Today's wheel was Defrag, Shim, Defrag, Shim, Sandbox, Null, with 2 Defrags, 2 Shims and no status.

**Transition:** none (single phase).

## 3. Sustain and intake
- **Sustain:** none. The Defrag and Sandbox slices are defense, not heal. At most 0 % of reference damage. The rule is met.
- **Intake per turn** (reference player, T3 factor 1.69). A needle landing is roughly uniform by slice width (ticks/30):

| Slice | Share | Base dmg | ×1.69 |
|---|---|---|---|
| Leash | 5/30 | 3 | 5 |
| Shim | 5/30 | 8 | 13.5 |
| Overflow | 6/30 | 14 | 23.7 |
| Defrag/Sandbox/Null | 14/30 | 0 | 0 |

- Raw expected ≈ (5×5 + 13.5×5 + 23.7×6)/30 ≈ 7.8 per turn at T3, before player block or nudging. That is above 0.
- With a free nudge and one dodge, a good player takes about 2-3 per turn. A weak player takes the full ~8, plus a LEASH tax on the next landing.
- T1 expected raw ≈ 4.6, T2 ≈ 6.0, T4 ≈ 10.3.

## 4. HP by tier
Normal (1 phase). The R2 budget is dpt × 3.5 × needles, with no sustain. The reference player's needles hit once.

| Tier | dpt | Budget | Chosen hp_by_tier |
|---|---|---|---|
| T1 | 9 | 31.5 | 34 |
| T2 | 11 | 38.5 | 42 |
| T3 | 14 | 49 | 52 |
| T4 | 18 | 63 | 66 |

All values are inside the Normal bands (28-36, 34-44, 44-56, 56-70). The 64 HP today (a T-less value, above T2 and T3 bands) is replaced. Block and shield (6 and 5 FLAT, ×1.3^(t−1)) soak a little; the +2 to +3 over budget is the tolerance for that, so the fight stays in 3-4 turns.

## 5. Enrage
None. Normals have it off (R4). With no sustain, no stall is possible.

## 6. Buffs and counter Exploits
Not applicable (normal enemy).

## 7. Counterplay
- **Good player:**
  - Reads the Leash intent and moves its landing with the free nudge, or stacks a Cleanse or Encrypt.
  - Steers its needle off Overflow using Resistance-free nudges on *its own* wheel (their own wheel has no resistance). Resistance 2 means nudging the Proxy's wheel only works with a 3-tick move or a Ghost-class ignore.
  - Bursts on Null or Sandbox turns for the damage window.
- **Weak player:**
  - Ignores Leash, so their next Perfect Shim lands at 0.75×.
  - Spends RAM nudging the Proxy's resistant wheel and wastes it.
  - Overvalues defense against 8-damage Shims and loses to Overflow.

## 8. Systems needed
- **N12** (variable slice sizes) for the 4 and 6-tick slices. **Fallback:** 5-tick slices on six slots, with the same effects.
- **N8/N9** (×N stacks, OUTPUT_DOWN). **Fallback:** the existing PARASITE status (halves the slice) as the Leash. It is stronger, so Leash damage drops to 2.
- **N1/N2** (FLAT scaling by tier and `hp_by_tier`). Without them the numbers fall back to a single `hp`.
- Not needed: N3, N4, N5, N6, N10, N11.

## 9. Delta vs today
- **Kept:** id, corporation, passive_resistance 2, a single needle at 0, cycle_reward 15, the Sandbox and Null slices.
- **Changed:**
  - Defrag 8 / 8 → one Defrag 6.
  - Shim 10 / 10 → one Shim 8.
  - A Leash slice and an Overflow 14 are new.
  - The 6-slot uniform wheel becomes uneven sizes.
  - HP 64 → 34 / 42 / 52 / 66.
  - Description: "Marks your best slice, then hits it."
- **heat_effects:** none exist on the file, so none are added.
- Today's wheel has no pressure beyond two Shims, so at T1 the intake is near 5 per turn already. The new one is more varied.

## 10. Predicted sim check
There is no baseline row, so this is an estimate from the wheel.
- **Turns:** 3.5 mean, p90 5.
- **Win %:** T1 ≥ 97, T2 ≥ 96, T3 ≈ 92, T4 ≈ 88.
- Why: intake ~5-10 raw per turn against 45-60 starting HP and a 3-4 turn fight. T4 sits below the 90 % bar and may need Overflow at 12.

## 11. Q:
- Q: Should Leash target the slice your pointer will read *this* resolve, or your best slice, which is a stronger and more opaque design?
- Q: Does ×1 OUTPUT_DOWN on a WEAK landing still apply (R8 and Q11 default: yes)?
- Q: Do FLAT enemy block and shield also scale by tier, or should the shield stay fixed at 5?
- Q: Is Resistance 2 enough of a signature once Cell Informant and Loyalty Test are redesigned?
