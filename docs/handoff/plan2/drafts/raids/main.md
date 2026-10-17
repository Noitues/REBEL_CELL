<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rfKTpQwx8NMWybA2QuuPB, custom_id raid__main; status ok; tokens in 6798 cache-write 32007 cache-read 0 out 27026; cost $0.182. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Raid design pass: R1-R4

## 1. Raid model recap

**Today.** A raid is a deterministic auto-battle on the Grid graph.

- **Setup (~4 min).** Threat vectors are shown along links from corporate Sites. The player places assets from the Armory (max 6) and repositions deployed ones. Each node shows the exact projected outcome (**HOLDS / DOWN / TAKEN**) as if the raid ran now.
- **Playout (30–60 s, max 30 steps).** Each step runs in this order:
  1. Threats move `edges_per_step` edges by `routing` (SHORTEST_TO_HOME, HIGHEST_VALUE, WEAKEST_NODE; decoys add `decoy_pull`).
  2. ICE Lock and Tar Pit hold threats on their node (`delay_steps` 2 / 3).
  3. Assets fire (range in hops, targeting rule).
  4. Threats damage the node they stand on. At 0 the node goes DOWN, and 50 % of the excess spreads to adjacent claimed nodes.
- **End.** Threats still standing on a node leave it TAKEN. Home integrity 50; 0 = BREACHED.
- **Rewards.** The raid's `schematic_reward` is paid on CELL HOLDS.
- **Heat.** Raids fire the first time a Heat threshold is crossed (25 / 50 / 75 / 100). Claim, node-built, retaliation and story raids fire at whatever Heat the campaign is at. Heat ≥ 75 gives raid strength +25 %. Bands: COOL 0–24, NOTICED 25–49, FLAGGED 50–74, HUNTED 75–99, PURGE 100.
- **Current content.** 40 raid files; each is a `RaidData` with `waves[]` of `RaidWaveData` threat lists. `raid_purge` already has two waves. Rewards today are 12 / 18 / 25 Schematics.

**Where the new rules plug in.** Every rule below is a setup-phase choice or a playout rule that is a pure function of (graph, assets, raid data, band, campaign seed). No new RNG is introduced.

| Rule | Plugs into | Phase |
|---|---|---|
| R1 EXPOSED | Step 4 (damage) and setup (move) | Setup choice, playout multiplier |
| R2 Encrypted | Setup preview and threat route reveal | Setup only |
| R3 Vehicles | Step 1 (spawn, landers), step 2 (holds), step 3 (turret damage) | Playout |
| R4 Second wave + ultimatum | Raid construction and the setup gate before "Start raid" | Setup choice |

**Band introduction (teaching order):**

| Band | R1 | R3 | R2 | R4 |
|---|---|---|---|---|
| COOL (claim / built raids) | no | GROUND only | no | no |
| NOTICED | yes | one non-GROUND threat | no | no |
| FLAGGED | yes | mixed | 1 threat per wave | yes (wave 2 = reinforcements) |
| HUNTED | yes | mixed | all threats | yes (bigger, with vehicle) |
| PURGE | yes (Home never exposed) | mixed | all, decrypt costs 2 | wave 2 mandatory (no ultimatum, "no deal") |

Off-threshold raids use the band Heat is in when they are built.

## 2. R1 EXPOSED spotlight

**How a node becomes EXPOSED.**
- Each raid has an `exposure_rule`, an enum resolved at raid construction with ties broken by node id. No RNG.
- Rule values: HIGHEST_VALUE (Vault > Compiler > Firewall > Safehouse > Proxy > Relay), MOST_ASSETS, FEWEST_ASSETS, MOST_LINKS, ENTRY_ADJACENT, LAST_CLAIMED.
- The Home server is never exposed. The spotlight lands on a claimed, non-DOWN node, and the rule reads the state at setup start.
- One node is exposed per raid, shown at setup start with a spotlight ring and a "×1.5" tag.

**Extra damage.**
- Choice: **PERCENT, ×1.5 on threat damage dealt to that node's integrity**, rounded up.
- Why: node integrities range 15–50, so a flat bonus would be trivial on a Firewall and lethal on a Relay. A multiplier scales with the threat.
- The multiplier applies before the 50 % spill, so spillover also grows.
- It applies to damage to the node only. It does not touch asset integrity or chip damage from other sources.
- It lasts the whole raid. If the node goes DOWN, a later hit that TAKES it also uses ×1.5.

**Moving the spotlight (setup only).**
- The player may slide the spotlight to an adjacent claimed non-Home node.
- The move costs **2 Heat or 3 Schematics per hop**, max 2 hops. The 2nd hop costs double (4 Heat or 6 Schematics).
- The Heat option shows its band crossing ("+2 Heat → crosses 75, queues a raid"). It is blocked if it would reach 100.
- A move is committed and cannot be rewound. Setup has no RNG, so no checkpoint is needed. It is saved.
- A move can be re-moved, paying again.

**Decision: defend, move or sacrifice.**
- **Defend:** stack Sentry, Flak and ICE Lock on the exposed node and kill threats before they reach it.
- **Move:** pay to shift the ring onto a node the routing won't reach (a dead-end Safehouse or Proxy), wasting the bonus. This is the cheap tactical lever; R4 is the big sink.
- **Sacrifice:** leave it on a cheap node that will fall anyway, and keep the valuable ones unexposed. Put a Decoy on the exposed node so threats chew the part you have already priced in.

**Preview and determinism.**
- The projection includes the multiplier. Exposed node chips read "EXPOSED ×1.5" in the breakdown tooltip.
- Moving the ring recomputes the projection instantly.
- Pure function of the graph, so preview = result.

**UI.**
- A spotlight cone over the node; a draggable ring with legal target nodes pulsing.
- A cost chip on each target ("2 Heat / 3 Sch").
- The tooltip shows the rule that picked it ("Collections target the Vault").

## 3. R2 Encrypted routes

**What "encrypted" hides.**
- Threat species, stats and entry point are always visible. What is hidden is **which routing rule it follows**.
- At raid construction each encrypted threat gets a hidden routing from the three legal rules (SHORTEST_TO_HOME, HIGHEST_VALUE, WEAKEST_NODE). It is a pure hash of (campaign seed, raid id, threat index), not an RNG stream.
- The species default routing is a hint ("Enforcers usually go for the weakest node"), but the hidden one may differ. This makes encryption a real question, not a delay.

**Bands:**

| Band | Encrypted threats |
|---|---|
| COOL / NOTICED | none |
| FLAGGED | the single highest-damage threat of each wave |
| HUNTED | every threat in every wave |
| PURGE | every threat; decryption costs 2 |

**Dashed paths and what the preview shows.**
- An encrypted threat draws **all three candidate routes as dashed lines**, in its colour.
- Node outcomes are an interval, not a single value: the **best and worst case across the three candidates** (e.g. "HOLDS … DOWN", hatched).
- The worst case drives a warning tint. A hatched "?" badge sits on each affected node.
- The interval is always sound: the real result lies inside it. Decrypting collapses it to exact, and the preview then equals the result.
- With every threat decrypted, the existing exact-preview guarantee is fully restored.

**Decryption cost** (per threat; the player picks which one):

| Source | Effect |
|---|---|
| Ghost operative stationed on any Safehouse | 1 free decrypt per raid |
| Intel Exploit held (campaign) | 2 free decrypts per raid |
| Schematics | 1 Schematic per extra threat (2 at PURGE) |

- Free decrypts apply first, automatically, to the highest-damage threats.
- Decryptions are committed and saved.
- Tethys has one threat always encrypted at any band (see §8).

**The decision: spend to know, or plan for the worst.**
- At HUNTED a 5-threat raid leaves the player ~2 paid decrypts after free ones. That is 2 Schematics against the information that lets the player move an ICE Lock or the spotlight efficiently.
- Planning for the worst means over-defending the worst-case node and leaving the others thin.
- Decoys and Honeypots still pull routing, so they remain a hard answer without information.

**Cost note.** R2 is deliberately a small tax (≤ 6 Schematics per raid). The large sink is R4.

## 4. R3 Vehicle types

**Rules.** `ThreatData.vehicle` is an enum: GROUND (default, so old files load unchanged), LANDER, FLYING, HEAVY. A threat has exactly one.

| Vehicle | Rule | Natural counter |
|---|---|---|
| LANDER | Does not enter at the corporate Site. It **drops onto a claimed non-Home node at `arrival_step` (default 2)**: the node its own `routing` rule would target. Pulled by Honeypot / Decoy. Once landed it obeys everything (ICE Lock on the landing node holds it). | Sentry / Flak on likely drop nodes; Honeypot to steer the drop; keep Home's neighbours covered |
| FLYING | Ignores ICE Lock and Tar Pit (never held). Frozen edges still apply. | Dense fire: Flak (3 shots), Sentry, Turrets; fragile (6–14 integrity) |
| HEAVY | **Takes half damage from TURRET-type assets**, rounded up, min 1 per shot. Slow (1 edge), high integrity (26–40). Not exempt from holds. | ICE Lock + Tar Pit stalling, Railgun (exempt, see below) |
| GROUND | Baseline | — |

**Asset rules.**
- "Turret damage" = every asset with `asset_type = TURRET`: Turret, Flak Array, Railgun, Sentry, and the Firewall Relay's built-in turret.
- Flak's 2-damage shots become 1; Turret 4 becomes 2; Sentry 3 becomes 2; built-in 3 becomes 2.
- **Railgun is exempt** (`DefenseAssetData.ignores_heavy_armor`, new). It is the rare answer, which keeps the triangle readable.
- Asset tooltips list "no effect on FLYING" (ICE Lock, Tar Pit) and "halved vs HEAVY".

**The mixed Armory decision.** Pure stalling loses to flyers, pure fire loses to heavies, and a thin perimeter loses to landers. The player cannot cover everything within 6 slots, so the Armory itself is the build.

**Existing threats retagged** (data only):

| Threat | Vehicle |
|---|---|
| lander | LANDER |
| courier, signal_jammer | FLYING |
| bailiff, hauler, debris_field, purger, tow_truck | HEAVY |
| collector, auditor, enforcer, lockdown_unit, inspector, customs_agent, icebreaker, informant, loyalist | GROUND |

(Which threat belongs to which corporation is inferred from flavour; verify against the files.)

**New threat entries** (fields match `content/threats/*.tres`; new fields `vehicle` and `arrival_step` marked):

| id | integrity | damage | edges_per_step | routing | other | vehicle | arrival_step |
|---|---|---|---|---|---|---|---|
| dosing_drone | 6 | 2 | 2 | 1 | | FLYING | n/a |
| gunship | 14 | 5 | 2 | 1 | | FLYING | n/a |
| drop_pod | 10 | 4 | 1 | 2 | | LANDER | 3 |
| siege_unit | 40 | 12 | 1 | 0 | | HEAVY | n/a |
| levy | 6 | 2 | 1 | 0 | | GROUND | n/a |
| bannerman | 26 | 8 | 1 | 2 | | HEAVY | n/a |
| submersible | 12 | 4 | 1 | 2 | | LANDER | 2 |
| pressure_hull | 34 | 10 | 1 | 2 | freezes_edges = true | HEAVY | n/a |
| rebel_mirror_* | copy of the player's asset type (existing template threats) | | | | | derived: TURRET-heavy Armory → HEAVY; lock-heavy → FLYING; own-node-heavy → LANDER | |

Descriptions are one line each; names are placeholders.

**Per-corporation vehicle mixes** (typical HUNTED wave 1 + wave 2, count by vehicle):

| Corporation | Signature mix | Notes |
|---|---|---|
| Solace (Collections) | 4 G, 1 H, 2 F | Bailiff for the heavy slot; dosing drones arrive as wave-2 flyers |
| Meridian | 2 G, 2 H, 2 F | Haulers and couriers: the clearest "stall or shoot" pair |
| Halcyon | 3 G, 2 H, 1 L | Tow trucks (heavy and freezing); one lander "inspection drop" |
| Orbital | 1 G, 1 H, 2 F, 2 L | Flyers and drop pods; debris field is the only heavy |
| Aurelian (LEVIES, assumed) | 5 G, 1 H, 1 F | Mass of levies; bannerman heavy; gunship as flyer in wave 2 |
| Tethys (assumed) | 1 G, 2 H, 3 L | Submersibles surface inside the network; pressure hulls freeze edges |
| REBEL_CELL | derived | Counters your Armory: heavy against Turret-stackers, flyers against lock-stackers, landers against own-node Sentries |

Aurelian and Tethys rosters are assumptions pending their corp passes (see Q).

## 5. R4 Heat-scaled second wave + ultimatum

**Trigger.**
- Eligible: FLAGGED (50–74) and HUNTED (75–99) raids, whether Heat-threshold or off-threshold.
- Not eligible: COOL / NOTICED (teach first), and PURGE, where the existing wave 2 is mandatory ("no deal").
- Rule: a raid caused by paying an ultimatum with Heat has no wave 2, so cascades are impossible.

**Composition (authored, not generated).**
- Each corporation authors a wave-2 entry per band as a `RaidWaveData` with `band_min` / `band_max`.
- FLAGGED wave 2 is ≤ 50 % of wave-1 threat budget, HUNTED ≤ 75 %, where budget = Σ(integrity + 3×damage).
- HUNTED wave 2 always includes one non-GROUND vehicle, and arrives with an announcement ("Reinforcements").
- Wave 2 spawns at `spawn_step` = 10, or the step wave 1 is fully dead if earlier. It uses the same defenses and does not re-open setup (sequential waves already exist in `raid_purge`; verify).

**The ultimatum.** Shown during setup, after the player has seen wave 2's composition and routes (still subject to R2). It must be resolved before **Start raid**.

| Option | FLAGGED | HUNTED |
|---|---|---|
| **Pay Schematics** (cancels wave 2) | 8 | 14 |
| **Pay Heat** (cancels wave 2) | +4 Heat | +6 Heat |
| **Refuse** (take wave 2) | wave 2 plays | wave 2 plays |

**Price curve.**
- Schematics price = band base × (1 + 0.25 × ultimatums already paid this campaign), cap ×2.0. So HUNTED goes 14 → 17.5 → 21 → … → 28.
- Anchor: the base is about the 50 % repair cost of one DOWN node. Paying costs about what failing would, so it is a real choice rather than free insurance.
- Heat options show their band crossing and a queued raid if any.
- If the player lacks Schematics, that option is greyed; if both are unaffordable or illegal, only Refuse remains.
- Both payments are committed and saved. Neither is refundable.

**Why it keeps Schematics scarce.**
- It scales with campaign progress (fatigue and band).
- It lands at exactly the moments the player also wants to repair, patch Home (1 Schematic per integrity point) and reinstall nodes.
- The Schematics-or-Heat fork gives a second currency, so there is always an alternative to spending.

**Reward for refusing and winning (CELL HOLDS after wave 2).**
- Bonus Schematics = 1.5 × the Schematics price (FLAGGED 12, HUNTED 21), at the base price (no fatigue).
- At HUNTED, plus one Armory asset of rarity ≥ 1 (see §7).
- Heat −3 ("they spent their assets").
- Paying yields none of this. The original raid reward is unchanged in both cases.

**Failure states.**
- Wave 2 that TAKES nodes costs reinstall, repair and a new entry point, as today.
- BREACHED ends the campaign. Wave 2 can breach Home, including after wave 1 left it weak.
- Paying Heat may queue another raid at the next band.
- Refusing without enough defense is the sink's real cost: damage taken instead of Schematics spent.

## 6. How the four combine

### Worked example A: HUNTED (Heat 76, Solace `raid_heat_75`, strength +25 %)

Network: Home H (50), Relay R (15), Vault V (20), Firewall F (30, built-in turret 3), Safehouse S (20, Ghost stationed). Links: Site X–R, R–V, R–F, F–H, V–S, S–H.

**Setup**
1. **R1.** Rule HIGHEST_VALUE puts the spotlight on V (×1.5).
2. **R2.** All 5 threats (4 wave 1 + wave-2 heavy, drones listed but cancellable) are encrypted. Free decrypts: Ghost 1 + Intel 2 = 3, and the player pays 1 Schematic for a 4th.
3. **Wave 1** (after the +25 % rounding): collector 15/6, auditor 10/4, enforcer 31/11, lockdown 23/8.
4. **Wave 2 preview** (HUNTED authored): bailiff (HEAVY 38/13), 2 dosing drones (FLYING 8/3).
5. **R4.** The ultimatum offers 14 Schematics or +6 Heat. The player has 18 Schematics.
6. **Armory.** ICE Lock and Turret on R, Sentry and Flak on V, Tar Pit on F.

**Reading the spotlight problem.** The enforcer on V deals 11×1.5 ≈ 17 per step against 20. The player's Sentry (3×2) and Flak (3×2) deal ~12 per step. The enforcer (31) needs 3 steps, so V falls on step 2 and is TAKEN on step 3. The player pays 3 Schematics to move the ring V → S (one hop), a node the routing never visits.

**Resolution (abridged)**
- **Steps 1–2.** The collector, auditor and lockdown unit enter R. ICE Lock holds two of them 2 steps; the Turret kills the auditor (10) in 3 shots. The lockdown unit freezes the R–F link.
- **Steps 3–5.** The enforcer reaches V and is shot to death by Sentry + Flak before V drops. V takes 22 total and goes DOWN with spillover to S; with the spotlight on S, V's damage was only ×1.
- **Wave 2 (the decision).** With 18 − 1 − 3 = 14 Schematics left, the player pays 14 and cancels it. The alternative would have been the bailiff (HEAVY, halved Turret damage) hammering R while the drones ignore the ICE Lock and Tar Pit.
- **Outcome.** CELL HOLDS, wave 1 reward 18 Schematics. Net +4 − 1 − 3 − 14 means the player is behind on Schematics but with all nodes and Heat unchanged.

### Worked example B: NOTICED (Heat 27, Meridian `raid_heat_25`)

Same graph shape, no Ghost, no Intel.
- **R1.** Rule MOST_LINKS puts the spotlight on R (3 links).
- **R2.** No encryption at NOTICED.
- **R3.** One non-GROUND threat: a courier (FLYING, 8/3, 2 edges), plus a customs agent (GROUND) and a hauler (HEAVY 28/10).
- **R4.** None; NOTICED is exempt.
- **Setup.** The player sees the courier will ignore an ICE Lock on R. A Turret and Sentry on R handle it. The hauler is HEAVY and halves Turret damage, so ICE Lock + Tar Pit stall it while Flak chips (1 per shot).
- **Spotlight.** R is both exposed and the choke. Moving costs 2 Heat per hop; the player declines and instead places a Decoy on S to drag the hauler to a node that matters less.
- **Outcome.** The raid is a puzzle with no dangerous second wave: a deliberate teaching raid. Schematics reward 12.

## 7. Raid-win reward screen

Shown on CELL HOLDS, after the playout summary. It is a **raid-view panel**: a recap plus a pick-one-of-three offer, with the raid's base Schematics always paid.

**Recap.** DOWN / TAKEN nodes and repair costs (as today), plus "what saved you": steps held by ICE Lock / Tar Pit, kills per asset, the spotlight outcome, and ultimatum result.

**Offers: pick 1 of 3.** Drawn from the pool below by the `rewards` RNG stream, seeded at the screen's checkpoint, so reloads can't reroll.

| Offer | Content |
|---|---|
| Salvage | One Armory asset, rarity by band (NOTICED 0, FLAGGED ≥ 0–1, HUNTED ≥ 1); weighted toward counters of the vehicle types that raided you |
| Field Repair | Repair one DOWN node free, or +5 Home integrity |
| Cool Down | −3 Heat (−5 if wave 2 was refused and cleared) |
| Intel Dump | Free decrypts for your next raid; reveals the next raid's exposure rule |
| Spoils | +Schematics bonus (small) |
| Raid event | A Terminal-style event with a corporation voice (e.g. "reprogram a captured drone or sell it"), using the N16 event hooks |

**Rules.**
- The refuse-and-hold bonus (Schematics, asset, −3 Heat) from R4 shows as a separate "Spoils" banner, outside the pick.
- A lost raid has a **lessons panel** instead (each threat's actual route, the spotlight, what encrypted threats were) with no offers.
- Table form: reuse N18 `RewardTableData` rows with a `raid` context (conditions: band, ultimatum refused, vehicle types faced).

## 8. Corporation flavour table

| Corporation | Raid name | Threat roster | Signature twist (exposure rule, data-defined) |
|---|---|---|---|
| Solace | Collections | collector, auditor, enforcer, lockdown_unit, bailiff, dosing_drone | Exposure: HIGHEST_VALUE (follows the money). The ultimatum is framed as a "Final Notice" (price shown in Schematics) |
| Meridian | Freight Audit | courier, hauler, customs_agent, gunship-lite (courier) | Exposure: MOST_LINKS (traffic). Customs agents seal links, so FLYING couriers become the way through |
| Halcyon | Compliance Sweep | inspector, tow_truck, lockdown_unit, drop_pod (inspection drop) | Exposure: FEWEST_ASSETS (they inspect the unguarded). Tow trucks are heavy and freeze |
| Orbital | Launch Window | lander, signal_jammer, debris_field, drop_pod, gunship | Exposure: ENTRY_ADJACENT, with optional sweep: the ring advances 1 link every 8 steps along a fixed path. Flyers and landers dominate |
| Aurelian Concord (assumed) | LEVIES | levy, bannerman, gunship | Exposure: LAST_CLAIMED. **Levy muster:** wave 2 gets +1 levy per TAKEN node (max 3) |
| Tethys Deep (assumed) | Undertow | submersible, pressure_hull, levy-lite grounds | Exposure: ENTRY_ADJACENT (the shore). **Dark water:** one threat per raid is always encrypted at any band |
| REBEL_CELL | Mirror Audit | rebel_mirror_* (existing template threats built from your Armory) | Exposure: MOST_ASSETS (your best node). Vehicles counter your Armory (see §4) |

## 9. Systems & data

**Systems.** None of N1–N20 covers raids; these are raid-sim systems.

| System | Description | Size | Fallback |
|---|---|---|---|
| NEW: raid_exposure (R1) | `exposure_rule`, ×mult in damage step, move action | S–M | None; needs sim code |
| NEW: raid_encryption (R2) | Hidden routing hash, interval preview, decrypt actions, UI | M | Visual-only dashes (no rule change) |
| NEW: raid_vehicles (R3) | `vehicle`, lander spawn, hold-immunity, turret halving | M | None |
| NEW: raid_ultimatum (R4) | Band-gated waves, ultimatum gate, price curve, payments | S–M plus UI M | Wave 2 as a plain extra wave (data only, existing `waves[]`) with no cancel |
| NEW: raid_reward_screen | Recap + pick-1-of-3 | M | Existing reward summary |
| N18 (optional) | Reward rows with raid context | M | Hard-coded offers |
| N16 (optional) | Raid event hooks | M | Skip the event offer |

**New fields.**
- `RaidData`: `exposure_rule` (enum), `ultimatum_allowed` (bool, default true), `no_deal` (bool, purge).
- `RaidWaveData`: `band_min`, `band_max` (-1 = any), `spawn_step`, `is_reinforcement`, `levy_per_taken` (Aurelian).
- `ThreatData`: `vehicle` (enum, default GROUND), `arrival_step` (default 2).
- `DefenseAssetData`: `ignores_heavy_armor` (bool).
- `CampaignState`: `ultimatums_paid`.

**Config keys** (`campaign_config.tres`):
- `exposed_damage_mult` = 1.5
- `spotlight_move_cost_heat` = 2, `spotlight_move_cost_schematics` = 3, `spotlight_move_max_hops` = 2
- `decrypt_cost_schematics_by_band` = [0, 0, 1, 1, 2]
- `ghost_free_decrypts` = 1, `intel_free_decrypts` = 2
- `heavy_turret_damage_mult` = 0.5
- `lander_arrival_step` = 2
- `ultimatum_price_by_band` = {FLAGGED 8, HUNTED 14}, `ultimatum_heat_by_band` = {4, 6}
- `ultimatum_fatigue_step` = 0.25, `ultimatum_fatigue_cap` = 2.0
- `wave2_reward_mult` = 1.5, `wave2_delay_steps` = 10

## 10. Balance & sim notes

- **Per band:** node loss rate (DOWN / TAKEN) and Home damage, with and without each rule on.
- **R1:** share of raids where moving the spotlight changes the outcome; Heat vs Schematics choice split.
- **R2:** decrypt spend per raid; value of information (outcome variance between interval and exact).
- **R3:** the counter triangle. Build a win matrix (stall / fire / perimeter Armories against each vehicle mix). Target: no pure Armory above 80 % or below 40 %.
- **R4 (the sink):**
  - Ultimatum payments as a share of Schematics income (target 15–25 %).
  - Pay / Heat / refuse split by band. If refuse is under 15 %, the reward is too weak; if pay is under 30 %, the price is too high.
  - Refuse win rate with a typical Armory (target 55–65 %).
- **Determinism:** a property test for preview = result when fully decrypted; interval soundness (real ∈ [best, worst]); the same inputs give the same raid.
- **Time:** setup under 4 minutes (a decision count per raid is a proxy).
- Reuse the sim runner; add per-wave metrics (N19 style).

## 11. Q: open questions

- Q: Is a preview interval (R2, "?" while encrypted) acceptable against "previews must equal results", given it is sound and collapses to exact on decrypt?
- Q: Do waves resolve sequentially with shared defenses today, and should wave 2 open a short re-setup window?
- Q: Is "pay Heat to cancel" acceptable as raising Heat (a bribe that can queue a new raid), or should it be a Heat *reduction* variant?
- Q: What are the Aurelian (LEVIES) and Tethys theme facts? The rosters, vehicle mixes and twists here are guesses.
- Q: Should Flak get a dedicated anti-air tag, or does its 3-shot profile suffice as the FLYING counter?
- Q: May a Home-adjacent node be sacrificed deliberately (spotlight there), and does that need a spill cap so it can't be used to bleed Home?
