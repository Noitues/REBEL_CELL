class_name MainframeSign
extends Control
## ART-9 4A (ART_BIBLE v2 §4.10, LOCKED v4): the MAINFRAME shop's vertical neon sign on the F1b
## Tenement facade: filled neon tubes (saturated body, thin hot centre line, unlit tubes as dark
## glass) on a circuit-board plate whose traces belong to the letters and light with them. Normal
## = blue; the takeover plays in the Cell's red: NO -> MoRE -> MAN, I AM -> AI, I AM -> NO -> MAN
## (round 33 `mainframe_sequence_v4`, `iamai_sequence_v4`, `iamnoman_sequence_v4`).
##
## Drawn from round 33's own renders, baked per letter (tools/art_bake/mainframe_sign_bake.py):
## the dark plate, then one light layer per tube added at its level (the frame, the rails, each
## letter in blue and red, the two A's lit only as an "o"), and the snapped glass and soot of the
## dead letters taken away. The sign is the diegetic name of the shop (a store name, never
## translated, like any sign in the world). Decoration: it changes no state.
##
## Motion: the tubes warm up on entering (`mainframe_sign_warmup`, each striking at its own
## hash-picked moment within `mainframe_sign_strike`, flickering for `mainframe_sign_flicker`),
## the traces light after them (`mainframe_trace`), then after `mainframe_takeover`'s delay the
## takeover plays once per visit (its frames at `amplitude` per second). Reduce effects and
## headless show the lit blue sign (the end state); a press that ends a motion lands it.

signal light_changed

const BASE := preload("res://assets/backdrops/shop/sign_base.png")
const LAYERS := preload("res://assets/backdrops/shop/sign_layers.png")
const TABLE := "res://assets/backdrops/shop/sign_layers.json"
## The letters (M0 A1 I2 N3 F4 R5 A6 M7 E8) and the two A's that light as an "o".
const LETTERS := 9
const A_TOPS: Array[int] = [1, 6]
## Takeover words as lit letters ([index, "o"] = only the A's top half), per sequence (LOCKED).
const SEQUENCES := {
	&"no_more_man": [["NO", [3, [6, "o"]]], ["MoRE", [0, [1, "o"], 5, 8]], ["MAN", [0, 1, 3]]],
	&"i_am_ai": [["I AM", [2, 6, 7]], ["AI", [1, 2]]],
	&"i_am_no_man": [["I AM", [2, 6, 7]], ["NO", [3, [6, "o"]]], ["MAN", [0, 1, 3]]],
}
const SEQUENCE_ORDER: Array[StringName] = [&"no_more_man", &"i_am_ai", &"i_am_no_man"]
## Round 33's frame plan (frames at the takeover's rate): the sign stutters into red, holds the
## Cell's red, its dead letters drop out, it goes dark, each word holds then stutters into the
## next (twice round), and the old sign flashes back before the blue returns.
const F_STUTTER := 10
const F_RED := 8
const F_DROP := 4
const F_DARK := 2
const F_WORD := 9
const F_BETWEEN := 3
const LOOPS := 2
const F_FLASH := 3
## Stutter: the share of tubes lit, half lit (a frame's draw, by hash).
const STUTTER_ON := 0.45
const STUTTER_HALF := 0.7
## A word's tube that dips on a hum frame, and how often a word hums.
const HUM_FRAMES: Array[int] = [3, 6]
const HUM_CHANCE := 0.6
## Takeover light on the street: the words keep about a tenth of the spill (bible §4.10).
const WORD_SPILL := 0.09
## The rails light at this share of the brightest letter when the frame is dark.
const RAIL_SHARE := 0.8
## ANIM-R3 A7: an unlit tube's level during the warm-up, the flicker steps and their lit chance.
const TUBE_OFF_ALPHA := 0.12
const WARM_STEPS := 14
const FLICKER_ON := 0.6
## Tube ids for the warm-up hash: the frame, then each letter (1..9).
const TUBE_BORDER := 0

## Warm-up progress (1 = lit, the rest state) and the traces' (ANIM-6).
var warm: float = 1.0
var trace: float = 1.0
## Which takeover this sign plays (SEQUENCE_ORDER index; the shop picks it per visit).
var sequence_index: int = 0
var _tweens: Array[Tween] = []
var _strike: float = 0.0
var _flicker: float = 0.0
## The takeover playing: its frames and the time into it (-1 = not playing).
var _frames: Array[Dictionary] = []
var _t: float = -1.0
var _wait: float = -1.0
## Levels shown now (see `_state`).
var _now: Dictionary = {}
var _adds: Control
var _subs: Control
static var _table: Dictionary = {}


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = canvas_size() * PLATE_SCALE
	MotionSkip.register_passive(self)
	_subs = _layer(CanvasItemMaterial.BLEND_MODE_SUB, &"sub")
	_adds = _layer(CanvasItemMaterial.BLEND_MODE_ADD, &"add")
	_now = blue_state(1.0)
	set_process(false)


## The sign canvas is drawn at this scale of its baked size by default (the plate lands on the
## facade's plate at 1280x720).
const PLATE_SCALE := 2.0 / 3.0


func _layer(blend: int, mode: StringName) -> Control:
	var c := Control.new()
	c.name = "Light_%s" % mode
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var m := CanvasItemMaterial.new()
	m.blend_mode = blend
	c.material = m
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.draw.connect(_draw_layers.bind(c, mode))
	add_child(c)
	return c


## The baked table: canvas size, plate rect and layers (name -> {rect, at, mode}).
static func table() -> Dictionary:
	if _table.is_empty():
		var j := load(TABLE) as JSON
		_table = j.data if j != null and j.data is Dictionary else {}
	return _table


## The baked canvas size (px).
static func canvas_size() -> Vector2:
	var c: Array = table().get("canvas", [250, 751])
	return Vector2(float(c[0]), float(c[1]))


## The plate's rect on the baked canvas (px).
static func plate_rect() -> Rect2:
	var p: Array = table().get("plate", [0, 0, 1, 1])
	return Rect2(float(p[0]), float(p[1]), float(p[2]), float(p[3]))


## Places the sign so its plate covers `plate` (the facade's plate, in the parent's space).
func fit_plate(plate: Rect2) -> void:
	var src := plate_rect()
	var k := plate.size.x / src.size.x
	size = canvas_size() * k
	position = plate.position - src.position * k


# ------------------------------------------------------------------ states (level tables)

## Every tube at `level` in blue (the normal sign).
static func blue_state(level: float) -> Dictionary:
	var s := _empty()
	s["blue_frame"] = level
	for i in LETTERS:
		s["blue_%d" % i] = level
	return s


## Every tube at `level` in the Cell's red.
static func red_state(level: float) -> Dictionary:
	var s := _empty()
	s["red"] = 1.0
	s["red_frame"] = level
	for i in LETTERS:
		s["red_%d" % i] = level
	return s


## Word `wi` of `seq` lit in red, the dead letters snapped and sooted, the frame dark.
static func word_state(seq: StringName, wi: int, level: float = 1.0) -> Dictionary:
	var s := _empty()
	s["red"] = 1.0
	_break_dead(s, seq)
	var word: Array = (SEQUENCES[seq] as Array)[wi][1]
	for it in word:
		if it is Array:
			s["red_%do" % int(it[0])] = level
		else:
			s["red_%d" % int(it)] = level
	return s


static func _empty() -> Dictionary:
	return {"red": 0.0, "soot": 0.0}


## The letters `seq` never lights (they get snapped tubes and soot).
static func dead_letters(seq: StringName) -> Array[int]:
	var used := {}
	for w: Array in SEQUENCES[seq]:
		for it in w[1]:
			used[int(it[0]) if it is Array else int(it)] = true
	var out: Array[int] = []
	for i in LETTERS:
		if not used.has(i):
			out.append(i)
	return out


static func _break_dead(s: Dictionary, seq: StringName) -> void:
	s["soot"] = 1.0
	for i in dead_letters(seq):
		s["brk_%d" % i] = 1.0


## The level of every light layer in state `s` (rails follow the frame or the brightest letter).
static func layer_levels(s: Dictionary) -> Dictionary:
	var out := {}
	var red := float(s.get("red", 0.0))
	out["glass_red"] = red
	out["glass_blue"] = red
	var brightest := {"blue": 0.0, "red": 0.0}
	for k: String in s:
		if k == "red":
			continue
		out[k] = float(s[k])
		for pal in ["blue", "red"]:
			if k.begins_with(pal + "_") and not k.ends_with("frame"):
				brightest[pal] = maxf(brightest[pal], float(s[k]))
	for pal in ["blue", "red"]:
		out["%s_rail" % pal] = maxf(float(s.get("%s_frame" % pal, 0.0)), RAIL_SHARE * float(brightest[pal]))
	return out


## The blue and red light this state throws on the street (0..1 each; MainframeFacade).
static func spill_of(s: Dictionary) -> Vector2:
	var b := float(s.get("blue_frame", 0.0))
	var r := float(s.get("red_frame", 0.0))
	var word := 0.0
	for i in LETTERS:
		b += float(s.get("blue_%d" % i, 0.0))
		r += float(s.get("red_%d" % i, 0.0))
	for i in A_TOPS:
		word += float(s.get("red_%do" % i, 0.0))
	b /= LETTERS + 1.0
	r /= LETTERS + 1.0
	if float(s.get("red_frame", 0.0)) <= 0.0 and r > 0.0:
		r = minf(1.0, (r * (LETTERS + 1.0) + word) / 4.0) * WORD_SPILL  # a word: its letters' tenth
	return Vector2(b, r)


## The light the sign throws now (x blue, y red).
func spill() -> Vector2:
	return spill_of(_now)


## The levels shown now (tests).
func shown_state() -> Dictionary:
	return _now.duplicate()


# ------------------------------------------------------------------ the takeover's frames

## Round 33's takeover for `seq` as frames of tube levels (deterministic: stutters by hash).
static func takeover_frames(seq: StringName) -> Array[Dictionary]:
	var fr: Array[Dictionary] = []
	var words: Array = SEQUENCES[seq]
	var dead := dead_letters(seq)
	for i in F_STUTTER:  # the takeover hits the controller: blue and red stutter
		var s := _empty()
		var red := _h(seq, i, 99) < 0.5
		s["red"] = 1.0 if red else 0.0
		var pal := "red" if red else "blue"
		for k in LETTERS:
			var r := _h(seq, i, k)
			s["%s_%d" % [pal, k]] = 1.0 if r < STUTTER_ON else (0.0 if r < STUTTER_HALF else 0.5)
		s["%s_frame" % pal] = 1.0 if _h(seq, i, 77) < 0.5 else 0.0
		fr.append(s)
	for i in F_RED:  # the Cell's red, fully lit
		fr.append(red_state(1.0))
	for i in F_DROP:  # the dead letters drop out first, then the frame
		var s := red_state(1.0)
		var n_off := int(ceil(float(dead.size()) * (i + 1) / F_DROP))
		for j in n_off:
			s["red_%d" % dead[j]] = 0.0
			s["brk_%d" % dead[j]] = 1.0
		s["soot"] = 1.0
		s["red_frame"] = 0.5 if i < 2 else 0.0
		fr.append(s)
	for i in F_DARK:
		var s := _empty()
		s["red"] = 1.0
		_break_dead(s, seq)
		fr.append(s)
	for lp in LOOPS:
		for wi in words.size():
			for j in F_WORD:
				var s := word_state(seq, wi)
				if HUM_FRAMES.has(j) and _h(seq, lp * 100 + wi * 10 + j, 55) < HUM_CHANCE:
					var word: Array = words[wi][1]
					var hum: Variant = word[int(_h(seq, lp * 100 + wi * 10 + j, 56) * word.size()) % word.size()]
					s["red_%do" % int(hum[0]) if hum is Array else "red_%d" % int(hum)] = 0.0
				fr.append(s)
			for j in F_BETWEEN:  # stutter between words
				var s := word_state(seq, wi, _h(seq, lp * 100 + wi * 10 + j, 57) * 0.6 + 0.3)
				var nxt := word_state(seq, (wi + 1) % words.size())
				for k: String in nxt:
					if k.begins_with("red_") and _h(seq, lp * 100 + wi * 10 + j, k.hash()) < 0.35:
						s[k] = nxt[k]
				fr.append(s)
	for lvl in [1.0, 0.0, 0.8]:  # the old sign flickers back for a moment
		fr.append(red_state(lvl))
	return fr


static func _h(seq: StringName, i: int, k: int) -> float:
	return float(absi(hash([String(seq), i, k, 33])) % 1000) / 1000.0


# ------------------------------------------------------------------ motion

## MotionSkip (ANIM-R6 D7): the sign is warming up.
func motion_running() -> bool:
	return warming()


## MotionSkip (ANIM-R6 D7): the sign lit at once.
func complete_motion() -> void:
	settle()


## Warms the sign up from dark (entering the Mainframe), then waits for the takeover.
func warm_up() -> void:
	settle()
	_strike = strike_share()
	_flicker = flicker_share()
	if Motion.live(&"mainframe_sign_warmup"):
		var e := Motion.entry(&"mainframe_sign_warmup")
		warm = 0.0
		var tw := create_tween()
		tw.tween_method(func(v: float) -> void:
			warm = v
			_refresh(), 0.0, 1.0, Motion.seconds(&"mainframe_sign_warmup")).set_delay(Motion.delay_of(&"mainframe_sign_warmup")).set_ease(e.ease).set_trans(e.trans)
		_tweens.append(tw)
	if Motion.live(&"mainframe_trace"):
		var te := Motion.entry(&"mainframe_trace")
		trace = 0.0
		var tt := create_tween()
		tt.tween_method(func(v: float) -> void:
			trace = v
			_refresh(), 0.0, 1.0, Motion.seconds(&"mainframe_trace")).set_delay(Motion.delay_of(&"mainframe_trace")).set_ease(te.ease).set_trans(te.trans)
		_tweens.append(tt)
	if Motion.live(&"mainframe_takeover"):
		_wait = Motion.delay_of(&"mainframe_takeover")
		set_process(true)
	_refresh()


## Ends the warm-up at once (lit) and stops a takeover (the blue sign: the end state).
func settle() -> void:
	for tw in _tweens:
		if tw != null and tw.is_valid():
			tw.kill()
	_tweens.clear()
	warm = 1.0
	trace = 1.0
	_t = -1.0
	_wait = -1.0
	_frames.clear()
	set_process(false)
	_refresh()


## True while the sign is still warming up.
func warming() -> bool:
	return warm < 1.0 or trace < 1.0


## True while the takeover plays (ambient: never a motion a press must end).
func taking_over() -> bool:
	return _t >= 0.0


## Starts the takeover now (the lab, captures); it plays only where motion plays.
func take_over() -> void:
	if not Motion.live(&"mainframe_takeover"):
		return
	_frames = takeover_frames(SEQUENCE_ORDER[posmod(sequence_index, SEQUENCE_ORDER.size())])
	_t = 0.0
	_wait = -1.0
	set_process(true)


## Shows takeover frame `i` and holds it (captures).
func show_frame(i: int) -> void:
	_frames = takeover_frames(SEQUENCE_ORDER[posmod(sequence_index, SEQUENCE_ORDER.size())])
	set_process(false)
	_t = -1.0
	_now = _frames[clampi(i, 0, _frames.size() - 1)]
	_redraw_all()


func _process(delta: float) -> void:
	if _wait >= 0.0:
		if warming():
			return
		_wait -= delta
		if _wait < 0.0:
			take_over()
		return
	if _t < 0.0:
		set_process(false)
		return
	_t += delta
	var i := int(_t * maxf(1.0, Motion.amplitude(&"mainframe_takeover")))
	if i >= _frames.size():
		_t = -1.0
		_frames.clear()
		set_process(false)
		_refresh()
		return
	_now = _frames[i]
	_redraw_all()


## A tube's brightness during the warm-up: lit once warm, else flickering on at hash-picked
## steps (ANIM-R3 A7: each strikes within strike_share() of the warm-up, flickers for
## flicker_share(), then holds lit, so the sign is whole before the warm-up ends).
func tube(id: int) -> float:
	if warm >= 1.0:
		return 1.0
	var strike := float(absi(hash([id, 41])) % 1000) / 1000.0 * _strike
	if warm < strike:
		return TUBE_OFF_ALPHA
	if warm >= strike + _flicker:
		return 1.0
	var step := floori(warm * WARM_STEPS)
	var h := float(absi(hash([id, step, 43])) % 1000) / 1000.0
	return 1.0 if h < FLICKER_ON else TUBE_OFF_ALPHA


func _refresh() -> void:
	if _t >= 0.0:
		return
	var s := _empty()
	s["blue_frame"] = tube(TUBE_BORDER)
	for i in LETTERS:
		s["blue_%d" % i] = tube(i + 1)
	_now = s
	_redraw_all()


func _redraw_all() -> void:
	queue_redraw()
	_adds.queue_redraw()
	_subs.queue_redraw()
	light_changed.emit()


func _draw() -> void:
	draw_texture_rect(BASE, Rect2(Vector2.ZERO, size), false)


func _draw_layers(c: Control, mode: StringName) -> void:
	var t := table()
	var layers: Dictionary = t.get("layers", {})
	var k := size.x / maxf(1.0, canvas_size().x)
	var lv := layer_levels(_now)
	# The rails light with the traces as they run (ANIM-6 `mainframe_trace`).
	for pal in ["blue", "red"]:
		lv["%s_rail" % pal] = float(lv["%s_rail" % pal]) * trace
	var names := lv.keys()
	names.sort()
	for name: String in names:
		var level := float(lv[name])
		if level <= 0.0 or not layers.has(name):
			continue
		var L: Dictionary = layers[name]
		if StringName(String(L["mode"])) != mode:
			continue
		var r: Array = L["rect"]
		var at: Array = L["at"]
		var src := Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
		var dst := Rect2(Vector2(float(at[0]), float(at[1])) * k, src.size * k)
		c.draw_texture_rect_region(LAYERS, dst, src, Color(Palette.NO_TINT, clampf(level, 0.0, 1.0)))


## The sign's words as drawn (tests): the shop's name, a diegetic sign (never translated).
func shown_words() -> PackedStringArray:
	return PackedStringArray(["MAINFRAME"])


## ANIM-R4 C5: each tube strikes within this share of the warm-up (`mainframe_sign_strike`).
static func strike_share() -> float:
	return clampf(Motion.amplitude(&"mainframe_sign_strike"), 0.0, 1.0)


## ANIM-R4 C5: a struck tube flickers for this share of the warm-up (`mainframe_sign_flicker`).
static func flicker_share() -> float:
	return clampf(Motion.amplitude(&"mainframe_sign_flicker"), 0.0, 1.0)
