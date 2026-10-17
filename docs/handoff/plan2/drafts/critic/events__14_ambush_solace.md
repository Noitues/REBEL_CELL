<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__14_ambush_solace; status ok; tokens in 3614 cache-write 0 cache-read 32585 out 1356; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/14_ambush_solace
**Verdict:** FIX

## Issues
1. **BLOCKER, template / mechanic family:** the AMBUSH stake. "the fight is lost if you end it below 40% max HP" is incoherent, because a fight won at 39% HP is both won and lost. The loss branch is undefined: "the clerk is then taken and you get the loss branch", yet `on_loss` is "none beyond normal combat defeat". It also conflicts with Q1, which asks whether Cycles are paid on a lost stake. The stake needs one clear definition.
2. **BLOCKER, systems:** the stake is invented as `combat_overrides.win_condition_min_hp_pct` with the fallback "plain victory". That is acceptable as a NEW tag, but it needs a name instead of a bare field. It also has no N# (N16 only covers `combat_overrides`). The "WITNESS" HUD line and the loss line are likewise unattached to any system.
3. **MAJOR, template / content:** choice 2 attaches a free enemy escort ("+1 enemy tag"). That is not an existing field and isn't in N16 (`next_combat_overrides` is only listed as a run-level override). Its data-only fallback (+2 Heat) is stated but changes the choice's numbers.
4. **MAJOR, rule:** choice 3's label says "−1 HP-cost scuffle" while `hp_cost` is 6, and its result text says "A small piece of the sweep still catches you". The label is wrong. "Smuggle her out blind" also gives the same −Heat payoff as choice 1 without risk.
5. **MAJOR, design (dominance):** choice 3 (−30 Cycles, −6 HP, −3 Heat) beats choice 1's Heat result (−2) at zero fight risk, and costs 30 Cycles where choice 1 pays +35 Cycles plus a Firmware. Choice 1 is only worth it for the Firmware. The numbers should make the 40% HP fail line the real price.
6. **NIT, arithmetic:** the T3 normal band of 44–56 HP is correct for R2, but Collections Agent is an existing normal. The note "elite-lite" and "~1.5× a normal reward" is unsupported, since no GDD 11 figure is cited.
7. **NIT, template:** `dispatch_clue: false` and `foreshadows` empty are fine. The title is not a duplicate. "Common Firmware (a 'Calibrated' chip)" invents content tied to R11's placeholder.

## Concrete fixes
- **Stake:** replace with "NEW: `combat_overrides.stake_min_hp_pct` = 0.40 (no N#; fallback: no stake). Win at ≥ 40% max HP: full reward. Win below 40%: the clerk is taken; pay half Cycles (+17), no Firmware, no Heat change. Normal defeat: normal run-death rules, no extra penalty." Q1 is then resolved.
- **Choice 2:** "next_combat_overrides: next fight node adds +1 Collections Agent as an extra enemy, 1 combat (N16)". The fallback is "+4 Heat becomes +6 Heat, no escort".
- **Choice 3 label:** "Pay for a quiet exit (−30 Cycles, −6 HP, −3 Heat)". To remove the dominance, change it to cycle_cost 40, hp_cost 8, Heat −2. Choice 1 then clearly out-earns it.
- **Firmware:** "one Common Firmware from the existing reward pool" (no named chip).

## Keep
Collections Agent is a thematically tight pick, and the stake is a real fight-quality test instead of pure attrition. Choices 2 and 4 are clear moral and economic anchors. Determinism is stated explicitly.

## Q:
- Should the stake threshold scale with tier (40% at T2, 50% at T4)?
- Does the clerk reappear later (a Terminal or a Safehouse) if saved?
