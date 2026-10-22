# M10 Manhunt sweep-raid lab

A playable Godot prototype of the M10 sweep raid (design lab round 10), so a critic can judge suspense and readability
in motion with every number coming from one rules engine. A design tool, not part of the game: nothing outside
`tools/raid_lab_m10/` is touched. Brief: `docs/handoff/raid_lab_m10/BRIEF.md`. Structure follows `tools/raid_lab_h7/`.

## Run it

- Play: open `res://tools/raid_lab_m10/raid_lab_m10.tscn` and run the scene (1280x720, text 1.0, mouse and keyboard).
  Windowed runs from a script go through `python tools/run_windowed.py` only.
- Parity check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd`
- Flow check (headless, rules, a full play of the leg in both SPOOF_MODEs and both REPAIR modes, and the scene driven
  through its own input path): `-s res://tools/raid_lab_m10/flow_check.gd`
- Captures: `python tools/run_windowed.py --log <log> -- --resolution 1280x720 res://tools/raid_lab_m10/raid_lab_m10.tscn -- --shots=<abs dir> [--spoof=choice|press] [--repair=value|half] [--key=<label>] [--scramble]`
  auto-plays raid 1 (network 22) and saves a PNG per screen and per playout beat, then plays raids 2 and 3 for the
  contact screens and the leg record. `--scramble` replaces every UI letter (digits and glyphs stay): the no-words test.
  Output of the delivered run: `D:/rc_tmp/raid_design_lab/lab_m10/shots_choice/`, `shots_press/`, `shots_scrambled/`.

## How to play

The leg is 3 raids on golden networks 22, 17 and 25. Each raid's reveal is candidate 0 (set in `M10Config.LEG_REVEAL`,
never random). Key and Heat carry from raid to raid.

1. **Contact.** Heat meter with the cobalt notch (50), the key bar, the network with its haul, and the cause drawn as a
   chain: run nodes, Heat, notch, contact. Raids 2 and 3 also show what the run since the last raid added. Enter.
2. **Plan.** Levers (keys 1 2 3, then click a node; click a placed lever or press Z to take it off):
   - GHOST (1 per raid): dashed ring on an asset node, +5 Heat charged on the meter at once.
   - DECOY (1 per raid): diamond on an empty node, -3 off the key at once. A beam stops on it and counts it as a find.
   - GO DARK (up to 3): black disc on an asset node; that node's next income (v // 2 + 1) is lost.
   - SPOOF x1 is held for after the reveal.
   The grid shows beam 1 (solid, badge 1), the three sealed beam-2 candidates (dashed, told apart by end shape and dash:
   triangle, square, diamond, badge 2) and the hunter's column (badge 3) drawn live as soon as the plan makes a first find
   (from beam 1 if it finds, else one thin column per candidate that finds something).
3. **Forecast** (Enter again), on the grid itself: a small shape on a node means "found if that sealed line is the real
   beam 2", the key bar gets a bracket with the loss range min..max over the candidates, a teal check marks a line that
   finds nothing (EVADE +6). No side table, no best plan. B edits the plan, Enter launches.
4. **Playout**, hands-off: beam 1, beam 2 unseals (lit; the others fade), the spoof decision, beam 2, the hunter turns,
   beam 3. Each touched node pulses (found red, hidden near miss white ring, decoy yellow, spoofed teal). Speed 1x / 2x / 4x
   (keys 1 2 4), SKIP (S) runs on but stops at the spoof decision.
   - SPOOF_MODE `choice` (default): the playout pauses; click a node on the lit beam-2 line and the beam skips it, or hold the spoof (H).
   - SPOOF_MODE `press`: click the target, then SPACE as the ring converges on the node. The ring is exact at 0.7 s,
     the hit window is +-0.22 s (`M10Config`), the window runs in real time at any speed; a miss or SKIP leaves the node found.
5. **Aftermath.** CELL HOLDS with N DOWN, or EVADED. DOWN nodes get a wrench and stay marked. One ledger in the key's
   currency (before, decoy, repair, optional evade, after) and one for Heat (before, ghost, evade -10, after), and the
   dark nodes' lost income on its own line (it comes off the next run's key gain, not this ledger).
6. **Leg record** after raid 3.

Toggles (strip at the bottom, or F1 F2 F3): SPOOF_MODE (choice / press), REPAIR (value / half), KEY_LABEL (Schematics, Scrap, Credits; label only).

## What is ported

Source of truth is `tools/raid_concepts/` (python). All deterministic `RefCounted` GDScript, no randomness:

| GDScript | Python |
| --- | --- |
| `m10_rules.gd` (`M10Rules.sweep`, `value`, `forecast`, `loss_range`) | `ghost2.py` `sweep()` (beam 1, beam 2, hunter on the first find or decoy, stop at a decoy, hidden nodes skipped, one spoof skips a node), `value()` (found values, decoy cost, dark cost v // 2 + 1, +6 evade, Heat at 0.4 x 5 per ghost); scarce levers `MAX_GHOST = MAX_DECOY = 1` |
| `m10_rules.gd` (`ledger`) | not in python; the aftermath ledger of the concept (key, Heat, EVADED +6 and Heat -10), written for the lab |
| `m10_config.gd` | the numbers of `ghost2.py` / `ghost.py` (checked against the golden `config`) and the toggles |
| `m10_data.gd` | loads `data/m10_golden.json` (written by `tools/raid_concepts/m10_golden.py`) |
| `m10_model.gd`, `m10_play.gd` | lab state (plan, undo, leg) and the playout state machine; they only call the rules |

The view is `raid_lab_m10.gd` (placeholder `_draw()` visuals, glyphs and the scramble in `m10_glyphs.gd`).

## Parity status: PASS

`parity_check.gd` replays every case of the golden (12 networks x 4 plans x 3 candidates, each with no spoof and with all
36 spoofs = 5328 sweeps), compares the found list and the value of each, plus the config constants, plus that the
REPAIR `half` toggle changes only the ledger's repair and never `value()`.
Result: 5328 sweeps, 10812 checks, 0 failed, `PARITY PASS`, exit 0. Log: `D:/rc_tmp/raid_design_lab/lab_m10/parity.log`.
`flow_check.gd`: PASS (225 checks: lever caps and costs, undo, loss range, the leg in choice and press mode with value and
half repair, forecast = real result, ledger reconciles on every raid, the scene's flow in both modes).

## Findings and known gaps

- A sweep whose only contact is a decoy counts as EVADED (+6, Heat -10) in the rules, because the decoy is not an asset
  found. The decoy's cost still stands. Worth a designer decision (a decoy hit reads as a contact on screen).
- The spoof in the lab acts on beam 2 only (the decision comes after the reveal and before beam 2 resolves). The golden and
  `M10Rules.sweep` accept a spoof on any beam; parity covers all three. If the hunter should be spoofable too, the
  decision needs a second pause.
- The key cannot go below 0: unpayable repair is a visible "UNPAID" row so the ledger still reconciles (network 22 with no
  plan loses 26 against a key of 19). Heat has no such cap issue in the leg (peaks around 91 of 100).
- Between raids the lab invents a run: +12 Heat, +12 key (less the dark nodes' lost income), so each contact has a cause
  (`M10Config.RUN_HEAT`, `RUN_KEY`). Not from the GDD or the concepts. EVADED's Heat -10 is applied on top of the ghost's +5.
- A spoof aimed beyond a decoy on the line is moot (the beam never gets there); in press mode no window opens.
- Press mode: SKIP counts as a miss. Window and timing are `M10Config` numbers, untuned.
- The dashed hunter columns of the plan view assume the revealed candidate could be any of the three; once a plan makes
  beam 1 find something, only the single real hunter column is drawn.
- Placeholder vector visuals, no animation polish beyond the pulses and beam heads, no sound, no save, no text scale or
  gamepad (out of scope).
