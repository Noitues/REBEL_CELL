<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__dosage_dispenser; status ok; tokens in 7628 cache-write 0 cache-read 32585 out 6310; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **1 (BLOCKER, HP ignored block sustain):** §4 now subtracts the BLOCK sustain per R2 using the formula (dpt − sustain) × 3.5. HP is 28 / 34 / 44 / 56, and the "+0.3 turn drift" line is deleted.
- **2 (BLOCKER, Standing Prescription needs a new hook and an invented RNG stream):** the hub rule is deleted and the design is now hub-less. Dose uses the existing `SlicePick.RANDOM_NON_NULL`, and no new RNG stream is named. N6 is no longer needed.
- **3 (MAJOR, Shim nerf, intake omits the hub, RAM tax not derived):**
  - Shim stays at today's 6 and Defrag at 5, so no unexplained nerf.
  - Intake is recomputed without the hub.
  - The RAM-tax figure is derived from stamps per turn (§3).
  - The old "3 of 5 slices by turn 3" claim is dropped.
- **4 (MAJOR, hub made steering pointless and contradicted the 1.2 stamps/turn figure):** with the hub gone, the needle position decides whether you get dosed, so steering matters. The 1.2 figure is replaced by a derived 0.43 stamps per turn.
- **5 (MAJOR, invented baseline):** the baseline column now cites only "today: 0.05 damage per turn". The unsourced turn and win figures are removed. The design target is stated as 3.5 turns.
- **6 (NIT):** the hub name is gone with the hub. The Dose B note is kept in simplified form.
- **7 (NIT, unsourced "hp 38"):** marked as unverified and to be checked against the .tres.
- **Fix 2 variants:**
  - The 7-slice variant was rejected because it needs the lifted slice cap.
  - The 6-slice layout is Dose A 5 · Shim 5 · Dose B 4 · Defrag 6 · Shim 5 · Null 5 = 30.
  - Dose B now stamps 2 slices, FLAT, so the 30 % Dose odds still carry a tax.
- **Kept:** the one question, the "you can only lose economically" framing, the slice-size intake method and the §8 fallback table.
- **Ruling conflicts:** none.

# dosage_dispenser: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage (R1, R4). Solace. It appears in L1-2 as the teaching fight for **corruption as a RAM tax** (R9), and in L5-6 as light pressure on an already-stressed economy.
- **Today's failure:** 0.05 damage per turn. It never threatens anything, and CORRUPTED as an inert self-damage trap never costs the player.
- **The one question: "Which of your slices is it dosing, and can you afford to read it?"** Each Dose stamps CORRUPTED on your wheel. Under R9 a card or nudge made while your pointer reads a corrupted slice costs 2× RAM. You choose each turn whether to steer its needle off the Doses, steer your own pointer off corrupted slices, cleanse, or just kill it.
- **Which answer shortens the fight:** burst plus steering. Dropping its needle on Null or Defrag costs it a dose, and a fast kill means few stamps ever land.
- **Distinct from siblings:**
  - Collections Agent and Billing Daemon: damage and RAM pressure.
  - Triage Unit: sustain.
  - Compliance Officer: resistance.
  - Care Swarm: multi-body.
  - Dispenser: the only normal whose threat is the corruption ledger.

## 2. Phase plan
Single phase, no threshold, no parking (R3: the only phase has no floor).

| Field | Value |
|---|---|
| Phase | 1 "Dispensing" (100 % → 0 %) |
| Needles | 1, tick 0, fixed |
| Hub | none |
| Statuses used | CORRUPTED (R9, RAM ×2) on the player's wheel, chosen by `SlicePick.RANDOM_NON_NULL` |
| Listeners | none |

**Wheel layout (R11, sum 30):**

| # | Slice | Ticks | Sub-tick map | Effect | Mode |
|---|---|---|---|---|---|
| 1 | Dose A | 5 | W G P G W | 3 damage + CORRUPTED on 1 random non-NULL player slice | damage FLAT (× tier factor); corruption FLAT 1 |
| 2 | Shim | 5 | W G P G W | 6 damage | FLAT |
| 3 | Dose B | 4 | W G G W | CORRUPTED on 2 random non-NULL player slices, no damage | corruption FLAT 2 |
| 4 | Defrag | 6 | W W G G W W | BLOCK 5 | FLAT |
| 5 | Shim | 5 | W G P G W | 6 damage | FLAT |
| 6 | Null | 5 | W G P G W | nothing | n/a |

Sum = 5+5+4+6+5+5 = **30**.

**Size notes:**
- Dose B is 4 ticks, so it has no Perfect. Its output is only ever Good or WEAK (WEAK at ×0.5, so a WEAK landing may stamp fewer slices, rounded, minimum 1).
- Defrag is 6 ticks, the widest. Its landings are mostly Good or WEAK, so its BLOCK is less reliable than it looks.
- The needle comes from the start-of-turn respin. Slice odds are proportional to size:

| Slice | P(resolves) |
|---|---|
| Dose A | 16.7 % |
| Dose B | 13.3 % |
| Shim ×2 | 33.3 % |
| Defrag | 20.0 % |
| Null | 16.7 % |

- P(any Dose) = **30 % per turn**. This is the steering question: a 1-tick nudge or a Spin/Freeze card that moves its needle off a Dose is worth RAM.
- Previews are deterministic. Which player slices get stamped is a random pick, so the preview shows odds per GDD 2.10, using the existing `RANDOM_NON_NULL` pick.

**Transition:** none.

## 3. Sustain and intake
- **Sustain:** one source, Defrag, BLOCK FLAT 5 × tier factor. It is temporary and not a heal. Expected block against the reference player is 20 % × 5 × factor:

| Tier | Factor | Sustain per turn |
|---|---|---|
| T1 | 1.0 | 1.0 |
| T2 | 1.3 | 1.3 |
| T3 | 1.69 | 1.7 |
| T4 | 2.2 | 2.2 |

  That is 11-12 % of the reference damage per turn (1.0/9, 1.3/11, 1.7/14, 2.2/18), well under the 30 % cap.
- **Intake per turn at the reference player (T1):**
  - Shim: 33.3 % × 6 = 2.0
  - Dose A damage: 16.7 % × 3 = 0.5
  - Total **2.5**
- **By tier** (× 1.0 / 1.3 / 1.69 / 2.2): **2.5 / 3.3 / 4.2 / 5.5**. Intake is above 0 at every tier (today: 0.05).
- **RAM tax, derived:**
  - Stamps per turn = 16.7 % × 1 + 13.3 % × 2 = **0.43**.
  - Over a 3.5-turn fight that is about 1.5 stamps, so about 1 corrupted slice among 5 non-NULL slices at the end.
  - Each turn your pointer reads a corrupted slice with probability about k/6 (k = corrupted count), so the tax is roughly 1 in 6 acts at 2× cost.
  - It is a steering choice, not a lock. A player who wastes turns faces up to 2 stamps per Dose B.

## 4. HP by tier
R2 normal band: 28-36 / 34-44 / 44-56 / 56-70. Budget = (reference dpt − block sustain) × 3.5 turns × 1 needle.

| Tier | Reference dpt | Sustain | Budget | HP (band floor) |
|---|---|---|---|---|
| T1 | 9 | 1.0 | (9 − 1.0) × 3.5 = 28.0 | **28** |
| T2 | 11 | 1.3 | (11 − 1.3) × 3.5 = 33.95 | **34** |
| T3 | 14 | 1.7 | (14 − 1.7) × 3.5 = 43.05 | **44** |
| T4 | 18 | 2.2 | (18 − 2.2) × 3.5 = 55.3 | **56** |

The T3 and T4 budgets fall under the band floor by under 1 HP, so HP is set to the floor. `hp_by_tier = [28, 34, 44, 56]`. Today's HP (38 in v1, unverified; check the .tres) is above the T1 band.

## 5. Enrage
**None** (normal, R4 default off). The 3-4 turn fight is short enough on its own.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads the preview and spends the free nudge to move its needle off Dose A or Dose B onto Null or Defrag.
  - Bursts it in about 3 turns with Overflow or a Perfect.
  - If a slice is corrupted, parks the pointer on a clean slice before playing cards.
  - Uses Cleanse or Encrypt on a key slice.
  - Pays 2× RAM only for a high-value Perfect.
- **Weak player:**
  - Keeps spending RAM with the pointer on a corrupted slice.
  - Spends cards defensively against 2.5 damage per turn.
  - Never steers its needle off the Doses, so stamps accumulate.
- **As a teacher:** damage is low enough that the only real loss is economic.

## 8. Systems needed
| Need | N# | Data-only fallback |
|---|---|---|
| CORRUPTED as RAM ×2 | N9 | None. This is the whole point; before N9 the fight is a weak enemy again. |
| Amount modes (FLAT; flat enemy amounts × tier factor), including corruption FLAT 2 | N1 | Authored per-tier values by hand; Dose B as two separate CORRUPTED effects |
| Tier tables (`hp_by_tier`, `enemy_damage_by_tier`) | N2 | Keep the HP multiplier |
| Variable slice sizes (5/5/4/6/5/5) | N12 | Six 5-tick slices; Dose odds become 33 % and Dose B has a Perfect |

No hub hook, no listener, no new RNG stream. N6 is not needed.

## 9. Delta vs today
- **Kept:** id, corporation, Dose/Shim/Defrag/Null vocabulary, single needle at tick 0, cycle_reward 15, Shim 6 and Defrag 5.
- **Changed:**
  - HP → `hp_by_tier` [28, 34, 44, 56].
  - Slice sizes 5×6 → 5/5/4/6/5/5.
  - Dose A gains 3 damage.
  - Dose B becomes pure corruption on 2 slices.
- **Heat effects:** none present, none added.
- **Description:** "Stamps CORRUPTED on your wheel; every corrupted slice doubles what you pay."

## 10. Predicted sim check
Today: 0.05 damage per turn (BASELINE). No other baseline figures are claimed.

| Tier | Turns (pred.) | Win % |
|---|---|---|
| T1 | 3.5 | ~100 |
| T2 | 3.5 | ~100 |
| T3 | 3.6 | ~99 |
| T4 | 3.7 | ~97 |

**Why:**
- HP follows the phase budget, so 3.5 turns is the design target.
- Intake rises from 0.05 to 2.5-5.5 per turn.
- The RAM tax is mild (about 0.43 stamps per turn), so wins stay ≥ 95 % at T1-T2 and ≥ 90 % at T3-T4.
- Without N9 the tax disappears, and only the damage is left as pressure.

## 11. Open questions
Q: Is 30 % Dose odds with 0.43 stamps per turn enough tax to teach corruption at L1-2?
Q: Should Dose B's FLAT 2 corruption cap at a share of the wheel so a 4-turn fight cannot lock a player?
Q: Does the free nudge on a corrupted slice cost 1 RAM (R9 doubles RAM for paid actions)?
Q: Does an L1-2 player read the corrupted-slice RAM tax without a tutorial tooltip?
Q: Do ENCRYPTED player slices fully block the stamp, or does Dose B still count a stamp against them?
