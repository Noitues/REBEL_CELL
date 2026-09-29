extends Control
## Design lab (not part of the game): the W4 card sheet (ART_BIBLE 6.3, 7.3). Real
## ZineCards at one text scale: the three card types (paper / black / pink) at each rarity,
## compact (hand) and full (fit_whole) faces, one card per illustration family, and the
## detail-size card. The sheet renders in a SubViewport at reference pixels (1:1).
##
## View: python tools/run_windowed.py --log lab.log -- res://tools/design_lab/cards_lab.tscn
## Options after a second `--`:
##   --scale=1.6          text scale of the sheet (default 1.0)
##   --out=C:/path.png    save the sheet as a PNG and quit
##   --foil-strip         a rare card at a row of foil tilts instead of the sheet
##   --detail             the detail view (DeckView's card detail) instead of the sheet
##   --reduce             reduce effects on for this run (never saved)

const WIDTH := 1600
const MARGIN := 32.0
const GAP := 18.0
const LABEL_GAP := 6.0
## Frames to wait before saving (the SubViewport and the art queue draw over a few frames).
const SAVE_AFTER_FRAMES := 90
## Types x rarities: [type word, [common, uncommon, rare]].
const TYPE_ROWS := [
	["WHEEL (paper)", [&"jolt", &"spin_cycle", &"overclock_nudges"]],
	["SYSTEM (black)", [&"firewall", &"bulwark", &"stim_patch"]],
	["HACK (pink)", [&"static_shock", &"arc_flash", &"short_circuit"]],
]
## Tilts shown by the foil strip (x, y in -1..1).
const FOIL_TILTS: Array[Vector2] = [Vector2(-1, -0.4), Vector2(-0.6, 0), Vector2(-0.2, 0.3), Vector2(0.2, 0.3), Vector2(0.6, 0), Vector2(1, -0.4)]

var viewport: SubViewport
var sheet: VBoxContainer
var scale_k: float = 1.0


func _ready() -> void:
	var out := ""
	var mode := "sheet"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--scale="):
			scale_k = float(a.trim_prefix("--scale="))
		elif a == "--foil-strip":
			mode = "foil"
		elif a == "--detail":
			mode = "detail"
		elif a == "--reduce":
			# This run only (never saved): the setting in memory and the shader global.
			Settings.reduce_effects = true
			RenderingServer.global_shader_parameter_set(Fx.REDUCE_GLOBAL, 1.0)
	Settings.text_scale = scale_k
	UiTheme.apply(self)
	viewport = SubViewport.new()
	viewport.size = Vector2i(WIDTH, 800)
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(viewport)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewport.add_child(bg)
	sheet = VBoxContainer.new()
	sheet.position = Vector2(MARGIN, MARGIN)
	sheet.custom_minimum_size.x = WIDTH - MARGIN * 2.0
	sheet.add_theme_constant_override("separation", roundi(GAP * 2.0))
	viewport.add_child(sheet)
	match mode:
		"foil":
			_foil_strip()
		"detail":
			_detail()
		_:
			_sheet()
	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scroll)
	var view := TextureRect.new()
	view.texture = viewport.get_texture()
	scroll.add_child(view)
	await get_tree().process_frame
	await get_tree().process_frame
	viewport.size = Vector2i(WIDTH, ceili(sheet.get_combined_minimum_size().y + MARGIN * 2.0))
	if out != "":
		for i in SAVE_AFTER_FRAMES:
			await RenderingServer.frame_post_draw
		var err := viewport.get_texture().get_image().save_png(out)
		print("cards_lab: saved %s (%s)" % [out, error_string(err)])
		get_tree().quit(0 if err == OK else 1)


func _card(id: StringName) -> CardData:
	return load("res://content/cards/%s.tres" % id) as CardData


func _zine(card: CardData, full: bool) -> ZineCard:
	var z := ZineCard.new(TextDb.t(card, "display_name"), card.ram_cost, TextDb.t(card, "description"), 0).scaled(scale_k).with_card(card)
	z.fit_whole = full
	z.focus_mode = Control.FOCUS_NONE
	return z


func _heading(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", Palette.CELL_ACID)
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", UiTheme.font_px_at(UiTheme.TITLE, scale_k))
	return l


func _caption(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", Palette.TEXT_MID)
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", UiTheme.font_px_at(UiTheme.CAPTION, scale_k))
	return l


## A card with a caption under it.
func _cell(z: Control, text: String) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", roundi(LABEL_GAP * scale_k))
	z.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	v.add_child(z)
	v.add_child(_caption(text))
	return v


func _row() -> HFlowContainer:
	var r := HFlowContainer.new()
	r.custom_minimum_size.x = WIDTH - MARGIN * 2.0
	r.add_theme_constant_override("h_separation", roundi(GAP * scale_k))
	r.add_theme_constant_override("v_separation", roundi(GAP * scale_k))
	return r


func _sheet() -> void:
	sheet.add_child(_heading("W4 CARDS  //  ART_BIBLE 6.3, 7.3  //  text scale %.1f" % scale_k))
	sheet.add_child(_heading("TYPE x RARITY  (compact hand face | full face)"))
	for row_def in TYPE_ROWS:
		var row := _row()
		for id in row_def[1]:
			var card := _card(id)
			var words := "%s / %s" % [String(row_def[0]), String(RC.Rarity.keys()[card.rarity])]
			row.add_child(_cell(_zine(card, false), words))
			row.add_child(_cell(_zine(card, true), "full"))
		sheet.add_child(row)
	_families()


## One card per illustration family (the base art, tinted by its type), then every card
## with unique art (rares and class cards, Q1).
func _families() -> void:
	var by_family := {}
	var unique: Array[CardData] = []
	var names := DirAccess.get_files_at("res://content/cards")
	names.sort()
	for f in names:
		if not f.ends_with(".tres"):
			continue
		var card := load("res://content/cards/" + f) as CardData
		var fam := CardArt.family_of(card)
		if not by_family.has(fam):
			by_family[fam] = []
		(by_family[fam] as Array).append(card)
		if CardArt.is_unique(card):
			unique.append(card)
	sheet.add_child(_heading("FAMILIES  //  base illustration per effect family (compact face)"))
	var row := _row()
	for fam in CardArt.FAMILIES:
		if by_family.has(fam):
			var cards: Array = by_family[fam]
			var base: CardData = null
			for c: CardData in cards:
				if not CardArt.is_unique(c):
					base = c
					break
			row.add_child(_cell(_zine(base if base != null else cards[0], false), "%s (%d)" % [fam, cards.size()]))
		else:
			var z := ZineCard.new("OVERCLOCK CHIP", -1, "Firmware: your ATTACK slices deal +1.", 0).scaled(scale_k)
			z.focus_mode = Control.FOCUS_NONE
			row.add_child(_cell(z, "%s (no card)" % fam))
	sheet.add_child(row)
	sheet.add_child(_heading("UNIQUE ART  //  rares and class cards (seeded by the card id)"))
	var urow := _row()
	for c in unique:
		urow.add_child(_cell(_zine(c, false), String(c.id)))
	sheet.add_child(urow)


func _foil_strip() -> void:
	sheet.add_child(_heading("FOIL  //  tilts (reduce effects %s)" % Settings.reduce_effects))
	var row := _row()
	for t in FOIL_TILTS:
		var z := _zine(_card(&"short_circuit"), false)
		z.foil_hold = true
		z.foil_tilt = t
		row.add_child(_cell(z, "tilt %.1f, %.1f" % [t.x, t.y]))
	sheet.add_child(row)


func _detail() -> void:
	sheet.add_child(_heading("CARD DETAIL  //  text scale %.1f" % scale_k))
