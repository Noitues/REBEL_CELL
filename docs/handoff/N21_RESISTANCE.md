# N21 resistance migration (rulings Q16, Q31)

Per-turn resistance = wheel `passive_resistance` + hub `hub_resistance`, before ICE / Heat "+1" and enrage.
Ranges (`campaign_config.tres`): normal 1-2, elite 3-4, mini-boss 3-4, boss 5-6. Rule: in range already = kept;
below = the low end; an authored 2 on an elite / mini-boss (it was the "resistant" one) = the top end, so the
old ordering survives. Satellites (2- and 3-slice wheels) are not fights and keep 0 (open question in DECISIONS).

| enemy | class | old (passive + hub) | new | why |
|---|---|---|---|---|
| billing_daemon | normal | 0 | 1 | low end |
| care_swarm | normal | 0 | 1 | low end |
| cargo_hauler | normal | 2 | 2 | in range |
| cell_informant | normal | 0 | 1 | low end |
| collections_agent | normal | 0 | 1 | low end |
| compliance_officer | normal | 0 + hub 3 | 0 + hub 2 | the hub (Compliance Lock) is the source: hub lowered to the top of the range, flavor kept |
| conveyor_warden | normal | 0 | 1 | low end |
| customs_scanner | normal | 0 | 1 | low end |
| dead_drop | normal | 0 | 1 | low end |
| dosage_dispenser | normal | 0 | 1 | low end |
| drone_dispatcher | normal | 0 | 1 | low end |
| echo_process | normal | 0 | 1 | low end |
| ground_control | normal | 0 | 1 | low end |
| handler_proxy | normal | 2 | 2 | in range |
| launch_pad | normal | 0 | 1 | low end |
| loyalty_test | normal | 0 | 1 | low end |
| mirror_script | normal | 0 | 1 | low end |
| orbital_debris | normal | 2 | 2 | in range |
| parking_warden | normal | 0 | 1 | low end |
| patrol_unit | normal | 0 | 1 | low end |
| permit_office | normal | 0 | 1 | low end |
| route_optimizer | normal | 0 | 1 | low end |
| surveillance_mast | normal | 0 | 1 | low end |
| tariff_collector | normal | 0 | 1 | low end |
| tracking_station | normal | 0 | 1 | low end |
| transit_controller | normal | 0 | 1 | low end |
| triage_unit | normal | 0 | 1 | low end |
| uplink_relay | normal | 0 | 1 | low end |
| utility_meter | normal | 1 | 1 | in range |
| weather_satellite | normal | 0 | 1 | low end |
| claims_adjuster | elite | 0 | 3 | low end |
| geostationary_guard | elite | 0 | 3 | low end |
| last_mile_enforcer | elite | 0 | 3 | low end |
| zoning_board | elite | 0 | 3 | low end |
| rc_template_elite | elite | 1 | 3 | low end |
| rc_template_elite_b | elite | 1 | 3 | low end |
| recall_unit | elite | 1 | 3 | low end |
| riot_control | elite | 1 | 3 | low end |
| station_commander | elite | 1 | 3 | low end |
| port_authority | elite | 2 | 4 | authored "resistant": top end |
| Mirror elites (`mirror_resistance`, config) | elite | 1 | 3 | low end |
| account_manager | mini-boss | 1 | 3 | low end |
| city_manager | mini-boss | 2 | 4 | authored "resistant": top end |
| logistics_director | mini-boss | 2 | 4 | authored "resistant": top end |
| mission_director | mini-boss | 2 | 4 | authored "resistant": top end |
| the_handler | mini-boss | 2 | 4 | authored "resistant": top end |
| civic_core | boss | 0 (phase 3 wheel 0) | 5 (phase 3 wheel 5) | low end; phase override kept equal |
| commons_array | boss | 0 (phase 3 wheel 0) | 5 (phase 3 wheel 5) | low end; phase override kept equal |
| dispatch_core | boss | 0 (phase 2, 3 wheels 0) | 5 (5, 5) | low end; phase overrides kept equal |
| renewal_engine | boss | 0 (phase 3 wheel 0) | 5 (phase 3 wheel 5) | low end; phase override kept equal |
| the_manifest | boss | 0 (phase 3 wheel 0) | 5 (phase 3 wheel 5) | low end; phase override kept equal |

Unchanged satellites (0): botnet_drone, care_drone, civic_drone, collections_drone, courier_drone, echo_drone,
orbital_drone, seed_drone.
