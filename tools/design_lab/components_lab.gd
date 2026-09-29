extends Control
## Design lab (not part of the game): the art pass W2 component kit (ART_BIBLE §6) with
## every component in all six states side by side (idle, hover, focus, pressed, disabled,
## refused; states forced through KitState), plus the one toast (refusal and note), a
## tooltip, the SAVED stamp, a stamp and the status and kit icons. `--glyphs` draws the pad
## glyph sheet instead: every set (Xbox, PlayStation, Switch, Steam Deck) x every button,
## and a prompt bar per set. The sheet renders in a SubViewport at reference pixels (1:1).
##
## View: python tools/run_windowed.py --log lab.log -- res://tools/design_lab/components_lab.tscn
## Flags after a second `--`: `--scale=1.6` (text scale; the player's setting is never
## saved), `--state=<idle|hover|focus|pressed|disabled|refused>` (that state only),
## `--glyphs`, `--out=C:/path/sheet.png` (save and quit).

const MARGIN := 32
const CELL_GAP := Vector2(24, 20)
const ROW_LABEL_W := 150
const SECTION_GAP := 36
## Frames to wait before saving (layout settles, the SubViewport draws).
const SAVE_AFTER_FRAMES := 8
## The sheet's width when it can't be measured yet (px).
const SHEET_MIN := Vector2i(1280, 720)

var viewport: SubViewport
var sheet: Control
var _states: Array[StringName] = KitState.ALL.duplicate()
var _glyphs := false
var _scale := 1.0
var _was_scale := 1.0
var _place_toasts: Callable = Callable()


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--scale="):
			_scale = float(a.trim_prefix("--scale="))
		elif a.begins_with("--state="):
			var st := StringName(a.trim_prefix("--state="))
			if KitState.ALL.has(st):
				_states = [st]
		elif a == "--glyphs":
			_glyphs = true
	# The lab's text scale lasts for this run only (never saved to the player's settings).
	_was_scale = Settings.text_scale
	Settings.text_scale = _scale
	viewport = SubViewport.new()
	viewport.size = SHEET_MIN
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(viewport)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewport.add_child(bg)
	sheet = VBoxContainer.new()
	sheet.position = Vector2(MARGIN, MARGIN)
	sheet.add_theme_constant_override("separation", SECTION_GAP)
	UiTheme.apply(sheet)
	viewport.add_child(sheet)
	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scroll)
	var view := TextureRect.new()
	view.texture = viewport.get_texture()
	scroll.add_child(view)
	_title("COMPONENT KIT  //  ART_BIBLE §6  (W2)", "text scale %.1f · reference px 1:1 · states forced (KitState)" % _scale)
	if _glyphs:
		_glyph_sheet()
	else:
		_state_grid()
		_extras()
	await get_tree().process_frame
	await get_tree().process_frame
	if _place_toasts.is_valid():
		_place_toasts.call()
	var need := Vector2i(sheet.get_combined_minimum_size()) + Vector2i(MARGIN * 2, MARGIN * 2)
	viewport.size = Vector2i(maxi(SHEET_MIN.x, need.x), maxi(SHEET_MIN.y, need.y))
	view.custom_minimum_size = Vector2(viewport.size)
	if out != "":
		for i in SAVE_AFTER_FRAMES:
			await RenderingServer.frame_post_draw
		var err := viewport.get_texture().get_image().save_png(out)
		print("components_lab: saved %s (%s)" % [out, error_string(err)])
		Settings.text_scale = _was_scale
		get_tree().quit(0 if err == OK else 1)


func _exit_tree() -> void:
	Settings.text_scale = _was_scale


func _label(text: String, step: int = UiTheme.CAPTION, col: Color = Palette.TEXT_MID, font: Font = null) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(step))
	l.add_theme_color_override(&"font_color", col)
	if font != null:
		l.add_theme_font_override(&"font", font)
	return l


func _title(text: String, note: String) -> void:
	var box := VBoxContainer.new()
	box.add_child(_label(text, UiTheme.HEADING, Palette.TEXT_HI, Palette.display()))
	box.add_child(_label(note))
	sheet.add_child(box)


func _section(text: String) -> VBoxContainer:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", UiTheme.SP_S)
	box.add_child(_label(text, UiTheme.TITLE, Palette.CELL_ACID))
	sheet.add_child(box)
	return box


## One component per row, one state per column.
func _state_grid() -> void:
	var sec := _section("§6 SIX STATES  ·  §6.4 BUTTONS  ·  §6.5 INPUTS  ·  §6.6 STAMP")
	var grid := GridContainer.new()
	grid.columns = _states.size() + 1
	grid.add_theme_constant_override("h_separation", int(CELL_GAP.x))
	grid.add_theme_constant_override("v_separation", int(CELL_GAP.y))
	sec.add_child(grid)
	var head := _label("", UiTheme.LABEL)
	head.custom_minimum_size.x = ROW_LABEL_W
	grid.add_child(head)
	for st in _states:
		grid.add_child(_label(String(st).to_upper(), UiTheme.LABEL, Palette.TEXT_HI))
	for row in _rows():
		grid.add_child(_label(String(row[0]), UiTheme.BODY, Palette.TEXT_MID))
		for st in _states:
			var c: Control = (row[1] as Callable).call()
			var cell := CenterContainer.new()
			cell.custom_minimum_size = Vector2(0, UiTheme.font_px(UiTheme.TITLE) * 2)
			cell.add_child(c)
			grid.add_child(cell)
			_force.call_deferred(c, st)


## [row name, maker] for every component row.
func _rows() -> Array:
	return [
		["PRIMARY", func() -> Control: return _button("CONTINUE", UiTheme.PRIMARY)],
		["SECONDARY", func() -> Control: return _button("BACK", UiTheme.SECONDARY)],
		["TERTIARY", func() -> Control: return _button("SKIP", UiTheme.TERTIARY, StatIcon.SKIP)],
		["DANGER", func() -> Control: return _button("DELETE", UiTheme.DANGER)],
		["MENU ITEM", func() -> Control: return _button("CODEX", &"MenuItem")],
		["TOGGLE", func() -> Control: return ZineToggle.new("Subtitles", true)],
		["SLIDER", func() -> Control:
			var s := ZineSlider.new(0.8, 2.0, 0.1, 1.6)
			s.format = func(v: float) -> String: return "%.1f×" % v
			return s],
		["STEPPER", func() -> Control:
			var s := Stepper.new(0, 5, 1, 3)
			return s],
		["TILE PICKER", func() -> Control:
			var tiles: Array[Dictionary] = [{"name": "SOLACE", "meta": "Biosystems", "icon": StatIcon.HOME},
				{"name": "ORBITAL", "meta": "Commons", "icon": StatIcon.SHOP, "locked": true, "unlock": "Win a campaign"}]
			return TilePicker.new(tiles)],
		["CODE FIELD", func() -> Control: return CodeField.new("7Q4K-22XB", true)],
		["STAMP", func() -> Control: return ZineStamp.new("JACK IN")],
		["STICKER", func() -> Control:
			var s := StickerButton.new("RESPIN", Palette.NOTE_YELLOW, -3.0)
			s.drawn_icon = "respin"
			return s],
	]


func _button(text: String, variation: StringName, icon: StringName = &"") -> Button:
	var b := Button.new()
	b.text = text
	b.theme_type_variation = variation
	if icon != &"":
		IconMark.attach(b, icon)
	return b


## Shows `st` on `c`: kit components by KitState.force, native controls by force_native.
func _force(c: Control, st: StringName) -> void:
	if c is CodeField:
		var cf := c as CodeField
		match st:
			KitState.HOVER, KitState.PRESSED:
				KitState.force_native(cf.copy_button, st)
			KitState.DISABLED:
				cf.disabled = true
				KitState.force_native(cf.field, st)
			KitState.FOCUS, KitState.REFUSED:
				KitState.force_native(cf.field, st)
		return
	if c is ZineToggle or c is ZineSlider or c is Stepper or c is TilePicker or c is ZineStamp or c is StickerButton:
		if st == KitState.DISABLED and c is BaseButton:
			(c as BaseButton).disabled = true
		elif st == KitState.DISABLED:
			c.set(&"disabled", true)
		KitState.force(c, st)
		return
	KitState.force_native(c, st)


func _extras() -> void:
	var sec := _section("§6.7 THE ONE TOAST  ·  §6.8 TOOLTIP  ·  SAVED  ·  §7.4 ICONS")
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", int(CELL_GAP.x) * 2)
	sec.add_child(row)
	var host := Control.new()
	host.custom_minimum_size = Vector2(900, 150) * _scale
	row.add_child(host)
	var refusal := Toast.new()
	host.add_child(refusal)
	var note := Toast.new()
	host.add_child(note)
	# The toasts' spots are global: placed once the sheet has laid out.
	_place_toasts = func() -> void:
		refusal.show_text("Not enough RAM: NEED 3 · HAVE 1", host.global_position + Vector2(220, 70) * _scale, 380 * _scale)
		note.show_note("Respin landed on DEFEND again.", host.global_position + Vector2(640, 70) * _scale, 380 * _scale)
	var saved := Label.new()
	saved.text = "SAVED"
	saved.add_theme_font_override(&"font", Palette.marker())
	saved.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.LABEL))
	saved.add_theme_color_override(&"font_color", Palette.INK)
	var paper := Toast.note_style()
	paper.content_margin_left = 8
	paper.content_margin_right = 8
	saved.add_theme_stylebox_override(&"normal", paper)
	saved.position = Vector2(220, 100) * _scale
	host.add_child(saved)
	var tip := PanelContainer.new()
	tip.theme_type_variation = &"TooltipPanel"
	tip.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	tip.add_child(UiTip.make("Daemon Twin Pointer\nYour wheel is also read at the bottom: both reads trigger.", "Twin Pointer"))
	row.add_child(tip)
	var icons := _IconRow.new()
	icons.custom_minimum_size = Vector2((StatIcon.STATUS_KINDS.size() + StatIcon.KIT_KINDS.size()) * 2 * 36, 48) * _scale
	icons.s = _scale
	sec.add_child(icons)
	sec.add_child(_label("status icons (open / filled when active) then the kit's marks: lock, no-entry, info, close, trash, copy, plus, minus, check"))


func _glyph_sheet() -> void:
	for s in PadGlyph.SETS:
		var sec := _section(String(s).to_upper())
		var grid := GridContainer.new()
		grid.columns = PadGlyph.BUTTONS.size()
		grid.add_theme_constant_override("h_separation", UiTheme.SP_M)
		grid.add_theme_constant_override("v_separation", UiTheme.SP_XS)
		sec.add_child(grid)
		for b in PadGlyph.BUTTONS:
			var g := PadGlyph.new(b, s)
			var cell := CenterContainer.new()
			cell.add_child(g)
			grid.add_child(cell)
		for b in PadGlyph.BUTTONS:
			grid.add_child(_label(PadGlyph.name_of(b, s)))
		var bar := HBoxContainer.new()
		bar.add_theme_constant_override("separation", UiTheme.SP_L)
		for p in [[PadGlyph.FACE_SOUTH, "Buy"], [PadGlyph.FACE_EAST, "Leave"], [PadGlyph.FACE_NORTH, "Inspect"], [PadGlyph.MENU, "Settings"],
				[PadGlyph.TRIGGER_L, "Wheel"], [PadGlyph.DPAD, "Move"]]:
			var pair := PadPrompts.make_pair(int(p[0]), String(p[1]))
			(pair.get_child(0) as PadGlyph).glyph_set = s
			bar.add_child(pair)
		sec.add_child(bar)


## The status icons (open, filled) and the kit's marks.
class _IconRow extends Control:
	var s := 1.0

	func _draw() -> void:
		var x := 18.0 * s
		var kinds: Array = StatIcon.STATUS_KINDS.values()
		for k in kinds:
			for filled in [false, true]:
				StatIcon.draw(self, Vector2(x, 24 * s), 12.0 * s, k, StatIcon.color_of(k), filled)
				x += 36.0 * s
		x += 24.0 * s
		for k in StatIcon.KIT_KINDS:
			StatIcon.draw(self, Vector2(x, 24 * s), 12.0 * s, k, StatIcon.color_of(k), k == StatIcon.NO_ENTRY or k == StatIcon.INFO)
			x += 36.0 * s
