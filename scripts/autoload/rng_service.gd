extends Node
## RngService autoload: named, seeded RNG streams derived from one campaign seed
## (TECH_SPEC §4). Core code receives the stream it needs as a parameter and never
## calls global randi()/randf(). Streams are independent: drawing from one never
## changes the sequence of another.
##
## Serialisation: RandomNumberGenerator.state is an unsigned 64-bit value and JSON
## only round-trips integers exactly up to 2^53, so to_dict() stores seeds and
## states as decimal strings.

const STREAM_NAMES: Array[StringName] = [&"map", &"combat", &"rewards", &"events", &"raids"]

var campaign_seed: int = 0
var _streams: Dictionary = {}


## Derives the seed of one stream from the campaign seed and the stream name.
## hash() of an Array holding an int and a StringName is stable across runs and platforms.
static func derive_seed(p_campaign_seed: int, stream_name: StringName) -> int:
	return hash([p_campaign_seed, stream_name])


## Creates a fresh RandomNumberGenerator for `stream_name` under `p_campaign_seed`.
static func make_stream(p_campaign_seed: int, stream_name: StringName) -> RandomNumberGenerator:
	var rng := RandomNumberGenerator.new()
	rng.seed = derive_seed(p_campaign_seed, stream_name)
	return rng


## (Re)creates every named stream from `p_campaign_seed`.
func seed_campaign(p_campaign_seed: int) -> void:
	campaign_seed = p_campaign_seed
	_streams.clear()
	for stream_name in STREAM_NAMES:
		_streams[stream_name] = make_stream(p_campaign_seed, stream_name)


## True once seed_campaign() (or from_dict()) has run.
func is_seeded() -> bool:
	return not _streams.is_empty()


## Returns the live stream `stream_name`. The caller may draw from it; the state
## advances in place so later draws continue the sequence.
func get_stream(stream_name: StringName) -> RandomNumberGenerator:
	if not _streams.has(stream_name):
		push_error("RngService: unknown or unseeded stream '%s'." % stream_name)
		return null
	return _streams[stream_name]


## Snapshot of one stream's state, for checkpoints (combat rewind restores only `combat`).
func get_stream_state(stream_name: StringName) -> int:
	var rng := get_stream(stream_name)
	return rng.state if rng != null else 0


## Restores one stream's state from a snapshot taken with get_stream_state().
func set_stream_state(stream_name: StringName, state: int) -> void:
	var rng := get_stream(stream_name)
	if rng != null:
		rng.state = state


## Save representation. All 64-bit values are decimal strings (see file comment).
func to_dict() -> Dictionary:
	var streams := {}
	for stream_name in STREAM_NAMES:
		if _streams.has(stream_name):
			var rng: RandomNumberGenerator = _streams[stream_name]
			streams[String(stream_name)] = {"seed": str(rng.seed), "state": str(rng.state)}
	return {"campaign_seed": str(campaign_seed), "streams": streams}


## Restores every stream from to_dict() output. Streams missing from `data` are
## recreated from the campaign seed.
func from_dict(data: Dictionary) -> void:
	seed_campaign(int(String(data.get("campaign_seed", "0"))))
	var streams: Dictionary = data.get("streams", {})
	for stream_name in STREAM_NAMES:
		var entry: Variant = streams.get(String(stream_name))
		if entry is Dictionary:
			var rng: RandomNumberGenerator = _streams[stream_name]
			rng.seed = int(String(entry.get("seed", str(rng.seed))))
			rng.state = int(String(entry.get("state", str(rng.state))))
