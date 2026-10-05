class_name DroneDock
extends Control
## The drones and satellites docked on one wheel (ART_BIBLE v2 §3.11, §3.21; round 41
## `drones_v2`, `combat_worst_case_v4`). By default each slice's drones collapse into one thin band
## outside the frame (a tile per drone: its current effect's glyph and value, its HP), on a short
## stem; hovering the slice (or the band), or aiming a card at a drone, blooms the band into full
## mini-wheels on a blended dock lobe, mirrored away from the screen's edges. Drones ride their
## slice with every spin and flip. Over the HP arc the dock stands outside it. View only.

## The bloom (band -> mini-wheels) in and out: `ui_motion.tres` (a hover state: never skipped).
const BLOOM_MOTION := &"drone_bloom"
## Master units (§3.21): the band hugs the frame (414) after BAND_GAP, BAND_DEPTH deep; a bloomed
## drone stands STEM past the band's inner edge (round 41: "drone at RA + 30").
const BAND_GAP := 6.0
const BAND_DEPTH := 34.0
const STEM := 30.0
## A satellite is the D4 frame at this share of its host's (round 41: 0.22).
const SAT_K := 0.22
## Floors in px at text scale 1.0 (the band's depth, a mini-wheel's radius) so text stays legible.
const MIN_BAND := 15.0
const MIN_MINI := 26.0
## Two drones on one slice sit this far either side of its midline (deg), or further when their
## mini-wheels would touch (plus PAIR_PAD px).
const PAIR_DEG := 14.0
const PAIR_PAD := 3.0
## The band covers this share of its slice's angle.
const BAND_SHARE := 0.8
## Over the HP arc the dock keeps this far outside it (px).
const HP_GAP := 4.0
## A bloomed mini-wheel turns round the rim in steps of this (rad), at most this often, until it is
## inside the view (bloomed drones mirror away from the screen's edges and the HUD).
const MIRROR_STEP := 0.06
const MIRROR_STEPS := 24
## Keeping off the HP block: slide steps along the slice (rad), at most this many each way, and the
## margin round a tile (px).
const AVOID_STEP := 0.04
const AVOID_STEPS := 12
const HP_PAD := 2.0
## Hover reach round a tile or a bloomed mini-wheel (px).
const HOVER_PAD := 6.0
## The band tile: glyph radius and text size as shares of the band's depth, never under MIN_TEXT.
const TILE_GLYPH := 0.4
const TILE_TEXT := 0.62
## Glyph, value and HP stand this far apart along the band (share of its depth).
const TILE_STEP := 1.15
const MIN_TEXT := 12
## A bloomed mini-wheel grows from this share of its size as it blooms.
const BLOOM_FROM := 0.45
## The band's outline width (px).
const LINE := 1.5
## The aim ring round a drone (px past it) and its width.
const AIM_RING := 4.0
const AIM_WIDTH := 3.0

var host: WheelAttachments = null
## Per-slot bloom 0..1 (eased by BLOOM_MOTION).
var bloom: Dictionary = {}
## Lab and tests: every slice bloomed.
var force_bloom: bool = false


func _init() -> void:
	name = "DroneDock"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## The bloom state as text (the host redraws on a change).
func signature() -> String:
	return str(bloom) + str(force_bloom)


## Where each shown drone docks now (local), in slot then id order: {sat, slot, index, count, mid,
## r0, r1, a0, a1 (its tile's angles), tile, mini, mini_r, up}. `rot` overrides the wheel's rotation
## (the card-play preview's ghost drones).
func entries(rot: Variant = null) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if host == null or not host.live():
		return out
	var c := host.shown()
	var sats := host.shown_satellites().duplicate()
	sats.sort_custom(func(x: CombatantState, y: CombatantState) -> bool: return x.dock_slot < y.dock_slot or (x.dock_slot == y.dock_slot and String(x.id) < String(y.id)))
	var per_slot := {}
	for s in sats:
		per_slot[s.dock_slot] = int(per_slot.get(s.dock_slot, 0)) + 1
	var seen := {}
	var r := float(host.view.shown_rotation()) if rot == null else float(rot)
	var u := host.unit()
	var ts := Settings.text_scale
	var frame := host.rim() * AttachStyle.MASTER_FRAME / AttachStyle.MASTER_RIM
	var depth := maxf(BAND_DEPTH * u, MIN_BAND * ts)
	var mini_r := maxf(frame * SAT_K, MIN_MINI * sqrt(ts))
	var span := TAU / maxi(1, c.wheel.slice_count) * BAND_SHARE
	var view_rect := Rect2(Vector2.ZERO, size).grow(-2.0)
	var slot_lay := {}
	for s in sats:
		var count := int(per_slot[s.dock_slot])
		var index := int(seen.get(s.dock_slot, 0))
		seen[s.dock_slot] = index + 1
		var mid := host.slot_angle(s.dock_slot, r)
		var r0 := frame + BAND_GAP * u
		if host.over_hp_arc(mid):
			r0 = maxf(r0, host.hp_arc_outer() + HP_GAP)
		elif host.in_hp_gap(mid):
			r0 = host.rim() + BAND_GAP * u  # over the HP number: hug the rim, clear of it
		# The band is as long as its tiles need, within its slice, and keeps off the HP number and
		# the plates under the wheel (§3.21 rule 6): it slides along its slice, else steps out.
		var tile_len := maxf(depth * TILE_STEP, MIN_TEXT * ts * 1.4) * 3.0 + depth * 0.6
		var band_span := minf(span, count * tile_len / (r0 + depth * 0.5))
		if not slot_lay.has(s.dock_slot):
			slot_lay[s.dock_slot] = _clear_of_hp(mid, r0, depth, band_span, count, TAU / maxi(1, c.wheel.slice_count))
		var lay: Vector2 = slot_lay[s.dock_slot]
		mid += lay.x
		r0 = lay.y
		var a0 := mid - band_span * 0.5 + band_span * index / count
		var a1 := a0 + band_span / count
		var tm := (a0 + a1) * 0.5
		var tile := host.center() + Vector2(cos(tm), sin(tm)) * (r0 + depth * 0.5)
		var d := r0 + STEM * u + mini_r
		var off := 0.0
		if count > 1:
			var half := maxf(deg_to_rad(PAIR_DEG), asin(clampf((mini_r + PAIR_PAD) / d, 0.0, 1.0)))
			off = lerpf(-half, half, float(index) / (count - 1))
		var a := mid + off
		var mini := host.center() + Vector2(cos(a), sin(a)) * d
		# Mirror away from the edges: the nearest turn round the rim (clockwise first) that fits.
		if not _fits(view_rect, mini, mini_r):
			for k in range(1, MIRROR_STEPS + 1):
				var found := false
				for sgn in [1.0, -1.0]:
					var t: float = a + sgn * k * MIRROR_STEP
					var p := host.center() + Vector2(cos(t), sin(t)) * d
					if _fits(view_rect, p, mini_r):
						a = t
						mini = p
						found = true
						break
				if found:
					break
		out.append({"sat": s, "slot": s.dock_slot, "index": index, "count": count, "mid": mid, "r0": r0, "r1": r0 + depth,
			"a0": a0, "a1": a1, "tile": tile, "mini": mini, "mini_r": mini_r, "up": a, "depth": depth})
	return out


## (angle shift, inner radius) for a slot's band so none of its `count` tiles meets the view's HP
## number, NEXT plate or LAST TURN plate: the nearest slide along the slice (clockwise first), else
## steps outward.
func _clear_of_hp(mid: float, r0: float, depth: float, band_span: float, count: int, slice_span: float) -> Vector2:
	var blocks: Array[Rect2] = host.view._hp_block_rects()
	if blocks.is_empty():
		return Vector2(0.0, r0)
	var reach := maxf(depth * 0.6, WheelView.SATELLITE_TOKEN * Settings.text_scale) + HP_PAD
	var room := maxf(0.0, (slice_span - band_span) * 0.5)
	for k in range(0, AVOID_STEPS + 1):
		for sgn in ([1.0] if k == 0 else [1.0, -1.0]):
			var shift: float = sgn * k * AVOID_STEP
			if absf(shift) > room:
				continue
			if _band_clear(mid + shift, r0, depth, band_span, count, reach, blocks):
				return Vector2(shift, r0)
	var r := r0
	for k in AVOID_STEPS:
		r += depth
		if _band_clear(mid, r, depth, band_span, count, reach, blocks):
			break
	return Vector2(0.0, r)


func _band_clear(mid: float, r0: float, depth: float, band_span: float, count: int, reach: float, blocks: Array[Rect2]) -> bool:
	for i in count:
		var tm := mid - band_span * 0.5 + band_span * (i + 0.5) / count
		var p := host.center() + Vector2(cos(tm), sin(tm)) * (r0 + depth * 0.5)
		var box := Rect2(p - Vector2(reach, reach), Vector2(reach, reach) * 2.0)
		for b in blocks:
			if box.intersects(b):
				return false
	return true


static func _fits(r: Rect2, at: Vector2, radius: float) -> bool:
	return r.encloses(Rect2(at - Vector2(radius, radius), Vector2(radius, radius) * 2.0))


## Where `sat` stands now (local): its tile, moving out to its mini-wheel as its slice blooms.
func satellite_pos(sat: CombatantState) -> Vector2:
	for e in entries():
		if (e["sat"] as CombatantState).id == sat.id:
			return (e["tile"] as Vector2).lerp(e["mini"], float(bloom.get(int(e["slot"]), 0.0)))
	return host.center() if host != null else Vector2.ZERO


## The slots that should bloom now: hovered (the slice, its band or its bloomed drones), aimed at
## (a card's satellite zones), or every slot (`force_bloom`).
func bloom_targets(list: Array[Dictionary]) -> Dictionary:
	var want := {}
	if host == null or not host.live():
		return want
	var v := host.view
	for e in list:
		var slot := int(e["slot"])
		if force_bloom:
			want[slot] = true
		for z in v.valid_zones:
			if String(z.get("kind", "")) == "satellite" and z.get("id") == (e["sat"] as CombatantState).id:
				want[slot] = true
		if String(v.hover_zone.get("kind", "")) == "satellite" and v.hover_zone.get("id") == (e["sat"] as CombatantState).id:
			want[slot] = true
	if not v.is_visible_in_tree():
		return want
	var mouse := get_global_mouse_position()
	if not v.get_global_rect().has_point(mouse):
		return want
	var local := mouse - global_position
	var hovered := v.slot_at_global(mouse)
	for e in list:
		var slot := int(e["slot"])
		if slot == hovered:
			want[slot] = true
		elif local.distance_to(e["tile"]) <= float(e["depth"]) * 0.5 + HOVER_PAD:
			want[slot] = true
		elif float(bloom.get(slot, 0.0)) > 0.5 and local.distance_to(e["mini"]) <= float(e["mini_r"]) + HOVER_PAD:
			want[slot] = true
	return want


func _process(delta: float) -> void:
	if host == null:
		return
	var list := entries()
	var want := bloom_targets(list)
	var live := Motion.live(BLOOM_MOTION)
	var rate := delta / maxf(0.001, Motion.seconds(BLOOM_MOTION))
	var changed := false
	var slots := {}
	for e in list:
		slots[int(e["slot"])] = true
	for slot in slots:
		var to := 1.0 if want.has(slot) else 0.0
		var was := float(bloom.get(slot, 0.0))
		var now := move_toward(was, to, rate) if live else to
		if now != was:
			bloom[slot] = now
			changed = true
	for slot in bloom.keys():
		if not slots.has(slot):
			bloom.erase(slot)
			changed = true
	if changed:
		queue_redraw()


func _draw() -> void:
	if host == null or not host.live():
		return
	var v := host.view
	var list := entries()
	var col := AttachStyle.owner_color(host.shown(), v.lookup)
	# Collapsed bands first (one per slot), then the lobes and the bloomed mini-wheels on top.
	var drawn_band := {}
	for e in list:
		var slot := int(e["slot"])
		var b := float(bloom.get(slot, 0.0))
		if not drawn_band.has(slot) and b < 1.0:
			drawn_band[slot] = true
			_draw_band(list, slot, col, 1.0 - b)
	for e in list:
		var b := float(bloom.get(int(e["slot"]), 0.0))
		if b > 0.0:
			_draw_lobe(e, col, b)
	for e in list:
		var b := float(bloom.get(int(e["slot"]), 0.0))
		var sat: CombatantState = e["sat"]
		var hp := float(v.anim_sat_hp.get(sat.id, sat.hp))
		var pulse := v.pulse_scale if sat.id == v.pulse_satellite else 1.0
		if b > 0.0:
			var at: Vector2 = (e["tile"] as Vector2).lerp(e["mini"], b)
			var rm := float(e["mini_r"]) * lerpf(BLOOM_FROM, 1.0, b) * pulse
			MiniWheel.draw(self, at, rm, float(e["up"]), sat, v.lookup, col, b, hp)
		_draw_aim(e, b)


## One slot's collapsed band: a thin plate outside the frame on a short stem, a tile per drone.
func _draw_band(list: Array[Dictionary], slot: int, col: Color, alpha: float) -> void:
	var v := host.view
	var c := host.center()
	var mine: Array[Dictionary] = []
	for e in list:
		if int(e["slot"]) == slot:
			mine.append(e)
	if mine.is_empty():
		return
	var first: Dictionary = mine[0]
	var last: Dictionary = mine[mine.size() - 1]
	var r0 := float(first["r0"])
	var r1 := float(first["r1"])
	var a0 := float(first["a0"])
	var a1 := float(last["a1"])
	var mid := float(first["mid"])
	# Short stem from the rim to the band.
	var stem_half := (a1 - a0) * 0.12
	var stem := PackedVector2Array([c + Vector2(cos(mid - stem_half), sin(mid - stem_half)) * host.rim(), c + Vector2(cos(mid - stem_half * 0.6), sin(mid - stem_half * 0.6)) * r0,
		c + Vector2(cos(mid + stem_half * 0.6), sin(mid + stem_half * 0.6)) * r0, c + Vector2(cos(mid + stem_half), sin(mid + stem_half)) * host.rim()])
	draw_colored_polygon(stem, Color(col, 0.55 * alpha))
	var plate := AttachStyle.sector(c, r0, r1, a0, a1, 14)
	draw_colored_polygon(plate, AttachStyle.glass(0.9 * alpha))
	var closed := plate.duplicate()
	closed.append(plate[0])
	draw_polyline(closed, Color(col, alpha), LINE, true)
	for e in mine:
		var sat: CombatantState = e["sat"]
		if int(e["index"]) > 0:
			var sa := float(e["a0"])
			draw_line(c + Vector2(cos(sa), sin(sa)) * r0, c + Vector2(cos(sa), sin(sa)) * r1, Color(col, 0.6 * alpha), 1.0, true)
		var depth := float(e["depth"])
		var at: Vector2 = e["tile"]
		var land := MiniWheel.landing(sat, v.lookup)
		var ts := maxi(MIN_TEXT, roundi(depth * TILE_TEXT))
		var hp := roundi(float(v.anim_sat_hp.get(sat.id, sat.hp)))
		var tangent := Vector2(-sin(float(e["mid"])), cos(float(e["mid"])))
		if tangent.x < -0.01 or (absf(tangent.x) <= 0.01 and tangent.y < 0.0):
			tangent = -tangent  # glyph, value, HP read left to right (top to bottom)
		var step := maxf(depth * TILE_STEP, ts * 1.4)
		if land != null:
			AttachStyle.draw_slice_glyph(self, at - tangent * step, depth * TILE_GLYPH, land.slice_type)
			if land.base_output > 0:
				AttachStyle.draw_centred(self, AttachStyle.value_font(), at, str(land.base_output), ts, Color(Palette.TEXT_HI, alpha), 2)
		AttachStyle.draw_centred(self, AttachStyle.label_font(), at + tangent * step, str(hp), ts, Color(Palette.GAIN, alpha), 2)


## The blended dock (§3.11): the slice's outline swells out of the rim into a waisted neck that
## wraps the mini-wheel, in the owner's colour.
func _draw_lobe(e: Dictionary, col: Color, b: float) -> void:
	var c := host.center()
	var mid := float(e["mid"])
	var start := c + Vector2(cos(mid), sin(mid)) * host.rim()
	var mini: Vector2 = (e["tile"] as Vector2).lerp(e["mini"], b)
	var rm := float(e["mini_r"]) * lerpf(BLOOM_FROM, 1.0, b)
	var toward := (start - mini).normalized()
	var end := mini + toward * rm * 0.9
	var ctrl := c + Vector2(cos(mid), sin(mid)) * (float(e["r0"]) + float(e["depth"]))
	var pts := PackedVector2Array()
	var steps := 10
	for k in steps + 1:
		var t := float(k) / steps
		pts.append(start.lerp(ctrl, t).lerp(ctrl.lerp(end, t), t))
	var neck := maxf(4.0, rm * 0.34)
	draw_polyline(pts, Color(col, b), neck + 3.0, true)
	draw_polyline(pts, AttachStyle.glass(b), neck, true)
	draw_circle(start, neck * 0.7, Color(col, b))
	draw_circle(start, neck * 0.7 - 1.5, AttachStyle.glass(b))


## The aim marks: a valid drone target rings acid (bright when hovered), the targeted one gets a
## crosshair ring.
func _draw_aim(e: Dictionary, b: float) -> void:
	var v := host.view
	var sat: CombatantState = e["sat"]
	var at := satellite_pos(sat)
	var r := lerpf(float(e["depth"]) * 0.6, float(e["mini_r"]), b) + AIM_RING
	for z in v.valid_zones:
		if String(z.get("kind", "")) == "satellite" and z.get("id") == sat.id:
			var hot: bool = String(v.hover_zone.get("kind", "")) == "satellite" and v.hover_zone.get("id") == sat.id
			draw_arc(at, r, 0, TAU, 32, Color(Palette.FOCUS, 1.0 if hot else 0.55 * v.zone_pulse), AIM_WIDTH if hot else AIM_WIDTH * 0.5, true)
			break
	if sat.id == v.targeted_satellite:
		draw_arc(at, r + AIM_RING, 0, TAU, 32, Palette.FOCUS, AIM_WIDTH * 0.5, true)
		for k in 4:
			var a := TAU * k / 4.0
			draw_line(at + Vector2(cos(a), sin(a)) * (r + AIM_RING * 0.5), at + Vector2(cos(a), sin(a)) * (r + AIM_RING * 2.5), Palette.FOCUS, AIM_WIDTH * 0.5, true)
