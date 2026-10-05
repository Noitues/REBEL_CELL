# REBEL_CELL art evolution

How the art direction started, changed and ended: from the shipped game look (timeline H23, 2026-09-27) and the M13 W1-W10 art pass (judged "underwhelming"), through concept rounds 1-43, to the locked set behind `docs/ART_BIBLE.md` v2 (2026-10-05).

| File | What |
|---|---|
| `rebel_cell_art_evolution.mp4` | Video, 1920x1080, 30 fps, H.264, 6:00 long, no audio. Encoded with Blender 5.2's video sequencer from frames drawn with Pillow. |
| `rebel_cell_art_evolution.pdf` | Slideshow, 92 pages at 1920x1080, one page per shot (for GIF shots, a single frame). |

Caption key: each shot names the round, what changed, and the designer's call, tagged `[LOCKED]` (lime), `[REJECTED]` (pink), `[ITERATE]` (yellow) or `[CONTEXT]` (cyan). Calls come from `docs/concepts/DIRECTION_REVIEW.md`.

## Chapters

| # | Chapter | Starts | Length | PDF page |
|---|---|---|---|---|
| - | Title | 0:00 | 0:05 | 1 |
| 00 | WHERE WE STARTED | 0:05 | 0:31 | 2 |
| 01 | WORLD STYLE | 0:36 | 0:26 | 10 |
| 02 | THE OVERLAY | 1:03 | 0:14 | 17 |
| 03 | SLICES & WHEEL | 1:18 | 0:41 | 21 |
| 04 | COMBAT | 1:59 | 0:38 | 32 |
| 05 | THE CITY | 2:38 | 0:21 | 42 |
| 06 | RAID | 2:59 | 0:24 | 48 |
| 07 | NETRUN | 3:23 | 0:29 | 55 |
| 08 | CORP HQs | 3:53 | 0:31 | 63 |
| 09 | SHOP & UI | 4:25 | 0:29 | 71 |
| 10 | SYSTEMS | 4:54 | 0:22 | 79 |
| 11 | WHERE WE ENDED | 5:17 | 0:43 | 85 |

## Shot list and sources

Times are when each shot starts in the video; the page is its PDF page.

- **0:00**, p.1: Title card

### 00 Where We Started (0:05)

- **0:08**, p.3: SEP 24: The M4 baseline: flat wheels on a plain panel. Call: Functional placeholders: every rule works, nothing looks like a world
  - `docs/timeline/2026-09-24_00_before_combat.png` (main checkout)
- **0:11**, p.4: H19: First visual pass: a neon city behind the menus. Call: Zine stickers, terminal glass, a wireframe-ish city
  - `docs/timeline/2026-09-26_13_merge_title.png` (main checkout)
- **0:15**, p.5: H23: Sept 27: the whole game, before the art pass. Call: Readable, but flat: UI floats on a generic neon map
  - `docs/timeline/2026-09-27_16_h23_fight.png` (main checkout)
  - `docs/timeline/2026-09-27_16_h23_grid.png` (main checkout)
  - `docs/timeline/2026-09-27_16_h23_raid.png` (main checkout)
  - `docs/timeline/2026-09-27_16_h23_modem.png` (main checkout)
- **0:19**, p.6: M13 W3: Art pass W1-W10: before | after on combat. Call: Tokens, components, wheels, cards, VFX, city, a11y: 53 screens recaptured
  - `docs/art_review/FINAL/gallery/combat_start_1.0_mouse.jpg`
- **0:23**, p.7: M13 FINAL: Every workstream merged, every lint green. Call: Polish on the same skeleton: before | after per screen
  - `docs/art_review/FINAL/gallery/grid_1.0_mouse.jpg`
  - `docs/art_review/FINAL/gallery/hq_1.0_mouse.jpg`
  - `docs/art_review/FINAL/gallery/modem_1.0_mouse.jpg`
  - `docs/art_review/FINAL/gallery/raid_result_1.0_mouse.jpg`
- **0:27**, p.8: M13 W7: City lighting, Heat states and territory tints. Call: Better, but still a HUD tint over a placeholder city
  - `docs/art_review/W7/lighting_before_after.jpg`
- **0:31**, p.9: THE VERDICT (text card). Call: "Underwhelming." / The M13 pass polished the UI but never found a look. / New rule: lead with bold concept art, decide by / comparison, then lock it in a new art bible.

### 01 World Style (0:36)

- **0:39**, p.11: R1: Five agents, five directions, same five subjects. Call: All five rejected, but C's geometry and E's cel shading survive
  - `docs/concepts/a_neon_ink/contact_sheet.jpg`
  - `docs/concepts/b_tiltshift_diorama/contact_sheet.jpg`
  - `docs/concepts/c_riso_zine/contact_sheet.jpg`
  - `docs/concepts/d_rain_noir/contact_sheet.jpg`
  - `docs/concepts/e_glitch_vector/contact_sheet.jpg`
  - `docs/concepts/COMPARE_01_combat.jpg`
- **0:46**, p.12: R2: Round 2: low-poly 3D, painterly, geo vector, neon paint, toon. Call: A, B and D rejected. C (geo vector) and E (toon) go forward
  - `docs/concepts/round2/COMPARE_all_directions.jpg`
- **0:49**, p.13: R2 Cv2: Cv2: gritty triangulated low-poly. Call: Variable facet sizes and per-triangle tone jitter. Cv3 regressed
  - `docs/concepts/round2/r2c_geo_vector_gritty/contact_sheet.jpg`
- **0:52**, p.14: R2 BLEND: Cv2 geometry + E's cel bands and ink lines. Call: LOCKED: the base world style
  - `docs/concepts/round2/r2_blend_EC_on_Cv2_day/city_day.png`
- **0:56**, p.15: R6: The game's own city, restyled: glowing streets. Call: "City looks great!"  Day, night and suspicion versions
  - `docs/concepts/round6_city_restyle/before_after.jpg`
- **0:59**, p.16: R6: Night + suspicion: helicopters, drones, red/blue. Call: Approved; it needs to move (city motion, rounds 24-26)
  - `docs/concepts/round6_city_restyle/views/restyle_suspicion_night_full.png`

### 02 The Overlay (1:03)

- **1:06**, p.18: R3: Six overlay materials on the same fight. Call: Tactical glass, stencil spray, vinyl sticker, light pen, ransom collage, ink brush
  - `docs/concepts/round3_overlay/COMPARE_01_combat.jpg`
- **1:11**, p.19: R3 v2: Vinyl stickers for words, grease pencil for plans. Call: LOCKED: stickers + pencil + light spill from the glowing world
  - `docs/concepts/round3_overlay/combined_v2/01_combat.png`
- **1:14**, p.20: R22: SEND IT as a raid-format vinyl sticker. Call: LOCKED. A verb sticker slaps over the washed-out system word
  - `docs/concepts/round22_combat_fx/send_it_sticker.png`

### 03 Slices & Wheel (1:18)

- **1:21**, p.22: R1 3D: Spinner depth studies: stack, parallax, lit, pre-rendered. Call: Depth wanted, but cheaply: layer parallax and a lens
  - `docs/concepts/spinner_3d/08_combo_everything.gif`
- **1:25**, p.23: R4: Four wheels: faceted, instrument dial, layered stack, segmented. Call: Ideas salvaged: W-B's hub readout, W-C's layer parallax
  - `docs/concepts/round4_wheel_card/wheels_compare.jpg`
- **1:28**, p.24: R5: Slice families A-D side by side. Call: LOCKED: family C, 'Screens & Data': live CRT screens, bold white glyph
  - `docs/concepts/round5_slices/COMPARE_wheels.jpg`
- **1:31**, p.25: R8-9: Pushing slices toward the city style. Call: Rejected: big illustrated and low-poly identity art didn't land
  - `docs/concepts/round8_program_identity/identity_library.png`
  - `docs/concepts/round9_poly_identity/compare_flat_vs_poly.jpg`
- **1:37**, p.26: R13: Wheel frames D1-D4. Call: LOCKED: D4 'Lens & rail' for every wheel; phase pips loved
  - `docs/concepts/round13_wheel_details/compare.jpg`
- **1:40**, p.27: R13: Temporary state overlays on a slice. Call: R15 "ship it": CORRUPTED, ENCRYPTED, FROZEN, LOCKED, BURNING...
  - `docs/concepts/round13_slice_system/states_fx.gif`
- **1:44**, p.28: R17: Card-play preview: ghost blades chase to the landing. Call: LOCKED: animated preview, ghost drones, no trace lines
  - `docs/concepts/round17_corp_wheels/preview.gif`
- **1:48**, p.29: R14-19: Corp kits: every enemy inherits its corp's slices. Call: LOCKED in R19: all five kits (Meridian, Solace, Halcyon, Orbital, Cell)
  - `docs/concepts/round18_corp_wheels/corps_compare.jpg`
- **1:52**, p.30: R16-34: Glyph package, tiers I-III and the new names. Call: Tier II steel bezel, tier III gold; SHIM, OVERFLOW, DEFRAG, DETOUR, HOTFIX
  - `docs/concepts/round34_slice_names/slice_system_final_v3.png`
- **1:55**, p.31: R41: Worst-case clutter: drones, parasites, statuses. Call: LOCKED: drones collapse to a thin layer, bloom on hover
  - `docs/concepts/round41_wheel_stack/combat_worst_case_spin_v4.gif`

### 04 Combat (1:59)

- **2:02**, p.33: R4: Cards: faceted print, data chip, sticker card, terminal. Call: LOCKED (R10): sticker cards, with peel and stick animations
  - `docs/concepts/round4_wheel_card/cards_compare.jpg`
- **2:05**, p.34: R10: Combat on the dimmed city. Call: The fade is right, but the view is too zoomed out
  - `docs/concepts/round10_combat_c/combat_night_regular.png`
- **2:09**, p.35: R11: A close-up of the building under attack. Call: LOCKED: night approved; day re-rendered cooler
  - `docs/concepts/round11_combat_target/combat_boss_night.png`
- **2:12**, p.36: R1: Binary damage shards: hits break into 0s and 1s. Call: Yes, but iterate. Hit and crit shards locked in R18
  - `docs/concepts/binary_damage/03_crit.gif`
- **2:16**, p.37: R18-19: The card play: peel, slap, dissolve. Call: LOCKED: dissolve A, the bit stream
  - `docs/concepts/round19_combat_fx/dissolve_A_bitstream.gif`
- **2:20**, p.38: R19-22: Heat: the city reacts, not a screen glitch. Call: LOCKED H1: police lights, searchlights, helicopters on all three bands
  - `docs/concepts/round22_combat_fx/heat_city_v4.gif`
- **2:24**, p.39: R23: Every effect stems from the card's slap on the target wheel. Call: LOCKED: overlay-only corrupt, word stickers dissolve into bits
  - `docs/concepts/round23_combat_fx/fx_corrupt_apply_v4.gif`
  - `docs/concepts/round23_combat_fx/fx_evade_v4.gif`
  - `docs/concepts/round23_combat_fx/fx_phase_change_v3.gif`
  - `docs/concepts/round23_combat_fx/fx_enemy_defeated_v2.gif`
- **2:30**, p.40: R24-26: Rule: the boss target IS the corp HQ. Call: LOCKED: zoomed-in framing, same model and roads as the map
  - `docs/concepts/round26_hq_targets/combat_halcyon.jpg`
- **2:34**, p.41: R31: Meridian: facing the boom, crane centred. Call: The train runs in front, takes a container, speeds off
  - `docs/concepts/round31_meridian_combat/combat_meridian_motion.gif`

### 05 The City (2:38)

- **2:41**, p.43: R24: City motion layers: traffic, drones, signs. Call: "Amazing". Add more highways and interchanges
  - `docs/concepts/round24_city_motion/city_ambient_night.gif`
- **2:45**, p.44: R26: Flying-car sky lanes at night. Call: LOCKED v4: lanes, speed, random lane colours day and night
  - `docs/concepts/round26_city_motion/city_ambient_night_v4.gif`
- **2:49**, p.45: R40-42: Unified city v3: opacity tuned per view. Call: LOCKED: "ready to lock"
  - `docs/concepts/round40_city_unified/three_views_v3.png`
- **2:52**, p.46: R27-34: REBEL_CELL district: red windows hide a fist. Call: LOCKED: tucked thumb; the ring and hand black out on the reveal
  - `docs/concepts/round34_rebel_cell/map_fist_reveal.gif`
- **2:56**, p.47: R42-43: Site markers for every kind, tier and state. Call: Plain-language legend; seized and disabled sites de-power links
  - `docs/concepts/round42_site_markers/site_markers_on_map_v4.png`

### 06 Raid (2:59)

- **3:02**, p.49: BEFORE: The raid war table in the shipped game. Call: Nodes on a flat board, apart from the city
  - `docs/timeline/2026-09-27_16_h23_raid.png` (main checkout)
- **3:06**, p.50: R18: Raid nodes on the street plane: holo tiles vs circuit inlay. Call: LOCKED: C, the circuit inlay. Holo tiles kept for later
  - `docs/concepts/round18_raid_grid/raid_options.png`
- **3:09**, p.51: R20-21: Panels by fiction: holo intel, corp work order. Call: LOCKED: option E; lime links; red pencil routes; DOWN wipes away
  - `docs/concepts/round21_raid_ui/raid_setup_night.png`
- **3:13**, p.52: R20-22: Stationed operators with class beacons. Call: LOCKED: R3 cone beacons; Rigger blinks
  - `docs/concepts/round20_raid_world/operator_drop.gif`
- **3:17**, p.53: R20: Campaign lost: a ransomware lock. Call: LOCKED: option A. The summary becomes a corp audit dossier
  - `docs/concepts/round20_raid_world/campaign_lost.png`
- **3:20**, p.54: R40: The raid, re-run inside the unified city. Call: LOCKED: every raid interaction re-run in the shared model
  - `docs/concepts/round40_city_unified/raid_view_v3.png`

### 07 Netrun (3:23)

- **3:26**, p.56: BEFORE: The netrun route in the shipped game. Call: A wireframe node map on its own screen
  - `docs/timeline/2026-09-27_16_h23_route.png` (main checkout)
- **3:30**, p.57: R31-32: Route ideas: blueprint, on the map, climb, transit. Call: Blueprint rejected. Combined vs separate vs hybrid
  - `docs/concepts/round32_netrun_route/options_overview.png`
- **3:33**, p.58: R32-34: Option D, the hybrid. Call: LOCKED: transit path for sites, a climb for the HQ, raids on the map
  - `docs/concepts/round34_netrun_route/route_d_transit.gif`
- **3:37**, p.59: R35: The HQ run as an overhead compound. Call: Heat B: darker orange, lights circle hardened nodes
  - `docs/concepts/round35_netrun/hq_compound_dynamic.gif`
- **3:41**, p.60: R36-37: Terminal connect, window despawns, wheel lens zooms. Call: LOCKED: about 4.4 s, skippable
  - `docs/concepts/round37_netrun/transition_mix.gif`
- **3:45**, p.61: R38-41: Transit v3: straight cable runs, solid walked path. Call: LOCKED: "perfect"
  - `docs/concepts/round38_netrun_transit/transit_step_v3.gif`
- **3:49**, p.62: R38: The Central Server breach. Call: LOCKED: the gate needs 3 Exploits from tier-2 sites
  - `docs/concepts/round38_landing_exploits/central_server_breach.gif`

### 08 Corp Hqs (3:53)

- **3:56**, p.64: R26: Halcyon's eye scans the city. Call: "Like the Eye of Sauron"
  - `docs/concepts/round26_hq_targets/halcyon_eye_scan.gif`
- **4:00**, p.65: R27: Meridian fortress shapes. Call: LOCKED: A, the container wall. No rounded shapes
  - `docs/concepts/round27_hq_targets/meridian_fortress_options.png`
- **4:04**, p.66: R28-30: Lower walls, a moat, a gantry-crane keep. Call: LOCKED: "good enough to move on"
  - `docs/concepts/round30_meridian_castle/hq_meridian_close_night.jpg`
- **4:07**, p.67: R26: REBEL_CELL: the player's home until the betrayal. Call: Tokyo canyon kept; holograms, painted roofs, floating fists dropped
  - `docs/concepts/round26_rebel_cell/idea_1_tokyo_street_close.jpg`
  - `docs/concepts/round26_rebel_cell/idea_2_painted_roofs_close.jpg`
  - `docs/concepts/round26_rebel_cell/idea_3_hijacked_skyline_close.jpg`
  - `docs/concepts/round26_rebel_cell/idea_4_knuckle_deck_close.jpg`
- **4:12**, p.68: R34: REBEL_CELL locked: home lays low, DISPATCH shouts. Call: LOCKED: anti-human signage and the fist hologram
  - `docs/concepts/round34_rebel_cell/map_A_home_crop.jpg`
  - `docs/concepts/round34_rebel_cell/canyon_dispatch.jpg`
- **4:17**, p.69: R42-43: Unique HQ mechanics: Orbital's missile loop. Call: Good for now; Meridian crane/train, Halcyon switchback, Solace strands
  - `docs/concepts/round43_hq_mechanics/hq_orbital_mechanic.gif`
- **4:21**, p.70: R43: DISPATCH finale: Sync Strike. Call: LOCKED: three runners hit three locks together
  - `docs/concepts/round43_hq_mechanics/dispatch_sync_strike.gif`

### 09 Shop & Ui (4:25)

- **4:28**, p.72: BEFORE: The MODEM shop in the shipped game. Call: The designer liked the original neon MODEM sign
  - `docs/timeline/2026-09-27_16_h23_modem.png` (main checkout)
- **4:31**, p.73: R12: A fixed shop facade on the street. Call: LOCKED: F1 Tenement, pinker spill, no cables
  - `docs/concepts/round12_modem_facade/f1b_night.png`
- **4:35**, p.74: R27: MARKET NEON takeover: NO -> MoRE -> MAN. Call: LOCKED, then renamed MAINFRAME in R31
  - `docs/concepts/round27_modem_sign_flicker/market_neon_more_sequence.gif`
- **4:39**, p.75: R32-34: MAINFRAME: filled neon wired into its circuit board. Call: LOCKED v4: NO-MoRE-MAN, I AM -> AI, I AM -> NO -> MAN
  - `docs/concepts/round33_mainframe_sign/iamai_sequence_v4.gif`
- **4:43**, p.76: R32-34: Shop: an offscreen slice wheel and a recycle bin. Call: LOCKED: no needle, the top slice's price tag hangs in its place
  - `docs/concepts/round34_firmware_daemons/shop_v5.png`
- **4:46**, p.77: R31-33: Title screen and UI kit. Call: LOCKED: menu A with SIMULATE; Courier Prime for corp paper
  - `docs/concepts/round31_ui_chrome/title_screen.gif`
- **4:50**, p.78: R31: Rewards peel from a loot sheet. Call: LOCKED: option A; dialogue is a cel bust on a CRT feed
  - `docs/concepts/round31_reward_event/reward_reveal.gif`

### 10 Systems (4:54)

- **4:57**, p.80: R33-34: Two systems that were never designed until round 33. Call: LOCKED: firmware plugs in from the hub side; daemon icons and rack
  - `docs/concepts/round34_firmware_daemons/firmware_trigger.gif`
  - `docs/concepts/round34_firmware_daemons/daemon_trigger.gif`
- **5:02**, p.81: R38-40: Operative portraits, states and contexts. Call: LOCKED: portraits v2 (Phantom and Rigger fixed)
  - `docs/concepts/round39_portraits/portraits_classes_v2.png`
- **5:05**, p.82: R38-40: Satellites as mini-wheels docked on slices. Call: LOCKED: blended dock; the old one returns as green bits
  - `docs/concepts/round40_satellites/replace.gif`
- **5:09**, p.83: R39-41: The parasite ring, beyond the needle tip. Call: LOCKED: option A; pops up when the needle settles
  - `docs/concepts/round41_wheel_stack/parasite_popup.gif`
- **5:13**, p.84: R38-40: Exploits: one per boss power-up, badged on the map. Call: LOCKED: map badge, tag on hover, never over grease pencil
  - `docs/concepts/round39_landing_exploits/exploit_on_map_v3.png`

### 11 Where We Ended (5:17)

- **5:20**, p.86: FIGHT: Combat. Call: Target HQ backdrop, D4 lens wheels, corp kits, sticker cards
  - `docs/timeline/2026-09-27_16_h23_fight.png` (main checkout)
  - `docs/concepts/round41_wheel_stack/combat_typical_v4.png`
- **5:26**, p.87: CITY: The City Grid. Call: One real low-poly city with sky lanes and Heat lights
  - `docs/timeline/2026-09-27_16_h23_grid.png` (main checkout)
  - `docs/concepts/round40_city_unified/city_grid_v3.png`
- **5:31**, p.88: RAID: Raid defence. Call: Circuit-inlay nodes on the street, pencil routes, live panels
  - `docs/timeline/2026-09-27_16_h23_raid.png` (main checkout)
  - `docs/concepts/round40_city_unified/raid_view_v3.png`
- **5:37**, p.89: NETRUN: The netrun. Call: Cable runs through the same city, walked path in lime
  - `docs/timeline/2026-09-27_16_h23_route.png` (main checkout)
  - `docs/concepts/round38_netrun_transit/transit_v3.png`
- **5:42**, p.90: SHOP: The shop. Call: MAINFRAME facade, offscreen slice wheel, recycle bin
  - `docs/timeline/2026-09-27_16_h23_modem.png` (main checkout)
  - `docs/concepts/round34_firmware_daemons/shop_v5.png`
- **5:48**, p.91: ART BIBLE v2 (text card). Call: WORLD: Cv2 gritty low-poly + E cel shading, light spill / VINYL STICKER: things that never change / GREASE PENCIL: plans true to the rules (yellow / red) / CRT TERMINAL: the Cell's own systems / CORP PAPER + DECRYPTED HOLO: intercepted corp intel / BINARY BITS: every dissolve, hit and transition
- **5:55**, p.92: Closing card: DIRECTION LOCKED

## How it was made

A Pillow script drew every frame (Anton, Share Tech Mono and IBM Plex fonts from `assets/fonts/`; palette from ART_BIBLE v2: Cell pink, Cell lime, terminal cyan, pencil yellow), with slow zooms, crossfades, GIF loops played at their own timing, and sticker title cards. Blender 5.2 (`-b --factory-startup`) encoded the frame sequence through its video sequencer. The scratch frames and scripts were deleted afterwards.
