class_name H7Glyphs
extends RefCounted
## Vector placeholder glyphs and palette for the H7 lab, matching the r7 mockups.
## Threats are cobalt, the Cell is yellow, red only marks loss, teal only the Cell's checks.

const BG := Color8(14, 16, 32)
const BG2 := Color8(22, 26, 48)
const PANEL := Color8(26, 30, 54)
const PANEL_EDGE := Color8(70, 80, 130)
const INK := Color8(232, 236, 245)
const DIM := Color8(140, 148, 175)
const CELL := Color8(255, 210, 63)
const CELL_DIM := Color8(130, 108, 40)
const THREAT := Color8(61, 107, 255)
const THREAT_LIGHT := Color8(140, 170, 255)
const DMG := Color8(255, 77, 77)
const DOWN_GREY := Color8(110, 114, 128)
const HOLD := Color8(255, 170, 40)
const CLEAN := Color8(90, 220, 200)
const BREACH := Color8(230, 40, 50)
const HEAT := Color8(255, 110, 40)

static var font: Font = ThemeDB.fallback_font


## Text with its top-left at `p`.
static func text(ci: CanvasItem, p: Vector2, s: String, size: int, col: Color = INK, align: int = HORIZONTAL_ALIGNMENT_LEFT, width: float = -1.0) -> void:
	ci.draw_string(font, p + Vector2(0, size * 0.95), s, align, width, size, col)


## Text centered on `c`.
static func text_c(ci: CanvasItem, c: Vector2, s: String, size: int, col: Color = INK) -> void:
	var w := font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	ci.draw_string(font, c + Vector2(-w * 0.5, size * 0.36), s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


## Rounded panel.
static func panel(ci: CanvasItem, r: Rect2, edge: Color = PANEL_EDGE, fill: Color = PANEL, width: float = 2.0) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.set_corner_radius_all(6)
	sb.border_color = edge
	sb.set_border_width_all(int(width))
	ci.draw_style_box(sb, r)


## Button; `hot` draws the hover state.
static func button(ci: CanvasItem, r: Rect2, label: String, hot: bool = false, enabled: bool = true, size: int = 20) -> void:
	var edge := CELL if enabled else PANEL_EDGE
	panel(ci, r, edge, Color8(60, 52, 24) if (hot and enabled) else PANEL, 3.0)
	text_c(ci, r.get_center(), label, size, CELL if enabled else DIM)


static func line(ci: CanvasItem, a: Vector2, b: Vector2, col: Color, w: float = 2.0) -> void:
	ci.draw_line(a, b, col, w, true)


static func circle(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 2.0) -> void:
	ci.draw_arc(c, r, 0.0, TAU, 28, col, w, true)


static func hexagon(ci: CanvasItem, c: Vector2, r: float, fill: Color, edge: Color, w: float = 3.0) -> void:
	var pts := PackedVector2Array()
	for k in range(6):
		var a := PI / 6.0 + k * PI / 3.0
		pts.append(c + Vector2(cos(a), sin(a)) * r)
	ci.draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	ci.draw_polyline(pts, edge, w, true)


## Strongbox: the BANK glyph.
static func strongbox(ci: CanvasItem, c: Vector2, r: float, col: Color = INK) -> void:
	ci.draw_rect(Rect2(c.x - r, c.y - r * 0.7, r * 2.0, r * 1.5), col, false, 3.0)
	ci.draw_line(Vector2(c.x - r, c.y - r * 0.1), Vector2(c.x + r, c.y - r * 0.1), col, 2.0)
	ci.draw_rect(Rect2(c.x - r * 0.2, c.y - r * 0.3, r * 0.4, r * 0.45), col)


## Coin (yellow ring with a bar).
static func coin(ci: CanvasItem, c: Vector2, r: float, col: Color = CELL) -> void:
	circle(ci, c, r, col, 3.0)
	ci.draw_line(c + Vector2(0, -r * 0.45), c + Vector2(0, r * 0.45), col, 3.0)


## Signed coin: the per-raid NET. Top-left at p.
static func signed_coin(ci: CanvasItem, p: Vector2, n: int, size: int = 20) -> void:
	coin(ci, p + Vector2(size * 0.45, size * 0.55), size * 0.45)
	var col := CLEAN if n > 0 else (DMG if n < 0 else DIM)
	text(ci, p + Vector2(size * 1.05, 0), "%+d" % n, size, col)


static func flame(ci: CanvasItem, c: Vector2, r: float, col: Color = HEAT) -> void:
	var pts := PackedVector2Array([c + Vector2(0, -r * 1.3), c + Vector2(r * 0.9, r * 0.2), c + Vector2(r * 0.5, r),
		c + Vector2(-r * 0.5, r), c + Vector2(-r * 0.9, r * 0.2), c + Vector2(-r * 0.2, -r * 0.4)])
	ci.draw_colored_polygon(pts, col)


static func check(ci: CanvasItem, c: Vector2, r: float, col: Color = CLEAN) -> void:
	ci.draw_polyline(PackedVector2Array([c + Vector2(-r, 0), c + Vector2(-r * 0.3, r * 0.7), c + Vector2(r, -r * 0.7)]), col, 3.0, true)


static func cross(ci: CanvasItem, c: Vector2, r: float, col: Color = DMG, w: float = 3.0) -> void:
	ci.draw_line(c + Vector2(-r, -r), c + Vector2(r, r), col, w, true)
	ci.draw_line(c + Vector2(-r, r), c + Vector2(r, -r), col, w, true)


static func netrun_hex(ci: CanvasItem, c: Vector2, r: float, col: Color = INK) -> void:
	hexagon(ci, c, r, Color(0, 0, 0, 0), col, 2.0)


static func eye(ci: CanvasItem, c: Vector2, r: float, col: Color = INK) -> void:
	ci.draw_arc(c + Vector2(0, r * 0.5), r * 1.1, PI * 1.2, PI * 1.8, 12, col, 2.0, true)
	ci.draw_arc(c + Vector2(0, -r * 0.5), r * 1.1, PI * 0.2, PI * 0.8, 12, col, 2.0, true)
	ci.draw_circle(c, r * 0.3, col)


static func person(ci: CanvasItem, c: Vector2, r: float, col: Color = CELL) -> void:
	ci.draw_circle(c + Vector2(0, -r * 0.55), r * 0.38, col)
	ci.draw_arc(c + Vector2(0, r * 0.9), r * 0.8, PI, TAU, 12, col, r * 0.4, true)


static func arrow(ci: CanvasItem, a: Vector2, b: Vector2, col: Color, w: float = 3.0, head: float = 9.0) -> void:
	var d := (b - a).normalized()
	ci.draw_line(a, b - d * head * 0.5, col, w, true)
	var n := Vector2(-d.y, d.x)
	ci.draw_colored_polygon(PackedVector2Array([b, b - d * head + n * head * 0.55, b - d * head - n * head * 0.55]), col)


## Fortress piece glyph.
static func piece(ci: CanvasItem, id: String, c: Vector2, r: float, col: Color = INK) -> void:
	match id:
		"TURRET":
			circle(ci, c, r, col)
			ci.draw_line(c + Vector2(-r * 1.3, 0), c + Vector2(r * 1.3, 0), col, 2.0)
			ci.draw_line(c + Vector2(0, -r * 1.3), c + Vector2(0, r * 1.3), col, 2.0)
		"SENTRY":
			ci.draw_rect(Rect2(c.x - r * 0.9, c.y - r, r * 0.6, r * 1.6), col)
			ci.draw_rect(Rect2(c.x + r * 0.3, c.y - r, r * 0.6, r * 1.6), col)
			ci.draw_rect(Rect2(c.x - r * 1.1, c.y + r * 0.6, r * 2.2, r * 0.4), col)
		"RAILGUN":
			ci.draw_rect(Rect2(c.x - r * 1.2, c.y - r * 0.25, r * 1.8, r * 0.5), col)
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(r * 1.3, 0), c + Vector2(r * 0.5, -r * 0.7), c + Vector2(r * 0.5, r * 0.7)]), col)
		"ICE":
			for k in range(3):
				var a := k * PI / 3.0
				var d := Vector2(cos(a), sin(a)) * r * 1.2
				ci.draw_line(c - d, c + d, col, 2.0)
		"DECOY":
			ci.draw_arc(c + Vector2(0, -r * 0.2), r * 0.7, PI, TAU, 14, col, 2.5, true)
			ci.draw_line(c + Vector2(r * 0.7, -r * 0.2), c + Vector2(r * 0.7, r * 0.9), col, 2.5)
			ci.draw_line(c + Vector2(-r * 0.7, -r * 0.2), c + Vector2(-r * 0.7, r * 0.3), col, 2.5)


## Node job icon (inside the node disc).
static func node_icon(ci: CanvasItem, id: String, c: Vector2, r: float, col: Color) -> void:
	match id:
		"HOME":
			ci.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(r * 0.7, 0),
				c + Vector2(r * 0.7, r * 0.8), c + Vector2(-r * 0.7, r * 0.8), c + Vector2(-r * 0.7, 0), c + Vector2(-r, 0)]), col)
		"FW":
			for k in range(3):
				ci.draw_rect(Rect2(c.x - r * 0.9 + (k % 2) * r * 0.3, c.y - r * 0.8 + k * r * 0.6, r * 1.5, r * 0.42), col)
		"VAULT":
			ci.draw_rect(Rect2(c.x - r * 0.9, c.y - r * 0.9, r * 1.8, r * 1.8), col, false, 3.0)
			ci.draw_rect(Rect2(c.x - r * 0.35, c.y - r * 0.35, r * 0.7, r * 0.7), col, false, 3.0)
		"SAFE":
			ci.draw_rect(Rect2(c.x - r * 0.6, c.y - r, r * 1.2, r * 2.0), col, false, 3.0)
			ci.draw_circle(c + Vector2(r * 0.25, 0), r * 0.15, col)
		"RELAY":
			ci.draw_line(c + Vector2(0, -r * 0.3), c + Vector2(0, r * 0.9), col, 3.0)
			ci.draw_circle(c + Vector2(0, -r * 0.4), r * 0.18, col)
			ci.draw_arc(c + Vector2(0, -r * 0.4), r * 0.6, -PI * 0.8, -PI * 0.2, 10, col, 2.5, true)
			ci.draw_arc(c + Vector2(0, -r * 0.4), r * 1.0, -PI * 0.8, -PI * 0.2, 10, col, 2.5, true)
		"PROXY":
			ci.draw_arc(c + Vector2(-r * 0.5, 0), r * 0.5, 0.0, TAU, 16, col, 3.0, true)
			ci.draw_arc(c + Vector2(r * 0.5, 0), r * 0.5, 0.0, TAU, 16, col, 3.0, true)


## Cobalt shield (a threat's counter-trait base).
static func shield(ci: CanvasItem, c: Vector2, r: float, col: Color = THREAT) -> void:
	ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-r, -r), c + Vector2(r, -r), c + Vector2(r, r * 0.2),
		c + Vector2(0, r * 1.1), c + Vector2(-r, r * 0.2)]), col)


## Counter-trait: a cobalt shield and the countered piece struck through.
static func trait_glyph(ci: CanvasItem, c: Vector2, trait_id: String, r: float = 8.0) -> void:
	shield(ci, c, r)
	var pc: String = {"PLATED": "RAILGUN", "ARMORED": "TURRET", "FROSTPROOF": "ICE", "BLIND": "DECOY"}[trait_id]
	piece(ci, pc, c + Vector2(r * 2.2, 0), r * 0.8, INK)
	ci.draw_line(c + Vector2(r * 1.2, r), c + Vector2(r * 3.2, -r), THREAT_LIGHT, 3.0, true)


## Threat chip: cobalt hex with its 3-letter code. `ghost` marks a survivor from an earlier raid.
static func threat(ci: CanvasItem, base_id: String, c: Vector2, r: float, hp: int = -1, ghost: bool = false) -> void:
	hexagon(ci, c, r, Color8(30, 44, 110) if not ghost else Color8(24, 30, 70), THREAT if not ghost else THREAT_LIGHT, 2.0 if ghost else 3.0)
	text_c(ci, c, H7Data.THREAT_SHORT.get(base_id, "?"), maxi(8, int(r * 0.7)), INK)
	if hp >= 0:
		var mx: int = H7Data.THREAT_DEF[base_id][0]
		var w := r * 1.8
		ci.draw_rect(Rect2(c.x - w * 0.5, c.y + r + 3, w, 4), Color8(40, 50, 100))
		ci.draw_rect(Rect2(c.x - w * 0.5, c.y + r + 3, w * clampf(float(hp) / mx, 0.0, 1.0), 4), THREAT_LIGHT)


## Strike-through for a killed threat.
static func pencil_x(ci: CanvasItem, c: Vector2, r: float) -> void:
	cross(ci, c, r, INK, 3.0)
