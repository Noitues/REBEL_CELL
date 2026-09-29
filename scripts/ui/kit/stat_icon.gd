class_name StatIcon
extends RefCounted
## Vector icons for the game's numbers and menus (H21 #10, #13; STYLE_GUIDE 4.1): one
## drawing per resource, the same wherever it appears (top-bar tags, CELL STATUS badges,
## Modem prices and wallet, event choice outcomes, run and profile tags), plus small icons
## for menu items and route node types. Drawn with CanvasItem line and polygon calls only
## (no font glyphs, no textures), so an icon reads the same in every language and at any
## text size. `draw(ci, centre, radius, kind, colour)` from any CanvasItem's draw pass
## (the combat scene can call it too). Draw-only; no game state.

# Resources (the numbers on the tags).
const HEAT := &"heat"
const SCHEMATICS := &"schematics"
const HOME := &"home"
const EXPLOITS := &"exploits"
const RAIDS := &"raids"
const ICE := &"ice"
const CREW := &"crew"
const HP := &"hp"
const CYCLES := &"cycles"
const CARDS := &"cards"
const RANK := &"rank"
const BANKED := &"banked"
const ARMORY := &"armory"
const COMBATS := &"combats"
const ELITES := &"elites"
const CAMPAIGNS := &"campaigns"
const WON := &"won"
const RUNS := &"runs"
const BADGES := &"badges"
const FIRMWARE := &"firmware"
const DAEMON := &"daemon"
const OPERATIVE := &"operative"
# Menus and actions.
const PLAY := &"play"
const CONTINUE := &"continue"
const MAP := &"map"
const CODEX := &"codex"
const SETTINGS := &"settings"
const SAVE := &"save"
const EXIT := &"exit"
const BACK := &"back"
const NEXT := &"next"
const SKIP := &"skip"
const SLOTS := &"slots"
const STATS := &"stats"
const TUTORIAL := &"tutorial"
const QUIT := &"quit"
const JACK_IN := &"jack_in"
const MORE := &"more"
# Route node types.
const FIGHT := &"fight"
const ELITE := &"elite"
const SHOP := &"shop"
const TERMINAL := &"terminal"
const RACK := &"rack"
# H24 K5: map concepts with a glyph of their own (a Heat reduction Site is not ICE's
# snowflake; the Modem shop is not an Exploit's diamond), and a Site run's outcomes.
const COOLING := &"cooling"
const CLAIM := &"claim"
const LINKS := &"links"
# ANIM-R6 B10 / B11 (the naive player's pass): RAM on a card's pictograms (a memory chip, as
# the RAM bar's chips), and the Modem's two verbs on its sign (a cart for BUY, a shredder for
# SHRED), readable whatever the language.
const RAM := &"ram"
const CART := &"cart"
const SHRED := &"shred"

## Every icon kind (tests draw each one).
const ALL: Array[StringName] = [HEAT, SCHEMATICS, HOME, EXPLOITS, RAIDS, ICE, CREW, HP, CYCLES, CARDS, RANK, BANKED,
	ARMORY, COMBATS, ELITES, CAMPAIGNS, WON, RUNS, BADGES, FIRMWARE, DAEMON, OPERATIVE, PLAY, CONTINUE, MAP, CODEX,
	SETTINGS, SAVE, EXIT, BACK, NEXT, SKIP, SLOTS, STATS, TUTORIAL, QUIT, JACK_IN, MORE, FIGHT, ELITE, SHOP, TERMINAL, RACK,
	COOLING, CLAIM, LINKS, RAM, CART, SHRED]

## Tag names (as the tags spell them) -> icon.
const TAG_KINDS := {"HEAT": HEAT, "SCHEMATICS": SCHEMATICS, "HOME": HOME, "EXPLOITS": EXPLOITS, "RAIDS": RAIDS,
	"ICE": ICE, "BEST ICE": ICE, "CREW": CREW, "HP": HP, "CYCLES": CYCLES, "CARDS": CARDS, "RANK": RANK,
	"BANKED": BANKED, "ARMORY": ARMORY, "COMBATS": COMBATS, "ELITES": ELITES, "CAMPAIGNS": CAMPAIGNS, "WON": WON,
	"RUNS": RUNS, "BADGES": BADGES}

## What each resource icon stands for (captions and tooltip titles).
const NAMES := {HEAT: "Heat", SCHEMATICS: "Schematics", HOME: "Home server", EXPLOITS: "Exploits", RAIDS: "Raids",
	ICE: "ICE", CREW: "Crew", HP: "HP", CYCLES: "Cycles", CARDS: "Cards", RANK: "Rank", BANKED: "Banked",
	ARMORY: "Armory", COMBATS: "Fights won", ELITES: "Elites", CAMPAIGNS: "Campaigns", WON: "Won", RUNS: "Runs",
	BADGES: "Badges", FIRMWARE: "Firmware", DAEMON: "Daemon", OPERATIVE: "Operative", COOLING: "Heat reduction",
	CLAIM: "Claim", LINKS: "Opens Sites", SHOP: "Shop"}


## The icon for a tag name ("HEAT" -> HEAT), or &"" when there is none.
static func kind_for(tag_name: String) -> StringName:
	return StringName(TAG_KINDS.get(tag_name.to_upper(), &""))


## The icon's own colour on the dark screens (paper tags draw it in ink instead).
static func color_of(kind: StringName) -> Color:
	match String(kind):
		"heat":
			return Color("#FF7A2F")
		"schematics", "banked", "firmware", "cooling", "links":
			return Palette.NET_CYAN
		"home", "exploits", "cycles", "won":
			return Palette.CELL_ACID
		"raids", "hp", "armory", "elites", "elite", "fight", "rack", "claim":
			return Palette.CELL_PINK
		"ice":
			return Color("#8FE8FF")
		"rank", "badges":
			return Palette.RESIST_GOLD
		"daemon":
			return Palette.NEON_VIOLET
		"shop":
			return Palette.CELL_ACID
		"ram":
			return Palette.NET_CYAN
		"terminal":
			return Palette.CRT_AMBER
	return Palette.TERMINAL_TEXT


## Draws icon `kind` centred on `c` within radius `r` in `col` on `ci` (call it from a draw
## pass). Unknown kinds draw a small ring.
static func draw(ci: CanvasItem, c: Vector2, r: float, kind: StringName, col: Color) -> void:
	var w := maxf(1.2, r * 0.17)
	match String(kind):
		"heat":
			_line(ci, c, r, [[0, -1.0], [0.38, -0.45], [0.62, 0.05], [0.58, 0.5], [0.3, 0.85], [0, 0.95], [-0.3, 0.85], [-0.58, 0.5], [-0.55, 0.0], [-0.3, -0.32], [-0.12, 0.02], [0, -1.0]], col, w)
			_line(ci, c, r, [[0.02, 0.05], [0.25, 0.45], [0.18, 0.72], [0, 0.8], [-0.18, 0.72], [-0.22, 0.45], [0.02, 0.05]], col, w * 0.8)
		"schematics":
			ci.draw_rect(Rect2(c + Vector2(-0.8, -0.65) * r, Vector2(1.6, 1.3) * r), col, false, w)
			ci.draw_line(c + Vector2(-0.8, 0.05) * r, c + Vector2(0.1, 0.05) * r, col, w * 0.8)
			ci.draw_line(c + Vector2(0.1, -0.65) * r, c + Vector2(0.1, 0.65) * r, col, w * 0.8)
			ci.draw_line(c + Vector2(-0.35, 0.05) * r, c + Vector2(-0.35, 0.65) * r, col, w * 0.6)
			ci.draw_arc(c + Vector2(0.45, -0.28) * r, 0.18 * r, 0, TAU, 12, col, w * 0.8)
		"home":
			_line(ci, c, r, [[-0.85, -0.02], [0, -0.85], [0.85, -0.02]], col, w)
			_line(ci, c, r, [[-0.6, -0.2], [-0.6, 0.8], [0.6, 0.8], [0.6, -0.2]], col, w)
			ci.draw_rect(Rect2(c + Vector2(-0.16, 0.3) * r, Vector2(0.32, 0.5) * r), col)
		"exploits":
			_line(ci, c, r, [[0, -0.92], [0.72, 0], [0, 0.92], [-0.72, 0], [0, -0.92]], col, w)
			_fill(ci, c, r, [[0, -0.38], [0.3, 0], [0, 0.38], [-0.3, 0]], col)
		"raids":
			_line(ci, c, r, [[0, -0.92], [0.76, -0.6], [0.7, 0.15], [0, 0.92], [-0.7, 0.15], [-0.76, -0.6], [0, -0.92]], col, w)
			ci.draw_line(c + Vector2(0, -0.48) * r, c + Vector2(0, 0.18) * r, col, w * 1.2)
			ci.draw_circle(c + Vector2(0, 0.45) * r, w * 0.75, col)
		"ice":
			for k in 3:
				var a := PI * 0.5 + k * PI / 3.0
				var d := Vector2(cos(a), sin(a))
				ci.draw_line(c - d * r * 0.92, c + d * r * 0.92, col, w)
				for side: float in [-1.0, 1.0]:
					var tip: Vector2 = c + d * r * 0.55 * side
					ci.draw_line(tip, tip + (d * side).rotated(0.7) * r * 0.32, col, w * 0.8)
					ci.draw_line(tip, tip + (d * side).rotated(-0.7) * r * 0.32, col, w * 0.8)
		"crew":
			_person(ci, c + Vector2(0.3, -0.08) * r, r * 0.78, col, w)
			_person(ci, c + Vector2(-0.22, 0.1) * r, r * 0.9, col, w)
		"operative":
			_person(ci, c + Vector2(0, 0.05) * r, r, col, w)
		"hp":
			ci.draw_circle(c + Vector2(-0.36, -0.26) * r, 0.38 * r, col)
			ci.draw_circle(c + Vector2(0.36, -0.26) * r, 0.38 * r, col)
			_fill(ci, c, r, [[-0.72, -0.14], [0.72, -0.14], [0, 0.86]], col)
		"cycles":
			ci.draw_arc(c, r * 0.85, 0, TAU, 24, col, w)
			ci.draw_arc(c, r * 0.5, 0, TAU, 18, col, w * 0.7)
			ci.draw_circle(c, r * 0.2, col)
		"cards":
			_box(ci, c, r, Vector2(-0.35, -0.9), Vector2(1.05, 1.4), col, w * 0.8, false)
			_box(ci, c, r, Vector2(-0.75, -0.55), Vector2(1.05, 1.45), col, w, true)
		"rank":
			_line(ci, c, r, [[-0.75, -0.05], [0, -0.7], [0.75, -0.05]], col, w * 1.2)
			_line(ci, c, r, [[-0.75, 0.55], [0, -0.1], [0.75, 0.55]], col, w * 1.2)
		"banked":
			ci.draw_rect(Rect2(c + Vector2(-0.82, -0.78) * r, Vector2(1.64, 1.56) * r), col, false, w)
			ci.draw_arc(c + Vector2(0.08, 0) * r, 0.4 * r, 0, TAU, 18, col, w)
			for k in 3:
				var a := -PI * 0.5 + k * TAU / 3.0
				ci.draw_line(c + Vector2(0.08, 0) * r, c + Vector2(0.08, 0) * r + Vector2(cos(a), sin(a)) * 0.4 * r, col, w * 0.7)
			ci.draw_line(c + Vector2(-0.7, -0.45) * r, c + Vector2(-0.7, -0.15) * r, col, w)
			ci.draw_line(c + Vector2(-0.7, 0.15) * r, c + Vector2(-0.7, 0.45) * r, col, w)
		"armory":
			ci.draw_rect(Rect2(c + Vector2(-0.8, -0.7) * r, Vector2(1.6, 1.4) * r), col, false, w)
			ci.draw_line(c + Vector2(-0.8, -0.3) * r, c + Vector2(0.8, -0.3) * r, col, w * 0.8)
			ci.draw_line(c + Vector2(-0.8, -0.3) * r, c + Vector2(0.8, 0.7) * r, col, w * 0.8)
			ci.draw_line(c + Vector2(0.8, -0.3) * r, c + Vector2(-0.8, 0.7) * r, col, w * 0.8)
		"combats", "fight_swords":
			for side: float in [-1.0, 1.0]:
				var a := c + Vector2(-0.78 * side, 0.78) * r
				var b := c + Vector2(0.7 * side, -0.7) * r
				ci.draw_line(a, b, col, w)
				var g := c + Vector2(-0.45 * side, 0.45) * r
				ci.draw_line(g + Vector2(-0.22, -0.22 * side) * r, g + Vector2(0.22, 0.22 * side) * r, col, w)
		"elites", "elite":
			_line(ci, c, r, [[-0.82, 0.6], [-0.82, -0.4], [-0.4, 0.08], [0, -0.66], [0.4, 0.08], [0.82, -0.4], [0.82, 0.6], [-0.82, 0.6]], col, w)
			ci.draw_line(c + Vector2(-0.82, 0.3) * r, c + Vector2(0.82, 0.3) * r, col, w * 0.7)
		"campaigns":
			ci.draw_line(c + Vector2(-0.6, -0.92) * r, c + Vector2(-0.6, 0.92) * r, col, w)
			_fill(ci, c, r, [[-0.6, -0.88], [0.78, -0.5], [-0.6, -0.08]], col)
		"won":
			var pts := PackedVector2Array()
			for k in 11:
				var a := -PI * 0.5 + k * PI / 5.0
				var rr := r * (0.92 if k % 2 == 0 else 0.4)
				pts.append(c + Vector2(cos(a), sin(a)) * rr)
			ci.draw_polyline(pts, col, w)
		"runs":
			_line(ci, c, r, [[-0.85, 0.6], [-0.2, 0.6], [-0.2, -0.25], [0.45, -0.25]], col, w)
			ci.draw_circle(c + Vector2(-0.85, 0.6) * r, w * 1.1, col)
			_fill(ci, c, r, [[0.4, -0.55], [0.9, -0.25], [0.4, 0.05]], col)
		"badges":
			ci.draw_line(c + Vector2(-0.4, -0.92) * r, c + Vector2(-0.05, -0.2) * r, col, w)
			ci.draw_line(c + Vector2(0.4, -0.92) * r, c + Vector2(0.05, -0.2) * r, col, w)
			ci.draw_arc(c + Vector2(0, 0.35) * r, 0.5 * r, 0, TAU, 20, col, w)
			ci.draw_circle(c + Vector2(0, 0.35) * r, 0.18 * r, col)
		"firmware":
			ci.draw_rect(Rect2(c - Vector2(0.52, 0.52) * r, Vector2(1.04, 1.04) * r), col, false, w)
			ci.draw_rect(Rect2(c - Vector2(0.2, 0.2) * r, Vector2(0.4, 0.4) * r), col)
			for k in 3:
				var o := (-0.3 + k * 0.3) * r
				ci.draw_line(c + Vector2(o, -0.52 * r), c + Vector2(o, -0.88 * r), col, w * 0.7)
				ci.draw_line(c + Vector2(o, 0.52 * r), c + Vector2(o, 0.88 * r), col, w * 0.7)
				ci.draw_line(c + Vector2(-0.52 * r, o), c + Vector2(-0.88 * r, o), col, w * 0.7)
				ci.draw_line(c + Vector2(0.52 * r, o), c + Vector2(0.88 * r, o), col, w * 0.7)
		"daemon":
			ci.draw_arc(c + Vector2(0, -0.2) * r, 0.62 * r, PI, TAU, 14, col, w)
			_line(ci, c, r, [[-0.62, -0.2], [-0.62, 0.8], [-0.31, 0.55], [0, 0.8], [0.31, 0.55], [0.62, 0.8], [0.62, -0.2]], col, w)
			ci.draw_circle(c + Vector2(-0.24, -0.18) * r, 0.11 * r + w * 0.3, col)
			ci.draw_circle(c + Vector2(0.24, -0.18) * r, 0.11 * r + w * 0.3, col)
		"play":
			_fill(ci, c, r, [[-0.5, -0.78], [0.75, 0], [-0.5, 0.78]], col)
		"continue":
			ci.draw_rect(Rect2(c + Vector2(-0.8, -0.7) * r, Vector2(0.26, 1.4) * r), col)
			_fill(ci, c, r, [[-0.3, -0.72], [0.82, 0], [-0.3, 0.72]], col)
		"map":
			_line(ci, c, r, [[-0.85, -0.6], [-0.3, -0.82], [0.3, -0.6], [0.85, -0.82], [0.85, 0.6], [0.3, 0.82], [-0.3, 0.6], [-0.85, 0.82], [-0.85, -0.6]], col, w)
			ci.draw_line(c + Vector2(-0.3, -0.82) * r, c + Vector2(-0.3, 0.6) * r, col, w * 0.7)
			ci.draw_line(c + Vector2(0.3, -0.6) * r, c + Vector2(0.3, 0.82) * r, col, w * 0.7)
		"codex":
			_line(ci, c, r, [[0, -0.55], [-0.88, -0.78], [-0.88, 0.6], [0, 0.82], [0.88, 0.6], [0.88, -0.78], [0, -0.55]], col, w)
			ci.draw_line(c + Vector2(0, -0.55) * r, c + Vector2(0, 0.82) * r, col, w)
			ci.draw_line(c + Vector2(-0.65, -0.35) * r, c + Vector2(-0.22, -0.26) * r, col, w * 0.6)
			ci.draw_line(c + Vector2(0.22, -0.26) * r, c + Vector2(0.65, -0.35) * r, col, w * 0.6)
		"settings":
			for k in 8:
				var a := k * TAU / 8.0
				var d := Vector2(cos(a), sin(a))
				ci.draw_line(c + d * r * 0.5, c + d * r * 0.9, col, w * 1.6)
			ci.draw_arc(c, r * 0.56, 0, TAU, 20, col, w * 1.2)
			ci.draw_arc(c, r * 0.2, 0, TAU, 12, col, w)
		"save":
			_line(ci, c, r, [[-0.82, -0.82], [0.5, -0.82], [0.82, -0.5], [0.82, 0.82], [-0.82, 0.82], [-0.82, -0.82]], col, w)
			ci.draw_rect(Rect2(c + Vector2(-0.45, -0.82) * r, Vector2(0.8, 0.45) * r), col, false, w * 0.8)
			ci.draw_rect(Rect2(c + Vector2(-0.5, 0.15) * r, Vector2(1.0, 0.67) * r), col)
		"exit":
			_line(ci, c, r, [[0.05, -0.5], [0.05, -0.88], [-0.82, -0.88], [-0.82, 0.88], [0.05, 0.88], [0.05, 0.5]], col, w)
			ci.draw_line(c + Vector2(-0.35, 0) * r, c + Vector2(0.62, 0) * r, col, w)
			_fill(ci, c, r, [[0.5, -0.3], [0.92, 0], [0.5, 0.3]], col)
		"back":
			ci.draw_line(c + Vector2(0.85, 0) * r, c + Vector2(-0.35, 0) * r, col, w * 1.2)
			_fill(ci, c, r, [[-0.88, 0], [-0.3, -0.5], [-0.3, 0.5]], col)
		"next":
			ci.draw_line(c + Vector2(-0.85, 0) * r, c + Vector2(0.35, 0) * r, col, w * 1.2)
			_fill(ci, c, r, [[0.88, 0], [0.3, -0.5], [0.3, 0.5]], col)
		"skip":
			_line(ci, c, r, [[-0.8, -0.62], [-0.18, 0], [-0.8, 0.62]], col, w * 1.3)
			_line(ci, c, r, [[0.05, -0.62], [0.67, 0], [0.05, 0.62]], col, w * 1.3)
		"slots":
			for k in 3:
				ci.draw_rect(Rect2(c + Vector2(-0.82, -0.78 + k * 0.58) * r, Vector2(1.64, 0.4) * r), col, false, w)
				ci.draw_circle(c + Vector2(0.55, -0.58 + k * 0.58) * r, w * 0.8, col)
		"stats":
			ci.draw_line(c + Vector2(-0.88, 0.85) * r, c + Vector2(0.88, 0.85) * r, col, w)
			ci.draw_rect(Rect2(c + Vector2(-0.7, 0.1) * r, Vector2(0.36, 0.7) * r), col)
			ci.draw_rect(Rect2(c + Vector2(-0.18, -0.7) * r, Vector2(0.36, 1.5) * r), col)
			ci.draw_rect(Rect2(c + Vector2(0.34, -0.25) * r, Vector2(0.36, 1.05) * r), col)
		"tutorial":
			ci.draw_arc(c, r * 0.9, 0, TAU, 24, col, w)
			ci.draw_arc(c + Vector2(0, -0.22) * r, 0.3 * r, PI * 1.05, PI * 2.35, 12, col, w)
			ci.draw_line(c + Vector2(0.14, 0.02) * r, c + Vector2(0, 0.24) * r, col, w)
			ci.draw_circle(c + Vector2(0, 0.52) * r, w * 0.8, col)
		"quit":
			ci.draw_arc(c + Vector2(0, 0.08) * r, 0.7 * r, -PI * 0.5 + 0.7, -PI * 0.5 - 0.7 + TAU, 20, col, w * 1.2)
			ci.draw_line(c + Vector2(0, -0.92) * r, c + Vector2(0, -0.1) * r, col, w * 1.2)
		"jack_in":
			ci.draw_rect(Rect2(c + Vector2(-0.42, -0.25) * r, Vector2(0.84, 0.62) * r), col)
			ci.draw_line(c + Vector2(-0.2, -0.25) * r, c + Vector2(-0.2, -0.85) * r, col, w * 1.2)
			ci.draw_line(c + Vector2(0.2, -0.25) * r, c + Vector2(0.2, -0.85) * r, col, w * 1.2)
			_line(ci, c, r, [[0, 0.37], [0, 0.62], [0.35, 0.8], [0.8, 0.8]], col, w)
		"more":
			_line(ci, c, r, [[-0.7, -0.5], [0, 0.1], [0.7, -0.5]], col, w * 1.3)
			_line(ci, c, r, [[-0.7, 0.05], [0, 0.65], [0.7, 0.05]], col, w * 1.3)
		"fight":
			ci.draw_arc(c, r * 0.62, 0, TAU, 20, col, w)
			for k in 4:
				var d := Vector2.RIGHT.rotated(k * PI * 0.5)
				ci.draw_line(c + d * r * 0.3, c + d * r * 0.95, col, w)
			ci.draw_circle(c, w * 0.9, col)
		"shop":
			ci.draw_rect(Rect2(c + Vector2(-0.68, -0.3) * r, Vector2(1.36, 1.15) * r), col, false, w)
			ci.draw_arc(c + Vector2(0, -0.3) * r, 0.36 * r, PI, TAU, 12, col, w)
			ci.draw_arc(c + Vector2(0, 0.28) * r, 0.2 * r, 0, TAU, 12, col, w * 0.7)
		"terminal":
			ci.draw_rect(Rect2(c + Vector2(-0.88, -0.68) * r, Vector2(1.76, 1.36) * r), col, false, w)
			_line(ci, c, r, [[-0.55, -0.28], [-0.2, 0], [-0.55, 0.28]], col, w)
			ci.draw_line(c + Vector2(-0.05, 0.3) * r, c + Vector2(0.45, 0.3) * r, col, w)
		"rack":
			for k in 3:
				ci.draw_rect(Rect2(c + Vector2(-0.7, -0.88 + k * 0.6) * r, Vector2(1.4, 0.5) * r), col, false, w)
				ci.draw_circle(c + Vector2(0.42, -0.63 + k * 0.6) * r, w * 0.8, col)
				ci.draw_line(c + Vector2(-0.5, -0.63 + k * 0.6) * r, c + Vector2(0.1, -0.63 + k * 0.6) * r, col, w * 0.6)
		"cooling":
			# Heat going down (H24 K5): a small flame and a bold down arrow beside it.
			_line(ci, c + Vector2(-0.32, 0.02) * r, r * 0.62, [[0, -1.0], [0.38, -0.45], [0.62, 0.05], [0.58, 0.5], [0.3, 0.85], [0, 0.95], [-0.3, 0.85], [-0.58, 0.5], [-0.55, 0.0], [-0.3, -0.32], [-0.12, 0.02], [0, -1.0]], col, w * 0.85)
			ci.draw_line(c + Vector2(0.52, -0.85) * r, c + Vector2(0.52, 0.35) * r, col, w * 1.2)
			_fill(ci, c, r, [[0.16, 0.25], [0.88, 0.25], [0.52, 0.9]], col)
		"claim":
			# The map's claimed mark: a spray-paint ring with a drip.
			ci.draw_arc(c + Vector2(0, -0.12) * r, 0.62 * r, 0, TAU, 20, col, w * 1.3)
			ci.draw_line(c + Vector2(0.32, 0.4) * r, c + Vector2(0.32, 0.9) * r, col, w)
			ci.draw_circle(c + Vector2(0.32, 0.92) * r, w * 0.8, col)
		"links":
			# Sites a run opens: a node, a street to a new node, its arrowhead.
			ci.draw_arc(c + Vector2(-0.6, 0.45) * r, 0.28 * r, 0, TAU, 12, col, w)
			ci.draw_line(c + Vector2(-0.4, 0.25) * r, c + Vector2(0.4, -0.45) * r, col, w)
			_fill(ci, c, r, [[0.88, -0.88], [0.62, -0.18], [0.18, -0.62]], col)
		"ram":
			# A memory stick: the board, three chips on it (the RAM bar's squares), its pins.
			ci.draw_rect(Rect2(c + Vector2(-0.92, -0.5) * r, Vector2(1.84, 0.82) * r), col, false, w)
			for k in 3:
				ci.draw_rect(Rect2(c + Vector2(-0.7 + k * 0.52, -0.32) * r, Vector2(0.36, 0.46) * r), col)
			for k in 5:
				var x := -0.72 + k * 0.36
				ci.draw_line(c + Vector2(x, 0.32) * r, c + Vector2(x, 0.62) * r, col, w * 0.7)
		"cart":
			# A shopping cart: the handle, the basket, two wheels.
			_line(ci, c, r, [[-0.95, -0.72], [-0.62, -0.72], [-0.38, 0.35], [0.66, 0.35], [0.88, -0.42], [-0.52, -0.42]], col, w)
			ci.draw_arc(c + Vector2(-0.25, 0.7) * r, 0.16 * r, 0, TAU, 10, col, w)
			ci.draw_arc(c + Vector2(0.52, 0.7) * r, 0.16 * r, 0, TAU, 10, col, w)
		"shred":
			# A shredder: the machine's mouth, a card going in, strips coming out.
			ci.draw_rect(Rect2(c + Vector2(-0.4, -0.95) * r, Vector2(0.8, 0.5) * r), col, false, w * 0.8)
			ci.draw_rect(Rect2(c + Vector2(-0.9, -0.42) * r, Vector2(1.8, 0.42) * r), col)
			for k in 5:
				var x := -0.64 + k * 0.32
				ci.draw_line(c + Vector2(x, 0.1) * r, c + Vector2(x, 0.9 - (k % 2) * 0.2) * r, col, w * 0.8)
		_:
			ci.draw_arc(c, r * 0.6, 0, TAU, 16, col, w)


## An open polyline through `pts` (in units of r around c).
static func _line(ci: CanvasItem, c: Vector2, r: float, pts: Array, col: Color, w: float) -> void:
	var out := PackedVector2Array()
	for p in pts:
		out.append(c + Vector2(float(p[0]), float(p[1])) * r)
	ci.draw_polyline(out, col, w)


## A filled convex polygon through `pts` (in units of r around c).
static func _fill(ci: CanvasItem, c: Vector2, r: float, pts: Array, col: Color) -> void:
	var out := PackedVector2Array()
	for p in pts:
		out.append(c + Vector2(float(p[0]), float(p[1])) * r)
	ci.draw_colored_polygon(out, col)


## A card-shaped box at `at` (units of r from c), `sz` in units of r; `solid` fills it faintly.
static func _box(ci: CanvasItem, c: Vector2, r: float, at: Vector2, sz: Vector2, col: Color, w: float, solid: bool) -> void:
	var rect := Rect2(c + at * r, sz * r)
	if solid:
		ci.draw_rect(rect, Color(col, 0.25))
	ci.draw_rect(rect, col, false, w)


## A head and shoulders of height ~2r centred on `c`.
static func _person(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float) -> void:
	ci.draw_arc(c + Vector2(0, -0.42) * r, 0.3 * r, 0, TAU, 14, col, w)
	ci.draw_arc(c + Vector2(0, 0.75) * r, 0.58 * r, PI, TAU, 14, col, w)
