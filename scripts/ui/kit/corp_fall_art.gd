class_name CorpFallArt
extends Control
## Art pass W8d (ART_BIBLE §11 Campaign end WON, §3.6, critique 62): the target
## corporation's billboard at the campaign's end. A night panel framed in the corp's hue and
## filled with its pattern (CorpPattern), its landmark standing on it as a baked silhouette
## (assets/art/campaign_end/landmark_<corp>.svg, tinted in the hue), then:
## 1. the landmark falls (`set_fall`: it tips over its right foot and sinks into the ground
##    line; the panel clips it);
## 2. the Cell crosses the hue and the pattern out in CELL_PINK spray (`set_spray`): two
##    marker strokes (W6 `marker_stroke`, strike-through shape) drawn on one after the other,
##    then the overspray and drips (baked) settle in.
## The corp reads without colour through the landmark's shape and the pattern (§3.6, §12).
## Presentation only: the stage drives both amounts; `set_fall(1)` + `set_spray(1)` is the
## end state (reduce effects, a skip). Display only (no focus, no clicks).

const LANDMARK_DIR := "res://assets/art/campaign_end/"
const SPRAY := "res://assets/art/campaign_end/spray_x.svg"
const MARKER_SHADER := preload("res://shaders/marker_stroke.gdshader")
## The panel's size at text scale 1.0 (px) and the most it grows with the text.
const BASE_SIZE := Vector2(232, 240)
const GROW_MAX := 1.3
## The landmark's height as a share of the panel's, and the ground line's inset (px at 1.0).
const LANDMARK_SHARE := 0.8
const GROUND_INSET := 10.0
## How far it falls: its tilt (degrees, over its right foot) and how deep it sinks (a share
## of its height) at the end.
const FALL_DEG := 20.0
const FALL_SINK := 0.1
## The frame's width, the pattern's opacity and scale (px at 1.0).
const FRAME := 3.0
const PATTERN_ALPHA := 0.35
const PATTERN_SCALE := 1.0
## The spray: each stroke's width, wobble and reach past the panel's corners (px at 1.0),
## the X's lean (degrees from horizontal) and where the overspray begins (a share of the
## spray's run).
const STROKE_W := 16.0
const STROKE_WOBBLE := 2.5
const STROKE_LEAN := 48.0
const STROKE_OVERHANG := 8.0
const OVERSPRAY_AT := 0.8

var corp_id: StringName = &""
var hue: Color = Palette.NET_CYAN
var pattern: int = CorpPattern.Kind.NONE
## The amounts shown (0..1).
var fall: float = 0.0
var spray: float = 0.0
var strokes: Array[ColorRect] = []
var overspray: TextureRect
var _landmark: Texture2D = null


func _init(p_corp_id: StringName = &"") -> void:
	name = "CorpFallArt"
	corp_id = p_corp_id
	hue = Palette.corp_color(corp_id)
	pattern = Palette.corp_pattern_id(corp_id)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	clip_contents = true
	custom_minimum_size = art_size()
	for i in 2:
		var s := ColorRect.new()
		s.name = "Spray%d" % i
		s.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var mat := ShaderMaterial.new()
		mat.shader = MARKER_SHADER
		mat.set_shader_parameter(&"shape", 2)
		mat.set_shader_parameter(&"ink", Palette.CELL_PINK)
		s.material = mat
		add_child(s)
		strokes.append(s)
	overspray = TextureRect.new()
	overspray.name = "Overspray"
	overspray.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overspray.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	overspray.stretch_mode = TextureRect.STRETCH_SCALE
	overspray.modulate = Color(Palette.CELL_PINK, 0.0)
	add_child(overspray)
	resized.connect(_place)


## The panel's size at the player's text size (px).
static func art_size() -> Vector2:
	return (BASE_SIZE * minf(Settings.text_scale, GROW_MAX)).round()


## The landmark silhouette's file for corporation `id` ("" when there is none).
static func landmark_path(id: StringName) -> String:
	var p := LANDMARK_DIR + "landmark_" + String(id) + ".svg"
	return p if FileAccess.file_exists(p) or ResourceLoader.exists(p) else ""


## The landmark's texture (null for a corporation without one: the panel keeps its pattern).
func landmark() -> Texture2D:
	return _landmark


func _ready() -> void:
	_place()


func _k() -> float:
	return minf(Settings.text_scale, GROW_MAX)


func _place() -> void:
	var k := _k()
	var path := landmark_path(corp_id)
	_landmark = SvgArt.texture(path, size.y * LANDMARK_SHARE) if path != "" else null
	# The X: two strokes corner to corner, a little past the panel's edges.
	var diag := Vector2(size.x, size.y).length() + STROKE_OVERHANG * 2.0 * k
	var w := STROKE_W * k
	for i in strokes.size():
		var s := strokes[i]
		s.size = Vector2(diag, w * 3.0)
		s.pivot_offset = s.size * 0.5
		s.position = size * 0.5 - s.size * 0.5
		s.rotation_degrees = STROKE_LEAN if i == 0 else -STROKE_LEAN
		var mat := s.material as ShaderMaterial
		mat.set_shader_parameter(&"size_px", s.size)
		mat.set_shader_parameter(&"width_px", w)
		mat.set_shader_parameter(&"wobble_px", STROKE_WOBBLE * k)
	var side := minf(size.x, size.y)
	overspray.texture = SvgArt.texture(SPRAY, side)
	overspray.size = Vector2(side, side)
	overspray.position = (size - overspray.size) * 0.5
	set_spray(spray)
	queue_redraw()


## Shows the landmark `t` of the way through its fall (0 standing, 1 down).
func set_fall(t: float) -> void:
	fall = clampf(t, 0.0, 1.0)
	queue_redraw()


## Shows the spray `t` of the way on (0 none; the first stroke, then the second, then the
## overspray; 1 the whole X).
func set_spray(t: float) -> void:
	spray = clampf(t, 0.0, 1.0)
	var run := spray / OVERSPRAY_AT
	for i in strokes.size():
		var p := clampf(run * 2.0 - i, 0.0, 1.0)
		(strokes[i].material as ShaderMaterial).set_shader_parameter(&"progress", p)
		strokes[i].visible = p > 0.0
	overspray.modulate.a = clampf((spray - OVERSPRAY_AT) / (1.0 - OVERSPRAY_AT), 0.0, 1.0)


## True once both strokes are drawn whole (tests).
func crossed_out() -> bool:
	for s in strokes:
		if float((s.material as ShaderMaterial).get_shader_parameter(&"progress")) < 1.0:
			return false
	return true


## The ground line's height (local y).
func ground_y() -> float:
	return size.y - GROUND_INSET * _k()


func _draw() -> void:
	var k := _k()
	var r := Rect2(Vector2.ZERO, size)
	var hc := Settings.high_contrast
	draw_rect(r, HighContrast.BG if hc else Palette.NIGHT_BLOCK)
	CorpPattern.fill_rect(self, r.grow(-FRAME * k), pattern, hue if hc else Color(hue, PATTERN_ALPHA), PATTERN_SCALE * k)
	var gy := ground_y()
	draw_line(Vector2(0, gy), Vector2(size.x, gy), hue, FRAME * k)
	if _landmark != null:
		var ts := _landmark.get_size() * (size.y * LANDMARK_SHARE / _landmark.get_size().y)
		# The fall: it tips over its right foot and sinks.
		var foot := Vector2(size.x * 0.5 + ts.x * 0.5, gy + ts.y * FALL_SINK * fall)
		var angle := deg_to_rad(FALL_DEG) * fall
		draw_set_transform(foot, angle, Vector2.ONE)
		draw_texture_rect(_landmark, Rect2(Vector2(-ts.x, -ts.y), ts), false, hue)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	draw_rect(r.grow(-FRAME * k * 0.5), hue, false, maxf(FRAME * k, PaperInk.EDGE_PX if hc else 0.0))
