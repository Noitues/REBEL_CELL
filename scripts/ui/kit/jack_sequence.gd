class_name JackSequence
extends Control
## ART-7 3B / NA-25b r6 (ART_BIBLE 4.6, netrun entry flow ruled 2026-10-15; art-pass A-046: NO wheel, no lens, no hub): the netrun jack along
## the chosen link, over the City Grid:
## 1. the Cell's terminal types `jack --from <A> --to <B>`, routing, handshake, CONNECTED; 2. binary rain falls along the chosen link only;
## 3. the terminal despawns as a CRT collapse, a line then a dot; 4. the dot hands straight to the dive (the switch runs under the night
## sky, holding as a CRT terminal when the load is slow; the street scene's own dive follows). Jack-out is the same chain reversed
## (`play_out`: the dive back ends on the CRT dot opening). One press skips the whole entry (STYLE 5.1). Fx owns the gate, the switch and
## the arrival wait (`play` takes Fx); headless and reduce effects never reach here (Fx takes its own paths). View only: no game state.

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
## The hold's line (`%s` = the building the run builds): a CRT terminal line when the switch is slow (1.2).
const LINE_HOLD := "routing ... building street_%s" # TR
## The CRT hold's look (A-031 item 2, A-037, A-045): the hex dump a column of text that reads at 1:1 (glyphs >= 11 px at 1080p), its alpha
## the newest rows' HOLD_HEX_ALPHA fading to HOLD_HEX_OLDEST_ALPHA at the top, in the rim (accent) cyan at HOLD_HEX_VALUE of its value;
## 3 px scanlines, a clear rim. The glass is the terminal panel's own (NA-25b r6: no hub field to key it to).
const HOLD_HEX_ALPHA := 0.65
const HOLD_HEX_OLDEST_ALPHA := 0.35
const HOLD_HEX_VALUE := 0.75
const HOLD_HEX_SCALE := 1.6
const HOLD_HEX_COLUMN_MARGIN := 48.0
const HOLD_SCAN_STRENGTH := 0.42
const HOLD_EDGE_PX := 4.0
const HOLD_INNER_GLOW := 0.7

## The link (screen px): from its owned end to the Site.
var points: PackedVector2Array = PackedVector2Array()
## Live state the draw reads.
var rain_t: float = -1.0
var switched: bool = false
var skipping: bool = false
## NA-25: the street entry's variant (`link["street"]`): the beats take the `entry_*` times. `night`: the switch happens under the night
## sky so no frame is black.
var street: bool = false
var night: bool = false
var _rain_id: StringName = &"jack_link_rain"
var _hold_line := ""
var _cover_t := 0.0
## True while the switch loads (the CRT hold shows once it passes `jack_hold_crt`).
var _holding := false
## The slow-load CRT hold: a screen of the terminal panel's own glass with its type-on routing line.
var hold: CrtTerminalPanel = null
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


## Plays the sequence for `link` ({from, to: words; points: PackedVector2Array screen px; build: the Site id}); Fx's `switch`
## coroutine (on_switch under the night sky, the arrival wait) runs once the terminal has collapsed to its dot, or at once on a skip.
func play(link: Dictionary, fx: Node, switch: Callable) -> void:
	_hold_saved(fx, true)
	_begin(link)
	if street:
		await _play_street(switch)
		return
	await _play_link(switch)


## The state both directions start from: the link's points, the flags, the terminal and the slow-load hold.
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
	_cover_t = 0.0
	visible = true
	_make_terminal(lines_for(String(link.get("from", "")), String(link.get("to", ""))))
	_hold_line = TranslationServer.translate(LINE_HOLD) % String(link.get("build", link.get("to", "")))
	_build_hold(vp)


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
	await _switch_phase(switch)


## Beat 4 of the chain, shared by the link jack and the street entry: the CRT dot hands straight to the dive. The switch runs under the
## night sky after a frame has drawn it (never the HQ page torn away to black); a slow load becomes a CRT hold (`_process`). No wheel,
## no lens, no hub (A-046).
func _switch_phase(switch: Callable) -> void:
	night = true
	queue_redraw()
	for f in 2:
		if not skipping:
			await get_tree().process_frame
	switched = true
	_holding = true
	await switch.call()
	_holding = false
	_end()


## NA-25 (PIPELINE_SPEC 10, beats 3a-3c): the terminal types over `entry_terminal`, the rain falls over `entry_rain`, the
## terminal collapses over `entry_collapse`; then the dot hands straight to the dive (`_switch_phase`).
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
	await _switch_phase(switch)


## NA-25b r6 (the HQ side of the jack-out, ART_BIBLE 4.6 reversed): the dive has played back to the HQ pose; the switch loads the HQ under
## the night sky, then the CRT comes back on (the collapse reversed: a dot opening to a line, then the glass), the rain rises and the
## lines untype. One press skips to the end (the HQ, no terminal).
func play_out(link: Dictionary, fx: Node, switch: Callable) -> void:
	_hold_saved(fx, true)
	_begin(link)
	street = true
	visible = true
	terminal.visible = false
	_text.visible_characters = -1
	night = true
	queue_redraw()
	for f in 2:
		await get_tree().process_frame
	switched = true
	_holding = true
	await switch.call()
	_holding = false
	hold.visible = false
	night = false
	queue_redraw()
	if skipping:
		_end()
		return
	# The CRT comes back on, the rain rises, the lines untype.
	var col_s := Motion.seconds_live(&"entry_collapse")
	var line_share := clampf(Motion.amplitude(&"entry_collapse"), 0.05, 0.95)
	terminal.pivot_offset = terminal.size * 0.5
	terminal.visible = true
	var t := 0.0
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


## NA-25b r5: the SAVED stamp waits out the transition (frames 4-7 and both HQ-side frames) and shows once the entry ends.
func _hold_saved(fx: Node, on: bool) -> void:
	if on:
		_fx = fx
	if _fx != null and is_instance_valid(_fx) and _fx.has_method(&"hold_saved"):
		_fx.hold_saved(on)
	if not on:
		_fx = null


var _fx: Node = null


func _end() -> void:
	_hold_saved(null, false)
	visible = false
	night = false
	_holding = false
	if hold != null and is_instance_valid(hold):
		hold.visible = false
	if terminal != null and is_instance_valid(terminal):
		terminal.queue_free()
	terminal = null
	queue_redraw()


## True while the switch loads under the night sky.
func covering() -> bool:
	return visible and switched


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


## The CRT hold's panel: the terminal panel's own glass over the screen, the dump a column on the right, hidden until the load runs long.
func _build_hold(vp: Vector2) -> void:
	if hold != null and is_instance_valid(hold):
		hold.queue_free()
	hold = CrtTerminalPanel.new()
	hold.name = "HoldTerminal"
	hold.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hold.size = vp
	hold.visible = false
	hold.text_step = UiTheme.TITLE  # a boot-log line over a whole screen of glass
	hold.caret_block = true
	var cell := CrtTerminalPanel.hex_cell()
	hold.hex_alpha_value = HOLD_HEX_ALPHA
	hold.hex_columns = 1
	hold.hex_scale = HOLD_HEX_SCALE
	hold.hex_origin_x = vp.x - cell.x * HOLD_HEX_SCALE * CrtTerminalPanel.HEX_COLUMN_CELLS - HOLD_HEX_COLUMN_MARGIN
	hold.shader_overrides = {&"hex_tint": hex_color(hold.accent()), &"hex_text_fade": 1.0, &"hex_age_height": vp.y,
		&"hex_age_oldest": HOLD_HEX_OLDEST_ALPHA / HOLD_HEX_ALPHA, &"scan_strength": HOLD_SCAN_STRENGTH, &"edge_px": HOLD_EDGE_PX,
		&"inner_glow": HOLD_INNER_GLOW}
	add_child(hold)


## The hold's dump glyph colour for the rim colour `rim`: its hue and saturation at HOLD_HEX_VALUE of its value.
static func hex_color(rim: Color) -> Color:
	return Color.from_hsv(rim.h, rim.s, rim.v * HOLD_HEX_VALUE)


## True while the CRT hold shows.
func holding() -> bool:
	return hold != null and is_instance_valid(hold) and hold.visible


## While the switch loads under the night sky: a load that passes `jack_hold_crt` becomes a CRT terminal (ART_BIBLE 1.2: glass, scanlines,
## a scrolling hex dump, edge glow, a type-on line and its caret). Bits only fall when real data moves, and nothing here moves any.
func _process(delta: float) -> void:
	if not _holding or hold == null:
		return
	_cover_t += delta
	if Motion.live(&"jack_hold_crt") and _cover_t >= Motion.seconds(&"jack_hold_crt") and not hold.visible:
		hold.visible = true
		hold.type_on(_hold_line)


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
