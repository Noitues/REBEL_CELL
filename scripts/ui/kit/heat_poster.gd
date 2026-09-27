class_name HeatPoster
extends Control
## Ransom-note Heat (STYLE_GUIDE 4): cut-out letters in mixed fonts on paper strips and
## the value in Anton. As a wanted poster in HQ (`poster = true`) it gains a border and a
## "WANTED" header. Heat bands follow the thresholds 25/50/75 (GDD 9.4).

## Colour of the number at high Heat: the campaign's corporation (set by the HQ).
var hot_color: Color = Palette.CORP_SOLACE
var heat: int = 0
var heat_max: int = 100
var poster: bool = false
var band: int = 0
## Threshold marks on the bar (the config's MAJOR Heat levels, passed by the scenes).
var marks: Array[int] = [25, 50, 75]
## Who the wanted poster shows (a PortraitArt subject; the HQ names the crew's lead).
var wanted: Dictionary = PortraitArt.operative_subject(&"operative")
## The mugshot's side on the wanted poster (px).
const MUG_SIZE := 44.0


## The Heat block's top on a wanted poster (under the header and mugshot), the band
## word's baseline below that block's top, its lettering, and the paper kept under it (px).
const POSTER_BLOCK_TOP := 84.0
const BAND_BASELINE := 68.0
const BAND_FONT := 13
const BAND_PAD := 6.0
## The Heat band words, by band.
const BAND_WORDS: Array[String] = ["cool", "noticed", "flagged", "hunted"]


func _init(p_poster: bool = false) -> void:
	poster = p_poster
	# H23 S6: the poster is tall enough for its band word ("cool" hung under the paper,
	# hidden by the Pirate Radio note).
	custom_minimum_size = Vector2(170, 96 if not p_poster else ceilf(band_label_rect().end.y + BAND_PAD))


## Where the band word ("cool", "hunted") is drawn (local px).
func band_label_rect() -> Rect2:
	var top := POSTER_BLOCK_TOP if poster else 0.0
	var f := Palette.marker()
	var word := BAND_WORDS[mini(band, 3)]
	var base := top + BAND_BASELINE
	return Rect2(8, base - f.get_ascent(BAND_FONT), f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT).x, f.get_height(BAND_FONT))
	# PASS: the scene's tooltip (what the thresholds do) shows on hover.
	mouse_filter = Control.MOUSE_FILTER_PASS


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text, "Heat") if for_text != "" else null


func set_heat(value: int, maximum: int, thresholds: Array[int] = [] as Array[int]) -> void:
	heat = value
	heat_max = maximum
	if not thresholds.is_empty():
		marks = thresholds
	band = 0
	for t in thresholds:
		if heat >= t:
			band += 1
	queue_redraw()


func _draw() -> void:
	var y := 0.0
	if poster:
		draw_rect(Rect2(Vector2.ZERO, size), Palette.PAPER_ALT)
		draw_rect(Rect2(Vector2.ZERO, size), Palette.INK, false, 3.0)
		draw_string(Palette.display(), Vector2(10, 30), "WANTED", HORIZONTAL_ALIGNMENT_LEFT, size.x - 20, 26, Palette.INK)
		PortraitArt.draw(self, Rect2(size.x * 0.5 - MUG_SIZE * 0.5, 38, MUG_SIZE, MUG_SIZE), wanted)
		y = POSTER_BLOCK_TOP
	var letters := ["H", "E", "A", "T"]
	var fonts := [Palette.display(), Palette.marker(), Palette.mono(), Palette.display()]
	var x := 8.0
	for i in letters.size():
		var strip := Rect2(x, y + 4 + (i % 2) * 4, 24, 28)
		draw_rect(strip, Palette.PAPER if i % 2 == 0 else Palette.CELL_PINK)
		draw_rect(strip, Palette.INK, false, 1.0)
		draw_string(fonts[i], strip.position + Vector2(5, 22), letters[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Palette.INK)
		x += 28
	draw_string(Palette.display(), Vector2(x + 6, y + 30), "%d" % heat, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.CELL_PINK if band < 2 else hot_color)
	draw_string(Palette.mono(), Vector2(x + 6, y + 44), "/%d" % heat_max, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.INK if poster else Palette.PAPER)
	var bar := Rect2(8, y + 44, size.x - 16, 8)
	draw_rect(bar, Color(Palette.INK, 0.3) if poster else Color(Palette.PAPER, 0.15))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * clampf(float(heat) / maxf(1.0, heat_max), 0.0, 1.0), bar.size.y)), Palette.CELL_PINK)
	for t in marks:
		var tx: float = bar.position.x + bar.size.x * int(t) / float(heat_max)
		draw_line(Vector2(tx, bar.position.y - 3), Vector2(tx, bar.end.y + 3), Palette.INK if poster else Palette.PAPER, 1.0)
	draw_string(Palette.marker(), Vector2(8, y + BAND_BASELINE), BAND_WORDS[mini(band, 3)], HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT, Palette.INK if poster else Palette.CELL_ACID)
