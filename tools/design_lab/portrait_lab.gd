extends Control
## ART-9 4B design lab: the operative portraits v2 and the dialogue feed on the real kit
## (PortraitFeed, PortraitArt prints, Polaroid, the Dialogue bar), one page per reference:
##   classes  - 8 classes x 3 rookies on the feed (round 39 portraits_classes_v2);
##   states   - one rookie in every state (round 38 portrait_states);
##   matrix   - every class x every state (the 4B acceptance: every class x state renders);
##   contexts - crew roster CRT rows, the corp dossier print, audit polaroids, DISPATCH;
##   dialogue - the speaker live, the listener dimmed, DISPATCH voice-only, the bar's feed
##              (round 31 dialogue);
##   strip_<s>, column_<s> - the subtitle bar's feed in the HQ strip and in the combat
##              column at text size s (1.0 / 1.6 / 2.0).
## One windowed launch walks every page and saves a PNG per page (the window must render:
## run it through tools/run_windowed.py):
##   python tools/run_windowed.py --log <log> -- res://tools/design_lab/portrait_lab.tscn -- --out=<dir> [--pages=a,b] [--still]
## --still turns reduce effects on first (every feed its end state). View only.

const PAGES: Array[String] = ["classes", "states", "matrix", "contexts", "dialogue", "strip_1.0", "strip_1.6", "strip_2.0", "column_1.0", "column_1.6", "column_2.0"]
const CLASSES: Array[StringName] = [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]
const CALLSIGNS := {
	&"breaker": ["KESTREL", "BRICK", "SAFFRON"], &"wrecker": ["MALLET", "OXIDE", "JUNO"], &"ghost": ["NULLCAT", "WREN", "SLEET"],
	&"phantom": ["MIRAGE", "VESPER", "ECHO"], &"rigger": ["SPROCKET", "TALLY", "KITE"], &"overclocker": ["FUSE", "AMPERE", "CINDER"],
	&"botnet": ["SWARM", "PIXEL", "HIVE-3"], &"hivemind": ["CHORUS", "LATTICE", "MOTH"],
}
## Frames a page settles before its capture.
const SETTLE_FRAMES := 20
const VIEW := Vector2(1280, 720)

var _out := "user://portrait_lab"
var _page_root: Control
var _scale_before := 1.0
var _reduce_before := false


func _ready() -> void:
	size = VIEW
	var pages := PAGES.duplicate()
	var still := false
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--pages="):
			pages.assign(a.trim_prefix("--pages=").split(",", false))
		elif a == "--still":
			still = true
	DirAccess.make_dir_recursive_absolute(_out)
	_scale_before = Settings.text_scale
	_reduce_before = Settings.reduce_effects
	if still != Settings.reduce_effects:
		Settings.set_reduce_effects(still)
		Fx.apply_settings()
	for p in pages:
		await _capture(p)
	Settings.set_text_scale(_scale_before)
	if Settings.reduce_effects != _reduce_before:
		Settings.set_reduce_effects(_reduce_before)
	print("PORTRAIT LAB SAVED ", _out)
	get_tree().quit()


func _capture(page: String) -> void:
	if _page_root != null:
		_page_root.queue_free()
	Dialogue.clear()
	Dialogue.dock_default()
	var ts := 1.0
	if page.contains("_"):
		ts = float(page.get_slice("_", 1))
	if not is_equal_approx(Settings.text_scale, ts):
		Settings.set_text_scale(ts)
	_page_root = Control.new()
	_page_root.size = VIEW
	add_child(_page_root)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.size = VIEW
	_page_root.add_child(bg)
	match page:
		"classes":
			_classes()
		"states":
			_states()
		"matrix":
			_matrix()
		"contexts":
			_contexts()
		"dialogue":
			_dialogue()
		_:
			_docks(page)
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(_out.path_join("%s.png" % page))
	print("PAGE ", page)


func _title(text: String, at: Vector2 = Vector2(24, 10)) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_override("font", Palette.display())
	l.add_theme_font_size_override("font_size", roundi(28.0))
	l.add_theme_color_override("font_color", Palette.RESIST_GOLD)
	_page_root.add_child(l)


func _note(text: String, at: Vector2, col: Color = Palette.TEXT_MID, fs: float = 13.0) -> Label:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", roundi(fs))
	l.add_theme_color_override("font_color", col)
	_page_root.add_child(l)
	return l


func _feed(cls: StringName, op: StringName, callsign: String, mode: int, rect: Rect2) -> PortraitFeed:
	var f := PortraitFeed.new(cls, op, callsign, mode)
	f.position = rect.position
	f.size = rect.size
	_page_root.add_child(f)
	return f


## The operative id whose variant is `k` for `cls` (PortraitBust.variant_for), so the lab
## shows variants 0, 1, 2 as rookies of real ids.
static func op_for(cls: StringName, k: int) -> StringName:
	if k == 0:
		return &""
	for i in 200:
		var id := StringName("op_%d" % i)
		if PortraitBust.variant_for(cls, id) == k:
			return id
	return &""


func _classes() -> void:
	_title("OPERATIVES")
	_note("8 classes x 3 rookies on the CRT comm feed (PortraitFeed + PortraitBust)", Vector2(220, 22))
	var cw := 312.0
	var ch := 330.0
	for i in CLASSES.size():
		var cls := CLASSES[i]
		var o := Vector2(12 + (i % 4) * (cw + 6), 58 + int(i / 4) * (ch + 4))
		var frame := Panel.new()
		frame.position = o
		frame.size = Vector2(cw, ch)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(Palette.NIGHT_SKY.lightened(0.03), 1.0)
		sb.border_color = Color(Palette.class_accent(cls), 0.6)
		sb.set_border_width_all(1)
		sb.set_corner_radius_all(6)
		frame.add_theme_stylebox_override("panel", sb)
		_page_root.add_child(frame)
		var names: Array = CALLSIGNS[cls]
		_feed(cls, op_for(cls, 0), names[0], PortraitFeed.Mode.IDLE, Rect2(o + Vector2(8, 8), Vector2(200, 222)))
		_feed(cls, op_for(cls, 1), names[1], PortraitFeed.Mode.IDLE, Rect2(o + Vector2(212, 8), Vector2(92, 108)))
		_feed(cls, op_for(cls, 2), names[2], PortraitFeed.Mode.IDLE, Rect2(o + Vector2(212, 122), Vector2(92, 108)))
		var l := Label.new()
		l.text = String(cls).to_upper()
		l.position = o + Vector2(10, 236)
		l.add_theme_font_override("font", Palette.display())
		l.add_theme_font_size_override("font_size", roundi(30.0))
		l.add_theme_color_override("font_color", Palette.class_accent(cls))
		_page_root.add_child(l)


func _states() -> void:
	_title("PORTRAIT STATES")
	_note("one rookie (RIGGER // SPROCKET), every state the feed can be in", Vector2(260, 22))
	var modes := [PortraitFeed.Mode.IDLE, PortraitFeed.Mode.TALK, PortraitFeed.Mode.HURT, PortraitFeed.Mode.STATIONED, PortraitFeed.Mode.DEAD, PortraitFeed.Mode.RECRUIT]
	var words := ["IDLE", "TALKING", "HURT", "STATIONED", "FLATLINED", "RECRUIT"]
	for i in modes.size():
		var o := Vector2(20 + (i % 3) * 420, 64 + int(i / 3) * 326)
		var f := _feed(&"rigger", &"", "SPROCKET", modes[i], Rect2(o, Vector2(280, 310)))
		f.site = "LANE 15 RELAY"
		f.hire_cost = 15
		if modes[i] == PortraitFeed.Mode.RECRUIT:
			f.callsign = "ROOKIE"
		if modes[i] == PortraitFeed.Mode.HURT:
			f.hp = 12
			f.max_hp = 55
		var l := Label.new()
		l.text = words[i]
		l.position = o + Vector2(292, 4)
		l.add_theme_font_override("font", Palette.display())
		l.add_theme_font_size_override("font_size", roundi(30.0))
		l.add_theme_color_override("font_color", Palette.HARM if modes[i] in [PortraitFeed.Mode.HURT, PortraitFeed.Mode.DEAD] else Palette.class_accent(&"rigger"))
		_page_root.add_child(l)


func _matrix() -> void:
	_title("EVERY CLASS x STATE")
	var modes := [PortraitFeed.Mode.IDLE, PortraitFeed.Mode.TALK, PortraitFeed.Mode.HURT, PortraitFeed.Mode.STATIONED, PortraitFeed.Mode.DEAD, PortraitFeed.Mode.RECRUIT, PortraitFeed.Mode.PRINT]
	var w := 78.0
	var h := 79.0
	for r in CLASSES.size():
		for c in modes.size():
			var f := _feed(CLASSES[r], op_for(CLASSES[r], r % 3), "", modes[c], Rect2(Vector2(140 + c * (w + 8), 52 + r * (h + 1)), Vector2(w, h)))
			f.hp = 5
			f.max_hp = 50
		_note(String(CLASSES[r]).to_upper(), Vector2(20, 52 + r * (h + 1) + h * 0.4), Palette.class_accent(CLASSES[r]))
	var f2 := PortraitFeed.dispatch()
	f2.position = Vector2(820, 60)
	f2.size = Vector2(300, 190)
	_page_root.add_child(f2)


func _contexts() -> void:
	_title("PORTRAIT CONTEXTS")
	# Crew roster (CRT rows).
	var win := TerminalWindow.new("> CREW ROSTER")
	win.position = Vector2(24, 60)
	win.custom_minimum_size = Vector2(520, 0)
	_page_root.add_child(win)
	var rows := [[&"rigger", "SPROCKET", PortraitFeed.Mode.IDLE, "READY"], [&"ghost", "WREN", PortraitFeed.Mode.STATIONED, "ON LANE 15 RELAY"],
		[&"breaker", "SAFFRON", PortraitFeed.Mode.IDLE, "READY"], [&"botnet", "SWARM", PortraitFeed.Mode.DEAD, "FLATLINED"]]
	for row in rows:
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 14)
		var f := PortraitFeed.new(row[0], op_for(row[0], 1), row[1], row[2])
		f.custom_minimum_size = Vector2(76, 84)
		hb.add_child(f)
		var vb := VBoxContainer.new()
		var n := Label.new()
		n.text = row[1]
		n.add_theme_font_override("font", Palette.display())
		n.add_theme_font_size_override("font_size", roundi(24.0))
		vb.add_child(n)
		var k := Label.new()
		k.text = "%s  //  RANK 1" % String(row[0]).to_upper()
		k.add_theme_color_override("font_color", Palette.class_accent(row[0]))
		vb.add_child(k)
		vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hb.add_child(vb)
		var st := Label.new()
		st.text = row[3]
		st.add_theme_color_override("font_color", Palette.HARM if row[2] == PortraitFeed.Mode.DEAD else Palette.GAIN)
		hb.add_child(st)
		win.body.add_child(hb)
	# Corp dossier: the print, paper-clipped, ringed in red pencil.
	var paper := ColorRect.new()
	paper.color = Palette.PAPER
	paper.position = Vector2(600, 70)
	paper.size = Vector2(430, 300)
	paper.rotation_degrees = -2.0
	_page_root.add_child(paper)
	var pf := PortraitFeed.new(&"rigger", &"", "SPROCKET", PortraitFeed.Mode.PRINT)
	pf.position = Vector2(24, 60)
	pf.size = Vector2(150, 166)
	paper.add_child(pf)
	var ring := Control.new()
	ring.size = paper.size
	ring.draw.connect(func() -> void:
		ring.draw_arc(Vector2(99, 143), 92.0, 0.0, TAU, 48, Color(PortraitFeed.pencil_red(), 0.9), 4.0, true))
	paper.add_child(ring)
	var head := Label.new()
	head.text = "MERIDIAN FREIGHT // LOSS PREVENTION\nPERSON OF INTEREST // FILE 0419-K"
	head.position = Vector2(20, 12)
	head.add_theme_color_override("font_color", Palette.CORP_MERIDIAN.darkened(0.3))
	head.add_theme_font_override("font", Palette.paper_bold())
	paper.add_child(head)
	# Audit polaroids (print; KIA crossed out).
	var x := 640.0
	for p in [[&"ghost", "WREN r1", false], [&"breaker", "SAFFRON r0", false], [&"botnet", "SWARM KIA", true]]:
		var pol := Polaroid.new(p[1], "[PORTRAIT]", -3.0 + x * 0.004)
		pol.position = Vector2(x, 420)
		pol.size = Vector2(150, 182)
		pol.kia = p[2]
		_page_root.add_child(pol)
		pol.set_operative(p[0], op_for(p[0], 1))
		x += 170.0
	# Contacts: DISPATCH never gets a face.
	var d := PortraitFeed.dispatch()
	d.position = Vector2(30, 470)
	d.size = Vector2(300, 190)
	_page_root.add_child(d)
	_note("DISPATCH: never a face, red voice trace", Vector2(30, 668), Palette.TEXT_MID)


func _dialogue() -> void:
	_title("BRIEFING", Vector2(180, 40))
	var speaker := _feed(&"breaker", op_for(&"breaker", 2), "SAFFRON", PortraitFeed.Mode.TALK, Rect2(60, 110, 300, 334))
	speaker.label_text = "COMMS // SAFFRON"
	var listener := _feed(&"ghost", op_for(&"ghost", 1), "WREN", PortraitFeed.Mode.IDLE, Rect2(1000, 200, 220, 244))
	listener.label_text = "CELL-9 // GHOST"
	listener.set_dimmed(true)
	var d := PortraitFeed.dispatch()
	d.position = Vector2(960, 24)
	d.size = Vector2(270, 150)
	_page_root.add_child(d)
	Dialogue.dock_at(Rect2(380, 300, 600, 170), 4)
	Dialogue.bark(&"breaker", "jack_in", 3)
	if not Dialogue.is_showing():
		Dialogue.say(RC.Voice.STREET_MERC, "Meridian moved the depot's Rack to the back lot. Logistics Director sits on it now. Two elite routers on the way in.", 30.0, &"", false, "", &"breaker")
	Dialogue.say(RC.Voice.DISPATCH, "Cell, the depot's yours. Keep it quiet.", 30.0)


## strip_<s>: the HQ / netrun strip (the default dock, one line) with DISPATCH, then (column_<s>)
## the combat column dock (paged lines, the name on its own row) with an operative's bark.
func _docks(page: String) -> void:
	var ts := Settings.text_scale
	_title("SUBTITLE FEED  %s" % page.to_upper())
	if page.begins_with("strip"):
		var strip := Rect2(8, 60, 964, Dialogue.band_height(1))
		_marker(strip)
		Dialogue.set_default_rect(strip, _page_root)
		Dialogue.dock_default()
		Dialogue.say(RC.Voice.DISPATCH, "Cell, the depot's yours. Keep it quiet and get out before the sweep.", 30.0)
	else:
		var lines := 3
		var col := Rect2(930, 60, 330, (24.0 + lines * 19.0) * ts)
		_marker(col)
		Dialogue.dock_at(col, lines)
		Dialogue.say(RC.Voice.STREET_MERC, "Wheel's hot. Give me one clean spin and this thing folds.", 30.0, &"", false, "", &"wrecker")


func _marker(r: Rect2) -> void:
	var box := ColorRect.new()
	box.color = Color(Palette.TEXT_LO, 0.12)
	box.position = r.position - Vector2(0, 4)
	box.size = r.size + Vector2(0, 8)
	_page_root.add_child(box)
