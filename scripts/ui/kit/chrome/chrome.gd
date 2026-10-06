class_name Chrome
extends RefCounted
## ART-10 4C: the v2 chrome seam for the menus, title, settings and HQ (ART_BIBLE v2 §1.2,
## §2.9, §2.10, §4.13). One face per medium: Anton for vinyl stickers, Share Tech Mono for
## the Cell's terminals, IBM Plex Sans Condensed for prose, Courier Prime for corp paper,
## Permanent Marker for the grease pencil. The 4C views read faces, sizes and drawn pieces
## only through here, so Group 1's foundations (1A faces / theme types, 1B materials)
## switch in at one place when they land. View only.

## The chamfer cut off a terminal panel's top-right corner, and the length of the small
## bracket drawn at its bottom-left (px at 1280x720, ui_kit.jpg).
const CHAMFER := 12.0
const FOOT_TICK := 10.0
## Terminal edge width (px) and the header strip's height as a multiple of its font size.
const EDGE_W := 1.5
const HEADER_LINE := 1.55
## The header's square marker (px) and its inset from the right edge.
const SQUARE := 8.0
## Scanline period (px) and strength on the glass; the hex-dump's alpha (§1.2: 3 px, 10 %;
## hex 6 %).
const SCAN_PERIOD := 3.0
const SCAN_ALPHA := 0.1
const HEX_ALPHA := 0.06
## The hex-dump's columns (characters) and the text it repeats (a fixed dump: no RNG).
const HEX_TEXT := "4F 2A 9C 11 E0 7B 3D A2 5E 88 0C F1 6B 92 D4 17 3A C9 0E 7F B3 21 58 E6 9A 04 CD 6E 13 F8 A7 42 "


## Anton for the drawn stickers and the neon sign: the kit's raster copy (Group 1B,
## VinylSticker.art_font). Their die-cut, keyline, extrude and glow are outlines wider than
## an MSDF field holds; everything else keeps the MSDF face.
static func sticker_font() -> Font:
	return VinylSticker.art_font()


## `path`'s texture, kept in `into` (a view's own holder) so it lives as long as the view
## that draws it.
static func held(into: Dictionary, path: String) -> Texture2D:
	if not into.has(path):
		into[path] = load(path) as Texture2D if ResourceLoader.exists(path) else null
	return into[path]


static func terminal_font() -> Font:
	return Palette.mono()


static func body_font() -> Font:
	return Palette.body()


static func body_medium_font() -> Font:
	return Palette.body_medium()


static func pencil_font() -> Font:
	return Palette.pencil()


## Courier Prime (corp paper fields, §2.9; Group 1A's face).
static func paper_font() -> Font:
	return Palette.paper()


static func paper_bold_font() -> Font:
	return Palette.paper_bold()


## The pixel size of type step `step` at the player's text scale.
static func px(step: int) -> int:
	return UiTheme.font_px(step)


## The terminal mono tracked for CAPS at `step` (§2.9: CAPS +8 %).
static func caps_font(step: int) -> Font:
	return UiTheme.tracked(Palette.mono(), UiTheme.TRACK_MONO_CAPS, step)


## A label in the terminal mono: CAPS tracked, `step`, `color`.
static func caps_label(text: String, step: int, color: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override(&"font", caps_font(step))
	l.add_theme_font_size_override(&"font_size", px(step))
	l.add_theme_color_override(&"font_color", color)
	UiWrap.whole_words(l)  # a page's UiWrap.fit leaves it be
	# Terminal CAPS are short labels: they hold their line (a caption that wraps reads as two).
	l.custom_minimum_size.x = ceilf(caps_font(step).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px(step)).x)
	return l


## A prose label in Plex Sans Condensed (`step`, TEXT_MID unless given), wrapping at words.
static func body_label(text: String, step: int = UiTheme.BODY, color: Color = Palette.TEXT_MID) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override(&"font", Palette.body())
	l.add_theme_font_size_override(&"font_size", px(step))
	l.add_theme_color_override(&"font_color", color)
	UiWrap.whole_words(l)
	return l


## The navy glass of a terminal with its cut corner (top right) as a polygon in `r`.
static func panel_shape(r: Rect2, chamfer: float = CHAMFER) -> PackedVector2Array:
	return PackedVector2Array([r.position, Vector2(r.end.x - chamfer, r.position.y), Vector2(r.end.x, r.position.y + chamfer),
		r.end, Vector2(r.position.x, r.end.y)])


## Draws a v2 terminal panel on `ci` (ui_kit.jpg "TERMINAL"): navy glass with its cut
## corner, faint scanlines (off under reduce effects), the accent edge and the small bracket
## at the bottom left. High contrast: opaque black and a solid edge (§5.6).
static func draw_terminal(ci: CanvasItem, r: Rect2, accent: Color, glass: Color = Palette.TERMINAL_BG, chamfer: float = CHAMFER) -> void:
	var shape := panel_shape(r, chamfer)
	var hc := Settings.high_contrast
	accent = PaletteSkins.chrome(accent)  # ART-12 12s-b: the skin's edge and glass
	glass = PaletteSkins.chrome(glass)
	ci.draw_colored_polygon(shape, HighContrast.BG if hc else glass)
	if not hc and not Settings.reduce_effects:
		var y := r.position.y + SCAN_PERIOD
		while y < r.end.y - 1.0:
			ci.draw_line(Vector2(r.position.x + 1.0, y), Vector2(r.end.x - (chamfer if y < r.position.y + chamfer else 1.0), y), Color(Palette.NET_BG_OUTER, SCAN_ALPHA), 1.0)
			y += SCAN_PERIOD
	var edge := shape.duplicate()
	edge.append(shape[0])
	ci.draw_polyline(edge, accent if hc else Color(accent, 0.85), EDGE_W * (2.0 if hc else 1.0), true)
	var foot := Vector2(r.position.x - 3.0, r.end.y + 3.0)
	ci.draw_polyline(PackedVector2Array([foot + Vector2(0, -FOOT_TICK), foot, foot + Vector2(FOOT_TICK, 0)]), Color(accent, 0.7), EDGE_W)


## Draws the faint hex-dump on a terminal's glass (§1.2: 6 %), right-aligned columns.
static func draw_hex(ci: CanvasItem, r: Rect2, color: Color = Palette.NET_CYAN) -> void:
	color = PaletteSkins.chrome(color)  # ART-12 12s-b
	if Settings.high_contrast or Settings.reduce_effects:
		return
	var f := Palette.mono()
	var size := px(UiTheme.CAPTION)
	var line := f.get_height(size)
	var y := r.position.y + line
	var i := 0
	while y < r.end.y:
		var at := (i * 7) % HEX_TEXT.length()
		var text := (HEX_TEXT + HEX_TEXT).substr(at, int(r.size.x / maxf(1.0, f.get_string_size("0", HORIZONTAL_ALIGNMENT_LEFT, -1, size).x)))
		ci.draw_string(f, Vector2(r.position.x, y), text, HORIZONTAL_ALIGNMENT_LEFT, r.size.x, size, Color(color, HEX_ALPHA))
		y += line
		i += 1


## Draws a terminal header strip (`> TITLE`, an optional tag chip and the square marker)
## across the top of `r`; returns its height.
static func draw_header(ci: CanvasItem, r: Rect2, title: String, accent: Color, tag: String = "", step: int = UiTheme.BODY) -> float:
	var size := px(step)
	var h := ceilf(size * HEADER_LINE)
	var strip := Rect2(r.position, Vector2(r.size.x, h))
	ci.draw_rect(strip, Color(accent, 0.12))
	ci.draw_line(Vector2(strip.position.x, strip.end.y), Vector2(strip.end.x, strip.end.y), Color(accent, 0.6), 1.0)
	var f := caps_font(step)
	var base := strip.position.y + (h + f.get_ascent(size) - f.get_descent(size)) * 0.5
	ci.draw_string(f, Vector2(strip.position.x + size * 0.6, base), "> " + title, HORIZONTAL_ALIGNMENT_LEFT, -1, size, accent)
	var right := strip.end.x - CHAMFER - SQUARE - size * 0.4
	ci.draw_rect(Rect2(Vector2(right, strip.position.y + (h - SQUARE) * 0.5), Vector2(SQUARE, SQUARE)), accent)
	if tag != "":
		var tw := f.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		var chip := Rect2(Vector2(right - tw - size * 1.4, strip.position.y + h * 0.18), Vector2(tw + size * 0.8, h * 0.64))
		ci.draw_rect(chip, Color(accent, 0.9), false, 1.0)
		ci.draw_string(f, Vector2(chip.position.x + size * 0.4, base), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, size, accent)
	return h
