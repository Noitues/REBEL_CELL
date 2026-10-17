<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01LxQs8RvJGj9WzDuV2avpgt, custom_id node__black_market; status ok; tokens in 14005 cache-write 0 cache-read 32007 out 4776; cost $0.041. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Black Market (unknown event node): design draft

## 1. Purpose & the decision it creates
The Black Market is a Terminal-slot node that looks like any other "?" event until entered. It does not trade Cycles for power the way the Mainframe does. It trades **things the player normally protects**: Heat, HP, a Firmware socket, a spare Daemon, a card. The question is "what am I willing to be poorer in to get stronger now?", not "what can I afford?". Every offer has a visible price in a non-Cycle currency and a visible downside. Nothing is hidden after the reveal, so the risk is a decision, not a gamble. Trade-in gives a way out for players with nothing to sell.

**Distinct from the Shop:** it has no Cycle prices (except one fence row), a smaller stock (3 items plus the fence), and every item has a rider. **Distinct from events:** it is a stable menu with previews, not a story choice, and it has no random outcomes except an optional wheel the player starts deliberately.

## 2. Rules
**Stock:** 4 rows per visit: 3 goods and 1 "Fence" (trade-in) row. Each good has a `price_kind`, an `amount_mode` and an optional `curse`.

**Price kinds** (config `black_market.price_kinds`):
| Kind | Rule |
|---|---|
| HEAT | Campaign Heat +N when you leave. FLAT 3–8, tier-independent. Applied via the existing MODIFY_HEAT. Crossing a threshold fires its one-time event as normal. |
| HP | Operative loses HP now. PERCENT of max HP (10–25 %). Can't take you below 1 HP. The row is greyed if it would. |
| CYCLES | Only the fence-adjacent "cheap" row: 1.5× the Mainframe price for the same kind of item, no rider. |
| TRADE | Give up a named owned thing: a card (remove from deck), a Firmware (unsocket), or a Daemon. The player picks which. Nothing is refunded. |
| CURSE | The item is free or cheap but attaches a curse (below). |

**Curses** (data: `CurseData`, riders attached to the item and visible):
- *Hot*: the item adds +1 Heat per combat while carried (max 3 combats).
- *Brittle*: a Firmware that is ENCRYPTED-immune and loses its effect after 3 combats.
- *Leaky*: a Daemon that costs −1 max RAM.
- *Marked*: the next elite on this run gets +1 resistance.

**Purchase limits:** 1 HEAT-priced good and 1 HP-priced good max per visit, so the player cannot buy the whole stock with one currency. Total Heat taken per visit is capped at `bm_heat_cap` = 10. The Heat price is rounded **down** to the nearest MINOR threshold and previewed: "Heat 18 → 23, no threshold crossed."

**Fence (trade-in):** sell one owned card, Firmware or Daemon. The payout is Schematics banked now (FLAT: card 2, Firmware 4, Daemon 6) or a **Heat wipe** (−2 Heat per item, max −4 per visit). Banking Schematics is tier-independent. The Fence is the only way to convert surplus into Heat relief on a netrun.

**Wheel option ("Roll for the crate"):** a 3-slice event wheel (N17) on a sealed crate: Jackpot (a RARE good, free), Standard (a common good, free), Bust (a curse item forced on you). Starting the wheel costs 1 Heat. The player gets one nudge from a budget of 1; extra nudges cost 5 % max HP each. Without N17 the option is simply absent (see §6). The result is previewed on the wheel in the standard way (the pointer shows the slice before commit); the only randomness is the initial spin, which uses the `events` RNG at a checkpoint, so undo cannot reroll.

**Limits:** one purchase from each price kind except TRADE (up to 2). Leaving costs nothing. No refunds after leaving the page.

## 3. Placement & generation
- **Node:** appears as a Terminal slot with an UNKNOWN icon. Config `black_market.chance_per_terminal` = 0.12 on layers 3–6. Cap 1 per netrun; never on layer 1–2, never on the layer before the final Rack, never adjacent to a Mainframe.
- **Weights by tier:** T1 0 (teaching), T2 0.08, T3 0.12, T4 0.15. Weights by Heat band: ×0.5 under COOL, ×1.5 at FLAGGED+ (the cell is desperate).
- **By corporation:** Solace and Meridian use base weight; Halcyon ×0.5 (a police state, fewer black markets); Orbital ×1.0; REBEL_CELL 0 (it is your own network).
- **Guarantee:** if a run reaches layer 5 with 0 Black Markets and 0 events seen of type "trade", no forced insertion (do not guarantee; scarcity is the point).
- **Stock roll:** `rng.stream("black_market")`, a new named stream seeded from the map seed and the node id. Stock is fixed at map generation, so entering, leaving and rewinding always show the same stock.
- **Exclusion:** the unknown node does not appear in the Terminal pool when the Heat is ≥ 90 (the Purge is imminent).

## 4. UX flow
1. **Map:** an UNKNOWN glyph (the same as unresolved events). A hover shows "Unknown signal". Entering is a commitment; there is no peek.
2. **Reveal:** a CRT flicker, a stall-style sticker, "OFF-GRID VENDOR" in the Corpo voice with a street-slang line. 1.2 s, skippable.
3. **Menu:** 3 goods and the Fence as cards. Each shows: item, price icon with number, curse badge, and a **result chip** (resulting Heat, HP, deck size).
4. **Select a good:** a detail panel with the full text, the tooltip breakdown, and a CONFIRM / CANCEL. For TRADE the panel opens a picker listing the player's items with a "−N value" tag.
5. **Confirm:** the action is applied atomically. The row greys. The page stays open for the next purchase.
6. **Undo:** before leaving, a single UNDO of the last purchase restores everything (state snapshot per purchase, no RNG consumed). The wheel option sets a checkpoint, so undo is blocked after the spin (shown on UNDO itself, as in combat).
7. **Leave:** a confirm if any HEAT price was paid ("Heat +6 takes effect: 41 → 47").

**Text keys:** `bm.title`, `bm.reveal`, `bm.price.heat|hp|trade|curse|cycles`, `bm.curse.hot|brittle|leaky|marked`, `bm.fence`, `bm.wheel.*`, `bm.leave_confirm`, `bm.refused.*` (hp_floor, heat_cap, limit).

## 5. Interactions
- **Heat:** the central interaction. HEAT prices push toward the raid thresholds; the preview warns about crossings ("crosses 25: RAID"). The Fence is a Heat sink (−2 per item). Scrubber, Proxy Relay and Cold Exit interact normally.
- **Raids:** Heat paid here can trigger a raid mid-run; that is the risk. A raid in the middle of the run uses the existing interlude.
- **Daemons / Firmware:** Clean Signal and Cold Exit are not affected. A Daemon can sell for 6 at the Fence, so players with rule-breaking Daemons choose. Stolen Intent-class Daemons are flagged "cannot be traded" (`tradeable = false`).
- **Other nodes:** Mainframe sells for Cycles, the Market sells for risk. A Terminal event never offers the same item as the Market on the same run (a shared exclusion list).
- **Exploits:** the final Rack Exploit is never sold. No Exploit, key or story beat is for sale.
- **Tiers:** goods scale in rarity (T2 common/uncommon, T3–T4 up to RARE). Price numbers are tier-independent (R2: percent amounts read the owner's max HP; Heat is flat).
- **Death:** HP prices cannot kill. Death still applies if a curse is carried into combat.

## 6. Data & systems
**New data:**
- `BlackMarketItemData`: `id`, `reward_ref` (card / Firmware / Daemon), `price_kind`, `price_amount`, `amount_mode` (FLAT/PERCENT), `trade_slot_kind`, `curse_ref`, `rarity`, `min_tier`, `corp_filter`.
- `CurseData`: `id`, `kind`, `params`, `duration_combats`, `display_key`.
- `BlackMarketConfig` in `campaign_config.tres`: the chances, caps, fence values, `bm_heat_cap`, `bm_hp_floor`.
- `EventWheelData` (N17) for the crate.

**Systems:**
| System | Need | Size | Fallback |
|---|---|---|---|
| N1 amount modes | PERCENT HP price | S | FLAT HP numbers |
| N18 reward lists | The stock pool as a reward-table row with price conditions | M | Hard-coded pool in `black_market_pool.tres` |
| N16 | A Marked curse alters the next elite (`next_combat_overrides`) | M | Drop Marked |
| N17 | The crate wheel | M | Drop the wheel; 3 goods only |
| NEW: curses | Run-level carried riders with a duration | S–M | Only Hot (a MODIFY_HEAT trigger on combat end, existing) |
| NEW: node kind | An UNKNOWN Terminal subtype and a page | M | An event with `choices` using existing event effects |

**Data-only fallback:** a regular Terminal event with 3 choices using MODIFY_HEAT, HP loss and GAIN_* effects. It loses trade-in pickers and previews, so it is a prototype only.
**Total:** M–L; M with the fallbacks.

## 7. Examples
**A. T2, COOL Heat (Solace), the "desperate cell" inventory**
1. Patch+ Firmware, price HEAT +4 (Heat 12 → 16). No curse.
2. Uncommon card "Overclock Burst", price HP 15 % max (9 of 60).
3. Stolen Daemon "Leaky Signal" (Kernel Sync variant), CURSE: free, −1 max RAM.
4. Fence: card 2 Schematics, or −2 Heat per item.

**B. T3, FLAGGED Heat 55 (Meridian), the "Heat is already high" inventory**
1. Rare Firmware Mirror, price TRADE: one Daemon.
2. Elite-loot card, price HEAT +8 (55 → 63; no threshold crossed, but 75 is 12 away).
3. HEALTH pack (heal 40 % max HP, PERCENT), price CYCLES at 1.5× Mainframe (≈ 90).
4. Fence: Firmware 4 Schematics or −2 Heat; a good place to bleed Heat before 75.
Crate wheel: Jackpot RARE / Standard / Bust; cost 1 Heat.

**C. T4, HUNTED Heat 80 (Orbital), the "no good options" inventory**
1. Rare Daemon "Zero Day", CURSE Hot (+1 Heat per combat for 3 combats). Free.
2. Rare card, price HP 25 % max (15 of 60).
3. Brittle Firmware Burner variant, TRADE: any card.
4. Fence: Daemon 6 Schematics or −2 Heat.
No wheel (Heat ≥ 75 disables it: the market is under watch).

## 8. Risks & balance notes
- **Heat-banking exploit:** buy with Heat, then bleed it back at the Fence by selling junk. The net is bounded: the Fence heals at most −4 per visit while prices can add 10; the cap is `bm_heat_cap`. Sim: Heat at campaign end with and without Market visits.
- **HP laundering:** HP price then rest at HQ for free. Mitigate: the HP floor, and HP loss matters mid-run because HP carries between fights. Sim: the death rate after HP purchases.
- **Dominant good:** a free curse item that nets positive because the curse is weak. Test every curse for a negative net at T3 (win rate with and without).
- **Trade-in degenerate loop:** buy a card for Heat, then sell it for Schematics. Block it: bought items have `fence_value = 0` this visit.
- **Information:** the player knows a "?" can be the Market; at 12 % chance the unknown node still reads as ordinary. Don't let the Market become the best "?" (compare Market vs event value per node).
- **Sim:** a policy that buys the cheapest in-currency item vs a policy that never visits; measure win rate, Heat at the boss, and raid count. Target: the Market is positive for skilled players, neutral for the average.
- **Preview integrity:** all prices are deterministic, so the preview equals the result; only the crate wheel uses randomness, at a checkpoint.

## 9. Open questions
Q: Should the Market be recognisable after the first visit (a profile unlock "Fixer contact" that reveals it on the map), or stay unknown forever?
Q: Are curses permanent for the run, or do they expire after N combats as drafted (3)?
Q: Can the Fence accept Server Rack Schematics assets or the Armory pieces, or only deck, Firmware and Daemons?
Q: Does paying Heat here count as "Heat gained from an objective" for retaliation (4.4), or is it exempt?
Q: Should the Market appear in HQ runs (G12), or only street netruns?
