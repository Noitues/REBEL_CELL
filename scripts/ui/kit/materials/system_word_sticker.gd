class_name SystemWordSticker
extends Control
## "Word over a system word" (ART-1 1B; ART_BIBLE v2 §1.3; round 22 `send_it_sticker.png`,
## round 3 kit sheet "primary verb (holo) over system word"): a verb sticker slapped at an
## angle over the washed-out system word in the terminal font. SEND IT over `EXECUTE` (with
## `> turn_resolve.exe [SPACE]`), BREACH over `CONNECT`. The sticker is the action; the
## system word is the machine underneath and stays readable (washed: 45 % alpha, scanlined).
## A view: the button behaviour stays the caller's (StickerButton / its own input).

const SCAN_PX := 3.0
## The system word's alpha (round 22 says 30 %; the round 3 kit sheet's EXECUTE reads stronger: 45 %).
const WORD_ALPHA := 0.45
## Where the sticker's centre sits down the panel (share of its height: on its bottom edge,
## so the system word above reads) and its tilt.
const STICKER_DROP := 1.08
const STICKER_TILT_DEG := -5.0
const CORNER_PX := 16.0

## The system word (the machine underneath).
@export var system_word: String = "EXECUTE":
	set(v):
		system_word = v
		queue_redraw()
## The hint line under it (`> turn_resolve.exe [SPACE]`); empty for none.
@export var hint: String = "":
	set(v):
		hint = v
		queue_redraw()
@export var word_step: int = UiTheme.DISPLAY

var sticker: VinylSticker = null


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	sticker = VinylSticker.new()
	sticker.name = "Sticker"
	add_child(sticker)


func _ready() -> void:
	resized.connect(_layout)
	_layout()


## Sets the verb sticker's word and fill.
func set_verb(word: String, fill: VinylSticker.Fill = VinylSticker.Fill.PINK) -> void:
	sticker.text = word
	sticker.fill = fill
	_layout()


func _layout() -> void:
	sticker.tilt_deg = STICKER_TILT_DEG
	sticker.place_center(Vector2(size.x * 0.5, size.y * STICKER_DROP))
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.CRT_GLASS_TOP
	sb.border_color = Palette.NET_CYAN.darkened(0.45)
	sb.set_border_width_all(2)
	draw_style_box(sb, r)
	draw_colored_polygon(PackedVector2Array([Vector2.ZERO, Vector2(CORNER_PX, 0), Vector2(0, CORNER_PX)]), Palette.NET_CYAN.darkened(0.3))
	var font := Palette.mono()
	var px := UiTheme.font_px(word_step)
	var col := Palette.TERMINAL_TEXT
	col.a = WORD_ALPHA
	var w := font.get_string_size(system_word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var base := Vector2((size.x - w) * 0.5, font.get_ascent(px) + UiTheme.SP_S)
	draw_string(font, base, system_word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	if hint != "":
		var hp := UiTheme.font_px(UiTheme.CAPTION)
		var hw := font.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, hp).x
		draw_string(font, Vector2((size.x - hw) * 0.5, size.y - UiTheme.SP_S), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, hp, col)
	# the static scanlines over the washed word
	var dark := Palette.CRT_GLASS_BOTTOM
	dark.a = WORD_ALPHA
	var y := 0.0
	while y < size.y:
		draw_rect(Rect2(0, y + SCAN_PX * 0.5, size.x, SCAN_PX * 0.5), dark)
		y += SCAN_PX
