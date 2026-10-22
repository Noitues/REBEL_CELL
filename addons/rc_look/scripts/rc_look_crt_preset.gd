class_name RcLookCrtPreset
extends Resource
## LOOK-TOOLBOX module 14: one CRT / terminal look (RcLookCrt, rc_crt.gdshaderinc): the numbers a screen of the game
## hard-codes today. Read only.

## The glass's accent (edge, glow, roll and wash) and its two glass colours (top to bottom).
@export var accent: Color = Color("#5CE1FF")
@export var glass_top: Color = Color("#0B1630")
@export var glass_bottom: Color = Color("#050A1A")
## Scanlines: the period (px) and the phase of the step form (crt_terminal 0.08, the FRAGCOORD forms 0), the strength, and
## the sine form's density (cycles of pi per screen height; 0 = the step form).
@export var scan_px: float = 3.0
@export var scan_phase: float = 0.08
@export var scan_strength: float = 0.10
@export var scan_sine_density: float = 0.0
## Flicker: the strength, and the rate (rad/s).
@export var flicker: float = 0.0
@export var flicker_rate: float = 43.0
## The rolling band: strength, seconds per pass, gaussian half-width (share of the panel's height).
@export var roll_strength: float = 0.03
@export var roll_seconds: float = 7.0
@export var roll_width: float = 0.08
## Edge: line (px), outer glow reach (px) and strength, the inner glow (strength, reach px), the accent wash's reach (px),
## the corner notch (px) and the corner radius (px).
@export var edge_px: float = 1.5
@export var glow_px: float = 10.0
@export var glow_strength: float = 0.45
@export var inner_glow: float = 0.18
@export var inner_glow_px: float = 10.0
@export var wash_px: float = 18.0
@export var notch_px: float = 14.0
@export var corner_px: float = 3.0
## The glass's inner vignette: its reach (px) and the gain it keeps at the edge.
@export var vignette_px: float = 28.0
@export var vignette_floor: float = 0.78
## The screen vignette (scanline.gdshader): amount and the smoothstep's two ends.
@export var screen_vignette: float = 0.0
@export var screen_vignette_inner: float = 0.45
@export var screen_vignette_outer: float = 0.85
## The hex dump's alpha on the glass (crt_terminal: 0.06; 0 = none).
@export var hex_alpha: float = 0.06


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if scan_px < 1.0:
		errs.append("scan_px must be at least 1 (%s)" % scan_px)
	if scan_strength < 0.0 or scan_strength > 1.0:
		errs.append("scan_strength must be 0..1 (%s)" % scan_strength)
	if flicker < 0.0 or flicker > 1.0:
		errs.append("flicker must be 0..1 (%s)" % flicker)
	if roll_seconds <= 0.0 or roll_width <= 0.0:
		errs.append("roll_seconds and roll_width must be above 0 (%s, %s)" % [roll_seconds, roll_width])
	if vignette_px <= 0.0 or vignette_floor < 0.0 or vignette_floor > 1.0:
		errs.append("vignette_px must be above 0 and vignette_floor 0..1 (%s, %s)" % [vignette_px, vignette_floor])
	if screen_vignette < 0.0 or screen_vignette > 1.0 or screen_vignette_outer <= screen_vignette_inner:
		errs.append("screen vignette: amount 0..1 and outer above inner (%s, %s, %s)" % [screen_vignette,
				screen_vignette_inner, screen_vignette_outer])
	if hex_alpha < 0.0 or hex_alpha > 1.0:
		errs.append("hex_alpha must be 0..1 (%s)" % hex_alpha)
	if glow_px <= 0.0 or edge_px <= 0.0:
		errs.append("glow_px and edge_px must be above 0 (%s, %s)" % [glow_px, edge_px])
	return errs
