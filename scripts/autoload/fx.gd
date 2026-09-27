extends CanvasLayer
## Fx autoload: the screen-space effects layer shared by every scene (STYLE_GUIDE 5-6,
## GDD 9.4-9.6). Scanlines + flicker + chromatic aberration overlay, the Heat distortion
## pulse, screen flashes through the FlashLimiter, short freeze frames and the jack-in /
## jack-out transition. Reduce-effects switches every animated effect off; the flash
## limiter never lets more than 3 flashes through per second.

const SCANLINE_SHADER := preload("res://shaders/scanline.gdshader")
const DISTORTION_SHADER := preload("res://shaders/distortion.gdshader")
const JACK_SHADER := preload("res://shaders/jack_cover.gdshader")
const CREEP_SHADER := preload("res://shaders/corp_creep.gdshader")
## ANIM-5 (4.1): the node group a scene puts its deck CRT in (the point jack in pushes
## into and jack out pulls out of); the screen's centre when none shows.
const JACK_FOCUS_GROUP := &"jack_focus"
## Share of the push zoom the scene on the far side of the cover starts at (it keeps the
## push going as the cover clears).
const JACK_ARRIVE_SHARE := 0.15
const SCANLINE_MOTION := &"jack_scanlines"
const CREEP_MOTION := &"net_creep"

var scanlines: ColorRect
var distortion: ColorRect
var flash_rect: ColorRect
var transition_rect: ColorRect
## ANIM-5: the jack cover (dissolve to the wireframe city, rolling scanlines) and the
## Heat crossing's corporate wireframe creeping in from the edges.
var jack_cover: ColorRect
var creep_rect: ColorRect
## Heat pulses played (one per threshold crossing; tests read this).
var heat_pulses: int = 0
var _jacking: bool = false
var _cover_opaque: bool = false
var _creep_tween: Tween
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
	creep_rect = _full_rect(Color.WHITE)
	creep_rect.material = ShaderMaterial.new()
	creep_rect.material.shader = CREEP_SHADER
	creep_rect.material.set_shader_parameter("reach", 0.0)
	creep_rect.visible = false
	flash_rect = _full_rect(Color(1, 1, 1, 0))
	jack_cover = _full_rect(Color.WHITE)
	jack_cover.material = ShaderMaterial.new()
	jack_cover.material.shader = JACK_SHADER
	jack_cover.visible = false
	transition_rect = _full_rect(Color(0, 0, 0, 0))
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
	# H24 S4: translated when shown (show_saved), shown as given.
	saved_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	saved_label.text = tr("SAVED")
	saved_label.position = Vector2(1200, 690)
	saved_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	saved_label.modulate.a = 0.0
	add_child(saved_label)
	if has_node("/root/SignalBus"):
		get_node("/root/SignalBus").save_completed.connect(func(_path: String) -> void: show_saved())
	Settings.changed.connect(apply_settings)
	apply_settings()


## Lets the Motion kit's table go before the engine checks for leaked resources at exit.
func _exit_tree() -> void:
	Motion.use_config(null)


func _process(_delta: float) -> void:
	if fps_label.visible:
		fps_label.text = "%d fps" % Engine.get_frames_per_second()
	# H24 S7: while the stamp shows, it follows the layout (a page built after the save,
	# a pad prompt row appearing) and never sits on a control.
	if _saved_live and saved_label.modulate.a > 0.0:
		place_saved(saved_screen)
	elif _saved_live and (_saved_tween == null or not _saved_tween.is_valid()):
		_saved_live = false


## Autosave indicator (gap analysis 2.5): a marker "SAVED" that fades out, placed where it
## covers no control (H23 S1: in the bottom-right corner it sat on the raid's Back to HQ and
## the route legend). H24 S7: placed a frame later, once the page the save came from has
## laid out (a save runs before its new page is built, so the stamp was placed on the old
## page's geometry: over the Daemons button after a new campaign), and placed again every
## frame while it shows. Holds and fades per the `saved_stamp` motion entry
## (Animation pass).
func show_saved() -> void:
	saved_label.text = tr("SAVED")
	saved_label.modulate.a = 0.0
	if _saved_tween != null and _saved_tween.is_valid():
		_saved_tween.kill()
	_saved_live = false
	await get_tree().process_frame
	place_saved(saved_screen)
	saved_label.modulate.a = 1.0
	# Animation pass ANIM-6: the stamp stamps down (`saved_stamp_in`) before it holds and fades.
	saved_label.pivot_offset = saved_label.size * 0.5
	saved_label.scale = Vector2.ONE * (Motion.amplitude(&"saved_stamp_in") if Motion.live(&"saved_stamp_in") else 1.0)
	Motion.run(&"saved_stamp_in", saved_label, ^"scale", Vector2.ONE)
	_saved_live = true
	var e := Motion.entry(&"saved_stamp")
	_saved_tween = create_tween()
	_saved_tween.tween_property(saved_label, "modulate:a", 0.0, Motion.seconds(&"saved_stamp")).set_delay(Motion.delay_of(&"saved_stamp")).set_ease(e.ease).set_trans(e.trans)


## The stamp is up and follows the layout (H24 S7), and its fade.
var _saved_live: bool = false
var _saved_tween: Tween = null
## The screen rect the stamp keeps to (empty: the viewport; tests set the 1280x720 page).
var saved_screen: Rect2 = Rect2()
## The process frame the stamp was last placed on (tests).
var saved_placed_frame: int = -1


## Whether the SAVED stamp is on screen now (tests).
func saved_showing() -> bool:
	return saved_label.modulate.a > 0.0


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
	saved_placed_frame = Engine.get_process_frames()
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
		creep_rect.visible = false
		if _creep_tween != null and _creep_tween.is_valid():
			_creep_tween.kill()
	limiter.enabled = Settings.flash_limiter
	fps_label.visible = Settings.show_fps


func effects_enabled() -> bool:
	return not Settings.reduce_effects


## Screen flash (Perfect latch, threshold events). Returns whether it was shown. A
## negative strength or seconds takes the `screen_flash` motion entry's amplitude/duration.
func flash(color: Color = Color.WHITE, strength: float = -1.0, seconds: float = -1.0) -> bool:
	var now := Time.get_ticks_msec() / 1000.0
	if not limiter.request(now):
		return false
	if strength < 0.0:
		strength = Motion.amplitude(&"screen_flash")
	if seconds < 0.0:
		seconds = Motion.seconds(&"screen_flash")
	flashes_shown.append(now)
	flash_rect.color = Color(color, strength)
	var tw := create_tween()
	tw.tween_property(flash_rect, "color:a", 0.0, seconds)
	return true


## Heat threshold distortion pulse (GDD 9.4): pulses, never stays on. Rises for
## HEAT_PULSE_RISE of the time to the `heat_pulse` entry's amplitude, then falls; a
## negative `seconds` takes the entry's duration. ANIM-5 (4.12): one per threshold
## crossing (HeatPoster calls it); `creep` (a corporation's colour, alpha > 0) also sends
## the corporate wireframe creeping in from the screen's edges over the zine layer and back
## (`net_creep`). Counted in `heat_pulses` even under reduce effects (nothing shows then).
func heat_pulse(seconds: float = -1.0, creep: Color = Color(0, 0, 0, 0)) -> void:
	heat_pulses += 1
	if not effects_enabled():
		return
	if creep.a > 0.0:
		_creep(creep)
	if seconds < 0.0:
		seconds = Motion.seconds(&"heat_pulse")
	var peak := Motion.amplitude(&"heat_pulse")
	distortion.visible = true
	distortion.material.set_shader_parameter("intensity", 0.0)
	if _pulse_tween != null and _pulse_tween.is_valid():
		_pulse_tween.kill()
	_pulse_tween = create_tween()
	_pulse_tween.tween_method(func(v: float) -> void: distortion.material.set_shader_parameter("intensity", v), 0.0, peak, seconds * HEAT_PULSE_RISE)
	_pulse_tween.tween_method(func(v: float) -> void: distortion.material.set_shader_parameter("intensity", v), peak, 0.0, seconds * (1.0 - HEAT_PULSE_RISE))
	_pulse_tween.tween_callback(func() -> void: distortion.visible = false)


## The corporate wireframe creeps in from the edges to `net_creep`'s reach and back.
func _creep(col: Color) -> void:
	if _creep_tween != null and _creep_tween.is_valid():
		_creep_tween.kill()
	var m := creep_rect.material as ShaderMaterial
	m.set_shader_parameter("tint", col)
	m.set_shader_parameter("reach", 0.0)
	creep_rect.visible = true
	var e := Motion.entry(CREEP_MOTION)
	var half := Motion.seconds(CREEP_MOTION) * 0.5
	var reach := Motion.amplitude(CREEP_MOTION)
	var set_reach := func(v: float) -> void: m.set_shader_parameter("reach", v)
	_creep_tween = create_tween()
	_creep_tween.tween_method(set_reach, 0.0, reach, half).set_ease(Tween.EASE_OUT).set_trans(e.trans)
	_creep_tween.tween_method(set_reach, reach, 0.0, half).set_ease(Tween.EASE_IN).set_trans(e.trans)
	_creep_tween.tween_callback(func() -> void: creep_rect.visible = false)


## Freezes time for `frames` frames (Perfect hit feel); a negative count takes the
## `hit_freeze` motion entry's amplitude. No-op under reduce-effects.
func freeze_frames(frames: int = -1) -> void:
	if frames < 0:
		frames = roundi(Motion.amplitude(&"hit_freeze"))
	if not effects_enabled() or _frozen or frames <= 0:
		return
	_frozen = true
	Engine.time_scale = 0.001
	for i in frames:
		await get_tree().process_frame
	Engine.time_scale = 1.0
	_frozen = false


## Jack in (STYLE_GUIDE 5, ANIM-5 4.1): the camera pushes into the deck CRT (the scene
## scales up about its `jack_focus` node) while the screen dissolves, cell by cell from the
## CRT outward, into the wireframe city with scanlines rolling; `on_switch` runs when the
## cover is opaque (the scene change), then the net arrives as the cover clears. Jack out
## reverses it: the net pulls back into the dissolve and the HQ comes out of the CRT.
## Timing from the `jack_in` / `jack_out` entries (a negative `seconds` takes the entry's
## duration; amplitude = the push zoom). No frame shows both scenes: the old one is only
## ever under a partial cover before the switch, the new one only after it. Reduce
## effects: one short fade (`jack_fade_reduced`); headless (tests): the switch at once.
func jack_in(on_switch: Callable, seconds: float = -1.0) -> void:
	await _transition(on_switch, seconds, &"jack_in")


func jack_out(on_switch: Callable, seconds: float = -1.0) -> void:
	await _transition(on_switch, seconds, &"jack_out")


## Share of a Heat pulse spent rising (the rest falls).
const HEAT_PULSE_RISE := 0.3


## True while a jack transition runs (views hold their own effects till it ends).
func transitioning() -> bool:
	return _jacking


## True while the jack cover hides the whole screen (the scene switches then).
func cover_opaque() -> bool:
	return _cover_opaque


func _transition(on_switch: Callable, seconds: float, id: StringName) -> void:
	if DisplayServer.get_name() == "headless" and not Motion.force_live:
		on_switch.call()
		return
	_jacking = true
	if not effects_enabled():
		await _fade_switch(on_switch)
		_jacking = false
		return
	var inward := id == &"jack_in"
	if seconds < 0.0:
		seconds = Motion.seconds(id)
	var e := Motion.entry(id)
	var half := seconds * 0.5
	var zoom := maxf(1.0, Motion.amplitude(id))
	var arrive := 1.0 + (zoom - 1.0) * JACK_ARRIVE_SHARE
	var vp := get_viewport().get_visible_rect().size
	var m := jack_cover.material as ShaderMaterial
	m.set_shader_parameter("screen", vp)
	m.set_shader_parameter("tile", Vector2(NeonCity.TILE_A, NeonCity.TILE_B))
	m.set_shader_parameter("scan", Motion.amplitude(SCANLINE_MOTION))
	m.set_shader_parameter("lattice", Palette.NET_CYAN)
	var old := get_tree().current_scene as Control
	var focus := _jack_focus(old, vp)
	m.set_shader_parameter("focus", focus)
	jack_cover.visible = true
	_set_cover(0.0, 0.0)
	var t0 := Time.get_ticks_msec()
	var tw := create_tween().set_parallel(true)
	tw.tween_method(func(v: float) -> void: _set_cover(v, _roll(t0)), 0.0, 1.0, half).set_ease(Tween.EASE_IN).set_trans(e.trans)
	var old_scale := Vector2.ONE
	if old != null:
		old_scale = old.scale
		old.pivot_offset = focus - old.global_position
		tw.tween_property(old, "scale", Vector2.ONE * (zoom if inward else 1.0 / arrive), half).set_ease(Tween.EASE_IN).set_trans(e.trans)
	await tw.finished
	_set_cover(1.0, _roll(t0))
	_cover_opaque = true
	on_switch.call()
	if is_instance_valid(old):
		old.scale = old_scale
	# The new scene takes over at the end of this frame and builds its page in the next.
	for f in 2:
		await get_tree().process_frame
	var fresh := get_tree().current_scene as Control
	focus = _jack_focus(fresh, vp)
	m.set_shader_parameter("focus", focus)
	var tw2 := create_tween().set_parallel(true)
	if fresh != null:
		fresh.pivot_offset = focus - fresh.global_position
		fresh.scale = Vector2.ONE * (arrive if inward else zoom)
		tw2.tween_property(fresh, "scale", Vector2.ONE, half).set_ease(Tween.EASE_OUT).set_trans(e.trans)
	_cover_opaque = false
	tw2.tween_method(func(v: float) -> void: _set_cover(v, _roll(t0)), 1.0, 0.0, half).set_ease(Tween.EASE_OUT).set_trans(e.trans)
	await tw2.finished
	if is_instance_valid(fresh):
		fresh.scale = Vector2.ONE
	jack_cover.visible = false
	_jacking = false


## Reduce effects: one short fade through black (`jack_fade_reduced`), the switch at its
## darkest.
func _fade_switch(on_switch: Callable) -> void:
	var e := Motion.entry(&"jack_fade_reduced")
	var half := (e.duration if e != null else 0.0) * 0.5
	var tw := create_tween()
	tw.tween_property(transition_rect, "color:a", 1.0, half)
	await tw.finished
	_cover_opaque = true
	on_switch.call()
	for f in 2:
		await get_tree().process_frame
	_cover_opaque = false
	var tw2 := create_tween()
	tw2.tween_property(transition_rect, "color:a", 0.0, half)
	await tw2.finished


func _set_cover(progress: float, roll: float) -> void:
	var m := jack_cover.material as ShaderMaterial
	m.set_shader_parameter("progress", progress)
	m.set_shader_parameter("roll", roll)


## The scanlines' phase: one roll every `jack_scanlines` seconds since `t0` (msec).
func _roll(t0: int) -> float:
	var period := maxf(Motion.seconds(SCANLINE_MOTION), 0.001)
	return fmod((Time.get_ticks_msec() - t0) / 1000.0 / period, 1.0)


## The deck CRT in `scene` (the first visible node of JACK_FOCUS_GROUP in it; viewport
## px), else the middle of the screen.
func _jack_focus(scene: Node, vp: Vector2) -> Vector2:
	if scene != null and is_inside_tree():
		for n in get_tree().get_nodes_in_group(JACK_FOCUS_GROUP):
			if n is Control and scene.is_ancestor_of(n) and (n as Control).is_visible_in_tree():
				return (n as Control).get_global_rect().get_center()
	return vp * 0.5
