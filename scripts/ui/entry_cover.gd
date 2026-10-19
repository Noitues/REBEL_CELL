class_name EntryCover
extends Control
## NA-25 (PIPELINE_SPEC 10): the street entry's player, over a `StreetRouteView`. It runs the street beats (3d dive, 4 REVEAL,
## 5 MARK + hold, 6 ZOOM + settle) as one timeline and ends on beat 7 (CHOOSE: DECISION on the current room, input back).
## Jack-out (`reverse`) reads the same timeline backwards in the same total time, then holds the HQ select state for
## `entry_select_hold`. One press (MotionSkip; Space is the shown key, input action `route_skip`) jumps to the end state in
## the same frame, the hold included. Headless, reduce effects or the entry switched off: every beat is 0 s, so `start` shows the
## end state at once with no timer pending. The beats' staging is `EntryBeats`; the view draws it (`StreetRouteView.entry_*`).
## View only: it emits signals up and changes no game state.

## The run's entry ended (played or skipped).
signal entry_finished
## A press ended the entry early (emitted before `entry_finished`).
signal entry_skipped
## How far the route UI (the ROUTE window) has come in, 0..1: it arrives with the markers and leaves first on the way out.
signal ui_changed(k: float)

## The key hint under the page while the entry plays (`%s` = the key's name).
const HINT := "%s: SKIP" # TR
const HINT_FONT := 16
const HINT_BOTTOM := 28.0

var view: StreetRouteView = null
var reverse: bool = false
## True while the timeline runs.
var playing: bool = false
var _fwd: Array[Dictionary] = []
var _total := 0.0
var _hold := 0.0
var _t := 0.0
var _hint: Label = null
var _mark_start := 0.0


func _init() -> void:
	name = "EntryCover"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MotionSkip.register(self)


## Plays the entry over `p_view` (`p_reverse`: the jack-out, ending on the HQ select state). Ends at once when no beat animates.
func start(p_view: StreetRouteView, p_reverse: bool = false) -> void:
	view = p_view
	reverse = p_reverse
	_fwd = EntryBeats.table(EntryBeats.STREET_BEATS)
	_total = EntryBeats.total(_fwd)
	_hold = EntryBeats.beat_seconds(&"select_hold") if reverse else 0.0
	_t = 0.0
	_mark_start = 0.0
	for row in _fwd:
		if StringName(row["beat"]) == &"mark":
			_mark_start = float(row["start"])
	view.entry_begin()
	ui_changed.emit(0.0)
	if _total + _hold <= 0.0:
		_finish(false)
		return
	playing = true
	_show_hint()
	_apply()


## The timeline's length (s), the jack-out hold excluded.
func total_seconds() -> float:
	return _total


## Seconds played so far.
func elapsed() -> float:
	return _t


## One press: straight to the end state (the hold of a jack-out included).
func skip() -> void:
	if playing:
		_finish(true)


func _process(delta: float) -> void:
	if not playing:
		return
	_t += delta
	if _t >= _total + _hold:
		_finish(false)
	else:
		_apply()


func _input(event: InputEvent) -> void:
	if playing and MotionSkip.handle(event, self) != MotionSkip.Verdict.IGNORE:
		get_viewport().set_input_as_handled()


## MotionSkip: the helper contract.
func motion_running() -> bool:
	return playing


## MotionSkip: a press ends the entry.
func complete_motion() -> void:
	skip()


## Draws the view for the playing time.
func _apply() -> void:
	var ft := EntryBeats.forward_time(_total, _t, reverse)
	var st := EntryBeats.at(_fwd, ft)
	var u := float(st["u"])
	var ui_s := Motion.seconds_live(&"entry_ui_in")
	ui_changed.emit(clampf((ft - _mark_start) / maxf(ui_s, 0.0001), 0.0, 1.0))
	match StringName(st["beat"]):
		&"dive":
			view.entry_dive(u)
		&"reveal":
			view.entry_reveal(u * Motion.seconds(&"entry_reveal"), Motion.seconds(&"entry_reveal"))
		&"mark":
			view.entry_mark(u * Motion.seconds(&"entry_mark"))
		&"mark_hold":
			view.entry_mark(Motion.seconds(&"entry_mark"))
		&"zoom":
			view.entry_zoom(u)
		&"zoom_settle":
			view.entry_zoom(1.0)


func _finish(skipped: bool) -> void:
	var was_playing := playing
	playing = false
	_t = _total + _hold
	if _hint != null and is_instance_valid(_hint):
		_hint.queue_free()
	_hint = null
	if not reverse:
		view.entry_end()
	ui_changed.emit(0.0 if reverse else 1.0)
	if skipped and was_playing:
		entry_skipped.emit()
	entry_finished.emit()


func _show_hint() -> void:
	_hint = Label.new()
	_hint.name = "SkipHint"
	_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hint.text = TranslationServer.translate(HINT) % Settings.key_name(Settings.key_for(&"route_skip"))
	_hint.add_theme_font_override(&"font", Palette.mono())
	_hint.add_theme_font_size_override(&"font_size", UiTheme.font_px(HINT_FONT))
	_hint.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	_hint.add_theme_color_override(&"font_outline_color", Palette.INK)
	_hint.add_theme_constant_override(&"outline_size", 4)
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_hint.offset_top = -HINT_BOTTOM * 2.0
	_hint.offset_bottom = -HINT_BOTTOM
	add_child(_hint)
