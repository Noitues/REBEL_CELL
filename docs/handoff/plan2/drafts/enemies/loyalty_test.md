<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__loyalty_test; status ok; tokens in 16046 cache-write 0 cache-read 32007 out 3417; cost $0.036. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# loyalty_test: direct design

## 1. Identity & the one question
**Class:** Normal, 1 phase, 3-4 turns, no enrage. **Corporation:** REBEL_CELL. **Layers:** L5-6 pressure. REBEL_CELL is the unlock corporation, so L1-2 teaching does not apply. It is a fast check on whether the player is in control of their own wheel.

**Concept:** a test of loyalty. The enemy answers your *greedy* play. It does not guard itself or heal. It punishes the player who lands the biggest possible hit, and rewards the one who takes the safe Good.

**The one question:** "Do you take the Perfect, or the safe landing?"
- A listener, **Report** (N6, ON_PERFECT): each time you land a Perfect on any pointer of your own wheel, it hits you for a small flat amount (4 × tier damage factor). It fires once per Perfect, never at 0 resolutions.
- The Perfect still pays. The Perfect hook and damage are the player's burst, and the fight is 3-4 turns, so a Perfect-heavy player kills it fast and eats about 4-8 damage. A cautious player takes Good, loses little damage (Good is 1.0×, the same as Perfect, per GDD 2.4), and takes no Report damage. Only class hooks and Perfect-based effects are lost.
- **Which answer shortens the fight:** Good landings do the same raw damage, so the real choice is hooks. Breaker (double resolve) takes more Report but ends it faster. This asks a cost question, not an attrition one.

**Distinct from siblings:** Mirror Script and Echo Process copy or echo your wheel. Handler Proxy and the Handler hold the shadow or mirror theme. Loyalty Test is the only normal with a *punish-on-Perfect* listener. The Handler's Echo (P2) also reacts to Perfects, but at 50 % replay and on a mini-boss. This one is a flat tax on the best landing and a simple read.

## 2. Phase plan
**One phase, no threshold, no floor.** One needle, tick 0.

| Slot | Size | Effect | Mode |
|---|---|---|---|
| Shim (Audit) | 6 | Deal 9 | FLAT |
| Null | 4 | none | n/a |
| Defrag (Clearance) | 5 | BLOCK 8 | FLAT |
| Shim (Audit) | 5 | Deal 9 | FLAT |
| Overflow (Verdict) | 4 | Deal 14 | FLAT |
| Null | 6 | none | n/a |
| **Sum** | **30** | | |

Layout in ticks, clockwise from tick 0 (slice centres): Audit 3, Null 8, Defrag 12.5→ use 13 (ticks 10-14), Audit 18 (15-19... ), see the cumulative boundaries below.

- Audit 0-5 (centre 2.5 → ticks 2/3 are G/G; a 6-tick slice reads W W G G W W, no Perfect).
- Null 6-9 (4 ticks).
- Defrag 10-14 (5 ticks, centre 12, W G P G W).
- Audit 15-19 (5 ticks, centre 17, has a Perfect).
- Overflow 20-23 (4 ticks, centre 21.5, no Perfect: W G G W).
- Null 24-29 (6 ticks).

So the two heavy slices differ in readability: the big **Overflow has no Perfect**, so it is never a "Perfect-landed" slice and Report never involves it. The needle at tick 0 sits on the Audit 6-slice's WEAK edge, so the natural resting position is weak.

- **Hub rule:** none.
- **Statuses:** none. **Parasites:** none.
- **Listener (N6):** Report. Trigger ON_PERFECT, player-owned wheel only, result: deal 4 FLAT (× tier factor) to the player. Not pierce. A SANDBOX negates it as one resolution of the listener's hit. Preview shows "REPORT −4" on the Perfect landing, undo-clean.
- **Transition:** none.

## 3. Sustain and intake
**Sustain:** none. The Hotfix is removed. Block is a one-off 8 FLAT on a 5-tick slice, which is a defense on the pointer turns it lands, not a heal. 0 % of reference damage.

**Intake at the reference player** (needle random each turn, wheel respins at turn start; the player nudges it):
- Per-turn probabilities by tick share: Audit 11/30 (9 each, so 36.7 %×9), Overflow 4/30 (13.3 %×14), Defrag/Null 0 damage. Expected raw ≈ 0.367×9 + 0.133×14 ≈ 3.3 + 1.9 = 5.2 per turn at T1.
- Perfect Report: the reference player lands a Perfect about 40 % of the time on a Perfect-capable slice, for about 1.6 per turn expected, giving a total intake of about **6-7 per turn at T1**, T3 ×1.69 ≈ 11. Over 3-4 turns this is about 20-25 damage at T1 and 35-40 at T3. It is above 0.
- With nudging (a good player steers to Null or Defrag): about 2-3 per turn. A player who skips Perfects pays no Report damage.

## 4. HP by tier
Normal (1 phase) band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. No sustain, so the budget is the full reference damage.

Phase budget: reference_dpt × 3.5 turns = T1 9×3.5 ≈ 32 · T2 11×3.5 ≈ 38.5 · T3 14×3.5 = 49 · T4 18×3.5 = 63. Current 54 flat is above T1/T2 bands.

| Tier | hp_by_tier |
|---|---|
| T1 | 32 |
| T2 | 39 |
| T3 | 50 |
| T4 | 63 |

All inside the bands. Both Audit slices can resolve on a landing, so there are two ways the enemy attacks, but its HP is for its own needle count (one), so no extra needle scaling.

## 5. Enrage
**None.** Normal class default is off. The fight is short, and a stall is not possible: the enemy has no defense or heal worth stalling on.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** reads the Report cost before the landing. On a Perfect that also wins the turn (lethal or a class hook that matters), takes it. Otherwise, nudges one tick to Good and keeps their HP. Steers the enemy's needle to a Null or onto Audit's WEAK edge at tick 0-1, which halves the 9. SANDBOX on an Overflow turn.
- **Weak player:** chases Perfects every turn without checking Report, and also leaves the enemy needle on the 14 Overflow. They also forget Defrag is an 8 BLOCK on the slice at tick 12 and waste a hit into it.

## 8. Systems needed
- **N6** (enemy listener, ON_PERFECT): required for Report.
- **N12** (slice sizes 4/5/6 and sub-tick map): required for the layout above. **Fallback without N12:** six 5-tick slices (Audit, Null, Defrag, Audit, Overflow, Null). It stays playable, but the Overflow then has a Perfect and the "never Perfect" read is lost.
- **N1** (flat amounts × tier damage factor) and **N2** (`hp_by_tier`): required.
- Data-only fallback for N6: none exists. Without it, the enemy has no question and falls back to a plain damage wheel, which fails the one-question rule.

## 9. Delta vs today
- Removed: Hotfix 6 (the sustain), and the Solar Flare (it is Orbital content, on a REBEL_CELL enemy, and was a stray).
- Kept: Shim, Defrag, Overflow, Null, and the single needle at tick 0.
- Changed: HP 54 → [32, 39, 50, 63]. Layout has sizes 6/4/5/5/4/6. Added Report.
- Reduced Shim from 12 to 9 and Overflow from 16 to 14 so that the Report tax plus attacks gives similar total intake, not more.
- **heat_effects:** none on the current file, so nothing to keep or retire. `cycle_reward = 15` stays. `description` becomes "Punishes your Perfects."

## 10. Predicted sim check
No baseline row (the sweep covered Solace only), so this is an estimate from the wheel.
- **Turns:** about 3.5 at the reference player at all tiers (HP is tied to reference damage). A bot at 16-35 damage per turn ends it in 2-3.
- **Win %:** about 97 % at T1, 96 % at T2, 93 % at T3, and 90 % at T4. The losses come from intake of about 11-14 per turn at T3-T4 stacking on carried HP, not from the fight length.
- **Why:** no sustain and one short phase, so the fight ends before attrition. The Report tax is the only soft risk.

## 11. Questions
Q: Should Report fire on a Perfect landed on the enemy's wheel by a card or nudge effect, or only on your own wheel's resolution? I chose own-wheel resolution only (one resolve, preview-clean).
Q: Is a flat 4 tax too weak to change play against classes with Perfect hooks (Breaker doubling the slice)? A PERCENT of your max HP (about 7 %) would be a harder question, but it would not scale like the other values.
Q: Does a SANDBOX negating the Report's hit count as "negating a whole attack", or does a listener hit sit outside the resolution?
Q: Should the Overflow 4-tick slice stay without a Perfect, or does the tester feel it makes the best hit too safe to read?
