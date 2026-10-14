class_name RouteCover
extends TextureRect
## ART-R1 9a (ANIM-FLOW M6, art-pass review): the route page never shows the empty map (a flat
## purple plane with the links and pips and no city, about 800 ms after a reward pick). While the
## city behind the arriving page has not drawn, the last frame of the page that left stays up over
## the whole screen; when the city is drawn the cover fades out and frees itself. It waits at most
## `MAX_WAIT` seconds (a city that never reports ready must not hold the screen). View only.

## The most the cover holds (s), the frames the city must report ready in a row, and the fade that
## takes it off (the `reward_page_in` entry's seconds).
const MAX_WAIT := 2.5
const READY_FRAMES := 3
const FADE := &"reward_page_in"

## True when the city is drawn (set by the host: its look is current and its camera has settled).
var ready_check: Callable = Callable()
var _waited: float = 0.0
var _ready_run: int = 0
var _leaving: bool = false


## A cover of `frame` (the last frame of the page that left), over the whole screen.
static func make(frame: Texture2D, check: Callable) -> RouteCover:
	var c := RouteCover.new()
	c.name = "RouteCover"
	c.texture = frame
	c.ready_check = check
	c.mouse_filter = Control.MOUSE_FILTER_STOP
	c.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	c.stretch_mode = TextureRect.STRETCH_SCALE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return c


## The reveal rule (pure): the cover lifts once the city has been ready for `READY_FRAMES` frames
## in a row, or after `MAX_WAIT` seconds.
static func lifts(ready_frames: int, waited: float) -> bool:
	return ready_frames >= READY_FRAMES or waited >= MAX_WAIT


func _process(delta: float) -> void:
	if _leaving:
		return
	_waited += delta
	var ok := ready_check.is_valid() and bool(ready_check.call())
	_ready_run = _ready_run + 1 if ok else 0
	if lifts(_ready_run, _waited):
		_leave()


## True while the cover still hides the page (tests).
func holding() -> bool:
	return not _leaving


func _leave() -> void:
	_leaving = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var secs := Motion.seconds(FADE)
	if secs <= 0.0 or not Fx.effects_enabled():
		queue_free()
		return
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, secs)
	tw.tween_callback(queue_free)
