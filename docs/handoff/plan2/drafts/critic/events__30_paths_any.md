<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__30_paths_any; status ok; tokens in 3492 cache-write 0 cache-read 32585 out 1651; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/30_paths_any

**Verdict:** FIX

## Issues

1. **BLOCKER, determinism / "preview = result" (Design notes, Determinism).** The `debt_due` enemy is "picked from the `events` RNG stream at a checkpoint (before the choice is committed)". Drawing before commit gives a reroll or peek, and it contradicts "fixed by the `events` RNG stream" in choice 1. It also contradicts "chosen by fixed tie-break rules, not random". The enemy must be fixed and shown on the choice.

2. **MAJOR, choice dominance (Choices 1 vs 2).** Pay gives the same link, a reveal, and a free Terminal conversion for 40 Cycles. Borrow's debt (about +1 fight, 8–12 HP) saves about one layer (one fight). Net, Borrow gains no time or HP, it only saves Cycles. Walking on is nearly the same as Borrow, with no risk. Borrow is therefore dominated by Walk on, because the debt cancels the shortcut.

3. **MAJOR, TURN_NODE inconsistency (Choice 2).** The Router-to-Terminal conversion "is a reprieve" and removes a fight, which makes Pay far stronger than the stated 40-Cycle cost. It also silently removes Heat and reward from that node. If the target is not a Router, the effect is undefined.

4. **MAJOR, Burn is a pure loss (Choice 3).** It gives −1 Heat for a lost option, and the cut is chosen by "lowest inbound count", which tends to remove the weakest, least dangerous lane. Nothing in the text lets the player choose or see what is cut, so there is no readable trade. The result_text also contradicts the mechanic ("the ledger's host node goes dark").

5. **MAJOR, safety guard (Choices 1 and 3).** The Mainframe guarantee is only a note ("the engine should skip"), not a `map_edits` constraint. The same applies to Rack protection on ADD_LINK targets.

6. **MAJOR, incomplete override spec (Choice 1).** The duration is contradictory: "next 1 combat after the target node is entered, or run end". It is unclear whether the debt applies if the link is never taken, which is the typical Walk on. The stake is unquantified, and "extra normal enemy" breaks R1 phase and turn assumptions (the fight length is not specified).

7. **NIT.** `dispatch_clue: false` and `foreshadows: &""` follow the field type, but the choice-4 fields are missing (cost, effects, reward). The Pay result_text says "Cheap it isn't", which is odd. The fallback is weak: a "flat +1 Heat" is not a stand-in for a path change. "Text keys" is not needed.

## Concrete fixes

- **Fix 1:** replace the RNG line with: "The added enemy is fixed: the lowest-id normal enemy in the corporation's pool at the player's tier. It is named in the choice tooltip and on the `debt_due` badge. No RNG draw."
- **Fix 2:** make Borrow pay out. Change it to "ADD_LINK skipping one layer, plus +10 Cycles from the shortcut cache". Alternatively, make the debt an Elite Router conversion on the target's next node. Pick one; the first is simpler.
- **Fix 3:** `TURN_NODE: target Router → Terminal` becomes `REVEAL_TYPE` only. Pay then costs 40 Cycles for a clean, revealed link. State "if the target is not a Router, no TURN_NODE".
- **Fix 4:** change Burn to "CLOSE_NODE on the Elite Router in the next layer if one exists (else no cut), −2 Heat". The player can then see what is lost.
- **Fix 5:** add the constraints `never remove or target a Rack; skip the candidate if it is the last Mainframe in layers 3–5; never leave a layer empty`.
- **Fix 6:** set `next_combat_overrides.debt_due`: `trigger = first combat entered via the added link`; `expires = run end`; `if the link is never taken, the debt voids`. Add `+1 enemy` and its 3–4 turn cap.
- **Fix 7:** choice 4 fields: `cycle_cost 0, hp_cost 0, effects none, reward none`.

## Keep

- Three different currencies (later danger, Cycles, route flexibility) plus a neutral Walk on is a good frame.
- The tie-break rules for links and node removal are deterministic and documented.
- The ledger kiosk text is tonally on point and makes the "debt" metaphor legible.

## Q:

- Q: Should the debt void if the player never takes the added link, or follow the run?
- Q: Is a conversion of a node to Terminal ever acceptable as a priced option, or only reveal and links?
