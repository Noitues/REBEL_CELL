<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__13_paths_tethys; status ok; tokens in 3377 cache-write 0 cache-read 32585 out 1567; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/13_paths_tethys
**Verdict:** FIX

## Issues
1. **BLOCKER, template / systems (Choice 3):** The enemy is unresolved. The Stake line says "`port_authority` is not used; it is `last_mile_enforcer`". Both are Meridian ids, not Tethys. `starts_combat` is "none", yet the reward is "granted only once the combat is won". No combat is defined, and a TURN_NODE into an Elite Router has no reward hook.
2. **BLOCKER, rulings (Choice 1):** ADD_LINK skips a layer, which can bypass the layer-4 Rack or even the layer-7 final Rack. The draft's own note says it "doesn't break" the Rack layers but gives no rule. It also skips a Terminal and Mainframe layer, and the draft doesn't check the guarantee "Mainframe in layers 3–5". The fix must be a hard constraint, not a Q.
3. **MAJOR, systems:** Choice 2's fallback "reveal one random node's type" uses RNG. Any random pick must be deterministic and previewable. Revealing a node is not random information, so the roll is unnecessary. Also, the D4 ruling has "Intel: no (the reward is known before the run)", and a free reveal edges toward that.
4. **MAJOR, design quality (Choice 3):** The Rare Firmware plus 30 Cycles for a forced Elite is probably dominant for a strong run. Choices 1 and 2 give no loot. Choice 2 is weak: an Elite is cut only if one exists, otherwise a reveal, so the outcome is uneven. Choice 4 is a free decline.
5. **MAJOR, template:** The "(new)" lines for `starts_combat`, `combat_overrides` and `next_combat_overrides` are muddled. The text says "Whatever you tell it, it will do for the rest of this dive", but no lasting effect exists.
6. **NIT:** The Heat arithmetic ("roughly a third of one Elite Router's Heat") is unsupported. An Elite Router gives +1 Heat, so +4 is four times that. The "Billing Loop" comparison cites an event not shown. The "13% of 60 HP" figure is correct (8/60). No N# is tagged anywhere. Name them: map_edits = N16, which depends on N2. A data-only fallback must be stated (none exists; without N16 the event can only use HP, Cycles and Heat).
7. **NIT:** `foreshadows: &""` is GDScript syntax in a markdown draft.

## Concrete fixes
- **Fix 1:** Choice 3 becomes: `map_edits: TURN_NODE next layer's lowest-index Router → Elite Router (type revealed)`. Remove `starts_combat`. Reward: `Rare Firmware "Pressure Seal"` as the node's added elite reward, via an N18 row or N16 `combat_overrides` on that node: `reward_bonus = firmware_rare`. Result text: replace the "Something in the dark" sentence with "A fat shape already sits on the next relay." Tag **N16**.
- **Fix 2:** Choice 1 constraint: `ADD_LINK from this node to the lowest-index node exactly 2 layers ahead; invalid if the target layer is 4 or 7 or the skipped layer holds the only Mainframe`. If invalid, the choice is greyed with a reason. This answers Q1.
- **Fix 3:** Choice 2 edit: `CUT_OPTION: remove the highest-index Elite Router in the next layer; if none, REVEAL_TYPE on the lowest-index unrevealed node in that layer.` There is no RNG, so drop the events-stream note.
- **Fix 4:** Rebalance: Choice 3 costs 30 Cycles and 6 HP; Choice 2 becomes −8 HP, −3 Heat. Add a note that Choice 3 greys out if the next layer has no Router.
- **Fix 5:** Add the line "Dependencies: N16 (map_edits), N2. No data-only fallback; without N16, drop the event."

## Keep
- The text is strong and in genre.
- Three distinct edit kinds (add, cut, convert) map to three distinct costs (Heat, HP, Cycles).
- The deterministic, previewable edit applied at resolution and saved in run state.

## Q:
- Should the Elite conversion be shown on the map before commit (my fix: yes, because the preview must equal the result)?
- Is a Heat-for-shortcut trade acceptable given Tethys's own Heat identity, or should the cost be HP?
