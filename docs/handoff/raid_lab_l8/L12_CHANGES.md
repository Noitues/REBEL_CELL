# L11 → L12: presentation polish only (no rule changes; l8_rules.gd, sweep_l8.py and the golden stay as they are)

From the L11 batch critic.

1. **Honest, causal between-raid verdicts** (main scene). Everything is computed from existing `L8Rules` calls
   (`safe_next`, `between`, `decay`, `capture_options`). This adds no rule.
   - Each intensity card's badge reads **"HOLDABLE: a plan exists"** (shield) or **"LOST: no plan holds HOME"**
     (skull). The word "SAFE" is gone.
   - **Each repair and build option** shows its own badge, from `safe_next` with that option at the selected intensity.
   - When skipping an option, or picking another, turns a holdable next raid into a lost one, show a red-bordered
     requirement line naming it. For example: "Repair MID 0, or raid 3 cannot be held". Or: "Build N, or raid 2
     cannot be held".
2. **Launch friction** (main scene). If the FORECAST for the current placement shows HOME breached on every sealed
   route, LAUNCH needs a second Enter or click, and shows: "Every route breaks HOME with this plan: change it?".
   - If `safe_next` says some plan holds (re-checked for this raid from the post-capture state), the panel names one
     fix: the first placement, in the rules' enumeration order, that holds HOME on every candidate.
3. **Verdicts on the board** (board and main scene).
   - `L8Board.show_route_verdicts(v: Array)`, with one entry per candidate route: `{route: int, tier: String}`.
   - Each entry stamps the tier glyph where that route meets HOME: a heart (HOLDS / EVADED), a broken heart
     (BATTERED / DAMAGED) or a skull (BREACHED).
   - It is called in FORECAST and hidden at launch.
4. **District marks** (board).
   - A DOWN district shows a "TAKEN next raid" countdown mark: a cobalt "1" in a ring next to the wrench.
   - A district hit this raid but still OK (a BATTERED contributor) shows a crack decal until the next raid.
   - API: `show_state` reads the existing status; the countdown appears on every DOWN district (decay is certain).
5. **Thin the plan lines.**
   - Unselected candidates: 15% alpha, with no arrowheads.
   - Known beams: a solid lane at full strength.
   - Selected candidate: full strength, with a pulse.
   - Hide gray block decals on roads that no line uses.
6. **Starfield and frame.** The board takes more of the frame: cut the dark sky margin and dim the starfield behind
   the board. Keep the camera fit to the free area.
