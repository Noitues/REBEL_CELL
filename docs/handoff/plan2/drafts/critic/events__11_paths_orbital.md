<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__11_paths_orbital; status ok; tokens in 3397 cache-write 0 cache-read 32585 out 1589; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/11_paths_orbital

**Verdict:** FIX

## Issues

1. **BLOCKER, template / N-tags.** Every "(new)" line lacks an N#. `map_edits` and `next_combat_overrides` belong to N16 (`EventChoiceData.map_edits`, `next_combat_overrides`), which depends on N2. The draft says "Fallback without N16" but never tags the fields.
2. **BLOCKER, invented content / rules.** `next_combat_overrides: enemy_enrage_start_turn −2` in choice 2. Normals have enrage off (R4), so the override does nothing in most fights. Elites start at turn 8, and a normal fight lasts 3–4 turns. The cost is either null or arbitrary. It also reads as a penalty for scouting that has no thematic link to reading a manifest.
3. **MAJOR, map_edits vocabulary.** `add_link`, `reveal_type`, `remove_node` and `convert_node` are used with no definition. The N16 list gives: open/close/add a link or node, reveal a type, convert a type, cut a layer's option. Pin the ops to that list. Choice 3's `remove_node` plus re-routing is a "cut a layer's option" op and must say it never empties a layer.
4. **MAJOR, determinism / preview.** Choice 1 says "the one with the most branches, preferring a non-Elite" with no tie-break, while the notes say ties go to the lowest node id. Put the rule in the field. Choice 3's fallback ("nearest Elite, if none convert a Router") must be shown in the preview.
5. **MAJOR, design quality.** Choice 2 is near-dominated. Revealing two layers is cheap. Choice 4 is dominated by choice 2 if the enrage cost is null. A shortcut that skips fights also skips Cycles and Heat, so choice 1 is ambiguous. The text says "Heat from routers" is saved, but Routers give 0 Heat per GDD 4.2, so the claim is wrong. Only Elites give +1 Heat, and MODIFY_HEAT +1 is nearly free.
6. **MAJOR, economy.** In choice 3, "6 HP is roughly a fight's worth of attrition at T2" is unsupported. 15 Cycles for 6 HP plus removing an Elite (a threat) is clearly generous. GDD 11 numbers are not cited.
7. **NIT, text.** The "debt" backstory is inconsistent with "a stranger's favor" in the one-line decision. The `dispatch_clue: false` and `foreshadows` fields are fine. The text runs 5 sentences, which is acceptable. The title differs between the heading ("A Favor on Pad Nine") and the field ("Pad Nine Favor").
8. **NIT, Q2.** The `okafor_debt` flag would need run-level state beyond N16. Tag it NEW: event flags.

## Concrete fixes

- **Tags:** put "(N16, needs N2)" on every `map_edits` / `next_combat_overrides` line. Fallback: a data-only version via Cycles/Heat/HP, as already described.
- **Choice 2:** replace the override with a real cost, `cycle_cost: 10`. Result text: "She charges for the read." Keep `reveal_type` on layers +1 and +2 only. Drop `next_combat_overrides`.
- **Choice 1:** `map_edits: add_link` (one-way) from the node in layer+1 with the most outgoing links (tie: lowest node id) to the lowest-id non-Elite node in layer+3. If no such node exists, the choice is greyed out with the reason. The edit may not skip a layer holding the guaranteed Mainframe (validate it against the layer 3–5 guarantee), or else show a "SKIPS MAINFRAME" warning in the preview.
- **Choice 3:** `map_edits: cut_option`. Remove the nearest Elite Router ahead (tie: lowest id) and re-link its predecessors to its successors; never empty a layer. If there is none, the choice is greyed out rather than converting a Router.
- **Choice 5 (replace the Heat claim):** note "Shortcut: −2 fights, so fewer Cycles and cards."

## Keep

- Deterministic selection rules, with a preview of the exact edit.
- Four distinct trade-offs (tempo, information, safety, nothing), a sensible spread of risk.
- Clean voice and a thematically apt Orbital setting.

## Q:
- Q: Is a one-way `add_link` readable on the map without a new edge style?
- Q: Should choice 3 grey out when no Elite remains ahead, or stay available with a different payout?
