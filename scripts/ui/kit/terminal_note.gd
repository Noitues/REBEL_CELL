class_name TerminalNote
extends ZineNote
## ART-2 2D (ART_BIBLE v2 §4.13): a ZineNote on a terminal panel (the combat tutorial's note):
## dark CRT glass, a chamfered corner, a `> TITLE` header in mono caps over a cyan rule, the
## text in the terminal colour. Same API and paging as ZineNote. View only.

## Header lettering (px at text scale 1.0) and the header's height.
const HEADER_FONT := 14
const HEADER_H := 24.0


func _init(p_title: String = "", min_size: Vector2 = Vector2(240, 120)) -> void:
	PaletteSkins.watch(self)  # ART-12 12s-b: the skin's chrome follows a pick
	super(p_title, min_size)
	paper_color = HudSkin.TERMINAL_BG
	# B5 (B1c follow-up 2): the kit's CRT glass behind the note (the hex dump fades under its words).
	CrtTerminalPanel.behind(self)
	label.offset_top = HEADER_H + 4.0 if p_title != "" else 8.0
	label.add_theme_color_override("default_color", HudSkin.TERMINAL_TEXT)
	label.add_theme_font_override("normal_font", HudSkin.body())


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	HudSkin.draw_terminal_edge(self, r, HudSkin.TERMINAL_EDGE)
	if title == "":
		return
	var f := HudSkin.mono()
	var fs := roundi(HEADER_FONT * minf(Settings.text_scale, 1.0))
	draw_string(f, Vector2(10.0, (HEADER_H + f.get_ascent(fs) - f.get_descent(fs)) * 0.5), "> " + title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, HudSkin.TERMINAL_HI)
	draw_line(Vector2(0.0, HEADER_H), Vector2(size.x - HudSkin.CHAMFER, HEADER_H), Color(PaletteSkins.chrome(HudSkin.TERMINAL_EDGE), 0.6), 1.0)
