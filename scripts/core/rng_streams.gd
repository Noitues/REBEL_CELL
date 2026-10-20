class_name RngStreams
extends RefCounted
## Named, seeded RNG streams derived from one seed (TECH_SPEC 4), as pure data for the
## core. RngService (autoload) wraps one of these for the campaign; a netrun owns its
## own set derived from the run seed so map, combat, rewards and events never interfere.
##
## 64-bit seeds and states are serialised as decimal strings (JSON keeps only 2^53).

const STREAM_NAMES: Array[StringName] = [&"map", &"combat", &"rewards", &"events", &"raids"]
## Plan 2 NA-12: named streams made on demand by `make_stream`, never part of the saved set
## (so a city never advances a gameplay stream): the campaign's city seed from its campaign
## seed (`CITY_SEED_STREAM`), and a city's layout from its city seed (`CITY_LAYOUT_STREAM`).
const CITY_SEED_STREAM: StringName = &"city_seed"
const CITY_LAYOUT_STREAM: StringName = &"city_layout"
## Plan 2 WH-10: the Solace HQ ladder's room kinds, made on demand from the run seed.
const HQ_GRAPH_STREAM: StringName = &"hq_graph"
## CITY-A2: a city's blocks, lots and buildings inside the A2 plan (CityA2Builder.lots_for), from its city seed.
const CITY_BLOCKS_STREAM: StringName = &"city_blocks"
## CITY-A2 step 2: the A2 terrain's noise lattice (CityA2Terrain), from the config's fixed terrain seed (no campaign seed).
const CITY_TERRAIN_STREAM: StringName = &"city_terrain"
## Halcyon v2: the Eye's first octant, drawn once at campaign start and stored.
const EYE_START_STREAM: StringName = &"eye_start"

var root_seed: int = 0
var _streams: Dictionary = {}


static func derive_seed(p_root_seed: int, stream_name: StringName) -> int:
	return hash([p_root_seed, stream_name])


static func make_stream(p_root_seed: int, stream_name: StringName) -> RandomNumberGenerator:
	var rng := RandomNumberGenerator.new()
	rng.seed = derive_seed(p_root_seed, stream_name)
	return rng


static func seeded(p_root_seed: int) -> RngStreams:
	var s := RngStreams.new()
	s.reseed(p_root_seed)
	return s


func reseed(p_root_seed: int) -> void:
	root_seed = p_root_seed
	_streams.clear()
	for stream_name in STREAM_NAMES:
		_streams[stream_name] = make_stream(p_root_seed, stream_name)


func is_seeded() -> bool:
	return not _streams.is_empty()


func get_stream(stream_name: StringName) -> RandomNumberGenerator:
	if not _streams.has(stream_name):
		push_error("RngStreams: unknown or unseeded stream '%s'." % stream_name)
		return null
	return _streams[stream_name]


func get_stream_state(stream_name: StringName) -> int:
	var rng := get_stream(stream_name)
	return rng.state if rng != null else 0


func set_stream_state(stream_name: StringName, state: int) -> void:
	var rng := get_stream(stream_name)
	if rng != null:
		rng.state = state


func to_dict() -> Dictionary:
	var streams := {}
	for stream_name in STREAM_NAMES:
		if _streams.has(stream_name):
			var rng: RandomNumberGenerator = _streams[stream_name]
			streams[String(stream_name)] = {"seed": str(rng.seed), "state": str(rng.state)}
	return {"root_seed": str(root_seed), "streams": streams}


static func from_dict(data: Dictionary) -> RngStreams:
	var s := RngStreams.new()
	s.reseed(int(String(data.get("root_seed", data.get("campaign_seed", "0")))))
	var streams: Dictionary = data.get("streams", {})
	for stream_name in STREAM_NAMES:
		var entry: Variant = streams.get(String(stream_name))
		if entry is Dictionary:
			var rng: RandomNumberGenerator = s._streams[stream_name]
			rng.seed = int(String(entry.get("seed", str(rng.seed))))
			rng.state = int(String(entry.get("state", str(rng.state))))
	return s
