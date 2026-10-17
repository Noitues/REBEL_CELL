<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__nodes__heat_sink; status ok; tokens in 8681 cache-write 0 cache-read 32585 out 5311; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, premise vs extraction check):** fixed. §2 now defines the retaliation check as reading Heat at Rack capture (GDD 4.4 does not say when, so this is a stated assumption; see Q1). Because flushes are HQ-only, the player must flush before JACK IN so that **pre-run Heat + the run's Heat gain up to capture ≤ 49**. New `preview_extraction_guard` shows "projected Heat at capture" using the run's known Heat gain (netrun tier base + node-type Heat per GDD 4.2). Example A is rewritten with the full arithmetic. In-run flush is not added (no scope); it stays a Q.
- **Issue 2 (BLOCKER, clamp):** replaced the two clamps with one rule: a flush is limited by `sink_max_drop` = 8, and the result may not fall below the floor of the band directly under the current one (so at most one band down). Precedence: the lower limit wins. Example B is redone with correct arithmetic.
- **Issue 3 (MAJOR, dead launder brake):** `sink_free_flush_total` 20 → 12. Example C is recomputed.
- **Issue 4 (MAJOR, numbers):** §8 now says 70 Heat over 8 runs ≈ 9 per run and one Sink offsets ≈ 3 (a third). The sim target is justified with arithmetic.
- **Issue 5 (MAJOR, invented systems):** `ON_RAID_END` dropped. The raid-held bonus is resolver-direct. Charge is a plain dictionary, tagged "NEW: Sink charge state (S–M)". `adjacency_bonuses`, `partner_type`, `raid_priority`, `triggers_raid` and `profile_unlock_required` are marked "verify exists, else add to NetworkNodeData". The `HEAT_SINK_PCT` rule is resolved: the flush does not multiply by it, and it stays a Q for the designer.
- **Issue 6 (MAJOR, found-Sink conversion):** removed. Objective Sites stay used up per GDD 4.1. The Sink is build-only. D4 confirms it is a grid-view node.
- **Issue 7 (NIT):** the RNG hand-wave is dropped. The Sink uses no RNG.
- **Issue 8 (NIT):** PURGE is stated once: flushes cannot take Heat out of the PURGE band (Heat 100 is not flushable below 100), and it is no longer a Q.
- **Kept:** charge-and-flush timing; the pure `preview_flush` twin; the list of modifiers switching off and threshold events not re-firing; the sim metrics list.

# Heat Sink: design draft (v2)

## 1. Purpose & the decision it creates

The Heat Sink is a buildable grid-view network node, not a netrun node (D4). It stores **charge** and turns charge into **Heat reduction** at HQ, on demand. Unlike the Proxy Relay (a passive −1 per netrun) and the Heat objective Site (one netrun, −5, used up), it is infrastructure with a timing choice and a raid risk. The player weighs:
- 30 Schematics on a Sink, or on a Firewall Relay or Vault?
- Flush now, or bank charge for a specific moment?
- Defend the Sink, or let it go DOWN and pay the repair?

It pays most when it drops Heat **under a band line** (25 / 50 / 75), switching off that band's ongoing modifier, or when it keeps Heat ≤ 49 through an Exploit Rack capture (§2). Shaving Heat inside a band does little. One-time threshold events never re-fire (GDD 4.3), so flushing never buys a second raid.

## 2. Rules

**Node:** `NetworkNodeType.HEAT_SINK`, appended at the end of the enum so saved ints stay valid.

| Field | Value | Config key |
|---|---|---|
| install_cost | 30 Schematics | `heat_sink.install_cost` |
| integrity | 15 | `heat_sink.integrity` |
| repair | 50 % of install cost (GDD 3.3) = 15 | existing rule |
| asset_slots | 1 | verify exists, else add |
| raid_priority | 1 (below Vault) | verify exists, else add |
| triggers_raid | false | verify exists, else add |
| profile unlock | none (core node) | verify exists, else add |

**Charge:** each Sink holds `charge`, 0 to `sink_capacity` = 8 (FLAT).
- Each **completed netrun** adds `sink_charge_per_netrun` = 3 to every UP Sink.
- A raid that ends CELL HOLDS with the Sink HOLDING adds `sink_charge_per_raid_held` = 2. The raid resolver applies this directly.
- DOWN: charge is kept, flush is disabled until repaired. TAKEN: charge is lost.

**Flush** (HQ only, between runs, free in Schematics up to the free pool): spends charge 1:1 for Heat reduction. The amount is FLAT, never PERCENT of Heat (R5; avoids compounding at high Heat).

**Single clamp rule:** a flush reduces Heat by at most `sink_max_drop` = 8, **and** the resulting Heat may not fall below the floor of the band directly under the current band. If the two disagree, the lower limit wins, whichever stops the flush first. Band floors: 0 / 25 / 50 / 75. Heat in PURGE (100) cannot be flushed.

**Launder fee:** the first `sink_free_flush_total` = 12 Heat flushed in the campaign is free. Beyond that, each Heat costs `sink_launder_fee` = 1 Schematic.

**Extraction guard (the headline combo):**
- Assumption: the Exploit retaliation check (GDD 4.4, "Exploit extracted at Heat ≥ 50") reads Heat **at Rack capture**, and the run's own Heat gain before capture counts (Q1).
- Heat gain before capture = tier Heat per node type crossed (GDD 4.2) + Rack Heat (GDD 11.5 table). The route is fixed once chosen, so a **projected Heat at capture** can be computed.
- `preview_extraction_guard(site, route)` shows it. The player dodges retaliation only if pre-run Heat − flush + projected run gain ≤ 49.

**Limits:** `heat_sink.max_per_component` = 1 (one per connected territory); `heat_sink.max_total` = 2.

## 3. Placement & generation

- **Build-only** on a claimed Site, using the standard HQ install flow. No found or converted Sinks.
- **Build gate:** Heat ≥ `heat_sink.min_heat_to_build` = 25, so there is no pointless T1 build.
- **RNG:** none. Placement is player choice and charge changes are arithmetic; no named stream is read.
- **Corporation weights:** none in the first pass.
- **Exclusions:** not on home-server internal nodes; not on TAKEN or DOWN Sites; not adjacent to another Sink.

## 4. UX flow

1. **Install list:** Heat Sink is greyed with "Needs Heat 25+" until the gate is met. The card shows cost 30, integrity 15, capacity 8, +3 per netrun, +2 per raid held.
2. **Gauge:** 8 pips on the node glyph in the City Grid, with a ghost pip for the next netrun's +3. The DOWN white bolt (GDD 9.3) overrides it.
3. **Flush panel** (select the Sink): an amount stepper from 0 to min(charge, clamp). The preview shows:
   - Heat now → after, and the band change ("FLAGGED → NOTICED");
   - the modifiers that switch off ("Raid strength +25 % off");
   - the launder fee in Schematics;
   - the threshold events already fired, which do not re-fire;
   - **Projected Heat at capture** for the currently selected Site (the guard line), marked "≤ 49: no retaliation" or "≥ 50: retaliation".
4. **Confirm / cancel:** cancel changes nothing. After confirm there is no undo (campaign-layer action). The preview equals the result because it is pure arithmetic on stored numbers (`preview_flush`).
5. **Raid setup:** the Sink is marked as a value target, with a slot icon when an asset is installed.
6. **Text keys:** `node.heat_sink.name`, `.desc`, `.build_gate`, `.flush_title`, `.flush_preview_band`, `.flush_modifiers_off`, `.flush_launder_fee`, `.flush_clamped`, `.guard_projected`, `.guard_safe`, `.guard_retaliation`, `.down_charge_kept`, `.taken_charge_lost`, `ui.gauge.charge`.

## 5. Interactions

- **Heat bands:** use it to drop back under a band line right after a run pushes you over. NOTICED → COOL stops elite frequency; FLAGGED → NOTICED drops +1 resistance; HUNTED → FLAGGED drops raid strength +25 %. PURGE is unflushable.
- **Raids:** the Sink is a target at priority 1. If it goes DOWN, repair is 15 Schematics. If it holds, +2 charge.
- **Proxy Relay:** they stack. An adjacency bonus of +1 charge per netrun (verify the adjacency data exists, else add) rewards clustering and makes the cluster a bigger target.
- **Vault Terminal:** the Vault triggers a raid when built; the Sink does not.
- **Daemons:** Clean Signal, Cold Exit and Scrubber reduce Heat in netruns and interact only through arithmetic.
- **Exploits:** the extraction guard above is the main combo. It matters most for Exploit Sites at Heat ≥ 50.
- **Tiers / ICE:** capacity and charge are tier-independent (R2). `HEAT_GAIN_PCT` raises the projected gain, so the guard preview already includes it. `HEAT_SINK_PCT` does **not** scale the flush (ruling for v2; see Q3).

## 6. Data & systems

- **NetworkNodeData:** `sink_capacity`, `sink_charge_per_netrun`, `sink_charge_per_raid_held`, `sink_max_drop` (or config keys).
- **NEW: Sink charge state (S–M):** `sink_charge: Dictionary` (node id → int) and `heat_flushed_total: int` on campaign state. No new effect type and no `ON_RAID_END`; the raid resolver adds the held bonus directly. The save bump is additive, and D3 drops old saves anyway.
- **Config (`campaign_config.tres`):** `heat_sink_min_heat_to_build`, `sink_free_flush_total` (12), `sink_launder_fee`, `heat_sink_max_per_component`, `heat_sink_max_total`.
- **Functions:** `CampaignRules.flush_heat_sink(node_id, amount)`, with pure twins `preview_flush` and `preview_extraction_guard`.
- **UI:** an install card, the gauge, the flush panel, and one new Grid glyph (art request).
- **Size:** **M** total. No N-system dependency; it uses the existing node and raid code. Data-only fallback: none needed.

## 7. Examples

**A. The retaliation dodge.** Heat 52, charge 8, an Exploit Site. The projected run gain up to capture is +6 (placeholder: 5 route nodes ≈ +1 Elite, Rack +5). Target: 52 − flush + 6 ≤ 49 → flush ≥ 9. The clamp gives at most 8 (and FLAGGED's lower neighbor floor is 25, no issue). The preview says "Projected Heat at capture 50: retaliation". The player instead flushes 8 → 44, projected 50, still retaliation, and so must also take a Heat objective Site first. A different case: at Heat 47, flush 4 → 43, projected 49: **safe**. The player learns the guard is a planning tool, not a free pass.

**B. The clamped panic flush.** Heat 88 (HUNTED), charge 8, fee-free pool left 12. The 8 limit gives 80; the band-floor limit allows down to 75. The lower limit (more drop-limiting) is 8, so the result is Heat 80, still HUNTED, +25 % raid strength on. The preview says "Clamped at 8. 6 more would reach 74 (FLAGGED)". After the next run's +3 charge, a further flush of up to 3 gets to 77; Heat must drop 3 more via Daemons or a Proxy Relay. The Sink alone cannot undo a bad streak.

**C. The tax.** 12 Heat flushed so far. At Heat 40 with charge 6, flushing 5 gives Heat 35 and a launder fee of 5 Schematics (all 5 are beyond the free pool). The same −5 from a Heat objective Site costs one netrun. The player picks Schematics now or a run later.

## 8. Risks & balance notes

- **Laundering:** capacity 8, charge via netruns only, a fee after 12 Heat, and 2 Sinks maximum. 12 free Heat is about 4 netruns of charge, so by mid-campaign the fee bites.
- **Offset size:** the 8-run minimum path reaches Heat ≈ 70 before the boss (GDD 4.1), so about 9 per run. One Sink adds 3 charge per run, 24 over 8 runs, offsetting about a third. With 12 free and fees after, 15–20 Heat used well takes the boss-entry Heat from ~70 to ~50–55. This is the sim target.
- **Always-build trivial choice:** the R4 raid ultimatum is the intended Schematics sink. The Sink must lose to Firewall Relay or Vault in some mid-campaign states; sim the build rate.
- **Proxy Relay overlap:** if the Relay is never built, drop per-netrun charge to 2.
- **Raid fragility:** at 15 integrity and priority 1 it might never be hit. Target: it is the first node downed in 15–30 % of raids.
- **Charge lost on TAKEN:** test whether it feels unfair; fallback is to keep half.
- **Extraction guard accuracy:** the projected gain must use the actual route and the same Heat rules as the run; test preview = result on 1000 seeds.
- **Sim metrics:** boss-entry Heat, flush count, charge at flush, share of Sinks DOWN, Schematics on Sink vs alternatives, retaliation raids avoided, guard preview accuracy.

## 9. Open questions

Q: Is the Exploit retaliation check evaluated at Rack capture or at run end, and does the run's own Heat gain count? The guard design assumes capture, including run gain.
Q: Should an in-run flush be allowed at a Rack (the Sink is HQ-only today)? It would make the guard exact but needs a new system.
Q: Should `HEAT_SINK_PCT` from ICE scale the flush? v2 says no, to keep preview simple.
Q: Is the 12-Heat free pool plus a 1:1 Schematic fee the right brake, or should it be a hard campaign cap?
Q: Should the Sink be profile-unlocked like the Proxy Relay and Vault, or core with only the Heat ≥ 25 gate?
