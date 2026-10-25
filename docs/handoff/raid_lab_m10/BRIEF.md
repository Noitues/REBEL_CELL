# Raid lab M10: playable Manhunt sweep raid (Godot prototype brief)

## Goal
A playable Godot 4.7 lab of the M10 Manhunt sweep raid. It is a design tool, so a critic can judge suspense and
readability **in motion**, with every number coming from one rules engine (mockups kept getting the ledger wrong).
Everything lives under `tools/raid_lab_m10/`. Never touch `scripts/`, `content/`, `scenes/` or the GDD. Model it on
`tools/raid_lab_h7/` (read its README and structure first; reuse its patterns, not its rules).

## Source of truth (python, read-only)
- `tools/raid_concepts/ghost2.py`: the sweep rules: `sweep()`, `value()`, `allocations()`, `SPOOFS`, scarce levers
  (`MAX_GHOST = MAX_DECOY = 1`).
- `tools/raid_concepts/ghost.py`: the network size and `network()`.
- `tools/raid_concepts/concept_m10_manhunt.py` and `concept_m9_base.py`: the intended frames and glyph language.
  Mockups: `docs/design/raid_concepts/m_manhunt_r10/r10/mockups/`.
- Golden: `tools/raid_lab_m10/data/m10_golden.json`, written by `tools/raid_concepts/m10_golden.py`. It holds 12
  networks × 4 plans × 3 candidates, each with no spoof and with every spoof: found lists and values.

## Rules to port (deterministic RefCounted GDScript, no randomness)
- A 4 × 3 network. Assets have values.
- **Beam 1:** a known line.
- **Beam 2:** one of 3 sealed candidate lines. The reveal is the case's candidate index, chosen in the lab's leg
  setup, never random.
- **Beam 3, the hunter:** it scans the column of the first thing found in beams 1 and 2 (a decoy counts); otherwise
  its own line.
- **Beams stop at a decoy.** Hidden nodes (ghost or dark) are skipped.
- **One spoof:** a beam skips one node.
- **Value** is as in `ghost2.value()`.
- **Parity:** `parity_check.gd` (headless) must reproduce every found list and value in the golden. Exit non-zero on
  any mismatch.

## Designer decisions pending: build both behind a toggle in a lab config (`.tres` or a const dictionary in the lab)
1. **SPOOF_MODE.** `"choice"` is the default: after the reveal, playout pauses and the player clicks the node the
   revealed beam skips. `"press"`: a timing window as the beam crosses the chosen node; SPACE lands it.
   - Reason: GDD pillar 4 versus a timed press.
2. **REPAIR.** `"value"` is the default: repair = asset value. `"half"`: repair = value // 2 (GDD 3.3).
   - Only the displayed ledger changes. Parity stays on `"value"`.
3. **KEY_LABEL.** The key bar's unit (Schematics by default). It is a label only.

## Screens (1280×720, text 1.0, mouse and keyboard)
1. **Contact.**
   - Heat meter with the cobalt threshold notch; a drawn cause chain (run nodes → Heat → notch → contact).
   - The network with the haul.
2. **Plan.**
   - Place 1 ghost (+5 Heat, charged immediately on the Heat meter), 1 decoy (−3 off the key, charged immediately),
     and go dark (marks the node's next income lost).
   - Undo is allowed.
   - Beams drawn: beam 1 solid; the sealed candidates as dashed lines told apart by end shape (triangle, square,
     diamond); the hunter's turn drawn live on the grid as soon as the plan creates a first find.
   - Beam order numbers 1, 2, 3 on the beams only.
3. **Forecast, on the grid itself.** Invisible, Inc. guard vision: no side table.
   - Each candidate's found nodes are marked on the grid with that candidate's shape.
   - The key bar shows the loss range as a bracket (min..max over the candidates).
   - No computed best plan, and no "recommended" anything.
4. **Playout (hands-off).**
   - Beat by beat: beam 1, then beam 2 unseals (the chosen line lights, the others fade), then the spoof decision
     (choice or press), then beam 2 resolves, then the hunter turns and sweeps.
   - Each node a beam touches pulses; found = red, near miss on a hidden node = ring.
   - Speed controls 1x / 2x / 4x / SKIP. All three beams visibly play.
5. **Aftermath.**
   - Stamp: CELL HOLDS with "N DOWN", or EVADED.
   - DOWN nodes get a wrench and stay marked.
   - One ledger in one currency: key before → ghost/decoy costs → repair → after, plus Heat before → after. EVADED
     shows its own +6 and Heat −10.

The lab runs a **leg of 3 raids** on golden networks 22, 17 and 25. Each raid uses that case's reveal = candidate 0.

## Checks
- **`parity_check.gd` (headless):** all golden cases.
- **`flow_check.gd` (headless):** a scripted play of the leg in both SPOOF_MODEs. The forecast must equal the real
  result for the revealed candidate, and the ledger must reconcile on every screen.

## Captures
- One PNG per screen and per playout beat, for raid 1 (network 22) in both modes.
- Plus a scrambled set, with every UI letter replaced (`--scramble`).
- Write them to `D:/rc_tmp/raid_design_lab/lab_m10/shots/` (and `shots_choice/`, `shots_press/`, `shots_scrambled/`).
- Windowed runs only via `python tools/run_windowed.py --log <file> -- <args>`.
- Review your own captures for overlaps and clipped text.
