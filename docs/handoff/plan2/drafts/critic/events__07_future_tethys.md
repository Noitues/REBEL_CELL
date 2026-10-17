<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__07_future_tethys; status ok; tokens in 3450 cache-write 0 cache-read 32585 out 1588; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/07_future_tethys

**Verdict:** FIX

## Issues

1. **BLOCKER, determinism / R-core, choice 2.** The 50/50 roll "decided by the `events` RNG stream at a checkpoint" is not a preview-equals-result outcome. The note also says the tooltip shows "Rumor: 50/50". The `events` stream is only introduced with N17, an event-wheel system, so using it here has no tag. Hidden-outcome events are acceptable only if the roll sits at a saved checkpoint. The draft says that but never names the system, and its fallback drops the split.
2. **MAJOR, design quality, choice 2 vs 1.** The notes call choice 2's True outcome "strictly better than verifying". That is not the same as no dominant option. The gap between the options is also lopsided. The True outcome gives Frozen, −1 resistance and a free nudge across 2 fights. The False outcome gives +20% damage, +1 resistance and a lost nudge across 2 fights. The draft claims EV is "roughly even" but shows no arithmetic, and the stated effect sizes are not comparable.
3. **MAJOR, choice 1.** The result text says the rumor is "half true". The override is a 1-turn nudge lock plus a phase reveal. Phase reveal is useless against normals, which have 1 phase (R1), so the reward is dead on most next fights. It also cites N3 for the reveal, while the Chart Hidden buff belongs to N5.
4. **MAJOR, choice 3.** Selling gives +25 Cycles, +2 Heat and a 1-fight +10% damage on turn 1, a very mild cost. Heat is not part of the FUTURE family, and the draft itself asks whether it belongs (Q2). Choice 3 is also the weakest-effect option while paying more than choice 1 costs, so it is close to dominant for any Cycle-starved player. The text also says "the divers will remember" but nothing carries that memory forward.
5. **MAJOR, systems / Rule compliance.** The "free extra nudge on turn 1" and "lost free nudge" are not existing effects. Neither has a N# tag. The Frozen start and the resistance change need field names under N16, and "a satellite removed" is not used. The Ghost and Hub Breach interaction is fine, but "Frozen" is defined only in passing.
6. **NIT, "Pay the pump tech's cousin..." / text.** The event text and the choice 1 header contradict each other: the header says "pump tech's cousin", the label says only "Pay to verify". The speaker is STREET_MERC, but the text reads as narration. The enrage defaults are untouched, which is fine.
7. **NIT, weight / corp.** min_tier 2 is fine for an unlockable corporation, but the draft never states whether Tethys exists as a corporation id in the content list. The template said to use only listed ids, so confirm `tethys`.

## Concrete fixes

- **Fix 1 (BLOCKER):** replace the roll with a deterministic, previewed hook. Option: make the truth a function of a saved run field, e.g. next fight's enemy id parity. Preferred: keep the roll, tag it "N16 + `events` RNG checkpoint (N17 stream)" and state the fallback "data-only: fixed True outcome at +10 Cycles cost".
- **Fix 2:** balance numbers to the same size. True: Frozen, −1 resistance, free nudge, next **1** combat only. False: +15% damage, +1 resistance, no free nudge, next **1** combat. EV is then symmetrical and sits below verifying's certainty.
- **Fix 3:** choice 1 override, "next 1 combat: enemy starts Frozen and `nudge_locked` turn 1; if the target has 2+ phases, reveal layouts". Tag the reveal "N5 Chart Hidden counter".
- **Fix 4:** choice 3: GAIN_CYCLES 25 and next combat enemy +20% damage turn 1 only, plus enemy +1 resistance. Drop the MODIFY_HEAT or make it +1.
- **Fix 5:** name the nudge override field as `next_combat_overrides.player_free_nudge: +1/−1 (N16)`.

## Keep

- The three-way verify, bet or sell structure is clear and fits the FUTURE family.
- The rumor premise is fresh and well matched to noir text.
- Making the false outcome hurt both the nudge and the damage is a good cost.

## Q:

Q: Should the roll in choice 2 exist at all, or should the event be fully deterministic with a paid or free split?
Q: Is `tethys` a confirmed corporation id (D1)?
