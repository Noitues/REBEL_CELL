<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01LxQs8RvJGj9WzDuV2avpgt, custom_id node__heat_sink; status ok; tokens in 14063 cache-write 0 cache-read 32007 out 5871; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Heat Sink: design draft

Working frame: the existing **Proxy Relay** already gives −1 Heat per completed netrun, and GDD 4.1 has **Heat objective Sites** (one-shot, −5 Heat, used up). The Heat Sink must be distinct from both:
- It is **on-demand and capped**, not a passive trickle.
- It is a **raid target with a real cost when lost**, not a one-time Site.
- It trades Schematics for Heat at a visible rate, so the player can choose between offense and safety.

## 1. Purpose & the decision it creates

The Heat Sink is a claimable, buildable network node. It converts a stockpile of **Schematics** into **Heat reduction** at HQ, on demand, up to a per-node capacity that refills only by completing netruns. The player weighs three things:
- Buy a Firewall Relay or Vault now, or bank Schematics to "flush" Heat before a threshold (25 / 50 / 75) fires its raid?
- Defend the Sink with assets, or accept that it may go DOWN right when Heat is highest and the player needs it most?
- Flush early to stay COOL and keep elites rare, or push Heat for faster Exploit extraction and flush just before the next threshold?

Heat events fire only on the first crossing, but modifiers (elite frequency, +1 resistance, +25 % raid strength) apply while at or above the band. The Sink therefore pays most when it drops you back under a band, never when it merely shaves Heat inside a band.

## 2. Rules

**Node:** `heat_sink` (new `NetworkNodeType` HEAT_SINK, appended at the end of the enum so saved ints stay valid).

| Field | Value | Config key |
|---|---|---|
| install_cost | 30 Schematics | `heat_sink.install_cost` |
| integrity | 15 | `heat_sink.integrity` |
| repair_cost_ratio | 0.5 (like all nodes) | existing |
| asset_slots | 1 | existing |
| raid_priority | 1 (soft magnet, below Vault's 2) | existing field |
| triggers_raid | false | existing field |
| profile_unlock_required | false (core node, see Q1) | existing field |

**Charge model (the core rule):** each Sink holds `charge`, from 0 to `sink_capacity` = 8 Heat.
- Each **completed netrun** adds `sink_charge_per_netrun` = 3 charge to every UP Sink. Cap: 8.
- A **raid survived** (CELL HOLDS) with the Sink HOLDING adds `sink_charge_per_raid_held` = 2.
- **Flush** (an HQ action, free, any time between runs): spends charge for Heat at a 1:1 ratio, up to the current charge. The player chooses the amount. Charge is never lost except as below.
- A Sink that goes **DOWN** keeps its charge but cannot flush until repaired. If it is **TAKEN**, the charge is lost.

**Amount mode (R5):** the flush amount is FLAT Heat points (charge → Heat 1:1). Capacity and charge are FLAT. Reduction is never PERCENT of Heat, to avoid compounding at high Heat.

**Limits:**
- **One Sink per territory component** (a connected set of claimed nodes): `heat_sink.max_per_component` = 1.
- Campaign-wide: `heat_sink.max_total` = 2.
- **Diminishing returns on flushes:** total Heat flushed per campaign is soft-capped. Each flush beyond `sink_free_flush_total` = 20 Heat in the campaign costs +1 Schematic per Heat as a **launder fee** (`sink_launder_fee` = 1). Heat is sunk at the same rate, but the fee punishes using it as the main plan.
- **Bands:** flush output is clamped so Heat never falls below the floor of the band **below** the current one in a single flush (`sink_max_drop` = 8). It cannot drop you from HUNTED to COOL in one action. That prevents resetting out of a raid wave.
- **Heat threshold events** never re-fire (GDD 4.3), so flushing under a threshold and crossing it again gives **no second raid**. Modifiers do switch off while under the threshold. This is the Sink's actual value.

**Why charge instead of a plain per-netrun trickle:** the Proxy Relay already does the trickle at −1. A buffered, player-timed flush creates the timing decision and the bank-and-protect tension.

**Distinct from the Heat objective Site (GDD 4.1):** the objective is −5 once, costs a netrun, and gives no standing infrastructure. The Sink is infrastructure that rewards netruns you were doing anyway. Its numbers must stay below the objective Site per unit of player time (see §8).

## 3. Placement & generation

- **Built by the player** on a claimed Site (like Relay / Safehouse), plus an occasional **found** instance as a reward.
- **Found:** the Heat objective Site (GDD 4.1), when cleared, offers **claim as a free Heat Sink** instead of a normal claim. This ties the two designs together. A claimed objective Site starts at charge 4.
- **Build gate:** the Sink requires Heat ≥ 25 (`heat_sink.min_heat_to_build` = 25). Below that it is wasted spend, and the gate stops a T1 opening build.
- **No new RNG stream:** placement is deterministic from player choice. For the found-Sink offer, the existing `campaign` stream is read **only** when the Site is generated (not at claim time), so saved streams do not shift.
- **Corporation weights:** the story paths do not change. A corporation may carry a modifier that raises `sink_charge_per_netrun` by 1 in its district (Halcyon "smart-city scrubbers"; flavor only). It is data-only and optional, so skip it in the first pass.
- **Exclusions:**
  - Not buildable on the home server's internal nodes.
  - Not adjacent to another Sink (see max per component).
  - Not placeable on a TAKEN or DOWN Site.

## 4. UX flow

1. **Build:** the HQ node-install list shows Heat Sink greyed until Heat ≥ 25, with the reason ("Needs Heat 25+"). The install card lists cost 30, integrity 15, capacity 8, +3 per netrun, +2 per raid held.
2. **Charge display:** a small gauge on the node in the City Grid (8 pips). A ghost pip marks the next netrun's +3. The DOWN white bolt (GDD 9.3) overrides the gauge.
3. **Flush:** select the Sink → an amount stepper (0 to charge, clamped by `sink_max_drop`). The preview shows:
   - Heat now → Heat after;
   - band change, e.g. "FLAGGED → NOTICED";
   - which modifiers switch off ("Raid strength +25 % off", "All enemies +1 resistance off");
   - the launder fee in Schematics once past the free pool;
   - which threshold events have already fired and so will NOT fire again.
4. **Confirm / cancel:** Confirm commits. Cancel before commit changes nothing. After commit there is no undo (a campaign-layer action). The preview equals the result because it is pure arithmetic on stored numbers.
5. **Raid setup:** the Sink is flagged as a "value target" like the Vault, with a lock/shield icon when an asset is slotted.
6. **Text keys:** `node.heat_sink.name`, `.desc`, `.build_gate`, `.flush_title`, `.flush_preview_band`, `.flush_modifiers_off`, `.flush_launder_fee`, `.flush_clamped`, `.down_charge_kept`, `.taken_charge_lost`, `ui.gauge.charge`.

## 5. Interactions

- **Heat bands:** the best use is to drop back **under** 25, 50 or 75 right after a netrun pushes you over, shedding the ongoing modifier. NOTICED → COOL stops elite frequency. FLAGGED → NOTICED removes +1 resistance. HUNTED → FLAGGED removes +25 % raid strength before the next raid. PURGE at 100 is not preventable by the Sink (Q3).
- **Raids:** the Sink is a raid target at `raid_priority` 1. A raid that downs it makes the player pay 50 % of 30 = 15 Schematics to repair. This is the main "defend vs offense" tax. The Sink HOLDING after a raid also gives +2 charge, a small reward for defense.
- **Proxy Relay:** they stack, but the Relay's −1 is passive and tiny. A Sink next to a Proxy Relay gets an **adjacency bonus**: +1 charge per netrun (`adjacency_bonuses`, partner_type = PROXY_RELAY). That is a cheap reason to cluster them, and it makes the cluster a juicy raid target.
- **Firewall Relay adjacency:** none; a Firewall protects by its built-in turret, not by a bonus, so protecting the Sink costs real asset slots.
- **Vault Terminal:** the Vault triggers a raid when built. Players who build both should expect a double target. The Sink does not trigger a raid itself.
- **Daemons:**
  - Clean Signal, Cold Exit and Scrubber reduce Heat inside netruns. They interact only through arithmetic and need no code.
  - A future Daemon "Heat Bank" could add +1 charge on a Perfect streak. It is not required.
- **Stationing:** a stationed operative on a Sink node (Safehouse-style) is not supported. The Sink has no station slots. A Ghost-class station bonus ("threats delayed 1 step") may still apply via asset slots.
- **Exploits:** an Exploit extraction at Heat ≥ 50 triggers a RETALIATION raid (GDD 4.4). The Sink lets the player flush **before** extracting, below 50, so the retaliation does not fire. This is the headline combo and the primary reason to hold charge.
- **Tiers / ICE:** `sink_capacity` and the per-netrun charge are tier-independent (R2 spirit). ICE levels that raise Heat gain (`HEAT_GAIN_PCT`) make the Sink more valuable. An ICE rule `HEAT_SINK_PCT` already exists in `RuleModifierType` and scales sinks (Heat reduction sources). Check whether it already scales Proxy Relay and Scrubber; if so, the Sink flush multiplies by it too.

## 6. Data & systems

- **New `NetworkNodeData` fields:** `sink_capacity: int`, `sink_charge_per_netrun: int`, `sink_charge_per_raid_held: int`, `sink_max_drop: int`. Alternatively, use `passive_effects` with a new effect type (see below).
- **New effect type:** `GAIN_SINK_CHARGE`, target CAMPAIGN, used by `ON_NETRUN_COMPLETE` and `ON_RAID_END` passives. NEW: no N# fits. It is data-only if charge lives in a plain dictionary on the campaign state.
- **New enum value:** `NetworkNodeType.HEAT_SINK`, appended at the end.
- **Campaign state:** `sink_charge: Dictionary` (node id → int), plus `heat_flushed_total: int`. This is a **save version bump** (additive, with a default for old saves); the designer has already ruled to drop old campaign saves (D3), so there is no migration cost.
- **Config (`campaign_config.tres`):** `heat_sink_min_heat_to_build`, `sink_free_flush_total`, `sink_launder_fee`, `heat_sink_max_per_component`, `heat_sink_max_total`.
- **Flush action:** a `CampaignRules.flush_heat_sink(node_id, amount)` function with a pure preview twin `preview_flush`, to guarantee preview = result.
- **ON_RAID_END trigger:** may not exist. `Trigger` has ON_RAID_START only. Add `ON_RAID_END` (size S), or do the raid-held bonus directly in the raid resolver. The latter is the data-only fallback and recommended.
- **UI:** an install card entry, a gauge on the node glyph, a flush panel. A new asset for the Grid glyph (an art request).
- **Sizes:** the data node + config is S. Charge state + flush logic + preview is M. UI (gauge + flush panel) is M. Total: **M**. It depends on no N-system. It relies on the Grid layer's existing node and raid code.

## 7. Examples

**A. The retaliation dodge.** Heat 52 (FLAGGED), charge 8, free flush pool unused. The player is about to extract an Exploit; at Heat ≥ 50 that provokes a RETALIATION raid. Flush 3: Heat 49 (NOTICED), "All enemies +1 resistance" off, no fee. Extract, Heat rises by the netrun's own gain, and the raid risk has been dodged. Cost: 3 of the 8 stored charge, regenerable in one netrun.

**B. The panic flush, clamped.** Heat 88 (HUNTED), charge 8. The player wants Heat 80. `sink_max_drop` = 8 would allow it, but the band floor rule says a flush may not cross out of the current band's *lower neighbour*. A drop to 79 would leave HUNTED, which is allowed, but 79 to 74 would not. The preview reads: "Flush 8 → Heat 80 (HUNTED). 5 more would reach 75: FLAGGED. Clamped at 8." Raid strength +25 % stays on until Heat ≤ 74, so the player must pair this with a Proxy Relay or a Heat objective Site. The Sink alone cannot undo a bad streak.

**C. The tax.** The player has flushed 20 Heat across the campaign. At Heat 40 with charge 6, the preview says: "Flush 5 → Heat 35. Launder fee: 5 Schematics." The same 5 Heat via the objective Site would cost one netrun. The player picks by tempo: Schematics now, or a run later.

## 8. Risks & balance notes

- **Degenerate: infinite Heat laundering** (push Heat, flush back, repeat). Mitigations: the capacity cap of 8, the charge refilling only through netruns, the launder fee after 20 Heat, and a max of 2 Sinks. At 3 charge per netrun, one Sink absorbs roughly 3 Heat per run. A typical run gains about 4–9 Heat (T1–T4 objective runs at Heat ≈ 70 before the boss, per 4.1). A Sink offsets about a third to a half, never all of it. Check that the 8-run minimum path still ends near Heat ≈ 70 only with a Sink flush at the right moments, otherwise it is too strong. Sim target: campaign Heat at the boss falls from ~70 to about 50–60 with one Sink used well.
- **Always-build trivial choice:** if 30 Schematics is always right, the decision dies. Check the Schematic sink order: the R4 raid ultimatum is the designer's intended Schematics sink, so the Sink must lose to Firewall Relay or Vault in at least some mid-campaign states.
- **Overlap with Proxy Relay (25 Schematics, −1 per run, passive).** The Sink must not make the Relay obsolete. The Relay is cheaper and unlock-gated, while the Sink is better at timed use. If sims show the Relay is never built, drop the Sink's per-netrun charge to 2.
- **Too safe at low Heat:** the build gate Heat ≥ 25 prevents a pointless T1 build.
- **Raid target fragility:** at 15 integrity and priority 1 it might never be attacked, which removes the defend decision. Sim: how often is the Sink the first node downed? Target 15–30 % of raids.
- **Charge lost on TAKEN:** harsh but fair. Test whether players feel cheated. If so, keep half.
- **Sim metrics to add:** Heat at the boss, flush count, charge at flush, share of Sinks DOWN, Schematics spent on Sink vs alternatives, retaliation raids avoided.

## 9. Open questions

Q: Is the Sink a profile-unlocked node (like Proxy Relay and Vault) or core from campaign start? Recommend core, with the Heat ≥ 25 build gate doing the gating.
Q: Should the objective Site's "claim as Heat Sink" conversion exist, or should the Sink be build-only to keep the two designs separate?
Q: Should PURGE (Heat 100) be flushable below 100 to avert it, or is PURGE the one threshold the Sink can never stop? Recommend uninterruptible.
Q: Does `HEAT_SINK_PCT` from ICE levels already scale node-based Heat reduction, or only Daemons and objective Sites? This determines whether the flush must multiply by it.
Q: Is the launder fee (1 Schematic per Heat beyond 20) the right brake, or should the brake be a hard campaign cap with no fee?
