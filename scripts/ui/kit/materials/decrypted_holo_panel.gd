class_name DecryptedHoloPanel
extends Control
## The decrypted holo panel (ART-1 1B; ART_BIBLE v2 §1.2 "Decrypted holo": hacked corp intel,
## what the Cell stole and decrypted: the selected Site file, THREAT INTEL, intercepted corp
## news toasts; never anything the Cell owns). The corp tint at about 78 %, 4 px scanlines,
## 3-4 slow bands (`holo_bands`, T0), a +-2 px RGB split on the edge only, a near-opaque
## scrim (0.88) behind it, the corp seal cracked with a red fracture and a DECRYPTED stamp in
## its slot. `shaders/kit/decrypted_holo.gdshader`, glass under `content`, scanlines over.
## Reduce effects: the bands hold still and the RGB split is off (§5.4). A view only.

const SHADER := preload("res://shaders/kit/decrypted_holo.gdshader")
const BANDS := &"holo_bands"
## Look (§1.2): tint share, scanline period, edge split.
const TINT_SHARE := 0.78
const SCAN_PX := 4.0
const SPLIT_PX := 2.0
## The seal's radius and the fracture's kinks; the stamp's tilt (deg).
const SEAL_R := 30.0
const FRACTURE_KINKS := 7
const STAMP_TILT_DEG := -8.0
const STAMP_WORD := "DECRYPTED"
const STAMP_SLOT := Vector2(180, 48)

@export var corp_color: Color = Palette.CORP_SOLACE:
	set(v):
		corp_color = v
		_sync()
## The corp's seal letter (crest stand-in until the corp crests land).
@export var seal_letter: String = "S":
	set(v):
		seal_letter = v
		queue_redraw()
## Lays the 0.88 scrim over the whole screen behind the panel.
@export var scrim: bool = true:
	set(v):
		scrim = v
		if _scrim != null:
			_scrim.visible = v
@export var seed: int = 5

var content: Control = null
## The stamp slot (top right): DECRYPTED is drawn here; a caller may add its own stamp.
var stamp_slot: Control = null

var _glass_mat: ShaderMaterial = null
var _over_mat: ShaderMaterial = null
var _over: Control = null
var _scrim: ColorRect = null
var _seal: Control = null


func _init() -> void:
	_glass_mat = ShaderMaterial.new()
	_glass_mat.shader = SHADER
	_glass_mat.set_shader_parameter(&"mode", 0)
	_over_mat = ShaderMaterial.new()
	_over_mat.shader = SHADER
	_over_mat.set_shader_parameter(&"mode", 1)
	_scrim = ColorRect.new()
	_scrim.color = Palette.HOLO_SCRIM
	_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scrim.top_level = true  # the whole screen, behind the panel
	add_child(_scrim, false, Node.INTERNAL_MODE_FRONT)
	var glass := Control.new()
	glass.name = "Glass"
	glass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	glass.material = _glass_mat
	glass.draw.connect(func() -> void: glass.draw_rect(Rect2(Vector2.ZERO, size).grow(SPLIT_PX + 2.0), Palette.NO_TINT))
	add_child(glass, false, Node.INTERNAL_MODE_FRONT)
	glass.set_anchors_preset(Control.PRESET_FULL_RECT)
	content = Control.new()
	content.name = "Content"
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(content, false, Node.INTERNAL_MODE_FRONT)
	content.set_anchors_preset(Control.PRESET_FULL_RECT)
	_seal = Control.new()
	_seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_seal.draw.connect(_draw_seal)
	add_child(_seal, false, Node.INTERNAL_MODE_FRONT)
	_seal.set_anchors_preset(Control.PRESET_FULL_RECT)
	stamp_slot = Control.new()
	stamp_slot.name = "StampSlot"
	stamp_slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stamp_slot.draw.connect(_draw_stamp)
	add_child(stamp_slot, false, Node.INTERNAL_MODE_FRONT)
	_over = Control.new()
	_over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_over.material = _over_mat
	_over.draw.connect(func() -> void: _over.draw_rect(Rect2(Vector2.ZERO, size), Palette.NO_TINT))
	add_child(_over, false, Node.INTERNAL_MODE_BACK)
	_over.set_anchors_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	resized.connect(_layout)
	Settings.changed.connect(_sync)
	_layout()


func _layout() -> void:
	stamp_slot.size = STAMP_SLOT
	stamp_slot.position = Vector2(size.x - stamp_slot.size.x - UiTheme.SP_M, UiTheme.SP_S)
	_scrim.visible = scrim
	_scrim.position = Vector2.ZERO
	_scrim.size = get_viewport_rect().size if is_inside_tree() else size
	_sync()
	for c in get_children(true):
		if c is CanvasItem:
			(c as CanvasItem).queue_redraw()


func _sync() -> void:
	if _glass_mat == null:
		return
	var live := Motion.live(BANDS)
	for m in [_glass_mat, _over_mat]:
		var sm := m as ShaderMaterial
		sm.set_shader_parameter(&"panel", Vector4(0, 0, size.x, size.y))
		sm.set_shader_parameter(&"tint", corp_color)
		sm.set_shader_parameter(&"deep", Palette.NET_BG_OUTER)
		sm.set_shader_parameter(&"tint_share", TINT_SHARE)
		sm.set_shader_parameter(&"scan_px", SCAN_PX)
		sm.set_shader_parameter(&"split_px", SPLIT_PX if Fx.effects_enabled() else 0.0)
		sm.set_shader_parameter(&"band_seconds", maxf(Motion.seconds(BANDS), 0.1))
		sm.set_shader_parameter(&"band_strength", Motion.amplitude(BANDS) if live or not Motion.animating() else 0.0)


## The seal at the bottom right: a corp ring with its letter, cracked by a red fracture.
func _draw_seal() -> void:
	var c := Vector2(size.x - SEAL_R - UiTheme.SP_M, size.y - SEAL_R - UiTheme.SP_M)
	var ring := corp_color
	ring.a = 0.8
	_seal.draw_arc(c, SEAL_R, 0.0, TAU, 48, ring, 3.0, true)
	_seal.draw_arc(c, SEAL_R - 6.0, 0.0, TAU, 48, ring, 1.0, true)
	var font := Palette.display()
	var px := UiTheme.font_px(UiTheme.TITLE)
	var w := font.get_string_size(seal_letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	_seal.draw_string(font, c + Vector2(-w.x * 0.5, w.y * 0.32), seal_letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px, ring)
	# the red fracture across it (KitNoise kinks)
	var pts := PackedVector2Array()
	for i in FRACTURE_KINKS + 1:
		var t := float(i) / float(FRACTURE_KINKS)
		var p := c + Vector2(lerpf(-SEAL_R * 1.3, SEAL_R * 1.3, t), lerpf(-SEAL_R * 0.9, SEAL_R * 0.8, t))
		p += Vector2(KitNoise.h11(seed, i, 1), KitNoise.h11(seed, i, 2)) * SEAL_R * 0.22
		pts.append(p)
	_seal.draw_polyline(pts, Palette.HARM, 2.5, true)


## The DECRYPTED stamp: Anton in a ruled red box, tilted (a rubber stamp's ink).
func _draw_stamp() -> void:
	var font := Palette.display()
	var px := UiTheme.font_px(UiTheme.HEADING)
	var sz := font.get_string_size(STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var col := Palette.HARM
	col.a = 0.9
	var centre := stamp_slot.size * 0.5
	stamp_slot.draw_set_transform(centre, deg_to_rad(STAMP_TILT_DEG))
	var box := Rect2(-sz * 0.5 - Vector2(8, 2), sz + Vector2(16, 4))
	stamp_slot.draw_rect(box, col, false, 3.0)
	stamp_slot.draw_string(font, Vector2(-sz.x * 0.5, sz.y * 0.32), STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	stamp_slot.draw_set_transform(Vector2.ZERO, 0.0)
