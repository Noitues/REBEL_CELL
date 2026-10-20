class_name CityTerrainColor
extends RefCounted
## LOOK L5 (whole-city plate parity, hybrid port): the land's albedo by height, slope and noise, ported from the Blender
## plate build (art-pass city_all_corps/scripts/city_world_a2.py `terrain_col`, day TCOL): meadow -> forest with height and
## noise, rock on steep or high ground, snow on the peaks, beach on the low shore. Heights are BU (the Blender build's lot is
## the same 6 BU); `terrain_h_scale` maps the Blender thresholds onto r2's lower mountains. Pure: same inputs, same colour.

const SEED_COARSE := 7750
const SEED_FINE := 7751


## The albedo of land corner `l` (lot coordinates) of `terrain`.
static func at(cfg: CityConfig, terrain: CityA2Terrain, l: Vector2i) -> Color:
	var r: Dictionary = cfg.terrain_rule
	var k: float = cfg.terrain_h_scale
	var h := terrain.height_at(l.x, l.y)
	var sl := slope_at(cfg, terrain, l)
	var n := CityMeshKit.hash01(SEED_COARSE, l.x >> 1, l.y >> 1) * 0.5 + CityMeshKit.hash01(SEED_FINE, l.x, l.y) * 0.5
	var tc: Dictionary = cfg.terrain_colors
	var base := (tc["meadow"] as Color).lerp(tc["forest"], clampf(float(r["forest_from"]) + h / (float(r["forest_h"]) * k)
			+ (n - 0.5) * float(r["forest_noise"]), 0.0, 1.0))
	var rock := clampf((sl - float(r["rock_slope"])) / float(r["rock_slope_span"]), 0.0, 1.0) \
			+ maxf(0.0, (h - float(r["rock_h"]) * k) / (float(r["rock_h_span"]) * k))
	var c := base.lerp(tc["rock"], clampf(rock, 0.0, 1.0))
	if h > float(r["snow_h"]) * k:
		c = c.lerp(tc["snow"], clampf((h - float(r["snow_h"]) * k) / (float(r["snow_span"]) * k) + (n - 0.5) * 0.5, 0.0, 1.0))
	if h < float(r["beach_h"]) and h > 0.0:
		c = c.lerp(tc["beach"], float(r["beach_k"]))
	var g: float = float(r["noise_lo"]) + float(r["noise_span"]) * n
	return Color(c.r * g, c.g * g, c.b * g)


## The ground's slope at corner `l` (rise per BU, central differences over one lot).
static func slope_at(cfg: CityConfig, terrain: CityA2Terrain, l: Vector2i) -> float:
	var dx := terrain.height_at(l.x + 1, l.y) - terrain.height_at(l.x - 1, l.y)
	var dy := terrain.height_at(l.x, l.y + 1) - terrain.height_at(l.x, l.y - 1)
	return Vector2(dx, dy).length() / (2.0 * cfg.lot_bu)
