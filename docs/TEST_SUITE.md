# REBEL_CELL — Test suite

How the GUT suite is run, split and kept fast, and what the 2026-09-27 optimization pass
changed (DECISIONS "Test suite optimization"). The rules for what must be tested are in
CLAUDE.md (rule 6) and TECH_SPEC 9; this page is about running the tests.

## Commands

| What | Command | Wall time on the dev machine |
|---|---|---|
| Full suite, one process (unchanged) | `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit` | 586 s and 744 s (two runs, 10-12 min) |
| Full suite, 4 parallel shards | `python tools/run_tests.py` | 188, 292 and 281 s (median 281 s, 4.7 min) |
| Full suite, N shards | `python tools/run_tests.py -j N` | N=2: 427 and 406 s (about 7 min), N=1: 779 s (one run) |
| Fast tier (iteration) | `python tools/run_tests.py --tier fast` | 56 s (4 shards), 118 s (1) |
| Scripts whose path contains a word | `python tools/run_tests.py --select pass24` | |
| Show the shards without running | `python tools/run_tests.py --list` | |
| Refresh the measured times | `python tools/run_tests.py --update-times` | |
| Extra GUT argument for every shard | `python tools/run_tests.py --gut-arg=-gunit_test_name=fold` | |

- **Before declaring work done, run the full suite** (single process or the runner) plus
  `tools/schema_smoke_test.gd` and `tools/validate_content.gd`. The fast tier is for
  iteration only.
- Import first on a fresh clone or after adding a `class_name`
  (`godot --headless --path . --import`), as always.
- The runner is a Python 3 file (the content generators already use Python). Run it as
  a file, never through `python -` (a stdin Python hangs the shell on this machine).
- The runner prints where it keeps each shard's log (`shard<i>/gut.log`) and JUnit
  results (`shard<i>/results.xml`); `--out <folder>` picks the folder.
- The suite always runs headless (`--headless --audio-driver Dummy`): no window, no
  sound, nothing that can take focus.

## Windowed checks (quiet)

Headless has no renderer, so anything that must draw (Movie Maker captures, the
storyboard, the motion lab, frame profiling, GPU bake checks) runs in a real window.
Launch every such run through `tools/run_windowed.py`, never `godot` directly, so it
never takes keyboard or mouse focus from whoever is using the machine and makes no sound:

```
python tools/run_windowed.py --log <file> -- res://tools/design_lab/motion_lab.tscn --write-movie <dir>/f.png --fixed-fps 30 --quit-after 60 -- --demo-anim=card_hover
```

- It writes `override.cfg` in the project folder (`display/window/size/no_focus`, the
  Dummy audio driver) for the run and removes it when the last quiet run there ends
  (ignored by git). The window is created without focus, so Windows never makes it the
  foreground window, even when the machine has been idle.
- It sets `REBEL_CELL_QUIET_WINDOW=1`: Settings keeps the window windowed at its
  resolution and moves it to (-30000, -30000) on its first frame; AudioDirector mutes
  Master (`played` still logs). Godot keeps a window's start position on a screen and a
  minimized window stops drawing, so the window can show, without focus, for its first
  frame. `--quiet-window` as a user argument does the same in-game part.
- It refuses the main checkout, because `override.cfg` would also apply to anyone
  launching the game there meanwhile: run it in a git worktree or a copy (agents already
  work in worktrees), or pass `--allow-main-checkout` knowingly.
- Godot's output goes to `--log`; `--timeout` (default 600 s) stops a hung run. Make the
  Movie Maker folder first (Godot writes nothing into a missing one). Checked on this
  machine with a foreground-window watcher: focus never left the active window.

## How the runner works

- **Shards.** Every `tests/unit/test_*.gd` and `tests/integration/test_*.gd` script is
  scheduled longest first onto the shard with the least work so far, by the seconds in
  `tests/test_manifest.json` (ties by path, so a split is deterministic). A script
  missing from the manifest still runs (at 10 s) and is reported. Each shard is one
  `godot --headless ... -gconfig= -gtest=<its scripts> -gjunit_xml_file=...` process.
- **Isolation.** Each shard gets its own user:// folder (the runner points `APPDATA` on
  Windows and `XDG_DATA_HOME` on Linux into the shard's output folder), so GUT's temp
  files, settings, save slots and profiles never meet another shard or a game run. The
  tests are isolated on their own too, for runs started by hand side by side: under GUT,
  Settings uses `user://gut_settings_<pid>.json` and SaveService `user://saves/gut_<pid>/`
  (removed when the run ends), and the tests' own temp files carry the process id.
- **Result.** The runner merges the shards' JUnit results and exits non-zero when any
  test fails, a shard crashes or times out (`--timeout`, 3600 s), or a script it gave a
  shard did not run (GUT skips a script that fails to parse and still exits 0; the
  runner catches that).
- **Order.** Shards run scripts in another order than the single process does. That
  surfaced one leak (pad reachability left the pad active); a script must leave the
  Settings and autoload state it changes as it found it.

## Tiers and the manifest

`tests/test_manifest.json` lists every test script once with its measured seconds and its
tier:

- `fast`: every pure-core rule script (wheel math, resistance, targeting, statuses,
  preview == result, rewind and checkpoints, seeded replay, RNG, map generator, raid
  resolver, save round trip, content, cards, Firmware, Daemons, campaign and Heat
  rules...), the suite integrity check, the campaign flow and menus, and the screen
  scripts that run in under 5 s. 77 scripts, about 115 s of test time.
- `full`: the rest (the big screen, city and animation sweeps). They run only in the
  full suite.

When you add a test script, add it to the manifest with a tier (`seconds` can be a guess;
`python tools/run_tests.py --update-times` measures it). `test_suite_integrity.gd` fails
on a script missing from the manifest, a listed script that does not exist, a script
with no test, or a fast tier without the rule guards (preview, rewind, replay, RNG, wheel
math, raid resolver, map generator, save service, the integrity check itself).

## Test-run switches (inert outside GUT)

Both are static vars on `NeonCity`, on only when the process runs GUT (`gut_cmdln.gd` on
the command line); the game never sees them. `test_city_geometry_memo.gd` guards them.

- `geometry_memo_enabled`: the procedural city's geometry is kept by every input its
  build reads (seed, district, net mode, inks, face texture, cultures, exact creep and
  influence, corporation colour, size, camera) and reused by a redraw with the same
  inputs. Proven equal to a fresh build; every input re-keys it. At most
  `GEOMETRY_MEMO_CAP` geometries are kept.
- `emit_triangles` off: the build skips the triangles (the headless dummy renderer never
  draws them) and places every roof, window light, trail, beacon and sign exactly as a
  full build does (checked for every district, physical and net). The drawing code still
  runs in that test with triangles on.

A test that needs the triangles sets `NeonCity.emit_triangles = true` and puts it back.

### What bakes or threads run headless

`CityBakeCache.can_bake()` is false headless, so no city asks for a bake. With
`CityBakeCache.simulate` (test_anim_r2_city) the cities take the baked path but
`request` frees each painter at once: nothing builds, no worker task starts. Only two
tests start real worker builds, on purpose, by calling `request` directly
(`test_shutdown_stops_a_running_bake_and_frees_its_painter`,
`test_a_threaded_bake_builds_in_slices_and_lets_the_slot_go`); their `after_each`
`shutdown()` joins every task. A headless bake stops at its readback (the dummy renderer
never posts a frame) and never touches a RenderingDevice.

### Freeing views inside a frame (bake crash)

GUT's `add_child_autofree` frees with `free()` while the tree's `process_frame` emission
is still running (a test resumes from `await get_tree().process_frame`). A lambda using
self connected to a frame signal would then run on freed memory: scripts connect methods
to `process_frame` / `physics_frame` / `frame_pre_draw` / `frame_post_draw`, never
lambdas. `test_suite_integrity.gd` guards it in `scripts/`, `tests/` and `tools/` (a
test's or a lab's lambda outlives a freed node the same way; ANIM-R4 H8), in every form:
`<sig>.connect(func`, any spacing, `connect("<sig>", func`, `Signal(obj, "<sig>").connect(`,
`Callable(func`, a lambda held in a variable, a `func` on the line after an open call.
`test_bake_crash.gd` reproduces the crash on the old code. See DECISIONS "Animation pass —
bake crash".

### Waiting on motion (bounded waits)

A test that starts a motion (`Motion.force_live`) never waits a fixed time before asserting
how far it got: under parallel shards one slow frame, a tween chain that starts a frame
late or a timer firing before the tween it waits for lands the assert early. Use
`BoundedWait` (`tests/helpers/bounded_wait.gd`):

- `await BoundedWait.until(get_tree(), cond, limit)`: polls `cond` once a frame and
  returns as soon as it holds; gives up only after `limit` seconds of game time (the
  frames' deltas, the clock tweens and timers run on) **and** `MIN_FRAMES` frames. Derive
  the limit from the Motion table: `BoundedWait.motion_limit([&"id", ...])` (their delay
  and seconds plus `SLACK`). Then assert on the end state.
- `await BoundedWait.timed(get_tree(), cond, limit)`: the same, returning the game time
  the motion took less its two longest frames, for "ends in its time" asserts.
- `await BoundedWait.frozen_frames(get_tree(), n)`: `n` frames with `Engine.time_scale`
  0, for an assert that a motion is still under way after the layout's frames.
- Count events instead of catching a state mid-way (`WheelView.tag_flips`), and poll
  view-side queries (`motion_busy()`, `PageTransition.running()`, `FlightFx.active_count()`).

`test_suite_integrity.gd` fails on a fixed wait or a wall-clock read in a test script that
an assertion follows in the same test (or in any helper function, whose caller asserts):
`create_timer(`, `wait_seconds(`, `Time.get_ticks_msec/usec(`, a `tween_interval(` that is
awaited (on its line, or a later `await ... .finished` in the function; an interval that
only keeps a sequence running is no wait), a Timer made in the test (`Timer.new()`, its
`wait_time`), a blocking sleep (`OS.delay_msec(` / `OS.delay_usec(`) and the wall clock's
other reads (`get_unix_time`). A sleep inside a lambda (a poll's condition standing in for
a loaded machine's slow frames) is load, not a wait. Inner classes' methods are functions
of their own. The shared helpers in `tests/helpers/` are scanned too (ANIM-R5): every
function there is a helper, so any fixed wait in one is flagged; `BoundedWait`'s own polls
(a frame at a time, counting game time) are no fixed wait and carry no marker. A line (or
the comment line above it) carrying `# fixed-wait-ok: <reason>` is let through (a wait that
only lets motion run before a skip or settle, or the resolver's performance bound). See
DECISIONS "Test suite: bounded waits".

### Headless has no RenderingDevice

Tests run `--headless`: the dummy renderer never posts a frame and there is no
RenderingDevice, so GPU and rendering paths (the city bake's GPU copy, viewport readbacks,
shaders' look) never run in the suite. Three green runs shipped a grey city once (ANIM-R4).
A change to a rendering path is verified in a windowed run as well (the windowed render
check tool, or a Movie Maker capture of the scene: `--write-movie <dir>/f.png`, the folder
made first, and the frames read).

### The integrity rules stay fast

`test_suite_integrity.gd` reads each source once and compiles each pattern once, and reads
a line further only when it names a frame signal or a fixed-wait call: well under a second
of tests (ANIM-R5; it had grown to 40 s). That every test script compiles is
`test_suite_compiles.gd` (full tier): loading every script loads the whole game behind it,
most of a minute on its own. The parallel runner also reports any script that did not run.

## The 2026-09-27 optimization pass

### Before and after

| Run | Before | After |
|---|---|---|
| Single process, full suite | about 49 min for 858 tests (the coordinator's run on main); on the busy machine the main-tip baseline was stopped by its 60 min timeout at script 65 of 97 | 586 s and 744 s (two runs, 10-12 min) (864 tests) |
| Parallel runner, N=4 | 1697 s with the city switches off (the profiling run; no runner existed before) | 188, 292 and 281 s (median 281 s, 4.7 min) |
| Parallel runner, N=2 | | 427 and 406 s (about 7 min) |
| Parallel runner, N=1 | | 779 s (one run) |
| Sum of test times (the work) | 5299 s (4 shards, busy machine) | 551 s |

Other agents ran Godot on the machine throughout, so every time is noisy; the runner
times are medians where a run was repeated (N=4 ran three times, N=2 twice, N=1 once and the single process twice, one after another, all passing but the second single run, which caught the Polaroid tilt timing fixed since).

### Cost drivers found

1. **The headless city (about 87% of the test time: 5299 s of work fell to 668 s with the two city switches alone).** `NeonCity` builds its city in GDScript:
   2-4 s per build, and a build ran on every scene open (HQ, Grid, raid setup, route,
   combat arena), every Grid or raid camera fit pass (two or three each) and every
   resize. A test opening 30 settled Grids spent six minutes building the same few
   cities. The geometry memo and the skipped triangles make a build 0.3-0.5 s and a
   repeated one free.
2. **Sweeps that kept every scene alive.** The anim2 beat/number sweeps opened 12 fights
   each and freed none until the test ended, so every later frame processed all of them.
   Each sweep now frees a fight when it is done with it (anim2, H24 arrows and satellites).
3. **Overlapping sweeps.** Four passes each opened every corporation's Grid (50 settled
   Grids) to check the same maps; merged into one sweep of 30.
4. Smaller: fixed waits (`wait_seconds`, 40-60 frame settles), a 1.0 s linger in the
   netrun scene test, first loads of each scene (about 2-3 s once per process).

### Consolidation: removed tests and where each assertion lives now

Removed or merged tests, and for every assertion the test that keeps it
(`sweeps` = `tests/unit/test_city_map_sweeps.gd`). Scopes are the same or wider unless
noted.

| Removed test | Its assertions | Kept by |
|---|---|---|
| H21 city `test_grid_labels_never_overlap_for_every_corporation` | labels drawn; no two node icons overlap; no two labels overlap; no label covers a node icon (every corporation, early, 1.0) | sweeps `test_the_grid_for_every_corporation_text_size_and_stage` → `_assert_no_overlap`, early campaign at 1.0, 1.3 and 1.6 (wider) |
| | with the last node selected: the ring circles its icon, is wider than it, no label hits the ring, still no overlap | sweeps → `_check_every_selection(ring = true)` at 1.0, early, every corporation |
| | text size set to 1.5 live: no overlap | sweeps → `_check_live_text_size` (1.0 → 1.6 live: no overlap, labels on screen) |
| H21 city `test_route_labels_never_overlap_for_every_corporation` | route labels and icons apart at the start and under way, every corporation | sweeps `test_the_route_for_every_corporation` (same states) |
| H22 city `test_grid_labels_stay_on_screen_for_every_node_of_every_corporation` | every node selected in turn at 1.0 and 1.6: the selected Site labelled; every label inside the label area and clear of the side column's block; with home selected, every landmark labelled | sweeps → `_check_every_selection` (`_assert_on_screen`, the selected label, the landmarks) at 1.0 and 1.6 on fresh Grids; the live text change is covered by `_check_live_text_size`; the column block being registered is also asserted there |
| H22 city `test_route_you_are_here_stays_on_screen_for_every_corporation` | YOU ARE HERE labelled; route labels inside the area and clear of the route window, at 1.0 and 1.6, every corporation | sweeps `test_the_route_for_every_corporation` |
| H23 city `test_the_grid_at_every_corporation_and_text_size` | #3 the key on screen, over the map, clear of the column, text at the scale, rows at the scale, covering no node (1.0, 1.6) | sweeps → `_check_legend` at 1.0, 1.3, 1.6, early and late (wider) |
| | #5 every node icon and its tier pips on the map area, none under the column (1.0, 1.6) | sweeps → `_check_nodes_beside_the_column`, all 30 Grids (wider) |
| | #2/#4 every node selected: selected Site labelled, labels apart, inside the map, within LABEL_REACH (1.0, 1.6) | sweeps → `_check_every_selection` (1.0, 1.6, early) |
| | #7 run rows and Site steps carry their map icon and name the kind (Solace, 1.0, 1.6) | sweeps → `_check_run_rows_and_steps` (Solace, 1.0, 1.6) |
| H24 city `test_the_grid_keeps_its_map_labels_and_icons_at_every_text_size` | K1 key folds only at big text, one line folded; steps icon-only at big text with tooltips, inside the column; K6 icons apart; K1 labels apart, below the top bar, on the map area, within reach, every Site with room labelled (every corporation, 1.0/1.3/1.6, early and late); the zoom and reach log lines | sweeps → `_check_key_and_steps`, `_check_icons_apart`, `_check_labels_k1`, the same 30 Grids and log lines |
| H23 screens `test_the_saved_stamp_covers_no_control` (its screens) | SAVED on screen and covering no control on the raid setup, route and Modem at 1.0 and 1.6 (placement computed on the spot) | H24 screens `test_the_saved_stamp_is_placed_on_the_page_it_lands_on`: the same screens at 1.0 and 1.6 with the stamp where it really lands after an autosave, keyboard and pad (wider). H23 keeps the corner check as `test_a_control_in_the_corner_moves_the_saved_stamp` |

Not merged, on purpose (they look alike but check different states, or are the only
check of something): H20 and H21 "subtitles never cover a control" (different screen
sets; H21 also checks the band), H23 raid nodes inside the map (early campaign) and H24
late raid map (late campaign, the strip key), the raid legend tests of H22/H23 (different
rules), every combat pass (each is the regression guard of a fixed bug and costs seconds
now). No UI sweep was sampled down: every corporation has its own generated Grid (the
boss Site was clipped for four corporations once), 1.3 is `MapLegend.FOLD_SCALE`, and early
and late campaigns lay out differently; after the city fix the merged sweep costs about
a minute. Pure-core sweeps (1,000 map seeds, 500 preview turns, every wheel tick) are
fast and untouched.

The merged sweep checks H21's "no label covers a node icon" wherever H21 did and more (the
early campaign at every text size). Widened to the late campaign it failed at 1.3 and 1.6
for four corporations (the selected Site's long name over other nodes' icons); ANIM-R1 M13
fixed the layout (a closer search round the node, then a spot clear of other icons, else
the label is left out) and the late campaign is asserted too. H21 and H22 checked their Grids three
frames after opening; the merged sweep checks settled Grids (twelve frames, as H23 and H24
did).

Test count: 858 before; 6 tests removed into 2 merged ones, 1 H23 test reduced to its
corner check, 5 new switch tests, 2 new save-isolation tests and 3 new suite-integrity
tests: 864 after.

### Other changes to tests

- Fights freed as sweeps move on (anim2, H24).
- Robust timing: anim6 motion checks and the anim5 jack fade measure game time less the
  longest frame, with slack of the motion's own length (a stalled frame on a busy machine
  had failed fixed waits and wall-clock limits); the anim6
  event stamp compares with the row's own size (with fast frames the row was still in
  its entrance pop one frame after the page settled); the resolver timing takes the
  fastest of 20 short batches (same 300 turns, same 1 ms limit).
- Pad reachability puts back the pad state; the key-hint merge test starts on the keyboard.
- Save isolation per run (above) and the tests' temp files by process id.

## Profile

Measured with GUT's JUnit export (`-gjunit_xml_file`), whose per-test time includes the
test's `before_each` / `after_each`. "Before" is this branch with both city switches off
(a GUT pre-run hook set them, which is main's city code), run as 4 shards while other
agents also ran Godot: absolute seconds are inflated by the load, the ranking is what
matters. "After" is the final branch, one process, the command in CLAUDE.md.

### Before: top 40 tests (861 tests, 5299 s of test time)

| # | s | script | test |
|---:|---:|---|---|
| 1 | 349.7 | unit/test_horizontal_pass24_city.gd | test_the_grid_keeps_its_map_labels_and_icons_at_every_text_size |
| 2 | 186.3 | unit/test_anim2_combat_motion.gd | test_numbers_never_cover_the_next_resolving_needle |
| 3 | 167.1 | unit/test_anim2_combat_motion.gd | test_resolve_beats_match_the_engine_events |
| 4 | 153.4 | unit/test_horizontal_pass24_screens.gd | test_late_campaign_raid_map_fits_with_its_key_clear |
| 5 | 146.2 | unit/test_horizontal_pass24.gd | test_satellite_tokens_and_plates_keep_off_hp_next_and_last_turn |
| 6 | 138.7 | unit/test_horizontal_pass23_city.gd | test_the_grid_at_every_corporation_and_text_size |
| 7 | 128.3 | unit/test_anim6_screen_motion.gd | test_end_state_layout_is_the_instant_layout_at_every_text_size |
| 8 | 127.8 | unit/test_horizontal_pass23_screens.gd | test_raid_nodes_sit_inside_the_map_for_every_corporation |
| 9 | 122.2 | unit/test_horizontal_pass21_screens.gd | test_subtitles_cover_no_control_and_no_stat_tag_on_any_screen |
| 10 | 115.1 | unit/test_anim4b_run_drag_drop.gd | test_loot_dropped_where_it_goes_matches_taking_it |
| 11 | 113.9 | unit/test_horizontal_pass24_screens.gd | test_the_saved_stamp_is_placed_on_the_page_it_lands_on |
| 12 | 77.9 | unit/test_horizontal_pass22_city.gd | test_grid_labels_stay_on_screen_for_every_node_of_every_corporation |
| 13 | 75.3 | integration/test_netrun_scene.gd | test_a_whole_run_plays_through_the_scene_and_autosaves |
| 14 | 68.9 | unit/test_horizontal_pass23_screens.gd | test_the_saved_stamp_covers_no_control |
| 15 | 68.0 | unit/test_anim4b_run_drag_drop.gd | test_raid_interlude_asset_drags_match_their_buttons |
| 16 | 67.4 | unit/test_horizontal_pass20_screens.gd | test_subtitles_never_cover_controls_on_any_screen |
| 17 | 66.9 | unit/test_horizontal_pass21_city.gd | test_grid_labels_never_overlap_for_every_corporation |
| 18 | 60.5 | unit/test_horizontal_pass23_screens.gd | test_pad_prompts_on_hq_raid_route_shop_and_loot |
| 19 | 59.2 | unit/test_horizontal_pass22_screens.gd | test_more_below_covers_no_control |
| 20 | 54.9 | unit/test_horizontal_pass23.gd | test_satellite_hp_plates_keep_clear_of_the_tag |
| 21 | 48.0 | unit/test_anim4b_run_drag_drop.gd | test_an_event_reward_dropped_on_the_deck_matches_the_choice |
| 22 | 47.2 | unit/test_horizontal_pass21_city.gd | test_route_labels_never_overlap_for_every_corporation |
| 23 | 43.8 | unit/test_anim4b_run_drag_drop.gd | test_the_new_pieces_keep_the_layout_at_each_text_size |
| 24 | 42.8 | unit/test_horizontal_pass23_screens.gd | test_the_event_title_is_clear_of_the_subtitle_band_and_an_empty_band_hides |
| 25 | 39.5 | unit/test_horizontal_pass21.gd | test_last_turn_lines_match_the_real_hp_change |
| 26 | 38.8 | unit/test_anim4b_run_drag_drop.gd | test_modem_cards_and_daemons_dropped_on_their_tags_match_buy |
| 27 | 36.7 | unit/test_anim6_screen_motion.gd | test_a_loot_pick_ends_in_the_deck |
| 28 | 36.3 | unit/test_suite_integrity.gd | test_every_test_script_compiles |
| 29 | 35.7 | unit/test_horizontal_pass22_city.gd | test_route_you_are_here_stays_on_screen_for_every_corporation |
| 30 | 35.5 | unit/test_anim4_drag_drop.gd | test_the_new_pieces_keep_the_layout_at_each_text_size |
| 31 | 35.2 | unit/test_horizontal_pass20.gd | test_the_tags_show_every_change_the_turn_brings |
| 32 | 34.4 | unit/test_horizontal_pass21_screens.gd | test_every_stat_tag_has_its_icon_on_every_screen |
| 33 | 34.1 | unit/test_horizontal_pass22_screens.gd | test_subtitles_page_cjk_and_pseudolocalised_text_inside_the_band |
| 34 | 34.0 | unit/test_horizontal_pass23_screens.gd | test_a_long_subtitle_pages_and_says_it_goes_on |
| 35 | 33.1 | unit/test_anim6_screen_motion.gd | test_a_settings_change_animates_nothing |
| 36 | 33.0 | unit/test_horizontal_pass23_screens.gd | test_one_raid_legend_listing_what_the_map_shows_clear_of_the_tags |
| 37 | 32.0 | unit/test_horizontal_pass12.gd | test_raid_setup_end_and_title_panels_fit_at_every_text_scale |
| 38 | 30.0 | unit/test_horizontal_pass24_screens.gd | test_defence_cards_say_what_they_do_and_the_button_says_defend |
| 39 | 29.2 | unit/test_horizontal_pass24_screens.gd | test_a_keyboard_esc_never_leaves_when_settings_is_rebound |
| 40 | 28.1 | unit/test_horizontal_pass21_screens.gd | test_grid_side_column_scrolls_and_the_hq_says_there_is_more_below |

### Before: time per script

| s | tests | script |
|---:|---:|---|
| 481.1 | 23 | unit/test_horizontal_pass24_screens.gd |
| 464.9 | 18 | unit/test_horizontal_pass23_screens.gd |
| 443.2 | 16 | unit/test_anim4b_run_drag_drop.gd |
| 431.5 | 14 | unit/test_anim2_combat_motion.gd |
| 419.6 | 9 | unit/test_horizontal_pass24_city.gd |
| 334.1 | 15 | unit/test_horizontal_pass21_screens.gd |
| 302.3 | 16 | unit/test_anim6_screen_motion.gd |
| 266.4 | 19 | unit/test_horizontal_pass24.gd |
| 229.2 | 16 | unit/test_anim4_drag_drop.gd |
| 227.3 | 13 | unit/test_horizontal_pass22_screens.gd |
| 196.1 | 23 | unit/test_horizontal_pass20_screens.gd |
| 173.4 | 13 | unit/test_horizontal_pass21_city.gd |
| 171.1 | 5 | unit/test_horizontal_pass23_city.gd |
| 140.1 | 10 | unit/test_horizontal_pass22_city.gd |
| 128.6 | 17 | unit/test_horizontal_pass20.gd |
| 104.4 | 10 | unit/test_horizontal_pass23.gd |
| 94.4 | 14 | unit/test_horizontal_pass21.gd |
| 93.8 | 14 | unit/test_anim5_map_motion.gd |
| 79.7 | 3 | integration/test_netrun_scene.gd |
| 59.2 | 12 | unit/test_anim3_card_motion.gd |
| 53.1 | 14 | unit/test_horizontal_pass20_city.gd |
| 37.6 | 3 | unit/test_panel_widths.gd |
| 36.5 | 4 | unit/test_suite_integrity.gd |
| 35.1 | 6 | integration/test_visual_merge.gd |
| 32.2 | 7 | unit/test_horizontal_pass12.gd |
| 29.4 | 13 | unit/test_horizontal_pass1.gd |
| 28.6 | 8 | unit/test_horizontal_pass22.gd |
| 26.9 | 7 | unit/test_pad_reachability.gd |
| 16.5 | 9 | unit/test_pools.gd |
| 13.7 | 15 | unit/test_horizontal_pass14.gd |
| 13.6 | 4 | integration/test_title_and_menus.gd |
| 13.6 | 5 | integration/test_campaign_flow.gd |
| 12.1 | 4 | integration/test_layout_rules.gd |
| 9.1 | 5 | unit/test_horizontal_pass18.gd |
| 8.8 | 5 | unit/test_horizontal_pass5.gd |
| 7.6 | 6 | integration/test_combat_ui_pickers.gd |
| 7.6 | 7 | unit/test_horizontal_pass16.gd |
| 6.8 | 3 | unit/test_horizontal_pass19.gd |
| 6.5 | 5 | integration/test_vertical_pass2.gd |
| 6.0 | 9 | unit/test_horizontal_pass13.gd |
| 5.5 | 3 | unit/test_preview.gd |
| 5.3 | 7 | unit/test_horizontal_pass3.gd |
| 5.2 | 8 | unit/test_horizontal_pass15.gd |
| 5.0 | 3 | unit/test_simulation.gd |
| 4.4 | 6 | unit/test_horizontal_pass4.gd |
| 3.3 | 16 | integration/test_netrun.gd |
| 3.1 | 8 | unit/test_rebel_cell.gd |
| 3.0 | 5 | integration/test_combat_scene.gd |
| 2.9 | 3 | unit/test_audio_director.gd |
| 2.9 | 3 | unit/test_solace_content.gd |
| 2.4 | 3 | integration/test_netrun_extras.gd |
| 2.1 | 6 | integration/test_m3_answers.gd |
| 1.9 | 5 | integration/test_keyboard_combat.gd |
| 1.7 | 15 | unit/test_corporations.gd |
| 1.6 | 10 | unit/test_map_generator.gd |
| 1.4 | 11 | unit/test_horizontal_pass2.gd |
| 0.9 | 8 | unit/test_polish.gd |
| 0.7 | 7 | unit/test_horizontal_pass11.gd |
| 0.6 | 12 | unit/test_content_registry.gd |
| 0.4 | 18 | unit/test_motion.gd |
| 0.4 | 18 | unit/test_classes.gd |
| 0.3 | 8 | unit/test_nodes.gd |
| 0.3 | 8 | unit/test_ice_combat.gd |
| 0.2 | 26 | unit/test_cards.gd |
| 0.2 | 7 | integration/test_save_service.gd |
| 0.2 | 5 | unit/test_ring_segments.gd |
| 0.1 | 3 | unit/test_story_and_text.gd |
| 0.1 | 7 | unit/test_ice_campaign.gd |
| 0.1 | 5 | unit/test_settings_extras.gd |
| 0.1 | 10 | unit/test_targeting.gd |
| 0.1 | 9 | unit/test_drones.gd |
| 0.1 | 6 | unit/test_horizontal_pass17.gd |
| 0.1 | 10 | unit/test_firmware.gd |
| 0.1 | 8 | unit/test_resistance.gd |
| 0.1 | 14 | unit/test_campaign_rules.gd |
| 0.1 | 4 | unit/test_replay.gd |
| 0.1 | 8 | unit/test_statuses.gd |
| 0.1 | 8 | unit/test_breaker.gd |
| 0.0 | 6 | unit/test_daemons.gd |
| 0.0 | 11 | unit/test_wheel_math.gd |
| 0.0 | 5 | unit/test_resolution_order.gd |
| 0.0 | 7 | unit/test_accessibility.gd |
| 0.0 | 6 | unit/test_enemies_m2.gd |
| 0.0 | 7 | unit/test_raid_extras.gd |
| 0.0 | 6 | unit/test_rewind.gd |
| 0.0 | 6 | unit/test_input_map.gd |
| 0.0 | 9 | unit/test_raid_resolver.gd |
| 0.0 | 4 | unit/test_boss_telegraph.gd |
| 0.0 | 6 | unit/test_boss.gd |
| 0.0 | 3 | unit/test_respin_action.gd |
| 0.0 | 5 | unit/test_flash_limiter.gd |
| 0.0 | 6 | unit/test_heat_rules.gd |
| 0.0 | 11 | unit/test_rng_service.gd |
| 0.0 | 5 | unit/test_dialogue.gd |
| 0.0 | 2 | integration/test_raid_playout.gd |
| 0.0 | 10 | unit/test_campaign_config.gd |
| 0.0 | 6 | unit/test_combat_content.gd |

### After (single process): top 40 tests (864 tests, 551 s of test time)

| # | s | script | test |
|---:|---:|---|---|
| 1 | 66.0 | unit/test_city_map_sweeps.gd | test_the_grid_for_every_corporation_text_size_and_stage |
| 2 | 29.0 | unit/test_horizontal_pass24_screens.gd | test_late_campaign_raid_map_fits_with_its_key_clear |
| 3 | 22.0 | unit/test_city_geometry_memo.gd | test_a_build_without_triangles_places_everything_a_full_build_does |
| 4 | 20.0 | unit/test_pools.gd | test_every_event_choice_resolves |
| 5 | 17.1 | unit/test_horizontal_pass1.gd | test_every_corporations_events_resolve_in_its_own_campaign |
| 6 | 17.0 | unit/test_anim6_screen_motion.gd | test_end_state_layout_is_the_instant_layout_at_every_text_size |
| 7 | 14.5 | unit/test_horizontal_pass23_screens.gd | test_raid_nodes_sit_inside_the_map_for_every_corporation |
| 8 | 13.3 | integration/test_netrun_scene.gd | test_a_whole_run_plays_through_the_scene_and_autosaves |
| 9 | 13.2 | unit/test_horizontal_pass24_screens.gd | test_the_saved_stamp_is_placed_on_the_page_it_lands_on |
| 10 | 10.0 | unit/test_horizontal_pass20_screens.gd | test_subtitles_never_cover_controls_on_any_screen |
| 11 | 7.4 | unit/test_anim4b_run_drag_drop.gd | test_raid_interlude_asset_drags_match_their_buttons |
| 12 | 6.4 | unit/test_horizontal_pass20_screens.gd | test_the_grid_is_a_site_card_not_a_list_and_every_site_is_reachable |
| 13 | 6.2 | unit/test_horizontal_pass24_screens.gd | test_defence_cards_say_what_they_do_and_the_button_says_defend |
| 14 | 5.5 | unit/test_city_geometry_memo.gd | test_a_reused_geometry_equals_a_fresh_build |
| 15 | 5.0 | unit/test_city_map_sweeps.gd | test_the_route_for_every_corporation |
| 16 | 4.5 | unit/test_horizontal_pass21_screens.gd | test_subtitles_cover_no_control_and_no_stat_tag_on_any_screen |
| 17 | 4.1 | unit/test_horizontal_pass12.gd | test_raid_setup_end_and_title_panels_fit_at_every_text_scale |
| 18 | 4.0 | unit/test_horizontal_pass22_screens.gd | test_subtitles_page_cjk_and_pseudolocalised_text_inside_the_band |
| 19 | 3.8 | unit/test_horizontal_pass24_screens.gd | test_hq_raid_and_grid_words_are_translated_once |
| 20 | 3.5 | unit/test_anim4b_run_drag_drop.gd | test_loot_dropped_where_it_goes_matches_taking_it |
| 21 | 3.5 | unit/test_anim4b_run_drag_drop.gd | test_the_new_pieces_keep_the_layout_at_each_text_size |
| 22 | 3.4 | unit/test_anim4_drag_drop.gd | test_the_new_pieces_keep_the_layout_at_each_text_size |
| 23 | 3.4 | unit/test_preview.gd | test_preview_equals_actual_for_500_random_turns |
| 24 | 3.4 | unit/test_anim2_combat_motion.gd | test_resolve_beats_match_the_engine_events |
| 25 | 3.3 | unit/test_horizontal_pass22_screens.gd | test_more_below_covers_no_control |
| 26 | 3.2 | unit/test_horizontal_pass24_city.gd | test_the_step_row_stays_in_the_column_pseudolocalised |
| 27 | 3.2 | unit/test_anim4b_run_drag_drop.gd | test_views_never_change_game_state |
| 28 | 2.8 | unit/test_horizontal_pass23_city.gd | test_the_hq_mini_map_on_the_hq_page_keeps_labels_apart |
| 29 | 2.8 | integration/test_campaign_flow.gd | test_new_campaign_shows_hq_and_the_grid_lists_ten_t1_sites |
| 30 | 2.8 | unit/test_horizontal_pass22_city.gd | test_tier_pips_on_the_map_the_mini_map_and_the_legend |
| 31 | 2.6 | unit/test_anim4_drag_drop.gd | test_a_crew_chip_on_jack_in_matches_picking_them_and_pressing_jack_in |
| 32 | 2.6 | unit/test_horizontal_pass24_screens.gd | test_modem_text_icons_and_stickers_never_overlap |
| 33 | 2.6 | unit/test_horizontal_pass24_screens.gd | test_route_nodes_clear_of_the_route_column_and_choices_told_apart |
| 34 | 2.5 | unit/test_anim4_drag_drop.gd | test_recruit_and_boost_drops_match_their_buttons |
| 35 | 2.4 | unit/test_horizontal_pass21.gd | test_last_turn_lines_match_the_real_hp_change |
| 36 | 2.4 | unit/test_anim5_map_motion.gd | test_heat_pulse_fires_once_per_crossing_and_never_on_a_steady_value |
| 37 | 2.4 | unit/test_anim4b_run_drag_drop.gd | test_keys_and_pad_reach_every_target_and_drop_like_the_mouse |
| 38 | 2.3 | unit/test_anim4b_run_drag_drop.gd | test_a_chip_on_a_slot_it_does_not_fit_is_refused_with_the_rule_in_names |
| 39 | 2.3 | unit/test_horizontal_pass23_screens.gd | test_pad_prompts_on_hq_raid_route_shop_and_loot |
| 40 | 2.2 | unit/test_horizontal_pass24_city.gd | test_the_folded_key_opens_on_hover_press_and_pad_and_does_not_refit |

### After (single process): time per script

| s | tests | script |
|---:|---:|---|
| 71.0 | 2 | unit/test_city_map_sweeps.gd |
| 70.7 | 23 | unit/test_horizontal_pass24_screens.gd |
| 33.4 | 16 | unit/test_anim4b_run_drag_drop.gd |
| 29.5 | 23 | unit/test_horizontal_pass20_screens.gd |
| 28.0 | 18 | unit/test_horizontal_pass23_screens.gd |
| 27.8 | 5 | unit/test_city_geometry_memo.gd |
| 24.0 | 16 | unit/test_anim6_screen_motion.gd |
| 22.7 | 16 | unit/test_anim4_drag_drop.gd |
| 21.2 | 13 | unit/test_horizontal_pass1.gd |
| 20.6 | 9 | unit/test_pools.gd |
| 17.4 | 13 | unit/test_horizontal_pass22_screens.gd |
| 15.7 | 15 | unit/test_horizontal_pass21_screens.gd |
| 15.0 | 3 | integration/test_netrun_scene.gd |
| 12.1 | 14 | unit/test_anim5_map_motion.gd |
| 12.1 | 14 | unit/test_anim2_combat_motion.gd |
| 10.5 | 8 | unit/test_horizontal_pass24_city.gd |
| 7.6 | 11 | unit/test_horizontal_pass21_city.gd |
| 7.2 | 14 | unit/test_horizontal_pass21.gd |
| 6.7 | 5 | integration/test_campaign_flow.gd |
| 6.6 | 19 | unit/test_horizontal_pass24.gd |
| 6.3 | 17 | unit/test_horizontal_pass20.gd |
| 6.0 | 14 | unit/test_horizontal_pass20_city.gd |
| 6.0 | 4 | unit/test_horizontal_pass23_city.gd |
| 5.7 | 8 | unit/test_horizontal_pass22_city.gd |
| 5.1 | 10 | unit/test_horizontal_pass23.gd |
| 4.4 | 3 | unit/test_panel_widths.gd |
| 4.2 | 7 | unit/test_horizontal_pass12.gd |
| 4.2 | 12 | unit/test_anim3_card_motion.gd |
| 3.4 | 3 | unit/test_preview.gd |
| 3.1 | 7 | unit/test_pad_reachability.gd |
| 2.4 | 11 | unit/test_horizontal_pass2.gd |
| 2.2 | 5 | integration/test_combat_scene.gd |
| 2.2 | 4 | integration/test_title_and_menus.gd |
| 2.0 | 3 | unit/test_solace_content.gd |
| 2.0 | 6 | integration/test_visual_merge.gd |
| 1.8 | 16 | integration/test_netrun.gd |
| 1.7 | 8 | unit/test_horizontal_pass22.gd |
| 1.7 | 3 | unit/test_simulation.gd |
| 1.6 | 3 | integration/test_netrun_extras.gd |
| 1.5 | 10 | unit/test_map_generator.gd |
| 1.4 | 4 | integration/test_layout_rules.gd |
| 1.3 | 15 | unit/test_horizontal_pass14.gd |
| 1.2 | 6 | unit/test_horizontal_pass4.gd |
| 1.2 | 6 | integration/test_m3_answers.gd |
| 1.1 | 3 | unit/test_horizontal_pass19.gd |
| 1.0 | 7 | unit/test_horizontal_pass16.gd |
| 1.0 | 15 | unit/test_corporations.gd |
| 1.0 | 5 | unit/test_horizontal_pass5.gd |
| 1.0 | 7 | unit/test_horizontal_pass3.gd |
| 0.9 | 8 | unit/test_rebel_cell.gd |
| 0.9 | 8 | unit/test_polish.gd |
| 0.9 | 5 | integration/test_vertical_pass2.gd |
| 0.8 | 3 | unit/test_audio_director.gd |
| 0.7 | 6 | integration/test_combat_ui_pickers.gd |
| 0.7 | 9 | unit/test_horizontal_pass13.gd |
| 0.6 | 7 | unit/test_horizontal_pass11.gd |
| 0.5 | 9 | unit/test_drones.gd |
| 0.5 | 8 | unit/test_nodes.gd |
| 0.5 | 3 | unit/test_story_and_text.gd |
| 0.5 | 18 | unit/test_motion.gd |
| 0.5 | 8 | unit/test_ice_combat.gd |
| 0.5 | 5 | integration/test_keyboard_combat.gd |
| 0.4 | 8 | unit/test_horizontal_pass15.gd |
| 0.4 | 18 | unit/test_classes.gd |
| 0.4 | 4 | unit/test_suite_integrity.gd |
| 0.4 | 12 | unit/test_content_registry.gd |
| 0.3 | 26 | unit/test_cards.gd |
| 0.3 | 5 | unit/test_horizontal_pass18.gd |
| 0.3 | 7 | unit/test_accessibility.gd |
| 0.2 | 10 | unit/test_targeting.gd |
| 0.2 | 2 | integration/test_raid_playout.gd |
| 0.2 | 7 | unit/test_ice_campaign.gd |
| 0.2 | 11 | unit/test_wheel_math.gd |
| 0.2 | 8 | unit/test_statuses.gd |
| 0.2 | 10 | unit/test_firmware.gd |
| 0.1 | 5 | unit/test_settings_extras.gd |
| 0.1 | 8 | unit/test_resistance.gd |
| 0.1 | 6 | unit/test_heat_rules.gd |
| 0.1 | 5 | unit/test_flash_limiter.gd |
| 0.1 | 5 | unit/test_ring_segments.gd |
| 0.1 | 9 | integration/test_save_service.gd |
| 0.1 | 6 | unit/test_horizontal_pass17.gd |
| 0.1 | 14 | unit/test_campaign_rules.gd |
| 0.1 | 8 | unit/test_breaker.gd |
| 0.1 | 4 | unit/test_replay.gd |
| 0.1 | 11 | unit/test_rng_service.gd |
| 0.1 | 6 | unit/test_enemies_m2.gd |
| 0.1 | 6 | unit/test_daemons.gd |
| 0.1 | 9 | unit/test_raid_resolver.gd |
| 0.1 | 5 | unit/test_resolution_order.gd |
| 0.1 | 6 | unit/test_rewind.gd |
| 0.1 | 7 | unit/test_raid_extras.gd |
| 0.0 | 6 | unit/test_boss.gd |
| 0.0 | 5 | unit/test_dialogue.gd |
| 0.0 | 6 | unit/test_input_map.gd |
| 0.0 | 10 | unit/test_campaign_config.gd |
| 0.0 | 6 | unit/test_combat_content.gd |
| 0.0 | 3 | unit/test_respin_action.gd |
| 0.0 | 4 | unit/test_boss_telegraph.gd |

