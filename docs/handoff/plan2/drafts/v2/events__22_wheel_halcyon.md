<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__22_wheel_halcyon; status ok; tokens in 5194 cache-write 0 cache-read 32585 out 3540; cost $0.026. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, odds/EV unproven)** -> Odds are now re-derived from the new ring (Rebate 6/30 = 20 %, Curfew 3/30 = 10 %, Merit 6/30 = 20 %, Citation 4/30 = 13.3 %, Clinic 5/30 = 16.7 %, Holiday 6/30 = 20 %, total 100 %). The EV is worked out line by line with explicit values for Firmware, HEAL and Heat, in a table. The invented "~12" claim is dropped and replaced by the derived figure.
- **Issue 2 (BLOCKER, second random draw at confirm)** -> The Curfew target slice is drawn once at wheel open, in the same `events` checkpoint as the start tick. The wheel UI marks that slice. Nothing random happens after the checkpoint, so preview equals result.
- **Issue 3 (MAJOR, adjacency false)** -> Ring reordered as the critic specified: Rebate 6 · Curfew 3 · Merit 6 · Citation 4 · Clinic 5 · Holiday 6. Curfew now sits between the two best slices (Rebate and Merit). The one-liner and notes state only true adjacencies, wrap included (Holiday neighbors Rebate).
- **Issue 4 (MAJOR, option 2 beats option 1)** -> Option 1 now has 2 free nudges and extra nudges cost 8 HP, max 2. Option 2 has 1 free nudge and extra nudges cost 2 Heat each, max 2, plus the +2 Heat entry. Option 2's cheapest full play costs 2 + 4 = 6 Heat, which is real. Option 3 is shown against the derived EV.
- **Issue 5 (MAJOR, systems)** -> HEAL is now target SELF. The Curfew status is applied at resolution through the wheel outcome, with the remainder of the netrun scoped by a `next_combat_overrides`-style duration (N16). Slice outcomes are written as EffectData-style rows, with hp_cost as a separate (new) line. Each slice carries an N17 tag. The fallback is now data-only: three split choices.
- **Issue 6 (NIT)** -> HP percentages use Breaker 60 HP (8 HP = 13 %). "Terminal" capitalization is made consistent. The text is kept to 5 sentences.
- **Keep list** -> Kept the three-way structure with a safe skip, the legible slice sizes, the Heat-for-nudge currency and the CORRUPTED/R9 tie.
- **Critic Q1 (show start tick before paying)** -> Decided: yes, the start tick and marked Curfew slice are shown on a locked preview before the fee is paid. Option 1 and 2 labels show it, and the preview is deterministic, so this is safe.
- **Critic Q2 (cap Heat nudges at 2)** -> Adopted: max 2 extra.
- **Ruling check:** nothing here conflicts with a designer ruling.

# ev_hal_public_address: Emergency Broadcast Lottery

**Mechanic:** WHEEL, corporation halcyon, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Pay Cycles for a steadier hold on the city's notice dial, or pay Heat for a looser one, knowing the 3-tick Curfew sits between the two best slices.

## TerminalEventData fields
- id: `ev_hal_public_address`
- title: Emergency Broadcast Lottery
- speaker: CORPO
- text: "ATTENTION RESIDENTS. This is a mandatory civic announcement, brought to you by your neighborhood utility. A public-address terminal on the corner has locked onto your signal and is reading out today's Civic Notices at full volume. Each notice is a binding municipal outcome, drawn from a rotating dial. The terminal will let you hold the dial for a small processing fee. Thank you for your compliance."
- corporation_id: `halcyon`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Take the dial**
- label: "Take the dial (-15 Cycles)"
- result_text: "The speakers crackle. Your notice is read to the whole block."
- cycle_cost: 15
- hp_cost: 0
- effects: none directly; the wheel supplies them
- reward: none
- (new) event_wheel: `wheel_civic_notice`, 2 free nudges, extra nudges cost 8 HP each, max 2 extra (N17)
- (new) starts_combat / combat_overrides / map_edits: none

**2. Hijack the feed**
- label: "Hijack the feed (+2 Heat)"
- result_text: "You skip the fee. The terminal logs a tampering flag."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount 2
- (new) event_wheel: `wheel_civic_notice`, 1 free nudge, extra nudges cost 2 Heat each, max 2 extra (N17)

**3. Jam the speakers**
- label: "Jam the speakers (+10 Cycles)"
- result_text: "You sell the dead air to a block vendor who hates the noise. Nobody gets a notice today."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 10
- reward: none

## Event wheel: `wheel_civic_notice` (N17)
Ring order (wraps Holiday → Rebate), sizes sum 6+3+6+4+5+6 = 30. One fixed needle. Nudge ±1 tick rotates the whole wheel; only the slice under the needle counts, so sub-tick quality is irrelevant.

| # | Size | Slice | Outcome | Neighbors |
|---|---|---|---|---|
| 1 | 6 | Utility Rebate | GAIN_CYCLES, CAMPAIGN, +30 | Holiday, Curfew |
| 2 | 3 | Curfew Order | APPLY_STATUS CORRUPTED on the pre-marked slice of the operative's wheel, until the end of the netrun (N16 duration; R9: that slice costs 2× RAM) | Rebate, Merit |
| 3 | 6 | Civic Merit Award | Reward: one common Firmware (working: "Patch+") | Curfew, Citation |
| 4 | 4 | Noise Citation | MODIFY_HEAT, CAMPAIGN, +3; (new) hp_cost 5 | Merit, Clinic |
| 5 | 5 | Free Clinic Day | HEAL, SELF, 12 | Citation, Holiday |
| 6 | 6 | Public Holiday | MODIFY_HEAT, CAMPAIGN, -2 | Clinic, Rebate |

**Nudge budget:** per choice above (2 free + 2 extra at 8 HP, or 1 free + 2 extra at 2 Heat).

**Determinism:** on opening the choice screen, one draw from the `events` stream at a checkpoint fixes both the start tick and the non-NULL slice that Curfew would corrupt (marked on the operative's wheel in the preview). The start tick is previewed before any fee is paid. After that, no randomness: every nudge and the final result are deterministic, and preview equals result.

## Design notes
- **Decision shape.** Rebate and Merit, the two best slices, flank the 3-tick Curfew, so nudging between them risks the worst landing. Citation is the only other hazard and sits beside Merit. A good start tick makes extra nudges pointless; a bad one makes them worth buying.
- **Derived EV at zero nudges** (placeholder values: Firmware ≈ 25 Cycles, 1 HP ≈ 1 Cycle, 1 Heat ≈ 5 Cycles, Curfew ≈ −15 Cycles):

| Slice | P | Value | Contribution |
|---|---|---|---|
| Rebate | 0.200 | +30 | +6.0 |
| Curfew | 0.100 | −15 | −1.5 |
| Merit | 0.200 | +25 | +5.0 |
| Citation | 0.133 | −5 HP −15 (3 Heat) = −20 | −2.7 |
| Clinic | 0.167 | +12 | +2.0 |
| Holiday | 0.200 | +10 (2 Heat) | +2.0 |

  EV ≈ +10.8 Cycles-equivalent. Option 1 nets about −4 before nudges (15 fee), so it only pays when nudges steer away from bad slices; this is the intended gamble. Option 2 costs 2 Heat (≈ −10) for the same EV: roughly break-even, with up to 4 more Heat if nudging (total 6 Heat ≈ −30). Option 3 is a guaranteed +10 Cycles, so it matches the raw EV and is the safe line.
- **Typical economy.** A router pays about 15–25 Cycles at T2, so +30 is a strong swing. 8 HP is 13 % of a Breaker's 60 HP.
- **Interactions.** Scrubber and Cold Exit interact with the Heat outcomes; the map Heat chip should show pending Heat. Curfew's CORRUPTED is a RAM tax, not damage, so it is survivable.
- **Text keys:** `ev.hal_public_address.*` for the title, body, three labels, six slice names and six results; a sticker-style "NOTICE" banner above the wheel.
- **Fallback without N17 (data-only):** three choices that each commit to a fixed slice: "Claim the rebate" (-15 Cycles, +30 Cycles), "Take the clinic day" (HEAL 12), and "Jam the speakers" as above. That loses the nudge gamble.

## Q:
Q: Should Curfew's CORRUPTED last the whole netrun (as written) or only the next combat, if testers find 3 ticks plus a netrun-long tax too harsh?
Q: Should the shown start tick make a "bad start" reason to walk away, or should the preview wait until payment to keep the gamble alive?
