class_name L7Config
extends RefCounted
## Every timing of the raid's motion in one place (seconds at 1x; the 1x / 2x / 4x toggle scales the whole raid layer, and
## the instant toggle skips the pacing: the same events, the same end state, no waiting). Presentation only: no rule reads
## these, the resolver's events decide what happens and in which order (STYLE_GUIDE 5.3: raids play from the resolver's
## events and are never recomputed).

## The speed toggle (keys 1 2 4, the buttons on the sweep panel).
const SPEEDS: Array = [1.0, 2.0, 4.0]

# ---- 1 launch: the beams sweep cell by cell along their fixed lanes ----
## A beam glows at its pylon this long before its head moves.
const BEAM_LEAD: float = 0.3
## One cell of travel.
const STEP_T: float = 0.32
## A beam holds this long after its last cell before the next one starts.
const BEAM_TAIL: float = 0.35
## A touched cell flashes this long (a hex ring on the floor and the tower's light).
const FLASH_T: float = 0.5
## A decoy pulls the beam aside: the arcs draw over this time.
const DECOY_PULL_T: float = 0.55

# ---- 2 unseal: the three candidate lines shimmer, two collapse, the real one ignites end to end ----
const UNSEAL_T: float = 1.7
## Fractions of UNSEAL_T: shimmer to here, then the two collapse until here, then the real line ignites to the end.
const UNSEAL_SHIMMER_END: float = 0.35
const UNSEAL_COLLAPSE_END: float = 0.7
## After the response, the lit real line holds this long before it fires.
const FIRE_HOLD: float = 0.5

# ---- 3 spoof window: SKIP targets and JAM pulse, a countdown ring that never forces a pick ----
## The ring drains over this long, then rests empty (the lab is turn-based).
const DECIDE_RING_T: float = 8.0
## The pick's own effect: the skipped node's bypass arc draws, or the hunter's turn is struck out.
const PICK_FX_T: float = 0.7
## The ambient pulse of the SKIP / JAM marks (period).
const PULSE_T: float = 0.9

# ---- 4 hunter ----
const TURN_T: float = 1.2
## The hunter's beam leads shorter than the other beams.
const HUNTER_LEAD: float = 0.15

# ---- 5 impact ----
## The wrench drops in and the node shakes.
const WRENCH_T: float = 0.6
const SHAKE_T: float = 0.45
## A second hit takes the node: the ground flips to the corp's over this time.
const FLIP_T: float = 0.7
## HOME's drain: the pip goes at once, the white lag bar follows over HOME_LAG_T after a short beat.
const HOME_LAG_DELAY: float = 0.25
const HOME_LAG_T: float = 1.1
## The floating "-1" over HOME.
const HOME_NUM_T: float = 1.2

# ---- 6 stamp ----
## The stamp slams in after the last beam: the delay, then the slam.
const STAMP_DELAY: float = 0.3
const STAMP_T: float = 0.5
const END_T: float = 1.6
## The leg verdict counts up on the record.
const COUNT_UP_T: float = 1.2

# ---- 7 heat ----
## The meter's number and fill ease to the new Heat over this long; each threshold crossed pulses and stamps its glyph.
const HEAT_EASE_T: float = 1.0
const HEAT_PULSE_T: float = 0.9

# ---- other beats ----
## The "no spoof left" beat.
const NOTE_T: float = 0.9
## The settled breach's fast playout (one short beat per beam).
const FAST_BEAT: float = 0.5
const FAST_UNSEAL: float = 0.4
const FAST_TURN: float = 0.4
const FAST_END: float = 0.9
## The BREACHED card slams in over this long.
const BREACH_CARD_T: float = 0.7

## True while the instant toggle is on: the raid skips to the next decision or to its end in one frame, every effect drawn
## in its settled state. The events and their order are the same as animated (checked in flow_check).
static var instant: bool = false


## The ease of a 0..1 progress that overshoots a little and settles (the slam).
static func ease_back(u: float) -> float:
	var x := clampf(u, 0.0, 1.0) - 1.0
	return 1.0 + x * x * (2.70158 * x + 1.70158)


## Ease out (fast first, then slow).
static func ease_out(u: float) -> float:
	var x := 1.0 - clampf(u, 0.0, 1.0)
	return 1.0 - x * x * x


## A drop that bounces once: 0 at the start, 1 at the landing and after (a falling token).
static func drop(u: float) -> float:
	var x := clampf(u, 0.0, 1.0)
	if x < 0.7:
		var f := x / 0.7
		return f * f
	var b := (x - 0.7) / 0.3
	return 1.0 - 0.14 * sin(b * PI)
