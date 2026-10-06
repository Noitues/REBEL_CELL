class_name VinylSticker
extends Control
## The vinyl sticker (ART-1 1B; ART_BIBLE v2 §1.2 "Vinyl sticker", §1.3, §6.3, §6.4): things
## that never change (verbs, titles, name plates, stamps, node stickers, cards). Ported from
## the round 3 combined_v2 concept toolkit (`sticker_lib.py`: lettering, build_sticker,
## apply_curl, place) and round 19's gloss_k / round 22's states (`send_it_sticker.png`).
##
## Look: Anton lettering with per-glyph jitter, an ink keyline, a chunky extrude, a thick
## white die-cut border, the vinyl's rim light and cut line, gloss 0.22 at rest with one slow
## sweep on one sticker at a time (StickerSweepQueue), a soft two-layer drop shadow. Objects
## (`Shape.RECT` / `CIRCLE`) take any content under `content_root` on a white or kraft body.
## The art is drawn once into a SubViewport (redrawn only when it changes, or every frame
## for holo foil, whose hue drifts); `shaders/kit/vinyl_sticker.gdshader` adds the rim,
## gloss, peel, shadow, dissolve and disabled grey on top.
##
## Motion (ui_motion.tres; every one shows its end state at once under reduce effects,
## headless or switched off, and ends with any press another helper takes: MotionSkip
## passive): `slap` (APPEAR), `peel` (EXIT), `dissolve` (a temporary word into bits),
## `sweep` (the one gloss sweep), the idle corner flutter, and the states REST / HOVER /
## PRESSED / DISABLED. A view; it never changes game state. The per-locale baked atlas of
## sticker words is ART-4/10's; this is the runtime sticker.

signal motion_finished(kind: StringName)

enum Shape { WORD, RECT, CIRCLE }
enum Fill { PINK, RED, YELLOW, HOLO, WHITE, INK }
enum Stock { GLOSS, KRAFT, HOLO }
enum State { REST, HOVER, PRESSED, DISABLED }
enum Lift { TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT }

const SHADER := preload("res://shaders/kit/vinyl_sticker.gdshader")
const FILL_SHADER := preload("res://shaders/kit/sticker_fill.gdshader")
## Look (round 3 combined_v2 `word_sticker` / `build_sticker` defaults, 1x px).
const BORDER_PX := 18.0
## Parity STICKER_EDGE (designer 2026-10-05): the die-cut edge of a LETTERED sticker is proportional to its
## lettering (a fixed 18 px edge read far too thick on a menu-sized sticker), up to the concept's own edge
## (round 33 ui31.sticker border 12 px on the 1920 board = 8 px on the 1280 frame at 1.0, and the edge
## grows with the text scale like the lettering does). The concept's edge / body height runs 0.08 (the title
## verbs) to 0.27 (CANCEL at 28 px); `EDGE_SHARE` of the lettering keeps menu stickers at about 0.2.
const EDGE_SHARE := 0.14
const EDGE_MAX_PX := 8.0
## Designer 2026-10-06 (B1d): focus and hover are the PEEL-BACK only (the lift, the grow and the corner curl,
## HOVER_CURL); the holo-foil (`rainbow`) gloss belongs to the ONE scheduled sweep (StickerSweepQueue), never to focus.
const KEYLINE_PX := 5.0
## draw_string_outline's size is the outline's whole width (both sides of the contour):
## a reach of r px out from the glyph takes an outline of r x this.
const OUTLINE_PER_REACH := 4.0
const EXTRUDE_PX := 8.0
const JITTER_DEG := 4.0
const TRACK_PX := 1.0
const LINE_GAP := 0.98
## Room round the art for the shadow at full lift (soft offset 32x44 + blur 32).
const SHADOW_PAD := 56.0
## The gloss at rest (round 19 gloss_k) and its band's rest position on the diagonal.
const GLOSS_REST := 0.22
const GLOSS_POS_REST := 0.32
## The sweep runs the band from off one corner to off the other.
const SWEEP_FROM := -0.3
const SWEEP_TO := 1.3
## The extrude's slant (x per y px).
const EXTRUDE_SLANT := 0.55
## Share of the font size that is the caps' height (Anton): the body's top.
const CAP_SHARE := 0.74
## Slap (lifecycle APPEAR): the start scale, the squash and its time, the drop's share.
const SLAP_FROM_SCALE := 1.24
const SLAP_SQUASH := Vector2(1.13, 0.84)
## The slap's drop and the peel's curl-away shapes (named, ANIM-R6 rule: no inline tween shapes).
const DROP_EASE := Tween.EASE_IN
const DROP_TRANS := Tween.TRANS_QUAD
const PEEL_AWAY_TRANS := Tween.TRANS_CUBIC
const SLAP_SQUASH_SECONDS := 0.09
const SLAP_DROP_SHARE := 0.45
## Peel (EXIT): the curl away down-left (px, deg) and the share of the time the fade takes at
## its end.
const PEEL_AWAY := Vector2(-46.0, 64.0)
const PEEL_TURN_DEG := -24.0
const PEEL_FADE_SHARE := 0.35
## Idle flutter low end (fold), hover's lift and curl, pressed's x squash, disabled's alpha.
const FLUTTER_LOW := 0.08
const HOVER_LIFT := 0.6
const HOVER_CURL := 0.12
const PRESS_X := 1.04
const DISABLED_ALPHA := 0.8

const SLAP := &"sticker_slap"
const PEEL := &"sticker_peel"
const DISSOLVE := &"sticker_dissolve"
const SWEEP := &"sticker_gloss_sweep"
const FLUTTER := &"sticker_corner_flutter"
const HOVER := &"sticker_hover"
const PRESS := &"sticker_press"

@export var text: String = "SEND IT":
	set(v):
		text = v
		_rebuild()
@export var shape: Shape = Shape.WORD:
	set(v):
		shape = v
		_rebuild()
@export var fill: Fill = Fill.PINK:
	set(v):
		fill = v
		_rebuild()
@export var stock: Stock = Stock.GLOSS:
	set(v):
		stock = v
		_rebuild()
## Type step of the lettering (UiTheme steps; scales with the text scale).
@export var font_step: int = UiTheme.HERO:
	set(v):
		font_step = v
		_rebuild()
## The body of an object sticker (RECT / CIRCLE), px.
@export var body_size: Vector2 = Vector2(180, 120):
	set(v):
		body_size = v
		_rebuild()
@export var corner_radius: float = 16.0
## The die-cut border (px); negative = automatic: proportional to the lettering for a word (`edge_for`),
## BORDER_PX for an object sticker.
@export var border_px: float = -1.0:
	set(v):
		border_px = v
		_rebuild()
## The jitter's seed (KitNoise): the same seed, the same sticker.
@export var seed: int = 1:
	set(v):
		seed = v
		_rebuild()
## The corner that lifts (curl at rest, flutter, hover curl, peel).
@export var lifted_corner: Lift = Lift.TOP_RIGHT:
	set(v):
		lifted_corner = v
		_sync()
## The corner's curl at rest (0 = flat).
@export var rest_curl: float = 0.0:
	set(v):
		rest_curl = v
		fold = v
## The sticker's resting tilt (deg).
@export var tilt_deg: float = 0.0:
	set(v):
		tilt_deg = v
		rotation_degrees = v
## Joins StickerSweepQueue: the one rainbow sweep runs on the screen's primary sticker in its turn.
@export var ambient_sweep: bool = false:
	set(v):
		ambient_sweep = v
		if is_inside_tree():
			_join_sweep()
## The screen names this sticker its primary verb: the queue sweeps it before any other (rank 0).
@export var sweep_primary: bool = false
## The idle corner flutter (lifecycle IDLE; T0).
@export var flutter: bool = false

## Shader-driven state (the motions tween these).
var gloss_k: float = GLOSS_REST:
	set(v):
		gloss_k = v
		_sync()
var gloss_pos: float = GLOSS_POS_REST:
	set(v):
		gloss_pos = v
		_sync()
var fold: float = 0.0:
	set(v):
		fold = v
		_sync()
var lift: float = 0.0:
	set(v):
		lift = v
		_sync()
var dissolve_t: float = 0.0:
	set(v):
		dissolve_t = v
		_sync()
var grey: float = 0.0:
	set(v):
		grey = v
		_sync()
## 1 while the scheduled sweep crosses: the gloss runs in holo-foil colours (the shader's `rainbow`).
var rainbow: float = 0.0:
	set(v):
		rainbow = v
		_sync()

var state: State = State.REST
## The body's rect inside this control (px): where the sticker itself is.
var body_rect: Rect2 = Rect2()
## Where the content of an object sticker goes (inside the SubViewport, at the body).
var content_root: Control = null

var _vp: SubViewport = null
var _base: Control = null
var _fill: Control = null
var _mat: ShaderMaterial = null
var _fill_mat: ShaderMaterial = null
var _face: Control = null
var _face_mat: ShaderMaterial = null
var _tween: Tween = null
var _tween_kind: StringName = &""
var _sweep_tween: Tween = null
var _glyphs: Array = []  # [char, Vector2 pos (baseline), float angle, Vector2 centre]
var _lines_y: Array[float] = []
var _px: int = 0
var _font: Font = null
var _flutter_clock: float = 0.0
var _built: bool = false
## M14 asset parity: the art pass's finished sticker for this word (StickerArt), {} = lettered live.
var _baked: Dictionary = {}
## Look the word up in StickerArt (off: always letter it live).
static var use_baked_art: bool = true


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	material = _mat
	_fill_mat = ShaderMaterial.new()
	_fill_mat.shader = FILL_SHADER
	_vp = SubViewport.new()
	_vp.transparent_bg = true
	_vp.disable_3d = true
	_vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	add_child(_vp, false, Node.INTERNAL_MODE_FRONT)
	_base = Control.new()
	_base.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_base.draw.connect(_draw_base)
	_vp.add_child(_base)
	# a holo object's foil face (Stock.HOLO), under its content
	_face_mat = ShaderMaterial.new()
	_face_mat.shader = FILL_SHADER
	_face_mat.set_shader_parameter(&"mode", 1)
	_face = Control.new()
	_face.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_face.material = _face_mat
	_face.draw.connect(_draw_face)
	_vp.add_child(_face)
	content_root = Control.new()
	content_root.name = "Content"
	content_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_vp.add_child(content_root)
	_fill = Control.new()
	_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fill.material = _fill_mat
	_fill.draw.connect(_draw_fill)
	_vp.add_child(_fill)


func _ready() -> void:
	MotionSkip.register_passive(self)  # ANIM-R6 D7: a slap, peel or dissolve ends with any press that ends a motion
	_built = true
	_rebuild()
	_join_sweep()


func _exit_tree() -> void:
	StickerSweepQueue.leave(self)


## The viewport texture holding the sticker's art (tests, the baked atlas later).
func art_texture() -> Texture2D:
	return _vp.get_texture()


## Redraws the art (after `content_root`'s children change).
func refresh() -> void:
	if _base == null:
		return
	_base.queue_redraw()
	_fill.queue_redraw()
	_face.queue_redraw()
	for c in content_root.get_children():
		if c is CanvasItem:
			(c as CanvasItem).queue_redraw()
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS if _holo() else SubViewport.UPDATE_ONCE


## Places the sticker so its body's centre is at `p` (in the parent's space).
func place_center(p: Vector2) -> void:
	position = p - pivot_offset


# --- Build -------------------------------------------------------------------------------

static var _art_font: FontFile = null


## The lettering face for the sticker's art: Anton rasterised (not MSDF). The die-cut border
## and keyline are outlines far wider than an MSDF field's range (Palette.FONTS_MSDF_RANGE),
## which an MSDF face clips to a thin fringe; the art is drawn once into its SubViewport at
## its own size, so a plain raster face loses nothing.
static func art_font() -> FontFile:
	if _art_font == null:
		var src := load(Palette.FONT_DISPLAY) as FontFile
		_art_font = FontFile.new()
		_art_font.data = src.data
		_art_font.multichannel_signed_distance_field = false
		_art_font.antialiasing = TextServer.FONT_ANTIALIASING_GRAY
	return _art_font


## The die-cut edge (px) of a lettered sticker whose lettering is `px` (see EDGE_SHARE).
static func edge_for(px: float) -> float:
	return minf(px * EDGE_SHARE, EDGE_MAX_PX * maxf(1.0, Settings.text_scale))


## This sticker's die-cut border (px) as drawn.
func edge() -> float:
	if border_px >= 0.0:
		return border_px
	return edge_for(float(_px)) if shape == Shape.WORD else BORDER_PX


func _holo() -> bool:
	return (shape == Shape.WORD and fill == Fill.HOLO) or (shape != Shape.WORD and stock == Stock.HOLO)


func _rebuild() -> void:
	if not _built:
		return
	_font = art_font()
	_px = UiTheme.font_px(font_step)
	var key := KEYLINE_PX
	var reach := edge() + key
	var art := Vector2.ZERO
	var body_pos := Vector2.ZERO
	var body_sz := Vector2.ZERO
	_glyphs.clear()
	_lines_y.clear()
	_baked = StickerArt.lookup(text) if use_baked_art and shape == Shape.WORD else {}
	if not _baked.is_empty():
		# The art pass's own sticker, at the size this step letters its word.
		var tex: Texture2D = _baked["tex"]
		body_sz = tex.get_size() * (float(_px) / float(_baked["lettering_px"]))
		art = body_sz
		body_pos = Vector2(SHADOW_PAD, SHADOW_PAD)
	elif shape == Shape.WORD:
		var lines := text.split("\n")
		var asc := _font.get_ascent(_px)
		var line_h := float(_px) * LINE_GAP
		var cap := float(_px) * CAP_SHARE
		var widest := 0.0
		var widths: Array[float] = []
		for line in lines:
			var w := 0.0
			for i in line.length():
				w += _font.get_string_size(line[i], HORIZONTAL_ALIGNMENT_LEFT, -1, _px).x + TRACK_PX
			widths.append(maxf(w - TRACK_PX, 0.0))
			widest = maxf(widest, widths[-1])
		var block_h := cap + line_h * float(lines.size() - 1)
		body_sz = Vector2(widest + reach * 2.0, block_h + reach * 2.0)
		art = body_sz + Vector2(EXTRUDE_PX * EXTRUDE_SLANT, EXTRUDE_PX)
		body_pos = Vector2(SHADOW_PAD, SHADOW_PAD)
		var gi := 0
		for li in lines.size():
			var line: String = lines[li]
			var x := body_pos.x + reach + (widest - widths[li]) * 0.5
			var base_y := body_pos.y + reach + cap + line_h * float(li)
			_lines_y.append(base_y)
			for i in line.length():
				var ch := line[i]
				var adv := _font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, _px).x
				if ch != " ":
					var ang := deg_to_rad(KitNoise.h11(seed, gi, 1) * JITTER_DEG)
					var dy := KitNoise.h11(seed, gi, 2) * 0.03 * float(_px)
					var centre := Vector2(x + adv * 0.5, base_y - cap * 0.5 + dy)
					_glyphs.append([ch, Vector2(x, base_y + dy), ang, centre, asc])
				x += adv + TRACK_PX
				gi += 1
	else:
		body_sz = body_size
		art = body_sz
		body_pos = Vector2(SHADOW_PAD, SHADOW_PAD)
	var full := art + Vector2(SHADOW_PAD, SHADOW_PAD) * 2.0
	_vp.size = Vector2i(ceili(full.x), ceili(full.y))
	_base.size = full
	_fill.size = full
	content_root.position = body_pos + (Vector2(edge(), edge()) if stock != Stock.KRAFT and shape != Shape.WORD else Vector2.ZERO)
	content_root.size = body_sz - (Vector2(edge(), edge()) * 2.0 if stock != Stock.KRAFT and shape != Shape.WORD else Vector2.ZERO)
	body_rect = Rect2(body_pos, body_sz)
	custom_minimum_size = full
	size = full
	pivot_offset = body_rect.get_center()
	_fill_mat.set_shader_parameter(&"mode", 1 if fill == Fill.HOLO else 0)
	var cols := _fill_colors()
	_fill_mat.set_shader_parameter(&"fill_top", cols[0])
	_fill_mat.set_shader_parameter(&"fill_bottom", cols[1])
	_fill_mat.set_shader_parameter(&"band_top", body_pos.y + reach)
	_fill_mat.set_shader_parameter(&"band_bottom", body_pos.y + body_sz.y - reach)
	_fill_mat.set_shader_parameter(&"field_size", body_sz)
	_fill_mat.set_shader_parameter(&"holo_seed", float(seed))
	_fill_mat.set_shader_parameter(&"holo_drift", HOLO_DRIFT if _holo() else 0.0)
	_face.size = full
	_face_mat.set_shader_parameter(&"field_size", body_sz)
	_face_mat.set_shader_parameter(&"holo_seed", float(seed))
	_face_mat.set_shader_parameter(&"holo_drift", HOLO_DRIFT if _holo() else 0.0)
	_sync()
	refresh()
	queue_redraw()

## Holo hue cycles per second (lifecycle IDLE "the holo foil hue drifts").
const HOLO_DRIFT := 0.04
## The shader's die-cut rim light for lettered stickers (its default).
const RIM := 0.8


func _fill_colors() -> Array[Color]:
	match fill:
		Fill.RED:
			return Palette.STICKER_FILL_RED
		Fill.YELLOW:
			return Palette.STICKER_FILL_YELLOW
		Fill.WHITE:
			return [Palette.STICKER_DIE_CUT, Palette.VINYL_WHITE_LO]
		Fill.INK:
			return [Palette.VINYL_INK, Palette.VINYL_EXTRUDE]
	return Palette.STICKER_FILL_PINK


## Draws one glyph rotated about its centre (`layer` is the SubViewport control).
func _glyph(layer: Control, g: Array, offset: Vector2, outline_px: float, col: Color) -> void:
	var centre: Vector2 = g[3] + offset
	layer.draw_set_transform(centre, g[2])
	var at: Vector2 = g[1] + offset - centre
	if outline_px > 0.0:
		layer.draw_string_outline(_font, at, g[0], HORIZONTAL_ALIGNMENT_LEFT, -1, _px, int(outline_px), col)
	layer.draw_string(_font, at, g[0], HORIZONTAL_ALIGNMENT_LEFT, -1, _px, col)


## True while the sticker shows the art pass's own image (StickerArt) for its word.
func is_baked() -> bool:
	return not _baked.is_empty()


func _draw_base() -> void:
	if not _baked.is_empty():
		_base.draw_texture_rect(_baked["tex"], body_rect, false)
		return
	if shape == Shape.WORD:
		_draw_word_base()
		return
	var r := body_rect
	var face := Palette.KRAFT if stock == Stock.KRAFT else Palette.STICKER_DIE_CUT
	if shape == Shape.CIRCLE:
		_base.draw_circle(r.get_center(), minf(r.size.x, r.size.y) * 0.5, face)
	else:
		var sb := StyleBoxFlat.new()
		sb.bg_color = face
		sb.set_corner_radius_all(int(corner_radius))
		sb.anti_aliasing = true
		_base.draw_style_box(sb, r)
	if stock == Stock.KRAFT:
		_draw_kraft(r)


## Kraft stock: fibres and blotches from KitNoise (sticker_lib kraft_tex).
func _draw_kraft(r: Rect2) -> void:
	var n := int(r.size.x * r.size.y / KRAFT_FIBRE_AREA)
	for i in n:
		var p := r.position + Vector2(KitNoise.h01(seed, i, 11) * r.size.x, KitNoise.h01(seed, i, 12) * r.size.y)
		var a := KitNoise.h01(seed, i, 13) * PI
		var l := lerpf(3.0, 10.0, KitNoise.h01(seed, i, 14))
		var c := Palette.KRAFT_FIBRE
		c.a = lerpf(0.12, 0.32, KitNoise.h01(seed, i, 15))
		var q := p + Vector2(cos(a), sin(a)) * l
		if r.has_point(p) and r.grow(-2.0).has_point(q):
			_base.draw_line(p, q, c, 1.0, true)
	for i in int(n / KRAFT_BLOTCH_SHARE):
		var p := r.position + Vector2(KitNoise.h01(seed, i, 21) * r.size.x, KitNoise.h01(seed, i, 22) * r.size.y)
		var rad := lerpf(4.0, 12.0, KitNoise.h01(seed, i, 23))
		if r.grow(-rad).has_point(p):
			var c := Palette.KRAFT.lightened(0.25) if KitNoise.h01(seed, i, 24) > 0.5 else Palette.KRAFT_FIBRE
			c.a = 0.08
			_base.draw_circle(p, rad, c)

## Kraft: one fibre per this many px² of stock, one blotch per this many fibres.
const KRAFT_FIBRE_AREA := 130.0
const KRAFT_BLOTCH_SHARE := 6


func _draw_word_base() -> void:
	var reach := edge() + KEYLINE_PX
	# 1. the die-cut body: every glyph grown by the border and the keyline, plus a band
	# through each line's middle that closes the notches between letters.
	for g in _glyphs:
		_glyph(_base, g, Vector2.ZERO, reach * OUTLINE_PER_REACH, Palette.STICKER_DIE_CUT)
	_base.draw_set_transform(Vector2.ZERO, 0.0)
	var cap := float(_px) * CAP_SHARE
	for y in _lines_y:
		var x0 := body_rect.position.x + reach * 0.6
		var x1 := body_rect.end.x - reach * 0.6
		var band := Rect2(x0, y - cap + reach * 0.35, x1 - x0, cap - reach * 0.7)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Palette.STICKER_DIE_CUT
		sb.set_corner_radius_all(int(reach))
		sb.anti_aliasing = true
		if band.size.y > 0.0:
			_base.draw_style_box(sb, band)
	# 2. the extrude: the keyline shape stepped down-right.
	var step := 1.0
	while step <= EXTRUDE_PX:
		for g in _glyphs:
			_glyph(_base, g, Vector2(step * EXTRUDE_SLANT, step), KEYLINE_PX * OUTLINE_PER_REACH, Palette.VINYL_EXTRUDE)
		step += 1.0
	# 3. the keyline.
	for g in _glyphs:
		_glyph(_base, g, Vector2.ZERO, KEYLINE_PX * OUTLINE_PER_REACH, Palette.VINYL_INK)
	_base.draw_set_transform(Vector2.ZERO, 0.0)


## A holo object's foil face: the body inset by the border, drawn through the holo shader.
func _draw_face() -> void:
	if shape == Shape.WORD or stock != Stock.HOLO:
		return
	var r := body_rect.grow(-edge() * 0.5)
	if shape == Shape.CIRCLE:
		_face.draw_circle(r.get_center(), minf(r.size.x, r.size.y) * 0.5, Palette.STICKER_DIE_CUT)
	else:
		var sb := StyleBoxFlat.new()
		sb.bg_color = Palette.STICKER_DIE_CUT
		sb.set_corner_radius_all(int(maxf(corner_radius - edge() * 0.5, 2.0)))
		_face.draw_style_box(sb, r)


func _draw_fill() -> void:
	if shape != Shape.WORD or not _baked.is_empty():
		return
	for g in _glyphs:
		_glyph(_fill, g, Vector2.ZERO, 0.0, Palette.STICKER_DIE_CUT)
	_fill.draw_set_transform(Vector2.ZERO, 0.0)


func _draw() -> void:
	draw_texture(_vp.get_texture(), Vector2.ZERO)


func _sync() -> void:
	if _mat == null:
		return
	_mat.set_shader_parameter(&"art_tex", _vp.get_texture())
	_mat.set_shader_parameter(&"body_rect",Vector4(body_rect.position.x, body_rect.position.y, body_rect.size.x, body_rect.size.y))
	_mat.set_shader_parameter(&"gloss_k", 0.0 if bool(_baked.get("own_finish", false)) else gloss_k)
	_mat.set_shader_parameter(&"gloss_pos", gloss_pos)
	var own := bool(_baked.get("own_finish", false))
	_mat.set_shader_parameter(&"glossy", 0.0 if stock == Stock.KRAFT or own else 1.0)
	# A baked sticker has its die-cut rim drawn in; one with its own finish has its shadow too.
	_mat.set_shader_parameter(&"rim", 0.0 if not _baked.is_empty() else RIM)
	_mat.set_shader_parameter(&"shadow_k", 0.0 if own else 1.0)
	_mat.set_shader_parameter(&"fold", fold)
	_mat.set_shader_parameter(&"corner", int(lifted_corner))
	_mat.set_shader_parameter(&"lift", lift)
	_mat.set_shader_parameter(&"dissolve", dissolve_t)
	_mat.set_shader_parameter(&"grey", grey)
	_mat.set_shader_parameter(&"rainbow", rainbow)
	_mat.set_shader_parameter(&"backing_color", Palette.KRAFT.lightened(0.2) if stock == Stock.KRAFT else Palette.VINYL_BACKING)
	_mat.set_shader_parameter(&"shadow_color", Palette.VINYL_EXTRUDE)


# --- Motion ------------------------------------------------------------------------------

## True while a slap, peel, dissolve, hover or press plays (MotionSkip).
func motion_running() -> bool:
	return (_tween != null and _tween.is_valid() and _tween.is_running()) or sweep_running()


## True while the rainbow sweep crosses.
func sweep_running() -> bool:
	return _sweep_tween != null and _sweep_tween.is_valid() and _sweep_tween.is_running()


## Ends the running motion at its end state (MotionSkip; a press): a running sweep ends at once.
func complete_motion() -> void:
	if sweep_running():
		_sweep_tween.kill()
		_sweep_tween = null
		_finish_sweep()
	if not (_tween != null and _tween.is_valid() and _tween.is_running()):
		return
	var kind := _tween_kind
	_tween.kill()
	_tween = null
	_end_state(kind)


func _start(kind: StringName) -> Tween:
	if _tween != null and _tween.is_valid():
		var was := _tween_kind
		_tween.kill()
		_end_state(was)
	_tween_kind = kind
	_tween = create_tween()
	return _tween


func _end_state(kind: StringName) -> void:
	match kind:
		SLAP:
			scale = Vector2.ONE
			rotation_degrees = tilt_deg
			modulate.a = 1.0
			visible = true
		PEEL:
			fold = Motion.amplitude(PEEL)
			lift = 1.0
			modulate.a = 0.0
			visible = false
		DISSOLVE:
			dissolve_t = 1.0
			visible = false
		HOVER:
			_apply_state_end(state)
		PRESS:
			_apply_state_end(state)
	_tween_kind = &""
	motion_finished.emit(kind)


## Lifecycle APPEAR (`sticker_slap`, T2): drops in from 1.24x over-rotated by the entry's
## amplitude, slaps (squash 1.13 / 0.84 for 90 ms), overshoots once and settles at its tilt,
## then the shine sweeps. Returns the seconds it takes (0: shown at once).
func slap() -> float:
	visible = true
	fold = rest_curl
	lift = 0.0
	dissolve_t = 0.0
	if not Motion.live(SLAP):
		_start(SLAP).kill()
		_end_state(SLAP)
		return 0.0
	var e := Motion.entry(SLAP)
	var d := Motion.seconds(SLAP)
	var drop := d * SLAP_DROP_SHARE
	var squash := minf(SLAP_SQUASH_SECONDS / maxf(Motion.speed, Motion.SPEED_MIN), d * 0.3)
	scale = Vector2.ONE * SLAP_FROM_SCALE
	rotation_degrees = tilt_deg + e.amplitude
	modulate.a = 0.0
	var tw := _start(SLAP)
	tw.tween_property(self, "modulate:a", 1.0, drop * 0.5)
	tw.parallel().tween_property(self, "scale", SLAP_SQUASH, drop).set_ease(DROP_EASE).set_trans(DROP_TRANS)
	tw.parallel().tween_property(self, "rotation_degrees", tilt_deg - e.amplitude * 0.15, drop).set_ease(DROP_EASE).set_trans(DROP_TRANS)
	tw.tween_interval(squash)
	var rest := maxf(d - drop - squash, 0.01)
	tw.tween_property(self, "scale", Vector2.ONE, rest).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(self, "rotation_degrees", tilt_deg, rest).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_method(_sweep_step, 0.0, 1.0, rest)
	tw.tween_callback(func() -> void:
		_tween = null
		_end_state(SLAP))
	return d


## Lifecycle EXIT (`sticker_peel`, T2): peels from the lifted corner (fold 0 -> amplitude),
## lifts (the shadow blurs) and curls away down-left, gone at the end. Returns its seconds.
func peel() -> float:
	if not Motion.live(PEEL):
		_start(PEEL).kill()
		_end_state(PEEL)
		return 0.0
	var e := Motion.entry(PEEL)
	var d := Motion.seconds(PEEL)
	var from := position
	var tw := _start(PEEL)
	tw.tween_property(self, "fold", e.amplitude, d).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(self, "lift", 1.0, d * 0.6)
	tw.parallel().tween_property(self, "position", from + PEEL_AWAY, d).set_delay(d * 0.3).set_ease(DROP_EASE).set_trans(PEEL_AWAY_TRANS)
	tw.parallel().tween_property(self, "rotation_degrees", tilt_deg + PEEL_TURN_DEG, d).set_delay(d * 0.3).set_ease(DROP_EASE)
	tw.parallel().tween_property(self, "modulate:a", 0.0, d * PEEL_FADE_SHARE).set_delay(d * (1.0 - PEEL_FADE_SHARE))
	tw.tween_callback(func() -> void:
		_tween = null
		position = from
		_end_state(PEEL))
	return d


## A temporary word dissolves (`sticker_dissolve`, T2): its cells go left to right with a
## white-hot rim; with an `emitter` the cells leave as binary bits towards `target`
## (BinaryBits). Returns its seconds.
func dissolve(emitter: BinaryBits = null, target: Vector2 = Vector2.ZERO) -> float:
	_mat.set_shader_parameter(&"dissolve_cell", Motion.amplitude(DISSOLVE))
	if emitter != null:
		emitter.burst_from_rect(get_global_transform() * body_rect, target, Palette.CELL_PINK)
	if not Motion.live(DISSOLVE):
		_start(DISSOLVE).kill()
		_end_state(DISSOLVE)
		return 0.0
	var e := Motion.entry(DISSOLVE)
	var d := Motion.seconds(DISSOLVE)
	var tw := _start(DISSOLVE)
	tw.tween_property(self, "dissolve_t", 1.0, d).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void:
		_tween = null
		_end_state(DISSOLVE))
	return d


## The one slow rainbow gloss sweep (`sticker_gloss_sweep`, T0): the band crosses in holo-foil colours with the
## gloss up to the amplitude, then back to rest. Returns its seconds (0 when it doesn't play).
func sweep() -> float:
	if _sweep_tween != null and _sweep_tween.is_valid():
		_sweep_tween.kill()
	if not Motion.live(SWEEP):
		_finish_sweep()
		return 0.0
	var e := Motion.entry(SWEEP)
	var d := Motion.seconds(SWEEP)
	rainbow = 1.0
	_sweep_tween = create_tween()
	_sweep_tween.tween_method(_sweep_step, 0.0, 1.0, d).set_ease(e.ease).set_trans(e.trans)
	_sweep_tween.tween_callback(_finish_sweep)
	return d


func _finish_sweep() -> void:
	gloss_k = GLOSS_REST
	gloss_pos = GLOSS_POS_REST
	rainbow = 0.0
	StickerSweepQueue.done(self, Time.get_ticks_msec(), Motion.seconds(SWEEP))


## StickerSweepQueue interface: the order the screen's sticker is considered primary (0 named, 1 pink, 2 the rest).
func sweep_rank() -> int:
	if sweep_primary:
		return 0
	return 1 if fill == Fill.PINK else 2


## StickerSweepQueue interface: it may take the turn (shown, not disabled).
func sweep_ready() -> bool:
	return is_visible_in_tree() and state != State.DISABLED and not sweep_running()


## StickerSweepQueue interface: runs the sweep; returns its seconds.
func run_sweep() -> float:
	return sweep()


func _sweep_step(t: float) -> void:
	gloss_pos = lerpf(SWEEP_FROM, SWEEP_TO, t)
	gloss_k = lerpf(GLOSS_REST, Motion.amplitude(SWEEP), sin(t * PI))
	if t >= 1.0:
		gloss_pos = GLOSS_POS_REST
		gloss_k = GLOSS_REST


## REST / HOVER / PRESSED / DISABLED (round 22 send_it_sticker: hover lifts 0.6 and grows to
## `sticker_hover`'s scale with a 0.12 curl and a full sweep; pressed squashes to 1.04 /
## `sticker_press`'s y, the shadow snaps in; disabled is greyscale vinyl at 80 %).
func set_state(s: State) -> void:
	state = s
	var id := PRESS if s == State.PRESSED else HOVER
	if not Motion.live(id) or s == State.DISABLED:
		if motion_running():
			_tween.kill()
			_tween = null
		_apply_state_end(s)
		return
	var e := Motion.entry(id)
	var d := Motion.seconds(id)
	var to := _state_values(s)
	var tw := _start(id)
	tw.tween_property(self, "scale", to["scale"], d).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(self, "lift", to["lift"], d if s != State.PRESSED else 0.0)
	tw.parallel().tween_property(self, "fold", to["fold"], d)
	tw.tween_callback(func() -> void:
		_tween = null
		_end_state(id))


func _state_values(s: State) -> Dictionary:
	match s:
		State.HOVER:
			return {"scale": Vector2.ONE * Motion.amplitude(HOVER), "lift": HOVER_LIFT, "fold": maxf(rest_curl, HOVER_CURL)}
		State.PRESSED:
			return {"scale": Vector2(PRESS_X, Motion.amplitude(PRESS)), "lift": 0.0, "fold": rest_curl}
	return {"scale": Vector2.ONE, "lift": 0.0, "fold": rest_curl}


func _apply_state_end(s: State) -> void:
	var v := _state_values(s)
	scale = v["scale"]
	lift = v["lift"]
	fold = v["fold"]
	grey = 1.0 if s == State.DISABLED else 0.0
	# Focus / hover is the peel-back only (no gloss change); the rest gloss is the static sheen.
	if s == State.REST and not sweep_running():
		gloss_k = GLOSS_REST
		gloss_pos = GLOSS_POS_REST
	modulate.a = DISABLED_ALPHA if s == State.DISABLED else 1.0


func _join_sweep() -> void:
	if ambient_sweep:
		StickerSweepQueue.join(self)
	else:
		StickerSweepQueue.leave(self)


func _process(delta: float) -> void:
	if ambient_sweep and StickerSweepQueue.take_turn(self, Time.get_ticks_msec()):
		if sweep() <= 0.0:
			StickerSweepQueue.done(self, Time.get_ticks_msec(), 0.0)
	if flutter and not motion_running() and state == State.REST:
		if Motion.live(FLUTTER):
			_flutter_clock += delta
			var period := maxf(Motion.seconds(FLUTTER), 0.01)
			var t := 0.5 - 0.5 * cos(_flutter_clock / period * TAU)
			fold = lerpf(FLUTTER_LOW, Motion.amplitude(FLUTTER), t)
		elif fold != rest_curl:
			fold = rest_curl
