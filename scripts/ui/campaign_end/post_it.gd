class_name PostIt
extends Control
## ART-11 4D: an auditor's post-it on the dossier (ART_BIBLE v2 §1.2: "auditor's blue ballpoint
## post-its"; round 21 dossier21.py `postit`): a square note, its glued band a shade darker,
## its foot lifting off the page, the auditor's words in blue ballpoint. It lands with the
## dossier's note motion. Look only.

var words: String = ""
var paper: Color = Palette.END_NOTE_YELLOW
var tilt: float = 0.0

## The note's side at text scale 1.0 (px), the glued band's share, the inner pad (px at 1.0),
## the darkening of the band and of the lifted foot.
const SIDE := Vector2(150, 136)
const BAND_SHARE := 0.16
const PAD := 10.0
const BAND_DARK := 0.07
const FOOT_DARK := 0.12
## The ballpoint's size (type step) and its line height.
const HAND_STEP := UiTheme.LABEL
const LINE_SHARE := 1.12


func _init(p_words: String = "", p_paper: Color = Palette.END_NOTE_YELLOW, p_tilt: float = 0.0) -> void:
	words = p_words
	paper = p_paper
	tilt = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	refit()


## Measures the note at the text size now: its side grows with the words it must hold.
func refit() -> void:
	var s := Settings.text_scale
	var f := EndFaces.ballpoint()
	var fs := UiTheme.font_px(HAND_STEP)
	var w := SIDE.x * s
	# Never narrower than its longest word (a word is never broken between letters).
	for word in words.split(" ", false):
		w = maxf(w, f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + PAD * 2.0 * s + 2.0)
	var lines := HeatPoster.wrap_words(f, words, fs, w - PAD * 2.0 * s)
	var h := maxf(SIDE.y * s, SIDE.y * s * BAND_SHARE + PAD * 2.0 * s + lines.size() * f.get_height(fs) * LINE_SHARE)
	custom_minimum_size = Vector2(w, h)
	size = custom_minimum_size
	pivot_offset = size * 0.5
	rotation_degrees = tilt
	queue_redraw()


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + Vector2(4, 7) * s, r.size), Palette.SHADOW)
	var band := size.y * BAND_SHARE
	# The paper darkens toward its lifted foot.
	var steps := 8
	for i in steps:
		var y0 := band + (size.y - band) * i / steps
		draw_rect(Rect2(0, y0, size.x, (size.y - band) / steps + 1.0), PaperInk.opaque(paper.darkened(FOOT_DARK * i / steps)))
	draw_rect(Rect2(0, 0, size.x, band), PaperInk.opaque(paper.darkened(BAND_DARK)))
	var f := EndFaces.ballpoint()
	var fs := UiTheme.font_px(HAND_STEP)
	var lines := HeatPoster.wrap_words(f, words, fs, size.x - PAD * 2.0 * s + 1.0)
	var y := band + PAD * s + f.get_ascent(fs)
	for line in lines:
		draw_string(f, Vector2(PAD * s, y), line, HORIZONTAL_ALIGNMENT_LEFT, size.x - PAD * 2.0 * s, fs, PaperInk.text(Palette.END_BALLPOINT))
		y += f.get_height(fs) * LINE_SHARE
	if PaperInk.on():
		draw_rect(r, PaperInk.edge(Palette.INK), false, PaperInk.edge_width(1.0))
