class_name RcLookBitsPreset
extends Resource
## LOOK-TOOLBOX module 16: one way of drawing and flying bits (RcLookBits, rc_bits.gdshaderinc). Read only. Each preset
## is today's look of one caller; the rulings (hot colour, outline, flip vs trail, spin offset, turn) are fields, so
## the designer's choice becomes a one-line change here once the lab sheet is ruled on.

## How the path bows: round a wheel's rim (control point on the rim bisector) or sideways by a share of its length.
enum Path { RIM, FREE }
## The rim of a glyph: its own colour (the atlas' same-colour outline) or the night-sky rim (BitsSeam's dark rim).
enum Outline { SAME_COLOUR, NIGHT_RIM }
## What gives a bit its life: flipping 0 <-> 1 while it tumbles, or a faint trail copy behind it.
enum Life { FLIP_TUMBLE, TRAIL }

@export var path: Path = Path.RIM
@export var outline: Outline = Outline.SAME_COLOUR
@export var life: Life = Life.FLIP_TUMBLE
## The colour a bit starts in (WHITE_HOT today on the GPU and the CPU fallback; BitsSeam's start is PAPER).
@export var hot_color: Color = Color(1, 1, 1)
## Whether the tumble starts at the bit's flip phase x a turn (the GPU shader does; the CPU fallback does not today).
@export var spin_phase: bool = true
## A turn in the tumble, radians: today's 6.28; TAU is the ruling option.
@export var spin_turn: float = 6.28


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if spin_turn < 6.0 or spin_turn > 6.5:
		errs.append("spin_turn must be about one turn (%s)" % spin_turn)
	return errs
