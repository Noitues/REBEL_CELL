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

## The print's width at text scale 1.0 (px; its height follows), the frame, the caption band
## (shares of the width), the tape's size (px at 1.0) and the vignette's strength.
const WIDTH := 172.0
const HEIGHT_SHARE := 1.2
const FRAME_SHARE := 0.05
const CAPTION_SHARE := 0.16
const TAPE := Vector2(70, 18)
const VIGNETTE := 0.35
## The drawn stand-in grid's cell (px at 1.0).
const GRID_CELL := 14.0


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
	rotation_degrees = tilt
	queue_redraw()


## The picture's rect inside the frame (local px).
func image_rect() -> Rect2:
	var m := size.x * FRAME_SHARE
	return Rect2(Vector2(m, m), Vector2(size.x - m * 2.0, size.x - m * 2.0))


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + Vector2(4, 7) * s, r.size), Palette.SHADOW)
	draw_rect(r, PaperInk.opaque(Palette.PAPER))
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
	var fs := UiTheme.font_px(UiTheme.BODY)
	var band_top := img.end.y
	var base := band_top + (size.y - band_top + f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	draw_string(f, Vector2(img.position.x, base), caption, HORIZONTAL_ALIGNMENT_CENTER, img.size.x, fs, PaperInk.text(Palette.END_BALLPOINT))
	# The tape over the top edge.
	var t := TAPE * s
	draw_set_transform(Vector2(size.x * 0.5, 0.0), deg_to_rad(4.0), Vector2.ONE)
	draw_rect(Rect2(-t * 0.5, t), PaperInk.opaque(Palette.TAPE, Palette.PAPER))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
