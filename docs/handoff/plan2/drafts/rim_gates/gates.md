<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01NeYS5u3wGiiBtezG2p3UAd, custom_id rim__gates; status ok; tokens in 17864 cache-write 0 cache-read 32585 out 5607; cost $0.049. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# rim_gates: mechanic design

## 1. What a rim gate is

A **rim gate** is a marker on one tick boundary of a wheel's rim. It is fixed to the wheel's **tick frame**, not to a slice and not to the pointer. It does not rotate with the wheel; it marks "tick position g". The wheel's slices slide past it. A pointer or needle is a position in the same frame, so the real question a gate asks is: **did this move carry the wheel's content past tick g?**

Decision: gates sit on the tick frame, not on the wheel's content (the slices), because content-bound gates would be crossed by nothing. Pointers are also fixed in the frame, so "a gate crossed by a needle" and "the wheel rotated past the gate" are the same event. This is the Orbital draft's wording: a move that "carries a gate past its needle".

**Owner and scope.**
- A gate belongs to a wheel and has an `owner_side` (who triggers it, who benefits).
- Gates exist on enemy wheels (boss, mini-boss, elite), player wheels (Firmware, Daemon, class, event) and satellite wheels. A satellite's wheel is fixed (R12), so its gates can only be crossed by its own orbit or by the host's rotation. Default: satellites have no gates.

**Crossing vs stopping.**
- **Cross:** the move's path passes over tick g and ends past it (a gate sits between tick g−1 and g, the "edge before tick g").
- **Stop (rest):** the move ends with the needle exactly on tick g, a pointer resting on the gate.
- A cross fires the gate's `on_cross` effect. A stop fires an optional `on_rest` effect (some types have only one). Most types use cross only; **Latch** (§3) uses rest only.
- Stopping on a gate never counts as crossing it. The gate is the edge entering tick g, so the move that arrives at g crosses it and then rests there. Rule: arrival at g from either side crosses the edge once, and `on_rest` fires in addition.

## 2. Rules

**Edge model.** Gate g sits on the edge between tick g−1 and tick g (mod 30). A move of the wheel by k ticks passes k edges. A gate fires once per edge passed.

**Traversal by action:**

| Action | Counts? | Rule |
|---|---|---|
| Nudge ±1 | Yes | Passes 1 edge; fires if that edge is a gate. |
| Card Spin N | Yes | Passes N edges in order, after resistance: only the ticks that actually move the wheel count. Resistance-absorbed ticks cross nothing. |
| Start-of-turn spin/respin (random) | **No** | Excluded in all forms. Respin card, 4 RAM respin and the turn-start respin never traverse. |
| Flip, Snap to center | **No** | A teleport; no path. Mirror/Shunt neighbour resolves don't move the wheel. |
| Orbit / Migrate (boss motion) | **No by default** (`counts_orbit` flag) | Passive pointer motion is enemy-authored, so not gate-triggering unless a gate sets `counts_orbit`. |
| Freeze | No move. | |
| Linked Bus echo | Yes, if it actually rotates the wheel via nudge. | |

**Direction.** Gates may be `direction = ANY / CW / CCW`. Default ANY.

**Who triggers.** Each gate has `trigger_by`: PLAYER_ACTIONS (default), ENEMY_ACTIONS, or ANY. This resolves the Orbital draft's open question: only player nudges and spins by default; the enemy's orbit never crosses unless flagged.

**Order and multiple gates in one move.**
1. The move is resolved first, with resistance applied.
2. Crossed edges are listed in path order (from the start tick toward the end tick).
3. Gates fire in that order, each once per crossing. Two gates in one 12-tick spin both fire; the same gate twice in a 30+-tick spin fires twice, but a spin over 29 is capped per gate to 1 per action (`once_per_action`, default true; this stops a Spin 60 from becoming a combo).
4. Gate effects resolve after the move and after the ON_NUDGE/ON_CARD_PLAYED listeners (N6), but before the next action. Effects are staged and undo with the action.
5. A cap `max_fires_per_turn` (default: unlimited for countdown-type, 1 for damage types) limits stacking.

**Interactions:**
- **Threshold parking (R3):** gate damage to a boss goes through `deal_hit`, so the floor applies and excess is lost. A gate effect that would push the phase threshold is parked like any hit. A phase change from a gate hit happens at the end of the resolve, so it also resolves late-lost hits.
- **Variable slice sizes (R11):** gates are on ticks, not slices, so sizes don't matter. A gate may also be placed with `at = SLICE_BOUNDARY(i)` at authoring time, which converts to the tick of that boundary and, with sizes summing to 30, stays valid.
- **Tick quality:** a gate on tick g does not change the quality map. A gate's `on_rest` can apply "quality −1 tier" (Latch type) as a TIER_DOWN-like rule.
- **Satellites:** moving the host carries satellites with it, and the host's crossings fire; the satellite's own mini-wheel is separate and fixed. Satellites never trigger the host's gates.
- **Statuses (R6):** statuses move with slices, gates stay put. A status is never "crossed". A gate can apply a status at crossing.
- **Parasite ring (N10):** a parasite ring rotates with the player wheel. Player gates are on the tick frame, so parasite segments passing a gate don't count. A Parasite segment may carry its own gate type later, reading the same rules.
- **Phase change:** gates are part of a phase's wheel override. A new phase replaces its gate list; counters reset unless `keep_counter`.

**Determinism and preview.**
- Traversal is a pure function of (start rotation, applied ticks, direction). No randomness.
- The preview of any nudge, spin or hovered card lights the gates it would cross and the effects (e.g. "COUNTDOWN 1→2", "−6 to boss, PARKED −2"). Preview = result because both use the same `crossed_edges(start, applied_ticks)` helper.
- Gate counters are CombatantState fields, checkpointed with the turn and undo-clean.

## 3. Gate types (catalog)

| # | Type | Trigger | Effect (placeholders) | Who benefits |
|---|---|---|---|---|
| 1 | **Countdown** | cross, player | +1 counter; at N, fires a payload (add an OVERFLOW resolve, then reset) | Enemy |
| 2 | **Toll** | cross, player | Player pays 1 RAM per crossing (FLAT), or 25 % extra on a card | Enemy |
| 3 | **Breach / Abort** | cross, player | Deals 6 FLAT to the wheel's owner (once per gate per turn) | Player, vs the wheel's owner |
| 4 | **Latch** | rest | A needle stopped on the gate has its tier read one lower (TIER_DOWN, one landing) | Enemy |
| 5 | **Charge** | cross, any | Stores 1 charge on the wheel; at 3 the wheel's next hit gets ×1.5 | Whoever owns the wheel |
| 6 | **Vent** | cross | Removes one status from the slice currently under the crossed pointer, or cleanses one CORRUPTED slice | Whoever owns the wheel |
| 7 | **Mint** (player-side) | cross | +1 RAM, max once per turn (Firmware "Rim Dynamo") | Player |
| 8 | **Anchor** | cross, enemy | Enemy-side: absorbs 1 tick of nudge resistance per crossing, a soft Compliance Lock. | Enemy |

**Player-side sources.**
- **Firmware** "Rim Dynamo" adds a Mint gate at a chosen tick of the player's wheel (the socket's slice boundary).
- **Daemon** "Gatekeeper": cross a player wheel gate with a nudge, +2 BLOCK.
- **Class** (one class's Core): a Charge gate at tick 15 of its own wheel.
- **Event:** a "install a gate" choice, with a Heat or HP cost; also a negative event ("jam a gate onto your wheel", an enemy Toll).
- Player wheel gates are crossed only by the player's own nudges and spins (`trigger_by = PLAYER_ACTIONS`), which makes spin-heavy classes and Linked Bus meaningful.

**Amounts:** all FLAT enemy amounts × tier damage factor (R2); PERCENT amounts read the owner's max HP. Gate damage to a player is never scaled by buffs.

## 4. Readability and counterplay

**Art/HUD.**
- A gate is a notch and chevron on the wheel's rim, in the frame colour of its owner (enemy red, player cyan), with an icon for its type. It is drawn on the fixed frame, so the wheel visibly slides under it. A counter pip row sits at the gate.
- On hover or while dragging a nudge/spin, the path of edges is highlighted, and each gate it crosses flashes with its effect text. A crossed-gates tooltip lists totals.
- The result chip adds "GATES: Countdown +1, Toll −1 RAM".

**Learning.**
- The first gate encountered is a Breach/Abort type on a T1 elite (positive for the player): the first crossing is rewarded, so the player learns "gates matter" without a punishment.
- Codex entry plus a one-line tutorial line at the first gate on the first preview.

**Counterplay.**
- **Route around:** the path is the choice. Use the shorter way (nudge ±1 either direction), or use cards that don't traverse (Flip, Snap).
- **Disarm:** cards Jam/Strip move the enemy wheel; **Cleanse-style** "Jam Gate" cards disable a gate for one turn; the matching Exploit (R7) removes a boss's gate type permanently.
- **Move:** a rare card "Reposition" shifts one gate by ±3 ticks.
- **Exploit:** the Abort type turns a boss's own constraint into player damage.

**Anti-frustration rules.**
- A gate never fires on the turn-start respin, so the player never starts a turn with a penalty they could not see and avoid.
- A move that would fire a harmful gate is marked in red before commitment and is freely undoable (rewind).
- A harmful gate effect has a hard cap per turn: at most 2 fires of Toll and 1 Countdown step per turn.
- Gates are never placed so every tick of the player's reachable free-nudge range crosses one: the free nudge ±1 must always have a non-crossing option (validator rule: no two harmful gates adjacent within 1 tick).
- Never more than 3 gates on one wheel.

## 5. Worked example: Orbital mini-boss, T3 (HP 150)

P1 Countdown: gates at ticks 7 and 22 (Countdown type, player-crossed), needle at tick 0. Enemy layout: Shim 6 · Defrag 4 · Overflow 5 · Flare 5 · Null 6 · Shim 4 (sum 30).

Start-of-turn spin leaves rotation r. The player wants Null under the needle. Suppose Overflow is at the needle and Null needs +8 ticks.
- A Spin 8 card moves 8 edges, resistance 1 absorbs 1, so 7 move: from rotation 0 to 7, crossing edges 1…7, which includes edge 7 (gate A). Countdown 0→1. Preview: "COUNTDOWN 1/3".
- A better plan: two nudges (1 free, 1 for 1 RAM) of +1 each, plus Flip, crossing no gates. Cost 1 RAM.
- A greedy Spin 15 from rotation 0 crosses gate A (edge 7) and gate B (edge 22 isn't reached; 15 ticks reach 15), so only A. A Spin 25 crosses both: Countdown +2.
- At Countdown 3 the next resolve adds an OVERFLOW at 8 → ×tier 1.69 = 13.5 at T3 (taken from 8). Counter resets.

P3 Abort Window: gates are retyped to Breach/Abort (6 FLAT to the Director, once per gate per turn, owner = player-benefit). The player's Spin 25 crosses both gates: 12 damage. With the floor at 33 %: Director HP 150, P3 floor 0 (last phase), so no parking. In P2 the same crossing would park at the 66→33 floor, and the excess is lost.

Hotfix heals 3 % = 4.5 → 4 per turn, so 12 damage per big spin is about 3× the heal. This makes P3 about 3–4 turns at 14 dpt plus gate damage.

## 6. Data and systems

**Fields (new, on WheelData and a phase override):**
- `WheelData.gates: Array[RimGateData]` (max 3).
- `RimGateData`: `tick: int` (0–29, edge before this tick), `gate_type` enum, `trigger_by` (PLAYER / ENEMY / ANY), `direction` (ANY/CW/CCW), `on_cross: Array[EffectData]`, `on_rest: Array[EffectData]`, `amount_mode`, `amount`, `counter_max`, `max_fires_per_turn`, `once_per_action`, `counts_orbit`, `owner_side`.
- `BossPhaseData.gates_override` (replace the list; `keep_counter` flag).
- CombatantState: `gate_counters: Dictionary`, `gate_fires_this_turn`.
- `WheelMath.crossed_edges(start, applied_ticks, dir) -> Array[int]`.

**N15 scope (M).**
1. `WheelMath.crossed_edges` plus unit tests.
2. Hook in `effect_interpreter.nudge/spin` after resistance, calling a `GateResolver` that stages effects.
3. Preview lighting (shares the resolver in dry-run mode).
4. HUD notch and chip.
5. Validator (max 3, spacing rule).

**Rollout.**
1. Core helper + Countdown, Breach/Abort, Toll (needed by the Orbital mini-boss).
2. Preview and art.
3. Player-side gates (Mint, Charge) and Firmware/Daemon hooks.
4. Latch, Vent, Anchor and the Reposition card.

**Fallback (data-only).** None for the crossing itself; the signature needs N15. Interim: a "no gate" Orbital P1 using the Hub's resistance 2 and Overflow tempo, which loses the signature.

**Tests (preview == result):**
- A nudge ±1 across a gate fires once; a nudge not crossing fires none.
- Spin N with resistance R crosses exactly N−R edges.
- Spin 29+ fires each gate at most once (`once_per_action`).
- Respin, turn-start spin, Flip, Snap and orbit never fire.
- Rewind restores counters; the rewind-and-redo is identical.
- Preview text equals post-action state for 1000 random (start, spin) pairs.
- A gate hit that crosses a phase floor parks the HP.
- Gates are preserved or replaced across phases per `keep_counter`.
- Variable slice sizes: a gate's behaviour is unchanged.
- Satellite host moves fire only the host's gates.
- A save/load mid-turn preserves counters.

## 7. Open questions

Q: Is "once per gate per action" too forgiving, since a Spin 30 would then cross everything once? Or should the gate fire per full revolution?
Q: Should the enemy's own orbit (P3 Orbital) ever fire gates, or stay excluded for readability?
Q: Does a player Linked Bus echo on the enemy wheel count as a player action for gate triggers?
Q: Is a three-gate cap per wheel right, given 30 ticks and uneven needles?
Q: Should Toll gates cost RAM at the corrupted 2× rate (R9), or a flat 1 RAM?
