<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01LxQs8RvJGj9WzDuV2avpgt, custom_id node__cache; status ok; tokens in 14045 cache-write 0 cache-read 32007 out 5805; cost $0.046. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# CACHE: design draft

**Verdict on EV4 "Dial the vault" as proposed:** the idea is good, but the proposal is too close to combat as written. A 6-slice wheel with N nudges is the combat verb restated, so players would simply see "another wheel". I keep the wheel but change what the player reads, what a nudge costs, and what is at stake. The revised spec is below.

Vetting findings:
- **Good:** it teaches nudging in a no-damage context and gives a quiet choice between a safe and a risky outcome.
- **Readable:** only if the player sees every outcome up front. A fixed, fully revealed layout with a deterministic result is readable.
- **Too similar to combat:** yes, if it reuses pointer, precision tiers and RAM. So the Cache drops tiers (no PERFECT/GOOD/WEAK) and uses a **slice-only landing**. It also drops RAM, and its cost currency is Heat or HP, which combat doesn't use for nudges.
- **Cost model problem:** "extra nudges cost HP/Heat" is two currencies on one action. I choose one per Cache (Heat or HP), shown before commit.

## 1. Purpose & the decision it creates
A Cache is a stash node on the netrun map (a locked lockbox in a server closet). It asks a question no fight or shop asks: **"How much do I risk for a better lock position?"** The wheel is already spun and fully visible, so the player knows exactly what each slice gives. The first nudge is free; each extra nudge costs Heat or HP. The player decides whether to take a mediocre reward now or pay for the jackpot slice. It doubles as the cheapest tutorial for nudging: no enemy, no clock, no RAM, only "turn the wheel to the slice you want".

## 2. Rules
**Wheel:** 6 slices of 5 ticks (the standard wheel, N12 not required). One fixed pointer at tick 0. The Cache wheel uses **no precision tiers**: whichever slice the pointer's tick falls in is the result (slice = round(tick/5) mod 6). Reading is by slice only, so the player never judges sub-ticks.

**Start position:** the wheel starts at a rotation drawn once from the `events` stream (see §3). That draw is the only randomness. The layout is data and fixed per Cache type.

**Nudge:** ±1 slice (5 ticks) per nudge, not ±1 tick. This is a Cache-specific rule (`cache_nudge_ticks` = 5), so the player turns one clear step at a time and never needs tick precision. The first nudge is free (`cache_free_nudges` = 1). Each further nudge costs `cache_extra_nudge_cost`:
- **PAY_HEAT** variant: +2 Heat per extra nudge (campaign meter, FLAT).
- **PAY_HP** variant: 5 % of the operative's max HP per extra nudge (PERCENT, rounded, minimum 1).

Each Cache authors one variant. Never both.

**Budget:** `cache_max_nudges` = 3 total (1 free + 2 paid), tier-independent. After the budget is spent, the wheel locks.

**Commit:** the player presses CRACK, and the slice under the pointer resolves. They may also **walk away** (LEAVE): no reward and no cost beyond nudges already paid. Paid nudges can be undone before CRACK (see §4), so walking away costs nothing.

**Failure:** one slice of the six is a **TRIPWIRE**. Landing on it triggers `cache_trip_cost`:
- PERCENT 15 % max HP damage, and
- +3 Heat (FLAT).

The reward wheel is fully visible, including the TRIPWIRE. Failure is therefore a risk the player chose, never a surprise. There is no hidden trap (this keeps preview = result).

**Reward slice types (amount modes noted):**
- CYCLES: FLAT, scaled by the layer table.
- SCHEMATICS: FLAT, banked on completion like Rack Schematics.
- HEAL: PERCENT of max HP (never scaled by tier, per R2).
- CARD_OFFER: pick 1 of 3 (via the existing `_offer`).
- FIRMWARE_OFFER: pick 1 of 2.
- HEAT_DOWN: FLAT −Heat (small).
- TRIPWIRE: above.
- EMPTY: nothing.

**Config keys (new, in `campaign_config.tres`):** `cache_free_nudges`, `cache_max_nudges`, `cache_nudge_ticks`, `cache_extra_nudge_heat`, `cache_extra_nudge_hp_pct`, `cache_trip_hp_pct`, `cache_trip_heat`.

**Wheel layout rule:** the best slice (JACKPOT) is never adjacent to the start position. The generator picks a start rotation that puts the pointer on a mid or low slice. The jackpot is therefore always at least 1 nudge away: free nudge = reachable for one slice distance only, so a jackpot 2 slices away costs 1 paid nudge.

## 3. Placement & generation
- **Where:** a new `InfilNodeType` value, CACHE (NEW: node type; appended to the enum, never renumbered).
- **Count per netrun:** 0 to 1. Chance: layers 2–6 only. Base chance per run is `cache_run_chance` = 0.6, so typically one Cache every other run. It is never in layer 1 or 7, and never on the Rack layer slot.
- **Placement:** replaces one Terminal-eligible slot, sharing the Terminal share (~25 % of remaining nodes). It never replaces a Mainframe guarantee or an Elite guarantee.
- **Weights by tier/layer:** the layer table raises the reward values; the chance is flat. Layers 2–3: reward Cycles / card offers dominate. Layers 5–6: Firmware offers and jackpots appear. The Cache layout is drawn from a small authored set (see §7).
- **Corporation:** each corporation skins the Cache (Solace: billing vault; Meridian: parcel locker; Halcyon: city strongbox; Orbital: telemetry cache; REBEL_CELL: dead drop). The mechanics are identical; only the reward weighting differs slightly (Solace leans heal, Meridian leans Cycles).
- **Exclusions:** no Cache on Reclaim or Patrol netruns; never two Caches adjacent in the graph; none on a boss-only path.

**RNG handling (deterministic):**
- Map generation draws "is there a Cache, which layer, which layout id" from the existing `map` stream.
- On entering the node, one draw from the `events` stream picks the **starting rotation** (one of 6 slice positions, constrained by the layout rule above). This draw sets a **checkpoint** and is saved. Quitting and reloading cannot reroll it.
- Nudging, undoing and cracking draw nothing. The full outcome (slice, cost) is a pure function of start rotation, layout, nudges taken and operative HP.
- Reward contents resolve on CRACK. Card and Firmware offers draw from the same streams the existing rewards use (`_offer`), after the click, with a second checkpoint. The reward **kind** is fixed by the slice and previewed; only the specific offered cards are not shown before CRACK. That is the same as any other reward offer.

## 4. UX flow
1. Player selects the CACHE node on the route. The node card says "CACHE: crack a stash" with the cost variant icon (Heat or HP).
2. **Cache page** opens: a six-slice wheel, each slice labelled with its reward icon and amount (including the red TRIPWIRE). The pointer sits at the top. A line reads "Free turns: 1. Extra turn: +2 Heat" (or "−5 % HP").
3. **Preview before commit:** the slice currently under the pointer is highlighted with its outcome text. Hovering any slice shows "Needs N turns, cost X". A running total shows "Cost so far: +2 Heat". The CRACK button text names the slice: "CRACK: +40 Cycles".
4. **Nudge controls:** two arrow buttons (◀ ▶) and keys. The first is free; later ones show the cost on the button. A budget pip row shows 3 pips.
5. **UNDO:** every nudge can be undone back to the start rotation, restoring the cost. Undo stops once CRACK is pressed. The starting rotation is a checkpoint, so UNDO never rerolls it.
6. **CRACK:** applies the slice, charges costs, then shows the reward list or offer. Card and Firmware offers use the standard reward UI.
7. **LEAVE:** from any state before CRACK, with no penalty and a confirm line "Leave the stash? Nothing is paid."

**Text keys:** `cache.title`, `cache.hint_free`, `cache.hint_extra_heat`, `cache.hint_extra_hp`, `cache.crack`, `cache.leave`, `cache.slice.<type>`, `cache.trip`, `cache.locked`, `cache.tutorial_nudge`.

**Teaching nudging:** the first Cache a profile ever meets (a profile flag `seen_cache`) uses a **tutorial layout**: the start rotation is forced (not drawn, so the RNG stream is untouched) and the jackpot is exactly one slice away. A callout reads "Nudge turns the wheel one slice. The first is free." The player nudges once for free and wins. The second Cache onward is normal. Nudge costs, "reading the slice under the pointer", and the undo are all taught here, so combat nudging (RAM, ticks, precision) then adds only the tick-level detail.

## 5. Interactions
- **Heat:** PAY_HEAT variants raise Heat directly, feeding MINOR/MAJOR thresholds. A paid nudge that crosses a threshold shows a warning chip ("crosses Heat 25: raid") before it is paid. HEAT_DOWN slices are small (−2) so they never replace Heat objective Sites.
- **Raids:** none directly. Heat raised by Caches is the link.
- **Daemons/Firmware:** Clean Signal and Cold Exit are untouched. A new Daemon hook is possible (`cache_free_nudge +1`). Linked Bus does not apply (no enemy wheel).
- **Other nodes:** it competes with Terminals for the map slot. A Mainframe on the same layer makes Cycles from a Cache more valuable.
- **Exploits:** no Exploit is ever a Cache reward (they sit on Racks, per GDD 4.2). A story-beat Cache variant could be authored later.
- **Tiers:** the reward tables scale (see below); the nudge budget and costs don't (R2: buffs and costs are tier-independent). HEAL is PERCENT, so it never rescales.
- **Operatives:** the Ghost's first-nudge-ignores-resistance, Rigger's free nudge and Accelerator are combat rules and are ignored here. A Rigger bonus (+1 free Cache nudge via a Hub passive) is a cheap optional hook.
- **Death:** a TRIPWIRE can never kill. Damage is capped to leave 1 HP (`cache_trip_cannot_kill` = true).

## 6. Data & systems
**New resources:**
- `CacheData`: id, layout (6 `CacheSliceData`), cost_variant (PAY_HEAT / PAY_HP), min_layer, max_layer, corp weights.
- `CacheSliceData`: kind, amount, amount_mode (FLAT / PERCENT per R5), pool id for offers.
- `InfilNodeType.CACHE` (appended).

**Systems:**
- **N17 (event wheel):** reuse as the wheel page and `events` checkpoint. The Cache is the first consumer. This draft fixes N17's spec as **no tiers, slice-step nudges, a cost variant, a visible layout**. Size M.
- **N18 (rewards list):** the offer rows can reuse `RewardTableData`. A data-only fallback uses the existing `_offer`.
- **N14/N1:** amount modes. The HEAL PERCENT slice needs N1 (S). Without N1, use FLAT heal as a fallback.
- **Map gen:** a Cache slot rule in `map_graph` (S).
- **Save:** one extra `cache_state` (rotation, nudges used, cracked) in the run state (S).

**Data-only fallback for the whole node:** an existing Terminal event with three choices (safe / mid / risky) gives a reduced version. It loses the wheel and the nudging lesson. Not recommended.

**Size:** M overall (the page plus data), given N17.

## 7. Examples
Reward table (layers 2–3, base; amounts are placeholders; later layers scale Cycles ×1.5 and add Firmware):

| Slice kind | Amount |
|---|---|
| CYCLES | 30 |
| SCHEMATICS | 3 |
| HEAL | 20 % max HP |
| CARD_OFFER | pick 1 of 3 |
| FIRMWARE_OFFER | pick 1 of 2 (layers 4+) |
| HEAT_DOWN | −2 |
| TRIPWIRE | 15 % HP + 3 Heat |
| EMPTY | nothing |

1. **Billing vault (Solace, layer 2, PAY_HEAT).** Layout clockwise: CYCLES 30 · HEAL 20 % · TRIPWIRE · CARD_OFFER · EMPTY · SCHEMATICS 3. Start: pointer on EMPTY. Free nudge to CARD_OFFER: crack for a card at 0 cost. Or pay +2 Heat to take two steps further to SCHEMATICS. Decision: a card now, or 3 Schematics for 2 Heat.
2. **Parcel locker (Meridian, layer 5, PAY_HP).** CYCLES 45 · FIRMWARE pick 1 of 2 · TRIPWIRE · HEAL 20 % · CYCLES 45 · HEAT_DOWN −2. Start: pointer on TRIPWIRE. Free nudge lands on FIRMWARE or CYCLES (either side). The Firmware is adjacent, so it is free. Safe but boring: the player may spend 5 % HP to move twice for HEAL if hurt. The lesson is "the free nudge escapes the trap".
3. **Tutorial strongbox (first Cache ever).** Start forced on EMPTY with CARD_OFFER one slice away. One free nudge, crack, card. No Heat, no trap on the adjacent slices.

## 8. Risks & balance notes
- **Dominant strategy:** a layout where the best slice is always reachable for free would make the Cache a free gift. The generator rule (jackpot never adjacent, free nudge reaches one slice) guarantees at least one paid nudge for a jackpot. Sim: win rate and reward value by nudges bought.
- **Heat farming:** PAY_HEAT players could skip Caches entirely to avoid Heat, which is fine. The risk is the opposite, with Caches becoming the safe Cycles faucet. Cap one per run and watch Cycles per run.
- **HP variant in early layers:** a low-HP operative can't afford it. The 1-HP floor on the TRIPWIRE and "LEAVE is free" prevent a soft-lock or death trap.
- **Information is perfect:** the only variance is the start rotation and the offered card names. This keeps preview = result. The sim tests the expected-value gap between the best and the median slice: the target is that a paid nudge is worth about 1.0–1.5 × its cost.
- **Too similar to combat:** mitigated by slice-only reads, no RAM and no enemy. Test that players don't confuse nudge cost currencies (playtest question).
- **Replay value:** a small authored layout set can get stale. Aim for 6–8 layouts per corporation at launch.
- **Sim metrics:** Cache presence per run, mean nudges bought, TRIPWIRE rate, Heat added, HP lost, reward value per Cache.

## 9. Q:
Q: Should the PAY_HEAT / PAY_HP variant be tied to the corporation (Solace = HP, Meridian = Heat), or rolled per Cache from the `map` stream?
Q: Is a PERCENT-HP trap acceptable given "a TRIPWIRE can't kill", or should the trap cost only Heat to avoid HP attrition?
Q: Do Caches ever appear in HQ netruns, where G12 wants each run unique, or are they street-only?
Q: Should the free nudge be one per Cache (as drafted) or one per run, which would turn the Cache into a resource-allocation puzzle across several Caches?
Q: Should a Cache reward slice ever be an Exploit-adjacent item (an access key hint, per D5), or does that blur the Rack's role?
