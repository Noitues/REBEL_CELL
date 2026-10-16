# HQ netrun: REBEL_CELL / DISPATCH, "Sync Strike" (2026-10-15, option A)

The DISPATCH finale in the approved route-map look (AAA-2 r3) with the designer's HQ lighting rule. Revised the same
day after the designer's review: **no landmark tower** (the first version's DISPATCH stack is archived in
`D:\rc_scratch\hq_rebel_cell\v1_core\`); the district is the bible's normal street grid with the fist drawn in red
windows; the red is **subtle until the blackout** and then spreads through the fist; three concept options were
proposed for Sync Strike and the designer picked **option A: three stacked lanes in one side-view section**. Only A is
rendered (option C's graph and build stay in `scripts/` as `hq_graph_C.py` / `hq_build_C.py`, unused; B was never
built). Nothing is committed; Cycles HIP in the shared GPU queue; Eevee for layout previews.

## Files

| File | What it is |
|---|---|
| `H_overview.png` | Option A, the whole section: the rooftop lane (BREAKER), the street lane (GHOST), the service tunnel (RIGGER) under the street, all three mid-run; the kill-switch column, the service shaft, DISPATCH (TARGET) in the palm row's building. |
| `H_decision.png` | Mid-run (step 2): the two roof / tunnel detours chosen to wait for the GHOST's COUNTERED stall; the SYNC dial: all three at their switches on step 5. |
| `H_hover.png` | The same, hovering BREAKER's detour: the power cut, the lane's branch, the rule note. |
| `H_switch.png` | The kill-switch moment: all three switches THROWN on the same step; the fist's lines pulse red. |
| `H_showdown.png` | The convergence: two operatives PARKED at their switches (support), the third takes the shaft into DISPATCH. |
| `H_red_1_before.png` .. `H_red_4_full.png` | The red sequence from above (no UI): an ordinary district (the fist barely hinted), the BLACKOUT (the ring and the hand's lines go dark), the red SPREADING from the palm, the FULL fist. |
| `H_mechanic_states.png` | The sheet: the red sequence, the three option A frames, the rules (real vs proposal), the GDD questions. |
| `H_reveal.mp4` / `.gif` | 6.5 s HQ beat = the red sequence in motion (the round 34 blackout reveal, then the spread). |
| `plates/`, `scripts/` | Plates without UI; everything to rebuild. |

## 1. The district and the section (`scripts/rc_district.py`, `hq_graph_A.py`, `hq_build_A.py`)

| Element | Rule |
|---|---|
| District | A 12 BU block grid (9 BU blocks, 3 BU streets) over the fist's box plus a margin; one continuous city (the hq_kit ring beyond). Each block is classified from the round 15 fist glyph (`fist_mask.py`, cropped, 5 samples per block): FIST, a fist LINE (finger splits, thumb edge, cuff: windowless after the blackout), the blackout RING (round 34), or plain. |
| Windows | One shader for every block, two values per frame: `SEQ` (0 before: ~8 % of the fist's lit windows red and dim; 0-1 the sector washes out, then the ring and the lines go dark; 1-2 the red spreads from the palm, a front `spread_r` x (SEQ - 1); 2-3 full: 85 % red at full strength; the fist's roof skylights join in, so the fist reads from above) and `PULSE` (the kill switch: the LINE blocks glow red). The red stays a lit-window effect. Netrun frames use SEQ 2 (the fist lit, not at full blaze). |
| The section (option A) | Derived from the real grid (the designer: future netruns from real map lots, one continuous city): the cut is a street line of the block grid (`stack.cut`) just south of DISPATCH's row at the palm; blocks south of it and the ground in front of it are removed (a dollhouse); the first row behind it hosts the lanes: its blocks under the lane rooms become LANE BUILDINGS (ground floor = the street rooms, roof = the rooftop rooms; their windows still follow the fist sequence). The EARTH under the street is cut open: the service TUNNEL (third lane) and a deeper level for its detour. |
| Lanes | L BREAKER on the roofs (detour: over raised roof huts), C GHOST at street level (DISPATCH counters C2: STALL +1), R RIGGER in the tunnel (detour: the deeper level). 3 rooms + a KILL SWITCH each; the switches in one column; the SERVICE SHAFT beside it joins the three levels to DISPATCH's server floor. |
| How it generalises | A section = (a street line of the grid, a run of lots along it, the target lot). Any district can host the same three lanes: the roofs and ground floors of the lots along the line, the utility corridor under the street. |

## 2. Preset variant
r3 look; `PRESET["hq"]`: Cell red #E8141E for the windows, DISPATCH red for the switches / the shaft, per-operative
accents (pink BREAKER, cyan GHOST, green RIGGER: token frames and a thin edge line beside their wax only; the route keeps
lime / orange / white / grey), the window sequence numbers (`win_k`, `red_before_p`, `red_k`, `red_full_p`, `wash_k`,
`spread_r`, `pulse_k`), the section (`stack`). `HQ_VARIANT` (A | C) and `HQ_DISTRICT_ONLY` pick the build.

## 3. The mechanic: GDD vs proposal

| What | Source | Status |
|---|---|---|
| REBEL_CELL = the final unlock campaign built from your profile; elites use your wheels (M11: mirror elites x1.5, one pointer, your Daemons); the final boss is DISPATCH | GDD 8.5, M11, 8.2 | **Real.** Every elite wears MIRROR. |
| The district: a normal grid, the fist in red windows (90 % for DISPATCH), the blackout reveal | Bible 4.4, round 34 | Art direction, kept; the slow spread after the blackout is the review's. |
| SYNC STRIKE: three operatives, three kill switches thrown on the same step, a lone throw re-arms, DISPATCH counters a lane, ONE enters the showdown | Round 43 decision + the review | **Proposal** (not in the GDD). |
| STALL +1 on a countered room; detours (+1) to stay in step; the parked two as support | This round | **Proposal**. |

### GDD questions (for DECISIONS.md)
1. **Turn order**: do all three choose at once each step (as drawn: one step = three moves), or does the turn rotate between operatives?
2. **HP / RAM**: shared between the three, or each operative its own (the stationed crew)?
3. **One operative dies** before the switches: does the strike fail (retreat), or can the other two finish with a lone-throw penalty?
4. **The parked two in the showdown**: what support (a passive buff per class, a card each, absorbing DISPATCH's counter-attacks)?
5. **Mirror combats** (round 43 / M11): every elite (as drawn) or one per lane?
6. **Decks**: one deck or one per operative (round 43 open question; proposal: one per operative)?
7. **The countered room**: chosen from the player's most-used firmware (GDD 8.5 "built from your profile")?

## 4. Camera beats
| Beat | Rule |
|---|---|
| DECISION | The side view (the V3 dollhouse): straight at the section (yaw 0), nearly level (pitch 5-8), framing the three operatives and their options; each step it slides east along the street with them. |
| OVERVIEW | The whole section (pitch 7). |
| REVEAL | The red sequence from above (whole district), then the camera settles lower. |

## 5. Godot 4.7 mapping
| Element | Godot | Perf |
|---|---|---|
| District | One MultiMesh of blocks with per-instance category + height; the window shader reads the category and two global uniforms (`seq`, `pulse`). | 1 draw. |
| Section | A clip plane (or simply not spawning the lots south of the cut) + an earth mesh with the tunnel cavities; the lane buildings as scenes on their lots. | Small. |
| Lanes, tokens | Room scenes, 3 tokens with accent frames, the shaft as a scene. | ~17 rooms. |

## 6. Value checks and render log

| Still (2560 x 1440, 64 spp) | median | < 0.10 | > 0.85 | landmark / local background |
|---|---|---|---|---|
| H_overview (the section) | 0.157 | 22 % | 1.5 % | 0.171 / 0.116 = 1.48 |
| H_decision | 0.092 | 54 % | 1.1 % | 0.106 / 0.073 = 1.46 |
| H_red_1_before (from above) | 0.010 | 87 % | 0.1 % | 2.2 |
| H_red_4_full | 0.013 | 80 % | 0.1 % | 3.6 |

The section frames meet the landmark rule (~1.5x). The red sequence frames are far too dark overall (median ~0.01):
the overhead view looks down through the fog onto window-lit blocks with no street light; the fist reads, the frame
does not meet the r3 median. Fix for a next pass (light, not exposure): street lamps on the grid's streets and a
brighter `win_k` for the plain windows in the before / blackout beats.
Render log (one locked batch with Orbital's reveal): stills 201 s, the 3 option frames 211 s, the 4 red frames 252 s,
the reveal 156 frames in 696 s; compose 97 + 91 + 100 + 125 s, encode 13 s.

## 7. Gaps for the tools step
- The lane rooms' x positions and roof heights are preset numbers along the cut line (the cut and the lots are from the grid).
- The countered room is a preset id.
- The fist's box is a preset; the ring radius is a preset.

## 8. Open questions for the designer
See the GDD questions above; plus: does the netrun show the fist at full blaze (SEQ 3) or lit (SEQ 2, as drawn)?
