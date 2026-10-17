<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__dead_drop; status ok; tokens in 5540 cache-write 0 cache-read 32585 out 1529; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/dead_drop

**Verdict:** FIX

## Issues

1. **BLOCKER, R11/arithmetic, §2 layout:** the ticks are 6+4+5+5+6+4 = 30, so the sum is fine. But the tick maps do not follow the R11 defaults. Slice 0 (6 ticks) is W W G G W W, which matches the default. Slice 4 (6 ticks) matches too. The real problem is the Perfect claim: "Pickup ... Handoff has none either" is true for 4-tick and 6-tick slices, but "the only Perfect on the enemy wheel is on Cache" leaves a 5-tick slice, Dose, unaddressed. Dose is also a 5-tick slice with a Perfect, so the claim is false. Fix the text, or make Dose a 4-tick slice.
2. **BLOCKER, R2/§4 arithmetic:** the HP budget ignores the pointer rule and the drone soak, and the "trimmed below budget" claim is unquantified. T3 budget 49 − 4.2 = 44.8, but 46 is chosen, which is above the budget. T4: 63 − 5.3 = 57.7, but 58 is chosen. The note says HP is trimmed below, yet the T3/T4 values exceed the budget.
3. **BLOCKER, §3 sustain math:** the Stash shield is 12 % of max HP per landing, and the landing odds are 6/30 = 0.2. The sustain at T4 (1.5 per turn) is not derived: 12 % of 58 = 7, × 0.2 = 1.4. It is also a SHIELD (lingering), and the draft's own Q asks whether it stacks, so the cap is unresolved. Cache's BLOCK, though not healing, absorbs damage and is a second defense source. The brief says at most one source.
4. **MAJOR, R2 flat scaling:** "Shim 9 FLAT" is given only for T1. The intake rows scale by ×1.69 and ×2.2, which is the damage table, so that part is OK. But the drone HP is stated as "6 ... ×tier damage factor", and the Q then asks whether it is fixed. The draft contradicts itself.
5. **MAJOR, invented/unverified content:** the draft assumes the echo_drone.tres contents ("I have not seen its file"). The "Undock card" Q is also speculative. Intake of "about 0.5 from the drone" is unsupported.
6. **MAJOR, design/R12:** the "weak player" is told "steering the player's own pointer is the only fix", while §1 says to "kill the drone with one cheap hit". With max_active 1 and a drone spawning every 2 turns, REPLACE respawns it, so killing it only buys a turn. The "3 turns" path is not shown.
7. **NIT:** the Dose "10 % per turn" is wrong. Slice 3 is 5/30 = 16.7 %, not 3/30. The §3 text also says "3/30".
8. **NIT:** the Perfect on Cache is a dead choice, since nothing rewards it.

## Concrete fixes

- Issue 1: change the line to "Cache (5 ticks) and Dose (5 ticks) keep the W G P G W map; neither Perfect rewards the player."
- Issue 2, rebuilt HP: T1 28, T2 34, T3 44, T4 56 (the band minima, since drone soak removes damage from the body).
- Issue 3: delete the BLOCK on Cache. Make slice 2 (5 ticks) a SHIM 6 FLAT. Then Stash is the sole sustain, and it is a SHIELD, not a heal. State "stacks to cap 15; sustain = 0.2 × 12 % × HP ≈ 1.2/turn at T3".
- Issue 4: set the drone HP to FLAT 6 × the tier damage factor (6 / 8 / 10 / 13) and remove the Q.
- Issue 7: Dose = 5/30 = 16.7 % per turn.

## Keep

- A spatial question distinct from its siblings.
- Dose retired as damage and kept as a RAM tax (R9).
- max_active 1 bounds the soak.
- The N12/N1/N13 fallbacks are stated.

## Q:

1. Should the Stash SHIELD stack, or refresh to a cap?
2. Does REPLACE count the destroyed drone for Daemons?
3. Is one drone per 2 turns too slow to matter against a 3-turn fight?
