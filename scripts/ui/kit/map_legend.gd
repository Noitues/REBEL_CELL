class_name MapLegend
extends TerminalWindow
## The map key for the city map views (Settings.map_legend): what the highlight colours,
## marks, line styles and badge glyphs mean. Every status row has its own glyph, so the
## key never relies on colour alone (GDD 9.6): claimed Sites carry a spray ring, Seized
## ones a cross. Follows the setting live, and can resize a linked control with it (the
## HQ Grid's Site list takes the legend's room back when it is off).
##
## H22: every row's text, glyph and icon follow Settings.text_scale (rebuilt live when it
## changes); rows are plain Labels so the legend reports its full minimum size at once
## (a legend pinned over a map grows upward from its corner and never runs off it); the
## tier row shows the map's difficulty pips.

const ROWS := [["○", "#FF3DA8", "claimed (yours): spray ring"], ["■", "#5CE1FF", "cleared"], ["■", "", "corporate"], ["✕", "#FFD24D", "seized: crossed out"],
	["━", "#FF3DA8", "your network link"], ["- -", "", "threat route"]]
## The node icons (H21 #14), drawn by CityMapOverlay.draw_icon exactly as on the map:
## [kind, text shown in the icon, meaning].
const ICON_ROWS := [[CityMapOverlay.KIND_EXPLOIT, "", "exploit"], [CityMapOverlay.KIND_HEAT, "", "heat reduction"],
	[CityMapOverlay.KIND_BOSS, "", "boss"], [CityMapOverlay.KIND_HOME, "", "CORE (your home)"], [CityMapOverlay.KIND_TIER, "T2", "Site tier: more lit pips, harder"]]
## The tier row's example tier (its icon text above is "T2").
const TIER_EXAMPLE := 2
## Legend width, glyph column width, the full and compact variants' font sizes (legends
## pinned over a map are compact), and the title's; all at text scale 1.0. The full
## variant sits in a screen's column: it keeps WIDTH and its text wraps (at least
## MIN_TEXT_WIDTH per line); the compact one grows with the text scale unwrapped.
const WIDTH := 230.0
const MIN_TEXT_WIDTH := 110.0
const GLYPH_WIDTH := 22.0
const FULL_FONT := 15
const COMPACT_FONT := 12
const TITLE_FONT := 15
## Icon swatch side (px) at text scale 1.0, and the icon's radius as a share of it.
const ICON_SWATCH := 22.0
const ICON_SHARE := 0.36
const ICON_SWATCH_GAP := 8
## Margin (px) of a legend pinned to a map area's bottom-left corner.
const PIN_MARGIN := 10.0

## H23 S4: each ROWS row's key (the ICON_ROWS rows are keyed by their kind).
const ROW_KEYS: Array[String] = ["claimed", "cleared", "corporate", "seized", "link", "threat"]

var compact: bool = false
## H23 S4: the rows shown, by key (ROW_KEYS, icon kinds); empty = every row. A map key
## lists what its map shows (the raid legend took a quarter of the screen).
var only: Array[String] = []
var _corp_hex: String = ""
var _built_scale: float = -1.0
var _linked: Control = null
var _size_on: Vector2 = Vector2.ZERO
var _size_off: Vector2 = Vector2.ZERO


func _init(corporation_id: StringName = &"", p_compact: bool = false) -> void:
	super("MAP LEGEND")
	name = "MapLegend"
	compact = p_compact
	_corp_hex = Palette.corp_color(corporation_id).to_html(false)
	_build()
	visible = Settings.map_legend
	Settings.changed.connect(_on_settings_changed)


## The rows' font size now (px): the variant's size at the current text scale.
func font_size() -> int:
	return roundi((COMPACT_FONT if compact else FULL_FONT) * Settings.text_scale)


## (Re)builds every row at the current text scale.
func _build() -> void:
	_built_scale = Settings.text_scale
	var s := Settings.text_scale
	custom_minimum_size.x = WIDTH * s if compact else WIDTH
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.add_theme_font_size_override("font_size", roundi(TITLE_FONT * s))
	for child in body.get_children():
		body.remove_child(child)
		child.free()
	var fs := font_size()
	for i in ROWS.size():
		var r: Array = ROWS[i]
		if not only.is_empty() and not only.has(ROW_KEYS[i]):
			continue
		var row := HBoxContainer.new()
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_theme_constant_override("separation", roundi(ICON_SWATCH_GAP * s))
		var glyph := Label.new()
		glyph.text = r[0]
		glyph.custom_minimum_size.x = GLYPH_WIDTH * s
		glyph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		glyph.add_theme_color_override("font_color", Color.html(r[1] if r[1] != "" else _corp_hex))
		glyph.add_theme_font_size_override("font_size", fs)
		glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(glyph)
		row.add_child(_text(r[2], fs))
		body.add_child(row)
	for r in ICON_ROWS:
		if not only.is_empty() and not only.has(String(r[0])):
			continue
		body.add_child(_icon_row(r[0], r[1], r[2], fs))
	update_minimum_size()


func _text(text: String, fs: int) -> Label:
	var l := Label.new()
	l.text = text
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", fs)
	if not compact:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		l.custom_minimum_size.x = MIN_TEXT_WIDTH
	return l


## A key row with the map's own icon of `kind` (named "Icon_<kind>"); the tier row adds
## the map's difficulty pips under its icon.
func _icon_row(kind: String, text: String, meaning: String, fs: int) -> HBoxContainer:
	var s := Settings.text_scale
	var row := HBoxContainer.new()
	row.name = "Icon_%s" % kind
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(ICON_SWATCH_GAP * s))
	var side := ICON_SWATCH * s
	var tier := kind == CityMapOverlay.KIND_TIER
	var pips := CityMapOverlay.tier_pips_size(s)
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(maxf(side, pips.x), side + (pips.y + CityMapOverlay.TIER_PIP_GAP * s if tier else 0.0))
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	swatch.draw.connect(func() -> void:
		var c := Vector2(swatch.size.x * 0.5, side * 0.5)
		var r := side * ICON_SHARE
		CityMapOverlay.draw_icon(swatch, kind, c, r, Palette.PAPER, text)
		if tier:
			CityMapOverlay.draw_tier(swatch, Vector2(c.x, side + CityMapOverlay.TIER_PIP_GAP * s + pips.y * 0.5), TIER_EXAMPLE, Palette.PAPER, s))
	row.add_child(swatch)
	var l := _text(meaning, fs)
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


## A compact legend pinned to `area`'s bottom-left corner (the raid maps: the map is the
## city behind the panels, `area` the open part of the screen over it). It grows up and
## right from that corner with its minimum size (bigger text makes it taller).
static func pin_to(area: Control, corporation_id: StringName) -> MapLegend:
	var legend := MapLegend.new(corporation_id, true)
	legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	area.add_child(legend)
	legend.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT, Control.PRESET_MODE_MINSIZE, int(PIN_MARGIN))
	legend.grow_vertical = Control.GROW_DIRECTION_BEGIN
	legend.minimum_size_changed.connect(legend._repin)
	return legend


## Shows only the rows keyed in `keys` (ROW_KEYS and icon kinds; [] = every row).
func show_only(keys: Array[String]) -> MapLegend:
	only = keys.duplicate()
	_build()
	return self


## The row keys a city map graph shows (H23 S4): marks, the Sites' statuses (from the
## campaign grid), link and threat route edges, and the node icon kinds.
static func keys_of(graph: Dictionary, grid: GridState) -> Array[String]:
	var out: Array[String] = []
	for n in graph.get("nodes", []):
		match String(n.get("mark", "")):
			CityMapOverlay.MARK_SPRAY:
				_add_key(out, "claimed")
			CityMapOverlay.MARK_CROSS:
				_add_key(out, "seized")
		if grid != null:
			match grid.status_of(n["id"]):
				GridState.SiteStatus.CLEARED:
					_add_key(out, "cleared")
				GridState.SiteStatus.CORPORATE:
					_add_key(out, "corporate")
		var kind := String(n.get("kind", ""))
		if kind != "":
			_add_key(out, kind)
	for e in graph.get("edges", []):
		if bool(e.get("dashed", false)):
			_add_key(out, "threat")
		elif bool(e.get("flow", false)):
			_add_key(out, "link")
	return out


static func _add_key(out: Array[String], key: String) -> void:
	if not out.has(key):
		out.append(key)


## Keeps a pinned legend's bottom-left corner in place when its minimum size changes.
func _repin() -> void:
	if get_parent() is Container:
		return
	var ms := get_combined_minimum_size()
	offset_right = offset_left + ms.x
	offset_top = offset_bottom - ms.y


## Keeps `control`'s minimum size at `with_legend` while the legend shows, `without`
## otherwise, live.
func link_size(control: Control, with_legend: Vector2, without: Vector2) -> void:
	_linked = control
	_size_on = with_legend
	_size_off = without
	_apply_link()


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	if not is_equal_approx(_built_scale, Settings.text_scale):
		_build()
	_apply_link()


func _apply_link() -> void:
	if _linked != null and is_instance_valid(_linked):
		_linked.custom_minimum_size = _size_on if Settings.map_legend else _size_off
