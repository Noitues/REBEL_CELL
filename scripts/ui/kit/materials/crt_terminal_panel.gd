class_name CrtTerminalPanel
extends Control
## The CRT terminal panel (ART-1 1B; ART_BIBLE v2 §1.2 "CRT terminal": the Cell's own
## systems: slices, menus, resources, the Heat strip, the crew roster, tooltips, toggles,
## toasts, forecasts, Daemon tiles, the dialogue feed). Navy glass, an accent edge (cyan for
## the Cell; lime firmware, gold Schematics, the corp colour inside corp Terminals, red
## DISPATCH: `Accent`), 3 px scanlines at 10 %, a faint scrolling hex dump at 6 %, the edge
## glow, Share Tech Mono text that types on (`crt_type_on`, through Typing: one press shows
## it whole) behind a `>` prompt, and a blinking caret (`crt_caret_blink`).
##
## Built from `shaders/kit/crt_terminal.gdshader` (glass under the text, scanlines over it);
## the hex dump is the shared `shaders/kit/hex_dump.gdshaderinc` on the glass (B1c, review
## D23: `hexdump` = HEX_ALPHA on every terminal by default; the old per-frame CPU redraw is gone).
## Children added to `content` sit on the glass under the scanlines. Reduce effects: the
## hex dump and the caret hold still, the text shows whole, the static scanlines stay
## (§5.4). Tier: T0 (the hex scroll, the caret) and T1 (type-on). A view only.

enum Accent { CELL, FIRMWARE, SCHEMATICS, CORP, DISPATCH }

const SHADER := preload("res://shaders/kit/crt_terminal.gdshader")
const TYPE_ON := &"crt_type_on"
const CARET := &"crt_caret_blink"
const HEX := &"crt_hex_scroll"
## Look (§1.2, §6.4): scanline period and strength, hex-dump alpha, the glow's reach.
const SCAN_PX := 3.0
const SCAN_STRENGTH := 0.10
const HEX_ALPHA := 0.06
const GLOW_PX := 10.0
const PAD := Vector2(UiTheme.PANEL_PAD_H, UiTheme.PANEL_PAD_V)
## The prompt before typed text, and the caret glyph.
const PROMPT := "> "
const CARET_GLYPH := "_"
## Bytes per hex-dump row and how many rows the dump block holds before it repeats (the
## shader's HEX_BYTES / HEX_ROWS).
const HEX_BYTES := 12
const HEX_ROWS := 48
## The hex dump's default seed (the shared terminal material uses it too).
const HEX_SEED := 7
## B1c: the hex dump's glyphs (Share Tech Mono 0-F; tools/design_lab/hex_atlas_bake.py).
const HEX_ATLAS := preload("res://shaders/kit/hex_atlas.png")
## B1c-b (art director): the dump's glyph size, fixed: about 11 px on a 1080p screen (the game
## lays out at 1280x720, 1.5x smaller), never scaled by the text size, so it reads as texture.
const HEX_GLYPH_PX := 11.0 / 1.5
## B1c-b: behind a line of words the dump drops to this share (texture, never a second text).
const HEX_TEXT_FADE := 0.5
## B1c-b: the most word rects the glass fades the dump under (the shader's array size), and
## how often (s) a live panel re-reads them.
const HEX_TEXT_MAX := 16
const HEX_TEXT_REFRESH_S := 0.25
## The font size the glyph grid is measured at before it is scaled to HEX_GLYPH_PX.
const HEX_MEASURE_PX := 64

@export var accent_kind: Accent = Accent.CELL:
	set(v):
		accent_kind = v
		_sync()
## The corp colour for `Accent.CORP`.
@export var corp_color: Color = Palette.CORP_SOLACE:
	set(v):
		corp_color = v
		_sync()
@export var text: String = "":
	set(v):
		text = v
		if label != null:
			label.text = PROMPT + v if prompt else v
## Shows the `>` prompt before the text.
@export var prompt: bool = true
## Shows the blinking caret after the typed text.
@export var caret: bool = true
## The faint hex dump on the glass (on by default on every terminal: review D23).
@export var hex_dump: bool = true:
	set(v):
		hex_dump = v
		_sync()
@export var text_step: int = UiTheme.BODY
## Seed of the hex dump's bytes (the shader's hash; HEX_SEED by default).
@export var seed: int = HEX_SEED
## B1c-b: where the words over this glass live (their rects fade the dump). Default: the
## parent when the glass is a backing (internal or drawn behind its parent), else the panel.
var text_scope: Control = null

var label: Label = null
var content: Control = null

var _glass_mat: ShaderMaterial = null
var _over_mat: ShaderMaterial = null
var _over: Control = null
var _caret_clock: float = 0.0
var _caret_on: bool = true


func _init() -> void:
	clip_contents = false
	_glass_mat = ShaderMaterial.new()
	_glass_mat.shader = SHADER
	_glass_mat.set_shader_parameter(&"mode", 0)
	_over_mat = ShaderMaterial.new()
	_over_mat.shader = SHADER
	_over_mat.set_shader_parameter(&"mode", 1)
	material = _glass_mat
	content = Control.new()
	content.name = "Content"
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(content, false, Node.INTERNAL_MODE_FRONT)
	content.set_anchors_preset(Control.PRESET_FULL_RECT)
	label = Label.new()
	label.name = "Text"
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	content.add_child(label)
	content.draw.connect(_draw_caret)
	_over = Control.new()
	_over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_over.material = _over_mat
	_over.draw.connect(_draw_over)
	add_child(_over, false, Node.INTERNAL_MODE_BACK)
	_over.set_anchors_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	PaletteSkins.bind(self, _sync)  # ART-12 12s-b
	label.add_theme_font_override(&"font", Palette.mono())
	label.add_theme_font_size_override(&"font_size", UiTheme.font_px(text_step))
	label.position = PAD
	label.text = PROMPT + text if prompt else text
	resized.connect(_layout)
	_layout()
	_sync()


## The accent colour in use.
func accent() -> Color:
	match accent_kind:
		Accent.FIRMWARE:
			return Palette.CELL_ACID
		Accent.SCHEMATICS:
			return Palette.RESIST_GOLD
		Accent.CORP:
			return PaletteSkins.chrome(corp_color)  # ART-12 12s-b: a Cell-cyan accent given as a corp colour
		Accent.DISPATCH:
			return Palette.HARM
	return PaletteSkins.chrome(Palette.NET_CYAN)  # ART-12 12s: the Cell's edge follows the skin


## Types `t` on behind the prompt (`crt_type_on`; Typing: a press shows it whole, the
## Options switch, reduce effects and headless show it at once). Returns its seconds.
func type_on(t: String) -> float:
	text = t
	return Typing.type_in(label, TYPE_ON)


## True while the text types.
func typing() -> bool:
	return Typing.typing(label)


func _layout() -> void:
	label.size = Vector2(maxf(size.x - PAD.x * 2.0, 0.0), maxf(size.y - PAD.y * 2.0, 0.0))
	_sync()
	queue_redraw()
	_over.queue_redraw()


func _sync() -> void:
	if _glass_mat == null:
		return
	var c := accent()
	for m in [_glass_mat, _over_mat]:
		var sm := m as ShaderMaterial
		sm.set_shader_parameter(&"panel", Vector4(0.0, 0.0, size.x, size.y))
		sm.set_shader_parameter(&"accent", c)
		sm.set_shader_parameter(&"glass_top", PaletteSkins.chrome(Palette.CRT_GLASS_TOP))
		sm.set_shader_parameter(&"glass_bottom", PaletteSkins.chrome(Palette.CRT_GLASS_BOTTOM))
		sm.set_shader_parameter(&"glow_px", GLOW_PX)
		sm.set_shader_parameter(&"scan_px", SCAN_PX)
		sm.set_shader_parameter(&"scan_strength", SCAN_STRENGTH)
	sync_hex(_glass_mat, c, hex_dump, seed)
	refresh_text_mask()
	_over_mat.set_shader_parameter(&"hexdump", 0.0)  # the dump sits under the text only
	if label != null:
		label.add_theme_color_override(&"font_color", PaletteSkins.chrome(Palette.TERMINAL_TEXT))


## The glass, grown by the glow (the shader's panel rect sits GLOW_PX in).
func _draw() -> void:
	draw_rect(_grown(), Palette.NO_TINT)


func _grown() -> Rect2:
	return Rect2(-Vector2(GLOW_PX, GLOW_PX), size + Vector2(GLOW_PX, GLOW_PX) * 2.0)


func _draw_over() -> void:
	_over.draw_rect(_grown(), Palette.NO_TINT)


## The caret, on the content layer (under the scanlines), once the text has typed on.
func _draw_caret() -> void:
	if caret and _caret_on and not typing():
		var at := caret_position()
		var px := UiTheme.font_px(text_step)
		content.draw_string(Palette.mono(), at, CARET_GLYPH, HORIZONTAL_ALIGNMENT_LEFT, -1, px, accent())


## Where the caret sits (after the shown text; unwrapped text), local px.
func caret_position() -> Vector2:
	var shown := label.text
	if label.visible_characters >= 0:
		shown = shown.substr(0, label.visible_characters)
	var lines := shown.split("\n")
	var font := Palette.mono()
	var px := UiTheme.font_px(text_step)
	var last: String = lines[lines.size() - 1]
	var line_h := font.get_height(px) + float(label.get_theme_constant(&"line_spacing"))
	var x := font.get_string_size(last, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	return label.position + Vector2(x, font.get_ascent(px) + line_h * float(lines.size() - 1))


## B1c (review D23): sets the shared hex-dump uniforms (`hex_dump.gdshaderinc`) on `mat`: the
## atlas, the alpha (HEX_ALPHA, 0 when `on` is false), the character grid (the mono advance and
## line height at HEX_GLYPH_PX, whatever the text size), the accent tint, and the
## scroll (`crt_hex_scroll`'s px/s while that motion is live; 0 holds it still: reduce effects,
## the motion switch, headless). Shared with UiTheme.crt_material.
static func sync_hex(mat: ShaderMaterial, tint: Color, on: bool, hex_seed: int) -> void:
	mat.set_shader_parameter(&"hex_atlas", HEX_ATLAS)
	mat.set_shader_parameter(&"hexdump", HEX_ALPHA if on else 0.0)
	mat.set_shader_parameter(&"hex_cell", hex_cell())
	mat.set_shader_parameter(&"hex_text_fade", HEX_TEXT_FADE)
	mat.set_shader_parameter(&"hex_origin", Vector2(PAD.x * 0.5, 0.0))
	mat.set_shader_parameter(&"hex_scroll", Motion.amplitude(HEX) if Motion.live(HEX) else 0.0)
	mat.set_shader_parameter(&"hex_seed", float(hex_seed))
	mat.set_shader_parameter(&"hex_tint", tint)


## B5 (B1c review follow-up 2): puts this glass behind `owner` (an internal child drawn before the owner's own
## drawing, full rect) in place of the shared `crt_panel` material: the owner gets the navy glass, scanlines, the
## accent edge glow and the hex dump that fades under its words (`text_scope` = the owner). `accent` is the
## edge's colour (the Cell's cyan follows the skin; a corp colour stays). The owner's own material is cleared;
## the owner draws only its edge, header and words over it. Returns the glass.
static func behind(owner: Control, accent_color: Color = Palette.NET_CYAN) -> CrtTerminalPanel:
	var g := HudSkin.crt_backing(owner)
	g.accent_kind = Accent.CORP
	g.corp_color = accent_color
	g.text_scope = owner
	owner.material = null
	return g


## The hex dump's character cell (px): the mono advance and line height at HEX_GLYPH_PX.
static func hex_cell() -> Vector2:
	var font := Palette.mono()
	var k := HEX_GLYPH_PX / float(HEX_MEASURE_PX)
	return Vector2(font.get_char_size(ord("0"), HEX_MEASURE_PX).x, font.get_height(HEX_MEASURE_PX)) * k


## The hex dump's alpha on the glass now (0 when off).
func hex_alpha() -> float:
	return float(_glass_mat.get_shader_parameter(&"hexdump"))


## B1c-b: the rects (panel-local) of the visible words over this glass: Labels, RichTextLabels,
## Buttons and LineEdits under `text_scope`, the ones that overlap the panel, at most HEX_TEXT_MAX
## (in tree order). The dump fades to HEX_TEXT_FADE under them.
func text_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var scope := _scope()
	if scope == null or not is_inside_tree():
		return out
	var inv := get_global_transform().affine_inverse()
	var own := Rect2(Vector2.ZERO, size)
	var stack: Array[Node] = [scope]
	while not stack.is_empty() and out.size() < HEX_TEXT_MAX:
		var n: Node = stack.pop_front()
		if n is CanvasItem and not (n as CanvasItem).visible:
			continue
		if n is Label or n is RichTextLabel or n is Button or n is LineEdit:
			var c := n as Control
			var g := c.get_global_rect()
			var r := Rect2(inv * g.position, inv.basis_xform(g.size)).abs()
			if r.has_area() and r.intersects(own) and not _has_no_words(c):
				out.append(r)
		for k in n.get_children(true):
			if k != self:
				stack.append(k)
	return out


func _has_no_words(c: Control) -> bool:
	if c == label:
		return text.strip_edges() == ""  # the bare prompt is not a line of words
	if c is Label:
		return (c as Label).text.strip_edges() == ""
	if c is Button:
		return (c as Button).text.strip_edges() == ""
	return false


func _scope() -> Control:
	if text_scope != null and is_instance_valid(text_scope):
		return text_scope
	var parent := get_parent() as Control
	if parent != null and (show_behind_parent or not get_parent().get_children(false).has(self)):
		return parent
	return self


## B1c-b: re-reads the word rects and hands them to the shader (a live panel does it every
## HEX_TEXT_REFRESH_S; layout changes do it at once).
func refresh_text_mask() -> void:
	if _glass_mat == null:
		return
	var rects := text_rects() if hex_dump else ([] as Array[Rect2])
	var packed := PackedVector4Array()
	packed.resize(HEX_TEXT_MAX)
	for i in rects.size():
		var r := rects[i]
		packed[i] = Vector4(r.position.x, r.position.y, r.end.x, r.end.y)
	_glass_mat.set_shader_parameter(&"hex_text_rects", packed)
	_glass_mat.set_shader_parameter(&"hex_text_count", rects.size())


var _mask_clock: float = 0.0


func _process(delta: float) -> void:
	if hex_dump:
		_mask_clock += delta
		if _mask_clock >= HEX_TEXT_REFRESH_S:
			_mask_clock = 0.0
			refresh_text_mask()
	if caret:
		var was := _caret_on
		if Motion.live(CARET):
			_caret_clock += delta
			var half := maxf(Motion.seconds(CARET), 0.05)
			_caret_on = int(_caret_clock / half) % 2 == 0
		else:
			_caret_on = true
		if was != _caret_on or typing():
			content.queue_redraw()
