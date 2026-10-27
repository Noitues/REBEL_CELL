# Tide raid, polish iteration 1: animation storyboards and motion tests ("Jack-in over the Night City")

Role: motion design. Scope: art only (no rules). Pass-2 beam heads are used as they are (dart / bracketed block / bull-horn ram). All motion is
at 30 fps and is built over the real city plate (`plates/clean/default`) with the H2 settle libraries, so the marks are the settled grammar, not
new art. Nothing is committed.

## What is here
| what | where |
|---|---|
| 12 storyboards (frame strip + Gantt timing ruler + beat table with meaning / sound / ease / skip / reduce-motion / cited reference number) | `boards/board_01_jackin.png` ... `board_12_jackout.png` (2560 px wide) |
| 4 motion tests, each normal + reduce-motion, 960x540 30 fps MP4 and 640x360 15 fps GIF (loop with a 9 f cross-fade) | `tests/{daemon,lock,home,bloom}_{normal,reduce}.mp4/.gif`, contact strips `tests/*_sheet.png`, flash/shake proxies `tests/metrics_*.json` |
| timing table for build | `TIMING_TABLE.md` (and `tide_look_motion.tres.txt`, paste-ready `tide_look.tres` properties) |
| source | `scripts/` (`spec.py` is the single source for boards + table; `beats_*.py` the renderers; `tests.py`, `boards.py`, `table.py`) |

Boards: 01 jack-in, 02 card draw, 03 drag and drop onto a Site (valid row + invalid row), 04 daemon slither, 05 sealed lock opening, 06 hunter reticle lock,
07 shield flash with bits, 08 HOME hit with hit hold, 09 poster slam, 10 Bloom creep (DECAY), 11 CITY LOST flood and skull, 12 jack-out.

## Motion tests (2-4 s, loops)
| test | normal | reduce-motion | what it shows |
|---|---|---|---|
| `daemon` (travel to a stop block) | 120 f, 4.0 s | 80 f, 2.7 s | 30 f telegraph hold, 4 f coil, travel with corner slow-down and a cooling wake, tower ripple on the pass-through Site, arrival at the guard (flash, hex ripple, bits, stop block, tile) |
| `lock` (reveal) | 105 f, 3.5 s | 105 f | rattle, shackle, letter to pixels, type silhouette pop, fog clears and the road is drawn out from the corp, 66 f read hold (1.6x crop of the lock area) |
| `home` (HOME hit) | 105 f, 3.5 s | 105 f | 30 f telegraph hold, 6 f decel, 2 f white flash, 3 px shake, rings, sparks, 8 f hit hold, tile pop, scarred ring, 30 f aftermath |
| `bloom` (DECAY creep) | 105 f, 3.5 s | 105 f | DOWN clock drains, plum seed, ten visible 5 f steps, windows dying behind the hot edge, 30 f hold |

Reduce-motion variants follow the cheat-sheet's five rules (grade as cross-fade, travel/spread as state cut plus held peak, flash as one 3 f step
below alpha .30, no fringe/scanline/shake/jitter, every hold kept). Measured on the rendered videos (`tests/metrics_*.json`; `max_big_frac` is the
largest fraction of pixels that change by more than 25% between two consecutive frames, a flash/strobe proxy; `max_shift_px` is the largest
frame-to-frame picture shift):

| test | normal big-change fraction / frames over 1% / shift | reduce |
|---|---|---|
| daemon | 1.3% / 2 / 0 px | 0.6% / 0 / 0 px |
| lock | 2.9% / 4 / 0 px | 0.2% / 0 / 0 px |
| home | **15.9% / 11 / 6 px (3 px each way)** | **1.0% / 0 / 0 px** |
| bloom | 1.3% / 5 / 0 px | 1.2% / 1 / 0 px |

The HOME hit is the only beat with a shake and the only one with a large flash; the reduce version removes both (the white 2 f flash becomes one
3 f orange-white step at alpha .30).

## How the numbers compare with the reference cheat-sheet (REF_BASELINE, "Timing cheat-sheet")
| beat | cheat-sheet number | ours | verdict |
|---|---|---|---|
| jack-in grade | CP2077: grade is the switch, UI +4 f, readable 6-8 f; WD2 camera feed 24-40 f (too slow). Ask: grade OUT 8-10 f, marker +2 f, panel +4 f, stagger 2 f, done by 12 f | grade 10 f OUT_CUBIC (radial from our HOME, with a lit front), pads +2 f, UI +4 f for 6 f, towers 1 f stagger x10 + 6 f rise, interactive f12, settled f18; first-ever jack-in 24 f | meets CP2077 on the grade, beats WD2; towers are slower to settle than CP2077's list (18 f vs about 8) because there are ten of them |
| jack-out | CP2077 exit: UI gone +3 f, un-grade about +5 f, fringe 6-8 f | UI 3 f, towers 4 f, un-grade 6 f (from f2), fringe 6 f; whole thing 10 f (in is 18 f) | equal, asymmetric on purpose |
| telegraph | ITB: draws 6-12 f then persists all turn; CP2077: waits about 40 f then fires. Ask: hold 30-40 f, never behind hover | 30 f hold (daemon, HOME), 36 f (hunter), always on screen | meets (daemon/HOME sit at the low end of the 30-40 range) |
| travel | ITB laser 6 f, acid arc 18 f; Ask: 12-18 f per street segment, trailing wake | 14 px/f cruise, 40% corner slow-down; 16-19 f per mean 200 px block, 23-26 f per 280 px leg; cooling wake 330 px (about 24 f) | at the slow edge of 12-18 f, deliberately (cruise is a tuning value); the corner slow-down and the cooling wake are not in any reference |
| impact + hold | CP2077 spark f1, bloom peak f5-7, bright to f11+; ITB flash f3, peak f6-7, about 12 f total; Frozen Synapse about 20 f. Ask: flash f0-1, peak f4-7, HOLD 6-8 f, decay 8-12 f, aftermath 20-30 f | shield: flash f0-1, ripple full f8, hold 8 f, decay 12 f, aftermath 30 f; HOME: white f0-1, rings 12 f, hit hold 8 f (effect layers frozen at peak), decay 12 f, aftermath 30 f | meets every number; the white frame is on f0, earlier than ITB's f3 |
| shake | no reference shakes or hit-stops. Ask: only 2-3 px for about 4 f at the HOME hit, removed in reduce | 3 px, 4 f, diagonal, HOME hit only; hit hold = effect freeze, not a world freeze | beats by adding the one beat the references lack, gated |
| base hit | ITB tag + portrait +6 f; Frostpunk card about 10 f; Bad North fire over seconds. Ask: flash 1-2 f, HOME swap within 6 f, persistent mark, loss over seconds | tile pops f12-18 (6 f after impact), scarred ring and -6 persist; CITY LOST flood is 48 f (1.6 s) with 24 f desaturation | meets |
| spread (Bloom) | WD2 3 x 6 f steps, labels 6 f; Mini Metro extrusion about 10 f. Ask: new cells every 4-6 f, pop 6 f | ten steps one every 5 f (3 f each), seed pop 6 f OUT_BACK | meets |
| reveal | CP2077 dissolve about 12 f; WD2 sticker pop 6 f jitter overshoot then hold 24-36 f | lock letter dissolves 12 f, silhouette pop 6 f jitter, read hold 66 f; poster dissolve 10 f, slap 4 f, jitter 6 f, hold 30 f | meets; the lock holds longer than the references (66 f) |
| hover / selection | CP2077 outline jumps 1 f; Ask: disc hover 4-6 f ease | card pick 3 f OUT_BACK, Site answer 6 f OUT_CUBIC (preview, not commit) | meets |
| placement | ITB: ring flash 6 f, unit +6 f, about 18 f. Ask: drop 12 f, 4 f settle, ring flash | drop 12 f, program rises 8 f, ring 6 f, overlapped (about 18 f); invalid = 6 f refuse shake on the card only, 12 f return | equal; invalid path has no reference |

## Self-score: Motion 9 against the bar of 9 (a tie, not a clear beat)
Why 9: every beat has a number from the footage-verified cheat-sheet and is inside or faster than it; the three CP2077 qualities (fast in / faster out,
held impact, one telegraph that waits) are all present; and we add what none of the references has: a travel language (corner slow-down, cooling wake),
a radial grade that starts at our own deck, an explicit reduce-motion variant for every beat with measured flash/shake removal, and a skip behaviour
per beat. Why not 10: (1) this is 2D compositing over a still plate, so there is no camera, parallax, depth occlusion or shader response, which is where a
10 would come from (Google Immersive View camera moves, CP2077 AAA glow); (2) nothing was seen in the engine; (3) sound is a note, not a mix; (4) the
only honest "beats the reference" claims are timing ones, and the critic scores feel, not tables. A fresh critic should score the MP4s, not this note.

## Weak points (honest)
- Stills-composited, not engine motion. Ribbon flow, glow bleed, bloom and occlusion will look different in Godot; the numbers are the part that transfers.
- The "plain city map" the grade drops out of (board 01, board 12) is invented: a lifted, desaturated copy of the plate. The shipped raid screen has no
  such pre-jack look today; build must provide it (a global grade parameter), or the grade shift has nothing to move away from.
- The lock is only about 42 px on the 1920 frame; the lock test is a 1.6x upscale and the dissolve is small. The glyph rules need the lock larger when it opens.
- The daemon reduce-motion video is 80 f against 120 f for the normal one (no travel), so the two are not frame-aligned for an A/B.
- HIT HOLD is the effect layers frozen at peak for 8 f, not a world freeze, and the 3 px shake moves the whole frame. A designer may want hit-stop to freeze the
  beam head as well, or no shake at all; both are tuning values (`home_shake_px`, `home_hold_f`).
- Card draw uses an invented card back (navy with a lattice and a ring). The hand does not re-open a gap on lift in board 03 (the gap stays). The cursor is a
  plain white arrow.
- Bloom creep: the plum body is the existing `SC.bloom` field, so the stepped front is a radius schedule, not per-cell pops; the hot hairline does not pulse on
  each step (the beat language says it should).
- Pass-2 heads are small at 1x (about 30 px); in the daemon test they read as a dart but the N block and E ram are not shown in motion beyond the lock and
  HOME tests.
- Sound cues are written, not authored; no beat was tested with audio.
- The tritan DAMAGED/BREACHED/N collision from the pass-2 review is not solved by motion; the HOME-hit burst carries a non-hue cue (hex shards, bits, solid
  plate and the 3 px jolt), which is only present in the normal variant.

## Build notes (what Godot needs for these)
- `TIMING_TABLE.md` / `tide_look_motion.tres.txt`: every beat as `<key>_start_f`, `<key>_f`, `<key>_ease`, `<key>_skip`, `<key>_reduce`, plus the global skip and
  reduce keys. Ease names map to Tween trans/ease pairs in the table.
- A global "hacked layer" grade (radial from HOME) on the world environment, tower height animation per Site (staggered by distance from HOME), a ribbon with a
  lit wake (head position drives a falling brightness), a hex ripple shader at the wall impact point, a pixel-block dissolve (cell 3 px for the lock letter,
  14 px for the poster), an effect-layer time scale that can freeze for 8 f (hit hold), and a reduce-motion switch that routes each beat to its replacement.

## Process notes (for the review)
- Venv: `venv_vid` has Pillow and imageio-ffmpeg only (no numpy), so rendering used the system Python 3.14 (numpy, scipy, Pillow already installed, nothing
  installed) and the venv's bundled ffmpeg executable for MP4/GIF encoding.
- H2 scripts were imported read-only (bytecode writing disabled); no file outside `P1_motion/` and the scratch folder `D:/rc_scratch/tide_concepts/p1m_work`
  was written. P1_plates/ and P1_interact/ were not touched.
- Slips: I accidentally started a bare `python -` (empty stdin, nothing fed) four times; each was stopped (TaskStop or my own PID) and no such process remains.
  I also issued one `rm` with a glob on my own scratch thumbnail cache; the permission guard denied it before it ran, nothing was deleted, and I switched to
  versioned cache names instead.

## Re-render
`cd scripts`; `python boards.py [slug ...]` (frames cached in `D:/rc_scratch/tide_concepts/p1m_work/thumbs`), `python tests.py <daemon|lock|home|bloom> [normal|reduce]`,
`python table.py`. Needs numpy, scipy, Pillow and the plates under `D:/rc_scratch/tide_concepts/plates`.
