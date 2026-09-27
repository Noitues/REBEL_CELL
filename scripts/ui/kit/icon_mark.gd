class_name IconMark
extends Control
## A StatIcon on a Button, or on its own beside a drawn control (H21 #13: menus and
## Skip / Leave buttons that carried their meaning in words only). `attach` gives the
## button an empty icon slot (a transparent 1x1 ImageTexture with a size override) so its
## text moves over, and the mark draws the icon in that slot at the button's font size (it
## follows the text scale); in a terminal menu the icon takes the chevron's place. The
## button keeps its text, key hint and tooltip; the icon kind is in the button's
## "icon_kind" meta (tests). Draw-only.
## H22 #14: `attach_map` puts a city map node icon on a button instead (drawn by the map's
## own painter, CityMapOverlay.draw_icon, so a route choice or a Grid run looks like its
## node on the map), with the map's tier pips after it (CityMapOverlay.draw_tier: the
## same difficulty cue as the map, legend and mini-map); the map kind is in the
## "map_icon_kind" meta and the tier in "tier_pips".

## Icon side relative to the button's font size.
const SIZE_FACTOR := 1.15
## A standalone mark's radius relative to its size.
const FILL := 0.45
## A map icon's radius relative to the slot (its silhouette overhangs a little).
const MAP_FILL := 0.4
## Gap between a map icon and its tier pips (share of the icon side).
const PIP_GAP := 0.25

var kind: StringName = &""
## Transparent = the button's font colour.
var color: Color = Color(0, 0, 0, 0)
## The button's empty icon slot: a transparent texture sized to the icon (a
## PlaceholderTexture2D would draw Godot's checkerboard).
var _slot: ImageTexture = null
## A city map node kind (CityMapOverlay.KIND_*) drawn instead of the StatIcon, its text
## (the tier "T2" in a hexagon) and the tier pips after it.
var map_kind: String = ""
var map_text: String = ""
var pips: int = 0


func _init(p_kind: StringName = &"", p_color: Color = Color(0, 0, 0, 0)) -> void:
	name = "IconMark"
	kind = p_kind
	color = p_color
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


## Puts icon `p_kind` on button `b` (replacing an earlier mark's kind); returns the mark.
static func attach(b: Button, p_kind: StringName, p_color: Color = Color(0, 0, 0, 0)) -> IconMark:
	b.set_meta(&"icon_kind", p_kind)
	var old := b.get_node_or_null(^"IconMark") as IconMark
	if old != null:
		old.kind = p_kind
		old.color = p_color
		old.queue_redraw()
		return old
	var m := IconMark.new(p_kind, p_color)
	var clear := Image.create_empty(1, 1, false, Image.FORMAT_RGBA8)
	clear.fill(Color(0, 0, 0, 0))
	m._slot = ImageTexture.create_from_image(clear)
	b.icon = m._slot
	b.add_child(m)
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m._fit()
	return m


## Puts the map's node icon `p_map_kind` (text `p_text`) and `p_pips` tier pips on button
## `b`, edged in `p_color` (H22 #14); returns the mark.
static func attach_map(b: Button, p_map_kind: String, p_color: Color, p_text: String = "", p_pips: int = 0) -> IconMark:
	var m := attach(b, IconMark.kind_of(b) if IconMark.kind_of(b) != &"" else &"map_node", p_color)
	m.map_kind = p_map_kind
	m.map_text = p_text
	m.pips = maxi(0, p_pips)
	b.set_meta(&"map_icon_kind", p_map_kind)
	b.set_meta(&"tier_pips", m.pips)
	m._fit()
	m.queue_redraw()
	return m


## The map node kind on button `b` ("" when it has none).
static func map_kind_of(b: Control) -> String:
	return String(b.get_meta(&"map_icon_kind", "")) if b != null else ""


## A mark of its own, `side` px square (beside a control that draws its own label).
static func standalone(p_kind: StringName, side: float, p_color: Color = Color(0, 0, 0, 0)) -> IconMark:
	var m := IconMark.new(p_kind, p_color)
	m.custom_minimum_size = Vector2(side, side)
	m.size = m.custom_minimum_size
	return m


## The icon kind on button `b` (&"" when it has none).
static func kind_of(b: Control) -> StringName:
	return StringName(b.get_meta(&"icon_kind", &"")) if b != null else &""


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		_fit()
		queue_redraw()
	elif what == NOTIFICATION_RESIZED:
		queue_redraw()


func _px() -> float:
	var b := get_parent() as Button
	if b == null:
		return minf(size.x, size.y)
	return roundf(b.get_theme_font_size(&"font_size") * SIZE_FACTOR)


func _fit() -> void:
	if _slot == null:
		return
	var px := _px()
	var want := Vector2(px + _pips_width(px), px)
	if Vector2(_slot.get_size()) != want:
		_slot.set_size_override(Vector2i(roundi(want.x), roundi(want.y)))
		var b := get_parent() as Button
		if b != null:
			b.update_minimum_size()


func _draw() -> void:
	var b := get_parent() as Button
	if b == null or _slot == null:
		var own := color if color.a > 0.0 else Palette.TERMINAL_TEXT
		StatIcon.draw(self, size * 0.5, minf(size.x, size.y) * FILL, kind, own)
		return
	var sb := b.get_theme_stylebox(&"normal")
	var left := sb.get_margin(SIDE_LEFT) if sb != null else 0.0
	var px := float(_slot.get_height())
	var col := color
	if col.a <= 0.0:
		col = b.get_theme_color(&"font_disabled_color" if b.disabled else &"font_color")
	if map_kind == "":
		StatIcon.draw(self, Vector2(left + px * 0.5, size.y * 0.5), px * FILL, kind, col)
		return
	CityMapOverlay.draw_icon(self, map_kind, Vector2(left + px * 0.5, size.y * 0.5), px * MAP_FILL, col, map_text)
	# The tier as the map draws it: lit pips of TIER_PIPS_MAX (the harder, the more lit).
	if pips > 0:
		var box := CityMapOverlay.tier_pips_size(_pip_scale(px))
		CityMapOverlay.draw_tier(self, Vector2(left + px + px * PIP_GAP + box.x * 0.5, size.y * 0.5), pips, col, _pip_scale(px))


## The tier pips' scale for an icon of side `px` (1.0 at the base button size).
func _pip_scale(px: float) -> float:
	return px / (UiTheme.BASE_SIZE * SIZE_FACTOR)


## Room the tier pips take after an icon of side `px`.
func _pips_width(px: float) -> float:
	return px * PIP_GAP + CityMapOverlay.tier_pips_size(_pip_scale(px)).x if pips > 0 else 0.0
