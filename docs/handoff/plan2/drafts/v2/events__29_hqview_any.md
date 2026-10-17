<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__29_hqview_any; status ok; tokens in 5388 cache-write 0 cache-read 32585 out 3423; cost $0.026. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, Meridian enemy in an `any` event):** `tariff_collector` is removed. Choice 4 now fights `rc_template_elite_b`, a REBEL_CELL elite built from the player's own profile, so it carries no hostile-corporation identity. Tier rule rewritten per R2: tier = the Site tier of the operative's next netrun, base HP from `hp_by_tier` and damage from `enemy_damage_by_tier`, no override. REBEL_CELL elites are two-phase (R1), so the fight is sized as an elite (about 6–8 turns), which is larger than v1's normal fight. The stake is repriced to match (see choice 4 and Q2).
- **Issue 2 (BLOCKER, sub-tick maps):** all three slices get authored `tick_quality` maps, and each is re-added to its size (10, 12, 8). The "narrowest Perfect" claim is dropped. Because R11 defines only default maps for sizes 2–7, the wheel now uses sizes 6 / 6 / 6 / 6 / 6 (five slices) as the main design, with the authored-map version as an N12 extension. See the wheel section.
- **Issue 3 (MAJOR, nudge buys the best slice):** the paid nudge is removed. Only the free ±1 nudge remains, and the fixed pre-wheel effects (+10 Schematics, +4 Heat) are removed. Choice 1 now has no fixed reward. All of its value is in the wheel, whose expectation is shown below.
- **Issue 4 (MAJOR, choice 2 dominates, HP heals at HQ):** the HP cost is removed because HP is free at HQ. Choice 2 now costs the inspecting operative their next netrun slot (Rest for this cycle), and the Firmware is a fixed reward with the Cycles cut to +10. This is a real cost, since the operative is unavailable.
- **Issue 5 (MAJOR, RNG and loss rule):** the Firmware draw is stated as an `events` stream draw at a checkpoint made when the choice is confirmed. The loss rule is rewritten: a loss has no HP stake; it costs +3 Heat and no reward (the operative is not killed).
- **Issue 6 (MAJOR, N# tags):** tags added: `event_wheel` N17, `starts_combat` N16, `next_combat_overrides` N16, tick sizes N12. Data-only fallbacks stated for each.
- **Issue 7 (NIT):** the text drops "hasn't ordered anything in weeks". Choice 2's label and cost both say "the operative who would launch next". Choice 3's flavor line is cut. The slot Q is answered in the design notes.
- **Critic Q on HQ HP costs:** answered, no HP costs in HQVIEW events.
- **Critic Q on Daemon from an HQ fight:** kept, because a win against an elite-sized fight justifies a common Daemon.

# ev_hq_dead_letter_crate: Unmarked Crate at the Loading Door

**Mechanic:** HQVIEW, corporation any, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** An unlabeled crate arrives at HQ. Open it on a wheel, pull a veteran off the roster to inspect it, ignore it, or trace the sender and fight whoever comes for it.

## TerminalEventData fields
- id: `ev_hq_dead_letter_crate`
- title: Unmarked Crate at the Loading Door
- speaker: NARRATOR
- text: "A courier bike idles at the loading door and leaves before anyone signs. It leaves a steel crate with no label, no manifest and a faint hum from the seams. Nobody in the Cell ordered it. It could be a gift, a trap, or someone else's problem that just became yours."
- corporation_id: `&""`
- min_tier: 1
- dispatch_clue: false
- foreshadows: `&""`
- weight: 0.8

## Choices

### 1. Pry it open
- label: "Pry it open (spin the contents)"
- result_text: "The lid comes up on foam, wiring and one sealed pouch. Half of it is junk. The other half is not."
- cycle_cost: 0; hp_cost: 0
- effects: none fixed; all outcomes come from the wheel
- reward: none beyond the wheel
- (new) event_wheel: below (N17)

### 2. Have a veteran inspect it
- label: "Have the next operative inspect it (sits out the next netrun)"
- result_text: "She reads the seams like a ledger, defuses the tamper wire and hands over the clean half. By the time she's done, the launch window is gone."
- cycle_cost: 0; hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 10
- reward: one common Firmware, drawn from the `events` RNG stream at a checkpoint when the choice is confirmed
- (new) map_edits: none
- Cost: the operative who would launch next is marked resting and is unavailable for one netrun launch (roster field, N16 `next_combat_overrides` carrier; fallback: a flat −10 Cycles).

### 3. Leave it on the dock
- label: "Log it as unclaimed"
- result_text: "You log it and walk away. By morning the crate is gone, and so is the heat on your records."
- cycle_cost: 0; hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount −2
- reward: none

### 4. Trace the sender
- label: "Trace the sender (−15 Cycles, elite fight)"
- result_text: "The trace bounces twice and lands on a handler's desk. Someone is already coming to collect."
- cycle_cost: 15; hp_cost: 0
- effects: none
- reward: one common Daemon, granted on a win
- (new) starts_combat (N16): enemy `rc_template_elite_b`, one impromptu fight in the HQ view with the operative who would launch next. Tier = the Site tier of that operative's next netrun, base values from R2 tables. Overrides: none. Stake: win = Daemon and −2 Heat; loss = +3 Heat, no reward, no operative death.
- (new) combat_overrides: none; this fight only.
- Fallback (no N16): a fixed +2 Heat toll for a Cycles refund of 15.

## Event wheel (choice 1 only; N17, sizes need N12)
Five slices of 6 ticks, so the R11 default map applies (W W G G W W). Wait: size 6 has no Perfect, so Perfect landings are not possible. This is deliberate: the event is a fair-odds reveal, with no skill premium.

| Slice | size_ticks | tick_quality (R11 size 6) | Outcome |
|---|---|---|---|
| Salvage | 6 | W W G G W W | GAIN_CYCLES +25 |
| Schematics cache | 6 | W W G G W W | GAIN_SCHEMATICS +8 |
| Dud | 6 | W W G G W W | nothing |
| Dud | 6 | W W G G W W | nothing |
| Live tracker | 6 | W W G G W W | MODIFY_HEAT +4; next netrun's first fight +1 enemy resistance (`next_combat_overrides`, 1 combat) |

- Sum: 6 × 5 = 30.
- The pointer starts from the `events` RNG at a checkpoint, so rewind can't reroll.
- Nudge budget: one free ±1 nudge. No paid nudges. At 6 ticks per slice, ±1 changes the slice only when the pointer starts on an edge tick, so the nudge is a small, honest edge-save.
- Output tier: WEAK landings halve the numeric reward (Cycles 12, Schematics 4). GOOD pays full. The preview shows the slice and tier before commit; preview equals the result.
- Fallback without N12/N17: five 6-tick slices cannot exist, so use the existing 6 × 5-tick wheel kit (one slice Null mapped to Dud, one to Tracker) and keep the same outcomes.

## Design notes
- **Choices spread across resources:** 1 is variance, 2 is Cycles plus a Firmware paid with a roster slot, 3 is Heat relief, 4 is the only Daemon and the only fight.
- **Choice 1 expectation:** 1/5 each. Salvage 25 Cycles (WEAK 12), cache 8 Schematics (WEAK 4), 2/5 nothing, tracker costs 4 Heat and a resistance point. Roughly +7 Cycles-equivalent per spin against a typical run of 100–150 Cycles, so it's a small positive gamble with a visible downside.
- **Choice 2 repriced:** +10 Cycles and a Firmware, paid with a whole netrun slot of one operative. It's strong when the roster is deep and poor when only one operative is free.
- **No dominance:** at high Heat, 3 (−2 Heat) wins. With a deep roster, 2 wins. A Cycle-rich, healthy operative takes 4 for the Daemon. 1 suits wheel-lovers.
- **HP:** no HP costs here, because operatives heal fully at HQ.
- **Interactions:** Scrubber and a Proxy Relay soften the Tracker. `rc_template_elite_b` is a REBEL_CELL elite, usable in any corporation's campaign.
- **Text keys:** `ev_hq_dead_letter_crate.title`, `.text`, `.c1`–`.c4`, wheel labels `salvage`, `cache`, `dud`, `tracker`.

## Q:
- Q: Is an HQ impromptu fight (choice 4) a free action between runs, or does it consume the operative's launch for that cycle?
- Q: Should the tracker's `next_combat_overrides` resistance stack with the Heat 50 resistance modifier, or take the higher value?
