class_name EventHeldMark
extends Control
## The "still typing" mark on a Terminal event's choice while its story types in (ANIM-R2
## E2): three dots over the note's top-right corner, like a typing indicator. The choice
## itself keeps its normal paper, words and outcome icons (a disabled note was nearly
## invisible). Drawn steady (no motion, so nothing to reduce); it goes when the choice is
## released. View only; takes no input.

## Dot radius, the gap between dots and the inset from the corner (px at text scale 1.0).
const DOT_R := 3.0
const DOT_GAP := 5.0
const INSET := Vector2(10, 0)
## How far the dots sit above the note's top edge (px): in the gap between the choices.
const DOT_LIFT := 2.0
## The dots' colour: the note's paper, over the dark gap.
const DOT_ALPHA := 0.85
const DOTS := 3


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## The dots' centres (local), right to left from the corner.
func dot_centres() -> PackedVector2Array:
	var s := Settings.text_scale
	var out := PackedVector2Array()
	var r := DOT_R * s
	for k in DOTS:
		# Just above the note's top edge (in the gap between choices): never on its words.
		out.append(Vector2(size.x - INSET.x * s - r - k * (r * 2.0 + DOT_GAP * s), -(r + DOT_LIFT)))
	return out


func _draw() -> void:
	var r := DOT_R * Settings.text_scale
	for c in dot_centres():
		# Art pass W8c (§12): high contrast draws the dots opaque in TEXT_HI.
		draw_circle(c, r, Palette.TEXT_HI if Settings.high_contrast else Color(Palette.NOTE_PAPER, DOT_ALPHA))
