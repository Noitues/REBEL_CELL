<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01LxQs8RvJGj9WzDuV2avpgt, custom_id node__workshop; status ok; tokens in 13992 cache-write 0 cache-read 32007 out 6007; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# WORKSHOP: design draft

## 1. Purpose & the decision it creates

The Workshop is the netrun's **spend-to-improve** node: the player pays Cycles to make something they already own permanently better for the rest of the run. The Shop sells new things. The Workshop improves existing things. Each visit asks one question: **"Which one thing do I already trust enough to invest in?"** A slice upgrade makes a wheel position more reliable or powerful, so it favours a steady wheel. A card upgrade makes a single deck line better, so it favours a build engine. The player weighs a certain, permanent gain now against saving Cycles for the next Mainframe, and against which of the 2–3 shown offers fits their wheel and deck. The node hosts either upgrade kind. Slice and card upgrades are separate design passes, so this draft defines the **node, offers, costs and limits** and leaves "what each Level does" to those passes. Their content plugs in through an `UpgradeOfferData` row.

## 2. Rules

**Inputs:** one upgradable target (slice or card) and Cycles. Optionally a Schematic-funded "Workshop License" at HQ (see §5).

**Output:** the target gains +1 Level, up to Level IV. Level 0 is the base item. A Level is defined by the target's own `levels` array (authored by the slice/card pass). Level IV is the cap for now, because "I, II, III, IV…" is open-ended and the cap is only a config value.

**One visit offers exactly 3 upgrade offers** (`workshop_offers_per_visit` = 3), picked deterministically from the player's eligible targets, and the player may buy **at most 1** (`workshop_buys_per_visit` = 1). Why: one purchase keeps each visit a decision, and a 3-offer menu means no screen of "upgrade everything".

**Offer mix (FLAT rule, no randomness inside the offer):** 2 slices + 1 card by default (`workshop_offer_mix` = {slice: 2, card: 1}). While the card-upgrade pass is unbuilt, the card slot is filled with a third slice offer (data-only fallback, see §6). If the player has no eligible target of a kind, that slot is filled from the other kind. If both are empty the node shows "NOTHING TO IMPROVE" and refunds nothing, because nothing was spent.

**Cost** (Cycles, `workshop_cost_by_level`):

| Upgrade to | Slice | Card |
|---|---|---|
| Level I | 40 | 30 |
| Level II | 70 | 55 |
| Level III | 110 | 85 |
| Level IV | 160 | 120 |

- Cost is a **FLAT** amount and is not tier-scaled. The tier already scales how many Cycles the player earns.
- A Daemon or Heat modifier changes cost through the existing `CYCLE_PRICE_PCT` rule modifier, which is a PERCENT amount of the listed price, rounded up.
- **Schematics are not spent at the node.** Schematics are a campaign currency; a netrun node that spends them would make a death during the run feel doubly punishing. Schematics enter only as the HQ unlock (§5).

**Limits:**
- Level gating by node depth: the Workshop can offer at most Level `workshop_max_level_by_layer`: layers 1–3 → I, 4–5 → up to II, 6–7 → up to III. Level IV comes only from the layer-7 Server Rack reward flash (G15 "flash", an N18 row), not the Workshop. This stops a deck stacking Level IV by layer 4.
- A target can be upgraded **one Level per visit** even across multiple Workshops (it can't skip from I to III).
- Per run cap: `workshop_run_upgrade_cap` = 6 total upgrades from Workshops.
- **Reroll:** none. Determinism and the preview rule already make the offers visible, and a paid reroll invites a Cycle sink exploit.
- **Downgrade/refund:** none. An upgrade is permanent for the run; the Shop already sells removal.

## 3. Placement & generation

- **New node type** `WORKSHOP` in `InfilNodeType` (append to the enum, so saved ints survive). Display "Workshop". Heat: 0.
- **Count:** 0–1 per netrun at layers 3–5 in the normal case (GDD 4.2 already guarantees a Mainframe there), plus an optional second at layer 6 only on T3+ targets. Target: **~0.9 per run**. A campaign of ~8 runs gives ~7 visits. That is enough for the economy to matter without a standing upgrade ritual.
- **Guarantee:** a netrun on T2+ gets at least one Workshop somewhere in layers 3–6. T1 netruns get none by default. That keeps the first runs on the teach path (Shop, Events, combat) and avoids overloading the tutorial.
- **Exclusions:** never in layer 1 (all Routers) and never as the final layer. Never adjacent in the same layer to a Mainframe, so a layer doesn't offer both "buy" and "improve" with the same Cycles. This forces a route decision.
- **Replaces** one slot of the Terminal share (the ≈25 % of remaining nodes), not Routers, so combat count (about 5 combats, ~15 minutes) is unchanged.
- **Weights by corporation:** a per-corporation `workshop_weight` in the site/corp data (default 1.0). Solace 1.0, Meridian 1.2 (logistics, fitting a refit theme), Halcyon 0.8, Orbital 1.0, REBEL_CELL 0.6 (it mirrors your build, so it's stingy). Weights only bias the generation roll and never override the guarantee.
- **RNG stream:** the existing `map` stream decides *whether and where* (at map generation). A new named stream `workshop` decides *which targets are offered*, seeded per node and checkpointed in RunState like the other streams. The offers are generated **when the node is entered**, from the stream's saved state, so quitting and reloading cannot reroll them. Selection rule: weight eligible targets by lower Level first (so a "fresh" target is more likely than a near-capped one), draw without replacement.

## 4. UX flow

1. **Approach on the route page:** a distinct wrench-and-sparks sticker. The hover card reads "WORKSHOP: improve a slice or a card. One upgrade per visit." The Heat chip shows 0.
2. **Enter:** a three-column offer page reusing the Shop's page kit (the Mainframe layout) so there is no new framework, but with a different header and colour (amber, not the Shop's green) so the nodes read differently at a glance.
3. **Each offer card shows:**
   - Target name and the art (the slice wedge or card face).
   - **Before → after** side by side, for example `Level I → II`.
   - The delta in plain numbers (damage 6 → 8, cost 2 → 1 RAM). For a slice, the **sub-tick map** is shown (R11) if the upgrade changes it.
   - The Cycle cost and the Cycles you will have left.
   - A greyed reason if unaffordable ("Need 22 more Cycles").
4. **Preview:** hovering an offer shows the new slice **on the wheel at its real position** with the landing tiers drawn. For a card, it shows the updated text and a "previously played in this combat" note if any. The preview equals the result. The upgraded data is just the next entry of the target's `levels` array.
5. **Commit:** a click selects the offer, and a second CONFIRM press pays. The two steps prevent a mis-click on a 100-Cycle purchase.
6. **Cancel/undo:** Esc or LEAVE any time before CONFIRM spends nothing. After CONFIRM the node closes its menu with a short "installed" beat. There is **no undo after payment** (consistent with the Shop). Because nothing is random, nothing needs a checkpoint beyond the stream state saved on entry.
7. **Leave:** the node is marked used. Re-entering it shows "USED" and no menu.

**Text keys needed:** `workshop.name`, `workshop.hover`, `workshop.header`, `workshop.offer.slice`, `workshop.offer.card`, `workshop.level_fmt` ("Level %s → %s"), `workshop.cost_fmt`, `workshop.need_more`, `workshop.confirm`, `workshop.leave`, `workshop.used`, `workshop.empty`, `workshop.cap_run`, `workshop.cap_layer`, `workshop.installed`, `workshop.fallback_slice`.

## 5. Interactions

- **Heat:** the Workshop adds 0 Heat (it is not a fight). The existing "shop stock −1" MINOR complication also applies: **the Workshop shows 2 offers instead of 3** while that complication is active (`workshop_offers_minus_on_heat_minor`). Heat NOTICED+ already raises Cycle prices through `CYCLE_PRICE_PCT`, which here is a normal PERCENT cost modifier.
- **Raids:** none directly. A mid-run raid does not close the node. A Workshop is not a network node, so no raid can DOWN it.
- **Daemons:**
  - A "Machinist" Daemon: the first Workshop upgrade each run costs −50 %.
  - Rule-breaking: "Overclock Bench": one upgrade per visit becomes two, but both go on the same target and the second becomes CORRUPTED for the next combat.
  - Cost modifiers stack by the existing modifier rules and round up.
- **Firmware:** a slice's Firmware socket **is kept on upgrade**. The Level applies to the slice's base values, and Firmware multiplies on top, in the order slice → Level → Firmware. This must be defined so "Patch+" plus "Level II" behaves identically in the preview and the resolve. A Level never overwrites a socketed Firmware.
- **Other nodes:** it competes with the Mainframe for Cycles (intended). Terminal events may later grant a free upgrade or a discount through N16's run-level `next_combat_overrides` style flag (`workshop_discount_next`).
- **Exploits:** none. Optional idea, not required: the Exploit Site's final Rack could award a coupon, but that belongs to the N18 reward table.
- **Tiers:** the layer gating (§2) is independent of the target tier, but T3+ unlocks the optional second Workshop. Enemy scaling is untouched, so upgrades **do not raise ICE damage**. The sim must check that upgrades don't beat the R2 reference damage by too much (see §8).
- **Campaign layer (the Schematic hook):** Workshop use is gated by a campaign-level unlock: the **Workshop License** at HQ (cost 30 Schematics, a profile-style unlock, `profile_unlock_required = true`, matching Compiler Rack and Vault Terminal). Without it, the node can still appear but is "LOCKED: needs a License" and the player can only look. That makes Schematics meaningful without charging them mid-run. An alternative that adds a node type is mentioned in Q1.

## 6. Data & systems

**New data:**
- `UpgradeOfferData` (resource, on the target): `target_kind` (SLICE/CARD), `level` (int), `cost_override` (optional), `description_key`, `effects_delta` (the slice/card pass fills this).
- `WorkshopConfigData` in `campaign_config.tres`: `offers_per_visit`, `buys_per_visit`, `offer_mix`, `cost_by_level` (4 entries each for slice and card), `max_level_by_layer`, `run_upgrade_cap`, `heat_minor_offer_penalty`, `license_cost`.
- `InfilNodeType.WORKSHOP` appended.
- `SliceData.levels` and `CardData.levels` (Array of `UpgradeOfferData`), and `RunState.slice_levels` / `card_levels` dictionaries keyed by the instance id.
- `RunState.workshop_used`, `workshop_upgrades_this_run`, and the `workshop` RNG stream state.
- Corporation `workshop_weight` float.

**Systems:**
- N18 (data-driven rewards) can host Workshop as a reward row later but isn't required.
- N2's band validator should lint upgraded values against class bands in the same pass as the slice-upgrade pass.
- N12 (variable slice sizes) interacts only if an upgrade changes `size_ticks` or the tick map. Avoid it in the first Workshop pass: **Levels I–III change amounts or riders only**, and size/tick-quality changes wait for N12.
- N1 (amount modes): upgrade deltas should be authored as FLAT or PERCENT (`amount_mode`) so they can read "+25 % block" or "+2 damage" without a new status type.
- No dependency on N5–N10.

**Fallbacks (data-only):** until the slice and card passes exist, ship the node with a **placeholder generic upgrade**: `generic_level` = +1 Level that gives +25 % output (FLAT +1 for the smallest amounts, minimum +1) on the slice, or −1 RAM cost (min 0) on the card. It uses the existing Patch+ rule (+50 %) scaled down, so no new rules are needed.

**Size estimate:** the node, config, offer generation, UI and tests are **M**. The slice and card content is a separate pass (**M–L** each). The License unlock is **S**.

## 7. Examples

1. **Layer 4 Workshop, Breaker, 95 Cycles, no Daemons.** Offers: (a) Shim slice Level 0 → I, 40 Cycles, 4 → 5 damage; (b) Overflow slice Level 0 → I, 40, 10 → 12 damage; (c) a card "Spin 2" Level 0 → I, 30, now Spin 3. The player buys the Overflow (leaves 55). A later Workshop offers Level I → II for 70 and they must choose between that and a Shop trip.

2. **Layer 6 Workshop, T3 target, Heat 30 (MINOR complication active), 160 Cycles.** The node shows 2 offers. Offers: Defrag (Level II → III) at 110, block 12 → 16; Perfect-hook slice (Level I → II) at 70. They have 160. The best Cycle value is the cheap one, leaving 90 for the layer-7 Rack's shop-adjacent path. Quote: "Heat made it a 2-choice menu, so I picked a line instead of a menu."

3. **Locked case, Rigger without License.** The player enters, sees 3 greyed offers and "LOCKED: Workshop License at HQ (30 Schematics)". They can read the deltas and plan, but not buy. After the next HQ visit, they buy the License and every Workshop in later netruns is live. This is a deliberate nudge: the first Workshop teaches, the second pays.

## 8. Risks & balance notes

- **Snowball:** stacking 6 upgrades on one slice could make a wheel that trivialises R2 phase budgets. Mitigations: one buy per visit, one Level per visit per target, the run cap, and layer gating on Level. **Test:** a sim policy "all upgrades on the best slice" vs "spread" against the reference dpt [9, 11, 14, 18]; the boss turn count must stay in 12–20.
- **Economy:** the total Cycles over a run vs the Workshop and the Shop. If the Shop is strictly better, nobody enters the Workshop. Measure the share of Cycles spent on each node. A target of 30–45 % Workshop spend is healthy.
- **Dominant slice:** a slice that scales best with Level (an Overflow ×4 Perfect) would always win. The slice pass must keep Level deltas roughly equal in value per Cycle. Lint: the `levels` delta value per Cost is within ±20 % across slice types.
- **Firmware interaction:** Patch+ and a Level both multiplying is a risk. The order (Level, then Firmware) is multiplicative. If the sim shows a runaway, make Level additive on base values.
- **Determinism:** the offers come from the `workshop` stream and are saved on entry. Test: save, quit, reload mid-menu gives the same three offers, and rewind in combat is unaffected.
- **Dead nodes:** if the player has nothing eligible (everything at the layer cap), the node is a wasted route choice. The map generator could check that and swap in a Terminal. Test the frequency of "empty" Workshops, target below 3 %.
- **Heat penalty:** "2 offers" is a mild penalty and may feel invisible; track whether players avoid it.
- **Aurelian and Tethys:** their corporation weights are unset (default 1.0).

**Q:**
- **Q1:** License as a Schematics sink (my choice) or a built network node (a "Machine Shop" near your territory that sets the netrun's Workshop count), tying it to the campaign layer and to raids?
- **Q2:** Should the card slot be on by default, or should the first release be slice-only (card slot empty) until the card pass lands?
- **Q3:** Is Level IV exclusive to Rack "flash" (my choice), or should the Workshop reach IV at layer 7?
- **Q4:** Is one buy per visit too tight when upgrades are the only permanent in-run growth? Would two buys at 1.5× cost be better?
- **Q5:** Should upgrades persist on an operative who survives and returns to HQ, as deck and Firmware do (GDD 4.2 "keeping deck, Firmware and Daemons"), or reset per netrun?
