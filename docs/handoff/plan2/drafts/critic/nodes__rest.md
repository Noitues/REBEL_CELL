<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__nodes__rest; status ok; tokens in 7488 cache-write 0 cache-read 32585 out 2025; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: nodes/rest

**Verdict:** FIX

## Issues

1. **BLOCKER, §3 Placement / D4 ruling.** "A second REST is allowed on tier T3+ (`rest_extra_chance` = 0.35)" and "Weights by tier: T2 0.15". It contradicts itself: T3+ only, yet T2 has 0.15. The key name also differs from the §6 key `rest_extra_chance_by_tier`.
2. **BLOCKER, §3 guarantee rule.** "exactly 1 guaranteed REST per netrun, placed on layer 4 or 5" collides with "REST may appear on layers 3–6" and with a "path from layer 1 to final Rack passes through a REST". With branching layers (2–4 nodes) a REST on one node cannot be on every path, and the draft says a side branch is acceptable. The guarantee is then vacuous, and "never skippable by graph structure" in §8 is false.
3. **MAJOR, §3 adjacency.** The sentence "never in the layer immediately after the layer-6 Elite cluster guaranteed... if an Elite sits on layer 6…" is unfinished garbage. The Mainframe rule ("never directly before a Mainframe") is also unclear. It also conflicts with REST being placed "after the Rack and Elite placement", and the layer-4 REST competes with the optional Rack (§8) yet the generator must keep both.
4. **MAJOR, §2 REWIRE rules.** The draft invents `requires_slice_types`, `lock_socket`, and "Leech: SHIM slice", "Hardened/Burner fixed sockets". GDD 6.1 says Leech works on a SHIM slice but there is no compatibility field, and "Calibrated" is a placeholder. The draft says "initial data: none fixed" but also treats Burner as movable. Further, "Slice-specific compatibility is preserved" contradicts example 1, which moves Patch+ freely. Mark both fields as NEW: Firmware socket rules, with the fallback "all Firmware movable to any slice". Example 2 moves Mirror and Calibrated with no check against that rule.
5. **MAJOR, Example 3.** It contains live self-correction ("as a neutral hint? No: the game does not give advice"). Also, the Botnet example says Hardened on a Trojan slice, but Botnet is 45 HP with 16 heal, and 15.75 rounds half up to 16. That is fine, but the text needs cleanup.
6. **MAJOR, §4 Undo.** "single UNDO ... restoring the pre-visit state; leaving commits". The GDD rewind is checkpoint-based. Define UNDO as a node-local action, and save state (`rest_used`) must not be set until leaving. §8 says `rest_used` is set "at commit", which allows an UNDO-then-both-modes exploit across a quit and reload. Pick one point: commit on leave.
7. **MAJOR, §2 sustain balance.** The figure "Router fight costs 10–15 HP at T1–T2" is unsourced; the baseline has 43 HP lost at T3 for Care Swarm. The 35% heal needs sim confirmation. A 35% heal plus a second REST is not 'no other sustain' with Hub HEAL absent; the premise is fine, so mark the numbers as placeholders.
8. **NIT, §5 "Heat modifiers ... a MINOR-threshold complication may not delete the REST".** This adds a rule with no Heat system hook. Say "none".
9. **NIT, §6.** The draft cites NA-02, NA-23 and NA-24 without a definition. "Replan holds for D4" is vague. The draft has no N# for the generator pass; use NEW: REST node generator (M), fallback: PATCH-only via a Terminal-style event.
10. **NIT, §1.** "REST never grants both ... never adds power" is good but "retune" overstates a 1-swap.

## Concrete fixes

- (1) Replace the tier lines with: `rest_extra_chance_by_tier` = [0, 0, 0.35, 0.35]; remove the T2 0.15.
- (2) Guarantee: "The generator places one REST on layer 4 or 5 and validates that **every** layer-4/5 branch point offers a REST-reachable route within one node of choice; otherwise re-place using the same `map` stream draw count." Remove the §8 "never skippable" sentence, replace with "reachable by at least one route".
- (3) Replace the broken sentence: "No REST on layer 6 if that layer holds a guaranteed Elite; no REST on a layer directly adjacent to the Mainframe's guaranteed layer. Placement runs after Rack, Elite and Mainframe, before the Terminal fill."
- (4) "Socket rules (NEW: Firmware socket rules, S): by default any Firmware moves to any outer slice. `requires_slice_types` and `lock_socket` are optional fields added only if a Firmware needs them. Data fallback: none declared, all legal."
- (5) Example 3 final sentence: "REWIRE has no useful swap, so the player PATCHes: 20/45 → 36/45."
- (6) "State changes apply to the run only when the player leaves the node; UNDO is local until then. Set `rest_used` on leave."
- (7) Add: "all REST numbers pending the sim; the 10–15 HP figure is an unmeasured estimate."

## Keep

The PERCENT heal tied to max HP (R2/R5), the "one mode per visit" decision, the slot-swap meaning of REWIRE (no new randomness, exact preview), the use of the existing `map` stream, and the examples' emphasis on neighbour reads.

## Q:

Q: Is a guaranteed REST per run too generous given the baseline's 605-minute campaign length?
Q: Does PATCH count as sustain under the 30% cap for fights that follow?
Q: Should leaving without acting still mark the node as spent?
