<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__nodes__cache; status ok; tokens in 8836 cache-write 0 cache-read 32585 out 6685; cost $0.046. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, layout rule vs RNG):** The "never adjacent" rule is replaced by an explicit constraint on the start draw. Each authored layout has exactly one JACKPOT. The `events` draw picks the start among slices at ring distance 2 or 3 from the JACKPOT, excluding the TRIPWIRE. The candidate set is sorted by slice index and one draw picks an index into it. The forced tutorial start is declared as a data field on the tutorial layout, so it draws nothing and the stream is untouched. Example 2 is rebuilt to obey the rule.
- **Issue 2 (BLOCKER, nudge arithmetic):** The nudge moves one slice and the ring wraps. The cost is now a pure function: nudges to the JACKPOT = ring distance d, paid nudges = max(0, d − 1), cost = paid × per-nudge cost. Distance 2 costs 1 paid nudge and distance 3 costs 2, so `cache_max_nudges` = 3 covers both. A table shows this, and Example 1 is corrected ("free nudge, then 1 paid nudge").
- **Issue 3 (config keys):** The key list is rewritten with values: `cache_free_nudges`, `cache_max_nudges`, `cache_extra_nudge_heat`, `cache_extra_nudge_hp_pct`, `cache_trip_hp_pct`, `cache_trip_heat`, `cache_run_chance`, `cache_trip_cannot_kill`. `cache_nudge_ticks` and `cache_extra_nudge_cost` are deleted. The reward amounts live in a `cache_rewards` table.
- **Issue 4 (systems):** `CacheData` is now an `EventWheelData` row (N17), not a duplicate resource. The "N14/N1" label becomes N1. The new enum value is tagged "NEW: InfilNodeType.CACHE", approved by D4 with the puzzle vetted first. The `seen_cache` profile flag is tagged "NEW: profile flag". The N18 `slice_flash` note is added. The Terminal fallback is kept.
- **Issue 5 (HP attrition):** The tripwire PERCENT damage is listed as a loss path that cannot kill (floor of 1 HP). Compounding is addressed in §8: the PAY_HP caches use a 10 % trap, and the sim tracks net HP across Caches.
- **Issue 6 (dominated slices):** HEAT_DOWN is −4 in PAY_HEAT caches (net +2 against one paid nudge) and does not appear in PAY_HP caches. EMPTY is replaced by a small CYCLES 10. A "reason not to LEAVE" is added: the jackpot is worth more than the average slice, and the free nudge always escapes the TRIPWIRE (see Q2).
- **Issue 7 (nit, placement):** The Terminal-share relationship is stated explicitly. "Boss-only path" is dropped because it is undefined; the exclusion is now "layer 7 and the Rack slot".
- **Issue 8 (nit, wording):** "Turns" is replaced by "nudges" throughout.
- **Critic Q1 (hidden layout):** Kept fully visible, because hiding it breaks preview = result.
- **Critic Q2 (LEAVE cost):** Kept free, because a cost would punish the exact skip the player is meant to weigh. It is raised again as Q:2.
- **Critic Q3 (Heat as cost):** Kept, because Heat is the node's second currency. The PAY_HEAT HEAT_DOWN slice no longer undercuts Heat objective Sites, and the variant is tied to the corporation (a ruling on this is requested in Q:1).
- **Kept as strong:** slice-only reads, no tiers, no RAM, the checkpointed `events` draw, the forced tutorial start, free LEAVE, the TRIPWIRE that cannot kill, one cost currency per Cache.

---

# CACHE: design draft

**Verdict on EV4 "Dial the vault":** keep the idea, but change what the player reads, what a nudge costs and what is at stake, so it is not "another combat wheel". Slice-only landing (no PERFECT/GOOD/WEAK), no RAM, one cost currency per Cache (Heat or HP, never both), and a fully visible layout.

## 1. Purpose & the decision it creates
A Cache is a stash node on the netrun map (a locked lockbox in a server closet). It asks a question no fight or shop asks: **"How much do I risk for a better lock position?"** The wheel is already spun and fully visible, so the player knows what each slice gives. The first nudge is free; each extra nudge costs Heat or HP. The player weighs a mediocre slice now against paying for the JACKPOT, and against the TRIPWIRE. The Cache is also the cheapest nudge tutorial: no enemy, no clock, no RAM, only "turn the wheel to the slice you want".

## 2. Rules
**Wheel:** 6 slices of 5 ticks (the standard wheel; N12 not required). One fixed pointer at tick 0. There are no precision tiers: the slice containing the pointer's tick is the result (slice = round(tick/5) mod 6).

**Layout constraints (authored data):**
- Exactly one JACKPOT slice and exactly one TRIPWIRE slice per layout.
- The TRIPWIRE is never the JACKPOT slice's neighbor on both sides (it may be adjacent on one side). Layouts are validated by a lint test.

**Start position (the only randomness):** a start slice is chosen from the candidate set = slices at ring distance 2 or 3 from the JACKPOT, excluding the TRIPWIRE slice, sorted by slice index. One draw from the `events` stream picks an index into that set. The tutorial layout instead has a fixed `forced_start` field and draws nothing.

**Nudge:** moves the wheel one slice (±1) per nudge, wrapping. The first nudge is free (`cache_free_nudges` = 1). Each further nudge costs:
- **PAY_HEAT:** +2 Heat (FLAT, `cache_extra_nudge_heat`).
- **PAY_HP:** 5 % of max HP (PERCENT, rounded, minimum 1, `cache_extra_nudge_hp_pct` = 0.05).

`cache_max_nudges` = 3 total (1 free + 2 paid); then the wheel locks.

**Cost to reach the JACKPOT (pure function):** distance d on the 6-ring is 2 or 3 by construction. Nudges needed = d, paid = d − 1.

| Distance | Nudges | Paid | PAY_HEAT cost | PAY_HP cost (60 HP operative) |
|---|---|---|---|---|
| 2 | 2 | 1 | +2 Heat | 3 HP |
| 3 | 3 | 2 | +4 Heat | 6 HP |

The budget of 3 covers both cases exactly. Passing through the TRIPWIRE on the way is harmless: only the slice under the pointer at CRACK resolves.

**Commit:** CRACK resolves the slice under the pointer. LEAVE (before CRACK) gives nothing and costs nothing. Paid nudges can be undone before CRACK, so a LEAVE after undoing pays nothing.

**TRIPWIRE:** costs `cache_trip_hp_pct` of max HP (0.15 in PAY_HEAT caches, 0.10 in PAY_HP caches) plus `cache_trip_heat` = 3 Heat (FLAT). HP loss can never kill: HP floors at 1 (`cache_trip_cannot_kill` = true). The TRIPWIRE is visible in the layout, so it is never a surprise.

**Reward slice kinds:**
- CYCLES: FLAT, from the layer table.
- SCHEMATICS: FLAT, banked on completion like Rack Schematics.
- HEAL: PERCENT of max HP (R5; never tier-scaled, R2).
- CARD_OFFER: pick 1 of 3 (existing `_offer`).
- FIRMWARE_OFFER: pick 1 of 2 (layers 4+).
- HEAT_DOWN: FLAT −4, PAY_HEAT caches only.
- TRIPWIRE: above.

**Config keys (new, `campaign_config.tres`):** `cache_free_nudges` = 1, `cache_max_nudges` = 3, `cache_extra_nudge_heat` = 2, `cache_extra_nudge_hp_pct` = 0.05, `cache_trip_hp_pct_heat_variant` = 0.15, `cache_trip_hp_pct_hp_variant` = 0.10, `cache_trip_heat` = 3, `cache_run_chance` = 0.6, `cache_trip_cannot_kill` = true, and a `cache_rewards` table (amounts by layer band).

## 3. Placement & generation
- **Where:** NEW: `InfilNodeType.CACHE` (appended, never renumbered; D4 approved the node, pending the puzzle vet that this draft provides).
- **Count:** 0 or 1 per netrun. `cache_run_chance` = 0.6. Layers 2–6 only (never layer 1, never layer 7, never the Rack slot).
- **Terminal share:** the Cache takes one slot from the Terminal-eligible pool, so Terminals keep about 25 % of the remaining nodes counted after the Cache is placed. It never replaces a Mainframe or Elite guarantee.
- **Weights:** layers 2–3 favor CYCLES and CARD_OFFER; layers 5–6 add FIRMWARE_OFFER and larger amounts. The chance is flat across layers.
- **Corporation:** skin and reward leaning only (Solace leans HEAL, Meridian leans CYCLES). The cost variant is tied to the corporation (see Q:1).
- **Exclusions:** no Cache on Reclaim or Patrol netruns, none adjacent to another in the graph.

**RNG (deterministic):**
- Map generation draws "Cache present, layer, layout id" from the `map` stream.
- On entering the node, one `events` draw picks the start slice from the candidate set above. It sets a checkpoint and is saved, so quitting cannot reroll it.
- Nudge, undo and LEAVE draw nothing. The result (slice, cost) is a pure function of start, layout, nudges taken and max HP.
- On CRACK, offers draw from the existing `_offer` streams with a second checkpoint. The reward kind is fixed and previewed; only the specific offered cards are unseen until CRACK.

## 4. UX flow
1. The node card on the route reads "CACHE: crack a stash" with the cost-variant icon.
2. The Cache page opens: a six-slice wheel with each slice labeled by reward icon and amount (including the red TRIPWIRE and the JACKPOT mark). The line reads "Free nudges: 1. Extra nudge: +2 Heat" (or "−5 % HP").
3. **Preview before commit:** the slice under the pointer shows its outcome. Hovering any slice shows "Needs N nudges, cost X". A running line shows "Cost so far". The CRACK button names the result: "CRACK: +30 Cycles". A paid nudge that would cross a Heat threshold shows a warning chip first.
4. **Nudge controls:** ◀ ▶ buttons and keys; paid ones show their cost; 3 budget pips.
5. **UNDO:** returns step by step to the start slice and refunds costs. It stops after CRACK. The start is a checkpoint, so UNDO never rerolls it.
6. **CRACK:** charges costs, applies the slice, then opens the standard reward UI for offers.
7. **LEAVE:** available any time before CRACK; confirm line "Leave the stash? Nothing is paid."

**Text keys:** `cache.title`, `cache.hint_free`, `cache.hint_extra_heat`, `cache.hint_extra_hp`, `cache.crack`, `cache.leave`, `cache.slice.<kind>`, `cache.trip`, `cache.locked`, `cache.tutorial_nudge`, `cache.heat_warn`.

**Teaching nudging:** the first Cache a profile meets (NEW: profile flag `seen_cache`) uses the tutorial layout with `forced_start`: the JACKPOT-equivalent CARD_OFFER is exactly one slice away and no trap is adjacent. A callout reads "A nudge turns the wheel one slice. The first is free." The player learns slice reading, nudging and undo here; combat later adds RAM, ticks and precision. Later Caches use the normal rules.

## 5. Interactions
- **Heat:** PAY_HEAT raises Heat and can cross MINOR/MAJOR thresholds, warned before payment. HEAT_DOWN (−4) is small and sits in PAY_HEAT caches only, so it never replaces Heat objective Sites.
- **Raids:** none directly; Heat is the link.
- **Daemons/Firmware:** Clean Signal and Cold Exit are untouched. A hook `cache_free_nudge +1` is possible; Linked Bus does not apply. Combat nudge rules (Ghost, Rigger, Accelerator) are ignored here.
- **Other nodes:** competes with Terminals for a slot; a Mainframe on a later layer makes Cache Cycles more valuable.
- **Exploits:** never a Cache reward (they sit on Racks, GDD 4.2).
- **Tiers:** reward tables scale by layer; nudge cost, budget and trap are tier-independent (R2). HEAL is PERCENT.
- **Death:** TRIPWIRE HP loss floors at 1 HP.

## 6. Data & systems
- **N17 (event wheel):** the Cache is a consumer. A `CacheData` is an `EventWheelData` row with `step_nudge` = 1 slice, `cost_variant`, a 6-entry `layout` and `forced_start`. No separate wheel resource. N17 needs: no tiers, slice-step nudges, a cost variant, a visible layout. Size M.
- **`CacheSliceData`** (kind, amount, amount_mode FLAT/PERCENT, pool id) is the row type inside the layout.
- **N1:** the HEAL PERCENT slice. Fallback: FLAT heal.
- **N18:** offer rows may use `RewardTableData`; fallback is the existing `_offer`. `slice_flash` is not used here.
- **NEW: InfilNodeType.CACHE** (S) and a Cache slot rule in `map_graph` (S).
- **NEW: profile flag `seen_cache`** (S).
- **Save:** `cache_state` (start slice, nudges used, cracked) in the run state (S).
- **Fallback for the whole node:** a Terminal event with three choices (safe / mid / risky). It loses the wheel and the nudge lesson; not recommended.
- **Size:** M overall.

## 7. Examples
Reward table (layers 2–3; later layers ×1.5 Cycles and add Firmware):

| Kind | Amount |
|---|---|
| CYCLES | 30 (small slice: 10) |
| SCHEMATICS | 3 |
| HEAL | 20 % max HP |
| CARD_OFFER | pick 1 of 3 |
| FIRMWARE_OFFER | pick 1 of 2 (layers 4+) |
| HEAT_DOWN | −4 (PAY_HEAT only) |
| TRIPWIRE | 15 % HP + 3 Heat |

1. **Billing vault (Solace, layer 2, PAY_HEAT).** Clockwise, slice 0–5: CYCLES 10 · HEAL 20 % · TRIPWIRE · CARD_OFFER · SCHEMATICS 3 (JACKPOT) · CYCLES 30. Candidates at distance 2–3 from slice 4, excluding slice 2: slices 0 (d=2), 1 (d=3), 3? no (d=1). So {0, 1}. Say start = slice 0. Free nudge ◀ reaches slice 5 (CYCLES 30, 1 nudge). A second nudge (paid, +2 Heat) reaches slice 4: 3 Schematics for 2 Heat. Decision: 30 Cycles free, or 3 Schematics for 2 Heat.
2. **Parcel locker (Meridian, layer 5, PAY_HP, 60 HP).** Slices 0–5: CYCLES 45 · HEAL 20 % · TRIPWIRE · CYCLES 45 · FIRMWARE pick 1 of 2 (JACKPOT) · CYCLES 10. Candidates from slice 4 at distance 2–3: slice 0 (d=2), 1 (d=3), 2 excluded (trap), so {0, 1}. Start = slice 1 (HEAL 20 %). Free: crack for HEAL. Jackpot is d=3: 3 nudges, 2 paid = 6 HP, while the HEAL gives 12 HP. Passing the TRIPWIRE at slice 2 is harmless.
3. **Tutorial strongbox (first Cache ever).** `forced_start` = slice 0 (CYCLES 10); CARD_OFFER on slice 1; no trap adjacent. One free nudge, CRACK, a card, zero cost.

## 8. Risks & balance notes
- **Free gift:** the start is always at distance ≥ 2 from the JACKPOT, so it always costs ≥ 1 paid nudge. Sim: reward value by nudges bought.
- **HP attrition:** the trap is 10 % in PAY_HP caches and HP floors at 1. Cap of one Cache per run. Sim: net HP across a run with a Cache.
- **LEAVE dominance:** the free nudge lets the player dodge a nearby TRIPWIRE, and at most 2 slices are bad. Test whether the average CRACK beats LEAVE at ≥ 90 % of starts.
- **Heat farming:** HEAT_DOWN −4 vs a paid nudge +2 means at most net −2 only by spending two nudges on it; watch Heat per run.
- **Value of a paid nudge:** target about 1.0–1.5 × its cost in the sim.
- **Too similar to combat:** mitigated by slice-only reads and no RAM; playtest for currency confusion.
- **Replay value:** 6–8 authored layouts per corporation.
- **Sim metrics:** Cache presence, nudges bought, TRIPWIRE rate, Heat added, HP lost, reward value.

## 9. Q:
Q: Should the PAY_HEAT / PAY_HP variant be fixed by corporation (Solace = HP, Meridian = Heat), or rolled per Cache from the `map` stream?
Q: Should LEAVE ever carry a cost (e.g. +1 Heat) to stop skipping Caches, or is a free LEAVE the right way to make every crack a real choice?
Q: Is a percent-HP trap acceptable given the 1-HP floor, or should the trap cost only Heat?
Q: Do Caches appear in HQ netruns, where G12 wants each run unique?
Q: Should the free nudge be one per Cache or one per run (a resource puzzle across several Caches)?
