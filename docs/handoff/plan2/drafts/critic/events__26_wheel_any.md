<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__26_wheel_any; status ok; tokens in 3727 cache-write 0 cache-read 32585 out 1743; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/26_wheel_any

**Verdict:** FIX

## Issues

1. **BLOCKER, determinism / R10, "a `events`-stream roll sets a start tick" and "Quality does not scale outcomes".** The start tick is a random event and needs a checkpoint. The draft says so, but it names no stream or checkpoint owner. Slice 6 draws "one random common Firmware" from the same stream *after* the commit. That is a second random event, and the preview cannot show it. This contradicts "nothing random happens after the start tick" and "preview equals result."
2. **BLOCKER, template / spec: slice 5 is inconsistent with its own stake.** The draft says "flee not allowed" while the event also has Skip and Crawlspace as safe outcomes. The real problem is that `starts_combat` lacks the required fields: no overrides, no stake on loss, and no statement of how HP carries over. Also, `patrol_unit` is a normal-tier enemy, but the draft's claim of "~44 HP at T2" is R2's band midpoint, not authored `hp_by_tier`. Say it comes from `hp_by_tier`.
3. **MAJOR, spec: the slice table does not spell out outcomes as asked.** Slice 3 (Skip) has no precise `map_edits` (which node ids, what happens on Rack layers, what happens if the next layer is the last). Slice 1 mixes `hp_cost` with an effect. The "Dead end" slice has no EffectData for HP loss (use DEAL_DAMAGE SELF or the choice-level `hp_cost`, but wheel slices need their own field).
4. **MAJOR, design: a dominated choice.** Option 3 (heal 4) is nearly always worse than option 2 (+15 Cycles), and the wheel's expected value exceeds both. Option 2's label also contradicts its body: "Pry the lid and read the wiring" versus the label "Salvage the dial mechanism." The wheel with 2 free nudges gets near-guaranteed choice among adjacent slices, and Stash (+30 Cycles, 4 ticks) beats Option 2 at zero cost. Only a Heat-threshold run has a reason to skip.
5. **MAJOR, economy: nudge costs are unquantified.** "About a small shop item's worth" is not a number. Six extra nudges at 2 HP, 1 Heat or 8 Cycles each cost up to 12 HP, 6 Heat or 48 Cycles, more than the best prize. Nothing caps total spend relative to the prize.
6. **NIT, template:** the text is 5 sentences and acceptable. "stenciled" is US spelling, fine. The "Sub-tick quality follows R11" line is noise, since quality is irrelevant here. The Dead end sizes the "worst" slice at 4, which reads as intended. Slice size 7 reads as a Perfect tick, but quality does not matter, so state that the pointer position within a slice is irrelevant.
7. **NIT:** `speaker: STREET_MERC (1)` should be the enum name only. The Q about currency per wheel overlaps note 2.

## Concrete fixes

- **Issue 1:** change slice 6 to a fixed reward: "Loose cable: reward `firmware` = first common Firmware in the Router pool not already owned, ordered by id." Or resolve the draw at wheel open, display it on the slice, and checkpoint it with the start tick. Add: "Start tick and the slice-6 reward are both drawn once on open from the `events` stream, then checkpointed."
- **Issue 2:** slice 5 becomes `starts_combat: enemy patrol_unit, tier = current, combat_overrides none; stake: win +20 Cycles, loss follows normal death rules; HP carries over; no flee.`
- **Issue 3:** slice 3 becomes `map_edits: remove the fight nodes of the next layer from the player's reachable set; connect the current node to every node of layer+1; Rack nodes are exempt (never bypassed); if next layer is the final, this slice becomes Stash.` Slice 1 becomes `DEAL_DAMAGE SELF 6; MODIFY_HEAT CAMPAIGN +2.`
- **Issue 4:** option 2 → +10 Cycles. Option 3 → "Walk on (heal 8 HP, −1 Heat)" so it competes when hurt or hot. Slice 4 (Stash) → +25.
- **Issue 5:** one cost per wheel: 2 HP, nudge budget 2 free plus max 3 extra, so worst case 6 HP.

## Keep
- The uneven slice sizes (sum 4+7+5+4+6+4 = 30, verified) make nudging a real aim problem.
- The Heat-band tension in choosing which currency to burn.
- A stated data-only fallback (fixed outcomes, no wheel).

## Q:
1. Should the wheel's start tick be shown before the player commits to cranking, so choice 1 versus 2 is an informed decision?
2. Is a Skip that removes a node's Heat acceptable, given that it bypasses Heat-generating Elite Routers?
