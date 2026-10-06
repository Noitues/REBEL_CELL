class_name AuditDossier
extends Control
## ART-11 4D: the campaign summary as the corporation's audit dossier on the Cell (ART_BIBLE v2
## §4.8; ref `campaign_end/round21_raid_world/campaign_dossier.jpg`, generator art-concepts-r43
## round 21 dossier21.py): an open manila folder on a desk. Left: prints of the network at the
## end and of the crew, the PERSONNEL sheet (DECEASED / AT LARGE), the annex (the story the
## Cell uncovered, the profile's records). Right: the typed AUDIT REPORT on the corporation's
## letterhead with the Heat trace, CASE CLOSED stamped over it. The auditor's ballpoint
## post-its; NEW CAMPAIGN / MAIN MENU are the Cell's vinyl stickers on the desk. A won
## campaign is the same file, the corporation's failure: AT LARGE stamped instead.
## Motion: the cover swings open (`dossier_open`), the stamp lands (`dossier_stamp`), the
## notes slap on one after another (`dossier_note`, `dossier_note_stagger`); one press
## completes them (MotionSkip); reduce effects and headless show the open file at once.
## View only: the buttons emit `new_campaign_pressed` / `main_menu_pressed` (Signal Up).

signal new_campaign_pressed
signal main_menu_pressed

## B5 (D24): the seed of the dossier sheets' tilts (PaperLie: 1-2 degrees either way, view decoration).
const SHEET_SEED := 2100
const OPEN := &"dossier_open"
const STAMP := &"dossier_stamp"
const NOTE := &"dossier_note"
const NOTE_STAGGER := &"dossier_note_stagger"
## M14 parity END-03: a won file's CORP DOWN poster slaps on (then the Cell's pencil X writes on,
## `pencil_write_on`, and CORP DOWN slaps on, `sticker_slap`).
const POSTER := &"dossier_poster"
const MOTIONS: Array[StringName] = [OPEN, STAMP, NOTE, NOTE_STAGGER, POSTER]

## The desk's margin round the folder, the folder's inner pad, the gap between the pages, the
## file tab's size and its inset from the right (px at 1.0).
const DESK_MARGIN := 18.0
const FOLDER_PAD := 12.0
const PAGE_GAP := 30.0
const TAB := Vector2(190, 22)
const TAB_INSET := 40.0
## The spine's crease (px) and how far the stickers overlap the folder's foot (px at 1.0).
const SPINE := 3.0
## The folder's manila stock (M14 asset parity, round 21 `manila`) and the cover's shade of it.
const MANILA_ART := "res://assets/campaign_end/manila.jpg"
const COVER_DARK := 0.06
const BUTTON_OVERLAP := 34.0
## A page's share of the post-it width it leaves free on its right for the notes.
const NOTE_ROOM := 0.62
## The CASE CLOSED stamp's spot on the report (share from its top-left) and tilt.
const STAMP_AT := Vector2(0.58, 0.22)
const STAMP_TILT := -12.0
## The letterhead seal's side (px at 1.0) and the rule under the letterhead (px).
const LETTERHEAD_SEAL := 58.0
const LETTERHEAD_RULE := 3.0
## The personnel rows' portrait prints (px at 1.0).
const BUST_PRINT := Vector2(28, 32)
## The typed fields' size at text scale 1.0 (bible §2.9: 20 px fields at 1080p, ÷1.5).
const FIELD_PX := 13
## Leader dots after a field name up to this many characters (the typed column).
const FIELD_WIDTH := 14
## M14 parity END-06: the report's head lines the stamp keeps clear of (SUBJECT, OPERATIONS,
## STATUS: their values; the concept inks over the bracketed tails only), and the gap it keeps
## from them (px at 1.0).
const STAMP_CLEAR_LINES := 3
const STAMP_GAP := 10.0
## M14 parity END-03: annex A's view on the story the Cell uncovered (every beat's title and
## words, scrolling inside the sheet past this height; px at 1.0), and the fewest typed lines it
## keeps when the page needs the room (side by side, the file fits the screen).
const STORY_VIEW := 150.0
const STORY_MIN_LINES := 2
## The CORP DOWN poster's tilt on the folder (degrees).
const POSTER_TILT := -2.0
## Frames the overlays are placed for after a layout change (the containers sort a frame late).
const PLACE_FRAMES := 3

var facts: DossierFacts = null
var style: CorpHouseStyle = null
## The prints: [{"caption": translated, "texture": Texture2D or null, "subject": {} or a
## PortraitArt subject}].
var photos: Array[Dictionary] = []
var elapsed: float = 0.0

var folder: MarginContainer = null
var spread: BoxContainer = null
var left_page: VBoxContainer = null
var right_page: VBoxContainer = null
var report: PaperSheet = null
var personnel: PaperSheet = null
var annex: PaperSheet = null
var case_stamp: RubberStamp = null
var cover: Control = null
var notes: Array[PostIt] = []
var main_menu_button: VinylButton = null
var new_campaign_button: VinylButton = null
## The folder's manila and the prints' stock, loaded once and held while the file is open
## (ART-12 12p: a `load()` nothing holds decodes the file again at every draw; the cover redraws
## every frame while it swings, ~45 ms frames at 1080p).
var _manila_tex: Texture2D = null
var _stock_tex: Texture2D = null
## A won file's CORP DOWN poster (END-03; null when lost or abandoned) and whether its sticker
## has slapped on.
var poster: CorpDownPoster = null
var _poster_slapped: bool = false
## Annex A's story view (null without a story), its MORE BELOW tag, and the typed fields of
## the report.
var story_view: ScrollContainer = null
var story_hint: ScrollHint = null
var fields: Label = null
## 12p (perf): built ahead and held still (the HQ builds it in the ransom lock's reading hold);
## its motion starts on `release`.
var held: bool = false
var _place_left: int = PLACE_FRAMES


func _init(p_facts: DossierFacts, p_photos: Array[Dictionary] = []) -> void:
	name = "AuditDossier"
	facts = p_facts
	style = CorpHouseStyle.of(p_facts.corporation_id)
	photos = p_photos
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	MotionSkip.register(self)
	_build()


# --- Words -----------------------------------------------------------------------------------

## The house's name as the file prints it (translated).
func house() -> String:
	return style.name_shown(facts.corporation_name)


## The audit's number on the file (the Cell's number, at least 1).
func audit_number() -> int:
	return maxi(1, facts.cell_number)


## The verdict the stamp says (translated): CASE CLOSED for a lost campaign, AT LARGE for a won one.
func stamp_word() -> String:
	return tr("AT LARGE") if facts.won else tr("CASE CLOSED")


## A typed field with its leader dots ("SUBJECT ....... value").
static func field(name_text: String, value: String) -> String:
	var dots := maxi(2, FIELD_WIDTH - name_text.length())
	return "%s %s %s" % [name_text, ".".repeat(dots), value]


## The report's typed lines (translated), top to bottom; "" is a blank line.
func report_lines() -> PackedStringArray:
	var f := facts
	var out := PackedStringArray()
	out.append(field(tr("SUBJECT"), tr("REBEL_CELL  (cell %02d)") % audit_number()))
	out.append(field(tr("OPERATIONS"), tr("%d netruns") % f.runs_started))
	if f.won:
		out.append(field(tr("STATUS"), tr("AT LARGE  (%s offline)") % f.boss_name))
	elif f.abandoned:
		out.append(field(tr("STATUS"), tr("STOOD DOWN  (operations abandoned)")))
	else:
		out.append(field(tr("STATUS"), tr("%s  (home server BREACHED)") % tr(style.verb)))
	out.append("")
	out.append(tr("ACTIVITY"))
	out.append("  " + field(tr("netruns"), tr("%d   (%d operatives lost)") % [f.runs_started, f.deaths]))
	out.append("  " + field(tr("raids"), tr("%d   (%d repelled, %d lost)") % [f.raids_won + f.raids_lost, f.raids_won, f.raids_lost]))
	out.append("  " + field(tr("exploits"), tr("%d / %d extracted") % [f.exploits_held, f.exploits_total]))
	out.append("  " + field(tr("schematics"), tr("%d held") % f.schematics))
	out.append("")
	out.append(tr("NETWORK AT CLOSURE"))
	out.append("  " + tr("held %d   down %d   taken %d") % [f.held, f.down, f.taken])
	out.append("  " + tr("home server  %d / %d") % [f.home_now, f.home_max])
	out.append("")
	out.append(tr("HEAT (subject's exposure), at closure %d:") % f.heat)
	return out


## The auditor's notes (translated), in the order they land.
func note_words() -> PackedStringArray:
	var f := facts
	var out := PackedStringArray()
	var who := String(f.most_troublesome.get("name", ""))
	out.append(tr("MOST TROUBLESOME -> %s") % who.to_upper() if who != "" else tr("no names. who ran this cell?"))
	var free := f.at_large()
	out.append(tr("%d still at large.") % free if free > 0 else tr("none left at large."))
	if f.won:
		out.append(tr("%s is offline. who signed off on this?") % f.boss_name)
	elif f.abandoned:
		out.append(tr("they walked away at heat %d. nobody walks away.") % f.heat)
	else:
		out.append(tr("heat reached %d. why weren't we told?") % f.heat)
	out.append(tr("they'll be back. flag ICE %d.") % f.next_ice)
	return out


# --- Building --------------------------------------------------------------------------------

func _build() -> void:
	var s := Settings.text_scale
	var column := VBoxContainer.new()
	column.name = "Desk"
	column.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	column.offset_left = DESK_MARGIN * 2.0 * s
	column.offset_right = -DESK_MARGIN * 2.0 * s
	column.add_theme_constant_override(&"separation", roundi(-BUTTON_OVERLAP * s))
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(column)
	folder = MarginContainer.new()
	folder.name = "Folder"
	folder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for side in ["left", "right", "bottom"]:
		folder.add_theme_constant_override("margin_" + side, roundi(FOLDER_PAD * s))
	folder.add_theme_constant_override(&"margin_top", roundi((FOLDER_PAD + TAB.y) * s))
	folder.draw.connect(_draw_folder)
	column.add_child(folder)
	spread = BoxContainer.new()
	spread.name = "Spread"
	spread.add_theme_constant_override(&"separation", roundi(PAGE_GAP * s))
	folder.add_child(spread)
	left_page = VBoxContainer.new()
	left_page.name = "LeftPage"
	left_page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left_page.add_theme_constant_override(&"separation", roundi(UiTheme.SP_S * s))
	spread.add_child(left_page)
	right_page = VBoxContainer.new()
	right_page.name = "RightPage"
	right_page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_page.add_theme_constant_override(&"separation", roundi(UiTheme.SP_M * s))
	spread.add_child(right_page)
	_build_photos()
	_build_personnel()
	_build_annex()
	_build_report()
	# END-06: room under the report for the stickers: they overlap the folder's manila foot (the
	# concept), never the report's last lines (the auditor's signature).
	var foot := Control.new()
	foot.name = "StickerRoom"
	foot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# The folder's own pad and the page's gap are manila too.
	foot.custom_minimum_size.y = maxf(0.0, BUTTON_OVERLAP - FOLDER_PAD - UiTheme.SP_M) * s
	right_page.add_child(foot)
	# The Cell's own stickers on the desk: MAIN MENU (yellow, the safe choice, first focus)
	# and NEW CAMPAIGN (pink, the verb).
	var buttons := HBoxContainer.new()
	buttons.name = "EndButtons"
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.add_theme_constant_override(&"separation", roundi(UiTheme.SP_L * s))
	column.add_child(buttons)
	main_menu_button = VinylButton.new(TextDb.mark("Main menu"), VinylSticker.Fill.YELLOW, UiTheme.LABEL)
	main_menu_button.name = "MainMenu"
	main_menu_button.tooltip_text = UiTip.fold(tr("Back to the title screen."))
	main_menu_button.pressed.connect(func() -> void: main_menu_pressed.emit())
	buttons.add_child(main_menu_button)
	new_campaign_button = VinylButton.new(TextDb.mark("New campaign"), VinylSticker.Fill.PINK, UiTheme.TITLE)
	new_campaign_button.name = "NewCampaign"
	new_campaign_button.tooltip_text = UiTip.fold(tr("Start a new campaign."))
	new_campaign_button.pressed.connect(func() -> void: new_campaign_pressed.emit())
	buttons.add_child(new_campaign_button)
	var right_room := Control.new()
	right_room.custom_minimum_size.x = DESK_MARGIN * 2.0 * s
	right_room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	buttons.add_child(right_room)
	# Over the pages: the stamp, the notes and the cover.
	case_stamp = RubberStamp.new(stamp_word(), Palette.END_STAMP_RED, UiTheme.DISPLAY, STAMP_TILT)
	case_stamp.name = "CaseStamp"
	add_child(case_stamp)
	var papers := [Palette.END_NOTE_PINK, Palette.END_NOTE_YELLOW, Palette.END_NOTE_BLUE, Palette.END_NOTE_GREEN]
	var tilts := [7.0, -6.0, 6.0, -5.0]
	var words := note_words()
	for i in words.size():
		var n := PostIt.new(words[i], papers[i % papers.size()], tilts[i % tilts.size()])
		n.name = "Note%d" % i
		add_child(n)
		notes.append(n)
	cover = Control.new()
	cover.name = "Cover"
	cover.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cover.draw.connect(_draw_cover)
	add_child(cover)
	resized.connect(_relayout)


func _typed(t: String, step: int = UiTheme.BODY, bold: bool = false, col: Color = Palette.END_TYPE_INK) -> Label:
	var l := Label.new()
	l.text = t
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # translated where built
	l.add_theme_font_override(&"font", EndFaces.typed_bold() if bold else EndFaces.typed())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(step))
	l.add_theme_color_override(&"font_color", PaperInk.text(col))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _build_photos() -> void:
	var s := Settings.text_scale
	var row := HBoxContainer.new()
	row.name = "Prints"
	row.add_theme_constant_override(&"separation", roundi(UiTheme.SP_S * s))
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	left_page.add_child(row)
	var tilts := [-5.0, 3.5, -2.5]
	var first := 0
	if facts.won:
		# END-03: a won file leads with the Cell's CORP DOWN poster over the corporation's own
		# notice; it takes the boss's print's place (the first print of a won campaign).
		poster = CorpDownPoster.new(facts.corporation_id, facts.corporation_name, facts.boss_name)
		row.add_child(TiltBox.new(POSTER_TILT, poster))
		first = 1
	for i in range(first, photos.size()):
		var p: Dictionary = photos[i]
		var ph := DossierPhoto.new(String(p.get("caption", "")))
		ph.name = "Print%d" % i
		ph.picture = p.get("texture", null)
		ph.subject = p.get("subject", {})
		ph.tint = style.color()
		row.add_child(TiltBox.new(tilts[i % tilts.size()], ph))


func _build_personnel() -> void:
	var s := Settings.text_scale
	personnel = PaperSheet.new(Palette.END_REPORT, PaperLie.tilt_deg(SHEET_SEED), UiTheme.SP_M)  # B5 (D24): a seeded 1-2 degree tilt
	personnel.name = "Personnel"
	personnel.add_theme_constant_override(&"margin_right", roundi(PostIt.SIDE.x * NOTE_ROOM * s))
	left_page.add_child(TiltBox.new(personnel.tilt, personnel))
	var col := VBoxContainer.new()
	col.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * s))
	personnel.add_child(col)
	col.add_child(_typed(tr("PERSONNEL  //  IDENTIFIED OPERATIVES"), UiTheme.BODY, true))
	col.add_child(_rule(Palette.END_TYPE_INK))
	for r in facts.crew:
		var row := HBoxContainer.new()
		row.name = "Operative_%s" % String(r["name"]).validate_node_name()
		row.add_theme_constant_override(&"separation", roundi(UiTheme.SP_S * s))
		col.add_child(row)
		# 4B's v2 portrait print of the operative's own face; KIA (dimmed, crossed out in red
		# pencil, as 4B's Polaroid.kia) when DECEASED.
		var bust := Control.new()
		bust.name = "Print"
		bust.custom_minimum_size = BUST_PRINT * s
		bust.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var subj := PortraitArt.operative_subject(r["class_id"], StringName(String(r.get("id", ""))), String(r["name"]))
		bust.draw.connect(_draw_print.bind(bust, subj, not bool(r["alive"])))
		row.add_child(bust)
		var names := VBoxContainer.new()
		names.add_theme_constant_override(&"separation", 0)
		names.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(names)
		var alive: bool = r["alive"]
		var head := _typed("%s  R%d" % [String(r["name"]).to_upper(), int(r["rank"])], FIELD_PX, true)
		head.name = "Name"
		if not alive:
			head.draw.connect(_strike.bind(head))
		names.add_child(head)
		names.add_child(_typed(tr("%s, %d runs") % [String(r["class_name"]), int(r["runs"])], UiTheme.CAPTION, false, Palette.END_TYPE_SOFT))
		var fate := ""
		if not alive:
			fate = tr("DECEASED")
		elif String(r["post"]) != "":
			fate = tr("AT LARGE (stationed: %s)") % String(r["post"])
		else:
			fate = tr("AT LARGE (reserve)")
		var fate_label := _typed(fate, FIELD_PX, false, Palette.END_STAMP_RED if not alive else Palette.END_TYPE_INK)
		fate_label.name = "Fate"
		fate_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		UiWrap.whole_words(fate_label)  # whole words, never mid-word (ART-0 F)
		row.add_child(fate_label)


## A personnel print: the portrait on its white border; KIA greyed and crossed out (4B's
## Polaroid.kia look and values).
func _draw_print(c: Control, subj: Dictionary, kia: bool) -> void:
	var r := Rect2(Vector2.ZERO, c.size)
	if _stock_tex == null:
		_stock_tex = load(DossierPhoto.STOCK_ART) as Texture2D
	c.draw_texture_rect(_stock_tex, r, false)
	var m := maxf(1.0, c.size.x * DossierPhoto.FRAME_SHARE)
	var img := r.grow(-m)
	PortraitArt.draw(c, img, subj)
	if kia:
		c.draw_rect(img, Color(Palette.INK, Polaroid.KIA_GREY))
	# B1b: the red pencil X is the kit's wax (one material, written on).
	PencilSet.show_on(c, PencilSet.cross_strokes(img, img.size.x * Polaroid.KIA_INSET) if kia else [] as Array[PackedVector2Array],
		GreasePencilMark.Ink.THREAT, Polaroid.KIA_SEED)
	c.draw_rect(r, PaperInk.edge(Color(Palette.INK, Polaroid.EDGE_ALPHA)), false, PaperInk.edge_width(1.0))


## A typed name struck through (a DECEASED operative).
func _strike(l: Label) -> void:
	var f := l.get_theme_font(&"font")
	var fs := l.get_theme_font_size(&"font_size")
	var w := minf(l.size.x, f.get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	var y := l.size.y * 0.5
	l.draw_line(Vector2(0, y), Vector2(w, y), PaperInk.text(Palette.END_TYPE_INK), maxf(1.5, Settings.text_scale * 1.5))


func _rule(col: Color, h: float = 2.0) -> ColorRect:
	var r := ColorRect.new()
	r.color = PaperInk.text(col)
	r.custom_minimum_size = Vector2(0, h)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


func _build_annex() -> void:
	var s := Settings.text_scale
	annex = PaperSheet.new(Palette.END_ANNEX, PaperLie.tilt_deg(SHEET_SEED + 1), UiTheme.SP_S)  # END-03: a tighter pad (the story's room at 720p)
	annex.name = "Annex"
	# The post-its' room on its right too (the second note reaches down over it).
	annex.add_theme_constant_override(&"margin_right", roundi(PostIt.SIDE.x * NOTE_ROOM * s))
	left_page.add_child(TiltBox.new(annex.tilt, annex))
	var col := VBoxContainer.new()
	col.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * s))
	annex.add_child(col)
	# Annex B: the profile's records and the next campaign's ICE cap.
	var risk := VBoxContainer.new()
	risk.name = "ProfileFacts"
	risk.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * s))
	risk.add_child(_typed(tr("ANNEX B  //  RESIDUAL RISK"), UiTheme.BODY, true))
	var best := tr("none") if facts.best_ice < 0 else "%d" % facts.best_ice
	var lines := [tr("subject's record: %d campaigns won, %d lost, best ICE %s.") % [facts.campaigns_won, facts.campaigns_lost, best],
		tr("the next %s campaign may start up to ICE %d.") % [facts.corporation_name, facts.next_ice]]
	for line: String in lines:
		var l := _typed(line, FIELD_PX)
		UiWrap.whole_words(l)  # whole words, never mid-word (ART-0 F)
		risk.add_child(l)
	if facts.beats.is_empty():
		col.add_child(risk)
		return
	var story := VBoxContainer.new()
	story.name = "EndStory"
	story.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * s))
	col.add_child(story)
	story.add_child(_typed(tr("ANNEX A  //  RECOVERED INTERCEPTS"), UiTheme.BODY, true))
	# END-03 (the build's STORY UNCOVERED paper, ported from art-m13-final
	# `campaign_end_stage.gd` `_story`, 5c077bc1): every intercept's title and its words, typed,
	# then annex B; past the sheet's room they scroll inside it (MORE BELOW).
	var text := VBoxContainer.new()
	text.name = "AnnexText"
	text.add_theme_constant_override(&"separation", roundi(UiTheme.SP_S * s))
	var beats := VBoxContainer.new()
	beats.name = "Intercepts"
	beats.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * s))
	text.add_child(beats)
	for i in facts.beats.size():
		var b: Dictionary = facts.beats[i]
		var title := _typed(String(b["title"]).to_upper(), FIELD_PX, true)
		title.name = "BeatTitle%d" % i
		UiWrap.whole_words(title)  # whole words, never mid-word (ART-0 F)
		beats.add_child(title)
		var words := _typed(String(b["text"]), FIELD_PX)
		words.name = "BeatText%d" % i
		UiWrap.whole_words(words)  # whole words, never mid-word (ART-0 F)
		beats.add_child(words)
	text.add_child(risk)
	# The kit's scroll view and MORE BELOW tag (as FitScroll lays them, but its view may be
	# shorter than FitScroll's least: the page fits the screen at 1.0, `_fit_story`).
	story_view = ScrollContainer.new()
	story_view.name = "StoryView"
	story_view.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	story_view.follow_focus = true
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	story_view.add_child(text)
	story.add_child(story_view)
	story_hint = ScrollHint.new(story_view)
	story_hint.snap_rows = true
	# The tag's room under the view, made here (the tag would add it while the sheet is still
	# setting up its children), as FitScroll does.
	var room := Control.new()
	room.name = "ScrollHintRoom"
	room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	story.add_child(room)
	story_hint.room = room
	story_hint.top_level = true
	story.add_child(story_hint)
	story_view.custom_minimum_size.y = STORY_VIEW * s


func _build_report() -> void:
	var s := Settings.text_scale
	report = PaperSheet.new(Palette.END_REPORT, PaperLie.tilt_deg(SHEET_SEED + 2), UiTheme.SP_M)
	report.name = "AuditReport"
	report.add_theme_constant_override(&"margin_right", roundi(PostIt.SIDE.x * NOTE_ROOM * s))
	right_page.add_child(TiltBox.new(report.tilt, report))
	var col := VBoxContainer.new()
	col.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * s))
	report.add_child(col)
	# The letterhead: the seal, the house, its division and the audit's number, a rule.
	var head := HBoxContainer.new()
	head.name = "Letterhead"
	head.add_theme_constant_override(&"separation", roundi(UiTheme.SP_M * s))
	col.add_child(head)
	var seal := Control.new()
	seal.custom_minimum_size = Vector2(LETTERHEAD_SEAL, LETTERHEAD_SEAL) * s
	var ink := letterhead_ink()
	seal.draw.connect(func() -> void: CorpSeal.draw_seal(seal, seal.size * 0.5, seal.size.x * 0.5, style.corp_id, ink, house()))
	head.add_child(seal)
	var names := VBoxContainer.new()
	names.alignment = BoxContainer.ALIGNMENT_CENTER
	names.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	names.add_theme_constant_override(&"separation", 0)
	head.add_child(names)
	var corp_line := Label.new()
	corp_line.text = house().to_upper()
	corp_line.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	corp_line.add_theme_font_override(&"font", Palette.body_medium())
	corp_line.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.TITLE))
	corp_line.add_theme_color_override(&"font_color", PaperInk.text(ink))
	names.add_child(corp_line)
	var div := Label.new()
	div.text = tr("%s  //  AUDIT %d") % [tr(style.division), audit_number()]
	div.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	div.add_theme_font_override(&"font", Palette.body())
	div.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY))
	div.add_theme_color_override(&"font_color", PaperInk.text(Palette.END_TYPE_SOFT))
	names.add_child(div)
	col.add_child(_rule(ink, LETTERHEAD_RULE))
	var title := _typed(tr("AUDIT REPORT"), UiTheme.TITLE, true)
	title.name = "Title"
	col.add_child(title)
	var lines := _typed("\n".join(report_lines()), FIELD_PX)
	lines.name = "Fields"
	col.add_child(lines)
	fields = lines
	var trace := HeatTrace.new()
	trace.name = "HeatTrace"
	trace.marks = facts.heat_marks
	trace.heat = facts.heat
	trace.heat_max = facts.heat_max
	trace.levels = facts.heat_levels
	col.add_child(trace)
	var filed := HBoxContainer.new()
	filed.add_theme_constant_override(&"separation", roundi(UiTheme.SP_M * s))
	col.add_child(filed)
	var by := _typed(tr("filed by: %s, AUDIT %d") % [style.auditor, audit_number()], UiTheme.CAPTION, false, Palette.END_TYPE_SOFT)
	by.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	by.size_flags_vertical = Control.SIZE_SHRINK_END
	filed.add_child(by)
	var sign := Label.new()
	sign.text = style.auditor.capitalize()
	sign.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	sign.add_theme_font_override(&"font", EndFaces.ballpoint())
	sign.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.TITLE))
	sign.add_theme_color_override(&"font_color", PaperInk.text(Palette.END_BALLPOINT))
	filed.add_child(sign)


## The letterhead's ink: the house hue, darkened to read on paper.
func letterhead_ink() -> Color:
	return style.color().darkened(0.45)


# --- Layout and motion -----------------------------------------------------------------------

func _ready() -> void:
	_relayout.call_deferred()


func _relayout() -> void:
	if spread == null:
		return
	# Side by side when both pages fit the folder; one over the other when not (large text).
	var s := Settings.text_scale
	spread.vertical = false
	var room := size.x - (FOLDER_PAD * 2.0 + PAGE_GAP + DESK_MARGIN * 4.0) * s
	var want := left_page.get_combined_minimum_size().x + right_page.get_combined_minimum_size().x
	spread.vertical = want > room
	custom_minimum_size.y = get_child(0).get_combined_minimum_size().y
	_fit_story.call_deferred()
	_place_left = PLACE_FRAMES
	_place_overlays()


func _process(delta: float) -> void:
	if held:
		return
	var end := motion_end()
	var moving := elapsed < end
	if moving:
		elapsed = minf(elapsed + delta, end)
		_place_left = PLACE_FRAMES
	# 12p: the overlays are placed while the file moves and for a few frames after a layout
	# change (the containers sort a frame late), never every frame at rest.
	if _place_left > 0:
		if not moving:
			_place_left -= 1
		_place_overlays()


## 12p: holds a file built ahead, unseen and still, until `release`. Its MORE BELOW tag is top
## level (it keeps no parent's modulate): it is hidden by its own.
func hold() -> void:
	held = true
	modulate.a = 0.0
	if story_hint != null:
		story_hint.self_modulate.a = 0.0
		story_hint.modulate.a = 0.0


## 12p: shows a file built ahead (`held`): its motion starts now.
func release() -> void:
	held = false
	modulate.a = 1.0
	if story_hint != null:
		story_hint.self_modulate.a = 1.0
		story_hint.modulate.a = 1.0
	elapsed = 0.0
	_place_left = PLACE_FRAMES
	_place_overlays()


## Where motion `id` stands now, 0..1 (1 at once when it does not play).
func phase(id: StringName, extra_delay: float = 0.0) -> float:
	if not Motion.live(id):
		return 1.0
	var d := Motion.seconds(id)
	var t := elapsed - Motion.delay_of(id) - extra_delay
	if d <= 0.0:
		return 1.0 if t >= 0.0 else 0.0
	return clampf(t / d, 0.0, 1.0)


## END-03: when the poster's pencil X starts writing on (s into the file's motion): once the
## poster has landed.
func poster_write_at() -> float:
	return Motion.delay_of(POSTER) + Motion.seconds(POSTER) if Motion.live(POSTER) else 0.0


## END-03: how long the pencil X takes to write on (s): `pencil_write_on`'s duration
## (GreasePencilMark.write_on's rule, B1b); 0 when it does not play.
func poster_write_seconds() -> float:
	if poster == null or not Motion.live(GreasePencilMark.WRITE):
		return 0.0
	return Motion.seconds(GreasePencilMark.WRITE)


## END-03: when CORP DOWN slaps on (s): as the pencil X is written.
func poster_slap_at() -> float:
	return poster_write_at() + poster_write_seconds()


func motion_end() -> float:
	var end := 0.0
	for id: StringName in [OPEN, STAMP, NOTE]:
		if Motion.live(id):
			var extra := Motion.seconds(NOTE_STAGGER) * maxf(0.0, notes.size() - 1.0) if id == NOTE else 0.0
			end = maxf(end, Motion.delay_of(id) + Motion.seconds(id) + extra)
	if poster != null:
		var slap := Motion.seconds(VinylSticker.SLAP) if Motion.live(VinylSticker.SLAP) else 0.0
		end = maxf(end, poster_slap_at() + slap)
	return end


## MotionSkip: the file still opens, stamps or takes its notes (a won file: its poster).
func motion_running() -> bool:
	return is_inside_tree() and not held and elapsed < motion_end()


## MotionSkip: the open file at once.
func complete_motion() -> void:
	elapsed = maxf(elapsed, motion_end())
	_place_overlays()
	if poster != null:
		_poster_slapped = true
		poster.sticker_at_rest()


func _input(event: InputEvent) -> void:
	if motion_running():
		MotionSkip.handle(event, self)


func _rect_in_self(c: Control) -> Rect2:
	var inv := get_global_transform().affine_inverse()
	var r := c.get_global_rect()
	return Rect2(inv * r.position, r.size)


## END-06: where the verdict stamp lands on the report (its top-left, in this view's space):
## beside the values of the report's head lines (SUBJECT, OPERATIONS, STATUS), over their
## bracketed tails as the concept inks it, never over a value; centred on those lines.
func stamp_spot() -> Vector2:
	var rep := _rect_in_self(report)
	if fields == null or not fields.is_inside_tree():
		return rep.position + rep.size * STAMP_AT - case_stamp.size * 0.5
	var f := fields.get_theme_font(&"font")
	var fs := fields.get_theme_font_size(&"font_size")
	var head := report_lines().slice(0, STAMP_CLEAR_LINES)
	var reach := 0.0
	for line in head:
		reach = maxf(reach, f.get_string_size(value_core(line), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	var at := _rect_in_self(fields)
	var line_h := f.get_height(fs) + fields.get_theme_constant(&"line_spacing")
	var mid_y := at.position.y + line_h * head.size() * 0.5
	var x := at.position.x + reach + STAMP_GAP * Settings.text_scale
	return Vector2(x, mid_y - case_stamp.size.y * 0.5)


## A typed field's line up to its value (the bracketed tail, "  (...)", cut off).
static func value_core(line: String) -> String:
	var cut := line.find("  (")
	return line.substr(0, cut) if cut >= 0 else line


func _place_overlays() -> void:
	if report == null or not report.is_inside_tree():
		return
	var s := Settings.text_scale
	var rep := _rect_in_self(report)
	var per := _rect_in_self(personnel)
	# The stamp beside the report's head values; the notes over the right edges of the two sheets.
	var sp := phase(STAMP)
	case_stamp.visible = sp > 0.0
	case_stamp.position = stamp_spot()
	var amp := Motion.amplitude(STAMP)
	case_stamp.scale = Vector2.ONE * (lerpf(amp, 1.0, ease(sp, 0.4)) if amp > 0.0 else 1.0)
	var spots := [Vector2(per.end.x - notes[0].size.x * 0.75, per.position.y + UiTheme.SP_L * s),
		Vector2(per.end.x - notes[1].size.x * 0.68, per.position.y + notes[0].size.y + UiTheme.SP_S * s),
		Vector2(rep.end.x - notes[2].size.x * 0.7, rep.position.y - UiTheme.SP_S * s),
		Vector2(rep.end.x - notes[3].size.x * 0.5, rep.end.y - notes[3].size.y * 1.05)]
	var stagger := Motion.seconds(NOTE_STAGGER) if Motion.live(NOTE_STAGGER) else 0.0
	var namp := Motion.amplitude(NOTE)
	var spine_x := (rep.position.x + per.end.x) * 0.5 if not spread.vertical else size.x * 0.5
	for i in notes.size():
		var n := notes[i]
		var at: Vector2 = spots[i % spots.size()]
		# END-06: the personnel sheet's notes stay on the left page (the concept): a note over
		# the report's left edge cut its typed lines (HEAT ... at closure). Tilted: the turned
		# corner's reach is kept too.
		if i < 2 and not spread.vertical:
			at.x = minf(at.x, spine_x - n.size.x - _tilt_reach(n))
		# On the desk, never past the screen's edge.
		n.position = Vector2(clampf(at.x, 0.0, maxf(0.0, size.x - n.size.x)), at.y)
		var p := phase(NOTE, stagger * i)
		n.visible = p > 0.0
		n.scale = Vector2.ONE * (lerpf(namp, 1.0, ease(p, 0.4)) if namp > 0.0 else 1.0)
	_apply_poster()
	# The cover swings open about the spine: over the right page first, then the left page
	# lands; at rest it is gone.
	var o := phase(OPEN)
	cover.visible = o < 1.0
	var fold := cos(PI * o)
	var folder_r := _rect_in_self(folder)
	if fold > 0.0:
		cover.position = Vector2(spine_x, folder_r.position.y + TAB.y * s)
		cover.size = Vector2(maxf(1.0, (folder_r.end.x - spine_x) * fold), folder_r.size.y - TAB.y * s)
	else:
		var w := (spine_x - folder_r.position.x) * -fold
		cover.position = Vector2(spine_x - w, folder_r.position.y + TAB.y * s)
		cover.size = Vector2(maxf(1.0, w), folder_r.size.y - TAB.y * s)
	left_page.modulate.a = 1.0 if fold <= 0.0 else 0.0
	if cover.visible:
		cover.queue_redraw()


## How far a tilted control's corners reach past its untilted rect sideways (px).
static func _tilt_reach(c: Control) -> float:
	var a := absf(deg_to_rad(c.rotation_degrees))
	return (c.size.x * (cos(a) - 1.0) + c.size.y * sin(a)) * 0.5


## END-03: annex A's view: as tall as the story up to STORY_VIEW, shorter (to STORY_MIN_LINES
## typed lines) when the file side by side would run past the page's foot. Stacked (large
## text) the page scrolls and the view keeps STORY_VIEW.
func _fit_story() -> void:
	if story_view == null or not story_view.is_inside_tree():
		return
	var s := Settings.text_scale
	var f := EndFaces.typed()
	var line_h := f.get_height(UiTheme.font_px(FIELD_PX)) + UiTheme.SP_XS * s
	var content_h := 0.0
	if story_view.get_child_count() > 0:
		content_h = (story_view.get_child(0) as Control).get_combined_minimum_size().y
	var cap := STORY_VIEW * s
	if not spread.vertical:
		var col_h := (get_child(0) as Control).get_combined_minimum_size().y
		var over := global_position.y + col_h - _page_bottom()
		cap = clampf(story_view.custom_minimum_size.y - over, line_h * STORY_MIN_LINES, STORY_VIEW * s)
	var view := floorf(minf(content_h, cap)) if content_h > 0.0 else cap
	if story_hint != null and story_hint.is_inside_tree():
		story_hint.set_view_min(view)
		story_hint.refresh()
	else:
		story_view.custom_minimum_size.y = view
	custom_minimum_size.y = (get_child(0) as Control).get_combined_minimum_size().y


## The foot of the page the file shows on (global px): its scroll view's, else the screen's.
func _page_bottom() -> float:
	var n := get_parent()
	while n != null:
		if n is ScrollContainer:
			return (n as ScrollContainer).get_global_rect().end.y
		n = n.get_parent()
	return get_viewport_rect().size.y


## END-03: the won file's beat: the poster slaps on (`dossier_poster`), the Cell's pencil X
## writes on, then CORP DOWN slaps on (`sticker_slap`). At rest when none of it plays.
func _apply_poster() -> void:
	if poster == null:
		return
	var w := 1.0
	var ws := poster_write_seconds()
	if ws > 0.0:
		w = clampf((elapsed - poster_write_at()) / ws, 0.0, 1.0)
	poster.apply(phase(POSTER), w, Motion.amplitude(POSTER))
	if held:
		poster.hold_sticker()
	elif not _poster_slapped and elapsed >= poster_slap_at():
		_poster_slapped = true
		poster.slap_sticker()
	elif not _poster_slapped:
		poster.hold_sticker()


func _draw() -> void:
	# The desk under the folder, warmer under the lamp: it runs to the screen's edges round the
	# page (the city never shows round the file).
	var vp := get_viewport_rect().size
	var origin := get_global_transform().affine_inverse() * Vector2.ZERO
	var r := Rect2(origin, vp).merge(Rect2(Vector2.ZERO, size))
	draw_rect(r, Palette.END_DESK)
	var lamp := Vector2(size.x * 0.32, size.y * 0.2)
	for i in 6:
		draw_circle(lamp, size.x * (0.65 - i * 0.09), Color(Palette.END_DESK_LAMP, 0.16))


func _draw_folder() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2(0, TAB.y * s), folder.size - Vector2(0, TAB.y * s))
	folder.draw_rect(Rect2(r.position + Vector2(6, 10) * s, r.size), Palette.SHADOW)
	# The file tab, its words typed on it.
	var tab := Rect2(Vector2(r.end.x - (TAB.x + TAB_INSET) * s, 0), Vector2(TAB.x * s, TAB.y * s + 2.0))
	_manila(folder, tab, Palette.NO_TINT)
	var f := EndFaces.typed_bold()
	var fs := UiTheme.font_px(UiTheme.BODY)
	var tab_text := tr("CELL-%02d / %s") % [audit_number(), tr("AT LARGE") if facts.won else tr("CLOSED")]
	folder.draw_string(f, Vector2(tab.position.x + UiTheme.SP_M * s, tab.position.y + (tab.size.y + f.get_ascent(fs)) * 0.5 - 2.0), tab_text, HORIZONTAL_ALIGNMENT_LEFT, tab.size.x - UiTheme.SP_M * s, fs, PaperInk.text(Palette.END_TYPE_SOFT))
	_manila(folder, r, Palette.NO_TINT)
	if not spread.vertical:
		var x := (_rect_in_self(left_page).end.x + _rect_in_self(right_page).position.x) * 0.5 - folder.position.x
		folder.draw_line(Vector2(x, r.position.y), Vector2(x, r.end.y), Palette.END_MANILA_EDGE, SPINE * s)
	folder.draw_rect(r, PaperInk.edge(Palette.END_MANILA_EDGE), false, PaperInk.edge_width(1.0))


## M14 asset parity: the folder's stock is round 21's own `manila` (one screen of it,
## `assets/campaign_end/manila.jpg`), laid 1:1 from its top-left (stretched only when a rect is
## bigger than the screen it was made for); `tint` darkens the cover.
func _manila(ci: Control, r: Rect2, tint: Color) -> void:
	if _manila_tex == null:
		_manila_tex = load(MANILA_ART) as Texture2D
	var t := _manila_tex
	var src := Rect2(Vector2.ZERO, Vector2(minf(r.size.x, t.get_width()), minf(r.size.y, t.get_height())))
	ci.draw_texture_rect_region(t, r, src, tint)


func _draw_cover() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, cover.size)
	_manila(cover, r, Palette.NO_TINT.darkened(COVER_DARK))
	cover.draw_rect(r, Palette.END_MANILA_EDGE, false, 2.0)
	if cover.size.x < r.size.y * 0.25:
		return
	# The cover's label and the house's verb stamped on it, squashed as it turns.
	var f := EndFaces.typed_bold()
	var fs := UiTheme.font_px(UiTheme.LABEL)
	var label := Rect2(r.size.x * 0.15, r.size.y * 0.18, r.size.x * 0.7, fs * 4.5)
	cover.draw_rect(label, PaperInk.opaque(Palette.PAPER))
	var y := label.position.y + fs * 1.3
	for t in [tr("%s  //  AUDIT %d") % [house().to_upper(), audit_number()], tr("SUBJECT: REBEL_CELL"), tr("CELL %02d  //  %d RUNS") % [audit_number(), facts.runs_started]]:
		cover.draw_string(f, Vector2(label.position.x + UiTheme.SP_S * s, y), t, HORIZONTAL_ALIGNMENT_LEFT, label.size.x - UiTheme.SP_M * s, fs, PaperInk.text(Palette.END_TYPE_INK))
		y += fs * 1.25
	CorpSeal.draw_seal(cover, Vector2(r.size.x * 0.5, r.size.y * 0.72), minf(r.size.x, r.size.y) * 0.14, style.corp_id, letterhead_ink(), house())
