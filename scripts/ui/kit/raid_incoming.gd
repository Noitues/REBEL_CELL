class_name RaidIncoming
extends Control
## B3 (review section c "Raid interlude": one binary-bits INCOMING transition, about 0.6 s, from
## the run page into the raid; ART_BIBLE v2 §1.2 "bits are transitions"): over the raid page's
## first moments a dark plate crosses the screen's middle with INCOMING on it (Anton, HARM red,
## an ink keyline: words over the world sit on a plate), while 1B's binary bits stream in from
## the screen's two sides into the word. Its timing is `raid_incoming` (ui_motion.tres): the plate
## and the word fade in over its first EDGE_SHARE, hold, and fade out over its last EDGE_SHARE;
## then the layer frees itself. Reduce effects, headless or the entry switched off: nothing
## plays (the end state is the raid page). MotionSkip: `complete_motion` ends it. View only.

const MOTION := &"raid_incoming"
## The word (a key, translated once where drawn).
const WORD := "INCOMING" # TR
## Share of the run the plate takes to fade in (and out at the end).
const EDGE_SHARE := 0.25
## The plate's height as a share of the word's, its ink's alpha, the word's keyline (px at
## text scale 1.0) and the bits each side sends.
const PLATE_SHARE := 2.2
const PLATE_ALPHA := 0.88
const KEYLINE_PX := 3
const BITS_PER_SIDE := 18
## The share of the screen's width each side's bits start from.
const SIDE_SHARE := 0.18

## How far the transition has run (0..1).
var t: float = 0.0:
	set(v):
		t = v
		queue_redraw()
var _bits: BinaryBits = null
var _tween: Tween = null


func _init() -> void:
	name = "RaidIncoming"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	MotionSkip.register_passive(self)


## Plays the transition over `host` (the netrun scene): added on top, freed at its end. Returns
## its seconds (0: nothing plays, no layer is added).
static func play(host: Control) -> float:
	if host == null or not Motion.live(MOTION):
		return 0.0
	var layer := RaidIncoming.new()
	host.add_child(layer)
	layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return layer.start()


## Starts the run (`raid_incoming`) and the bits; returns its seconds.
func start() -> float:
	var d := Motion.seconds(MOTION)
	t = 0.0
	_tween = create_tween()
	_tween.tween_property(self, ^"t", 1.0, d).set_delay(Motion.delay_of(MOTION))
	_tween.tween_callback(queue_free)
	_bits = BinaryBits.new()
	add_child(_bits)
	var r := get_global_rect()
	var target := r.get_center()
	var w := r.size.x * SIDE_SHARE
	_bits.burst_from_rect(Rect2(r.position, Vector2(w, r.size.y)), target, Palette.HARM, BITS_PER_SIDE, 1)
	_bits.burst_from_rect(Rect2(Vector2(r.end.x - w, r.position.y), Vector2(w, r.size.y)), target, Palette.HARM, BITS_PER_SIDE, 2)
	return d + Motion.delay_of(MOTION)


## The plate's and the word's alpha at `u` (0..1): in, hold, out.
static func envelope(u: float) -> float:
	if u <= 0.0 or u >= 1.0:
		return 0.0
	return clampf(minf(u, 1.0 - u) / EDGE_SHARE, 0.0, 1.0)


## The word as drawn (translated).
static func word() -> String:
	return TranslationServer.translate(WORD)


## The plate's rect (local px) for lettering `px`.
func plate_rect(px: int) -> Rect2:
	var h := px * PLATE_SHARE
	return Rect2(Vector2(0.0, (size.y - h) * 0.5), Vector2(size.x, h))


func _draw() -> void:
	var a := envelope(t)
	if a <= 0.0:
		return
	var px := UiTheme.font_px(UiTheme.DISPLAY)
	var plate := plate_rect(px)
	draw_rect(plate, Color(Palette.SCRIM, PLATE_ALPHA * a))
	var f := Palette.display()
	var text := word()
	var tw := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var base := Vector2((size.x - tw) * 0.5, plate.get_center().y + (f.get_ascent(px) - f.get_descent(px)) * 0.5)
	draw_string_outline(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(KEYLINE_PX * Settings.text_scale) * 2, Color(Palette.INK, a))
	draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(Palette.HARM, a))


## MotionSkip: true while the transition runs.
func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


## MotionSkip: ends it at once (the raid page shows).
func complete_motion() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	if _bits != null and is_instance_valid(_bits):
		_bits.complete_motion()
	queue_free()
