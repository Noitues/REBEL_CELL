class_name HudStats
extends Control
## Ransom-note stat tags for the top bar: each stat on its own taped paper tag (paper,
## pink, yellow), a marker name and the value in Anton, tilted a little. Decoration of
## numbers the scene provides; hovering a tag shows what the number means (the item's
## tooltip, H20). Clicks pass through.
## H21: every tag carries its resource's StatIcon (the same icon wherever that resource
## shows: badges, prices, event outcomes), and the tags follow the text size: while the
## full tags (name over icon and value) fit the row at the current text scale (or a little
## under it, FULL_MIN_FIT) they are drawn full; otherwise they go compact (icon and value,
## the name in the tooltip's title) and shrink only as far as the row needs. The height
## follows.
## H22 #14: outside a fight the words stay (the first-time player found icon-only tags
## worse): when the fixed-width full tags don't fit, the tags are fitted to their own words
## (name over icon and value, each tag as wide as its longest line) and shrink as a row;
## if even that would go under FULL_MIN_FIT of the text size (a narrow window), they wrap
## to two rows. Only a fight (max_height set) still goes compact.

## A full tag at text scale 1.0, and the gap between tags (px).
const TAG_SIZE := Vector2(100, 44)
const TAG_GAP := 8.0
## Full tags (with their names) may shrink to this share of the text scale to fit before
## the row goes compact.
const FULL_MIN_FIT := 0.85
## A compact tag's height at scale 1.0 (px).
const COMPACT_H := 34.0
## Room past a fitted tag's name (the tilt and the marker's overhang, px at 1.0).
const NAME_SLACK := 4.0
## Space above the tags (the tape) and below them (px at scale 1.0).
const TOP_ROOM := 7.0
const BOTTOM_ROOM := 3.0
## The icon's radius, the inner padding and lettering at scale 1.0.
const ICON_R := 9.0
const PAD := 6.0
const NAME_SIZE := 10
const VALUE_SIZE := 22
const SUFFIX_SIZE := 11
## What a tag shows for a number that doesn't exist yet (no best ICE): never "none".
const NO_VALUE := "—"
const PAPERS: Array[Color] = [Color("#E9DFC6"), Color("#F5AFCB"), Color("#F2DC7A"), Color("#F2EEE4")]

## [[name, value, suffix, tooltip, icon kind], ...] (tooltip and icon optional: the icon
## defaults to StatIcon.kind_for(name)).
var items: Array = []:
	set(v):
		_note_changes(items, v)
		items = v
		_relayout()
## Compact tags (icon and value) and the scale they are drawn at (read-only).
var compact: bool = false
var tag_scale: float = 1.0
## Rows of tags (2 when fitted tags wrap outside a fight).
var rows: int = 1
## When above 0, the tags never make the row taller than this (px): a fight keeps its
## height under the top bar (the netrun sets it while the combat scene is up).
var max_height: float = 0.0:
	set(v):
		max_height = v
		_relayout()
var _rects: Array[Rect2] = []
var _tip_title: String = ""
## H24 S16: small captions over groups of tags ([[first tag index, words, tooltip], ...],
## the words translated by the caller), drawn before their group's first tag outside a
## fight ("CAMPAIGN", "THIS RUN": the top bar's set changes between the HQ and a run).
var captions: Array = []:
	set(v):
		_note_caption_change(v)
		captions = v
		_relayout()
## The captions' rects as laid out now (local; empty while they are not drawn).
var _caption_rects: Array[Rect2] = []
## Caption lettering and the gap after a caption at scale 1.0 (px).
const CAPTION_SIZE := 10
const CAPTION_GAP := 6.0


## Animation pass ANIM-6 (ANIMATION_HANDOFF 4.24): a tag whose value changed bumps
## (`sticky_bump`: its scale to the entry's amplitude and back) and its number rolls from
## the old value (`number_roll`; Cycles and Schematics count up with `count_up` when they
## rise). Tags are matched by name between two sets, so only a changed value moves. When
## the captions change (CAMPAIGN / THIS RUN) the old ones fade out as the new fade in
## (`caption_crossfade`). Drawn only: the rects and the value shown at rest never change.
## Tag name -> {bump: 0..1, roll: 0..1, from: int, to: int, rolls: bool, tween}.
var _moving: Dictionary = {}
## Caption cross-fade: 0 -> 1 (1 = the new captions only) and the old captions' look.
var _caption_fade: float = 1.0
var _old_captions: Array = []
var _caption_tween: Tween = null


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	custom_minimum_size = Vector2(0, TOP_ROOM + TAG_SIZE.y + BOTTOM_ROOM)
	MotionSkip.register_passive(self)  # ANIM-R6 D7: bumps end with any press that ends a motion


## MotionSkip (ANIM-R6 D7): a tag bumps, rolls, pulses for a landing or its caption fades.
func motion_running() -> bool:
	return not _moving.is_empty() or not _landing.is_empty() or (_caption_tween != null and _caption_tween.is_valid())


## MotionSkip (ANIM-R6 D7): every bump, roll, landing pulse and cross-fade at its end.
func complete_motion() -> void:
	settle()


func _ready() -> void:
	Settings.changed.connect(_relayout)
	_relayout()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_relayout()


## The global centre of the tag carrying icon `kind` (a flight's target: a bought card goes
## to CARDS), or Vector2.INF when no tag has it.
func icon_point(kind: StringName) -> Vector2:
	for i in mini(items.size(), _rects.size()):
		if icon_of(i) == kind:
			return get_global_transform() * _rects[i].get_center()
	return Vector2.INF


## The tag names bumping now (tests).
func bumping() -> PackedStringArray:
	var out := PackedStringArray()
	for k in _moving:
		out.append(String(k))
	return out


## ANIM-R2 E9: a refused purchase flashes the money tag red with "PRICE > MONEY" under it
## (`price_refusal`: its seconds, amplitude = pulses), as RAM does for a card; static until
## the next change under reduce effects and headless.
const REFUSED_COLOR := Color("#FF4D4D")
const REFUSED_MIN_ALPHA := 0.45
const REFUSED_FILL := 0.35
const REFUSED_TEXT_SHARE := 0.7
var _refused_tag: String = ""
var _refused_text: String = ""
var refusal_alpha: float = 1.0
var _refusal_tween: Tween = null


## Flashes tag `tag` (its name, e.g. "CYCLES") with `text` ("150 > 120") under it.
func flash_refusal(tag: String, text: String) -> void:
	_refused_tag = tag
	_refused_text = text
	refusal_alpha = 1.0
	queue_redraw()
	if _refusal_tween != null and _refusal_tween.is_valid():
		_refusal_tween.kill()
	if not Motion.live(&"price_refusal") or not is_inside_tree():
		return
	var pulses := maxf(1.0, Motion.amplitude(&"price_refusal"))
	_refusal_tween = create_tween()
	_refusal_tween.tween_method(func(p: float) -> void:
		refusal_alpha = absf(cos(p * PI * pulses))
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"price_refusal"))
	_refusal_tween.tween_callback(func() -> void:
		_refused_tag = ""
		_refused_text = ""
		refusal_alpha = 1.0
		queue_redraw())


## ANIM-R4 C7: the refusal's words as drawn under a tag `width` px wide at `fs`: one line,
## or split at its dots when the line is wider than the tag (it ran past the panel edge).
static func refusal_lines(text: String, width: float, fs: int) -> PackedStringArray:
	if Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= width or not text.contains(" · "):
		return PackedStringArray([text])
	return text.split(" · ")


## The refusal shown on a tag now ("" when none; tests).
func refusal_text() -> String:
	return _refused_text


## ANIM-R2 E9: another set of tags this one mirrors (the Modem's wallet mirrors the top
## bar): a tag of the same name shows the mirror's number while it rolls, so the two never
## disagree mid-roll (the top bar read 119 while the wallet read 120).
## It redraws on the mirror's own roll steps (`rolled`), so both draw the same number in
## the same frame (a redraw asked from _process drew the step before).
var mirror: HudStats = null:
	set(v):
		if mirror != null and is_instance_valid(mirror) and mirror.rolled.is_connected(queue_redraw):
			mirror.rolled.disconnect(queue_redraw)
		mirror = v
		if mirror != null:
			mirror.rolled.connect(queue_redraw)

## A tag's number stepped in its roll (or the roll ended): mirrors redraw with it.
signal rolled


## The value tag `i` shows now (mid-roll: the rolling number).
func shown_value(i: int) -> String:
	var it: Array = items[i]
	if mirror != null and is_instance_valid(mirror) and mirror._moving.has(String(it[0])):
		for k in mirror.items.size():
			if String(mirror.items[k][0]) == String(it[0]) and String(mirror.items[k][1]) == String(it[1]):
				return mirror.shown_value(k)
	var m: Dictionary = _moving.get(String(it[0]), {})
	if m.is_empty() or not bool(m["rolls"]):
		return String(it[1])
	return str(roundi(lerpf(float(m["from"]), float(m["to"]), float(m["roll"]))))


## Ends every bump, roll and cross-fade now.
func settle() -> void:
	for k in _moving.keys():
		var tw: Tween = _moving[k]["tween"]
		if tw != null and tw.is_valid():
			tw.kill()
	_moving.clear()
	for k in _landing.keys():
		var lt: Tween = _landing[k]["tween"]
		if lt != null and lt.is_valid():
			lt.kill()
	_landing.clear()
	if _caption_tween != null and _caption_tween.is_valid():
		_caption_tween.kill()
	_caption_fade = 1.0
	_old_captions = []
	queue_redraw()


func _note_changes(old: Array, new: Array) -> void:
	if not (_refusal_tween != null and _refusal_tween.is_valid()) and old != new:
		_refused_tag = ""  # a static refusal (motion off) shows until the next change
		_refused_text = ""
	if old.is_empty() or not Motion.live(&"sticky_bump") or not is_inside_tree():
		return
	var before := {}
	for it in old:
		before[String(it[0])] = String(it[1])
	for it in new:
		var key := String(it[0])
		var value := String(it[1])
		if not before.has(key) or before[key] == value:
			continue
		var kind := StatIcon.kind_for(key) if it.size() <= 4 or String(it[4]) == "" else StringName(String(it[4]))
		_bump(key, String(before[key]), value, kind)


func _bump(key: String, from: String, to: String, kind: StringName) -> void:
	if _moving.has(key):
		var old_tw: Tween = _moving[key]["tween"]
		if old_tw != null and old_tw.is_valid():
			old_tw.kill()
	var rolls := from.is_valid_int() and to.is_valid_int()
	var rising := rolls and to.to_int() > from.to_int()
	var roll_id := &"count_up" if rising and kind in [StatIcon.CYCLES, StatIcon.SCHEMATICS] else &"number_roll"
	var m := {"bump": 0.0, "roll": 0.0, "from": from.to_int() if rolls else 0, "to": to.to_int() if rolls else 0, "rolls": rolls}
	var e := Motion.entry(&"sticky_bump")
	var tw := create_tween().set_parallel(true)
	tw.tween_method(func(v: float) -> void:
		m["bump"] = v
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"sticky_bump")).set_ease(e.ease).set_trans(e.trans)
	if rolls and Motion.live(roll_id):
		var re := Motion.entry(roll_id)
		tw.tween_method(func(v: float) -> void:
			m["roll"] = v
			rolled.emit()
			queue_redraw(), 0.0, 1.0, Motion.seconds(roll_id)).set_delay(Motion.delay_of(roll_id)).set_ease(re.ease).set_trans(re.trans)
	else:
		m["roll"] = 1.0
	tw.chain().tween_callback(func() -> void:
		if is_same(_moving.get(key, null), m):
			_moving.erase(key)
		rolled.emit()
		queue_redraw())
	m["tween"] = tw
	_moving[key] = m


## A tag's drawn scale while it bumps (1 at rest): up to the entry's amplitude and back;
## ANIM-R5 B5: times a flight's landing pulse on it.
func _bump_scale(key: String) -> float:
	var k := _pulse_scale(float(_landing.get(key, {}).get("t", 1.0)), Motion.amplitude(LAND_PULSE)) if _landing.has(key) else 1.0
	var m: Dictionary = _moving.get(key, {})
	if m.is_empty():
		return k
	return k * _pulse_scale(float(m["bump"]), Motion.amplitude(&"sticky_bump"))


## A pop's scale at progress `t` (0..1) peaking at `peak` (Motion.pop's shape).
static func _pulse_scale(t: float, peak: float) -> float:
	var up := t / Motion.POP_GROW_SHARE if t < Motion.POP_GROW_SHARE else 1.0 - (t - Motion.POP_GROW_SHARE) / (1.0 - Motion.POP_GROW_SHARE)
	return lerpf(1.0, peak, clampf(up, 0.0, 1.0))


## ANIM-R5 B5: a flight has landed on the tag carrying icon `kind` (a bought card on CARDS):
## the tag pulses (`flight_land_pulse`), bigger than a value's bump, so the eye finds where
## the item went. Nothing under reduce effects or headless. Returns whether a tag pulses.
const LAND_PULSE := &"flight_land_pulse"
## Tag name -> {t: 0..1, tween} while a landing pulse plays.
var _landing: Dictionary = {}


func land_pulse(kind: StringName) -> bool:
	if not Motion.live(LAND_PULSE) or not is_inside_tree():
		return false
	for i in items.size():
		if icon_of(i) != kind:
			continue
		var key := String(items[i][0])
		var old: Dictionary = _landing.get(key, {})
		if not old.is_empty() and old["tween"] != null and (old["tween"] as Tween).is_valid():
			(old["tween"] as Tween).kill()
		var p := {"t": 0.0, "tween": null}
		var e := Motion.entry(LAND_PULSE)
		var tw := create_tween()
		# ANIM-R6 B7: after the entry's delay, as every Motion helper plays it.
		tw.tween_interval(Motion.delay_of(LAND_PULSE))
		tw.tween_method(func(v: float) -> void:
			p["t"] = v
			queue_redraw(), 0.0, 1.0, Motion.seconds(LAND_PULSE)).set_ease(e.ease).set_trans(e.trans)
		tw.tween_callback(func() -> void:
			if is_same(_landing.get(key, null), p):
				_landing.erase(key)
			queue_redraw())
		p["tween"] = tw
		_landing[key] = p
		return true
	return false


## The tag names pulsing for a landing now (tests).
func landing() -> PackedStringArray:
	return PackedStringArray(_landing.keys())


static func _caption_words(a: Array) -> String:
	var parts := PackedStringArray()
	for c in a:
		parts.append(String(c[1]))
	return "|".join(parts)


func _note_caption_change(new: Array) -> void:
	if captions.is_empty() or _caption_words(captions) == _caption_words(new) or not Motion.live(&"caption_crossfade") or not is_inside_tree():
		return
	var order := captions.duplicate()
	order.sort_custom(func(a: Array, b: Array) -> bool: return int(a[0]) < int(b[0]))
	_old_captions = []
	for k in mini(order.size(), _caption_rects.size()):
		_old_captions.append([_caption_rects[k], String(order[k][1])])
	if _caption_tween != null and _caption_tween.is_valid():
		_caption_tween.kill()
	_caption_fade = 0.0
	var e := Motion.entry(&"caption_crossfade")
	_caption_tween = create_tween()
	_caption_tween.tween_method(func(v: float) -> void:
		_caption_fade = v
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"caption_crossfade")).set_ease(e.ease).set_trans(e.trans)
	_caption_tween.tween_callback(func() -> void: _old_captions = [])


## A best-ICE style number for a tag: NO_VALUE when there is none yet.
static func ice_value(level: int) -> String:
	return NO_VALUE if level < 0 else str(level)


## The icon of tag `i`.
## Tag `i`'s name as drawn and measured: translated (H23 S16; the icon still follows the
## name's own key). H24 S4: `tr`, so a bar shown as given still translates its keys.
func tag_name(i: int) -> String:
	return tr(String(items[i][0])) if i >= 0 and i < items.size() else ""


func icon_of(i: int) -> StringName:
	var it: Array = items[i]
	if it.size() > 4 and String(it[4]) != "":
		return StringName(String(it[4]))
	return StatIcon.kind_for(String(it[0]))


## Width the full tags take at scale `s`.
func full_width(s: float = 1.0) -> float:
	return items.size() * (TAG_SIZE.x + TAG_GAP) * s


## Width the compact tags take at scale `s` (the least room the row needs, at 1.0).
func compact_width(s: float = 1.0) -> float:
	var total := 0.0
	for it in items:
		total += (_compact_tag_width(it) + TAG_GAP) * s
	return total


## Each tag's rect (local), as laid out now.
func tag_rects() -> Array[Rect2]:
	return _rects.duplicate()


## Width of a tag fitted to its words at scale 1.0: the longer of the name and the icon
## with its value (H22 #14).
func _fitted_tag_width(it: Array) -> float:
	var name_w := Palette.marker().get_string_size(tr(String(it[0])), HORIZONTAL_ALIGNMENT_LEFT, -1, NAME_SIZE).x + NAME_SLACK
	return maxf(PAD + name_w + PAD, _compact_tag_width(it))


## Width the fitted tags `from`..`to` (exclusive) take at scale 1.0.
func _fitted_width(from: int, to: int) -> float:
	var total := 0.0
	for i in range(from, to):
		total += _fitted_tag_width(items[i]) + TAG_GAP
	return total


func _compact_tag_width(it: Array) -> float:
	var value := String(it[1])
	var w := Palette.display().get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, VALUE_SIZE).x
	if it.size() > 2 and String(it[2]) != "":
		w += 2.0 + Palette.marker().get_string_size(String(it[2]), HORIZONTAL_ALIGNMENT_LEFT, -1, SUFFIX_SIZE).x
	return PAD + ICON_R * 2.0 + 5.0 + w + PAD


## The captions' widths at scale `s` (each with its gap).
func _caption_width(s: float) -> float:
	var w := 0.0
	for c in captions:
		w += Palette.mono().get_string_size(String(c[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(CAPTION_SIZE * s)).x + CAPTION_GAP * s
	return w


## Whether the captions are drawn now (outside a fight, the tags on one row).
func captions_shown() -> bool:
	return not _caption_rects.is_empty()


## The caption rects as laid out now (local).
func caption_rects() -> Array[Rect2]:
	return _caption_rects.duplicate()


func _relayout() -> void:
	var text_s := Settings.text_scale
	var n := items.size()
	var room := size.x if size.x > 1.0 else full_width(text_s)
	_rects.clear()
	_caption_rects.clear()
	# The captions take their width off the tags' room (outside a fight).
	var with_captions := not captions.is_empty() and max_height <= 0.0 and n > 0
	if with_captions:
		room = maxf(1.0, room - _caption_width(text_s))
	# The largest scale each look may take (a height cap keeps a fight's top bar as it is).
	var s := text_s
	var most := text_s
	if max_height > 0.0:
		s = minf(text_s, maxf(1.0, max_height / (TOP_ROOM + TAG_SIZE.y + BOTTOM_ROOM)))
		most = minf(text_s, maxf(1.0, max_height / (TOP_ROOM + COMPACT_H + BOTTOM_ROOM)))
	var fit_full := room / maxf(1.0, full_width(1.0))
	rows = 1
	if n == 0 or fit_full >= s * FULL_MIN_FIT:
		compact = false
		tag_scale = minf(s, fit_full) if n > 0 else s
		var t := tag_scale
		for i in n:
			_rects.append(Rect2(i * (TAG_SIZE.x + TAG_GAP) * t, TOP_ROOM * t, TAG_SIZE.x * t, TAG_SIZE.y * t))
	elif max_height <= 0.0:
		# Words kept (H22 #14): fitted tags on one row, else on two.
		compact = false
		var fit_one := room / maxf(1.0, _fitted_width(0, n))
		var split := n
		if fit_one < s * FULL_MIN_FIT and n > 1:
			rows = 2
			split = ceili(n / 2.0)
			tag_scale = minf(s, room / maxf(1.0, maxf(_fitted_width(0, split), _fitted_width(split, n))))
		else:
			tag_scale = minf(s, fit_one)
		var t := tag_scale
		var x := 0.0
		for i in n:
			if i == split:
				x = 0.0
			var row := 0 if i < split else 1
			var w := _fitted_tag_width(items[i]) * t
			_rects.append(Rect2(x, (TOP_ROOM + row * (TAG_SIZE.y + TOP_ROOM)) * t, w, TAG_SIZE.y * t))
			x += w + TAG_GAP * t
	else:
		compact = true
		tag_scale = clampf(room / maxf(1.0, compact_width(1.0)), 0.5, most)
		var x := 0.0
		for it in items:
			var w := _compact_tag_width(it) * tag_scale
			_rects.append(Rect2(x, TOP_ROOM * tag_scale, w, COMPACT_H * tag_scale))
			x += w + TAG_GAP * tag_scale
	if with_captions and rows == 1 and not compact:
		_place_captions()
	var h := (TOP_ROOM + (COMPACT_H if compact else TAG_SIZE.y) + BOTTOM_ROOM + (rows - 1) * (TAG_SIZE.y + TOP_ROOM)) * tag_scale
	if not is_equal_approx(custom_minimum_size.y, h):
		custom_minimum_size.y = h
	queue_redraw()


## Moves the tags right to make room for each caption before its group's first tag.
func _place_captions() -> void:
	var t := tag_scale
	var order := captions.duplicate()
	order.sort_custom(func(a: Array, b: Array) -> bool: return int(a[0]) < int(b[0]))
	var shift := 0.0
	var next_cap := 0
	for i in _rects.size():
		while next_cap < order.size() and int(order[next_cap][0]) == i:
			var words := String(order[next_cap][1])
			var w := Palette.mono().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(CAPTION_SIZE * t)).x
			var at := _rects[i].position.x + shift
			_caption_rects.append(Rect2(at, _rects[i].position.y, w, _rects[i].size.y))
			shift += w + CAPTION_GAP * t
			next_cap += 1
		_rects[i].position.x += shift


## The caption index under `at` (local), or -1.
func caption_at(at: Vector2) -> int:
	for i in _caption_rects.size():
		if _caption_rects[i].has_point(at):
			return i
	return -1


## The tag index under `at` (local), or -1.
func tag_at(at: Vector2) -> int:
	for i in _rects.size():
		var r := _rects[i]
		if at.x >= r.position.x and at.x <= r.end.x and (rows == 1 or (at.y >= r.position.y - TOP_ROOM * tag_scale and at.y <= r.end.y)):
			return i
	return -1


func _get_tooltip(at_position: Vector2) -> String:
	var ci := caption_at(at_position)
	if ci >= 0:
		var order := captions.duplicate()
		order.sort_custom(func(a: Array, b: Array) -> bool: return int(a[0]) < int(b[0]))
		_tip_title = String(order[ci][1])
		return UiTip.fold(String(order[ci][2]) if order[ci].size() > 2 else "")
	var i := tag_at(at_position)
	if i < 0:
		return ""
	var it: Array = items[i]
	_tip_title = tr(String(it[0]))
	var tip := String(it[3]) if it.size() > 3 else ""
	if tip == "":
		tip = "%s: %s%s" % [String(StatIcon.NAMES.get(icon_of(i), String(it[0]).capitalize())), String(it[1]), String(it[2]) if it.size() > 2 else ""]
	return UiTip.fold(tip)


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text, _tip_title) if for_text != "" else null


func _draw() -> void:
	var s := tag_scale
	if not _caption_rects.is_empty():
		var order := captions.duplicate()
		order.sort_custom(func(a: Array, b: Array) -> bool: return int(a[0]) < int(b[0]))
		var cfs := roundi(CAPTION_SIZE * s)
		var mono := Palette.mono()
		for k in mini(order.size(), _caption_rects.size()):
			var cr := _caption_rects[k]
			draw_line(Vector2(cr.end.x + CAPTION_GAP * s * 0.5, cr.position.y), Vector2(cr.end.x + CAPTION_GAP * s * 0.5, cr.end.y), Color(Palette.CELL_ACID, 0.35 * _caption_fade), 1.0)
			draw_string(mono, Vector2(cr.position.x, cr.get_center().y + mono.get_ascent(cfs) * 0.5 - mono.get_descent(cfs) * 0.25), String(order[k][1]), HORIZONTAL_ALIGNMENT_LEFT, -1, cfs, Color(Palette.CELL_ACID, _caption_fade))
		# The old captions fade out where they were (the cross-fade).
		for oc in _old_captions:
			var orr: Rect2 = oc[0]
			draw_string(mono, Vector2(orr.position.x, orr.get_center().y + mono.get_ascent(cfs) * 0.5 - mono.get_descent(cfs) * 0.25), String(oc[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, cfs, Color(Palette.CELL_ACID, 1.0 - _caption_fade))
	for i in mini(items.size(), _rects.size()):
		var it: Array = items[i]
		var box := _rects[i]
		var tilt := (-2.0 if i % 2 == 0 else 2.5) * PI / 180.0
		draw_set_transform(box.get_center(), tilt, Vector2.ONE * _bump_scale(String(it[0])))
		var r := Rect2(-box.size * 0.5, box.size)
		draw_rect(Rect2(r.position + Vector2(3, 4), r.size), Palette.SHADOW)
		draw_rect(r, PAPERS[i % PAPERS.size()])
		draw_rect(r, Color(Palette.INK, 0.45), false, 1.0)
		draw_rect(Rect2(Vector2(-13, r.position.y - 5), Vector2(26, 9)), Palette.NOTE_TAPE)
		var value := shown_value(i)
		var vs := roundi(VALUE_SIZE * s)
		var icon_c: Vector2
		var value_at: Vector2
		if compact:
			icon_c = r.position + Vector2(PAD + ICON_R, COMPACT_H * 0.5) * s
			value_at = r.position + Vector2(PAD + ICON_R * 2.0 + 5.0, COMPACT_H * 0.5 + VALUE_SIZE * 0.36) * s
		else:
			draw_string(Palette.marker(), r.position + Vector2(PAD, 14) * s, tag_name(i), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - 10.0 * s, roundi(NAME_SIZE * s), Palette.INK)
			icon_c = r.position + Vector2(PAD + ICON_R, 30) * s
			value_at = r.position + Vector2(PAD + ICON_R * 2.0 + 5.0, 38) * s
		StatIcon.draw(self, icon_c, ICON_R * s, icon_of(i), Palette.INK)
		draw_string(Palette.display(), value_at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, vs, Palette.INK)
		if it.size() > 2 and String(it[2]) != "":
			var vw := Palette.display().get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, vs).x
			draw_string(Palette.marker(), value_at + Vector2(vw + 2.0 * s, -1.0 * s), String(it[2]), HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(SUFFIX_SIZE * s), Palette.INK)
		if _refused_tag != "" and String(it[0]) == _refused_tag:
			# ANIM-R2 E9: a refusal for want of this (Cycles): the tag flashes red and
			# "PRICE > MONEY" shows under it.
			var red := Color(REFUSED_COLOR, maxf(REFUSED_MIN_ALPHA, refusal_alpha))
			draw_rect(r, Color(red, red.a * REFUSED_FILL), true)
			draw_rect(r, red, false, 2.0)
			var rfs := roundi(VALUE_SIZE * s * REFUSED_TEXT_SHARE)
			# ANIM-R4 C7: wider than its tag, the words wrap at their dot (NEED 53 over HAVE 5):
			# on one line they ran past the Modem's panel edge at 1.6.
			var lines := refusal_lines(_refused_text, r.size.x, rfs)
			for li in lines.size():
				var tw := Palette.display().get_string_size(lines[li], HORIZONTAL_ALIGNMENT_LEFT, -1, rfs).x
				var at := Vector2(r.get_center().x - tw * 0.5, r.end.y + rfs * (li + 1))
				draw_string_outline(Palette.display(), at, lines[li], HORIZONTAL_ALIGNMENT_LEFT, -1, rfs, 4, Palette.NIGHT_SKY)
				draw_string(Palette.display(), at, lines[li], HORIZONTAL_ALIGNMENT_LEFT, -1, rfs, red)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
