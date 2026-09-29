extends Control
## Shader lab (dev tool, not exported; ART_BIBLE 13, art pass W6): the shader library's
## new shaders side by side on one 1280x720 page, each on a real input (a busy neon
## backdrop, paper, a gradient photo), so they can be judged and captured:
##   glass_blur, crt_overlay, paper_burn, glitch_dissolve, marker_stroke (circle, box,
##   underline) and halftone.
##
## Run:      godot --path . res://tools/design_lab/shader_lab.tscn
## Options (after `--`): --progress=<0..1> holds every progress uniform there (default
##   HOLD_PROGRESS); --animate sweeps them 0 -> 1 every SWEEP_SECONDS; --reduce sets the
##   library's `reduce_effects` global to 1 for this run only (the setting is not saved).
## Capture through tools/run_windowed.py with Movie Maker (ANIMATION_HANDOFF 6).

const SHADERS := {
	"glass_blur": "res://shaders/glass_blur.gdshader",
	"crt_overlay": "res://shaders/crt_overlay.gdshader",
	"paper_burn": "res://shaders/paper_burn.gdshader",
	"glitch_dissolve": "res://shaders/glitch_dissolve.gdshader",
	"marker_stroke": "res://shaders/marker_stroke.gdshader",
	"halftone": "res://shaders/halftone.gdshader",
}
## Tile layout (px): 3 columns x 2 rows under a title row.
const TILE := Vector2(400, 316)
const GAP := 16.0
const TOP := 56.0
const LABEL_H := 24.0
const TITLE_FONT := 22
const LABEL_FONT := 15
## The progress every shader is held at for a still, and the sweep period with --animate.
const HOLD_PROGRESS := 0.45
const SWEEP_SECONDS := 2.4
## Backdrop art: stripe width and count, and its word (px / count).
const STRIPE_W := 26.0
const STRIPES := 22
const BACKDROP_WORD := "REBEL_CELL"
const BACKDROP_FONT := 54
## Demo strengths (shown larger than in game so a still reads; the defaults are subtler).
const CRT_DEMO := {"scan_strength": 0.18, "roll_strength": 0.25, "roll_period": 3.0, "flicker": 0.02, "fringe_px": 2.0, "vignette": 0.45}
const GLITCH_DEMO := {"shift_px": 26.0, "split_px": 4.0}
const HALFTONE_DEMO := {"dot_px": 7.0, "ink2_amount": 0.4, "misregister_px": 2.0}

var _progress_mats: Array[ShaderMaterial] = []
var _hold: float = HOLD_PROGRESS
var _animate: bool = false
var _t: float = 0.0


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--progress="):
			_hold = clampf(float(arg.trim_prefix("--progress=")), 0.0, 1.0)
		elif arg == "--animate":
			_animate = true
		elif arg == "--reduce":
			# This run only: the library's one control (never the saved setting).
			RenderingServer.global_shader_parameter_set(Fx.REDUCE_GLOBAL, 1.0)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var title := _label("SHADER LAB  //  res://shaders  (reduce_effects = %s)" % ("1" if "--reduce" in OS.get_cmdline_user_args() else "0"), TITLE_FONT, Palette.CELL_PINK)
	title.position = Vector2(GAP, GAP)
	add_child(title)
	var art := _backdrop_texture()
	_tile(0, 0, "glass_blur  (SCRIM, 6 px, 55%)", _glass_blur_demo())
	_tile(1, 0, "crt_overlay  (city and glass)", _textured(art, "crt_overlay", CRT_DEMO))
	_tile(2, 0, "paper_burn", _paper_burn_demo())
	_tile(0, 1, "glitch_dissolve  (jack)", _textured(art, "glitch_dissolve", GLITCH_DEMO, true))
	_tile(1, 1, "marker_stroke  (loop, box, strike)", _marker_demo())
	_tile(2, 1, "halftone  (two-ink riso)", _textured(_photo_texture(), "halftone", HALFTONE_DEMO))
	_set_progress(_hold)


func _process(delta: float) -> void:
	if not _animate:
		return
	_t += delta
	_set_progress(fmod(_t, SWEEP_SECONDS) / SWEEP_SECONDS)


func _set_progress(p: float) -> void:
	for m in _progress_mats:
		m.set_shader_parameter("progress", p)


func _material(name: String, params: Dictionary = {}, has_progress: bool = false) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(SHADERS[name]) as Shader
	for k in params:
		m.set_shader_parameter(k, params[k])
	if has_progress:
		_progress_mats.append(m)
	return m


func _label(text: String, fs: int, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", fs)
	l.add_theme_color_override("font_color", col)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## A tile at column `cx`, row `cy`: `body` fills it under its caption.
func _tile(cx: int, cy: int, caption: String, body: Control) -> void:
	var at := Vector2(GAP + cx * (TILE.x + GAP), TOP + cy * (TILE.y + GAP))
	var frame := Panel.new()
	frame.position = at
	frame.size = TILE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.TERMINAL_BG
	sb.border_color = Palette.TERMINAL_EDGE
	sb.set_border_width_all(1)
	frame.add_theme_stylebox_override("panel", sb)
	add_child(frame)
	var cap := _label(caption, LABEL_FONT, Palette.TERMINAL_TEXT)
	cap.position = Vector2(8, 2)
	frame.add_child(cap)
	body.position = Vector2(0, LABEL_H)
	body.size = TILE - Vector2(0, LABEL_H)
	body.clip_contents = true
	frame.add_child(body)


## The busy neon backdrop (stripes, rings and a word) rendered once into a texture.
func _backdrop_texture() -> Texture2D:
	var vp := SubViewport.new()
	vp.size = Vector2i(TILE - Vector2(0, LABEL_H))
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.transparent_bg = false
	var art := _BackdropArt.new()
	art.size = Vector2(vp.size)
	vp.add_child(art)
	add_child(vp)
	return vp.get_texture()


## A soft "photo" for the halftone: a lit face-like blob and a dark ground.
func _photo_texture() -> Texture2D:
	var g := Gradient.new()
	g.set_color(0, Palette.PAPER)
	g.set_color(1, Palette.INK)
	g.add_point(0.45, Palette.NOTE_PINK.darkened(0.2))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.45, 0.4)
	t.fill_to = Vector2(1.05, 1.0)
	t.width = int(TILE.x)
	t.height = int(TILE.y - LABEL_H)
	return t


func _textured(tex: Texture2D, shader: String, params: Dictionary, has_progress: bool = false) -> Control:
	var r := TextureRect.new()
	r.texture = tex
	r.stretch_mode = TextureRect.STRETCH_SCALE
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	var p := params.duplicate()
	if shader == "halftone":
		p["paper"] = Palette.PAPER
		p["ink"] = Palette.INK
		p["ink2"] = Palette.CELL_PINK
	if shader == "glitch_dissolve":
		p["tint"] = Palette.NET_CYAN
	r.material = _material(shader, p, has_progress)
	return r


func _glass_blur_demo() -> Control:
	var host := Control.new()
	var art := _BackdropArt.new()
	art.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	host.add_child(art)
	var glass := ColorRect.new()
	glass.anchor_left = 0.4
	glass.anchor_right = 1.0
	glass.anchor_bottom = 1.0
	# W1-TOKEN: SCRIM (the bible's #02030A @ 55%): the shader's own default until W1 lands.
	glass.material = _material("glass_blur", {"blur_px": 6.0, "tint_alpha": 0.55})
	host.add_child(glass)
	var words := _label("GLASS\nover the city", LABEL_FONT, Palette.TERMINAL_TEXT)
	words.anchor_left = 0.45
	words.anchor_top = 0.4
	host.add_child(words)
	return host


func _paper_burn_demo() -> Control:
	var host := Control.new()
	var sheet := ColorRect.new()
	sheet.color = Palette.PAPER
	sheet.anchor_left = 0.12
	sheet.anchor_right = 0.88
	sheet.anchor_top = 0.08
	sheet.anchor_bottom = 0.92
	sheet.material = _material("paper_burn", {"ember": Palette.CRT_AMBER}, true)
	host.add_child(sheet)
	return host


func _marker_demo() -> Control:
	var host := ColorRect.new()
	host.color = Palette.PAPER
	var specs := [[0, Vector2(20, 20), Vector2(170, 130)], [1, Vector2(200, 30), Vector2(180, 90)], [2, Vector2(30, 190), Vector2(340, 40)]]
	for s in specs:
		var mark := ColorRect.new()
		mark.position = s[1]
		mark.size = s[2]
		mark.material = _material("marker_stroke", {"shape": s[0], "size_px": s[2], "ink": Palette.CELL_PINK, "boil_fps": 8.0}, true)
		host.add_child(mark)
	var word := Label.new()
	word.text = "SEIZED"
	word.add_theme_font_override("font", Palette.display())
	word.add_theme_font_size_override("font_size", 30)
	word.add_theme_color_override("font_color", Palette.INK)
	word.position = Vector2(236, 50)
	host.add_child(word)
	var line := Label.new()
	line.text = "CARDS  12  ->  11"
	line.add_theme_font_override("font", Palette.display())
	line.add_theme_font_size_override("font_size", 26)
	line.add_theme_color_override("font_color", Palette.INK)
	line.position = Vector2(60, 190)
	host.add_child(line)
	return host


## The lab's busy backdrop: neon stripes, rings and a word on the night.
class _BackdropArt extends Control:
	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), Palette.NET_BG_INNER)
		var inks := [Palette.CELL_PINK, Palette.NET_CYAN, Palette.CELL_ACID, Palette.NEON_VIOLET, Palette.CRT_AMBER]
		for k in STRIPES:
			var x := -size.y + k * STRIPE_W * 1.6
			draw_line(Vector2(x, size.y), Vector2(x + size.y, 0), inks[k % inks.size()], STRIPE_W * 0.35)
		for k in 5:
			draw_arc(Vector2(size.x * (0.15 + k * 0.18), size.y * (0.3 + 0.1 * (k % 2))), 22.0 + k * 6.0, 0, TAU, 32, inks[(k + 2) % inks.size()], 5.0)
		var f := Palette.marker()
		draw_string_outline(f, Vector2(24, size.y * 0.78), BACKDROP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, BACKDROP_FONT, 8, Palette.INK)
		draw_string(f, Vector2(24, size.y * 0.78), BACKDROP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, BACKDROP_FONT, Palette.PAPER)
