<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__nodes__black_market; status ok; tokens in 7877 cache-write 0 cache-read 32585 out 5642; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **1 (BLOCKER, new node kind)** -> The Black Market is now an unknown event outcome of the existing Terminal slot. It shows the normal event glyph and has no separate node kind. The "NEW: node kind" row is deleted. The event page is a stock-menu event, so the former fallback is now the primary implementation (an event with a stock list, a price preview, per-purchase undo and a picker). This is a new event-page layout, not a new node. It aligns with the D4 ruling ("maybe as an unknown event") and with the removal of Site names.
- **2 (BLOCKER, rounding rule)** -> The rounding rule is deleted. A Heat price is FLAT 3–8, previewed as "Heat 18 → 23; crosses 25? no". A crossing is shown in red and still allowed. Examples recomputed against this rule.
- **3 (MAJOR, arithmetic and invented ids)** -> Invented ids are replaced by existing content: Daemon Kernel Sync with a Leaky curse, Firmware Burner with a Brittle curse. The HEAL pack price cites its base: `mainframe_heal_price` = 60 × 1.5 = 90. The HP floor is shown in the examples (a 45 HP Botnet at 25 % loses 11, and the row greys when HP − price < 1).
- **4 (MAJOR, Hot vs cap)** -> Hot's total Heat (+1 × remaining combats, max 3) counts against `bm_heat_cap` at purchase and is added to the result chip. Hot is paid up front at purchase (answers the critic's Q): it is previewed as +3 Heat now and carries no later accrual.
- **5 (MAJOR, Brittle)** -> Brittle is now just "a Firmware that loses its effect after 3 combats" (`duration_combats` = 3). The ENCRYPTED text is removed.
- **6 (MAJOR, Fence)** -> The "only way" claim is deleted. The Fence pays a Schematics credit that banks only on Rack capture or run completion, per GDD 4.2, and is lost on death like other unbanked loot. The values are framed at the 10:1 Cycles equivalent (card 20, Firmware 40, Daemon 60 Cycles-equivalent, which is 2/4/6 Schematics). The Heat wipe is −2 Heat per item. The credit is a stated new economy path: it is counted in the sim, and the payout is capped at 6 Schematics per visit.
- **7 (MAJOR, Heat ≥ 90 vs desperation)** -> One statement: Heat ≥ 90 removes the market, HUNTED (75–89) keeps it with no crate wheel, and the ×1.5 weight applies at FLAGGED (50–74) only.
- **8 (MAJOR, wheel)** -> The extra nudge costs 4 % max HP, with one free nudge. The crate's initial spin uses the `events` stream at a checkpoint. The stock list is fixed at generation, and the crate's contents are drawn when the wheel is started, so the two statements no longer overlap.
- **9 (NIT, RNG stream)** -> The stock roll uses the `events` stream. The `black_market` stream is removed.
- **10 (NIT, corporations)** -> Weights added for Aurelian (×1.0) and Tethys (×1.0, the deep-sea fence fiction suits it).
- **Triage rows** -> Row 1 is handled by the changes under issue 1. Row 2 is handled by the changes under issue 2 (the unimplementable rounding rule is gone, and every Heat figure in the examples is plain addition).
- **Critic Qs** -> The signature price kind is Heat: the Market is the only place to sell the cell's safety. HP, TRADE and CURSE are secondary.
- **Kept, because strong:** non-Cycle prices with a visible downside, the preview with per-purchase undo and the crossing warning, and the exploit list with sim targets.

# Black Market (unknown event outcome): design draft

## 1. Purpose & the decision it creates
The Black Market is an unknown event that occupies a Terminal slot. It shows the normal event glyph and is revealed on entry. It does not trade Cycles for power the way the Mainframe does. It trades things the player normally protects: Heat (the signature price), HP, a Firmware socket, a spare Daemon, a card. The question is "what am I willing to be poorer in to get stronger now?", not "what can I afford?". Every offer shows a visible price and a visible downside, so the risk is a decision, not a gamble. A Fence row gives players with surplus a way to sell it.

**Distinct from the Mainframe:** no Cycle prices except one marked-up row, 3 goods plus the Fence, and every good has a rider. **Distinct from ordinary events:** a stable menu with previews, with randomness only in an optional crate the player starts deliberately.

## 2. Rules
**Stock:** 4 rows per visit: 3 goods and 1 Fence row. Each good has a `price_kind`, an `amount_mode` and an optional `curse_ref`.

**Price kinds** (config `black_market.price_kinds`):
| Kind | Rule |
|---|---|
| HEAT | FLAT 3–8, tier-independent, via MODIFY_HEAT, applied when you leave. The preview reads "Heat 18 → 23; crosses 25? no". A crossing is shown in red, names the event ("crosses 25: RAID"), and is still allowed. |
| HP | PERCENT of max HP, 10–25 %. Cannot take you below 1 HP; the row greys if HP − price < 1. |
| CYCLES | One row at 1.5× the Mainframe price for the same item kind, no rider. Base e.g. `mainframe_heal_price` = 60, so 90. |
| TRADE | Give up a named owned card (removed from the deck), Firmware (unsocketed) or Daemon. The player picks which. Nothing refunded. |
| CURSE | Free or cheap; attaches a visible curse. |

**Curses** (`CurseData`, shown on the row):
- *Hot*: +1 Heat per combat for 3 combats, **paid up front as +3 Heat at purchase**. It counts against `bm_heat_cap` and shows in the result chip.
- *Brittle*: a Firmware that loses its effect after 3 combats (`duration_combats` = 3).
- *Leaky*: a Daemon that costs −1 max RAM.
- *Marked*: the next elite on this run gets +1 resistance (N16 `next_combat_overrides`).

**Purchase limits:** at most 1 HEAT-priced and 1 HP-priced good per visit. Total Heat taken per visit (HEAT prices plus Hot) is capped at `bm_heat_cap` = 10; a row that would exceed it greys with `bm.refused.heat_cap`. One purchase per price kind except TRADE (up to 2).

**Fence (sell):** sell one owned card, Firmware or Daemon (up to 2 per visit). Payout per item is either:
- a **Schematics credit** (FLAT: card 2, Firmware 4, Daemon 6; max 6 per visit) that banks only on Rack capture or run completion (GDD 4.2) and is lost on death; or
- **−2 Heat** per item (max −4 per visit).

Items bought this visit have `fence_value` = 0. Stolen Intent-class Daemons carry `tradeable = false`. The Fence is one Heat-relief source among others (Scrubber, Proxy Relay, Heat-objective Sites).

**Crate wheel ("Roll for the crate"):** a 3-slice event wheel (N17): Jackpot (a RARE good, free), Standard (a common good, free), Bust (a Brittle or Leaky item forced on you). Starting costs 1 Heat. The initial spin uses the `events` stream at a checkpoint. The wheel has 1 free nudge; each extra nudge costs 4 % max HP. The preview shows the slice under the pointer before commit; undo is blocked after the spin (shown on UNDO itself). The contents of each slice are drawn when the wheel starts. The wheel is absent at Heat ≥ 75 and without N17.

**Limits:** leaving costs nothing. No refunds after leaving the page.

## 3. Placement & generation
- **Slot:** an unknown event outcome in a Terminal slot, with the normal event glyph. Config `black_market.chance_per_terminal` by tier: T1 0, T2 0.08, T3 0.12, T4 0.15, on layers 3–6. Cap 1 per netrun. Never on layers 1–2, never on the layer before the final Rack, never adjacent to a Mainframe.
- **Heat:** ×0.5 weight at COOL (0–24), ×1.5 at FLAGGED (50–74). **Heat ≥ 90 removes the market; HUNTED (75–89) keeps it, with no crate wheel.**
- **By corporation:** Solace, Meridian, Orbital, Aurelian, Tethys ×1.0; Halcyon ×0.5 (police state); REBEL_CELL 0 (your own network).
- **No guarantee:** scarcity is the point.
- **RNG:** the `events` stream (N16/N17). The stock is fixed at map generation (same node id, same stock), so enter, leave and rewind always show identical goods. Only the crate draw happens later, at a checkpoint.
- **Dedup:** a shared exclusion list stops an event on the same run offering the same item.

## 4. UX flow
1. **Map:** the normal event glyph, hover "Unknown signal". Entering commits; no peek.
2. **Reveal:** a CRT flicker and a stall sticker, "OFF-GRID VENDOR", 1.2 s, skippable.
3. **Menu:** 3 goods and the Fence as cards, each with item, price icon and number, a curse badge, and a **result chip** (resulting Heat with crossing flag, HP, deck size).
4. **Select a good:** a detail panel with full text, breakdown tooltip, and CONFIRM / CANCEL. TRADE opens a picker listing the player's items.
5. **Confirm:** applied atomically. The row greys; the page stays open.
6. **Undo:** a single UNDO of the last purchase restores everything (snapshot per purchase, no RNG consumed). The crate spin sets a checkpoint and blocks undo past it.
7. **Leave:** a confirm if any Heat is paid: "Heat +6 takes effect: 41 → 47".

**Text keys:** `bm.title`, `bm.reveal`, `bm.price.heat|hp|trade|curse|cycles`, `bm.curse.hot|brittle|leaky|marked`, `bm.fence`, `bm.wheel.*`, `bm.leave_confirm`, `bm.refused.hp_floor|heat_cap|limit`.

## 5. Interactions
- **Heat:** the central interaction; prices push toward thresholds with a visible crossing warning. A mid-run threshold raid uses the existing interlude. Scrubber, Proxy Relay and Cold Exit work normally. Retaliation (GDD 4.4): Heat paid here is not an objective extraction and does not provoke retaliation.
- **Daemons/Firmware:** a Daemon sells for 6 Schematics at the Fence, so rule-breakers choose; non-tradeable ones are flagged.
- **Other nodes:** the Mainframe sells for Cycles, the Market for risk.
- **Exploits:** no Exploit, key or story beat is ever for sale.
- **Tiers:** goods scale in rarity (T2 common/uncommon, T3–T4 up to RARE). Prices are tier-independent (R2).
- **Death:** HP prices cannot kill; carried curses still can matter in combat.

## 6. Data & systems
**New data:**
- `BlackMarketItemData`: `id`, `reward_ref`, `price_kind`, `price_amount`, `amount_mode`, `trade_slot_kind`, `curse_ref`, `rarity`, `min_tier`, `corp_filter`.
- `CurseData`: `id`, `kind`, `params`, `duration_combats`, `display_key`.
- `BlackMarketConfig` in `campaign_config.tres`: chances, `bm_heat_cap` = 10, `bm_hp_floor` = 1, fence values and caps.
- `EventWheelData` (N17) for the crate.

| System | Need | Size | Fallback |
|---|---|---|---|
| N1 amount modes | PERCENT HP price | S | FLAT HP numbers |
| N18 reward tables | The stock pool with price conditions | M | A fixed `black_market_pool.tres` |
| N16 | Marked curse | M | Drop Marked |
| N17 | Crate wheel | M | Drop the wheel |
| NEW: curses | Run-level riders with a duration | S–M | Only Hot (paid up front, so no carrying needed) and Leaky |
| NEW: stock-menu event page | An event layout with priced rows, pickers and per-purchase undo, reusing the event page | M | A plain 3-choice event with MODIFY_HEAT, HP loss and GAIN_* effects (prototype, no pickers) |

**Total:** M, plus S–M for curses; N17 optional.

## 7. Examples
**A. T2, COOL Heat 12 (Solace), 60 HP Breaker**
1. Firmware Patch+, HEAT +4 (12 → 16; crosses 25? no).
2. Uncommon card, HP 15 % = 9 (60 → 51, floor fine).
3. Kernel Sync with Leaky curse: free, −1 max RAM.
4. Fence: card 2 Schematics credit (banks at Rack capture) or −2 Heat.

**B. T3, FLAGGED Heat 55 (Meridian)**
1. Rare Firmware Mirror, TRADE: one Daemon.
2. Elite-loot card, HEAT +8 (55 → 63; crosses 75? no, 12 away).
3. HEAL pack (PERCENT 40 % max HP), CYCLES 60 × 1.5 = 90.
4. Fence: Firmware 4 Schematics or −2 Heat.
Crate wheel: Jackpot RARE / Standard / Bust, costs 1 Heat (63 → 64 with row 2).

**C. T4, HUNTED Heat 80 (Orbital), 45 HP Botnet**
1. Daemon Zero Day with Hot: free, +3 Heat now (80 → 83), within `bm_heat_cap`. Crosses 100? no.
2. Rare card, HP 25 % = 11 (45 → 34).
3. Firmware Burner with Brittle (3 combats), TRADE: any card.
4. Fence: Daemon 6 Schematics or −2 Heat.
No crate wheel at Heat ≥ 75.

## 8. Risks & balance notes
- **Heat banking:** buy with Heat, then sell junk for −Heat. Net bounded: the Fence removes at most 4 while prices add at most 10 (cap). Sim: Heat at the boss with and without visits.
- **HP laundering:** the floor, plus HP carries between fights mid-run. Sim: death rate after HP purchases.
- **Dominant free item:** test every curse for a negative net at T3.
- **Trade loop:** bought items have `fence_value` = 0.
- **Fence credit as a new economy path:** capped at 6 per visit, banked only at capture or completion, lost on death. Sim: Schematics per run with and without.
- **Best "?" problem:** compare Market value to the average event per node.
- **Sim policies:** always buy the cheapest in-currency item vs never visit. Target: positive for skilled players, neutral for average.
- **Preview integrity:** all prices are deterministic; only the crate draw is random, at a checkpoint.

## 9. Open questions
Q: Should the Market be recognizable after a first visit (a profile unlock that marks it on the map), or stay unknown?
Q: Should the Fence exist on a netrun at all, or only at HQ?
Q: Can the Fence accept Armory assets, or only deck, Firmware and Daemons?
Q: Does the Market appear in HQ runs (G12), or only street netruns?
Q: Should Hot be paid up front (as drafted) or accrue per combat?
