<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__care_swarm; status ok; tokens in 5184 cache-write 0 cache-read 32585 out 1884; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/care_swarm

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 / §4 arithmetic.** The core HP of 26/32/42/54 plus 8 for the drones is justified as "the band includes the satellites' HP", but R2 band values are enemy HP. Core HP also sits below the band (26 < 28, 32 < 34, 42 < 44, 54 < 56), and the budget table says nothing about the bodyguard tax (hits wasted on drones). The budget is 31.5/38.5/49/63. Core 26 + drones 8 = 34 against 31.5 is over budget at T1. Either the core is in band or the draft must show an explicit rule for counting satellites.
2. **BLOCKER, R2 flat scaling.** Drone HP is unscaled, and the draft itself flags this. The drone's Shim 2 is a flat enemy amount and must be multiplied by the tier factor. The §3 intake uses "≈3" at T3 (2 × 1.69 = 3.4), which is inconsistent with the table and with the stated "flat amounts × factor".
3. **MAJOR, §3 intake math.** The draft says "(2×5+8)/6 ≈ 3.0", but the core's Sting/Pulse only hit the player. The ≈1.0 drone term uses P = 2/6, yet the drones sit on the attacking slices, which are the same slots already counted. That double-counts, and the 2/6 is wrong. The sum of 4.0 is unsupported. T4 ≈ 5.2 and T1 ≈ 2.4 also don't follow from 4.0 (4.0 × 2.2/1.69 = 5.2 is fine, but 4.0 × 1/1.69 = 2.4 only if the base was already scaled correctly).
4. **MAJOR, §3 sustain.** Tend (BLOCK 4 on drone death) is a listener on satellite death. It is not covered by N6 (player-action reactions) and is not a hub rule that exists today. The draft says N6, but N6 lists player-action triggers and ON_HIT_DEALT. That is a mis-tag. Also, the Tend BLOCK is a defensive sustain source, which makes the "zero sustain" statement misleading.
5. **MAJOR, question quality (§1/§7).** With fixed drones on the two attacking slices, the best play is always "nudge off 1 and 4". A weak/no-nudge bot just eats the 8 drone HP. SWEEP-based play has no distinct payoff, so the choice is mostly dominated. Tend punishes killing drones, which makes "kill drones" nearly never right, contradicting the "kills shorten the fight" claim in §1.
6. **MAJOR, template.** §10 quotes the baseline as 3.0 / 4.2 / 6.5 / 6.5 without a source. §2 does not state a hub rule in table form or the tick-position table of the needle. NIT: "Cover" and "Sting" are placeholder names, fine.
7. **NIT, §8.** The N13 fallback says drones "may still be nudged until N13", but an existing `dock_slot` is not a fixed-satellite rule.

## Concrete fixes

- **Fix 1/2 (HP):** author core `hp_by_tier` inside the band and exclude the drones from it. Drones are 4 HP × factor (4, 5, 7, 9), counted as the guard tax:

| Tier | Core HP | Drone HP each | Total pool | Budget |
|---|---|---|---|---|
| T1 | 24 | 4 | 32 | 31.5 |
| T2 | 30 | 5 | 40 | 38.5 |
| T3 | 38 | 7 | 52 | 49 |
| T4 | 48 | 9 | 66 | 63 |

 State "pool = core + both drones, which lies in the R2 band". Alternatively, if the core must lie in the band, drop drone HP to 1 hit (HP 2).
- **Fix 2/3 (intake):** at T3 (×1.69) the Sting is 5, the Pulse is 8, and the drone Shim 2 is 3. The drone resolves only when its host slot is at the pointer, so its Shim replaces nothing. Expected intake per turn = (5 + 5 + 8 + 3 + 3) / 6 ≈ 4.0 with the drones alive, or about 3.0 once they are dead. Say that, and scale T1 (1.0) ≈ 2.4 and T4 (2.2) ≈ 5.2.
- **Fix 4 (Tend):** tag it "NEW: satellite-destroyed trigger (no N#)", keep the stated fallback (Cover BLOCK 6), and count the Tend BLOCK in §3 as defensive, not heal.
- **Fix 5:** swap Tend for a reward. When a drone dies, the core's next Cover slice is weakened (−2 BLOCK). Then killing drones helps the player.

## Keep
- Removing both HOTFIX slices and the random respawning third drone.
- The clear one-question focus: target selection through bodyguards.
- Drones fixed to the attacking slices, which makes the preview readable.
- Enrage off, and the layout summing to 30.

## Q:
- Should the pool be counted as core + drones in the band, or the core alone?
- Does a satellite-destroyed trigger belong under N6, or does it need its own N#?
- Is a Perfect window needed on the Pulse slice (e.g. size 4, no Perfect) to give nudging a second payoff?
