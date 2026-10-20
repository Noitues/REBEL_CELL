<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__hivemind; status ok; tokens in 12369 cache-write 0 cache-read 34418 out 2843; cost $0.030. DRAFT. -->

# Hivemind: raid operative design

## 1. Raid role

The Hivemind is a Botnet alternative, so its raid role mirrors Botnet's: a station bonus that adds free defense assets, not a new mechanic. The `.tres` excerpt shows station_bonus as one effect on `trigger = 12` (ON_RAID_START) with `type = 18` (DEPLOY_DRONE) and `amount = 1`, plus `station_bonus_multiplier` 1.25 / 1.5 / 2.0 at Rank 1 / 2 / 3. I read that as "stationed on a node, the operative adds drone guards at raid start". The excerpt does not show the effect's exact wiring, so everything below is the simplest reading, kept behind config. Hivemind is the "never leaves" swarm: more drones, all anchored to its own node.

- **Station bonus (setup/playout):** at ON_RAID_START, the stationed node gains `drones_base` swarm drones. The rank multiplier scales the count, rounded down, minimum 1.
- **R1 EXPOSED:** each drone absorbs one hit before damage reaches node integrity. The unified draft's order puts drones after the ×1.5, and the multiplier applies only to damage that reaches the node. So the swarm protects a node chosen as the spotlight node, and the player can station the Hivemind on the likeliest exposed node instead of paying to move the ring.
- **R2 encrypted routes:** no interaction. The Hivemind grants no free decrypts, and its value does not depend on knowing routes, because drones sit on a fixed node.
- **R3 vehicles:** a drone absorbs one hit from any threat. Its limit is that it is a per-hit absorber with no fire. It does not stall FLYING threats and does not pierce HEAVY armor.
- **R4:** no direct touch. Its drones lower the chance that refusing the ultimatum costs a node.
- **Hub Core passive (drone cap, persistence):** no raid analogue in the sources, so there is none.
- **Defenses are shared and the bonus is local.** Drones live on the stationed node only. They are not copied per operative, and there is no re-setup mid-raid.
- **Raids never kill operatives (Q24.1).** The Hivemind is stationed on a node, not fighting. A node falling returns the operative to the reserves unharmed, per GDD 3.3.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| config: campaign_config.raid_hivemind_drones_base | 3 | drones added at raid start on the stationed node, before the rank multiplier |
| config: content/classes/hivemind.tres.rank_rewards[0].station_bonus_multiplier | 1.25 | Rank 1 multiplier (read from the class file) |
| config: content/classes/hivemind.tres.rank_rewards[1].station_bonus_multiplier | 1.5 | Rank 2 multiplier |
| config: content/classes/hivemind.tres.rank_rewards[2].station_bonus_multiplier | 2.0 | Rank 3 multiplier |
| config: campaign_config.raid_hivemind_drone_hp | 1 | hits a drone absorbs (one hit each) |
| config: campaign_config.raid_hivemind_drone_cap | 8 | max swarm drones on one node after multiplier |
| config: campaign_config.raid_hivemind_persist_steps | 30 | steps drones last (the full raid, `raid_step_cap`) |
| config: campaign_config.raid_step_cap | 30 | existing GDD 7 key |
| config: campaign_config.exposed_damage_mult | 1.5 | existing unified key; applied before drones absorb |

Drone count = min(cap, floor(drones_base × multiplier)). That gives 3 at Rank 0, 3 at Rank 1 (3.75), 4 at Rank 2 (4.5) and 6 at Rank 3.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Node card (setup), stationed | `raid.hivemind.node_swarm`: "Swarm: {n} drones absorb {n} hits" | none |
| Node outcome tooltip | `raid.hivemind.absorb_line`: "Drones absorb {a} of {d} damage. {r} reaches the node." | none (if threats are encrypted, the interval shows through the existing R2 preview) |
| Exposed node | `raid.hivemind.exposed_note`: "EXPOSED x1.5, then drones absorb" | none |
| Station picker | `raid.hivemind.station_pick`: "Hivemind station: +{n} drones at raid start" | none |
| Playout log | `raid.hivemind.drone_lost`: "A drone on {node} is destroyed" | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| swarm_count_by_rank | fast | drone count is min(cap, floor(base × multiplier)) for Ranks 0-3 (3, 3, 4, 6) |
| swarm_cap | fast | a multiplier that would exceed `raid_hivemind_drone_cap` is clamped |
| drone_absorbs_one_hit | fast | each drone absorbs one hit; the next hit damages integrity |
| exposed_order | fast | the ×1.5 applies before drones absorb; multiplier only on damage reaching integrity |
| no_decrypt_or_route_effect | fast | the Hivemind grants no free decrypts and changes no routing |
| vehicle_neutral | fast | drones do not stall FLYING, do not pierce HEAVY armor, and absorb LANDER hits normally |
| local_swarm_only | fast | drones exist only on the stationed node |
| node_down_returns_operative | fast | the stationed node going DOWN or TAKEN returns the operative unharmed to reserves |
| determinism | fast | same seed and placements give identical raid outcomes |
| preview_equals_result | fast | with every threat decrypted, the preview equals the playout result exactly; with encrypted threats the result lies in the interval |
| q24_1_operative_loss | fast | an operative at 0 HP is lost and the active netrun abandoned; the raid itself is unchanged; no raid step reduces an operative's HP |
| q42_sink_once | fast | the ultimatum Schematics payment happens at most once per raid, and Hivemind changes no price |
| q42_shared_defenses | fast | the swarm is part of the shared network defense, with no per-operative copy |
| q42_no_resetup | fast | the swarm cannot be repositioned after Start raid |
| numbers_from_config | fast | every number read in the role comes from config keys in section 2 |
| rank_sweep | full | over 1000 seeds, T3 HUNTED raids with a Hivemind-stationed exposed node show fewer node DOWNs than the same raid without it |

## 5. Binding rule check

- **Q24.1:** the Hivemind only adds drones to a node. No raid step targets an operative, and a node falling returns the operative to reserves unharmed. An operative reaching 0 HP elsewhere is lost and the netrun abandoned without changing the raid (tested).
- **Q42 sink:** the Hivemind adds no Schematics cost, price modifier or second payment. The ultimatum stays once per raid.
- **Q42 shared defenses / no re-setup:** the swarm joins the one network defense, applies to every operative's cell equally, and is fixed once Start raid is pressed.

## 6. Q-DESIGNER lines

Q-DESIGNER: Should drones persist across raids or reset each raid? | DEFAULT: reset each raid, since the Hub's persistence is a netrun rule
Q-DESIGNER: Do swarm drones count as assets toward the Armory cap of 6? | DEFAULT: no, they are a station bonus, not Armory assets
Q-DESIGNER: Should the swarm also absorb the spill damage from a neighboring node? | DEFAULT: no, they guard only hits on their own node
Q-DESIGNER: Is the Hivemind's station bonus different enough from Botnet's, whose bonus is one free asset per raid? | DEFAULT: yes for now, with drones on the node instead of an asset, to be revisited at the station-bonus pass
