<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__10_paths_halcyon; status ok; tokens in 3434 cache-write 0 cache-read 32585 out 1507; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/10_paths_halcyon

**Verdict:** FIX

## Issues

1. **BLOCKER, template (new-system fields) / N16:** Choice 2's `add_link` target comes from a random `events` stream draw "at a checkpoint". The template says to use only N16 `map_edits`, and the N17 `events` RNG is introduced for the event wheel. Using it for a bare link target is unspecified. The draft also says "the choice preview shows the destination before commit", which is the opposite of a random outcome (GDD 2.10: random effects show odds, not a single result). The two claims contradict each other. Make the target deterministic.
2. **BLOCKER, design quality (dominated choice):** Choice 4 (-6 HP, no effect) is strictly dominated by choice 2, which costs nothing and *gains* 1 Heat reduction plus a shortcut. The draft admits choice 4 "buys nothing". A baseline option that nobody should pick is not a decision. Choice 2 itself is a free lunch against the 40-Cycle choice 1 unless the closed route is a real loss.
3. **MAJOR, hard rule (text/consistency):** The text promises "Two corridors are flagged for foreclosure; one for accelerated redevelopment." But choice 1 closes nothing and choice 2 closes one link. The foreclosure threat is never paid off and the choices don't match the notice.
4. **MAJOR, systems:** `reveal_node_type` with "duration: permanent for this netrun" and `convert_node` "first by node index" have no stated ids. `close_link` targets "the highest-tier option (the Elite Router if one exists, otherwise the Mainframe)". If neither exists, the edit is undefined. No data-only fallback is stated (N16 depends on N2 and is not built). Without it, the event could ship as a plain Cycles and Heat event.
5. **MAJOR, preview=result:** Choice 3 converts a node "at once" and the node is chosen by index. The player can't see which Router is affected unless the preview names it. Specify that the preview highlights the node.
6. **NIT, design notes:** "Elite Routers give +1 Heat" is correct per GDD 4.2. The note "Scrubber and Clean Signal synergize" is wrong: Scrubber only affects Server Rack capture, and Clean Signal needs Perfect streaks. Also, "Elites already drop better loot" is unsourced.
7. **NIT, template:** The Q lines are fine. Text keys are listed.

## Concrete fixes

- **Fix 1/2 (choice 2):** Replace the random link with a deterministic one. `add_link`: from this node to the *middle node* (by index, lower index on ties) two layers ahead. `close_link`: the link to the Elite Router, or, if none exists, the choice is not offered (greyed: `map_edit.blocked_no_path`). Remove the `events` RNG mention. Make the choice cost real: `cycle_cost 15`, plus the Heat -1.
- **Fix 2 (choice 4):** Replace with "Slip the barrier (-6 HP)": `reveal_node_type` on one node of the next layer, the first by index, and `MODIFY_HEAT` +1 ("trespass logged"). Now it is a cheaper, partial version of choice 1 that costs HP and Heat instead of Cycles.
- **Fix 3 (text):** Change to: "One corridor is flagged for foreclosure; one Router is flagged for 'accelerated redevelopment.'"
- **Fix 4:** Add: "Data-only fallback: choices 1 and 4 become Cycles/HP/Heat trades and reveal nothing; choices 2 and 3 are hidden until N16 ships."
- **Fix 6:** Delete the Scrubber and Clean Signal line.

## Keep
- The legal-notice Corpo voice and the "interest accrues" joke fit Halcyon well.
- Choice 3's Cycles-for-risk trade (+35 Cycles, +2 Heat, a Router becomes an Elite) is a real tension.
- The no-strand validation for closed links with a greyed-out reason is a good safeguard.

## Q:
Q: Should choice 2's shortcut be allowed to skip the layer 4 optional Server Rack, given that it banks Schematics?
Q: Is an Elite conversion always bad, or should it be a gamble the player can read (the Elite's reward is shown beforehand)?
