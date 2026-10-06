extends Control
## Design lab (not part of the game; ART-1 1A): the "type & chrome" sheet, palette v2 and the
## v2 theme laid out like `docs/art_reference/menus/round33_ui_chrome/typography.jpg` and
## `ui_kit.jpg`: one face per medium, the terminal chip and sticker verb in every state, tabs,
## toggles, a slider, the four panel media, a focused menu, live numbers and the token swatches.
## Everything comes from Palette and UiTheme (what the screens get).
##   python tools/run_windowed.py --log <log> -- res://tools/design_lab/type_chrome_sheet.tscn
##       --write-movie <dir>/f.png --fixed-fps 10 --quit-after 6 [-- --scale=2.0]

const STATES := ["normal", "hover", "pressed", "disabled", "focus"]
const STATE_WORDS := ["IDLE", "HOVER", "PRESSED", "DISABLED", "FOCUS"]
const STATE_FONT := {"normal": "font_color", "hover": "font_hover_color", "pressed": "font_pressed_color",
	"disabled": "font_disabled_color", "focus": "font_focus_color"}

var _theme: Theme


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--scale="):
			Settings.text_scale = float(a.trim_prefix("--scale="))
	UiTheme.apply(self)
	_theme = theme
	var bg := CyberdeckBackground.new()
	add_child(bg)
	bg.set_district(&"halcyon")
	var scrim := ColorRect.new()
	scrim.color = Palette.SCRIM
	scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scrim)
	var root := HBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.offset_left = UiTheme.SP_M
	root.offset_top = UiTheme.SP_S
	root.offset_right = -UiTheme.SP_M
	root.add_theme_constant_override("separation", UiTheme.GUTTER)
	add_child(root)
	root.add_child(_type_column())
	root.add_child(_kit_column())


func _caption(text: String, color: Color = Palette.NET_CYAN) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", color)
	l.add_theme_font_override("font", UiTheme.tracked(Palette.mono(), UiTheme.TRACK_MONO_CAPS, UiTheme.CAPTION))
	l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	return l


func _text(text: String, f: Font, step: int, color: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", f)
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	l.add_theme_color_override("font_color", color)
	return l


func _row(sep: int = UiTheme.SP_S) -> HBoxContainer:
	var r := HBoxContainer.new()
	r.add_theme_constant_override("separation", sep)
	return r


func _col(sep: int = UiTheme.SP_XS) -> VBoxContainer:
	var c := VBoxContainer.new()
	c.add_theme_constant_override("separation", sep)
	return c


func _type_column() -> Control:
	var col := _col(UiTheme.SP_S)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_child(_text("TYPE SYSTEM - one face per medium", UiTheme.tracked(Palette.display(), UiTheme.TRACK_DISPLAY, UiTheme.HEADING), UiTheme.HEADING, Palette.TEXT_HI))
	# 01 Anton: the sticker verb and a bare live number.
	col.add_child(_caption("01  STICKER / DISPLAY - ANTON", Palette.CELL_PINK))
	var a := _row(UiTheme.SP_M)
	var verb := Button.new()
	verb.text = "JACK IN"
	verb.theme_type_variation = &"HotButton"
	a.add_child(verb)
	var title := Button.new()
	title.text = "RAID SETUP"
	title.theme_type_variation = &"HotButton"
	title.add_theme_stylebox_override("normal", UiTheme.sticker_box(Palette.STICKER_SAFE))
	a.add_child(title)
	var hp := Label.new()
	hp.text = "41/60"
	hp.label_settings = UiTheme.live_number(UiTheme.DISPLAY, Palette.GAIN)
	a.add_child(hp)
	var heat := Label.new()
	heat.text = "75"
	heat.label_settings = UiTheme.live_number(UiTheme.DISPLAY, Palette.HEAT_HUNTED)
	a.add_child(heat)
	col.add_child(a)
	# 02 Share Tech Mono: a terminal panel.
	col.add_child(_caption("02  TERMINAL / SCREENS & DATA - SHARE TECH MONO"))
	var term := PanelContainer.new()
	term.theme_type_variation = UiTheme.CRT_GLASS_PANEL
	CrtTerminalPanel.behind(term)  # B5: the kit glass (no shared crt_panel material)
	var tl := _col()
	tl.add_child(_text("> YOUR NETWORK", UiTheme.tracked(Palette.mono(), UiTheme.TRACK_MONO_CAPS, UiTheme.LABEL), UiTheme.LABEL, Palette.NET_CYAN))
	var line1 := _row(UiTheme.SP_L)
	line1.add_child(_text("FIREWALL RELAY   INT 30/30", Palette.mono(), UiTheme.BODY, Palette.TERMINAL_TEXT))
	line1.add_child(_text("HOLDS", Palette.mono(), UiTheme.BODY, Palette.GAIN))
	tl.add_child(line1)
	var line2 := _row(UiTheme.SP_L)
	line2.add_child(_text("VAULT TERMINAL   INT 06/20", Palette.mono(), UiTheme.BODY, Palette.TERMINAL_TEXT))
	line2.add_child(_text("DOWN", Palette.mono(), UiTheme.BODY, Palette.WARN))
	tl.add_child(line2)
	tl.add_child(_text("turret 3 dmg  //  ice lock  //  station: GHOST R2", Palette.mono(), UiTheme.BODY, Palette.TEXT_MID))
	term.add_child(tl)
	col.add_child(term)
	# 03 Courier Prime: corp paper.
	col.add_child(_caption("03  PAPER / CORP DOCUMENTS - COURIER PRIME + PLEX MEDIUM", Palette.NEON_VIOLET))
	var paper := PanelContainer.new()
	paper.theme_type_variation = UiTheme.PAPER_PANEL
	var pc := _col()
	pc.add_child(_text("HALCYON CIVIC", Palette.body_medium(), UiTheme.TITLE, Palette.CORP_HALCYON.darkened(0.35)))
	pc.add_child(_text("AFTER-ACTION REPORT", Palette.paper_bold(), UiTheme.TITLE, Palette.INK))
	pc.add_child(_text("SUBJECT ...... REBEL_CELL (cell 03)", Palette.paper(), UiTheme.BODY, Palette.INK))
	pc.add_child(_text("OUTCOME ...... FAILED", Palette.paper(), UiTheme.BODY, Palette.HARM_INK))
	paper.add_child(pc)
	col.add_child(paper)
	# 04 Permanent Marker: grease pencil (plans), wax with a dark under-shadow.
	col.add_child(_caption("04  GREASE PENCIL / PLANS & THREATS - PERMANENT MARKER", Palette.PENCIL_PLAN))
	var pen := _row(UiTheme.SP_L)
	for pair in [["1. BREACH  2. DISABLE", Palette.PENCIL_PLAN], ["RIP", Palette.PENCIL_THREAT]]:
		var p := _text(pair[0], Palette.pencil(), UiTheme.TITLE, pair[1])
		p.add_theme_color_override("font_shadow_color", Palette.PENCIL_SHADOW)
		p.add_theme_constant_override("shadow_offset_x", 2)
		p.add_theme_constant_override("shadow_offset_y", 3)
		pen.add_child(p)
	col.add_child(pen)
	# 05 Plex: body / tooltip prose inside a terminal.
	col.add_child(_caption("05  BODY / TOOLTIP - IBM PLEX SANS CONDENSED", Palette.TEXT_HI))
	var tip := PanelContainer.new()
	tip.theme_type_variation = &"TerminalPanel"
	var body := RichTextLabel.new()
	body.theme_type_variation = UiTheme.BODY_TEXT
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size.x = 420
	body.text = "Hits for 12. On a [b]PERFECT[/b] aim the ring doubles it.\nBreaker core: the slice resolves twice."
	tip.add_child(body)
	col.add_child(tip)
	return col


func _state_button(variation: StringName, text: String, state: String) -> Control:
	var b := Button.new()
	b.text = text
	b.theme_type_variation = variation
	b.focus_mode = Control.FOCUS_NONE
	var box_name := "normal" if state == "focus" else state
	b.add_theme_stylebox_override("normal", _theme.get_stylebox(box_name, variation))
	b.add_theme_color_override("font_color", _theme.get_color(STATE_FONT[state], variation))
	if state == "focus":
		# The focus box draws over the idle box (as the engine does for a focused control).
		var over := Panel.new()
		over.add_theme_stylebox_override("panel", _theme.get_stylebox("focus", variation))
		over.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		over.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(over)
	var c := _col()
	c.add_child(b)
	c.add_child(_caption(STATE_WORDS[STATES.find(state)], Palette.TEXT_MID))
	return c


func _kit_column() -> Control:
	var col := _col(UiTheme.SP_S)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_child(_text("UI KIT - chrome by medium", UiTheme.tracked(Palette.display(), UiTheme.TRACK_DISPLAY, UiTheme.HEADING), UiTheme.HEADING, Palette.TEXT_HI))
	col.add_child(_caption("BUTTONS - primary = sticker verb, secondary = terminal chip", Palette.CELL_PINK))
	var stickers := _row(UiTheme.SP_L)
	var chips := _row(UiTheme.SP_L)
	for s in STATES:
		stickers.add_child(_state_button(&"HotButton", "JACK IN", s))
		chips.add_child(_state_button(UiTheme.TERMINAL_BUTTON, "RESPIN 4 RAM", s))
	col.add_child(stickers)
	col.add_child(chips)
	col.add_child(_caption("TOGGLES / SLIDERS / TABS"))
	var ctl := _row(UiTheme.SP_L)
	var on := CheckButton.new()
	on.text = "ON"
	on.button_pressed = true
	ctl.add_child(on)
	var off := CheckButton.new()
	off.text = "OFF"
	ctl.add_child(off)
	var slider := HSlider.new()
	slider.custom_minimum_size.x = 160
	slider.value = 60
	ctl.add_child(slider)
	var tabs := TabBar.new()
	tabs.clip_tabs = false
	for w in ["MAP", "CREW", "???"]:
		tabs.add_tab(w)
	tabs.set_tab_disabled(2, true)
	ctl.add_child(tabs)
	col.add_child(ctl)
	col.add_child(_caption("PANELS - one container per medium"))
	var panels := _row(UiTheme.SP_M)
	var crew := PanelContainer.new()
	crew.theme_type_variation = &"TerminalPanel"
	var cc := _col()
	cc.add_child(_text("> CREW  3/4", Palette.mono(), UiTheme.BODY, Palette.NET_CYAN))
	cc.add_child(_text("CELL-9   READY", Palette.mono(), UiTheme.BODY, Palette.TERMINAL_TEXT))
	cc.add_child(_text("GHOST    STATION", Palette.mono(), UiTheme.BODY, Palette.TERMINAL_TEXT))
	crew.add_child(cc)
	panels.add_child(crew)
	var holo := PanelContainer.new()
	holo.theme_type_variation = UiTheme.HOLO_PANEL
	holo.add_theme_stylebox_override("panel", UiTheme.holo_box(Palette.CORP_HALCYON))
	var hc := _col()
	hc.add_child(_text("THREAT INTEL", UiTheme.tracked(Palette.mono(), UiTheme.TRACK_MONO_CAPS, UiTheme.LABEL), UiTheme.LABEL, Palette.TEXT_HI))
	hc.add_child(_text("BAILIFF + COURIER", Palette.mono(), UiTheme.BODY, Palette.TEXT_HI))
	hc.add_child(_text("DECRYPTED 7F-A2", Palette.mono(), UiTheme.BODY, Palette.GAIN))
	holo.add_child(hc)
	panels.add_child(holo)
	var order := PanelContainer.new()
	order.theme_type_variation = UiTheme.PAPER_PANEL
	var oc := _col()
	oc.add_child(_text("MERIDIAN", Palette.body_medium(), UiTheme.LABEL, Palette.CORP_MERIDIAN.darkened(0.3)))
	oc.add_child(_text("WORK ORDER", Palette.paper_bold(), UiTheme.LABEL, Palette.INK))
	oc.add_child(_text("TARGET   SITE 07", Palette.paper(), UiTheme.BODY, Palette.INK))
	order.add_child(oc)
	panels.add_child(order)
	var menu := PanelContainer.new()
	menu.theme_type_variation = &"TerminalPanel"
	var mc := _col(0)
	mc.add_child(_text("> MENU", Palette.mono(), UiTheme.BODY, Palette.NET_CYAN))
	for i in 3:
		var item := Button.new()
		item.text = ["CONTINUE", "CAMPAIGNS", "OPTIONS"][i]
		item.theme_type_variation = &"MenuItem"
		mc.add_child(item)
		if i == 1:
			item.ready.connect(item.grab_focus)
	menu.add_child(mc)
	panels.add_child(menu)
	col.add_child(panels)
	col.add_child(_caption("TOKENS - corp kits, class accents, Heat bands, Daemon families, rarity"))
	col.add_child(_swatches([Palette.CORP_MERIDIAN, Palette.CORP_SOLACE, Palette.CORP_HALCYON, Palette.CORP_ORBITAL, Palette.CORP_REBEL_CELL,
		Palette.CORP_MERIDIAN_2, Palette.CORP_SOLACE_2, Palette.CORP_HALCYON_2, Palette.CORP_ORBITAL_2, Palette.CORP_REBEL_CELL_2]))
	col.add_child(_swatches(Palette.CLASS_ACCENTS.values()))
	var heat_words := ["COOL", "NOTICED", "FLAGGED", "HUNTED", "PURGE"]
	var hr := _row(UiTheme.SP_S)
	for i in Palette.HEAT_BAND_COLORS.size():
		hr.add_child(_text(heat_words[i], Palette.mono(), UiTheme.LABEL, Palette.HEAT_BAND_COLORS[i]))
	col.add_child(hr)
	col.add_child(_swatches(Palette.DAEMON_FAMILY_COLORS.values() + Palette.RARITY_COLORS + [Palette.PENCIL_PLAN, Palette.PENCIL_THREAT, Palette.HEAT_B, Palette.RING_AVAILABLE]))
	return col


func _swatches(colors: Array) -> Control:
	var r := _row(UiTheme.SP_XS)
	for c: Color in colors:
		var s := ColorRect.new()
		s.color = c
		s.custom_minimum_size = Vector2(UiTheme.SP_XL, UiTheme.SP_M)
		r.add_child(s)
	return r
