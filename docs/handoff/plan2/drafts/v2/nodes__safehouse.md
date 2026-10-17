<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__nodes__safehouse; status ok; tokens in 7592 cache-write 0 cache-read 32585 out 5855; cost $0.040. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, Rank 0 half-scale vs table):** dropped the "half scale, rounded down" rule. The table now lists explicit values for every class at every Rank, so nothing is derived. Rank 0 is explicit: Breaker +25 %, Ghost 0 steps, Rigger 3, Botnet no grant. Stated as a consequence, a rookie stationed with Ghost or Botnet gives nothing. The Q on whether rookies give any bonus is kept.
- **Issue 2 (BLOCKER, amount modes):** each `rank_scaling` entry now carries an `amount_mode` (R5). The Breaker bonus is PERCENT of the base asset damage. Ghost delay, Rigger repair and the Botnet grant are FLAT. Rigger repair stays FLAT (3/5/7/10 integrity) and the false claim that percent is "used only for repair" was removed. Flat integrity amounts are node-side values, not enemy amounts, so the R2 tier factor does not apply. This is stated in §2.
- **Issue 3 (MAJOR, stacking):** the slot rule is rewritten. A Level II Safehouse hosts 2 operatives. A second same-class operative contributes `second_slot_bonus_ratio` = 0.5 of its values (rounded down, minimum 0). Different classes stack fully. The key now appears in §2. This resolves old Q4, which is replaced. The 2nd operative appears in Example B.
- **Issue 4 (MAJOR, invented numbers and dependency tags):** Ghost is 0/1/1/2, with Rank 1 matching the GDD "delayed 1 step". The Botnet is now a fixed TURRET (3 damage, the Firewall Relay value) per raid, max 1, with the invented Rank 2 and Rank 3 persistence removed. This fits the Armory cap of 6 because the grant isn't an Armory asset, so it can't exceed the cap. The systems line is rewritten with consistent tags: NEW: station bonus raid hook (M), NEW: station asset grant (S).
- **Issue 5 (MAJOR, Example B / range contradiction):** `bonus_range_hops` = 0 at Level I and 1 at Level II. The "1 at Rank 3" rule was removed. Example B is recomputed under this rule.
- **Issue 6 (MAJOR, Example C / Rigger range):** Example C now places the Rigger's Level II Safehouse adjacent to the Vault Terminal, so the range-1 repair reaches it. The Rigger's value is also explained: it repairs the Safehouse itself at range 0 and neighbours at range 1.
- **Issue 7 (NIT):** the RNG statement is now explicit, with no stream used because placement is player-chosen. A cancel path for the Level II upgrade was added to §4.
- **Issue 8 (NIT):** kept; it restates GDD 5.4.
- **Triage row 1 (tier-or-hp-bands):** the Rank 0 values are explicit and not derived from any tier or half-scale factor. Bonuses scale with Rank only, never with Site tier or the R2 tables.
- **Triage row 2 (amount-modes-and-scaling):** handled as Issue 2.
- **Kept, because the critic marked it strong:** the cost-versus-benefit framing, the Heat-neutral stationing, the GDD-grounded class bonuses with alternates sharing a family (G8), and the 4-Safehouse cap and install curve.
- **Q changes:** added the critic's Q on rookies, Level II range for the Botnet grant, and Rank from raids. Kept the pre-built first Safehouse question. Dropped the Botnet pool question (the TURRET is now fixed) and the range-for-alternates question (alternates may only change numbers, a firm rule).

---

# Safehouse: design draft (v2)

## 1. Purpose & the decision it creates
The Safehouse is the Cell's bench. An operative who doesn't run this round is stationed here, and the node turns that idle body into a local bonus. The player weighs three costs against one gain.
- **Opportunity cost:** a stationed operative can't netrun, so Rank and loot are forgone.
- **Placement:** the bonus is local, so a Safehouse's position decides whether it pays off.
- **Risk:** a TAKEN or DOWN Safehouse sends the operative home unharmed (GDD 3.3), but the bonus is lost. Stationing is a bet on where the next raid lands.
- **Expansion:** each Safehouse costs Schematics that could go to a Relay or a Vault Terminal.

Stationing is the Heat-free alternative to running. Testers report too many runs, with 605 minutes against a 395 target. A stationed veteran gives a defensive economy that doesn't need a netrun.

## 2. Rules

**Stationing.**
- Only operatives between netruns can be stationed. Each takes one slot of the node's `station_slots`.
- Stationing and recalling are free and instant between runs. An operative on a run can't be stationed.
- A stationed operative takes no Heat, gains no Rank (see Q3) and cannot die.
- A Rank 0 rookie may be stationed, but several bonuses are 0 at Rank 0 (table below).

**Station bonus framework (G8).** Each class has one `StationBonusData`:
- `station_effect`: a typed effect applying to the Safehouse node, or to nodes within `bonus_range_hops`.
- `rank_scaling`: 4 entries (Rank 0–3), each `{amount, amount_mode}`. The mode is FLAT or PERCENT (R5). PERCENT here means a percent of the base asset damage, not of any max HP. FLAT integrity and step values are node-side amounts, and the enemy tier damage factor (R2) does not apply to them.
- `adjacency_synergy`: an optional bonus when the Safehouse neighbours a named node type (existing `AdjacencyBonusData`).

**Range.** `bonus_range_hops` is 0 at Level I (the node itself) and 1 at Level II. It does not change with Rank.

**Alternates (G8).** An alternate shares its parent's `station_bonus_family`. It may override only the numeric values, by at most ±25 %, never the effect type or the range.

**Class bonuses** (explicit values; nothing is derived):

| Class | Effect | R0 / R1 / R2 / R3 | Mode |
|---|---|---|---|
| Breaker | Assets in range deal more damage | +25 / +50 / +60 / +75 % | PERCENT of base asset damage |
| Ghost | Threats entering in-range nodes are delayed | 0 / 1 / 1 / 2 steps | FLAT |
| Rigger | In-range nodes regain integrity after each raid wave | 3 / 5 / 7 / 10 | FLAT |
| Botnet | A free TURRET (3 damage) on the Safehouse node each raid, max 1 | 0 / 1 / 1 / 1 | FLAT (count) |

Breaker Rank 1 (+50 %) and Ghost Rank 1 (1 step) match GDD 5.2. A rookie Ghost or Botnet gives nothing, so rookies are worth stationing only as Breakers or Riggers. The Botnet turret is granted by the Safehouse, not drawn from the Armory, so it can't exceed the Armory cap of 6. It exists only for that raid.

**Slots and stacking.**
- Level I hosts 1 operative. A Level II Safehouse hosts 2.
- A second same-class operative contributes `second_slot_bonus_ratio` = 0.5 of its values (rounded down, minimum 0). The Botnet's count stays at max 1 per Safehouse.
- Different classes stack fully.

**Upgrades.**

| Level | Effect |
|---|---|
| I (base) | 1 slot, integrity 20, 1 asset slot, range 0 |
| II | 2 slots, integrity 30, range 1 |

Level II costs `safehouse_upgrade_cost` = 30, independent of the install count. It is the choice to weigh against a new Safehouse: a new one covers a new area, an upgrade deepens one hub.

**Install cost curve.**
- `safehouse_install_costs` = [20, 30, 45, 65] for the 1st–4th Safehouse, in Schematics.
- `max_safehouses` = 4 per campaign. This is the main anti-degeneracy cap. The node needs no profile unlock.

**Raid interaction.**
- The Safehouse has no built-in asset, only integrity and an asset slot. Its value is borrowed from the station.
- The bonus applies for the whole raid. If the node goes DOWN mid-raid, the bonus ends at once. If it ends TAKEN, the operative returns to reserves unharmed (GDD 3.3).
- `raid_priority` = 0, so threats don't path to it on purpose. Rigger repair at range 0 therefore mostly matters when threats pass through, and its best use is at Level II covering a valued neighbour.

**Heat.** `station_heat_per_run` = 0. Stationing costs and gives no Heat, which keeps it distinct from the Proxy Relay and Heat objective Sites.

## 3. Placement & generation
- The player installs on any claimed Site with a free node slot, as for any network node.
- Placement is player-chosen, so no RNG stream is used. Bonuses are pure functions of Rank, level and node state.
- **Campaign count:** 0 at start (2 rookies, 20 Schematics, first Safehouse costs exactly 20). It is not pre-installed, so the opening has a real choice (Safehouse or Relay). See Q1.
- **Exclusions:** not on the home server, and not on a TAKEN or DOWN Site (G11).
- **By corporation:** none; the node is corporation-neutral.
- **Save:** each node record gains `stationed_operative_ids` and `node_level`.

## 4. UX flow
1. **HQ City Grid:** a Safehouse shows a badge with slots used and the stationed class glyph.
2. **Select the node:** the card lists integrity, slots, level, range and the current bonus. Empty: "Station an operative here".
3. **Station:** the player picks a reserve operative. The card previews the exact effect, e.g. "Ghost, Rank 2: threats entering delayed 1 step." A Rank 0 Ghost previews "No bonus at Rank 0".
4. **Confirm:** one confirm names the forgone run. The node updates at once.
5. **Raid setup:** the stationed bonus is included in the projected outcome (deterministic, GDD 7.1).
6. **Recall:** "Recall" works any time between runs. Cancelling before confirm changes nothing. Recall after confirm is free, so no Undo is needed.
7. **Upgrade to Level II:** a card shows the cost, new slot count and range. Cancel before confirm leaves everything unchanged. After confirm the Schematics are spent, with no refund.

**Text keys:** `node.safehouse.station`, `node.safehouse.recall`, `node.safehouse.empty`, `node.safehouse.upgrade_ii`, `node.safehouse.upgrade_confirm`, `node.safehouse.no_bonus_r0`, `station.bonus.<class>.desc` (per class), `station.bonus.rank_scaling`, `node.safehouse.max_reached`.

## 5. Interactions
- **Heat:** none directly. A raid triggered by Heat benefits from the bonus, so Safehouses make high-Heat play more survivable.
- **Raids:** the Ghost bonus pairs with ICE Locks, the Breaker with Firewall Relay turrets, the Rigger with multi-wave raids (R4's second wave), and the Botnet with raids when the Armory is empty.
- **Daemons/Firmware:** none; they belong to a run.
- **Other nodes:** a Breaker Safehouse adjacent to a Firewall Relay needs Level II (range 1) to boost the turret. A Safehouse on the Vault Terminal's Site, or a Level II next to it, lets the Rigger protect it.
- **Exploits:** none.
- **Tiers:** bonuses scale with Rank only, not Site tier. A stationed veteran is stronger than a rookie, which is the tension with running them.
- **Raid strength:** scales with Heat, not with stationed operatives.

## 6. Data & systems
**New fields.**
- `NetworkNodeData`: `station_bonus_enabled` (bool), `upgrade_levels` (array of level data), `bonus_range_hops` (int, by level).
- New `StationBonusData`: `class_id`, `family_id`, `station_effect` (TriggeredEffectData), `rank_scaling` (4 × {amount, amount_mode}), `adjacency_synergy` (optional).
- `campaign_config.tres`: `safehouse_install_costs` = [20, 30, 45, 65], `safehouse_upgrade_cost` = 30, `max_safehouses` = 4, `second_slot_bonus_ratio` = 0.5.
- Campaign save: `stationed_operative_ids`, `node_level`.

**Systems.**
- NEW: station bonus raid hook (M). The raid resolver reads a node's station bonus when applying asset damage, delay and repair.
- NEW: station asset grant (S). The Botnet's per-raid TURRET.
- Neither fits an N#. **Data-only fallback:** Breaker, Ghost and Rigger as node `passive_effects`; the Botnet is deferred.
- **Size:** M overall (data S, raid hooks M).

## 7. Examples

**A. Early Ghost.** The 1st Safehouse (20) is installed on a Relay-adjacent Site. A Rank 1 Ghost is stationed (range 0, 1 step). A Heat-25 raid's first threat entering that node is delayed 1 step. The player compares this with a Relay at 20 that would reach one more Site.

**B. Breaker hub.** The 2nd Safehouse (30) is installed next to a Firewall Relay (3-damage turret). A Rank 2 Breaker is stationed (+60 %), but range is 0, so the turret gets nothing. Level II (30 more) gives range 1, and the turret deals 3 × 1.6 = 4.8, rounded to 5. A second Breaker stationed too, at Rank 3, adds 75 × 0.5 = 37 % (rounded down), so +60 % + 37 % = +97 % and the turret deals 3 × 1.97 ≈ 5.9, rounded to 6. Total spent: 60 Schematics for the Level II hub.

**C. Rigger anchor.** The 3rd Safehouse (45) is installed adjacent to the Vault Terminal (integrity 20) and upgraded to Level II (30), 75 in total. A Rank 3 Rigger restores 10 integrity per wave to every node in range 1, including the Vault Terminal. Against R4's second wave the Terminal survives where it would have gone DOWN. The player judges 75 Schematics to protect +3 per run's income worth it.

## 8. Risks & balance notes
- **Stack exploit:** same-class stacking. The 0.5 ratio and the 4-Safehouse cap limit it. Sim: 4 Level II Safehouses with all Breakers.
- **Running vs stationing:** too strong and the campaign stalls; too weak and nobody stations. Compare average end-of-campaign Rank with and without stationing.
- **Rank inflation:** the best operatives are the ones you most want to run. That conflict is intended, but check the Rank 3 bonus isn't too small to justify benching one.
- **Rookie dump:** rookies (15 Schematics) give nothing as Ghost or Botnet at Rank 0, and a Breaker's +25 % or a Rigger's 3 is small. Check that mass-recruiting rookies to station is not cheaper than building defenses.
- **Botnet turret:** capped at 1 per Safehouse per raid, so 4 Safehouses give at most 4 free turrets. Test whether that outscales the Armory.
- **Determinism:** pure functions of Rank, level and node state, so previews equal results.
- **Sim tests:** raid hold rate with 0, 1, 2 and 4 Safehouses; Schematics spent per hold; campaign minutes against 395.

## 9. Q:
- Q: Should the first Safehouse come pre-built in the home server variants, or stay a 20-Schematic first purchase?
- Q: Should Rank 0 rookies give any bonus at all, or only Rank 1 and up (as the table now implies for Ghost and Botnet)?
- Q: Should a stationed operative's Rank advance from raids survived, or is the defensive bonus the only reward?
- Q: Does Level II range 1 apply to the Botnet's grant too (a turret on an adjacent node), or only to the Safehouse node?
- Q: Should same-class stacking at 50 % stay, or should the second slot require a different class?
