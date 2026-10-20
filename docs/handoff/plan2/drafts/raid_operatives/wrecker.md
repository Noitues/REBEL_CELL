<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__wrecker; status ok; tokens in 12396 cache-write 0 cache-read 34418 out 3211; cost $0.032. DRAFT. -->

# Wrecker: raid operative design

## 1. Raid role

The Wrecker is a Breaker alternative (`alternative_of = breaker`, same deck, a different core). Its `.tres` gives one station bonus: a trigger-12 effect (ON_NETRUN_COMPLETE or ON_RAID_START; the enum int is read from the file at build) with one effect of type 0 (DEAL_DAMAGE), target 0, multiplier 1.5. The Rank scale is ×1.25 / ×1.5 / ×2.0 (`station_bonus_multiplier`). The Hub Core and Perfect hook are not in the excerpt, so **no Hub or Perfect effect is read as a raid effect**. The unified draft's "Wrecker Strike" is the station bonus only, and no new mechanic is added.

**Role: station striker.** The Wrecker is stationed on a Safehouse slot (GDD 3.2 and 5.4). In the playout, step 3 (assets fire), it fires one strike per step at the first threat in range on its node. This is a bonus on top of asset fire.
- **Strike:** damage = `base_strike_damage` × the Rank multiplier, rounded up, min 1. It fires at most `strikes_per_step` times per step, in range `strike_range_hops`.
- **Targeting:** the threat with the highest remaining integrity within range; ties break by threat id, then node id. This is deterministic and needs no RNG.
- **Not turret damage:** per the unified draft, the strike ignores HEAVY halving (R3). It is not an asset, so it is not an ICE Lock or Tar Pit target and cannot be destroyed by threats.
- **Touches R3:** this is the Wrecker's counter to HEAVY threats.
- **Touches R1:** none directly. Placing the Wrecker's Safehouse in the spotlight is a setup choice (the player may move the ring there at the normal cost). No special rule.
- **Touches R2:** none (that is the Ghost's role).
- **Touches R4:** none. The Schematics sink is paid once per raid, by the player.
- **Setup:** the Wrecker adds a "strike coverage" overlay: the nodes in range of its Safehouse. Nothing is placed or paid for it.
- **Safety:** the Wrecker is never a target in a raid. Threats damage nodes, not operatives. If the Safehouse goes DOWN or TAKEN, the operative returns to the reserves unharmed (GDD 3.3) and stops striking. The netrun is unaffected.
- **Simplest choice:** the sources give only "multiplier 1.5 on a DEAL_DAMAGE", so the base damage and range are config placeholders tuned by the sim.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| `config: campaign_config.raid_wrecker_base_strike_damage` | 4 | damage per strike before the Rank multiplier |
| `config: classes/wrecker.station_bonus_multiplier` (Rank 0 / 1 / 2 / 3) | 1.0 / 1.25 / 1.5 / 2.0 | multiplier; the Rank 0 value comes from the effect's own `multiplier = 1.5` in the file, to be reconciled (Q-DESIGNER 1) |
| `config: campaign_config.raid_wrecker_strikes_per_step` | 1 | strikes per raid step |
| `config: campaign_config.raid_wrecker_strike_range_hops` | 1 | hops from the stationed node |
| `config: campaign_config.raid_wrecker_min_damage` | 1 | damage; floor after rounding |
| `config: campaign_config.heavy_turret_damage_mult` | 0.5 | exists in the unified draft; the Wrecker strike is exempt |
| `config: campaign_config.raid_step_cap` | 30 | steps (GDD 7) |
| `config: campaign_config.raid_wrecker_stationed_max` | 1 | Wrecker strikes per raid; one station slot gives one strike line |

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Setup, node tooltip (Safehouse with the Wrecker) | `Wrecker strike: {damage} per step, range {hops} hop(s)` (`raid.wrecker.strike_tooltip`) | none |
| Setup, coverage overlay | `In strike range: {node_list}` (`raid.wrecker.coverage`) | none |
| Setup, projected node outcome | `{node}: {HOLDS/DOWN/TAKEN}, strike deals {total} over the raid` (`raid.wrecker.outcome`) | when threats are encrypted (R2): the total is shown as `{best}-{worst}`; routes are the only unknown, and no part of the strike itself is random |
| Setup, HEAVY threat line | `Strike ignores armor: full {damage}` (`raid.wrecker.heavy_note`) | none |
| Playout log | `Wrecker strikes {threat} for {damage}` (`raid.wrecker.log_hit`) | none |
| Playout log, node lost | `Safehouse down: the Wrecker is safe and pulled back` (`raid.wrecker.pulled_back`) | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| strike_damage_by_rank | fast | the strike equals ceil(base × the Rank multiplier) for Rank 0-3, min `raid_wrecker_min_damage` |
| strike_targeting | fast | the highest remaining integrity in range is hit; ties break by threat id, then node id |
| strike_range | fast | threats beyond `strike_range_hops` are not hit; threats in range are |
| strike_in_step_3 | fast | the strike resolves in the asset-fire step, before threats damage nodes |
| strike_ignores_heavy_armor | fast | a HEAVY threat takes full strike damage while turret shots are halved |
| strike_not_destroyable | fast | no threat step targets the Wrecker; the strike is not an asset |
| safehouse_down_stops_strike | fast | once the Safehouse is DOWN or TAKEN the strikes stop; the operative is reserved, unharmed, HP unchanged |
| one_strike_line | fast | with two Wreckers stationed the cap `raid_wrecker_stationed_max` applies; extra strikes are refused with a reason |
| determinism | full | the same seed, graph and placements give an identical raid log over 100 seeds |
| preview_equals_result | full | fully decrypted: the previewed strike total equals the played total; with encrypted threats, the result lies in [best, worst] |
| q24_1_zero_hp | fast | an operative at 0 HP (from a netrun) is lost and the netrun is abandoned; the raid state is unchanged |
| q24_1_never_killed_in_raid | full | across a sweep of raids, no raid step reduces any operative's HP or marks one dead |
| q42_sink_once | fast | the ultimatum Schematics are charged at most once per raid; the Wrecker adds no charge |
| q42_shared_defenses | fast | every operative defends the same network; the Wrecker's strike uses the shared graph with no per-operative copy |
| q42_no_resetup | fast | stationing, strike config and placements are refused mid-raid with a reason |
| numbers_from_config | fast | all values load from config; a changed key changes the result and no literal appears in the code path |

## 5. Binding rule check

- **Q24.1:** the Wrecker's raid role only deals damage to threats. No raid step reads or writes operative HP; a Safehouse loss returns the operative unharmed (GDD 3.3). An operative at 0 HP is a netrun matter: it is lost and the netrun is abandoned, and the raid is unchanged (`q24_1_zero_hp`, `q24_1_never_killed_in_raid`).
- **Q42 sink:** the Wrecker adds no cost or sink. The ultimatum remains one payment per raid, made at setup by the player (`q42_sink_once`).
- **Q42 shared defenses / no re-setup:** the strike works on the one shared network, with no per-operative copy of assets or nodes. Stationing and strike settings lock when the raid starts (`q42_shared_defenses`, `q42_no_resetup`).

## 6. Q-DESIGNER lines

Q-DESIGNER: Does the file's `multiplier = 1.5` mean the Rank 0 strike is ×1.5 of the base, or is it ×1.0 with the Rank scale applied on top? | DEFAULT: Rank 0 is ×1.0, Ranks 1-3 are ×1.25 / ×1.5 / ×2.0, and the 1.5 stays a netrun-only value
Q-DESIGNER: Should the strike start at 4 damage, which is about half a T1 asset shot? | DEFAULT: 4, to be tuned by the sim so the Wrecker never replaces a Turret
Q-DESIGNER: Should a stationed Wrecker's strike range grow with Rank? | DEFAULT: no, range stays 1 hop; only damage scales with Rank
Q-DESIGNER: Should the Wrecker strike also hit a LANDER on arrival, before its first hold? | DEFAULT: yes, if it lands in range; it follows the normal range rule with no special case
