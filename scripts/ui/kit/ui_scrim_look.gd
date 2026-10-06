class_name UiScrimLook
extends Resource
## B1a (M14 integration review D1, D19, section d "World darkening under the UI"; ART_BIBLE v2
## §3.1, §4.1): the numbers of the world's darkening under the UI (`UiScrimPools`), its light
## spill and its panel shadows (`UiSpillShadows`). One file, `content/config/ui_scrim_look.tres`,
## read by every screen over the city. Lengths are px at a 1080 px tall screen
## (`reference_height`; the bible's numbers): the layers scale them to their own height.
## Read-only content: a view never writes it.

## The screen height the px lengths below are given at.
@export var reference_height: float = 1080.0

@export_group("Pools")
## What a wheel's pool leaves of the world (review D1: multiply by 0.55 inside the disc).
@export var wheel_pool_multiply: float = 0.55
## A wheel's pool holds its full darkness out to this radius, times the wheel's disc radius
## (review D1: 1.25 R), then fades out over `wheel_pool_fade` x R (B1a b: the pool shows as a
## dark ring round the wheel, never hidden under its disc).
@export var wheel_pool_reach: float = 1.25
@export var wheel_pool_fade: float = 0.3
## What a panel's pool leaves of the world round it (review section d: 0.55 pools).
@export var panel_pool_multiply: float = 0.55
## How far past a panel's edge its pool reaches (px at 1080), and the share of that it holds at
## full darkness before it fades out (B1a b: the margin reads at sheet size).
@export var panel_pool_margin_px: float = 120.0
@export var panel_pool_hold: float = 0.7
## The pools' saturation (review D1: the backdrop capped at 0.6 inside the pools; 1 = none),
## toward the pixel's own luma (Rec. 709), reached where a pool holds its full darkness.
@export var pool_saturation: float = 0.6

@export_group("Bands")
## What a bar's band leaves of the world (review D1: about 35 % black; B1a b: 42 %, so the city
## past the bar reads 0.55 to 0.65 of its open look, the art director's target).
@export var band_multiply: float = 0.58
## How far a band reaches past the bar it lies under (px at 1080; review D1: 70 px under the top
## strip, 120 px under the hand), and the share of that it holds at full darkness.
@export var band_reach_top_px: float = 70.0
@export var band_reach_bottom_px: float = 120.0
@export var band_hold: float = 0.75

@export_group("Light spill")
## The spill's additive strength at its element's edge (review D19: 20 to 30 %).
@export var spill_strength: float = 0.25
## The spill's radius, times its element's radius (half its diagonal; D19: 1.5x).
@export var spill_radius_scale: float = 1.5
## A pencil stroke's spill (the TARGET pencil, the aim): how far its light reaches from the wax
## line (px at 1080; spill_strength at the line, nothing at this distance) and the most segments
## one stroke is cut into (the spill's slots are shared by the screen).
@export var line_glow_px: float = 48.0
@export var line_segments: int = 6

@export_group("Panel shadows")
## A panel's drop shadow: its darkness (D19: black at 45 %), its soft edge (D19: 18 px) and
## its drop (px at 1080; the concepts' panels sit on the world, lit from above).
@export var shadow_alpha: float = 0.45
@export var shadow_soft_px: float = 18.0
@export var shadow_offset_px: Vector2 = Vector2(0.0, 6.0)

@export_group("Map dim (B4: the HQ idle, review D7, round 44 hq_idle)")
## What the dim leaves of the world outside the network's fit rect (D7: the 0.68 "map band"
## darkening) and inside it (round 44: x0.86), and the saturation outside (round 44: "slightly
## desaturated, but keeps its hue"; 1 = none).
@export var map_dim_outside: float = 0.68
@export var map_dim_inside: float = 0.86
@export var map_dim_saturation: float = 0.85
## How far the network's rect is grown round its icons and over how far its edge fades
## (px at 1080).
@export var map_dim_margin_px: float = 70.0
@export var map_dim_feather_px: float = 110.0
## The soft vignette round the selected Site where the city is fully lit (D7): full light out
## to `map_focus_hold_px`, back to the dim at `map_focus_end_px` (px at 1080).
@export var map_focus_hold_px: float = 110.0
@export var map_focus_end_px: float = 300.0

@export_group("Quality tiers (Settings.city_quality via CityConfig.tier_for)")
## Per tier: the spill and the shadows draw (tier 0, the cheapest, keeps the pools only: they
## carry the UI's contrast and cost one pass).
@export var tier_spill: Array[bool] = [false, true, true]
@export var tier_shadows: Array[bool] = [false, true, true]


## The tier's flag in `flags` (the last entry past its end).
static func flag_at(flags: Array[bool], tier: int) -> bool:
	if flags.is_empty():
		return true
	return flags[clampi(tier, 0, flags.size() - 1)]
