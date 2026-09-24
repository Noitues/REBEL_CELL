class_name RngStreams
extends RefCounted
## Named, seeded RNG streams derived from one seed (TECH_SPEC 4), as pure data for the
## core. RngService (autoload) wraps one of these for the campaign; a netrun owns its
## own set derived from the run seed so map, combat, rewards and events never interfere.
##
## 64-bit seeds and states are serialised as decimal strings (JSON keeps only 2^53).

const STREAM_NAMES: Array[StringName] = [&"map", &"combat", &"rewards", &"events", &"raids"]

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
