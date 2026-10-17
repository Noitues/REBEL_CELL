<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__08_paths_solace; status ok; tokens in 3496 cache-write 0 cache-read 32585 out 1587; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/08_paths_solace

**Verdict:** FIX

## Issues

1. **BLOCKER, template (choices / `next_combat_overrides`, `starts_combat`).** The draft lists "none" fields inconsistently, and choice 3 and choice 4 omit fields entirely. This is minor on its own, but it hides the real problem in issue 2.

2. **BLOCKER, rulings (D4 node list / PATHS family).** Choice 3 converts a node into a "Terminal (Event)". The draft's own notes justify it with "a Rest-type payoff". Rest is a new D4 node, but the choice makes a Terminal, so the justification doesn't match the effect. The choice is also weak: a Terminal is the cheapest node, and 45 Cycles buys little over Walk on. It is a near-dominated option.

3. **MAJOR, N16 / determinism ("Closed node is picked from the `events` stream at open time").** The draft says the preview "names it", but choice 1's label doesn't show which node closes before the player commits. It also says "chosen by the `events` RNG stream ... saved in a checkpoint". The event is open before the choice, so the closed node must be rolled and displayed on opening, not at choice time. The text doesn't state this.

4. **MAJOR, design quality (choice 1).** "Spring him" adds a link that skips a layer, and the player picks the target. That is strictly stronger than choice 3's single-node convert and rewards a rich player at -8 HP. Skipping a layer also bypasses a combat's drops and the layer-4 Rack (the Rack is an optional banking node), so the "Elite guarantee" claim is unsupported. The draft raises this in Q1 without resolving it.

5. **MAJOR, arithmetic and numbers.** "+2 Heat sits just below one Minor threshold step's worth (+1 per Elite, +10 per Minor tier)" is garbled: a Minor threshold is every 10 Heat. The 25-35 Cycles per combat income is attributed to GDD 11, which is not in the supplied text.

6. **MAJOR, rules (R1-R13 / Site names).** The text says "WELLNESS HOLD" and the title is a Site-like name. That is fine as flavor, but the draft calls for "Ward 9" and a "Collections lift". Fiction is fine, but flag that the map_edits use "the player picks" targets without specifying the UI field.

7. **NIT, template.** Choice 2's label says "(+0 Cycles, free)". The `dispatch_clue` and `foreshadows` fields are written as prose. The word "stenciled" is fine (US spelling).

8. **NIT, systems.** The preview strings are fine, but `reveal_type` on "every node in the next two layers" is generous. Choice 2 is free with no downside, so it dominates Walk on (choice 4) whenever the map isn't already readable.

## Concrete fixes

- **Issue 4:** Replace choice 1's `add_link` with: `add_link` from the current node to one *named* node in the next layer, which must be a different node from the closed one, plus `close_node` on a *named* node in that same layer. Both are shown on event open ("LINK: A→C, CLOSES: B"). No layer skip, so no Rack bypass.
- **Issue 3:** Replace the determinism note with: "The `events` stream rolls the closed node once, when the Terminal opens. The result is checkpointed and shown on the card as 'CLOSES: {name}' before any choice."
- **Issue 2 and the near-dominance of choice 3:** Change choice 3 to `convert_node`: the chosen next-layer node becomes a Rest (heal or swap Firmware locations), cost 30 Cycles. Delete the "Terminal" claim.
- **Issue 8:** Restrict choice 2's `reveal_type` to the next layer only, and add `cycle_cost: 10`.
- **Issue 5:** Replace the Heat line with: "+2 Heat is about a fifth of a MINOR step (every 10)." Delete the unsourced income figure or mark it "placeholder".
- **Issue 1:** Give choice 4 and choice 3 the full field list, with "none" where empty.

## Keep

- The spare premise, the sedated thumbprint, and "Hold's voluntary" are strong, and the Solace tone fits.
- Four choices with different resources (HP and Heat, free information, Cycles, nothing).
- Naming the preview strings and keeping the RNG deterministic.

## Q:

- Q: Should a closed node ever be allowed when the player has already committed to a path through it?
- Q: Is Rest (D4) available to PATHS events before the node type exists in the build?
