class_name DossierPhoto
extends Control
## ART-11 4D: a print in the audit dossier (ART_BIBLE v2 §1.2 "polaroids"; round 21
## dossier21.py `polaroid`, `tape`): a white frame, the picture printed a little warm and
## faded with a flash vignette, the auditor's ballpoint caption under it, taped to the folder.
## The picture is a crop of the screen at the end (the network as it stood), an operative's
## portrait (PortraitArt), or, with neither (headless), the night grid drawn in the
## corporation's hue. Look only.

var caption: String = ""
var tilt: float = 0.0
var picture: Texture2D = null
## An operative's portrait (PortraitArt subject) when there is no picture.
var subject: Dictionary = {}
var tint: Color = Palette.NET_CYAN
## The stock, loaded once and held (ART-12 12p: an unheld `load()` decodes it at every draw).
var _stock_tex: Texture2D = null

## The print's width at text scale 1.0 (px; its height follows), the frame, the caption band
## (shares of the width), the tape's size (px at 1.0) and the vignette's strength.
const WIDTH := 132.0
const HEIGHT_SHARE := 1.2
const FRAME_SHARE := 0.05
const CAPTION_SHARE := 0.16
const TAPE := Vector2(70, 18)
const VIGNETTE := 0.35
## The drawn stand-in grid's cell (px at 1.0).
const GRID_CELL := 14.0
## M14 asset parity: the print's white stock is round 21's own `sheet` (the polaroid's grain),
## exported by `tools/art_pipeline/parity/export_campaign_end.py`.
const STOCK_ART := "res://assets/campaign_end/print_stock.png"


func _init(p_caption: String = "", p_tilt: float = 0.0) -> void:
	caption = p_caption
	tilt = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	refit()


func refit() -> void:
	var w := WIDTH * minf(Settings.text_scale, 1.3)
	custom_minimum_size = Vector2(w, w * HEIGHT_SHARE)
	size = custom_minimum_size
	pivot_offset = size * 0.5
	queue_redraw()


## The caption as drawn: one line stepped down to the caption floor, or (a long name) its
## words wrapped at the floor. {"lines", "fs"}.
func caption_layout() -> Dictionary:
	var f := EndFaces.ballpoint()
	var room := size.x * (1.0 - FRAME_SHARE * 2.0)
	var fs := UiTheme.font_px(UiTheme.BODY)
	var floor_px := UiTheme.font_px(UiTheme.CAPTION)
	while fs > floor_px and f.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	if f.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room:
		return {"lines": PackedStringArray([caption]), "fs": fs}
	return {"lines": HeatPoster.wrap_words(f, caption, floor_px, room), "fs": floor_px}


## The picture's rect inside the frame (local px): square, smaller when the caption takes
## more than one line.
func image_rect() -> Rect2:
	var m := size.x * FRAME_SHARE
	var lay := caption_layout()
	var line_h := EndFaces.ballpoint().get_height(int(lay["fs"]))
	var band := maxf(size.y - size.x, line_h * (lay["lines"] as PackedStringArray).size() + m)
	var side := minf(size.x - m * 2.0, size.y - m - band)
	return Rect2(Vector2((size.x - side) * 0.5, m), Vector2(side, side))


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + Vector2(4, 7) * s, r.size), Palette.SHADOW)
	if _stock_tex == null:
		_stock_tex = load(STOCK_ART) as Texture2D
	draw_texture_rect(_stock_tex, r, false)
	var img := image_rect()
	if picture != null:
		draw_texture_rect(picture, img, false, Palette.PAPER.lerp(Palette.TEXT_HI, 0.5))
	elif not subject.is_empty():
		PortraitArt.draw(self, img, subject)
	else:
		draw_rect(img, Palette.NIGHT_BLOCK)
		var cell := GRID_CELL * s
		var x := img.position.x
		while x < img.end.x:
			draw_line(Vector2(x, img.position.y), Vector2(x, img.end.y), Color(tint, 0.3), 1.0)
			x += cell
		var y := img.position.y
		while y < img.end.y:
			draw_line(Vector2(img.position.x, y), Vector2(img.end.x, y), Color(tint, 0.3), 1.0)
			y += cell
	# The print's warm fade and the flash's vignette.
	draw_rect(img, Color(Palette.END_MANILA, 0.12))
	for i in 4:
		draw_rect(img.grow(-i * 2.0), Color(Palette.INK, VIGNETTE * 0.12 * (4 - i) / 4.0), false, 2.0)
	var f := EndFaces.ballpoint()
	var lay := caption_layout()
	var fs: int = lay["fs"]
	var lines: PackedStringArray = lay["lines"]
	var m := size.x * FRAME_SHARE
	var line_h := f.get_height(fs)
	var y := img.end.y + (size.y - img.end.y - line_h * lines.size()) * 0.5 + f.get_ascent(fs)
	for line in lines:
		draw_string(f, Vector2(m, y), line, HORIZONTAL_ALIGNMENT_CENTER, size.x - m * 2.0, fs, PaperInk.text(Palette.END_BALLPOINT))
		y += line_h
	# The tape over the top edge.
	var t := TAPE * s
	draw_set_transform(Vector2(size.x * 0.5, 0.0), deg_to_rad(4.0), Vector2.ONE)
	draw_rect(Rect2(-t * 0.5, t), PaperInk.opaque(Palette.TAPE, Palette.PAPER))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
