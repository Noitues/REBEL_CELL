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
## Built from `shaders/kit/crt_terminal.gdshader` (glass under the text, scanlines over it).
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
## Bytes per hex-dump row and how many rows the dump block holds before it repeats.
const HEX_BYTES := 12
const HEX_ROWS := 48

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
## The faint hex dump on the glass.
@export var hex_dump: bool = true
@export var text_step: int = UiTheme.BODY
## Seed of the hex dump's bytes (KitNoise).
@export var seed: int = 7

var label: Label = null
var content: Control = null

var _glass_mat: ShaderMaterial = null
var _over_mat: ShaderMaterial = null
var _hex: Control = null
var _over: Control = null
var _hex_offset: float = 0.0
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
	_hex = Control.new()
	_hex.clip_contents = true
	_hex.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hex.draw.connect(_draw_hex)
	add_child(_hex, false, Node.INTERNAL_MODE_FRONT)
	_hex.set_anchors_preset(Control.PRESET_FULL_RECT)
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
			return corp_color
		Accent.DISPATCH:
			return Palette.HARM
	return Palette.NET_CYAN


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
	_hex.queue_redraw()


func _sync() -> void:
	if _glass_mat == null:
		return
	var c := accent()
	for m in [_glass_mat, _over_mat]:
		var sm := m as ShaderMaterial
		sm.set_shader_parameter(&"panel", Vector4(0.0, 0.0, size.x, size.y))
		sm.set_shader_parameter(&"accent", c)
		sm.set_shader_parameter(&"glass_top", Palette.CRT_GLASS_TOP)
		sm.set_shader_parameter(&"glass_bottom", Palette.CRT_GLASS_BOTTOM)
		sm.set_shader_parameter(&"glow_px", GLOW_PX)
		sm.set_shader_parameter(&"scan_px", SCAN_PX)
		sm.set_shader_parameter(&"scan_strength", SCAN_STRENGTH)
	if label != null:
		label.add_theme_color_override(&"font_color", Palette.TERMINAL_TEXT)


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


## The faint hex dump: rows of bytes from KitNoise in the accent colour at HEX_ALPHA.
func _draw_hex() -> void:
	if not hex_dump:
		return
	var font := Palette.mono()
	var px := UiTheme.font_px(UiTheme.CAPTION)
	var line_h := font.get_height(px)
	var col := accent()
	col.a = HEX_ALPHA
	var rows := int(size.y / line_h) + 2
	var first := int(floor(_hex_offset / line_h))
	var shift := fmod(_hex_offset, line_h)
	for r in rows:
		var row := (first + r) % HEX_ROWS
		var s := "%04X " % (row * HEX_BYTES)
		for b in HEX_BYTES:
			s += "%02X " % int(KitNoise.h01(seed, row, b) * 255.0)
		_hex.draw_string(font, Vector2(PAD.x * 0.5, float(r) * line_h - shift + font.get_ascent(px)), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)


func _process(delta: float) -> void:
	if hex_dump and Motion.live(HEX):
		var font := Palette.mono()
		var block := font.get_height(UiTheme.font_px(UiTheme.CAPTION)) * float(HEX_ROWS)
		_hex_offset = fmod(_hex_offset + Motion.amplitude(HEX) * delta, block)
		_hex.queue_redraw()
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
