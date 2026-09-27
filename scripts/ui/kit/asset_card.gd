class_name AssetCard
extends Button
## A defence asset as a taped paper card (reference: DEFENSE LOADOUT): the asset's icon
## on a dark window, its name, integrity and how many sit in the Armory. Emits Button
## signals; the scene decides what a press means (deploy to the Site picked on the board).
## H22 #9: the numbers sit on a dark plate in light lettering (dark grey on beige was
## unreadable, more so under the disabled shade), the lettering follows the text size and
## the card's size is `card_size()` (the icon window gives way first at big text).

var asset_id: StringName = &""
var display_name: String = ""
var integrity: int = 0
var count: int = 1
var _hot: bool = false

## A card at text scale 1.0 (px), and how much of the text scale its size follows.
const BASE_SIZE := Vector2(110, 120)
const SIZE_FOLLOW := 0.5
## Lettering at text scale 1.0: name, integrity, count.
const NAME_SIZE := 12
const NUMBER_SIZE := 14
const COUNT_SIZE := 17
## Padding (px), the icon window's least height (px) and the icon's share of it.
const PAD := 8.0
const WINDOW_MIN_H := 40.0
const ICON_SHARE := 0.34
## The disabled shade (lighter than before: the numbers stay readable under it).
const DISABLED_SHADE := Color(0, 0, 0, 0.3)


func _init(p_asset_id: StringName = &"", p_name: String = "", p_integrity: int = 0, p_count: int = 1) -> void:
	asset_id = p_asset_id
	display_name = p_name
	integrity = p_integrity
	count = p_count
	custom_minimum_size = card_size()
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


## The card's size at the current text scale.
static func card_size() -> Vector2:
	return BASE_SIZE * (1.0 + (Settings.text_scale - 1.0) * SIZE_FOLLOW)


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(Vector2(4, 5), size), Palette.SHADOW)
	if _hot and not disabled:
		draw_rect(r.grow(4), Color(Palette.CELL_ACID, 0.45))
	draw_rect(r, Palette.NOTE_PAPER)
	draw_rect(r, Color(Palette.INK, 0.5), false, 1.0)
	draw_rect(Rect2(size.x * 0.35, -6, 40, 12), Palette.NOTE_TAPE)
	var mono := Palette.mono()
	var ns := roundi(NAME_SIZE * s)
	draw_string(mono, Vector2(PAD, PAD + mono.get_ascent(ns)), display_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, size.x - PAD * 2.0, ns, Palette.INK)
	# The numbers' plate at the foot: integrity (hexagon) and the count in the Armory.
	var num := roundi(NUMBER_SIZE * s)
	var cs := roundi(COUNT_SIZE * s)
	var plate_h := maxf(mono.get_height(num), Palette.marker().get_height(cs)) + PAD * 0.5
	var plate := Rect2(0, size.y - plate_h, size.x, plate_h)
	var top := PAD + mono.get_height(ns) + PAD * 0.5
	var win := Rect2(PAD, top, size.x - PAD * 2.0, maxf(WINDOW_MIN_H, plate.position.y - top - PAD * 0.5))
	draw_rect(win, Palette.NIGHT_SKY)
	var icon_r := minf(win.size.x, win.size.y) * ICON_SHARE
	draw_circle(win.get_center(), icon_r * 1.08, Color(AssetIcon.color_of(asset_id), 0.12))
	AssetIcon.draw_icon(self, win.get_center(), icon_r, asset_id, false)
	if disabled:
		draw_rect(Rect2(0, 0, size.x, plate.position.y), DISABLED_SHADE)
	draw_rect(plate, Palette.INK)
	var base_y := plate.get_center().y + mono.get_ascent(num) * 0.5 - mono.get_descent(num) * 0.25
	draw_string(mono, Vector2(PAD, base_y), "⬡ %d" % integrity, HORIZONTAL_ALIGNMENT_LEFT, -1, num, Palette.PAPER)
	var ct := "x%d" % count
	var cw := Palette.marker().get_string_size(ct, HORIZONTAL_ALIGNMENT_LEFT, -1, cs).x
	draw_string(Palette.marker(), Vector2(size.x - PAD - cw, base_y), ct, HORIZONTAL_ALIGNMENT_LEFT, -1, cs, Palette.CELL_PINK)
