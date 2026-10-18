# N2 band table and HP migration sheet

Built by the N2 slice (W0 N2, 2026-10-18) from `docs/handoff/plan2/CONTENT_DESIGN_V2.md` R1 / R2 and the
`hp` of every `content/enemies/*.tres` at base sha 4c77abb4. **Nothing here is applied to content:** N2 adds the
fields, the tables and the lint; every enemy stays on the legacy multiplier until the direct-design (re-author)
pass sets `hp_by_tier` / `hp_bands`. The migration column is a proposal for that pass.

## 1. Band table (R2; lives in `content/config/campaign_config.tres`, `hp_band_*`)

| Class (phases) | T1 | T2 | T3 | T4 | Config field |
|---|---|---|---|---|---|
| Normal (1) | 28-36 | 34-44 | 44-56 | 56-70 | `hp_band_normal` |
| Elite (2) | 56-72 | 68-88 | 88-112 | 112-144 | `hp_band_elite` |
| Mini-boss (2) | 56-72 | 68-88 | 88-112 | n/a (entry 0; T4 reads T3) | `hp_band_mini_boss_2` |
| Mini-boss (3) | 85-105 | 104-128 | 132-162 | n/a (entry 0; T4 reads T3) | `hp_band_mini_boss_3` |
| Boss (4-5) | n/a | n/a | n/a | `hp_bands` by ICE zone; sum of phase budgets (~300 Genome Core) | lint warning only (Q29) |

- Phase budget (R2, `HpBandLint.phase_budget`): (`reference_dpt_by_tier[t]` [9, 11, 14, 18] x needles - sustain per
  turn) x `target_turns_per_phase` 3.5, floored. Genome Core: P1 (18 - 3) x 3.5 = 52; P2 42; P3 / P4 105.
- Boss budget ceiling (warning only): phases x the T4 two-needle budget (126) = 504 for 4 phases.
- Damage table `enemy_damage_by_tier` = [1.0, 1.3, 1.69, 2.2] (output only). Legacy HP fallback
  `enemy_hp_scale_by_tier` = [1.0, 1.6, 2.56, 4.096] (today's 1.6^(t-1); only for enemies with no table).
- Mini-boss band class = phase entries + 1, held to 2..3. Today every mini-boss has 3 phase entries (4 phases) and
  reads the 3-phase band; the phase counts below are the CONTENT_DESIGN_V2 section 3 targets.

## 2. Every enemy: current HP and the proposed migration

Migration rule (proposal): rank-preserving. An enemy's place in its class's current HP range (normal 25-72, elite 106-154, mini-boss 150-170) maps linearly onto the band at each tier. Satellites and drones have no R2 band and keep the host's legacy multiplier.

| Enemy | Class | Current hp | Today T1 / T2 / T3 / T4 (legacy) | Proposed `hp_by_tier` |
|---|---|---|---|---|
| billing_daemon | normal | 42 | 42 / 67 / 108 / 172 | [31, 38, 48, 61] |
| care_swarm | normal | 25 | 25 / 40 / 64 / 102 | [28, 34, 44, 56] |
| cargo_hauler | normal | 72 | 72 / 115 / 184 / 295 | [36, 44, 56, 70] |
| cell_informant | normal | 46 | 46 / 74 / 118 / 188 | [32, 38, 49, 62] |
| collections_agent | normal | 40 | 40 / 64 / 102 / 164 | [31, 37, 48, 60] |
| compliance_officer | normal | 50 | 50 / 80 / 128 / 205 | [32, 39, 50, 63] |
| conveyor_warden | normal | 54 | 54 / 86 / 138 / 221 | [33, 40, 51, 65] |
| customs_scanner | normal | 50 | 50 / 80 / 128 / 205 | [32, 39, 50, 63] |
| dead_drop | normal | 48 | 48 / 77 / 123 / 197 | [32, 39, 50, 63] |
| dosage_dispenser | normal | 38 | 38 / 61 / 97 / 156 | [30, 37, 47, 60] |
| drone_dispatcher | normal | 44 | 44 / 70 / 113 / 180 | [31, 38, 49, 62] |
| echo_process | normal | 52 | 52 / 83 / 133 / 213 | [33, 40, 51, 64] |
| ground_control | normal | 52 | 52 / 83 / 133 / 213 | [33, 40, 51, 64] |
| handler_proxy | normal | 64 | 64 / 102 / 164 / 262 | [35, 42, 54, 68] |
| launch_pad | normal | 46 | 46 / 74 / 118 / 188 | [32, 38, 49, 62] |
| loyalty_test | normal | 54 | 54 / 86 / 138 / 221 | [33, 40, 51, 65] |
| mirror_script | normal | 50 | 50 / 80 / 128 / 205 | [32, 39, 50, 63] |
| orbital_debris | normal | 62 | 62 / 99 / 159 / 254 | [34, 42, 53, 67] |
| parking_warden | normal | 48 | 48 / 77 / 123 / 197 | [32, 39, 50, 63] |
| patrol_unit | normal | 54 | 54 / 86 / 138 / 221 | [33, 40, 51, 65] |
| permit_office | normal | 46 | 46 / 74 / 118 / 188 | [32, 38, 49, 62] |
| route_optimizer | normal | 48 | 48 / 77 / 123 / 197 | [32, 39, 50, 63] |
| surveillance_mast | normal | 44 | 44 / 70 / 113 / 180 | [31, 38, 49, 62] |
| tariff_collector | normal | 53 | 53 / 85 / 136 / 217 | [33, 40, 51, 64] |
| tracking_station | normal | 48 | 48 / 77 / 123 / 197 | [32, 39, 50, 63] |
| transit_controller | normal | 50 | 50 / 80 / 128 / 205 | [32, 39, 50, 63] |
| triage_unit | normal | 45 | 45 / 72 / 115 / 184 | [31, 38, 49, 62] |
| uplink_relay | normal | 46 | 46 / 74 / 118 / 188 | [32, 38, 49, 62] |
| utility_meter | normal | 56 | 56 / 90 / 143 / 229 | [33, 41, 52, 65] |
| weather_satellite | normal | 44 | 44 / 70 / 113 / 180 | [31, 38, 49, 62] |
| claims_adjuster | elite | 112 | 112 / 179 / 287 / 459 | [58, 70, 91, 116] |
| geostationary_guard | elite | 145 | 145 / 232 / 371 / 594 | [69, 84, 108, 138] |
| last_mile_enforcer | elite | 132 | 132 / 211 / 338 / 541 | [65, 79, 101, 129] |
| port_authority | elite | 144 | 144 / 230 / 369 / 590 | [69, 84, 107, 137] |
| rc_template_elite | elite | 150 | 150 / 240 / 384 / 614 | [71, 86, 110, 141] |
| rc_template_elite_b | elite | 150 | 150 / 240 / 384 / 614 | [71, 86, 110, 141] |
| recall_unit | elite | 106 | 106 / 170 / 271 / 434 | [56, 68, 88, 112] |
| riot_control | elite | 142 | 142 / 227 / 364 / 582 | [68, 83, 106, 136] |
| station_commander | elite | 154 | 154 / 246 / 394 / 631 | [72, 88, 112, 144] |
| zoning_board | elite | 132 | 132 / 211 / 338 / 541 | [65, 79, 101, 129] |
| account_manager | mini-boss-2 | 150 | 150 / 240 / 384 / 614 | [56, 68, 88, 0] |
| city_manager | mini-boss-3 | 150 | 150 / 240 / 384 / 614 | [85, 104, 132, 0] |
| logistics_director | mini-boss-3 | 150 | 150 / 240 / 384 / 614 | [85, 104, 132, 0] |
| mission_director | mini-boss-3 | 150 | 150 / 240 / 384 / 614 | [85, 104, 132, 0] |
| the_handler | mini-boss-3 | 170 | 170 / 272 / 435 / 696 | [105, 128, 162, 0] |
| civic_core | boss | 360 | 360 / 576 / 922 / 1475 | `hp_bands` pending its direct design (sum of phase budgets); placeholder = Genome Core bands |
| commons_array | boss | 420 | 420 / 672 / 1075 / 1720 | `hp_bands` pending its direct design (sum of phase budgets); placeholder = Genome Core bands |
| dispatch_core | boss | 460 | 460 / 736 / 1178 / 1884 | `hp_bands` pending its direct design (sum of phase budgets); placeholder = Genome Core bands |
| renewal_engine | boss | 360 | 360 / 576 / 922 / 1475 | `hp_bands` 1.00: 300, 1.15: 330, 1.30: 360, 99: 400 (CONTENT_DESIGN_V2 section 2) |
| the_manifest | boss | 400 | 400 / 640 / 1024 / 1638 | `hp_bands` pending its direct design (sum of phase budgets); placeholder = Genome Core bands |
| botnet_drone | satellite | 5 | 5 / 8 / 13 / 20 | none (no R2 band; inherits the host's scale) |
| care_drone | satellite | 4 | 4 / 6 / 10 / 16 | none (no R2 band; inherits the host's scale) |
| civic_drone | satellite | 5 | 5 / 8 / 13 / 20 | none (no R2 band; inherits the host's scale) |
| collections_drone | satellite | 5 | 5 / 8 / 13 / 20 | none (no R2 band; inherits the host's scale) |
| courier_drone | satellite | 5 | 5 / 8 / 13 / 20 | none (no R2 band; inherits the host's scale) |
| echo_drone | satellite | 5 | 5 / 8 / 13 / 20 | none (no R2 band; inherits the host's scale) |
| orbital_drone | satellite | 5 | 5 / 8 / 13 / 20 | none (no R2 band; inherits the host's scale) |
| seed_drone | satellite | 1 | 1 / 2 / 3 / 4 | none (no R2 band; inherits the host's scale) |

Counts: normal 30, elite 10, mini_boss_2 1, mini_boss_3 4, boss 5, satellite 8; total 58.
