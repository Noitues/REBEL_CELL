class_name CombatLegend
extends PanelContainer
## W2-A3: the fight's legend (key [L], the "?" chip beside Settings, and the pad through that
## chip's focus): every symbol and status a fight draws, each with its code and what it does.
## The rows come from `entries()` (pure, so a test reads what a player would), drawn as plain
## labels in a scroll area so the page holds at text scale 1.0 / 1.6 / 2.0. View only.

signal closed

## The input action that opens it (Settings.RUNTIME_ACTIONS).
const ACTION := &"open_legend"
## The legend's share of the viewport and its least / most size (px).
const VIEW_SHARE := Vector2(0.62, 0.86)
const SIZE_MIN := Vector2(520, 360)
const SIZE_MAX := Vector2(980, 700)
const PAD := 14
const ROW_GAP := 4
## The code column's width (px at scale 1).
const CODE_W := 92.0

var scroll: ScrollContainer
var close_button: Button


## The legend's rows: [{section, code, title, text}], in reading order. `code` is the mark as
## drawn in the fight ("OVFL", "1/0", "D 0"), `title` its whole name, `text` what it does.
static func entries() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var sec_slices := TranslationServer.translate("SLICES (on the wheels)")
	for t in Palette.SLICE_NAMES:
		var code := String(Palette.SLICE_NAMES[t])
		if t == RC.SliceType.NULL:
			code = "1/0"
		out.append({"section": sec_slices, "code": code, "title": TranslationServer.translate(String(Palette.SLICE_WORDS.get(t, ""))),
			"text": _body(String(Codex.SLICE_TYPE_TEXT.get(t, "")))})
	var sec_status := TranslationServer.translate("STATUSES (on a slice)")
	for st in Codex.STATUS_TEXT:
		out.append({"section": sec_status, "code": String(Palette.STATUS_GLYPHS.get(st, "")), "title": TranslationServer.translate(String(Palette.STATUS_WORDS.get(st, ""))),
			"text": _body(String(Codex.STATUS_TEXT[st]))})
	var sec_aim := TranslationServer.translate("AIM (the tag on a pointer)")
	for tier in Codex.TIER_TEXT:
		out.append({"section": sec_aim, "code": TranslationServer.translate(String(Palette.TIER_NAMES.get(tier, ""))), "title": "",
			"text": String(Codex.TIER_TEXT[tier])})
	var sec_read := TranslationServer.translate("READOUTS (HP, RAM and the chips)")
	for r in readouts():
		r["section"] = sec_read
		out.append(r)
	return out


## The HUD readouts (not slices or statuses): the chips beside a wheel's HP, the RAM panel and
## the Daemon badge.
static func readouts() -> Array[Dictionary]:
	var t := TranslationServer
	return [
		{"code": "60/60", "title": t.translate("HP"), "text": t.translate("Hit points now and the most. At 0 the wheel's owner is down.")},
		{"code": t.translate("HP -11"), "title": t.translate("HP lost"), "text": t.translate("What SEND IT would take off HP if pressed now (red box). A skull means it is lethal.")},
		{"code": t.translate("BLOCKED (3"), "title": t.translate("Absorbed"), "text": t.translate("Damage that block and shield soak up before it reaches HP.")},
		{"code": t.translate("GUARD +3"), "title": t.translate("Guard gained"), "text": t.translate("Block or shield this play adds. Block expires at the start of your next turn; shield stays.")},
		{"code": t.translate("RAM 6/12"), "title": t.translate("RAM"), "text": t.translate("What cards, respins and extra nudges cost. It refills each turn.")},
		{"code": t.translate("RAM (-1 THIS PLAY)"), "title": t.translate("RAM after this play"), "text": t.translate("The card or action under your pointer costs this much RAM. Negative means it spends RAM; positive means it gives some back.")},
		{"code": "☠?", "title": t.translate("Random status"), "text": t.translate("A status lands on a random slice. The chip's tooltip has the odds.")},
		{"code": "D 0", "title": t.translate("Daemons"), "text": t.translate("The number is how many Daemons you have installed (D 0: none). Press it to open the tray.")},
	]


## The text of a Codex line after its "CODE: " lead (the legend names the code itself).
static func _body(line: String) -> String:
	var at := line.find(": ")
	return line.substr(at + 2) if at > 0 and at < 24 else line


func _init() -> void:
	name = "CombatLegend"
	mouse_filter = Control.MOUSE_FILTER_STOP
	focus_mode = Control.FOCUS_NONE


func _ready() -> void:
	var view := get_viewport_rect().size
	var ts := Settings.text_scale
	custom_minimum_size = Vector2(clampf(view.x * VIEW_SHARE.x, SIZE_MIN.x, SIZE_MAX.x), clampf(view.y * VIEW_SHARE.y, SIZE_MIN.y, SIZE_MAX.y))
	size = custom_minimum_size
	position = ((view - size) / 2.0).floor()
	var box := StyleBoxFlat.new()
	var bg: Color = PaletteSkins.chrome(HudSkin.TERMINAL_BG)
	box.bg_color = Color(bg, 0.97)
	box.border_color = PaletteSkins.chrome(HudSkin.TERMINAL_EDGE)
	box.set_border_width_all(2)
	box.set_content_margin_all(PAD)
	add_theme_stylebox_override(&"panel", box)
	var col := VBoxContainer.new()
	col.add_theme_constant_override(&"separation", ROW_GAP * 2)
	add_child(col)
	var head := HBoxContainer.new()
	col.add_child(head)
	var title := Label.new()
	title.name = "LegendTitle"
	title.text = tr("LEGEND // WHAT THE FIGHT'S MARKS MEAN")
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title.autowrap_mode = TextServer.AUTOWRAP_WORD
	title.add_theme_color_override(&"font_color", PaletteSkins.chrome(HudSkin.TERMINAL_HI))
	head.add_child(title)
	close_button = Button.new()
	close_button.name = "LegendClose"
	close_button.text = ("%s %s" % [tr("CLOSE"), Settings.hint(ACTION)]).strip_edges()
	close_button.focus_mode = Control.FOCUS_ALL
	close_button.pressed.connect(close)
	head.add_child(close_button)
	scroll = ScrollContainer.new()
	scroll.name = "LegendScroll"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	col.add_child(scroll)
	var rows := VBoxContainer.new()
	rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rows.add_theme_constant_override(&"separation", ROW_GAP)
	scroll.add_child(rows)
	var section := ""
	for e in entries():
		if String(e["section"]) != section:
			section = String(e["section"])
			var h := Label.new()
			h.text = section
			h.add_theme_color_override(&"font_color", Palette.CELL_ACID)
			rows.add_child(h)
		rows.add_child(_row(e, ts))
	close_button.grab_focus.call_deferred()


func _row(e: Dictionary, ts: float) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", 10)
	var code := Label.new()
	code.text = String(e["code"])
	code.custom_minimum_size.x = CODE_W * ts
	code.add_theme_font_override(&"font", Palette.mono())
	code.add_theme_color_override(&"font_color", PaletteSkins.chrome(HudSkin.TERMINAL_HI))
	row.add_child(code)
	var words := Label.new()
	words.text = ("%s: %s" % [e["title"], e["text"]]) if String(e["title"]) != "" else String(e["text"])
	words.autowrap_mode = TextServer.AUTOWRAP_WORD
	words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	words.add_theme_color_override(&"font_color", HudSkin.TERMINAL_TEXT)
	row.add_child(words)
	return row


## Closes the legend (`closed` first).
func close() -> void:
	closed.emit()
	queue_free()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(ACTION):
		get_viewport().set_input_as_handled()
		close()
