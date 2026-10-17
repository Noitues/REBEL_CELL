<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__riot_control; status ok; tokens in 6784 cache-write 0 cache-read 32585 out 17656; cost $0.098. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **#1 (BLOCKER, HP arithmetic):** the formula is now applied the same way at every tier. Both phases have 2 enemy needles, so each player hit lands twice (pointer rule, GDD 2.7), and the phase budget is `dpt × 3.5 × 2 − tax`. This is the same treatment R2 gives the Genome Core's 2-needle phases. The critic offered "multiplier 1" or "roughly double". I chose double because multiplier 1 would contradict R2's "needles the player's hits land on". The v1 values 64/78/100/128 were single-needle numbers and are replaced by 115/140/178/228. HP now equals the sum of the two phase budgets rounded up, with no hidden "slack" rationale. The threshold changes from 0.50 to 0.51 so the floor matches the P1/P2 split.
- **#2 (BLOCKER, P1 layout):** the phantom "Citation-lite none" slot is gone. P1 is six real slices (6+4+5+5+6+4 = 30) with explicit tick ranges. Needle pairs at 0/15 were checked, and the layout is not point-symmetric. v1's critic-suggested order would have made the two needles mirror each other, so I used an asymmetric order.
- **#3 (MAJOR, intake):** intake is now computed at T1–T4 against a player HP assumption, with the Shove at T4 shown. P2 damage was lowered (Baton 5, Shove 10 FLAT) because v1's numbers would have exceeded a 60 HP player at T4.
- **#4 (MAJOR, transition):** "enemy block is cleared" is removed (BLOCK already expires on its own). The needle move is now an explicit `wheel_override` that sets the needles to (0, 11).
- **#5 (MAJOR, Citation):** I picked one definition: OUTPUT_DOWN ×1 on the slice under the player's pointer (`SlicePick.UNDER_POINTER`). It is deterministic and previewable with no RNG, so v1's RNG question is closed. Two Citations in one turn stack ×2 on the same slice, and the cap is ×3 (−75 %, R8).
- **#6 (MAJOR, sustain):** sustain is stated as 0. The Barrier's cost sits only in the HP budget as a tax.
- **#7 (MAJOR, listener):** Riot Response is replaced by the critic's ON_NUDGE listener. Each paid nudge on the enemy wheel gives the enemy +4 FLAT BLOCK, capped at 2 per turn. P2 now has no Barrier slice, so the earlier "no block anywhere" contradiction is gone.
- **#8 (MAJOR, heat_effects):** retire, none are carried. The global Heat ENEMY_RESISTANCE modifier is noted separately.
- **#9 (NIT):** the invented Zoning Board theme is removed. §10 now cites the Solace elite baseline rows, and the "142 vs 271–287" confusion is resolved: 142 is the file's base value.
- **Critic Q "resistance in P2":** resistance 1 is kept in P1 only. P2 swaps it for the nudge listener, so each phase has exactly one nudge tax.
- **Kept, because strong:** the question flip (which needle, then which slice), the uneven 0/11 needles with their fallback chain, and the enrage reasoning.

# riot_control: direct design

## 1. Identity & the one question
- **Class:** elite, Halcyon, 2 phases, one threshold at 0.51. It appears at L3–L6 as a pressure fight, not a teaching fight.
- **P1 "Shield Wall":** two needles 15 ticks apart. The layout pairs Barrier with something else under almost every rotation. *Question: where do you spend nudges, given that steering costs RAM?* Hub resistance 1 absorbs the first tick of manipulation each turn, so the free nudge is wasted. The first moving nudge costs 1 RAM, and Flip and Respin are blocked. Answer that shortens the fight: put one needle on Null or a WEAK Barrier edge and burst through the other.
- **P2 "Kettle":** no Barrier, uneven needles 0 / 11. Citations degrade the slice you are standing on. *Question: which slice do you let take the stacks, and is a paid steer worth feeding the enemy block?* Answers that shorten the fight: steer with the free nudge, burst while stacks are low, and Cleanse or Encrypt the slice you need.
- **Differs from the Halcyon mini-boss (stacks to ×3, nudge lockout):** Riot Control never locks nudges. It only prices them, and it has no pierce.

## 2. Phase plan

**Threshold:** P1 → P2 at 0.51. While P1 is active the floor is ceil(max HP × 0.51). Excess damage is lost (R3), and the preview shows "PARKED −N".

### P1 Shield Wall (100 → 51 %)
| Item | Value |
|---|---|
| Needles | 2 at ticks 0 / 15 |
| Layout (wheel ticks at rotation 0, sum 30) | Barrier 6 (0–5) · Baton 4 (6–9) · Shove 5 (10–14) · Null 5 (15–19) · Barrier 6 (20–25) · Baton 4 (26–29) |
| Barrier (DEFRAG → BLOCK, FLAT) | 10 × tier factor, on the enemy |
| Baton (SHIM, FLAT) | 5 × tier factor, 1 hit |
| Shove (OVERFLOW, FLAT) | 8 × tier factor |
| Null | nothing |
| Hub | resistance 1, restores each player turn (existing rule) |
| Statuses / listeners | none |

Sub-tick maps: size 6 is W W G G W W, size 4 is W G G W, and size 5 is W G P G W. Landing on a W tick halves the enemy output (GDD 2.4).

Needle pairs (tick t and t+15) show why steering is a real choice:

| Needle A reads | Needle B reads (mostly) |
|---|---|
| Barrier 0–5 | Null 15–19 (Barrier at tick 20) |
| Baton 6–9 | Barrier 21–24 |
| Shove 10–14 | Barrier 25 / Baton 26–29 |
| Null 15–19 | Barrier 0–4 |
| Barrier 20–25 | Barrier 5 / Baton 6–9 / Shove 10 |
| Baton 26–29 | Shove 11–14 |

### P2 Kettle (51 → 0 %)
| Item | Value |
|---|---|
| Needles | 2 at ticks 0 / 11 (uneven, R10) |
| Layout (sum 30) | Citation 5 (0–4) · Baton 4 (5–8) · Shove 6 (9–14) · Citation 5 (15–19) · Baton 4 (20–23) · Null 6 (24–29) |
| Citation (INFECT) | APPLY_STATUS OUTPUT_DOWN ×1 (−25 %) on the player's slice under the pointer (UNDER_POINTER), stack cap ×3 |
| Baton (SHIM, FLAT) | 5 × tier factor |
| Shove (OVERFLOW, FLAT) | 10 × tier factor |
| Hub | none (resistance 1 is removed, so Flip and Respin open up) |
| Listener (N6) | **Paid-steer tax:** ON_NUDGE, when a paid nudge (RAM spent) moves the enemy wheel, the enemy gains BLOCK 4 FLAT × tier factor, max 2 triggers per turn. The free nudge never triggers it. |

**Transition:**
- `wheel_override` sets the new layout. Needles are set explicitly to (0, 11) by a pointer override in the phase data, not by MULTIPLY.
- `hub_override` swaps resistance 1 for the listener.
- Your statuses survive with the R6 remap, and `cleanse_on_enter` = NONE.
- Enemy block expires on its own schedule.
- Phase line: "Hold the line." The new layout is revealed on entry.

## 3. Sustain and intake
- **Sustain: 0.** No heal. The Barrier is defense only, and its cost sits inside the P1 HP budget (§4).
- **Intake per turn, raw, both needles, tier factor f:**
  - P1: per needle Baton 8/30 × 5f = 1.33f and Shove 5/30 × 8f = 1.33f, so 2.67f. Two needles give 5.3f.
  - P2: per needle Baton 8/30 × 5f = 1.33f and Shove 6/30 × 10f = 2.0f, so 3.33f. Two needles give 6.7f, plus the Citation degrade.

| Tier (f) | P1 raw/turn | P2 raw/turn | Fight raw (3.5 turns each) |
|---|---|---|---|
| T1 (1.0) | 5.3 | 6.7 | 42 |
| T2 (1.3) | 6.9 | 8.7 | 55 |
| T3 (1.69) | 9.0 | 11.3 | 71 |
| T4 (2.2) | 11.7 | 14.7 | 92 |

- Intake is above 0 at every tier.
- A Shove at T4 is 8 × 2.2 = 17.6 in P1 and 22 in P2.
- I assume the reference player nets about 50 % of raw through steering, WEAK landings, BLOCK and SANDBOX against a roughly 60 HP operative.
- Net at T4 is about 46 HP of 60, which is hard but fair for an elite.

## 4. HP by tier
Phase budget = `reference_dpt[t] × 3.5 × 2 needles − tax`. Tax is the block the reference player lets through:
- **P1:** about 7f (one needle steered off, the other lands Barrier ~20 % of turns at 10f, over 3.5 turns).
- **P2:** about 4f (about 0.3 paid steers per turn × 4f × 3.5).

| Tier | dpt | Gross per phase | P1 (tax 7f) | P2 (tax 4f) | Sum | Per-needle band × 2 | **HP** | Floor (0.51) | P1 / P2 HP |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 9 | 63 | 56.0 | 59.0 | 115.0 | 112–144 | **115** | 59 | 56 / 59 |
| T2 | 11 | 77 | 67.9 | 71.8 | 139.7 | 136–176 | **140** | 72 | 68 / 72 |
| T3 | 14 | 98 | 86.2 | 91.2 | 177.4 | 176–224 | **178** | 91 | 87 / 91 |
| T4 | 18 | 126 | 110.6 | 117.2 | 227.8 | 224–288 | **228** | 117 | 111 / 117 |

- The R2 band is quoted per single needle (56–72 at T1 and so on), as for the Genome Core. A phase with 2 needles gets 2× that band, shown above.
- The hp_by_tier values are the sums rounded up. There is no slack.
- Today's base HP in the file is 142. R2 lists today's elites at 271–287 at T3.

## 5. Enrage
**Default:** start 8, every 5, +25 % damage (additive). The expected path is about 3.5 + 3.5 = 7 turns, so a reference player never sees enrage. It only punishes stalling. I don't author one, because P2's two needles already supply the pressure.

## 6. Buffs and counter Exploits
Not applicable (elite).

## 7. Counterplay
- **P1:**
  - The first nudge is absorbed by resistance, so plan one paid nudge to move a needle onto Null or a WEAK Barrier edge.
  - Burst the other needle's side.
  - Don't spend big spins into Barrier. Flip and Respin are blocked.
  - Check the pair table before you steer.
- **P2:**
  - The free nudge is clean. Each paid nudge on its wheel gives it BLOCK, so steer once and then commit.
  - SANDBOX the landed Shove.
  - Let the stacks fall on a slice you won't use, or Cleanse or Encrypt the one you need.
  - Flip and Respin now work.
  - A WEAK landing on a 4-tick Baton halves it.
- **Weak player:**
  - Pays RAM in P1 and still leaves Barrier on one needle.
  - Spams paid nudges in P2 and feeds the block.
  - Ignores stacks until their key slice reads ×3.

## 8. Systems needed
- **N1** (FLAT × tier factor) and **N2** (`hp_by_tier`).
- **N3** (threshold parking, `wheel_override`, status keep).
- **N4** (enrage defaults).
- **N6** (ON_NUDGE listener). Fallback: drop it and keep resistance 1 in P2, which is data-only.
- **N8 / N9** (OUTPUT_DOWN stacks). Fallback: the existing PARASITE status, which halves the slice and does not stack.
- **N11** (needles 0 / 11). Fallback: 0 / 10, which is data-only.
- **N12** (4 / 5 / 6-tick slices). Fallback: six 5-tick slices per wheel. It still works but loses the WEAK-edge puzzle.

## 9. Delta vs today
- **Changes:**
  - HP 142 → 115 / 140 / 178 / 228.
  - One wheel becomes two designed phases with a 0.51 threshold.
  - A layout with variable slice sizes.
  - Citation becomes OUTPUT_DOWN on the pointer slice.
  - A P2 nudge listener.
- **Kept:** two needles, resistance 1 (P1 only), Citation, the Barrier / Baton / Shove roles (values rescaled FLAT), `cycle_reward` 35.
- **heat_effects: retire.** None are carried, and any existing entry is deleted rather than ported. The global Heat 50 modifier ENEMY_RESISTANCE +1 (GDD 4.3) still applies as a game rule. It adds resistance in P2 at Heat ≥ 50 and is not elite-specific.

## 10. Predicted sim check
There is no Halcyon baseline. The nearest Solace elites are Recall Unit (20.2 turns at T3, 36 at T4) and Claims Adjuster. This design targets 6–8 turns, with p90 ≤ 10 for a 2-phase elite.
- **Win %:** T1 about 97, T2 about 95, T3 about 90, T4 about 75.
- **T4 is the soft spot** because the net intake is about 46 of 60 HP.
- **Why:** per-phase budgets are built so the reference player needs about 3.5 turns each. Win rate is limited by intake.

## 11. Open questions
Q: Is P1's resistance 1 (first nudge absorbed, Flip and Respin blocked) too heavy on top of the Barrier tax? Should it drop to P1-only on Flip?
Q: Is the cap of 2 listener triggers per turn right, or should the block scale with RAM spent?
Q: Does the validator accept per-needle bands scaled by needle count, or does this elite need an authored band override?
Q: What operative HP does the sim assume at T4 (this draft assumes about 60)?
Q: Should the P2 pair offset 11 show a tick guide on the HUD?
