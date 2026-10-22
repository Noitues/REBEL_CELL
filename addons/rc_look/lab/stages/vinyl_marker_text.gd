class_name RcLookVinylMarkerText
extends Control
## LOOK-TOOLBOX module 13 (lab): a word drawn in a chrome fill marker colour, the way VerbSticker draws its lettering
## for rc_vinyl_chrome (or the old chrome/vinyl_sticker shader). View only.

const FONT_PX := 56
## Baseline and left edge of the word inside the control (px).
const ORIGIN := Vector2(10.0, 54.0)

var text: String = "SEND IT"
## The marker colour: magenta (1, 0, 1) for the gradient, green (0, 1, b / 8) for the glitch fill (band b).
var marker: Color = Color(1, 0, 1)
## Extra copies drawn sideways (px) in their own marker bands, for a glitch burst: [{ "marker": Color, "dx": float }].
var extra: Array[Dictionary] = []


func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, ORIGIN, text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_PX, marker)
	for e in extra:
		draw_string(font, ORIGIN + Vector2(float(e["dx"]), 0.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_PX, e["marker"])
