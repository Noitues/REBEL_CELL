class_name OnAirTicker
extends Control
## ART-10 4C: the ON AIR ticker along the foot of the title (round 33 `title_screen.jpg`): a
## cyan ON AIR block and a terminal band whose words crawl left (`on_air_ticker`: amplitude
## = px a second). Under reduce effects, headless or with the entry off the words hold
## still. Words are given translated. View only.

const MOTION := &"on_air_ticker"
const STEP := UiTheme.BODY
## The band's height as a multiple of its font size, and the ON AIR block's width share.
const HEIGHT_SHARE := 2.0
const BLOCK_SHARE := 0.11
const ON_AIR_ART := "res://assets/ui/menus/kit/on_air.png"
const SEPARATOR := "   +++   "

var words: PackedStringArray = []
var _offset: float = 0.0


## The baked art this view draws, held while it lives (a texture loaded only inside _draw
## was freed before the frame drew it: a white box).
var _held: Dictionary = {}


func _init(p_words: PackedStringArray = []) -> void:
	words = p_words
	name = "OnAirTicker"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip_contents = true


func _get_minimum_size() -> Vector2:
	return Vector2(0, ceilf(Chrome.px(STEP) * HEIGHT_SHARE))


func _process(delta: float) -> void:
	if not Motion.live(MOTION):
		if _offset != 0.0:
			_offset = 0.0
			queue_redraw()
		return
	_offset += delta * Motion.amplitude(MOTION)
	queue_redraw()


func _line() -> String:
	return SEPARATOR + SEPARATOR.join(words)


func _draw() -> void:
	var px := Chrome.px(STEP)
	var f := Chrome.caps_font(STEP)
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(r, Color(Palette.NET_BG_OUTER, 0.92))
	draw_line(Vector2(0, 0.5), Vector2(size.x, 0.5), Color(Palette.NET_CYAN, 0.6), 1.0)
	# The concept's ON AIR block (round 33 title.py ticker(), baked), at the band's height.
	var tex := Chrome.held(_held, ON_AIR_ART)
	var block := Rect2(Vector2.ZERO, Vector2(tex.get_size().x * size.y / tex.get_size().y if tex != null else size.x * BLOCK_SHARE, size.y))
	var base := (size.y + f.get_ascent(px) - f.get_descent(px)) * 0.5
	var text := _line()
	var w := maxf(1.0, f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	var x := block.end.x + 12.0 - fmod(_offset, w)
	while x < size.x:
		draw_string(f, Vector2(x, base), text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.NET_CYAN)
		x += w
	if tex != null:
		draw_texture_rect(tex, block, false)
	else:
		draw_rect(block, Palette.NET_CYAN)
		draw_string(f, Vector2(block.position.x, base), tr("ON AIR"), HORIZONTAL_ALIGNMENT_CENTER, block.size.x, px, Palette.GLYPH_INK)
