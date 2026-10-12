class_name CamFeed
extends Control
## ART-9 4A (ART_BIBLE v2 §4.11 "a CAM feed in the world style"; round 31 `event_screen`): the
## event's security camera on the city: the city behind the page (a BackBufferCopy the event page
## puts after the city) magnified and graded in the corp colour, scanlines, grain and a roll bar
## (`event_cam_noise`; still under reduce effects), a REC dot and its caption ("CAM 04  LOCKED
## WARD"). A DISPATCH event has no feed: VOICE ONLY // NO FEED with a red voice trace. View only.

const SHADER := preload("res://shaders/cam_feed.gdshader")
## Magnification of the city in the feed, the caption's lettering and the REC dot (px at 1).
const ZOOM := 2.4
const CAPTION_PX := 13
const REC_R := 5.0
const FRAME := 3.0
## The voice-only words' inset from the frame's foot (px).
const VOICE_PAD := 2.0

var caption: String = ""
var tint: Color = Palette.CORP_SOLACE
var voice_only: bool = false
var text_scale: float = 1.0
var _pic: ColorRect


func _init(p_caption: String = "", p_tint: Color = Palette.CORP_SOLACE, p_voice_only: bool = false, ts: float = 1.0) -> void:
	name = "CamFeed"
	caption = p_caption
	tint = p_tint
	voice_only = p_voice_only
	text_scale = ts
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if not voice_only:
		_pic = ColorRect.new()
		_pic.name = "Picture"
		_pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var m := ShaderMaterial.new()
		m.shader = SHADER
		m.set_shader_parameter(&"tint", tint)
		m.set_shader_parameter(&"speed", Motion.amplitude(&"event_cam_noise") if Motion.live(&"event_cam_noise") else 0.0)
		_pic.material = m
		add_child(_pic)
	item_rect_changed.connect(_fit)


## B5 (review D9: never an empty CAM box): the feed shows `tex` (the run's Site close-up: its still or its city's
## texture) through the CAM look, a ZOOM-magnified crop round PICTURE_AIM of it, instead of the screen copy.
func show_picture(tex: Texture2D) -> void:
	picture = tex
	_fit()


## The close-up the feed shows (null: the screen copy behind the page).
var picture: Texture2D = null
## Where the feed aims on a picture (UV; the close-ups frame their target a little above the middle).
const PICTURE_AIM := Vector2(0.5, 0.45)


func _fit() -> void:
	if _pic == null:
		return
	_pic.position = Vector2.ONE * FRAME
	_pic.size = size - Vector2.ONE * FRAME * 2.0
	var mat := _pic.material as ShaderMaterial
	mat.set_shader_parameter(&"use_picture", picture != null)
	if picture != null:
		mat.set_shader_parameter(&"picture_tex", picture)
		var aspect := (size.x / maxf(size.y, 1.0)) / maxf(float(picture.get_width()) / maxf(float(picture.get_height()), 1.0), 0.01)
		var w := clampf(1.0 / ZOOM * maxf(aspect, 1.0), 0.05, 1.0)
		var h := clampf(w / maxf(aspect, 0.01), 0.05, 1.0)
		mat.set_shader_parameter(&"src", Vector4(clampf(PICTURE_AIM.x - w * 0.5, 0.0, 1.0 - w), clampf(PICTURE_AIM.y - h * 0.5, 0.0, 1.0 - h), w, h))
		return
	# the city behind the feed, magnified about its centre (screen UV)
	var vp := get_viewport_rect().size if is_inside_tree() else Vector2(1280, 720)
	var r := get_global_rect()
	var src := Rect2(r.get_center() - r.size / ZOOM * 0.5, r.size / ZOOM)
	(_pic.material as ShaderMaterial).set_shader_parameter(&"src", Vector4(src.position.x / vp.x, src.position.y / vp.y, src.size.x / vp.x, src.size.y / vp.y))


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(r, Palette.NIGHT_SKY)
	draw_rect(r, Color(tint, 0.5), false, FRAME)
	var s := text_scale
	var f := Palette.mono()
	var fs := roundi(CAPTION_PX * s)
	if voice_only:
		# M14 12Q-WORDS (L48): the words stand whole inside the frame, on as many lines as the feed's
		# width needs (at 1.6 / 2.0 one line ran past it: "VOICE ONLY // NO FEE"), at the foot; the
		# red voice trace fills the room above them.
		var inner := r.grow(-FRAME * 2.0)
		var lines := voice_lines(tr("VOICE ONLY // NO FEED"), f, fs, inner.size.x)
		var line_h := UiTheme.line_px(f, fs)
		var top := inner.end.y - VOICE_PAD - line_h * lines.size()
		for i in lines.size():
			HighContrast.draw_text(self, f, Vector2(inner.position.x, top + line_h * i + ceilf(f.get_ascent(fs))), lines[i], HORIZONTAL_ALIGNMENT_CENTER, inner.size.x, fs, Palette.HARM)
		# a red voice trace across the black, in the room over the words
		var mid := (inner.position.y + top) * 0.5
		var amp := minf(r.size.y * 0.3, maxf(0.0, top - inner.position.y))
		var pts := PackedVector2Array()
		var steps := 48
		for i in steps + 1:
			var x := r.size.x * 0.1 + r.size.x * 0.8 * i / steps
			var h := float(absi(hash([i, 9])) % 100) / 100.0
			pts.append(Vector2(x, mid + (h - 0.5) * amp * sin(PI * i / steps)))
		draw_polyline(pts, Palette.HARM, 2.0, true)
		return


## `words` broken into lines at most `width` px wide in `font` at `fs`: one line when it fits,
## else at its " // " first ("VOICE ONLY //" / "NO FEED"), then at its spaces (a word wider
## than a line stands alone, whole).
static func voice_lines(words: String, font: Font, fs: int, width: float) -> PackedStringArray:
	if font.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= width:
		return PackedStringArray([words])
	var parts := words.split(VOICE_BREAK)
	if parts.size() > 1:
		var out := PackedStringArray()
		for i in parts.size():
			out.append_array(_wrap_words(parts[i] + (VOICE_BREAK if i < parts.size() - 1 else ""), font, fs, width))
		return out
	return _wrap_words(words, font, fs, width)


## The separator voice_lines breaks at first.
const VOICE_BREAK := " //"


## `words` broken at its spaces into lines at most `width` px wide (a longer word alone, whole).
static func _wrap_words(words: String, font: Font, fs: int, width: float) -> PackedStringArray:
	var out := PackedStringArray()
	var cur := ""
	for word in words.split(" ", false):
		var trial := word if cur == "" else cur + " " + word
		if cur != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
			out.append(cur)
			cur = word
		else:
			cur = trial
	if cur != "":
		out.append(cur)
	return out


## The REC dot and the caption over the picture (a child: it draws after the picture).
func _ready() -> void:
	_fit()
	if voice_only:
		return
	var cap := Control.new()
	cap.name = "Caption"
	cap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cap.set_anchors_preset(Control.PRESET_FULL_RECT)
	cap.draw.connect(func() -> void:
		var s := text_scale
		var f := Palette.mono()
		var fs := roundi(CAPTION_PX * s)
		var words := caption
		var tw := f.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		# B5 (Q14): on the narrow strip the caption keeps its camera (CAM 17), never runs past the feed.
		if tw + REC_R * 4.0 * s + 12.0 + 10.0 * s > size.x:
			words = caption.get_slice("  ", 0)
			tw = f.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var box := Rect2(Vector2(10, 10) * s, Vector2(tw + REC_R * 4.0 * s + 12.0, f.get_height(fs) + 6.0))
		cap.draw_rect(box, Color(Palette.NIGHT_SKY, 0.75))
		cap.draw_circle(box.position + Vector2(REC_R * 2.0 * s, box.size.y * 0.5), REC_R * s, Palette.HARM)
		HighContrast.draw_text(cap, f, box.position + Vector2(REC_R * 4.0 * s, 3.0 + f.get_ascent(fs)), words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.TEXT_HI))
	add_child(cap)
