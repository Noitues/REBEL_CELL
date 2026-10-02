# Round 21 interaction gifs

Every interaction / state that changes, as a loop (<= 2 MB each). Medium: INLAY = street-plane decal, PENCIL = grease pencil (plans + static states, wipes after a beat), STICKER = static objects only, TERMINAL = C screens, FLOAT = diegetic hit/health floats.

| gif | interaction | feedback | medium |
|---|---|---|---|
| [01_pick_up.gif](01_pick_up.gif) | Pick up a defence | the card peels off the tray and PARKS in the slot; valid sockets pulse; a yellow pencil arrow starts from it to the cursor | STICKER + PENCIL + INLAY |
| [02_drag_valid.gif](02_drag_valid.gif) | Drag over a valid node | the pencil arrow follows the cursor; near the node it resolves into a yellow CIRCLE, the socket frame goes white, the forecast ring green, IF PLACED terminal | PENCIL + INLAY + TERMINAL |
| [03_drag_invalid.gif](03_drag_invalid.gif) | Invalid drop | near a full / seized socket the arrow ends in a red grease-pencil X and the socket flashes red; on release the arrow wipes and the card returns to the tray | PENCIL + INLAY + TERMINAL + STICKER |
| [04_placed_ripple.gif](04_placed_ripple.gif) | Defence placed | the card drops into the socket; a lime ripple; forecast ring settles green | STICKER + INLAY |
| [05_remove_defence.gif](05_remove_defence.gif) | Remove a defence | drag the unit off its socket to the tray; the forecast ring re-projects (amber) | INLAY + PENCIL + STICKER |
| [06_move_swap.gif](06_move_swap.gif) | Move / swap | the placed unit's sticker peels off its node and parks; the pencil arrow then targets the new node (yellow circle); a full slot swaps the two | STICKER + PENCIL + INLAY |
| [07_forecast_change.gif](07_forecast_change.gif) | Forecast changes | dashed ring = projected outcome, re-projects live; terminal numbers count to the new value | INLAY + TERMINAL |
| [08_routes_revealed.gif](08_routes_revealed.gif) | Threat routes revealed | entry sockets pulse; red grease pencil draws each route A/B/C to its target | INLAY + PENCIL |
| [09_decoy_setup.gif](09_decoy_setup.gif) | Decoy in setup (path rules) | SOLID = active route. Hovering the DECOY over the Relay scribbles through the part that would vanish and draws the new route DASHED; placing it erases the old part and draws the new route SOLID | PENCIL + STICKER + INLAY |
| [10_link_frozen.gif](10_link_frozen.gif) | Link frozen (setup) | the busiest link to home frosts over: round 19 ice traces + the slice FROZEN crust, ridges, cracks and glints; nothing routes or shoots across it | INLAY + FROST + TERMINAL |
| [11_start_defense.gif](11_start_defense.gif) | START DEFENSE | the one sticker button: slap-down squash, then the setup UI peels away | STICKER |
| [12_wave_incoming.gif](12_wave_incoming.gif) | Wave incoming | the entry socket rings red; pencil INCOMING writes, stays a moment, wipes away | INLAY + PENCIL |
| [13_threat_moving.gif](13_threat_moving.gif) | Threat moving | corp vehicle on the street with its red ring (lit segments = HP) | 3D + INLAY |
| [14_defence_fires.gif](14_defence_fires.gif) | Defence fires / hit | tracer, binary 0/1 shards, a rising numeral; the ring loses lit segments | FLOAT + INLAY |
| [15_threat_held_ice.gif](15_threat_held_ice.gif) | Threat held (ICE LOCK) | on the firewall node the unit is encased in ice (the slice FROZEN crust, ridges, cracks, glints) for its 2 steps, HELD 2 > 1, then thaws and moves on | 3D + FROST + INLAY + FLOAT |
| [16_decoy_destroyed_revert.gif](16_decoy_destroyed_revert.gif) | Decoy destroyed: route reverts | the unit follows the SOLID route set in setup; when the decoy is destroyed the lure ends, the decoy leg is erased and the original route is redrawn SOLID; the unit turns back | 3D + PENCIL + FLOAT |
| [17_unit_destroyed_wipe.gif](17_unit_destroyed_wipe.gif) | Unit destroyed (DOWN wipes) | shards, the ring breaks to a grey X; pencil X + DOWN writes, holds, then a cloth wipe clears it | FLOAT + INLAY + PENCIL |
| [18_node_damage.gif](18_node_damage.gif) | Node takes damage (health combo) | the lit part fades north > south with each hit; numbers float above only on hover / always-show | INLAY + FLOAT |
| [19_node_disabled_cascade.gif](19_node_disabled_cascade.gif) | Node disabled + cascade | the last lit sliver goes; amber dashed frame; 50% of the excess surges along both links into the neighbours | INLAY |
| [20_node_seized.gif](20_node_seized.gif) | Node seized | a disabled node hit again: violet corp hatch + corp glyph, links die; pencil LOST writes then wipes | INLAY + PENCIL |
| [21_node_lost.gif](21_node_lost.gif) | Node lost (after the raid) | the seized node is removed: burnt socket with embers until reclaimed + reinstalled | INLAY |
| [22_reaches_home.gif](22_reaches_home.gif) | Threat reaches home | the unit hits CORE: a binary-bit explosion (0/1 shards, flash, shock ring), CORE's fill drains from the north, HOME 50 > 41 | FLOAT + INLAY + TERMINAL |
| [23_wave_cleared.gif](23_wave_cleared.gif) | Wave cleared | the wave's pencil routes wipe away, entries stop pulsing, packets flow home | INLAY + PENCIL + TERMINAL |
| [24_raid_report.gif](24_raid_report.gif) | Raid report (corporate document) | the intercepted after-action report slides in (CLASSIFIED); the Cell's pencil circles what we gained / they lost and writes RIP on lost nodes; CELL HOLDS slaps on; Heat is settled here | PAPER + PENCIL + STICKER |
| [25_speed_skip.gif](25_speed_skip.gif) | Speed / skip | a live terminal strip (changes state, so not a sticker); SKIP jumps to the result | TERMINAL |
| [26_home_breached.gif](26_home_breached.gif) | Home breached / lost | CORE drains and burns out in a red bit-explosion; BREACHED is written heavy (double wax pass + underline) and stays: it is the end state | INLAY + FLOAT + PENCIL + TERMINAL |
| [27_node_health.gif](27_node_health.gif) | Node health combo | lit part drains north > south; hover shows numbers; 0 = disabled colour + dashed | INLAY + FLOAT |
| [heat_spotlights.gif](../../round19_raid/heat_spotlights.gif) | Spotlight: EXPOSED (locked, round 19) | the spotlit node is exposed (proposal for the GDD) | 3D + INLAY |

Round 21: every gif re-encoded with a shared multi-frame palette + dither (saturation kept). Redone: 01, 02, 03, 06 (card drag model),
09 + 16 (path rules: decoy setup / decoy destroyed), 10 (frozen), 12 (INCOMING spacing), 15 (frostier), 22 (bit explosion), 24 (corp report), 26 (BREACHED).
Heat never changes during a raid; it is settled on the report (24).
