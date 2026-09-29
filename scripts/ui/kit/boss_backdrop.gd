class_name BossBackdrop
extends Control
## Art pass W3 (ART_BIBLE §7.2): the stand-in for a boss's hologram behind its wheel until
## W5's Hologram plugs in (WheelView.set_backdrop): the boss's drawn face (PortraitArt),
## large and faint, in its corporation's hue, with scan lines. View only; it takes no input.

## Scan lines: their spacing (px) and strength; the face's alpha (it never competes with the
## wheel in front of it: §1 readability).
const SCAN_STEP := 4.0
const SCAN_ALPHA := 0.35
const FACE_ALPHA := 0.22

var subject: Dictionary = {}
var hue: Color = Palette.NET_CYAN


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	modulate.a = FACE_ALPHA


## Shows `p_subject` (a PortraitArt subject) tinted by `p_hue`.
func show_subject(p_subject: Dictionary, p_hue: Color) -> void:
	subject = p_subject
	hue = p_hue
	queue_redraw()


func _draw() -> void:
	if subject.is_empty():
		return
	var r := Rect2(Vector2.ZERO, size)
	PortraitArt.draw(self, r, subject)
	var y := 0.0
	while y < size.y:
		draw_line(Vector2(0, y), Vector2(size.x, y), Color(Palette.NIGHT_SKY, SCAN_ALPHA), 1.0)
		y += SCAN_STEP
	draw_rect(r, Color(hue, SCAN_ALPHA), false, 2.0)
