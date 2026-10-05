class_name StickerSeam
extends RefCounted
## ART-2 2C: the one place the played card picks its sticker material (ART_BIBLE v2 §3.18,
## §6.3: one CanvasItem shader for peel and gloss, `scan_y` for the dissolve). Group 1's 1B
## material kit brings the vinyl sticker material (peel / slap / dissolve); until it is
## merged on main the card uses `shaders/fx/card_sticker_fx.gdshader`. Switching is an edit
## to this file only. The material is new per card (a loaded Resource is never changed).

const SHADER_PATH := "res://shaders/fx/card_sticker_fx.gdshader"
const P_SIZE := &"card_size"
const P_SCAN := &"scan_y"
const P_GLOSS := &"gloss_t"


## A fresh material for a played card of `size` px.
static func card_material(size: Vector2) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(SHADER_PATH) as Shader
	m.set_shader_parameter(P_SIZE, size)
	m.set_shader_parameter(P_SCAN, 0.0)
	m.set_shader_parameter(P_GLOSS, -1.0)
	return m


## Sets the dissolve's scan front on `card` (0 = whole, 1 = gone).
static func set_scan(card: CanvasItem, share: float) -> void:
	var m := card.material as ShaderMaterial if is_instance_valid(card) else null
	if m != null:
		m.set_shader_parameter(P_SCAN, clampf(share, 0.0, 1.0))


## Sets the gloss band on `card` to `t` (-1 = none, 0..1 across; `t` first, for a tween).
static func set_gloss(t: float, card: CanvasItem) -> void:
	var m := card.material as ShaderMaterial if is_instance_valid(card) else null
	if m != null:
		m.set_shader_parameter(P_GLOSS, t)
