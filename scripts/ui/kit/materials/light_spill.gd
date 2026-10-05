class_name LightSpill
extends Node2D
## Light spill (ART-1 1B; ART_BIBLE v2 §1.2 "World", §6.3 Heat H1 "additive spill sprites";
## round 3 combined_v2 `kit.py` light_spill, kit sheet column D): a glowing element (a neon
## sign, the MAINFRAME sign, a spinner rim, a Heat light) lights the facets round it. Placed
## in the base layer right after what it lights (layer order: city + spill -> wheels ...),
## centred on its source; `shaders/kit/light_spill.gdshader` multiplies what is on screen
## under it by the light and adds a little haze (the emitter itself is not re-lit).
## `gain` is the per-screen tuning (round 3: combat 1.15, city 0.38, shop 1.2); `lit` (0..1)
## follows the source (a dead sign spills nothing; a neon's mean `lit`).
## The breathe (`light_spill_breathe`, T0) stops under reduce effects.
##
## 3D (1D's city, props): `uniforms_3d` packs spill sources for `shaders/kit/toon_ink.gdshader`
## (up to MAX_3D, world positions with radius, colour with intensity). A view only.

const SHADER := preload("res://shaders/kit/light_spill.gdshader")
const BREATHE := &"light_spill_breathe"
## Per-screen gains (round 3 kit sheet).
const GAIN_COMBAT := 1.15
const GAIN_CITY := 0.38
const GAIN_SHOP := 1.2
## Spill sources a toon material takes (shader uniform arrays).
const MAX_3D := 8

@export var color: Color = Palette.CELL_PINK:
	set(v):
		color = v
		_sync()
## The source's size (px), a rounded rect centred on this node.
@export var source_size: Vector2 = Vector2(60, 300):
	set(v):
		source_size = v
		_sync()
@export var source_corner: float = 12.0:
	set(v):
		source_corner = v
		_sync()
## How far the light reaches past the source (px).
@export var reach: float = 140.0:
	set(v):
		reach = v
		_sync()
@export var gain: float = GAIN_SHOP:
	set(v):
		gain = v
		_sync()
## How lit the source is (0 off .. 1 full).
@export var lit: float = 1.0:
	set(v):
		lit = clampf(v, 0.0, 1.0)
		_sync()

var _mat: ShaderMaterial = null


func _init() -> void:
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	material = _mat
	_sync()


## The rect the spill draws over (local).
func rect() -> Rect2:
	var sz := source_size + Vector2(reach, reach) * 2.0
	return Rect2(-sz * 0.5, sz)


func _sync() -> void:
	if _mat == null:
		return
	var r := rect()
	_mat.set_shader_parameter(&"color", color)
	_mat.set_shader_parameter(&"src_size", source_size)
	_mat.set_shader_parameter(&"src_corner", source_corner)
	_mat.set_shader_parameter(&"reach", reach)
	_mat.set_shader_parameter(&"gain", gain * lit)
	_mat.set_shader_parameter(&"rect_size", r.size)
	var live := Motion.live(BREATHE)
	_mat.set_shader_parameter(&"breathe_amp", Motion.amplitude(BREATHE) if live else 0.0)
	_mat.set_shader_parameter(&"breathe_period", maxf(Motion.seconds(BREATHE), 0.1))
	queue_redraw()


func _ready() -> void:
	Settings.changed.connect(_sync)
	_sync()


## The breathe's current share (1 = rest), as the shader computes it at `time` (tests).
func breathe_at(time: float) -> float:
	if not Motion.live(BREATHE):
		return 1.0
	return 1.0 + Motion.amplitude(BREATHE) * sin(time * TAU / maxf(Motion.seconds(BREATHE), 0.1))


func _draw() -> void:
	draw_rect(rect(), Color.WHITE)


## Packs spill sources for the 3D toon material: each {position: Vector3, radius: float,
## color: Color, intensity: float}. Returns {spill_lights, spill_colors, spill_count} ready
## for `ShaderMaterial.set_shader_parameter` (at most MAX_3D, in the order given).
static func uniforms_3d(sources: Array) -> Dictionary:
	var lights: Array[Vector4] = []
	var cols: Array[Vector4] = []
	for s in sources:
		if lights.size() >= MAX_3D:
			break
		var p: Vector3 = s.get("position", Vector3.ZERO)
		var c: Color = s.get("color", Palette.CELL_PINK)
		lights.append(Vector4(p.x, p.y, p.z, float(s.get("radius", 4.0))))
		cols.append(Vector4(c.r, c.g, c.b, float(s.get("intensity", 1.0))))
	while lights.size() < MAX_3D:
		lights.append(Vector4.ZERO)
		cols.append(Vector4.ZERO)
	var n := mini(sources.size(), MAX_3D)
	return {"spill_lights": lights, "spill_colors": cols, "spill_count": n}
