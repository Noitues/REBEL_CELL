<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__19_ambush_tethys; status ok; tokens in 4889 cache-write 0 cache-read 32585 out 2790; cost $0.022. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, tethys vs Meridian enemies):** Kept `corporation_id: tethys` (the event shows only on Tethys Grids) and justified the cross-corporation ambush in the text: Tethys contracts its retrieval to Meridian freight. No Tethys enemy ids exist in the inventory, so Meridian ids are the only legal option. Surfaced as Q1. The fight text now names a "Meridian-marked retrieval unit" and a "customs collector", matching the enemies.
- **Issue 2 (BLOCKER, tier tweak / phase budget):** Removed the "tier tweak −1 so it fights as a fresh elite" idea. `tier_offset` is 0, so the enemy fights at the Grid's tier. At min_tier 2, `last_mile_enforcer` is a 2-phase elite on the R2 T2 band of 68–88 HP, targeted at 78. The phase budget is shown in the design notes below.
- **Issue 3 (MAJOR, start block):** Now `enemy_start_block` 8 with `amount_mode` FLAT, multiplied by the enemy tier damage factor (1.3 at T2 ≈ 10). The contradictory "tier-independent" wording is gone.
- **Issue 4 (MAJOR, Heat and Cycles fields):** Heat is now a `stake` on entry, shown in the preview. Rewards sit in a `victory_effects` list (this answers v1 Q1). The enum values (MODIFY_HEAT 21, GAIN_CYCLES 22) were correct and are kept.
- **Issue 5 (MAJOR, dominance):** Rebalanced as the critic proposed. Choice 1 pays Firmware + 15 Cycles for +2 Heat and the elite risk. Choice 2 pays a card + 15 Cycles for −4 HP, with an easier fight. Choice 3 now has an upside: −1 Heat.
- **Issue 6 (MAJOR, text consistency):** Label changed to "+1 card, collector follows". The RAM −2 override is dropped. `customs_scanner` is a 1-phase normal, with its band and turn count stated.
- **Issue 7 (NIT):** The speaker is NARRATOR, with no int. Added text keys for the stake and preview lines. US spelling kept.
- **Critic Q on Heat when the player dies:** Heat is charged on entry and not refunded, because a signed delivery is traceable either way. Death already adds its own Heat under the GDD.

# ev_tet_pressure_courier: Pressure Courier

**Mechanic:** AMBUSH, corporation tethys, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Sign for a sealed delivery that Meridian will fight you for, pry it open for a cheap grab, or pay to void the claim.

## TerminalEventData fields
- id: `ev_tet_pressure_courier`
- title: Pressure Courier
- speaker: NARRATOR
- text: "A cargo sled noses out of a flooded service lock and parks against your Terminal, hull ticking as it equalizes. The panel reads: DELIVER TO ANY HAND. SIGNATURE VOIDS DEPTH LIABILITY. Tethys contracts its recoveries to Meridian freight, and a Meridian-marked retrieval unit is already surfacing behind the sled. Inside the crate something heavy shifts."
- corporation_id: `tethys`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Sign for the crate**
- label: "Sign for it (fight the retrieval unit: Firmware, +2 Heat)"
- result_text: "Your thumbprint clears the lock. The crate hisses, and the retrieval unit comes out of the dark water already working."
- cycle_cost: 0, hp_cost: 0
- effects: none
- (new) starts_combat (N16): enemy `last_mile_enforcer`
  - combat_overrides: `tier_offset` 0 (Grid tier); `enemy_start_block` 8, FLAT (N1), ≈10 at T2; no heat_effects.
  - stake: MODIFY_HEAT +2 (type 21, target CAMPAIGN) applied on entry and not refunded on death; normal operative death rules.
  - victory_effects: reward one Firmware from the uncommon pool; GAIN_CYCLES +15 (type 22, target CAMPAIGN).

**2. Pry it open and run**
- label: "Pry it open and run (+1 card, collector follows)"
- result_text: "You crack the seal before the sled stops. A card drops out, and the pressure alarm brings a collector to the door."
- cycle_cost: 0
- hp_cost: 4 (pressure burn on the lock)
- effects: none
- reward: one common Card (working: an instant BLOCK card), granted before the fight
- (new) starts_combat (N16): enemy `customs_scanner`
  - combat_overrides: `tier_offset` 0; no other overrides.
  - stake: HP only.
  - victory_effects: GAIN_CYCLES +15.

**3. Refuse delivery**
- label: "Refuse delivery (pay 15 Cycles, void the claim, −1 Heat)"
- result_text: "You wave the sled off and pay the liability fee through the lock. The voided claim scrubs your trace, and nobody follows."
- cycle_cost: 15, hp_cost: 0
- effects: MODIFY_HEAT −1 (type 21, target CAMPAIGN)
- reward: none
- Safe floor, no fight.

## Design notes
- **Phase budget (R2, choice 1):** Last-Mile Enforcer is a 2-phase elite. At T2, `reference_dpt` 11 × 3.5 turns × 2 phases ≈ 77 HP before sustain, inside the 68–88 band, so author 78 HP at T2 (40 / 38 across the 0.5 threshold). The fight runs ≈ 7 turns, inside the elite target of 6–8.
- **Choice 2 fight:** `customs_scanner` is a 1-phase normal, T2 band 34–44 HP, ≈ 3.5 turns.
- **No dominant option:**
  - Choice 1 gives a Firmware, the strongest run reward, for ≈ 7 turns of elite risk, +2 Heat and possible death.
  - Choice 2 gives a common card and 15 Cycles for 4 HP and a normal fight, a safe middle.
  - Choice 3 costs 15 of a typical ~60–100 Cycles per run, adds no risk and removes 1 Heat. It is the pick for a hurt or low-Heat-margin operative.
- **Determinism:** the enemy, overrides, stake and rewards are fixed data with no RNG, so the preview equals the result. The preview shows enemy name, tier, phases, stake and rewards.
- **Dependencies:** N16 (`starts_combat`, `combat_overrides`, `victory_effects`), N1 (FLAT block), N2 (T2 HP band). Data-only fallback: a plain choice using today's `hp_cost`, `effects` and `reward`, with no fight (the ambush is lost).
- **Interactions:** Scrubber and Clean Signal offset the Heat on choice 1. An operative at low HP should not take choice 1.
- **Text keys:** `ev_tet_pressure_courier.title`, `.text`, `.c1.label`, `.c1.result`, `.c1.stake`, `.c2.label`, `.c2.result`, `.c2.stake`, `.c3.label`, `.c3.result`, plus the ambush banner "RETRIEVAL IN PROGRESS".

## Q:
- Q: Is a cross-corporation enemy (Meridian in a Tethys event) allowed, or must it match `corporation_id`? If not, Tethys needs its own enemy ids.
- Q: Should `victory_effects` live on `EventChoiceData`, or on the combat override block?
