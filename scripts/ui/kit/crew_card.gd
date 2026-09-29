class_name CrewCard
extends PanelContainer
## An operative's dossier card (reference: the crew Polaroids laid on the deck): taped
## paper with the class accent stripe down its left edge (ART_BIBLE 7.1: the accent sits
## on the portrait, the bezel ornament and this stripe only), the Polaroid (the rank as
## its caption: the name is printed below it, critique `08`), the name in marker, the
## class with its silhouette glyph, an HP strip on the §3.5 scale, the kit as icon +
## number fields (StatField: HP, deck, Daemons) and the operative's orders underneath.
## `orders` holds the buttons the scene adds. A downed operative's card shows the
## flatlined portrait and is stamped. High contrast (§12): opaque black, TEXT_HI text.

var polaroid: Polaroid
var orders: VBoxContainer
var dead: bool = false:
	set(v):
		dead = v
		if polaroid != null:
			polaroid.set_expression(PortraitArt.Expr.FLATLINED if v else PortraitArt.Expr.NEUTRAL)
		queue_redraw()
var tilt: float = 0.0
var hp_frac: float = 1.0
var stamp_text: String = ""
## The class's content id (the stripe's accent and the silhouette glyph).
var class_id: StringName = &""
## The stamp over the Polaroid ("ON <SITE>", FLATLINED): width and largest font size.
const STAMP_WIDTH := 160.0
const STAMP_HEIGHT := 40.0
const STAMP_FONT_SIZE := UiTheme.HEADING
const STAMP_MIN_FONT_SIZE := UiTheme.CAPTION
const STAMP_TURN := -0.3
const STAMP_EDGE := 3.0
## The operative's name (the tooltip's title).
var name_text: String = ""
## Dossier width and lettering at text scale 1.0 (they grow with it, H21 #15): the name in
## `label` handwriting, the class and numbers in `caption` (§4.2).
const CARD_WIDTH := 196.0
const NAME_SIZE := UiTheme.LABEL
const DETAIL_SIZE := UiTheme.CAPTION
## H24 S11: at big text the dossier goes compact so the crew sits side by side and every
## dossier is on the page (at 1.6 the second was cut by MORE BELOW): from COMPACT_FROM the
## card grows with the text only up to CARD_MAX_SCALE and the Polaroid shrinks to
## COMPACT_POLAROID of its size.
const COMPACT_FROM := 1.3
const CARD_MAX_SCALE := 1.15
## ANIM-R2 R13: compact, the Polaroid is this share of its size and the class tags sit
## beside it (at 1.6 the tags were cut by the page's foot and the Loadout button hidden
## under MORE BELOW).
const COMPACT_POLAROID := 0.5
const POLAROID_SIZE := Vector2(120, 144)
## The accent stripe's width (px at 1.0) and the tape strip over the top edge.
const STRIPE_WIDTH := 6.0
const TAPE_SIZE := Vector2(48, 14)
## Paper panel: edge alpha, margins (px), shadow.
const EDGE_ALPHA := 0.45
const MARGIN_H := UiTheme.SP_S + 2
const MARGIN_V := UiTheme.SP_M - 4
const SHADOW_SIZE := 7
const SHADOW_OFFSET := Vector2(4, 5)
## Rows: the HP strip's height and bar, the stat fields' gap (px at 1.0).
const HP_STRIP_H := 16.0
const HP_BAR_H := 8.0
const HP_BAR_Y := 4.0
const STAT_GAP := UiTheme.SP_S + 2

var _stats: HFlowContainer
var _info: Label
var _labels: Array[Label] = []
var _fields: Array[StatField] = []
var _glyph: Control


func _init(p_name: String, p_class: String, rank: int, hp: int, max_hp: int, detail: String, p_tilt: float = 0.0) -> void:
	tilt = p_tilt
	name_text = p_name
	class_id = StringName(p_class.to_lower())
	hp_frac = clampf(float(hp) / maxf(1.0, max_hp), 0.0, 1.0)
	# The dossier's lettering and width follow the text size (H21 #15).
	var s := Settings.text_scale
	var compact := is_compact()
	custom_minimum_size = Vector2(CARD_WIDTH * (minf(s, CARD_MAX_SCALE) if compact else s), 0)
	add_theme_stylebox_override("panel", _panel_style())
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", UiTheme.SP_XS)
	add_child(box)
	# H24 S3: the rank tag in the player's language; the Polaroid carries the rank (not the
	# name, which is printed right below it: critique 08).
	polaroid = Polaroid.new(tr("R%d") % rank if compact else tr("RANK %d") % rank, "[%s PORTRAIT]" % p_class.to_upper(), -2.0 + tilt)
	polaroid.custom_minimum_size = POLAROID_SIZE * (COMPACT_POLAROID if compact else 1.0)
	polaroid.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(polaroid)
	var name_label := _label(p_name.to_upper(), NAME_SIZE, Palette.marker())
	name_label.name = "Name"
	box.add_child(name_label)
	# The class with its silhouette glyph (ART_BIBLE 7.1).
	var tags_row := HBoxContainer.new()
	tags_row.name = "ClassRow"
	tags_row.add_theme_constant_override("separation", UiTheme.SP_XS)
	_glyph = Control.new()
	_glyph.name = "ClassGlyph"
	_glyph.custom_minimum_size = Vector2.ONE * roundf(UiTheme.font_px(UiTheme.LABEL) * 1.2)
	_glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glyph.draw.connect(_draw_glyph)
	tags_row.add_child(_glyph)
	var tags := _label(tr("// %s") % p_class.to_upper(), DETAIL_SIZE, Palette.mono())
	tags.name = "ClassTag"
	tags.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tags.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tags.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	tags_row.add_child(tags)
	box.add_child(tags_row)
	var hp_strip := Control.new()
	hp_strip.name = "HpStrip"
	hp_strip.custom_minimum_size = Vector2(0, HP_STRIP_H)
	hp_strip.draw.connect(_draw_hp.bind(hp_strip))
	box.add_child(hp_strip)
	# The kit as icon + number fields; the deck and Daemons join once set_stats knows them.
	_stats = HFlowContainer.new()
	_stats.name = "Stats"
	_stats.add_theme_constant_override("h_separation", roundi(STAT_GAP * s))
	_stats.add_theme_constant_override("v_separation", UiTheme.SP_XS)
	box.add_child(_stats)
	_add_field(StatIcon.HP, "%d/%d" % [hp, max_hp])
	_info = _label(detail, DETAIL_SIZE, Palette.mono())
	_info.name = "Detail"
	_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_info.custom_minimum_size.x = custom_minimum_size.x - 20.0 * s
	box.add_child(_info)
	if compact:
		# ANIM-R1 M12: at big text the HP (strip and numbers) comes right under the name, so
		# the first screen of the HQ shows it (at 1.6 the page cut the dossier above it).
		box.move_child(hp_strip, name_label.get_index() + 1)
		box.move_child(_stats, hp_strip.get_index() + 1)
		box.move_child(_info, _stats.get_index() + 1)
		# ANIM-R2 R13: the class tags beside the Polaroid, so the orders (Loadout) come on the
		# first screen too.
		var top := HBoxContainer.new()
		top.add_theme_constant_override("separation", UiTheme.SP_S - 2)
		box.add_child(top)
		box.move_child(top, 0)
		polaroid.reparent(top)
		tags_row.reparent(top)
		tags_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tags_row.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	orders = VBoxContainer.new()
	orders.add_theme_constant_override("separation", UiTheme.SP_XS)
	box.add_child(orders)
	# Animation pass ANIM-6 (4.13): the Polaroid tilts a little while the dossier is hovered.
	mouse_entered.connect(tilt_polaroid.bind(true))
	mouse_exited.connect(tilt_polaroid.bind(false))


## The paper panel, or opaque black with a TEXT_HI edge under high contrast (§12).
func _panel_style() -> StyleBoxFlat:
	var hc := Settings.high_contrast
	var style := UiTheme.box(HighContrast.BG if hc else Palette.NOTE_PAPER, Palette.TEXT_HI if hc else Color(Palette.INK, EDGE_ALPHA),
		HighContrast.HC_TINT_BORDER if hc else 1, MARGIN_H, MARGIN_V)
	style.content_margin_left += STRIPE_WIDTH * Settings.text_scale
	style.shadow_color = Palette.SHADOW
	style.shadow_size = SHADOW_SIZE
	style.shadow_offset = SHADOW_OFFSET
	return style


## The dossier's text colour: INK on paper, TEXT_HI on black under high contrast.
static func text_color() -> Color:
	return Palette.TEXT_HI if Settings.high_contrast else Palette.INK


func _label(text: String, step: int, font: Font) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	l.add_theme_color_override("font_color", text_color())
	l.add_theme_color_override("font_shadow_color", Color(text_color(), 0.0))
	_labels.append(l)
	return l


func _add_field(kind: StringName, text: String) -> StatField:
	var f := StatField.new(kind, text, UiTheme.font_px(DETAIL_SIZE), text_color())
	_stats.add_child(f)
	_fields.append(f)
	return f


## Shows the kit as fields: HP, deck size and Daemons (icon + number each); the detail
## sentence the screen passed is then not shown.
func set_stats(hp: int, max_hp: int, deck: int, daemons: int) -> void:
	hp_frac = clampf(float(hp) / maxf(1.0, max_hp), 0.0, 1.0)
	for f in _fields:
		f.queue_free()
	_fields.clear()
	for f in _stats.get_children():
		_stats.remove_child(f)
	_add_field(StatIcon.HP, "%d/%d" % [hp, max_hp])
	_add_field(StatIcon.CARDS, str(deck))
	_add_field(StatIcon.DAEMON, str(daemons))
	_info.visible = false
	queue_redraw()


## The stat field of `kind` (StatIcon kind), or null.
func stat_field(kind: StringName) -> StatField:
	for f in _fields:
		if f.kind == kind:
			return f
	return null


## Every Label the dossier shows (tests: the caption floor).
func text_labels() -> Array[Label]:
	var out: Array[Label] = []
	for l in _labels:
		if l.visible:
			out.append(l)
	for f in _fields:
		out.append(f.value_label)
	return out


## Tilts the Polaroid `polaroid_tilt` degrees further (hover) or back to its rest.
func tilt_polaroid(on: bool) -> void:
	if polaroid == null or not polaroid.is_inside_tree():
		return
	if on and not _tilted:
		# Its rest as the dossier lays it out (the box straightens it).
		_polaroid_rest = polaroid.rotation_degrees
	_tilted = on
	polaroid.pivot_offset = polaroid.size * 0.5
	Motion.run(&"polaroid_tilt", polaroid, ^"rotation_degrees", _polaroid_rest + (Motion.amplitude(&"polaroid_tilt") if on else 0.0))


var _tilted: bool = false
var _polaroid_rest: float = 0.0


## Whether dossiers are compact at the current text size (H24 S11).
static func is_compact() -> bool:
	return Settings.text_scale >= COMPACT_FROM


## Gives the Polaroid this operative's own face (PortraitArt.operative_subject), the stripe
## its class accent, and, when the campaign has the operative, its kit as fields.
func set_operative(p_class_id: StringName, operative_id: StringName) -> void:
	class_id = p_class_id
	polaroid.set_operative(p_class_id, operative_id)
	var c := RunManager.campaign
	if c != null:
		for op in c.roster:
			if op.id == operative_id:
				set_stats(op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size())
				break
	_glyph.queue_redraw()
	queue_redraw()


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text, name_text) if for_text != "" else null


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


func _draw_glyph() -> void:
	PortraitArt.draw_silhouette(_glyph, Rect2(Vector2.ZERO, _glyph.size), class_id, text_color())


func _draw_hp(strip: Control) -> void:
	var r := Rect2(Vector2(0, HP_BAR_Y), Vector2(strip.size.x, HP_BAR_H))
	strip.draw_rect(r, Color(text_color(), 0.15))
	strip.draw_rect(Rect2(r.position, Vector2(r.size.x * hp_frac, r.size.y)), Palette.hp_color(hp_frac))
	strip.draw_rect(r, Color(text_color(), 0.6), false, 1.0)


func _draw() -> void:
	# The class accent stripe down the left edge (ART_BIBLE 7.1), then the tape.
	draw_rect(Rect2(Vector2.ZERO, Vector2(STRIPE_WIDTH * Settings.text_scale, size.y)), Palette.class_accent(class_id))
	draw_rect(Rect2(Vector2(size.x * 0.5 - TAPE_SIZE.x * 0.5, -TAPE_SIZE.y * 0.5), TAPE_SIZE), Palette.NOTE_TAPE)
	if dead or stamp_text != "":
		var t := stamp_text if stamp_text != "" else tr("FLATLINED")
		# FLATLINED is harm (§3.3); a posting stamp is plain ink.
		var col := Palette.HARM if stamp_text == "" else text_color()
		draw_set_transform(Vector2(size.x * 0.5, polaroid.position.y + polaroid.size.y * 0.55), STAMP_TURN, Vector2.ONE)
		draw_rect(Rect2(-STAMP_WIDTH * 0.5, -STAMP_HEIGHT * 0.5, STAMP_WIDTH, STAMP_HEIGHT), col, false, STAMP_EDGE)
		# Long Site names shrink to fit the stamp.
		var fs := STAMP_FONT_SIZE
		var w := Palette.display().get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if w > STAMP_WIDTH - 8.0:
			fs = maxi(STAMP_MIN_FONT_SIZE, floori(fs * (STAMP_WIDTH - 8.0) / w))
		draw_string(Palette.display(), Vector2(-STAMP_WIDTH * 0.5, fs * 0.35), t, HORIZONTAL_ALIGNMENT_CENTER, STAMP_WIDTH, fs, col)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
