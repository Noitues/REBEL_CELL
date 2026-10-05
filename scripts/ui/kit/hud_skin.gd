class_name HudSkin
extends RefCounted
## ART-2 2D (ART_BIBLE v2 §3.1, §1.3, §4.13): the one place the combat HUD picks its colour
## tokens, faces, panel style, sticker material and small glyphs. Group 1 lands palette v2 /
## theme types (1A), the vinyl sticker and CRT materials (1B) and the glyph atlas (1C) in
## parallel: switching the HUD to them is an edit here, not in every HUD part. View only; no
## game state.

# --- Colour roles (tokens only; 1A's palette v2 replaces the right-hand sides) ----------
## The result chips (D15): final damage (red, boxed), absorbed (blue), gained (green), other
## losses, and the text on a filled chip.
const CHIP_DAMAGE := Palette.HARM
const CHIP_ABSORBED := Palette.PROTECT
const CHIP_GAIN := Palette.GAIN
const CHIP_OTHER := Palette.TEXT_MID
const CHIP_INK := Palette.LIVE_NUMBER_RIM
## Terminal chrome (RESPIN / UNDO chips, the RAM panel, the TURN banner).
const TERMINAL_BG := Palette.TERMINAL_BG
const TERMINAL_EDGE := Palette.TERMINAL_EDGE
const TERMINAL_TEXT := Palette.TERMINAL_TEXT
const TERMINAL_DIM := Palette.TEXT_LO
const TERMINAL_HI := Palette.TEXT_HI
## The RAM pips: lit, spent, about to be spent, about to be gained.
const PIP_ON := Palette.NET_CYAN
const PIP_OFF := Palette.NIGHT_BLOCK_LIT
## Vinyl stickers: the pink verb (SEND IT), the yellow safe choice, the die-cut and keyline.
const VINYL_PINK := Palette.STICKER_COMMIT
const VINYL_YELLOW := Palette.STICKER_SAFE
const VINYL_DIE_CUT := Palette.STICKER_DIE_CUT
const VINYL_KEYLINE := Palette.INK
const VINYL_DISABLED := Palette.DISABLED
## The lime focus halo of a sticker (§2.10).
const FOCUS := Palette.FOCUS

# --- Shape (px at text scale 1.0) ---------------------------------------------------------
## The terminal panel's chamfered corner and its edge.
const CHAMFER := 10.0
const EDGE_PX := 1.5
## Vinyl: keyline, extrude and die-cut (the bible's 5 / 7 / 12 at 1080p, at the 720p layout).
const VINYL_KEYLINE_PX := 3.0
const VINYL_EXTRUDE_PX := 5.0
const VINYL_DIE_CUT_PX := 8.0
## Vinyl gloss at rest and on hover (alpha of the white sweep), and the disabled grey's share.
const VINYL_GLOSS_REST := 0.22
const VINYL_GLOSS_HOT := 0.5
const VINYL_GREY := Palette.STICKER_DISABLED_GREY
## The pink's light and dark ends (shares lightened / darkened).
const VINYL_LIGHT := 0.35
const VINYL_DARK := 0.35
## Alpha of a washed-out system word under a sticker (EXECUTE).
const SYSTEM_WORD_ALPHA := 0.3


## The display face (stickers, big numbers): Anton.
static func display() -> Font:
	return Palette.display()


## The terminal face: Share Tech Mono.
static func mono() -> Font:
	return Palette.mono()


## The tooltip / body face: Plex Sans Condensed.
static func body() -> Font:
	return Palette.body()


## 1C: the atlas glyph for a HUD mark (&"" = the drawn mark below), and for a status.
const GLYPHS := {"shield": &"picto_block", "ram": &"picto_ram", "hp": &"picto_hp", "ccw": &"picto_spin_ccw", "cw": &"picto_spin"}
const STATUS_GLYPHS := {RC.Status.CORRUPTED: &"status_corrupted", RC.Status.OVERCLOCKED: &"status_overclocked",
	RC.Status.ENCRYPTED: &"status_encrypted", RC.Status.PARASITE: &"status_parasite"}
## The smallest a glyph box is drawn (ART_BIBLE v2 §5.2, the 16 px glyph rule).
const GLYPH_MIN_PX := 16.0


## The atlas glyph for mark `kind` (&"" when it has none and is drawn).
static func glyph_name(kind: String) -> StringName:
	return GLYPHS.get(kind, &"")


## A glyph node for atlas glyph `name` in `fill` (1C's SDF shader), its box `box_px`.
static func glyph_node(name: StringName, box_px: float, fill: Color) -> GlyphIcon:
	var g := GlyphIcon.make(name, maxf(GLYPH_MIN_PX, box_px))
	g.fill = fill
	return g


## 1B seam: the vinyl sticker material (null = drawn by the sticker itself).
static func vinyl_material() -> Material:
	return null


## 1B seam: the CRT panel material (UiTheme's CRT shader until 1B's lands).
static func crt_material() -> Material:
	return UiTheme.crt_material()


## 1B: the CRT glass (CrtTerminalPanel: navy glass, scanlines, edge glow; the hex dump when
## `hex`) as `owner`'s backing, drawn behind it (the owner draws its words, pips and edge
## states on top). No prompt, no caret: the owner's words are its own.
static func crt_backing(owner: Control, hex: bool = false) -> CrtTerminalPanel:
	var c := CrtTerminalPanel.new()
	c.name = "CrtGlass"
	c.prompt = false
	c.caret = false
	c.hex_dump = hex
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.show_behind_parent = true
	owner.add_child(c, false, Node.INTERNAL_MODE_FRONT)
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return c


## A terminal panel's edge only (over a CRT backing): the chamfered outline.
static func draw_terminal_edge(ci: CanvasItem, r: Rect2, edge: Color) -> void:
	draw_terminal_panel(ci, r, edge, Color(TERMINAL_BG, 0.0))


## A terminal panel: dark glass, a thin cyan edge, its top-right corner cut (§4.13).
## `edge` overrides the edge colour (a hot or refused state).
static func draw_terminal_panel(ci: CanvasItem, r: Rect2, edge: Color = TERMINAL_EDGE, bg: Color = TERMINAL_BG) -> void:
	var c := minf(CHAMFER * Settings.text_scale, minf(r.size.x, r.size.y) * 0.4)
	var pts := PackedVector2Array([r.position, Vector2(r.end.x - c, r.position.y), Vector2(r.end.x, r.position.y + c),
		r.end, Vector2(r.position.x, r.end.y)])
	ci.draw_colored_polygon(pts, bg)
	var closed := pts.duplicate()
	closed.append(pts[0])
	ci.draw_polyline(closed, edge, EDGE_PX, true)


## The art pass's glyph (1C's atlas, regenerated from the concept scripts) for each HUD mark; heat
## has none (the concepts draw Heat as a gauge, never a glyph), so it stays the drawn flame.
const HUD_GLYPHS := {"shield": &"picto_block", "ram": &"picto_ram", "hp": &"picto_hp", "evade": &"slice_detour",
	"lock": &"state_locked", "ccw": &"picto_spin_ccw", "cw": &"picto_spin", "cards": &"picto_draw"}
## The atlas glyph's box over the mark's radius (the drawn marks span about 2 r).
const HUD_GLYPH_BOX := 2.1


## Small HUD glyphs: the atlas glyph (M14 asset parity) where the art pass has one, else the drawn
## mark. `kind`: "shield", "ram", "heat", "hp", "evade", "lock", "ccw", "cw", "cards".
static func draw_glyph(ci: CanvasItem, kind: String, c: Vector2, r: float, col: Color) -> void:
	if HUD_GLYPHS.has(kind) and WheelGlyphs.draw(ci, WheelGlyphs.named(HUD_GLYPHS[kind]), c, r * HUD_GLYPH_BOX, col):
		return
	match kind:
		"shield":
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.8, -r * 0.8), c + Vector2(r * 0.8, -r * 0.8),
				c + Vector2(r * 0.8, r * 0.05), c + Vector2(0, r), c + Vector2(-r * 0.8, r * 0.05)]), col)
		"ram":
			ci.draw_rect(Rect2(c - Vector2(r * 0.75, r * 0.55), Vector2(r * 1.5, r * 1.1)), col, false, maxf(1.0, r * 0.22))
			for k in 3:
				var x := c.x - r * 0.45 + k * r * 0.45
				ci.draw_line(Vector2(x, c.y + r * 0.55), Vector2(x, c.y + r * 0.9), col, maxf(1.0, r * 0.18))
		"heat":
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r), c + Vector2(r * 0.7, r * 0.2), c + Vector2(r * 0.45, r * 0.85),
				c + Vector2(-r * 0.45, r * 0.85), c + Vector2(-r * 0.7, r * 0.2)]), col)
		"hp":
			ci.draw_rect(Rect2(c - Vector2(r * 0.3, r * 0.9), Vector2(r * 0.6, r * 1.8)), col)
			ci.draw_rect(Rect2(c - Vector2(r * 0.9, r * 0.3), Vector2(r * 1.8, r * 0.6)), col)
		"evade":
			for k in 2:
				var x := c.x - r * 0.5 + k * r * 0.6
				ci.draw_polyline(PackedVector2Array([Vector2(x, c.y - r * 0.7), Vector2(x + r * 0.5, c.y), Vector2(x, c.y + r * 0.7)]), col, maxf(1.5, r * 0.25))
		"lock":
			ci.draw_rect(Rect2(c + Vector2(-r * 0.7, -r * 0.1), Vector2(r * 1.4, r * 1.0)), col)
			ci.draw_arc(c + Vector2(0, -r * 0.15), r * 0.45, PI, TAU, 10, col, maxf(1.5, r * 0.22))
		"ccw", "cw":
			var d := -1.0 if kind == "ccw" else 1.0
			var a0 := -PI * 0.5 - d * PI * 0.75
			var a1 := -PI * 0.5 + d * PI * 0.55
			ci.draw_arc(c, r * 0.62, minf(a0, a1), maxf(a0, a1), 18, col, maxf(2.0, r * 0.2), true)
			var tip := c + Vector2(cos(a1), sin(a1)) * r * 0.62
			var tg := Vector2(-sin(a1), cos(a1)) * d
			ci.draw_colored_polygon(PackedVector2Array([tip + tg * r * 0.42, tip + tg.orthogonal() * r * 0.32, tip - tg.orthogonal() * r * 0.32]), col)
		"cards":
			ci.draw_rect(Rect2(c + Vector2(-r * 0.75, -r * 0.6), Vector2(r * 1.0, r * 1.4)), col, false, maxf(1.0, r * 0.2))
			ci.draw_rect(Rect2(c + Vector2(-r * 0.25, -r * 0.9), Vector2(r * 1.0, r * 1.4)), col, false, maxf(1.0, r * 0.2))
		_:
			ci.draw_circle(c, r * 0.5, col)
