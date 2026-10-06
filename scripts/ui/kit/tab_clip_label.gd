class_name TabClipLabel
extends Control
## B5 (round 44 B_menus `campaign_slots.png`, review D21 / section c: the case files are the Cell's own, so the
## folder's label is the Cell's terminal tab clip, never a corp letterhead): a small CRT label holder clipped over a
## folder's tab: the kit's CRT glass (CrtTerminalPanel) with the Cell's cyan edge, the words in Share Tech Mono
## caps ("SLOT 1 // CELL-01"), and two metal clip tabs over its top edge (`campaign_slots.tab_clip`). A view only.

## The words' type step, the label's padding (px at text scale 1.0), and the clip tabs' size and inset (px).
const STEP := UiTheme.CAPTION
const PAD := Vector2(8.0, 3.0)
const CLIP := Vector2(4.0, 6.0)
const CLIP_INSET := 2.0
## The clip tabs' metal and its rim (round 44 tab_clip: (150, 160, 176) and (40, 44, 54)).
const CLIP_METAL := Palette.CLIP_METAL
const CLIP_RIM := Palette.CLIP_RIM

var text: String = ""
var _glass: CrtTerminalPanel = null


func _init(p_text: String = "") -> void:
	text = p_text
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glass = HudSkin.crt_backing(self)
	_glass.text_scope = self


func _ready() -> void:
	_fit()
	Settings.changed.connect(_fit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_fit):
		Settings.changed.disconnect(_fit)


## The words' font px now.
func font_px() -> int:
	return UiTheme.font_px(STEP)


func _fit() -> void:
	var w := Palette.mono().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x
	var s := Settings.text_scale
	custom_minimum_size = Vector2(ceilf(w + PAD.x * 2.0 * s), ceilf(Palette.mono().get_height(font_px()) + PAD.y * 2.0 * s))
	size = custom_minimum_size
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	HudSkin.draw_terminal_edge(self, r, PaletteSkins.chrome(Palette.NET_CYAN))
	for x in [CLIP_INSET, size.x - CLIP_INSET - CLIP.x]:
		var clip := Rect2(Vector2(x, -CLIP.y * 0.6), CLIP)
		draw_rect(clip, CLIP_METAL)
		draw_rect(clip, CLIP_RIM, false, 1.0)
	var f := Palette.mono()
	var px := font_px()
	var base := (size.y + f.get_ascent(px) - f.get_descent(px)) * 0.5
	draw_string(f, Vector2(PAD.x * Settings.text_scale, base), text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, PaletteSkins.chrome(Palette.NET_CYAN))
