class_name EntryBeats
extends RefCounted
## NA-25 (PIPELINE_SPEC 10): the street entry's beat table and its staging rules, pure. The animatic's beats are
## 3a terminal, 3b rain, 3c collapse (the HQ side, `JackSequence`), then 3d dive, 4 REVEAL, 5 MARK (+ hold), 6 ZOOM
## (+ settle) on the street (`EntryCover`); beat 7 CHOOSE is the player's. Every time is a `ui_motion.tres` entry
## `entry_<beat>`; a beat that does not play (headless, reduce effects, the entry switched off) takes 0 s, so the whole
## table collapses to its end state with no timer pending. Jack-out plays the same table backwards. No Nodes, no state.

const PREFIX := "entry_"
## The HQ side's beats (`JackSequence`, over the HQ page).
const HQ_BEATS: Array[StringName] = [&"terminal", &"rain", &"collapse"]
## The street side's beats (`EntryCover`), in animatic order.
const STREET_BEATS: Array[StringName] = [&"dive", &"reveal", &"mark", &"mark_hold", &"zoom", &"zoom_settle"]
## NA-25b (ART_BIBLE 4.1, one camera; only target and zoom change): the Grid / Route toggle is one camera ease between the Grid's framing
## (the HQ page pose) and the street DECISION, rooms already open: no dive, REVEAL or MARK beats.
const ZOOM_BEATS: Array[StringName] = [&"toggle"]
## The animatic's start of beat 7 (CHOOSE), seconds from the HQ idle's end; with the table above it is the whole entry.
const SELECT_HOLD := &"entry_select_hold"


## The `ui_motion.tres` id of `beat`.
static func motion_id(beat: StringName) -> StringName:
	return StringName(PREFIX + String(beat))


## Seconds `beat` plays now: its entry's length when it animates, else 0 (headless, reduce effects, switched off).
static func beat_seconds(beat: StringName) -> float:
	return Motion.seconds_live(motion_id(beat))


## The table of `beats` as `[{beat, start, end}]` in play order. `reverse` plays them backwards (the same lengths, last
## beat first). `live` false takes each entry's own length whatever the display says (the animatic check reads it so).
static func table(beats: Array, reverse: bool = false, live: bool = true) -> Array[Dictionary]:
	var order: Array = beats.duplicate()
	if reverse:
		order.reverse()
	var out: Array[Dictionary] = []
	var t := 0.0
	for b: StringName in order:
		var s := beat_seconds(b) if live else Motion.seconds(motion_id(b))
		out.append({"beat": b, "start": t, "end": t + s})
		t += s
	return out


## The table's length (s).
static func total(tbl: Array[Dictionary]) -> float:
	return 0.0 if tbl.is_empty() else float(tbl[tbl.size() - 1]["end"])


## Where time `t` falls in `tbl`: `{index, beat, u, done}`; `u` is the share (0..1) of the beat elapsed, `done` true at or
## past the end (index = the last beat then, u = 1). An empty table is done at once.
static func at(tbl: Array[Dictionary], t: float) -> Dictionary:
	if tbl.is_empty():
		return {"index": -1, "beat": &"", "u": 1.0, "done": true}
	for i in tbl.size():
		var row: Dictionary = tbl[i]
		if t < float(row["end"]):
			var span := float(row["end"]) - float(row["start"])
			return {"index": i, "beat": row["beat"], "u": clampf((t - float(row["start"])) / maxf(span, 0.0001), 0.0, 1.0), "done": false}
	return {"index": tbl.size() - 1, "beat": tbl[tbl.size() - 1]["beat"], "u": 1.0, "done": true}


## The forward timeline's time for playing time `t` of a run of `total_s`: reversed playback reads the same timeline back.
static func forward_time(total_s: float, t: float, reverse: bool) -> float:
	return clampf(total_s - t if reverse else t, 0.0, total_s)


# --- REVEAL (beat 4) -----------------------------------------------------------------------------------------

## Layer `layer` (1..`layers`) of the REVEAL over `reveal_s`: `{write_start, write_end, up_start, up_end}` (s into the beat).
## The first wall comes after `entry_reveal_lead`; the layers follow evenly so the last one ends with the beat.
static func layer_times(layer: int, layers: int, reveal_s: float) -> Dictionary:
	var lead := Motion.seconds_live(&"entry_reveal_lead")
	var write := Motion.seconds_live(&"entry_reveal_write")
	var up := Motion.seconds_live(&"entry_reveal_dissolve")
	var step := 0.0
	if layers > 1:
		step = maxf(0.0, (reveal_s - lead - write - up) / float(layers - 1))
	var w0 := lead + float(maxi(layer, 1) - 1) * step
	return {"write_start": w0, "write_end": w0 + write, "up_start": w0 + write, "up_end": w0 + write + up}


## How written-on the links into layer `layer` are at `s` seconds into the REVEAL (0..1).
static func write_k(layer: int, layers: int, reveal_s: float, s: float) -> float:
	var lt := layer_times(layer, layers, reveal_s)
	return _span_k(s, float(lt["write_start"]), float(lt["write_end"]))


## How far up layer `layer`'s rooms have come (0..1).
static func up_k(layer: int, layers: int, reveal_s: float, s: float) -> float:
	var lt := layer_times(layer, layers, reveal_s)
	return _span_k(s, float(lt["up_start"]), float(lt["up_end"]))


# --- MARK (beat 5) -------------------------------------------------------------------------------------------

## The scale of the `index`-th sticker (layer order, then id) `s` seconds into MARK: 0 before its slap, then the slap's start
## scale easing to 1.
static func slap_scale(index: int, s: float) -> float:
	var start := float(index) * Motion.seconds_live(&"entry_mark_stagger")
	if s < start:
		return 0.0
	var k := _span_k(s, start, start + Motion.seconds_live(&"entry_mark_slap"))
	return lerpf(Motion.amplitude(&"entry_mark_slap"), 1.0, NetrunCameraRig.ease(k))


## True once the rings and room frames show at `s` seconds into MARK.
static func rings_on(s: float) -> bool:
	return s >= (Motion.delay_of(&"entry_mark_rings") if Motion.live(&"entry_mark_rings") else 0.0)


## True once the option numbers and the token show.
static func numbers_on(s: float) -> bool:
	return s >= (Motion.delay_of(&"entry_mark_numbers") if Motion.live(&"entry_mark_numbers") else 0.0)


## True once the red TARGET circle and word show (last).
static func target_on(s: float) -> bool:
	return s >= (Motion.delay_of(&"entry_mark_target") if Motion.live(&"entry_mark_target") else 0.0)


static func _span_k(s: float, a: float, b: float) -> float:
	if b <= a:
		return 1.0 if s >= a else 0.0
	return clampf((s - a) / (b - a), 0.0, 1.0)
