<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__echo_process; status ok; tokens in 16374 cache-write 0 cache-read 32007 out 3060; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# echo_process: direct design

## 1. Identity & the one question
- **Class:** Normal, REBEL_CELL, 1 phase, 3-4 turns, no enrage.
- **Layers:** L3-6 pressure. The Echo listener punishes a habit, so L1-2 players should meet Cell Informant or Dead Drop first.
- **The question:** "Will you pay for your best landing?" Echo Process is a single-needle listener enemy. Its **Echo** listener hits back whenever you land a **Perfect**. Cards and nudges don't trigger it.
- **What shortens the fight:** landing GOOD, which costs 0 and does full damage. Perfect adds no output (1.0× for both) except through class hooks, so a player who takes Good everywhere never triggers it.
- **Why Perfect still tempts:** the Breaker's Perfect hook (resolves the slice twice) is worth more than Echo's price. Whether to pay is the real choice.
- **Distinct from siblings:**
  - The Handler mirrors your nudges.
  - Mirror Script copies your wheel.
  - Echo Process is the only normal that taxes precision itself.

## 2. Phase plan
One phase, no threshold, so no parking (R3) and no floor. HP is spent in 3-4 turns.

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub rule | None |
| Statuses / parasites | CORRUPTED (Dose) |
| Listener (N6) | **Echo**: ON_PERFECT (player's landed Perfect, once per Perfect slice resolved) → 4 damage to the player, FLAT, × tier damage factor. Cap: 1 trigger per turn, so a Breaker's double-resolve Perfect doesn't stack. |

**Layout (ticks sum to 30, R11):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Shim 8 | 5 | 8 damage | FLAT |
| 2 | Dose | 4 | 3 damage + CORRUPTED on 1 random non-NULL slice of yours | FLAT |
| 3 | Defrag 8 | 6 | BLOCK 8 | FLAT |
| 4 | Overflow 14 | 5 | 14 damage | FLAT |
| 5 | Null | 4 | none | n/a |
| 6 | Shim 8 | 6 | 8 damage | FLAT |

Sum = 5+4+6+5+4+6 = 30.

- **Tick quality (R11):**
  - The 4-tick slices (Dose, Null) have no Perfect.
  - The 6-tick slices (Defrag, Shim) read W W G G W W, also no Perfect.
  - Only Shim 8 (5 ticks) and Overflow 14 (5 ticks) can be Perfected.
- **Dropped from today:** Priority. Its RAM drain overlaps the Dose and CORRUPTED RAM tax (R9). Priority belongs to Meridian.
- **Dose and the tax:** each Dose adds a CORRUPTED slice, which doubles RAM costs on it. That slowly taxes a player who stays too long.

## 3. Sustain and intake
- **Sustain:** none from heal.
  - Defrag 8 (BLOCK, FLAT) is defense, not sustain, and only offsets about 8 of the player's damage when it lands.
  - At 1 landing in 6, it averages about 1.3 per turn against the 18 × 0.3 = 5.4 cap, which is fine.
- **Intake per turn at the reference player (T3, tier factor 1.69):**
  - Average slice damage: (8 + 3 + 0 + 14 + 0 + 8) / 6 = 5.5 → 9.3 at T3.
  - Echo: the reference player (calibrated between testers and the bot) lands a Perfect on about 1 turn in 3 → about 4 × 1.69 / 3 ≈ 2.3 per turn if they ignore it.
  - Total intake ≈ 9–11 per turn at T3. A 3.5-turn fight costs about 35 HP if you fully ignore Echo, and about 28 if you avoid Perfects. That's well above 0, with a real choice.
- **Intake at T1 (factor 1.0):** about 5.5 average + Echo ≈ 6.5.

## 4. HP by tier
R2 normal band: T1 28–36, T2 34–44, T3 44–56, T4 56–70. Budget = reference dpt × 3.5 turns × needles hit (1), minus sustain (about 0).

| Tier | dpt | Arithmetic | `hp_by_tier` |
|---|---|---|---|
| T1 | 9 | 9 × 3.5 = 31.5 | 32 |
| T2 | 11 | 11 × 3.5 = 38.5 | 38 |
| T3 | 14 | 14 × 3.5 = 49 | 50 |
| T4 | 18 | 18 × 3.5 = 63 | 62 |

A Perfect-chaser who eats the Echo trade bursts a little faster, while the Good-only player is slower by about 0.3 turns. Both fit 3–4 turns. Today's 52 HP at every tier is replaced.

## 5. Enrage
**None.** The normal default is off (R4), and a 3–4 turn fight doesn't need one.

## 6. Buffs and counter Exploits
Bosses only. Not applicable.

## 7. Counterplay
- **Good player:**
  - Reads the preview, nudges or steers off Perfect (a 1-tick nudge, free on the first), and takes GOOD on Shim and Overflow.
  - Spends Perfects only where the hook outweighs 4 × tier damage (Breaker double-resolve on Overflow).
  - Steers its needle to Null or Dose-WEAK and Defrag.
  - Cleanses or Encrypts to keep the CORRUPTED count at 0–1.
- **Weak player:**
  - Chases Perfect on every slice out of habit and takes the Echo hit each turn.
  - Lets Dose stack CORRUPTED, so RAM costs double and nudges to fix landings get expensive.
  - Hits Defrag with a big card and wastes it.

## 8. Systems needed
- **N6** (enemy listener ON_PERFECT). No data-only fallback for the listener.
  - Fallback: delete Echo and use an existing slice effect, e.g. the enemy gets a slice whose Perfect-read... not viable.
  - The honest fallback is the layout alone: with Priority kept, the fight is a plain damage-and-tax normal.
- **N1** (FLAT amounts × the tier damage factor) and **N2** (`hp_by_tier`, damage table).
- **N12** (`size_ticks` 4/5/6). Fallback: 5-tick slices, 6 slices, but you lose the 4/6-tick no-Perfect shape that makes Echo targetable.
- **N9** (CORRUPTED = RAM ×2) for Dose to matter in the new rules. With the old rule it still works (self-damage).
- **N19** for the sim metric (listener fires).

## 9. Delta vs today
- **Kept:** id, corporation, Shim, Dose, Defrag, Overflow, Null, one needle, cycle_reward 15.
- **Changed:**
  - HP is now per tier.
  - Slices are resized and the amounts are tuned.
  - Priority is removed.
  - The Echo listener is new, and the description should become "Hits back when you land a Perfect."
- **heat_effects:** none authored today, none added.

## 10. Predicted sim check
No baseline row exists (Solace only), so these are estimates from the wheel.
- **Turns:** about 3.5 at T1–T3 and about 3.8 at T4, p90 ≤ 5.5.
- **Win %:** T1 ~98 %, T2 ~96 %, T3 ~92 % (intake ≈ 30 HP), T4 ~85 % (intake ≈ 40 HP against a mid-run HP pool).
- **Why:** there is no heal, one needle, and 1.0× Echo plus Dose chip. The T4 shortfall against the proposed ≥ 90 % at T3 is a damage-table tuning call: the Echo amount can drop to 3.

## 11. Open questions
Q: Does Echo trigger on a class hook's second resolve (Breaker double), or only once per Perfect slice? (I chose a once-per-turn cap.)
Q: Should Echo apply once per Perfect or once per turn on a 2-wheel (drone/satellite) Perfect?
Q: Is 4 FLAT the right price, or should it scale with the Perfect slice's output (PERCENT of the landed damage)?
Q: Does a Good landing that the Calibrated Firmware raises to Perfect still trigger Echo?
