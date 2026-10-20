<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__breaker; status ok; tokens in 12675 cache-write 0 cache-read 34418 out 3296; cost $0.033. DRAFT. -->

# Breaker: raid operative design

## 1. Raid role

The Breaker's netrun kit (spin cards, Perfect double resolve, Overdrive) has no raid analogue. Its raid role is the GDD station bonus only: **a stationed Breaker adds +50 % damage to every asset on its node.** Rank scales the bonus through `station_bonus_multiplier` in `breaker.tres`. The Hub Core passive (+1 spin on cards) has no raid effect; the input does not support one, so none is invented.

- **Where it acts:** the playout, step 3 (assets fire). The bonus raises the damage of each asset shot fired from the Breaker's node. It applies to `asset_type` TURRET, including the Firewall Relay built-in turret. ICE Lock and Decoy deal no damage, so they gain nothing.
- **Station:** the Breaker holds a Safehouse slot, and the bonus applies to the assets of the node that Safehouse sits on (adjacency as in GDD 3.2). It is a setup-phase decision: placing assets and stationing the Breaker are chosen together.
- **R1 EXPOSED:** no direct effect. A strong exposed node benefits from the bonus like any other, which lets the player defend the spotlight node with kill speed instead of paying to move the ring.
- **R2 Encrypted routes:** none. The Breaker gives no free decrypts (that is the Ghost's role).
- **R3 Vehicles:** the bonus is a damage multiplier on turret shots, so it applies **before** the HEAVY halving. HEAVY takes half of the boosted shot (min 1 per shot). A boosted turret is still the weakest answer to HEAVY; ICE Lock plus Tar Pit stall, Railgun or station strikes remain the counters. The bonus never makes a shot ignore holds.
- **R4:** none. The Breaker does not alter the ultimatum price, the wave 2 composition or the refusal reward. It makes refusing safer by raising kill speed on the node that holds the line.
- **Modifier order on a shot:** asset base damage × Breaker multiplier (rounded up) → HEAVY halving (min 1 per shot).
- **Shared defenses:** the bonus is a node property. Any operative in the cell, other classes included, defends the same network; there is no per-operative copy.
- **Operative safety:** the Breaker is never attacked or damaged by raid steps. Stationing does not expose its HP.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| config: campaign_config.raid_breaker_asset_damage_mult | 1.5 | multiplier on each asset shot from the Breaker's node; mirrors the 1.5 on the `fx_station` effect in `breaker.tres` |
| config: breaker.station_bonus_multiplier (rank 0) | 1.0 | rank-scaled bonus factor, read from `ClassData` rank rewards |
| config: breaker.station_bonus_multiplier (rank 1) | 1.25 | scales only the bonus part |
| config: breaker.station_bonus_multiplier (rank 2) | 1.5 | scales only the bonus part |
| config: breaker.station_bonus_multiplier (rank 3) | 2.0 | scales only the bonus part |
| config: campaign_config.raid_breaker_round_mode | UP | rounding of boosted damage (round up, as the R1 multiplier does) |
| config: campaign_config.heavy_turret_damage_mult | 0.5 | HEAVY halving from the unified draft; applied after the Breaker multiplier |
| config: campaign_config.raid_breaker_min_shot | 1 | minimum damage per shot after halving |

Effective multiplier = 1 + 0.5 × station_bonus_multiplier(rank). At rank 0 that is 1.5; at rank 3 it is 2.0. The 0.5 is the base bonus part from `fx_station`.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Setup: Safehouse card with a Breaker stationed | `raid.breaker.station_card`: "Breaker stationed: assets on {node} deal ×{mult}." | none |
| Setup: asset tooltip on the boosted node | `raid.breaker.asset_line`: "{asset}: {base} dmg → {boosted} (Breaker ×{mult})" | none |
| Setup: asset tooltip against a HEAVY threat | `raid.breaker.heavy_line`: "vs HEAVY: {boosted} → {halved} (min {min})" | none |
| Setup: node projected outcome | `raid.breaker.node_outcome`: "{node}: {HOLDS/DOWN/TAKEN} with Breaker bonus" | the outcome shows as a "best ... worst" interval only for encrypted threats (R2) |
| Setup: stationing prompt | `raid.breaker.station_prompt`: "Station Breaker on {safehouse}? Assets on that node deal ×{mult}." | none |
| Playout log | `raid.breaker.shot_log`: "{asset} fires: {damage} (Breaker ×{mult})" | none |

All values are deterministic. Per Q19, only R2 encrypted routing leaves unknown parts.

## 4. Tests

| name | tier | assert |
|---|---|---|
| test_breaker_bonus_applies_to_turret_node | fast | A stationed Breaker multiplies each turret shot at its node by the config multiplier (rounded up) |
| test_breaker_bonus_ignores_non_damage_assets | fast | ICE Lock and Decoy are unchanged |
| test_breaker_bonus_scales_with_rank | fast | Ranks 0-3 give multipliers 1.5 / 1.625 / 1.75 / 2.0 from `station_bonus_multiplier` |
| test_breaker_bonus_only_own_node | fast | Assets on other nodes are unchanged |
| test_breaker_bonus_before_heavy_halving | fast | The boosted shot is halved vs HEAVY, minimum per config |
| test_breaker_bonus_no_hold_bypass | fast | A FLYING threat is still not held by ICE Lock; the bonus does not change holds |
| test_breaker_exposed_node_interaction | fast | On the EXPOSED node, threat damage ×1.5 is unchanged by the Breaker; only asset damage changes |
| test_breaker_unstationed_no_bonus | fast | With the Breaker recalled to the reserves, assets deal base damage |
| test_breaker_raid_deterministic | fast | Same graph, placements, seed and Breaker rank give an identical raid result twice |
| test_breaker_preview_equals_result | fast | With all threats decrypted, the previewed node outcomes and shot damage equal the playout result; with encrypted threats, the result lies in the interval |
| test_breaker_q24_1_zero_hp_lost | fast | A Breaker at 0 HP from any cause is lost and the active netrun abandoned; the raid state is identical to the no-change raid |
| test_breaker_never_killed_by_raid | fast | No raid step reduces any operative's HP, the stationed Breaker included |
| test_breaker_q42_sink_once | fast | With a Breaker stationed, the Schematics ultimatum is charged at most once per raid |
| test_breaker_q42_shared_defenses | fast | Defense state is one per network; any operative's presence reads the same placements |
| test_breaker_q42_no_resetup | fast | After Start raid, placement and station changes are refused |
| test_breaker_numbers_from_config | fast | Changing each config key in section 2 changes behavior; no literal in the raid code path |
| test_breaker_sweep_refuse_rate | full | Over a seed sweep, stationed-Breaker raids show a higher CELL HOLDS rate than unstationed ones at FLAGGED and HUNTED, with refusal share inside the unified draft's sim target |

## 5. Binding rule check

- **Q24.1:** the Breaker has no raid HP exposure. No raid step damages an operative, so the Breaker is never killed in a raid. If it reaches 0 HP elsewhere it is lost and the active netrun is abandoned, and the raid is unchanged (`test_breaker_q24_1_zero_hp_lost`, `test_breaker_never_killed_by_raid`).
- **Q42 sink:** the Breaker neither adds nor removes a Schematics charge. The ultimatum price stays as in the unified draft and is paid once per raid, whatever is stationed.
- **Q42 shared defenses / no re-setup:** the +50 % is a property of the node's assets in the one shared defense, not a per-operative copy. Stationing is fixed when Start raid is pressed, so there is no mid-raid re-setup.

## 6. Q-DESIGNER lines

Q-DESIGNER: Should the Breaker bonus apply to the Firewall Relay built-in turret, or only to placed Armory assets? | DEFAULT: yes, to both, since the built-in is a TURRET-type asset.
Q-DESIGNER: Should HEAVY halving apply after the Breaker multiplier, or should the Breaker's shots ignore it? | DEFAULT: halving applies after the multiplier, so stall and Railgun stay the HEAVY counters.
Q-DESIGNER: Should the rank 0 bonus be 1.5 with no rank scaling in raids? | DEFAULT: no, rank scales it as in `breaker.tres` (1.5 / 1.625 / 1.75 / 2.0).
