# Round 20 interaction gifs

Every interaction / state that changes, as a loop (<= 2 MB each). Medium: INLAY = street-plane decal, PENCIL = grease pencil (plans + static states, wipes after a beat), STICKER = static objects only, TERMINAL = C screens, FLOAT = diegetic hit/health floats.

| gif | interaction | feedback | medium |
|---|---|---|---|
| [01_pick_up.gif](01_pick_up.gif) | Pick up a defence | sticker peels off the tray; every socket that can take it pulses white | STICKER + INLAY |
| [02_drag_valid.gif](02_drag_valid.gif) | Drag over a valid node | white frame; dashed forecast ring turns green; yellow pencil arrow + circle; IF PLACED terminal | INLAY + PENCIL + TERMINAL |
| [03_drag_invalid.gif](03_drag_invalid.gif) | Invalid drop | red frame + X (no free slot / seized / not a node); the card springs back to the tray | INLAY + STICKER + TERMINAL |
| [04_placed_ripple.gif](04_placed_ripple.gif) | Defence placed | the card drops into the socket; a lime ripple; forecast ring settles green | STICKER + INLAY |
| [05_remove_defence.gif](05_remove_defence.gif) | Remove a defence | drag the unit off its socket to the tray; the forecast ring re-projects (amber) | INLAY + PENCIL + STICKER |
| [06_move_swap.gif](06_move_swap.gif) | Move / swap | drag a placed unit node to node (dashed pencil); dropping on a full slot swaps the two | INLAY + PENCIL |
| [07_forecast_change.gif](07_forecast_change.gif) | Forecast changes | dashed ring = projected outcome, re-projects live; terminal numbers count to the new value | INLAY + TERMINAL |
| [08_routes_revealed.gif](08_routes_revealed.gif) | Threat routes revealed | entry sockets pulse; red grease pencil draws each route A/B/C to its target | INLAY + PENCIL |
| [09_decoy_preview.gif](09_decoy_preview.gif) | Route redirect preview (DECOY) | only pull assets re-route: the old pencil route wipes, a dashed pencil bend draws to the decoy's node | INLAY + PENCIL + STICKER |
| [10_link_frozen.gif](10_link_frozen.gif) | Link frozen (setup) | the busiest link to home frosts over from the node end; nothing routes or shoots across it | INLAY + TERMINAL |
| [11_start_defense.gif](11_start_defense.gif) | START DEFENSE | the one sticker button: slap-down squash, then the setup UI peels away | STICKER |
| [12_wave_incoming.gif](12_wave_incoming.gif) | Wave incoming | the entry socket rings red; pencil INCOMING writes, stays a moment, wipes away | INLAY + PENCIL |
| [13_threat_moving.gif](13_threat_moving.gif) | Threat moving | corp vehicle on the street with its red ring (lit segments = HP) | 3D + INLAY |
| [14_defence_fires.gif](14_defence_fires.gif) | Defence fires / hit | tracer, binary 0/1 shards, a rising numeral; the ring loses lit segments | FLOAT + INLAY |
| [15_threat_held_ice.gif](15_threat_held_ice.gif) | Threat held (ICE LOCK) | on the firewall node the ring freezes into an ice crystal, the unit frosts, HELD 2 > 1, then it moves on | INLAY + FLOAT |
| [16_threat_lured_decoy.gif](16_threat_lured_decoy.gif) | Threat lured (DECOY) | decoy pylon on RELAY broadcasts; the threat's pencil route; at the proxy the old route wipes and a dashed pencil bend draws to the decoy; the unit turns | 3D + INLAY + PENCIL |
| [17_unit_destroyed_wipe.gif](17_unit_destroyed_wipe.gif) | Unit destroyed (DOWN wipes) | shards, the ring breaks to a grey X; pencil X + DOWN writes, holds, then a cloth wipe clears it | FLOAT + INLAY + PENCIL |
| [18_node_damage.gif](18_node_damage.gif) | Node takes damage (health combo) | the lit part fades north > south with each hit; numbers float above only on hover / always-show | INLAY + FLOAT |
| [19_node_disabled_cascade.gif](19_node_disabled_cascade.gif) | Node disabled + cascade | the last lit sliver goes; amber dashed frame; 50% of the excess surges along both links into the neighbours | INLAY |
| [20_node_seized.gif](20_node_seized.gif) | Node seized | a disabled node hit again: violet corp hatch + corp glyph, links die; pencil LOST writes then wipes | INLAY + PENCIL |
| [21_node_lost.gif](21_node_lost.gif) | Node lost (after the raid) | the seized node is removed: burnt socket with embers until reclaimed + reinstalled | INLAY |
| [22_reaches_home.gif](22_reaches_home.gif) | Threat reaches home | CORE's lit part drops from the north, pink pulse; HOME 50 > 41 in the terminal | INLAY + TERMINAL |
| [23_wave_cleared.gif](23_wave_cleared.gif) | Wave cleared | the wave's pencil routes wipe away, entries stop pulsing, packets flow home | INLAY + PENCIL + TERMINAL |
| [24_raid_result.gif](24_raid_result.gif) | Raid result (CELL HOLDS) | after the raid: the CELL HOLDS stamp slaps on, the report types out; Heat is settled here (win ±0, loss +5) | STICKER + TERMINAL |
| [25_speed_skip.gif](25_speed_skip.gif) | Speed / skip | a live terminal strip (changes state, so not a sticker); SKIP jumps to the result | TERMINAL |
| [26_home_breached.gif](26_home_breached.gif) | Home breached / lost | CORE drains to nothing and burns out; pencil BREACHED stays (end state) | INLAY + PENCIL + TERMINAL |
| [27_node_health.gif](27_node_health.gif) | Node health combo | lit part drains north > south; hover shows numbers; 0 = disabled colour + dashed | INLAY + FLOAT |
| [heat_spotlights.gif](../../round19_raid/heat_spotlights.gif) | Spotlight: EXPOSED (locked, round 19) | the spotlit node is exposed (proposal for the GDD) | 3D + INLAY |

Removed from round 19: the in-raid Heat escalation state. Heat never changes during a raid; it is settled on the result screen (24).
