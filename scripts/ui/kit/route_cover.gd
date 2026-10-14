class_name RouteCover
extends TextureRect
## ART-R1 9a (ANIM-FLOW M6, art-pass review): the route page never shows the empty map (a flat
## purple plane with the links and pips and no city, about 800 ms after a reward pick). While the
## city behind the arriving page has not drawn, the last frame of the page that left stays up over
## the whole screen; when the city is drawn the cover fades out and frees itself. It waits at most
## `MAX_WAIT` seconds (a city that never reports ready must not hold the screen). View only.
## ART-R2 9a: what it holds is the dark page (the night's colour), never the last frame: that frame
## was the loot sheet with its cards half dissolved to grey blanks, and a half-dissolved UI is never held.

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


## A cover over the whole screen: the dark page (`frame` null) or `frame` (tests).
static func make(frame: Texture2D, check: Callable) -> RouteCover:
	var c := RouteCover.new()
	c.name = "RouteCover"
	c.texture = frame if frame != null else dark_page()
	c.ready_check = check
	c.mouse_filter = Control.MOUSE_FILTER_STOP
	c.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	c.stretch_mode = TextureRect.STRETCH_SCALE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return c


## The held page: one pixel of the night's colour, scaled over the screen.
static func dark_page() -> Texture2D:
	var img := Image.create(1, 1, false, Image.FORMAT_RGBA8)
	img.fill(Palette.NIGHT_SKY)
	return ImageTexture.create_from_image(img)


## The reveal rule (pure): the cover lifts once the city has been ready for `READY_FRAMES` frames
## in a row, or after `MAX_WAIT` seconds.
static func lifts(ready_frames: int, waited: float) -> bool:
	return ready_frames >= READY_FRAMES or waited >= MAX_WAIT


func _ready() -> void:
	MotionSkip.register_passive(self)  # its fade out is a short motion (test_anim_r6_rules)


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
