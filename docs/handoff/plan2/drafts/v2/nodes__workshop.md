<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__nodes__workshop; status ok; tokens in 8832 cache-write 0 cache-read 32585 out 6009; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Critic 1 (BLOCKER, gating vs placement vs count):** fixed.
  - Gating is now `workshop_max_level_by_layer` = layer 3 → I, layers 4–5 → II, layers 6–7 → III.
  - Placement is now explicit by tier. T1: 0 (a teach-path exclusion, now stated as a ruling-compatible default). T2: exactly 1 at layers 3–5. T3+: 1 at layers 3–5 and a second at layer 6. T4: same as T3.
  - The "~0.9 per run" figure is replaced with arithmetic: with the campaign mix of T1/T2/T3/T4 runs per §3, the mean is about 1.2 per T2+ run and about 0.9 over all runs.
  - A Workshop at layer 3 can only ever offer Level I. This is intended and now stated.
- **Critic 2 (BLOCKER, Cycle costs vs earnings, 10:1 conversion):**
  - Added `cycles_per_netrun_estimate` = 220 (a placeholder pending the economy sim), with the Workshop budget capped at 35–45 % of it, i.e. 77–99 Cycles.
  - Rescaled costs: slice 25/45/70/100, card 20/35/55/80.
  - Level IV is removed from the Workshop. It is Rack-flash only (N18), so the 100-Cycle slice price is the layer 6–7 ceiling for Level III at 70.
  - Spending 70 Cycles forgoes 7 Schematics through the 10:1 conversion. That is stated as the intended opportunity cost.
  - The full-price run total is shown against the Schematic equivalents and compared to the 80-Schematic class unlock.
- **Critic 3 (MAJOR, License lock):** the lock is dropped. The Workshop is always usable. The License is now an optional Schematics purchase, `workshop_license_cost` = 30 Schematics (one layer: campaign, not profile), that adds +1 offer (3 → 4) and −15 % cost. `profile_unlock_required` is removed. The locked example is replaced.
- **Critic 4 (MAJOR, stream seed, rewind/abandon, invented Daemons):**
  - The seed derivation is stated: `workshop` stream seed = hash(run seed, node id), state saved on entry.
  - The abandon path is covered: the offers are discarded with the run.
  - Combat rewind is unaffected (no combat inside the node).
  - Daemons are marked as examples, not ids.
  - "Overclock Bench" is reworded to the R9 RAM-debuff meaning of CORRUPTED.
- **Critic 5 (MAJOR, fallback modes):** the fallback is now "generic_level: slice output +1, `amount_mode` FLAT; card −1 RAM, minimum 0". The order is stated as base → Level → Firmware. The reference to Patch+ is dropped.
- **Critic 6 (MAJOR, dpt drift):** added `workshop_dpt_ceiling` = 1.25. A full run of Workshop upgrades must keep the reference player's dpt ≤ reference × 1.25, and the slice pass lints it. The run cap is lowered from 6 to 5.
- **Critic 7 (NIT):**
  - The unsupported claim that Heat raises Cycle prices is removed. `CYCLE_PRICE_PCT` is cited only as an existing rule modifier.
  - The "adjacent to a Mainframe" rule becomes "not in the same layer as a Mainframe".
  - The Rack-flash dependency is marked as N18.
  - The filler quote is removed.
  - The Heat example is fixed: the MINOR complication fires on first crossing and is set per netrun.
- **Triage rows:** both are applied (see critic 1 and 2).
- **Critic Q2 (persistence):** the draft's Q5 is kept. GDD 4.2 keeps deck, Firmware and Daemons on completion, so upgrades persist on survivors and die with the operative. Stated in §5.
- **Critic Q3 (T1 availability):** kept at no Workshop on T1, because T1 netruns teach Shop, Event and combat first. Re-asked as a Q.
- **Kept, because strong:** one decision per visit, the real-position preview, the CONFIRM step, offers generated on entry from saved state, and the `levels` data split with a data-only fallback.

# WORKSHOP: design draft (v2)

## 1. Purpose & the decision it creates

The Workshop is the netrun's **spend-to-improve** node. The player pays Cycles to make something they already own permanently better for the rest of that operative's life. The Mainframe sells new things; the Workshop improves existing ones. Each visit asks one question: **"Which one thing do I already trust enough to invest in?"** A slice upgrade favours a steady wheel, and a card upgrade favours a build engine.

The player also weighs a certain gain now against Cycles saved for a Mainframe, and against the Schematics those Cycles would become at 10:1 (GDD 4.2). Slice and card upgrades are separate design passes. This draft defines the **node, offers, costs and limits**, and the content plugs in through `UpgradeOfferData`.

## 2. Rules

**Inputs:** one upgradable target (slice or card) and Cycles.

**Output:** the target gains +1 Level. The Workshop reaches at most Level III; Level IV comes only from the Rack flash reward (N18). Level 0 is the base item, and a Level is an entry of the target's own `levels` array.

**Offers:** 3 per visit (`workshop_offers_per_visit` = 3), and **at most 1 buy** per visit (`workshop_buys_per_visit` = 1).

**Offer mix:** `workshop_offer_mix` = {slice: 2, card: 1}.
- If the card pass is unbuilt, the card slot is filled with a third slice offer.
- If a kind has no eligible target, its slot is filled from the other kind.
- If both are empty, the node shows "NOTHING TO IMPROVE", and the map generator should have swapped in a Terminal (§3).

**Cost (Cycles, FLAT, `workshop_cost_by_level`):**

| Upgrade to | Slice | Card |
|---|---|---|
| Level I | 25 | 20 |
| Level II | 45 | 35 |
| Level III | 70 | 55 |

- Costs are not tier-scaled; the tier already scales earnings.
- `CYCLE_PRICE_PCT` (an existing rule modifier, PERCENT) modifies the price, rounded up.
- **Schematics are not spent at the node.**

**Economy check (placeholders, pending the economy sim):**
- `cycles_per_netrun_estimate` = 220.
- Workshop budget = 35–45 % of that = 77–99 Cycles per run.
- A typical run buys 1–2 upgrades. For example, one Level I slice (25) plus one Level II slice (45) = 70.
- The most a T3+ run can spend in the Workshop is I + II + III on slices = 140, over two visits. That is 64 % of the estimate, so it is only possible by skipping the Mainframe.
- Opportunity cost: 70 Cycles = 7 Schematics at the 10:1 conversion. The 80-Schematic class unlock would need about 1,140 Cycles of upgrade-equivalent savings, so Workshop spending can't plausibly rival it.

**Limits:**
- **Layer gating** (`workshop_max_level_by_layer`): layer 3 → I, layers 4–5 → II, layers 6–7 → III. The layer-3 Workshop therefore only offers Level I.
- A target gains one Level per visit, even across Workshops.
- Run cap: `workshop_run_upgrade_cap` = 5.
- **DPT ceiling:** `workshop_dpt_ceiling` = 1.25. A full set of Workshop upgrades must keep the reference player's dpt ≤ reference_dpt_by_tier × 1.25. The slice pass lints this, so the R2 phase budgets stay valid.
- No reroll and no refund.

**Order of effects:** base → Level → Firmware (§5).

## 3. Placement & generation

- **Node type:** `WORKSHOP`, appended to `InfilNodeType` so saved ints survive. Heat: 0.
- **Count by target tier:**
  - T1: 0. T1 runs stay on the teaching path.
  - T2: exactly 1, at layers 3–5.
  - T3 and T4: 1 at layers 3–5, plus a second at layer 6.
- **Arithmetic:** the campaign's 8-run minimum path is T1 ×3, T2 ×3, T3 ×1 and a boss. That gives about (0×3 + 1×3 + 2×1) / 7 ≈ 0.7 per non-boss run and 1.7 per T3 run, and an average of about 1.2 per T2+ run (T2–T3 runs: 5 runs, 5 Workshops). The boss netrun is excluded.
- **Replaces** one Terminal slot (the ≈ 25 % share). Routers are untouched, so the combat count is unchanged.
- **Exclusions:**
  - Never in layer 1 or 7.
  - Never in the same layer as a Mainframe, which forces a route decision.
  - If no eligible target exists at generation, a Terminal is placed instead (target "empty" rate below 3 %).
- **Corporation weights** (`workshop_weight`, default 1.0): Solace 1.0, Meridian 1.2, Halcyon 0.8, Orbital 1.0, REBEL_CELL 0.6. Aurelian and Tethys default to 1.0. Weights bias placement only and never override the T2+ guarantee.
- **RNG:**
  - The `map` stream decides whether and where.
  - A new `workshop` stream, seeded as hash(run seed, node id), picks the offers on entry. The state is checkpointed in RunState, so reload can't reroll.
  - Abandoning the run discards the offers.
  - Selection weights eligible targets by lower Level first, drawn without replacement.

## 4. UX flow

1. **Route page:** a wrench sticker. The hover card reads "WORKSHOP: improve a slice or a card. One upgrade per visit." Heat shows 0.
2. **Enter:** a three-column offer page that reuses the Mainframe page kit, with an amber header.
3. **Each offer shows:** the target art, "Level I → II", the delta in plain numbers, the cost and the Cycles left, and a greyed "Need N more Cycles" if unaffordable. A slice with a changed sub-tick map shows it (R11).
4. **Preview:** hover draws the upgraded slice at its real wheel position with the landing tiers. A card shows its updated text. The preview equals the result, because it is the next `levels` entry.
5. **Commit:** a click selects, and CONFIRM pays.
6. **Cancel:** Esc or LEAVE before CONFIRM spends nothing. There is no undo after payment, consistent with the Mainframe.
7. **Leave:** the node is marked "USED".

**Text keys:** `workshop.name`, `.hover`, `.header`, `.offer.slice`, `.offer.card`, `.level_fmt`, `.cost_fmt`, `.need_more`, `.confirm`, `.leave`, `.used`, `.empty`, `.cap_run`, `.cap_layer`, `.installed`, `.fallback_slice`, `.license_bonus`.

## 5. Interactions

- **Heat:** the Workshop adds 0 Heat. The existing "shop stock −1" MINOR complication (set per netrun) also gives 1 fewer offer (`workshop_offers_minus_on_heat_minor`; minimum 2).
- **Raids:** none. The Workshop isn't a network node, so a raid can't DOWN it.
- **Daemons (examples, not ids, pending content):**
  - A discount Daemon: the first Workshop upgrade is −50 %.
  - A rule-breaking Daemon: 2 upgrades per visit on the same target, where the second leaves that slice CORRUPTED (R9, a 2× RAM cost) for the next combat.
- **Firmware:** a socketed Firmware is kept. The order is base → Level → Firmware, so the preview equals the resolve. If the sim shows runaway, make Level additive on base values.
- **Persistence:** upgrades persist on a surviving operative, like deck and Firmware (GDD 4.2), and die with a dead operative.
- **Campaign layer:** an optional **Workshop License** at HQ, a campaign unlock costing `workshop_license_cost` = 30 Schematics. It adds +1 offer (3 → 4) and −15 % cost, and the node is fully usable without it. This gives the Schematics a use without charging mid-run.
- **Other nodes:** it competes with the Mainframe for Cycles (intended). Terminal events may later grant a discount via N16.
- **Exploits:** none.
- **Tiers:** layer gating is independent of tier. Upgrades never raise ICE damage, and the dpt ceiling (§2) bounds the player side.

## 6. Data & systems

**New data:**
- `UpgradeOfferData`: `target_kind`, `level`, `cost_override`, `description_key`, `effects_delta`.
- `WorkshopConfigData` in `campaign_config.tres`: `offers_per_visit`, `buys_per_visit`, `offer_mix`, `cost_by_level`, `max_level_by_layer`, `run_upgrade_cap`, `dpt_ceiling`, `cycles_per_netrun_estimate`, `heat_minor_offer_penalty`, `license_cost`, `license_offer_bonus`, `license_discount_pct`.
- `InfilNodeType.WORKSHOP`.
- `SliceData.levels`, `CardData.levels`.
- `RunState`: `slice_levels` and `card_levels` keyed by instance id, `workshop_used`, `workshop_upgrades_this_run`, and the `workshop` stream state.
- Corporation `workshop_weight`.

**Systems:**
- N1: delta amounts are authored with `amount_mode` (FLAT or PERCENT).
- N2: the band validator lints upgraded values.
- N12: Levels I–III change amounts or riders only. Size and tick-map changes wait for N12.
- N18: hosts the Level IV flash row later. It is not required.
- N16: optional, for discount events.

**Fallback (data-only):** `generic_level` gives slice output +1 (FLAT) and a card −1 RAM (minimum 0). The order is base → Level → Firmware.

**Size:** the node, config, generation, UI and tests are **M**. Slice and card content are separate passes (M–L each). The License is **S**.

## 7. Examples

1. **Layer 4 Workshop, T2, Breaker, 95 Cycles.** Offers: Shim Level 0 → I for 25 (4 → 5 damage); Overflow 0 → I for 25 (10 → 12); a Spin 2 card 0 → I for 20 (Spin 3). The player buys the Overflow and has 70 left. A later layer-6 Workshop offers Level I → II for 45.
2. **Layer 6 Workshop, T3, a MINOR complication active, 160 Cycles.** Only 2 offers show. Defrag II → III costs 70 (block 12 → 16), and a Perfect-hook slice I → II costs 45. The player takes the 70 Defrag and has 90 left for the next Mainframe.
3. **License owned, T2, layer 3.** 4 offers show, at −15 %. A Level I slice costs 21 (25 × 0.85, rounded up). The layer-3 cap means no Level II is offered, even though the player has Level I items.

## 8. Risks & balance notes

- **Snowball:** 5 upgrades on one slice. Mitigations are one buy and one Level per visit, the run cap, layer gating, and the dpt ceiling of ×1.25. **Test:** "all on the best slice" against "spread" at the reference dpt [9, 11, 14, 18], with boss turns staying in 12–20.
- **Economy:** measure the Workshop's share of Cycles, target 35–45 %. If the Mainframe strictly dominates, nobody enters the Workshop.
- **Dominant slice:** Level deltas must be roughly equal per Cycle. Lint: ±20 % across slice types.
- **Firmware:** the multiplicative order may run away. The fallback is additive Levels.
- **Determinism:** test save, quit and reload mid-menu for the same offers.
- **Dead nodes:** target an empty Workshop rate below 3 %.
- **Persistence:** upgrades that persist across a campaign's runs may snowball. The sim must track a veteran's total.

## 9. Q:

- **Q:** Should T1 get a teaching Workshop (Level I only), or stay at 0 as in this draft?
- **Q:** Is the License better as +1 offer and −15 % (this draft), or as a built network node tying it to raids?
- **Q:** Is one buy per visit too tight, given that upgrades are the only permanent in-run growth?
- **Q:** Should Level IV stay Rack-flash only, or should layer-7 Workshops reach IV?
- **Q:** Is persistence on surviving operatives right, or should upgrades reset each netrun?
