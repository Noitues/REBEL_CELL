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
## The heading (degrees) each corporation's Site layout is turned round its HQ, and whether it
## is mirrored (CityLayout.site_points_aimed).
var site_aim: Dictionary = {}
var site_mirror: Dictionary = {}
## The coast, or {} (no sea): {"side": 0 west (low i) / 1 east / 2 north (low j) / 3 south,
## "depth", "amp", "wavelength", "phase"} in lots from `rect`'s edge.
var coast: Dictionary = {}
## The city rect the coast is measured from (lots).
var rect: Rect2i = Rect2i()

const FIXED_CONFIG_PATH := "res://content/config/campaign_config.tres"

static var _cache: Dictionary = {}
static var _mutex: Mutex = Mutex.new()
static var _gen_config: CampaignConfigData = null


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


## How far point (x, y) (lots) lies inland of the coast (negative: in the sea); INF without one.
func land_depth(x: float, y: float) -> float:
	if coast.is_empty():
		return INF
	var side := int(coast["side"])
	var along := y if side < 2 else x
	var shore := float(coast["depth"]) + float(coast["amp"]) * sin(TAU * along / float(coast["wavelength"]) + float(coast["phase"]))
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
	return not coast.is_empty() and land_depth(i + 0.5, j + 0.5) < 0.0


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
	return {"layout_seed": ArtSeed.u64_str(city_seed), "fixed": fixed, "fallback": fallback, "territories": terr,
		"site_aim": aims, "site_mirror": mirrors, "coast": coast.duplicate(),
		"rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y]}


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


## A fresh generator run for `p_seed` with config `cfg` (not cached): the RNG is the seed's own
## named stream (RngStreams.make_stream(p_seed, CITY_LAYOUT_STREAM)), never a campaign stream.
static func generate(p_seed: int, cfg: CampaignConfigData) -> CityPlan:
	var frame := site_frame()
	var corp_ids: Array = []
	for t in NeonCity.TERRITORIES:
		if t["id"] != &"":
			corp_ids.append(t["id"])
	var p := CityGenerator.generate(RngStreams.make_stream(p_seed, RngStreams.CITY_LAYOUT_STREAM), cfg, CityView3D.CONFIG.city_rect,
		corp_ids, NeonCity.FIST_TERRITORY, NeonCity.HQ_LOTS, frame)
	if p.fallback:
		var f := make_fixed()
		f.fallback = true
		f.attempts = p.attempts
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
static func site_frame() -> Dictionary:
	return {"right": CityLayout.RIGHT, "down": CityLayout.DOWN, "run_half": CityLayout.RUN_HALF, "cross_half": CityLayout.CROSS_HALF,
		"boss_gap": CityLayout.BOSS_GAP, "cross_offset": CityLayout.CROSS_OFFSET, "spread": maxf(CityView3D.CONFIG.site_spread, 0.1)}


static func _config() -> CampaignConfigData:
	if _gen_config == null:
		_gen_config = load(FIXED_CONFIG_PATH)
	return _gen_config
