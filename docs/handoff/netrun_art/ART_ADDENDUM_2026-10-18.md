# Art session addendum (from the build session, 2026-10-18)

Read after `docs/concepts/HANDOFF_PACKAGE/ART_SESSION_HANDOFF.md` (art-pass @ e81ab2ad). Paths below are in the build
repo `D:/Godot/rebel_cell` (read only for you, as before). Everything here is a **Batch API draft**: nothing was rendered
or run against the city namespace. Treat it as a head start, not as approved work.

## Drafts that map onto your post-reset queue (§4)
| Your queue item | Draft in `docs/handoff/netrun_art/batch/` | State |
|---|---|---|
| 1. Tethys decision and hover finals | `tethys_shots/SHOTS.md` | shot and state specs (camera, framing, states) matched to the other corps' finals |
| 2. Aurelian HQ design pass | `aurelian_design/DESIGN.md` | a DESIGN.md draft (D10: unique netrun, may exceed 7 layers); still needs the architect pass, thumbnails, test, finals |
| 3. Golden plates | `golden_plates/SPEC_SECTION.md` | a draft spec section incl. Python/GDScript parity (§12.6) |
| 4. Standalone landmark modules | `landmarks/<corp>_landmark.py` ×5 + `NOTES.md` | Halcyon, Solace, Orbital, Aurelian, Rebel Cell; `ast.parse` only. Halcyon and Aurelian `build_hq` are `NotImplementedError` stubs; Solace and Orbital `build_hq` ported. |

## Findings for you
- `spec_audit/contradictions.md` and `spec_audit/naming_and_open_numbers.md`. Three BLOCKERs:
  1. The spec lags the replan: §8.5 / §3.4 still describe Meridian's container fort (the Gatehouse Gantry is approved);
     §14.1 says there is no REST node (D4: REST, Workshop, Cache are in); D3 (procedural planner city) is not
     reflected in §3.4 Z1-Z3, L1, L4. Replacement text is in the audit.
  2. The data contract vs D8: three layout inputs (recorder `city_layout.json`, planner JSON, `city.json`); building id
     is `key` in §3.1 but `(ci, key)` in §3.2; the §12 checks need Cycles passes, so they cannot run on Godot captures.
     **Settle this with the build session before its NA-02 freezes the contract.**
  3. Central Server names (the designer is ruling them on the decision sheet, A1-A4).
- `vision_review/<corp>.md` + `SUMMARY.md` (frames downscaled to 1568 px; leads to measure, not verdicts): in 5 of 6 corps
  the landmark doesn't lead its surroundings, the window carpet is even with no quiet apron, district hue isn't
  carried by the fabric, hero signage is missing or unreadable; the hover power cut deviates from §9.4 in 5 corps
  (Orbital near black, a suspected double 3D + 2D cut); Meridian's crane / moat / viaduct absent; Rebel Cell's
  MAINFRAME sign and fist cropped, its DECISION camera 3/4 instead of the §6.4 side view. The review recommends running
  §12.1, §12.2 and §12.7 on all plates before tuning.
- `asset_coverage/MATRIX_A_F.md`, `MATRIX_G_M.md` (Haiku; spot-check the counts).

## Questions routed to you (decision sheet A5, A6)
- Halcyon pyramid: cyan-white or violet?
- Tethys: the spec §3.4 blue or the frames' teal?
The designer may answer these in your start prompt; the sheet is at
`docs/handoff/plan2/drafts/questions/DECISION_SHEET.md`.
