extends CanvasLayer
## Fx autoload: the screen-space effects layer shared by every scene (STYLE_GUIDE 5-6,
## GDD 9.4-9.6). Scanlines + flicker + chromatic aberration overlay, the Heat distortion
## pulse, screen flashes through the FlashLimiter, short freeze frames and the jack-in /
## jack-out transition. Reduce-effects switches every animated effect off; the flash
## limiter never lets more than 3 flashes through per second.

const SCANLINE_SHADER := preload("res://shaders/scanline.gdshader")
const DISTORTION_SHADER := preload("res://shaders/distortion.gdshader")
const JACK_SHADER := preload("res://shaders/jack_cover.gdshader")
## ANIM-5 (4.1): the node group a scene puts its deck CRT in (the point jack in pushes
## into and jack out pulls out of); the screen's centre when none shows.
const JACK_FOCUS_GROUP := &"jack_focus"
## ANIM-R1 M8: a scene that builds its arriving screen over several frames (a city map to
## bake and frame) says when it is ready with this method (-> bool); the jack cover stays
## opaque until then (at most `jack_arrival_wait`).
const ARRIVAL_READY_METHOD := &"arrival_ready"
const SCANLINE_MOTION := &"jack_scanlines"
## ANIM-R1 M3: the jack's arrival (the reveal half) has an entry of its own.
const ARRIVE_MOTION := &"jack_arrive"
## ANIM-R1 M8: the most the jack cover waits, opaque, for the arriving screen to be built
## and framed (its duration, seconds).
const ARRIVAL_WAIT_MOTION := &"jack_arrival_wait"

var scanlines: ColorRect
var distortion: ColorRect
var flash_rect: ColorRect
var transition_rect: ColorRect
## ANIM-5: the jack cover (dissolve to the wireframe city, rolling scanlines).
var jack_cover: ColorRect
## Heat pulses played (one per threshold crossing; tests read this).
var heat_pulses: int = 0
var _jacking: bool = false
var _cover_opaque: bool = false
var limiter := FlashLimiter.new(3)
var fps_label: Label
var saved_label: Label
## Timestamps of flashes actually shown (tests read this).
var flashes_shown: Array[float] = []
var _pulse_tween: Tween
var _frozen: bool = false
## ANIM-R2 R3: the jack's input blocker, kept last under the root (first in the input order).
var input_gate: JackInputGate
## ANIM-R2 R5: "CONNECTING TO <place>" and its progress mark on the cover while the arriving
## screen builds (the wait was ~3 s of an empty tunnel with no words).
var connect_label: Label
var connect_bar: ColorRect
var connect_fill: ColorRect
## The place the running jack connects to (translated; "" = none named).
var _destination: String = ""
const CONNECT_MOTION := &"jack_connect"
const DISSOLVE_MOTION := &"jack_dissolve"
## ANIM-R3 B5: a second line under CONNECTING TO <place> ("INTERRUPTED: RAID INCOMING" when
## the run opens on a raid interlude; "" for none), translated by the caller.
var _note: String = ""
## ANIM-R4 H11a: the note is a stamp of its own under the bar: large amber lettering in a
## ruled box, tilted like a rubber stamp, held at least `raid_incoming_hold` (a raid naming
## its corporation must be read, not glimpsed). Lettering at text scale 1.0, tilt (degrees),
## ruling width and padding (px).
var note_label: Label
const NOTE_MOTION := &"raid_incoming_hold"
const NOTE_FONT := 34
const NOTE_TILT := -4.0
const NOTE_RULE := 4
const NOTE_PAD := 14
## The CONNECTING line's lettering at text scale 1.0 and the bar's height and gap (px).
const CONNECT_FONT := 20
const CONNECT_BAR_H := 4.0
const CONNECT_GAP := 12.0
## ANIM-R6 B13: the destination's own line under CONNECTING TO: large, bright, with the
## Site's tier icon (it was the end of a small dim teal line): its lettering at text scale
## 1.0 (px), the icon's side as a share of the lettering, the gap between them (px), and
## the least room it keeps off the screen's sides (px).
var connect_dest: Label
var connect_site: JackSiteIcon
const CONNECT_DEST_FONT := 44
const CONNECT_ICON_SHARE := 1.5
const CONNECT_ICON_GAP := 14.0
const CONNECT_DEST_MARGIN := 24.0
## The Site's tier the running jack connects to (0: none shown).
var _destination_tier: int = 0


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
	jack_cover = _full_rect(Color.WHITE)
	jack_cover.material = ShaderMaterial.new()
	jack_cover.material.shader = JACK_SHADER
	jack_cover.visible = false
	transition_rect = _full_rect(Color(0, 0, 0, 0))
	connect_label = Label.new()
	connect_label.name = "JackConnecting"
	connect_label.add_theme_font_override("font", Palette.mono())
	connect_label.add_theme_color_override("font_color", Palette.NET_CYAN)
	connect_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	connect_label.add_theme_constant_override("outline_size", 6)
	connect_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	connect_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	connect_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	connect_label.visible = false
	add_child(connect_label)
	connect_dest = Label.new()
	connect_dest.name = "JackDestination"
	connect_dest.add_theme_font_override("font", Palette.display())
	connect_dest.add_theme_color_override("font_color", Palette.PAPER)
	connect_dest.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	connect_dest.add_theme_constant_override("outline_size", 8)
	connect_dest.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	connect_dest.mouse_filter = Control.MOUSE_FILTER_IGNORE
	connect_dest.visible = false
	add_child(connect_dest)
	connect_site = JackSiteIcon.new()
	connect_site.name = "JackSiteIcon"
	connect_site.visible = false
	add_child(connect_site)
	note_label = Label.new()
	note_label.name = "JackRaidNote"
	note_label.add_theme_font_override("font", Palette.display())
	note_label.add_theme_color_override("font_color", Palette.CRT_AMBER)
	note_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	note_label.add_theme_constant_override("outline_size", 6)
	var ruled := StyleBoxFlat.new()
	ruled.bg_color = Color(Palette.NIGHT_SKY, 0.9)
	ruled.border_color = Palette.CRT_AMBER
	ruled.set_border_width_all(NOTE_RULE)
	ruled.set_content_margin_all(NOTE_PAD)
	note_label.add_theme_stylebox_override("normal", ruled)
	note_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	note_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	note_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	note_label.visible = false
	add_child(note_label)
	connect_bar = ColorRect.new()
	connect_bar.color = Color(Palette.NET_CYAN, 0.25)
	connect_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	connect_bar.visible = false
	add_child(connect_bar)
	connect_fill = ColorRect.new()
	connect_fill.color = Palette.NET_CYAN
	connect_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	connect_bar.add_child(connect_fill)
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
	input_gate = JackInputGate.new()
	get_tree().root.add_child.call_deferred(input_gate)
	_warm_materials()


## ANIM-R3 B1: the jack cover's and the Heat distortion's shaders are drawn once, invisibly
## (the cover at progress 0 draws nothing; the distortion at intensity 0 changes nothing),
## for WARM_FRAMES frames at start, so the first jack does not compile them in its first
## frame (a 70-92 ms hitch as the cover started).
func _warm_materials() -> void:
	if DisplayServer.get_name() == "headless":
		return
	_set_cover(0.0, 0.0)
	jack_cover.visible = true
	distortion.visible = true
	_warm_left = WARM_FRAMES
	get_tree().process_frame.connect(_warm_step)


const WARM_FRAMES := 2
var _warm_left: int = 0


func _warm_step() -> void:
	_warm_left -= 1
	if _warm_left > 0:
		return
	get_tree().process_frame.disconnect(_warm_step)
	if not _jacking:
		jack_cover.visible = false
	if _pulse_tween == null or not _pulse_tween.is_valid():
		distortion.visible = false


## Lets the Motion kit's table go before the engine checks for leaked resources at exit.
## ANIM-R2 R10: the city bakes too (running builds stopped and joined, their painters and
## viewports freed, every baked texture let go while the renderer still runs).
## ANIM-R5 P17: and every resource a script's static variable caches (fonts, the terminal
## material, the chevron), so none is freed with its script after the servers are gone.
func _exit_tree() -> void:
	CityBakeCache.shutdown()
	Motion.use_config(null)
	Palette.release_fonts()
	UiTheme.release()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		CityBakeCache.shutdown()


func _process(_delta: float) -> void:
	if _jacking and input_gate != null:
		input_gate.stay_last()
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
	# ANIM-R1: two saves in one frame each got here; the first one's fade must not outlive
	# the second's (it kept fading the new stamp).
	if _saved_tween != null and _saved_tween.is_valid():
		_saved_tween.kill()
	place_saved(saved_screen)
	saved_label.modulate.a = 1.0
	# Animation pass ANIM-6: the stamp stamps down (`saved_stamp_in`) before it holds and fades.
	saved_label.pivot_offset = saved_label.size * 0.5
	saved_label.scale = Vector2.ONE * (Motion.amplitude(&"saved_stamp_in") if Motion.live(&"saved_stamp_in") else 1.0)
	Motion.run(&"saved_stamp_in", saved_label, ^"scale", Vector2.ONE)
	_saved_live = true
	var e := Motion.entry(&"saved_stamp")
	_saved_tween = create_tween()
	if Motion.live(&"saved_stamp"):
		_saved_tween.tween_property(saved_label, "modulate:a", 0.0, Motion.seconds(&"saved_stamp")).set_delay(Motion.delay_of(&"saved_stamp")).set_ease(e.ease).set_trans(e.trans)
	else:
		# ANIM-R1 M3: no fade when the entry is off (or no motion plays): the stamp shows
		# still for its hold and fade time, then goes at once.
		_saved_tween.tween_interval(Motion.delay_of(&"saved_stamp") + Motion.seconds(&"saved_stamp"))
		_saved_tween.tween_callback(func() -> void: saved_label.modulate.a = 0.0)


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
## ANIM-R1 M15: the largest screen side the spot search walks (px).
const SAVED_SCREEN_MAX := 16384.0


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
	# ANIM-R1 M15: a measure that is not finite (or a screen far too big) never loops.
	if not (is_finite(right) and is_finite(bottom) and is_finite(inner.position.x) and is_finite(inner.position.y)) 			or inner.size.x > SAVED_SCREEN_MAX or inner.size.y > SAVED_SCREEN_MAX:
		return Vector2(right, bottom) if is_finite(right) and is_finite(bottom) else Vector2.ZERO
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
	# ANIM-R3 B13: when every spot along the edges covers something, a grid over the whole
	# screen (SAVED_INNER_STEP apart) is tried too: at 1.0 the least covered edge spot was
	# over UNDO.
	if best_hits > 0.0:
		var gy := bottom
		while gy >= inner.position.y and best_hits > 0.0:
			var gx := right
			while gx >= inner.position.x:
				var r := Rect2(Vector2(gx, gy), stamp)
				var hits := 0.0
				for a in avoid:
					if r.intersects(a):
						hits += r.intersection(a).get_area() + 1.0
				if hits < best_hits:
					best_hits = hits
					best = Vector2(gx, gy)
					if hits == 0.0:
						break
				gx -= SAVED_INNER_STEP
			gy -= SAVED_INNER_STEP
	return best


## ANIM-R3 B13: the step of the whole-screen grid tried after the edges (px).
const SAVED_INNER_STEP := 40.0


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
			if c is HudBar:
				# ANIM-R3 B13: the screen's title (at 1.6 SAVED landed on "CITY GRID").
				var tb: Control = (c as HudBar).title_box
				if tb != null and tb.is_visible_in_tree():
					out.append(tb.get_global_rect())
			if c is Label and c.name == &"TerminalTitle":
				# ANIM-R3 B13: and the windows' titles.
				out.append(_shown_rect(c.get_parent() as Control))
			if c is HudStats:
				# ANIM-R1 M12: the top bar's tags carry numbers (at 1.6 the stamp sat on CREW).
				var xf := c.get_global_transform()
				for r: Rect2 in (c as HudStats).tag_rects():
					out.append(Rect2(xf * r.position, r.size * xf.get_scale()))
				# ANIM-R2 R13: and its captions (at 1.6 SAVED sat on CAMPAIGN).
				var caps: Variant = c.get("_caption_rects")
				if caps is Array:
					for r: Rect2 in caps:
						out.append(Rect2(xf * r.position, r.size * xf.get_scale()))
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


## Screen flash (Perfect latch, threshold events). Returns whether it was shown. A
## negative strength or seconds takes the `screen_flash` motion entry's amplitude/duration.
## ANIM-R6 D8: never under reduce effects (a full-screen flash is what the setting is for;
## callers that gate on their own entry already skip it), and not when it takes
## `screen_flash`'s numbers and that entry is switched off.
func flash(color: Color = Color.WHITE, strength: float = -1.0, seconds: float = -1.0) -> bool:
	if not effects_enabled():
		return false
	if (strength < 0.0 or seconds < 0.0) and not Motion.switched_on(&"screen_flash"):
		return false
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
## crossing (HeatPoster calls it through `heat_pulse_at`). Counted in `heat_pulses` even
## under reduce effects (nothing shows then). ANIM-R3 B9: the corporate wireframe creep
## (`net_creep`) is gone; ANIM-R2 R8 had stopped every caller from asking for it.
func heat_pulse(seconds: float = -1.0) -> void:
	heat_pulses += 1
	if not effects_enabled():
		return
	# ANIM-R1 M3: an entry switched off (or headless) is its end state at once: no pulse.
	if not Motion.live(&"heat_pulse"):
		return
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
	_pulse_tween.tween_callback(func() -> void:
		distortion.visible = false
		distortion.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT))


## ANIM-R2 R8: a Heat crossing's distortion, local: only round `rect` (viewport px, grown
## by HEAT_PULSE_MARGIN; the whole screen when empty) and over `heat_pulse`'s duration (at
## most 0.3 s). No corporate creep: the full-screen wireframe lingered and read as a
## display fault. Counted in `heat_pulses` like `heat_pulse`.
func heat_pulse_at(rect: Rect2, seconds: float = -1.0) -> void:
	if rect.has_area():
		distortion.set_anchors_preset(Control.PRESET_TOP_LEFT)
		var r := rect.grow(HEAT_PULSE_MARGIN)
		distortion.position = r.position
		distortion.size = r.size
	else:
		distortion.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	heat_pulse(seconds)


## ANIM-R2 R8: how far past the poster its distortion reaches (px).
const HEAT_PULSE_MARGIN := 24.0


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
## ANIM-R2 R5: `destination` (translated) is named on the cover while the arriving screen
## builds ("CONNECTING TO <place>").
## ANIM-R6 B13: `tier` (1-4) shows the Site's tier icon beside its name (0: none).
func jack_in(on_switch: Callable, seconds: float = -1.0, destination: String = "", note: String = "", tier: int = 0) -> void:
	if not _jacking:
		_destination = destination
		_note = note
		_destination_tier = tier
	await _transition(on_switch, seconds, &"jack_in")


func jack_out(on_switch: Callable, seconds: float = -1.0, destination: String = "") -> void:
	if not _jacking:
		_destination = destination
		_destination_tier = 0
	await _transition(on_switch, seconds, &"jack_out")


## ANIM-R2 R5: the CONNECTING line (translated once here) over the opaque cover, its bar
## empty; it fades in over `jack_connect` (at once when motion doesn't play). The bar shows
## only when the line may animate (reduce effects: the words alone).
func _show_connect() -> void:
	var vp := get_viewport().get_visible_rect().size
	var fs := roundi(CONNECT_FONT * Settings.text_scale)
	connect_label.add_theme_font_size_override("font_size", fs)
	connect_label.text = tr("CONNECTING TO") if _destination != "" else tr("CONNECTING")
	_show_note(vp)
	connect_label.size = Vector2(vp.x, 0.0)
	connect_label.size = Vector2(vp.x, connect_label.get_combined_minimum_size().y)
	# ANIM-R6 B13: the destination on a line of its own under it, large and bright, with the
	# Site's tier icon; the line keeps its bottom at the screen's middle (the bar under it).
	var row_h := _show_destination(vp)
	connect_label.position = Vector2(0.0, vp.y * 0.5 - row_h - connect_label.size.y)
	var w := minf(Motion.amplitude(CONNECT_MOTION), vp.x * 0.8)
	connect_bar.size = Vector2(w, CONNECT_BAR_H)
	connect_bar.position = Vector2((vp.x - w) * 0.5, vp.y * 0.5 + CONNECT_GAP)
	connect_fill.size = Vector2(0.0, CONNECT_BAR_H)
	connect_label.visible = true
	connect_bar.visible = effects_enabled()
	# Whole at once (words, not an effect); it fades with the cover's reveal (`_set_cover`)
	# and stays up at least `jack_connect`'s duration so it can be read.
	connect_label.modulate.a = 1.0
	connect_bar.modulate.a = 1.0
	connect_dest.modulate.a = 1.0
	connect_site.modulate.a = 1.0
	_connect_since = Time.get_ticks_msec()


## ANIM-R6 B13: lays the destination's line out (its name large, the tier icon before it)
## centred with its bottom at the screen's middle; returns its height (0 when none). A long
## name steps its lettering down to fit the screen less its margins.
func _show_destination(vp: Vector2) -> float:
	connect_dest.visible = _destination != ""
	connect_site.visible = false
	if _destination == "":
		return 0.0
	connect_dest.text = _destination.to_upper()
	var fs := roundi(CONNECT_DEST_FONT * Settings.text_scale)
	var low := roundi(CONNECT_FONT * Settings.text_scale)
	var room := vp.x - CONNECT_DEST_MARGIN * 2.0
	var side := 0.0
	var width := 0.0
	while true:
		connect_dest.add_theme_font_size_override("font_size", fs)
		connect_dest.size = Vector2.ZERO
		connect_dest.size = connect_dest.get_combined_minimum_size()
		side = fs * CONNECT_ICON_SHARE if _destination_tier > 0 else 0.0
		width = connect_dest.size.x + (side + CONNECT_ICON_GAP if side > 0.0 else 0.0)
		if width <= room or fs <= low:
			break
		fs -= 1
	var h := maxf(connect_dest.size.y, side)
	var x := (vp.x - width) * 0.5
	var top := vp.y * 0.5 - h
	if side > 0.0:
		connect_site.show_tier(_destination_tier, side, Palette.NET_CYAN)
		connect_site.position = Vector2(x, top + (h - side) * 0.5)
		x += side + CONNECT_ICON_GAP
	connect_dest.position = Vector2(x, top + (h - connect_dest.size.y) * 0.5)
	return h


## The words the jack's cover says now ("CONNECTING TO SCRUB RECORDS"; tests).
func connect_words() -> String:
	return ("%s %s" % [connect_label.text, connect_dest.text]).strip_edges() if connect_dest.visible else connect_label.text


## ANIM-R4 H11a: the note's stamp (RAID INCOMING and the corporation) under the bar,
## centred, tilted; hidden when there is no note.
## ANIM-R5 P15: fitted to the screen: the tilted box never spans more than the screen less
## NOTE_MARGIN a side; the lettering steps down to NOTE_FONT_MIN (x the text size), then a
## line too long wraps between words (a long translation at 1.6 ran off both edges).
func _show_note(vp: Vector2) -> void:
	note_label.visible = _note != ""
	if _note == "":
		return
	note_label.text = _note.to_upper()
	var room := vp.x - NOTE_MARGIN * 2.0
	var top := roundi(NOTE_FONT * Settings.text_scale)
	var low := mini(top, roundi(NOTE_FONT_MIN * Settings.text_scale))
	note_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	var fs := top
	while true:
		note_label.add_theme_font_size_override("font_size", fs)
		note_label.custom_minimum_size = Vector2.ZERO
		note_label.size = Vector2.ZERO
		note_label.size = note_label.get_combined_minimum_size()
		if note_span(note_label.size) <= room or fs <= low:
			break
		fs -= 1
	if note_span(note_label.size) > room:
		# Still too wide at the smallest lettering: the words wrap inside the room.
		var a := deg_to_rad(absf(NOTE_TILT))
		note_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var w := floorf((room - note_label.size.y * sin(a)) / cos(a))
		note_label.custom_minimum_size = Vector2(w, 0.0)
		note_label.size = Vector2(w, 0.0)
		note_label.size = Vector2(w, note_label.get_combined_minimum_size().y)
	note_label.pivot_offset = note_label.size * 0.5
	note_label.rotation_degrees = NOTE_TILT
	note_label.position = Vector2((vp.x - note_label.size.x) * 0.5, vp.y * 0.5 + CONNECT_GAP * 2.0 + CONNECT_BAR_H)
	note_label.modulate.a = 1.0


## ANIM-R5 P15: the smallest the stamp's lettering gets before it wraps (px at text scale
## 1.0), and the screen edge it keeps clear of (px).
const NOTE_FONT_MIN := 22
const NOTE_MARGIN := 16.0


## The width a note box of size `s` spans tilted by NOTE_TILT (px).
static func note_span(s: Vector2) -> float:
	var a := deg_to_rad(absf(NOTE_TILT))
	return s.x * cos(a) + s.y * sin(a)


## When the CONNECTING line came up (msec).
var _connect_since: int = 0
## ANIM-R6: how long (s, wall time) the CONNECTING line last stayed up, measured by the line
## itself from when it showed to when it went (tests read it: a test measuring from when it
## first saw the line lost whatever a slow frame took before that).
var last_connect_shown: float = 0.0


## ANIM-R2 R5: waits until the CONNECTING line has shown `jack_connect`'s duration (game
## time is not needed: it is a reading time). ANIM-R3 B2: a reading time, not an effect, so
## it holds under reduce effects too (the fade's line showed ~2 frames); only the entry
## switched off skips it. Never reached headless (the jack switches at once there).
func _hold_connect() -> void:
	var e := Motion.entry(CONNECT_MOTION)
	if not connect_label.visible or e == null or not e.enabled:
		return
	# ANIM-R4 H11a: a raid's stamp holds its own reading time (at least a second).
	var hold := Motion.seconds(CONNECT_MOTION)
	if note_label.visible:
		hold = maxf(hold, note_hold())
	while Time.get_ticks_msec() - _connect_since < hold * 1000.0:
		await get_tree().process_frame


## The bar's fill: `share` (0..1) of the arrival wait spent.
func _connect_progress(share: float) -> void:
	connect_fill.size = Vector2(connect_bar.size.x * clampf(share, 0.0, 1.0), CONNECT_BAR_H)


## ANIM-R4 H11a: the RAID INCOMING stamp's reading time (s): `raid_incoming_hold`, a
## reading time like CONNECTING's (it holds under reduce effects too; 0 only switched off).
func note_hold() -> float:
	var e := Motion.entry(NOTE_MOTION)
	return e.duration if e != null and e.enabled else 0.0


func _hide_connect() -> void:
	if connect_label.visible:
		last_connect_shown = (Time.get_ticks_msec() - _connect_since) / 1000.0
	note_label.visible = false
	connect_label.visible = false
	connect_bar.visible = false
	connect_dest.visible = false
	connect_site.visible = false
	_destination = ""
	_destination_tier = 0
	_note = ""


## True while the CONNECTING line shows (tests).
func connecting() -> bool:
	return connect_label.visible


## Share of a Heat pulse spent rising (the rest falls).
const HEAT_PULSE_RISE := 0.3


## True while a jack transition runs (views hold their own effects till it ends).
func transitioning() -> bool:
	return _jacking


## True while the jack cover hides the whole screen (the scene switches then).
func cover_opaque() -> bool:
	return _cover_opaque


func _transition(on_switch: Callable, seconds: float, id: StringName) -> void:
	# ANIM-R1 M1: one jack at a time; a second one asked for during it does nothing (its
	# scene change is never made).
	if _jacking:
		return
	if DisplayServer.get_name() == "headless" and not Motion.force_live:
		on_switch.call()
		return
	if effects_enabled() and not Motion.live(id):
		# ANIM-R1 M3: the entry is off: the switch at once (the end state), no cover.
		on_switch.call()
		return
	_set_jacking(true)
	if not effects_enabled():
		await _fade_switch(on_switch)
		_set_jacking(false)
		return
	var inward := id == &"jack_in"
	# The push takes the entry's duration, the reveal `jack_arrive`'s (ANIM-R1 M3).
	var push := Motion.seconds(id) if seconds < 0.0 else seconds
	# ANIM-R6 D3: `jack_arrive` switched off: the new screen shows at once (no reveal).
	var reveal := Motion.seconds_live(ARRIVE_MOTION)
	var e := Motion.entry(id)
	var ae := Motion.entry(ARRIVE_MOTION)
	var zoom := maxf(1.0, Motion.amplitude(id))
	var arrive := 1.0 + (zoom - 1.0) * Motion.amplitude(ARRIVE_MOTION)
	var vp := get_viewport().get_visible_rect().size
	var m := jack_cover.material as ShaderMaterial
	m.set_shader_parameter("screen", vp)
	m.set_shader_parameter("tile", Vector2(NeonCity.TILE_A, NeonCity.TILE_B))
	m.set_shader_parameter("scan", Motion.amplitude(SCANLINE_MOTION))
	m.set_shader_parameter("lattice", Palette.NET_CYAN)
	# ANIM-R3 B5: a calm wave from the CRT (`jack_dissolve`), not scattered hard cells.
	# ANIM-R6 D3: switched off, no wave (the cover comes in whole). The entry's duration is
	# the wave's feather (a width in the shader, not a time).
	var dissolve := Motion.entry(DISSOLVE_MOTION)
	var waves := Motion.live(DISSOLVE_MOTION)
	m.set_shader_parameter("spread", clampf(dissolve.amplitude, 0.0, 1.0) if waves else 0.0)
	m.set_shader_parameter("feather", maxf(dissolve.duration if waves else 0.0, 0.001))
	var old := get_tree().current_scene as Control
	var focus := _jack_focus(old, vp)
	m.set_shader_parameter("focus", focus)
	jack_cover.visible = true
	_set_cover(0.0, 0.0)
	var t0 := Time.get_ticks_msec()
	var tw := create_tween().set_parallel(true)
	tw.tween_method(func(v: float) -> void: _set_cover(v, _roll(t0)), 0.0, 1.0, push).set_ease(e.ease).set_trans(e.trans)
	var old_scale := Vector2.ONE
	if old != null:
		old_scale = old.scale
		old.pivot_offset = focus - old.global_position
		tw.tween_property(old, "scale", Vector2.ONE * (zoom if inward else 1.0 / arrive), push).set_ease(e.ease).set_trans(e.trans)
	await tw.finished
	_set_cover(1.0, _roll(t0))
	_cover_opaque = true
	on_switch.call()
	_show_connect()
	if is_instance_valid(old):
		old.scale = old_scale
	# ANIM-R1 M8: the new scene takes over at the end of this frame and builds its page in
	# the next; the cover stays opaque (its scanlines rolling) until the arriving screen is
	# built and framed (the route on its city, the raid setup's framed map), at most
	# `jack_arrival_wait` seconds, so the cover never lifts onto an empty screen.
	for f in 2:
		await get_tree().process_frame
	await _wait_arrival(func() -> void: _set_cover(1.0, _roll(t0)))
	await _hold_connect()
	var fresh := get_tree().current_scene as Control
	focus = _jack_focus(fresh, vp)
	m.set_shader_parameter("focus", focus)
	var tw2 := create_tween().set_parallel(true)
	if fresh != null:
		fresh.pivot_offset = focus - fresh.global_position
		fresh.scale = Vector2.ONE * (arrive if inward else zoom)
		tw2.tween_property(fresh, "scale", Vector2.ONE, reveal).set_ease(ae.ease).set_trans(ae.trans)
	_cover_opaque = false
	tw2.tween_method(func(v: float) -> void: _set_cover(v, _roll(t0)), 1.0, 0.0, reveal).set_ease(ae.ease).set_trans(ae.trans)
	await tw2.finished
	if is_instance_valid(fresh):
		fresh.scale = Vector2.ONE
	jack_cover.visible = false
	_hide_connect()
	_set_jacking(false)


## ANIM-R1 M8: waits (calling `tick` each frame) until the scene now current says its
## arriving screen is ready (`ARRIVAL_READY_METHOD`), or `jack_arrival_wait` has passed.
func _wait_arrival(tick: Callable = Callable()) -> void:
	# Game time (frame deltas), so a capture at a fixed frame rate waits as the game does.
	var wait := Motion.seconds(ARRIVAL_WAIT_MOTION)
	var left := wait
	while left > 0.0:
		left -= get_process_delta_time()
		_connect_progress(1.0 - left / maxf(wait, 0.001))
		var scene := get_tree().current_scene
		if scene == null or not scene.has_method(ARRIVAL_READY_METHOD) or bool(scene.call(ARRIVAL_READY_METHOD)):
			return
		if tick.is_valid():
			tick.call()
		await get_tree().process_frame


## Jacking on / off (ANIM-R1 M1): the cover takes the mouse and `_input` swallows every
## other press while a jack runs, so the page under it (or arriving) takes no input.
func _set_jacking(on: bool) -> void:
	_jacking = on
	# ANIM-R2 R3: the gate sees every press before the scene's own `_input` handlers.
	if input_gate != null:
		input_gate.blocking = on
		input_gate.stay_last()
	var stop := Control.MOUSE_FILTER_STOP if on else Control.MOUSE_FILTER_IGNORE
	jack_cover.mouse_filter = stop
	transition_rect.mouse_filter = stop


## ANIM-R1 M1: while a jack runs, no press reaches the screens (a second JACK IN, Save &
## Quit or Go to HQ during it would start a second run or ask for a second scene).
func _input(event: InputEvent) -> void:
	if _jacking and not (event is InputEventMouseMotion):
		get_viewport().set_input_as_handled()


## Reduce effects: one short fade through black (`jack_fade_reduced`: `amplitude` of its
## duration spent going dark, the rest coming back), the switch at its darkest, once the
## arriving screen is ready (ANIM-R1 M8). Off: the switch at once.
func _fade_switch(on_switch: Callable) -> void:
	var e := Motion.entry(&"jack_fade_reduced")
	if e == null or not Motion.switched_on(&"jack_fade_reduced"):
		on_switch.call()
		return
	# ANIM-R6 D2: at Motion.speed (it read the raw duration) and with the entry's shape.
	var times := reduced_fade_times()
	var tw := create_tween()
	tw.tween_property(transition_rect, "color:a", 1.0, times.x).set_ease(e.ease).set_trans(e.trans)
	await tw.finished
	_cover_opaque = true
	on_switch.call()
	_show_connect()
	for f in 2:
		await get_tree().process_frame
	await _wait_arrival()
	await _hold_connect()
	_hide_connect()
	_cover_opaque = false
	var tw2 := create_tween()
	tw2.tween_property(transition_rect, "color:a", 0.0, times.y).set_ease(e.ease).set_trans(e.trans)
	await tw2.finished


## ANIM-R6 D2: the reduced jack's seconds at the current speed: x going dark
## (`jack_fade_reduced`'s amplitude share of it), y coming back.
func reduced_fade_times() -> Vector2:
	var total := Motion.seconds(&"jack_fade_reduced")
	var dark := total * clampf(Motion.amplitude(&"jack_fade_reduced"), 0.0, 1.0)
	return Vector2(dark, total - dark)


func _set_cover(progress: float, roll: float) -> void:
	if connect_label.visible and not _cover_opaque:
		# ANIM-R2 R5: the CONNECTING line goes with the cover as it lifts.
		connect_label.modulate.a = progress
		connect_bar.modulate.a = progress
		connect_dest.modulate.a = progress
		connect_site.modulate.a = progress
		note_label.modulate.a = progress
	var m := jack_cover.material as ShaderMaterial
	m.set_shader_parameter("progress", progress)
	m.set_shader_parameter("roll", roll)


## The scanlines' phase: one roll every `jack_scanlines` seconds since `t0` (msec).
func _roll(t0: int) -> float:
	# ANIM-R6 D3: switched off, the scanlines hold still.
	if not Motion.live(SCANLINE_MOTION):
		return 0.0
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
