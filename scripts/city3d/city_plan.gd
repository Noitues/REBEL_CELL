class_name CityPlan
extends RefCounted
## Plan 2 NA-12 (D3): where a city seed's territories, HQ lots, Site layouts and coast lie, in
## lots. NeonCity (and so CityLayoutRecorder, CityModel, city.json and every map) reads its city
## through the plan of its `city_seed`: the fixed seed (`CityConfig.city_seed`) is today's fixed
## city (NeonCity.TERRITORIES, the config's Site headings, no coast), the fallback that goldens
## and fixtures pin; every other seed is CityGenerator's. Pure data plus pure lookups; the
## plans are cached by seed (a plan is a pure function of its seed and the configs).
##
## The campaign's city is `current()`: the running campaign's `city_seed`, else the fixed one.

## Territories: {"id": StringName (&"" = neutral Sprawl), "at": Vector2 (lots; a corporation's
## HQ rect's top-left), "pull": float}, the corporations sorted by id, then the Sprawl centres.
var territories: Array[Dictionary] = []
var city_seed: int = 0
## True for the fixed city (no generator run).
var fixed: bool = false
## True when the generator found no layout in `city_gen_attempts` and fell back to the fixed
## territories (never seen in the 1,000-seed sweep; kept so a bad config never breaks a city).
var fallback: bool = false
## Generator attempts used (1 = the first layout passed).
var attempts: int = 0
## Why the generator's last attempt failed ("" when it passed; a diagnostic, not saved).
var failure: String = ""
## The heading (degrees) each corporation's Site layout is turned round its HQ, and whether it
## is mirrored (CityLayout.site_points_aimed).
var site_aim: Dictionary = {}
var site_mirror: Dictionary = {}
## The coast, or {} (no sea): {"side": 0 west (low i) / 1 east / 2 north (low j) / 3 south,
## "depth", "amp", "wavelength", "phase", "amp2", "wavelength2", "phase2" (two waves), "bay_at", "bay_depth",
## "bay_width" (the A2 bay: a Gaussian bump of the shore into the land)} in lots from `rect`'s edge (`shore_at`).
var coast: Dictionary = {}
## NA-12 r2: terrain hills (data only until NA-12c renders them), city_A2.json's Gaussian form in lots and BU:
## {"centre": Vector2 (lots), "sigma_x", "sigma_y" (lots), "height" (BU), "rotation" (radians)}.
var hills: Array[Dictionary] = []
## The city rect the coast is measured from (lots).
var rect: Rect2i = Rect2i()
## CITY-A2 step 1: the planner city A2 on the lot grid (CityA2Builder), or null for the fixed and grid-generated cities.
## When set it answers water, land depth and territories (`coast` then holds only "side" and "a2").
var a2: CityA2Raster = null
## CITY-A2: the lots the Site layouts stand on (Vector2i -> true; a building there stays one lot, never merged).
var a2_sites: Dictionary = {}

const FIXED_CONFIG_PATH := "res://content/config/campaign_config.tres"

static var _cache: Dictionary = {}
static var _mutex: Mutex = Mutex.new()
static var _gen_config: CampaignConfigData = null
## The corporations' Site layouts (corp id -> PackedVector2Array of uv), read once from CORP_DIR.
static var _uvs: Dictionary = {}
const CORP_DIR := "res://content/corporations"


## The HQ rect's top-left of territory `id` (lots), or the city centre (Vector2.ZERO) when it
## has none.
func hq_of(id: StringName) -> Vector2:
	for t in territories:
		if t["id"] == id:
			return t["at"]
	return Vector2.ZERO


## Whether territory `id` is on this plan.
func has_territory(id: StringName) -> bool:
	if id == &"":
		return false
	for t in territories:
		if t["id"] == id:
			return true
	return false


## The corporations' HQ rects (lots), corp id -> Rect2i (`hq_lots` square).
func hq_rects(hq_lots: int) -> Dictionary:
	var out := {}
	for t in territories:
		if t["id"] != &"":
			var at: Vector2 = t["at"]
			out[t["id"]] = Rect2i(int(at.x), int(at.y), hq_lots, hq_lots)
	return out


## The shore's distance (lots) from `rect`'s sea edge at `along` (the coordinate along that edge: j for a west / east
## sea, i for a north / south one): the base depth, two waves, and the bay (a Gaussian bump into the land at "bay_at").
func shore_at(along: float) -> float:
	var s := float(coast["depth"]) + float(coast["amp"]) * sin(TAU * along / float(coast["wavelength"]) + float(coast["phase"]))
	s += float(coast.get("amp2", 0.0)) * sin(TAU * along / float(coast.get("wavelength2", 1.0)) + float(coast.get("phase2", 0.0)))
	var u := (along - float(coast.get("bay_at", 0.0))) / maxf(float(coast.get("bay_width", 1.0)), 0.001)
	return s + float(coast.get("bay_depth", 0.0)) * exp(-u * u)


## The inland unit vector (lots) of the sea side.
func inland() -> Vector2:
	return [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)][int(coast["side"])]


## The lot point `d` lots inland of the sea edge at `along`.
func edge_point(along: float, d: float) -> Vector2:
	match int(coast["side"]):
		0:
			return Vector2(float(rect.position.x) + d, along)
		1:
			return Vector2(float(rect.end.x) - d, along)
		2:
			return Vector2(along, float(rect.position.y) + d)
	return Vector2(along, float(rect.end.y) - d)


## How far point (x, y) (lots) lies inland of the coast (negative: in the sea); INF without one.
func land_depth(x: float, y: float) -> float:
	if a2 != null:
		return a2.depth_at(x, y)
	if coast.is_empty():
		return INF
	var side := int(coast["side"])
	var along := y if side < 2 else x
	var shore := shore_at(along)
	match side:
		0:
			return x - float(rect.position.x) - shore
		1:
			return float(rect.end.x) - x - shore
		2:
			return y - float(rect.position.y) - shore
	return float(rect.end.y) - y - shore


## True when lot (i, j)'s centre is in the sea.
func is_water(i: int, j: int) -> bool:
	if a2 != null:
		return a2.is_water(i, j)
	return not coast.is_empty() and land_depth(i + 0.5, j + 0.5) < 0.0


## CITY-A2: [owner, runner-up, border 0-1] of lot (i, j) from the A2 districts (NeonCity's `_territory_pair` form),
## or [] for a city without A2 (NeonCity then uses its nearest-centre territories).
func territory_pair(i: int, j: int) -> Array:
	return a2.territory_pair(i, j) if a2 != null else []


## The sea lots inside `rect`, row by row (j, then i).
func sea_cells() -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	if coast.is_empty():
		return out
	for j in range(rect.position.y, rect.end.y):
		for i in range(rect.position.x, rect.end.x):
			if is_water(i, j):
				out.append(Vector2i(i, j))
	return out


## The land lots inside `rect` with a sea lot as a 4-neighbour (the sea wall's lots), row by row.
func shoreline() -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	if coast.is_empty():
		return out
	for j in range(rect.position.y, rect.end.y):
		for i in range(rect.position.x, rect.end.x):
			if is_water(i, j):
				continue
			for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				if is_water(i + d.x, j + d.y):
					out.append(Vector2i(i, j))
					break
	return out


## The compass word of the sea side in plan coordinates (x east = +i, y north = -j).
func sea_side() -> String:
	return ["W", "E", "N", "S"][int(coast["side"])] if not coast.is_empty() else ""


## NA-12 r2: the optional additive `city.json` v1 sections of this city (NA02_FIELDS 2, "Optional sections"):
## `coast {sea_side, shoreline [[i, j]...], sea_cells [[i, j]...]}` (lots, row order) and `terrain {hills [{centre [x, y],
## sigma_x, sigma_y, height, rotation}]}` (plan BU, city_A2.json's Gaussian form). {} for the fixed city (no key).
func city_sections(lot_bu: float, origin: Vector2) -> Dictionary:
	if fixed or coast.is_empty():
		return {}
	var shore := []
	for c in shoreline():
		shore.append([c.x, c.y])
	var sea := []
	for c in sea_cells():
		sea.append([c.x, c.y])
	var hl := []
	for h in hills:
		hl.append({"centre": NetrunArtExport.plan_point(h["centre"], lot_bu, origin), "sigma_x": float(h["sigma_x"]) * lot_bu,
			"sigma_y": float(h["sigma_y"]) * lot_bu, "height": float(h["height"]), "rotation": -float(h["rotation"])})  # plan y = -j
	return {"coast": {"sea_side": sea_side(), "shoreline": shore, "sea_cells": sea}, "terrain": {"hills": hl}}


## The plan as plain data (ints, floats, strings; sorted keys when made canonical), for
## byte-identity checks and the save-and-resume test.
func to_dict() -> Dictionary:
	var terr: Array = []
	for t in territories:
		var at: Vector2 = t["at"]
		terr.append({"id": String(t["id"]), "at": [at.x, at.y], "pull": float(t["pull"])})
	var aims := {}
	for k: StringName in site_aim:
		aims[String(k)] = float(site_aim[k])
	var mirrors := {}
	for k: StringName in site_mirror:
		mirrors[String(k)] = bool(site_mirror[k])
	var hl := []
	for h in hills:
		var c: Vector2 = h["centre"]
		hl.append({"centre": [c.x, c.y], "sigma_x": h["sigma_x"], "sigma_y": h["sigma_y"], "height": h["height"], "rotation": h["rotation"]})
	var sites: Array = []
	for l: Vector2i in a2_sites:
		sites.append(l)
	sites.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y if a.y != b.y else a.x < b.x)
	var site_list: Array = []
	for l: Vector2i in sites:
		site_list.append([l.x, l.y])
	return {"layout_seed": ArtSeed.u64_str(city_seed), "fixed": fixed, "fallback": fallback, "territories": terr,
		"site_aim": aims, "site_mirror": mirrors, "coast": coast.duplicate(), "hills": hl,
		"rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y], "source": source(), "a2_sites": site_list}


## Where this plan's city comes from: "fixed", "a2" (the planner city) or "grid" (NA-12's CityGenerator).
func source() -> String:
	return "fixed" if fixed else ("a2" if a2 != null else "grid")


# --- The game's plans ---------------------------------------------------------------------------

## The fixed city's seed (CityConfig.city_seed: the layout every golden and fixture pins).
static func fixed_seed() -> int:
	return CityView3D.CONFIG.city_seed


## The city seed of the running campaign (its `city_seed`; 0 = the fixed city), else the fixed seed.
static func current_seed() -> int:
	var loop := Engine.get_main_loop() as SceneTree
	var rm: Node = loop.root.get_node_or_null("RunManager") if loop != null else null
	if rm != null:
		var c: Variant = rm.get("campaign")
		if c is CampaignState and (c as CampaignState).city_seed != 0:
			return (c as CampaignState).city_seed
	return fixed_seed()


## The plan of the running campaign's city.
static func current() -> CityPlan:
	return for_seed(current_seed())


## The plan of `p_seed` (cached; thread-safe: worker builds read it).
static func for_seed(p_seed: int) -> CityPlan:
	_mutex.lock()
	var p: CityPlan = _cache.get(p_seed)
	if p == null:
		p = make_fixed() if p_seed == fixed_seed() else generate(p_seed, _config())
		p.city_seed = p_seed
		_cache[p_seed] = p
	_mutex.unlock()
	return p


## A fresh plan for `p_seed` with config `cfg` (not cached): CITY-A2, the planner city (CityA2Builder.make_plan) when
## `cfg.city_layout_source` is &"a2", else NA-12's grid generator (`generate_grid`). The RNG is the seed's own named
## stream (RngStreams.make_stream(p_seed, CITY_LAYOUT_STREAM)), never a campaign stream; a failed plan falls back to the
## fixed city with `fallback` set.
static func generate(p_seed: int, cfg: CampaignConfigData) -> CityPlan:
	if cfg.city_layout_source != &"a2":
		return generate_grid(p_seed, cfg)
	var p := CityA2Builder.make_plan(p_seed, cfg, CityView3D.CONFIG.city_rect, _corp_ids(), NeonCity.FIST_TERRITORY, NeonCity.HQ_LOTS,
		site_frame(), NeonCity.BORDER_BLEND, CityView3D.CONFIG.lot_bu)
	if p.fallback:
		var f := make_fixed()
		f.fallback = true
		f.failure = p.failure
		p = f
	p.city_seed = p_seed
	return p


## Forgets every cached plan and A2 subdivision (tests: a rebuild from scratch).
static func forget_all() -> void:
	_mutex.lock()
	_cache.clear()
	_mutex.unlock()
	CityA2Builder.forget()


static func _corp_ids() -> Array:
	var out: Array = []
	for t in NeonCity.TERRITORIES:
		if t["id"] != &"":
			out.append(t["id"])
	return out


## NA-12's grid generator run for `p_seed` (CityGenerator; the `city_layout_source` &"grid" fallback, step 2 removes it).
static func generate_grid(p_seed: int, cfg: CampaignConfigData) -> CityPlan:
	var frame := site_frame()
	var corp_ids := _corp_ids()
	var p := CityGenerator.generate(RngStreams.make_stream(p_seed, RngStreams.CITY_LAYOUT_STREAM), cfg, CityView3D.CONFIG.city_rect,
		corp_ids, NeonCity.FIST_TERRITORY, NeonCity.HQ_LOTS, frame)
	if p.fallback:
		var f := make_fixed()
		f.fallback = true
		f.attempts = p.attempts
		f.failure = p.failure
		p = f
	p.city_seed = p_seed
	return p


## Today's fixed city: NeonCity.TERRITORIES, the config's Site headings, no coast.
static func make_fixed() -> CityPlan:
	var p := CityPlan.new()
	p.fixed = true
	p.rect = CityView3D.CONFIG.city_rect
	for t in NeonCity.TERRITORIES:
		p.territories.append({"id": t["id"], "at": t["at"], "pull": t["pull"]})
		if t["id"] != &"":
			p.site_aim[t["id"]] = float(CityView3D.CONFIG.site_aim_deg.get(t["id"], 0.0))
			p.site_mirror[t["id"]] = bool(CityView3D.CONFIG.site_mirror.get(t["id"], false))
	return p


## The Site layout's frame (CityLayout.site_points_aimed's numbers) for the generator.
## NA-12 r2: with each corporation's Site layout (`uvs`, CityLayout.site_uvs, read from the content folder so any
## process mode gives the same city), so its Sites, not its whole layout box, keep off the other HQs.
static func site_frame() -> Dictionary:
	if _uvs.is_empty():
		for f in ResourceLoader.list_directory(CORP_DIR):
			if f.ends_with(".tres"):
				var c := load(CORP_DIR.path_join(f)) as CorporationData
				if c != null and c.city_grid != null:
					_uvs[c.id] = CityLayout.site_uvs(c)
	return {"right": CityLayout.RIGHT, "down": CityLayout.DOWN, "run_half": CityLayout.RUN_HALF, "cross_half": CityLayout.CROSS_HALF,
		"boss_gap": CityLayout.BOSS_GAP, "cross_offset": CityLayout.CROSS_OFFSET, "spread": maxf(CityView3D.CONFIG.site_spread, 0.1),
		"uvs": _uvs}


## The campaign config the game's plans are made with (the generator's and A2's numbers).
static func plan_config() -> CampaignConfigData:
	return _config()


static func _config() -> CampaignConfigData:
	if _gen_config == null:
		_gen_config = load(FIXED_CONFIG_PATH)
	return _gen_config
