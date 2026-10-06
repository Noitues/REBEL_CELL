class_name HeatTerminal
extends CrtWindow
## HQ-B (M14, designer rulings Q1 / Q2 2026-10-05; the HQ redesign's `heat_indicator.jpg`):
## the Heat terminal the HEAT tag drops: `> HEAT // SUSPECT FILE` with the band word on its
## tag, the rules in force (each with the threshold that put it in force), the next
## thresholds and what they bring, the sinks, and at the HQ the one Heat action the GDD
## gives it: SCRUB HEAT (11.4, its price and the next one). In a run it opens read-only
## (Q2: no SCRUB). The WANTED poster's and CELL STATUS's Heat rows live here now (Q1). It
## reads the campaign (a view): SCRUB is a signal up, the scene buys. Named "HeatTerminal";
## the scrub chip "ScrubHeat".

signal scrub_pressed
signal closed

## The window's width at text scale 1.0 (px; it grows with the text) and the gap under the tag.
const WIDTH := 360.0
const GAP := 4.0
## The row captions' column (px at 1.0).
const CAPTION_WIDTH := 84.0
## How many thresholds NEXT names at most.
const NEXT_MAX := 2
## Words (translation keys, translated here once).
const TITLE := "HEAT // SUSPECT FILE" # TR
const ROW_IN_FORCE := "IN FORCE" # TR
const ROW_NEXT := "NEXT" # TR
const ROW_SINKS := "SINKS" # TR
const NOTHING_YET := "nothing yet" # TR
const NONE_LEFT := "the top of the scale" # TR
const NEXT_RAID := "RAID" # TR
const NEXT_COMPLICATION := "complication" # TR
const NEXT_RULES := "harder rules" # TR
const SINK_WORDS := "Heat objective Sites (the cooling mark on the map)" # TR
const SCRUB := "SCRUB HEAT %s" # TR
const SCRUB_LINE := "pay %d Schematics (next %d)" # TR
const READ_ONLY_LINE := "Scrub Heat at the HQ." # TR

var read_only: bool = false
var scrub: MenuChip = null


## The terminal for the campaign `c` under `cfg`; `p_read_only` in a run (no SCRUB).
func _init(c: CampaignState = null, cfg: CampaignConfigData = null, p_read_only: bool = false) -> void:
	super(TranslationServer.translate(TITLE), Palette.HEAT_BAND_COLORS[mini(Palette.heat_band(c.heat if c != null else 0, HeatRules.band_levels(c, cfg) if c != null and cfg != null else [] as Array[int]), Palette.HEAT_BAND_COLORS.size() - 1)])
	name = "HeatTerminal"
	read_only = p_read_only
	top_level = true
	z_index = Z
	mouse_filter = Control.MOUSE_FILTER_STOP
	custom_minimum_size.x = WIDTH * Settings.text_scale
	if c == null or cfg == null:
		return
	var levels := HeatRules.band_levels(c, cfg)
	tag_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	tag_label.text = TranslationServer.translate(HeatPoster.BAND_WORDS[mini(HeatPoster.band_of(c.heat, levels), HeatPoster.BAND_WORDS.size() - 1)]).to_upper()
	var rows := VBoxContainer.new()
	rows.name = "HeatRows"
	rows.add_theme_constant_override("separation", 4)
	body.add_child(rows)
	var in_force := PackedStringArray()
	for t in _sorted(cfg.heat_thresholds):
		if c.heat < t.heat:
			continue
		for m in t.ongoing_modifiers:
			if m != null:
				in_force.append("%s (%d+)" % [modifier_text(m), t.heat])
	_row(rows, "InForce", ROW_IN_FORCE, "\n".join(in_force) if not in_force.is_empty() else TranslationServer.translate(NOTHING_YET), Palette.TEXT_HI)
	var next := PackedStringArray()
	for t in _sorted(cfg.heat_thresholds):
		if t.heat > c.heat and next.size() < NEXT_MAX:
			next.append("%d %s" % [HeatRules.effective_heat(t, c, cfg), _brings(t)])
	_row(rows, "Next", ROW_NEXT, "  //  ".join(next) if not next.is_empty() else TranslationServer.translate(NONE_LEFT), Palette.HEAT_FLAGGED)
	_row(rows, "Sinks", ROW_SINKS, TranslationServer.translate(SINK_WORDS), Palette.TEXT_HI)
	if read_only:
		_row(rows, "ReadOnly", "", TranslationServer.translate(READ_ONLY_LINE), Palette.TEXT_MID)
		return
	var amount := HeatRules.scaled_delta(c, -cfg.heat_purchase_amount, cfg)
	var price := CampaignRules.heat_purchase_price(c, cfg)
	scrub = MenuChip.new(TranslationServer.translate(SCRUB) % TextDb.signed(amount),
		TranslationServer.translate(SCRUB_LINE) % [price, price + cfg.heat_purchase_increment], Palette.HEAT_FLAGGED)
	scrub.pre_translated = true
	scrub.name = "ScrubHeat"
	scrub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scrub.tooltip_text = UiTip.fold(TranslationServer.translate("Costs %d Schematics (you have %d): Heat changes by %d.") % [price, c.schematics, amount])
	scrub.pressed.connect(func() -> void: scrub_pressed.emit())
	body.add_child(scrub)


## Draw order over the page (the drop-down reads over the map and the hand).
const Z := 40


## Drops the terminal under `tag` (global rect), kept on the screen.
func drop_under(tag: Rect2, screen: Rect2) -> void:
	_tag = tag
	_screen = screen
	_place()
	if not minimum_size_changed.is_connected(_place):
		minimum_size_changed.connect(_place)
	if not resized.is_connected(_place):
		resized.connect(_place)


var _tag: Rect2 = Rect2()
var _screen: Rect2 = Rect2()


## Under the tag, as wide as its words need, kept on the screen (its rows wrap after the
## first layout: placed again when its size settles).
func _place() -> void:
	var s := get_combined_minimum_size()
	if size != s:
		size = s
	var at := Vector2(_tag.position.x, _tag.end.y + GAP)
	position = at.clamp(_screen.position, (_screen.end - s).max(_screen.position))


## The thresholds in Heat order (ties by id: deterministic).
static func _sorted(list: Array) -> Array[HeatThresholdData]:
	var out: Array[HeatThresholdData] = []
	for t in list:
		if t != null:
			out.append(t)
	out.sort_custom(func(a: HeatThresholdData, b: HeatThresholdData) -> bool: return a.heat < b.heat or (a.heat == b.heat and String(a.id) < String(b.id)))
	return out


## What crossing threshold `t` brings, in a word: a raid, a complication, harder rules.
static func _brings(t: HeatThresholdData) -> String:
	if t.event_raid != null:
		return TranslationServer.translate(NEXT_RAID)
	if not t.event_complications.is_empty():
		return TranslationServer.translate(NEXT_COMPLICATION)
	return TranslationServer.translate(NEXT_RULES)


## A rule modifier as words ("Raid strength +10%"), translated.
static func modifier_text(m: RuleModifierData) -> String:
	var key: String = RC.RuleModifierType.keys()[m.type]
	var pct := key.ends_with("_PCT")
	return "%s %s%s" % [TranslationServer.translate(key.trim_suffix("_PCT").capitalize()), TextDb.signed(roundi(m.value)), "%" if pct else ""]


func _row(rows: VBoxContainer, id: String, caption: String, value: String, col: Color) -> void:
	var row := HBoxContainer.new()
	row.name = id
	row.add_theme_constant_override("separation", 8)
	var cap := Label.new()
	cap.text = TranslationServer.translate(caption) if caption != "" else ""
	cap.custom_minimum_size.x = CAPTION_WIDTH * Settings.text_scale
	cap.add_theme_font_override("font", Palette.mono())
	cap.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	cap.add_theme_color_override("font_color", Palette.TEXT_MID)
	row.add_child(cap)
	var v := Label.new()
	v.name = "Value"
	v.text = value
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_color_override("font_color", col)
	UiWrap.whole_words(v)
	row.add_child(v)
	rows.add_child(row)
	TextDb.shown_as_given(row)


## A press outside closes it, as do Esc / B (the scene frees it and puts focus back).
func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed and not get_global_rect().has_point((event as InputEventMouseButton).global_position):
		closed.emit()
	elif event.is_action_pressed(&"ui_cancel"):
		closed.emit()
		get_viewport().set_input_as_handled()
