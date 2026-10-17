<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__21_wheel_meridian; status ok; tokens in 5093 cache-write 0 cache-read 32585 out 3476; cost $0.026. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, pointer start):** Deleted "starts on tick 0" and the "center of slice 1" claim. The start tick is now one `events` stream draw in 0-29, checkpointed before the first nudge. Explicit tick ranges are listed per slice, and the R11 sub-tick map (W/G/P per tick) is shown per slice.
- **Issue 2 (BLOCKER, random rewards):** Slice 2's Firmware and slice 6's Daemon are now named at event spawn (one `events` draw each, stored in the event instance) and printed on the wheel face. The preview shows the exact result. No randomness happens after the checkpoint.
- **Issue 3 (MAJOR, nudge economics):** 2 free nudges; extra nudges cost 5 HP or +3 Heat each, max 3 extra (5 ticks maximum, under a quarter of the wheel). The EV arithmetic is now shown.
- **Issue 4 (MAJOR, dominated choices):** Choice 3 is now "−3 Heat and +10 Cycles". Choice 2 is 30 Cycles with no Heat rider, so the two safe options trade Cycles against Heat.
- **Issue 5 (MAJOR, adjacency):** Reordered per critic fix 5. The dud buffers the jackpot, and the bad cluster is stated honestly.
- **Issue 6 (MAJOR, slice 5 stake):** Combat override has the duration "whole fight", and `flee_allowed = false` is a new field on `starts_combat`. A loss follows normal combat rules, and the +30 is paid on a win only.
- **Issue 7 (NIT):** Kept, since spelling was already US.
- **Critic Qs:** The wheel face reveals each slice's reward (kept, which is what makes the preview exact). Heat cost scaling by band is not adopted, to avoid adding scope.

# ev_mer_favor_slot: Favor Slot

**Mechanic:** WHEEL, corporation meridian, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Spend a dead dispatcher's favor on a rigged sort wheel and decide how much HP or Heat to pay to steer it, or take a safe payout instead.

## TerminalEventData fields
- id: `ev_mer_favor_slot`
- title: Favor Slot
- speaker: STREET_MERC
- text: "Hub sorter, third shift, nobody home. A dispatcher named Okafor left a note taped to the scanner: 'You moved my sister's crate once. This slot is yours, one pull, no questions.' The sorter wheel is a manual override, the kind Meridian swears it removed. Every bin on it is a different kind of trouble. Okafor can't collect on the favor anymore, so you owe nobody and everybody."
- corporation_id: `meridian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (none)
- weight: 0.8

## Choices

**1. Pull the lever**
- label: "Pull the lever (2 free nudges)"
- result_text: "The sorter spins, clicks, and drops your parcel where it drops it."
- cycle_cost: 0, hp_cost: 0
- effects: none directly; resolves the event wheel.
- reward: per the landed slice.
- (new) event_wheel: `ew_favor_slot`
- (new) starts_combat / map_edits: none on the choice. Slice 5 carries its own.

**2. Sell the favor to a broker**
- label: "Sell the slot (+30 Cycles)"
- result_text: "A fixer pays cash for a dead man's name on a ticket. The cash is clean. The conscience is not."
- cycle_cost: 0, hp_cost: 0
- effects: GAIN_CYCLES, CAMPAIGN, amount 30
- reward: none
- (new) none

**3. Burn the note**
- label: "Burn the note (−3 Heat, +10 Cycles)"
- result_text: "No favor on the books means no thread back to you. You pocket the scanner's petty cash on the way out."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount −3; GAIN_CYCLES, CAMPAIGN, amount 10
- reward: none
- (new) none

## Event wheel: `ew_favor_slot`
**Start and RNG:** At event spawn, the `events` stream draws (a) the Firmware for slice 2, (b) the Daemon for slice 6, both stored on the event instance and shown on the wheel face. On choosing "Pull," it draws the pointer start tick (0-29) and checkpoints it before the first nudge. Undo cannot reroll it. After that checkpoint there is no randomness: the preview shows the exact result of each pending nudge.

**Nudges:** ±1 tick. 2 free. Extra nudges cost 5 HP or +3 Heat each (player picks per nudge), max 3 extra. Maximum steering is 5 ticks. The pointer reads the slice it ends on. Slices are clockwise in order; wraparound joins slice 5 to slice 1.

| # | Bin | size_ticks | Ticks | Sub-tick map (R11) | Outcome |
|---|---|---|---|---|---|
| 1 | Express Crate | 4 | 0-3 | W G G W | GAIN_CYCLES CAMPAIGN +50 |
| 2 | Dead Letter | 7 | 4-10 | W W G P G W W | Nothing. "Returned to sender." |
| 3 | Spare Parts | 6 | 11-16 | W W G G W W | reward: the pre-drawn common Firmware (shown on the face) |
| 4 | Customs Hold | 5 | 17-21 | W G P G W | MODIFY_HEAT +4, GAIN_CYCLES +20 |
| 5 | Hot Freight | 4 | 22-25 | W G G W | reward: the pre-drawn uncommon Daemon, plus (new) `next_combat_overrides`: enemy damage ×1.25 for the next 1 combat |
| 6 | Audit Flag | 4 | 26-29 | W G G W | (new) starts_combat: `customs_scanner`, stake: win = +30 Cycles. `combat_overrides`: enemy RESISTANCE +1 for the whole fight; `flee_allowed = false` (new field). A loss follows normal combat rules; the +30 is paid on a win only. |

Sizes: 4 + 7 + 6 + 5 + 4 + 4 = 30. Ticks are contiguous (0-3, 4-10, 11-16, 17-21, 22-25, 26-29).

The wheel's slice quality map matters only for nudge readability here; the outcome depends on the slice, not the tier.

Note: I renumbered the bins in this table (Express 1, Dead Letter 2, Spare Parts 3, Customs 4, Hot Freight 5, Audit Flag 6) to match the critic's ordering, so the order from slice 1 is best, dud, mid, mild-bad, jackpot-with-cost, fight.

## Design notes
- **EV arithmetic (blind pull, uniform start):** Cycles-equivalent per slice, with Firmware ≈ 40, Daemon ≈ 70, and a fight's net ≈ +30 × win rate of about 0.9 minus 8 HP of risk ≈ +15: Express 50 × 4/30 = 6.7; Dead Letter 0; Spare Parts 40 × 6/30 = 8; Customs (20 − Heat 4 ≈ 8) × 5/30 = 1.3; Hot Freight (70 − fight risk 15 = 55) × 4/30 = 7.3; Audit Flag 15 × 4/30 = 2. Total ≈ 25, below the sale (30) and the burn (10 + 3 Heat). Steering is needed to beat the safe options, and each steered tick costs 5 HP or 3 Heat, so the gamble is worth it only when the player can reach slice 1, 3 or 5 cheaply.
- **No dominant option:** Sale is best for Cycles-starved runs, the burn for hot runs, the pull for runs with free nudges that line up or spare HP.
- **Geometry:** The dud (7 ticks) buffers the jackpot slice 1 from slice 3. Bad slices 4-6 form a 13-tick cluster (4: mild, 5: mixed, 6: fight). Slice 6 wraps next to slice 1, so over-nudging from slice 1 backwards lands on the Audit Flag fight, and the preview shows this before commit.
- **Economy placeholders:** 50 Cycles is about one Mainframe purchase. The Daemon in slice 5 is the jackpot, but the +25 % damage fight is a real cost on a low-HP operative.
- **Interactions:** Scrubber and Cold Exit make slice 4 cheaper. Low-HP runs pay Heat, hot runs pay HP.
- **Dependencies:** N17 (wheel page, `events` checkpoint), N16 (`starts_combat`, `next_combat_overrides`, the `flee_allowed` field), N12 (the variable sizes; required for the 4/7/6/5/4/4 layout). **Data-only fallback:** Choice 1 becomes a three-option list (Cycles +50 with +4 Heat / pre-drawn Firmware / Audit Flag fight for +30 Cycles); choices 2 and 3 are as written. Without N12 the wheel falls back to six 5-tick slices.
- **Text keys:** `ev_mer_favor_slot.title/.text`, six bin labels, `.nudge_extra_hp`, `.nudge_extra_heat`, `.pull_result.<1-6>`.

## Q:
- Q: Should extra-nudge costs mix (HP or Heat per nudge) or be one fixed currency per event?
- Q: Does winning the Audit Flag fight also grant a normal combat reward, or does the +30 Cycles stake replace it?
