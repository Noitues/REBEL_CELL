class_name JackSequence
extends Control
## ART-7 3B (ART_BIBLE v2 Â§4.6 transition, LOCKED ~4.4 s, skippable; round 36 "A wheel lens" +
## round 37 `transition_mix`): the netrun jack along the chosen link, over the City Grid:
## 1. the Cell's terminal types `jack --from <A> --to <B>`, routing, handshake, CONNECTED
##    (`jack_terminal_type`); 2. binary rain falls along the chosen link only
##    (`jack_link_rain`); 3. the terminal despawns as a CRT collapse, a line then a dot
##    (`jack_crt_collapse`); 4. the operative's wheel slaps onto the link and spins up
##    (`jack_wheel_slap`, `jack_wheel_spin`); 5. the wheel lens: the wheel swells until its hub
##    fills the screen (the switch happens under it, with the CONNECTING line), then the hub
##    opens onto the run and the ring flies past the camera (`jack_lens`).
## One press skips to the end state (STYLE 5.1): the switch, then the run at once. Fx owns the
## gate, the switch and the arrival wait (`play` takes Fx); headless and reduce effects never
## reach here (Fx takes its own paths). View only: no game state.

## The terminal's lines (keys; %s = the two ends' names).
const LINE_JACK := "> jack --from %s --to %s" # TR
const LINE_ROUTE := "routing via border link ... ok" # TR
const LINE_HANDSHAKE := "handshake ... ok" # TR
const LINE_CONNECTED := "> CONNECTED" # TR
## The terminal's width at text scale 1.0 (px), its gap above the link's midpoint (px), and its
## lettering (px at text scale 1.0).
const TERMINAL_W := 380.0
const TERMINAL_GAP := 30.0
## Rain: lettering (px), the height a bit falls from (px), its white-hot share of its fall.
const RAIN_FONT := 14
const RAIN_DROP := 120.0
const RAIN_HOT := 0.2
## The share of the typing (from its end) the rain overlaps.
const RAIN_LEAD := 0.35
## The class wheel at rest on the link (px radius at text scale 1.0); its hub's share of the radius is the wheel's own
## (`JackWheel.hub_share`).
const WHEEL_R := 80.0
## The hub hold's line (`%s` = the building the run builds): a CRT terminal line when the switch is slow (1.2).
const LINE_HOLD := "routing ... building street_%s" # TR
## The plain breathe under a short hold: the cyan lift's share of the hub (low .. high).
const BREATHE_LOW := 0.10
const BREATHE_HIGH := 0.20
const BREATHE_RATE := 0.004
## The lens: the share of `jack_lens` spent swelling to cover (the rest opens), and how far
## past the screen's half-diagonal the hub swells (share).
const LENS_COVER_SHARE := 0.45
const LENS_OVERSCAN := 1.15
## NA-25b r4 (A-031 item 3): the CRT hold lives on the hub, so it fades out over this share of the opening; the destination's HUD bar and
## subtitle bar stay hidden under the hub until the hole has passed their farthest corner, then come in over this share of the screen's
## diagonal.
const OPEN_HOLD_FADE_SHARE := 0.15
const HUD_FADE_SHARE := 0.04

## The link (screen px): from its owned end to the Site.
var points: PackedVector2Array = PackedVector2Array()
## Live state the draw reads.
var rain_t: float = -1.0
var wheel_scale: float = 0.0
var wheel_turn: float = 0.0
var wheel_at: Vector2 = Vector2.ZERO
var wheel_r: float = 0.0
## The lens opening (0 closed .. 1 open past the screen); < 0 before it opens.
var open_t: float = -1.0
var switched: bool = false
var skipping: bool = false
## NA-25: the street entry's variant (`link["street"]`): the beats take the `entry_*` times, there is no wheel or lens, and the
## switch happens under the night sky (`night`) so no frame is black.
var street: bool = false
var night: bool = false
var _rain_id: StringName = &"jack_link_rain"
## The class wheel, its lens and its hub hold (`JackWheel`).
var wheel_view: JackWheel = null
var _hold_line := ""
var _spin_rate := 0.0
var _cover_t := 0.0
## True while the switch loads under the covering hub (the hub's hold).
var _holding := false
## The destination's HUD controls held under the hub while the lens opens (their rects union), and the hole's radius now.
var _hud_hidden: Array[Control] = []
var _hud_rect: Rect2 = Rect2()
var _hole_r := 0.0
var terminal: CrtTerminalPanel
var _text: Label


func _init() -> void:
	name = "JackSequence"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	visible = false


## The terminal's lines for a jack from `from_word` to `to_word` (translated).
static func lines_for(from_word: String, to_word: String) -> PackedStringArray:
	return PackedStringArray([TranslationServer.translate(LINE_JACK) % [from_word, to_word], TranslationServer.translate(LINE_ROUTE),
		TranslationServer.translate(LINE_HANDSHAKE), TranslationServer.translate(LINE_CONNECTED)])


## Plays the sequence for `link` ({from, to: words; points: PackedVector2Array screen px;
## operative: OperativeState; build: the Site id}); Fx's `switch` coroutine (on_switch under the covering hub, the
## arrival wait) runs once the lens covers the screen, or at once on a skip.
func play(link: Dictionary, fx: Node, switch: Callable) -> void:
	_begin(link)
	if street:
		await _play_street(switch)
		return
	await _play_link(switch)


## The state both directions start from: the link's points, the flags, the terminal and the class wheel.
func _begin(link: Dictionary) -> void:
	points = link.get("points", PackedVector2Array())
	var vp := get_viewport_rect().size
	if points.size() < 2:
		points = PackedVector2Array([vp * Vector2(0.35, 0.6), vp * Vector2(0.65, 0.4)])
	switched = false
	skipping = false
	night = false
	street = bool(link.get("street", false))
	_rain_id = &"entry_rain" if street else &"jack_link_rain"
	rain_t = -1.0
	wheel_scale = 0.0
	open_t = -1.0
	_cover_t = 0.0
	_spin_rate = 0.0
	visible = true
	_make_terminal(lines_for(String(link.get("from", "")), String(link.get("to", ""))))
	_hold_line = TranslationServer.translate(LINE_HOLD) % String(link.get("build", link.get("to", "")))
	if wheel_view != null and is_instance_valid(wheel_view):
		wheel_view.queue_free()
	wheel_view = JackWheel.new()
	add_child(wheel_view)
	wheel_view.setup(link, vp)


func _play_link(switch: Callable) -> void:
	var vp := get_viewport_rect().size
	# 1-2. Typing, the rain joining over its last lines.
	var lines: PackedStringArray = _text.get_meta(&"lines")
	var per_char := Motion.seconds_live(&"jack_terminal_type")
	var pause := Motion.delay_of(&"jack_terminal_type") if Motion.live(&"jack_terminal_type") else 0.0
	var total_chars := _text.text.length()
	var type_s := per_char * total_chars + pause * lines.size()
	var rain_s := Motion.seconds_live(&"jack_link_rain")
	var rain_from := maxf(0.0, type_s - rain_s * RAIN_LEAD)
	var t := 0.0
	while t < maxf(type_s, rain_from + rain_s) and not skipping:
		t += get_process_delta_time()
		_text.visible_characters = _typed_at(t, lines, per_char, pause)
		rain_t = clampf((t - rain_from) / maxf(rain_s, 0.001), 0.0, 1.0) if t >= rain_from else -1.0
		queue_redraw()
		await get_tree().process_frame
	_text.visible_characters = -1
	rain_t = -1.0
	# 3. CRT collapse: a line, then a dot.
	var col_s := Motion.seconds_live(&"jack_crt_collapse")
	var line_share := clampf(Motion.amplitude(&"jack_crt_collapse"), 0.05, 0.95)
	terminal.pivot_offset = terminal.size * 0.5
	t = 0.0
	while t < col_s and not skipping:
		t += get_process_delta_time()
		var u := clampf(t / maxf(col_s, 0.001), 0.0, 1.0)
		if u < line_share:
			terminal.scale = Vector2(1.0, lerpf(1.0, 0.02, u / line_share))
		else:
			terminal.scale = Vector2(lerpf(1.0, 0.0, (u - line_share) / (1.0 - line_share)), 0.02)
		await get_tree().process_frame
	terminal.visible = false
	await _play_wheel(switch)


## Beats 4-5 of the LOCKED chain (ART_BIBLE 4.6), shared by the link jack and the street entry: the operative's class wheel (`JackWheel`,
## the combat's own WheelView) slaps onto the link's Site end like a vinyl sticker (overshoot and settle) and spins up, the wheel lens
## swells until its hub core covers the screen (the switch runs under it, after the covering frame has rendered), then the hub core
## opens onto the run.
func _play_wheel(switch: Callable) -> void:
	var vp := get_viewport_rect().size
	var t := 0.0
	# 4. The wheel slaps onto the link's Site end and spins up.
	wheel_at = points[points.size() - 1]
	wheel_r = WHEEL_R * Settings.text_scale
	var slap_s := Motion.seconds_live(&"jack_wheel_slap")
	var slap := Motion.entry(&"jack_wheel_slap")
	var spin_s := Motion.seconds_live(&"jack_wheel_spin")
	# The spin keeps its rate through the lens (none when switched off).
	var spin_rate := _spin_rate_now(spin_s)
	_spin_rate = spin_rate
	var turns := Motion.amplitude(&"jack_wheel_spin")
	t = 0.0
	while t < slap_s + spin_s and not skipping:
		t += get_process_delta_time()
		var u := clampf(t / maxf(slap_s, 0.001), 0.0, 1.0)
		var e := float(Tween.interpolate_value(0.0, 1.0, u, 1.0, slap.trans, slap.ease)) if slap != null else u
		wheel_scale = lerpf(maxf(1.0, slap.amplitude if slap != null else 1.0), 1.0, e)
		var v := clampf((t - slap_s) / maxf(spin_s, 0.001), 0.0, 1.0)
		wheel_turn = TAU * turns * v * v
		_place(CardFx.slap_scale(u) if slap_s > 0.0 and u < 1.0 else Vector2.ONE)
		await get_tree().process_frame
	wheel_scale = 1.0
	# 5. The lens: swell until the hub core covers the screen, switch under it, open the hub onto the run.
	var lens_s := Motion.seconds(&"jack_lens")
	var cover_s := lens_s * LENS_COVER_SHARE
	var start_at := wheel_at
	var cover_scale := cover_scale_for(vp, wheel_view.hub_share(), wheel_r)
	t = 0.0
	while t < cover_s and not skipping:
		t += get_process_delta_time()
		var u := clampf(t / maxf(cover_s, 0.001), 0.0, 1.0)
		var e := u * u
		wheel_at = start_at.lerp(vp * 0.5, e)
		wheel_scale = lerpf(1.0, cover_scale, e)
		wheel_turn += _spin_rate * get_process_delta_time()
		_place()
		await get_tree().process_frame
	wheel_at = vp * 0.5
	wheel_scale = cover_scale
	_place()
	_cover_t = 0.0
	# The switch runs under a covering frame that has been drawn (the sub-viewport lags the main one by a frame).
	for f in 2:
		if not skipping:
			await get_tree().process_frame
	switched = true
	_holding = true
	await switch.call()
	_holding = false
	if skipping:
		_end()
		return
	# Open: the hub core burns through; the hole grows past the screen.
	var open_s := lens_s - cover_s
	open_t = 0.0
	_hold_hud()
	t = 0.0
	while t < open_s and not skipping:
		t += get_process_delta_time()
		open_t = clampf(t / maxf(open_s, 0.001), 0.0, 1.0)
		wheel_turn += _spin_rate * get_process_delta_time()
		_place()
		wheel_view.set_hold_fade(1.0 - open_t / OPEN_HOLD_FADE_SHARE)
		_reveal_hud(vp)
		await get_tree().process_frame
	if not switched:
		await switch.call()
	_end()


## The wheel's scale (of `WHEEL_R`, `wheel_r` px) at which its hub core covers a screen of `vp` (the lens's end of the swell).
static func cover_scale_for(vp: Vector2, hub_share: float, base_r: float) -> float:
	return vp.length() * 0.5 * LENS_OVERSCAN / maxf(hub_share, 0.01) / maxf(base_r, 1.0)


## The wheel's turn rate (rad/s) while it spins up (0 when the spin does not play).
static func _spin_rate_now(spin_s: float) -> float:
	return TAU * Motion.amplitude(&"jack_wheel_spin") / maxf(Motion.seconds(&"jack_wheel_spin"), 0.001) if spin_s > 0.0 else 0.0


## Draws the wheel for the live state (`wheel_at`, `wheel_scale`, `wheel_turn`, `open_t`): the class wheel through the lens hole.
func _place(squash: Vector2 = Vector2.ONE) -> void:
	if wheel_view == null or wheel_scale <= 0.0:
		return
	var r := wheel_r * wheel_scale
	wheel_view.place(wheel_at, r, wheel_turn, squash)
	wheel_view.set_enlargement(wheel_scale)
	var vp := get_viewport_rect().size
	_hole_r = JackWheel.hole_radius(open_t, r * wheel_view.hub_share(), vp) if open_t >= 0.0 else 0.0
	wheel_view.set_hole(wheel_at, _hole_r)


## NA-25 (PIPELINE_SPEC 10, beats 3a-3c): the terminal types over `entry_terminal`, the rain falls over `entry_rain`, the
## terminal collapses over `entry_collapse`; then the LOCKED chain goes on (`_play_wheel`): the wheel slaps onto the link, the lens swells
## and the switch happens under the covering hub, which opens onto the dive.
func _play_street(switch: Callable) -> void:
	var lines: PackedStringArray = _text.get_meta(&"lines")
	var type_s := Motion.seconds_live(&"entry_terminal")
	var per_char := type_s / maxf(float(_text.text.length()), 1.0)
	var t := 0.0
	while t < type_s and not skipping:
		t += get_process_delta_time()
		_text.visible_characters = _typed_at(t, lines, per_char, 0.0)
		await get_tree().process_frame
	_text.visible_characters = -1
	var rain_s := Motion.seconds_live(&"entry_rain")
	t = 0.0
	while t < rain_s and not skipping:
		t += get_process_delta_time()
		rain_t = clampf(t / maxf(rain_s, 0.001), 0.0, 1.0)
		queue_redraw()
		await get_tree().process_frame
	rain_t = -1.0
	var col_s := Motion.seconds_live(&"entry_collapse")
	var line_share := clampf(Motion.amplitude(&"entry_collapse"), 0.05, 0.95)
	terminal.pivot_offset = terminal.size * 0.5
	t = 0.0
	while t < col_s and not skipping:
		t += get_process_delta_time()
		var u := clampf(t / maxf(col_s, 0.001), 0.0, 1.0)
		if u < line_share:
			terminal.scale = Vector2(1.0, lerpf(1.0, 0.02, u / line_share))
		else:
			terminal.scale = Vector2(lerpf(1.0, 0.0, (u - line_share) / (1.0 - line_share)), 0.02)
		await get_tree().process_frame
	terminal.visible = false
	await _play_wheel(switch)


## NA-25b (the HQ side of the jack-out, ART_BIBLE 4.6 backwards): the lens closes over the dive's last frame (the HQ page), the switch
## loads the HQ under the covering hub, the hub shrinks back to the wheel on the link, the wheel un-slaps, then the CRT comes back on
## (the collapse reversed), the rain rises and the lines untype. One press skips to the end (the HQ, no terminal).
func play_out(link: Dictionary, fx: Node, switch: Callable) -> void:
	_begin(link)
	street = true
	visible = true
	terminal.visible = false
	_text.visible_characters = -1
	var vp := get_viewport_rect().size
	wheel_at = vp * 0.5
	wheel_r = WHEEL_R * Settings.text_scale
	var spin_s := Motion.seconds_live(&"jack_wheel_spin")
	var spin_rate := _spin_rate_now(spin_s)
	_spin_rate = spin_rate
	var lens_s := Motion.seconds_live(&"jack_lens")
	var cover_s := lens_s * LENS_COVER_SHARE
	var open_s := lens_s - cover_s
	var cover_scale := cover_scale_for(vp, wheel_view.hub_share(), wheel_r)
	wheel_scale = cover_scale
	open_t = 1.0
	_place()
	# 1. The lens closes over the street: the hub core's hole shrinks to nothing.
	var t := 0.0
	while t < open_s and not skipping:
		t += get_process_delta_time()
		open_t = 1.0 - clampf(t / maxf(open_s, 0.001), 0.0, 1.0)
		wheel_turn += spin_rate * get_process_delta_time()
		_place()
		await get_tree().process_frame
	open_t = -1.0
	_place()
	_cover_t = 0.0
	# The HQ loads under a covering frame that has been drawn (never the city showing through: `JackWheel.covers`).
	for f in 2:
		if not skipping:
			await get_tree().process_frame
	switched = true
	_holding = true
	await switch.call()
	_holding = false
	wheel_view.show_hold(false)
	wheel_view.set_breathe(0.0)
	if skipping:
		_end()
		return
	# 2. The hub shrinks back to the wheel on the link's Site end.
	var site_at: Vector2 = points[points.size() - 1]
	t = 0.0
	while t < cover_s and not skipping:
		t += get_process_delta_time()
		var e := 1.0 - clampf(t / maxf(cover_s, 0.001), 0.0, 1.0)
		e = e * e
		wheel_at = site_at.lerp(vp * 0.5, e)
		wheel_scale = lerpf(1.0, cover_scale, e)
		wheel_turn += spin_rate * get_process_delta_time()
		_place()
		await get_tree().process_frame
	# 3. The wheel spins down and comes off the link (the slap backwards: it shrinks away).
	var off_s := Motion.seconds_live(&"jack_wheel_slap") + spin_s
	wheel_at = site_at
	t = 0.0
	while t < off_s and not skipping:
		t += get_process_delta_time()
		wheel_scale = 1.0 - clampf(t / maxf(off_s, 0.001), 0.0, 1.0)
		wheel_turn += spin_rate * get_process_delta_time()
		_place()
		await get_tree().process_frame
	wheel_scale = 0.0
	wheel_view.clear()
	if skipping:
		_end()
		return
	# 4. The CRT comes back on, the rain rises, the lines untype.
	var col_s := Motion.seconds_live(&"entry_collapse")
	var line_share := clampf(Motion.amplitude(&"entry_collapse"), 0.05, 0.95)
	terminal.pivot_offset = terminal.size * 0.5
	terminal.visible = true
	t = 0.0
	while t < col_s and not skipping:
		t += get_process_delta_time()
		var u := 1.0 - clampf(t / maxf(col_s, 0.001), 0.0, 1.0)
		if u < line_share:
			terminal.scale = Vector2(1.0, lerpf(1.0, 0.02, u / line_share))
		else:
			terminal.scale = Vector2(lerpf(1.0, 0.0, (u - line_share) / (1.0 - line_share)), 0.02)
		await get_tree().process_frame
	terminal.scale = Vector2.ONE
	var rain_s := Motion.seconds_live(&"entry_rain")
	t = 0.0
	while t < rain_s and not skipping:
		t += get_process_delta_time()
		rain_t = 1.0 - clampf(t / maxf(rain_s, 0.001), 0.0, 1.0)
		queue_redraw()
		await get_tree().process_frame
	rain_t = -1.0
	var type_s := Motion.seconds_live(&"entry_terminal")
	var chars := _text.text.length()
	t = 0.0
	while t < type_s and not skipping:
		t += get_process_delta_time()
		_text.visible_characters = int(float(chars) * (1.0 - clampf(t / maxf(type_s, 0.001), 0.0, 1.0)))
		await get_tree().process_frame
	_end()


## One press: straight to the end state (Fx switches at once if it has not).
func skip() -> void:
	skipping = true


func _end() -> void:
	_restore_hud()
	visible = false
	night = false
	open_t = -1.0
	wheel_scale = 0.0
	_holding = false
	if wheel_view != null and is_instance_valid(wheel_view):
		wheel_view.clear()
	if terminal != null and is_instance_valid(terminal):
		terminal.queue_free()
	terminal = null
	queue_redraw()


## The HUD alpha at a hole of radius `hole_r` centred on `at`: 0 until the hole has passed the farthest corner of `rect`, whole `fade_px`
## later (the pure rule the opening and its test share).
static func hud_alpha(at: Vector2, hole_r: float, rect: Rect2, fade_px: float) -> float:
	var far := 0.0
	for corner in [rect.position, Vector2(rect.end.x, rect.position.y), Vector2(rect.position.x, rect.end.y), rect.end]:
		far = maxf(far, at.distance_to(corner))
	return clampf((hole_r - far) / maxf(fade_px, 0.001), 0.0, 1.0)


## Takes the destination's HUD bar and the subtitle bar (the scene's `hud`, `Dialogue.bar`) out of sight: they stay under the hub until the hole passes.
func _hold_hud() -> void:
	_restore_hud()
	var scene := get_tree().current_scene
	var held: Array[Control] = [Dialogue.bar]  # the subtitle bar docked under the HUD (the autoload's, layer 90: under the lens too)
	if scene != null:
		held.append(scene.get(&"hud") as Control)
	var first := true
	for c in held:
		if c == null or not is_instance_valid(c) or not c.is_visible_in_tree():
			continue
		_hud_rect = c.get_global_rect() if first else _hud_rect.merge(c.get_global_rect())
		first = false
		c.modulate.a = 0.0
		_hud_hidden.append(c)


## Brings the held HUD in as the hole passes it.
func _reveal_hud(vp: Vector2) -> void:
	if _hud_hidden.is_empty():
		return
	var a := hud_alpha(wheel_at, _hole_r, _hud_rect, vp.length() * HUD_FADE_SHARE)
	for c in _hud_hidden:
		if is_instance_valid(c):
			c.modulate.a = a


func _restore_hud() -> void:
	for c in _hud_hidden:
		if is_instance_valid(c):
			c.modulate.a = 1.0
	_hud_hidden.clear()


## True while the lens covers the whole screen (before it opens).
func covering() -> bool:
	return visible and switched and open_t < 0.0


func _typed_at(t: float, lines: PackedStringArray, per_char: float, pause: float) -> int:
	var shown := 0
	var left := t
	for i in lines.size():
		var n := lines[i].length() + (1 if i < lines.size() - 1 else 0)
		var need := n * per_char
		if left < need:
			return shown + int(left / maxf(per_char, 0.0001))
		shown += n
		left -= need + pause
		if left < 0.0:
			return shown
	return -1


func _make_terminal(lines: PackedStringArray) -> void:
	if terminal != null and is_instance_valid(terminal):
		terminal.queue_free()
	var s := Settings.text_scale
	# 1B's CRT terminal (the Cell's own system): glass, scanlines, hex dump, caret; the lines
	# carry their own ">" prompts and type on this sequence's clock.
	terminal = CrtTerminalPanel.new()
	terminal.name = "JackTerminal"
	terminal.prompt = false
	terminal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	terminal.text = "\n".join(lines)
	add_child(terminal)
	_text = terminal.label
	_text.set_meta(&"lines", lines)
	_text.add_theme_color_override("font_color", Palette.CELL_ACID)
	_text.visible_characters = 0
	_text.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	# The panel sets its face in _ready; measure with it now (the window is sized before then).
	_text.add_theme_font_override(&"font", Palette.mono())
	_text.add_theme_font_size_override(&"font_size", UiTheme.font_px(terminal.text_step))
	var tsize := _text.get_combined_minimum_size() + CrtTerminalPanel.PAD * 2.0
	terminal.size = Vector2(maxf(TERMINAL_W * s, tsize.x), tsize.y)
	var mid := (points[0] + points[points.size() - 1]) * 0.5
	var vp := get_viewport_rect().size
	var at := mid - Vector2(terminal.size.x * 0.5, terminal.size.y + TERMINAL_GAP * s)
	terminal.position = at.clamp(Vector2.ZERO, (vp - terminal.size).max(Vector2.ZERO))


## While the hub core covers the screen (the switch loads): the wheel keeps turning, a short hold breathes, and a hold that passes
## `jack_hub_crt` becomes a CRT terminal (ART_BIBLE 1.2: navy glass, scanlines, a scrolling hex dump, edge glow, a type-on line and its
## caret). Bits only fall when real data moves, and nothing here moves any, so none do.
func _process(delta: float) -> void:
	if not _holding or wheel_view == null:
		return
	_cover_t += delta
	wheel_turn += _spin_rate * delta
	_place()
	var crt_after := Motion.seconds(&"jack_hub_crt")
	if Motion.live(&"jack_hub_crt") and _cover_t >= crt_after:
		wheel_view.show_hold(true, _hold_line)
		wheel_view.set_breathe(0.0)
	else:
		var breathe := 0.5 + 0.5 * sin(float(Time.get_ticks_msec()) * BREATHE_RATE)
		wheel_view.set_breathe(BREATHE_LOW + (BREATHE_HIGH - BREATHE_LOW) * breathe)


func _draw() -> void:
	if night:
		draw_rect(Rect2(Vector2.ZERO, get_viewport_rect().size), Palette.NIGHT_SKY)
	if rain_t >= 0.0:
		_draw_rain()


## Binary rain along the link: bits fall onto it, white-hot first, flipping 0/1.
func _draw_rain() -> void:
	var f := Palette.mono()
	var s := Settings.text_scale
	var fs := roundi(RAIN_FONT * s)
	var total := 0.0
	for i in points.size() - 1:
		total += points[i].distance_to(points[i + 1])
	var count := maxi(4, roundi(total / 100.0 * Motion.amplitude(_rain_id)))
	for i in count:
		var h := absi(hash(i * 7919))
		var u := float(h % 1000) / 1000.0
		var start := float((h >> 10) % 1000) / 1000.0 * 0.6
		var fall := clampf((rain_t - start) / 0.4, 0.0, 1.0)
		if fall <= 0.0:
			continue
		var p := _along(u * total)
		var y := p.y - RAIN_DROP * s * (1.0 - fall)
		var bit := "1" if (h + int(rain_t * 20.0)) % 2 == 0 else "0"
		var col := Palette.TEXT_HI if fall < RAIN_HOT else Palette.CELL_ACID
		var a := 1.0 - maxf(0.0, fall - 0.8) / 0.2
		f.draw_string_outline(get_canvas_item(), Vector2(p.x - fs * 0.3, y), bit, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, roundi(3.0 * s), Color(Palette.NIGHT_SKY, a))
		f.draw_string(get_canvas_item(), Vector2(p.x - fs * 0.3, y), bit, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, a))


func _along(d: float) -> Vector2:
	for i in points.size() - 1:
		var seg := points[i].distance_to(points[i + 1])
		if d <= seg:
			return points[i].lerp(points[i + 1], d / maxf(seg, 0.001))
		d -= seg
	return points[points.size() - 1]
