extends GutTest
## ART-12 12s-b (skin chrome sweep): view-drawn chrome outside the kit's own painters follows the
## palette skin. A static lint scans scripts/ for a direct use of the v2 chrome colours
## (Palette.TERMINAL_EDGE / TERMINAL_BG / TERMINAL_BG_HOT / NET_CYAN and HudSkin.TERMINAL_EDGE /
## TERMINAL_BG): a use must go through PaletteSkins (chrome, track_box, bind, watch) or a painter
## that does (HudSkin.draw_terminal_panel, Chrome.draw_terminal, UiTheme.terminal_box), or sit in
## ALLOWED below with its reason (SEMANTIC: cyan that means PROTECT / net / hack / Uncommon stays
## #5CE1FF on every skin, the 12s ruling). A new direct use fails here until it is routed or
## given a reason. The behaviour tests check a terminal window, a tracked box and the glass
## edge turn with the skin and that a corp accent never does.

## The v2 chrome colours as written in code.
const TOKEN := "\\b(?:Palette\\.(?:NET_CYAN|TERMINAL_EDGE|TERMINAL_BG_HOT|TERMINAL_BG)|HudSkin\\.TERMINAL_(?:EDGE|BG))\\b"
## A line that routes its token: through PaletteSkins, or into a painter that does.
const ROUTED := "PaletteSkins\\.|HudSkin\\.draw_terminal_(?:panel|edge)\\(|Chrome\\.draw_terminal\\(|UiTheme\\.terminal_box\\(|terminal_button_boxes"
## A function's default argument carries a v2 value into a painter that routes it.
const DEFAULT_ARG := "^\\s*(?:static\\s+)?func\\s.*=\\s*(?:Palette|HudSkin)\\."
## Comment start (a "#" after whitespace or at the line start).
const COMMENT := "(?:^|\\s)#"
const ANY := -1

const SEM_NET := "SEMANTIC: net / hack cyan on the City Grid, the netrun map, the jack and the 3D city (NET_CYAN means the net, #5CE1FF on every skin)"
const SEM_PROTECT := "SEMANTIC: cyan that means PROTECT (shield slices, wall, FX, the guard chip), #5CE1FF on every skin"
const SEM_BADGE := "SEMANTIC: a status / info colour passed as data (a badge, a map mark, a chip tile), not the panel's frame"
const SEM_WORLD := "SEMANTIC: diegetic city / portrait art (world neon, photo tint), not interface chrome"
const ROUTED_THEME := "CHROME, routed: every colour and box here is part of the theme, re-valued by PaletteSkins.apply / apply_box"
const ROUTED_TRACK := "CHROME, routed: the v2 values are recorded and re-valued by PaletteSkins.track_box on the next line"
const ROUTED_CARRY := "CHROME, routed: a declaration carrying the v2 value, drawn through PaletteSkins.chrome / skin_accent"

## file -> [number of direct uses, reason]. ANY = every use in the file (ui_theme only).
const ALLOWED := {
	"scripts/autoload/dialogue.gd": [1, "CHROME, routed: the speaker accent goes into crt_style > UiTheme.terminal_box, which applies the skin"],
	"scripts/autoload/fx.gd": [5, "SEMANTIC: the CONNECTING readout, its bar, the tier site and the lattice are the jack into the net (net / hack cyan)"],
	"scripts/city3d/city_network_data.gd": [3, SEM_NET],
	"scripts/ui/campaign_end/dossier_photo.gd": [1, SEM_WORLD],
	"scripts/ui/combat_scene.gd": [1, SEM_PROTECT],
	"scripts/ui/fx/heat_city.gd": [1, "SEMANTIC: the cool (negative Heat) blue of the city's Heat recolour"],
	"scripts/ui/hq_scene.gd": [8, "SEMANTIC: Heat -/ Schematics / opens-one badges, map marks and the Site accent are data colours (net meaning); line 2793 is the accent of a RaidTerminal, which routes it"],
	"scripts/ui/kit/asset_icon.gd": [1, SEM_BADGE],
	"scripts/ui/kit/badge.gd": [1, SEM_BADGE],
	"scripts/ui/kit/chrome/menu_chip.gd": [1, ROUTED_CARRY],
	"scripts/ui/kit/city_layout.gd": [3, SEM_NET],
	"scripts/ui/kit/city_map_overlay.gd": [4, SEM_NET],
	"scripts/ui/kit/city_minimap.gd": [1, SEM_NET],
	"scripts/ui/kit/combat_fx_layer.gd": [7, SEM_PROTECT],
	"scripts/ui/kit/grid_map_view.gd": [4, SEM_NET],
	"scripts/ui/kit/hud_bar.gd": [1, ROUTED_TRACK],
	"scripts/ui/kit/hud_skin.gd": [3, "CHROME, routed: TERMINAL_BG / TERMINAL_EDGE are the v2 constants HudSkin's painters re-value; PIP_ON is the RAM pip (a resource colour, kept)"],
	"scripts/ui/kit/hud_stats.gd": [1, "CHROME, routed: EDGES is passed to HudSkin.draw_terminal_panel, which applies the skin"],
	"scripts/ui/kit/inspect_popup.gd": [2, ROUTED_TRACK],
	"scripts/ui/kit/jack_sequence.gd": [2, SEM_NET],
	"scripts/ui/kit/jack_site_icon.gd": [1, SEM_NET],
	"scripts/ui/kit/materials/system_word_sticker.gd": [2, "SEMANTIC: the SYSTEM word sticker is a sticker (stickers keep v2 on every skin, the 12s ruling)"],
	"scripts/ui/kit/neon_city.gd": [4, SEM_WORLD],
	"scripts/ui/kit/netrun_map_view.gd": [4, SEM_NET],
	"scripts/ui/kit/pad_glyph.gd": [2, "SEMANTIC: the platform's face-button colours"],
	"scripts/ui/kit/portrait_art.gd": [6, SEM_WORLD],
	"scripts/ui/kit/raid_fx_layer.gd": [3, SEM_NET],
	"scripts/ui/kit/raid_skin.gd": [2, "SEMANTIC: the default hue of a corp's raid kit (replaced by the corp's own)"],
	"scripts/ui/kit/raid_speed_strip.gd": [4, ROUTED_TRACK],
	"scripts/ui/kit/raid_terminal.gd": [1, "CHROME, routed: compares the accent to pick the Cell's CRT, which follows the skin"],
	"scripts/ui/kit/ram_bar.gd": [1, "SEMANTIC: the +RAM float is the RAM resource colour"],
	"scripts/ui/kit/route_ink.gd": [1, SEM_NET],
	"scripts/ui/kit/route_overlay.gd": [1, "SEMANTIC: the route label's ring colour when a node has no state (net cyan)"],
	"scripts/ui/kit/spinner_mini.gd": [1, SEM_PROTECT],
	"scripts/ui/kit/spinner_view.gd": [1, SEM_PROTECT],
	"scripts/ui/kit/stat_icon.gd": [2, SEM_BADGE],
	"scripts/ui/kit/terminal_chip.gd": [1, "CHROME, routed: the base class's fill, never drawn: the chip paints its glass through HudSkin.draw_terminal_panel"],
	"scripts/ui/kit/terminal_note.gd": [1, "CHROME, routed: the base class's paper colour, never drawn: the note paints its glass through HudSkin.draw_terminal_panel"],
	"scripts/ui/kit/terminal_window.gd": [1, ROUTED_CARRY],
	"scripts/ui/kit/ui_theme.gd": [ANY, ROUTED_THEME],
	"scripts/ui/kit/wireframe_background.gd": [1, SEM_WORLD],
	"scripts/ui/kit/zine_card.gd": [1, "SEMANTIC: a card's default accent (S-CARDFACE: the holo hues and the PROTECT fill went with the drawn sticker)"],
	"scripts/ui/kit/zine_panel.gd": [1, "CHROME, routed: the glass's first colour; _draw_terminal re-values it through PaletteSkins.chrome"],
	"scripts/ui/netrun_scene.gd": [10, "SEMANTIC: net-map nodes and edges, the result colour and chip tiles (net cyan); five more are the accent of a CrtWindow (loot, payout, clerk, info, the event RUN terminal), which routes it through the skin (CrtWindow.skin_accent, CrtTerminalPanel.accent)"],
	"scripts/ui/kit/chrome/crt_window.gd": [1, "CHROME, routed: kind_for only compares the accent to pick the Cell's CRT kind, which follows the skin"],
	"scripts/ui/wheel_view.gd": [15, SEM_PROTECT],  # B2: + FROZEN and LOCKDOWN as standing chips (status colour as data)
}
## The kit's own definitions (not uses).
const DEFINITIONS: Array[String] = ["scripts/ui/kit/palette.gd", "scripts/ui/kit/palette_skins.gd"]

var _saved: Dictionary = {}


func before_each() -> void:
	_saved = Settings.snapshot()


func after_each() -> void:
	Settings.restore(_saved)


func _re(pattern: String) -> RegEx:
	var re := RegEx.new()
	assert_eq(re.compile(pattern), OK, "pattern compiles: %s" % pattern)
	return re


func _gd_files(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_gd_files(dir.path_join(d), out)


## Whether `line` is a direct, unrouted use of a v2 chrome colour.
func _is_direct_use(line: String, token: RegEx, routed: RegEx, default_arg: RegEx, comment: RegEx) -> bool:
	var code := line
	var c := comment.search(line)
	if c != null:
		code = line.substr(0, c.get_start())
	if token.search(code) == null:
		return false
	return routed.search(code) == null and default_arg.search(code) == null


## Direct uses per file: {path: count}.
func _scan() -> Dictionary:
	var files: Array[String] = []
	_gd_files("res://scripts", files)
	files.sort()
	var token := _re(TOKEN)
	var routed := _re(ROUTED)
	var default_arg := _re(DEFAULT_ARG)
	var comment := _re(COMMENT)
	var out := {}
	for path in files:
		var rel := path.trim_prefix("res://")
		if DEFINITIONS.has(rel):
			continue
		var n := 0
		for line in FileAccess.get_file_as_string(path).split("\n"):
			if _is_direct_use(line, token, routed, default_arg, comment):
				n += 1
		if n > 0:
			out[rel] = n
	return out


func test_the_lint_reads_a_use_a_route_a_default_and_a_comment() -> void:
	var token := _re(TOKEN)
	var routed := _re(ROUTED)
	var default_arg := _re(DEFAULT_ARG)
	var comment := _re(COMMENT)
	var cases := {
		"\tdraw_rect(r, Palette.NET_CYAN)": true,
		"\tdraw_rect(r, Color(HudSkin.TERMINAL_EDGE, 0.4))": true,
		"\tdraw_rect(r, Palette.TERMINAL_BG_HOT)": true,
		"\tdraw_rect(r, PaletteSkins.chrome(Palette.NET_CYAN))": false,
		"\tHudSkin.draw_terminal_panel(self, r, HudSkin.TERMINAL_EDGE)": false,
		"static func edge(e: Color = Palette.TERMINAL_EDGE) -> Color:": false,
		"\t# Palette.NET_CYAN in a comment": false,
		"\tdraw_rect(r, Palette.PROTECT)": false,
		"\tvar c := Palette.TERMINAL_BGX": false,
		"\tdraw_rect(r, Palette.CELL_ACID)  # not Palette.NET_CYAN": false,
	}
	for line in cases:
		assert_eq(_is_direct_use(line, token, routed, default_arg, comment), cases[line], line)


func test_no_new_direct_use_of_a_v2_chrome_colour_outside_the_kits_painters() -> void:
	var found := _scan()
	for rel in found:
		if not ALLOWED.has(rel):
			fail_test("%s has %d direct use(s) of Palette.NET_CYAN / TERMINAL_EDGE / TERMINAL_BG: route chrome through PaletteSkins.chrome (see PaletteSkins), or add the file to ALLOWED with the reason it is semantic" % [rel, found[rel]])
			continue
		var want: int = (ALLOWED[rel] as Array)[0]
		if want != ANY:
			assert_eq(int(found[rel]), want, "%s: direct uses (a new one must be routed or justified; a removed one must lower ALLOWED)" % rel)
	for rel in ALLOWED:
		assert_true(FileAccess.file_exists("res://" + rel), "%s exists" % rel)
		assert_ne(String((ALLOWED[rel] as Array)[1]), "", "%s has a reason" % rel)
		if int((ALLOWED[rel] as Array)[0]) != ANY:
			assert_true(found.has(rel), "%s no longer has a direct use: drop it from ALLOWED" % rel)


func test_every_allowed_use_is_either_semantic_or_a_routed_carrier() -> void:
	for rel in ALLOWED:
		var reason := String((ALLOWED[rel] as Array)[1])
		assert_true(reason.begins_with("SEMANTIC") or reason.begins_with("CHROME, routed"), "%s: the reason says which it is" % rel)


func _glass_of(w: CrtWindow) -> Color:
	return w.skin_accent()


func test_a_cell_terminal_window_turns_with_the_skin_and_a_corp_one_does_not() -> void:
	var cell: CrtWindow = add_child_autofree(CrtWindow.new("CYBERDECK"))
	var corp: CrtWindow = add_child_autofree(CrtWindow.new("OFFER", Palette.CORP_SOLACE))
	for skin in [&"cobalt", &"graphite", &"v2"]:
		Settings.set_palette_skin(skin)
		var want := Color(PaletteSkins.chrome(Palette.NET_CYAN, skin), 1.0)
		var head := cell.find_child("TerminalTitle", true, false) as Label
		assert_eq(Color(head.get_theme_color(&"font_color"), 1.0), want, "%s: the CYBERDECK heading" % skin)
		assert_eq(Color(cell._square.color, 1.0), want, "%s: the header square" % skin)
		assert_eq(Color(_glass_of(cell), 1.0), want, "%s: the frame accent" % skin)
		assert_eq(Color(cell.glass.accent(), 1.0), want, "%s: the glass edge" % skin)
		assert_eq(Color(_glass_of(corp), 1.0), Color(Palette.CORP_SOLACE, 1.0), "%s: a corp accent is never re-valued" % skin)
	assert_ne(PaletteSkins.chrome(Palette.NET_CYAN, &"cobalt"), Palette.NET_CYAN, "cobalt moves the Cell's cyan")


func test_a_tracked_box_follows_the_skin_live_and_stops_when_freed() -> void:
	var sb := PaletteSkins.track_box(UiTheme.box(Palette.TERMINAL_BG, Palette.NET_CYAN, 1, 4, 4))
	for skin in [&"cobalt", &"graphite", &"v2"]:
		Settings.set_palette_skin(skin)
		assert_eq(Color(sb.border_color, 1.0), Color(PaletteSkins.chrome(Palette.NET_CYAN, skin), 1.0), "%s: the edge" % skin)
		assert_eq(Color(sb.bg_color, 1.0), Color(PaletteSkins.chrome(Palette.TERMINAL_BG, skin), 1.0), "%s: the glass" % skin)
	assert_almost_eq(sb.bg_color.a, Palette.TERMINAL_BG.a, 0.001, "alpha is kept")
	sb = null
	Settings.set_palette_skin(&"cobalt")
	assert_true(true, "a freed tracked box is skipped without an error")


func test_the_kit_state_edge_and_the_hud_painters_follow_the_skin() -> void:
	Settings.set_palette_skin(&"cobalt")
	assert_eq(Color(KitState.edge_color(KitState.IDLE), 1.0), Color(PaletteSkins.chrome(Palette.TERMINAL_EDGE, &"cobalt"), 1.0), "a glass component's rest edge")
	assert_eq(KitState.edge_color(KitState.REFUSED), Palette.HARM, "a refusal stays HARM")
	assert_eq(KitState.edge_color(KitState.DISABLED), Palette.DISABLED, "disabled stays grey")
	Settings.set_palette_skin(&"v2")
	assert_eq(KitState.edge_color(KitState.IDLE), Palette.TERMINAL_EDGE, "v2 is the identity")


func test_toast_and_inspect_popup_glass_follow_the_skin() -> void:
	var toast: Toast = add_child_autofree(Toast.new())
	Settings.set_palette_skin(&"cobalt")
	toast.show_note("note", Vector2(100, 100))
	var panel := toast.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_eq(Color(panel.bg_color, 1.0), Color(PaletteSkins.chrome(Palette.TERMINAL_BG, &"cobalt"), 1.0), "the toast's glass")
	assert_eq(Color(panel.border_color, 1.0), Color(PaletteSkins.chrome(Palette.TERMINAL_EDGE, &"cobalt"), 1.0), "the toast's edge")
	var tip: InspectPopup = add_child_autofree(InspectPopup.new())
	var box := tip.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_eq(Color(box.border_color, 1.0), Color(PaletteSkins.chrome(Palette.TERMINAL_EDGE, &"cobalt"), 1.0), "the inspect popup's edge")
	Settings.set_palette_skin(&"graphite")
	assert_eq(Color(box.border_color, 1.0), Color(PaletteSkins.chrome(Palette.TERMINAL_EDGE, &"graphite"), 1.0), "the popup turns live")
