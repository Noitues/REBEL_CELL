<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__loyalty_test; status ok; tokens in 6656 cache-write 0 cache-read 32585 out 6391; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Critic 1 (BLOCKER, no Perfect payoff):** fixed with a Perfect payoff for the player. The enemy gets a hub rule, **Vetting**: hits that come from a non-Perfect landing do ×0.75 to it. Report (4 flat) now taxes the Perfect that Vetting rewards. Always-Perfect finishes faster and costs more; Good-only is cheaper per turn but takes longer. This is the real tension the critic asked for. Vetting is NEW (small), with a stated fallback (§8).
- **Critic 2 (BLOCKER, geometry):** scratch notes deleted and the layout rebuilt as a clean table with explicit tick spans, centres and sub-tick maps. Sizes re-added: 6+4+5+5+4+6 = 30. Each slice's centre is recomputed.
- **Critic 3 (MAJOR, HP budget):** the "two Audit slices" sentence is removed (one needle). The budget arithmetic is now shown against Vetting's effective damage multiplier. HP drops to 30/36/46/58, so turns stay at 3.8-3.9.
- **Critic 4 (MAJOR, intake):** the critic's per-tier numbers are adopted (6.8 / 8.8 / 11.5 / 15 unsteered). §10 now uses the same figures, including T4, and shows the win-rate reasoning.
- **Critic 5 (MAJOR, Report rule):** decided. Report is a normal non-pierce hit that resolves as part of the enemy's attack resolution. BLOCK and SHIELD absorb it, and a SANDBOX that negates that resolution negates Report too. This closes the old Q.
- **Critic 6 (NIT):** claims about the current `.tres` are marked "per v1 notes, verify".
- **Critic 7 (NIT):** the N6 fallback is stated plainly: a plain damage wheel.
- **Kept, because the critic marked them strong:** Report as a readable listener with a preview chip, no sustain, HP inside bands, the Overflow slice with no Perfect, and the honest "no baseline" flag.

# loyalty_test: direct design

## 1. Identity & the one question
**Class:** Normal, 1 phase, 3-4 turns, no enrage. **Corporation:** REBEL_CELL. **Layers:** L5-6 pressure. REBEL_CELL is an unlock corporation, so it has no L1-2 teaching role. It is a fast check that the player controls their own wheel.

**The one question:** "Is the Perfect worth the tax?"
- **Vetting (hub rule):** damage from any non-Perfect landing is ×0.75 against this enemy. A Perfect landing does full damage and triggers class hooks.
- **Report (listener, N6, ON_PERFECT):** every Perfect you land on your own wheel hits you for 4 FLAT (× tier damage factor).
- **Which answer shortens the fight:** Perfect-heavy play kills about half a turn sooner and pays 4 per Perfect. Good-only play pays no tax but runs about 0.5 turn longer, and the enemy's intake is about 7 per turn. Steering costs the free nudge plus 1 RAM for each extra tick.
- **Class dependence:** classes with a strong Perfect hook (Breaker's double resolve) take the tax gladly. Classes without one choose per turn.

**Distinct from siblings:** Mirror Script and Echo Process copy your wheel. The Handler's Echo replays your landed slice at 50 %. This is the only normal that both rewards and taxes Perfects.

## 2. Phase plan
One phase, no threshold, no floor. One needle at tick 0.

| Slot | Ticks (span) | Size | Centre | Sub-tick map | Effect | Mode |
|---|---|---|---|---|---|---|
| Audit (Shim) | 0-5 | 6 | 2.5 | W W G G W W | Deal 9 | FLAT |
| Null | 6-9 | 4 | 7.5 | W G G W | none | n/a |
| Clearance (Defrag) | 10-14 | 5 | 12 | W G P G W | BLOCK 8 | FLAT |
| Audit (Shim) | 15-19 | 5 | 17 | W G P G W | Deal 9 | FLAT |
| Verdict (Overflow) | 20-23 | 4 | 21.5 | W G G W | Deal 14 | FLAT |
| Null | 24-29 | 6 | 26.5 | W W G G W W | none | n/a |
| **Sum** | | **30** | | | | |

- **Perfect on its own wheel:** only the 5-tick Audit and Clearance slices can read Perfect. Verdict (the big hit) has no Perfect tick.
- **Hub rule, Vetting:** damage dealt to it by non-Perfect landings is ×0.75. The preview shows a "VETTED −25 %" chip.
- **Listener, Report:**
  - It fires once per Perfect, at the end of the enemy's attack resolution.
  - It is a non-pierce 4 FLAT hit, so BLOCK and SHIELD absorb it.
  - A SANDBOX that negates the enemy's resolution negates Report too.
  - The preview shows "REPORT −4" and is undo-clean.
- **Statuses and parasites:** none. **Transition:** none.

## 3. Sustain and intake
**Sustain:** none, so 0 % of reference damage. Clearance is a pointer-turn BLOCK, not a heal.

**Intake, unsteered** (the wheel respins at turn start, so the needle is random):
- Audit covers 11/30 = 36.7 % × 9 = 3.3. Verdict covers 4/30 = 13.3 % × 14 = 1.9. Raw ≈ 5.2.
- Report adds about 0.4 × 4 = 1.6 for a player who lands Perfect 40 % of the time. Total ≈ 6.8 at T1.
- Scaled by the damage factors 1.3 / 1.69 / 2.2 (flat amounts scale per R2): **T1 ≈ 6.8, T2 ≈ 8.8, T3 ≈ 11.5, T4 ≈ 15** per turn.
- A steering player cuts raw intake to about 2-3 by parking the needle on Null or Clearance. Intake is above 0 at every tier.

## 4. HP by tier
Band for a normal enemy (R2): T1 28-36, T2 34-44, T3 44-56, T4 56-70.

**Arithmetic.** The reference budget is dpt × 3.5 turns: 31.5 / 38.5 / 49 / 63. Vetting makes the reference player's effective multiplier ≈ 0.4 × 1.0 + 0.6 × 0.75 = 0.85. I set HP just inside the band and check turns = HP / (dpt × 0.85).

| Tier | hp_by_tier | Effective dpt | Turns |
|---|---|---|---|
| T1 | 30 | 9 × 0.85 = 7.65 | 3.9 |
| T2 | 36 | 11 × 0.85 = 9.35 | 3.85 |
| T3 | 46 | 14 × 0.85 = 11.9 | 3.9 |
| T4 | 58 | 18 × 0.85 = 15.3 | 3.8 |

An all-Perfect player ends it in about 3.3 turns; an all-Good player in about 4.4. The reference player lands inside the 3-4 target.

## 5. Enrage
None (normal class default is off). The fight has no defense or heal worth stalling on, and an all-Good player is bounded at about 4.4 turns.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Takes the Perfect when it also does something the fight needs: a class hook, lethal, or breaking Clearance.
  - Otherwise lands Good and accepts a slower kill.
  - Steers the needle to Null or Audit's WEAK edge, and SANDBOXes a turn where Verdict (14) is likely.
  - Reads the Report chip before committing.
- **Weak player:**
  - Chases Perfects on every pointer and pays the tax every turn.
  - Or never takes a Perfect and drags the fight out.
  - Wastes a hit into Clearance's 8 BLOCK.

## 8. Systems needed
- **N6** (enemy listener, ON_PERFECT): for Report.
- **N12** (slice sizes 4/5/6, sub-tick map): for the layout. **Fallback without N12:** six 5-tick slices (Audit, Null, Clearance, Audit, Verdict, Null). Verdict then has a Perfect, which weakens the "no Perfect on the big hit" read.
- **N1** (flat amounts × tier factor) and **N2** (`hp_by_tier`).
- **NEW: Vetting** (an incoming-damage modifier keyed on landing tier, a hub field read in `deal_hit`; size S). **Fallback without Vetting:** drop it and restore HP to 32 / 39 / 50 / 63. The question then reduces to "hook value vs 4 tax", which is weaker.
- **Fallback without N6:** a plain damage wheel with no question.

## 9. Delta vs today
Claims about the current file come from v1 notes and need verification against the `.tres`.
- **Removed (per v1 notes):** the Hotfix 6 sustain and the Solar Flare, which is Orbital content.
- **Kept:** Shim, Defrag, Overflow, Null and the single needle at tick 0.
- **Changed:**
  - HP 54 → [30, 36, 46, 58].
  - The layout uses sizes 6/4/5/5/4/6.
  - Shim 12 → 9 and Overflow 16 → 14, to offset the Report tax.
  - Added Vetting and Report.
- **heat_effects:** none known; verify. `cycle_reward = 15` stays. Description becomes "Taxes your Perfects. Rewards them too."

## 10. Predicted sim check
No baseline row exists (the sweep covered Solace only), so this is an estimate.
- **Turns:** about 3.8-3.9 at the reference player at every tier (§4). The bot's best play (16-35 dpt) ends it in about 2.
- **Win %:**
  - About 97 % at T1, 96 % at T2, 92 % at T3 and 88 % at T4.
  - Unsteered intake over about 3.9 turns is about 27 / 34 / 45 / 58 at T1-T4. That is the lethal-pressure case, which a steering player cuts by half or more.
  - At T4 an operative with 45-60 HP needs steering to survive, hence the lower win rate.
- **Why:** one short phase and no sustain, so the fight ends before attrition. Vetting and Report are the only variance.

## 11. Questions
Q: Is Vetting at ×0.75 enough payoff, or should it be ×0.6, given that nudging to Perfect already costs RAM?
Q: Should Report fire for a Perfect landed on a satellite or drone slice, or only on your own wheel's pointers? (I chose pointers only.)
Q: Does Vetting need a visible hub-style badge on the enemy, or is the preview chip alone enough?
Q: Is the 4 FLAT tax too small against a Breaker's double resolve? A 7 % max-HP PERCENT mode would bite harder.
