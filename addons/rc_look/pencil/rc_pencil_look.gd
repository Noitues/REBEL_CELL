class_name RcPencilLook
extends Resource
## LOOK-TOOLBOX module 12: the grease pencil's look numbers (addons/rc_look/config/pencil_look.tres), read by the wax
## engine (GreasePencilMark, GreasePencilWord, PencilShapes). Sizes are 1080p px unless named otherwise. Pure data.

const DEFAULT_PATH := "res://addons/rc_look/config/pencil_look.tres"

@export_group("Width")
## A mark's width (underlines, routes, crosses, small rings) and a hero mark's (the aim arc and its loop, a TARGET ring).
@export var mark_width_1080: float = 10.0
@export var hero_width_1080: float = 16.0
@export_group("Pressure")
@export var mark_pressure: RcPencilPressure
@export var hero_pressure: RcPencilPressure
@export var word_pressure: RcPencilPressure
## Width-curve knots per stroke (the pressure is sampled this many times along the drawn part).
@export var pressure_knots: int = 18
@export_group("Hand")
## A hand path's sideways wobble (share of the width) and its wave length (widths).
@export var path_wobble: float = 0.32
@export var path_wave: float = 9.0
## An underline: its bow (share of the width), its overshoot past each end (share of its length, then widths at
## least) and the hooked downstroke at its far end: length (widths) and turn (degrees, clockwise on screen).
@export var line_bow: float = 0.45
@export var line_overshoot: float = 0.035
@export var line_overshoot_min: float = 1.2
@export var hook_len: float = 2.6
@export var hook_turn_deg: float = 115.0
## A hand route's corners: the radius they round to (widths) and the overshoot past a corner before the turn (widths).
@export var corner_radius: float = 2.2
@export var corner_overshoot: float = 0.9
## A hand loop: its radius jitter (share), an egg's second-harmonic squash (share), the overlap past the start (deg),
## the tail's run outward (share of the radius) and the tilt of its axis (radians, either way).
@export var loop_jitter: float = 0.045
@export var loop_egg: float = 0.04
@export var loop_overlap_deg: float = 34.0
@export var loop_tail_out: float = 0.11
@export var loop_tilt: float = 0.1
@export_group("Word")
## A pencil word's wax width (share of its font px) and its hand: per-letter turn (radians), baseline drop (share of
## the font px), size jitter (share) and a sideways wobble of each stroke (share of the font px).
@export var word_width_em: float = 0.2
@export var word_letter_turn: float = 0.06
@export var word_baseline_jitter: float = 0.035
@export var word_size_jitter: float = 0.04
@export var word_wobble_em: float = 0.012


static var _default: RcPencilLook = null


## The default look, loaded once.
static func current() -> RcPencilLook:
	if _default == null:
		_default = load(DEFAULT_PATH)
	return _default
