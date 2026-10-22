# Brief: H7 Bastion raid lab (playable Godot prototype)

This is a design-lab prototype for the raid design lab (branch `claude/raid-design-lab-2d2e2e`). It is not an area fix.
Put everything under `tools/raid_lab_h7/`. Never touch `scripts/`, `scenes/`, `content/`, `tests/`, `project.godot`, or
`D:/rc_art`.

## Source of truth (port these exactly)
- **`tools/raid_concepts/sim.py`** is the resolver mirror. Use the rule set `h7_campaign.RULE`:
  - fixed_routes;
  - avoid_home;
  - tiebreak "weakest";
  - ice_blocks;
  - no_cascade;
  - crew_flat.

  Port only what these toggles need: fixed routes, threat traits, the Lockdown link freeze, start_taken, and rounding
  with halves away from zero.
- **`tools/raid_concepts/h7_campaign.py`** holds the leg rules. Port:
  - `State`;
  - `roster_for` (foothold entry, corp-adaptation trait);
  - `raid_result`;
  - `settle` (payout, repair bill, free scuff heal after CLEAN, TAKEN = lost node for the leg, survivors rejoin,
    income by node job);
  - the costs and constants.
- **`tools/raid_concepts/h7_golden.json`** holds the golden results. The port must reproduce every field **exactly** for
  both lines of leg 0: roster, frozen, steps, nodes, kills, clean, net, bank, lost, survivors. The file also holds 5
  seeded legs' rosters, all of which must be playable.
- **Visual reference:**
  - `docs/design/raid_concepts/h_bastion/r7/mockups/*.png` (layout, glyphs) and `h_bastion/SPEC_R6.md`;
  - `tools/raid_concepts/concept_h7_bastion.py` (the PIL mockup code: what each panel contains).

  Placeholder vector `_draw()` visuals are fine; match the mockup layout and palette. Threats are cobalt `#3D6BFF`, the
  Cell is yellow, red is only for losses, teal only for the Cell's checks.

## Architecture
- **Rules:** deterministic `RefCounted` GDScript classes with static typing, one class per file, and `##` doc comments.
  No Nodes and no randomness (the legs are fixed data).
- **View:** a separate scene, `tools/raid_lab_h7/raid_lab_h7.tscn`, that only calls the rules and draws.
- **Scope:** text scale 1.0, mouse and keyboard, US English.

## Playable flow
One leg of 3 raids, with a picker for the 5 legs.

1. **Leg view.**
   - The telegraphed raid panels show Heat, netruns before the raid, and the threats with their traits; survivors are
     marked. While the PROXY holds, two raids ahead are shown; otherwise one.
   - The map shows 6 nodes, 2 corp sites and the node job icons.
   - The bank is shown as a strongbox.
2. **Visit.**
   - **Shop:** 5 pieces with their costs. Click a piece, then a held node, to buy and place it: at most 2 per visit,
     within the bank. Undo is allowed before START.
   - **Crew:** click the crew, then a node (only while the SAFEHOUSE holds).
   - **Live fortress forecast:** this raid plus the remaining telegraphed raids, with this fortress and no further buys.
     Each raid shows: clean, lost nodes, net (a signed coin), and the bank after (a strongbox).
   - **Map:** the fixed cobalt routes and per-node outcome tags (HOLDS, SCUFFED -N, DOWN, TAKEN).
   - **Corp-adaptation chip:** the most-invested piece, then the trait, then the threat that gains it.
3. **START RAID.** A hands-off playout driven by the resolver's step log:
   - threats move;
   - shots appear with numbered badges, plus damage numbers;
   - about 1 s per beat;
   - the only controls are 1x / 2x / 4x / skip.
4. **Aftermath.**
   - A CLEAN / HOLDS / BREACHED stamp.
   - The net box: salvage × kills + clean bonus − patch = net.
   - Income by job: base + Vault + Relay.
   - The node marks.
   - A "Next visit" button.
5. **Leg record.** A bank line and the CLEAN shields.

## Verification (required)
1. **Parity check.** `tools/raid_lab_h7/parity_check.gd` (a SceneTree script) replays both leg-0 lines from the golden,
   prints PASS/FAIL per field, and exits 0 only on full parity. Run it with:
   `timeout 300 godot --headless --path . -s res://tools/raid_lab_h7/parity_check.gd > D:/rc_tmp/raid_design_lab/lab/parity.log 2>&1`

   Import first if needed:
   `godot --headless --path . --import > D:/rc_tmp/raid_design_lab/lab/import.log 2>&1`

   It must PASS.
2. **Capture mode.** `-- --shots=<abs dir>` auto-plays leg 0's planned line and saves PNGs at each of:
   - the leg view;
   - each visit;
   - 3 beats of raid 1;
   - each aftermath;
   - the record.

   Run it windowed **only** with:
   `python tools/run_windowed.py --log D:/rc_tmp/raid_design_lab/lab/capture.log -- --resolution 1280x720 res://tools/raid_lab_h7/raid_lab_h7.tscn -- --shots=D:/rc_tmp/raid_design_lab/lab/shots`

   Then Read the PNGs and fix any overlaps, clipped text or unreadable glyphs.
3. **README.** `tools/raid_lab_h7/README.md` covers how to run the lab, what is ported, and the parity status.

## Machine rules
- **Output location.** All temp files, logs and captures go under `D:/rc_tmp/raid_design_lab/lab/`. Set TEMP=TMP=D:/rc_tmp/tmp.
- **Godot runs.** Never pipe Godot output; redirect it to a file. Wrap headless runs in `timeout`.
- **Python.** NEVER type `python -` in any form. Write a `.py` file and run it.
- **Windowed runs.** Run windowed Godot only through `tools/run_windowed.py`, one window at a time.
- **Process hygiene.** Kill only the processes you started. Do not run the full test suite.
- **Git.** Commit on your own branch only. Never push, and never merge to main.
