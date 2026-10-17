<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__19_ambush_tethys; status ok; tokens in 6419 cache-write 0 cache-read 32007 out 1951; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_tet_pressure_courier: Pressure Courier

**Mechanic:** AMBUSH, corporation tethys, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Sign for a sealed delivery that someone is willing to fight you for, or refuse it and risk the courier opening up on you anyway.

## TerminalEventData fields
- id: `ev_tet_pressure_courier`
- title: Pressure Courier
- speaker: NARRATOR (0)
- text: "A cargo sled noses out of a flooded service lock and parks against your Terminal, hull ticking as it equalizes. The courier's panel reads: DELIVER TO ANY HAND. SIGNATURE VOIDS DEPTH LIABILITY. Inside the sealed crate something heavy shifts. A second ping tells you someone upstream wants it back before the pressure rating expires."
- corporation_id: `tethys`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Sign for the crate**
- label: "Sign for it (fight the retrievers: +reward, risk HP)"
- result_text: "Your thumbprint clears the lock. The crate hisses, and the retrieval unit comes out of the dark water already working."
- cycle_cost: 0, hp_cost: 0
- effects: none (resolved by the fight)
- reward: none directly; the fight reward is below
- (new) starts_combat: enemy `last_mile_enforcer`
  - combat_overrides: tier tweak −1 (min 1) so it fights as a fresh elite; `enemy_start_block` +8 (pressure plating, tier-independent flat amount); no heat_effects.
  - stake: on defeat, normal operative death rules. On victory the crate pays out.
  - reward on victory: one Firmware from the uncommon pool ("sealed crate: rare chip") plus +30 Cycles. A GAIN_CYCLES effect (type 22, target 6, amount 30) is attached to the victory branch.
  - Heat: +2 (MODIFY_HEAT, type 21, target 6, amount 2), applied on entering the fight, since a signed delivery is traceable.

**2. Open it first, take the contents**
- label: "Pry it open and run (+1 Daemon-fragment card, ambush follows)"
- result_text: "You crack the seal before the sled stops. A cheap card drops out, and the pressure alarm brings a collector to the door."
- cycle_cost: 0
- hp_cost: 4 (hull-pressure burn on the lock)
- effects: none
- reward: a common Card (working: "Pressure Valve", an instant block card), granted before the fight
- (new) starts_combat: enemy `customs_scanner`
  - combat_overrides: tier +0; the player starts with RAM −2 (the alarm taxes your link). Reward on victory: +15 Cycles. No stake beyond HP.
  - Cheaper fight, smaller prize, but you are already hurt.

**3. Refuse and leave it**
- label: "Refuse delivery (pay 15 Cycles to void the claim)"
- result_text: "You wave the sled off and pay the liability fee through the lock. It drifts away. Nobody follows you."
- cycle_cost: 15, hp_cost: 0
- effects: none
- reward: none
- (new) next_combat_overrides: none. Safe option, at a price.

## Design notes
- **No dominant option:** Choice 1 is a high-risk elite fight (tier −1, so about 6–8 turns at the R1 target) for a Firmware, which is the strongest reward in the run economy; it costs HP, Heat and possible death. Choice 2 is a short normal fight for a common card and 15 Cycles, but starts at −4 HP and −2 RAM. Choice 3 costs 15 Cycles of a typical ~60–100 per run and nothing else, the safe floor.
- **Stake logic:** both fights are optional and clearly previewed (enemy name, tier tweak, reward) so the player can judge feel.
- **Elite design check (R1):** an elite in a Terminal is a deliberate spike. The tier −1 tweak keeps its HP in the T2-adjacent band, not an extra HP multiplier, honoring R2. The +8 start block is a flat amount, scaled by the enemy damage factor at that tier.
- **Determinism:** no RNG. The enemy, overrides and rewards are fixed data, so the preview equals the result.
- **Dependencies:** N16 (`EventChoiceData.starts_combat` and `combat_overrides`), N2 (tier tables for the tier tweak). Data-only fallback: replace both fights with a plain choice (HP cost plus a reward) using today's `hp_cost`, `effects` and `reward`; this loses the ambush but keeps the structure.
- **Interactions:** Heat +2 on choice 1 pairs with Scrubber and Clean Signal Daemons; the −2 RAM override on choice 2 pairs with Rigger's max-RAM Hub Core.
- **Text keys:** `ev_tet_pressure_courier.title`, `.text`, `.c1.label`, `.c1.result`, `.c2.label`, `.c2.result`, `.c3.label`, `.c3.result`, plus an ambush banner key "RETRIEVAL IN PROGRESS".

## Q:
- Should a combat reward be a single choice in `EventChoiceData` (victory branch) or a separate `victory_effects` list?
- Does a tier tweak on an impromptu fight also move the enemy's HP band (hp_by_tier), or only its starting damage?
