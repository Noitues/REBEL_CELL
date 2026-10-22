class_name RcLookSignPreset
extends Resource
## LOOK-TOOLBOX module 11: one neon tube treatment (RcLookSign, rc_sign.gdshaderinc). Read only.

## How the tube's centre is drawn: flat colour (today's signs), lightened toward the core colour across the tube, or a
## thin hot core.
enum Treatment { FLAT, LIGHTEN, HOT }

@export var treatment: Treatment = Treatment.FLAT
## The tube's half width (px at 1080p), the hot core's width as a share of it, and how far the core goes toward the core
## colour (0 none, 1 all the way).
@export var half_w_px: float = 4.0
@export var core_share: float = 0.35
@export var hot: float = 0.0
@export var core_color: Color = Color("#FFE3F7")
## The glow around the tube: reach (px past the tube's edge), shape (rcl_fall_exp k) and gain (linear).
@export var glow_px: float = 18.0
@export var glow_k: float = 1.4
@export var glow_gain: float = 0.6


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if half_w_px <= 0.0:
		errs.append("half_w_px must be above 0 (%s)" % half_w_px)
	if core_share <= 0.0 or core_share > 1.0:
		errs.append("core_share must be in (0, 1] (%s)" % core_share)
	if hot < 0.0 or hot > 1.0:
		errs.append("hot must be 0..1 (%s)" % hot)
	if treatment == Treatment.FLAT and hot != 0.0:
		errs.append("a flat tube has no hot core (hot %s)" % hot)
	if glow_px <= 0.0 or glow_k <= 0.0:
		errs.append("glow_px and glow_k must be above 0 (%s, %s)" % [glow_px, glow_k])
	return errs
