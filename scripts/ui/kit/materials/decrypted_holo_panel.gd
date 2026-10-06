class_name DecryptedHoloPanel
extends Control
## The decrypted holo panel (ART-1 1B; ART_BIBLE v2 §1.2 "Decrypted holo": hacked corp intel,
## what the Cell stole and decrypted: the selected Site file, THREAT INTEL, intercepted corp
## news toasts; never anything the Cell owns). The corp tint at about 78 %, 4 px scanlines,
## 3-4 slow bands (`holo_bands`, T0), a +-2 px RGB split on the edge only, a near-opaque
## scrim (0.88) behind it, the corp seal cracked with a red fracture and a DECRYPTED stamp in
## its slot. `shaders/kit/decrypted_holo.gdshader`, glass under `content`, scanlines over.
## Reduce effects: the bands hold still and the RGB split is off (§5.4). A view only.
##
## M14 B1c (integration review D17; round 21 `intel_decrypt.png`, round 44 `raid_setup.png`):
## the finished material by default on every holo: the tint at 78 %, 4 px scanlines at 12 %,
## three slow bands (`holo_bands`: one pass in 6 s), the +-2 px edge split, a local 0.88 scrim
## right behind the plate (`backing`; `scrim` keeps the whole-screen one for modals), and the
## corp's seal (its emblem when `corporation` is set; ui21 `seal_overlay`: the two halves
## offset, a red fracture down the middle) under the DECRYPTED stamp, which is in the Cell's
## acid like the concepts' green stamp. Skins only swap the accent tokens.

const SHADER := preload("res://shaders/kit/decrypted_holo.gdshader")
const BANDS := &"holo_bands"
## Look (§1.2): tint share, scanline period, edge split. B1c-b (art director): TINT_SHARE is
## the tint's strength on the words and the edge (`ink`); the body is FILL_SHARE of the tint
## over the dark 0.88 glass (round 21 `intel_decrypt`, round 44 `raid_setup`).
const TINT_SHARE := 0.78
const FILL_SHARE := 0.28
const GLASS_ALPHA := 0.88
const SCAN_PX := 4.0
const SPLIT_PX := 2.0
## B1c (D17): the scanlines' strength and the number of slow bands on the plate.
const SCAN_STRENGTH := 0.12
const BAND_COUNT := 3.0
## B1c (D17): the local scrim right behind the plate (px round it; HOLO_SCRIM is 0.88).
const BACKING_OUT := 4.0
## B1c (ui21 `seal_overlay`): the cracked crest's halves offset (px at a 40 px seal radius,
## left half then right half) and the fracture's points (shares of the seal's box, top to
## bottom); the fracture's width.
const CRACK_LEFT := Vector2(-3.0, 2.0)
const CRACK_RIGHT := Vector2(1.0, -2.0)
const FRACTURE := [Vector2(0.52, 0.0), Vector2(0.46, 0.3), Vector2(0.56, 0.55), Vector2(0.47, 0.8), Vector2(0.53, 1.0)]
const FRACTURE_W := 2.5
## The crest's half size as a share of the seal radius (CorpSeal: the emblem inside the ring).
const CREST_SHARE := 0.62
## The seal's radius and the fracture's kinks; the stamp's tilt (deg).
const SEAL_R := 30.0
const STAMP_TILT_DEG := -8.0
const STAMP_WORD := "DECRYPTED"
const STAMP_SLOT := Vector2(180, 48)
## B1c: the stamp's ink (the Cell's acid, as the route holo's DECRYPTED chip) and its alpha.
const STAMP_COLOR := Palette.CELL_ACID
const STAMP_ALPHA := 0.9
## B1c-b (art director): a dark ink under-shadow so the acid stamp reads on every corp tint
## (Solace's green above all): its offset (px) and alpha.
const STAMP_SHADOW_OFFSET := Vector2(2, 2)
const STAMP_SHADOW_ALPHA := 0.7

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
## B1c (D17): the 0.88 scrim right behind the plate (BACKING_OUT round it), so the holo reads
## over a busy city even where the whole-screen scrim is off.
@export var backing: bool = true:
	set(v):
		backing = v
		queue_redraw()
## B1c: the corporation whose emblem the seal carries (CorpSeal); empty: the seal letter.
@export var corporation: StringName = &"":
	set(v):
		corporation = v
		if stamp_slot != null:
			stamp_slot.queue_redraw()
@export var seed: int = 5
## Parity ROUTE-03: the cracked corp seal (off for the route's node holo: the concept's DEPOT 15
## holo has none, and it sat on the fields). B1c (D17): it sits under the DECRYPTED stamp, in
## the stamp's slot, so it moves with the stamp.
@export var seal: bool = true:
	set(v):
		seal = v
		if stamp_slot != null:
			stamp_slot.queue_redraw()

var content: Control = null
## The stamp slot (top right): DECRYPTED is drawn here; a caller may add its own stamp.
var stamp_slot: Control = null

var _glass_mat: ShaderMaterial = null
var _over_mat: ShaderMaterial = null
var _over: Control = null
var _scrim: ColorRect = null


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
		sm.set_shader_parameter(&"fill_share", FILL_SHARE)
		sm.set_shader_parameter(&"glass_alpha", GLASS_ALPHA)
		sm.set_shader_parameter(&"scan_px", SCAN_PX)
		sm.set_shader_parameter(&"scan_strength", SCAN_STRENGTH)
		sm.set_shader_parameter(&"band_count", BAND_COUNT)
		sm.set_shader_parameter(&"split_px", SPLIT_PX if Fx.effects_enabled() else 0.0)
		sm.set_shader_parameter(&"band_seconds", maxf(Motion.seconds(BANDS), 0.1))
		sm.set_shader_parameter(&"band_strength", Motion.amplitude(BANDS) if live or not Motion.animating() else 0.0)


## B1c (D17): the local 0.88 scrim right behind the plate.
func _draw() -> void:
	if backing:
		draw_rect(Rect2(Vector2.ZERO, size).grow(BACKING_OUT), Palette.HOLO_SCRIM)


## The seal's centre (stamp-slot local): under the stamp, the stamp's centre.
func seal_center() -> Vector2:
	return stamp_slot.size * 0.5


## The seal under the stamp: a corp ring with its emblem (or letter), the emblem's halves
## offset and a red fracture down the middle (ui21 `seal_overlay`).
func _draw_seal() -> void:
	var c := seal_center()
	var ring := corp_color
	ring.a = 0.8
	stamp_slot.draw_arc(c, SEAL_R, 0.0, TAU, 48, ring, 3.0, true)
	stamp_slot.draw_arc(c, SEAL_R - 6.0, 0.0, TAU, 48, ring, 1.0, true)
	var half := SEAL_R * CREST_SHARE
	var k := SEAL_R / 40.0
	var t := CorpSeal.emblem(corporation) if corporation != &"" else null
	if t != null:
		var ts := t.get_size()
		var box := Rect2(c - Vector2(half, half), Vector2(half, half) * 2.0)
		stamp_slot.draw_texture_rect_region(t, Rect2(box.position + CRACK_LEFT * k, Vector2(box.size.x * 0.5, box.size.y)), Rect2(Vector2.ZERO, Vector2(ts.x * 0.5, ts.y)), ring)
		stamp_slot.draw_texture_rect_region(t, Rect2(box.position + Vector2(box.size.x * 0.5, 0.0) + CRACK_RIGHT * k, Vector2(box.size.x * 0.5, box.size.y)), Rect2(Vector2(ts.x * 0.5, 0.0), Vector2(ts.x * 0.5, ts.y)), ring)
	else:
		var font := Palette.display()
		var px := UiTheme.font_px(UiTheme.TITLE)
		var w := font.get_string_size(seal_letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
		stamp_slot.draw_string(font, c + Vector2(-w.x * 0.5, w.y * 0.32), seal_letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px, ring)
	# the red fracture down the middle, across the ring
	var pts := PackedVector2Array()
	for f: Vector2 in FRACTURE:
		pts.append(c + (f - Vector2(0.5, 0.5)) * SEAL_R * 2.0)
	stamp_slot.draw_polyline(pts, Palette.HARM, FRACTURE_W, true)


## The DECRYPTED stamp over the cracked seal: Anton in a ruled box, tilted (a rubber stamp's
## ink), in the Cell's acid (the concepts' green DECRYPTED: the Cell's own mark on stolen data).
func _draw_stamp() -> void:
	if seal:
		_draw_seal()
	var font := Palette.display()
	var px := UiTheme.font_px(UiTheme.HEADING)
	var sz := font.get_string_size(STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var col := STAMP_COLOR
	col.a = STAMP_ALPHA
	var centre := stamp_slot.size * 0.5
	var box := Rect2(-sz * 0.5 - Vector2(8, 2), sz + Vector2(16, 4))
	for pass_shadow in [true, false]:
		var at: Vector2 = centre + (STAMP_SHADOW_OFFSET if pass_shadow else Vector2.ZERO)
		var ink: Color = stamp_shadow_color() if pass_shadow else col
		stamp_slot.draw_set_transform(at, deg_to_rad(STAMP_TILT_DEG))
		stamp_slot.draw_rect(box, ink, false, 3.0)
		stamp_slot.draw_string(font, Vector2(-sz.x * 0.5, sz.y * 0.32), STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px, ink)
	stamp_slot.draw_set_transform(Vector2.ZERO, 0.0)


## B1c-b: the stamp's under-shadow ink (dark, STAMP_SHADOW_ALPHA).
static func stamp_shadow_color() -> Color:
	return Color(Palette.INK, STAMP_SHADOW_ALPHA)


## B1c-b: the holo's words and edge colour for corp tint `tint`: the tint at TINT_SHARE over the
## bright text white (the full corp colour on the words; the body stays dark).
static func ink(tint: Color) -> Color:
	return Palette.TEXT_HI.lerp(tint, TINT_SHARE)
