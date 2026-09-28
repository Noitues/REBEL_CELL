class_name OutcomeRow
extends Control
## What a Terminal event choice does, as icons with numbers (H21 #13: the outcome was in
## words only): each item is a StatIcon (the resource's own icon: coin for Cycles, flame
## for Heat, heart for HP, blueprint for Schematics, card / chip / daemon / crate /
## operative for what the choice gives) and a signed amount, green when it helps and red
## when it costs. `attach` puts the row under a choice button's words. `of_choice` reads
## the amounts from the choice's data the way NetrunSession applies them (Heat through
## HeatRules.scaled_delta). View only.

## Icon radius, gap after an icon and between items at text scale 1.0 (px).
const ICON_R := 8.0
const ICON_GAP := 3.0
const ITEM_GAP := 12.0
## Amount colours on the paper choice notes.
const GOOD := Color("#17702c")
const BAD := Color("#b3122f")
## Why an amount is less than the choice's number (tooltip words, H22 #12).
const CAPPED_WORDS := {StatIcon.HP: "HP is full", StatIcon.HEAT: "Heat stops at its limit"} # TR
## A reward's kind in the button's words (one of it).
const REWARD_WORDS := {StatIcon.CARDS: "Card", StatIcon.FIRMWARE: "Firmware", StatIcon.DAEMON: "Daemon", StatIcon.ARMORY: "Asset"} # TR
## StatIcon.NAMES' words (translation keys; H24 S3: outcome words are translated).
const RESOURCE_WORDS := ["Heat", "Schematics", "Home server", "Exploits", "Raids", "ICE", "Crew", "HP", "Cycles", "Cards", # TR
	"Rank", "Banked", "Armory", "Fights won", "Elites", "Campaigns", "Won", "Runs", "Badges", "Firmware", "Daemon", "Operative"] # TR
## H24 S9: the neutral item of a choice that changes nothing (drawn as an empty-set mark).
const NO_CHANGE := &"none"

## [{kind: StringName, amount: int, text: String, good: bool, name: String}]
var items: Array[Dictionary] = []


func _init(p_items: Array[Dictionary] = []) -> void:
	name = "OutcomeRow"
	items = p_items
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


## The outcome of `choice` for session `s`: costs first, then gains, then the reward.
## H22 #12: the amounts the choice will really apply now, read (not applied) the way
## NetrunSession applies them in order: a heal stops at max HP ("+0" at full HP), Heat
## stops at 0 and at the maximum (a sink of 3 at Heat 1 shows -1); a rescue names no class
## (the class is rolled from the roster when it happens).
static func of_choice(s: NetrunSession, choice: EventChoiceData) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if choice == null:
		return out
	if choice.cycle_cost > 0:
		out.append(_item(StatIcon.CYCLES, -choice.cycle_cost, false))
	var hp_loss := s.choice_hp_loss(choice)
	if hp_loss > 0:
		out.append(_item(StatIcon.HP, -hp_loss, false))
	var op := s.run.operative
	var hp := maxi(0, op.hp - choice.hp_cost)
	var heat := s.campaign.heat
	for e in choice.effects:
		if e == null:
			continue
		match e.type:
			RC.EffectType.GAIN_CYCLES:
				if e.amount != 0:
					out.append(_item(StatIcon.CYCLES, e.amount, e.amount > 0))
			RC.EffectType.MODIFY_HEAT:
				var dh := HeatRules.scaled_delta(s.campaign, e.amount, s.config)
				var applied := clampi(heat + dh, 0, s.config.heat_max) - heat
				heat += applied
				var hi := _item(StatIcon.HEAT, applied, dh <= 0)
				hi["capped"] = applied != dh
				out.append(hi)
			RC.EffectType.HEAL:
				var healed := mini(e.amount, op.max_hp - hp)
				hp += healed
				var it := _item(StatIcon.HP, healed, true)
				it["capped"] = healed != e.amount
				out.append(it)
			RC.EffectType.DEAL_DAMAGE:
				hp = maxi(0, hp - e.amount)
			RC.EffectType.GAIN_SCHEMATICS:
				out.append(_item(StatIcon.SCHEMATICS, e.amount, e.amount >= 0))
	if choice.reward != null:
		var kind := StatIcon.OPERATIVE
		if choice.reward is CardData:
			kind = StatIcon.CARDS
		elif choice.reward is FirmwareData:
			kind = StatIcon.FIRMWARE
		elif choice.reward is DaemonData:
			kind = StatIcon.DAEMON
		elif choice.reward is DefenseAssetData:
			kind = StatIcon.ARMORY
		var it := _item(kind, 1, true)
		# A rescue's class is rolled from the roster: no class name (H22 #12).
		it["name"] = TextDb.t(choice.reward, "display_name") if kind != StatIcon.OPERATIVE and "display_name" in choice.reward else ""
		out.append(it)
	return out


## The items a choice shows (H23 S9: "(+0 Heat) +0" showed a change that is none): the
## amounts that change something and the rewards; a zero amount shows no number (the
## tooltip still says why, e.g. "HP is full").
static func shown(p_items: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for it in p_items:
		if int(it.get("amount", 0)) != 0:
			out.append(it)
	return out


## The row in the words a choice button carries after its label ("-25 Cycles, -2 Heat,
## Card: Jam, rescue an operative"), with the capped amounts (H22 #12); zero amounts are
## left out (H23 S9).
static func words(p_items: Array[Dictionary]) -> String:
	var parts := PackedStringArray()
	for it in shown(p_items):
		var kind := StringName(it["kind"])
		if kind == StatIcon.OPERATIVE:
			parts.append(TranslationServer.translate("rescue an operative"))
		elif String(it.get("name", "")) != "":
			parts.append("%s: %s" % [TranslationServer.translate(String(REWARD_WORDS.get(kind, StatIcon.NAMES.get(kind, String(kind))))), it["name"]])
		else:
			parts.append("%s %s" % [it["text"], _name_of(kind)])
	return ", ".join(parts)


## A resource's name in the player's language (StatIcon.NAMES).
static func _name_of(kind: StringName) -> String:
	return TranslationServer.translate(String(StatIcon.NAMES.get(kind, String(kind))))


static func _item(kind: StringName, amount: int, good: bool) -> Dictionary:
	# H24 S2: the sign from TextDb.signed.
	return {"kind": kind, "amount": amount, "text": TextDb.signed(amount), "good": good, "name": "", "capped": false}


## The row a choice that changes nothing shows (H24 S9: it showed nothing at all, and a
## player who cannot read the words could not tell): one neutral empty-set mark and "no
## change".
static func no_change() -> Array[Dictionary]:
	return [{"kind": NO_CHANGE, "amount": 0, "text": TranslationServer.translate("no change"), "good": true, "neutral": true, "name": "", "capped": false}] as Array[Dictionary]


## The row in words (a tooltip line): "Cycles -25, Heat +2, Card: Jam".
static func describe(p_items: Array[Dictionary]) -> String:
	var parts := PackedStringArray()
	for it in p_items:
		var what := _name_of(StringName(it["kind"]))
		var part := ("%s: %s" % [what, it["name"]]) if String(it.get("name", "")) != "" else "%s %s" % [what, it["text"]]
		if int(it.get("amount", 0)) == 0:
			part = TranslationServer.translate("%s: no change") % what  # H23 S9: no "+0"
		if bool(it.get("capped", false)):
			part += " (%s)" % TranslationServer.translate(String(CAPPED_WORDS.get(it["kind"], "capped")))
		parts.append(part)
	return ", ".join(parts)


## Puts `row` under the words of choice button `b`: the button's styles get room at the
## bottom (recomputed when the text size changes) and the row sits there.
static func attach(b: Button, row: OutcomeRow) -> void:
	b.add_child(row)
	row._fit_parent()


func _scale() -> float:
	return maxf(1.0, get_theme_font_size(&"font_size", &"Label") / float(UiTheme.BASE_SIZE))


func _font() -> Font:
	return get_theme_font(&"font", &"Label")


func _get_minimum_size() -> Vector2:
	var s := _scale()
	# ANIM-R1 M9: the row wraps inside its choice (at 1.6 six outcome items pushed the page
	# off the screen): as narrow as its widest item, as tall as its lines at its width.
	var w := 0.0
	for it in items:
		w = maxf(w, _item_width(it))
	var lines := maxi(1, lines_at(size.x if size.x > 0.0 else _one_line_width()).size())
	return Vector2(w, _line_height() * lines + LINE_GAP * s * (lines - 1))


## The width of one item: its icon, the gap, its words (px).
func _item_width(it: Dictionary) -> float:
	var s := _scale()
	var fs := get_theme_font_size(&"font_size", &"Label")
	return (ICON_R * 2.0 + ICON_GAP) * s + _font().get_string_size(String(it["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x


## Every item on one line (px).
func _one_line_width() -> float:
	var w := 0.0
	for it in items:
		w += _item_width(it) + ITEM_GAP * _scale()
	return w


func _line_height() -> float:
	var fs := get_theme_font_size(&"font_size", &"Label")
	return maxf(ICON_R * 2.0 * _scale(), _font().get_height(fs))


## ANIM-R1 M9: the items laid out in lines no wider than `width` (each line an Array of
## item indices, in order; an item wider than the line still gets a line of its own).
func lines_at(width: float) -> Array[Array]:
	var out: Array[Array] = []
	var line: Array = []
	var x := 0.0
	var gap := ITEM_GAP * _scale()
	for k in items.size():
		var w := _item_width(items[k])
		if not line.is_empty() and x + w > width:
			out.append(line)
			line = []
			x = 0.0
		line.append(k)
		x += w + gap
	if not line.is_empty():
		out.append(line)
	return out


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		# ANIM-R2 E2: the button's own boxes are read again under the new theme (read before
		# the button was in the tree they were Godot's default grey boxes: the event's notes
		# lost their paper).
		_base_margins.clear()
		_fitted_h = -1.0
		update_minimum_size()
		_fit_parent.call_deferred()
		queue_redraw()


## Room at the bottom of the parent button for the row (its lines at the button's width;
## again whenever the button's width changes); the row placed in it.
func _fit_parent() -> void:
	var b := get_parent() as Button
	if b == null or items.is_empty() or not b.is_inside_tree():
		return  # its theme (and so its boxes) is known once it is in the tree
	if not b.resized.is_connected(_on_parent_resized):
		b.resized.connect(_on_parent_resized)
	var left := 0.0
	var bottom := 0.0
	var normal := b.get_theme_stylebox(&"normal")
	if normal != null and not _base_margins.has(&"normal"):
		for st in [&"normal", &"hover", &"pressed", &"hover_pressed", &"focus", &"disabled"]:
			b.remove_theme_stylebox_override(st)
			var sb := b.get_theme_stylebox(st)
			if sb != null:
				_base_margins[st] = [sb.get_margin(SIDE_LEFT), sb.get_margin(SIDE_BOTTOM), sb]
	if not _base_margins.has(&"normal"):
		return
	left = float(_base_margins[&"normal"][0])
	bottom = float(_base_margins[&"normal"][1])
	var width := b.size.x - left * 2.0 if b.size.x > left * 2.0 else _one_line_width()
	var lines := maxi(1, lines_at(width).size())
	var h := _line_height() * lines + LINE_GAP * _scale() * (lines - 1)
	if is_equal_approx(h, _fitted_h):
		return
	_fitted_h = h
	for st in _base_margins:
		var sb: StyleBox = _base_margins[st][2]
		var room := sb.duplicate() as StyleBox
		room.content_margin_bottom = float(_base_margins[st][1]) + h + 4.0
		b.add_theme_stylebox_override(st, room)
	set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	offset_left = left
	offset_right = -left
	offset_bottom = -bottom
	offset_top = -bottom - h
	update_minimum_size()
	queue_redraw()


func _on_parent_resized() -> void:
	_fit_parent.call_deferred()


## The parent button's own style boxes (and their left and bottom margins) before the row
## made room in them, and the row height the room was made for.
var _base_margins: Dictionary = {}
var _fitted_h: float = -1.0
## Gap between the row's lines at text scale 1.0 (px).
const LINE_GAP := 2.0


func _draw() -> void:
	var s := _scale()
	var fs := get_theme_font_size(&"font_size", &"Label")
	var font := _font()
	var line_h := _line_height()
	var y0 := 0.0
	for line: Array in lines_at(size.x):
		var x := 0.0
		var mid := y0 + line_h * 0.5
		for k: int in line:
			var it: Dictionary = items[k]
			var col := GOOD if bool(it["good"]) else BAD
			if bool(it.get("neutral", false)):
				col = Palette.INK
			if StringName(it["kind"]) == NO_CHANGE:
				# The empty-set mark: a ring with a slash (no StatIcon means "nothing").
				var c := Vector2(x + ICON_R * s, mid)
				draw_arc(c, ICON_R * s * 0.8, 0.0, TAU, 18, Palette.INK, 1.6 * s, true)
				draw_line(c + Vector2(-ICON_R, ICON_R) * s, c + Vector2(ICON_R, -ICON_R) * s, Palette.INK, 1.6 * s, true)
			else:
				StatIcon.draw(self, Vector2(x + ICON_R * s, mid), ICON_R * s, StringName(it["kind"]), Palette.INK)
			x += (ICON_R * 2.0 + ICON_GAP) * s
			var t := String(it["text"])
			draw_string(font, Vector2(x, mid + font.get_ascent(fs) * 0.5 - font.get_descent(fs) * 0.25), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
			x += font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + ITEM_GAP * s
		y0 += line_h + LINE_GAP * s