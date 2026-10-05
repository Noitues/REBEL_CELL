class_name DefenceCardFace
extends Control
## ART-11 4D: the face of a defence card sticker on the glass (ref round 20 `campaign_lost.jpg`
## tray: a dark card, the asset's accent bar and line icon, its name in Anton), drawn inside a
## 1B VinylSticker object (Shape.RECT) whose white die-cut body frames it. Look only.

var asset_id: StringName = &""
var title: String = ""

## A card's size at text scale 1.0 (px) and its accent bar (px).
const SIZE := Vector2(76, 92)
const BAR := 3.0
const PAD := 4.0


func _init(p_asset: StringName = &"", p_title: String = "") -> void:
	asset_id = p_asset
	title = p_title
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	var col := AssetIcon.color_of(asset_id)
	draw_rect(r, Palette.NIGHT_SKY)
	draw_rect(Rect2(Vector2.ZERO, Vector2(size.x, BAR * s)), col)
	AssetIcon.draw_icon(self, Vector2(size.x * 0.5, size.y * 0.38), size.x * 0.22, asset_id, false)
	var f := Palette.display()
	var room := size.x - PAD * 2.0 * s
	var fs := UiTheme.font_px(UiTheme.LABEL)
	# The name steps down to the caption floor to fit the card.
	while fs > UiTheme.font_px(UiTheme.CAPTION) and f.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	draw_string(f, Vector2(PAD * s, size.y - PAD * 2.0 * s), title, HORIZONTAL_ALIGNMENT_LEFT, room, fs, Palette.TEXT_HI)
