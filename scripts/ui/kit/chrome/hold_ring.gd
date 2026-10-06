class_name HoldRing
extends Control
## The lime ring that fills round a sticker while the pad / keyboard holds its verb (round 33
## `abandon_dialog`, "BURN IT hold A": a lime arc round the focused sticker, from the top,
## clockwise). Drawn (the concept draws it as a plain arc over the baked sticker; no art to
## export). View only: AbandonDialog sets `progress`.

## The ring's stroke (px at text scale 1.0) and how far it sits outside the sticker's box
## (share of the box: the sticker's box already holds the die-cut halo's room, so the ring
## rides on it and clears the caption under it).
const STROKE := 5.0
const OUTSET := 0.0
## The arc's segments for a full turn (a smooth ellipse at 2.0).
const SEGMENTS := 64

## 0 = empty, 1 = full (the confirm lands).
var progress: float = 0.0:
	set(v):
		progress = clampf(v, 0.0, 1.0)
		queue_redraw()


func _init() -> void:
	name = "HoldRing"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


func _draw() -> void:
	if progress <= 0.0:
		return
	var c := size * 0.5
	var r := size * (0.5 + OUTSET)
	var n := maxi(2, ceili(SEGMENTS * progress))
	var pts := PackedVector2Array()
	for i in n + 1:
		# From the top (-90 degrees), clockwise.
		var a := -PI * 0.5 + TAU * progress * float(i) / float(n)
		pts.append(c + Vector2(cos(a) * r.x, sin(a) * r.y))
	draw_polyline(pts, Palette.FOCUS, STROKE * Settings.text_scale, true)
