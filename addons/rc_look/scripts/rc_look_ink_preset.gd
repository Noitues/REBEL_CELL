class_name RcLookInkPreset
extends Resource
## LOOK-TOOLBOX module 5: one ink look (RcLookInk, rc_ink.gdshaderinc). A hull preset uses colour, width, wobble and
## wobble_scale; a post preset uses colour, width, wobble_px, alpha and the two edge thresholds. Read only.

@export var color: Color = Color(0.047, 0.039, 0.086, 1.0)
## Line width in screen px (hull: grown outward; post: the tap distance).
@export var width_px: float = 2.5
## Hull: the width's wobble share (0..1) and the noise's world scale.
@export var wobble: float = 0.0
@export var wobble_scale: float = 1.0
## Post: the line's wobble in px, its opacity, and the edge thresholds (normal / material change, view depth jump
## at the reference ortho size).
@export var wobble_px: float = 0.0
@export var alpha: float = 1.0
@export var normal_edge: float = 0.42
@export var depth_edge: float = 1.2


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if width_px <= 0.0:
		errs.append("width_px must be above 0 (%s)" % width_px)
	if wobble < 0.0 or wobble > 1.0:
		errs.append("wobble must be 0..1 (%s)" % wobble)
	if alpha < 0.0 or alpha > 1.0:
		errs.append("alpha must be 0..1 (%s)" % alpha)
	if normal_edge <= 0.0 or depth_edge <= 0.0:
		errs.append("edge thresholds must be above 0 (%s, %s)" % [normal_edge, depth_edge])
	return errs
