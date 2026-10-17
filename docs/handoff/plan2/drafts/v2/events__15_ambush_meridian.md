<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__15_ambush_meridian; status ok; tokens in 5015 cache-write 0 cache-read 32585 out 2957; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, invented fields, phase skipping):** Removed `enemy_phase_skip` and `starting_hp_pct`. Choice 2 now uses `combat_overrides: {tier_delta: -1}` only. Choice 3 uses `{enemy_id, tier_delta: 0, consumes, expires, converts}` as the critic specified. R1 is respected: the Enforcer keeps 2 phases with threshold parking, and enemy HP comes from `hp_by_tier` (N2).
- **Issue 2 (BLOCKER, Sign dominated):** Sign now costs 25 Cycles and +6 Heat. The fight pays 35 Cycles plus a Firmware choice, with no Heat change on entry and +2 Heat on win. Sign is now the only choice that skips the fight entirely and avoids HP loss and permadeath risk. It is also the only option that keeps the run's Firmware slots on schedule. The notes make that risk and Heat-for-Firmware trade explicit.
- **Issue 3 (MAJOR, Sneak is a trap):** Sneak now defers the same fight at run tier (tier_delta 0) and pays 35 Cycles plus the same Firmware choice. It costs 8 HP up front. If no Elite Router remains, the override converts to the next Router instead of fizzling, and a tooltip says so. Per the critic's fix, the "+25 Cycles" bonus is folded into the equal 35-Cycle reward rather than stacked, to avoid double-counting.
- **Issue 4 (MAJOR, label arithmetic):** The header now reads "-25 Cycles, +6 Heat" and matches `cycle_cost`. The swing is recomputed in the notes.
- **Issue 5 (MAJOR, no stake):** Stake added to the voluntary fight: +2 Heat on win (the courier files a loss report). The loss stake is operative death (existing rules).
- **Issue 6 (NIT, ambush-as-option):** Kept, because the ruling allows ambush as an event option. The text and Choice 2 label now make clear that refusing is the player's choice.
- **Issue 7 (NIT, pacing):** Fight length and HP stated in the notes: 2 phases, 6-8 turns, tier-1 HP from `hp_by_tier`.
- **Issue 8 (NIT):** Kept as is.
- **Critic Q on convert vs fizzle:** Decided: convert to the next Router.
- **Critic Q on N18:** The combat reward is carried as a reward-table row on `starts_combat`. It is data-only and can be moved into an N18 row later.

# ev_mer_exclusive_carrier: Exclusive Carrier Clause

**Mechanic:** AMBUSH, corporation meridian, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Pay Meridian's price (Cycles and Heat) to avoid a hunter entirely, fight him now and risk your operative, or dodge him at an HP cost and meet him later.

## TerminalEventData fields
- id: `ev_mer_exclusive_carrier`
- title: Exclusive Carrier Clause
- speaker: STREET_MERC
- text: "A contract slides across the Terminal screen: 'Exclusive Carrier Agreement. Cell to move no data except via Meridian.' The signature box is already pulsing. Behind it, a dead-eyed courier in a Last-Mile jacket leans on the doorframe, scanning your face against a bounty list. The fine print says refusal 'triggers enforcement of delivery terms.' You can sign, you can refuse and take what comes, or you can slip out the back. He is already counting you."
- corporation_id: `meridian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Sign it (-25 Cycles, +6 Heat)**
- label: "Sign the clause (-25 Cycles, +6 Heat)"
- result_text: "Ink dries on nothing. The courier tips two fingers and goes back to the street. Meridian now knows exactly which lane you use."
- cycle_cost: 25
- hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / amount 6
- reward: none
- (new) starts_combat: none
- (new) next_combat_overrides: none

**2. Void it and fight now**
- label: "Void the clause and call him out"
- result_text: "You flag the contract as fraud. He drops the clipboard, and a drone swarm unfolds behind him. 'Enforcement of terms,' he says."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: set by the fight (below)
- (new) starts_combat: enemy `last_mile_enforcer`
  - combat_overrides: `{tier_delta: -1}` (run tier minus 1, minimum 1). Enemy HP comes from `hp_by_tier` (N2); 2 phases with threshold parking (R3).
  - stake: you enter with current HP and cannot flee; defeat is normal operative death. On a win, +2 Heat ("the courier files a loss report").
  - reward on win: 35 Cycles + Firmware choice (1 of 3, common pool).

**3. Slip out through the freight lift (-8 HP)**
- label: "Slip out through the freight lift (-8 HP)"
- result_text: "You squeeze past the scanner arc and take a pallet corner to the ribs. Behind you, the courier lowers his scanner and starts typing. He will find you."
- cycle_cost: 0
- hp_cost: 8
- effects: none
- reward: set by the deferred fight
- (new) next_combat_overrides: `{enemy_id: last_mile_enforcer, tier_delta: 0, consumes: next Elite Router, expires: netrun end, converts: if no Elite Router remains, the next Router}`. The fight rewards 35 Cycles + the same Firmware choice, with no Heat change. Heat +2 on win does not apply to this one.
- (new) map_edits: none

## Design notes
- **Three different prices:** Sign costs resources and the campaign (25 Cycles and 6 Heat, roughly a Mainframe item plus most of a MINOR step) but removes all risk and all Firmware. Fight now costs HP and death risk for 35 Cycles and a Firmware choice, plus 2 Heat. Sneak costs 8 HP now and the same fight later at run tier (one tier harder than choice 2) for the same reward and no Heat.
- **Economy check:** Fight vs Sign is a swing of 60 Cycles (+35 vs -25), a Firmware choice, and 4 Heat (+2 vs +6). The price is an expected HP loss of about 15-25 at tier 2 for a fed operative, plus death risk. A strong run fights, a weak or low-HP run signs, and a run that wants the Firmware and has Elite Routers still ahead may sneak.
- **Fight length:** The Enforcer is a 2-phase elite, 6-8 turns, 56-72 HP at tier 1 and 68-88 at tier 2 under the R2 bands, so choice 2 at run tier 2 fights the tier-1 numbers. Choice 3's deferred fight uses the run tier, so it is harder than choice 2 and less than a free lunch. Its price is an HP-timing choice and the fight at its worse tier.
- **No dominant option:** Sneak beats Fight only on the Heat saved (2) and the delay, and loses on tier difficulty and the 8 HP. Sign beats both only when HP or survival is the constraint.
- **Determinism:** Fights use standard RNG streams. The deferred override is stored in checkpointed run state, with no random trigger. The tooltip shows "next Elite Router becomes a Last-Mile Enforcer; if none remains, the next Router does."
- **Systems:** N16 (`starts_combat`, `combat_overrides` with `tier_delta`, `next_combat_overrides`), N2 for `hp_by_tier`. No data-only fallback for choices 2 and 3. Reward Firmware choice can later move into an N18 row.
- **Text keys:** `ev_mer_exclusive_carrier.title/text`, three labels, three results, and a tooltip key for the deferred ambush.

## Q:
- Q: Should the deferred Enforcer count toward the guaranteed Elite per layer, or replace one?
- Q: Should the tier-1 voluntary fight reduce the Firmware pool quality, or is it flat?
