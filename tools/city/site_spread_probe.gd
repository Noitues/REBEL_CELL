extends Node
## ART-5 5e: the Site layout's sweep (headless). For every corporation it prints how many of
## its Sites the shipped layout (CityLayout.site_points: the x2 spread aimed into its
## territory) lays inside its own territory, on another HQ's plaza, off the city, or on a
## lot another Site took; with `--search` it also tries every aim (72 headings, 5 degrees apart, x mirror) at
## the shipped spread and prints the best ones. Run:
## godot --headless --path . res://tools/city/site_spread_probe.tscn [-- --search]

const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"orbital", &"rebel_cell", &"solace"]


func _ready() -> void:
	var search := OS.get_cmdline_user_args().has("--search")
	var city := NeonCity.new()
	var cfg: CityConfig = CityView3D.CONFIG
	for id in CORPS:
		var corp := load("res://content/corporations/%s.tres" % id) as CorporationData
		var r := CityLayout.spread_report(city, corp, CityLayout.site_points(corp))
		print("SCREEN %s need=%.1f" % [id, screen_need(CityLayout.site_points(corp))])
		print("SPREAD %s aim=%s mirror=%s spread=%.2f sites=%d in=%d off=%s hq=%d out=%d dup=%d" % [id,
			cfg.site_aim_deg.get(id, 0.0), cfg.site_mirror.get(id, false), CityLayout.spread_of(id), r["sites"], r["in"],
			str(r["off"]), r["hq"], r["out"], r["dup"]])
		if not search:
			continue
		var rows: Array = []
		for k in 72:
			for m in [false, true]:
				var pts := CityLayout.site_points_aimed(corp, k * 5.0, m, cfg.site_spread)
				var rr := CityLayout.spread_report(city, corp, pts)
				var score := int(rr["in"]) - 4 * (int(rr["hq"]) + int(rr["out"]) + int(rr["dup"]))
				rows.append([score, k * 5.0, m, rr, screen_need(pts)])
		rows.sort_custom(func(a: Array, b: Array) -> bool: return a[0] > b[0] if a[0] != b[0] else a[4] < b[4])
		for i in 8:
			var row: Array = rows[i]
			var rr: Dictionary = row[3]
			print("  BEST %s aim=%.1f mirror=%s in=%d/%d off=%s hq=%d out=%d dup=%d screen=%.1f" % [id, row[1], row[2], rr["in"], rr["sites"],
				str(rr["off"]), rr["hq"], rr["out"], rr["dup"], row[4]])
	city.free()
	get_tree().quit()


## How far the Grid must zoom out to frame layout `pts` (lots across the Grid page's free map
## area, ~1.84 times as wide as tall): its screen box in the 3D projection (x - y across,
## (x + y) sin(pitch) down), the larger of width / FREE_ASPECT and height.
const FREE_ASPECT := 1.84
static func screen_need(pts: Dictionary) -> float:
	var lo := Vector2(INF, INF)
	var hi := -lo
	var k := sin(deg_to_rad(CityView3D.CONFIG.pitch_deg))
	for id in pts:
		var p: Vector2 = pts[id]
		var q := Vector2(p.x - p.y, (p.x + p.y) * k)
		lo = lo.min(q)
		hi = hi.max(q)
	return maxf((hi.x - lo.x) / FREE_ASPECT, hi.y - lo.y)
