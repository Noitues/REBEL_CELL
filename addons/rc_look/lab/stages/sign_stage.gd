extends RcLookLabStage
## LOOK-TOOLBOX module 11 in the lab: should neon tubes get a white-hot core (DECISIONS: the designer's open question)?
## Three panels, one per preset ("flat" today's signs, "lighten" the tube lightened toward its own core (white tinted 0.15 toward the tube), "hot" a
## thin hot core), each the word OPEN in neon tubes (pink, cyan, lime, pink) on a dark wall: the tube by rcl_tube_cov,
## its centre by the preset (rcl_hot_to x rcl_tube_core), its glow by rcl_fall_exp added under rc_light's soft ceiling
## (rcl_light_add), the 2D bloom (rc_bloom) over all at the capture's tier. Under each panel: the tube's cross-section
## (shader) over the GDScript mirror (RcLookSign.tube_color) as chips. Static: no flicker on the sheet.
## Day / night change the wall.

## Layout (px): margins, gap, label size, the strip's height and chips, the word's box inside a panel (share).
const MARGIN := Vector2(60.0, 70.0)
const GAP := 40.0
const LABEL_SIZE := 15
const STRIP_H := 40.0
const CHIPS := 24
const WORD_BOX := Rect2(0.08, 0.3, 0.84, 0.4)
## The ring's sides; the letters' stroke layout in a letter cell (share of the cell: x0, y0, x1, y1 per segment).
const RING_SIDES := 14
const LETTER_GAP := 0.18
const P_SEGS: Array[Vector4] = [Vector4(0.1, 0.0, 0.1, 1.0), Vector4(0.1, 0.0, 0.75, 0.0), Vector4(0.75, 0.0, 0.9, 0.15),
		Vector4(0.9, 0.15, 0.9, 0.4), Vector4(0.9, 0.4, 0.75, 0.55), Vector4(0.75, 0.55, 0.1, 0.55)]
const E_SEGS: Array[Vector4] = [Vector4(0.15, 0.0, 0.15, 1.0), Vector4(0.15, 0.0, 0.9, 0.0), Vector4(0.15, 0.5, 0.75, 0.5),
		Vector4(0.15, 1.0, 0.9, 1.0)]
const N_SEGS: Array[Vector4] = [Vector4(0.1, 1.0, 0.1, 0.0), Vector4(0.1, 0.0, 0.9, 1.0), Vector4(0.9, 1.0, 0.9, 0.0)]
const TUBES: Array[Color] = [Palette.NEON_TUBE, Palette.NET_CYAN, Palette.CORP_SOLACE, Palette.NEON_TUBE]
const WALL_DAY := Palette.DESK_METAL
const WALL_NIGHT := Palette.NET_BG_OUTER
const NAMES: Array[StringName] = [&"flat", &"lighten", &"hot"]
const MAX_SEGS := 48

const PANEL_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_light.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"
uniform vec2 size = vec2(1.0);
uniform vec3 wall;
uniform vec4 segs[48];
uniform float seg_col[48];
uniform int seg_n = 0;
uniform vec3 tube[4];
uniform int treatment = 0;
uniform float half_w = 4.0;
uniform float core_share = 0.35;
uniform float hot = 0.0;
uniform vec3 core_col = vec3(1.0);
uniform float core_tint = 0.0;
uniform vec3 glow = vec3(18.0, 1.4, 0.6);
float seg_d(vec2 p, vec2 a, vec2 b) {
	vec2 ab = b - a;
	float t = clamp(dot(p - a, ab) / max(dot(ab, ab), 1e-5), 0.0, 1.0);
	return length(p - a - ab * t);
}
void fragment() {
	vec2 px = UV * size;
	float d = 1e6;
	int ci = 0;
	vec3 add = vec3(0.0);
	for (int i = 0; i < 48; i++) {
		if (i >= seg_n) {
			break;
		}
		float di = seg_d(px, segs[i].xy, segs[i].zw);
		if (di < d) {
			d = di;
			ci = int(seg_col[i]);
		}
	}
	// Glow: each colour's nearest tube, added in linear light under the soft ceiling.
	for (int c = 0; c < 4; c++) {
		float dc = 1e6;
		for (int i = 0; i < 48; i++) {
			if (i >= seg_n) {
				break;
			}
			if (int(seg_col[i]) == c) {
				dc = min(dc, seg_d(px, segs[i].xy, segs[i].zw));
			}
		}
		add += rcl_to_lin(tube[c]) * rcl_fall_exp(max(dc - half_w, 0.0), glow.x, glow.y) * glow.z;
	}
	vec3 lit = rcl_light_add(wall, add);
	vec3 col = tube[ci];
	if (treatment == 1) {
		col = rcl_hot_to(col, rcl_neon_core(col, core_col, core_tint), hot);
	} else if (treatment == 2) {
		col = rcl_hot_to(col, rcl_neon_core(col, core_col, core_tint), hot * rcl_tube_core(d, half_w * core_share));
	}
	COLOR = vec4(mix(lit, col, rcl_tube_cov(d, half_w, 1.0)), 1.0);
}
"""

const STRIP_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"
uniform vec3 tube;
uniform int treatment = 0;
uniform float half_w = 4.0;
uniform float core_share = 0.35;
uniform float hot = 0.0;
uniform vec3 core_col = vec3(1.0);
uniform float core_tint = 0.0;
void fragment() {
	float d = abs(UV.x * 2.0 - 1.0) * half_w;
	vec3 col = tube;
	if (treatment == 1) {
		col = rcl_hot_to(col, rcl_neon_core(col, core_col, core_tint), hot);
	} else if (treatment == 2) {
		col = rcl_hot_to(col, rcl_neon_core(col, core_col, core_tint), hot * rcl_tube_core(d, half_w * core_share));
	}
	COLOR = vec4(col, 1.0);
}
"""

var _panels: Array[ShaderMaterial] = []
var _bloom: ColorRect


func _ready() -> void:
	var view := get_viewport_rect().size
	var col_w := (view.x - MARGIN.x * 2.0 - GAP * 2.0) / 3.0
	var panel_h := view.y - MARGIN.y * 2.0 - STRIP_H - GAP - LABEL_SIZE
	for c in NAMES.size():
		var p := RcLookSign.preset(NAMES[c])
		var x := MARGIN.x + c * (col_w + GAP)
		_label("%s%s" % [NAMES[c],
				" (today)" if p.treatment == RcLookSignPreset.Treatment.FLAT else ": %.2f toward the tube's core%s" % [p.hot,
				", core %.0f%% of the tube" % (p.core_share * 100.0) if p.treatment == RcLookSignPreset.Treatment.HOT else ""]],
				Vector2(x, MARGIN.y - LABEL_SIZE - 8.0))
		var panel := ColorRect.new()
		panel.position = Vector2(x, MARGIN.y)
		panel.size = Vector2(col_w, panel_h)
		var m := ShaderMaterial.new()
		m.shader = _shader(PANEL_CODE)
		var segs := _word(Rect2(col_w * WORD_BOX.position.x, panel_h * WORD_BOX.position.y, col_w * WORD_BOX.size.x,
				panel_h * WORD_BOX.size.y))
		m.set_shader_parameter(&"size", panel.size)
		m.set_shader_parameter(&"segs", segs[0])
		m.set_shader_parameter(&"seg_col", segs[1])
		m.set_shader_parameter(&"seg_n", (segs[0] as Array).size())
		var tubes: Array[Vector3] = []
		for t in TUBES:
			tubes.append(_v3(t))
		m.set_shader_parameter(&"tube", tubes)
		_set_tube(m, p)
		m.set_shader_parameter(&"glow", Vector3(p.glow_px, p.glow_k, p.glow_gain))
		panel.material = m
		_panels.append(m)
		add_child(panel)
		var y := MARGIN.y + panel_h + GAP
		_label("pink tube across, %.0f px (shader / mirror)" % (p.half_w_px * 2.0), Vector2(x, y - LABEL_SIZE - 8.0))
		var strip := ColorRect.new()
		strip.position = Vector2(x, y)
		strip.size = Vector2(col_w, STRIP_H * 0.5)
		var sm := ShaderMaterial.new()
		sm.shader = _shader(STRIP_CODE)
		sm.set_shader_parameter(&"tube", _v3(TUBES[0]))
		_set_tube(sm, p)
		strip.material = sm
		add_child(strip)
		for k in CHIPS:
			var x0 := roundf(x + col_w * float(k) / CHIPS)
			var chip := ColorRect.new()
			chip.position = Vector2(x0, y + STRIP_H * 0.5)
			chip.size = Vector2(roundf(x + col_w * float(k + 1) / CHIPS) - x0, STRIP_H * 0.5)
			var d := absf((float(k) + 0.5) / CHIPS * 2.0 - 1.0) * p.half_w_px
			chip.color = RcLookSign.tube_color(p, TUBES[0], d)
			add_child(chip)
	_bloom = ColorRect.new()
	_bloom.position = Vector2(MARGIN.x, MARGIN.y)
	_bloom.size = Vector2(view.x - MARGIN.x * 2.0, panel_h)
	_bloom.material = RcLookLight.bloom_material()
	add_child(_bloom)
	apply(&"night", null)


func apply(time: StringName, quality: RcLookQualityState) -> void:
	for m in _panels:
		m.set_shader_parameter(&"wall", _v3(WALL_DAY if time == &"day" else WALL_NIGHT))
	if _bloom != null:
		RcLookLight.apply_bloom(_bloom.material as ShaderMaterial, quality)


## The word OPEN as tube segments in `box` (px): [Array[Vector4] segments, Array[float] colour index].
func _word(box: Rect2) -> Array:
	var segs: Array[Vector4] = []
	var cols: Array[float] = []
	var cell := Vector2(box.size.x / (4.0 + LETTER_GAP * 3.0), box.size.y)
	for li in 4:
		var o := box.position + Vector2(li * cell.x * (1.0 + LETTER_GAP), 0.0)
		var letter: Array[Vector4] = []
		if li == 0:
			for k in RING_SIDES:
				var a0 := TAU * k / RING_SIDES
				var a1 := TAU * (k + 1) / RING_SIDES
				letter.append(Vector4(0.5 + 0.42 * cos(a0), 0.5 + 0.5 * sin(a0), 0.5 + 0.42 * cos(a1), 0.5 + 0.5 * sin(a1)))
		else:
			letter.assign([P_SEGS, E_SEGS, N_SEGS][li - 1])
		for s in letter:
			segs.append(Vector4(o.x + s.x * cell.x, o.y + s.y * cell.y, o.x + s.z * cell.x, o.y + s.w * cell.y))
			cols.append(float(li))
	assert(segs.size() <= MAX_SEGS)
	return [segs, cols]


static func _set_tube(m: ShaderMaterial, p: RcLookSignPreset) -> void:
	m.set_shader_parameter(&"treatment", int(p.treatment))
	m.set_shader_parameter(&"half_w", p.half_w_px)
	m.set_shader_parameter(&"core_share", p.core_share)
	m.set_shader_parameter(&"hot", p.hot)
	m.set_shader_parameter(&"core_col", _v3(p.core_color))
	m.set_shader_parameter(&"core_tint", p.core_tint)


func _label(text: String, at: Vector2) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
	add_child(l)


static func _shader(code: String) -> Shader:
	var s := Shader.new()
	s.code = code
	return s


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)
