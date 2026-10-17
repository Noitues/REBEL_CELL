<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01LxQs8RvJGj9WzDuV2avpgt, custom_id node__safehouse; status ok; tokens in 14028 cache-write 0 cache-read 32007 out 4612; cost $0.040. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Safehouse: design draft

## 1. Purpose & the decision it creates
The Safehouse is the Cell's bench. An operative who doesn't run this round is stationed here, and the node turns that idle body into a local bonus. The player weighs three costs against one gain.
- **Opportunity cost:** a stationed operative can't netrun, so Rank and loot are forgone.
- **Placement:** the bonus is local, so a Safehouse's position decides whether it pays off.
- **Risk:** a TAKEN or DOWN Safehouse sends the operative home unharmed (GDD 3.3), but the bonus is lost. Stationing is a bet on where the next raid lands.
- **Expansion:** each Safehouse also costs Schematics that could go to a Relay or a Vault Terminal.

The framework is built so that "run again" versus "station" is a real choice. The campaign's tester pain is too many runs, with 605 minutes against a 395 target. A stationed veteran therefore also provides a defensive economy that doesn't require playing a netrun.

## 2. Rules

**Stationing.**
- Only operatives between netruns can be stationed; each takes one `station_slots` slot. The current `safehouse.tres` has `station_slots = 1`.
- Stationing and recalling are free and instant between runs. An operative on a run can't be stationed.
- A stationed operative takes no Heat and gains no Rank, and cannot die.
- A Rank 0 rookie can be stationed, but with the reduced bonus described below.

**Station bonus framework (G8).**
Each class has one `StationBonusData` with three parts:
- `station_effect`: a typed effect applying to the Safehouse node, or to the nodes within `bonus_range_hops` of it. Range is 0 by default (the node itself) and 1 at Rank 3.
- `rank_scaling`: an amount per Rank (0–3), written as FLAT. Percent amounts read the target node's max integrity and are used only for repair.
- `adjacency_synergy`: an optional bonus when the Safehouse neighbours a named node type, reusing `AdjacencyBonusData`.

**Alternates feel similar (G8).**
- Alternate versions of a class (same deck with a different core, or the reverse) share the parent class's `station_bonus_family`.
- An alternate may override only the numeric scaling, by at most ±25 %. It can never change the effect type.
- The bonus therefore reads the same across a class's alternates, which is what G8 asked for.

**Station bonuses for the existing classes** (the effect lines follow the GDD 5.2 station column and are made concrete here):

| Class | Effect | Rank 0 / 1 / 2 / 3 |
|---|---|---|
| Breaker | Assets on this node deal +% damage | +25 / +50 / +60 / +75 % |
| Ghost | Threats entering this node are delayed N steps | 1 / 1 / 2 / 2 steps |
| Rigger | Node regains integrity after each raid wave | 3 / 5 / 7 / 10 |
| Botnet | Node gets free asset(s) per raid, from a drone pool | 1 asset per raid at all Ranks; at Rank 2 it is a TURRET, at Rank 3 it persists |

The Breaker's Rank 1 value (+50 %) matches the GDD. Rank 0 is half scale, rounded down.

**Slot rule.** A Safehouse's `station_slots` is 1 at install. Upgrading it to level II adds a slot. Each slot hosts one operative, so two stationed operatives of the same class stack at 50 % for the second.

**Upgrades.** There are two levels. Both use `upgrade_cost` taken from the same table as the install curve.

| Level | Effect |
|---|---|
| I (base) | 1 slot, integrity 20, 1 asset slot |
| II | 2 slots, integrity 30, `bonus_range_hops` +1 |

The second slot is the purchase to weigh against a new Safehouse. A new Safehouse covers a new area; an upgrade doubles one hub.

**Install cost curve.**
- `safehouse_install_costs` = [20, 30, 45, 65] for the 1st through 4th Safehouse in a campaign, and 85 for any beyond.
- Level II costs 30 and is not tied to the install count.
- The cost is paid in Schematics and the node has `profile_unlock_required = false`, so it is always available.
- A cap of 4 Safehouses per campaign (`max_safehouses`) prevents blanketing the grid. This is the main anti-degeneracy cap.

**Raid interaction.**
- The Safehouse has no built-in asset, only an asset slot and integrity 20, so it is a weak node by itself and its value is borrowed from its station.
- A stationed operative's bonus applies for the whole raid.
- If the node goes DOWN mid-raid, the bonus ends at once. If it ends the raid TAKEN, the operative returns to reserves unharmed (GDD 3.3).
- `raid_priority` stays 0, so threats don't path to it on purpose. Stationed operatives shouldn't make the node a magnet.

**Heat interaction.**
- Each stationed operative adds `station_heat_per_run` = 0, so stationing has no Heat cost. That is deliberate: it is the Heat-free alternative to running.
- It also has no Heat benefit. This keeps it separate from the Proxy Relay and the Heat objective Sites.

## 3. Placement & generation
- The player chooses where to install: any claimed Site that has a free node slot, as for any network node.
- There is no random placement, so no new RNG stream is needed.
- **Campaign counts:** 0 at start. The campaign starts with 2 rookies and 20 Schematics, and the first Safehouse costs exactly 20. The designer should weigh whether the first Safehouse should be pre-installed in the home server variants; this draft does not do that, so the opening has a real choice (Safehouse or Relay).
- **Exclusions:**
  - It can't be installed on the home server.
  - It can't be installed on a TAKEN or DOWN Site (G11).
- **By corporation:** none. The node is corporation-neutral.
- **Stationed operative state:** it is saved with the campaign, so the node's save record gains `stationed_operative_ids`.

## 4. UX flow
1. **HQ page, City Grid:** a Safehouse shows a small badge with its slot count and the stationed class glyph.
2. **Select the node:** the card lists integrity, slots, the level, and the bonus the stationed operative gives. If it is empty, it reads "Station an operative here".
3. **Station:** the player picks an operative from the roster (reserve operatives only) and the card previews the exact effect: "Ghost, Rank 2: threats entering delayed 2 steps."
4. **Confirm:** one confirm shows the lost run opportunity. The node updates at once.
5. **Raid setup view:** the stationed bonus appears in the projected outcome. Since resolution is deterministic (GDD 7.1), the outcome preview already includes it.
6. **Recall:** a "Recall" button is available at any time between runs. Cancelling a station before confirming leaves no change; after confirming, recalling is free, so no Undo is needed.

**Text keys:** `node.safehouse.station`, `node.safehouse.recall`, `node.safehouse.empty`, `node.safehouse.upgrade_ii`, `station.bonus.<class>.desc` (one per class), `station.bonus.rank_scaling`, `node.safehouse.max_reached`.

## 5. Interactions
- **Heat:** none directly (above). A raid that Heat triggers benefits from the stationed bonus, so Safehouses indirectly make high-Heat play more survivable.
- **Raids:** the bonus is the core interaction. The Ghost bonus pairs with ICE Locks, the Breaker with Firewall Relay turrets, the Rigger with attritional multi-wave raids (R4's second wave), and the Botnet with raids where the Armory is empty.
- **Daemons/Firmware:** no interaction, since those belong to a run and a stationed operative isn't on one.
- **Other nodes:**
  - Firewall Relay: adjacent to the Breaker's Safehouse, the turret gets the damage bonus.
  - Vault Terminal: raid priority 2 draws threats, so it pairs with the Ghost bonus on the next node.
  - Compiler Rack and Proxy Relay: no special interaction.
- **Exploits:** none. Exploit Sites aren't affected.
- **Tiers:** the bonus does not scale with Site tier, only with the operative's Rank. Rank is the reward for running, so a veteran stationed is stronger than a rookie. That is the tension with running them.
- **Raid strength:** raids scale with Heat, not with the number of stationed operatives, so stationing does not make raids harder.

## 6. Data & systems
**New fields.**
- `NetworkNodeData`: `station_bonus_enabled` (bool), `upgrade_levels` (Array of node level data), `bonus_range_hops` (int).
- New `StationBonusData`: `class_id`, `station_effect` (TriggeredEffectData), `rank_scaling` (Array[int], 4), `adjacency_synergy` (AdjacencyBonusData, optional), `family_id`.
- `campaign_config.tres`: `safehouse_install_costs`, `safehouse_upgrade_cost`, `max_safehouses`, `second_slot_bonus_ratio` = 0.5.
- Campaign save: `stationed_operative_ids` per node, and `node_level`.

**Systems.**
- No N# system is required; this builds on existing raid code and stationing.
- It needs the raid resolver (`raid_resolver`) to read a node's station bonus when applying asset damage, delay, repair, and spawn. That is a new hook but not a numbered system.
- **Data-only fallback:** the Breaker, Ghost, and Rigger bonuses can be expressed as `passive_effects` on the node if the raid code already supports raid triggers. The Botnet bonus ("free asset per raid") needs a small new effect type, `GRANT_RAID_ASSET`, which is NEW: station asset grant.
- **Size:** M overall. The data is S, and the raid hooks are M.

## 7. Examples

**A. Early Ghost.** The 1st Safehouse (20 Schematics) is installed on a Relay-adjacent Site. A Rank 1 Ghost is stationed. A Heat-25 raid arrives, and the first threat entering the node is delayed 1 step. The player compares this with a Relay at 20 that would reach one more Site.

**B. Breaker hub.** The 2nd Safehouse (30) is installed next to a Firewall Relay (3-damage turret). A Rank 2 Breaker is stationed (+60 %), so the turret deals 3 × 1.6 = 4.8, rounded to 5. At Level II (30 more), range 1 also boosts a second turret one hop away. Total spent: 60 Schematics for a modest, defensible chokepoint.

**C. Rigger anchor.** The 3rd Safehouse (45) is installed at the Vault Terminal's neighbour. A Rank 3 Rigger restores 10 integrity after each wave. Against R4's Heat-scaled second wave, the Vault Terminal (integrity 20) survives where it would have gone DOWN. The player decided that 45 Schematics to protect +3 per run was worth it.

## 8. Risks & balance notes
- **Stack exploit:** two same-class operatives stacking. The second-slot ratio of 0.5 and the 4-Safehouse cap limit this. Test with the sim: 4 Level II Safehouses, all Breakers.
- **Running vs stationing:** if stationing is too strong, players stop running and the campaign stalls. If it is too weak, nobody stations. Test the average Rank at campaign end with and without stationing.
- **Rank inflation:** the bonus scales with Rank, so the best operatives are the ones you most want to run. That conflict is the point, but check that it isn't a trap where the bonus is too small to justify benching a Rank 3.
- **Rookie dump:** rookies are cheap (15 Schematics) and have reduced bonuses. Check that mass-recruiting rookies to station them is not cheaper than building defenses.
- **Botnet bonus:** a free asset per raid can outscale the Armory limit of 6. Cap at one asset per Safehouse per raid.
- **Determinism:** bonuses are pure functions of Rank and node state, with no randomness, so previews equal results.
- **Sim tests:** raid hold rate with 0, 1, 2, and 4 Safehouses; Schematics spent per hold; campaign minutes against the 395 target.

## 9. Q:
- Q: Should the first Safehouse come pre-built in the home server variants, so every campaign starts with a station, or stay a 20-Schematic first purchase?
- Q: Should stationed operatives recover something (for example, a Rank progress tick every N raids survived), or is the defensive bonus the only reward?
- Q: Does the Botnet's free asset use the Armory type pool, or is it a fixed Safehouse-specific TURRET variant?
- Q: Should a second stationed operative stack at 50 %, or should the second slot hold a different class bonus only (no same-class stacking)?
- Q: Should class alternates be allowed a different bonus range (hops), or only different numbers?
