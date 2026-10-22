extends RcLookLabStage
## LOOK-TOOLBOX module 14, the reduce-effects ruling sheet: what "reduce effects" does to the CRT glass under the three
## conventions the code has today, side by side, on the terminal glass (scanlines, flicker, roll) and on the screen
## overlay (the fx_overlay vignette and flicker over a busy card). Column 0 is effects on; 1 KEEP_STATIC (the shaders'
## rc_live: motion stops, static scanlines stay); 2 ZERO_SCAN (ui_theme, neon_city: a script zeroes the scanline strength
## too); 3 HIDE (fx.gd: the whole overlay layer is hidden). Fixed clock, like crt_stage. The lab's reduce-effects flag is
## ignored: every convention is shown at once.

const CrtStage := preload("res://addons/rc_look/lab/stages/crt_stage.gd")

const MARGIN := Vector2(40.0, 60.0)
const GAP := Vector2(24.0, 22.0)
const LABEL_SIZE := 13
const TEXT_SIZE := 15
const PANEL_H := 150.0
const COLUMNS := 4
## Column captions (the convention and the code that does it).
const CAPTIONS: Array[String] = ["effects on", "KEEP_STATIC: rc_live in the shader; motion stops, scanlines stay (crt_terminal, crt_panel, city_sketch, city_live when a view leaves the strength alone)",
		"ZERO_SCAN: a script zeroes scan_strength and flicker (ui_theme._sync_crt, neon_city)",
		"HIDE: the overlay layer is hidden (fx.gd: scanlines.visible = not reduce_effects)"]
const CONVENTIONS: Array[int] = [-1, RcLookCrt.Reduce.KEEP_STATIC, RcLookCrt.Reduce.ZERO_SCAN, RcLookCrt.Reduce.HIDE]
const ROWS: Array[StringName] = [&"terminal", &"fx_overlay"]
const BODY_LINES := ["> COLLECTOR  >  HOME SERVER", "> KEY 4C-E7  ACCEPTED", "> ROUTE  WEAKEST NODE"]
const CARD_BLOCK := Color(0.85, 0.8, 0.7)
## The recommendation (one paragraph; the ruling is the designer's).
const RECOMMENDATION := "Recommendation: KEEP_STATIC everywhere, one rule. Reduce effects exists for motion and flashes (ART_BIBLE §5.4: scroll, flicker, roll, aberration); a scanline pattern is a still texture, and it is what makes a screen read as a screen, so removing it changes the look without helping anyone. The shaders already do exactly this through rc_live, and the code that zeroes scan_strength on the CPU (ui_theme, neon_city) or hides the overlay (fx.gd) leaves the same screen looking different on each path. Only high contrast should take the static texture away (it already does on the terminal glass). One cost: fx.gd's overlay carries only the vignette and a 1 % flicker once Fx zeroes its scanlines, so KEEP_STATIC there means the vignette stays under reduce effects, as the paper look expects."


func _ready() -> void:
	var view := get_viewport_rect().size
	var col_w := (view.x - MARGIN.x * 2.0 - GAP.x * (COLUMNS - 1)) / COLUMNS
	var title := _label("Reduce effects on the CRT glass: the three conventions, side by side (fixed clock).", Vector2(MARGIN.x, 16.0), LABEL_SIZE)
	title.add_theme_color_override(&"font_color", Color.WHITE)
	var y := MARGIN.y
	for row in ROWS.size():
		var p := RcLookCrt.preset(ROWS[row])
		if row == 0:
			for c in COLUMNS:
				_label(CAPTIONS[c], Vector2(MARGIN.x + c * (col_w + GAP.x), y), LABEL_SIZE, col_w)
			y += 5.0 * (LABEL_SIZE + 6.0) + 12.0
		_label(String(ROWS[row]), Vector2(MARGIN.x, y - LABEL_SIZE - 4.0), LABEL_SIZE)
		for c in COLUMNS:
			var at := Vector2(MARGIN.x + c * (col_w + GAP.x), y)
			var r := RcLookCrt.resolve(p, c > 0, CONVENTIONS[c])
			var glass := _rect(at, Vector2(col_w, PANEL_H), 0)
			if row == 0:
				for i in BODY_LINES.size():
					_label(BODY_LINES[i], at + Vector2(p.glow_px + 14.0, p.glow_px + 14.0 + i * 28.0), TEXT_SIZE)
			else:
				var card := ColorRect.new()
				card.color = CARD_BLOCK
				card.position = at + Vector2(p.glow_px, p.glow_px)
				card.size = Vector2(col_w - p.glow_px * 2.0, PANEL_H - p.glow_px * 2.0)
				add_child(card)
			var over := _rect(at, Vector2(col_w, PANEL_H), 1)
			CrtStage._fill(glass, p, RcLookCrt.resolve(p, false) if row == 1 else r)
			CrtStage._fill(over, p, r)
		y += PANEL_H + GAP.y + LABEL_SIZE + 4.0
	_label(RECOMMENDATION, Vector2(MARGIN.x, y), LABEL_SIZE, view.x - MARGIN.x * 2.0)


func settle_frames() -> int:
	return 12


func _rect(at: Vector2, size_px: Vector2, mode: int) -> ColorRect:
	var rc := ColorRect.new()
	rc.position = at
	rc.size = size_px
	var m := ShaderMaterial.new()
	m.shader = CrtStage._shader(CrtStage.PANEL_CODE)
	m.set_shader_parameter(&"mode", mode)
	rc.material = m
	add_child(rc)
	return rc


func _label(text: String, at: Vector2, px: int, width: float = 0.0) -> Label:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", px)
	if width > 0.0:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = width
	add_child(l)
	return l
