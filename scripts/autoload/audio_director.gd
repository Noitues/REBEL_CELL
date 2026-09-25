extends Node
## AudioDirector autoload: placeholder audio generated in code (no asset files yet).
## Mechanical ratchet (GDD 10): every tick clicks, spins run down in decelerating clicks,
## nudges click once, flips clack; precision feedback sounds; and looping context music
## with Heat layers. Views call play_sfx()/play_music(); nothing here touches game state.

const MIX_RATE := 22050
const CONTEXTS := ["hq", "grid", "netrun", "combat", "raid", "boss", "solace_raid", "meridian_raid", "halcyon_raid", "orbital_raid", "rebel_cell"]
## Corporation-specific music (GDD 10): which context replaces a generic one.
const CORP_CONTEXTS := {
	&"solace": {"raid": "solace_raid"}, &"meridian": {"raid": "meridian_raid"}, &"halcyon": {"raid": "halcyon_raid"},
	&"orbital": {"raid": "orbital_raid"}, &"rebel_cell": {"hq": "rebel_cell", "grid": "rebel_cell"},
}

var _sfx: Dictionary = {}
var _music: Dictionary = {}
var _players: Array[AudioStreamPlayer] = []
var _music_player: AudioStreamPlayer
var _layer_player: AudioStreamPlayer
var current_context: String = ""
var heat_layers: int = 0
## Set by tests to skip actual playback (headless runs still generate the streams).
var muted: bool = false
## Log of what was played (tests read it).
var played: Array[String] = []


func _ready() -> void:
	_build_sfx()
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Master"
	add_child(_music_player)
	_layer_player = AudioStreamPlayer.new()
	add_child(_layer_player)
	for i in 8:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	if Engine.has_singleton("Settings") or has_node("/root/Settings"):
		get_node("/root/Settings").changed.connect(_apply_volumes)
	_apply_volumes()


# --- Public ----------------------------------------------------------------------------------

## Plays a named placeholder sound: tick, click, clack, latch, stutter, static, stamp, jack_in.
func play_sfx(name: String) -> void:
	played.append(name)
	if muted or not _sfx.has(name):
		return
	for p in _players:
		if not p.playing:
			p.stream = _sfx[name]
			p.play()
			return


## A spin of `ticks` ticks: a decelerating run of clicks.
func play_spin(ticks: int) -> void:
	var n := clampi(absi(ticks), 1, 12)
	played.append("spin:%d" % n)
	if muted:
		return
	var delay := 0.0
	for i in n:
		get_tree().create_timer(delay).timeout.connect(play_sfx.bind("tick"))
		delay += 0.04 + 0.03 * i


## Precision feedback (GDD 10): Perfect latch, Good click, Partial stutter, Miss static.
func play_precision(tier: int, is_miss_slice: bool) -> void:
	if is_miss_slice:
		play_sfx("static")
	elif tier == RC.PrecisionTier.PERFECT:
		play_sfx("latch")
	elif tier == RC.PrecisionTier.GOOD:
		play_sfx("click")
	else:
		play_sfx("stutter")


## Switches the looping context music (GDD 10 table). Same context = no restart.
func play_music(context: String, corporation_id: StringName = &"") -> void:
	context = context_for(context, corporation_id)
	if context == current_context:
		return
	current_context = context
	played.append("music:%s" % context)
	if muted:
		return
	if not _music.has(context):
		_music[context] = _make_music(context)
	_music_player.stream = _music[context]
	_music_player.play()
	_update_layer()


## The context actually played for `context` in a campaign against `corporation_id`.
static func context_for(context: String, corporation_id: StringName) -> String:
	return String(CORP_CONTEXTS.get(corporation_id, {}).get(context, context))


## Combat music gains a layer per Heat threshold band crossed (0-3).
func set_heat_layers(n: int) -> void:
	heat_layers = clampi(n, 0, 3)
	_update_layer()


func stop_music() -> void:
	current_context = ""
	_music_player.stop()
	_layer_player.stop()


# --- Generation -----------------------------------------------------------------------------

func _build_sfx() -> void:
	_sfx["tick"] = _wav(_click(0.012, 2600.0, 0.5))
	_sfx["click"] = _wav(_click(0.02, 1800.0, 0.7))
	_sfx["clack"] = _wav(_click(0.05, 700.0, 0.9))
	_sfx["latch"] = _wav(_tone_burst([880.0, 1320.0], 0.09, 0.8))
	_sfx["stutter"] = _wav(_stutter())
	_sfx["static"] = _wav(_noise(0.12, 0.6))
	_sfx["stamp"] = _wav(_click(0.08, 300.0, 1.0))
	_sfx["jack_in"] = _wav(_sweep(0.5, 200.0, 2400.0, 0.5))
	_sfx["alarm"] = _wav(_tone_burst([440.0, 466.0], 0.3, 0.6))


func _click(seconds: float, freq: float, gain: float) -> PackedFloat32Array:
	var n := int(seconds * MIX_RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	for i in n:
		var t := float(i) / MIX_RATE
		var env := exp(-t * 90.0)
		out[i] = gain * env * (sin(TAU * freq * t) * 0.6 + (_rand(i) - 0.5) * 0.8)
	return out


func _tone_burst(freqs: Array, seconds: float, gain: float) -> PackedFloat32Array:
	var n := int(seconds * MIX_RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	for i in n:
		var t := float(i) / MIX_RATE
		var env := minf(1.0, t * 200.0) * exp(-t * 18.0)
		var v := 0.0
		for f in freqs:
			v += sin(TAU * float(f) * t)
		out[i] = gain * env * v / freqs.size()
	return out


func _stutter() -> PackedFloat32Array:
	var n := int(0.09 * MIX_RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	for i in n:
		var t := float(i) / MIX_RATE
		var gate := 1.0 if fmod(t, 0.03) < 0.012 else 0.0
		out[i] = 0.6 * gate * sin(TAU * 900.0 * t) * exp(-t * 20.0)
	return out


func _noise(seconds: float, gain: float) -> PackedFloat32Array:
	var n := int(seconds * MIX_RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	for i in n:
		var t := float(i) / MIX_RATE
		out[i] = gain * (_rand(i) * 2.0 - 1.0) * exp(-t * 25.0)
	return out


func _sweep(seconds: float, f0: float, f1: float, gain: float) -> PackedFloat32Array:
	var n := int(seconds * MIX_RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	var phase := 0.0
	for i in n:
		var t := float(i) / MIX_RATE
		var f := lerpf(f0, f1, t / seconds)
		phase += TAU * f / MIX_RATE
		out[i] = gain * sin(phase) * (1.0 - t / seconds)
	return out


## A 4-second loop per context: lo-fi pad (hq/grid), dark ambient (netrun), synthwave
## arpeggio (combat), industrial pulses (raid), industrial synthwave (boss), hold music
## (solace_raid), slowed and wrong lo-fi (rebel_cell).
func _make_music(context: String) -> AudioStreamWAV:
	var seconds := 4.0
	var n := int(seconds * MIX_RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	var root := 110.0
	for i in n:
		var t := float(i) / MIX_RATE
		var v := 0.0
		match context:
			"hq", "grid":
				v = 0.25 * (sin(TAU * root * t) + 0.5 * sin(TAU * root * 1.5 * t) + 0.3 * sin(TAU * root * 2.0 * t))
				v *= 0.7 + 0.3 * sin(TAU * 0.5 * t)
			"netrun":
				v = 0.2 * (sin(TAU * root * 0.5 * t) + 0.4 * sin(TAU * root * 0.75 * t + sin(t)))
			"combat":
				var step := int(t * 8.0) % 4
				var f: float = root * [2.0, 3.0, 2.5, 4.0][step]
				v = 0.22 * (sign(sin(TAU * f * t)) * 0.4 + sin(TAU * f * t) * 0.6) * (1.0 - fmod(t * 8.0, 1.0) * 0.5)
			"raid":
				var beat := fmod(t * 2.0, 1.0)
				v = 0.3 * (_rand(i) * 2.0 - 1.0) * exp(-beat * 12.0) + 0.15 * sin(TAU * 55.0 * t)
			"boss":
				var step2 := int(t * 6.0) % 4
				var f2: float = root * [1.0, 1.0, 1.5, 1.33][step2]
				v = 0.25 * sign(sin(TAU * f2 * t)) * exp(-fmod(t * 6.0, 1.0) * 3.0) + 0.1 * (_rand(i) * 2.0 - 1.0) * exp(-fmod(t * 3.0, 1.0) * 10.0)
			"solace_raid":
				v = 0.2 * (sin(TAU * 330.0 * t) + 0.5 * sin(TAU * 415.0 * t) + 0.5 * sin(TAU * 494.0 * t)) * (0.6 + 0.4 * sin(TAU * 0.25 * t))
			"meridian_raid":
				var pulse := fmod(t * 3.0, 1.0)
				v = 0.22 * sign(sin(TAU * 82.4 * t)) * exp(-pulse * 6.0) + 0.1 * sin(TAU * 164.8 * t) * (1.0 - pulse)
			"halcyon_raid":
				v = 0.18 * (sin(TAU * 440.0 * t) * float(int(t * 2.0) % 2 == 0) + 0.6 * sin(TAU * 220.0 * t)) * (0.5 + 0.5 * sin(TAU * 0.5 * t))
			"orbital_raid":
				v = 0.2 * sin(TAU * (root * 2.0 + 40.0 * sin(TAU * 0.25 * t)) * t) + 0.08 * (_rand(i) * 2.0 - 1.0) * exp(-fmod(t * 4.0, 1.0) * 8.0)
			"rebel_cell":
				v = 0.25 * (sin(TAU * root * 0.98 * t) + 0.5 * sin(TAU * root * 1.48 * t)) * (0.6 + 0.4 * sin(TAU * 0.3 * t + sin(t * 2.0)))
			_:
				v = 0.15 * sin(TAU * root * t)
		out[i] = v
	var wav := _wav(out)
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	wav.loop_end = n
	return wav


func _update_layer() -> void:
	if muted:
		return
	if heat_layers <= 0 or current_context != "combat":
		_layer_player.stop()
		return
	if not _music.has("layer"):
		_music["layer"] = _make_music("raid")
	_layer_player.stream = _music["layer"]
	_layer_player.volume_db = linear_to_db(clampf(0.2 * heat_layers, 0.0, 1.0)) + _music_db()
	if not _layer_player.playing:
		_layer_player.play()


func _wav(samples: PackedFloat32Array) -> AudioStreamWAV:
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = MIX_RATE
	wav.stereo = false
	var bytes := PackedByteArray()
	bytes.resize(samples.size() * 2)
	for i in samples.size():
		var v := int(clampf(samples[i], -1.0, 1.0) * 32767.0)
		bytes.encode_s16(i * 2, v)
	wav.data = bytes
	return wav


## Deterministic pseudo-noise (no global RNG; audio is not game state anyway).
static func _rand(i: int) -> float:
	var x := (i * 1103515245 + 12345) & 0x7fffffff
	return float(x % 10000) / 10000.0


func _music_db() -> float:
	var s := get_node_or_null("/root/Settings")
	return linear_to_db(maxf(0.0001, s.music_volume if s != null else 0.6))


func _apply_volumes() -> void:
	var s := get_node_or_null("/root/Settings")
	var sfx: float = s.sfx_volume if s != null else 0.8
	_music_player.volume_db = _music_db()
	for p in _players:
		p.volume_db = linear_to_db(maxf(0.0001, sfx))
	_update_layer()
