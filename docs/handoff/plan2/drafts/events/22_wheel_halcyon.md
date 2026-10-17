<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__22_wheel_halcyon; status ok; tokens in 6439 cache-write 0 cache-read 32007 out 2324; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_hal_public_address: Emergency Broadcast Lottery

**Mechanic:** WHEEL, corporation halcyon, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Pay Cycles to take over a city-wide emergency broadcast and spin its "Civic Notice" wheel, or pay HP and Heat to push extra nudges, because the best slices sit next to the worst.

## TerminalEventData fields
- id: `ev_hal_public_address`
- title: Emergency Broadcast Lottery
- speaker: CORPO (Halcyon voice, cheerful and bureaucratic)
- text: "ATTENTION RESIDENTS. This is a mandatory civic announcement, brought to you by your neighborhood utility. A public-address Terminal on the corner has locked onto your signal and is reading out today's Civic Notices at full volume. Each notice is a binding municipal outcome, drawn from a rotating wheel. The Terminal will let you hold the dial for a small processing fee. Thank you for your compliance."
- corporation_id: `halcyon`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Take the dial (spin the Notice wheel)**
- label: "Take the dial (-15 Cycles)"
- result_text: "The speakers crackle. Your notice is read to the whole block."
- cycle_cost: 15
- hp_cost: 0
- effects: none directly; the wheel supplies them
- reward: none
- (new) event_wheel: `wheel_civic_notice` (below), 1 free nudge, extra nudges cost 8 HP each, max 3 extra
- (new) starts_combat / combat_overrides / map_edits: none

**2. Hijack the feed (cheap, loud)**
- label: "Hijack the feed (+2 Heat), spin for free"
- result_text: "You skip the fee. The Terminal logs a tampering flag."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount 2
- (new) event_wheel: `wheel_civic_notice`, 0 free nudges, extra nudges cost 1 Heat each, max 3 extra

**3. Jam the speakers**
- label: "Jam the speakers (+10 Cycles)"
- result_text: "You sell the dead air to a block vendor who hates the noise. Nobody gets a notice today."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 10
- reward: none

## Event wheel: `wheel_civic_notice` (new, N17)
Sizes sum to 30; the pointer is a single fixed needle. The start tick comes from the `events` RNG stream (checkpointed, so no reroll by reload). Nudge ±1 tick moves the whole wheel. The landing preview shows the slice under the needle before commit.

| # | Size | Slice | Outcome |
|---|---|---|---|
| 1 | 6 | Utility Rebate | GAIN_CYCLES +30 |
| 2 | 4 | Noise Citation | MODIFY_HEAT +3; hp_cost 5 |
| 3 | 5 | Free Clinic Day | HEAL 12 (CAMPAIGN-scope HP restore on the operative) |
| 4 | 3 | Curfew Order | APPLY_STATUS CORRUPTED on one random non-NULL slice of the operative's wheel (`events` RNG), lasts the next combat |
| 5 | 6 | Public Holiday | Nothing, and MODIFY_HEAT -2 |
| 6 | 6 | Civic Merit Award | Reward: one Common Firmware (working: "Patch+"), no cost |

Sub-tick layout uses the R11 map. Slice 4 is only 3 ticks (G P G), so it is narrow. It sits between Holiday and Merit Award on the ring; order is as listed, wrapping 6 back to 1. Perfect/Good/Weak do not matter here. Only the slice under the needle counts.

**Nudge budget:** the option 1 or 2 free nudge count above, then the choice's extra-nudge cost, max 3 extra.

**Determinism:** the start tick is drawn once, at wheel open, from the `events` stream at a checkpoint. Every nudge is deterministic. The CORRUPTED slice pick is drawn at confirm from the same stream, and the preview shows "1 random slice" odds as per GDD 2.10.

## Design notes
- **Decision shape.** Slice 1 (+30 Cycles) and slice 6 (Firmware) are the good outcomes. Curfew (3 ticks) and Citation (4 ticks) are the bad ones. The ring order puts Citation beside Free Clinic and Curfew beside Holiday and Merit, so a nudge toward Merit risks Curfew. Players weigh how much an extra nudge is worth.
- **Option costs.** Option 1: 15 Cycles plus the optional HP to chase a result. Expected value is roughly 12 Cycles equivalent per spin at no nudges (area-weighted: Rebate 20 %, Clinic 17 %, Holiday 20 %, Award 20 %, Citation 13 %, Curfew 10 %), so it is break-even to slightly positive. Option 2 is free but drives Heat (about 2–5 per run) and its nudge costs push Heat further. Option 3 is a safe +10 Cycles, so skipping is never dominated.
- **Typical economy.** A router pays roughly 15–25 Cycles at T2, so +30 is a strong swing, and 8 HP per nudge is about 15 % of a Rookie's HP.
- **Interactions.** CORRUPTED from Curfew doubles RAM on that slice (R9), a real but survivable cost. Scrubber and Cold Exit Daemons interact with the Heat results. The Heat chip on the map should show the pending Heat.
- **Text keys:** `ev.hal_public_address.*` for the title, the body, three labels, six slice names and six results; the Halcyon CORPO voice with the sticker-style "NOTICE" banner above the wheel.
- **Fallback without N17:** the wheel collapses to a weighted outcome (RNG pick), but that loses the nudge decision, so it is not recommended.

## Q:
Q: Should the CORRUPTED slice from Curfew last the whole netrun instead of the next combat, to make the 3-tick slice scarier?
Q: Is a Heat-paid nudge in option 2 too punishing next to the +2 Heat entry fee, or should it be capped at 2 extra?
