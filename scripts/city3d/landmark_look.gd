class_name LandmarkLook
extends Resource
## ART-5 5b: the tuning of the landmark materials (assets/city/landmarks/landmark_look.tres): the concept's
## target_corps MODES (night and the round 11b cool day), its per-corp ramp TINT, hq_scene's floodlit and light-cone
## numbers and the round 34 reveal. Read-only at runtime (LandmarkMaterials copies values into materials).

## 3-band toon ramp (shadow / mid / lit) at night and by day, and the band edges on N.L (the spike's edges include
## the concept's 0.03 world light).
@export var ramp_night: Array[Color] = [Color(0.09, 0.08, 0.21), Color(0.20, 0.17, 0.36), Color(0.36, 0.30, 0.54)]
@export var ramp_day: Array[Color] = [Color(0.22, 0.26, 0.42), Color(0.50, 0.54, 0.64), Color(0.84, 0.84, 0.82)]
@export var ramp_edges: Vector2 = Vector2(0.118, 0.363)
## Per-corp tint on the ramp (target_corps.TINT), keyed by corporation id.
@export var corp_tint: Dictionary = {&"meridian": Color(1, 1, 1), &"solace": Color(0.92, 1.07, 0.96),
	&"halcyon": Color(1.0, 0.94, 1.08), &"orbital": Color(0.76, 1.02, 1.12), &"rebel_cell": Color(1.16, 0.88, 0.92)}
## Floodlit surfaces (lm_lit): emission share of the colour.
@export var lit_emission: float = 0.42
## Emission gains: neon (trims, rings, chaser) and windows, night and day; by day windows mix toward dark glass.
@export var neon_gain_night: float = 1.0
@export var neon_gain_day: float = 0.75
@export var window_gain_night: float = 1.0
@export var window_gain_day: float = 0.55
@export var window_glass_day: Color = Color(0.10, 0.14, 0.20)
@export var window_glass_mix_day: float = 0.55
@export var sign_gain: float = 1.0
## Light cones (lm_beam): opacity of the emission over what is behind.
@export var beam_alpha: float = 0.22
## REBEL_CELL reveal (map34): the blackout front's flicker band, the lit share of detail-line windows before the
## reveal, and how far the detail-line buildings darken toward lines_dark once revealed.
@export var flicker_band: float = 0.12
## The red fist windows' emission over the city windows' (map34 lights the crest brighter and spills a red glow).
@export var fist_gain: float = 1.8
@export var lines_window_share: float = 0.85
@export var lines_dark: Color = Color(8.0 / 255.0, 6.0 / 255.0, 12.0 / 255.0)
@export var lines_dark_k: float = 0.55
