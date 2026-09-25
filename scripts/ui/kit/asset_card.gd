class_name AssetCard
extends Button
## A defence asset as a taped paper card (reference: DEFENSE LOADOUT): the asset's icon
## on a dark window, its name, integrity and how many sit in the Armory. Emits Button
## signals; the scene decides what a press means (deploy to the Site picked on the board).

var asset_id: StringName = &""
var display_name: String = ""
var integrity: int = 0
var count: int = 1
var _hot: bool = false


func _init(p_asset_id: StringName = &"", p_name: String = "", p_integrity: int = 0, p_count: int = 1) -> void:
	asset_id = p_asset_id
	display_name = p_name
	integrity = p_integrity
	count = p_count
	custom_minimum_size = Vector2(124, 150)
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(Vector2(4, 5), size), Palette.SHADOW)
	if _hot and not disabled:
		draw_rect(r.grow(4), Color(Palette.CELL_ACID, 0.45))
	draw_rect(r, Palette.NOTE_PAPER)
	draw_rect(r, Color(Palette.INK, 0.5), false, 1.0)
	draw_rect(Rect2(size.x * 0.35, -6, 40, 12), Palette.NOTE_TAPE)
	draw_string(Palette.mono(), Vector2(8, 20), display_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, 12, Palette.INK)
	var win := Rect2(10, 28, size.x - 20, 76)
	draw_rect(win, Palette.NIGHT_SKY)
	draw_circle(win.get_center(), 28, Color(AssetIcon.color_of(asset_id), 0.12))
	AssetIcon.draw_icon(self, win.get_center(), 26.0, asset_id, false)
	draw_string(Palette.mono(), Vector2(10, size.y - 14), "⬡ %d" % integrity, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Palette.INK)
	draw_string(Palette.marker(), Vector2(size.x - 38, size.y - 12), "x%d" % count, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Palette.CELL_PINK)
	if disabled:
		draw_rect(r, Color(0, 0, 0, 0.45))
