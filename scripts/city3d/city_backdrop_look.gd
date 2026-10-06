class_name CityBackdropLook
extends Resource
## Parity fix TITLE-01 (designer 2026-10-05, concept round 33 `title_screen.png`): how a
## BlurredCityBackdrop frames and softens the one 3D city behind a menu: the city quality
## tiers that take the 3D city (below them the screen keeps its 2D NeonCity), the fixed camera
## (a corp's HQ landmark at a screen anchor), the tilt-shift blur (a sharp band, soft above and
## below) and the darkening the menu reads over. The darkening numbers are round 33 `title.py`
## `backdrop()`'s, unchanged (art-concepts-r43 dcfdf74). Read-only content: a view never writes it.

@export_group("Tiers")
## Per city quality tier (CityConfig.tier_for): the 3D city (true) or the 2D fallback (false).
@export var city_tiers: Array[bool] = [false, true, true]

@export_group("Framing")
## The corp whose HQ stands in the frame when no campaign has been played (round 33: Halcyon).
@export var default_corp: StringName = &"halcyon"
## Ortho width (BU) of the view.
@export var ortho: float = 300.0
## Height (BU) of the HQ point placed at `anchor`.
@export var lift: float = 20.0
## Where the HQ's point lands (share of the view: x from the left, y from the top).
@export var anchor: Vector2 = Vector2(0.86, 0.64)

@export_group("Tilt-shift blur")
## Blur radius (px at `ref_height` px of view height; round 33: GaussianBlur 5 at 1080).
@export var blur_px: float = 5.0
@export var ref_height: float = 1080.0
## The sharp band: its centre (share of the height), half height and edge power
## (band = clamp(1 - |v - centre| / half, 0, 1) ^ power).
@export var focus_centre: float = 0.56
@export var focus_half: float = 0.36
@export var focus_power: float = 0.8

@export_group("Darkening")
## The menu side: darkened by `side_dark` at the left edge, fading out by `side_reach` of the
## width, with power `side_power` (round 33: 0.62, 900 / 1920, 1.4).
@export var side_dark: float = 0.62
@export var side_reach: float = 0.46875
@export var side_power: float = 1.4
## The foot: darkened by `foot_dark` at the bottom, from `foot_from` of the height down.
@export var foot_dark: float = 0.35
@export var foot_from: float = 0.82
## Vignette: 1 - strength * (((u - cx) * sx)^2 + ((v - cy) * sy)^2).
@export var vignette: float = 0.35
@export var vignette_centre: Vector2 = Vector2(0.6, 0.5)
@export var vignette_scale: Vector2 = Vector2(1.3, 1.1)
## Overall gain after the darkening.
@export var gain: float = 0.86


## True when city quality tier `tier` takes the 3D city and a renderer can draw it.
func city_mode(tier: int, can_render: bool) -> bool:
	return can_render and tier >= 0 and tier < city_tiers.size() and city_tiers[tier]


## The sharp share (0 blurred .. 1 sharp) at view share `uv` (the shader's `band`).
func focus_at(uv: Vector2) -> float:
	return pow(clampf(1.0 - absf(uv.y - focus_centre) / maxf(focus_half, 0.0001), 0.0, 1.0), focus_power)


## The brightness factor the darkening leaves at view share `uv` (the shader's `dark * vig *
## gain`): 1 untouched .. 0 black.
func field_at(uv: Vector2) -> float:
	var side := pow(clampf(1.0 - uv.x / maxf(side_reach, 0.0001), 0.0, 1.0), side_power)
	var foot := clampf((uv.y - foot_from) / maxf(1.0 - foot_from, 0.0001), 0.0, 1.0)
	var dark := 1.0 - side_dark * side - foot_dark * foot
	var d := (uv - vignette_centre) * vignette_scale
	var vig := 1.0 - vignette * (d.x * d.x + d.y * d.y)
	return maxf(dark * vig * gain, 0.0)


## The largest field_at over rect `r` (px) of a view of `size` px (a grid of samples, edges
## included): the brightest the backdrop gets behind `r`.
func max_field(r: Rect2, size: Vector2, steps: int = 8) -> float:
	var best := 0.0
	for i in steps + 1:
		for j in steps + 1:
			var p := r.position + r.size * Vector2(float(i) / steps, float(j) / steps)
			best = maxf(best, field_at(p / size.max(Vector2.ONE)))
	return best
