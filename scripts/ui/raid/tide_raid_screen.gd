class_name TideRaidScreen
extends Control
## Phase 3: the Solace Infected Tide raid screen. The raid plays out on the live 3D city (a CityMapOverlay at the RAID band, with a
## TideRaidLayer over it) and this screen carries the HUD, the hand row, the deck strip and the side panel of each beat:
## DECAY, DRAW, PLAN, FORECAST, SEALED A, RESPONSE, the playout, the AFTERMATH stamp and the HQ step. A view over TideRaidFlow: it
## draws what the flow holds and tells it what the player pressed (the flow calls the rules); it changes no game state itself.
## Text 1.0, mouse and keyboard. Ported from the raid lab (L14 to L17 UI): inline results on the response rows, the honest guard line,
## ghost rows with a reason, the launch confirm, five tier shapes, dimmed DONE beams, wordless cards.

## Emitted when the raid and its HQ step are over (the HQ takes the player on).
signal finished
## A beat of the flow was entered (capture and tests read it): the label is `phase_label`.
signal beat(label: String)

const PANEL_W := 396.0
const HAND_H := 122.0
const HUD_H := 56.0
const DECK_W := 70.0
const CARD_W := 74.0
const CARD_H := 104.0
const MAX_GROUPS := 8
const TXT := 14
const SMALL := 13
const BIG := 22
const PAD := 8.0
const INK := TideGlyphs.INK
const DIM := TideGlyphs.DIM
const GOLD := TideGlyphs.GOLD
const PANEL_BG := Palette.TIDE_PANEL_GLASS
const EDGE := TideGlyphs.EDGE
const PLAYOUT_LOG_MAX := 12

var flow: TideRaidFlow = null
var overlay: CityMapOverlay = null
var layer: TideRaidLayer = null
var panel: PanelContainer
var body: VBoxContainer
var hand_row: HBoxContainer
var deck_strip: Control
var hud_strip: PanelContainer
var _status: String = ""
var _log: Array[String] = []
var _skip: bool = false
var _playing: bool = false
var _past_beams: Array[String] = []
var _hq_repair: StringName = &""
var _hq_build: String = ""
var _hq_patch: bool = false
var _more_open: bool = false
var _sub_open: int = -1
var _preview: Array = []
## The beat label last emitted (shot names for the capture tooling).
var last_beat: String = ""


func _init() -> void:
	name = "TideRaidScreen"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL


## Starts the screen over `p_flow` on the mounted map `p_overlay`.
func setup(p_flow: TideRaidFlow, p_overlay: CityMapOverlay) -> void:
	flow = p_flow
	overlay = p_overlay
	_build_frame()
	layer = TideRaidLayer.new()
	layer.overlay = overlay
	layer.core = flow.board().core
	layer.home = flow.board().home
	add_child(layer)
	move_child(layer, 0)
	if overlay != null and not overlay.node_clicked.is_connected(site_clicked):
		overlay.node_clicked.connect(site_clicked)
	_rebuild()


func _exit_tree() -> void:
	if overlay != null and is_instance_valid(overlay) and overlay.node_clicked.is_connected(site_clicked):
		overlay.node_clicked.disconnect(site_clicked)


# ------------------------------------------------------------------------------------------------ frame
func _build_frame() -> void:
	panel = PanelContainer.new()
	panel.name = "TidePanel"
	panel.anchor_left = 1.0
	panel.anchor_right = 1.0
	panel.anchor_top = 0.0
	panel.anchor_bottom = 1.0
	panel.offset_left = -PANEL_W - PAD
	panel.offset_right = -PAD
	panel.offset_top = PAD
	panel.offset_bottom = -HAND_H - PAD
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	panel.add_theme_stylebox_override("panel", UiTheme.box(PANEL_BG, EDGE, 2, 10, 8))
	add_child(panel)
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.add_child(scroll)
	body = VBoxContainer.new()
	body.name = "TideBody"
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 6)
	scroll.add_child(body)

	hud_strip = PanelContainer.new()
	hud_strip.name = "TideHud"
	hud_strip.anchor_left = 0.0
	hud_strip.anchor_right = 1.0
	hud_strip.offset_left = DECK_W + PAD * 2.0
	hud_strip.offset_right = -PANEL_W - PAD * 2.0
	hud_strip.offset_top = PAD
	hud_strip.offset_bottom = PAD + HUD_H
	hud_strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud_strip.add_theme_stylebox_override("panel", UiTheme.box(PANEL_BG, EDGE, 1, 8, 4))
	add_child(hud_strip)

	deck_strip = Control.new()
	deck_strip.name = "TideDeck"
	deck_strip.anchor_top = 0.0
	deck_strip.anchor_bottom = 1.0
	deck_strip.offset_left = PAD
	deck_strip.offset_right = PAD + DECK_W
	deck_strip.offset_top = PAD
	deck_strip.offset_bottom = -HAND_H - PAD
	deck_strip.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(deck_strip)
	deck_strip.draw.connect(_draw_deck)

	var hand_box := PanelContainer.new()
	hand_box.name = "TideHandBox"
	hand_box.anchor_top = 1.0
	hand_box.anchor_bottom = 1.0
	hand_box.anchor_right = 1.0
	hand_box.offset_left = DECK_W + PAD * 2.0
	hand_box.offset_right = -PANEL_W - PAD * 2.0
	hand_box.offset_top = -HAND_H
	hand_box.offset_bottom = -PAD
	hand_box.mouse_filter = Control.MOUSE_FILTER_STOP
	hand_box.add_theme_stylebox_override("panel", UiTheme.box(PANEL_BG, EDGE, 1, 8, 6))
	add_child(hand_box)
	hand_row = HBoxContainer.new()
	hand_row.name = "TideHand"
	hand_row.add_theme_constant_override("separation", 8)
	hand_box.add_child(hand_row)


func _clear(c: Node) -> void:
	for ch in c.get_children():
		c.remove_child(ch)
		ch.queue_free()


func _lab(text: String, px: int = TXT, col: Color = INK, wrap: bool = true) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", px)
	l.add_theme_color_override("font_color", col)
	l.add_theme_font_override("font", Palette.mono())
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _btn(text: String, cb: Callable, enabled: bool = true, accent: Color = TideGlyphs.TIER_COLOR["HOLDS"]) -> Button:
	var b := Button.new()
	b.text = text
	b.disabled = not enabled
	b.focus_mode = Control.FOCUS_ALL
	b.add_theme_font_size_override("font_size", TXT)
	b.add_theme_font_override("font", Palette.mono())
	b.add_theme_stylebox_override("normal", UiTheme.box(Palette.TIDE_BUTTON, accent, 2, 10, 6))
	b.add_theme_stylebox_override("hover", UiTheme.box(Palette.TIDE_BUTTON_HOT, accent.lightened(0.3), 2, 10, 6))
	b.add_theme_stylebox_override("pressed", UiTheme.box(accent.darkened(0.4), accent, 2, 10, 6))
	b.add_theme_stylebox_override("disabled", UiTheme.box(Palette.TIDE_BUTTON_OFF, Palette.TIDE_EDGE_OFF, 1, 10, 6))
	b.add_theme_color_override("font_color", INK)
	b.add_theme_color_override("font_disabled_color", Palette.TIDE_OFF)
	b.pressed.connect(cb)
	return b


func _title(text: String) -> Label:
	var l := _lab(text, BIG, GOLD)
	l.name = "TideTitle"
	return l


func _hrow(sep: int = 6) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", sep)
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return h


func _gap(px: float = 4.0) -> Control:
	var c := Control.new()
	c.custom_minimum_size.y = px
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


func _tier_word(t: String) -> String:
	return tr(t)


## A tier glyph and its word.
func _tier_tag(t: String, px: float = 20.0) -> HBoxContainer:
	var h := _hrow(4)
	h.add_child(TideGlyphView.tier(t, px))
	h.add_child(_lab(_tier_word(t), TXT, TideGlyphs.tier_color(t), false))
	return h


# ------------------------------------------------------------------------------------------------ the whole screen
func _rebuild() -> void:
	if flow == null:
		return
	_clear(body)
	_clear(hand_row)
	_sync_layer()
	_build_hud()
	_build_hand()
	deck_strip.queue_redraw()
	match flow.phase:
		TideRaidFlow.Phase.DECAY:
			_page_decay()
		TideRaidFlow.Phase.DRAW:
			_page_draw()
		TideRaidFlow.Phase.PLAN:
			_page_plan()
		TideRaidFlow.Phase.FORECAST:
			_page_forecast()
		TideRaidFlow.Phase.REVEAL:
			_page_reveal()
		TideRaidFlow.Phase.RESPONSE:
			_page_response()
		TideRaidFlow.Phase.PLAYOUT:
			_page_playout()
		TideRaidFlow.Phase.AFTERMATH:
			_page_aftermath()
		TideRaidFlow.Phase.HQ_STEP:
			_page_hq()
	body.add_child(_gap(6))
	body.add_child(_ladder())
	last_beat = phase_label()
	beat.emit(last_beat)


## The shot name of the flow's current beat.
func phase_label() -> String:
	return String(TideRaidFlow.Phase.keys()[flow.phase]).to_lower()


func _status_line() -> void:
	if _status != "":
		var l := _lab(_status, TXT, TideGlyphs.RED)
		l.name = "TideStatus"
		body.add_child(l)


# ------------------------------------------------------------------------------------------------ HUD, hand, deck
func _build_hud() -> void:
	_clear(hud_strip)
	var h := flow.hud()
	var row := _hrow(14)
	row.alignment = BoxContainer.ALIGNMENT_BEGIN
	hud_strip.add_child(row)
	# INFECTED and healthy cards with the CITY LOST line.
	var inf := VBoxContainer.new()
	inf.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var in_row := _hrow(4)
	var gv := TideGlyphView.new()
	gv.kind = TideGlyphView.Kind.PIP_DECK
	gv.word = "WOUND"
	gv.custom_minimum_size = Vector2(20, 20)
	in_row.add_child(gv)
	var danger := int(h["infected"]) > int(h["healthy"])
	in_row.add_child(_lab(tr("INFECTED %d  healthy %d") % [h["infected"], h["healthy"]], TXT, TideGlyphs.RED if danger else INK, false))
	inf.add_child(in_row)
	inf.add_child(_lab(tr("CITY LOST when INFECTED passes %d") % int(h["healthy"]), SMALL, DIM, false))
	inf.tooltip_text = tr("CITY LOST: the INFECTED cards outnumber the healthy ones (DOSE counts as healthy).")
	inf.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_child(inf)
	# HOME integrity.
	var home := VBoxContainer.new()
	home.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var hr := _hrow(4)
	hr.add_child(TideGlyphView.tier("HOLDS" if int(h["home"]) > 0 else "BREACHED", 20.0))
	hr.add_child(_lab(tr("HOME %d / %d") % [h["home"], h["home_max"]], TXT, INK, false))
	home.add_child(hr)
	var bar := ProgressBar.new()
	bar.min_value = 0
	bar.max_value = maxi(1, int(h["home_max"]))
	bar.value = int(h["home"])
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(120, 6)
	home.add_child(bar)
	row.add_child(home)
	# Heat bands with +1 beam / +1 card.
	var heat := VBoxContainer.new()
	heat.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var heat_top := _hrow(4)
	var fl := TideGlyphView.icon(TideGlyphView.Kind.FLAME, 20.0)
	heat_top.add_child(fl)
	heat_top.add_child(_lab(tr("HEAT %d") % int(h["heat"]), TXT, TideGlyphs.HEAT_COL, false))
	heat.add_child(heat_top)
	var ticks := _hrow(6)
	for t in flow.heat_ticks():
		var on: bool = int(h["heat"]) >= int(t["heat"])
		var col := GOLD if on else Palette.TIDE_OFF
		ticks.add_child(_lab("%d" % int(t["heat"]), SMALL, col, false))
		if bool(t["beam"]):
			ticks.add_child(TideGlyphView.icon(TideGlyphView.Kind.BEAM, 14.0, col))
		if bool(t["card"]):
			ticks.add_child(TideGlyphView.icon(TideGlyphView.Kind.CARD_TICK, 14.0, col))
	heat.add_child(ticks)
	heat.tooltip_text = tr("Heat levels: a beam icon adds one known beam, a card icon adds one card to the hand.")
	heat.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_child(heat)
	# DOSE count and the hand and beam counts.
	var misc := VBoxContainer.new()
	misc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	misc.add_child(_lab(tr("DOSE %d  ghost %d") % [h["doses"], h["ghost"]], SMALL, DIM, false))
	misc.add_child(_lab(tr("hand %d  beams %d") % [h["hand"], h["beams"]], SMALL, DIM, false))
	row.add_child(misc)


func _build_hand() -> void:
	if flow.phase < TideRaidFlow.Phase.DRAW or flow.raid.ctx == null:
		hand_row.add_child(_lab(tr("The hand is dealt after DECAY."), TXT, DIM))
		return
	var resp_phase := flow.phase >= TideRaidFlow.Phase.REVEAL
	var cards := flow.hand_cards()
	for c in cards:
		var card: Array = [c["id"], c["type"], c["verb"]]
		var placed := String(c["site"]) != ""
		var held: bool = (c["verb"] == "SHIFT" or c["verb"] == "JAM") and not placed
		var col := VBoxContainer.new()
		col.mouse_filter = Control.MOUSE_FILTER_IGNORE
		col.add_theme_constant_override("separation", 2)
		var cv := TideGlyphView.card_face(card, Vector2(CARD_W, CARD_H - 22.0), placed, bool(c["extra"]))
		cv.name = "Card_%s" % c["id"]
		cv.mouse_filter = Control.MOUSE_FILTER_STOP
		cv.tooltip_text = _card_tip(c)
		var id: String = c["id"]
		cv.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
				card_pressed(id))
		if flow.sel_card == id:
			cv.custom_minimum_size.y += 0.0
			cv.modulate = Palette.TIDE_GOLD
		col.add_child(cv)
		var cap := _lab(tr("on %s") % flow.site_name(StringName(c["site"])) if placed else (tr("held for response") if held and not resp_phase else ""), 11, GOLD if held else DIM, false)
		cap.custom_minimum_size.y = 18
		col.add_child(cap)
		hand_row.add_child(col)


func _card_tip(c: Dictionary) -> String:
	var verb_tip := {"GUARD": tr("GUARD: stands on a district and blocks a beam of its own type."),
		"SHIFT": tr("SHIFT: stands guard, or moves a sentry at the RESPONSE."),
		"JAM": tr("JAM: stands guard, or stops the hunter at the RESPONSE."),
		"WOUND": tr("INFECTED: a dead card that clogs the hand."), "DOSE": tr("DOSE: a healthy card that cures at DECAY.")}
	return "%s (%s)" % [verb_tip.get(c["verb"], ""), tr(_type_name(String(c["type"])))] if c["verb"] != "WOUND" else verb_tip["WOUND"]


func _type_name(t: String) -> String:
	match t:
		"D":
			return "DRONE"
		"N":
			return "NETRUNNER"
		"E":
			return "ENFORCER"
	return t


func _draw_deck() -> void:
	var h := flow.hud() if flow != null else {}
	if h.is_empty():
		return
	deck_strip.draw_rect(Rect2(Vector2.ZERO, deck_strip.size), PANEL_BG)
	deck_strip.draw_rect(Rect2(Vector2.ZERO, deck_strip.size), EDGE, false, 1.0)
	deck_strip.draw_string(ThemeDB.fallback_font, Vector2(6, 16), "DECK", HORIZONTAL_ALIGNMENT_LEFT, -1, SMALL, DIM)
	var deck: Array = h["deck"]
	var cols := 4
	for i in deck.size():
		var c: Array = deck[i]
		var p := Vector2(8 + (i % cols) * 14, 26 + (i / cols) * 16)
		var wound := String(c[2]) == "WOUND"
		var r := Rect2(p, Vector2(11, 13))
		if wound:
			deck_strip.draw_rect(r, TideGlyphs.WOUND_FILL)
			TideGlyphs.crack(deck_strip, p + Vector2(5.5, 6.5), 5.0, TideGlyphs.RED, 1.2)
		elif String(c[2]) == "DOSE":
			deck_strip.draw_rect(r, TideGlyphs.PANEL)
			deck_strip.draw_rect(r, TideGlyphs.ACID, false, 1.0)
		else:
			deck_strip.draw_rect(r, TideGlyphs.type_color(String(c[1])).darkened(0.5))
			deck_strip.draw_rect(r, TideGlyphs.type_color(String(c[1])), false, 1.0)
	deck_strip.tooltip_text = tr("Deck: %d cards, %d INFECTED, %d DOSE.") % [deck.size(), h["infected"], h["doses"]]


# ------------------------------------------------------------------------------------------------ the layer
## Gives the layer the beams, sentries, tints and marks of the current beat.
func _sync_layer() -> void:
	if layer == null:
		return
	var f := flow
	var st: SolaceTideState = f.raid.st
	var infected: Array[StringName] = []
	var taken: Array[StringName] = []
	var after := f.phase >= TideRaidFlow.Phase.AFTERMATH and f.raid.resolved and not f.raid.over
	var owned: Dictionary = st.owned
	var deck: Array = st.deck
	if after:
		var ns := SolaceTideCampaign.load_state(f.campaign, f.corp, f.cfg)
		owned = ns.owned
		deck = ns.deck
	for c in deck:
		if String(c[2]) == "WOUND" and String(c[1]) != String(SolaceTideRules.HOME_WORD):
			infected.append(StringName(c[1]))
	for s in owned:
		if int(owned[s]) == SolaceTideState.Cond.TAKEN:
			taken.append(s)
	var front: Array[StringName] = []
	var b := f.board()
	for s in infected:
		for n in b.all_adj.get(s, []):
			if not infected.has(n) and n != b.home and n != b.core and not front.has(n):
				front.append(n)
	IdSort.sort_ids(front)
	layer.infected = infected
	layer.front = front
	layer.taken = taken
	layer.home_tiers = []
	layer.ghost_home = false
	layer.beams = []
	layer.blocks = []
	layer.hits = {}
	layer.sentries = _sentries_now()
	if f.raid.ctx != null and f.phase >= TideRaidFlow.Phase.PLAN and f.phase <= TideRaidFlow.Phase.RESPONSE:
		layer.ghost_home = f.raid.place["ghost"] != &""
		_plan_beams()
		if f.phase == TideRaidFlow.Phase.PLAN or f.phase == TideRaidFlow.Phase.FORECAST:
			layer.home_tiers = f.route_tiers()
	if f.phase == TideRaidFlow.Phase.PLAYOUT or (f.phase == TideRaidFlow.Phase.AFTERMATH and f.raid.resolved and not f.raid.over):
		_playout_beams()


func _sentries_now() -> Dictionary:
	var out := {}
	if flow.raid.ctx == null:
		return out
	var sw := SolaceTideRules.launch(flow.raid.ctx, flow.raid.st, flow.raid.place)
	if flow.raid.resolved and not flow.result.is_empty():
		sw = SolaceTideRules.launch(flow.raid.ctx, flow.raid.st, flow.raid.place)
		SolaceTideRules.respond(flow.raid.ctx, sw, flow.raid.resp)
	elif flow.phase == TideRaidFlow.Phase.RESPONSE and flow.resp_sel >= 0 and not _preview.is_empty():
		SolaceTideRules.respond(flow.raid.ctx, sw, _preview)
	for s in sw.sent:
		var c: Array = flow.raid.ctx.cards[sw.sent[s]]
		out[s] = c
	return out


func _line_beam(ln: Dictionary, role: String, label: String, alpha: float, dashed: bool, width: float = TideRaidLayer.LINE_W) -> Dictionary:
	return {"cells": ln["cells"], "type": ln["type"], "role": role, "label": label, "alpha": alpha, "dashed": dashed, "width": width,
		"route": String(ln["kind"]) == "ROUTE", "home": bool(ln["home"])}


func _plan_beams() -> void:
	var f := flow
	var d: Dictionary = f.raid.ctx.draw
	var n_fire := f.known_firing()
	var revealed := f.phase >= TideRaidFlow.Phase.REVEAL
	for i in (d["known"] as Array).size():
		if i < n_fire:
			layer.beams.append(_line_beam(d["known"][i], "known", tr("K%d") % (i + 1), 0.95, false))
	for i in (d["cands"] as Array).size():
		var is_real := i == f.real_a()
		if revealed and not is_real:
			layer.beams.append(_line_beam(d["cands"][i], "cand", "", 0.3, true))
		else:
			layer.beams.append(_line_beam(d["cands"][i], "cand", ["A", "B", "C"][i] if not revealed else tr("SEALED A"), 1.0 if revealed else 0.7, not revealed, 5.0 if revealed else TideRaidLayer.LINE_W))
	if not revealed:
		for i in (d["hunters"] as Array).size():
			layer.beams.append(_line_beam(d["hunters"][i], "hunter", tr("HUNTER %d") % (i + 1), 0.55, true, 2.0))
	if f.phase == TideRaidFlow.Phase.RESPONSE and not _preview.is_empty():
		_preview_beam()


func _preview_beam() -> void:
	var head := String(_preview[0])
	if head == "DIVERT":
		var ln: Dictionary = flow.raid.ctx.draw["known"][int(_preview[1])]
		layer.beams.append({"cells": _preview[2], "type": ln["type"], "role": "known", "label": tr("DIVERT"), "alpha": 0.9, "dashed": true,
			"width": 4.0, "route": String(ln["kind"]) == "ROUTE", "home": bool(ln["home"])})


var _cur_beam: String = ""
var _beam_n: int = -1


func _playout_beams() -> void:
	var beats := flow.beats()
	for i in beats.size():
		var b: Dictionary = beats[i]
		var ln: Dictionary = b["line"]
		var done := i < _beam_n
		var cur := i == _beam_n
		var shown := i <= _beam_n or flow.phase == TideRaidFlow.Phase.AFTERMATH
		if not shown:
			continue
		var role := "known" if b["kind"] == "known" else ("hunter" if String(b["kind"]).begins_with("hunter") else "cand")
		var alpha := 1.0 if cur else TideRaidLayer.DONE_ALPHA
		var lab := ""
		if cur:
			lab = _beam_label(b)
		var beam := _line_beam(ln, role, lab, alpha, String(b["kind"]) == "hunter_jammed", 5.0 if cur else 2.0)
		beam["current"] = cur
		layer.beams.append(beam)
		if done or cur or flow.phase == TideRaidFlow.Phase.AFTERMATH:
			for e in b["trace"]:
				if e[2] == "hit":
					layer.hits[StringName(e[1])] = "hit"
				elif e[2] == "block" and cur:
					layer.blocks.append([e[1], ln["type"]])


func _beam_label(b: Dictionary) -> String:
	match String(b["kind"]):
		"known":
			return tr("KNOWN BEAM")
		"sealed_a":
			return tr("SEALED A")
		"sealed_b":
			return tr("SEALED B")
		"hunter":
			return tr("HUNTER")
		"hunter_jammed":
			return tr("HUNTER JAMMED")
	return ""


# ------------------------------------------------------------------------------------------------ input
func card_pressed(id: String) -> void:
	if flow.pick_card(id):
		_status = ""
	else:
		_status = tr("That card cannot be picked now.")
	_rebuild()


## A district was clicked on the map (the overlay's node_clicked).
func site_clicked(id: StringName) -> void:
	if flow == null or flow.phase != TideRaidFlow.Phase.PLAN:
		return
	if (flow.raid.place["sentries"] as Dictionary).has(id) and flow.sel_card == "":
		flow.unplace(id)
		_status = ""
	else:
		var err := flow.place_on(id)
		_status = tr(err) if err != "" else ""
	_rebuild()


func _unhandled_key_input(event: InputEvent) -> void:
	if flow == null or not (event is InputEventKey) or not event.pressed or event.echo:
		return
	var key := (event as InputEventKey).keycode
	match key:
		KEY_ENTER, KEY_KP_ENTER:
			_primary()
			get_viewport().set_input_as_handled()
		KEY_Z:
			undo()
			get_viewport().set_input_as_handled()
		KEY_G:
			ghost()
			get_viewport().set_input_as_handled()
		KEY_ESCAPE:
			if flow.phase == TideRaidFlow.Phase.FORECAST:
				back()
				get_viewport().set_input_as_handled()


## The main button of the current beat (Enter).
func _primary() -> void:
	match flow.phase:
		TideRaidFlow.Phase.DECAY, TideRaidFlow.Phase.DRAW, TideRaidFlow.Phase.AFTERMATH:
			cont()
		TideRaidFlow.Phase.PLAN:
			to_forecast()
		TideRaidFlow.Phase.FORECAST:
			launch()
		TideRaidFlow.Phase.RESPONSE:
			commit()
		TideRaidFlow.Phase.HQ_STEP:
			done_hq()
		TideRaidFlow.Phase.PLAYOUT:
			_skip = true


func cont() -> void:
	_status = ""
	flow.advance()
	_rebuild()
	if flow.phase == TideRaidFlow.Phase.AFTERMATH and flow.raid.over:
		pass
	elif flow.phase == TideRaidFlow.Phase.DONE:
		finished.emit()


func undo() -> void:
	if flow.undo():
		_status = ""
	_rebuild()


func ghost() -> void:
	if not flow.toggle_ghost():
		_status = tr("The ghost is not available.")
	else:
		_status = ""
	_rebuild()


func to_forecast() -> void:
	if not flow.to_forecast():
		_status = tr("That placement is not legal.")
	else:
		_status = ""
	_rebuild()


func back() -> void:
	flow.back_to_plan()
	_rebuild()


func launch() -> void:
	var r := flow.launch()
	_status = ""
	_rebuild()
	if r == "launched":
		_after_launch()


func _after_launch() -> void:
	if flow.fast:
		_status = ""
		flow.reveal_done()
		_commit_now([TideRaidFlow.HOLD], true)
		return
	var hold := Motion.seconds_live(&"raid_phase_gap")
	if hold > 0.0:
		await get_tree().create_timer(hold).timeout
		if not is_inside_tree() or flow.phase != TideRaidFlow.Phase.REVEAL:
			return
	flow.reveal_done()
	_rebuild()


func commit() -> void:
	if flow.resp_sel < 0:
		_status = tr("Pick a response first.")
		_rebuild()
		return
	_commit_now(_selected_resp(), false)


func _selected_resp() -> Array:
	return _preview if not _preview.is_empty() else [TideRaidFlow.HOLD]


func _commit_now(resp: Array, force: bool) -> void:
	var r := flow.commit(resp, force)
	if r == "confirm":
		_rebuild()
		return
	if r != "committed":
		return
	_preview = []
	_beam_n = -1
	_log.clear()
	_past_beams.clear()
	_skip = false
	_rebuild()
	await _play()


func _play() -> void:
	_playing = true
	var beats := flow.beats()
	var gap := Motion.seconds_live(&"raid_step_beat")
	for i in beats.size():
		_beam_n = i
		var b: Dictionary = beats[i]
		_log.append(_beat_line(b))
		_sync_layer()
		_playout_refresh()
		if gap > 0.0 and not _skip:
			await get_tree().create_timer(gap).timeout
			if not is_inside_tree():
				return
	_playing = false
	_beam_n = beats.size()
	flow.playout_done()
	_rebuild()


## Rebuilds only the side log during the playout.
func _playout_refresh() -> void:
	_clear(body)
	_page_playout()
	body.add_child(_gap(6))
	body.add_child(_ladder())


func _beat_line(b: Dictionary) -> String:
	var parts := PackedStringArray()
	for e in b["trace"]:
		match String(e[2]):
			"hit":
				parts.append(tr("hits %s") % flow.site_name(StringName(e[1])))
			"block":
				parts.append(tr("BLOCKED at %s") % flow.site_name(StringName(e[1])))
			"home":
				parts.append(tr("HOME hit"))
			"shield":
				parts.append(tr("HOME shielded"))
	var head := _beam_label(b)
	if String(b["kind"]) == "sealed_b":
		head += " (%s)" % (tr("lean flipped") if bool(b.get("flipped", false)) else tr("the corp picked it"))
	return "%s: %s" % [head, ", ".join(parts) if not parts.is_empty() else tr("touches nothing")]


func done_hq() -> void:
	var opt: Array = [_hq_repair, _hq_build, _hq_patch]
	flow.apply_hq_step(opt)
	finished.emit()


# ------------------------------------------------------------------------------------------------ pages
func _page_decay() -> void:
	body.add_child(_title(tr("DECAY")))
	body.add_child(_lab(tr("Raid %d") % (flow.raid.raid_idx + 1), TXT, DIM))
	if flow.raid.open_events.is_empty():
		body.add_child(_lab(tr("Nothing decays before the first raid, and no district sat DOWN since the last."), TXT))
	else:
		for e in flow.raid.open_events:
			body.add_child(_lab(String(e.get("text", "")), TXT))
	if flow.raid.over:
		body.add_child(_lab(tr("CITY LOST in the DECAY: the infection outnumbers the healthy defenses."), TXT, TideGlyphs.RED))
	body.add_child(_btn(tr("CONTINUE"), cont))


func _page_draw() -> void:
	body.add_child(_title(tr("DRAW")))
	var h := flow.hud()
	body.add_child(_lab(tr("The deck deals %d cards. A gold edge marks the card a Heat level adds.") % int(h["hand"]), TXT))
	body.add_child(_lab(tr("%d known beams will fire after your RESPONSE; they are shown now.") % int(h["beams"]), TXT, DIM))
	body.add_child(_btn(tr("CONTINUE"), cont))


func _page_plan() -> void:
	body.add_child(_title(tr("PLAN")))
	body.add_child(_lab(tr("Pick a card, then a district on a beam's path. Up to %d guards. The ghost shields HOME for a Heat cost.") % flow.cfg.solace_tide_max_placed, TXT))
	_beam_legend()
	body.add_child(_guard_line())
	_summary_lines()
	var row := _hrow(6)
	var ghost_on: bool = flow.raid.place["ghost"] != &""
	row.add_child(_btn(tr("GHOST OFF") if ghost_on else tr("GHOST ON HOME (+%d Heat)") % flow.cfg.solace_tide_ghost_heat, ghost, ghost_on or flow.raid.st.ghost > 0))
	row.add_child(_btn(tr("UNDO"), undo, flow.can_undo()))
	body.add_child(row)
	body.add_child(_btn(tr("FORECAST"), to_forecast))
	_status_line()


func _beam_legend() -> void:
	var d: Dictionary = flow.raid.ctx.draw
	var n_fire := flow.known_firing()
	for i in (d["known"] as Array).size():
		var ln: Dictionary = d["known"][i]
		var live := i < n_fire
		var r := _hrow(6)
		r.add_child(_type_icon(String(ln["type"]), not live))
		r.add_child(_lab(tr("Known beam %d: %s, fires after the RESPONSE") % [i + 1, tr(_type_name(String(ln["type"])))] if live else tr("Known beam %d: waits for more Heat") % (i + 1), SMALL, INK if live else Palette.TIDE_OFF, true))
		body.add_child(r)
	var rr := _hrow(6)
	for i in (d["cands"] as Array).size():
		rr.add_child(_type_icon(String(d["cands"][i]["type"]), false))
		rr.add_child(_lab(["A", "B", "C"][i], SMALL, DIM, false))
	rr.add_child(_lab(tr("Sealed routes: two will fire"), SMALL, DIM, true))
	body.add_child(rr)
	var hr := _hrow(6)
	var hd: Array = d["hunters"]
	hr.add_child(_type_icon(String(d["hunter_type"]), false))
	var hh := TideGlyphView.new()
	hh.custom_minimum_size = Vector2(18, 18)
	hh.draw.connect(func() -> void: TideGlyphs.hound(hh, hh.size * 0.5))
	hr.add_child(hh)
	hr.add_child(_lab(tr("Hunter: one of %d streets, revealed last") % hd.size(), SMALL, DIM, true))
	body.add_child(hr)


func _type_icon(t: String, dim: bool) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = TideGlyphView.Kind.TYPE
	g.word = t
	g.color = TideGlyphs.type_color(t).darkened(0.5) if dim else Palette.CLEAR
	g.custom_minimum_size = Vector2(18, 18)
	return g


## The honest guard line: HOLD -> tier . best: row -> tier, or no response changes this.
func _guard_line() -> Control:
	var g := flow.guard()
	var box := _hrow(4)
	box.name = "GuardLine"
	box.add_child(_lab(tr("HOLD"), TXT, INK, false))
	box.add_child(_arrow_view(INK))
	box.add_child(TideGlyphView.tier(String(g["hold"]), 18.0))
	box.add_child(_lab(tr(String(g["hold"])), TXT, TideGlyphs.tier_color(String(g["hold"])), false))
	if (g["best"] as Dictionary).is_empty():
		box.add_child(_lab("· " + tr("no response changes this"), SMALL, DIM, true))
	else:
		var best: Dictionary = g["best"]
		box.add_child(_lab("· " + tr("best:"), SMALL, DIM, false))
		box.add_child(TideGlyphView.resp(best["resp"], 24.0))
		box.add_child(_arrow_view(GOLD))
		box.add_child(TideGlyphView.tier(String(best["worst"]), 18.0))
		box.add_child(_lab(tr(String(best["worst"])), TXT, TideGlyphs.tier_color(String(best["worst"])), false))
	return box


func _arrow_view(col: Color) -> Control:
	var a := Control.new()
	a.custom_minimum_size = Vector2(16, 16)
	a.mouse_filter = Control.MOUSE_FILTER_IGNORE
	a.draw.connect(func() -> void: TideGlyphs.arrow(a, 1.0, 8.0, col))
	return a


func _summary_lines() -> void:
	var s := flow.plan_summary()
	if bool(s["locked"]):
		var r := _hrow(4)
		r.add_child(TideGlyphView.tier(String(s["worst"]), 18.0))
		r.add_child(_lab(tr("LOCKED: every outcome is %s under HOLD.") % tr(String(s["worst"])), TXT, GOLD, true))
		body.add_child(r)
	else:
		var r := _hrow(4)
		r.add_child(_lab(tr("Under HOLD, worst"), SMALL, DIM, false))
		r.add_child(TideGlyphView.tier(String(s["worst"]), 18.0))
		r.add_child(_lab(tr("best"), SMALL, DIM, false))
		r.add_child(TideGlyphView.tier(String(s["best"]), 18.0))
		body.add_child(r)


func _page_forecast() -> void:
	body.add_child(_title(tr("FORECAST")))
	body.add_child(_lab(tr("Every outcome of this plan under HOLD: sealed route A, then B, then the hunter's street. HOME's tier sits at the end of each route."), SMALL, DIM))
	var rows := flow.forecast()
	var tiers := flow.route_tiers()
	var table := HBoxContainer.new()
	table.add_theme_constant_override("separation", 10)
	table.name = "ForecastTable"
	for a in (flow.raid.ctx.draw["cands"] as Array).size():
		var col := VBoxContainer.new()
		col.add_theme_constant_override("separation", 3)
		var head := _hrow(4)
		head.add_child(_type_icon(String(flow.raid.ctx.draw["cands"][a]["type"]), false))
		head.add_child(_lab("A=%s" % ["A", "B", "C"][a], SMALL, INK, false))
		head.add_child(TideGlyphView.tier(String(tiers[a]), 16.0))
		col.add_child(head)
		var grid := GridContainer.new()
		grid.columns = 2
		grid.add_theme_constant_override("h_separation", 3)
		grid.add_theme_constant_override("v_separation", 3)
		for slot in 2:
			for h in 2:
				var tier_word := ""
				for r in rows:
					if r["a"] == a and r["b_slot"] == slot and r["hunter"] == h:
						tier_word = String(r["tier"])
				var cell := TideGlyphView.tier(tier_word, 24.0)
				var pip := TideGlyphView.new()
				pip.custom_minimum_size = Vector2(28, 28)
				var tw := tier_word
				pip.draw.connect(func() -> void: TideGlyphs.tier_pip(pip, pip.size * 0.5, tw, 12.0))
				pip.tooltip_text = tr("B slot %d, hunter street %d: %s") % [slot + 1, h + 1, tr(tw)]
				cell.queue_free()
				grid.add_child(pip)
		col.add_child(grid)
		table.add_child(col)
	body.add_child(table)
	body.add_child(_lab(tr("Rows: the corp's B pick (slot 1 or 2). Columns: the hunter's street."), SMALL, DIM))
	body.add_child(_guard_line())
	_summary_lines()
	var fr := flow.friction()
	if fr != TideRaidFlow.FRICTION_NONE:
		body.add_child(_lab(_friction_text(fr), TXT, TideGlyphs.HEAT_COL))
	var row := _hrow(6)
	row.add_child(_btn(tr("BACK"), back))
	var armed := flow.launch_armed
	row.add_child(_btn(tr("CONFIRM LAUNCH") if armed else tr("LAUNCH"), launch, true, GOLD if armed else TideGlyphs.TIER_COLOR["HOLDS"]))
	body.add_child(row)


func _friction_text(fr: String) -> String:
	match fr:
		TideRaidFlow.FRICTION_BREACH:
			return tr("Every outcome breaks HOME with this plan: change it?")
		TideRaidFlow.FRICTION_LOSS:
			return tr("Every outcome costs HOME with this plan: change it?")
		TideRaidFlow.FRICTION_LAST:
			return tr("HOME is at 1: one hit ends the campaign. Launch?")
	return ""


func _page_reveal() -> void:
	body.add_child(_title(tr("SEALED A")))
	var ln: Dictionary = flow.raid.ctx.draw["cands"][flow.real_a()]
	var r := _hrow(6)
	r.add_child(_type_icon(String(ln["type"]), false))
	r.add_child(_lab(tr("Sealed route A is a %s route. It fires after your RESPONSE.") % tr(_type_name(String(ln["type"]))), TXT))
	body.add_child(r)
	if flow.fast:
		body.add_child(_fast_chip())
	body.add_child(_btn(tr("CONTINUE"), func() -> void:
		flow.reveal_done()
		_rebuild()))


func _fast_chip() -> Control:
	var chip := PanelContainer.new()
	chip.name = "FastChip"
	chip.add_theme_stylebox_override("panel", UiTheme.box(Palette.TIDE_PANEL_HI, GOLD, 2, 8, 3))
	chip.add_child(_lab(tr("LOCKED: every response gives one tier, fast resolve"), SMALL, GOLD))
	return chip


func _page_response() -> void:
	body.add_child(_title(tr("RESPONSE")))
	body.add_child(_guard_line())
	if flow.fast:
		body.add_child(_fast_chip())
	var shown := mini(MAX_GROUPS, flow.groups.size()) if not _more_open else flow.groups.size()
	for gi in shown:
		body.add_child(_group_row(gi))
		if flow.resp_sel == gi and (flow.groups[gi]["members"] as Array).size() > 1:
			body.add_child(_variants(gi))
	if flow.groups.size() > MAX_GROUPS:
		body.add_child(_btn(tr("fewer") if _more_open else tr("more (%d)") % (flow.groups.size() - MAX_GROUPS), func() -> void:
			_more_open = not _more_open
			_rebuild()))
	for g in flow.ghosts:
		var gr := _hrow(6)
		gr.add_child(TideGlyphView.resp([g[0]], 24.0, "", true))
		gr.add_child(_lab(tr(String(g[1])), SMALL, Palette.TIDE_OFF, true))
		gr.name = "Ghost_%s" % g[0]
		body.add_child(gr)
	if flow.hold_armed:
		var w := flow.hold_worse_group()
		var r := _hrow(4)
		r.add_child(_lab(tr("HOLD is worse than"), TXT, TideGlyphs.HEAT_COL, false))
		if w >= 0:
			r.add_child(TideGlyphView.resp(flow.groups[w]["members"][0]["resp"], 24.0))
		r.add_child(_lab(tr("launch anyway?"), TXT, TideGlyphs.HEAT_COL, false))
		body.add_child(r)
	var armed := flow.hold_armed
	body.add_child(_btn(tr("CONFIRM HOLD") if armed else tr("COMMIT"), commit, flow.resp_sel >= 0, GOLD if armed else TideGlyphs.TIER_COLOR["HOLDS"]))
	_status_line()


func _group_row(gi: int) -> Control:
	var g: Dictionary = flow.groups[gi]
	var m: Dictionary = g["members"][0]
	var sel := flow.resp_sel == gi
	var better: bool = g["better"]
	var nothing: bool = g["changes_nothing"]
	var btn := Button.new()
	btn.name = "Resp_%d" % gi
	btn.focus_mode = Control.FOCUS_ALL
	btn.custom_minimum_size.y = 46.0
	var edge := GOLD if better else (Palette.TIDE_EDGE_OFF if nothing else EDGE)
	btn.add_theme_stylebox_override("normal", UiTheme.box(Palette.TIDE_PANEL_HI if sel else Palette.TIDE_ROW, edge, 2, 6, 3))
	btn.add_theme_stylebox_override("hover", UiTheme.box(Palette.TIDE_ROW_HOT, edge.lightened(0.3), 2, 6, 3))
	btn.add_theme_stylebox_override("pressed", UiTheme.box(Palette.TIDE_ROW_PRESSED, GOLD, 2, 6, 3))
	btn.pressed.connect(func() -> void: select_group(gi))
	btn.mouse_entered.connect(func() -> void: _hover_group(gi))
	var row := _hrow(6)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.offset_left = 6
	row.offset_right = -6
	var sent_t := ""
	if String(m["head"]) == "REDEPLOY":
		sent_t = String(flow.raid.ctx.cards[(flow.raid.place["sentries"] as Dictionary).get(m["resp"][1], "")][0]) if (flow.raid.place["sentries"] as Dictionary).has(m["resp"][1]) else ""
	var gl := TideGlyphView.resp(m["resp"], 34.0, sent_t, nothing)
	gl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(gl)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_theme_constant_override("separation", 0)
	var lab := _lab(_group_label(g), TXT, DIM if nothing else INK, false)
	lab.clip_text = true
	col.add_child(lab)
	var sub := _cost_note(m, nothing)
	if sub != "":
		col.add_child(_lab(sub, 11, DIM, false))
	row.add_child(col)
	var worst := String(m["worst"])
	var best := String(m["best"])
	var tr_ := _hrow(2)
	tr_.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tr_.add_child(_ignore(TideGlyphView.tier(worst, 20.0)))
	if best != worst:
		tr_.add_child(_lab("/", SMALL, DIM, false))
		tr_.add_child(_ignore(TideGlyphView.tier(best, 20.0)))
	row.add_child(tr_)
	btn.add_child(row)
	btn.tooltip_text = _group_tip(g)
	return btn


func _ignore(c: Control) -> Control:
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


func _cost_note(m: Dictionary, nothing: bool) -> String:
	var parts := PackedStringArray()
	if SolaceTideRules.CARD_RESPONSES.has(String(m["head"])):
		parts.append(tr("+%d Heat") % flow.cfg.solace_tide_card_response_heat)
	if nothing:
		parts.append(tr("changes nothing"))
	var need := _card_need(m["resp"])
	if need != "":
		parts.append(need)
	return ", ".join(parts)


func _card_need(r: Array) -> String:
	match String(r[0]):
		"REDEPLOY", "DIVERT":
			return tr("needs a SHIFT card")
		"DEPLOY":
			return tr("uses a %s card") % tr(_type_name(String(r[1])))
		"JAM", "JAM_B":
			return tr("needs a JAM card")
	return ""


func _group_label(g: Dictionary) -> String:
	var members: Array = g["members"]
	var r0: Array = members[0]["resp"]
	if members.size() == 1:
		return _resp_label(r0)
	var head := String(r0[0])
	var base := head
	match head:
		"REDEPLOY":
			base = tr("MOVE %s") % flow.site_name(StringName(r0[1]))
		"DEPLOY":
			base = tr("DEPLOY %s") % tr(_type_name(String(r0[1])))
		"SACRIFICE":
			base = tr("SACRIFICE")
		"DIVERT":
			base = tr("DIVERT beam %d") % (int(r0[1]) + 1)
	return "%s  x%d" % [base, members.size()]


func _resp_label(r: Array) -> String:
	match String(r[0]):
		"HOLD":
			return tr("HOLD")
		"JAM":
			return tr("JAM the hunter")
		"JAM_B":
			return tr("JAM sealed B")
		"DEPLOY":
			return tr("DEPLOY %s > %s") % [tr(_type_name(String(r[1]))), flow.site_name(StringName(r[2]))]
		"SACRIFICE":
			return tr("SACRIFICE %s") % flow.site_name(StringName(r[1]))
		"REDEPLOY":
			return tr("MOVE %s > %s") % [flow.site_name(StringName(r[1])), flow.site_name(StringName(r[2]))]
		"DIVERT":
			return tr("DIVERT beam %d") % (int(r[1]) + 1)
	return String(r[0])


func _group_tip(g: Dictionary) -> String:
	var m: Dictionary = g["members"][0]
	var lines := PackedStringArray([_resp_label(m["resp"])])
	lines.append(tr("Worst %s, best %s over the remaining outcomes.") % [tr(String(m["worst"])), tr(String(m["best"]))])
	if bool(g["better"]):
		lines.append(tr("Better than doing nothing."))
	return "\n".join(lines)


func _variants(gi: int) -> Control:
	var box := VBoxContainer.new()
	box.name = "Variants"
	var members: Array = flow.groups[gi]["members"]
	for mi in members.size():
		var m: Dictionary = members[mi]
		var b := _btn(_resp_label(m["resp"]), func() -> void: select_group(gi, mi), true, EDGE)
		b.add_theme_font_size_override("font_size", SMALL)
		box.add_child(b)
	return box


func _hover_group(gi: int) -> void:
	if flow.phase != TideRaidFlow.Phase.RESPONSE or flow.resp_sel >= 0 and flow.resp_sel != gi:
		return


func select_group(gi: int, mi: int = 0) -> void:
	_preview = flow.select_group(gi, mi)
	_status = ""
	_rebuild()


func _page_playout() -> void:
	body.add_child(_title(tr("RAID")))
	for line in _log:
		body.add_child(_lab(line, TXT, INK))
	if _playing:
		body.add_child(_btn(tr("SKIP"), func() -> void: _skip = true))


func _page_aftermath() -> void:
	body.add_child(_title(tr("AFTERMATH")))
	var a := flow.aftermath()
	var tier_word := String(a["tier"])
	var stamp := _hrow(10)
	stamp.name = "AftermathStamp"
	if tier_word != "CITY LOST":
		stamp.add_child(TideGlyphView.tier(tier_word, 48.0))
		stamp.add_child(_lab(tr(tier_word), 28, TideGlyphs.tier_color(tier_word), false))
	else:
		stamp.add_child(TideGlyphView.tier("BREACHED", 48.0))
		stamp.add_child(_lab(tr("CITY LOST"), 28, TideGlyphs.RED, false))
	body.add_child(stamp)
	var banner := String(a["banner"])
	var col := TideGlyphs.TIER_COLOR["HOLDS"] if banner == "CELL HOLDS" else TideGlyphs.RED
	body.add_child(_lab(tr(banner), BIG, col))
	if not bool(a["campaign_lost"]):
		body.add_child(_lab(tr("HOME %d to %d") % [a["home_before"], a["home_after"]], TXT))
		body.add_child(_lab(tr("%d DOWN, %d TAKEN, %d INFECTED in all") % [(a["down"] as Array).size(), (a["taken"] as Array).size(), a["infected"]], TXT))
		if int(a["heat_delta"]) != 0 or int(a["schematics_delta"]) != 0:
			body.add_child(_lab(tr("Heat %+d, Schematics %+d") % [a["heat_delta"], a["schematics_delta"]], TXT, DIM))
	body.add_child(_btn(tr("CONTINUE"), cont))


func _page_hq() -> void:
	body.add_child(_title(tr("HQ STEP")))
	var m := flow.hq_menu()
	body.add_child(_lab(tr("Schematics: %d. One repair, one build and a patch.") % int(m["schematics"]), TXT, DIM))
	var patch: Array = m["patch"]
	if bool(m["can_patch"]):
		var cb := CheckBox.new()
		cb.text = tr("PATCH HOME +%d (%d Schematics)") % [patch[0], patch[1]]
		cb.button_pressed = _hq_patch
		cb.toggled.connect(func(on: bool) -> void:
			_hq_patch = on
			_rebuild())
		body.add_child(cb)
	for d in m["downs"]:
		var cb := CheckBox.new()
		cb.text = tr("REPAIR %s (%d Schematics)") % [flow.site_name(d), m["repair_cost"]]
		cb.button_pressed = _hq_repair == d
		cb.toggled.connect(func(on: bool) -> void:
			_hq_repair = d if on else &""
			_rebuild())
		body.add_child(cb)
	var build_row := _hrow(6)
	build_row.add_child(_btn(tr("no build"), func() -> void:
		_hq_build = ""
		_rebuild(), true, GOLD if _hq_build == "" else EDGE))
	if bool(m["can_clean"]):
		build_row.add_child(_btn(tr("CLEAN (%d)") % int(m["clean_price"]), func() -> void:
			_hq_build = "CLEAN"
			_rebuild(), true, GOLD if _hq_build == "CLEAN" else EDGE))
	if bool(m["can_cool"]):
		build_row.add_child(_btn(tr("COOL (%d)") % int(m["cool_price"]), func() -> void:
			_hq_build = "COOL"
			_rebuild(), true, GOLD if _hq_build == "COOL" else EDGE))
	body.add_child(build_row)
	if (m["cleared"] as Array).size() > 0:
		body.add_child(_lab(tr("%d cleared districts wait to be installed at the HQ.") % (m["cleared"] as Array).size(), SMALL, DIM))
	var opt: Array = [_hq_repair, _hq_build, _hq_patch]
	var legal := false
	for o in flow.hq_options():
		if o[0] == opt[0] and o[1] == opt[1] and o[2] == opt[2]:
			legal = true
	if not legal:
		body.add_child(_lab(tr("The Schematics do not cover that."), SMALL, TideGlyphs.RED))
	body.add_child(_btn(tr("DONE"), done_hq, legal))


## The tier ladder, best to worst, pinned in the panel foot.
func _ladder() -> Control:
	var box := HFlowContainer.new()
	box.name = "TierLadder"
	box.add_theme_constant_override("h_separation", 8)
	for t in TideGlyphs.TIER_LADDER:
		var r := _hrow(2)
		r.add_child(TideGlyphView.tier(t, 16.0))
		r.add_child(_lab(tr(t), 11, TideGlyphs.tier_color(t), false))
		box.add_child(r)
	return box
