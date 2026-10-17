<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01PcdHiKPUftbyJsQfMG5RZa, custom_id raid3__unified; status ok; tokens in 21975 cache-write 32585 cache-read 0 out 11194; cost $0.119. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# raids: unified design pass

## 1. Raid model recap

| GDD 7 / config fact | Value | Where the new rules plug in |
|---|---|---|
| Setup | about 4 min; place Armory assets (max 6); every node shows its projected HOLDS / DOWN / TAKEN | R1 move, R2 decrypt, R4 ultimatum all resolve here |
| Playout | up to `raid_step_cap` = 30 steps | R3 changes steps 1-3; R1 changes step 4 |
| Step order | 1) threats move (`edges_per_step`, routing, decoy pull) 2) ICE Lock / Tar Pit hold 3) assets fire 4) threats damage their node. At 0 the node goes DOWN and 50 % of the excess spreads to adjacent claimed nodes | |
| End | Threats still on nodes leave them TAKEN. Home integrity 50; 0 = BREACHED | |
| Rewards | `raid_schematics_by_tier` = 8 / 12 / 18 / 25, paid on CELL HOLDS | R4 bonus is extra |
| Heat | Raids fire on thresholds 25 / 50 / 75 / 100. Heat ≥ 75 gives raid strength +25 %. Bands: NOTICED 25-49, FLAGGED 50-74, HUNTED 75-99, PURGE 100 | Band picks which rules are on |
| Baseline | 5.2 raids per campaign (1.6 won, 3.6 lost); income about 1410 Schematics, unspent about 191 | Sink sizing in §2 R4 |

All four rules are pure functions of (graph, placements, raid data, band, campaign seed). **No RNG is added.**

## 2. The four rules

### R1 EXPOSED spotlight

- **Selection:** `exposure_rule` on `RaidData`, resolved when the raid is built, with ties broken by node id. The rule reads the graph state at setup start.
  - Rule values: HIGHEST_VALUE, MOST_ASSETS, FEWEST_ASSETS, MOST_LINKS, ENTRY_ADJACENT, LAST_CLAIMED.
  - Home is never exposed. One claimed, non-DOWN node is exposed per raid.
- **Effect:** threat damage to that node's integrity is ×1.5 (rounded up), applied before the 50 % spill, so the spill grows too. Asset integrity and other sources are untouched.
  - Order of modifiers on a hit: Ghost "Slip the Lock" −% first, then ×1.5, then Botnet drones, SANDBOX or Rigger Buffer absorb.
  - Why a multiplier: node integrities run 15-50, so a flat bonus would be trivial on a Firewall and lethal on a Relay.
- **Move (setup only):** slide the ring to an adjacent claimed non-Home node.
  - Cost per hop: 3 Schematics or 2 Heat. Max 2 hops; the second hop costs double.
  - The Heat option is illegal if it would cross a Heat threshold (it would queue a raid) or reach 100.
  - A move is committed and saved. Setup has no RNG, so no rewind is needed.
- **Decision:** defend it, move it to a node the routing reaches late, or sacrifice a cheap node (a Decoy on the exposed node pulls threats onto the damage you have already priced in).

### R2 Encrypted routes

- **Hidden:** which of the three legal routing rules (SHORTEST_TO_HOME, HIGHEST_VALUE, WEAKEST_NODE) a threat follows.
  - Species, stats, entry point and wave-2 composition are always visible.
  - Routing is a hash of (campaign seed, raid id, threat index), computed when the raid is built and stored. It is not an RNG stream.
- **Bands:**

| Band | Encrypted threats |
|---|---|
| NOTICED | none |
| FLAGGED | the highest-damage threat of each wave |
| HUNTED | all |
| PURGE | all; paid decrypts cost 2 |

- **Preview (BLOCKER fix):**
  - Every decrypted threat is exact.
  - Each encrypted threat draws its 3 candidate routes dashed.
  - A node's outcome is a hatched interval, "best … worst". The preview runs the resolver over every routing combination (3^k combinations for k encrypted threats; k is capped at 6, so at most 729 pure sims).
  - The result is guaranteed to lie inside the interval, and the interval collapses to the exact result as threats are decrypted.
  - Floor: every raid grants at least 1 free decrypt, so the preview is never fully blind.
- **Decrypt sources:**
  - Ghost-class operative stationed on a Safehouse: 1 free.
  - Intel Exploit held: 2 free.
  - Otherwise 1 Schematic per threat (2 at PURGE).
  - The player chooses which threat each free decrypt opens.
  - Decrypts are committed and saved.
- **Cost:** at most 6 Schematics per raid. It is an information tax, not a sink.

### R3 Vehicle types

`ThreatData.vehicle` enum: GROUND (default, so old files load), LANDER, FLYING, HEAVY.

| Vehicle | HP (base, before Heat scaling) | Speed (edges/step) | Route behavior | Counter | Tier availability |
|---|---|---|---|---|---|
| GROUND | 10-30 | 1-2 | Enters at the corporate Site, obeys holds | ICE Lock, Tar Pit, any fire | T1-T4 |
| FLYING | 6-14 | 2 | Never held by ICE Lock or Tar Pit; frozen edges still apply | Flak (3 shots), Sentry, Mesh chips, Decoy pull | T2+ (1 per raid at NOTICED) |
| HEAVY | 26-40 | 1 | Obeys holds; takes half damage from TURRET-type asset shots (min 1 per shot) | ICE Lock + Tar Pit stall; Railgun (`ignores_heavy_armor`); station strikes and Pierce | T2+ (1 per raid at NOTICED) |
| LANDER | 10-12 | 1 | Skips the entry; drops at `arrival_step` (default 2) onto the claimed non-Home node its own routing picks, steered by Decoy / Honeypot. Held normally after landing | Cover likely drop nodes; Decoy steer; Phantom SANDBOX | T3+ (T2 allowed in FLAGGED) |

- "Turret damage" = every asset with `asset_type = TURRET`, including the Firewall built-in.
- Station strikes (Breaker volley, Wrecker Strike, Ghost reduction) are not turret damage, so HEAVY halving never applies to them. The triangle stays "stall / shoot / cover".
- Retag existing threats data-only. Verify corporation ownership against the files; the round-1 retag list was inferred.
- New threat ids are placeholders, to be authored in each corp pass. Aurelian and Tethys rosters wait for their corp passes (Q).

### R4 Second wave and ULTIMATUM (the Schematics sink)

**Heat scaling table** (tier T = raid tier; reward R_T = 8 / 12 / 18 / 25):

| Band | Wave 2 | Wave 2 budget vs wave 1 | Encrypted | Ultimatum |
|---|---|---|---|---|
| NOTICED | none | n/a | none | no |
| FLAGGED | reinforcements | ≤ 50 % | top threat | yes |
| HUNTED | reinforcements + one non-GROUND | ≤ 75 % | all | yes |
| PURGE | mandatory existing wave 2 | per file | all | no ("no deal") |

Budget = Σ(integrity + 3 × damage). Wave 2 is authored per band as a `RaidWaveData`, never generated.

**Timing:** wave 2 spawns at `spawn_step` = 10, or the step after wave 1 is fully dead if earlier. It uses the same defenses and does not reopen setup. `raid_purge` already has two waves; verify spawn timing in the resolver before relying on it. Fallback: plain extra wave, no cancel.

**Offer (shown after the player has seen wave-2 composition, resolved before Start raid):**

| Option | Cost | Effect |
|---|---|---|
| Pay Schematics | price below | cancels wave 2 |
| Pay Heat | +4 (FLAGGED) / +6 (HUNTED) | cancels wave 2; illegal if it would cross a threshold or reach 100 |
| Refuse | none | wave 2 plays |

**Price formula (Schematics):**

`price = round(R_T × band_factor × (1 + 0.25 × ultimatums_paid)) + surplus_levy`
- `band_factor` = 0.5 FLAGGED, 0.75 HUNTED.
- `ultimatums_paid` counts payments this campaign; the fatigue factor is capped at ×2.0.
- `surplus_levy` = 0.2 × max(0, Schematics held − 60), capped at 30. Shown as "Final Notice: levy on holdings".

**Why it sinks surplus without being mandatory:**
- The baseline player ends with about 191 unspent. About 2.5 of 5.2 raids are FLAGGED or HUNTED (Heat peaks around 84).
  - Typical T3 HUNTED price: 14, plus a levy of about 26 at 191 held, so about 40 for that raid.
  - Roughly 2.5 payments total is about 90-100 Schematics, about 7 % of income and about half the idle surplus.
  - The round-1 15-25 % target is dropped as too high (it would eat 78 % of a single raid reward). Sim target: 5-8 % of income.
  - A player holding 60 or less pays only the base price.
- The Heat option is always an alternative currency. Refusing is always legal; FLAGGED wave 2 (≤ 50 % budget) is survivable with a good Armory.
- **Refuse-and-hold bonus** (outside any pick): Schematics = 1.25 × base price (no levy, no fatigue), Heat −3, and at HUNTED one Armory asset of rarity ≥ 1. Paying yields none of this.
- **No cascade:** a raid queued by paying Heat has no wave 2.

## 3. How the four interact

### Worked raid: T3 HUNTED, Heat 76 (strength ×1.25, rounded up)

**Network:** Home H 50; Relay R 15; Vault V 20; Firewall F 30 (built-in turret 3); Safehouse S 20; Proxy P 15 (Ghost stationed, dead end off F, off any route). Links: X-R, R-V, R-F, F-H, V-S, S-H, F-P. Rule HIGHEST_VALUE exposes V.

**Wave 1 (base → scaled):** collector 12/5 → 15/7; auditor 8/3 → 10/4; enforcer 25/9 → 32/12; lockdown unit 18/6 → 23/8. Wave 2: bailiff HEAVY 38/13 and 2 dosing drones FLYING 8/3.

1. **R1.** V is exposed. The enforcer (HIGHEST_VALUE) hits V for 12 × 1.5 = 18 per step against 20. V survives one hit and falls on the second.
2. **R2.** All 5 threats are encrypted. The Ghost gives 1 free decrypt and the Intel Exploit 2, so 3 are free. The player opens the enforcer, the bailiff and the lockdown unit, and pays 1 Schematic for the collector. Exact routes: enforcer to V; the rest follow shortest-to-home via F.
3. **Moving the ring.** Moving to S (V and S are linked) costs 3. Threats do not reach S unless V falls and the enforcer survives, so the bonus is wasted. The player instead stacks Sentry (3/step) plus Flak (2 × 3 shots) on V and ICE Lock on R. The enforcer dies at V before it deals its second hit, so the ring never costs V. Nothing was moved.
4. **R3.** The bailiff halves Turret fire (Turret 4 becomes 2, Flak 2 becomes 1). The drones ignore the ICE Lock on R. The player keeps Tar Pit on F for the bailiff and relies on Sentry and Flak for the drones.
5. **R4.** Price = round(18 × 0.75 × 1.0) = 14, levy 0 (the player holds 60, minus the 1 Schematic decrypt = 59). Pay: 59 − 14 = 45; CELL HOLDS adds 18, so 63. Refuse and win: 59 + 18 + round(1.25 × 14) = 94 plus a rarity-1 asset and Heat −3. Refuse and lose: wave 2 plus the bailiff hammers F, F goes DOWN, and repair costs about half its install cost.

### Failure modes and dominated plays

| Failure / dominated play | Why it fails | Guard |
|---|---|---|
| Always pay Heat | Each payment raises Heat by 4-6, which pushes the next band and queues raids | Illegal across thresholds; no wave 2 on queued raids |
| Always refuse | Wave 2 without cover costs repairs and BREACH risk | Refusal reward is real; sim target refuse ≈ 20-35 % |
| Spotlight on a dead end every time | Costs 3 per hop; the move is to a node the routing reaches late | Only works if routes are known (R2 decrypt) |
| Ignore R2 and plan for worst case | Over-defends one node | Interval shows best and worst; decrypt cost is 1-2 |
| Pure turret Armory | HEAVY halves it, FLYING ignores holds | Mixed raids from FLAGGED up |
| Pure stall Armory | FLYING and LANDER bypass it | Same |
| Sacrifice a node adjacent to Home | The spill bleeds Home | Spill from an exposed node to Home is capped at the original 50 % of the unmultiplied damage (Q) |

**Station bonuses:**
- Phantom SANDBOX negates a whole exposed hit.
- Rigger Buffer absorbs after the ×1.5.
- Botnet drones absorb a hit each; the multiplier only applies to damage that reaches node integrity.

## 4. Preview and determinism

- Setup shows each node's exact outcome for decrypted threats, and a hatched interval for any encrypted ones.
- It also shows the exposed node ("EXPOSED ×1.5" in the tooltip), vehicle icons, lander drop candidates, wave-2 composition, and ultimatum prices with the Heat crossing.
- **RNG:** none in the raid. Raid construction (exposure, hidden routing) is a hash of (campaign seed, raid id, node/threat ids) and is stored in the save. The reward-screen pick uses a named checkpointed stream (`rewards`) if one exists; otherwise a deterministic list.
- **Tests:** fully decrypted, preview equals result exactly; with encrypted threats, result ∈ [best, worst]; same inputs give the same raid; ties break by content id, then node id.

## 5. Data and new systems

| System | Dependency | Fallback | Size |
|---|---|---|---|
| Exposure: `exposure_rule`, ×mult in the damage step, move action | NEW: raid_exposure | none | S-M |
| Encryption: hidden routing, interval preview, decrypt | NEW: raid_encryption | decorative dashes only | M |
| Vehicles: `vehicle`, `arrival_step`, hold immunity, turret halving | NEW: raid_vehicles | none | M |
| Ultimatum: band-gated waves, gate, price curve | NEW: raid_ultimatum | plain extra wave, no cancel | S-M (UI M) |
| Raid-win reward screen (recap, pick 1 of 3) | N18 (raid context), N16 (optional event offer) | existing summary | M |

**Fields:**
- `RaidData`: `exposure_rule`, `ultimatum_allowed`, `no_deal`.
- `RaidWaveData`: `band_min`, `band_max`, `spawn_step`, `is_reinforcement`.
- `ThreatData`: `vehicle`, `arrival_step`.
- `DefenseAssetData`: `ignores_heavy_armor`.
- `CampaignState`: `ultimatums_paid`.

**Config keys:**
- `exposed_damage_mult` = 1.5
- `spotlight_move_cost_schematics` = 3
- `spotlight_move_cost_heat` = 2
- `spotlight_move_max_hops` = 2
- `decrypt_cost_by_band` = [0, 0, 1, 1, 2]
- `ghost_free_decrypts` = 1
- `intel_free_decrypts` = 2
- `heavy_turret_damage_mult` = 0.5
- `ultimatum_band_factor` = {0.5, 0.75}
- `ultimatum_heat_by_band` = {4, 6}
- `ultimatum_fatigue_step` = 0.25
- `ultimatum_fatigue_cap` = 2.0
- `surplus_levy_rate` = 0.2
- `surplus_levy_floor` = 60
- `surplus_levy_cap` = 30
- `wave2_delay_steps` = 10
- `wave2_refuse_reward_mult` = 1.25

## 6. Differences vs the round-1 draft

- **BLOCKER 1 (arithmetic):** rewritten worked raid with stated base stats, consistent per-line Schematics totals and no "net" fudge.
- **BLOCKER 2 (spotlight logic):** the Ghost moved to an off-route Proxy; the ring-to-S move is tested honestly and the player decides not to move.
- **BLOCKER 3 (preview = result):** interval kept but made sound (3^k enumeration, k ≤ 6), with a guaranteed free decrypt floor. Still raised as Q1.
- **MAJOR (wave timing):** marked "verify in the resolver" with a data-only fallback; decrypt is placed before the ultimatum.
- **MAJOR (invented rosters and ids):** vehicle rules kept, but Aurelian and Tethys rosters deferred to their corp passes; the made-up "lite" ids are removed.
- **MAJOR (price):** the 8 / 14 flat anchor is replaced by a tier-reward formula, a fatigue factor and a surplus levy; the sink target falls from 15-25 % to 5-8 %.
- **MAJOR (PURGE / Heat cancel):** PURGE is "no deal"; the Heat cancel is blocked across thresholds and at 100.
- **NIT:** free decrypts are now player-chosen; the `rewards` stream is flagged as unconfirmed; N16 stays optional.
- **Kept:** hash-based hidden routing, the vehicle triangle with the Railgun exemption, the Heat-or-Schematics fork, no-cascade.
- **New:** station-bonus reconciliation and a modifier order.

## 7. Q:

- Q: Is a sound interval preview acceptable under "previews must equal results", or is a fully exact (blind-free) preview required?
- Q: Is the 5-8 % income sink target enough, or should the surplus levy be steeper?
- Q: Should the spill from an exposed node to Home be capped?
- Q: Should Flak get a dedicated anti-air tag?
- Q: What are the Aurelian and Tethys threat rosters and vehicle mixes?
