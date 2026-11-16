# Review 2026-11-16: plates vs the game (port-campaign-b @ ffb8c8db)

Real captures of the merged port (Deface v3 fight look, raid look on the v42 slots (S8e), HQ integrity art + D1 end
memo, the staged street run), each set beside the approved / latest art plate. Left = plate, right = the game. Each row
has a "Differences" caption written after looking at both.

| Sheet | Rows | Plates from |
|---|---|---|
| `sheet_fight.jpg` | board at rest, WORM held (picks), a single-target program held (TIME LOCK), forecast hover, cannot-stick refusal, COMMIT replay mid-step, win | `takeover_board/v3/v3_*.png`; cannot-stick: `takeover_board/inspiration/rendered/df3_invalid.png` (v3 has no refusal plate) |
| `sheet_raid.jpg` | brief with the work order folded and unfolded, PURGE plan, PURGE with a shotgun held (street slots lit), site raid held + legal hover, site refused slot, PURGE playback mid-round, after-action report | set 8 `raid_v3/set8/r8_*.png` (v42 DRAFT), set 7 `raid_v3/r3_plan.png`, `r3_aftermath.png` |
| `sheet_hq_end.jpg` | HQ damage stages 0 / 2 / 4, HQ workshop (in game over the map, and alone at stage 3), end won, end lost | `round42_hq_room/hq_room.png`, `hq_actions.png`; `solace_endscreens/d1_win.png`, `d1_lose.png` |
| `sheet_street.jpg` | first layer (street entry), pick-B hover, middle layer L4, last street layer L6, city overview | `netrun_cel/zoom_rules/staged_run/run8_*.png`, `netrun_cel/street_b/street_branch_B_next.png` |

`captures/` holds every raw PNG (1920 x 1080), including extra states not on the sheets (`*_x*`, `street_x_L*`,
`hq_stage_1/3`, `end_lost_mid_arrival`, `end_*_bgame`).

## How they were captured
Worktree `D:/rc_art/review_cap` at ffb8c8db, `godot --headless --path . --import` once, then one windowed run at a time:

    python tools/run_windowed.py --log <log> -- --resolution 1920x1080 res://tools/b_capture/review_hires.tscn -- \
        --tool=res://tools/b_capture/<tool>.tscn --out=<dir>

- `<tool>` = `b_raid_capture` (site raid, v42 refusals, PURGE playback + facts), `b_look_capture` (HQ stages, workshop
  stage 3, end memo won / lost), `b_g3_capture` (HQ workshop in BGame, end screens in BGame) - all as committed;
- and `review_cap` (scratch, untracked, deleted after): Campaign B seed 7 played by `tests/helpers/b_flow_driver.gd`
  through BGame like `b_capture`, shooting the first fight (rest, forecast hover, WORM held, cannot-stick, the COMMIT
  replay caught at step 8 of 17, win), every netrun layer of the first street (+ the pick-B hover), the map; then from
  the golden seed 2 the brief folded / unfolded (`look_skin().set_open`) and raid 2 (v42) with a weapon held.
- `review_cap2` (scratch, deleted after): TIME LOCK held in the same first fight; the PURGE plan (golden seed 2, raid 4)
  with the weapon that has the most legal slots (a SHOTGUN, 12) held and a slot hovered.
- `review_hires` (scratch, deleted after) only sets `Settings.resolution` to 1920 x 1080 for the quiet window (the
  user setting otherwise keeps it at 1280 x 720) and mounts the tool.
- Sheets: `D:/rc_scratch/review_cap/make_sheets.py` (PIL), captions in `D:/rc_scratch/review_cap/captions.json`.

## What to look at, per sheet (and known gaps)

**Fight**
- The skin is in (enamel, vinyl stickers, pencil, SEND IT, win ring); the panels are not: empty SCHEDULE, plain mono HUD,
  no backdrop, no wedge glyphs.
- Aim and refusal: the game loops every legal wedge, which buries the WORM picks and the cannot-stick slash.
- The COMMIT replay piles every step onto one or two wedges into an unreadable knot; HUD says "step - of 17".
- Gap: the single-target hold is TIME LOCK on your own NODE (its only legal wedge), not an attack like the plate's
  BREACH; the forecast hover is on a one-step turn, so it under-sells the numbered arrows.

**Raid**
- Work order folded / unfolded matches set 7 / set 8 closely; the briefing body, shop and CREW are still S8 text panels.
- v42 slots: the at-rest slot tiles are not drawn. Held in the PURGE: 12 slots lit as white X tiles, close to set 8's
  "the street lights up", but the dock radius is drawn round the whole district although it limits nothing (B-104 #3),
  and there are no refusal badges or forecast delta. (The road raid 2 hold in `captures/raid_x_v42_road_weapon_held_1slot.png`
  has only one legal slot.)
- Player text: the site refusal line still uses v40 wording ("not a socket ... street intersections within 3 cells"),
  and the PURGE refusal line leaks a lever name ("(lever slotShare)"); both run under the status strip.
- After-action: paper, CLASSIFIED and pencil are in; no HELD / OVERRUN result sticker, CREW line runs off the paper.

**HQ / end**
- There is no plate for the damage stages; the plate column is the round 42 room the art is cropped from. Check the
  stages at their real 160 x 72 (the lower small image): the tally carries stage 2, the cracks do not read.
- The workshop is still the S8 text screen with the art as a 160 x 72 header thumbnail.
- End memo: the D1 folder layout reads well won and lost; the plate is the Solace skin, the game the Meridian folder;
  heat graph and duration are not mapped yet; the "Claimed" fact is a 6-line list.

**Street**
- Biggest gap: the game's street does not look like the staged-run plates. The camera is further back and higher; the
  frontage is a thin strip with tall dark towers and an elevated highway arc over it, where the plates fill the frame
  with shopfronts.
- Rooms are placeholder rectangles; pick-B hover (pink edge + beam) is there but hairline at this scale.
- Last layer: L6 is the last netrun screen (L7 is the boss room, which is the fight), so the plate's L7 is paired with L6.
- The "city overview" row is not like for like: the game has no City-band zoom-out with the target highlighted; the
  closest screen is the Campaign B MAP (site grid over the 3D city), shown instead.
