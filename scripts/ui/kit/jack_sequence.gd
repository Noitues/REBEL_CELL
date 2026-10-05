class_name JackSequence
extends Control
## ART-7 3B (ART_BIBLE v2 §4.6 transition, LOCKED ~4.4 s, skippable; round 36 "A wheel lens" +
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
## The wheel at rest on the link (px radius at text scale 1.0), its hub's share of the radius,
## the ring's ink keyline (px).
const WHEEL_R := 46.0
const HUB_SHARE := 0.55
const WHEEL_KEYLINE := 3.0
## The lens: the share of `jack_lens` spent swelling to cover (the rest opens), and how far
## past the screen's half-diagonal the hub swells (share).
const LENS_COVER_SHARE := 0.45
const LENS_OVERSCAN := 1.15

## The link (screen px): from its owned end to the Site.
var points: PackedVector2Array = PackedVector2Array()
## The wheel's slice colours, in slot order.
var slices: Array[Color] = []
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
## slices: Array[Color]}); Fx's `switch` coroutine (on_switch under the covering hub, the
## arrival wait) runs once the lens covers the screen, or at once on a skip.
func play(link: Dictionary, fx: Node, switch: Callable) -> void:
	points = link.get("points", PackedVector2Array())
	slices.clear()
	for c in link.get("slices", []):
		slices.append(c)
	if slices.is_empty():
		slices.assign([Palette.CELL_PINK, Palette.NET_CYAN, Palette.SLICE_HOTFIX, Palette.CELL_PINK, Palette.NET_CYAN, Palette.SLICE_NULL])
	var vp := get_viewport_rect().size
	if points.size() < 2:
		points = PackedVector2Array([vp * Vector2(0.35, 0.6), vp * Vector2(0.65, 0.4)])
	switched = false
	skipping = false
	rain_t = -1.0
	wheel_scale = 0.0
	open_t = -1.0
	visible = true
	_make_terminal(lines_for(String(link.get("from", "")), String(link.get("to", ""))))
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
	# 4. The wheel slaps onto the link's Site end and spins up.
	wheel_at = points[points.size() - 1]
	wheel_r = WHEEL_R * Settings.text_scale
	var slap_s := Motion.seconds_live(&"jack_wheel_slap")
	var slap := Motion.entry(&"jack_wheel_slap")
	var spin_s := Motion.seconds_live(&"jack_wheel_spin")
	# The spin keeps its rate through the lens (none when switched off).
	var spin_rate := TAU * Motion.amplitude(&"jack_wheel_spin") / maxf(Motion.seconds(&"jack_wheel_spin"), 0.001) if spin_s > 0.0 else 0.0
	var turns := Motion.amplitude(&"jack_wheel_spin")
	t = 0.0
	while t < slap_s + spin_s and not skipping:
		t += get_process_delta_time()
		var u := clampf(t / maxf(slap_s, 0.001), 0.0, 1.0)
		var e := float(Tween.interpolate_value(0.0, 1.0, u, 1.0, slap.trans, slap.ease)) if slap != null else u
		wheel_scale = lerpf(maxf(1.0, slap.amplitude if slap != null else 1.0), 1.0, e)
		var v := clampf((t - slap_s) / maxf(spin_s, 0.001), 0.0, 1.0)
		wheel_turn = TAU * turns * v * v
		queue_redraw()
		await get_tree().process_frame
	wheel_scale = 1.0
	# 5. The lens: swell until the hub covers the screen, switch under it, open onto the run.
	var lens_s := Motion.seconds(&"jack_lens")
	var cover_s := lens_s * LENS_COVER_SHARE
	var start_at := wheel_at
	var cover_r := vp.length() * 0.5 * LENS_OVERSCAN / HUB_SHARE
	t = 0.0
	while t < cover_s and not skipping:
		t += get_process_delta_time()
		var u := clampf(t / maxf(cover_s, 0.001), 0.0, 1.0)
		var e := u * u
		wheel_at = start_at.lerp(vp * 0.5, e)
		wheel_scale = lerpf(1.0, cover_r / maxf(wheel_r, 1.0), e)
		wheel_turn += spin_rate * get_process_delta_time()
		queue_redraw()
		await get_tree().process_frame
	wheel_at = vp * 0.5
	wheel_scale = cover_r / maxf(wheel_r, 1.0)
	queue_redraw()
	switched = true
	await switch.call()
	if skipping:
		_end()
		return
	# Open: the hub becomes a hole onto the run; the ring flies past.
	var open_s := lens_s - cover_s
	open_t = 0.0
	t = 0.0
	while t < open_s and not skipping:
		t += get_process_delta_time()
		open_t = clampf(t / maxf(open_s, 0.001), 0.0, 1.0)
		wheel_turn += spin_rate * get_process_delta_time()
		queue_redraw()
		await get_tree().process_frame
	if not switched:
		await switch.call()
	_end()


## One press: straight to the end state (Fx switches at once if it has not).
func skip() -> void:
	skipping = true


func _end() -> void:
	visible = false
	open_t = -1.0
	wheel_scale = 0.0
	if terminal != null and is_instance_valid(terminal):
		terminal.queue_free()
	terminal = null
	queue_redraw()


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


func _draw() -> void:
	if rain_t >= 0.0:
		_draw_rain()
	if wheel_scale > 0.0:
		_draw_wheel()


## Binary rain along the link: bits fall onto it, white-hot first, flipping 0/1.
func _draw_rain() -> void:
	var f := Palette.mono()
	var s := Settings.text_scale
	var fs := roundi(RAIN_FONT * s)
	var total := 0.0
	for i in points.size() - 1:
		total += points[i].distance_to(points[i + 1])
	var count := maxi(4, roundi(total / 100.0 * Motion.amplitude(&"jack_link_rain")))
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


## The operative's wheel: slices round a dark hub; while the lens opens the hub is a hole onto
## the run and the ring flies outward past the screen.
func _draw_wheel() -> void:
	var r := wheel_r * wheel_scale
	var hub := r * HUB_SHARE
	var k := maxf(1.0, wheel_scale)
	if open_t >= 0.0:
		var vp := get_viewport_rect().size
		var far := vp.length() * 0.5 * LENS_OVERSCAN
		var e := 1.0 - pow(1.0 - open_t, 3.0)
		hub = lerpf(0.0, far * 1.6, e)
		r = hub / HUB_SHARE
	var n := slices.size()
	for i in n:
		var a0 := wheel_turn + TAU * i / n
		var a1 := wheel_turn + TAU * (i + 1) / n
		var mid_r := (hub + r) * 0.5
		var w := r - hub
		draw_arc(wheel_at, mid_r, a0, a1, 24, slices[i], w, false)
		var edge := Vector2.from_angle(a0)
		draw_line(wheel_at + edge * hub, wheel_at + edge * r, Palette.INK, WHEEL_KEYLINE * k * 0.5)
	draw_arc(wheel_at, r, 0, TAU, 64, Palette.INK, WHEEL_KEYLINE * k)
	draw_arc(wheel_at, hub, 0, TAU, 64, Palette.INK, WHEEL_KEYLINE * k)
	if open_t < 0.0:
		draw_circle(wheel_at, hub, Palette.NIGHT_SKY)
		draw_arc(wheel_at, hub * 0.8, 0, TAU, 48, Color(Palette.NET_CYAN, 0.5), WHEEL_KEYLINE * k * 0.5)
