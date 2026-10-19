# NA-26 port map (old route page tests -> new homes)

Dispositions: PORTED (to a named test), RULE-MOVED (the rule lives elsewhere and is tested there), DROPPED (reason).

## Tests
| File | Test | Asserted | Disposition |
|---|---|---|---|
| test_w3_route | click selects, confirm travels | pick prompt, confirm, route_selected | PORTED `test_w3_route::test_a_selection_waits_for_the_confirm_which_travels` (street) |
| test_w3_route | keyboard press travels directly | list row press | PORTED `test_w3_route::test_a_run_whose_street_cannot_be_derived...` (fallback page) |
| test_w3_route | links between drawn nodes drawn | hidden-node link rule | DROPPED: D13 retired, the street draws the full graph (test_na23_route_flow: every option has a room) |
| test_w3_route | shapes / node file HP / HP walk | kit + rules | unchanged |
| test_parity_route | hidden nodes fully hidden, hover brings links | D13 + links hover | PORTED `test_art7_netrun::test_the_key_hover_lights_every_link_and_changes_no_state` (hidden part DROPPED, D13) |
| test_parity_route | no district plates | 2D plates | DROPPED: the plates were 2D overlay; the street page has none |
| test_parity_route | choices are focus stops on stickers; Enter picks | 2D stop placement | RULE-MOVED: keys / Enter / confirm in test_na23_route_flow; list-row press in test_w3_route fallback |
| test_parity_route | no YOU ARE HERE words / tags | 2D labels | DROPPED: the street rooms carry only the hover tag (`_street_tag`, test_art7_netrun heat test) |
| test_parity_route | dossier letterhead | OperativeDossier | PORTED (builds the dossier directly) |
| test_parity_route | key strip states / title | RouteLegend, title | kept |
| test_parity_route | fit frames YOU ARE HERE | 2D fit | DROPPED: the fit code retired; street camera is NA-23 rig (test_na23_route_view) |
| test_art7_netrun | option A states and TARGET | ring colours, options, TARGET | PORTED `test_the_route_draws_option_a_states_and_the_target` |
| test_art7_netrun | hidden nodes legend/pointer/setting | D13 + setting | PORTED to the key-hover test + `test_the_retired_show_all_nodes_key_loads_and_is_ignored` |
| test_art7_netrun | setting round trip + options row | setting | PORTED (legacy key ignored, no row) |
| test_art7_netrun | calm Heat marks | route_heat_marks rule; Heat preview == rule | PORTED `test_calm_heat_marks_come_from_the_rules` (+ street tag shows the entering Heat) |
| test_art7_netrun | route sweeps every corp | labels, you-are-here, dossier | PORTED `test_the_route_sweeps_every_corporation_on_the_street_page` (falls back on a derive failure) |
| test_art7_netrun | cables one turn | 2D cable | DROPPED: RouteOverlay cables retired |
| test_art7_netrun | dossier and node panel say the rules | dossier_data, node_panel_data | PORTED (node file via show_node_panel) |
| test_art7_netrun | dossier folds at big text | OperativeDossier on the page | DROPPED: no dossier on the page; text scale > 1.0 deferred |
| test_art7_netrun | F13 key hover never resizes | RouteLegend | PORTED `test_f13_the_key_hover_never_resizes_the_strip` |
| test_art7_netrun | F14 key row rings every node of its kind | 2D ring | DROPPED: no kind ring on the street page (Q: wanted?) |
| test_art7_netrun_city | 5 router + cable tests | RouteCableRouter | DROPPED: router retired |
| test_art7_netrun_city | route page is the 3D city; camera is a view | band, camera | PORTED (street page; camera test on the Grid view) |
| test_b3_raid_map_route | link hairlines until hover; route frames at round-44 zoom + TARGET arrow | 2D overlay | DROPPED: retired with the page; hover = test_art7_netrun, camera = NA-23 |
| test_b3_raid_map_route | route window buttons | GridZoom, RouteConfirm, SaveQuit | PORTED (street page) |
| test_art_r1 (file) | RouteCover lifts | RouteCover | DROPPED: cover retired; the dive over the street is EntryCover (NA-25) |
| test_s_mapview | route nodes on the link; layers spread; deterministic | RouteLinkLayout | PORTED deterministic derive (`test_street_route_placement_is_deterministic_on_seeded_replays`); placement tests DROPPED (street derive is NA-23) |
| test_s_mapview | jack rides the same link | from_site | kept (now `CampaignRules.jack_from_site`) |
| test_anim_p1_flow | lit node reaches to building; travel marker | 2D overlay motion | DROPPED: motion retired with the page |
| test_anim_r1_campaign | labels after a move | 2D labels | DROPPED |
| test_anim_r4_city | move shows choices, marker off them, trail | 2D travel | DROPPED (reachability = test_na23_route_flow enter) |
| test_anim_r3_city | route frames marker and choices | 2D fit | DROPPED |
| test_horizontal_pass21 | route buttons differ | list rows | PORTED to the fallback page (street_route off) |
| test_horizontal_pass22 | route buttons draw map icon | 2D stickers | DROPPED |
| test_horizontal_pass23 | key lists the route's kinds | RouteLegend kinds | PORTED (kinds from the map) |
| test_heat_all | dossier has no Heat stamp | dossier_data | PORTED (class checked directly) |
| (new) test_na26_route_port | zoom out and back; fallback page; default on | | NEW |

## Symbols retired
RouteCableRouter, RouteLinkLayout (`from_site` -> `CampaignRules.jack_from_site`), RouteCover, RouteStopPlacer, RouteOverlay instance code (static kit stays), NetrunScene route_graph / fit_route_map / route_frames / route_free_area / route_target / dossier / _build_route_frame, Settings.always_show_all_nodes, SettingsPanel all_nodes_check, RouteLegend.set_showing_all. `grep` of the first three names over scripts/ tests/ returns 0.
Playtest route files referencing the old page: not edited (orchestrator re-records).
