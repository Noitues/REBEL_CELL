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
## Off = the end state at once, as under reduce effects (ANIM-R5: by kind of entry, see
## UiMotionData.OFF_PARTS and ALWAYS_ON).
@export var enabled: bool = true
## ART-0 E (ported from art-pass W6, ART_BIBLE v2 5.3): the effect's VFX tier, spectacle by
## importance. The FX layers clamp an effect to its tier's limits (coverage, duration, flash
## alpha, shake and hit-stop: VfxTier); only T4 may cover the whole screen.
enum Tier { T0_AMBIENT, T1_FEEDBACK, T2_OUTCOME, T3_MOMENT, T4_CINEMATIC }
@export var tier: Tier = Tier.T1_FEEDBACK
## ART-0 audit E2: what `duration` measures. ONE_SHOT: an effect that plays once; it must fit
## its tier's longest duration (VfxTier.MAX_SECONDS). HOLD: how long something stays or is
## waited for (a hold, a wait, a budget, a note left up to be read), not an effect's length.
## LOOP: one period (or half-period) of a motion that repeats while a state lasts. HOLD and
## LOOP are not held to the tier's duration; their look still follows the tier.
enum Kind { ONE_SHOT, HOLD, LOOP }
@export var kind: Kind = Kind.ONE_SHOT


## Problems with this entry (empty when valid).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if id == &"":
		errors.append("Motion entry has no id.")
	if duration < 0.0 or delay < 0.0:
		errors.append("Motion %s: duration and delay must be >= 0." % id)
	if tier < Tier.T0_AMBIENT or tier > Tier.T4_CINEMATIC:
		errors.append("Motion %s: tier must be T0..T4." % id)
	if kind < Kind.ONE_SHOT or kind > Kind.LOOP:
		errors.append("Motion %s: kind must be ONE_SHOT, HOLD or LOOP." % id)
	return errors
