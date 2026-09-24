extends Node
## RngService autoload: the campaign's named, seeded RNG streams (TECH_SPEC §4), a thin
## wrapper over the pure RngStreams core class. Core code receives the stream it needs
## as a parameter and never calls global randi()/randf().

const STREAM_NAMES: Array[StringName] = RngStreams.STREAM_NAMES

var _streams: RngStreams = RngStreams.new()

var campaign_seed: int:
	get:
		return _streams.root_seed


static func derive_seed(p_campaign_seed: int, stream_name: StringName) -> int:
	return RngStreams.derive_seed(p_campaign_seed, stream_name)


static func make_stream(p_campaign_seed: int, stream_name: StringName) -> RandomNumberGenerator:
	return RngStreams.make_stream(p_campaign_seed, stream_name)


## (Re)creates every named stream from `p_campaign_seed`.
func seed_campaign(p_campaign_seed: int) -> void:
	_streams.reseed(p_campaign_seed)


func is_seeded() -> bool:
	return _streams.is_seeded()


## The live stream `stream_name`; draws advance it in place.
func get_stream(stream_name: StringName) -> RandomNumberGenerator:
	return _streams.get_stream(stream_name)


func get_stream_state(stream_name: StringName) -> int:
	return _streams.get_stream_state(stream_name)


func set_stream_state(stream_name: StringName, state: int) -> void:
	_streams.set_stream_state(stream_name, state)


## Save representation; 64-bit values travel as decimal strings.
func to_dict() -> Dictionary:
	var d := _streams.to_dict()
	d["campaign_seed"] = d["root_seed"]
	return d


func from_dict(data: Dictionary) -> void:
	_streams = RngStreams.from_dict(data)
