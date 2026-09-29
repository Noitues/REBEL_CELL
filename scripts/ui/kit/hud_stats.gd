class_name HudStats
extends Control
## Ransom-note stat tags for the top bar: each stat on its own taped paper tag (paper,
## pink, yellow), tilted a little. Decoration of numbers the scene provides; hovering a
## tag shows what the number means (the item's tooltip, H20). Clicks pass through.
##
## Art pass W8b (ART_BIBLE §5.2, §6.9): one icon + label + value per tag, the value in
## Anton `title`, the label in Share Tech Mono CAPS at `caption` (a handwritten label under
## 16 px broke §4.1). The row is ONE row at every text scale and its height depends on the
## text scale alone (never on the values):
## - tags share the width evenly (never wider than a full tag, TAG_W) and don't grow with a
##   long value: a value that doesn't fit its tag steps down the type scale (title, label,
##   body, caption; never under caption);
## - below FOLD_SCALE a tag shows its label over its icon and value; from FOLD_SCALE up
##   (and whenever a label doesn't fit its tag) the labels fold away and the words stay in
##   each tag's tooltip, so the row keeps one line and the bar a short, fixed height;
## - the group captions ("CAMPAIGN", "THIS RUN") fold to a rule the same way (their words
##   in the rule's tooltip);
## - a fight (`max_height` set) keeps its band height: folded tags, the value stepping down
##   until it fits the height.
## A tag that is a drop target (CARDS, DAEMONS) shows FOCUS brackets while a matching item
## is carried (`hot_kinds`, set by HudBar.watch_drops). High contrast draws the tags square
## with a heavy ink edge and no shadow (Settings.high_contrast).

## A full tag's width and height at text scale 1.0 (the preferred and largest width), and
## a folded tag's height (px).
const TAG_W := 100.0
const TAG_H := 44.0
const TAG_H_FOLDED := 34.0
## The gap between tags (px at scale 1.0).
const TAG_GAP := UiTheme.SP_S
## From this text scale up the labels fold into the tooltip (the map key's fold scale).
const FOLD_SCALE := 1.3
## Space above the tags (the tape) and below them (px at scale 1.0).
const TOP_ROOM := 7.0
const BOTTOM_ROOM := 3.0
## The icon's radius, the inner padding, the gap between icon and value and the value's
## baseline share of its size (a digit's half height in Anton) at scale 1.0.
const ICON_R := 9.0
const PAD := 6.0
const PAD_V := 4.0
const ICON_GAP := 5.0
const DIGIT_HALF := 0.36
## The value's type steps, largest first (§6.9: `title`, stepping down to fit).
const VALUE_STEPS: Array[int] = [UiTheme.TITLE, UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]
## The tape's size and the drop shadow's offset (px at scale 1.0), the tags' tilt (degrees,
## alternating), the outline's alpha and the high-contrast edge (px).
const TAPE := Vector2(26, 9)
const SHADOW_OFFSET := Vector2(3, 4)
const TILT_EVEN := -2.0
const TILT_ODD := 2.5
const OUTLINE_ALPHA := 0.45
const HC_EDGE := 2.0
## A folded caption's rule: its width (px at scale 1.0) and alpha.
const RULE_W := 10.0
const RULE_ALPHA := 0.35
## What a tag shows for a number that doesn't exist yet (no best ICE): never "none".
const NO_VALUE := "—"
## The tag stocks, in turn (§3.2 paper and note tokens).
const PAPERS: Array[Color] = [Palette.NOTE_PAPER, Palette.STICKER_PINK, Palette.NOTE_YELLOW, Palette.PAPER]

## [[name, value, suffix, tooltip, icon kind], ...] (tooltip and icon optional: the icon
## defaults to StatIcon.kind_for(name)).
var items: Array = []:
	set(v):
		_note_changes(items, v)
		items = v
		_relayout()
## True when the labels are folded away (icon and value only) and the text scale the row
## is drawn at (read-only).
var compact: bool = false
var tag_scale: float = 1.0
## Rows of tags: always 1 (§5.2 "never wraps"; kept for callers).
var rows: int = 1
## When above 0, the tags never make the row taller than this (px): a fight keeps its
## height under the top bar (the netrun sets it while the combat scene is up).
var max_height: float = 0.0:
	set(v):
		max_height = v
		_relayout()
## §6.9: StatIcon kinds whose tag is a drop target for the item being carried now (FOCUS
## brackets round it); empty when nothing is carried.
var hot_kinds: Array[StringName] = []:
	set(v):
		hot_kinds = v
		queue_redraw()
var _rects: Array[Rect2] = []
var _tip_title: String = ""
## The value's font size in use (px; the same on every tag) and the label's.
var _value_px: int = UiTheme.TITLE
var _label_px: int = UiTheme.CAPTION
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
## True when the captions are folded to their rule (their words in its tooltip).
var _captions_folded: bool = false
## The gap after a caption at scale 1.0 (px).
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
	custom_minimum_size = Vector2(0, row_height(1.0))


func _ready() -> void:
	Settings.changed.connect(_relayout)
	_relayout()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_relayout()


## §5.2: the row's height at text scale `s` outside a fight (px): the same for every set
## of tags and values, one row.
static func row_height(s: float) -> float:
	var tag_h := TAG_H_FOLDED if s >= FOLD_SCALE - 0.001 else TAG_H
	return (TOP_ROOM + tag_h + BOTTOM_ROOM) * s


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
## the next change under reduce effects and headless. §3.3: the flash is HARM.
const REFUSED_COLOR := Palette.HARM
const REFUSED_MIN_ALPHA := 0.45
const REFUSED_FILL := 0.35
const REFUSED_OUTLINE := 2.0
const REFUSED_TEXT_OUTLINE := 4
## The refusal's words under the tag: a type step (§4.2).
const REFUSED_STEP := UiTheme.BODY
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


## A tag's drawn scale while it bumps (1 at rest): up to the entry's amplitude and back.
func _bump_scale(key: String) -> float:
	var m: Dictionary = _moving.get(key, {})
	if m.is_empty():
		return 1.0
	var t := float(m["bump"])
	var up := t / Motion.POP_GROW_SHARE if t < Motion.POP_GROW_SHARE else 1.0 - (t - Motion.POP_GROW_SHARE) / (1.0 - Motion.POP_GROW_SHARE)
	return lerpf(1.0, Motion.amplitude(&"sticky_bump"), clampf(up, 0.0, 1.0))


static func _caption_words(a: Array) -> String:
	var parts := PackedStringArray()
	for c in a:
		parts.append(String(c[1]))
	return "|".join(parts)


func _note_caption_change(new: Array) -> void:
	if captions.is_empty() or _caption_words(captions) == _caption_words(new) or not Motion.live(&"caption_crossfade") or not is_inside_tree():
		return
	var order := _caption_order()
	_old_captions = []
	if not _captions_folded:
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


## Tag `i`'s name as drawn and measured: translated (H23 S16; the icon still follows the
## name's own key). H24 S4: `tr`, so a bar shown as given still translates its keys.
func tag_name(i: int) -> String:
	return tr(String(items[i][0])) if i >= 0 and i < items.size() else ""


## The icon of tag `i`.
func icon_of(i: int) -> StringName:
	var it: Array = items[i]
	if it.size() > 4 and String(it[4]) != "":
		return StringName(String(it[4]))
	return StatIcon.kind_for(String(it[0]))


## Width the full tags take at scale `s` (their preferred width).
func full_width(s: float = 1.0) -> float:
	return items.size() * (TAG_W + TAG_GAP) * s


## Width the folded tags need at scale `s` with their values at `title` (the least room
## the row wants).
func compact_width(s: float = 1.0) -> float:
	var total := 0.0
	for it in items:
		total += _value_width(it, s, UiTheme.font_px_at(UiTheme.TITLE, s)) + (PAD * 2.0 + TAG_GAP) * s
	return total


## Each tag's rect (local), as laid out now.
func tag_rects() -> Array[Rect2]:
	return _rects.duplicate()


## The value font size in use (px; tests).
func value_font_size() -> int:
	return _value_px


## The label font size in use (px; tests): the `caption` step at the scale drawn.
func label_font_size() -> int:
	return _label_px


## Width of tag `it`'s icon, value and suffix at scale `s` with the value at `vfs` px.
func _value_width(it: Array, s: float, vfs: int) -> float:
	var w := ICON_R * 2.0 * s + ICON_GAP * s + Palette.display().get_string_size(String(it[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, vfs).x
	if it.size() > 2 and String(it[2]) != "":
		w += Palette.display().get_string_size(String(it[2]), HORIZONTAL_ALIGNMENT_LEFT, -1, _suffix_px(s)).x
	return w


## The suffix ("/100") size at scale `s`: the caption step (§4.2).
static func _suffix_px(s: float) -> int:
	return UiTheme.font_px_at(UiTheme.CAPTION, s)


## The captions in tag order.
func _caption_order() -> Array:
	var order := captions.duplicate()
	order.sort_custom(func(a: Array, b: Array) -> bool: return int(a[0]) < int(b[0]))
	return order


## The captions' widths at scale `s`, each with its gap (folded: the rule's width).
func _caption_width(s: float, folded: bool) -> float:
	var w := 0.0
	for c in captions:
		if folded:
			w += (RULE_W + CAPTION_GAP) * s
		else:
			w += Palette.mono().get_string_size(String(c[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px_at(UiTheme.CAPTION, s)).x + CAPTION_GAP * s
	return w


## Whether the captions are drawn now (outside a fight): their words, or folded to rules.
func captions_shown() -> bool:
	return not _caption_rects.is_empty()


## True when the captions are folded to their rules (tests).
func captions_folded() -> bool:
	return _captions_folded


## The caption rects as laid out now (local).
func caption_rects() -> Array[Rect2]:
	return _caption_rects.duplicate()


func _relayout() -> void:
	var s := Settings.text_scale
	var n := items.size()
	var room := size.x if size.x > 1.0 else full_width(s)
	_rects.clear()
	_caption_rects.clear()
	var fight := max_height > 0.0
	var with_captions := not captions.is_empty() and not fight and n > 0
	tag_scale = s
	rows = 1
	_label_px = UiTheme.font_px_at(UiTheme.CAPTION, s)
	# Folded by the text scale, in a fight, or when a label doesn't fit its tag.
	var folded := fight or s >= FOLD_SCALE - 0.001
	_captions_folded = folded
	var caps_w := _caption_width(s, _captions_folded) if with_captions else 0.0
	var gap := TAG_GAP * s
	var tag_w := minf(TAG_W * s, (room - caps_w - gap * maxf(0.0, n - 1)) / maxf(1.0, n)) if n > 0 else 0.0
	tag_w = maxf(1.0, tag_w)
	if not folded:
		for i in n:
			if Palette.mono().get_string_size(tag_name(i), HORIZONTAL_ALIGNMENT_LEFT, -1, _label_px).x + PAD * 2.0 * s > tag_w:
				folded = true
				break
	compact = folded
	var tag_h := (TAG_H_FOLDED if s >= FOLD_SCALE - 0.001 or fight else TAG_H) * s
	var room_v := TOP_ROOM * s + BOTTOM_ROOM * s
	if fight:
		tag_h = minf(tag_h, maxf(1.0, max_height - room_v))
	# The value's step: the largest that fits every tag's width (and a fight's height).
	_value_px = UiTheme.font_px_at(VALUE_STEPS[VALUE_STEPS.size() - 1], s)
	for step in VALUE_STEPS:
		var px := UiTheme.font_px_at(step, s)
		var fits := true
		if fight and Palette.display().get_height(px) > tag_h - PAD_V * 2.0 * s:
			fits = false
		for it in items:
			if not fits:
				break
			if _value_width(it, s, px) + PAD * 2.0 * s > tag_w:
				fits = false
		if fits:
			_value_px = px
			break
	for i in n:
		_rects.append(Rect2(i * (tag_w + gap), TOP_ROOM * s, tag_w, tag_h))
	if with_captions:
		_place_captions(s)
	var h := room_v + tag_h
	if not is_equal_approx(custom_minimum_size.y, h):
		custom_minimum_size.y = h
	queue_redraw()


## Moves the tags right to make room for each caption before its group's first tag.
func _place_captions(s: float) -> void:
	var order := _caption_order()
	var shift := 0.0
	var next_cap := 0
	var fs := UiTheme.font_px_at(UiTheme.CAPTION, s)
	for i in _rects.size():
		while next_cap < order.size() and int(order[next_cap][0]) == i:
			var w := RULE_W * s if _captions_folded else Palette.mono().get_string_size(String(order[next_cap][1]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var at := _rects[i].position.x + shift
			_caption_rects.append(Rect2(at, _rects[i].position.y, w, _rects[i].size.y))
			shift += w + CAPTION_GAP * s
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
		if at.x >= r.position.x and at.x <= r.end.x:
			return i
	return -1


func _get_tooltip(at_position: Vector2) -> String:
	var ci := caption_at(at_position)
	if ci >= 0:
		var order := _caption_order()
		_tip_title = String(order[ci][1])
		return UiTip.fold(String(order[ci][2]) if order[ci].size() > 2 else "")
	var i := tag_at(at_position)
	if i < 0:
		return ""
	var it: Array = items[i]
	# §6.9: the tag's words stay in its tooltip's title when its label is folded away.
	_tip_title = tr(String(it[0]))
	var tip := String(it[3]) if it.size() > 3 else ""
	if tip == "":
		tip = "%s: %s%s" % [String(StatIcon.NAMES.get(icon_of(i), String(it[0]).capitalize())), String(it[1]), String(it[2]) if it.size() > 2 else ""]
	return UiTip.fold(tip)


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text, _tip_title) if for_text != "" else null


func _draw() -> void:
	var s := tag_scale
	var hc := Settings.high_contrast
	_draw_captions(s)
	var mono := Palette.mono()
	var anton := Palette.display()
	for i in mini(items.size(), _rects.size()):
		var it: Array = items[i]
		var box := _rects[i]
		var tilt := 0.0 if hc else deg_to_rad(TILT_EVEN if i % 2 == 0 else TILT_ODD)
		draw_set_transform(box.get_center(), tilt, Vector2.ONE * _bump_scale(String(it[0])))
		var r := Rect2(-box.size * 0.5, box.size)
		if not hc:
			draw_rect(Rect2(r.position + SHADOW_OFFSET * s, r.size), Palette.SHADOW)
		draw_rect(r, PAPERS[i % PAPERS.size()])
		draw_rect(r, Palette.INK if hc else Color(Palette.INK, OUTLINE_ALPHA), false, HC_EDGE * s if hc else 1.0)
		draw_rect(Rect2(Vector2(-TAPE.x * 0.5 * s, r.position.y - TAPE.y * 0.55 * s), TAPE * s), Palette.NOTE_TAPE)
		var value := shown_value(i)
		var value_mid: float
		if compact:
			value_mid = r.get_center().y
		else:
			var label_base := r.position.y + PAD_V * s + mono.get_ascent(_label_px)
			draw_string(mono, Vector2(r.position.x + PAD * s, label_base), tag_name(i), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD * 2.0 * s, _label_px, Palette.INK)
			value_mid = (label_base + mono.get_descent(_label_px) + r.end.y - PAD_V * s) * 0.5
		# Icon and value centred together in the tag (the value never grows the tag).
		var vw := _value_width(it, s, _value_px)
		var x0 := r.position.x + maxf(PAD * s, (r.size.x - vw) * 0.5)
		StatIcon.draw(self, Vector2(x0 + ICON_R * s, value_mid), ICON_R * s, icon_of(i), Palette.INK)
		var value_at := Vector2(x0 + (ICON_R * 2.0 + ICON_GAP) * s, value_mid + _value_px * DIGIT_HALF)
		draw_string(anton, value_at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, _value_px, Palette.INK)
		if it.size() > 2 and String(it[2]) != "":
			var w := anton.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, _value_px).x
			draw_string(anton, value_at + Vector2(w, 0), String(it[2]), HORIZONTAL_ALIGNMENT_LEFT, -1, _suffix_px(s), Palette.INK)
		if _refused_tag != "" and String(it[0]) == _refused_tag:
			_draw_refusal(r, s)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		if hot_kinds.has(icon_of(i)):
			# §6.9: a drop target for the carried item: FOCUS brackets round the tag.
			StyleBoxBrackets.draw_on(self, box, Palette.FOCUS)


## The group captions: their words (below FOLD_SCALE) or a rule each (folded; the words in
## the rule's tooltip), with the old ones fading out during a cross-fade.
func _draw_captions(s: float) -> void:
	if _caption_rects.is_empty():
		return
	var order := _caption_order()
	var cfs := UiTheme.font_px_at(UiTheme.CAPTION, s)
	var mono := Palette.mono()
	for k in mini(order.size(), _caption_rects.size()):
		var cr := _caption_rects[k]
		if _captions_folded:
			var x := cr.get_center().x
			draw_line(Vector2(x, cr.position.y), Vector2(x, cr.end.y), Color(Palette.FOCUS, _caption_fade), maxf(1.0, s))
			continue
		draw_line(Vector2(cr.end.x + CAPTION_GAP * s * 0.5, cr.position.y), Vector2(cr.end.x + CAPTION_GAP * s * 0.5, cr.end.y), Color(Palette.FOCUS, RULE_ALPHA * _caption_fade), 1.0)
		draw_string(mono, Vector2(cr.position.x, cr.get_center().y + mono.get_ascent(cfs) * 0.5 - mono.get_descent(cfs) * 0.25), String(order[k][1]), HORIZONTAL_ALIGNMENT_LEFT, -1, cfs, Color(Palette.FOCUS, _caption_fade))
	# The old captions fade out where they were (the cross-fade).
	for oc in _old_captions:
		var orr: Rect2 = oc[0]
		draw_string(mono, Vector2(orr.position.x, orr.get_center().y + mono.get_ascent(cfs) * 0.5 - mono.get_descent(cfs) * 0.25), String(oc[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, cfs, Color(Palette.FOCUS, 1.0 - _caption_fade))


## ANIM-R2 E9: a refusal for want of this (Cycles): the tag flashes HARM and "NEED n · HAVE
## m" shows under it (drawn in the tag's own transform `r`).
func _draw_refusal(r: Rect2, s: float) -> void:
	var red := Color(REFUSED_COLOR, maxf(REFUSED_MIN_ALPHA, refusal_alpha))
	draw_rect(r, Color(red, red.a * REFUSED_FILL), true)
	draw_rect(r, red, false, REFUSED_OUTLINE * s)
	var rfs := UiTheme.font_px_at(REFUSED_STEP, s)
	# ANIM-R4 C7: wider than its tag, the words wrap at their dot (NEED 53 over HAVE 5): on
	# one line they ran past the Modem's panel edge at 1.6.
	var lines := refusal_lines(_refused_text, r.size.x, rfs)
	for li in lines.size():
		var tw := Palette.display().get_string_size(lines[li], HORIZONTAL_ALIGNMENT_LEFT, -1, rfs).x
		var at := Vector2(r.get_center().x - tw * 0.5, r.end.y + rfs * (li + 1))
		draw_string_outline(Palette.display(), at, lines[li], HORIZONTAL_ALIGNMENT_LEFT, -1, rfs, REFUSED_TEXT_OUTLINE, Palette.NIGHT_SKY)
		draw_string(Palette.display(), at, lines[li], HORIZONTAL_ALIGNMENT_LEFT, -1, rfs, red)
