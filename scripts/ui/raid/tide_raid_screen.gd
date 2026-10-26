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
## A playout beam reached a stage (beam index, stage: 1 the impact landed, 2 settled); the capture and the tests read it.
signal beat_stage(beam: int, stage: int)

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
const CITY_LOST_PX := 72
const PAD := 8.0
const INK := TideGlyphs.INK
const DIM := TideGlyphs.DIM
const GOLD := TideGlyphs.GOLD
const PANEL_BG := Palette.TIDE_PANEL_GLASS
const EDGE := TideGlyphs.EDGE
const PLAYOUT_LOG_MAX := 12
const METER_MAX_W := 150.0
const METER_CELL_W := 13.0
const METER_H := 20.0
## The forecast tile (px).
const TILE_W := 100.0
const TILE_H := 26.0
## The deck strip: cells per row and one cell's size (px).
const DECK_COLS := 4
const DECK_CELL := Vector2(11.0, 13.0)

var flow: TideRaidFlow = null
var overlay: CityMapOverlay = null
var layer: TideRaidLayer = null
var panel: PanelContainer
var body: VBoxContainer
var foot: VBoxContainer
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
## The playout beat's stage: 0 the pulse travels, 1 the impact lands (the INFECTED count ticks), 2 the beat settles.
var _stage: int = 0
## The CITY LOST full-screen moment (null when not shown) and whether it has been shown for this raid.
var _lost_overlay: Control = null
var _lost_shown: bool = false
## The beat label last emitted (shot names for the capture tooling).
var last_beat: String = ""


func _init() -> void:
	name = "TideRaidScreen"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	MotionSkip.register_passive(self)  # the CITY LOST moment lands with any press that ends a motion


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
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 6)
	panel.add_child(col)
	var scroll := ScrollContainer.new()
	scroll.name = "TideScroll"
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(scroll)
	body = VBoxContainer.new()
	body.name = "TideBody"
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 6)
	scroll.add_child(body)
	# The foot is pinned under the scrolling page: the beat's main button (COMMIT) is always on screen, whatever the list above holds.
	foot = VBoxContainer.new()
	foot.name = "TideFoot"
	foot.add_theme_constant_override("separation", 4)
	col.add_child(foot)

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
	return _tierw(t)


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
	_focus_hover = ""
	if flow.phase != TideRaidFlow.Phase.PLAN:
		_focus_pin = ""
	_clear(body)
	_clear(foot)
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


## The beam the PLAN legend points at: the row under the mouse, else the one the player clicked ("" = none).
func _focus_now() -> String:
	return _focus_hover if _focus_hover != "" else _focus_pin


## The shot name of the flow's current beat.
func phase_label() -> String:
	return String(TideRaidFlow.Phase.keys()[flow.phase]).to_lower()


func _status_line(parent: Control = null) -> void:
	if _status != "":
		var l := _lab(_status, TXT, TideGlyphs.RED)
		l.name = "TideStatus"
		(parent if parent != null else body).add_child(l)


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
	# The meter: one cell per INFECTED card the city bears, the last cell (flagged) is the CITY LOST line.
	var mrow := _hrow(6)
	var cells := int(h["healthy"]) + 1
	var mw := minf(METER_MAX_W, float(cells) * METER_CELL_W)
	var meter := TideGlyphView.meter(int(h["infected"]), int(h["healthy"]), Vector2(mw, METER_H))
	meter.name = "InfectedMeter"
	mrow.add_child(meter)
	var margin := flow.loss_margin(h)
	if margin <= 1:
		var wl := _lab(tr("1 more = CITY LOST") if margin == 1 else tr("CITY FALLS AT RAID END"), SMALL, TideGlyphs.RED, false)
		wl.name = "LossWarning"
		mrow.add_child(wl)
	else:
		mrow.add_child(_lab(tr("CITY LOST at %d") % (int(h["healthy"]) + 1), SMALL, DIM, false))
	inf.add_child(mrow)
	inf.tooltip_text = tr("CITY LOST: the INFECTED cards outnumber the healthy ones (DOSE counts as healthy). The flagged cell of the meter is the line.")
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
	var heat_lab := _lab(_heat_text(h), TXT, TideGlyphs.HEAT_COL, false)
	heat_lab.name = "HeatLabel"
	heat_top.add_child(heat_lab)
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
	misc.add_child(_lab(tr("RAID %d") % flow.raid_number(), TXT, GOLD, false))
	misc.add_child(_lab(tr("DOSE %d  ghost %d") % [h["doses"], h["ghost"]], SMALL, DIM, false))
	misc.tooltip_text = tr("Raid %d of the campaign. The hand holds %d cards and %d known beams fire.") % [flow.raid_number(), h["hand"], h["beams"]]
	misc.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_child(misc)


## The header's Heat: "HEAT 80" and, while the raid is planned and before it resolves, "HEAT 80 → 85": the Heat the plan (or the picked
## response) leaves, read from the forecast so it is what the raid will really do (ghost, card response, clean defense).
func _heat_text(h: Dictionary) -> String:
	var now := int(h["heat"])
	var ph := flow.phase
	if flow.raid.ctx != null and ph >= TideRaidFlow.Phase.PLAN and ph <= TideRaidFlow.Phase.RESPONSE and not flow.raid.resolved:
		var lo := now
		var hi := now
		if ph == TideRaidFlow.Phase.RESPONSE and not _preview.is_empty():
			var st := flow.resp_stats(_preview)
			lo = now + int(st["heat_lo"])
			hi = now + int(st["heat_hi"])
		else:
			var pend := flow.pending_heat()
			lo = int(pend["lo"])
			hi = int(pend["hi"])
		if lo != now or hi != now:
			return tr("HEAT %d → %s") % [now, ("%d" % lo) if lo == hi else ("%d-%d" % [lo, hi])]
	return tr("HEAT %d") % now


func _build_hand() -> void:
	if flow.phase < TideRaidFlow.Phase.DRAW or flow.raid.ctx == null:
		hand_row.add_child(_lab(tr("The hand is dealt after DECAY."), TXT, DIM))
		return
	var cards := flow.hand_cards()
	for c in cards:
		var card: Array = [c["id"], c["type"], c["verb"]]
		var placed := String(c["site"]) != ""
		var held: bool = (c["verb"] == "SHIFT" or c["verb"] == "JAM") and not placed
		var col := VBoxContainer.new()
		col.mouse_filter = Control.MOUSE_FILTER_IGNORE
		col.add_theme_constant_override("separation", 2)
		var heat_cost := -1
		if SolaceTideRules.PLACEABLE.has(String(c["verb"])):
			heat_cost = flow.cfg.solace_tide_card_response_heat  # a card keeps its cost where it stands: standing guard is free, playing it adds it
		var cv := TideGlyphView.card_face(card, Vector2(CARD_W, CARD_H - 22.0), placed, bool(c["extra"]), _verb_title(String(c["verb"])), heat_cost)
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
		var cap := _lab(tr("on %s") % flow.site_name(StringName(c["site"])) if placed else (tr("held for response") if held and flow.phase < TideRaidFlow.Phase.PLAYOUT else ""), 11, GOLD if held else DIM, false)
		cap.custom_minimum_size.y = 18
		col.add_child(cap)
		hand_row.add_child(col)


## The card's title word.
func _verb_title(verb: String) -> String:
	match verb:
		"GUARD":
			return tr("GUARD")
		"SHIFT":
			return tr("SHIFT")
		"JAM":
			return tr("JAM")
		"WOUND":
			return tr("INFECTED")
		"DOSE":
			return tr("DOSE")
	return verb


func _card_tip(c: Dictionary) -> String:
	var verb_tip := {"GUARD": tr("GUARD: stands on a district and blocks a beam of its own type."),
		"SHIFT": tr("SHIFT: stands guard, or moves a sentry at the RESPONSE."),
		"JAM": tr("JAM: stands guard, or stops the hunter at the RESPONSE."),
		"WOUND": tr("INFECTED: a dead card that clogs the hand."), "DOSE": tr("DOSE: a healthy card that cures at DECAY.")}
	if c["verb"] == "WOUND":
		return verb_tip["WOUND"]
	var tip := "%s (%s)" % [verb_tip.get(c["verb"], ""), _type_name(String(c["type"]))]
	if SolaceTideRules.PLACEABLE.has(String(c["verb"])):
		tip += "\n" + tr("Standing guard is free; playing it at the RESPONSE adds %d Heat.") % flow.cfg.solace_tide_card_response_heat
	return tip


func _type_name(t: String) -> String:
	match t:
		"D":
			return tr("DRONE")
		"N":
			return tr("NETRUNNER")
		"E":
			return tr("ENFORCER")
	return t


## The raid tier words, translated.
func _tierw(t: String) -> String:
	match t:
		"HOLDS":
			return tr("HOLDS")
		"BATTERED":
			return tr("BATTERED")
		"DAMAGED":
			return tr("DAMAGED")
		"BREACHED":
			return tr("BREACHED")
		"EVADED":
			return tr("UNTOUCHED")  # the rules' tier word EVADED is a retired player word (N14): the player reads UNTOUCHED
		"CITY LOST":
			return tr("CITY LOST")
	return t


func _draw_deck() -> void:
	var h := flow.hud() if flow != null else {}
	if h.is_empty():
		return
	deck_strip.draw_rect(Rect2(Vector2.ZERO, deck_strip.size), PANEL_BG)
	deck_strip.draw_rect(Rect2(Vector2.ZERO, deck_strip.size), EDGE, false, 1.0)
	deck_strip.draw_string(ThemeDB.fallback_font, Vector2(6, 16), "DECK", HORIZONTAL_ALIGNMENT_LEFT, -1, SMALL, DIM)
	var deck: Array = h["deck"]
	for i in deck.size():
		var c: Array = deck[i]
		var p := _deck_cell(i)
		var wound := String(c[2]) == "WOUND"
		var r := Rect2(p, DECK_CELL)
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
	var deck: Array = f.hud()["deck"]
	if after:
		owned = SolaceTideCampaign.load_state(f.campaign, f.corp, f.cfg).owned
	elif f.phase == TideRaidFlow.Phase.PLAYOUT and f.raid.resolved and not f.raid.over:
		owned = _live_owned()
	var downs: Array[StringName] = []
	for c in deck:
		if String(c[2]) == "WOUND" and String(c[1]) != String(SolaceTideRules.HOME_WORD):
			infected.append(StringName(c[1]))
	for s in owned:
		if int(owned[s]) == SolaceTideState.Cond.TAKEN:
			taken.append(s)
		elif int(owned[s]) == SolaceTideState.Cond.DOWN:
			downs.append(s)
	IdSort.sort_ids(taken)
	IdSort.sort_ids(downs)
	layer.downs = downs
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
	layer.home_cols = []
	layer.ghost_home = false
	layer.beams = []
	layer.preview = []
	layer.blocks = []
	layer.hits = {}
	layer.impacts = []
	layer.focus = _focus_now() if f.phase == TideRaidFlow.Phase.PLAN else ""
	layer.sentries = _sentries_now()
	if f.raid.ctx != null and f.phase >= TideRaidFlow.Phase.PLAN and f.phase <= TideRaidFlow.Phase.RESPONSE:
		layer.ghost_home = f.raid.place["ghost"] != &""
		_plan_beams()
		if f.phase == TideRaidFlow.Phase.PLAN or f.phase == TideRaidFlow.Phase.FORECAST:
			layer.home_tiers = f.route_tiers()
			for ln in (f.raid.ctx.draw["cands"] as Array):
				layer.home_cols.append(TideGlyphs.type_color(String(ln["type"])))
	if f.phase == TideRaidFlow.Phase.PLAYOUT or (f.phase == TideRaidFlow.Phase.AFTERMATH and f.raid.resolved and not f.raid.over):
		_playout_beams()
	if f.phase == TideRaidFlow.Phase.RESPONSE and not _preview.is_empty():
		_set_layer_preview(_preview)


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


func _line_beam(ln: Dictionary, role: String, label: String, alpha: float, dashed: bool, width: float = TideRaidLayer.LINE_W, beam_name: String = "") -> Dictionary:
	return {"cells": ln["cells"], "type": ln["type"], "role": role, "label": label, "alpha": alpha, "dashed": dashed, "width": width,
		"route": String(ln["kind"]) == "ROUTE", "home": bool(ln["home"]), "name": beam_name}


func _plan_beams() -> void:
	var f := flow
	var d: Dictionary = f.raid.ctx.draw
	var n_fire := f.known_firing()
	var revealed := f.phase >= TideRaidFlow.Phase.REVEAL
	for i in (d["known"] as Array).size():
		if i < n_fire:
			layer.beams.append(_line_beam(d["known"][i], "known", tr("K%d") % (i + 1), 0.95, false, TideRaidLayer.LINE_W, "known%d" % i))
	for i in (d["cands"] as Array).size():
		var is_real := i == f.real_a()
		if revealed and not is_real:
			layer.beams.append(_line_beam(d["cands"][i], "cand", "", 0.3, true, TideRaidLayer.LINE_W, "cand%d" % i))
		else:
			var cb := _line_beam(d["cands"][i], "cand", "" if not revealed else tr("SEALED A"), 1.0 if revealed else 0.7, not revealed, 5.0 if revealed else TideRaidLayer.LINE_W, "cand%d" % i)
			cb["chip"] = ["A", "B", "C"][i]
			layer.beams.append(cb)
	if not revealed:
		for i in (d["hunters"] as Array).size():
			var hn := "hunter%d" % i
			# The HUNTER word only shows for the street the player points at, so it never covers a district tag.
			layer.beams.append(_line_beam(d["hunters"][i], "hunter", tr("HUNTER %d") % (i + 1) if _focus_now() == hn else "", 0.55, true, 2.0, hn))
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
## The hunter reveal's stage: 0 none, 1 both streets lit, 2 the other street dark.
var _hunter_stage: int = 0
## The street the hunter does not take fades to this alpha.
const HUNTER_DARK_ALPHA := 0.12
## Plan focus: the beam the legend row under the mouse names, and the one the player clicked.
var _focus_hover: String = ""
var _focus_pin: String = ""


func _playout_beams() -> void:
	var beats := flow.beats()
	var taken_now: Array = flow.last_raid.get("taken", [])
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
		if cur and _hunter_stage == 1 and role == "hunter":
			_hunter_stage_beams()
			continue
		var beam := _line_beam(ln, role, lab, alpha, String(b["kind"]) == "hunter_jammed", 5.0 if cur else 2.0, String(b["beam"]))
		beam["current"] = cur
		beam["stop"] = _stop_of(b)
		beam["pulse"] = cur and _stage == 0 and flow.phase == TideRaidFlow.Phase.PLAYOUT
		var passed: Array = []
		for e in b["trace"]:
			if e[2] == "hit":
				passed.append(String(e[1]))
		beam["hit_sites"] = passed
		layer.beams.append(beam)
		if cur and _hunter_stage == 2 and role == "hunter":
			_dark_street_beam()
		# A beat's marks land with its impact (stage 1 on); the beats before it are over.
		var landed := done or flow.phase == TideRaidFlow.Phase.AFTERMATH or (cur and _stage >= 1)
		if landed:
			for e in b["trace"]:
				if e[2] == "hit":
					layer.hits[StringName(e[1])] = "hit"
					if cur and not taken_now.has(String(e[1])):
						layer.impacts.append({"site": e[1], "col": TideGlyphs.type_color(String(ln["type"])), "label": tr("HIT: %s") % flow.site_name(StringName(e[1]))})
				elif e[2] == "block" and cur:
					layer.blocks.append([e[1], ln["type"]])


## Where beat `b` stops: its guard when a sentry blocks it, HOME when it ends there (a hit or a shield), "" when it runs its whole path.
func _stop_of(b: Dictionary) -> String:
	var stop := ""
	for e in b["trace"]:
		if e[2] == "block":
			return String(e[1])
		if e[2] == "home" or e[2] == "shield":
			stop = "HOME"
	return stop


## The owned Sites as the playout has shown them: the raid's hits applied, the beats before the current one and the current one once it lands.
func _live_owned() -> Dictionary:
	var owned: Dictionary = flow.raid.st.owned.duplicate()
	var beats := flow.beats()
	for i in beats.size():
		if i > _beam_n or (i == _beam_n and _stage < 1):
			break
		for e in beats[i]["trace"]:
			if e[2] != "hit":
				continue
			var s := StringName(String(e[1]))
			var was := int(owned.get(s, -1))
			if was == SolaceTideState.Cond.OK:
				owned[s] = SolaceTideState.Cond.DOWN
			elif was == SolaceTideState.Cond.DOWN:
				owned[s] = SolaceTideState.Cond.TAKEN
	return owned


## The hunter's reveal, stage 1: both candidate streets lit at full strength and numbered.
func _hunter_stage_beams() -> void:
	var hs: Array = flow.raid.ctx.draw["hunters"]
	for hi in hs.size():
		var hb := _line_beam(hs[hi], "hunter", tr("HUNTER %d") % (hi + 1), 1.0, false, 5.0, "hunter%d" % hi)
		hb["current"] = true
		layer.beams.append(hb)


## Stage 2: the street the hunter does not take goes dark (the taken one plays as the beat).
func _dark_street_beam() -> void:
	var hs: Array = flow.raid.ctx.draw["hunters"]
	var real := int(flow.raid.ctx.draw["hunter_real"])
	for hi in hs.size():
		if hi != real:
			layer.beams.append(_line_beam(hs[hi], "hunter", "", HUNTER_DARK_ALPHA, true, 3.0, "hunter%d" % hi))


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
			if city_lost_showing():
				_dismiss_city_lost()
			else:
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
	_dismiss_city_lost()
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
	_stage = 0
	var beats := flow.beats()
	var gap := Motion.seconds_live(&"raid_step_beat")
	var rest := Motion.seconds_live(&"raid_phase_gap")
	# A beat is the pulse's travel, the impact's rest and the settle: the travel takes what the step beat leaves after the two rests.
	var travel := maxf(0.0, gap - 2.0 * rest)
	for i in beats.size():
		_beam_n = i
		var b: Dictionary = beats[i]
		layer.clear_fx()
		if String(b["kind"]).begins_with("hunter"):
			# The reveal, staged: both candidate streets light and hold for a beat, then one goes dark as the hunter takes the other.
			_hunter_stage = 1
			_stage = 0
			_log.append(tr("HUNTER: both streets are lit."))
			_sync_layer()
			_playout_refresh()
			if not await _wait(gap):
				return
			_hunter_stage = 2
		# Stage 0: the pulse travels from its start along the path to where the raid stops it.
		_stage = 0
		layer.start_pulse(0.0 if _skip else travel)
		_sync_layer()
		_playout_refresh()
		if not await _wait(travel):
			return
		# Stage 1: the impact lands (a shield bursts at the guard, HOME is hit, a Site is lost and its card flies into the deck).
		_stage = 1
		layer.pulse_secs = 0.0
		_land_beat(b)
		_log.append(_beat_line(b))
		_sync_layer()
		_build_hud()
		deck_strip.queue_redraw()
		_playout_refresh()
		beat_stage.emit(_beam_n, _stage)
		if not await _wait(rest):
			return
		# Stage 2: the beat settles before the next one fires.
		_stage = 2
		_sync_layer()
		beat_stage.emit(_beam_n, _stage)
		if not await _wait(rest):
			return
	_hunter_stage = 0
	_playing = false
	_beam_n = beats.size()
	_stage = 0
	layer.clear_fx()
	flow.playout_done()
	_rebuild()


## Waits `secs` of the playout (none under SKIP or reduced motion). False when the screen left the tree meanwhile.
func _wait(secs: float) -> bool:
	if secs > 0.0 and not _skip:
		await get_tree().create_timer(secs).timeout
	return is_inside_tree()


## The beat `b` lands: what its trace says the beam did, as effects on the map, and the INFECTED cards it adds tick the HUD live.
func _land_beat(b: Dictionary) -> void:
	var col := TideGlyphs.type_color(String(b["line"]["type"]))
	var taken_now: Array = flow.last_raid.get("taken", [])
	var shield_t := Motion.seconds_live(&"shield_hex")
	var mark_t := Motion.seconds_live(&"impact_mark")
	for e in b["trace"]:
		var site := StringName(String(e[1]))
		match String(e[2]):
			"block":
				layer.add_burst("shield", site, col, shield_t)
			"shield":
				layer.add_burst("shield", &"HOME", TideGlyphs.COBALT_HOT, shield_t)
			"home":
				layer.add_burst("home", &"HOME", TideGlyphs.RED, mark_t)
				if flow.cfg.solace_tide_home_hit_infects:
					_land_card(&"HOME")
			"hit":
				if taken_now.has(String(e[1])):
					layer.add_burst("bloom", site, col, mark_t)
					_land_card(site)


## One INFECTED card lands: the flow counts it (the meter and the deck strip tick) and a card flies from `site` to its slot in the deck strip.
func _land_card(site: StringName) -> void:
	flow.land_infected()
	var fresh := flow.new_wounds()
	var n := mini(flow.landed, fresh.size())
	if n <= 0:
		return
	var id := String(fresh[n - 1][0])
	var deck: Array = flow.hud()["deck"]
	var idx := 0
	for i in deck.size():
		if String(deck[i][0]) == id:
			idx = i
			break
	layer.add_flight(site, _deck_slot(idx), Motion.seconds_live(&"raid_phase_gap") * 2.0)


## The centre of deck cell `i` of the deck strip, in the layer's px.
func _deck_slot(i: int) -> Vector2:
	var local := _deck_cell(i) + DECK_CELL * 0.5
	return layer.get_global_transform().affine_inverse() * (deck_strip.get_global_transform() * local)


## The top-left of deck cell `i` in the deck strip.
func _deck_cell(i: int) -> Vector2:
	return Vector2(8 + (i % DECK_COLS) * 14, 26 + (i / DECK_COLS) * 16)


## Rebuilds only the side log during the playout.
func _playout_refresh() -> void:
	_clear(body)
	_clear(foot)
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
	var line := "%s: %s" % [head, ", ".join(parts) if not parts.is_empty() else tr("touches nothing")]
	if String(b["kind"]) == "sealed_b":
		var others := SolaceTideRules._others(flow.raid.ctx, flow.real_a())
		var lean: String = ["A", "B", "C"][int(others[int(b["lean"])])]
		var pick: String = ["A", "B", "C"][int(others[int(b["pick"])])]
		line = (tr("The corp leans to route %s") % lean) + "\n" + (tr("JAM flips the pick: route %s") % pick if bool(b.get("flipped", false)) else tr("It picks route %s") % pick) + "\n" + line
	elif String(b["kind"]) == "hunter":
		line = tr("HUNTER REVEAL: street %d") % (int(flow.raid.ctx.draw["hunter_real"]) + 1) + "\n" + line
	return line


func done_hq() -> void:
	var opt: Array = [_hq_repair, _hq_build, _hq_patch]
	flow.apply_hq_step(opt)
	finished.emit()


# ------------------------------------------------------------------------------------------------ pages
func _page_decay() -> void:
	body.add_child(_title(tr("DECAY")))
	body.add_child(_lab(tr("Raid %d") % flow.raid_number(), TXT, DIM))
	if flow.raid.raid_idx == 0:
		body.add_child(_lab(tr("Nothing decays before the first raid."), TXT))
	elif flow.decay_tally.is_empty() or _tally_parts(flow.decay_tally, {}).is_empty():
		body.add_child(_lab(tr("No district sat DOWN since the last raid: nothing decays."), TXT))
	else:
		body.add_child(_lab(tr("Districts left DOWN since the last raid fall to the Tide."), TXT))
		_tally_block(flow.infected_tally(), true)
	if flow.raid.over:
		body.add_child(_lab(tr("The infection now outnumbers the healthy cards."), TXT, TideGlyphs.RED))
	body.add_child(_btn(tr("CONTINUE"), cont))


## The INFECTED tally rows: [{label, n (signed), tip}] for DECAY's tally `dec` and the raid's `rd` (either may be empty).
func _tally_parts(dec: Dictionary, rd: Dictionary) -> Array:
	var parts: Array = []
	if not dec.is_empty():
		if int(dec["taken"]) > 0:
			var names := PackedStringArray()
			for s in flow.decay_sites():
				names.append(flow.site_name(s))
			parts.append({"label": tr("DECAY TAKEN: %s") % ", ".join(names), "n": int(dec["taken"]), "tip": tr("A district left DOWN since the last raid is TAKEN and adds an INFECTED card.")})
		if bool(dec["spread"]):
			parts.append({"label": tr("Spread: the Tide moves on"), "n": 1, "tip": tr("Enough Sites fell since the last raid for the infection to spread.")})
		if bool(dec["cancelled"]):
			parts.append({"label": tr("A DOSE stopped the spread"), "n": 0, "tip": ""})
		if int(dec["cured"]) > 0:
			parts.append({"label": tr("DOSE cured %d") % int(dec["cured"]), "n": -int(dec["cured"]), "tip": ""})
	if not rd.is_empty():
		if int(rd["sites"]) > 0:
			var lost := PackedStringArray()
			for s in flow.last_raid.get("taken", []):
				lost.append(flow.site_name(StringName(String(s))))
			parts.append({"label": tr("Site lost: %s") % ", ".join(lost), "n": int(rd["sites"]), "tip": tr("TAKEN in the raid: each lost Site adds an INFECTED card.")})
		if int(rd["home"]) > 0:
			parts.append({"label": tr("HOME hit"), "n": int(rd["home"]), "tip": tr("A hit on HOME infects a card.")})
	return parts


## The INFECTED tally in two sections that never share a row: DECAY (before the raid: "INFECTED before to mid") and, when `decay_only` is false and the
## raid was played, THE RAID ("INFECTED mid to after"), each with one row per source of its change (see `_tally_parts`).
func _tally_block(t: Dictionary, decay_only: bool) -> void:
	var box := VBoxContainer.new()
	box.name = "InfectedTally"
	box.add_theme_constant_override("separation", 4)
	var dparts := _tally_parts(t["decay"], {})
	if decay_only or not dparts.is_empty():
		box.add_child(_tally_section(tr("DECAY (before the raid)"), "TallyDecay", int(t["before"]), int(t["mid"]), dparts, ""))
	if not decay_only and not (t["raid"] as Dictionary).is_empty():
		var rparts := _tally_parts({}, t["raid"])
		box.add_child(_tally_section(tr("THE RAID"), "TallyRaid", int(t["mid"]), int(t["after"]), rparts, tr("No Site lost, no HOME hit: no INFECTED card.")))
	body.add_child(box)


## One section of the tally: its title, "INFECTED a to b" and a row per source (or `none_text` when there is none).
func _tally_section(title: String, node_name: String, start: int, end: int, parts: Array, none_text: String) -> Control:
	var sec := VBoxContainer.new()
	sec.name = node_name
	sec.add_theme_constant_override("separation", 2)
	sec.add_child(_lab(title, SMALL, GOLD, false))
	var head := _hrow(6)
	var gv := TideGlyphView.new()
	gv.kind = TideGlyphView.Kind.PIP_DECK
	gv.word = "WOUND"
	gv.custom_minimum_size = Vector2(18, 18)
	head.add_child(gv)
	head.add_child(_lab(tr("INFECTED %d to %d") % [start, end], TXT, TideGlyphs.RED if end > start else INK, false))
	sec.add_child(head)
	for p in parts:
		var r := _hrow(6)
		var n := int(p["n"])
		var sign_txt := "+%d" % n if n > 0 else ("%d" % n if n < 0 else "0")
		r.add_child(_lab(sign_txt, SMALL, TideGlyphs.RED if n > 0 else (TideGlyphs.TIER_COLOR["HOLDS"] if n < 0 else DIM), false))
		var l := _lab(String(p["label"]), SMALL, INK, true)
		r.add_child(l)
		if String(p["tip"]) != "":
			r.tooltip_text = String(p["tip"])
			r.mouse_filter = Control.MOUSE_FILTER_PASS
		sec.add_child(r)
	if parts.is_empty() and none_text != "":
		sec.add_child(_lab(none_text, SMALL, DIM, true))
	return sec


func _page_draw() -> void:
	body.add_child(_title(tr("DRAW")))
	var h := flow.hud()
	body.add_child(_lab(tr("The deck deals %d cards. A gold edge marks the card a Heat level adds.") % int(h["hand"]), TXT))
	body.add_child(_lab(tr("%d known beams will fire after your RESPONSE; they are shown now.") % int(h["beams"]), TXT, DIM))
	body.add_child(_btn(tr("CONTINUE"), cont))


func _page_plan() -> void:
	body.add_child(_title(tr("PLAN")))
	body.add_child(_lab(tr("Pick a card, then a district on a beam's path. Up to %d guards. The ghost shields HOME for a Heat cost.") % flow.cfg.solace_tide_max_placed, TXT))
	_loss_banner()
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


## The PLAN legend. Each row names a beam; the one under the mouse (or clicked) stays lit on the map and every other route dims.
## The warning when one more INFECTED card ends the city.
func _loss_banner() -> void:
	if not flow.loss_warning():
		return
	var chip := PanelContainer.new()
	chip.name = "LossBanner"
	chip.add_theme_stylebox_override("panel", UiTheme.box(Palette.TIDE_PANEL_HI, TideGlyphs.RED, 2, 8, 4))
	var r := _hrow(6)
	r.add_child(TideGlyphView.tier("BREACHED", 20.0))
	var fallen := flow.loss_margin() == 0
	r.add_child(_lab(tr("CITY FALLS AT RAID END") if fallen else tr("1 more = CITY LOST"), BIG if not fallen else TXT, TideGlyphs.RED, false))
	chip.add_child(r)
	chip.tooltip_text = tr("The infection already outnumbers the healthy cards: the city falls when this raid closes, unless HOME falls first.") if fallen \
		else tr("One more INFECTED card and the infection outnumbers the healthy cards: the campaign ends when this raid resolves.")
	body.add_child(chip)


func _beam_legend() -> void:
	var d: Dictionary = flow.raid.ctx.draw
	var n_fire := flow.known_firing()
	for i in (d["known"] as Array).size():
		var ln: Dictionary = d["known"][i]
		var live := i < n_fire
		var r := _hrow(6)
		r.add_child(_type_icon(String(ln["type"]), not live))
		r.add_child(_lab(tr("Known beam %d: %s, fires after the RESPONSE") % [i + 1, _type_name(String(ln["type"]))] if live else tr("Known beam %d: waits for more Heat") % (i + 1), SMALL, INK if live else Palette.TIDE_OFF, true))
		if live:
			body.add_child(_legend_hot(r, "known%d" % i))
		else:
			body.add_child(r)
	var rr := _hrow(6)
	rr.add_child(_lab(tr("Sealed routes: two will fire"), SMALL, DIM, false))
	for i in (d["cands"] as Array).size():
		var cell := _hrow(3)
		cell.add_child(TideGlyphView.chip(["A", "B", "C"][i], TideGlyphs.type_color(String(d["cands"][i]["type"]))))
		cell.add_child(_type_icon(String(d["cands"][i]["type"]), false))
		rr.add_child(_legend_hot(cell, "cand%d" % i))
	body.add_child(rr)
	var hr := _hrow(6)
	var hd: Array = d["hunters"]
	hr.add_child(_type_icon(String(d["hunter_type"]), false))
	var hh := TideGlyphView.new()
	hh.custom_minimum_size = Vector2(18, 18)
	hh.draw.connect(func() -> void: TideGlyphs.hound(hh, hh.size * 0.5))
	hr.add_child(hh)
	hr.add_child(_lab(tr("Hunter: one of %d streets, revealed last") % hd.size(), SMALL, DIM, false))
	for i in hd.size():
		var cell := _hrow(2)
		cell.add_child(_lab("%d" % (i + 1), SMALL, INK, false))
		hr.add_child(_legend_hot(cell, "hunter%d" % i))
	body.add_child(hr)
	if _focus_pin != "":
		body.add_child(_lab(tr("Click the lit row again to show every route."), 11, DIM))


## Makes legend row `row` point at beam `beam`: hover lights it, a click pins it. Returns the wrapper to add.
func _legend_hot(row: Control, beam: String) -> Control:
	var box := PanelContainer.new()
	box.name = "Legend_%s" % beam
	var pinned := _focus_pin == beam
	box.add_theme_stylebox_override("panel", UiTheme.box(Palette.TIDE_PANEL_HI if pinned else Palette.CLEAR, GOLD if pinned else Palette.CLEAR, 1, 3, 1))
	box.mouse_filter = Control.MOUSE_FILTER_STOP
	box.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	box.add_child(row)
	_ignore_tree(row)
	box.mouse_entered.connect(func() -> void: _set_hover(beam))
	box.mouse_exited.connect(func() -> void:
		if _focus_hover == beam:
			_set_hover(""))
	box.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
			_focus_pin = "" if _focus_pin == beam else beam
			_focus_hover = ""
			_rebuild())
	return box


func _ignore_tree(c: Node) -> void:
	if c is Control:
		(c as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	for ch in c.get_children():
		_ignore_tree(ch)


func _set_hover(beam: String) -> void:
	_focus_hover = beam
	_sync_layer()


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
	box.add_child(_lab(_tierw(String(g["hold"])), TXT, TideGlyphs.tier_color(String(g["hold"])), false))
	if (g["best"] as Dictionary).is_empty():
		box.add_child(_lab("· " + tr("no response changes this"), SMALL, DIM, true))
	else:
		var best: Dictionary = g["best"]
		box.add_child(_lab("· " + tr("best:"), SMALL, DIM, false))
		box.add_child(TideGlyphView.resp(best["resp"], 24.0))
		box.add_child(_arrow_view(GOLD))
		box.add_child(TideGlyphView.tier(String(best["worst"]), 18.0))
		box.add_child(_lab(_tierw(String(best["worst"])), TXT, TideGlyphs.tier_color(String(best["worst"])), false))
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
		r.add_child(_lab(tr("LOCKED: every outcome is %s under HOLD.") % _tierw(String(s["worst"])), TXT, GOLD, true))
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
	body.add_child(_lab(tr("Every outcome of this plan under HOLD. Each column is the corp's first sealed route (A, B or C); its tiles count the outcomes that end in that tier, over the corp's second route and the hunter's street."), SMALL, DIM))
	_loss_banner()
	var table := HBoxContainer.new()
	table.add_theme_constant_override("separation", 10)
	table.name = "ForecastTable"
	for a in (flow.raid.ctx.draw["cands"] as Array).size():
		var col := VBoxContainer.new()
		col.name = "Route_%s" % ["A", "B", "C"][a]
		col.add_theme_constant_override("separation", 4)
		# The column head carries the beam: the same chip (letter on the beam's color) the map draws at that route's start and at HOME,
		# the beam glyph in its color and the type shape.
		var head := _hrow(4)
		var rtype := String(flow.raid.ctx.draw["cands"][a]["type"])
		head.add_child(TideGlyphView.chip(["A", "B", "C"][a], TideGlyphs.type_color(rtype), 22.0))
		head.add_child(TideGlyphView.icon(TideGlyphView.Kind.BEAM, 22.0, TideGlyphs.type_color(rtype)))
		head.add_child(_type_icon(rtype, false))
		col.add_child(head)
		# The outcomes of this route, one tile per (tier, INFECTED added, ends the run), worst first: no row of identical tiles.
		var total := 0
		for r in flow.forecast():
			if r["a"] == a:
				total += 1
		for t in flow.route_tiles(a):
			var tile := TideGlyphView.tile(String(t["tier"]), Vector2(TILE_W, TILE_H), int(t["n"]), int(t["inf"]), bool(t["lethal"]))
			tile.name = "Tile_%s_%d" % [t["tier"], int(t["inf"])]
			var tip := tr("%d of %d outcomes of route %s end %s, +%d INFECTED.") % [t["n"], total, ["A", "B", "C"][a], _tierw(String(t["tier"])), t["inf"]]
			if bool(t["lethal"]):
				tip += "\n" + tr("ENDS RUN: the infection outnumbers the healthy cards.")
			tile.tooltip_text = tip
			col.add_child(tile)
		table.add_child(col)
	body.add_child(table)
	body.add_child(_guard_line())
	_summary_lines()
	var fr := flow.friction()
	if fr != TideRaidFlow.FRICTION_NONE:
		body.add_child(_lab(_friction_text(fr), TXT, TideGlyphs.HEAT_COL))
	var row := _hrow(6)
	row.add_child(_btn(tr("BACK"), back))
	var armed := flow.launch_armed
	row.add_child(_btn(tr("CONFIRM LAUNCH") if armed else tr("LAUNCH"), launch, true, GOLD if armed else TideGlyphs.TIER_COLOR["HOLDS"]))
	foot.add_child(row)


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
	r.add_child(_lab(tr("Sealed route A is a %s route. It fires after your RESPONSE.") % _type_name(String(ln["type"])), TXT))
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
		gr.add_child(TideGlyphView.resp([g[0]], 20.0, "", true))
		gr.add_child(_lab(tr(String(g[1])), 11, Palette.TIDE_OFF, true))
		gr.name = "Ghost_%s" % g[0]
		body.add_child(gr)
	# The foot: what a second press means, and the button, pinned so the list above can scroll under it.
	if flow.lethal_armed:
		var lr := _hrow(4)
		lr.name = "LethalConfirm"
		lr.add_child(TideGlyphView.tier("BREACHED", 22.0))
		lr.add_child(_lab(tr("This response can END THE RUN. Press again to commit it."), TXT, TideGlyphs.RED, true))
		foot.add_child(lr)
	elif flow.hold_armed:
		var w := flow.hold_worse_group()
		var r := _hrow(4)
		r.add_child(_lab(tr("HOLD is worse than"), TXT, TideGlyphs.HEAT_COL, false))
		if w >= 0:
			r.add_child(TideGlyphView.resp(flow.groups[w]["members"][0]["resp"], 24.0))
		r.add_child(_lab(tr("launch anyway?"), TXT, TideGlyphs.HEAT_COL, false))
		foot.add_child(r)
	_status_line(foot)
	var armed := flow.hold_armed or flow.lethal_armed
	var word := tr("COMMIT")
	var accent: Color = TideGlyphs.TIER_COLOR["HOLDS"]
	if flow.lethal_armed:
		word = tr("CONFIRM: END THE RUN")
		accent = TideGlyphs.RED
	elif flow.hold_armed:
		word = tr("CONFIRM HOLD")
		accent = GOLD
	var commit_btn := _btn(word, commit, flow.resp_sel >= 0, accent)
	commit_btn.name = "Commit"
	foot.add_child(commit_btn)
	if armed:
		_focus.call_deferred(commit_btn)


func _group_row(gi: int) -> Control:
	var g: Dictionary = flow.groups[gi]
	var m: Dictionary = g["members"][0]
	var sel := flow.resp_sel == gi
	var better: bool = g["better"]
	var lethal: bool = g["lethal_any"]
	var btn := Button.new()
	btn.name = "Resp_%d" % gi
	btn.focus_mode = Control.FOCUS_ALL
	btn.custom_minimum_size.y = 42.0
	var edge := TideGlyphs.RED if lethal else (GOLD if better else EDGE)
	btn.add_theme_stylebox_override("normal", UiTheme.box(Palette.TIDE_PANEL_HI if sel else Palette.TIDE_ROW, edge, 2, 6, 3))
	btn.add_theme_stylebox_override("hover", UiTheme.box(Palette.TIDE_ROW_HOT, edge.lightened(0.3), 2, 6, 3))
	btn.add_theme_stylebox_override("pressed", UiTheme.box(Palette.TIDE_ROW_PRESSED, GOLD, 2, 6, 3))
	btn.pressed.connect(func() -> void: select_group(gi))
	btn.mouse_entered.connect(func() -> void: _hover_group(gi))
	var row := _hrow(5)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.offset_left = 4
	row.offset_right = -2
	var sent_t := ""
	if String(m["head"]) == "REDEPLOY":
		sent_t = String(flow.raid.ctx.cards[(flow.raid.place["sentries"] as Dictionary).get(m["resp"][1], "")][0]) if (flow.raid.place["sentries"] as Dictionary).has(m["resp"][1]) else ""
	var gl := TideGlyphView.resp(m["resp"], 30.0, sent_t, false)
	gl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(gl)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_theme_constant_override("separation", 0)
	var lab := _lab(String(g["label"]), SMALL, INK, false)
	lab.name = "Label"
	lab.clip_text = true
	lab.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_child(lab)
	var sub := _row_note(g)
	if sub.text != "":
		col.add_child(sub)
	else:
		sub.free()
	row.add_child(col)
	# The row's numbers, from the forecast: the Heat the response leaves, the INFECTED cards it adds, then the tier (worst / best).
	row.add_child(_ignore(_stat_chip("HEAT", int(m["heat_lo"]), int(m["heat_hi"]))))
	row.add_child(_ignore(_stat_chip("INFECTED", int(m["inf_lo"]), int(m["inf_hi"]))))
	var worst := String(m["worst"])
	var best := String(m["best"])
	var tr_ := _hrow(2)
	tr_.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tr_.add_child(_ignore(TideGlyphView.tier(worst, 18.0)))
	if best != worst:
		tr_.add_child(_lab("/", SMALL, DIM, false))
		tr_.add_child(_ignore(TideGlyphView.tier(best, 18.0)))
	row.add_child(tr_)
	btn.add_child(row)
	btn.tooltip_text = _group_tip(g)
	return btn


func _ignore(c: Control) -> Control:
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


## A number chip of a response row: the Heat flame or the INFECTED pip with "+N" (or "+lo-hi" when the outcomes differ). The label child
## `Val` holds the text.
func _stat_chip(kind: String, lo: int, hi: int) -> Control:
	var h := _hrow(2)
	h.name = "HeatChip" if kind == "HEAT" else "InfChip"
	if kind == "HEAT":
		h.add_child(_ignore(TideGlyphView.icon(TideGlyphView.Kind.FLAME, 16.0)))
	else:
		var pip := TideGlyphView.new()
		pip.kind = TideGlyphView.Kind.PIP_DECK
		pip.word = "WOUND"
		pip.custom_minimum_size = Vector2(14, 16)
		h.add_child(_ignore(pip))
	var txt := "%+d" % lo if lo == hi else "%+d..%+d" % [lo, hi]
	var bad := hi > 0 if kind == "INFECTED" else false
	var col: Color = TideGlyphs.RED if bad else (TideGlyphs.HEAT_COL if kind == "HEAT" and hi > 0 else DIM)
	var v := _lab(txt, SMALL, col, false)
	v.name = "Val"
	h.add_child(_ignore(v))
	h.tooltip_text = tr("Heat the raid leaves with this response.") if kind == "HEAT" else tr("INFECTED cards this response adds.")
	return h


## The small line under a row's text: how many rows fold into HOLD, and the mark of a response that can end the run.
func _row_note(g: Dictionary) -> Label:
	var parts := PackedStringArray()
	var col := DIM
	if int(g.get("same", 0)) > 0:
		parts.append(tr("%d rows = HOLD") % int(g["same"]))
	if bool(g["lethal_any"]):
		parts.append(tr("ENDS RUN") if bool(g["lethal_all"]) else tr("may END RUN"))
		col = TideGlyphs.RED
	var l := _lab(", ".join(parts), 11, col, false)
	l.name = "Note"
	return l


## What a response needs from the hand, in words (the row's tooltip carries it; the row itself stays short).
func _card_need(r: Array) -> String:
	match String(r[0]):
		"REDEPLOY", "DIVERT":
			return tr("needs a SHIFT card")
		"DEPLOY":
			return tr("uses a %s card") % flow.type_name(String(r[1]))
		"JAM", "JAM_B":
			return tr("needs a JAM card")
	return ""


func _group_tip(g: Dictionary) -> String:
	var m: Dictionary = g["members"][0]
	var lines := PackedStringArray([flow.resp_label_long(m["resp"])])
	lines.append(tr("Worst %s, best %s over the remaining outcomes.") % [_tierw(String(m["worst"])), _tierw(String(m["best"]))])
	lines.append(tr("Heat %s, INFECTED %s.") % [_range_txt(int(m["heat_lo"]), int(m["heat_hi"])), _range_txt(int(m["inf_lo"]), int(m["inf_hi"]))])
	var need := _card_need(m["resp"])
	if need != "":
		lines.append(need)
	if bool(g["lethal_any"]):
		lines.append(tr("ENDS RUN on %s of the outcomes: the infection outnumbers the healthy cards.") % (tr("every one") if bool(g["lethal_all"]) else tr("some")))
	if bool(g["better"]):
		lines.append(tr("Better than doing nothing."))
	return "\n".join(lines)


func _range_txt(lo: int, hi: int) -> String:
	return ("%+d" % lo) if lo == hi else ("%+d to %+d" % [lo, hi])


func _variants(gi: int) -> Control:
	var box := VBoxContainer.new()
	box.name = "Variants"
	var members: Array = flow.groups[gi]["members"]
	for mi in members.size():
		var m: Dictionary = members[mi]
		var b := _btn(flow.resp_label_long(m["resp"]), func() -> void: select_group(gi, mi), true, EDGE)
		b.add_theme_font_size_override("font_size", SMALL)
		box.add_child(b)
	return box


func _hover_group(gi: int) -> void:
	if flow.phase != TideRaidFlow.Phase.RESPONSE or flow.resp_sel >= 0 or layer == null:
		return
	_set_layer_preview(flow.groups[gi]["members"][0]["resp"])


func _set_layer_preview(r: Array) -> void:
	layer.preview = r
	layer.preview_type = ""
	if not r.is_empty() and String(r[0]) == "REDEPLOY":
		var sent: Dictionary = flow.raid.place["sentries"]
		if sent.has(r[1]):
			layer.preview_type = String(flow.raid.ctx.cards[sent[r[1]]][0])


func select_group(gi: int, mi: int = 0) -> void:
	_preview = flow.select_group(gi, mi)
	_status = ""
	_rebuild()
	_set_layer_preview(_preview)


func _page_playout() -> void:
	body.add_child(_title(tr("RAID")))
	for line in _log:
		body.add_child(_lab(line, TXT, INK))
	# While a pulse travels its beam is named, its result not yet told.
	if _playing and _stage == 0 and _beam_n >= 0 and _beam_n < flow.beats().size():
		body.add_child(_lab(tr("%s: travelling...") % _beam_label(flow.beats()[_beam_n]), TXT, DIM))
	if _playing:
		body.add_child(_btn(tr("SKIP"), func() -> void: _skip = true))


func _page_aftermath() -> void:
	body.add_child(_title(tr("AFTERMATH")))
	var a := flow.aftermath()
	var tier_word := String(a["tier"])
	# The raid's own tier always stamps; CITY LOST is the banner under it, never a replacement for it (DECAY alone can end the city: then
	# there is no raid tier and the stamp is the loss itself).
	var lost_word := tier_word == "CITY LOST"
	var stamp := _hrow(10)
	stamp.name = "AftermathStamp"
	stamp.add_child(TideGlyphView.tier("BREACHED" if lost_word else tier_word, 48.0))
	stamp.add_child(_lab(_tierw(tier_word), 28, TideGlyphs.RED if lost_word else TideGlyphs.tier_color(tier_word), false))
	body.add_child(stamp)
	var banner := String(a["banner"])
	var col := TideGlyphs.TIER_COLOR["HOLDS"] if banner == "CELL HOLDS" else TideGlyphs.RED
	var bl := _lab(_banner_word(banner), BIG, col)
	bl.name = "Banner"
	body.add_child(bl)
	if bool(a["raided"]):
		body.add_child(_lab(tr("HOME %d to %d") % [a["home_before"], a["home_after"]], TXT))
		body.add_child(_lab(tr("%d DOWN, %d TAKEN, %d INFECTED in all") % [(a["down"] as Array).size(), (a["taken"] as Array).size(), a["infected"]], TXT))
		if int(a["heat_delta"]) != 0 or int(a["schematics_delta"]) != 0:
			body.add_child(_lab(tr("Heat %+d, Schematics %+d") % [a["heat_delta"], a["schematics_delta"]], TXT, DIM))
	# Where the INFECTED cards came from, so the count never jumps unexplained: DECAY's changes and the raid's own, apart.
	_tally_block(a["tally"], false)
	if banner_is_loss(a):
		body.add_child(_lab(tr("CITY LOST: the INFECTED cards outnumber the healthy ones."), TXT, TideGlyphs.RED))
	body.add_child(_btn(tr("CONTINUE"), cont))
	if banner_is_loss(a) and not _lost_shown:
		_show_city_lost(a)


## True when the aftermath is the CITY LOST stamp.
func banner_is_loss(a: Dictionary) -> bool:
	return String(a["banner"]) == "CITY LOST"


## CITY LOST as a full-screen moment: the screen goes dark red, the skull and the words land over it with the final count; CONTINUE (or Enter)
## lets the aftermath show.
func _show_city_lost(a: Dictionary) -> void:
	_lost_shown = true
	if _lost_overlay != null and is_instance_valid(_lost_overlay):
		_lost_overlay.queue_free()
	var ov := Control.new()
	ov.name = "CityLost"
	ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ov.mouse_filter = Control.MOUSE_FILTER_STOP
	var wash := ColorRect.new()
	wash.color = Color(Palette.TIDE_RED.darkened(0.82), 0.93)
	wash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	wash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ov.add_child(wash)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ov.add_child(center)
	var box := VBoxContainer.new()
	box.name = "CityLostBox"
	box.add_theme_constant_override("separation", 14)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	center.add_child(box)
	var skull := TideGlyphView.tier("BREACHED", 150.0)
	skull.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(skull)
	var title := _lab(tr("CITY LOST"), CITY_LOST_PX, TideGlyphs.RED, false)
	title.name = "CityLostTitle"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)
	var h := flow.hud()
	var sub := _lab(tr("INFECTED %d outnumber the healthy cards (%d)") % [int(a["infected"]), int(h["healthy"])], BIG, INK, false)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(sub)
	var go := _btn(tr("CONTINUE"), _dismiss_city_lost, true, TideGlyphs.RED)
	go.name = "CityLostContinue"
	go.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	go.custom_minimum_size = Vector2(220, 44)
	box.add_child(go)
	add_child(ov)
	_lost_overlay = ov
	if Motion.live(&"defeat_stamp"):
		ov.modulate.a = 0.0
		_lost_fade = Motion.fade(ov, 1.0, &"defeat_stamp")
	_lost_pop = Motion.pop(title, &"raid_result_banner")
	_focus.call_deferred(go)


var _lost_fade: Tween = null
var _lost_pop: Tween = null


## MotionSkip (a short motion: `register_passive`): true while the CITY LOST moment fades or pops in.
func motion_running() -> bool:
	return (_lost_fade != null and _lost_fade.is_valid() and _lost_fade.is_running()) or (_lost_pop != null and _lost_pop.is_valid() and _lost_pop.is_running())


## MotionSkip: the CITY LOST moment at rest.
func complete_motion() -> void:
	if city_lost_showing():
		Motion.settle(_lost_overlay, ^"modulate:a")
		var title := _lost_overlay.find_child("CityLostTitle", true, false)
		if title != null:
			Motion.settle(title, ^"scale")
	_lost_fade = null
	_lost_pop = null


## Gives `c` the keyboard focus when it is still on screen (called deferred).
func _focus(c: Control) -> void:
	if is_instance_valid(c) and c.is_inside_tree():
		c.grab_focus()


## True while the CITY LOST moment covers the screen.
func city_lost_showing() -> bool:
	return _lost_overlay != null and is_instance_valid(_lost_overlay) and not _lost_overlay.is_queued_for_deletion()


func _dismiss_city_lost() -> void:
	if _lost_overlay != null and is_instance_valid(_lost_overlay):
		_lost_overlay.queue_free()
	_lost_overlay = null


func _page_hq() -> void:
	body.add_child(_title(tr("HQ STEP")))
	var m := flow.hq_menu()
	var sel: Array = [_hq_repair, _hq_build, _hq_patch]
	body.add_child(_lab(tr("Schematics: %d. One repair, one build and a patch. Every price is in Schematics.") % int(m["schematics"]), TXT, DIM))
	# Every action the step offers: the ones the Cell cannot take now stay on the list, greyed, with the reason under them.
	for act in flow.hq_actions(sel):
		body.add_child(_hq_row(act))
	var total := flow.hq_total(sel)
	body.add_child(_lab(tr("Picked: %d of %d Schematics") % [total, int(m["schematics"])], TXT, GOLD if total > 0 else DIM))
	var legal := false
	for o in flow.hq_options():
		if o[0] == sel[0] and o[1] == sel[1] and o[2] == sel[2]:
			legal = true
	if not legal:
		body.add_child(_lab(tr("The Schematics do not cover that."), SMALL, TideGlyphs.RED))
	body.add_child(_btn(tr("DONE"), done_hq, legal))


## One action of the HQ step: a toggle button with its price, and under it the reason when it cannot be taken.
func _hq_row(act: Dictionary) -> Control:
	var box := VBoxContainer.new()
	var kind := String(act["kind"])
	box.name = "Hq_%s" % kind if StringName(act["site"]) == &"" else "Hq_%s_%s" % [kind, act["site"]]
	box.add_theme_constant_override("separation", 0)
	var label := ""
	match kind:
		"patch":
			label = tr("PATCH HOME +%d") % int(act["points"]) if int(act["points"]) > 0 else tr("PATCH HOME")
		"repair":
			label = tr("REPAIR %s") % flow.site_name(StringName(act["site"])) if StringName(act["site"]) != &"" else tr("REPAIR a district")
		"clean":
			label = tr("CLEAN an INFECTED card")
		"cool":
			label = tr("COOL: Heat -%d") % flow.cfg.heat_purchase_amount
		"install":
			label = tr("INSTALL %d cleared districts") % int(act["points"])
	var picked := bool(act["picked"])
	var b := _btn("%s%s  (%d)" % ["> " if picked else "", label, int(act["cost"])], func() -> void: _hq_pick(act), bool(act["enabled"]), GOLD if picked else EDGE)
	b.name = "Pick"
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.clip_text = true
	b.tooltip_text = label
	box.add_child(b)
	if String(act["why"]) != "":
		var why := tr(String(act["why"]))
		if (act["why_args"] as Array).size() > 0:
			why = why % act["why_args"]
		var wl := _lab(why, 11, TideGlyphs.RED.darkened(0.15), true)
		wl.name = "Why"
		box.add_child(wl)
	return box


## Toggles the pick of HQ action `act` (a patch, a repair, one build).
func _hq_pick(act: Dictionary) -> void:
	match String(act["kind"]):
		"patch":
			_hq_patch = not _hq_patch
		"repair":
			var s := StringName(act["site"])
			_hq_repair = &"" if _hq_repair == s else s
		"clean":
			_hq_build = "" if _hq_build == SolaceTideRules.BUILD_CLEAN else SolaceTideRules.BUILD_CLEAN
		"cool":
			_hq_build = "" if _hq_build == SolaceTideRules.BUILD_COOL else SolaceTideRules.BUILD_COOL
	_rebuild()


## The tier ladder, best to worst, pinned in the panel foot.
func _banner_word(b: String) -> String:
	match b:
		"CELL HOLDS":
			return tr("CELL HOLDS")
		"BREACHED":
			return tr("BREACHED")
		"CITY LOST":
			return tr("CITY LOST")
	return b


func _ladder() -> Control:
	var box := HFlowContainer.new()
	box.name = "TierLadder"
	box.add_theme_constant_override("h_separation", 8)
	for t in TideGlyphs.TIER_LADDER:
		var r := _hrow(2)
		r.add_child(TideGlyphView.tier(t, 16.0))
		r.add_child(_lab(_tierw(t), 11, TideGlyphs.tier_color(t), false))
		box.add_child(r)
	return box
