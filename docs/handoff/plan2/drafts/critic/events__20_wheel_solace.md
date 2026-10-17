<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__20_wheel_solace; status ok; tokens in 3623 cache-write 0 cache-read 32585 out 1840; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/20_wheel_solace
**Verdict:** FIX

## Issues
1. **BLOCKER, Template/choice fields, choice 2:** the effect is "MODIFY_HEAT -1" for a 40-Cycle payment, while the result text promises "a stranger's key fob" with no reward. The fob is an unlisted reward and the text contradicts the data. Paying 40 for -1 Heat is also dominated by the wheel (see 4).
2. **BLOCKER, R11 / Wheel table:** the sub-tick claim is wrong. Size 3 reads G P G, so Debt Forgiven and Referral have no WEAK ticks. The text says "WEAK on Hardship Grant pays 12" but a 5-tick slice's WEAK ticks are the outer two, which is fine. The rule "GOOD or better pays in full" is then trivially true for slice 1. The design note "Both extremes are narrow" confuses quality with slice width. Sizes do sum to 30 (3+5+6+7+6+3).
3. **MAJOR, Adjacency/wrap:** the notes say "Debt Forgiven is adjacent to Referral on the wrap (tick 0 / 29)". With the table order, slice 1 spans ticks 0-2 and slice 6 spans 27-29, so they are adjacent. Fine, but the notes then claim "two hazard slices flanking the jackpot". Only one flank is hazardous: slice 2 is Hardship Grant, a gain. The hazard framing is overstated.
4. **MAJOR, EV and dominance:** by tick weight the EV is (3×45 − 3×1·Heat + 5×25 + 7×(−20) + …)/30 ≈ +4 to +9 Cycles, with Heat penalties on top. The design note says +9 "ignoring the fight tail". Late Penalty (+3 Heat, 6 ticks) and Referral (+1 Heat plus a fight) cost real Heat. Net Heat EV is about +0.8 per spin, so the wheel is roughly neutral, while Walk away is free. Nothing in the numbers shows why anyone spins at T1; the free first nudge is the only edge. State the EV honestly.
5. **MAJOR, Nudge budget text:** "2 free nudges" conflicts with the choice label "free first nudge" and with the GDD rule that the first nudge is free and the rest cost. Also, "up to 4 extra" at 3 HP each is 12 HP for a ±6-tick reach. That reaches most of the wheel from any start, so the preview makes the wheel a menu purchase, not a gamble.
6. **MAJOR, Choice 3 (new) field:** "enemy `collections_agent` added as an extra enemy" and "+1 start-of-fight Block" are not a precise override list. The stake is trivial, so Wipe (+2 Heat plus a harder fight) is clearly dominated by Walk away. Heat payoff is absent, so the choice has no upside.
7. **MAJOR, Systems:** the slice effects use "MODIFY_HEAT 3" and "GAIN_CYCLES 45" correctly, but "Referral" `starts_combat` lacks an overrides/stake field. No N# is tagged for `starts_combat` (N16). The fallback says "flat 3-outcome choice" without listing the outcomes.
8. **NIT:** Q1 is already answered by the draft (it wraps). A Heat-on-fight rule is undecided.
9. **NIT:** "Smile, subbie." works, but the text is 5 sentences plus a fragment.

## Concrete fixes
- **Choice 2:** result_text: "The balance clears. Okafor's file closes with a stamped SETTLED." Set cycle_cost 25, MODIFY_HEAT −2, so it competes with the wheel's best-case profit.
- **Wheel quality:** Debt Forgiven (size 3) pays full on any tick (G P G). Add a bonus: PERFECT (centre tick) pays 60 Cycles. Hardship Grant (size 5, W G P G W): WEAK pays 12, GOOD 25, PERFECT 35.
- **Budget:** 1 free nudge, then extra nudges cost 3 HP or 1 Heat (player's pick), up to 3 extra.
- **Choice 3:** `next_combat_overrides`: {combat_type: any Router; extra_enemy: `collections_agent`; reward_multiplier: ×1.5 Cycles; duration: 1 combat}. Keep MODIFY_HEAT +2.
- **Referral slice:** `starts_combat`: {enemy: `collections_agent`, overrides: none, stake: normal rewards, +1 Heat on entry}. Tag it N16.
- **Fallback:** replace choice 1 with: 40 % +25 Cycles, 40 % nothing, 20 % +3 Heat, each previewed as odds.

## Keep
- The wrap adjacency, where the jackpot sits next to the fight, is a good tension.
- The Referral slice leads into a real fight without a new enemy id.
- A deterministic `events` RNG with checkpoint and undo is correct.

## Q:
Q: Should PERFECT on the 3-tick jackpot pay extra, given it needs an exact pointer landing?
Q: Is Heat the right currency for the second nudge cost, given the +3 Heat Late Penalty slice?
