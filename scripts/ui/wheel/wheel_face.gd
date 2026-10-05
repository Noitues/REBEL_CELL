class_name WheelFace
extends RefCounted
## The wheel stack's drawn parts over the disc (ART-2 2A; ART_BIBLE v2 3.2-3.8, 3.16, 3.21; ported
## from the round 41 recipes: slicelib icon_block, frames.blade / telemetry / banner, d4corp, the
## combat_wheel HP arc). Static helpers the WheelView calls from its `_draw` in the round 41 z-order:
## read blocks (7), badges (8), the rail (9), blades (13). Geometry is in master units (the slice
## rim R_OUT = 360) scaled by `k` px per master unit; angles are degrees clockwise from the top.

const R_OUT := 360.0
const R_IN := 130.0
const RCH0 := 368.0
const RCH1 := 404.0
const R1 := 414.0
## The boss threat ring's depth beyond the bezel (3.2).
const THREAT_DEPTH := 30.0
## The read block's centre radius (slicelib: R_IN + 0.6 of the band) and its glyph box.
const READ_R := R_IN + 0.6 * (R_OUT - R_IN)
const GLYPH_MASTER := 72.0
## The value's font size against the glyph box (Anton, 3.6) and the gap between them.
const NUMBER_SHARE := 1.16
const BLOCK_GAP := 0.06
## A block with no value (NULL, specials) shows its glyph larger.
const BARE_SCALE := 1.3
## The read plate's padding round the block (master units).
const PLATE_PAD := Vector2(14.0, 12.0)
## Blade (frames.blade, d4): tip inside the rim, shoulder and top over the bezel, value window.
const BLADE_TIP := R_OUT - 24.0
const BLADE_SHOULDER := 18.0
const BLADE_TOP := 96.0
const BLADE_W_SHOULDER := 34.0
const BLADE_W_TOP := 50.0
const BLADE_NOTCH := 16.0
const WINDOW_IN := 30.0
const WINDOW_OUT := 18.0
const WINDOW_HALF := 36.0
const BLADE_INK := 3.5
## At r = 60 the blade is scaled x1.6 (3.2).
const LOD_RADIUS := 60.0
const LOD_BLADE := 1.6
## Rail: +-50 degrees over the needle, a +-8 degree dark gap round each needle (3.2, round 39).
const RAIL_HALF := 50.0
const NEEDLE_GAP := 8.0
const RAIL_TEXT := 14.0
## The HP arc (combat_wheel.draw_hp): 30 segments from 130 to 230 degrees, 16..40 beyond the frame.
const HP_SEGS := 30
const HP_A0 := 130.0
const HP_A1 := 230.0
const HP_R0 := 6.0
const HP_R1 := 26.0
## The corner badge (3.8): outer clockwise corner of the slice, its size and the tag under it.
const BADGE_R := 326.0
const BADGE_SIZE := 44.0
const BADGE_INSET := 9.0
## The boss banner (frames.banner): height, title and sub sizes, the mount notch.
const BANNER_H := 86.0
const BANNER_TITLE := 46.0
const BANNER_SUB := 15.0
const BANNER_PAD := 70.0
## Crest lugs on the threat ring (frames.armour_lugs): hexagons at 90 and 270 degrees.
const LUG_R := 40.0


## A point at radius `r` (master) and angle `deg` round `center`.
static func at(center: Vector2, k: float, r: float, deg: float) -> Vector2:
	var a := deg_to_rad(deg)
	return center + Vector2(sin(a), -cos(a)) * r * k


## A point on the axis at `deg`, `r` out and `v` across (clockwise positive), master units.
static func axis(center: Vector2, k: float, r: float, v: float, deg: float) -> Vector2:
	var a := deg_to_rad(deg)
	return center + (Vector2(sin(a), -cos(a)) * r + Vector2(cos(a), sin(a)) * v) * k


## The read block's size in master units for a value text (the plate's radii are half of it plus
## PLATE_PAD).
static func block_size(value: String) -> Vector2:
	var gs := GLYPH_MASTER * (BARE_SCALE if value == "" else 1.0)
	if value == "":
		return Vector2(gs, gs)
	var fs := gs * NUMBER_SHARE
	var w := Palette.display().get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(1, roundi(fs))).x
	return Vector2(gs + gs * BLOCK_GAP + w, maxf(gs, fs * 0.8))


## The read plate radii (master units) under a block showing `value`.
static func plate_radii(value: String) -> Vector2:
	return block_size(value) * 0.5 + PLATE_PAD


## The read block (3.4, 3.6): white glyph + value on the slice at `deg`, always upright.
static func read_block(ci: CanvasItem, center: Vector2, k: float, deg: float, glyph: StringName, value: String, alpha: float = 1.0) -> void:
	var c := at(center, k, READ_R, deg)
	var bare := value == ""
	var gs := GLYPH_MASTER * k * (BARE_SCALE if bare else 1.0)
	var white := Color(Palette.TEXT_HI, alpha)
	var ink := Color(Palette.INK, alpha)
	if bare:
		WheelGlyphs.draw(ci, glyph, c, gs, white, ink)
		return
	var fs := maxi(1, roundi(gs * NUMBER_SHARE))
	var font := Palette.display()
	var tw := font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var gap := gs * BLOCK_GAP
	var x0 := c.x - (gs + gap + tw) * 0.5
	WheelGlyphs.draw(ci, glyph, Vector2(x0 + gs * 0.5, c.y), gs, white, ink)
	var base := Vector2(x0 + gs + gap, c.y + cap_height(font, fs) * 0.5)
	var ow := maxi(1, roundi(gs * WheelGlyphs.OUTLINE_SHARE * 2.0))
	ci.draw_string_outline(font, base, value, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, ow, ink)
	ci.draw_string(font, base, value, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, white)


## The height of a capital in `font` at `fs` (centring numbers on a point).
static func cap_height(font: Font, fs: int) -> float:
	return font.get_ascent(fs) * 0.78


## A needle blade (3.2, frames.blade): cream notched blade rooted in the bezel, its tip biting the
## slice, a dark value window with the live value, accent chevrons near the tip, an index tab on a
## multi-needle wheel. `rt` is the frame's outer radius (R1, or the threat ring's on a boss).
## `crown`: the boss's crowned blade in the corp colour.
static func blade(ci: CanvasItem, center: Vector2, k: float, deg: float, rt: float, accent: Color, body: Color,
		value: String, glyph: StringName, program: Color, index: int = 0, crown: bool = false, scale: float = 1.0, alpha: float = 1.0) -> void:
	var s := scale
	var tip := BLADE_TIP
	var sh := rt + BLADE_SHOULDER * s
	var top := rt + BLADE_TOP * s
	var wsh := BLADE_W_SHOULDER * s
	var wtop := BLADE_W_TOP * s
	var q := func(r: float, v: float) -> Vector2: return axis(center, k, r, v, deg)
	var ink := Color(Palette.INK, alpha)
	var pts := PackedVector2Array([q.call(tip, 0.0), q.call(sh, wsh), q.call(top - 12.0 * s, wtop), q.call(top, wtop - 12.0),
		q.call(top, BLADE_NOTCH), q.call(top - BLADE_NOTCH * s, 0.0), q.call(top, -BLADE_NOTCH), q.call(top, -wtop + 12.0),
		q.call(top - 12.0 * s, -wtop), q.call(sh, -wsh)])
	if crown:
		for side in [1.0, -1.0]:
			var horn := PackedVector2Array([q.call(top - 30.0 * s, (wtop - 2.0) * side), q.call(top + 26.0 * s, (wtop + 18.0) * side), q.call(top - 4.0 * s, (wtop - 18.0) * side)])
			ci.draw_colored_polygon(horn, Color(body.lightened(0.2), alpha))
			_outline(ci, horn, ink, maxf(1.0, 3.0 * k))
	# soft glow in the accent, then the body with its ink outline
	ci.draw_colored_polygon(_grow(pts, center, 6.0 * k), Color(accent, 0.28 * alpha))
	ci.draw_colored_polygon(pts, Color(body, alpha))
	# bevel: the left half catches the key light, the right falls into shade
	var hl := PackedVector2Array([q.call(tip + 10.0 * s, 0.0), q.call(sh, -wsh + 6.0), q.call(top - 14.0 * s, -wtop + 7.0), q.call(top - 6.0 * s, -wtop + 14.0), q.call(top - 6.0 * s, -2.0)])
	ci.draw_colored_polygon(hl, Color(body.lightened(0.08), alpha))
	var dk := PackedVector2Array([q.call(tip + 10.0 * s, 0.0), q.call(sh, wsh - 6.0), q.call(top - 14.0 * s, wtop - 7.0), q.call(top - 6.0 * s, wtop - 14.0), q.call(top - 6.0 * s, 2.0)])
	ci.draw_colored_polygon(dk, Color(body.darkened(0.18), alpha))
	_outline(ci, pts, ink, maxf(1.0, BLADE_INK * k))
	for c in 2:
		var r := sh - 14.0 * s - c * 13.0 * s
		var w := (r - tip) / (sh - tip) * wsh * 0.62
		ci.draw_polyline(PackedVector2Array([q.call(r + 8.0 * s, -w), q.call(r, 0.0), q.call(r + 8.0 * s, w)]), Color(accent if not crown else Palette.INK, alpha), maxf(1.0, 4.0 * k * s))
	# the value window
	var w0 := rt + WINDOW_IN * s
	var w1 := top - WINDOW_OUT * s
	var ww := WINDOW_HALF * s
	var frame := PackedVector2Array([q.call(w0 - 4.0 * s, -ww - 5.0), q.call(w0 - 4.0 * s, ww + 5.0), q.call(w1 + 4.0 * s, ww + 5.0), q.call(w1 + 4.0 * s, -ww - 5.0)])
	ci.draw_colored_polygon(frame, ink)
	var win := PackedVector2Array([q.call(w0, -ww), q.call(w0, ww), q.call(w1, ww), q.call(w1, -ww)])
	ci.draw_colored_polygon(win, Color(Palette.NIGHT_SKY, alpha))
	_outline(ci, win, Color(accent, alpha), maxf(1.0, 2.4 * k))
	var mid: Vector2 = q.call((w0 + w1) * 0.5, 0.0)
	var hgt := (w1 - w0) * k
	if value != "":
		var fs := maxi(1, roundi(hgt * 0.92))
		var font := Palette.display()
		var base := Vector2(mid.x, mid.y + cap_height(font, fs) * 0.5)
		var tw := font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		ci.draw_string_outline(font, base - Vector2(tw * 0.5, 0.0), value, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(3.0 * k)), ink)
		ci.draw_string(font, base - Vector2(tw * 0.5, 0.0), value, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.TEXT_HI, alpha))
	else:
		WheelGlyphs.draw(ci, glyph, mid, hgt * 0.8, Color(Palette.TEXT_HI, alpha), ink)
	# the program colour pip strip on the window's lower edge
	ci.draw_colored_polygon(PackedVector2Array([q.call(w0 + 2.0 * s, -ww + 6.0), q.call(w0 + 2.0 * s, ww - 6.0), q.call(w0 + 7.0 * s, ww - 6.0), q.call(w0 + 7.0 * s, -ww + 6.0)]), Color(program, alpha))
	if index > 0:
		# the index tab (1, 2, 3) on a multi-needle wheel, beside the shoulder
		var tab: Vector2 = q.call(sh + 2.0, wsh + 16.0)
		var tr_ := 11.0 * k * s
		ci.draw_circle(tab, tr_ + maxf(1.0, 2.0 * k), ink)
		ci.draw_circle(tab, tr_, Color(accent, alpha))
		var nf := maxi(1, roundi(tr_ * 1.5))
		var t := str(index)
		var font2 := Palette.display()
		var tw2 := font2.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, nf).x
		ci.draw_string(font2, Vector2(tab.x - tw2 * 0.5, tab.y + cap_height(font2, nf) * 0.5), t, HORIZONTAL_ALIGNMENT_LEFT, -1, nf, ink)


## The rail over a needle (3.2): the channel tinted the program colour with brackets, its text
## (`OVERFLOW 12 // CRIT // PERFECT //`) static, split round every needle in `needles`.
static func rail(ci: CanvasItem, center: Vector2, k: float, deg: float, needles: Array[float], text: String, tint: Color, word_tint: Color, alpha: float = 1.0) -> void:
	var r_text := (RCH0 + RCH1) * 0.5
	var spans := _rail_spans(deg, needles)
	for sp in spans:
		var a0: float = sp.x
		var a1: float = sp.y
		ci.draw_colored_polygon(arc_band(center, k, RCH0 + 2.0, RCH1 - 2.0, a0, a1), Color(tint.darkened(0.58), alpha))
	for a in [deg - RAIL_HALF, deg + RAIL_HALF]:
		ci.draw_line(at(center, k, RCH0 - 1.0, a), at(center, k, RCH1 + 1.0, a), Color(tint, alpha), maxf(1.0, 3.0 * k))
	var fs := roundi(RAIL_TEXT * k)
	if fs < MIN_TEXT_PX:
		for sp in spans:
			_dashes(ci, center, k, r_text, sp.x, sp.y, Color(word_tint, alpha))
		return
	for sp in spans:
		_text_arc(ci, center, k, r_text, sp.x + 1.0, sp.y - 1.0, text, Palette.mono(), fs, Color(word_tint, alpha))


## Below this font size (px) ring text becomes a dotted data strip (frames.telemetry lod).
const MIN_TEXT_PX := 4


## The rail's arcs round needle `deg`: +-RAIL_HALF less a +-NEEDLE_GAP gap at every needle.
static func _rail_spans(deg: float, needles: Array[float]) -> Array[Vector2]:
	var out: Array[Vector2] = [Vector2(deg - RAIL_HALF, deg + RAIL_HALF)]
	for n in needles:
		var nd := deg + wrapf(n - deg, -180.0, 180.0)
		var next: Array[Vector2] = []
		for sp in out:
			if nd + NEEDLE_GAP <= sp.x or nd - NEEDLE_GAP >= sp.y:
				next.append(sp)
				continue
			if nd - NEEDLE_GAP > sp.x:
				next.append(Vector2(sp.x, nd - NEEDLE_GAP))
			if nd + NEEDLE_GAP < sp.y:
				next.append(Vector2(nd + NEEDLE_GAP, sp.y))
		out = next
	return out


## Text written along a ring (combat_wheel.text_ring): each character upright to the ring, from
## `a0` clockwise to `a1`, the text repeating to fill.
static func _text_arc(ci: CanvasItem, center: Vector2, k: float, r: float, a0: float, a1: float, text: String, font: Font, fs: int, col: Color) -> void:
	if text == "":
		return
	var rr := r * k
	var a := a0
	var i := 0
	var guard := 0
	while a < a1 and guard < 512:
		guard += 1
		var ch := text[i % text.length()]
		var adv := font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var step := rad_to_deg(adv / maxf(rr, 1.0))
		if a + step > a1:
			break
		if ch != " ":
			var am := a + step * 0.5
			var p := at(center, k, r, am)
			ci.draw_set_transform(p, deg_to_rad(am), Vector2.ONE)
			ci.draw_char(font, Vector2(-adv * 0.5, fs * 0.35), ch, fs, col)
		a += step
		i += 1
	ci.draw_set_transform(Vector2.ZERO)


static func _dashes(ci: CanvasItem, center: Vector2, k: float, r: float, a0: float, a1: float, col: Color) -> void:
	var a := a0
	while a + 2.0 < a1:
		ci.draw_line(at(center, k, r, a), at(center, k, r, a + 2.0), col, maxf(1.0, 4.0 * k))
		a += 3.0


## A ring band between radii r0..r1 (master) and angles a0..a1 (degrees clockwise from the top).
static func arc_band(center: Vector2, k: float, r0: float, r1: float, a0: float, a1: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var steps := maxi(3, ceili(absf(a1 - a0) / 3.0))
	for s in steps + 1:
		pts.append(at(center, k, r1, lerpf(a0, a1, float(s) / steps)))
	for s in steps + 1:
		pts.append(at(center, k, r0, lerpf(a1, a0, float(s) / steps)))
	return pts


## The HP arc (3.2): thick segments under the wheel, lit to `frac` (HP now), `after` (this turn's
## result) and `lag` (the white trail of a loss); boss phase pips at `phases` (fractions, 3.16).
static func hp_arc(ci: CanvasItem, center: Vector2, k: float, rt: float, frac: float, after: float, lag: float,
		on: Color, loss: Color, gain: Color, phases: Array[float], phase_now: int, alpha: float = 1.0) -> void:
	var r0 := rt + HP_R0
	var r1 := rt + HP_R1
	var off := Color(on.darkened(0.78), 0.85 * alpha)
	for i in HP_SEGS:
		# HP fills from the left end (230) towards the right (130), as the recipe's arc.
		var aa := HP_A1 - (HP_A1 - HP_A0) * (i + 0.12) / HP_SEGS
		var ab := HP_A1 - (HP_A1 - HP_A0) * (i + 0.88) / HP_SEGS
		var f := (i + 0.5) / HP_SEGS
		var col := off
		if f < minf(frac, after):
			col = on
		elif f < frac:
			col = loss
		elif f < after:
			col = gain
		elif f < lag:
			col = Palette.PAPER
		ci.draw_colored_polygon(arc_band(center, k, r0, r1, ab, aa), Color(col, col.a * alpha))
	for p in phases.size():
		var a := HP_A1 - (HP_A1 - HP_A0) * phases[p]
		var lit := p + 2 <= phase_now
		ci.draw_line(at(center, k, r0 - 4.0, a), at(center, k, r1 + 4.0, a), Color(Palette.RESIST_GOLD, alpha), maxf(1.0, 3.0 * k))
		var c := at(center, k, r1 + 13.0, a)
		var r := 9.0 * k
		var dia := PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0)])
		ci.draw_colored_polygon(dia, Color(Palette.RESIST_GOLD if lit else Palette.RESIST_GOLD.darkened(0.5), alpha))
		_outline(ci, dia, Color(Palette.INK, alpha), maxf(1.0, k * 2.0))


## The corner badge of a slice's state (3.8): the status glyph on its shape (circle helps,
## diamond hurts) in the outer clockwise corner, and the x1.5 / x0.5 tag under it.
static func badge(ci: CanvasItem, center: Vector2, k: float, deg: float, span: float, status: int, helps: bool, tag: String, alpha: float = 1.0) -> void:
	var a := deg + span * 0.5 - BADGE_INSET
	var c := at(center, k, BADGE_R, a)
	var r := BADGE_SIZE * 0.5 * k
	var fill := Color(Palette.NIGHT_SKY, 0.92 * alpha)
	var edge := Color(Palette.GAIN if helps else Palette.HARM, alpha)
	if helps:
		ci.draw_circle(c, r, fill)
		ci.draw_arc(c, r, 0.0, TAU, 24, edge, maxf(1.0, 2.5 * k), true)
	else:
		var dia := PackedVector2Array([c + Vector2(0, -r * 1.15), c + Vector2(r * 1.15, 0), c + Vector2(0, r * 1.15), c + Vector2(-r * 1.15, 0)])
		ci.draw_colored_polygon(dia, fill)
		_outline(ci, dia, edge, maxf(1.0, 2.5 * k))
	WheelGlyphs.draw(ci, WheelGlyphs.status_id(status), c, r * 1.25, Color(Palette.TEXT_HI, alpha), Color(Palette.INK, alpha))
	if tag != "":
		var fs := maxi(MIN_TEXT_PX, roundi(r * 0.95))
		var font := Palette.display()
		var tw := font.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var tp := at(center, k, BADGE_R - BADGE_SIZE * 0.95, a)
		var box := Rect2(tp - Vector2(tw * 0.5 + 3.0, fs * 0.55), Vector2(tw + 6.0, fs * 1.1))
		ci.draw_rect(box, Color(Palette.INK, 0.92 * alpha))
		ci.draw_rect(box, Color(Palette.RESIST_GOLD, alpha), false, 1.0)
		ci.draw_string(font, Vector2(box.position.x + 3.0, tp.y + cap_height(font, fs) * 0.5), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.RESIST_GOLD, alpha))


## The boss nameplate banner as the blade's mount (frames.banner, mount): dark plate with the corp
## edge, hazard chamfers, the title and the corp / rank / phase line. `bottom` is its lower edge
## (local y).
static func banner(ci: CanvasItem, center_x: float, bottom: float, k: float, title: String, sub: String, accent: Color, alpha: float = 1.0) -> Rect2:
	var font := Palette.display()
	var tf := maxi(1, roundi(BANNER_TITLE * k))
	var sf := maxi(MIN_TEXT_PX, roundi(BANNER_SUB * k))
	var tw := maxf(font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, tf).x, Palette.mono().get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, sf).x) + BANNER_PAD * k
	var y1 := bottom
	var y0 := y1 - BANNER_H * k
	var x0 := center_x - tw * 0.5
	var x1 := center_x + tw * 0.5
	var notch := 46.0 * k
	var poly := PackedVector2Array([Vector2(x0 - 20.0 * k, y0), Vector2(x1 + 20.0 * k, y0), Vector2(x1, y1), Vector2(center_x + 60.0 * k, y1),
		Vector2(center_x + notch, y1 + 16.0 * k), Vector2(center_x - notch, y1 + 16.0 * k), Vector2(center_x - 60.0 * k, y1), Vector2(x0, y1)])
	ci.draw_colored_polygon(_grow(poly, Vector2(center_x, (y0 + y1) * 0.5), 5.0 * k), Color(accent, 0.3 * alpha))
	ci.draw_colored_polygon(poly, Color(Palette.NIGHT_SKY, 0.96 * alpha))
	_outline(ci, poly, Color(accent, alpha), maxf(1.0, 3.0 * k))
	for side: float in [-1.0, 1.0]:
		var xe := center_x + side * (tw * 0.5 + 4.0 * k)
		for c in 4:
			var yk := y0 + (12.0 + c * 17.0) * k
			ci.draw_colored_polygon(PackedVector2Array([Vector2(xe, yk), Vector2(xe + side * 10.0 * k, yk), Vector2(xe + side * 4.0 * k, yk + 10.0 * k), Vector2(xe - side * 6.0 * k, yk + 10.0 * k)]), Color(accent, alpha))
	ci.draw_line(Vector2(x0 + 14.0 * k, y1 - 9.0 * k), Vector2(x1 - 14.0 * k, y1 - 9.0 * k), Color(accent, alpha), maxf(1.0, 2.0 * k))
	var ttw := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, tf).x
	var tb := Vector2(center_x - ttw * 0.5, y0 + 6.0 * k + font.get_ascent(tf) * 0.92)
	ci.draw_string_outline(font, tb, title, HORIZONTAL_ALIGNMENT_LEFT, -1, tf, maxi(1, roundi(4.0 * k)), Color(Palette.INK, alpha))
	ci.draw_string(font, tb, title, HORIZONTAL_ALIGNMENT_LEFT, -1, tf, Color(Palette.TEXT_HI, alpha))
	var sw := Palette.mono().get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, sf).x
	ci.draw_string(Palette.mono(), Vector2(center_x - sw * 0.5, y1 - 14.0 * k), sub, HORIZONTAL_ALIGNMENT_LEFT, -1, sf, Color(accent, alpha))
	return Rect2(x0 - 20.0 * k, y0, tw + 40.0 * k, y1 - y0 + 16.0 * k)


## Crest lugs (3.16): corp-crest hexagons on the threat ring at 90 and 270 degrees.
static func crest_lugs(ci: CanvasItem, center: Vector2, k: float, rt: float, accent: Color, crest: StringName, alpha: float = 1.0) -> void:
	for a in [90.0, 270.0]:
		var c := at(center, k, rt + 8.0, a)
		var r := LUG_R * k
		var hexp := PackedVector2Array()
		for j in 6:
			hexp.append(c + Vector2(cos(deg_to_rad(60.0 * j)), sin(deg_to_rad(60.0 * j))) * r)
		ci.draw_colored_polygon(_grow(hexp, c, 4.0 * k), Color(accent, 0.3 * alpha))
		ci.draw_colored_polygon(hexp, Color(Palette.NIGHT_SKY, alpha))
		_outline(ci, hexp, Color(accent, alpha), maxf(1.0, 3.0 * k))
		WheelGlyphs.draw(ci, crest, c, r * 1.1, Color(accent, alpha), Color(Palette.INK, alpha))


static func _outline(ci: CanvasItem, pts: PackedVector2Array, col: Color, w: float) -> void:
	var closed := pts.duplicate()
	closed.append(pts[0])
	ci.draw_polyline(closed, col, w, true)


## `pts` pushed out from `c` by `d` px (a cheap glow shape).
static func _grow(pts: PackedVector2Array, c: Vector2, d: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in pts:
		var v := p - c
		out.append(p + (v.normalized() * d if v.length() > 0.001 else Vector2.ZERO))
	return out
