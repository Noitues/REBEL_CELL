<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__nodes__rest; status ok; tokens in 9374 cache-write 0 cache-read 32585 out 5944; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, T3+ vs T2 0.15, key mismatch):** the only extra-REST key is `rest_extra_chance_by_tier` = [0, 0, 0.35, 0.35]. The T2 0.15 is removed, and the prose now matches the key (T3 and T4 only).
- **Issue 2 (BLOCKER, vacuous guarantee):** the guarantee is redefined. The generator places one REST on layer 4 or 5, and a validator requires that every layer-3 and layer-4 node can reach a REST node within one further node choice. If the check fails, it re-places using the same `map` stream draw count. The §8 "never skippable" claim is replaced with "reachable by at least one route, and by a one-node detour from every branch point at layers 3-4". The guarantee covers reachability, not forced entry.
- **Issue 3 (MAJOR, broken adjacency sentence, placement order):** rewritten as: no REST on layer 6 if that layer holds a guaranteed Elite, and none on a layer adjacent to the Mainframe's guaranteed layer. Placement runs after Rack, Elite and Mainframe and before the Terminal fill. The layer-4 Rack is never displaced, because REST takes only a Terminal-budget slot.
- **Issue 4 (MAJOR, invented Firmware fields):** both fields are marked "NEW: Firmware socket rules (S)". The default is that any Firmware moves to any outer slice, and the fields are added only if a Firmware needs them. The Leech, Hardened and Burner claims are dropped. Examples are re-checked against the default.
- **Issue 5 (MAJOR, example 3):** the self-correction is removed. The ending is now "REWIRE has no useful swap, so the player PATCHes: 20/45 → 36/45".
- **Issue 6 (MAJOR, UNDO / `rest_used`):** state commits only when the player leaves the node. UNDO is node-local until then, and `rest_used` is set on leave. A quit mid-node reloads the unspent node, so an exploit cannot gain both modes.
- **Issue 7 (MAJOR, sustain numbers):** all REST numbers are marked pending the sim, and the "10-15 HP per Router fight" figure is labeled an unmeasured estimate.
- **Issue 8 (NIT, Heat hook):** replaced with "Heat: none".
- **Issue 9 (NIT, NA refs, N#):** NA-02, NA-23 and NA-24 references are replaced with plain descriptions. The generator is marked NEW: REST node generator (M), with the fallback of a PATCH-only Terminal-style event.
- **Issue 10 (NIT, "retune" overstates):** §1 now says "adjust" and states that one swap is a small adjustment.
- **Critic Qs:** the guaranteed-count and campaign-length concern is carried into Q1. Leaving without acting: kept as "leave without acting does not spend the node" (nothing happened, nothing to spend); Q3 asks whether it should. The sustain-cap question is noted in §8 as a sim item.
- **Triage rows:** both are covered by issues 1 and 2. The phase-budget arithmetic tag is addressed by checking that REST adds no enemy HP or phase load, and that the sustain it gives is node-level (see §8).

# REST (netrun node): design draft

## 1. Purpose & the decision it creates

REST is the one place on a netrun map where the run stops being a gauntlet. HP carries between fights and no other sustain exists, so each REST asks one question: **repair the body, or adjust the build?** Mode A (PATCH) restores HP. Mode B (REWIRE) swaps where installed Firmware sits on the wheel. Slice position decides when a slice lands and which neighbours Mirror and Shunt read, so one swap is a small but real build decision. A healthy operative with a poor layout should rewire. A sound layout at 40% HP should patch. The player weighs this against what lies ahead: an Elite, the layer-4 Rack, and Heat already paid. REST never grants both modes in one visit and never adds power. It converts tempo into HP or arrangement.

## 2. Rules

**Entry.** REST is entered like any map node. It shows PATCH, REWIRE and LEAVE. One mode per visit. Leaving without acting does not spend the node; it can be re-entered (see Q3).

**Mode A: PATCH (heal).**
- Uses the existing HEAL effect with `amount_mode = PERCENT` (R5): a share of the operative's own max HP, never rescaled (R2). Percent is fair across a 45 HP Botnet and a 60 HP Breaker.
- `rest_heal_pct` = 35 (`campaign_config.tres`). Breaker 60 → 21; Botnet 45 → 15.75, rounded half up to 16. The result is clamped to max HP, and the preview shows the clamped number.
- Tier, ICE and Heat do not scale it. It cures no statuses (wheel statuses end with combat).
- 35% is a placeholder. The assumption that a Router fight costs 10-15 HP at T1-T2 is an unmeasured estimate. The sim must confirm that a REST is a real recovery, not a full reset.

**Mode B: REWIRE (swap Firmware locations).**
- **Meaning:** swap the sockets of exactly two outer-ring slices on the operative's own wheel, carrying their Firmware. Only Firmware moves; slice type, values, tick size and status stay put.
- Moving a Firmware onto an empty socket counts as a swap with empty. This covers the common one-Firmware case.
- **Scope:** outer-ring slices only. Inner Ring segments are not rewirable (G1 redesign pending). Daemons are run-wide and have no location.
- **Limit:** `rest_rewire_swaps` = 1 per visit.
- **Cost:** no HP, RAM or Cycles. The cost is not healing. If REWIRE dominates at full HP, the fallback is a small `rest_rewire_cycles` fee (Q2).
- **Socket rules (NEW: Firmware socket rules, S):** by default any Firmware moves to any outer slice. Optional fields `requires_slice_types` and `lock_socket` are added only if a Firmware needs them. Data fallback: none declared, so all swaps are legal.
- **R11 interaction:** the swap moves Firmware only, so sub-tick maps are unaffected. A tick-raising Firmware (placeholder "Calibrated") moves with its chip, for example onto a 4-tick slice to turn G G into G P P G reads.
- **Why this meaning:** it makes a real puzzle (neighbour reads, which slice sits under the next pointer) without slice rearranging, which G1 ruled low priority. There is no randomness, so the preview is exact.

## 3. Placement & generation

- **Eligible layers:** 3-6 of the 7-layer map. Never layer 1 (all Routers) or layer 7 (the final Rack).
- **Guaranteed REST:** exactly one per netrun, on layer 4 or 5. The generator validates that every layer-3 and layer-4 node reaches a REST within one further node choice. If the check fails, it re-places using the same fixed `map` stream draw count. The guarantee is reachability by at least one route, not forced entry; skipping stays legal.
- **Extra REST:** `rest_extra_chance_by_tier` = [0, 0, 0.35, 0.35]. So only T3 and T4 can roll a second REST, on an eligible layer other than the guaranteed one's. Maximum 2 per run (`rest_max_per_run`), which prevents heal-spam.
- **Budget:** REST takes one slot from the Terminal share ("Terminals ≈ 25% of remaining nodes"). It never replaces a Router, an Elite, the Mainframe guarantee (at least one in layers 3-5) or the layer-4 Rack option.
- **Exclusions:**
  - No REST on layer 6 if that layer holds a guaranteed Elite.
  - No REST on a layer adjacent to the Mainframe's guaranteed layer.
  - Never two RESTs on one layer.
- **Order:** placement runs after Rack, Elite and Mainframe, before the Terminal fill.
- **Corporation weights:** none. The generator cannot read live Heat; it reads only the seeded `map` stream.
- **RNG:** existing `map` stream. The guaranteed pick uses a fixed draw count (layer, then node within the layer), and the extra roll is one draw. This ordering is part of the data contract. The `run_graph` save gains node type REST, and saves in progress are dropped (D3).

## 4. UX flow

1. The player selects the REST node on the full-graph map (D7). Hover card: "REST: heal 35% or rewire one Firmware".
2. Entering shows a room with the operative card (HP bar, wheel), two large buttons PATCH and REWIRE, and LEAVE.
3. **PATCH hover:** the HP bar ghosts to the new value ("+21 → 54/60"). The preview is deterministic.
4. **PATCH commit:** one click applies it on-screen without a confirm dialog.
5. **REWIRE flow:**
   1. The wheel appears large. Slices with Firmware are highlighted. The player picks a source slice by click or keys 1-6.
   2. Valid targets light. If socket rules ever exist, invalid targets grey with a reason tooltip.
   3. Picking a target shows the after-wheel preview: both slices with new Firmware, updated Mirror and Shunt text, and the sub-tick maps (R11).
   4. **CONFIRM** applies the swap on-screen.
6. **Cancel and Undo:** before a mode is applied, Esc or BACK returns to the mode screen. After applying, a node-local **UNDO** restores the pre-visit state and re-offers both modes. State is written to the run only when the player leaves the node, and `rest_used` is set then. Quitting on the node reloads it unspent. UNDO is not a checkpoint rewind and involves no randomness.
7. Leaving after an applied mode marks the node spent with the used sticker. Leaving without acting leaves it available.

**Text keys:** `rest.title`, `rest.patch.label`, `rest.patch.preview`, `rest.rewire.label`, `rest.rewire.pick_source`, `rest.rewire.pick_target`, `rest.rewire.invalid.<reason>`, `rest.confirm`, `rest.undo`, `rest.leave`, `rest.spent`, `rest.hover.card`, `rest.tutorial.first_visit`.

**Presentation hooks:**
- A warm amber low-saturation room light with a slow flicker, the calmest room on the route. The reduced-effects path uses static light.
- A vinyl sticker with a bed or battery glyph, warm yellow, distinct from Terminal and Mainframe. The used state is half peeled with a pencil strike-through.
- A low room-tone loop and a softer UI click set, with no combat bed.
- Hover power cut behaves as for other nodes.

## 5. Interactions

- **Heat:** REST adds 0 Heat and Heat does not scale its heal. No Heat hook is added.
- **Death (GDD 4.2):** unchanged. REST is not a banking point and banks no assets or Schematics.
- **Raids:** a scheduled mid-run raid triggers on leaving the node, as for other nodes.
- **Daemons and Firmware:** no Daemon hooks in the first version. Mirror and Shunt depend on neighbours, so REWIRE is their tuning tool. Burner moves like any Firmware, so REWIRE can park it on a slice that won't resolve this fight.
- **Other nodes:** a Mainframe can sell Firmware, and REWIRE then places it. REST offers no shop and no event outcome.
- **Exploits:** none. The Site's Exploit stays on the final Rack.
- **Tiers:** REST is present at all tiers. The extra chance applies at T3 and T4 only. The heal percent is tier-independent (R2).
- **HQ netruns (G12):** this draft does not include REST in them. Each HQ is authored uniquely, and the generator accepts an HQ graph with zero RESTs.

## 6. Data & systems

New data:
- `InfilNodeType.REST` appended to the enum (append only, to keep saved ints).
- `campaign_config.tres` keys: `rest_heal_pct` (35), `rest_rewire_swaps` (1), `rest_guaranteed_count` (1), `rest_guaranteed_layers` ([4, 5]), `rest_extra_chance_by_tier` ([0, 0, 0.35, 0.35]), `rest_max_per_run` (2), `rest_eligible_layers` ([3, 4, 5, 6]).
- Optional `FirmwareData` fields `requires_slice_types` and `lock_socket` (NEW: Firmware socket rules, S), added only when needed.
- `RunState`: a `rest_used` flag per node, set on leave. A rewired layout is written into the operative's wheel data on leave.
- `NetrunSession`: `preview_rest(mode, params)` and `apply_rest(mode, params)`. The preview equals the result because no RNG is read.
- UI: a REST page reusing the wheel kit and loadout wheel view, a route-overlay sticker and glyph, and a room preset.

Systems:
- **N1 amount modes** (PERCENT heal): needed. Fallback: a flat heal computed from max HP in the session, which duplicates N1 and is not recommended.
- **NEW: REST node generator (M):** the placement pass and its validator. Fallback: PATCH-only through a Terminal-style event with no map change.
- **N12** is a soft link only. REWIRE works on 5-tick slices, and sub-tick maps in the preview appear once N12 lands. N2 and N18 are not needed.
- Art: a REST room kind and sticker dressing, the "heal / rest markers" item held under D4.

Size: **M** overall. A PATCH-only slice is **S** and can ship first.

## 7. Examples

1. **Breaker, T1, layer 4.** HP 36/60, wheel Overflow(Patch+), Shim, Shim, Shim(Leech), Defrag, Null. PATCH heals 21 → 57/60. The REWIRE alternative moves Patch+ from Overflow to a Shim slice. With the default socket rules it is legal. At 60% HP with an Elite on layer 5, the player PATCHes.
2. **Rigger, T3, second REST rolled.** HP 52/55, so PATCH shows "+3". The player REWIREs. Mirror sits on slice 2 (Shim) and a tick-raising Firmware on slice 4 (Defrag, 4 ticks). Moving it to slice 3, a 4-tick Shim, makes that slice read G P P G, and Mirror's copied neighbour is now Perfect-capable. The after-wheel preview shows the new neighbour text before CONFIRM.
3. **Botnet, T2, layer 4.** HP 20/45. PATCH = 15.75 → 16 → 36/45. The only Firmware is Hardened on a Trojan slice and REWIRE has no useful swap, so the player PATCHes: 20/45 → 36/45.

## 8. Risks & balance notes

- **REWIRE at full HP is free:** PATCH is worthless there. Mitigation: REST is rare (1-2 per run). Test the REWIRE share per HP band; flag it above 80% at HP above 80%.
- **Heal inflation:** 35% per REST, up to 2 on T3+, may soften fights. Test ICE 0/5 campaign win rate and minutes against ~395 with `rest_heal_pct` at 25/35/45. All REST numbers are pending the sim.
- **Sustain cap:** REST is a node-level heal between fights, not in-fight sustain, so the 30% per-turn cap (§4 pass criteria) and the R2 phase budget are unaffected. Confirm no pass criterion counts it.
- **Reachability:** test the share of runs where a REST is visited, by tier, and that the validator never fails to re-place.
- **Layer-4 Rack tension:** a REST on layer 4 competes with the optional Rack. This is intended. Test that the Rack is never removed.
- **Determinism:** the heal is integer-rounded half up and the preview uses the same function. Sim metrics: REST visited, mode, HP before and after, Firmware moved.
- **Saves and exploit:** `rest_used` is set only on leave, so reloading can't grant both modes. An UNDO-then-other-mode path is allowed by design and costs nothing.

## 9. Q:

Q: Is one guaranteed REST per run too generous given the baseline's 605-minute campaign against the ~395 target, or should it drop to T2+?
Q: Should REWIRE cost something (a small Cycles fee or 1 Heat) to keep it from being the default at high HP?
Q: Should leaving without acting spend the node (this draft: no)?
Q: Do HQ netruns include REST nodes, or is sustain authored per HQ?
Q: Is the Inner Ring included in REWIRE once the G1 redesign settles how segments are manipulated?
