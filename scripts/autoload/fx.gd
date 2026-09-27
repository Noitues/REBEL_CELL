extends CanvasLayer
## Fx autoload: the screen-space effects layer shared by every scene (STYLE_GUIDE 5-6,
## GDD 9.4-9.6). Scanlines + flicker + chromatic aberration overlay, the Heat distortion
## pulse, screen flashes through the FlashLimiter, short freeze frames and the jack-in /
## jack-out transition. Reduce-effects switches every animated effect off; the flash
## limiter never lets more than 3 flashes through per second.

const SCANLINE_SHADER := preload("res://shaders/scanline.gdshader")
const DISTORTION_SHADER := preload("res://shaders/distortion.gdshader")

var scanlines: ColorRect
var distortion: ColorRect
var flash_rect: ColorRect
var transition_rect: ColorRect
var crt_rect: ColorRect
var limiter := FlashLimiter.new(3)
var fps_label: Label
var saved_label: Label
## Timestamps of flashes actually shown (tests read this).
var flashes_shown: Array[float] = []
var _pulse_tween: Tween
var _frozen: bool = false


func _ready() -> void:
	layer = 100
	scanlines = _full_rect(Color.WHITE)
	scanlines.material = ShaderMaterial.new()
	scanlines.material.shader = SCANLINE_SHADER
	# The CRT look lives on the city and terminal glass (their own shaders); screen-wide
	# only a faint vignette and a whisper of flicker remain, so paper stays clean.
	scanlines.material.set_shader_parameter("scanline_strength", 0.0)
	scanlines.material.set_shader_parameter("aberration", 0.0)
	scanlines.material.set_shader_parameter("flicker_strength", 0.01)
	scanlines.material.set_shader_parameter("vignette", 0.18)
	distortion = _full_rect(Color.WHITE)
	distortion.material = ShaderMaterial.new()
	distortion.material.shader = DISTORTION_SHADER
	distortion.material.set_shader_parameter("intensity", 0.0)
	distortion.visible = false
	flash_rect = _full_rect(Color(1, 1, 1, 0))
	transition_rect = _full_rect(Color(0, 0, 0, 0))
	crt_rect = ColorRect.new()
	crt_rect.color = Color(Palette.CRT_AMBER, 0.0)
	crt_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	crt_rect.visible = false
	add_child(crt_rect)
	fps_label = Label.new()
	fps_label.add_theme_font_override("font", Palette.mono())
	fps_label.add_theme_font_size_override("font_size", 12)
	fps_label.add_theme_color_override("font_color", Palette.CELL_ACID)
	fps_label.position = Vector2(1180, 4)
	fps_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fps_label.visible = false
	add_child(fps_label)
	saved_label = Label.new()
	saved_label.add_theme_font_override("font", Palette.marker())
	saved_label.add_theme_font_size_override("font_size", 14)
	saved_label.add_theme_color_override("font_color", Palette.CELL_PINK)
	saved_label.text = "SAVED"
	saved_label.position = Vector2(1200, 690)
	saved_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	saved_label.modulate.a = 0.0
	add_child(saved_label)
	if has_node("/root/SignalBus"):
		get_node("/root/SignalBus").save_completed.connect(func(_path: String) -> void: show_saved())
	Settings.changed.connect(apply_settings)
	apply_settings()


func _process(_delta: float) -> void:
	if fps_label.visible:
		fps_label.text = "%d fps" % Engine.get_frames_per_second()


## Autosave indicator (gap analysis 2.5): a marker "SAVED" that fades out, placed where it
## covers no control (H23 S1: in the bottom-right corner it sat on the raid's Back to HQ and
## the route legend).
func show_saved() -> void:
	place_saved()
	saved_label.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_property(saved_label, "modulate:a", 0.0, 1.2).set_delay(0.6)


## The SAVED stamp's lettering at text scale 1.0 and its margin from the screen edge (px).
const SAVED_FONT := 14
const SAVED_MARGIN := 8.0
## Step between the spots tried along the screen's edges (px).
const SAVED_STEP := 24.0


## Puts the SAVED stamp at the first spot of `screen` (the viewport when empty) that
## covers no control on screen: along the bottom edge right to left, then the top edge,
## then the left and right edges; the least covered spot when none is clear. Returns its
## rect.
func place_saved(screen: Rect2 = Rect2()) -> Rect2:
	if not screen.has_area():
		screen = get_viewport().get_visible_rect()
	var fs := roundi(SAVED_FONT * Settings.text_scale)
	saved_label.add_theme_font_size_override("font_size", fs)
	saved_label.size = Vector2.ZERO
	var own := saved_label.get_combined_minimum_size()
	var spot := saved_spot(own, screen, avoid_rects(get_tree().root))
	saved_label.position = spot
	saved_label.size = own
	return Rect2(spot, own)


## The first spot for a `stamp`-sized rect in `screen` that meets none of `avoid` (see
## place_saved); pure, for tests.
static func saved_spot(stamp: Vector2, screen: Rect2, avoid: Array[Rect2]) -> Vector2:
	var inner := screen.grow(-SAVED_MARGIN)
	var right := inner.end.x - stamp.x
	var bottom := inner.end.y - stamp.y
	var spots: Array[Vector2] = []
	var x := right
	while x >= inner.position.x:
		spots.append(Vector2(x, bottom))
		x -= SAVED_STEP
	x = right
	while x >= inner.position.x:
		spots.append(Vector2(x, inner.position.y))
		x -= SAVED_STEP
	var y := bottom
	while y >= inner.position.y:
		spots.append(Vector2(inner.position.x, y))
		spots.append(Vector2(right, y))
		y -= SAVED_STEP
	var best := Vector2(right, bottom)
	var best_hits := INF
	for at in spots:
		var r := Rect2(at, stamp)
		var hits := 0.0
		for a in avoid:
			if r.intersects(a):
				hits += r.intersection(a).get_area() + 1.0
		if hits < best_hits:
			best_hits = hits
			best = at
			if hits == 0.0:
				break
	return best


## Screen rects of the controls on screen under `root` the stamp must not cover: usable
## buttons, fields and sliders, and map legends (as far as a scroll view shows them).
func avoid_rects(root: Node) -> Array[Rect2]:
	var out: Array[Rect2] = []
	_collect_avoid(root, out)
	return out


func _collect_avoid(node: Node, out: Array[Rect2]) -> void:
	for child in node.get_children():
		if child == self or child == saved_label:
			continue
		if child is CanvasItem and not (child as CanvasItem).visible:
			continue
		if child is Control:
			var c := child as Control
			var usable := (c is BaseButton and c.mouse_filter != Control.MOUSE_FILTER_IGNORE) or c is LineEdit or (c is Range and not (c is ScrollBar))
			if usable or c is MapLegend or c is RouteLegend or c is PadPrompts:
				var r := _shown_rect(c)
				if r.has_area():
					out.append(r)
				if usable:
					continue
		_collect_avoid(child, out)


## `c`'s rect clipped to the scroll views above it (the part on screen).
static func _shown_rect(c: Control) -> Rect2:
	var r := c.get_global_rect()
	var p := c.get_parent()
	while p != null:
		if p is ScrollContainer:
			r = r.intersection((p as Control).get_global_rect())
		p = p.get_parent()
	return r


func _full_rect(color: Color) -> ColorRect:
	var r := ColorRect.new()
	r.color = color
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(r)
	return r


## Reduce-effects disables scanlines, flicker, chromatic aberration and the distortion
## pulse everywhere; the flash limiter follows its own setting.
func apply_settings() -> void:
	scanlines.visible = not Settings.reduce_effects
	if Settings.reduce_effects:
		distortion.visible = false
		distortion.material.set_shader_parameter("intensity", 0.0)
		if _pulse_tween != null and _pulse_tween.is_valid():
			_pulse_tween.kill()
	limiter.enabled = Settings.flash_limiter
	fps_label.visible = Settings.show_fps


func effects_enabled() -> bool:
	return not Settings.reduce_effects


## Screen flash (Perfect latch, threshold events). Returns whether it was shown.
func flash(color: Color = Color.WHITE, strength: float = 0.45, seconds: float = 0.15) -> bool:
	var now := Time.get_ticks_msec() / 1000.0
	if not limiter.request(now):
		return false
	flashes_shown.append(now)
	flash_rect.color = Color(color, strength)
	var tw := create_tween()
	tw.tween_property(flash_rect, "color:a", 0.0, seconds)
	return true


## Heat threshold distortion pulse (GDD 9.4): pulses, never stays on.
func heat_pulse(seconds: float = 0.7) -> void:
	if not effects_enabled():
		return
	distortion.visible = true
	distortion.material.set_shader_parameter("intensity", 0.0)
	if _pulse_tween != null and _pulse_tween.is_valid():
		_pulse_tween.kill()
	_pulse_tween = create_tween()
	_pulse_tween.tween_method(func(v: float) -> void: distortion.material.set_shader_parameter("intensity", v), 0.0, 0.85, seconds * 0.3)
	_pulse_tween.tween_method(func(v: float) -> void: distortion.material.set_shader_parameter("intensity", v), 0.85, 0.0, seconds * 0.7)
	_pulse_tween.tween_callback(func() -> void: distortion.visible = false)


## Freezes time for `frames` frames (Perfect hit feel). No-op under reduce-effects.
func freeze_frames(frames: int = 2) -> void:
	if not effects_enabled() or _frozen or frames <= 0:
		return
	_frozen = true
	Engine.time_scale = 0.001
	for i in frames:
		await get_tree().process_frame
	Engine.time_scale = 1.0
	_frozen = false


## Jack in (STYLE_GUIDE 5): the camera pushes into the deck CRT and dissolves to
## wireframe. `on_switch` runs at the darkest point (the scene change). Instant under
## reduce-effects.
func jack_in(on_switch: Callable, seconds: float = 0.7) -> void:
	await _transition(on_switch, seconds, true)


func jack_out(on_switch: Callable, seconds: float = 0.7) -> void:
	await _transition(on_switch, seconds, false)


func _transition(on_switch: Callable, seconds: float, inward: bool) -> void:
	if not effects_enabled():
		on_switch.call()
		return
	var vp := get_viewport().get_visible_rect().size
	crt_rect.visible = true
	crt_rect.size = Vector2(vp.x * 0.3, vp.y * 0.3) if inward else vp
	crt_rect.position = (vp - crt_rect.size) / 2.0
	crt_rect.color = Color(Palette.CRT_AMBER if inward else Palette.NET_CYAN, 0.0)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(crt_rect, "color:a", 0.55, seconds * 0.5)
	tw.tween_property(crt_rect, "size", vp * 1.2 if inward else Vector2(vp.x * 0.3, vp.y * 0.3), seconds * 0.5)
	tw.tween_property(crt_rect, "position", -vp * 0.1 if inward else (vp - Vector2(vp.x * 0.3, vp.y * 0.3)) / 2.0, seconds * 0.5)
	tw.tween_property(transition_rect, "color:a", 1.0, seconds * 0.5)
	await tw.finished
	on_switch.call()
	crt_rect.visible = false
	var tw2 := create_tween()
	tw2.tween_property(transition_rect, "color:a", 0.0, seconds * 0.5)
	await tw2.finished
