<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01LxQs8RvJGj9WzDuV2avpgt, custom_id node__rest; status ok; tokens in 14005 cache-write 32007 cache-read 0 out 6312; cost $0.086. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# REST (netrun node): design draft

## 1. Purpose & the decision it creates

REST is the one place on a netrun map where the run stops being a gauntlet and the player decides what the operative is. HP carries between fights and there is no other sustain, so each REST asks one question: **repair the body, or retune the build?** Mode A (PATCH) restores HP. Mode B (REWIRE) rearranges where installed Firmware sits on the wheel. Firmware is one socket per slice (GDD 6.1), and slice position decides when a slice lands and which neighbours Mirror and Shunt read, so rewiring is a build decision. A healthy operative with a bad layout should rewire. A sound layout at 40% HP should patch. The player weighs this against the next layers: an Elite Router ahead, a Rack at layer 4 or 7, and Heat already paid. REST never grants both in one visit, and it never adds power. It converts tempo into either HP or arrangement.

## 2. Rules

**Eligibility.** The node is entered like any map node. It shows two mode buttons plus LEAVE. One mode per visit, then the node is spent. Leaving without acting is legal and costs nothing, though the preview shows the choice is being wasted.

**Mode A: PATCH (heal).**
- Heals through the existing HEAL effect with `amount_mode = PERCENT` (R5): a share of the operative's max HP. This follows R2: percent amounts read the owner's own max HP and are never rescaled. A flat amount would be worth far more to a 45 HP Botnet than a 60 HP Breaker, so percent is the fair mode.
- `rest_heal_pct` = 35 (config key on `campaign_config.tres`). Examples: Breaker 60 HP → 21; Botnet 45 HP → 15.75, rounded to 16 (round half up). The result is clamped to max HP, and the preview shows the clamped number.
- Tier and ICE do not scale it. The Heat chip and Heat bands do not scale it either (see §5).
- Does not cure statuses; wheel statuses already end with combat.
- Choice: 35% is above the heal a typical Router fight costs (about 10–15 HP lost at T1–T2) but below one Elite's cost at T3+. Each REST is a real recovery, not a full reset, so full-heal-and-forget is not available.

**Mode B: REWIRE (swap Firmware locations).**
- **Meaning:** swap the sockets of exactly **two slices** on the operative's own wheel, carrying their Firmware with them. Only the Firmware moves. The slice itself (type, base values, tick size, status) stays where it is.
- Concretely: slice X holds Firmware F1 and slice Y holds F2 (or nothing). After REWIRE, X holds F2 and Y holds F1. Moving a Firmware onto an empty slice is a legal "swap" with an empty socket, and this covers the common one-Firmware case.
- **Scope:** outer-ring slices only. Inner Ring segments are not rewirable (G1 redesign pending; the ring does not read well today). Daemons are run-wide and have no location.
- **Limit:** one swap per REST visit (`rest_rewire_swaps` = 1).
- **Cost:** no HP cost, no RAM cost, no Cycles. The cost is the opportunity cost of not healing. If playtests show REWIRE is chosen at full HP every time, the fallback is `rest_rewire_cycles` = 0 raised to a small Cycles fee (see Q1).
- **Restrictions:**
  - Firmware with the permanent flag "fixed" (Hardened/Burner fixed sockets, if the Firmware data sets `lock_socket`) cannot move. Initial data: none are fixed, so the field defaults to false.
  - Slice-specific compatibility is preserved: Firmware that requires a type (Leech: SHIM slice) is **not** movable onto an incompatible slice. The UI greys incompatible targets and explains why.
  - The swap respects R11 variable sizes: it moves Firmware only, so sub-tick maps are unaffected. A "Calibrated" Firmware that raises sub-ticks moves with the Firmware, which is the intended play (move it to a 4-tick slice to give it a Perfect).
- **Why this meaning:** it creates a real puzzle (neighbour reads for Mirror/Shunt, which slice sits under the next pointer) without touching slice rearranging, which the designer ruled low priority (G1: rearranging not a priority). No random output, so the preview is exact.

## 3. Placement & generation

- **Layers:** REST may appear on layers 3–6 of the 7-layer map. Never layer 1 (all Routers, GDD 4.2) and never layer 7 (the single final Rack node).
- **Count:** exactly **1 guaranteed REST per netrun**, placed on layer 4 or 5 (at or after the layer-4 Rack choice). A second REST is allowed on tier T3+ (`rest_extra_chance` = 0.35 on layers 3–6, excluding the layer holding the guaranteed one). Maximum 2 per run. Hard cap prevents a heal-spam path.
- **Guarantee:** at least one path from layer 1 to the final Rack passes through a REST. This means a player who wants it can always reach it, but a player skipping it also can. A graph with the REST on only a side branch is acceptable as long as one full path exists.
- **Layer share:** REST replaces one Terminal's slot in the "Terminals ≈ 25% of remaining nodes" budget. It does not replace Routers, Elites or the Mainframe guarantee (at least one Mainframe in layers 3–5 stays).
- **Adjacency exclusions:** REST is never on the same layer as another REST, never directly before a Mainframe on the same path where it forms a 2-node pure-recovery chain (to avoid stacking the cluster of no-risk nodes), and never in the layer immediately after the layer-6 Elite cluster guaranteed... if an Elite sits on layer 6, REST is placed on layer 5 or earlier.
- **Weights by tier:** the guaranteed REST is present at every tier. The extra REST chance scales: T1 0, T2 0.15, T3 0.35, T4 0.35. Tier ladders are harsher; a second chance to heal matters more there.
- **Weights by corporation:** none. Corporation identity is not part of REST. The Heat band modifies nothing in generation (the generator cannot read live Heat, only the seeded `map` stream).
- **RNG:** uses the existing `map` stream (TECH_SPEC §6). The guaranteed placement consumes a fixed number of draws (layer pick, then node pick within the layer) after the Rack and Elite placement and before the Terminal fill. Extra-REST roll is one draw. This ordering is part of the data contract. `run_graph.json` gains node type `REST` (NA-02 version bump or included in v1 if drafted before the contract freezes).
- **Existing-map compatibility:** the new node type changes map generation, so pre-change saves in progress are dropped (consistent with D3).

## 4. UX flow

1. The player selects the REST node on the map (full-graph look, D7). Hover shows a warm card: "REST: heal 35% or rewire one Firmware".
2. Entering plays the room beat: a warm-light interior (see below). Operative card on the left with HP bar and wheel. Two large buttons: **PATCH** and **REWIRE**, plus LEAVE.
3. **PATCH hover:** the HP bar ghosts to the new value ("+21 → 54/60"). No other preview needed; it is deterministic.
4. **PATCH commit:** one click, then a confirm-free application (a single clear action; undo is available until the node is left).
5. **REWIRE flow:**
   1. The wheel appears large. Slices with Firmware are highlighted; the player picks a source slice (click or number key 1–6).
   2. Valid target slices light; invalid ones grey with a reason tooltip ("Leech needs a SHIM slice").
   3. Picking a target shows the **after-wheel preview**: both slices with their new Firmware, the changed neighbour reads (Mirror/Shunt effects text updates live), and the per-slice sub-tick maps (R11).
   4. **CONFIRM** applies and spends the node.
6. **Cancel/Undo:** until CONFIRM or PATCH is pressed, Esc/BACK returns to the two-mode screen. After commit, a single **UNDO** is available while the player stays on the node screen, restoring the pre-visit state (HP or socket layout); leaving the node commits permanently. This respects rewind principles without adding a checkpoint (no randomness is involved).
7. Leaving marks the node as spent on the map, with the sticker changed to the used state.

**Text keys:** `rest.title`, `rest.patch.label`, `rest.patch.preview`, `rest.rewire.label`, `rest.rewire.pick_source`, `rest.rewire.pick_target`, `rest.rewire.invalid.<reason>`, `rest.confirm`, `rest.leave`, `rest.spent`, `rest.hover.card`, `rest.tutorial.first_visit`.

**Presentation hooks (art side):**
- Warm light: the node room uses the warm amber point-light preset (the one low-saturation "inhabited" colour in a cold-neon city) and a slow flicker, with the beam and fog shader settings at their lowest tier. The room should be the calmest one on the route and read as safe from the overview.
- Sticker: a vinyl sticker with a single glyph (a bed/cot or a plug-in battery), warm yellow on the route overlay, distinct from Terminal and Mainframe glyphs. Used state: the sticker is half peeled with a pencil strike-through.
- Hover power cut (§9.4) behaves as for other nodes.
- Audio: a low room-tone loop, a softer UI click set, no combat bed.
- Reduced-effects path: no flicker; static warm light.

## 5. Interactions

- **Heat:** REST adds **0 Heat** (like Router/Terminal/Mainframe). Heat does not scale its heal. It is a rare safe node, so it does not feed raids or thresholds. Heat modifiers that remove or alter nodes (a "no REST" modifier) are deliberately **not** added. A MINOR-threshold complication may not delete the REST (the guaranteed one stays); extra elites may be added elsewhere.
- **Death rules (GDD 4.2):** REST does not change them. Death still loses everything unbanked. REST is never a banking point and never a save-checkpoint reward; a REST does not bank assets or Schematics.
- **Raids:** a mid-run raid interlude between map nodes does not occur inside the REST screen. If a raid is scheduled, it triggers on leaving the node, as for other nodes.
- **Daemons/Firmware:**
  - Daemons with a heal trigger could add a bonus (Q3). Initial data: none.
  - Burner (permanent OVERCLOCKED, +1 Heat per trigger) moves like any Firmware, which makes REWIRE a way to put it on a slice you will not resolve this fight.
  - Mirror/Shunt rely on neighbours; REWIRE is their main tuning tool.
  - A new Daemon hook `ON_REST_ENTER` is not required for the first version.
- **Other nodes:** Mainframe can sell Firmware; REWIRE then lets the player place it without buying a Patch slice. REST never offers a shop and never an event outcome.
- **Exploits:** none; REST is not an Exploit holder. The Site's Exploit sits on the final Rack as before.
- **Tiers:** REST appears at all tiers. Extra-REST chance rises with tier (§3). The heal percentage is tier-independent (R2).
- **Compiler Rack and campaign nodes:** no relation. A future Safehouse or Proxy upgrade could add a bonus; not in scope.
- **Boss netruns (HQ):** HQ runs are unique per corporation (G12); this draft does not include REST in them. The HQ designer rules per corporation, and the generator accepts an HQ graph with zero RESTs (§6).

## 6. Data & systems

New data:
- `InfilNodeType.REST` appended to the enum (append only, to keep saved ints).
- `campaign_config.tres` keys: `rest_heal_pct` (35), `rest_rewire_swaps` (1), `rest_guaranteed_count` (1), `rest_guaranteed_layers` ([4, 5]), `rest_extra_chance_by_tier` ([0, 0.15, 0.35, 0.35]), `rest_max_per_run` (2), `rest_eligible_layers` ([3, 4, 5, 6]).
- `FirmwareData`: `requires_slice_types` (array, empty = any) if not already derivable, and `lock_socket` (bool, default false).
- `MapGraph`: node type REST, and a generator pass with the placement rules above. The pass is a pure function of the `map` stream; a validator checks guarantees.
- `RunState`: a `rest_used` flag per node (saved). A rewired layout is written into the operative's wheel data.
- `NetrunSession`: `apply_rest(mode, params)` with a validated preview function `preview_rest(mode, params)` returning the numbers the UI shows; the preview equals the result because no RNG is read.
- UI: a REST page reusing the wheel kit and the loadout wheel view; route-overlay sticker and glyph; room preset for the street netrun view (NA-23 room kinds).

Systems:
- **N1 amount modes** (PERCENT heal): needed. Data fallback: a precomputed flat heal from max HP in the session, but this duplicates N1 and is not recommended.
- **N2** is not needed. **N12** (variable slice sizes) is only a soft link: REWIRE works on 5-tick slices alone, and the sub-tick map in the preview appears once N12 lands.
- **N18** (data-driven rewards) is not needed.
- Art: NA-23 room kind plus NA-24 dressing; this is the "heal / rest markers" item the replan holds for D4.

Size: **M** (generator pass + session action + page + sticker/room hooks). A data-only slice (PATCH only, no UI beyond a button) is **S** and can ship first.

## 7. Examples

1. **Breaker, T1, layer 4 REST.** HP 36/60, wheel: Overflow(Patch+), Shim, Shim, Shim(Leech), Defrag, Null. PATCH heals 35% = 21 → 57/60. REWIRE alternative: move Patch+ from Overflow (slice 0) to Shim (slice 1) so it lands in a more reachable arc; Patch+ has no type requirement, so it is legal. Player is at 60% HP with an Elite on layer 5, so PATCH.
2. **Rigger, T3, layer 5 REST (second one rolled).** HP 52/55. PATCH would heal 3 (the clamped preview says "+3"), so the player chooses REWIRE. Firmware: Mirror on slice 2 (Shim), Calibrated on slice 4 (Defrag, 4 ticks). Move Calibrated to slice 3, a 4-tick Shim, so its sub-ticks read G P P G and Mirror's copied neighbour is now a Perfect-capable slice. The preview shows the new neighbour output text before CONFIRM.
3. **Botnet, T2, layer 4 REST.** HP 45 max, 20/45. PATCH = 35% = 15.75 → 16 → 36/45. REWIRE has one Firmware (Hardened on a Trojan slice), and moving it to the Shim slice is allowed but pointless; the screen shows "no better layout found" only as a neutral hint? No: the game does not give advice. The player simply heals.

## 8. Risks & balance notes

- **REWIRE at full HP becomes free:** with no cost, the optimal play is to always choose the strictly better mode at the moment, which is fine, but the HP-full case makes PATCH worthless and REWIRE a free action. Mitigation: placement is rare (1–2 per run), so REWIRE is a limited resource. Test: share of REST visits choosing REWIRE per HP band; flag if above 80% at HP above 80%.
- **Heal inflation:** 35% per REST plus 2 RESTs on T3+ may double effective HP across a run and soften the boss-win baseline further? The baseline says T4 bosses win 4–8% in campaigns, so the relative shift is small. Test: ICE 0/5 campaign win rate and minutes against ~395, with `rest_heal_pct` at 25/35/45.
- **Route forcing:** the guaranteed path rule means REST is never skippable by graph structure, but the player can still skip it. Test: fraction of runs where a REST is taken, by tier.
- **Layer 4 overlap with the optional Rack:** the layer-4 Rack is a risk/reward choice; a REST on the same layer competes with it. This is intended tension; test that the layer 4 REST does not remove the Rack option (the generator keeps the Rack).
- **Death-heat interplay:** REST makes dying later less likely, so Heat from death falls slightly. This is acceptable; check Heat curves.
- **Determinism:** the heal is integer-rounded with a documented rounding rule (half up); previews use the same function. Sim metrics: REST visited, mode, HP before/after, Firmware moved.
- **Mid-run saves:** saving on the REST screen must store the unspent state; quitting and reloading cannot allow both modes (the `rest_used` flag is set at commit).

## 9. Q:

Q: Should REWIRE cost something (a small Cycles fee or 1 Heat) to keep it from being the default at high HP, or is the opportunity cost enough?
Q: Should REWIRE be allowed to swap two slices' Firmware only, or also move a Firmware to an empty socket (this draft: yes)? Confirm the empty-socket case.
Q: Should a Daemon family hook REST (for example a "Field Medic" Daemon: PATCH +10%), and if so does it need an `ON_REST_ENTER` trigger?
Q: Do HQ netruns (unique per corporation, G12) include REST nodes, or is the sustain there authored per HQ?
Q: Is the Inner Ring included in REWIRE once the G1 redesign settles how segments are manipulated?
