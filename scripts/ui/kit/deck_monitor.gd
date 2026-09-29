class_name DeckMonitor
extends PanelContainer
## The HQ's Grid monitor (ART_BIBLE §2 DECK, §11 HQ: "Grid monitor (CRT, curvature, amber
## readouts)"): a DESK_DARK casing with a DESK_METAL rim, a CRT screen holding its content
## (the City Grid mini-map) through W6's `crt_overlay` (static scanlines, a slow roll band;
## still under reduce effects), curved glass drawn over it (rounded screen corners, a
## highlight arcing across the top, darker edges) and amber readouts (CRT_AMBER: the title,
## the status and a line of numbers, the only amber on the screen). DECK material: no
## paper, no terminal glass inside it. `screen` holds the content; `set_readouts` words
## the lines (translated by the caller). High contrast: opaque casing, no highlight.

## The casing's rim and corner radius, its padding and the screen's own corner radius (px
## at text scale 1.0; the rim is hardware and stays).
const RIM := 3
const CASE_CORNER := 12
const CASE_PAD := 10
const SCREEN_CORNER := 14.0
## The curved glass: the highlight's alpha and height share, the edge shading's alpha and
## width (px), the corner wedges' arc steps.
const GLARE_ALPHA := 0.07
const GLARE_SHARE := 0.22
const EDGE_ALPHA := 0.35
const EDGE_W := 6.0
const CORNER_STEPS := 8
## The crt_overlay settings on the screen (W6's shader; its roll is T0, at least 3 s).
const CRT_SHADER := "res://shaders/crt_overlay.gdshader"
const CRT_SCAN := 0.12
const CRT_ROLL := 0.04
const CRT_ROLL_PERIOD := 7.0
## The readouts' type step (§4.2) and the gap between the screen and them.
const READOUT_STEP := UiTheme.BODY
const TITLE_STEP := UiTheme.BODY
const GAP := UiTheme.SP_XS

var title_label: Label
var status_label: Label
var readout_label: Label
## The CRT screen: put the content here (it fills it).
var screen: Control
var _glass: Control


func _init(p_title: String = "") -> void:
	name = "DeckMonitor"
	var box := StyleBoxFlat.new()
	box.bg_color = Palette.DESK_DARK
	box.border_color = Palette.DESK_METAL
	box.set_border_width_all(RIM)
	box.set_corner_radius_all(CASE_CORNER)
	box.set_content_margin_all(CASE_PAD)
	add_theme_stylebox_override("panel", box)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", GAP)
	add_child(col)
	var head := HBoxContainer.new()
	col.add_child(head)
	title_label = _amber(p_title, TITLE_STEP)
	title_label.name = "MonitorTitle"
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	head.add_child(title_label)
	status_label = _amber("", READOUT_STEP)
	status_label.name = "MonitorStatus"
	status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	head.add_child(status_label)
	screen = Control.new()
	screen.name = "Screen"
	screen.size_flags_vertical = Control.SIZE_EXPAND_FILL
	screen.clip_contents = true
	col.add_child(screen)
	readout_label = _amber("", READOUT_STEP)
	readout_label.name = "MonitorReadout"
	readout_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	col.add_child(readout_label)
	_glass = Control.new()
	_glass.name = "Glass"
	_glass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glass.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_glass.draw.connect(_draw_glass)
	screen.add_child(_glass)
	TextDb.shown_as_given(self)


func _ready() -> void:
	Settings.changed.connect(_on_settings)
	screen.resized.connect(_glass.queue_redraw)
	_on_settings()


## An amber CRT readout label at type step `step` x the text scale.
func _amber(text: String, step: int) -> Label:
	var l := Label.new()
	l.text = text
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	l.add_theme_color_override("font_color", Palette.CRT_AMBER)
	l.set_meta(&"step", step)
	return l


func _on_settings() -> void:
	for l in [title_label, status_label, readout_label]:
		(l as Label).add_theme_font_size_override("font_size", UiTheme.font_px(int((l as Label).get_meta(&"step"))))
	_glass.queue_redraw()


## Puts `content` on the screen (filling it) under the curved glass, through the CRT shader.
func set_content(content: Control) -> void:
	content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	screen.add_child(content)
	screen.move_child(content, 0)
	var sh := load(CRT_SHADER) as Shader
	if sh != null:
		var mat := ShaderMaterial.new()
		mat.shader = sh
		mat.set_shader_parameter(&"scan_strength", CRT_SCAN)
		mat.set_shader_parameter(&"roll_strength", CRT_ROLL)
		mat.set_shader_parameter(&"roll_period", CRT_ROLL_PERIOD)
		content.material = mat
	screen.custom_minimum_size = content.custom_minimum_size


## The amber lines: the status (top right) and the readout under the screen.
func set_readouts(status: String, readout: String) -> void:
	status_label.text = status
	readout_label.text = readout
	readout_label.visible = readout != ""


## The curved glass over the screen: corners rounded off by the casing, darker edges, a
## highlight arcing across the top (no highlight in high contrast).
func _draw_glass() -> void:
	var r := Rect2(Vector2.ZERO, screen.size)
	if r.size.x <= SCREEN_CORNER * 2.0 or r.size.y <= SCREEN_CORNER * 2.0:
		return
	for k in 4:
		_glass.draw_rect(r.grow(-k * EDGE_W * 0.5), Color(Palette.INK, EDGE_ALPHA * (1.0 - k / 4.0)), false, EDGE_W * 0.5)
	if not Settings.high_contrast:
		var arc := PackedVector2Array()
		var h := r.size.y * GLARE_SHARE
		for k in CORNER_STEPS * 2 + 1:
			var t := float(k) / (CORNER_STEPS * 2)
			arc.append(Vector2(r.size.x * (0.08 + 0.84 * t), SCREEN_CORNER * 0.6 + sin(t * PI) * -h * 0.25 + h * 0.5))
		for k in range(CORNER_STEPS * 2, -1, -1):
			var t := float(k) / (CORNER_STEPS * 2)
			arc.append(Vector2(r.size.x * (0.08 + 0.84 * t), SCREEN_CORNER * 0.6 + sin(t * PI) * -h * 0.25))
		_glass.draw_colored_polygon(arc, Color(Palette.PAPER, GLARE_ALPHA))
	for c in [Vector2.ZERO, Vector2(r.size.x, 0), Vector2(0, r.size.y), r.size]:
		_corner(c, r)


## A rounded screen corner at `c`: casing colour outside a quarter circle.
func _corner(c: Vector2, r: Rect2) -> void:
	var sx := 1.0 if c.x <= r.position.x else -1.0
	var sy := 1.0 if c.y <= r.position.y else -1.0
	var centre := c + Vector2(SCREEN_CORNER * sx, SCREEN_CORNER * sy)
	var pts := PackedVector2Array([c])
	var a0 := atan2(-sy, 0.0)
	var sweep := wrapf(atan2(0.0, -sx) - a0, -PI, PI)  # the quarter turn facing the corner
	for k in CORNER_STEPS + 1:
		var a := a0 + sweep * k / CORNER_STEPS
		pts.append(centre + Vector2(cos(a), sin(a)) * SCREEN_CORNER)
	_glass.draw_colored_polygon(pts, Palette.DESK_DARK)
