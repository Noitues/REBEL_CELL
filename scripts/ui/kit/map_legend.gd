class_name MapLegend
extends TerminalWindow
## The map key for the city map views (Settings.map_legend): what the highlight colours,
## marks, line styles and badge glyphs mean. Every status row has its own glyph, so the
## key never relies on colour alone (GDD 9.6): claimed Sites carry a spray ring, Seized
## ones a cross. Follows the setting live, and can resize a linked control with it (the
## HQ Grid's Site list takes the legend's room back when it is off).

const ROWS := [["○", "#FF3DA8", "claimed (yours): spray ring"], ["■", "#5CE1FF", "cleared"], ["■", "", "corporate"], ["✕", "#FFD24D", "seized: crossed out"],
	["━", "#FF3DA8", "your network link"], ["- -", "", "threat route"], ["◈", "#F2EEE4", "exploit"], ["❄", "#F2EEE4", "heat reduction"],
	["✦", "#F2EEE4", "boss"], ["⌂", "#F2EEE4", "home / CORE"]]
## Row width, and the compact variant's font size (legends pinned over a map).
const ROW_WIDTH := 200.0
const COMPACT_FONT := 12
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
	visible = Settings.map_legend
	Settings.changed.connect(_on_settings_changed)


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
