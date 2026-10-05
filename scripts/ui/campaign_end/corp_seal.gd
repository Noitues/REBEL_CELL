class_name CorpSeal
extends RefCounted
## ART-11 4D: a corporation's seal (ART_BIBLE v2 §2.4 crests; round 20 lost20.py `seal`): a
## double ring with the house name round it and the crest inside (Halcyon's eye, Meridian's
## crane-A, Solace's helix, Orbital's ringed planet, DISPATCH's fist). Drawn on any CanvasItem
## (the ransom notice, the dossier's letterhead). Look only.

## The rings' widths and the name band's radius, as shares of the seal's radius.
const OUTER_LINE := 0.06
const INNER_LINE := 0.03
const INNER_RING := 0.68
const NAME_RING := 0.84
const NAME_SIZE := 0.17
## The crest's size as a share of the radius.
const CREST := 0.42
## Arc segments for drawn circles.
const SEGMENTS := 48


## Draws the seal of `corporation_id` centred on `c`, radius `r`, in `col`, with `house_name`
## (translated) round it.
static func draw_seal(ci: CanvasItem, c: Vector2, r: float, corporation_id: StringName, col: Color, house_name: String) -> void:
	ci.draw_arc(c, r * (1.0 - OUTER_LINE * 0.5), 0.0, TAU, SEGMENTS, col, maxf(1.0, r * OUTER_LINE), true)
	ci.draw_arc(c, r * INNER_RING, 0.0, TAU, SEGMENTS, col, maxf(1.0, r * INNER_LINE), true)
	# The name round the band, repeated to fill it, each letter on the tangent.
	var f := Palette.mono()
	var fs := maxi(1, roundi(r * NAME_SIZE))
	var words := ("  %s  *" % house_name).to_upper()
	var ring := words + words
	var n := ring.length()
	for i in n:
		var a := -PI * 0.5 + TAU * i / n
		var p := c + Vector2(cos(a), sin(a)) * r * NAME_RING
		ci.draw_set_transform(p, a + PI * 0.5, Vector2.ONE)
		ci.draw_char(f, Vector2(-fs * 0.25, fs * 0.35), ring[i], fs, col)
	ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	draw_crest(ci, c, r * CREST, corporation_id, col)


## Draws `corporation_id`'s crest centred on `c`, half size `r`.
static func draw_crest(ci: CanvasItem, c: Vector2, r: float, corporation_id: StringName, col: Color) -> void:
	var w := maxf(1.5, r * 0.14)
	match corporation_id:
		&"meridian":
			# The crane-A: an A frame with a jib and its hook.
			ci.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.75, r), c + Vector2(0, -r * 0.8), c + Vector2(r * 0.75, r)]), col, w, true)
			ci.draw_line(c + Vector2(-r * 0.4, r * 0.25), c + Vector2(r * 0.4, r * 0.25), col, w)
			ci.draw_line(c + Vector2(-r, -r * 0.8), c + Vector2(r, -r * 0.8), col, w)
			ci.draw_line(c + Vector2(r * 0.85, -r * 0.8), c + Vector2(r * 0.85, -r * 0.2), col, w * 0.6)
		&"solace":
			# The helix: two strands crossing, with rungs.
			var a := PackedVector2Array()
			var b := PackedVector2Array()
			for k in 13:
				var t := float(k) / 12.0
				var y := lerpf(-r, r, t)
				var x := sin(t * TAU) * r * 0.55
				a.append(c + Vector2(x, y))
				b.append(c + Vector2(-x, y))
				if k % 2 == 1:
					ci.draw_line(c + Vector2(x, y), c + Vector2(-x, y), col, w * 0.5)
			ci.draw_polyline(a, col, w, true)
			ci.draw_polyline(b, col, w, true)
		&"orbital":
			# The ringed planet.
			ci.draw_circle(c, r * 0.55, col)
			ci.draw_set_transform(c, -0.35, Vector2(1.0, 0.32))
			ci.draw_arc(Vector2.ZERO, r * 1.05, 0.0, TAU, SEGMENTS, col, w * 2.5, true)
			ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		&"rebel_cell":
			# The raised fist: four knuckles over a palm, the thumb tucked.
			var fw := r * 1.2
			for k in 4:
				ci.draw_rect(Rect2(c + Vector2(-fw * 0.5 + k * fw / 4.0, -r * 0.9), Vector2(fw / 4.0 - w * 0.4, r * 0.55)), col)
			ci.draw_rect(Rect2(c + Vector2(-fw * 0.5, -r * 0.3), Vector2(fw, r * 0.7)), col)
			ci.draw_rect(Rect2(c + Vector2(-fw * 0.3, r * 0.4), Vector2(fw * 0.6, r * 0.6)), col)
		_:
			# Halcyon's EYE: the watch-triangle under a halo.
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r * 0.55), c + Vector2(r * 0.85, r * 0.85), c + Vector2(-r * 0.85, r * 0.85)]), col)
			ci.draw_set_transform(c + Vector2(0, -r * 0.85), 0.0, Vector2(1.0, 0.35))
			ci.draw_arc(Vector2.ZERO, r * 0.6, 0.0, TAU, SEGMENTS, col, w * 2.0, true)
			ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
