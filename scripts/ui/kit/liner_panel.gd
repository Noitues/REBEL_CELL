class_name LinerPanel
extends PanelContainer
## B5 (integration review section c / f: "cards are stickers on a sheet, like loot"; round 44 B_menus
## `deck_viewer.png`, `stats.png`): a white sticker liner sheet (#F7F7F2) behind stickers that live on it: the loot
## sheet's own liner art (round 32 `reward.liner`, MainframeArt "liner": silicone paper with its faint repeat
## print), a kiss-cut slot outline under each sticker of `slots_host` (MainframeArt "slot_empty"; a slot whose
## sticker is peeled up shows its shiny empty outline), a small mono caption at its top left and a tag at its top
## right in the liner's grey print, and its drop shadow. Put the stickers in `body` (or point `slots_host` at the
## grid that holds them). A view only.

## The liner's margins (px at text scale 1.0): sides, top (under the caption), bottom; the slot's reach past its
## sticker (px) and the caption's type step.
const PAD := Vector2(18.0, 12.0)
const CAPTION_ROOM := 22.0
const SLOT_GROW := 5.0
const CAPTION_STEP := UiTheme.CAPTION
## The liner's print ink (round 44: the caption in a soft grey on the white liner) and the drop shadow's offset.
const PRINT_INK := Palette.LINER_PRINT
const SHADOW_OFFSET := Vector2(5, 8)

var caption: String = ""
var tag: String = ""
var body: VBoxContainer
## The container whose children each sit in a kiss-cut slot (default: `body`'s first grid / row, set by the host).
var slots_host: Container = null


func _init(p_caption: String = "", p_tag: String = "") -> void:
	caption = p_caption
	tag = p_tag
	name = "Liner"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var s := Settings.text_scale
	var sb := StyleBoxEmpty.new()
	sb.content_margin_left = PAD.x * s
	sb.content_margin_right = PAD.x * s
	sb.content_margin_top = (PAD.y + (CAPTION_ROOM if caption != "" or tag != "" else 0.0)) * s
	sb.content_margin_bottom = PAD.y * s
	add_theme_stylebox_override(&"panel", sb)
	body = VBoxContainer.new()
	body.name = "LinerBody"
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(body)
	sort_children.connect(queue_redraw)


## The kiss-cut slots (local rects): one under each shown child of `slots_host`.
func slot_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if slots_host == null or not is_instance_valid(slots_host):
		return out
	var inv := get_global_transform().affine_inverse()
	for c in slots_host.get_children():
		var cc := c as Control
		if cc != null and cc.visible:
			var g := cc.get_global_rect()
			out.append(Rect2(inv * g.position, g.size).grow(SLOT_GROW * Settings.text_scale))
	return out


func _process(_d: float) -> void:
	# The stickers move inside a scroll and on hover: the slots follow them.
	if slots_host != null and is_visible_in_tree():
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + SHADOW_OFFSET, r.size), Palette.SHADOW)
	var lt := MainframeArt.tex("liner")
	if lt != null:
		var src := Vector2(minf(r.size.x / MainframeArt.SCALE, lt.get_size().x), minf(r.size.y / MainframeArt.SCALE, lt.get_size().y))
		draw_texture_rect_region(lt, r, Rect2(Vector2.ZERO, src))
	else:
		draw_rect(r, Palette.LINER)
	var slot := MainframeArt.tex("slot_empty")
	var clip := r.grow(-2.0)
	for sl in slot_rects():
		if not clip.encloses(sl):
			continue  # scrolled out of the sheet's view
		if slot != null:
			draw_texture_rect(slot, sl, false)
		else:
			draw_rect(sl, Color(PRINT_INK, 0.55), false, 1.5)
	var mono := Palette.mono()
	var px := UiTheme.font_px(CAPTION_STEP)
	var s := Settings.text_scale
	var base := (PAD.y + CAPTION_ROOM * 0.5) * s + (mono.get_ascent(px) - mono.get_descent(px)) * 0.5
	if caption != "":
		draw_string(mono, Vector2(PAD.x * s, base), caption, HORIZONTAL_ALIGNMENT_LEFT, r.size.x * 0.6, px, PRINT_INK)
	if tag != "":
		draw_string(mono, Vector2(r.size.x * 0.6, base), tag, HORIZONTAL_ALIGNMENT_RIGHT, r.size.x * 0.4 - PAD.x * s, px, PRINT_INK)
