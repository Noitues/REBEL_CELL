class_name CardPreviewOverlay
extends Control
## The animated card-play preview (ART_BIBLE v2 §3.17, round 17 `preview_storyboard`; z-order 14 of
## §3.21, over everything): while a spin or nudge card (or a nudge button) is hovered or aimed, one
## set of large ghosted chevrons outside the rim chases from the top needle to where it lands, a
## dashed ghost blade stands at every needle's landing with its value window and index tab, the
## landing slices get a dashed outline in their program colour, and every docked drone gets a dashed
## ghost where it ends up. No trace lines, no aim pips, no arrowheads. Labels ("1 LANDS HERE",
## "DRONE ENDS HERE") only while the card waits; aimed, it holds at HELD_ALPHA. On commit the
## ghost rides the turning slices so it meets the blade as the wheel lands (LANDED = PREVIEW).
## Fed only by the view's `ghost_rotation`, which the combat scene sets from the engine's preview
## of the action (the forecast's code path), so the ghost is the result. View only.

## The chevrons' chase (one pass, then it loops while shown); reduce effects: lit, still.
const CHASE_MOTION := &"preview_chevron_chase"
## How the ghost comes in and goes (and rides the slices on commit).
const GHOST_MOTION := &"preview_ghost"
## Chevrons: how many, their size (master units: 46 px at r = 220 is ~ 87 master), how far out.
const CHEVRONS := 9
const CHEVRON_SIZE := 87.0
const CHEVRON_AT := 1.36
## A chevron's unlit and lit alpha.
const CHEVRON_DIM := 0.28
const CHEVRON_LIT := 0.95
## Ghost blade: root and tip (shares of the rim), half width at the root (share); value window.
const BLADE_ROOT := 1.24
const BLADE_TIP := 0.94
const BLADE_HALF := 0.075
const WINDOW_AT := 1.3
const WINDOW_SIZE := 0.1
## Dash and gap (px), line width.
const DASH := 6.0
const GAP := 4.0
const LINE := 2.0
## Through peel, drag and slap the preview holds at this alpha (§3.17: 50 %).
const HELD_ALPHA := 0.5
## Label text size (px at text scale 1.0) and its distance outside the ghost (px).
const LABEL_PX := 13
const LABEL_OUT := 18.0

var host: WheelAttachments = null
## 0..1: the ghost's presence.
var shown_amount: float = 0.0
## 0..1: where the chevron chase is (loops).
var chase: float = 0.0
## The ghost being shown: {rot (ticks the wheel lands on), base (the rotation it was set from)}.
var ghost: Dictionary = {}
## True after the card is played: the ghost rides the turning slices until the wheel lands.
var committed: bool = false


func _init() -> void:
	name = "CardPreview"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func signature() -> String:
	return "%s|%.3f|%.3f|%s" % [str(ghost), shown_amount, chase, str(committed)]


## The wheel's turn this preview shows (ticks, the shortest way round), 0 when none.
func delta_ticks() -> int:
	if ghost.is_empty():
		return 0
	var d := posmod(int(ghost["rot"]) - int(ghost["base"]), RC.TICKS)
	return d - RC.TICKS if d > RC.TICKS / 2 else d


## The slot each needle lands on in this preview (the slice under it once the wheel has turned).
func landing_slots() -> Array[int]:
	var out: Array[int] = []
	var c := host.shown() if host != null else null
	if c == null or c.wheel == null or ghost.is_empty():
		return out
	for p in c.wheel.pointer_ticks:
		out.append(WheelMath.slice_at(WheelMath.tick_at(int(ghost["rot"]), p), c.wheel.slice_count))
	return out


func _process(delta: float) -> void:
	if host == null or host.view == null:
		return
	var v := host.view
	var c := host.shown()
	var want: Variant = v.ghost_rotation if not v.replaying else null
	if want != null and c != null and c.wheel != null and int(want) != c.wheel.rotation:
		ghost = {"rot": int(want), "base": c.wheel.rotation}
		committed = false
	elif not ghost.is_empty() and not committed:
		# The card was played: the ghost rides the slices while the wheel turns to it.
		if c != null and c.wheel != null and c.wheel.rotation == int(ghost["rot"]) and v.motion_running():
			committed = true
		else:
			ghost = {} if shown_amount <= 0.0 else ghost
	if committed and (c == null or not v.motion_running()):
		committed = false
		ghost = {}
	var target := 1.0 if (want != null or committed) and not ghost.is_empty() else 0.0
	var live := Motion.live(GHOST_MOTION)
	shown_amount = move_toward(shown_amount, target, delta / maxf(0.001, Motion.seconds(GHOST_MOTION))) if live else target
	if shown_amount <= 0.0 and want == null and not committed:
		ghost = {}
	if Motion.live(CHASE_MOTION) and not ghost.is_empty():
		chase = fposmod(chase + delta / maxf(0.001, Motion.seconds(CHASE_MOTION)), 1.0)
	else:
		chase = 1.0


func _draw() -> void:
	if host == null or not host.live() or ghost.is_empty() or shown_amount <= 0.0:
		return
	var v := host.view
	var c := host.shown()
	var w := c.wheel
	var dt := delta_ticks()
	if dt == 0:
		return
	var aimed := not v.valid_zones.is_empty()
	var alpha := shown_amount * (HELD_ALPHA if aimed else 1.0)
	var center := host.center()
	var rim := host.rim()
	var u := host.unit()
	# The ghost's frame: before the commit it stands where the landing slices are now; after, it
	# rides them (shown rotation catching up with the ghost's).
	var ride := float(int(ghost["base"])) if not committed else v.shown_rotation()
	var shift := float(int(ghost["rot"])) - ride
	var landings := landing_slots()
	var tps := w.ticks_per_slice()
	# Landing slices: dashed outline in their program colour.
	for i in landings.size():
		var slot: int = landings[i]
		var slice := v.lookup.get_content(w.slot_slice_ids[slot]) as SliceData
		var sc := AttachStyle.slice_color(slice.slice_type) if slice != null else Palette.TEXT_HI
		var a0 := WheelView._ang(slot * tps - tps * 0.5 - ride)
		var a1 := WheelView._ang(slot * tps + tps * 0.5 - ride)
		var wedge := AttachStyle.sector(center, rim - host.band(), rim, minf(a0, a1), maxf(a0, a1), 14)
		wedge.append(wedge[0])
		AttachStyle.draw_dashed(self, wedge, Color(sc, alpha), LINE, DASH, GAP)
	# Chevrons from the top needle to its landing (not after the commit: the wheel shows the way).
	if not committed and not w.pointer_ticks.is_empty():
		var p0 := float(w.pointer_ticks[0])
		var from := WheelView._ang(p0)
		var to := WheelView._ang(p0 + dt)
		var cs := CHEVRON_SIZE * u
		for k in CHEVRONS:
			var t := (k + 0.5) / CHEVRONS
			var a := lerpf(from, to, t)
			var lit := _chevron_light(k)
			_draw_chevron(center + Vector2(cos(a), sin(a)) * rim * CHEVRON_AT, a, signf(to - from), cs, Color(AttachStyle.cream(), alpha * lerpf(CHEVRON_DIM, CHEVRON_LIT, lit)))
	# Ghost blades at every needle's landing.
	for i in w.pointer_ticks.size():
		var a := WheelView._ang(float(w.pointer_ticks[i]) + shift)
		var slot: int = landings[i] if i < landings.size() else -1
		var slice := v.lookup.get_content(w.slot_slice_ids[slot]) as SliceData if slot >= 0 else null
		_draw_ghost_blade(center, rim, a, i, w.pointer_ticks.size(), slice, alpha)
		if not aimed and not committed:
			var lp := center + Vector2(cos(a), sin(a)) * (rim * WINDOW_AT + LABEL_OUT * Settings.text_scale + rim * WINDOW_SIZE)
			_label(lp, tr("%d LANDS HERE") % (i + 1), alpha)
	# Ghost drones where each docked drone ends up (they ride their slice).
	var after := host.dock.entries(float(int(ghost["rot"])) if not committed else null)
	var labelled := false
	for e in after:
		if committed:
			break
		var at: Vector2 = e["tile"]
		var r := float(e["depth"]) * 0.6
		if float(host.dock.bloom.get(int(e["slot"]), 0.0)) > 0.5:
			at = e["mini"]
			r = float(e["mini_r"])
		AttachStyle.draw_dashed(self, AttachStyle.arc_points(at, r, 0.0, TAU, 28), Color(AttachStyle.cream(), alpha), LINE, DASH, GAP)
		if not aimed and not labelled:
			labelled = true  # one label: the first drone (slot order) names the ghost for all
			var out := (at - center).normalized()
			_label(at + out * (r + LABEL_OUT * Settings.text_scale), tr("DRONE ENDS HERE"), alpha)


## How lit chevron `k` is now: the chase lights them in turn in the direction of travel.
func _chevron_light(k: int) -> float:
	return clampf(chase * (CHEVRONS + 1) - k, 0.0, 1.0)


func _draw_chevron(at: Vector2, a: float, way: float, s: float, col: Color) -> void:
	var tangent := Vector2(-sin(a), cos(a)) * way
	var normal := Vector2(cos(a), sin(a))
	var tip := at + tangent * s * 0.35
	var back := at - tangent * s * 0.35
	var arm := s * 0.42
	var thick := s * 0.24
	var pts := PackedVector2Array([back + normal * arm, tip, back - normal * arm, back - normal * arm + tangent * thick, tip + tangent * thick, back + normal * arm + tangent * thick])
	draw_colored_polygon(pts, col)


func _draw_ghost_blade(center: Vector2, rim: float, a: float, index: int, count: int, slice: SliceData, alpha: float) -> void:
	var dir := Vector2(cos(a), sin(a))
	var side := dir.orthogonal() * rim * BLADE_HALF
	var root := center + dir * rim * BLADE_ROOT
	var tip := center + dir * rim * BLADE_TIP
	var col := Color(AttachStyle.cream(), alpha)
	draw_colored_polygon(PackedVector2Array([tip, root + side, root - side]), Color(AttachStyle.cream(), 0.14 * alpha))
	AttachStyle.draw_dashed(self, PackedVector2Array([tip, root + side, root - side, tip]), col, LINE, DASH * 0.6, GAP * 0.6)
	# Value window: the landing slice's value, and the needle's index tab on multi-needle wheels.
	var win := center + dir * rim * WINDOW_AT
	var ws := rim * WINDOW_SIZE
	var box := Rect2(win - Vector2(ws, ws * 0.7), Vector2(ws * 2.0, ws * 1.4))
	draw_rect(box, AttachStyle.glass(0.8 * alpha))
	AttachStyle.draw_dashed(self, PackedVector2Array([box.position, Vector2(box.end.x, box.position.y), box.end, Vector2(box.position.x, box.end.y), box.position]), col, 1.0, DASH * 0.5, GAP * 0.5)
	var fs := maxi(LABEL_PX, roundi(ws * 1.1))
	if slice != null and slice.base_output > 0:
		AttachStyle.draw_centred(self, AttachStyle.value_font(), win, str(slice.base_output), fs, col, 2)
	elif slice != null:
		AttachStyle.draw_slice_glyph(self, win, ws * 0.6, slice.slice_type)
	if count > 1:
		AttachStyle.draw_centred(self, AttachStyle.label_font(), win + dir.orthogonal() * ws * 1.6, str(index + 1), LABEL_PX, col, 2)


func _label(at: Vector2, text: String, alpha: float) -> void:
	var fs := roundi(LABEL_PX * Settings.text_scale)
	var font := AttachStyle.label_font()
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Rect2(at - Vector2(w * 0.5 + 4.0, fs * 0.7), Vector2(w + 8.0, fs * 1.4))
	box.position.x = clampf(box.position.x, 0.0, maxf(0.0, size.x - box.size.x))
	box.position.y = clampf(box.position.y, 0.0, maxf(0.0, size.y - box.size.y))
	draw_rect(box, AttachStyle.glass(0.85 * alpha))
	draw_rect(box, Color(Palette.RESIST_GOLD, alpha), false, 1.0)
	AttachStyle.draw_centred(self, font, box.get_center(), text, fs, Color(Palette.RESIST_GOLD, alpha))
