<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__raids__main; status ok; tokens in 13733 cache-write 0 cache-read 32585 out 34520; cost $0.190. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **#1 (BLOCKER, §6A arithmetic and logic):**
  - Rebuilt Example A on a new network so the numbers can be checked.
  - Base stats are stated before the +25 % strength, with a rounding rule (half up).
  - Assumed asset stats are listed.
  - Only the enforcer is traced, hit by hit. Exposed, it deals 17 + 17 = 34 and F goes DOWN. Unexposed, it deals 11 + 11 = 22 and F holds with 8 left.
  - The ledger is now: 18 start − 3 (move) − 8 (pay) = 7, then + 18 reward = 25. The "behind" claim is gone.
  - The v1 contradiction (V falls on step 2 / V takes 22 / V "only ×1") is removed, because V is no longer the example node.
- **#2 (BLOCKER, spotlight logic):**
  - The example network now has the Ghost's Safehouse S as an off-route node. It links only to F and H, and F–H is shorter, so no SHORTEST_TO_HOME, HIGHEST_VALUE or WEAKEST_NODE route in this raid passes through S.
  - Moving the ring F→S therefore wastes the bonus on purpose, and it costs 3 Schematics.
  - A line says the Ghost's free decrypt works wherever the ring is.
  - Example A now tests the stated "move" decision.
- **#3 (BLOCKER, preview = result):**
  - Replaced the interval preview with a scope-exact preview.
  - Chips show the exact result for decrypted threats only and are tagged "excl. N encrypted". Encrypted threats show dashed candidate routes and a "?" badge.
  - A node's chip never shows a predicted range.
  - Added a separate, labeled hard bound line ("encrypted threats could add up to +X on this node"). It is a worst-case sum, not a prediction.
  - The rule is that fully decrypted raids have preview = result by property test.
  - Added a data-only fallback: ship R2 disabled.
  - The critic's "show the most likely rule" suggestion was **not** adopted. It would put a guess in the preview that can be wrong.
- **#4 (MAJOR, wave 2 premise):**
  - "Sequential waves with `spawn_step`" is now marked as needing verification against `raid_purge`. If missing, it is NEW (raid_ultimatum), with a data-only fallback of a plain extra wave and no cancel.
  - The ultimatum order versus R2 is specified. Wave 2's species and count are visible at the ultimatum, its routes follow R2, and the player may decrypt before choosing.
  - The wave-2 "cancellable drones" wording is replaced by "the whole wave 2 is cancelled".
- **#5 (MAJOR, ids and tables):**
  - Aurelian and Tethys rosters are labeled placeholder proposals (new threat entries), not facts.
  - The invented non-ids ("levy-lite", "gunship-lite") are removed. Tethys gets a real placeholder id, `tidal_warden`.
  - `siege_unit` is dropped because nothing used it.
  - The new-entry table now has a named routing column (enum names) and `freezes_edges`.
  - The `rebel_mirror_*` row is replaced by a derivation rule.
  - The retag table says "verify against the files".
  - Vehicle mixes were recounted against rosters. Orbital has 0 GROUND.
- **#6 (MAJOR, price curve):**
  - Base prices are now 5 (FLAGGED) / 8 (HUNTED). Fatigue is +0.25 per paid ultimatum, capped ×2.0, rounded half up. HUNTED runs 8, 10, 12, 14, 16 and FLAGGED 5, 6, 8, 9, 10.
  - The "50 % repair cost" anchor is dropped, since install costs aren't given. The anchor is now about 42–44 % of that band's raid reward, with a campaign target of payments ≈ 20 % of Schematics income.
  - The refuse bonus is 1.25× the base price (FLAGGED 6, HUNTED 10).
  - The 1.5× wording is removed.
- **#7 (MAJOR, PURGE and Heat limit):**
  - PURGE wave 2 is mandatory, set via `no_deal`. This is explained in §1, §5 and §9.
  - The "blocked if it would reach 100" rule now applies to the R4 Heat payment too.
  - Added: a Heat payment shows the threshold crossing and queued raid. Cascades are still impossible.
- **#8 (NIT, rewards RNG):**
  - The `rewards` RNG stream is dropped, since no named checkpointed stream is confirmed. The offers are a pure hash of (campaign seed, raid id, ultimatum result), so reloads can't reroll.
  - The "Raid event" offer is listed only when N16 exists.
- **#9 (NIT, free decrypt):** the player now picks which threats get free decrypts. The default pre-selection is the highest-damage threats. It is an option, not forced.
- **Kept, because strong (critic's Keep list):** the hash-based hidden routing, the stall / fire / perimeter vehicle triangle with the Railgun exemption, the Heat-or-Schematics fork, and no cascades from ultimatums.
- **Rulings check:** no fix conflicted with a designer ruling. R2 was ruled by the designer (decrypt with Ghost / Intel / 1 Schematic), so the encrypted-threat reveal stays. The preview change keeps "previews must equal results" for everything the preview claims to show.

---

# Raid design pass: R1-R4

## 1. Raid model recap

**Today.** A raid is a deterministic auto-battle on the Grid graph.

- **Setup (~4 min).** Threat vectors are shown along links from corporate Sites. The player places assets from the Armory (max 6) and repositions deployed ones. Each node shows the exact projected outcome (**HOLDS / DOWN / TAKEN**) as if the raid ran now.
- **Playout (30–60 s, max 30 steps).** Each step runs in this order:
  1. Threats move `edges_per_step` edges by `routing` (SHORTEST_TO_HOME, HIGHEST_VALUE, WEAKEST_NODE; decoys add `decoy_pull`).
  2. ICE Lock and Tar Pit hold threats on their node (`delay_steps` 2 / 3).
  3. Assets fire (range in hops, targeting rule).
  4. Threats damage the node they stand on. At 0 the node goes DOWN, and 50 % of the excess spreads to adjacent claimed nodes.
- **End.** Threats still standing on a node leave it TAKEN. Home integrity is 50; 0 = BREACHED.
- **Rewards.** The raid's `schematic_reward` is paid on CELL HOLDS. Rewards today are 12 / 18 / 25 Schematics.
- **Heat.** Raids fire the first time a Heat threshold is crossed (25 / 50 / 75 / 100). Claim, node-built, retaliation and story raids fire at whatever Heat the campaign is at. Heat ≥ 75 gives raid strength +25 %. Bands: COOL 0–24, NOTICED 25–49, FLAGGED 50–74, HUNTED 75–99, PURGE 100.
- **Current content.** 40 raid files; each is a `RaidData` with `waves[]` of `RaidWaveData` threat lists. `raid_purge` already has two waves; whether waves play sequentially with a spawn delay must be verified before R4 is built (Q).

**Conventions used below.**
- Raid strength (+25 % at HUNTED) multiplies threat integrity and damage, rounded half up.
- A fully decrypted raid keeps today's guarantee: the preview equals the result.

**Where the new rules plug in.** Each rule is a setup-phase choice or a playout rule that is a pure function of (graph, assets, raid data, band, campaign seed). No new RNG is introduced.

| Rule | Plugs into | Phase |
|---|---|---|
| R1 EXPOSED | Step 4 (damage) and setup (move) | Setup choice, playout multiplier |
| R2 Encrypted | Setup preview scope and route reveal | Setup only |
| R3 Vehicles | Step 1 (landers), step 2 (holds), step 3 (turret damage) | Playout |
| R4 Second wave + ultimatum | Raid construction and the setup gate before "Start raid" | Setup choice |

**Band introduction (teaching order):**

| Band | R1 | R3 | R2 | R4 |
|---|---|---|---|---|
| COOL (claim / built raids) | no | GROUND only | no | no |
| NOTICED | yes | one non-GROUND threat | no | no |
| FLAGGED | yes | mixed | the highest-damage threat of each wave | yes (wave 2 = reinforcements) |
| HUNTED | yes | mixed | all threats | yes (bigger, includes a vehicle) |
| PURGE | yes (Home never exposed) | mixed | all, decrypt costs 2 | wave 2 mandatory via `no_deal`: no ultimatum is shown |

Off-threshold raids use the band Heat is in when they are built.

## 2. R1 EXPOSED spotlight

**How a node becomes EXPOSED.**
- Each raid has an `exposure_rule`, an enum resolved at raid construction with ties broken by node id. No RNG.
- Rule values: HIGHEST_VALUE (Vault > Compiler > Firewall > Safehouse > Proxy > Relay among nodes present), MOST_ASSETS, FEWEST_ASSETS, MOST_LINKS, ENTRY_ADJACENT, LAST_CLAIMED.
- The Home server is never exposed. The spotlight lands on a claimed, non-DOWN node, and the rule reads the state at setup start.
- One node is exposed per raid, shown at setup start with a spotlight ring and a "×1.5" tag.

**Extra damage.**
- Choice: **PERCENT, ×1.5 on threat damage dealt to that node's integrity**, rounded up.
- Why: node integrities range 15–50, so a flat bonus would be trivial on a Firewall and lethal on a Relay. A multiplier scales with the threat.
- The multiplier applies before the 50 % spill, so spillover also grows.
- It applies to damage to the node only. It does not touch asset integrity.
- It lasts the whole raid. If the node goes DOWN, a later hit that TAKES it also uses ×1.5.

**Moving the spotlight (setup only).**
- The player may slide the spotlight to an adjacent claimed non-Home node.
- The move costs **2 Heat or 3 Schematics per hop**, max 2 hops. The 2nd hop costs double (4 Heat or 6 Schematics).
- The Heat option shows its band crossing ("+2 Heat → crosses 75, queues a raid"). It is blocked if it would reach 100.
- A move is committed and cannot be rewound. Setup has no RNG, so no checkpoint is needed. It is saved.
- A move can be re-moved, paying again.
- Where the ring sits never affects other bonuses (e.g. a stationed Ghost's free decrypt).

**Decision: defend, move or sacrifice.**
- **Defend:** stack Sentry, Flak and ICE Lock on the exposed node and kill threats before they reach it.
- **Move:** pay to shift the ring onto a node no route reaches (an off-route Safehouse or Proxy), wasting the bonus. This is the cheap tactical lever; R4 is the big sink.
- **Sacrifice:** leave it on a cheap node that will fall anyway, and keep the valuable ones unexposed. A Decoy on the exposed node pulls threats onto the part you have already priced in.

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

**Preview rule: exact for what it shows.**
- The preview never shows a guess or a range for a node.
- **Decrypted threats:** drawn on their real route and included in every node chip, exactly as today.
- **Encrypted threats:** drawn as **three dashed candidate routes** in their colour, with a "?" badge on each node a candidate reaches. Their damage is **not** in the chips.
- Each chip carries a tag: "HOLDS (excl. 4 encrypted)".
- A separate, labeled **bound line** on the node tooltip reads "encrypted threats could add up to +X here". It sums their maximum possible damage over the candidate routes that reach the node. It is a hard bound, not a prediction.
- The playout summary lists the encrypted threats' actual contribution separately, so the player sees what the tag covered.
- With every threat decrypted, the chips cover the whole raid and the preview equals the result. This is covered by a property test.
- **Fallback if the designer rejects scoped previews:** ship R2 disabled (no band lists encrypted threats). R1, R3 and R4 don't depend on it, and the sink is R4.

**Decryption cost** (per threat; the player picks which one):

| Source | Effect |
|---|---|
| Ghost operative stationed on any Safehouse | 1 free decrypt per raid |
| Intel Exploit held (campaign) | 2 free decrypts per raid |
| Schematics | `decrypt_cost_schematics_by_band` per extra threat: 1 at FLAGGED / HUNTED, 2 at PURGE |

- Free decrypts are **chosen by the player**. The UI pre-selects the highest-damage threats as a default and the player may change it.
- Decryptions are committed and saved.
- Tethys has one threat always encrypted at any band (see §8).

**The decision: spend to know, or plan for the worst.**
- At HUNTED a 7-threat raid (4 + 3) leaves the player ~4 encrypted threats after 3 free decrypts. Paying 1 Schematic each buys the information that lets the player move an ICE Lock or the spotlight efficiently.
- Planning for the worst means over-defending the node the bound line names and leaving the others thin.
- Decoys and Honeypots still pull routing, so they remain a hard answer without information.

**Cost note.** R2 is deliberately a small tax (≤ 6 Schematics per raid). The large sink is R4.

## 4. R3 Vehicle types

**Rules.** `ThreatData.vehicle` is an enum: GROUND (default, so old files load unchanged), LANDER, FLYING, HEAVY. A threat has exactly one.

| Vehicle | Rule | Natural counter |
|---|---|---|
| LANDER | Does not enter at the corporate Site. It **drops onto a claimed non-Home node at `arrival_step` (default 2)**: the node its own `routing` rule would target. Pulled by Honeypot / Decoy. Once landed it obeys everything (ICE Lock on the landing node holds it). | Sentry / Flak on likely drop nodes; Honeypot to steer the drop; keep Home's neighbors covered |
| FLYING | Ignores ICE Lock and Tar Pit (never held). Frozen edges still apply. | Dense fire: Flak (3 shots), Sentry, Turrets; fragile (6–14 integrity) |
| HEAVY | **Takes half damage from TURRET-type assets**, rounded up, min 1 per shot. Slow (1 edge), high integrity (26–40). Not exempt from holds. | ICE Lock + Tar Pit stalling, Railgun (exempt) |
| GROUND | Baseline | none |

**Asset rules.**
- "Turret damage" = every asset with `asset_type = TURRET`: Turret, Flak Array, Railgun, Sentry, and the Firewall Relay's built-in turret.
- Against HEAVY: Flak's 2-damage shots become 1; Turret 4 becomes 2; Sentry 3 becomes 2; built-in 3 becomes 2.
- **Railgun is exempt** (`DefenseAssetData.ignores_heavy_armor`, new). It is the rare answer, which keeps the triangle readable.
- Asset tooltips list "no effect on FLYING" (ICE Lock, Tar Pit) and "halved vs HEAVY".

**The mixed Armory decision.** Pure stalling loses to flyers, pure fire loses to heavies, and a thin perimeter loses to landers. The player cannot cover everything within 6 slots, so the Armory itself is the build.

**Existing threats retagged** (data only; **verify the ids and their corporation against `content/threats/*.tres` before applying**):

| Threat | Vehicle |
|---|---|
| lander | LANDER |
| courier, signal_jammer | FLYING |
| bailiff, hauler, debris_field, purger, tow_truck | HEAVY |
| collector, auditor, enforcer, lockdown_unit, inspector, customs_agent, icebreaker, informant, loyalist | GROUND |

**New threat entries** (placeholders; fields match `content/threats/*.tres` plus the new `vehicle` and `arrival_step`; `arrival_step` is used only by LANDER):

| id | integrity | damage | edges_per_step | routing | freezes_edges | vehicle | arrival_step |
|---|---|---|---|---|---|---|---|
| dosing_drone | 6 | 2 | 2 | HIGHEST_VALUE | false | FLYING | n/a |
| gunship | 14 | 5 | 2 | HIGHEST_VALUE | false | FLYING | n/a |
| drop_pod | 10 | 4 | 1 | WEAKEST_NODE | false | LANDER | 3 |
| levy | 6 | 2 | 1 | SHORTEST_TO_HOME | false | GROUND | n/a |
| bannerman | 26 | 8 | 1 | WEAKEST_NODE | false | HEAVY | n/a |
| submersible | 12 | 4 | 1 | WEAKEST_NODE | false | LANDER | 2 |
| pressure_hull | 34 | 10 | 1 | WEAKEST_NODE | true | HEAVY | n/a |
| tidal_warden | 16 | 6 | 1 | SHORTEST_TO_HOME | false | GROUND | n/a |

Names are placeholders. `levy`, `bannerman`, `submersible`, `pressure_hull` and `tidal_warden` belong to the Aurelian and Tethys placeholder rosters and wait for their corporation passes.

**REBEL_CELL derivation rule** (no new rows). The existing `rebel_mirror_*` template threats get their vehicle at raid construction from the player's Armory, as a pure function:
- more TURRET-type assets than lock-type (ICE Lock / Tar Pit) → the mirror's heavy slot is HEAVY;
- more lock-type than TURRET-type → FLYING;
- a majority of assets on their own node (Sentry-type) → LANDER;
- ties break in the order HEAVY, FLYING, LANDER.

**Per-corporation vehicle mixes** (typical HUNTED wave 1 + wave 2, count by vehicle; G = GROUND, H = HEAVY, F = FLYING, L = LANDER):

| Corporation | Mix | Notes |
|---|---|---|
| Solace (Collections) | 4 G, 1 H, 2 F | collector, auditor, enforcer, lockdown_unit; bailiff; 2 dosing_drone |
| Meridian | 2 G, 2 H, 2 F | 2 customs_agent, 2 hauler, 2 courier: the clearest "stall or shoot" pair |
| Halcyon | 3 G, 2 H, 1 L | 2 inspector, lockdown_unit; 2 tow_truck (heavy, freezing); one drop_pod "inspection drop" |
| Orbital | 0 G, 1 H, 2 F, 2 L | debris_field; signal_jammer, gunship; lander, drop_pod |
| Aurelian (LEVIES) | 5 G, 1 H, 1 F | 5 levy; bannerman; gunship in wave 2 (roster assumed) |
| Tethys | 1 G, 2 H, 3 L | tidal_warden; 2 pressure_hull; 3 submersible (roster assumed) |
| REBEL_CELL | derived | Counters your Armory by the rule above |

## 5. R4 Heat-scaled second wave + ultimatum

**Trigger.**
- Eligible: FLAGGED (50–74) and HUNTED (75–99) raids, whether Heat-threshold or off-threshold.
- Not eligible: COOL / NOTICED (teach first), and PURGE, where the existing wave 2 is mandatory (`no_deal = true`; no ultimatum is shown).
- Rule: a raid caused by paying an ultimatum with Heat has no wave 2, so cascades are impossible.

**Composition (authored, not generated).**
- Each corporation authors a wave-2 entry per band as a `RaidWaveData` with `band_min` / `band_max`.
- FLAGGED wave 2 is ≤ 50 % of the wave-1 threat budget and HUNTED ≤ 75 %, where budget = Σ(integrity + 3 × damage) after raid strength.
- HUNTED wave 2 always includes one non-GROUND vehicle and arrives with an announcement ("Reinforcements").
- Wave 2 spawns at `spawn_step` = 10, or the step wave 1 is fully dead if earlier. It uses the same defenses and does not re-open setup.
- **Dependency:** sequential waves with a spawn step must be verified against `raid_purge`. If missing, it is NEW (raid_ultimatum). The data-only fallback is a plain extra wave in `waves[]` with no cancel.

**The ultimatum.** Shown during setup, after the player has seen wave 2's species and count. Its routes follow R2, so the player may spend decrypts before deciding. It must be resolved before **Start raid**.

| Option | FLAGGED | HUNTED |
|---|---|---|
| **Pay Schematics** (cancels the whole wave 2) | 5 | 8 |
| **Pay Heat** (cancels the whole wave 2) | +4 Heat | +6 Heat |
| **Refuse** (take wave 2) | wave 2 plays | wave 2 plays |

**Price curve.**
- Schematics price = band base × (1 + 0.25 × ultimatums already paid this campaign), cap ×2.0, rounded half up.
  - FLAGGED: 5, 6, 8, 9, 10.
  - HUNTED: 8, 10, 12, 14, 16.
- Anchor: the base is about 42–44 % of that band's typical raid reward (FLAGGED 12 → 5, HUNTED 18 → 8). Paying costs a visible share of the win, so it is a choice, not free insurance.
- Campaign target: **ultimatum payments ≈ 20 % of total Schematics income** (sim target in §10). Install and repair costs are not in this document, so no repair-based anchor is used (Q).
- **Heat option:**
  - It shows its band crossing and any queued raid.
  - It is blocked if it would bring Heat to 100 or more.
  - At FLAGGED, +4 from 71–74 crosses 75 and queues a raid.
- If the player lacks Schematics, that option is greyed; if both are unaffordable or illegal, only Refuse remains.
- Both payments are committed and saved. Neither is refundable.

**Why it keeps Schematics scarce.**
- It scales with campaign progress (fatigue and band).
- It lands at exactly the moments the player also wants to repair, patch Home (1 Schematic per integrity point) and reinstall nodes.
- The Schematics-or-Heat fork gives a second currency, so there is always an alternative to spending, at the price of a higher band.

**Reward for refusing and winning (CELL HOLDS after wave 2).**
- Bonus Schematics = 1.25 × the **base** price (no fatigue): FLAGGED 6, HUNTED 10.
- At HUNTED, plus one Armory asset of rarity ≥ 1 (see §7).
- Heat −3 ("they spent their assets").
- Paying yields none of this. The original raid reward is unchanged in both cases.
- The bonus is deliberately smaller than the risk: the sim target is a 55–65 % refuse win rate (§10), so refusing is a gamble, not free money.

**Failure states.**
- Wave 2 that TAKES nodes costs reinstall, repair and a new entry point, as today.
- BREACHED ends the campaign. Wave 2 can breach Home, including after wave 1 left it weak.
- Paying Heat may queue another raid at the next band.
- Refusing without enough defense is the sink's real cost: damage taken instead of Schematics spent.

## 6. How the four combine

### Worked example A: HUNTED (Heat 76, Solace `raid_heat_75`, strength +25 %)

**Assumed placeholder stats** (rounding half up; all threats 1 edge per step unless noted):
- Base wave-1 stats (integrity/damage): collector 12/5, auditor 8/3, enforcer 25/9, lockdown 18/6.
- After +25 %: collector 15/6, auditor 10/4, enforcer 31/11, lockdown 23/8.
- Wave 2: bailiff base 30/10 → 38/13 (HEAVY); dosing_drone base 6/2 → 8/3 (FLYING, 2 edges per step), two of them.
- Budget check (integrity + 3 × damage): wave 1 = 33 + 22 + 64 + 47 = 166. Wave 2 = 77 + 17 + 17 = 111. The HUNTED cap is 75 % of 166 = 124.5, so wave 2 passes.
- Assets: Sentry 3 × 2 shots = 6 per step; Flak 2 × 3 shots = 6; Firewall built-in turret 3 × 1 = 3; Turret 4 × 1 = 4. Assets fire only at threats on their own node; targeting is lowest integrity first.

**Network.**
- Home H (50), Relay R (15), Firewall F (30, built-in turret), Safehouse S (20, Ghost stationed). Intel Exploit held.
- Links: Site X–R, R–F, F–H, F–S, S–H.
- S is never on a route: H is reachable via F–H directly, so no routing rule in this raid passes through S.

**Setup**
1. **R1.** HIGHEST_VALUE (no Vault or Compiler present, so the Firewall wins) puts the spotlight on F (×1.5).
2. **R2.** All 7 threats are encrypted. Free decrypts: Ghost 1 + Intel 2 = 3, chosen by the player: the enforcer (HIGHEST_VALUE → F), the lockdown unit (WEAKEST_NODE → R) and the bailiff. Four stay encrypted (collector, auditor, 2 dosing drones). F's chip reads "excl. 4 encrypted".
3. **R4.** The ultimatum offers 8 Schematics or +6 Heat. The player has 18 Schematics.
4. **Armory.** ICE Lock and Turret on R, Sentry and Flak on F. The other three wave-1 threats are handled on R by the Turret (it shoots the smaller threats first) and R, a cheap Relay, is expected to go DOWN; that is accepted and not traced here.

**The spotlight problem (enforcer at F).**
- Step 1: the enforcer enters R. ICE Lock holds it 2 steps (steps 2 and 3). The R Turret spends its shots on the smaller threats.
- Step 4: it moves R→F. F's assets fire 6 + 6 + 3 = 15: 31 → 16. It hits F.
- Step 5: assets fire 15: 16 → 1. It hits F again.
- Step 6: assets fire first and kill it. No third hit.
- **Exposed:** 17 + 17 = 34 against F's 30. F goes DOWN on step 5 (excess 4, spill 2).
- **Unexposed:** 11 + 11 = 22. F ends at 8 and HOLDS.
- The player pays **3 Schematics** to slide the ring F→S (one hop), where no route goes. F now takes ×1. Alternative: 2 Heat (to 78; no threshold crossed).

**Wave 2 (the decision).**
- With the ring moved, Schematics are 18 − 3 = 15. The player pays **8** to cancel wave 2 (Schematics 7).
- **If refused:** the bailiff (HEAVY) takes halved fire at F (Sentry 2 × 2 = 4, Flak 1 × 3 = 3, built-in 2 = 9 per step; 38 integrity needs 5 steps). F has only 8 left against its first hit of 13, so F goes DOWN and the bailiff walks on toward Home. The drones ignore ICE Lock, so R's ICE Lock does nothing against them. Refusing also meant skipping the −3 Heat and asset only if the player had held, which would need heavier defense than this Armory.

**Outcome.** CELL HOLDS with R DOWN. Schematics ledger: 18 start − 3 (move) − 8 (ultimatum) = 7, then + 18 raid reward = **25**. Heat stays 76. The sink took 11 of the player's 18 Schematics, but income of 18 per raid pays it back and F stays up.

### Worked example B: NOTICED (Heat 27, Meridian `raid_heat_25`)

Same graph shape, no Ghost, no Intel, no strength bonus (Heat < 75).
- **R1.** MOST_LINKS puts the spotlight on R (3 links).
- **R2.** No encryption at NOTICED. The preview is exact.
- **R3.** One non-GROUND threat in the mix: a courier (FLYING 8/3, 2 edges), plus a customs agent (GROUND) and a hauler (HEAVY 28/10).
- **R4.** None; NOTICED is exempt.
- **Setup.** The preview shows the courier will ignore an ICE Lock on R, so a Turret and Sentry on R handle it. The hauler is HEAVY and halves Turret damage, so ICE Lock + Tar Pit stall it while Flak chips (1 per shot).
- **Spotlight.** R is both exposed and the choke. Moving costs 2 Heat per hop; the player declines and instead places a Decoy on S to drag the hauler to a node that matters less.
- **Outcome.** A puzzle with no second wave and no unknowns: a deliberate teaching raid. Schematics reward 12.

## 7. Raid-win reward screen

Shown on CELL HOLDS, after the playout summary. It is a **raid-view panel**: a recap plus a pick-one-of-three offer, with the raid's base Schematics always paid.

**Recap.** DOWN / TAKEN nodes and repair costs (as today), plus "what saved you": steps held by ICE Lock / Tar Pit, kills per asset, the spotlight outcome, the encrypted threats' actual contribution (§3) and the ultimatum result.

**Offers: pick 1 of 3.** The three offers are chosen from the pool below by a pure hash of (campaign seed, raid id, ultimatum result). No RNG stream is used, so reloads cannot reroll.

| Offer | Content |
|---|---|
| Salvage | One Armory asset, rarity by band (NOTICED 0, FLAGGED 0–1, HUNTED ≥ 1); weighted toward counters of the vehicle types that raided you |
| Field Repair | Repair one DOWN node free, or +5 Home integrity |
| Cool Down | −3 Heat (−5 if wave 2 was refused and cleared) |
| Intel Dump | Free decrypts for your next raid; reveals the next raid's exposure rule |
| Spoils | A small Schematics bonus |
| Raid event | A Terminal-style event with a corporation voice (e.g. "reprogram a captured drone or sell it"); only in the pool if N16 exists |

**Rules.**
- The refuse-and-hold bonus (Schematics, asset, −3 Heat) from R4 shows as a separate "Spoils" banner, outside the pick.
- A lost raid has a **lessons panel** instead (each threat's actual route, the spotlight, what the encrypted threats were) with no offers.
- Table form: reuse N18 `RewardTableData` rows with a `raid` context (conditions: band, ultimatum refused, vehicle types faced). Without N18 the offers are hard-coded.

## 8. Corporation flavour table

| Corporation | Raid name | Threat roster | Signature twist (exposure rule, data-defined) |
|---|---|---|---|
| Solace | Collections | collector, auditor, enforcer, lockdown_unit, bailiff, dosing_drone | Exposure: HIGHEST_VALUE (follows the money). The ultimatum is framed as a "Final Notice" (price shown in Schematics) |
| Meridian | Freight Audit | courier, hauler, customs_agent | Exposure: MOST_LINKS (traffic). Customs agents seal links, so FLYING couriers become the way through |
| Halcyon | Compliance Sweep | inspector, tow_truck, lockdown_unit, drop_pod (inspection drop) | Exposure: FEWEST_ASSETS (they inspect the unguarded). Tow trucks are heavy and freeze |
| Orbital | Launch Window | lander, signal_jammer, debris_field, drop_pod, gunship | Exposure: ENTRY_ADJACENT, with optional sweep: the ring advances 1 link every 8 steps along a fixed path. Flyers and landers dominate; the only heavy is the debris field |
| Aurelian Concord (placeholder) | LEVIES | levy, bannerman, gunship | Exposure: LAST_CLAIMED. **Levy muster:** wave 2 gets +1 levy per TAKEN node (max 3) |
| Tethys Deep (placeholder) | Undertow | submersible, pressure_hull, tidal_warden | Exposure: ENTRY_ADJACENT (the shore). **Dark water:** one threat per raid is always encrypted at any band |
| REBEL_CELL | Mirror Audit | existing `rebel_mirror_*` template threats built from your Armory; vehicles derived per §4 | Exposure: MOST_ASSETS (your best node). Vehicles counter your Armory |

## 9. Systems & data

**Systems.** None of N1–N20 covers raids; these are raid-sim systems.

| System | Description | Size | Fallback |
|---|---|---|---|
| NEW: raid_exposure (R1) | `exposure_rule`, ×mult in the damage step, move action | S–M | None; needs sim code |
| NEW: raid_encryption (R2) | Hidden routing hash, scope-tagged preview (exact for decrypted threats only), bound line, decrypt actions, UI | M | Ship R2 disabled |
| NEW: raid_vehicles (R3) | `vehicle`, lander spawn, hold immunity, turret halving | M | None |
| NEW: raid_ultimatum (R4) | Band-gated waves, ultimatum gate, price curve, payments, wave spawn step | S–M plus UI M | Wave 2 as a plain extra wave (existing `waves[]`) with no cancel |
| NEW: raid_reward_screen | Recap + pick-1-of-3 via a pure hash | M | Existing reward summary |
| N18 (optional) | Reward rows with raid context | M | Hard-coded offers |
| N16 (optional) | Raid event hooks for the "Raid event" offer | M | Omit that offer |

**New fields.**
- `RaidData`: `exposure_rule` (enum), `ultimatum_allowed` (bool, default true), `no_deal` (bool; true on purge raids).
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
- `ultimatum_price_by_band` = {FLAGGED 5, HUNTED 8}, `ultimatum_heat_by_band` = {FLAGGED 4, HUNTED 6}
- `ultimatum_fatigue_step` = 0.25, `ultimatum_fatigue_cap` = 2.0
- `ultimatum_heat_blocks_at` = 100
- `wave2_reward_mult` = 1.25 (of the base price), `wave2_delay_steps` = 10

## 10. Balance & sim notes

- **Per band:** node loss rate (DOWN / TAKEN) and Home damage, with and without each rule on.
- **R1:** share of raids where moving the spotlight changes the outcome; Heat vs Schematics choice split.
- **R2:** decrypt spend per raid; value of information (outcome difference between the scope-tagged chips and the final result).
- **R3:** the counter triangle. Build a win matrix (stall / fire / perimeter Armories against each vehicle mix). Target: no pure Armory above 80 % or below 40 %.
- **R4 (the sink):**
  - Ultimatum payments as a share of total Schematics income (target ≈ 20 %).
  - Pay / Heat / refuse split by band. If refuse is under 15 %, the reward is too weak; if pay is under 30 %, the price is too high.
  - Refuse win rate with a typical Armory (target 55–65 %).
- **Determinism:**
  - A property test for preview = result when fully decrypted.
  - A scope test: the chip equals the result computed over decrypted threats only.
  - A bound test: the bound line is always ≥ the actual added damage.
  - The same inputs give the same raid.
- **Time:** setup under 4 minutes (a decision count per raid is a proxy).
- Reuse the sim runner; add per-wave metrics (N19 style).

## 11. Q: open questions

- Q: Is a scope-exact preview (chips cover decrypted threats only, plus a hard bound line) acceptable for encrypted routes under "previews must equal results", or should R2 ship disabled?
- Q: Do waves resolve sequentially with shared defenses and a spawn delay today (check `raid_purge`)?
- Q: Is "pay Heat to cancel" acceptable as raising Heat (a bribe that can queue a new raid), or should it be a Heat-reduction variant?
- Q: What are the Aurelian (LEVIES) and Tethys theme facts? The rosters, mixes and twists here are placeholders.
- Q: What are the node install and repair costs, so the ultimatum price can be anchored to them instead of to the raid reward?
