extends Control
## Design lab: where installed Daemons live on screen. Each Daemon is a unique sigil
## (DaemonSigil); hover shows a tooltip card, click opens its detail.
## Run: godot --path . res://tools/design_lab/daemon_concepts.tscn

const DAEMONS := [&"twin_pointer", &"shield_cache", &"zero_day", &"feedback_loop", &"cold_exit"]
var art: Control
var lookup: ContentLookup


func _ready() -> void:
	UiTheme.apply(self)
	lookup = RunManager.lookup()
	var bg := WireframeBackground.new()
	bg.city.dim = 0.55
	add_child(bg)
	art = Control.new()
	art.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	art.draw.connect(_draw_art)
	add_child(art)


func _name(id: StringName) -> String:
	var d := lookup.get_content(id) as DaemonData
	return d.display_name if d != null else String(id)


func _draw_art() -> void:
	# D1: a rail of sigils in the top bar, right of the stats; hovered one shows its card.
	_title(Vector2(20, 24), "DAEMON 1  //  TOP-BAR RAIL (hover card)")
	art.draw_rect(Rect2(0, 34, 1280, 56), Color(0.02, 0.04, 0.1, 0.92))
	art.draw_rect(Rect2(0, 88, 1280, 2), Palette.NET_CYAN)
	art.draw_string(Palette.mono(), Vector2(14, 60), "01", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.CELL_PINK)
	art.draw_string(Palette.mono(), Vector2(14, 80), "NETRUN // ROUTE", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Palette.PAPER)
	art.draw_string(Palette.mono(), Vector2(760, 66), "DAEMONS", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.NEON_VIOLET)
	for i in DAEMONS.size():
		DaemonSigil.draw_sigil(art, Vector2(850 + i * 44, 62), 17, DAEMONS[i])
	_hover_card(Vector2(900, 96), DAEMONS[1])
	# D2: sigils orbiting the player's spinner in combat.
	_title(Vector2(20, 300), "DAEMON 2  //  ORBIT THE SPINNER (combat)")
	var c := Vector2(300, 510)
	art.draw_circle(c, 110, Color(0, 0, 0, 0.6))
	art.draw_arc(c, 90, 0, TAU, 64, Palette.CELL_PINK, 30.0)
	art.draw_circle(c, 70, Color("#07080F"))
	for i in DAEMONS.size():
		var a := PI * 0.95 + PI * 0.55 * i / (DAEMONS.size() - 1)
		DaemonSigil.draw_sigil(art, c + Vector2(cos(a), sin(a)) * 150, 19, DAEMONS[i])
	art.draw_string(Palette.mono(), c + Vector2(-150, 150), "pulse when they trigger", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.CELL_ACID)
	# D3: a sticker sheet: each Daemon a die-cut sticker with its sigil and name.
	_title(Vector2(660, 300), "DAEMON 3  //  STICKER SHEET (side panel)")
	var sheet := Rect2(680, 330, 260, 330)
	art.draw_rect(Rect2(sheet.position + Vector2(5, 6), sheet.size), Palette.SHADOW)
	art.draw_rect(sheet, Palette.NOTE_PAPER)
	art.draw_rect(Rect2(sheet.position + Vector2(100, -7), Vector2(60, 14)), Palette.NOTE_TAPE)
	art.draw_string(Palette.marker(), sheet.position + Vector2(14, 28), "DAEMONS", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Palette.INK)
	for i in DAEMONS.size():
		var p := sheet.position + Vector2(40, 70 + i * 56)
		art.draw_circle(p, 24, Palette.PAPER)
		art.draw_arc(p, 24, 0, TAU, 24, Color(Palette.INK, 0.4), 1.0)
		DaemonSigil.draw_sigil(art, p, 18, DAEMONS[i])
		art.draw_string(Palette.marker(), p + Vector2(34, 6), _name(DAEMONS[i]), HORIZONTAL_ALIGNMENT_LEFT, 180, 15, Palette.INK)
	_detail(Vector2(970, 360), DAEMONS[2])


func _title(at: Vector2, text: String) -> void:
	art.draw_rect(Rect2(at + Vector2(-6, -16), Vector2(430, 22)), Color(0, 0, 0, 0.85))
	art.draw_string(Palette.mono(), at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.CELL_ACID)


func _hover_card(at: Vector2, id: StringName) -> void:
	var d := lookup.get_content(id) as DaemonData
	var r := Rect2(at, Vector2(300, 110))
	art.draw_rect(r, Color(0.02, 0.03, 0.08, 0.97))
	art.draw_rect(r, DaemonSigil.color_of(id), false, 1.5)
	DaemonSigil.draw_sigil(art, at + Vector2(34, 34), 22, id)
	art.draw_string(Palette.display(), at + Vector2(66, 34), _name(id).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Palette.PAPER)
	var desc := d.description if d != null else ""
	art.draw_multiline_string(Palette.mono(), at + Vector2(12, 70), desc, HORIZONTAL_ALIGNMENT_LEFT, 280, 11, 3, Palette.TERMINAL_TEXT)


func _detail(at: Vector2, id: StringName) -> void:
	var d := lookup.get_content(id) as DaemonData
	var r := Rect2(at, Vector2(290, 250))
	art.draw_rect(r, Color(0.02, 0.03, 0.08, 0.97))
	art.draw_rect(r, Palette.CELL_ACID, false, 1.5)
	art.draw_string(Palette.mono(), at + Vector2(12, 20), "CLICK -> DAEMON DETAIL", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.CELL_ACID)
	DaemonSigil.draw_sigil(art, at + Vector2(145, 90), 44, id)
	art.draw_string(Palette.display(), at + Vector2(0, 160), _name(id).to_upper(), HORIZONTAL_ALIGNMENT_CENTER, 290, 22, Palette.PAPER)
	art.draw_multiline_string(Palette.mono(), at + Vector2(12, 190), d.description if d != null else "", HORIZONTAL_ALIGNMENT_LEFT, 266, 11, 4, Palette.TERMINAL_TEXT)
