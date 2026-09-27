class_name MapLegend
extends TerminalWindow
## The map key for the city map views (Settings.map_legend): what the highlight colours,
## marks, line styles and badge glyphs mean. Every status row has its own glyph, so the
## key never relies on colour alone (GDD 9.6): claimed Sites carry a spray ring, Seized
## ones a cross. Follows the setting live, and can resize a linked control with it (the
## HQ Grid's Site list takes the legend's room back when it is off).

const ROWS := [["○", "#FF3DA8", "claimed (yours): spray ring"], ["■", "#5CE1FF", "cleared"], ["■", "", "corporate"], ["✕", "#FFD24D", "seized: crossed out"],
	["━", "#FF3DA8", "your network link"], ["- -", "", "threat route"]]
## The node icons (H21 #14), drawn by CityMapOverlay.draw_icon exactly as on the map:
## [kind, text shown in the icon, meaning].
const ICON_ROWS := [[CityMapOverlay.KIND_EXPLOIT, "", "exploit"], [CityMapOverlay.KIND_HEAT, "", "heat reduction"],
	[CityMapOverlay.KIND_BOSS, "", "boss"], [CityMapOverlay.KIND_HOME, "", "CORE (your home)"], [CityMapOverlay.KIND_TIER, "T2", "Site tier (T1-T4)"]]
## Row width, and the compact variant's font size (legends pinned over a map).
const ROW_WIDTH := 200.0
const COMPACT_FONT := 12
## Icon swatch side (px) at text scale 1.0, and the icon's radius as a share of it.
const ICON_SWATCH := 22.0
const ICON_SHARE := 0.36
const ICON_SWATCH_GAP := 8
## Margin (px) of a legend pinned to a map area's bottom-left corner.
const PIN_MARGIN := 10.0

var _linked: Control = null
var _size_on: Vector2 = Vector2.ZERO
var _size_off: Vector2 = Vector2.ZERO


func _init(corporation_id: StringName = &"", compact: bool = false) -> void:
	super("MAP LEGEND")
	name = "MapLegend"
	custom_minimum_size.x = 230
	var corp := Palette.corp_color(corporation_id).to_html(false)
	for r in ROWS:
		var l := RichTextLabel.new()
		l.bbcode_enabled = true
		l.fit_content = true
		l.scroll_active = false
		l.custom_minimum_size.x = ROW_WIDTH
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if compact:
			l.add_theme_font_size_override("normal_font_size", COMPACT_FONT)
		l.text = "[color=#%s]%s[/color]  %s" % [r[1].trim_prefix("#") if r[1] != "" else corp, r[0], r[2]]
		body.add_child(l)
	for r in ICON_ROWS:
		body.add_child(_icon_row(r[0], r[1], r[2], compact))
	visible = Settings.map_legend
	Settings.changed.connect(_on_settings_changed)


## A key row with the map's own icon of `kind` (named "Icon_<kind>").
func _icon_row(kind: String, text: String, meaning: String, compact: bool) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Icon_%s" % kind
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", ICON_SWATCH_GAP)
	var side := ICON_SWATCH * Settings.text_scale
	var swatch := Control.new()
	swatch.custom_minimum_size = Vector2(side, side)
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	swatch.draw.connect(func() -> void:
		CityMapOverlay.draw_icon(swatch, kind, swatch.size * 0.5, minf(swatch.size.x, swatch.size.y) * ICON_SHARE, Palette.PAPER, text))
	row.add_child(swatch)
	var l := Label.new()
	l.text = meaning
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if compact:
		l.add_theme_font_size_override("font_size", COMPACT_FONT)
	row.add_child(l)
	return row


## A compact legend pinned to `area`'s bottom-left corner (the raid maps: the map is the
## city behind the panels, `area` the open part of the screen over it).
static func pin_to(area: Control, corporation_id: StringName) -> MapLegend:
	var legend := MapLegend.new(corporation_id, true)
	legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	area.add_child(legend)
	legend.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT, Control.PRESET_MODE_MINSIZE, int(PIN_MARGIN))
	legend.grow_vertical = Control.GROW_DIRECTION_BEGIN
	return legend


## Keeps `control`'s minimum size at `with_legend` while the legend shows, `without`
## otherwise, live.
func link_size(control: Control, with_legend: Vector2, without: Vector2) -> void:
	_linked = control
	_size_on = with_legend
	_size_off = without
	_apply_link()


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	_apply_link()


func _apply_link() -> void:
	if _linked != null and is_instance_valid(_linked):
		_linked.custom_minimum_size = _size_on if Settings.map_legend else _size_off
