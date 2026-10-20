<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__botnet; status ok; tokens in 12554 cache-write 34418 cache-read 0 out 3116; cost $0.071. DRAFT. -->

# Botnet: raid operative design

## 1. Raid role

The Botnet is the cell's **"free body" operative**. Its netrun kit (drones that soak hits, Trojan slices, Parasite drones that halve enemy output) has no live raid analogue, because wheel mechanics exist only in combat (GDD pillar 4). In a raid it contributes only its **station bonus**, plus a tie-in to the existing "drones absorb a hit each" line in the unified draft §3. Role: **cheap, steady asset volume and R1 hit-absorption insurance. It does nothing for R2 information and nothing for R4 pricing.**

Rules (numbers are in section 2):
1. **Station asset (setup).** A Botnet stationed on a node places one free TURRET asset on that node for the raid (the station bonus: "node gains one free asset per raid"; `.tres` `DEPLOY_DRONE` amount 1, via `config.station_deploy_asset`). The asset is a normal `DefenseAssetData` and uses the existing assets rules. It does not count against the Armory cap. It is shown in setup like any placed asset and is removed after the raid. It is a TURRET, so HEAVY halving (R3) applies to its shots.
2. **Rank scaling.** The `.tres` rank rewards give `station_bonus_multiplier` 1.25 / 1.5 / 2.0. Simplest reading behind config: the multiplier scales the free asset's damage (rounded, minimum 1 added). It does not add more assets.
3. **Shared defenses.** The free asset sits on the stationed node, but it is part of the shared network defense. It fires at threats within its range, like every asset. There is no per-operative copy.
4. **Drone soak (R1 touch).** The Botnet's drones are the "drones absorb a hit each" case. The simplest role behind config: while a Botnet is stationed on the exposed node, the first `raid_botnet_exposed_soak_hits` threat hits on that node are absorbed by the station asset before ×1.5 applies to node integrity. This reuses the unified draft's modifier order (×1.5, then drones absorb). It is one hit per raid and removes the asset's integrity by the hit's damage.
5. **R2, R4.** None. The Botnet gives no free decrypt, does not change the ultimatum price, and does not pay the sink. It is stationed in the cell and defends; the player pays the sink.
6. **Q24.1.** A raid never damages, kills or removes an operative. The stationed Botnet returns to reserves unharmed if its node goes DOWN or TAKEN (GDD 3.3). Its HP is not read in the raid. If the Botnet's HP is 0 at any time, it is lost and the netrun is abandoned. The raid is unchanged.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| config: campaign_config.station_deploy_asset | the existing turret asset id (the `.tres` `fx_station` asset) | content id, unchanged |
| config: campaign_config.raid_botnet_station_assets | 1 | free assets per raid on the stationed node |
| config: campaign_config.raid_botnet_rank_mult | 1.0 / 1.25 / 1.5 / 2.0 (rank 0-3) | multiplier on the free asset's damage, read from the `.tres` `station_bonus_multiplier` |
| config: campaign_config.raid_botnet_exposed_soak_hits | 1 | threat hits absorbed per raid when stationed on the EXPOSED node |
| config: campaign_config.raid_botnet_soak_counts_armory | 0 | free asset counts against the Armory cap (0 = no, 1 = yes) |
| config: campaign_config.exposed_damage_mult | 1.5 | existing key (R1); read only |
| config: campaign_config.heavy_turret_damage_mult | 0.5 | existing key (R3); applies to the free asset |

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Setup, node tooltip (stationed Botnet) | `raid.botnet.station` = "Botnet station: +{assets} free turret ({damage} damage)" | none |
| Setup, exposed node with Botnet | `raid.botnet.soak` = "Botnet soak: absorbs {hits} hit before EXPOSED ×{mult}" | none |
| Setup, projected outcome | `raid.botnet.outcome` = "{node}: {outcome} (Botnet turret counted)" | the outcome is shown as an interval when any threat is still encrypted (R2); the Botnet adds no "?" |
| Raid summary | `raid.botnet.summary` = "Botnet station turret: {kills} kills, {absorbed} damage absorbed" | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| botnet_station_places_asset | fast | A stationed Botnet adds exactly `raid_botnet_station_assets` TURRET asset on its node at raid start. |
| botnet_asset_not_in_armory_cap | fast | With the Armory at 6/6, the free asset still places and the Armory count is unchanged. |
| botnet_rank_scaling | fast | The free asset's damage at ranks 0-3 equals base × `raid_botnet_rank_mult`, rounded, with a minimum of base. |
| botnet_asset_removed_after_raid | fast | After the raid ends, the free asset is gone and the Armory is unchanged. |
| botnet_heavy_halving | fast | Against a HEAVY threat, the free asset's shot is halved (minimum 1). |
| botnet_exposed_soak | fast | On the exposed node, the first `raid_botnet_exposed_soak_hits` hit is absorbed before ×1.5; the next hit takes ×1.5. |
| botnet_soak_only_on_exposed | fast | On a non-exposed node, no soak applies. |
| botnet_no_r2_r4_effect | fast | The decrypt count, ultimatum price and wave-2 composition are identical with and without a Botnet stationed. |
| botnet_determinism | full | Same seed, graph and placements give the same raid result across 100 runs. |
| botnet_preview_equals_result | full | With all threats decrypted, the previewed outcome equals the resolved outcome for the Botnet's node; with encrypted threats, the result lies in the interval. |
| botnet_q24_1_netrun_lost | fast | An operative at 0 HP is lost and the active netrun is abandoned; the raid state is unchanged. |
| botnet_q24_1_no_raid_kill | fast | No raid step changes any operative's HP or removes any operative; a stationed Botnet on a DOWN or TAKEN node returns to reserves unharmed. |
| botnet_q42_sink_once | fast | The Schematics sink is paid at most once per raid; the Botnet's presence does not add a payment. |
| botnet_q42_shared_defenses | fast | The free asset defends the shared network (fires at threats in range on any node); no per-operative copy exists. |
| botnet_q42_no_resetup | fast | After Start raid, the free asset cannot be moved or re-placed. |
| botnet_numbers_from_config | fast | Changing each key in section 2 changes behavior, and no literal number appears in the role code. |

## 5. Binding rule check

- **Q24.1:** The raid reads no operative HP and applies no damage to operatives. A stationed Botnet whose node goes DOWN or TAKEN returns to reserves unharmed. An operative at 0 HP at any time is lost and the netrun abandoned, with the raid unchanged; `botnet_q24_1_netrun_lost` and `botnet_q24_1_no_raid_kill` check this.
- **Q42 sink:** The Botnet adds no Schematics cost, discount or second payment. The ultimatum price is unchanged by it (`botnet_no_r2_r4_effect`, `botnet_q42_sink_once`).
- **Q42 shared defenses / no re-setup:** The free asset is a normal asset in the shared network defense, not a per-operative copy. It is placed during setup and locked at Start raid (`botnet_q42_shared_defenses`, `botnet_q42_no_resetup`).

## 6. Q-DESIGNER lines

Q-DESIGNER: Should the exposed-node soak (rule 4) exist, or should the Botnet be only the free turret? | DEFAULT: keep it, 1 hit per raid, so the Botnet has a visible R1 role
Q-DESIGNER: Should rank scaling raise the free asset's damage or the number of free assets? | DEFAULT: damage only (1.0 / 1.25 / 1.5 / 2.0), one asset
Q-DESIGNER: Should the free asset count against the Armory cap of 6? | DEFAULT: no, it is a station bonus
Q-DESIGNER: Should the free asset always be a TURRET (halved by HEAVY), or may the player pick another type? | DEFAULT: always the existing turret asset, so the triangle stays "stall / shoot / cover"
