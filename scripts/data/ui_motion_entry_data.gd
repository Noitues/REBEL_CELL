class_name UiMotionEntryData
extends Resource
## One animation's timing in `content/config/ui_motion.tres` (ANIMATION_HANDOFF 3, STYLE_GUIDE
## 5): read by the `Motion` helpers by `id`. View tuning only; never read by a rule.

## Animation id (e.g. &"card_hover"). Unique across content (the registry checks).
@export var id: StringName
## Seconds at 1x speed. For a loop it is one period; for a per-step motion, one step.
@export_range(0.0, 10.0, 0.005, "or_greater") var duration: float = 0.2
## Seconds before the motion starts (at 1x); a stagger for sequences.
@export_range(0.0, 10.0, 0.005, "or_greater") var delay: float = 0.0
@export var ease: Tween.EaseType = Tween.EASE_OUT
@export var trans: Tween.TransitionType = Tween.TRANS_QUAD
## Size of the motion in the unit its helper names (the entry's comment in the .tres says
## which): px for slides, lifts and shakes; a scale for pops and bumps (and a radius
## multiplier for bursts under 4); an alpha for fades, blinks and flashes; degrees for
## tilts and flips; frames for the hit freeze; ticks per second for the spin blur; tenths
## of a tick for spin overshoot; seconds as a cap (a menu line's typing); a share (0..1)
## for splits of a motion's time or of a quantity; px per second for speeds; a count for
## pulses.
@export var amplitude: float = 0.0
## Off = the end state at once, as under reduce effects.
@export var enabled: bool = true


## Problems with this entry (empty when valid).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if id == &"":
		errors.append("Motion entry has no id.")
	if duration < 0.0 or delay < 0.0:
		errors.append("Motion %s: duration and delay must be >= 0." % id)
	return errors
