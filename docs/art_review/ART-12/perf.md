# ART-12 12p — frame-time profile of every screen (INTERIM, measured under load)

**Interim, measured under load.** Every number here was taken on the dev PC (RX 6700 XT,
1920x1080 quiet window, v-sync off) while about nine other agents ran Godot (CPU load ~70 %,
two or three other Godot windows sharing the GPU). Frame times swing 30-100 % between runs of
the same screen; GPU times swing less but are not clean either. The parity work landing now
(wheels, arena backdrop, card faces, city sky lanes, HQ redesign) changes the numbers again. A
clean run on a quiet machine is owed (see "The clean run" at the end).

## How it is measured

`tools/visual_qa/perf_pack.tscn` (ONE windowed launch through `tools/run_windowed.py`) walks the
review pack's screens (the QA matrix's own drivers) plus its own (the HQ run's page and gate, the
worst arena_lab fixture), once per `--tiers` city quality tier. Per screen, once reached: v-sync
off, `--warmup` frames, then `--perf` seconds timed. A PERF line gives the frame mean / p95 / max,
the GPU time of the root viewport (the 2D layers: HUD, wheels, FX, the composited city), of every
CityView3D (the 3D city) and of every live SubViewport, render CPU, draws, primitives and video
memory; a SPIKES line lists frames over 16.7 ms with their time; `--census` counts redraws per
CanvasItem. Only-when-named probe screens: `combat_worst_probe` (each part of the fight hidden in
turn, plus a redraw count), `combat_worst_redraw`, `combat_worst_fxlayer`.

```
python tools/run_windowed.py --log <f> --timeout 5800 -- --resolution 1920x1080 \
  res://tools/visual_qa/perf_pack.tscn -- --out=<abs dir> --tiers=2,1 --perf=4 --warmup=60 --save-size=480x270
```

Budgets: 60 fps at 1920x1080 = 16.7 ms a frame (TECH_SPEC 10); city <= 8 ms GPU
(`CityConfig.budget_ms`, ART_REINTEGRATION_PLAN 5.2); wheels + FX <= 4 ms on the worst clutter
fixture (plan 5.2) = `combat_worst` (or `combat_worst_send`) minus `combat_worst_bare` (the same
fixture with the wheels and the FX layer hidden). Tier 1 is the Deck tier
(`Settings.CITY_QUALITY_STEAM_DECK`), measured here at 1920x1080 on this PC. No Steam Deck was
available: a real Deck run is owed (DECISIONS, open questions).

## Over budget: found and fixed

| Finding | Cause | Fix | Before -> after (tier 2) |
|---|---|---|---|
| Worst arena fixture 17 ms a frame; wheels + FX 12 ms (budget 4) | the card-play preview's chevron chase changed `WheelAttachments`' signature every frame, so the sockets and the drone dock (6 bloomed mini-wheels on the boss) redrew every frame; `DroneDock._draw_aim` re-laid every entry once per drone (`satellite_pos` -> `entries()`: O(n²), each with the HP-block layout); the preview re-laid the ghost drones every frame | the preview's own signature redraws the preview alone; `_draw_aim` uses its own entry; `CardPreviewOverlay._ghost_entries` keeps the layout while the dock and the ghost hold | worst 16.99 -> 8.15 ms, bare 4.98 -> 5.01 ms: wheels + FX 12.0 -> 3.1 ms |
| Every fight: both telemetry rings redrew their full text arc every frame | `WheelTelemetry` was a Control, and `Control.set_rotation` queues a redraw, so its slow scroll redrew it | `WheelTelemetry` extends Node2D (it turns without redrawing) | combat_start 7.9 -> 5.0 ms, hover 9.6 -> 5.4 ms (quieter re-run) |
| Campaign lost: the dossier opens at 43-56 ms frames for ~1 s | `load()` of the manila JPG (and the print stock, the post-it paper) inside `_draw`, held by nothing: Godot decodes the file again at every draw (15 ms headless per manila load), and the cover redraws every frame while it swings | the textures are loaded once and held by their node | 43-56 ms -> 17-34 ms frames (busy PC) |

Tests: `tests/unit/test_art12_perf.gd` (fast): the ring turns without redrawing; the chase
redraws the preview alone, never the sockets or the dock; the ghost drones follow the ghost and
the dock; the dossier and the post-its hold their paper across redraws.

## Still over budget (proposed slices)

1. **Wheels + FX while FX play.** The worst fixture with SEND IT pressed (`combat_worst_send`):
   11.54 ms vs bare 6.65 ms = 4.9 ms (busy run; over 4 by ~1 ms). A synthetic volley (a Perfect
   burst, a precision landing, a number and a hit line on both wheels every 12 frames,
   `combat_worst_fx`): ~9.5 ms over bare. Measured with timing marks in `WheelView._draw_view`
   (worst fixture, ~2.0 ms per wheel per redraw): disc sync + slice read blocks 0.6 ms, HP arc +
   hub 0.6, rails 0.2, blades 0.2, banner 0.1; a landing tween redraws the whole wheel every
   frame (`combat_worst_redraw`: +4.9 ms for the two wheels); the FX layer's volley alone
   (`combat_worst_fxlayer`) +3.2 ms. **Slice:** split the wheel's still drawing (read blocks,
   hub, HP, rails) from the landing / pulse layer so a landing redraws only its layer; cache
   `hp_layout()` and the hub's fitted font sizes per state.
2. **combat_aiming** 9-15 ms (the drop-zone pulse redraws both wheels every frame while a card
   is aimed): the same slice as 1.
3. **Campaign lost: the lock -> dossier switch** is one 640-870 ms frame (`AuditDossier.new`
   ~240 ms + mounting ~240 ms + the first draw) under the lock's CRT collapse (black), and the
   lock's start reads the screen back for the prints (a 130-180 ms frame). Covered page
   switches (the ANIM rule), but long. **Slice:** build the dossier during the lock's static
   reading hold; `AuditDossier._place_overlays` costs ~2 ms a frame and runs at rest too (place
   only while the motion runs or the layout changes).

## Results (interim; the full run after the fixes, busy machine)

Frame times in ms (mean, p95); GPU in ms (total of every viewport; city = the 3D city's
viewports). T2 = tier 2 (default), T1 = tier 1 (Deck tier), both at 1920x1080.

| Screen | T2 frame mean | T2 p95 | T2 GPU total | T2 city GPU | T1 frame mean | T1 p95 | T1 GPU total | T1 city GPU | Draws (T2) |
|---|---|---|---|---|---|---|---|---|---|
| title | 2.90 | 4.69 | 1.26 | 0.00 | 3.28 | 4.89 | 1.01 | 0.00 | 541 |
| title_confirm | 3.70 | 5.35 | 2.01 | 0.00 | 3.64 | 5.43 | 1.65 | 0.00 | 596 |
| slots | 3.37 | 4.90 | 1.29 | 0.00 | 2.89 | 5.08 | 1.05 | 0.00 | 630 |
| new_campaign | 5.11 | 6.39 | 1.66 | 0.00 | 4.31 | 6.17 | 1.63 | 0.00 | 1303 |
| new_campaign_picker | 5.11 | 6.38 | 1.73 | 0.00 | 4.06 | 5.03 | 1.70 | 0.00 | 1318 |
| hq | 6.40 | 7.78 | 2.14 | 0.00 | 5.82 | 7.69 | 2.10 | 0.00 | 1866 |
| hq_black_market | 6.04 | 7.59 | 2.17 | 0.00 | 7.06 | 11.27 | 1.46 | 0.00 | 1784 |
| hq_crew | 6.21 | 7.80 | 2.08 | 0.00 | 7.13 | 9.90 | 1.16 | 0.00 | 1672 |
| hq_loadout_deck | 5.92 | 7.91 | 2.66 | 0.00 | 8.63 | 14.59 | 1.52 | 0.00 | 2095 |
| hq_loadout_spinner | 5.83 | 6.77 | 2.59 | 0.00 | 7.79 | 9.94 | 2.55 | 0.00 | 2107 |
| hq_pause | 6.52 | 8.33 | 2.42 | 0.00 | 8.81 | 14.63 | 1.87 | 0.00 | 2161 |
| hq_heat_band | 6.10 | 8.09 | 2.18 | 0.00 | 10.67 | 20.04 | 1.63 | 0.00 | 1902 |
| grid | 7.86 | 10.48 | 5.03 | 4.44 | 10.87 | 14.55 | 6.50 | 5.59 | 2478 |
| grid_site_selected | 9.58 | 14.49 | 6.30 | 5.66 | 10.45 | 13.95 | 6.47 | 5.53 | 2547 |
| grid_raid_pending | 13.44 | 18.91 | 8.93 | 8.17 | 12.03 | 13.99 | 7.81 | 6.65 | 2672 |
| grid_influence | 8.28 | 11.73 | 5.44 | 4.79 | 9.13 | 12.63 | 5.75 | 4.88 | 2580 |
| grid_drag_crew | 8.25 | 11.71 | 5.43 | 4.78 | 10.63 | 13.81 | 6.56 | 5.56 | 2559 |
| grid_meridian | 9.88 | 14.22 | 6.40 | 5.54 | 9.33 | 10.88 | 5.75 | 4.65 | 2526 |
| grid_halcyon | 9.63 | 14.55 | 4.07 | 3.44 | 10.20 | 13.05 | 5.51 | 4.64 | 2838 |
| grid_orbital | 8.59 | 11.19 | 4.44 | 3.91 | 10.48 | 14.20 | 6.55 | 5.65 | 2596 |
| grid_rebel_cell | 10.11 | 15.97 | 4.01 | 3.42 | 11.37 | 16.74 | 4.34 | 3.75 | 2793 |
| raid_setup | 7.35 | 9.38 | 3.25 | 2.55 | 10.10 | 16.79 | 4.09 | 3.11 | 1843 |
| raid_drag_asset | 8.72 | 12.97 | 4.33 | 3.46 | 10.13 | 18.27 | 5.05 | 3.87 | 1851 |
| raid_playout | 6.92 | 13.81 | 3.37 | 2.77 | 5.82 | 10.19 | 2.62 | 2.06 | 910 |
| raid_result | 6.94 | 11.39 | 4.27 | 3.53 | 5.20 | 8.54 | 2.43 | 1.90 | 903 |
| raid_report | 3.96 | 5.55 | 2.35 | 1.85 | 3.39 | 5.43 | 1.90 | 1.41 | 570 |
| raid_interlude | 3.65 | 8.13 | 1.02 | 0.00 | 3.30 | 4.99 | 1.40 | 0.00 | 224 |
| route | 6.27 | 13.72 | 3.12 | 2.56 | 5.49 | 10.54 | 2.52 | 1.97 | 817 |
| combat_start | 8.28 | 15.27 | 2.48 | 1.63 | 8.53 | 17.44 | 2.90 | 1.69 | 740 |
| combat_hover | 10.14 | 18.23 | 2.29 | 1.48 | 8.57 | 14.78 | 2.34 | 1.38 | 777 |
| combat_aiming | 15.00 | 20.96 | 2.88 | 1.85 | 13.17 | 18.63 | 2.52 | 1.53 | 847 |
| combat_resolving | 8.70 | 17.35 | 2.55 | 1.66 | 8.02 | 15.98 | 1.89 | 1.12 | 753 |
| combat_after | 9.93 | 19.15 | 2.40 | 1.63 | 7.91 | 14.80 | 2.23 | 1.26 | 753 |
| combat_refused | 9.21 | 17.02 | 2.16 | 1.43 | 6.87 | 13.70 | 2.66 | 1.56 | 743 |
| combat_boss_p2 | 8.69 | 15.37 | 2.86 | 2.00 | 8.50 | 15.23 | 2.59 | 1.74 | 1021 |
| combat_boss_p3 | 8.60 | 16.03 | 2.24 | 1.64 | 9.08 | 16.12 | 2.95 | 1.99 | 1030 |
| combat_victory | 2.26 | 7.27 | 0.65 | 0.00 | 1.39 | 3.58 | 0.44 | 0.00 | 241 |
| combat_defeat | 5.38 | 6.82 | 3.17 | 2.12 | 5.58 | 12.73 | 1.27 | 0.76 | 574 |
| loot | 1.99 | 3.66 | 0.97 | 0.00 | 2.43 | 9.29 | 0.53 | 0.00 | 253 |
| mainframe | 4.65 | 6.10 | 1.73 | 0.00 | 5.83 | 13.43 | 0.67 | 0.00 | 2021 |
| mainframe_socket | 4.79 | 7.22 | 1.94 | 0.00 | 6.08 | 14.43 | 0.76 | 0.00 | 2053 |
| mainframe_remove | 4.91 | 6.46 | 2.38 | 0.00 | 5.46 | 10.61 | 2.08 | 0.00 | 2271 |
| mainframe_overwrite | 4.84 | 6.24 | 2.40 | 0.00 | 5.74 | 12.11 | 1.22 | 0.00 | 2131 |
| event | 1.81 | 3.53 | 0.86 | 0.00 | 2.28 | 8.93 | 0.53 | 0.00 | 198 |
| event_dispatch | 1.46 | 2.54 | 0.70 | 0.00 | 2.35 | 9.55 | 0.56 | 0.00 | 204 |
| codex | 2.08 | 3.79 | 1.01 | 0.00 | 2.47 | 5.28 | 0.85 | 0.00 | 183 |
| options | 4.72 | 12.36 | 1.19 | 0.00 | 5.36 | 10.97 | 0.80 | 0.00 | 922 |
| stats | 2.51 | 4.17 | 0.95 | 0.00 | 3.62 | 10.08 | 0.56 | 0.00 | 252 |
| run_end | 1.80 | 3.53 | 0.80 | 0.00 | 2.77 | 9.79 | 0.42 | 0.00 | 153 |
| run_end_clean | 1.96 | 3.85 | 0.78 | 0.00 | 2.17 | 6.68 | 0.42 | 0.00 | 152 |
| campaign_won | 2.86 | 8.24 | 0.97 | 0.00 | 3.00 | 8.69 | 0.93 | 0.00 | 405 |
| campaign_lost | 6.75 | 29.48 | 1.06 | 0.00 | 5.72 | 26.12 | 0.93 | 0.00 | 288 |
| deck_view | 6.90 | 14.51 | 4.04 | 3.20 | 4.56 | 6.29 | 2.21 | 1.62 | 1044 |
| card_detail | 4.82 | 6.64 | 2.61 | 2.00 | 5.34 | 12.02 | 2.84 | 2.08 | 1107 |
| daemon_tray | 5.43 | 8.10 | 3.36 | 2.76 | 4.24 | 5.93 | 2.02 | 1.57 | 876 |
| tutorial | 8.70 | 14.61 | 3.43 | 2.61 | 7.75 | 14.86 | 1.95 | 1.40 | 920 |
| jack_in | 7.96 | 11.56 | 1.52 | 0.00 | 7.32 | 15.40 | 0.87 | 0.00 | 1867 |
| pause_netrun | 7.57 | 13.85 | 4.05 | 3.26 | 11.24 | 21.98 | 5.58 | 4.34 | 1138 |
| pause_fight | 7.61 | 10.78 | 3.63 | 2.25 | 8.56 | 18.27 | 3.75 | 2.13 | 1036 |
| pause_fight_quit | 8.68 | 12.68 | 4.25 | 2.14 | 8.39 | 16.00 | 2.12 | 0.92 | 1058 |
| hq_run | 5.61 | 8.90 | 3.19 | 2.52 | 5.98 | 14.16 | 1.86 | 1.36 | 506 |
| hq_run_gate | 6.33 | 9.24 | 3.68 | 2.72 | 6.28 | 13.37 | 1.90 | 1.28 | 780 |
| combat_worst | 10.15 | 12.76 | 6.08 | 4.21 | 14.37 | 25.56 | 2.60 | 1.53 | 1943 |
| combat_worst_fx | 19.42 | 29.53 | 7.13 | 4.77 | 19.48 | 27.62 | 2.98 | 2.01 | 2053 |
| combat_worst_send | 11.54 | 13.51 | 6.88 | 4.71 | 12.42 | 17.55 | 4.74 | 2.94 | 1868 |
| combat_worst_bare | 6.65 | 8.51 | 3.32 | 2.61 | 5.34 | 6.97 | 3.10 | 2.35 | 598 |

Reading it:

- **16.7 ms mean:** every screen inside it but the synthetic stress `combat_worst_fx` (19.4).
  Over at p95: campaign_lost (the lock -> dossier switch, slice 3) and, in this busy run, the
  combat hover / aiming / after screens (7-12 ms p95 on the quieter combat re-runs).
- **City GPU <= 8 ms:** inside it everywhere but grid_raid_pending at tier 2 in this run (8.17;
  6.02 in the first run): the GPU was shared with other agents' windows; re-check on the clean
  run. Tier 1 holds 3.7-6.7 ms on the Grid.
- **Wheels + FX <= 4 ms:** the fixture at rest with a card hovered 3.1-3.5 ms (pass); with SEND
  IT 4.9 ms (busy run, slice 1); the synthetic volley ~9.5 ms (slice 1).
- Quieter combat re-run after the fixes (tier 2): combat_start 5.02, hover 5.41, aiming 9.33,
  worst 8.15, worst_fx 14.62, bare 5.01 ms. First run before any fix (tier 2): combat_start 7.92,
  aiming 13.21, worst 16.99, worst_fx 24.07, bare 4.98 ms (tier 1: worst 17.44, bare 5.12).

## The clean run (owed)

On a quiet machine (no other Godot running), after the parity work (wheels, arena backdrop,
card faces, city sky lanes, HQ redesign) has landed:

- `perf_pack.tscn --tiers=2,1 --perf=6 --warmup=60` over every screen (66), twice; report medians.
- The budget lines: 16.7 ms a frame per screen; city GPU <= 8 ms (Grid pages, raid setup /
  playout / report, route, HQ run and gate, combat backdrop); wheels + FX <= 4 ms =
  `combat_worst` and `combat_worst_send` minus `combat_worst_bare` (`combat_worst_fx` as the
  stress line).
- Hitches: the SPIKES lines of campaign_lost (the lock's start, the lock -> dossier switch),
  jack_in, the raid playout; `--census` on any screen that redraws more than expected.
- The Deck tier also at 1280x800 (`--size=1280x800`, the Deck's screen) next to the earlier 5e /
  7w Deck numbers; then the real Steam Deck run.
- **Combat backdrop at the concept's low angle (owed, designer round 2 2026-10-05).** The close-up
  now looks at 24 degrees (HQ) / 22 degrees (Site) as combat_solace.jpg, accepted over budget: the
  designer's figure 9-10.5 ms of city GPU at 1080p tier 2 for the HQ views. Measured on a shared
  machine (hq_run_lab, 1920x1080, close-up rendered at backdrop_render_height 640): tier 2 HQ
  4.5-8.75 ms, Sites 1.5-8.3 ms, the canyon 3.4-4.2 ms; runs varied by up to 3 ms. Owed: the
  quiet run of every HQ and Site close-up (`hq_run_lab --states=hq_<corp>,site_<corp> --tier=2`,
  twice, medians) against the 8 ms line. Proposed optimisation slice (not built): a backdrop LOD
  for CityView3D (LOD1 facets past a depth along the view, a far-chunk cut beyond the frame's top
  ground point), and the extension chunks (the city recorded past city_rect round an edge Site)
  limited to those in the frustum.
