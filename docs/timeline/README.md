# Timeline

Screen captures of each system over time, oldest first. Captured headless with Godot's
Movie Maker (`godot --path . --resolution 1280x720 --write-movie <file>.png --fixed-fps 10
--quit-after 12 -- --demo-<hq|grid|raid|run|combat>`); the last frame is kept.

| Date | Tag | Screens |
|---|---|---|
| 2026-09-24 | 00_before | Baseline after M4, before the vertical-slice fix loop. |
| 2026-09-24 | 01_combat_rules | Combat after vertical batch 1: pickers, respin, inspect/Daemons note, drones, odds. |
| 2026-09-24 | 02_campaign | HQ (boosts, unlocks, ICE), 32-Site Grid, raid setup, wireframe netrun map after vertical batch 2. |
| 2026-09-24 | 05_pass2 | Grid with a selected Site and patrols; Modem as zine stickers (vertical batch 5). |
| 2026-09-24 | 04_menus | Title screen, options (Controls section) and the tutorial overlay after vertical batch 4. |
| 2026-09-24 | 03_narrative | HQ with the pirate-radio DJ line and the Codex button after vertical batch 3 (subtitles, DISPATCH, barks, story paths). |
| 2026-09-24 | 06_m6 | HQ roster with Ghost and Rigger operatives and the class unlocks; a Botnet fight with Deploy slices (M6 class roster). |
| 2026-09-24 | 07_m7 | Modem stock drawn from the M7 pools (60 shared cards, 18 Firmware, 24 Daemons, 12 shop slices). |
| 2026-09-24 | 08_m8 | New-campaign Target picker; Meridian Freight Systems' 32-Site Grid in amber (M8). |
| 2026-09-24 | 09_m9 | Halcyon Civic's 32-Site Grid in mint (M9). |
| 2026-09-24 | 10_m10 | Orbital Commons' 32-Site Grid in gold (M10). |
| 2026-09-24 | 11_m11 | REBEL_CELL's Grid (template) in red: the Cell's own history as the map (M11). |
| 2026-09-24 | 12_h9 | HQ with every Profile unlock listed: button rows now wrap inside the 1280 screen (horizontal pass 9). |
| 2026-09-26 | 13_merge | Visual/UI pass merged into main (H19): title menu on the neon city, HQ top bar and crew dossiers, the Grid drawn on the city with its legend, the netrun route, combat with the sticker column (bound keys) and intent tags, the MODEM cyber shop, the raid war table. The scene is passed before `--` (e.g. `res://scenes/netrun_map/netrun_scene.tscn -- --demo-combat`); demo runs bump the shared profile's counters, so back up and restore `profile.json` around a capture. |
| 2026-09-26 | 14_h20 | Horizontal batch H20: HQ with CELL STATUS badges, the Grid's Site card and runs list (no text log), raid setup with its raid card and per-node outcome badges, combat with nudge arrows, outcome chips and RESPIN / UNDO by SEND IT, a card being aimed (drop zones lit), the Modem. Captured with `tools/playtest/storyboard.tscn` (private save slot). |
| 2026-09-27 | 15_h21 | Horizontal batch H21: stat icons on the top bar and badges, the subtitle band, the Grid with drawn map icons and scaled labels, the route with node words and you-are-here, a fight after SEND IT with LAST TURN lines, plain-word tags and card pictograms, a card aimed with a pad at text scale 1.6, the Modem wallet and price tags, event choices with outcome icons. |
| 2026-09-27 | 16_h23 | Horizontal batch H23: HQ, the Grid fitted beside its column with the legend strip on the map and icons on every run row, raid setup with its intro line and labelled numbers, the route with its own legend, a fight after SEND IT (LAST TURN counts block and statuses, "YOU TAKE" wording, one nudge key pair on the status line) at 1.0 and at 1.6 with a pad (the subtitle keeps its words when docked), the Modem with buy stickers, an event without zero deltas. Captured with `tools/playtest/storyboard.tscn` (private save slot). |
| 2026-10-05 | 17_art0 | ART-0: the baseline before the v2 look (names, settings to 2.0, kit behaviour; palette still v1). HQ, the Grid, raid setup (TAKEN / DOWN words), a fight after SEND IT (NULL, RESPIN), the Mainframe shop (FIRMWARE) and an event. Captured with `tools/playtest/storyboard.tscn` (private save slot). |
| 2026-10-05 | 18_art1 | ART-1 (Group 1, foundations), as it looks on main after M14 Groups 1-4 merged (ART-12 12b, one capture pass; no per-group frames were kept at the time, so frames 18-21 show the current look, grouped by the group's own screens). The v2 palette, faces (Anton, Share Tech Mono, Plex, Permanent Marker, Courier Prime), the theme and the material kit on real screens: the title's neon sign, verb stickers and CRT terminals, the HQ, Options on the kit (switches, tabs, Heat glitch preview). Captured with `tools/visual_qa/capture_pack.py` (text 1.0, mouse, 1280x720). |
| 2026-10-05 | 19_art2 | ART-2 (Group 2, combat): the wheel stack (lens and rail frame, slice screens, hub cores), the v2 HUD (result chips, SEND IT vinyl sticker, RESPIN / UNDO chips, hand card faces), a fight after SEND IT, a card being aimed, a boss fight in phase 2 on the live city backdrop (D17). The harness took the boss frame while its HP count was still running. |
| 2026-10-05 | 20_art5 | ART-5 to ART-8 (Group 3, city): the City Grid on the real-time 3D city (Solace, Meridian, REBEL_CELL), Site markers v4, the map key and the TARGET pencil; raid setup on the city at the RAID band with the threat route and the CRT / paper / holo panels; the netrun route on the city with sticker nodes. Not kept: the raid playout (the harness frame caught START DEFENSE mid-transition) and the HQ-run canyon (see `docs/art_review/ART-8/8w`). |
| 2026-10-05 | 21_art10 | ART-9 to ART-11 (Group 4, screens): the abandon dialog (title delete slot), the run-end panel (JACKED OUT sticker), the HQ crew dossiers. **TODO (4A, still landing): shop (MAINFRAME), rewards, events and the deck viewer are not on main yet; add `21_art9_*` frames (mainframe, loot, event, deck_view) when 4A merges.** The campaign-lost ransom lock is in `docs/art_review/ART-11/4D` (the harness frame caught the glitch wipe). |
