extends Control
## Design lab (not part of the game): the art pass WF kit follow-ups side by side, for the
## review crops in docs/art_review/WF/: TilePicker tiles with the longest content names
## (item 2), the combat stickers (item 3), Polaroid captions (item 4) and the custom-drawn
## paper pieces (case file, receipt, badges, toast, Polaroid; item 7). Renders in a
## SubViewport at reference pixels (1:1).
##
## View: python tools/run_windowed.py --log lab.log -- res://tools/design_lab/wf_kit_lab.tscn
## Flags after a second `--`: `--scale=2.0` (text scale; never saved), `--hc` (high
## contrast for this run only), `--only=tiles|stickers|polaroids|paper`, `--out=C:/p.png`
## (save and quit).

const MARGIN := 24
const SECTION_GAP := 28
const SAVE_AFTER_FRAMES := 8
const SHEET_MIN := Vector2i(640, 200)
## The combat sticker box's width at 1.0 (px): the column beside SEND IT.
const STICKER_BOX_W := 300.0

var viewport: SubViewport
var sheet: VBoxContainer
var _scale := 1.0
var _hc := false
var _only := ""
var _was_scale := 1.0
var _was_hc := false


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--scale="):
			_scale = float(a.trim_prefix("--scale="))
		elif a.begins_with("--only="):
			_only = a.trim_prefix("--only=")
		elif a == "--hc":
			_hc = true
	_was_scale = Settings.text_scale
	_was_hc = Settings.high_contrast
	Settings.text_scale = _scale
	Settings.high_contrast = _hc
	viewport = SubViewport.new()
	viewport.size = SHEET_MIN
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(viewport)
	var bg := ColorRect.new()
	bg.color = Color.BLACK if _hc else Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewport.add_child(bg)
	sheet = VBoxContainer.new()
	sheet.position = Vector2(MARGIN, MARGIN)
	sheet.add_theme_constant_override("separation", SECTION_GAP)
	UiTheme.apply(sheet)
	viewport.add_child(sheet)
	var view := TextureRect.new()
	view.texture = viewport.get_texture()
	add_child(view)
	var note := _label("text scale %.1f%s" % [_scale, "  ·  high contrast" if _hc else ""])
	sheet.add_child(note)
	if _only in ["", "tiles"]:
		_tiles()
	if _only in ["", "stickers"]:
		_stickers()
	if _only in ["", "polaroids"]:
		_polaroids()
	if _only in ["", "paper"]:
		_paper()
	for i in 3:
		await get_tree().process_frame
	var need := Vector2i(sheet.get_combined_minimum_size()) + Vector2i(MARGIN * 2, MARGIN * 2)
	viewport.size = Vector2i(maxi(SHEET_MIN.x, need.x), maxi(SHEET_MIN.y, need.y))
	view.custom_minimum_size = Vector2(viewport.size)
	if out != "":
		for i in SAVE_AFTER_FRAMES:
			await RenderingServer.frame_post_draw
		var err := viewport.get_texture().get_image().save_png(out)
		print("wf_kit_lab: saved %s (%s)" % [out, error_string(err)])
		_restore()
		get_tree().quit(0 if err == OK else 1)


func _exit_tree() -> void:
	_restore()


func _restore() -> void:
	Settings.text_scale = _was_scale
	Settings.high_contrast = _was_hc


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.CAPTION))
	l.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	return l


func _section(title: String) -> VBoxContainer:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", UiTheme.SP_S)
	box.add_child(_label(title))
	sheet.add_child(box)
	return box


func _tiles() -> void:
	var box := _section("TilePicker: the longest corporation, class and home-server names (§4.3 rule 3)")
	var tiles: Array[Dictionary] = [
		{"name": "Meridian Freight Systems", "meta": "Tier 2", "icon": StatIcon.HOME},
		{"name": "Overclocker", "meta": "Class", "icon": StatIcon.CREW},
		{"name": "Relay Nest home server", "meta": "Home", "icon": StatIcon.HOME},
		{"name": "Orbital Commons", "meta": "", "icon": StatIcon.HOME, "locked": true, "unlock": "Win a campaign"},
	]
	var tp := TilePicker.new(tiles, 4)
	tp.value = 0
	box.add_child(tp)


func _stickers() -> void:
	var box := _section("Combat stickers (RESPIN with its cost and key, UNDO)")
	var row := HBoxContainer.new()
	row.custom_minimum_size.x = STICKER_BOX_W * _scale
	row.add_theme_constant_override("separation", UiTheme.SP_S)
	box.add_child(row)
	for sp in [["RESPIN 2 RAM R", Palette.STICKER_PINK, 3.0, "respin"], ["UNDO Z", Palette.NOTE_PAPER, -3.0, "undo"]]:
		var b := StickerButton.new(sp[0], sp[1], sp[2])
		b.pre_translated = true
		b.drawn_icon = sp[3]
		# The cap as combat will use it (opt-in; the page is the 1280 px reference viewport).
		b.container_width = StickerButton.REFERENCE_WIDTH
		b.max_share = StickerButton.MAX_SHARE
		row.add_child(b)
		b.refit()


func _polaroids() -> void:
	var box := _section("Polaroid captions (combat 110 x 134, crew compact 60 x 74)")
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", UiTheme.SP_L)
	box.add_child(row)
	for spec in [["Breaker", "[BREAKER PORTRAIT]", Vector2(110, 134)], ["Mara Voss-Okonkwo", "[GHOST PORTRAIT]", Vector2(110, 134)],
			["RANK 12", "[RIGGER PORTRAIT]", Vector2(110, 134)], ["Overclocker", "[OVERCLOCKER PORTRAIT]", Vector2(60, 74)]]:
		var p := Polaroid.new(spec[0], spec[1], -3.0)
		p.custom_minimum_size = spec[2]
		var holder := CenterContainer.new()
		holder.custom_minimum_size = spec[2] + Vector2(16, 16)
		holder.add_child(p)
		row.add_child(holder)


func _paper() -> void:
	var box := _section("Paper pieces: case file, receipt, badges, toast, Polaroid")
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", UiTheme.SP_L)
	box.add_child(row)
	var summary := {"corporation": "solace", "heat": 62, "runs": 4, "ice": 3, "saved_at": 1790000000.0, "state": "lost"}
	var crew := [{"id": "op_a", "name": "Mara", "class_id": "breaker", "alive": true}, {"id": "op_b", "name": "Jin", "class_id": "ghost", "alive": false}]
	row.add_child(CaseFileCard.new("1", summary, crew, true))
	var receipts := VBoxContainer.new()
	receipts.add_child(RunReceipt.of_run({"tier": 2, "site": "Patient Records Vault", "outcome": "cleared", "cycles": 34, "banked": 12}, "Solace Biosystems", 0))
	row.add_child(receipts)
	var badges := VBoxContainer.new()
	badges.add_theme_constant_override("separation", UiTheme.SP_S)
	badges.add_child(AchievementBadge.new(&"first_blood", "First Blood", "Finish a run.", true))
	badges.add_child(AchievementBadge.new(&"wall", "The Wall", "Hold a raid.", false))
	row.add_child(badges)
	var right := VBoxContainer.new()
	right.add_theme_constant_override("separation", UiTheme.SP_L)
	row.add_child(right)
	var p := Polaroid.new("RANK 3", "[PHANTOM PORTRAIT]", -3.0)
	p.custom_minimum_size = Vector2(110, 134)
	var ph := CenterContainer.new()
	ph.custom_minimum_size = Vector2(130, 150)
	ph.add_child(p)
	right.add_child(ph)
	var toast := Toast.new()
	toast.top_level = false
	right.add_child(toast)
	toast.show_note("Respin landed on BLOCK.", Vector2.ZERO)
	toast.top_level = false
