<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__09_paths_meridian; status ok; tokens in 3393 cache-write 0 cache-read 32585 out 1676; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/09_paths_meridian

**Verdict:** FIX

## Issues

1. **BLOCKER, Template/R1: "Redirect" combat design.** `tariff_collector` is a normal (1 phase) enemy. "+1 pointer, uneven 0 / 11" is an authored override that isn't listed as an N# dependency. Pointers on any tick is N11 and multi-pointer overrides sit under N16 `combat_overrides`, but neither is tagged. Normal-strength HP at T2 is 34-44, and a second needle doubles intake against the per-turn target. "Expected loss 8-12 HP" is unsupported arithmetic.
2. **BLOCKER, Systems: unresolved map_edit semantics.** Redirect says CLOSE_LINK "the shortcut to a Mainframe in the next layer", but the map has no such shortcut unless Sign created it. The design notes then say Sign and Redirect "conflict on the same Mainframe link", though they are mutually exclusive choices in one event, so there is no conflict. The Redirect close edit can leave a map with no Mainframe at all, since the GDD guarantees one in layers 3-5. It can also disconnect nodes.
3. **MAJOR, Systems: no N# tags and no fallback.** `map_edits`, `starts_combat` and `combat_overrides` are all N16 (depends on N2) but are not tagged, and no data-only fallback is stated.
4. **MAJOR, Rule: fiction vs. mechanics (text).** "A node two layers ahead, one that doesn't exist on your map" conflicts with Sign's REVEAL_TYPE and the "skipping 1 layer" ADD_LINK. The "first Mainframe, or Elite Router if none" fallback is also unsafe: it can send a low-HP player into an elite. If the current node is in layer 6-7, "two layers ahead" doesn't exist. No min-layer condition is given.
5. **MAJOR, Design: Redirect label/reward mismatch.** The label says "15 Cycles of Loot" but the reward is Firmware, and no Cycles are given. "Tracked Parcel +1 Cycle per Router" is a new Firmware effect with no source. Firmware changes what its slice does, so a Cycle income effect breaks that rule. Use a card or existing Firmware instead.
6. **MAJOR, Design: Open dominates.** +40 Cycles for 6 HP, with the node removal chosen by a deterministic rule that the player can plan around. This beats Refuse in most cases. The cost needs to be bigger or the thinning harder to ignore.
7. **MAJOR, Design: Sign reward is overstated.** "Saves roughly 2 minutes" is unsupported. A skipped layer also skips that layer's loot, and Heat +2 is trivially small against a per-run economy, so Sign is a free gain.
8. **NIT, Template:** the Redirect "stake" (4 HP lost) is ad hoc, and the speaker value should be named from the Voice enum, not "(0)". Weight 0.8 is fine.

## Concrete fixes

- **Fix 1/3:** Tag "(new) starts_combat / combat_overrides / map_edits: N16 (needs N2, N11 for the second needle)". Fallback: a plain `starts_combat` of `tariff_collector` with no overrides, and map_edits replaced by a reward-only choice. Drop the second needle; use "enemy damage +25 %, no HP change" as a tier-independent buff.
- **Fix 2:** Redirect map_edits becomes: "CLOSE_LINK: one link into the next layer's Mainframe, only if that Mainframe keeps at least 1 other inbound link; otherwise no edit." Delete the "conflict" bullet from the interactions line.
- **Fix 4:** Condition: "Offered only on layers 1-5." Replace ADD_LINK's fallback with "the first Router, or no edit". Reword text: "…addressed to a node two layers ahead that your map hasn't drawn yet."
- **Fix 5:** Label "Redirect the pod (fight the recipient's enforcer)". Reward: one existing common card or Firmware from the pool, "working description: Patch+".
- **Fix 6:** Open: hp_cost 8, Cycles +30, and the removed node is "the Mainframe in that layer if one exists, else the first Router". This makes the cost felt.
- **Fix 7:** Sign: Heat +4, with the ADD_LINK one-way (this answers Q2).

## Keep
Four distinct prices on the same pod, determinism by fixed target-selection rules, the Final-Rack protection, and the strong Meridian "reroutes the blame" voice.

## Q:
Q: Should REVEAL_TYPE ever reveal a Server Rack's Exploit?
Q: Is a Sign link that bypasses a layer's Mainframe guarantee acceptable?
