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
