# N22: EASY / HARD normal pools (designer ruling Q12, 2026-10-18)

One row per normal-fight enemy (6-slice, not elite / mini-boss / boss). `tests/unit/test_normal_pools_content.gd`
reads the corp, id and pool columns and checks them against the `.tres` (`EnemyData.normal_pool`; HARD is the
default and is not written).

**Rule applied (the proposed one):** EASY = no listeners or locks, at most one status source, per-turn resistance 1
(N21), and a reference-deck sim win rate >= 90 % at T1 with mean HP lost <= 25 %. HARD = everything else.

- *Listener*: an effect on a trigger that reacts to the player (ON_CARD_PLAYED, ON_NUDGE, ON_PERFECT, ON_NULL_SLICE,
  ON_RESOLVE, ON_SATELLITE_DESTROYED) on the hub, a slice, a Firmware or the ring. *Lock*: a FREEZE effect.
  No shipped normal has either.
- *Status source*: a wheel slot (or hub / ring entry) that applies a status (an INFECT slice and its APPLY_STATUS
  count as one source).
- *Sim*: `python tools/balance/balance.py run fight --seeds 1000:1019 -j 1 --chunk 20 --tiers 1 --categories enemy
  --corp <corp>` (builtin policy, Breaker starter, skill 1.0, ICE 0; N19 metrics), main at 54509fb8 + N22.
  Every normal won 20 / 20 with mean HP lost under 25 %, so the sim separates nothing: resistance and status
  sources decide.
- Satellite spawns (column "spawns") are not part of the rule; listed for the designer.

| corp | enemy | pool | resistance | listeners / locks | status sources | sim win % | sim HP lost % (mean) | spawns | reason |
|---|---|---|---|---|---|---|---|---|---|
| halcyon | `parking_warden` | EASY | 1 | none | 1 (slot1:INFECT, slot1:PARASITE) | 100 | 2.9 | 0 | meets every EASY test |
| halcyon | `patrol_unit` | EASY | 1 | none | 0 | 100 | 8.0 | 0 | meets every EASY test |
| halcyon | `permit_office` | EASY | 1 | none | 1 (slot3:INFECT, slot3:PARASITE) | 100 | 9.2 | 1 | meets every EASY test |
| halcyon | `surveillance_mast` | EASY | 1 | none | 1 (slot4:INFECT, slot4:PARASITE) | 100 | 6.4 | 0 | meets every EASY test |
| halcyon | `transit_controller` | EASY | 1 | none | 0 | 100 | 5.3 | 0 | meets every EASY test |
| halcyon | `utility_meter` | EASY | 1 | none | 0 | 100 | 1.8 | 0 | meets every EASY test |
| meridian | `cargo_hauler` | HARD | 2 | none | 0 | 100 | 5.1 | 0 | resistance 2 |
| meridian | `conveyor_warden` | EASY | 1 | none | 1 (slot4:INFECT) | 100 | 4.2 | 0 | meets every EASY test |
| meridian | `customs_scanner` | EASY | 1 | none | 1 (slot1:INFECT) | 100 | 2.7 | 0 | meets every EASY test |
| meridian | `drone_dispatcher` | EASY | 1 | none | 1 (slot4:INFECT) | 100 | 12.0 | 1 | meets every EASY test |
| meridian | `route_optimizer` | EASY | 1 | none | 0 | 100 | 14.8 | 0 | meets every EASY test |
| meridian | `tariff_collector` | EASY | 1 | none | 1 (slot3:INFECT) | 100 | 3.5 | 0 | meets every EASY test |
| orbital | `ground_control` | EASY | 1 | none | 0 | 100 | 5.0 | 0 | meets every EASY test |
| orbital | `launch_pad` | EASY | 1 | none | 1 (slot3:INFECT, slot3:OVERCLOCKED) | 100 | 8.2 | 1 | meets every EASY test |
| orbital | `orbital_debris` | HARD | 2 | none | 0 | 100 | 5.5 | 0 | resistance 2 |
| orbital | `tracking_station` | EASY | 1 | none | 1 (slot4:INFECT, slot4:OVERCLOCKED) | 100 | 5.3 | 0 | meets every EASY test |
| orbital | `uplink_relay` | EASY | 1 | none | 1 (slot1:INFECT, slot1:OVERCLOCKED) | 100 | 3.3 | 0 | meets every EASY test |
| orbital | `weather_satellite` | EASY | 1 | none | 1 (slot4:INFECT, slot4:OVERCLOCKED) | 100 | 5.4 | 0 | meets every EASY test |
| rebel_cell | `cell_informant` | HARD | 1 | none | 2 (slot1:INFECT, slot4:INFECT, slot4:PARASITE) | 100 | 1.1 | 0 | 2 status sources |
| rebel_cell | `dead_drop` | EASY | 1 | none | 1 (slot3:INFECT, slot3:CORRUPTED) | 100 | 12.0 | 1 | meets every EASY test |
| rebel_cell | `echo_process` | HARD | 1 | none | 2 (slot1:INFECT, slot4:INFECT, slot1:CORRUPTED) | 100 | 1.6 | 0 | 2 status sources |
| rebel_cell | `handler_proxy` | HARD | 2 | none | 0 | 100 | 5.7 | 0 | resistance 2 |
| rebel_cell | `loyalty_test` | EASY | 1 | none | 1 (slot4:INFECT, slot4:OVERCLOCKED) | 100 | 1.2 | 0 | meets every EASY test |
| rebel_cell | `mirror_script` | HARD | 1 | none | 2 (slot1:INFECT, slot4:INFECT, slot1:PARASITE, slot4:OVERCLOCKED) | 100 | 1.1 | 0 | 2 status sources |
| solace | `billing_daemon` | EASY | 1 | none | 0 | 100 | 6.0 | 0 | meets every EASY test |
| solace | `care_swarm` | EASY | 1 | none | 0 | 100 | 20.8 | 1 | meets every EASY test |
| solace | `collections_agent` | EASY | 1 | none | 1 (slot3:INFECT, slot3:CORRUPTED) | 100 | 9.7 | 1 | meets every EASY test |
| solace | `compliance_officer` | HARD | 2 | none | 0 | 100 | 8.0 | 0 | resistance 2 |
| solace | `dosage_dispenser` | HARD | 1 | none | 2 (slot0:INFECT, slot2:INFECT, slot0:CORRUPTED, slot2:CORRUPTED) | 100 | 0.2 | 0 | 2 status sources |
| solace | `triage_unit` | EASY | 1 | none | 0 | 100 | 1.5 | 0 | meets every EASY test |

## Per corp

| corp | EASY | HARD |
|---|---|---|
| halcyon | 6 | **0** |
| meridian | 5 | 1 |
| orbital | 5 | 1 |
| rebel_cell | 2 | 4 |
| solace | 4 | 2 |

Every corp has at least 2 EASY normals. **Halcyon has no HARD normal** under the rule: its fights 3+ fall back to
the EASY pool (all six), so Q12 changes nothing there. Meridian and Orbital have one HARD normal each, so every
later Router fight against them is that one enemy (`cargo_hauler`, `orbital_debris`). Open question for the
designer (DECISIONS, "Open questions"): tighten the rule (for example "no status source", a lower sim HP-lost bar,
or count spawns), or move some Halcyon / Meridian / Orbital normals to HARD by hand.
