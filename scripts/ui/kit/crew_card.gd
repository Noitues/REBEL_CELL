class_name CrewCard
extends PanelContainer
## An operative's dossier card (reference: the crew Polaroids laid on the deck): taped
## paper with the Polaroid, the name in marker, "// CLASS // RANK" tags, an HP strip,
## the kit in numbers and the operative's orders underneath. `orders` holds the buttons
## the scene adds. A downed operative's card is greyed and stamped.

var polaroid: Polaroid
var orders: VBoxContainer
var dead: bool = false
var tilt: float = 0.0
var hp_frac: float = 1.0
var stamp_text: String = ""
## The stamp over the Polaroid ("ON <SITE>", FLATLINED): width and largest font size.
const STAMP_WIDTH := 160.0
const STAMP_FONT_SIZE := 26
const STAMP_MIN_FONT_SIZE := 10
## The operative's name (the tooltip's title).
var name_text: String = ""
## Dossier width and lettering at text scale 1.0 (they grow with it, H21 #15).
const CARD_WIDTH := 196.0
const NAME_SIZE := 20
const DETAIL_SIZE := 12
## H24 S11: at big text the dossier goes compact so the crew sits side by side and every
## dossier is on the page (at 1.6 the second was cut by MORE BELOW): from COMPACT_FROM the
## card grows with the text only up to CARD_MAX_SCALE and the Polaroid shrinks to
## COMPACT_POLAROID of its size.
const COMPACT_FROM := 1.3
const CARD_MAX_SCALE := 1.15
## ART-0 C (text scale 2.0): above BIG_FROM the compact card widens again by BIG_GROW of
## each step of text scale (196 px x 1.43 at 2.0: two dossiers still side by side in the
## crew window, the name on one line, the dossier inside the page's view). 1.6 and below
## are unchanged.
const BIG_FROM := 1.6
const BIG_GROW := 0.7
## ANIM-R2 R13: compact, the Polaroid is this share of its size and the class tags sit
## beside it (at 1.6 the tags were cut by the page's foot and the Loadout button hidden
## under MORE BELOW).
const COMPACT_POLAROID := 0.5
const POLAROID_SIZE := Vector2(120, 144)


func _init(p_name: String, p_class: String, rank: int, hp: int, max_hp: int, detail: String, p_tilt: float = 0.0) -> void:
	tilt = p_tilt
	name_text = p_name
	hp_frac = clampf(float(hp) / maxf(1.0, max_hp), 0.0, 1.0)
	# The dossier's lettering and width follow the text size (H21 #15).
	var s := Settings.text_scale
	var compact := is_compact()
	custom_minimum_size = Vector2(CARD_WIDTH * (minf(s, CARD_MAX_SCALE) + maxf(0.0, s - BIG_FROM) * BIG_GROW if compact else s), 0)
	var style := UiTheme.box(Palette.NOTE_PAPER, edge_color(), roundi(edge_width()), 10, 12)
	style.shadow_color = Palette.SHADOW
	style.shadow_size = 7
	style.shadow_offset = Vector2(4, 5)
	add_theme_stylebox_override("panel", style)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 4)
	add_child(box)
	# H24 S3: the rank tag and the class tags in the player's language ("R0" and "RANK" were
	# English); the words come translated, the card shows them as given.
	polaroid = Polaroid.new(tr("%s R%d") % [p_name, rank], "[%s PORTRAIT]" % p_class.to_upper(), -2.0 + tilt)
	polaroid.custom_minimum_size = POLAROID_SIZE * (COMPACT_POLAROID if compact else 1.0)
	polaroid.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(polaroid)
	var name_label := Label.new()
	name_label.text = p_name.to_upper()
	name_label.add_theme_font_override("font", Palette.marker())
	name_label.add_theme_font_size_override("font_size", roundi(NAME_SIZE * s))
	name_label.add_theme_color_override("font_color", text_ink())
	name_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	box.add_child(name_label)
	var tags := Label.new()
	tags.text = tr("// %s // RANK %d") % [p_class.to_upper(), rank]
	tags.add_theme_color_override("font_color", PaperInk.text(Color(Palette.INK, TAGS_ALPHA)))
	tags.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	tags.add_theme_font_size_override("font_size", roundi(DETAIL_SIZE * s))
	UiWrap.whole_words(tags)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	box.add_child(tags)
	var hp_strip := Control.new()
	hp_strip.custom_minimum_size = Vector2(0, 16)
	hp_strip.draw.connect(func() -> void:
		var r := Rect2(Vector2(0, 4), Vector2(hp_strip.size.x, 8))
		hp_strip.draw_rect(r, PaperInk.opaque(Color(Palette.INK, HP_BACK_ALPHA), Palette.NOTE_PAPER))
		hp_strip.draw_rect(Rect2(r.position, Vector2(r.size.x * hp_frac, r.size.y)), Palette.CELL_PINK if hp_frac < 0.35 else Color("#2a8f3c"))
		hp_strip.draw_rect(r, PaperInk.edge(Color(Palette.INK, HP_EDGE_ALPHA)), false, PaperInk.edge_width(1.0)))
	box.add_child(hp_strip)
	var info := Label.new()
	info.text = detail
	UiWrap.whole_words(info)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	info.custom_minimum_size.x = custom_minimum_size.x - 20.0 * s
	info.add_theme_color_override("font_color", text_ink())
	info.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	info.add_theme_font_size_override("font_size", roundi(DETAIL_SIZE * s))
	box.add_child(info)
	if compact:
		# ANIM-R1 M12: at big text the HP (strip and numbers) comes right under the name, so
		# the first screen of the HQ shows it (at 1.6 the page cut the dossier above it).
		box.move_child(hp_strip, name_label.get_index() + 1)
		box.move_child(info, hp_strip.get_index() + 1)
		# ANIM-R2 R13: the class tags beside the Polaroid, so the orders (Loadout) come on the
		# first screen too.
		var top := HBoxContainer.new()
		top.add_theme_constant_override("separation", 6)
		box.add_child(top)
		box.move_child(top, 0)
		polaroid.reparent(top)
		tags.reparent(top)
		tags.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tags.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	orders = VBoxContainer.new()
	orders.add_theme_constant_override("separation", 4)
	box.add_child(orders)
	# Animation pass ANIM-6 (4.13): the Polaroid tilts a little while the dossier is hovered.
	mouse_entered.connect(tilt_polaroid.bind(true))
	mouse_exited.connect(tilt_polaroid.bind(false))


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


## Gives the Polaroid this operative's own face (PortraitArt.operative_subject).
func set_operative(class_id: StringName, operative_id: StringName) -> void:
	polaroid.set_operative(class_id, operative_id)


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text, name_text) if for_text != "" else null


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


func _draw() -> void:
	draw_rect(Rect2(size.x * 0.5 - 24, -7, 48, 14), PaperInk.opaque(Palette.NOTE_TAPE, Palette.NOTE_PAPER))
	if dead or stamp_text != "":
		var t := stamp_text if stamp_text != "" else tr("FLATLINED")
		draw_set_transform(Vector2(size.x * 0.5, polaroid.position.y + polaroid.size.y * 0.55), -0.3, Vector2.ONE)
		draw_rect(Rect2(-80, -20, 160, 40), Color(Palette.CELL_PINK, 0.85), false, 3.0)
		# Long Site names shrink to fit the stamp.
		var fs := STAMP_FONT_SIZE
		var w := Palette.display().get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if w > STAMP_WIDTH - 8.0:
			fs = maxi(STAMP_MIN_FONT_SIZE, floori(fs * (STAMP_WIDTH - 8.0) / w))
		draw_string(Palette.display(), Vector2(-STAMP_WIDTH * 0.5, 10), t, HORIZONTAL_ALIGNMENT_CENTER, STAMP_WIDTH, fs, Color(Palette.CELL_PINK, 0.9))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


# --- High contrast on paper (ART-0 F (ported from art-pass WF b9af7e3, ART_BIBLE v2 §5.6)) -------------------------
## The dossier's soft edge, class tags and HP strip alphas out of high contrast.
const EDGE_ALPHA := 0.45
const TAGS_ALPHA := 0.75
const HP_BACK_ALPHA := 0.15
const HP_EDGE_ALPHA := 0.6


## The dossier's words: INK on paper (7:1 under high contrast too).
func text_ink() -> Color:
	return PaperInk.text(Palette.INK)


## The paper's edge: soft INK, or opaque INK under high contrast.
func edge_color() -> Color:
	return PaperInk.edge(Color(Palette.INK, EDGE_ALPHA))


## The paper's edge width (px): 1, or PaperInk.EDGE_PX under high contrast.
func edge_width() -> float:
	return PaperInk.edge_width(1.0)
