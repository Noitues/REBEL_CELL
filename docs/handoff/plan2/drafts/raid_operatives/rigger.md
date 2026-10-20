<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__rigger; status ok; tokens in 12466 cache-write 0 cache-read 34418 out 3315; cost $0.032. DRAFT. -->

# Rigger: raid operative design

## 1. Raid role

The Rigger is the **sustain station**. Its netrun kit (RAM, nudges, Perfect refund) has no raid analogue, so the Hub Core and Perfect hook do nothing in a raid. The raid role is the station bonus alone, which already exists in `rigger.tres` as a HEAL of 5 integrity (type 14, target 0) on trigger 12, ON_RAID_START. It is read here as a raid effect and stays behind config. This draft invents no mechanic beyond the unified raid draft, the GDD, and the Q24.1 / Q42 rulings. Where those sources are silent, the simplest option behind config is chosen.

Role:
- **Station bonus ("Field Repair"):** a Rigger stationed on a Safehouse restores integrity to its own node after each wave and when the raid ends. The base amount is scaled by the Rank multiplier (1.0 / 1.25 / 1.5 / 2.0 for ranks 0-3), rounded up.
  - "After each wave" means at the step where wave 1 is fully dead or wave 2 spawns (`spawn_step`), whichever the resolver already uses as the wave boundary. The heal is capped at the node's max integrity.
  - A DOWN node is not healed: a repair needs a node that is not DOWN. A TAKEN node is unaffected.
- **R1 EXPOSED:** the heal comes after the ×1.5 exposure hit, so it offsets a spotlight on the Rigger's own node. It never changes the multiplier. Order on a hit stays: Ghost reduction, ×1.5, absorbers (drone, SANDBOX, Buffer), node integrity. The Rigger heal runs only at wave boundaries and raid end, never mid-step.
- **R2 encrypted routes:** no role. The Rigger grants no decrypts (Ghost 1, Intel 2 remain the only free sources).
- **R3 vehicles:** no role. The heal is not turret damage and is not affected by HEAVY halving.
- **R4 ultimatum:** an indirect role. The wave-boundary heal makes a refused wave 2 more survivable on the Rigger's node, which supports the refusal branch. The Rigger never reduces the Schematics price or the sink, and it is neither paid nor refused on the player's behalf.
- **Placement:** one Rigger per Safehouse slot. Defenses are shared, so the heal covers only the node the Rigger is stationed on. An operative on a Safehouse that goes DOWN or TAKEN returns to the reserves unharmed (GDD 3.3), and the heal stops.
- **Operative safety (Q24.1):** a raid never reduces operative HP. The Rigger takes part in no raid step that targets it.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| config: campaign_config.raid_rigger_heal_base | 5 | integrity points per heal trigger at Rank 0; matches `fx_station` amount (5) |
| config: campaign_config.raid_rigger_rank_mult | [1.0, 1.25, 1.5, 2.0] | multiplier by Rank 0-3; read from `station_bonus_multiplier` in rigger.tres |
| config: campaign_config.raid_rigger_heal_triggers | [wave_end, raid_end] | when the heal fires |
| config: campaign_config.raid_rigger_heal_max_per_raid | 3 | cap on heal triggers per raid (wave 1 end, wave 2 end, raid end) |
| config: campaign_config.raid_rigger_heal_rounding | UP | rounding of the Rank-scaled amount |
| config: campaign_config.raid_step_cap | 30 | steps; existing GDD 7 key, unchanged |
| config: campaign_config.exposed_damage_mult | 1.5 | multiplier; unified draft key, read only for the preview text |
| config: campaign_config.wave2_delay_steps | 10 | steps; unified key; defines the wave boundary when wave 2 exists |
| config: campaign_config.ultimatum_band_factor | {0.5, 0.75} | unified key; the Rigger does not modify it |

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Setup, node tooltip (Rigger stationed) | `Field Repair: +{heal} integrity after each wave and at raid end ({max} max).` (TextDb `raid.rigger.node_tooltip`) | none |
| Setup, node projected outcome | `Projected: {node} {outcome} (repairs included)` (TextDb `raid.rigger.projected`) | none for decrypted threats; for encrypted threats it shows the unified hatched interval, with the heal applied inside each simulated combination |
| Setup, exposed node with Rigger | `EXPOSED x{mult}, Field Repair +{heal}` (TextDb `raid.rigger.exposed_note`) | none |
| Playout, heal event | `{node} repaired +{heal} ({integrity}/{max})` (TextDb `raid.rigger.heal_event`) | none |
| Playout, blocked heal | `{node} is DOWN: no repair` (TextDb `raid.rigger.heal_blocked`) | none |
| Summary | `Field Repair restored {total} integrity this raid.` (TextDb `raid.rigger.summary`) | none |

The heal is pure arithmetic, so nothing it adds is random.

## 4. Tests

| name | tier | assert |
|---|---|---|
| rigger_heal_after_wave | fast | A stationed Rigger's node regains `raid_rigger_heal_base` × rank multiplier, rounded up, at the wave boundary, capped at max integrity |
| rigger_heal_at_raid_end | fast | The heal also fires when the raid ends if the node is not DOWN |
| rigger_heal_rank_scaling | fast | Ranks 0-3 give 5 / 7 / 8 / 10 from the config table |
| rigger_heal_down_node | fast | A DOWN node receives no heal and the blocked-heal line shows |
| rigger_heal_cap_per_raid | fast | No more than `raid_rigger_heal_max_per_raid` heals fire in one raid |
| rigger_exposed_order | fast | On an exposed node the hit is ×1.5, then absorbers, then the heal at the boundary; heal never reduces the multiplier |
| rigger_no_effect_without_station | fast | No Rigger stationed means no heal and no tooltip line |
| rigger_one_node_only | fast | The heal applies only to the Rigger's own node, not adjacent nodes |
| rigger_not_turret | fast | HEAVY half-damage never applies to the heal and the heal is not turret damage |
| rigger_determinism | full | Same seed, graph and placements give identical raid logs and heal totals across 100 seeds |
| rigger_preview_equals_result | full | With all threats decrypted, the projected outcome equals the played result exactly; with encrypted threats, the result lies inside the interval |
| rigger_q24_1_operative_zero_hp | fast | An operative at 0 HP is lost and the active netrun is abandoned; the raid state is unchanged |
| rigger_q24_1_no_raid_kill | fast | No raid step reduces any operative's HP, including the stationed Rigger's |
| rigger_q42_sink_once | fast | The ultimatum Schematics sink is paid at most once per raid regardless of Rigger presence |
| rigger_q42_shared_defenses | fast | Two operatives in the cell see the same defenses; the Rigger adds no per-operative copy |
| rigger_q42_no_resetup | fast | No setup action is available after Start raid; the heal triggers need no player input |
| rigger_numbers_from_config | fast | Changing each config key in section 2 changes behavior; no literal in the heal code path |
| rigger_text_keys | fast | Every string in section 3 resolves in TextDb in US English |

## 5. Binding rule check

- **Q24.1:** The raid never targets or damages operative HP. The station heal affects node integrity only. An operative at 0 HP for any reason is lost and the netrun is abandoned, while the raid state stays as is (tests `rigger_q24_1_*`).
- **Q42 sink:** The Rigger neither charges nor refunds Schematics and never touches the ultimatum price. The sink stays once per raid, owned by the unified draft (`rigger_q42_sink_once`).
- **Q42 shared defenses / no re-setup:** The heal is an existing station effect on the shared network and adds no per-operative defenses. It runs automatically at wave boundaries with no mid-raid input, so setup is never reopened (`rigger_q42_shared_defenses`, `rigger_q42_no_resetup`).

## 6. Q-DESIGNER lines

Q-DESIGNER: Should the Rigger heal also fire mid-wave (every N steps) so a long wave 1 is covered? | DEFAULT: No; wave end and raid end only, capped at 3 heals per raid
Q-DESIGNER: Should the Rigger heal apply to adjacent nodes at half strength? | DEFAULT: No; own node only, to keep shared-defense bookkeeping simple
Q-DESIGNER: Should the heal be allowed on a node that is exposed (R1)? | DEFAULT: Yes; it is applied after the ×1.5 hit and never alters the multiplier
Q-DESIGNER: Should the Rigger count toward the HEAVY or FLYING counters? | DEFAULT: No; the heal is neither turret nor asset damage
