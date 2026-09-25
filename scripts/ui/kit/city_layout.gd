class_name CityLayout
extends RefCounted
## Where the campaign's Grid sits in the city (view-only): Sites are laid out like the
## Grid data inside the corporation's territory, the boss end towards its HQ. Shared by
## the Grid, raid and netrun map overlays so a Site is the same building everywhere.

const RIGHT := Vector2(1, -1)
const DOWN := Vector2(1, 1)


## Grid point (lots) for every Site id of `corp`'s City Grid.
static func site_points(corp: CorporationData) -> Dictionary:
	var out := {}
	var min_p := Vector2(1e9, 1e9)
	var max_p := Vector2(-1e9, -1e9)
	for sd in corp.city_grid.sites:
		if sd != null:
			min_p = min_p.min(sd.map_position)
			max_p = max_p.max(sd.map_position)
	var span := (max_p - min_p).max(Vector2(1, 1))
	var origin := NeonCity.hq_of(corp.id) + Vector2(2.5, 2.5) - RIGHT * 8.0 + DOWN * 1.5
	for sd in corp.city_grid.sites:
		if sd == null:
			continue
		var uv := (sd.map_position - min_p) / span * 2.0 - Vector2.ONE
		out[sd.id] = origin + RIGHT * uv.x * 7.5 + DOWN * uv.y * 5.0
	return out
