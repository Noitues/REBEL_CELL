extends RcLookLabStage
## LOOK-TOOLBOX module 14 in the lab: the CRT / terminal glass. One panel per preset (terminal, firmware, schematics,
## dispatch, corp, ui_panel, fx_overlay, neon_sketch), drawn by a lab shader made of rc_crt.gdshaderinc's functions at a
## FIXED clock (flicker at CLOCK_S, the roll band at BAND_AT), so a capture is repeatable. Under each panel three probe
## strips, shader over mirror chips (RcLookCrt): the scanline pattern down 24 pixel rows, the flicker over one second, the
## roll's profile down the panel. The reduce-effects flag (quality state) applies the config's convention (RcLookCrt.resolve).
## A parity check at the foot draws the game's own crt_terminal.gdshader and the lab shader with the same numbers at the same
## spot in turn (reduce effects frozen in the global so its clock never matters, the roll off) and prints the largest pixel
## difference per pass. Static: the stage never reads TIME.

const MARGIN := Vector2(40.0, 56.0)
const GAP := Vector2(24.0, 18.0)
const COLUMNS := 4
const LABEL_SIZE := 13
const PANEL_H := 92.0
const PROBE_H := 8.0
const PROBE_CHIPS := 24
const PROBE_ROWS := 3
## The fixed clock: the flicker's time (s) and the roll band's position (0..1).
const CLOCK_S := 0.37
const BAND_AT := 0.5
## Parity pair: size (px) and the mixed 8-bit difference reported.
const PARITY_SIZE := Vector2(260.0, 90.0)
## Frames between parity steps; the passes compared (bit 0 glass, bit 1 overlay) and their names.
const PARITY_STEP := 6
const PARITY_SHOTS: Array[int] = [1, 2, 3]
const PARITY_NAMES: Array[String] = ["glass", "overlay", "both"]
const PARITY_BACKDROP := Color(0.06, 0.07, 0.1)

const PANEL_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_crt.gdshaderinc"
uniform int mode = 0;
uniform vec4 panel = vec4(0.0, 0.0, 100.0, 100.0);
uniform vec4 glass_top : source_color;
uniform vec4 glass_bottom : source_color;
uniform vec4 accent : source_color;
uniform float edge_px = 1.5;
uniform float glow_px = 10.0;
uniform float glow_strength = 0.45;
uniform float inner_glow = 0.18;
uniform float inner_glow_px = 10.0;
uniform float wash_px = 18.0;
uniform float scan_px = 3.0;
uniform float scan_phase = 0.08;
uniform float scan_strength = 0.1;
uniform float scan_sine = 0.0;
uniform float flicker_amount = 0.0;
uniform float flicker_rate = 43.0;
uniform float clock = 0.0;
uniform float roll_strength = 0.03;
uniform float roll_width = 0.08;
uniform float roll_band = 0.5;
uniform float notch_px = 14.0;
uniform float corner_px = 3.0;
uniform float vig_px = 28.0;
uniform float vig_floor = 0.78;
uniform float screen_vig = 0.0;
uniform vec2 screen_vig_range = vec2(0.45, 0.85);
varying vec2 local_px;
void vertex() {
	local_px = VERTEX;
}
float panel_sd(vec2 p) {
	vec2 c = panel.xy + panel.zw * 0.5;
	vec2 q = abs(p - c) - panel.zw * 0.5 + vec2(corner_px);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - corner_px;
}
void fragment() {
	vec2 p = local_px;
	float sd = panel_sd(p);
	vec4 col = vec4(0.0);
	if (mode == 0) {
		if (sd <= 0.0) {
			float t = clamp((p.y - panel.y) / max(panel.w, 1.0), 0.0, 1.0);
			vec4 g = mix(glass_top, glass_bottom, t);
			g.rgb *= rcl_crt_vignette_sd(sd, vig_px, vig_floor);
			g.rgb += accent.rgb * (1.0 - smoothstep(0.0, wash_px, -sd)) * inner_glow * 0.5;
			col = g;
			float edge = 1.0 - smoothstep(edge_px - 0.5, edge_px + 0.5, -sd);
			col = mix(col, vec4(accent.rgb, 1.0), edge);
			vec2 n = p - panel.xy;
			if (n.x + n.y < notch_px) {
				col = vec4(accent.rgb * 0.85, 1.0);
			}
		} else {
			col = vec4(accent.rgb, rcl_crt_glow(sd, glow_px, glow_strength));
		}
	} else {
		if (sd <= 0.0) {
			float line = mix(rcl_crt_scan((p.y - panel.y), scan_px, scan_phase), rcl_crt_scan_sine((p.y - panel.y) / max(panel.w, 1.0), scan_px), scan_sine);
			float y = (p.y - panel.y) / max(panel.w, 1.0);
			float roll = rcl_crt_roll(y, roll_band, roll_width) * roll_strength;
			float ig = (1.0 - smoothstep(0.0, inner_glow_px, -sd)) * inner_glow;
			col = vec4(0.0, 0.0, 0.0, scan_strength * line);
			col = mix(col, vec4(accent.rgb, 1.0), clamp(roll + ig * 0.5, 0.0, 1.0) * 0.6);
			col.a = max(col.a, (roll + ig * 0.5) * 0.6);
			// the flicker and the screen vignette darken what is under (alpha black over the glass)
			float gain = rcl_crt_flicker(clock, flicker_rate, flicker_amount) * rcl_crt_vignette_uv((p - panel.xy) / panel.zw, screen_vig, screen_vig_range.x, screen_vig_range.y);
			col.rgb *= gain;
			col.a = max(col.a, 1.0 - gain);
		}
	}
	COLOR = col;
}
"""

## A probe strip: shader draws what the mirror's chips below draw. kind 0 scan pattern down rows, 1 flicker over a second, 2 roll.
const PROBE_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_crt.gdshaderinc"
uniform int kind = 0;
uniform float chips = 24.0;
uniform float period = 3.0;
uniform float phase = 0.08;
uniform float strength = 0.1;
uniform float amount = 0.0;
uniform float rate = 43.0;
uniform float band = 0.5;
uniform float width = 0.08;
uniform float roll_gain = 0.03;
void fragment() {
	float i = floor(UV.x * chips);
	float v;
	if (kind == 0) {
		v = 1.0 - strength * rcl_crt_scan(i + 0.5, period, phase);
	} else if (kind == 1) {
		v = rcl_crt_flicker((i + 0.5) / chips, rate, amount);
	} else {
		v = 1.0 - roll_gain * rcl_crt_roll((i + 0.5) / chips, band, width);
	}
	COLOR = vec4(vec3(v), 1.0);
}
"""

const GAME_SHADER := "res://shaders/kit/crt_terminal.gdshader"

var _view_re := false
var _rects: Array[ColorRect] = []
var _preset_names: Array[StringName] = []
var _probes: Array[ShaderMaterial] = []
var _chip_rows: Array = []
var _label_reduce: Label
var _parity_rects: Array = []
var _parity_imgs: Array = [null, null, null, null, null, null]
var _parity_origin := Vector2i.ZERO
var _parity_label: Label
var _parity_frames := 0


func _ready() -> void:
	var view := get_viewport_rect().size
	var col_w := (view.x - MARGIN.x * 2.0 - GAP.x * (COLUMNS - 1)) / COLUMNS
	var row_h := LABEL_SIZE + 6.0 + PANEL_H + 8.0 + PROBE_ROWS * (PROBE_H * 2.0 + 3.0) + GAP.y
	var names := RcLookCrt.REQUIRED
	for i in names.size():
		var n: StringName = names[i]
		_preset_names.append(n)
		var at := Vector2(MARGIN.x + (i % COLUMNS) * (col_w + GAP.x), MARGIN.y + (i / COLUMNS) * row_h)
		var l := _label(String(n), at)
		var rect := Vector2(col_w, PANEL_H)
		_panel_rect(at + Vector2(0.0, LABEL_SIZE + 6.0), rect, 0)
		_panel_rect(at + Vector2(0.0, LABEL_SIZE + 6.0), rect, 1)
		_probe_rows(n, at + Vector2(0.0, LABEL_SIZE + 6.0 + PANEL_H + 8.0), col_w)
		l.text = String(n)
	# the game shader reads rc_time(TIME) (its hex dump scrolls): freeze it for the parity pair
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 1.0)
	_label_reduce = _label("", Vector2(MARGIN.x, 18.0))
	_parity(Vector2(MARGIN.x, MARGIN.y + 2.0 * row_h + 10.0))
	apply(&"night", RcLookQualityState.make(2))


func apply(_time: StringName, quality: RcLookQualityState) -> void:
	_view_re = quality != null and quality.reduce_effects
	for i in _preset_names.size():
		var p := RcLookCrt.preset(_preset_names[i])
		var r := RcLookCrt.resolve(p, _view_re)
		for rc: ColorRect in [_rects[i * 2], _rects[i * 2 + 1]]:
			_fill(rc, p, r)
		for k in PROBE_ROWS:
			_fill_probe(_probes[i * PROBE_ROWS + k], p, r, k)
			_fill_chips(_chip_rows[i * PROBE_ROWS + k], p, r, k)
	_label_reduce.text = "CRT glass at a fixed clock (flicker %.2f s, band %.2f). Reduce effects %s%s" % [CLOCK_S, BAND_AT,
			"ON: convention %s" % RcLookCrt.Reduce.keys()[RcLookCrt.default_config().reduce] if _view_re else "off",
			". Probes: shader over mirror."]


func settle_frames() -> int:
	return 12


func _panel_rect(at: Vector2, size_px: Vector2, mode: int) -> ShaderMaterial:
	var rc := ColorRect.new()
	rc.position = at
	rc.size = size_px
	var m := ShaderMaterial.new()
	m.shader = _shader(PANEL_CODE)
	m.set_shader_parameter(&"mode", mode)
	rc.material = m
	add_child(rc)
	_rects.append(rc)
	return m


static func _fill(rect: ColorRect, p: RcLookCrtPreset, r: Dictionary) -> void:
	var m := rect.material as ShaderMaterial
	var sz := rect.size
	var inset := p.glow_px
	m.set_shader_parameter(&"panel", Vector4(inset, inset, sz.x - inset * 2.0, sz.y - inset * 2.0))
	# HIDE hides the overlay pass only (fx.gd hides its scanline layer); the glass under the words is the art itself
	rect.visible = bool(r[&"visible"]) or int(m.get_shader_parameter(&"mode")) == 0
	m.set_shader_parameter(&"glass_top", p.glass_top)
	m.set_shader_parameter(&"glass_bottom", p.glass_bottom)
	m.set_shader_parameter(&"accent", p.accent)
	m.set_shader_parameter(&"edge_px", p.edge_px)
	m.set_shader_parameter(&"glow_px", p.glow_px)
	m.set_shader_parameter(&"glow_strength", p.glow_strength)
	m.set_shader_parameter(&"inner_glow", p.inner_glow)
	m.set_shader_parameter(&"inner_glow_px", p.inner_glow_px)
	m.set_shader_parameter(&"wash_px", p.wash_px)
	m.set_shader_parameter(&"scan_px", p.scan_px if p.scan_sine_density == 0.0 else p.scan_sine_density)
	m.set_shader_parameter(&"scan_phase", p.scan_phase)
	m.set_shader_parameter(&"scan_strength", r[&"scan_strength"])
	m.set_shader_parameter(&"scan_sine", 0.0 if p.scan_sine_density == 0.0 else 1.0)
	m.set_shader_parameter(&"flicker_amount", r[&"flicker"])
	m.set_shader_parameter(&"flicker_rate", p.flicker_rate)
	m.set_shader_parameter(&"clock", CLOCK_S)
	m.set_shader_parameter(&"roll_strength", r[&"roll_strength"])
	m.set_shader_parameter(&"roll_width", p.roll_width)
	m.set_shader_parameter(&"roll_band", BAND_AT)
	m.set_shader_parameter(&"notch_px", p.notch_px)
	m.set_shader_parameter(&"corner_px", p.corner_px)
	m.set_shader_parameter(&"vig_px", p.vignette_px)
	m.set_shader_parameter(&"vig_floor", p.vignette_floor)
	m.set_shader_parameter(&"screen_vig", r[&"screen_vignette"])
	m.set_shader_parameter(&"screen_vig_range", Vector2(p.screen_vignette_inner, p.screen_vignette_outer))


func _probe_rows(_n: StringName, at: Vector2, w: float) -> void:
	for k in PROBE_ROWS:
		var y := at.y + k * (PROBE_H * 2.0 + 3.0)
		var strip := ColorRect.new()
		strip.position = Vector2(at.x, y)
		strip.size = Vector2(w, PROBE_H)
		var m := ShaderMaterial.new()
		m.shader = _shader(PROBE_CODE)
		m.set_shader_parameter(&"kind", k)
		strip.material = m
		add_child(strip)
		_probes.append(m)
		var chips: Array[ColorRect] = []
		for c in PROBE_CHIPS:
			var x0 := roundf(at.x + w * float(c) / PROBE_CHIPS)
			var chip := ColorRect.new()
			chip.position = Vector2(x0, y + PROBE_H)
			chip.size = Vector2(roundf(at.x + w * float(c + 1) / PROBE_CHIPS) - x0, PROBE_H)
			add_child(chip)
			chips.append(chip)
		_chip_rows.append(chips)


func _fill_probe(m: ShaderMaterial, p: RcLookCrtPreset, r: Dictionary, k: int) -> void:
	m.set_shader_parameter(&"chips", float(PROBE_CHIPS))
	m.set_shader_parameter(&"period", p.scan_px)
	m.set_shader_parameter(&"phase", p.scan_phase)
	m.set_shader_parameter(&"strength", maxf(float(r[&"scan_strength"]), 0.0) * PROBE_GAIN)
	m.set_shader_parameter(&"amount", float(r[&"flicker"]) * PROBE_GAIN)
	m.set_shader_parameter(&"rate", p.flicker_rate)
	m.set_shader_parameter(&"band", BAND_AT)
	m.set_shader_parameter(&"width", p.roll_width)
	m.set_shader_parameter(&"roll_gain", float(r[&"roll_strength"]) * PROBE_GAIN)


## The probes exaggerate the small strengths so a 1 % difference is visible on the sheet (the shader and its chips both).
const PROBE_GAIN := 6.0


func _fill_chips(chips: Array, p: RcLookCrtPreset, r: Dictionary, k: int) -> void:
	for c in PROBE_CHIPS:
		var v: float
		match k:
			0:
				v = 1.0 - float(r[&"scan_strength"]) * PROBE_GAIN * RcLookCrt.scan(c + 0.5, p.scan_px, p.scan_phase)
			1:
				v = RcLookCrt.flicker((c + 0.5) / PROBE_CHIPS, p.flicker_rate, float(r[&"flicker"]) * PROBE_GAIN)
			_:
				v = 1.0 - float(r[&"roll_strength"]) * PROBE_GAIN * RcLookCrt.roll((c + 0.5) / PROBE_CHIPS, BAND_AT, p.roll_width)
		(chips[c] as ColorRect).color = Color(v, v, v)


## The parity check: the game's crt_terminal.gdshader and the lab shader draw the same numbers at the SAME screen position
## on the same opaque backdrop, one after the other (the lab set and Fx's screen overlay shade the screen by x, so a pair
## side by side would differ by that alone). Compared per pass (glass, overlay) and together.
func _parity(at: Vector2) -> void:
	_label("parity: crt_terminal.gdshader vs lab shader, terminal preset, same spot in turn (max channel difference below)", at)
	var p := RcLookCrt.preset(&"terminal")
	var inset := p.glow_px
	var origin := at + Vector2(0.0, LABEL_SIZE + 6.0)
	_parity_origin = Vector2i(origin)
	var back := ColorRect.new()
	back.color = PARITY_BACKDROP
	back.position = origin
	back.size = PARITY_SIZE
	add_child(back)
	for side in 2:
		var pair: Array[ColorRect] = []
		for mode in 2:
			var rc := ColorRect.new()
			rc.position = origin
			rc.size = PARITY_SIZE
			rc.visible = false
			var m := ShaderMaterial.new()
			m.shader = load(GAME_SHADER) if side == 0 else _shader(PANEL_CODE)
			m.set_shader_parameter(&"mode", mode)
			m.set_shader_parameter(&"panel", Vector4(inset, inset, PARITY_SIZE.x - inset * 2.0, PARITY_SIZE.y - inset * 2.0))
			m.set_shader_parameter(&"glass_top", p.glass_top)
			m.set_shader_parameter(&"glass_bottom", p.glass_bottom)
			m.set_shader_parameter(&"accent", p.accent)
			m.set_shader_parameter(&"roll_strength", 0.0)
			if side == 0:
				m.set_shader_parameter(&"hexdump", 0.0)
			else:
				m.set_shader_parameter(&"scan_strength", p.scan_strength)
				m.set_shader_parameter(&"scan_px", p.scan_px)
				m.set_shader_parameter(&"scan_phase", p.scan_phase)
			rc.material = m
			add_child(rc)
			pair.append(rc)
		_parity_rects.append(pair)
	_parity_label = _label("", at + Vector2(0.0, LABEL_SIZE + 6.0 + PARITY_SIZE.y + 6.0))


func _process(_dt: float) -> void:
	if _parity_rects.is_empty():
		return
	_parity_frames += 1
	if _parity_frames % PARITY_STEP != 0:
		return
	var step := _parity_frames / PARITY_STEP - 1
	if step > 0 and step <= PARITY_SHOTS.size() * 2:
		var s := (step - 1) / 2
		var side := (step - 1) % 2
		_parity_imgs[s * 2 + side] = get_viewport().get_texture().get_image()
	if step < PARITY_SHOTS.size() * 2:
		var s := step / 2
		var side := step % 2
		for k in 2:
			for j in 2:
				(_parity_rects[k][j] as ColorRect).visible = k == side and (PARITY_SHOTS[s] & (1 << j)) != 0
		return
	var out := PackedStringArray()
	var overall := 0
	for s in PARITY_SHOTS.size():
		var worst := 0
		for y in int(PARITY_SIZE.y):
			for x in int(PARITY_SIZE.x):
				var ca := (_parity_imgs[s * 2] as Image).get_pixel(_parity_origin.x + x, _parity_origin.y + y)
				var cb := (_parity_imgs[s * 2 + 1] as Image).get_pixel(_parity_origin.x + x, _parity_origin.y + y)
				for ch in 3:
					worst = maxi(worst, absi(int(roundf(ca[ch] * 255.0)) - int(roundf(cb[ch] * 255.0))))
		out.append("%s %d" % [PARITY_NAMES[s], worst])
		overall = maxi(overall, worst)
	for rc_pair: Array in _parity_rects:
		(rc_pair[0] as ColorRect).visible = true
		(rc_pair[1] as ColorRect).visible = true
	(_parity_rects[0][0] as ColorRect).visible = false
	(_parity_rects[0][1] as ColorRect).visible = false
	_parity_label.text = "parity max channel difference / 255: %s" % ", ".join(out)
	print("crt_stage: parity max diff ", overall, " (", ", ".join(out), ")")
	_parity_rects.clear()


## The lab runs with effects on; Fx sets the global in the game.
func _exit_tree() -> void:
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 0.0)


func _label(text: String, at: Vector2) -> Label:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
	add_child(l)
	return l


static func _shader(code: String) -> Shader:
	var s := Shader.new()
	s.code = code
	return s
