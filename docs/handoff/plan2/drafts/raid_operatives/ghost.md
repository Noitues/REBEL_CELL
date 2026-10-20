<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__ghost; status ok; tokens in 12485 cache-write 0 cache-read 34418 out 3433; cost $0.033. DRAFT. -->

# Ghost: raid operative design

## 1. Raid role

The Ghost is the information and delay specialist of the raid. It touches R2 (encrypted routes) and the existing node-defense layer. It has no raid analogue for R1, R3 or R4, so it adds nothing there beyond the shared rules.

Roles, in setup and playout:

- **R2 free decrypt (setup).** A Ghost stationed on a Safehouse grants `ghost_free_decrypts` free decrypts, each chosen by the player. This is the unified draft's source. It is not a new mechanic.
- **Station bonus: "Slip the Lock" (playout).** The class data reads FREEZE amount 1 (rank-scaled). A threat that enters the Ghost's node is held `hold_steps` steps. The hold is applied at step 2 (hold phase), as the existing ICE Lock does.
  - The hold scales by rank through the class `station_bonus_multiplier` (1.0 / 1.25 / 1.5 / 2.0), and the table below gives the resulting steps.
  - **Vehicle interaction (R3).** The hold is a station effect, not an asset. FLYING threats ignore holds from ICE Lock and Tar Pit. As the simplest choice behind config, the Ghost hold also does not affect FLYING (`ghost_hold_affects_flying` = false). HEAVY and LANDER are held normally after landing.
  - **R1 interaction.** If the Ghost's node is the exposed node, the hold still applies before damage. The unified draft's modifier order mentions a "Slip the Lock −%" step. This draft does not use a percent reduction. It uses the delay hold only, because the class data supports a hold and not a percent. The percent reduction in the unified draft is treated as not applying (see Q).
- **Hub Core passive and Perfect hook:** "first nudge ignores resistance" and "strip 2 resistance" are wheel mechanics with no raid analogue. They have no raid effect.
- **R4:** no Ghost effect. The ultimatum price, the levy and the refuse reward are class-blind.

Placement rule: the hold applies only while the Ghost is stationed on the node and the node is claimed and not DOWN. A Ghost stationed on a node that goes DOWN or TAKEN returns to the reserves unharmed (GDD 3.3). Q24.1: no raid step damages, injures or kills an operative. An operative at 0 HP at any time, for any reason, is lost and its netrun is abandoned, while the raid itself is unchanged.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| config: campaign_config.ghost_free_decrypts | 1 | free decrypts per raid; Ghost on a Safehouse (unified key) |
| config: campaign_config.raid_ghost_hold_steps_base | 1 | steps a threat is held on entering the Ghost's node, Rank 0 (class data FREEZE amount) |
| config: content/classes/ghost.tres.rank_rewards[0].station_bonus_multiplier | 1.25 | Rank 1 multiplier (from the class file) |
| config: content/classes/ghost.tres.rank_rewards[1].station_bonus_multiplier | 1.5 | Rank 2 multiplier (from the class file) |
| config: content/classes/ghost.tres.rank_rewards[2].station_bonus_multiplier | 2.0 | Rank 3 multiplier (from the class file) |
| config: campaign_config.raid_ghost_hold_rounding | ceil | rounds base × multiplier to whole steps; yields 1 / 2 / 2 / 2 for Rank 0-3 (see Q) |
| config: campaign_config.raid_ghost_hold_affects_flying | 0 | 0 = no, 1 = yes (FLYING ignores holds) |
| config: campaign_config.raid_ghost_hold_per_threat_once | 1 | 1 = a threat is held at most once per raid by the Ghost node |
| config: campaign_config.raid_ghost_decrypt_node_types | Safehouse | node type where the Ghost grants decrypts |
| config: campaign_config.raid_step_cap | 30 | steps (GDD 7, unchanged) |

Hold arithmetic: steps = ceil(base × multiplier). Rank 0: ceil(1 × 1.0) = 1. Rank 1: ceil(1.25) = 2. Rank 2: ceil(1.5) = 2. Rank 3: ceil(2.0) = 2. The class comment says 1 / 1 / 2 / 2, so `raid_ghost_hold_rounding` is set to floor to match: 1, 1, 1, 2. The default is therefore **floor** (the table row above is corrected here; the class file comment wins). The step values are 1 / 1 / 1 / 2 for Rank 0-3.

(Q below asks the designer to confirm which rounding matches the intended 1 / 1 / 2 / 2.)

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Setup, node tooltip (Ghost stationed) | `raid.ghost.hold`: "Ghost holds each ground threat {steps} step(s) here." | none |
| Setup, node tooltip (flying threat) | `raid.ghost.flying_ignores`: "Flying threats ignore the hold." | none |
| Setup, decrypt panel | `raid.ghost.free_decrypt`: "Ghost: {n} free decrypt(s). Choose a threat." | none |
| Setup, node outcome | `raid.ghost.outcome`: "{node}: {HOLDS/DOWN/TAKEN} (hold included)" | the interval parts for encrypted threats, shown as "?" until decrypted |
| Playout log | `raid.ghost.held`: "{threat} held at {node} for {steps} step(s)." | none |

Nothing about the hold is random. The only "?" parts come from R2 encryption.

## 4. Tests

| name | tier | assert |
|---|---|---|
| hold_steps_by_rank | fast | the hold is 1 / 1 / 1 / 2 steps for Rank 0-3 with floor rounding, read from config |
| hold_applies_on_entry | fast | a ground threat entering the Ghost node waits the configured steps before moving or damaging |
| hold_once_per_threat | fast | the same threat is not held twice at that node |
| hold_ignores_flying | fast | a FLYING threat is not held when `raid_ghost_hold_affects_flying` = 0 |
| hold_heavy_lander | fast | HEAVY and a landed LANDER are held normally |
| hold_not_when_node_down | fast | a DOWN or TAKEN node gives no hold |
| free_decrypt_one | fast | a Ghost on a Safehouse gives `ghost_free_decrypts` decrypts, player-chosen |
| free_decrypt_not_elsewhere | fast | a Ghost on a non-Safehouse node gives no free decrypt |
| exposed_order | fast | on the exposed node the hold applies before the ×1.5 damage |
| determinism | full | the same seed, graph and placements give the identical raid result across 100 raids |
| preview_equals_result | full | with all threats decrypted, the preview equals the result exactly; with encrypted threats, the result lies inside the interval |
| q24_1_operative_zero_hp | fast | an operative at 0 HP is lost and its netrun abandoned; the raid result is unchanged |
| q24_1_no_raid_kill | full | across a sweep, no raid step reduces any operative HP or kills one; a stationed Ghost on a lost node returns to the reserves unharmed |
| q42_sink_once | fast | the Schematics sink is charged at most once per raid |
| q42_shared_defenses | fast | the Ghost hold and defenses apply to the one shared network, not a per-operative copy |
| q42_no_resetup | fast | no placement or station change is accepted after Start raid |
| numbers_from_config | fast | changing each config key changes behavior, with no literals in code |

## 5. Binding rule check

- **Q24.1:** The Ghost's hold and decrypt are setup and playout effects on nodes. No step touches operative HP. A stationed Ghost on a DOWN or TAKEN node returns to the reserves unharmed, and any operative at 0 HP is lost with its netrun abandoned and the raid unchanged (tests `q24_1_*`).
- **Q42 sink:** The Ghost has no Schematics cost or refund. The sink stays class-blind and is paid once per raid under R4; the Ghost's free decrypt only lowers the 1-Schematic decrypt tax and never touches the sink.
- **Q42 shared defenses / no re-setup:** The hold belongs to the shared network node the Ghost is stationed on and benefits every operative's defense equally. The Ghost can be stationed only before Start raid, and no re-setup is allowed after it.

## 6. Q-DESIGNER lines

Q-DESIGNER: Should the Ghost hold round up or down, given the class comment says 1 / 1 / 2 / 2 steps but the multipliers 1.0 / 1.25 / 1.5 / 2.0 do not give that with either rounding? | DEFAULT: use the authored per-rank steps 1 / 1 / 2 / 2 as direct config values instead of a multiplier
Q-DESIGNER: Does the unified draft's "Slip the Lock −%" damage reduction exist, or is the Ghost's raid role only the hold? | DEFAULT: hold only, and the −% line is dropped from the unified draft
Q-DESIGNER: Should the Ghost hold affect FLYING threats? | DEFAULT: no, FLYING ignores the Ghost hold like ICE Lock
Q-DESIGNER: Should the free decrypt need a Safehouse, or work anywhere the Ghost is stationed? | DEFAULT: Safehouse only, as in the unified draft
