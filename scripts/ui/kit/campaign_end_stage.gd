class_name CampaignEndStage
extends Control
## Art pass W8d (ART_BIBLE §11 Campaign end (WON / LOST), §8 T4, critique 62/63, §9 "what
## would embarrass the game"): the payoff of a whole campaign, staged over the city as two
## distinct templates that read at a glance and in greyscale.
##
## WON (`campaign_end_won`, T4): the target corporation's billboard (CorpFallArt): its
## landmark falls, its hue and pattern are crossed out in CELL_PINK spray; the city leans all
## the way to the corp's hue (W7 campaign progress 1.0, through `city_lean`); CORP DOWN slams
## across the billboard's foot at `hero` size (W8c VerdictStamp); the crew's Polaroids go up on
## the wall, triumphant (the dead flatlined).
## LOST (`campaign_end_lost`, T4): the Cell's own hexagon cracks and splits (CellCrackArt);
## the city grades to grey (W8c's desaturate-and-dim grade); CELL BURNED slams across it; the
## crew wall shows the living hurt and the dead flatlined.
## Both: the story the campaign uncovered on PAPER in Plex body (≤ 70 columns, scrolling inside
## when long), the profile and ICE records on a taped receipt as icon + number fields, then
## the actions (§6.4: New campaign Primary, Back to title Secondary).
##
## The sequence is skippable with any press, and a page settle ends it (`Typing.META`, as
## RunEndStage). Under reduce effects nothing moves: the end state shows at once and the
## page's own entrance (a cross-fade) brings it in. View only: the screen passes the words,
## the crew and the records; the city is the screen's (Signal Up, Call Down).

## Emitted while the WON sequence leans the city toward the corp: campaign progress 0..1.
signal city_lean(progress: float)

const MOTION_WON := &"campaign_end_won"
const MOTION_LOST := &"campaign_end_lost"
## Where each beat starts and how much of the sequence it takes (shares of the motion).
const AT_ART := 0.08
const ART_SHARE := 0.3
const AT_SPRAY := 0.36
const SPRAY_SHARE := 0.28
const AT_SPLIT := 0.36
const SPLIT_SHARE := 0.12
const AT_GRADE := 0.12
const GRADE_SHARE := 0.4
const AT_STAMP := 0.62
const STAMP_SHARE := 0.1
const AT_WALL := 0.7
const WALL_STAGGER := 0.03
const WALL_SHARE := 0.1
const AT_FOOT := 0.78
const FOOT_SHARE := 0.2
## A photo's start scale as it goes up on the wall.
const WALL_POP := 1.12
## The widest the stamp may be (px; 140% slack is kept inside it).
const STAMP_MAX_WIDTH := 900.0
## The story's columns (§4.2: ≤ 70 characters a line), its least scrolling height (px at
## 1.0) and, when the page stacks (large text), the share of the page it may take.
const STORY_COLUMNS := 70
const STORY_MIN_H := 120.0
const STORY_STACKED_SHARE := 0.55
## The gaps (§5.1).
const GAP := UiTheme.SP_M
const ROW_GAP := UiTheme.SP_L

var won: bool = true
var corp_id: StringName = &""
var grade: ColorRect
var scrim: GlassScrim
var column: VBoxContainer
var hero_row: BoxContainer
var foot_row: BoxContainer
var hero: StampOverlap
## The WON billboard or the LOST hexagon.
var art: Control
var stamp: VerdictStamp
var wall: CrewWall
var story: ZinePanel
var story_labels: Array[Label] = []
## The story's line width in use (px; its longest folded line).
var story_w: float = 0.0
var receipt: RunReceipt
var actions: VBoxContainer
var new_button: Button
var title_button: Button
## The city's campaign progress when the sequence starts (the lean runs from it to 1.0).
var lean_from: float = 0.0
var _tween: Tween = null
var _u: float = 1.0
var _laying_out: bool = false


## `p_won` picks the template; `corp_id` / `corp_name` the target; `headline` (translated) heads
## the story; `crew` = CrewWall.crew_of(roster); `beats` = [[title, text], ...] translated;
## `records` = records_of(...).
func _init(p_won: bool = true, p_corp_id: StringName = &"", corp_name: String = "", headline: String = "",
		crew: Array = [], beats: Array = [], records: Dictionary = {}) -> void:
	name = "CampaignEndStage"
	won = p_won
	corp_id = p_corp_id
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	grade = ColorRect.new()
	grade.name = "GreyGrade"
	grade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = RunEndStage.GRADE_CODE
	var mat := ShaderMaterial.new()
	mat.shader = sh
	mat.set_shader_parameter(&"dim", RunEndStage.GREY_DIM)
	grade.material = mat
	grade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(grade)
	# §2 CITY: the city sits behind a blur-and-dim scrim wherever the page's pieces sit over
	# it (the stamp's ink would meet a lit sign otherwise). The copy lets the scrim read the
	# graded (grey) city rather than the first copy of the screen.
	var copy := BackBufferCopy.new()
	copy.name = "GradeCopy"
	copy.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	add_child(copy)
	scrim = GlassScrim.new()
	scrim.name = "EndScrim"
	scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scrim)
	var center := CenterContainer.new()
	center.name = "EndCenter"
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	column = VBoxContainer.new()
	column.name = "EndColumn"
	column.alignment = BoxContainer.ALIGNMENT_CENTER
	column.add_theme_constant_override("separation", roundi(ROW_GAP * Settings.text_scale))
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.minimum_size_changed.connect(update_minimum_size)
	center.add_child(column)
	# The hero: the art with the verdict stamped across its foot, then the crew wall.
	hero_row = _row("HeroRow")
	column.add_child(hero_row)
	hero = StampOverlap.new()
	hero.name = "Hero"
	hero.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hero_row.add_child(hero)
	if won:
		art = CorpFallArt.new(corp_id)
	else:
		art = CellCrackArt.new()
	hero.add_child(art)
	stamp = VerdictStamp.new(tr(verdict_of(won)), color_of(won), STAMP_MAX_WIDTH)
	stamp.name = "VerdictStamp"
	hero.add_child(stamp)
	wall = CrewWall.new(crew, won)
	wall.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hero_row.add_child(wall)
	# The foot: the story on paper, the records on a receipt, the actions.
	foot_row = _row("FootRow")
	column.add_child(foot_row)
	story = _story(headline, beats)
	foot_row.add_child(story)
	receipt = _receipt(corp_name, records)
	foot_row.add_child(receipt)
	actions = VBoxContainer.new()
	actions.name = "EndActions"
	actions.add_theme_constant_override("separation", roundi(GAP * Settings.text_scale))
	actions.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	foot_row.add_child(actions)
	new_button = Button.new()
	new_button.name = "NewCampaign"
	new_button.theme_type_variation = UiTheme.PRIMARY
	new_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	actions.add_child(new_button)
	title_button = Button.new()
	title_button.name = "BackToTitle"
	title_button.theme_type_variation = UiTheme.SECONDARY
	title_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	actions.add_child(title_button)
	# Each piece keeps its own width in either direction (stacked, a receipt never
	# stretches into a full-width bar).
	for piece: Control in [hero, wall, story, receipt, actions]:
		piece.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	resized.connect(_relayout)
	column.sort_children.connect(_refresh_hint, CONNECT_DEFERRED)
	_set_grade(grade_to())


func _row(n: String) -> BoxContainer:
	var r := BoxContainer.new()
	r.name = n
	r.alignment = BoxContainer.ALIGNMENT_CENTER
	r.add_theme_constant_override("separation", roundi(ROW_GAP * Settings.text_scale))
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## The story's line width (px): STORY_COLUMNS of the body face at the body step.
static func story_width() -> float:
	return ceilf(Palette.body().get_string_size(UiTip.COLUMN_SAMPLE.repeat(STORY_COLUMNS), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.BODY)).x)


func _story(headline: String, beats: Array) -> ZinePanel:
	var panel := ZinePanel.new(tr("STORY UNCOVERED"), -1.0)
	panel.name = "EndStory"
	panel.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var box := VBoxContainer.new()
	box.name = "Beats"
	box.add_theme_constant_override("separation", roundi(UiTheme.SP_S * Settings.text_scale))
	panel.content.add_child(box)
	var head := _paper_label(headline, UiTheme.LABEL, Palette.display())
	head.name = "Headline"
	box.add_child(head)
	for b in beats:
		var t := _paper_label(String(b[0]).to_upper(), UiTheme.BODY, Palette.display())
		t.name = "BeatTitle"
		box.add_child(t)
		# §4.2: folded at word boundaries to ≤ STORY_COLUMNS characters a line (Plex runs
		# narrower than its "n" column, so a width alone would let ~85 through).
		var body := _paper_label(UiTip.fold_to(String(b[1]), STORY_COLUMNS), UiTheme.BODY, null)
		body.name = "BeatText"
		body.theme_type_variation = UiTheme.BODY_TEXT
		body.autowrap_mode = TextServer.AUTOWRAP_OFF
		box.add_child(body)
	# The paper is as wide as its longest folded line (never wider than the columns' width).
	var px := UiTheme.font_px(UiTheme.BODY)
	var w := 0.0
	for l in story_labels:
		if l.name == &"BeatText":
			w = maxf(w, ceilf(Palette.body().get_multiline_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x))
	story_w = minf(story_width(), w) if w > 0.0 else story_width()
	for l in story_labels:
		l.custom_minimum_size.x = story_w if l.autowrap_mode != TextServer.AUTOWRAP_OFF else 0.0
	return panel


func _paper_label(words: String, step: int, font: Font) -> Label:
	var l := Label.new()
	l.text = words
	if font != null:
		l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	l.add_theme_color_override("font_color", PaperInk.text(Palette.INK))
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = story_width()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	story_labels.append(l)
	return l


func _receipt(corp_name: String, r: Dictionary) -> RunReceipt:
	var slip := RunReceipt.new(RunReceipt.TILT_STEP)
	slip.name = "EndReceipt"
	slip.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	slip.line(corp_name.to_upper(), UiTheme.BODY, Palette.display())
	slip.line("-")
	slip.fields([[StatIcon.WON, r.get("won", 0)], [StatIcon.CLOSE, r.get("lost", 0)], [StatIcon.ICE, r.get("best", HudStats.NO_VALUE)]])
	slip.line("-")
	slip.line(tr("BEST ICE"), UiTheme.CAPTION)
	var row := HFlowContainer.new()
	row.name = "CorpRecords"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("h_separation", roundi(GAP * Settings.text_scale))
	for c: Array in r.get("corps", []):
		row.add_child(CorpGlyphField.new(StringName(c[0]), String(c[1]), String(c[2]), UiTheme.font_px(UiTheme.BODY), PaperInk.text(Palette.INK)))
	slip.lines.add_child(row)
	slip.line("-")
	var next := slip.line(tr("NEXT CAMPAIGN: UP TO ICE %d") % int(r.get("cap", 0)), UiTheme.CAPTION)
	next.name = "NextIce"
	if String(r.get("note", "")) != "":
		slip.line(String(r.get("note", "")), UiTheme.CAPTION).name = "IceNote"
	return slip


## The profile's records as the receipt shows them (read only): {won, lost, best (text),
## corps: [[corp_id, name, best ICE text], ...] in content-id order, cap (the next campaign's
## ICE ceiling for this corp), note (what opens at ICE `need` everywhere, "" once all
## cleared)}. The same corps and words as the screen's `ice_records_text()`.
static func records_of(profile: ProfileState, lookup: ContentLookup, need: int, cap: int) -> Dictionary:
	var corps: Array = []
	var cleared := 0
	var total := 0
	var ids: Array = lookup.ids_of_class(&"CorporationData")
	ids.sort()
	for id in ids:
		var corp := lookup.get_content(id) as CorporationData
		if corp == null:
			continue
		if corp.generated_from_profile and not CampaignRules.corporation_available(profile, lookup, corp):
			continue
		corps.append([corp.id, TextDb.t(corp, "display_name"), HudStats.ice_value(profile.best_ice_for(corp.id))])
		if not corp.generated_from_profile:
			total += 1
			if profile.best_ice_for(corp.id) >= need:
				cleared += 1
	var note := (TranslationServer.translate("Something opens at ICE %d everywhere (%d/%d).") % [need, cleared, total]) if cleared < total else ""
	return {"won": profile.campaigns_won, "lost": profile.campaigns_lost, "best": HudStats.ice_value(profile.best_ice),
		"corps": corps, "cap": cap, "note": note}


## The verdict's words (keys; §6.6: one thing in ≤ 3 words).
static func verdict_of(p_won: bool) -> String:
	return "CORP DOWN" if p_won else "CELL BURNED" # TR


## The verdict's ink (§3.3: gain for the win, harm for the loss; never colour alone: the
## word, the art and the grey city say it too).
static func color_of(p_won: bool) -> Color:
	return Palette.GAIN if p_won else Palette.HARM


## The template's motion id.
func motion() -> StringName:
	return MOTION_WON if won else MOTION_LOST


## How grey the city ends (1 for a loss; the win keeps its colour).
func grade_to() -> float:
	return 0.0 if won else RunEndStage.GREY_AMOUNT


# --- Layout ------------------------------------------------------------------------------

func _page_size() -> Vector2:
	var n := get_parent()
	while n != null:
		if n is ScrollContainer:
			return (n as ScrollContainer).size
		n = n.get_parent()
	return get_viewport_rect().size if is_inside_tree() else Vector2(size)


## Lays the rows out for the room: side by side when they fit the page's width, stacked
## otherwise (large text); the wall's columns fill its room; the story scrolls inside
## when it is taller than what is left of the page.
func _relayout() -> void:
	if _laying_out or size.x <= 0.0:
		return
	_laying_out = true
	var s := Settings.text_scale
	var room := size.x - UiTheme.SAFE_MARGIN * 2.0
	var gap := roundf(ROW_GAP * s)
	var n := wall.cells.size()
	var hero_w := hero.get_combined_minimum_size().x
	var side := n > 0 and hero_w + gap + CrewWall.row_width(mini(n, 2)) <= room
	hero_row.vertical = not side
	var wall_room := room - hero_w - gap if side else room
	var cols := 1
	while cols < n and CrewWall.row_width(cols + 1) <= wall_room:
		cols += 1
	wall.columns = maxi(1, cols)
	var foot_w := story_w + UiTheme.PANEL_PAD_H * 2.0 + receipt.get_combined_minimum_size().x + actions.get_combined_minimum_size().x + gap * 2.0
	foot_row.vertical = foot_w > room
	# Stacked, the actions come first under the hero (the focus starts on the primary, and a
	# pad player lands next to the verdict, not at the page's foot); side by side, last.
	foot_row.move_child(actions, 0 if foot_row.vertical else foot_row.get_child_count() - 1)
	# One page, one scroll (§5.3): side by side the page fits the screen and a long story
	# scrolls inside its paper; stacked (large text) the page scrolls and the paper shows
	# all its words (a scroll inside a scroll would leave its MORE BELOW tag behind).
	if not foot_row.vertical and not hero_row.vertical:
		var page := _page_size()
		var hero_h := maxf(hero.get_combined_minimum_size().y, wall.get_combined_minimum_size().y)
		var room_h := page.y - hero_h - gap - UiTheme.SAFE_MARGIN * 2.0
		# The paper's own height round its view (title, padding, the MORE BELOW tag's room),
		# measured once the view exists.
		story.scroll_content(maxf(STORY_MIN_H * s, room_h - story.content.get_theme_constant(&"margin_top") - UiTheme.PANEL_PAD_V))
		var view := story.fit.scroll.custom_minimum_size.y
		var chrome := story.get_combined_minimum_size().y - view
		if story.fit.hint.room == null or story.fit.hint.room.custom_minimum_size.y <= 0.0:
			chrome += story.fit.hint.get_combined_minimum_size().y + ScrollHint.MARGIN.y * 2.0
		story.fit.max_height = maxf(STORY_MIN_H * s, room_h - chrome)
	elif story.fit != null:
		story.fit.max_height = 0.0
	_laying_out = false
	_refresh_hint.call_deferred()


## The story's MORE BELOW tag follows the paper once the rows have been laid out (it places
## itself on the screen and the stage centres its column after it).
func _refresh_hint() -> void:
	if is_instance_valid(story) and story.fit != null and story.fit.hint != null and story.fit.hint.is_inside_tree():
		story.fit.hint.refresh()


# --- The T4 sequence ---------------------------------------------------------------------

## Plays the T4 sequence (or shows its end at once when the motion doesn't play).
func play() -> void:
	finish_now()
	var id := motion()
	if not Motion.live(id):
		return
	_apply(0.0)
	_tween = create_tween()
	_tween.tween_method(_apply, 0.0, 1.0, Motion.seconds(id))
	_tween.tween_callback(finish_now)
	# PageTransition.settle / Typing.finish_all end a page's motions through this meta (as
	# RunEndStage): the stage then shows its end.
	set_meta(Typing.META, _tween)


## True while the sequence plays.
func running() -> bool:
	return _tween != null and _tween.is_valid()


## Shows the end state now (a press, a settle, reduce effects).
func finish_now() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null
	if has_meta(Typing.META):
		remove_meta(Typing.META)
	_apply(1.0)


## A beat's progress 0..1 at sequence time `u`.
static func beat(u: float, at: float, share: float) -> float:
	return clampf((u - at) / share, 0.0, 1.0) if share > 0.0 else (1.0 if u >= at else 0.0)


## The sequence at time `u` (0..1): every piece set from `u` alone, so a skip, a settle and
## reduce effects all land on the same end state (`_apply(1)`).
func _apply(u: float) -> void:
	_u = u
	if won:
		var fall := beat(u, AT_ART, ART_SHARE)
		(art as CorpFallArt).set_fall(fall * fall)
		(art as CorpFallArt).set_spray(beat(u, AT_SPRAY, SPRAY_SHARE))
		city_lean.emit(lerpf(lean_from, 1.0, smoothstep(0.0, 1.0, beat(u, AT_ART, AT_STAMP - AT_ART))))
	else:
		(art as CellCrackArt).set_crack(beat(u, AT_ART, ART_SHARE))
		var sp := beat(u, AT_SPLIT, SPLIT_SHARE)
		(art as CellCrackArt).set_split(1.0 - (1.0 - sp) * (1.0 - sp))
		_set_grade(grade_to() * smoothstep(0.0, 1.0, beat(u, AT_GRADE, GRADE_SHARE)))
	var st := beat(u, AT_STAMP, STAMP_SHARE)
	stamp.modulate.a = minf(1.0, st * 2.0)
	stamp.pivot_offset = stamp.size * 0.5
	stamp.scale = Vector2.ONE * lerpf(Motion.amplitude(motion()) if u < 1.0 else 1.0, 1.0, st * st)
	for i in wall.cells.size():
		var c := wall.cells[i]
		var w := beat(u, AT_WALL + WALL_STAGGER * i, WALL_SHARE)
		c.modulate.a = w
		c.pivot_offset = c.size * 0.5
		c.scale = Vector2.ONE * lerpf(WALL_POP, 1.0, w)
	var f := beat(u, AT_FOOT, FOOT_SHARE)
	for p: CanvasItem in [story, receipt, actions]:
		p.modulate.a = f
	# The MORE BELOW tag is top level (it keeps no parent's modulate): it fades with the paper.
	if story.fit != null and story.fit.hint != null:
		story.fit.hint.modulate.a = f


func _set_grade(v: float) -> void:
	(grade.material as ShaderMaterial).set_shader_parameter(&"amount", v)
	grade.visible = v > 0.0


## The grade's amount now (0 colour, 1 grey; tests).
func grade_amount() -> float:
	return float((grade.material as ShaderMaterial).get_shader_parameter(&"amount"))


## The sequence's time now (0..1; 1 = the end state).
func progress() -> float:
	return _u


func _process(_delta: float) -> void:
	# A settle took the meta (PageTransition.settle, Typing.finish_all): end now.
	if _tween != null and not has_meta(Typing.META):
		finish_now()


func _input(event: InputEvent) -> void:
	# §8 T4: skippable: a press shows the end at once (and does nothing else).
	if not running():
		return
	var pressed := (event is InputEventKey and (event as InputEventKey).pressed and not (event as InputEventKey).echo) \
		or (event is InputEventMouseButton and (event as InputEventMouseButton).pressed) \
		or (event is InputEventJoypadButton and (event as InputEventJoypadButton).pressed)
	if pressed:
		finish_now()
		get_viewport().set_input_as_handled()


## At least as tall as its column (a page taller than the screen scrolls; its top never
## centres off the screen).
func _get_minimum_size() -> Vector2:
	return column.get_combined_minimum_size() + Vector2(0, UiTheme.SAFE_MARGIN * 2.0) if column != null else Vector2.ZERO
