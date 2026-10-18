# Handoff: merge the visual/UI pass, re-review, resume the fix loop (H20)

Paste everything below the line into a new Claude Code session opened at
`C:\Users\noitu\Documents\Godot\rebel_cell`. This version reflects the visual branch at tip
`39caa10` (32 commits) and `main` at `d9654b5` (H19). If either has moved on, run `git fetch`
and re-check Step 1's facts before merging.

---

You are continuing work on **REBEL_CELL** (Godot 4.7.2 / GDScript cyberpunk roguelite
deckbuilder). Repo: `https://github.com/Noitues/REBEL_CELL.git`, branch `main`.

Before anything else, read:
- `CLAUDE.md`, `docs/MILESTONES.md`, `docs/GDD.md`, `docs/TECH_SPEC.md`;
- `docs/DECISIONS.md` (newest entries first; H1–H19);
- `docs/GAP_ANALYSIS.md` (the H1–H19 table).

After the merge, also read the branch's `docs/STYLE_GUIDE.md` (§1.1 and §4 were rewritten by the
visual pass) and `docs/ANIMATION_HANDOFF.md`.

## Standing rules (from the designer)

- Work through the whole task without asking questions. Make a call on every decision, pick the
  simplest option consistent with the GDD, and log it in `docs/DECISIONS.md`. Open designer
  questions go under "Open questions for the designer".
- When in doubt about balance, raise elite and boss strength. The current balance is already on
  the slow side (see the state at handoff), so don't retune unless a fix clearly calls for it;
  record the simulator numbers after any combat change.
- **Pause points.** Stop and report:
  1. after the merge plus the vertical and horizontal re-review (step 3);
  2. then after each fix batch **and** its follow-up review.

  The designer resumes you each time.
- **Motion is out of scope.** The branch includes `docs/ANIMATION_HANDOFF.md`, a brief for a
  *separate* motion/animation agent. Do not start that work. Keep the document intact, and keep
  its ground rules true: animations are views only, respect reduce-effects and the flash limiter,
  never block logic headless, and have no magic numbers.
- CLAUDE.md rules are non-negotiable:
  - a deterministic pure core;
  - RNG only through streams;
  - never mutate loaded Resources;
  - signal up, call down;
  - no magic numbers (use config / `.tres`);
  - every rule gets a test;
  - deterministic tie-breaks;
  - log schema changes and add them to `tools/schema_smoke_test.gd`.
- Commits: small, one per pass or batch, with the acceptance criteria in the message, ending with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Push to `origin main` after each
  green batch. Stage explicitly. Never `git add -A` at the repo root, because the designer keeps
  personal files around. `docs/reference/` is theirs; commit it only when asked.
- Keep timeline screenshots in `docs/timeline/` with a README row when a visual milestone lands.

## Machine and tool practice (important)

- Godot 4.7.2 is on PATH.
- **Never pipe Godot output.** Redirect it to a file in the session scratchpad and wrap the
  command in `timeout`. A `-s` script that fails to parse never quits.
- Run `godot --headless --path . --import` after adding a `class_name`, script or content. The
  branch adds many new `class_name` kit scripts, so import right after the merge.
- Checks: run all three before declaring anything done.
  - Tests: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`
  - Smoke test: `godot --headless --path . -s tools/schema_smoke_test.gd`
  - Content validation: `godot --headless --path . -s tools/validate_content.gd`
- Balance: `godot --headless --path . -s tools/simulate_campaign.gd -- <seeds> <ice> [verbose] class=<id> corp=<id>`.
  The baseline is `-- 8 5` (Breaker vs Solace, ICE 5). Several can run in parallel in the
  background. Wait with an `until grep -q '^SIMULATION' file; do sleep 5; done` loop, not a bare
  sleep.
- Bash heredocs break on apostrophes and `\n`. Write patch scripts with the Write tool (a Python
  `patch(path, [(old, new)])` helper that asserts the old text exists), then run them.
- Tests must use `gut_`-prefixed save slots. Slots with that prefix keep a private profile; every
  other slot shares `profile.json`.
- Tests that change `Settings` must restore it in `after_each`. After every run, check that
  `%APPDATA%/Godot/app_userdata/REBEL_CELL/settings.json` still has `"text_scale": 1.0` and
  `"keybinds": {}`. A crashed run once left it at 1.6. After the merge, settings.json also
  carries `map_legend` and `system_log`; check that tests restore those too.
- GDScript gotchas:
  - A lambda captures ints by value; use an Array as a counter.
  - `var x := <untyped expr>` fails to parse; type it.
  - Deferred static calls need untyped parameters and an `is_instance_valid` check.
  - `CombatSession.apply` replaces `s.state`, so re-fetch combatants after an action.
  - A CanvasLayer stops theme inheritance: call `UiTheme.apply()` on anything placed on one.
- Headless mouse clicks only register if you hide GUT's `GutLayer`, send the viewport
  `NOTIFICATION_VP_MOUSE_ENTER`, and map positions through `get_final_transform()`. The
  headless window is 64x64.
- Auditor agents: tell them to do the work themselves, with no sub-agents. Sub-agents return
  early and their parent reports nothing. Throwaway tests go in the scratchpad, run with
  `-gdir=<dir>`, never in the repo. Tell them the project files are read-only and give them the
  settings.json and `gut_` rules above.

## Step 1: merge the parallel visual/UI branch into main

### Facts

- **Branch:** `origin/claude/game-visual-ui-update-pkc0aj`, tip `39caa10`. It forked from main
  at `2b35d87` (H16) and has 32 commits: 111 files, about +8,400 / −500 lines. It has **not**
  merged anything from main since the fork.
- **Main since the fork:** H17 (`3eb394c`), H18 (`7cc8bac`) and H19 (`d9654b5`).
- **Branch contents, by area:**
  - **The city.** One city with organic corporate territories and culture HQs (`NeonCity`,
    `CityLayout`, `CityMapOverlay`). The Grid, raids and the netrun route live on the city
    map, with a legend toggle.
  - **HQ and chrome.** A top bar (neon title, ransom-note stats, VIEW LOADOUT), a loadout
    view, and deck and spinner viewers. A HUD bar and screen headers, terminal windows and
    crew dossiers. `DripLabel` / `DripButton` lettering, `StickerButton`, a Daemon tray.
  - **Screens.** Modem quadrants with the MODEM sign, a raid war table and raid board, a
    daily-run panel, the title menu.
  - **Wheels and effects.** Pink/cyan translucent slices with bold slice icons (wheels,
    spinner view, Modem tiles). Zine paper, portrait styles, and a subtitle dock in combat.
  - **Combat, rebuilt in the owner's chosen style.**
    - The dropdown `controls_row` is hidden.
    - The preview wall (`preview_note`) and the log strip (`log_note`) are hidden.
    - What will resolve is shown as an `intent` tag over each spinner.
    - Actions are `StickerButton`s around the player spinner (`_stickers`: nudge_l,
      nudge_r, respin, undo, wheel, ring, cards, dir).
    - SEND IT is a `DripButton`.
  - **HQ and netrun system log.** Hidden by default behind the new Options toggle
    `Settings.system_log`.
  - **New Settings.** `map_legend` (default on) and `system_log` (default off), both
    serialised. Test `test_system_log_strip_shows_only_when_toggled_in_options`.
  - **`Fx`.** The screen-wide scanline and aberration are off; only a faint vignette and
    flicker remain. The shader parameters are inline in `fx.gd`, so check them against the
    no-magic-numbers rule.
  - **Tools and docs.**
    - `tools/design_lab/*.tscn` / `.gd`: concept review scenes (city poster, combat, Daemon,
      Modem backdrops, portraits, top bar). These are dev tools; keep them out of any export
      and make sure they don't break import or tests.
    - `docs/ANIMATION_HANDOFF.md`, a STYLE_GUIDE rewrite, and "Visual pass" DECISIONS entries.
- **Files changed on both sides.** Expect conflicts in:
  - `docs/DECISIONS.md`
  - `scripts/autoload/dialogue.gd`
  - `scripts/autoload/settings.gd`
  - `scripts/ui/combat_scene.gd`
  - `scripts/ui/hq_scene.gd`
  - `scripts/ui/kit/pause_menu.gd`
  - `scripts/ui/kit/settings_panel.gd`
- **What the branch already has.** It carries main's H11–H16 behaviour: `UiWrap`, `focus_hand`,
  the pause-menu CanvasLayer and `MENU_SIZE`, `TUTORIAL_RECT`, `phase_layout`, `node_heat`,
  `choice_error`, `repair_cost`, and the rest.
- **What the branch lacks: H17–H19.** The merge must bring all of it in:
  - **H17:**
    - the pause-menu `Backdrop` (full-screen, `MOUSE_FILTER_STOP`, `_cover_screen`);
    - `Settings.bind_error` / `RESERVED_KEYS` and the kept-waiting rebind;
    - Shunt landings and the resolver copy rules. These are core files with no conflict, so
      they merge cleanly, but verify them.
  - **H18:**
    - `reset_keybinds()` re-applies the controller binds;
    - `UiTheme.apply(_settings_panel)` for the combat pause menu on its CanvasLayer;
    - subtitle font sizes from `Settings.text_scale` (`SPEAKER_FONT_SIZE` / `TEXT_FONT_SIZE`,
      `_apply_text_scale`);
    - Mirror copies dropping only the Overclock boost (core).
  - **H19:**
    - the wrapped `BindNote` label for refused rebinds;
    - `_refresh_key_hints()` on `Settings.changed`, with every hint from `Settings.key_text`;
    - HQ key hints from the bound Pause key;
    - the README autoload list.

### Conflict resolution: keep the branch's look and main's behaviour

1. `git fetch`, then `git switch -c merge/visual-into-main main`, then
   `git merge --no-ff origin/claude/game-visual-ui-update-pkc0aj`.
2. Resolve each conflict:
   - **`settings.gd`:**
     - keep both sets of additions: the branch's `map_legend` / `system_log` fields,
       setters and serialisation, and main's `key_text`, `bind_error`, `RESERVED_KEYS`, and
       `reset_keybinds()` calling `apply_controller_bindings()`;
     - `to_dict` / `from_dict` must carry every field.
   - **`settings_panel.gd`:**
     - keep the branch's new Accessibility checks (map legend, system log) and its styling;
     - keep main's `_input` rebind capture, the `bind_error` refusal written to the wrapped
       `BindNote` label (not the key button), `trap_focus`, `_get_minimum_size()` via
       `_paper_panel`, and `UiWrap.fit` per section.
   - **`pause_menu.gd`:**
     - keep the branch's styling;
     - keep main's `Backdrop` ColorRect (first child, `MOUSE_FILTER_STOP`), `_cover_screen()`
       on ready and visibility, swallowing unhandled key and pad input, Esc in the Codex
       returning to the menu, and `UiFocus.trap`.
   - **`dialogue.gd`:**
     - the branch added a combat subtitle dock (`dock_bottom()`, `dock_at(rect)`), so keep it;
     - apply main's `_apply_text_scale()` to the branch's fonts;
     - at text scale 1.6 the docked rect must still fit the text: grow the dock rect with
       the scale, or let the text wrap within it.
     - Test it at 1.0 and 1.6 in combat and at HQ.
   - **`combat_scene.gd`:** the branch's layout wins, but these main behaviours must be kept or
     remapped onto the new UI:
     - **Key hints (H19):**
       - `_refresh_key_hints()` must now label the stickers and the SEND IT DripButton
         (`[key]` from `Settings.key_text`, including the sticker toggles'
         toggle_nudge_wheel / toggle_ring / toggle_card_target / toggle_direction);
       - keep the hidden `controls_row` options consistent if other code reads them;
       - update the labels on `Settings.changed`.
     - **Pause menu:** `UiTheme.apply(_settings_panel)` on the CanvasLayer menu (H18).
     - **Tutorial:** it sits at `TUTORIAL_RECT` over the old log-strip area. The log strip is
       now hidden, so re-place the tutorial where it covers no wheel, sticker or intent tag,
       and keep it in `layout_violations`.
     - **`layout_violations`** must also cover the stickers and intent tags (no sticker over a
       wheel slice).
     - **Previews:** the End Turn preview logic (odds only for `random` status events, fixed
       slots named) now feeds the intent tags. Keep it correct there.
     - Keep `focus_hand()`, and the pad focus order across the hand, the stickers and SEND IT.
   - **`hq_scene.gd`:**
     - keep the branch's top bar, dossiers and log toggle;
     - keep main's `UiWrap.fit` in `_set_panel`, status wrapping, Site label wrapping,
       `Repair (N)`, `HeatRules.scaled_delta` Heat labels, `rookie_price`, the stationed note,
       `PauseMenu.MENU_SIZE` centring, and `Settings.key_text` hints.
   - **`docs/DECISIONS.md`:** keep both sides' entries, newest first. Where a visual-pass entry
     and an H17–H19 entry disagree (for example the log strip, preview wall or controls row),
     add a short "merge" entry saying which wins and why.
3. Run the import, then all three checks, and fix whatever the merge broke. Tests likely to need
   updating:
   - `tests/integration/test_layout_rules.gd`, which the branch already changed: keep its new
     assertions;
   - `test_combat_scene.gd`, `test_combat_ui_pickers.gd`, `test_keyboard_combat.gd`;
   - `tests/unit/test_panel_widths.gd`, `test_pad_reachability.gd`;
   - `test_horizontal_pass13.gd` (tutorial), `pass14` (netrun root width), `pass16` (pause
     layer), `pass18` (subtitles, combat pause theme), `pass19` (key hints);
   - `test_title_and_menus.gd`.

   Change a test only when the visual pass changed the layout on purpose, never to hide lost
   behaviour. Log each such change in DECISIONS.
4. Capture timeline screenshots of the merged screens into `docs/timeline/` (title, HQ with
   the top bar, Grid on the city, netrun route, combat with stickers, Modem, raid board), with
   README rows.
5. Commit the merge ("Merge visual/UI pass into main: …" with acceptance lines), then
   fast-forward `main` and push. Delete the local merge branch. Leave the remote visual branch
   alone.

## Step 2: re-review, vertical and horizontal

Run two audit agents. They can run in parallel, but each must do its own work with no
sub-agents.

- **Vertical re-review:**
  - Re-check every milestone M0–M12 acceptance box in `docs/MILESTONES.md` against the merged
    build, confirming each by running something. Pay most attention to STYLE_GUIDE compliance
    for the new visuals.
  - Check readability (GDD 9.2): no zine element, sticker, intent tag, tutorial or subtitle
    dock over a wheel slice or pointer at decision time.
  - Check 1280x720 fit at text scale 1.0 and 1.6 on every screen, including **heights** (the
    embedded netrun fight especially).
  - Check pad reachability and focus on every panel, modal and the new sticker controls.
  - Check that previews still equal results (the intent tags must show what really resolves),
    and that save/resume works mid-fight, mid-event, mid-shop and mid-raid.
  - Check that the tutorial still runs and makes sense in the new combat layout.
  - Check that the design-lab scenes don't affect the game.
- **Horizontal re-review:**
  - Look for consistency gaps across all five corporations, eight classes, home variants, the
    ICE ladder and assist mode.
  - Check that every new visual works for each corporation: city territories and culture HQs,
    district colours, the raid board and dossiers for REBEL_CELL and the Mirror elites, and
    all eight classes' portraits and spinners.
  - Check that the new UI code keeps Signal Up / Call Down, holds no game state, uses no game
    RNG (decoration randomness must come from hashes), has no magic numbers (`fx.gd` shader
    parameters, NeonCity tuning), and has tests.
  - Check that `map_legend` and `system_log` persist and are reachable by pad.

## Step 3: build the H20 list and PAUSE

Combine both re-reviews with the four items from the pass-20 review. That review ran on
**main before the merge**. Re-check each against the new UI: the combat rework may have fixed,
changed or worsened them.

1. **P1: netrun fights cut off the hand and SEND IT at text scale 1.3 and above.**
   - On main, the combat scene sits in the netrun ScrollContainer with a combined minimum size
     of (0,0), so the scroll range stays 0. Measured at 1.6: 57% of each card and SEND IT is
     visible.
   - Re-measure with the merged layout (DripButton SEND IT, stickers, subtitle dock, hidden
     log strip).
   - Fix: give the embedded combat a real minimum height so the scroll works, or compress the
     layout with the text scale. Add a **height** test at 1.6.
2. **P2: the End Turn preview hid Heat, Cycles, Schematics, RAM, resistance, Hub Breach,
   Cleanse, card draw, Steady Hand, Kernel Sync and Zero Day results.**
   - On main, `_show_end_turn_preview` printed only a fixed list of event types. For example,
     Burner's `MODIFY_HEAT +1` never showed.
   - In the merged build the preview wall is hidden and the intent tags carry the preview.
     Check that the tags, or something the player can see, show every resolve result,
     including campaign effects as "Heat +N" via `HeatRules.scaled_delta` (GDD 2.10: "the full
     outcome").
3. **P2: pad players only see keyboard keys.**
   - `Settings.key_text` names keyboard keys only. It's used by every hint, the DripButton
     SEND IT label, and the tutorial ("Press Q or E", "Right-click any slice to inspect it").
   - Fix: add a pad-button name helper and use it when the last input came from a pad. That
     includes the stickers and the tutorial.
4. **P3: rebind hints go stale outside combat.**
   - HQ has no `Settings.changed` listener, and tutorial text is filled in only when a step is
     shown.
   - Fix: HQ rebuilds its current panel on `Settings.changed`, and the tutorial redraws its
     current step. Include the branch's new top bar and stickers in the check.

Also mentioned by the pass-20 audit, not confirmed: hints and refusal messages use physical key
names, while the Controls grid converts to the keyboard layout, so they may disagree on AZERTY.
Check it if you can.

Write the combined list into `docs/GAP_ANALYSIS.md` as the pending H20 row, then **PAUSE and
report** the numbered list to the designer, ranked by severity.

## Step 4: when resumed, run the fix and review loop

- For each batch Hn, starting at H20:
  1. fix every item;
  2. add `tests/unit/test_horizontal_passNN.gd`;
  3. run all three checks;
  4. run the balance simulator if combat rules changed;
  5. write a DECISIONS entry and a GAP_ANALYSIS row, and update the test count in
     GAP_ANALYSIS;
  6. commit and push.
- Then run the next audit (pass n+1) with an audit prompt like the earlier ones:
  - state what the batch changed;
  - ask it to verify those changes and their neighbours;
  - ask it to look for any remaining player-facing gaps;
  - require a verified list (severity, file:line evidence, the failure, a fix) or CLEAN.
- Pause and report after each review, as the designer asked.
- Stop the loop when an audit returns CLEAN.

## State at handoff (main `d9654b5`, H19; visual branch `39caa10`)

- **Tests on main:** 533 passing. The schema smoke test and content validation pass. The branch's
  own test state is unknown until the merge.
- **Balance** (bot, 8 seeds, main): Breaker ICE 5 wins 2/8, averaging about 49 runs, against the
  GDD 11.8 target of about 24. Earlier: Ghost ICE 0 6/8 in 27 runs, Botnet ICE 0 8/8 in 22,
  Rigger ICE 0 5/8 in 36.
- **Why it's slow:** passes H12–H18 closed loopholes that had been carrying the bot:
  - Daemons fired once per resolution and once per Mirror copy;
  - Mirror and Burner copies took Overclock bonuses for free;
  - the final Rack offered a Daemon.
- **Open designer questions** (in DECISIONS): pacing; the Rigger at ICE 0; the final Rack's
  prize. A deliberate balance pass is likely needed once the designer answers.
- **Next after this loop:** motion and animation, per `docs/ANIMATION_HANDOFF.md`, by a
  separate agent.
