# Sweep-raid lab, round 2 (L2)

A playable Godot prototype of the round-2 sweep raid, so a critic can judge suspense and readability in motion with every
number coming from one rules engine. A design tool, not part of the game: nothing outside `tools/raid_lab_m10/` is touched.
Brief: `docs/handoff/raid_lab_l2/BRIEF.md`. Rules source of truth: `tools/raid_concepts/sweep_l2.py` (python).
The folder name `raid_lab_m10` and the scene `raid_lab_m10.tscn` are kept as the entry point.

**Round 1 (M10) was replaced, not kept behind a `RULESET` constant.** The key, the press-timing spoof and the per-raid
networks are gone, and keeping both rule sets in one view would have cost more than the rewrite. The M10 code and golden
live in git history (commit ba2aa5e6 and earlier on this branch's base).

## Run it

- Play: open `res://tools/raid_lab_m10/raid_lab_m10.tscn` and run the scene (1280x720, text 1.0, mouse and keyboard).
  Windowed runs from a script go through `python tools/run_windowed.py` only.
- Parity check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd`
- Flow check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd`
- Captures: `python tools/run_windowed.py --log <log> -- --resolution 1280x720 res://tools/raid_lab_m10/raid_lab_m10.tscn -- --shots=<abs dir> [--leg=0|3|5|8|11|14] [--line=planned|greedy|naive] [--lite] [--scramble] [--spoofview=on|off] [--key=<label>]`
  plays the whole leg of 3 raids through the lab's own input path (each raid really played: levers, forecast, sweep with
  the spoof decision, aftermath, repair step) following a golden line, saving a PNG per screen and per playout beat.
  `--lite` takes fewer frames, `--scramble` replaces every UI letter (digits and glyphs stay): the no-words test.
  Delivered runs (in `D:/rc_tmp/raid_design_lab/lab_l2/`): `shots/` (leg 0, planned line, 44 frames),
  `shots_breach/` (leg 0, naive line, breaches in raid 3, 44 frames), `shots_scrambled/` (leg 5, planned, lite, 23 frames).

## Rules (as built, from `sweep_l2.py`)

- ONE network for the whole leg of 3 raids: 4 x 3 grid, 6 assets (value v) plus the HOME server (integrity 3).
- Asset status: OK, DOWN, TAKEN. A find on an OK asset makes it DOWN (no income; repair = v // 2 between raids); a find on a
  DOWN asset makes it TAKEN (lost for the leg; beams pass through TAKEN cells). A find on HOME costs 1 integrity; at 0 the
  campaign is lost: BREACHED, a full-screen end.
- Heat sets the raid's strength: beam 1, the sealed beam 2 (3 shaped candidates) and the hunter always run; Heat >= 50 adds a
  known beam, Heat >= 75 a second one, both scanned after beam 1. The Heat the sweep runs at includes the ghost's +5.
- Levers: 1 ghost (+5 Heat at placement; may hide HOME), 1 decoy (-3 Schematics), go dark on at most 1 asset (no income from
  it this interval). Between raids: repair DOWN assets (v // 2 each, paid from the bank, in click order).
- Spoof: a choice after the reveal; beam 2 skips one node (any node of the lit line, or hold).
- Hunter: turns down the column of the first touch (a find or a decoy), else its own line.
- EVADED: nothing touched at all (a decoy counts as a touch): Heat -10. Otherwise Heat is unchanged.
- Between raids: Heat +12; income = sum(v // 3) over OK, non-dark assets (after the repairs).
- No key. One ledger: Schematics (bank), Heat, home integrity, asset status. Leg score = bank + sum(v) of assets not TAKEN
  (a DOWN asset less its repair) - 8 per integrity lost; BREACHED = -100.

## How to play

The leg is golden leg 0 (`--leg=N` for 3, 5, 8, 11, 14). The revealed sealed line is candidate 0 (the corp's real pick in the
python), never random.

1. **Contact.** The raid's strength drawn by Heat band: three rows (under 50, 50 and up, 75 and up) with the beams each brings
   (1 known beam, `+` and `++` extra known beams, `?` the sealed beam, 3 the hunter), the current band lit, a Heat -> line 50 ->
   line 75 -> beams chain, the network's status counts, and what the run between raids added. The grid shows beam 1 and the
   extras that come.
2. **Plan.** Levers (keys 1 2 3, then click a node; click a placed lever or Z to take it off). The grid shows the known beams
   live (the ghost's +5 Heat can push the raid over a line and add a beam: the "This raid's beams" panel says so), the 3 sealed
   candidates (dashed, told apart by end shape: triangle, square, circle; badge `?`) and the hunter's columns.
3. **Forecast** (Enter). Per candidate, each node it touches carries a slot: the candidate's shape and the outcome it would
   suffer (white bolt on grey = DOWN, cobalt corp marker = TAKEN, `-1` = HOME). The forecast **includes the held spoof**: the
   panel lists each line "hold -> best spoof" (with chips x DOWN, x TAKEN, HOME -1), a teal mark on the grid shows the node
   that line's best spoof would skip, and the HOME pips show the projected loss (hatched), the pips the spoof saves (teal ring)
   and the worst case with and without the spoof. B edits the plan, Enter launches.
4. **Playout**, hands-off: beam 1, the known extras, beam 2 unseals, the spoof decision (the panel lists "hold" and each node of
   the lit line with the result if skipped; click a node or hold with H), beam 2, the hunter turns, the hunter beam. Statuses
   change on the map as each beam touches (pulses: DOWN white, TAKEN cobalt, HOME red, decoy yellow, hidden near miss white
   ring, spoofed teal). Speed 1x/2x/4x (keys 1 2 4), SKIP (S) runs on but stops at the spoof decision.
5. **Aftermath.** CELL HOLDS or EVADED; status changes stamped on the nodes (DOWN, TAKEN, HOME -1); the ledger (bank: before,
   decoy, after; Heat: before, ghost, evaded, after; HOME pips). If HOME reaches 0 the playout ends in the full-screen
   BREACHED / CAMPAIGN LOST screen instead (leg score -100).
6. **Between raids.** The same network, DOWN assets clickable: each shows its repair cost, picked repairs show as OK, the
   ledger (bank: after the raid, repair, income, next raid; Heat: after the raid, +12, next raid and the beams it brings). Dark
   assets show "dark: +0".
7. **Leg record.** Raid by raid: Heat before -> after and the beams the sweep ran with, a mini map of the network after the raid
   (touched nodes outlined), status changes, bank, HOME pips, levers, between-step repairs and income, the next raid's Heat band,
   and the score line.

Visual vocabulary: the diamond means only the decoy (candidate shapes are triangle, square, circle); DOWN is the GDD mark (white bolt on a greyed
node); TAKEN is a cobalt corp marker; threats and beams stay cobalt. A legend row sits under the grid.

Toggles (strip at the bottom, or F1 F2): SPOOF IN FORECAST (on: the forecast shows the best spoof, marks and range; off: the
forecast ignores the held spoof, to judge whether the information matters), CURRENCY label (Schematics, Scrap, Credits; label only).

## What is ported

| GDScript | Python (`tools/raid_concepts/sweep_l2.py`) |
| --- | --- |
| `l2_rules.gd` (`L2Rules.sweep`, `resolve`, `between`, `score`, `best_spoof`, `why_not`, `naive_decide`) | `sweep`, `resolve`, `between`, `score`, `raid_options` (best spoof), the caps of `allocations`, `naive_leg` |
| `l2_state.gd` | `State` |
| `l2_config.gd` | the constants at the top of `sweep_l2.py`, checked against the golden `config` |
| `l2_data.gd` | loads `data/l2_golden.json` and `data/l2_extra.json` |
| `l2_model.gd`, `l2_play.gd` | lab state (plan, undo, leg, forecast, repair step) and the playout state machine; they only call the rules |

The view is `raid_lab_m10.gd` (placeholder `_draw()` visuals; glyphs and the scramble in `l2_glyphs.gd`). Deterministic
`RefCounted` rules, no randomness anywhere in the lab.

`data/gen_l2_extra.py` (run from the repo root) writes `data/l2_extra.json`: the golden does not carry each raid's second extra
beam (`extra2`, needed from Heat 75), the constant `EXTRA_AT = 50`, nor the naive line. It imports `sweep_l2.py` and
`l2_golden.py` read-only.

## Parity status: PASS

`parity_check.gd`: the config constants; every step of the planned, greedy and naive line of the 6 golden legs (18 lines, 54
steps: state before, touches, state after the raid, between step, state after, score); all 200 random single-raid resolutions
(touches, status, Heat, bank, home integrity, score); every golden allocation passes the lab's lever validation.
Result: 1171 checks, 0 failed, `PARITY PASS`, exit 0 (non-zero on any mismatch). Log: `D:/rc_tmp/raid_design_lab/lab_l2/parity.log`.
`flow_check.gd`: PASS (160 checks: lever caps and costs, undo, the heat bands and the ghost pushing a raid over a line, golden
leg 0 on its planned line through the model with the forecast for the revealed line and the chosen spoof equal to the result,
touches logged beat by beat, the ledger and the between ledger reconcile, naive line on all 6 legs ending as the golden
(breach on legs 0, 5, 8: score -100, no between step), the scene driven through its own input path for a planned raid with the
repair step and a full naive breach leg to the record).

## Findings (rules ambiguities) and known gaps

- The golden does not export `extra2` or `EXTRA_AT` (see above); without them nothing at Heat >= 75 could be checked. Worth adding
  to `l2_golden.py` so the lab need not carry a supplement.
- A decoy is a touch: a sweep whose only contact is a decoy is NOT evaded (no Heat -10) but costs nothing but the decoy's 3. Python
  repeats the decoy touch once per beam that reaches it; the lab dedupes it on screen (the rules list keeps every touch).
- The hunter's first touch can be a decoy: it then turns down the decoy's column. A touch on a hidden (ghost / dark) cell does not
  count, so the hunter takes its own line when everything is hidden.
- The best spoof of `raid_options` maximises (score after the raid, fewest touches) and ties keep "no spoof" (strict
  improvement), so the forecast says "no spoof helps" on lines where skipping changes nothing. The score ignores the later repair
  and income, so a spoof that saves a DOWN asset the bank could repair anyway is still "best".
- The spoof acts on beam 2 only (the python too); the extra known beams and the hunter cannot be spoofed.
- Heat is never capped (python has no cap); the meter is drawn to 100 and the number can exceed it. EVADED subtracts 10 from the
  Heat the sweep ran at, so it can go below 0 with a low Heat (not reachable in the golden legs).
- The bank cannot pay for a repair it lacks the Schematics for: the click is refused with the cost shown (the python `between`
  silently skips it, same result). Repairs are applied in click order, as the python applies them in the given order.
- Dark assets earn nothing in the interval right after the raid they were set for, and are hidden from every beam like a
  ghosted one (so a dark asset cannot be found). The income it forgoes is v // 3.
- Candidate end shapes are triangle, square and circle (the diamond is reserved for the decoy, per the brief).
- Contact uses golden leg 0 by default; the networks' beams drawn as straight lines with perpendicular offsets where lines
  coincide, badges nudged apart; very dense raids (3 known beams) still overlap in places.
- Placeholder vector visuals, no animation polish beyond pulses and beam heads, no sound, no save, no text scale or gamepad
  (out of scope).
