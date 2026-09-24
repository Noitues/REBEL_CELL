# REBEL_CELL — Data Resource Schemas (GDD §12)

Godot 4 `Resource` classes. Designers author content as `.tres` files in the
Inspector; no code needed except for rule-breaking Daemons (`custom_handler`).
Verified in Godot 4.3 (compile, validation, save/load round trip).

## How the pieces fit

```
WheelData ─┬─ slots[6] → WheelSlotData ─┬─ SliceData
           │                            └─ FirmwareData (optional)
           ├─ hub → HubCoreData (passives + Perfect hook)
           ├─ inner_ring → InnerRingData → RingSegmentData[3]
           └─ pointer_ticks (1+ pointers; bosses can have several)

CardData, DaemonData, FirmwareData, RingSegmentData, HubCoreData,
NetworkNodeData, SliceData
   └─ all describe behaviour as TriggeredEffectData → EffectData[]

SiteData (City Grid)    NetworkNodeData → AdjacencyBonusData
InfiltrationNodeData    DefenseAssetData    ThreatData
RC = shared constants + enums (30 ticks, 6 slices, 3 ring segments)
```

## One effect language
Everything that *does* something uses the same two resources:
- **EffectData** — one atomic action (DEAL_DAMAGE, NUDGE, FLIP, MODIFY_HEAT…).
- **TriggeredEffectData** — *when* it fires (ON_PERFECT, ON_NETRUN_COMPLETE…),
  plus min precision tier, consecutive count, and per-combat limit.

One effect interpreter in `CombatEngine` (and one in the raid resolver) then
covers slices, cards, Firmware, rings, Hubs, Daemons and network nodes.

## Authoring examples
| Content | How it's built |
|---|---|
| Mirror | Firmware, `neighbor_rule = MIRROR` |
| Shunt | Firmware, `neighbor_rule = SHUNT`, `neighbor_multiplier = 1.5` |
| Leech | Firmware, ATTACK only; ON_SLICE_TRIGGER, min GOOD → GAIN_RAM 1 |
| Burner | Firmware, `permanent_status = OVERCLOCKED`; ON_SLICE_TRIGGER → MODIFY_HEAT +1 |
| Echo | Ring segment; ON_SLICE_TRIGGER → RETRIGGER ×0.5 |
| Anchor | Ring segment; ON_PERFECT → FREEZE own wheel |
| Clean Signal | Daemon; ON_PERFECT, consecutive 3 → MODIFY_HEAT −2 (CAMPAIGN) |
| Twin Pointer | Daemon with `custom_handler` (rule-breaker) |
| Proxy Relay | Network node; ON_NETRUN_COMPLETE → MODIFY_HEAT −1 |
| Satellite | WheelData with `slice_count = 3` (10 ticks per slice) |
| 3-pointer boss | WheelData, `pointer_ticks = [0, 10, 20]` |

## Built-in validation
`validate()` returns a list of problems, for use in editor tools or tests:
- Wheel slot count matches `slice_count`, and `slice_count` divides 30.
- Firmware fits its slice type; pointers are within 0–29; ring has 3 segments.
- SPIN / FLIP / RESPIN must hit the whole wheel; NUDGE must hit one ring.
- Heat-reduction Sites must have negative `heat_change`; EXPLOIT Sites need a type.

## Rule: never change a Resource at runtime
Godot shares loaded Resources, so editing one mid-combat changes every copy.
Keep runtime data (wheel position, remaining resistance, statuses, drones,
operative's upgraded wheel) in state objects owned by `CombatEngine` /
`RunManager`. Veterans save their *state*, which references these resources.

## Batch 2: operatives, enemies, campaign, story, profile

```
ClassData ─┬─ starting_wheel → WheelData
           ├─ starting_deck / exclusive_cards → CardData[]
           ├─ station_bonus → TriggeredEffectData[]
           └─ rank_rewards → RankRewardData[] (ring, hub upgrade, segment options)

EnemyData ─┬─ wheel → WheelData (satellites use slice_count 2-3)
           ├─ spawns → SatelliteSpawnData → EnemyData (satellite)
           ├─ phases → BossPhaseData (MULTIPLY / MIGRATE / ORBIT)
           └─ heat_effects → HeatGatedEffectData (active while Heat >= min)

CorporationData ─┬─ city_grid → CityGridData → SiteData[]
                 ├─ enemies / elites / final_boss → EnemyData
                 ├─ exploits → ExploitData (what each does to the breach)
                 ├─ story_paths → StoryPathData → StoryBeatData[]
                 ├─ raids → RaidData → RaidWaveData → ThreatData[]
                 └─ events → TerminalEventData → EventChoiceData[]

CampaignConfigData (one global .tres: all Section 11 tuning)
  ├─ heat_thresholds → HeatThresholdData (one-time events + ongoing modifiers)
  └─ ice_ladder → IceLevelData → RuleModifierData[]

ProfileUnlockData → unlocks ClassData / CorporationData / HomeServerVariantData / …
HomeServerVariantData → core + internal NetworkNodeData, index-pair links
```

| Content | How it's built |
|---|---|
| Solace final boss | EnemyData `is_boss`; phases at 0.66 (MULTIPLY to [0, 15]) and 0.33 (ORBIT 2/turn) |
| Botnet drones | Hub `max_drones = 3`; DEPLOY slice; drone = EnemyData-style satellite wheel |
| Class alternative | ClassData with `alternative_of = &"breaker"`, same deck, new Hub Core |
| Heat 25 threshold | HeatThresholdData MAJOR: `event_raid` + ongoing ENEMY_RESISTANCE +1 |
| ICE 6 | IceLevelData with RuleModifier HEAT_SINK_PCT −15 |
| REBEL_CELL | CorporationData `generated_from_profile = true`; ProfileUnlockData `requires_all_corporations_at_ice = 10` |
| Ghost Patient path | StoryPathData, `foreshadows = &"dispatch"` |
| Intel Exploit | ExploitData `reveals_boss_phases`, `opens_locked_links` |

### Extra validation in batch 2
- **City Grid:** unique ids, links point to real Sites, each T1 opens at most
  one T2, enough Exploit Sites for the breach, boss reachable from home.
  `size_warnings()` flags grids outside 30–40 Sites.
- **Enemies:** boss phases in descending HP order; ORBIT needs a speed.
- **Classes:** Hub Core has a Perfect hook; exclusive cards tagged to the
  class; no duplicate rank rewards.
- **Corporations:** 5–6 story paths, each with enough beats for the minimum
  Exploits; final boss marked as a boss.
- **Config:** Heat thresholds ascending; no duplicate ICE levels.

## Deliberately left to code, not data
- Rule-breaking Daemons and CUSTOM effects (`custom_handler` scripts).
- REBEL_CELL's generator (builds its grid and enemies from profile stats).
- Runtime state and save files (OperativeState, CampaignState, ProfileState).
