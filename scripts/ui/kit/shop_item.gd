class_name ShopItem
extends ZineCard
## ART-9 4A (ART_BIBLE v2 §4.10, round 34 `shop_v5`): a MAINFRAME item in its v5 look, keeping
## every ZineCard behaviour (the press buys, the kraft tag is its BuyButton, drag, focus, SOLD
## stub, tips). Cards keep their sticker (Group 2's). The other shelves show the concept's own art
## (MainframeArt: exported unchanged from the round 34 scripts):
## - FIRMWARE: the socketed die (`fwlib.chip`; its LED and plate flare when hovered) with its pins
##   pushed into the pegboard's pink foam and a foam lip over them; its name on label-maker tape,
##   rarity and valid slots under it;
## - DAEMON: the CRT tile in its cartridge housing (`shop_v5.daemon_row`), name tape, rarity;
## - SLICE: its wedge of the stock wheel (`slicekit.wheel`, the slice's own screen and value),
##   turned to its place about the hub, a yellow arc on its rim, its tag hung there;
## - BIN: the recycle bin (`recycle.scene`; the lid lifts when hovered) under its RECYCLE BIN tape.
## The whole text of an item shows in the pegboard's info strip and its tip. View only.

enum Shelf { CARD, FIRMWARE, DAEMON, SLICE, BIN }

## Rarity colours (§2.7) and words.
const RARITY_COLOURS: Array[Color] = [Palette.RARITY_COMMON, Palette.RARITY_UNCOMMON, Palette.RARITY_RARE, Palette.CELL_PINK]
const RARITY_WORDS: Array[String] = ["COMMON", "UNCOMMON", "RARE", "BOSS"] # TR
## Lettering at text scale 1 (px): the name tape and the small lines.
const NAME_PX := 15
const SMALL_PX := 12
## Room kept between an object, its words and its kraft tag (px).
const GLYPH_GAP := 4.0
## Drawn objects grow with the text size only this far; their words and tags grow with it fully.
const OBJECT_MAX_SCALE := 1.3
## The stock wheel's wedge: its half angle (12 slices).
const WEDGE_HALF := PI / 12.0
## Where a chip's pin comb sits in its art (share of its height): the foam line.
const CHIP_PIN_LINE := 0.13
## A chip's art at text scale 1 (game px): fwlib.chip(84) x MainframeArt.SCALE.
const CHIP_W := 68.0
## The label-maker tape's padding round its word (px at text scale 1).
const TAPE_PAD := Vector2(8, 2)

var shelf: int = Shelf.CARD
var rarity: int = RC.Rarity.COMMON
## The words under the object (rarity, what it fits), the content id its art is named by.
var kind_line: String = ""
var art_id: StringName = &""
## A slice wedge: hub (local), outer and inner radius (px), its direction (radians; 0 = up). The
## item itself is never rotated: it is the wedge's bounding box, so its rect is where the wedge is.
var hub: Vector2 = Vector2.ZERO
var radius_out: float = 0.0
var radius_in: float = 0.0
var wedge_angle: float = 0.0
## The 1C glyph, only for an object the bake has no art for (new content).
var glyph: GlyphIcon = null


## The art part for this item ("" when the bake has none).
func art_name() -> String:
	match shelf:
		Shelf.FIRMWARE:
			return "chip_%s%s" % [art_id, "_lit" if _hot() and MainframeArt.has("chip_%s_lit" % art_id) else ""]
		Shelf.DAEMON:
			return "daemon_%s" % art_id
		Shelf.SLICE:
			# cut at its own place on the wheel (its read block upright): -30, 0 or +30 degrees
			return "wedge_%s_%s" % [art_id, {-1: "m1", 0: "0", 1: "p1"}.get(int(get_meta(&"wedge", 0)), "0")]
		Shelf.BIN:
			return "bin_open" if _hot() else "bin_shut"
	return ""


func _has_art() -> bool:
	var n := art_name()
	return n != "" and MainframeArt.has(n)


## Puts atlas glyph `name` on an object the bake has no art for.
func with_glyph(name: StringName) -> ShopItem:
	if name == &"" or _has_art():
		return self
	if glyph == null:
		glyph = GlyphIcon.make(name, 24.0)
		glyph.name = "Glyph"
		add_child(glyph)
		resized.connect(_place_glyph)
	glyph.glyph = name
	_place_glyph()
	return self


## The object's box (local): the chip, the cartridge, the wedge's read block, the bin's body.
func glyph_spot() -> Rect2:
	var r := object_rect()
	if shelf == Shelf.SLICE:
		var box := 34.0 * minf(text_scale, TILE_VALUE_MAX_SCALE)
		var tag := buy_button.size.y if buy_button != null else 0.0
		var rg := minf(radius_in + (radius_out - radius_in) * 0.62, radius_out - tag - GLYPH_GAP - box * 0.5)
		var at := hub + Vector2(0, -rg).rotated(wedge_angle)
		# kept inside the wedge's shown box (at big text the band above the screen's foot is shallow)
		at = at.clamp(Vector2.ONE * box * 0.5, size - Vector2.ONE * box * 0.5) if size.x > box and size.y > box else at
		return Rect2(at, Vector2.ONE * box)
	return Rect2(r.get_center(), r.size * 0.5)


func _place_glyph() -> void:
	if glyph == null:
		return
	var spot := glyph_spot()
	glyph.box_px = spot.size.x
	glyph.size = glyph.custom_minimum_size
	glyph.position = spot.position - glyph.size * 0.5
	glyph.modulate = Color(Palette.NO_TINT, 0.45 if (disabled or sold_stub) else 1.0)


## The atlas glyph for a shop object: a Firmware's or a Daemon's own, a slice type's.
static func glyph_of(kind: String, id: StringName, slice_type: int = -1) -> StringName:
	var t := GlyphIcon.table()
	if t == null:
		return &""
	match kind:
		"firmware":
			return t.glyph_for(StringName("firmware_" + String(id)))
		"daemons":
			var g := t.glyph_for(StringName("daemon_" + String(id)))
			return g if g != &"" else t.glyph_for(id)
		"slices":
			return t.glyph_for(GlyphTableData.key_for_slice_type(slice_type))
	return &""


## The object's art size at this text size (game px).
func _art_size(name: String) -> Vector2:
	var t := MainframeArt.tex(name)
	return t.get_size() * MainframeArt.SCALE * obj_scale() if t != null else Vector2(CHIP_W, CHIP_W) * obj_scale()


## Where the object's art is drawn (local).
func object_rect() -> Rect2:
	match shelf:
		Shelf.FIRMWARE, Shelf.DAEMON:
			var sz := _art_size("chip_" + String(art_id) if shelf == Shelf.FIRMWARE else "daemon_" + String(art_id))
			return Rect2(Vector2((size.x - sz.x) * 0.5, 0.0), sz)
		Shelf.BIN:
			var tape := _tape_rect()
			var foot := (buy_button.size.y + BuyButton.EDGE * text_scale + GLYPH_GAP * text_scale) if buy_button != null else 0.0
			var room := Rect2(Vector2(0, tape.end.y + GLYPH_GAP), Vector2(size.x, maxf(10.0, size.y - tape.end.y - GLYPH_GAP - foot)))
			var t := MainframeArt.tex("bin_shut")
			var art := t.get_size() if t != null else Vector2(336, 338)
			var k := minf(room.size.x / art.x, room.size.y / art.y)
			return Rect2(room.position + (room.size - art * k) * Vector2(0.5, 1.0), art * k)
	return Rect2(Vector2.ZERO, size)


## The words and the tag fit under the object: the item grows to hold them.
func _fit_to_words() -> void:
	if buy_button == null or not (shelf == Shelf.FIRMWARE or shelf == Shelf.DAEMON):
		return
	var need: float = float(_caption_layout(_caption_top())["end"]) + GLYPH_GAP * text_scale + buy_button.size.y + BuyButton.EDGE * text_scale
	# the object stops growing at OBJECT_MAX_SCALE, its tag's price never shrinks below the text size
	var wide := buy_button.full_width() + BuyButton.EDGE * 2.0 * text_scale
	if custom_minimum_size.y < need or custom_minimum_size.x < wide:
		custom_minimum_size = Vector2(maxf(custom_minimum_size.x, wide), maxf(custom_minimum_size.y, need))
		buy_button.refit()


func _notification(what: int) -> void:
	if what == NOTIFICATION_CHILD_ORDER_CHANGED and buy_button != null and not buy_button.resized.is_connected(_fit_to_words):
		buy_button.resized.connect(_fit_to_words)
		_fit_to_words.call_deferred()


## Makes this a `p_shelf` item named `p_art` (its art), sized at text scale `ts`.
func on_shelf(p_shelf: int, ts: float, p_art: StringName = &"") -> ShopItem:
	shelf = p_shelf
	text_scale = ts
	if p_art != &"":
		art_id = p_art
	match shelf:
		Shelf.FIRMWARE, Shelf.DAEMON:
			look = Look.CHIP
			var art := object_rect().size
			custom_minimum_size = Vector2(maxf(art.x * 1.45, CHIP_W * 1.5 * obj_scale()), art.y + _words_h(ts))
		Shelf.SLICE:
			look = Look.SLICE_TILE
		Shelf.BIN:
			look = Look.CARD_TILE
			custom_minimum_size = Vector2(150, 190) * obj_scale() + Vector2(0, BuyButton.BUY_HEIGHT * (ts - obj_scale()) + NAME_PX * 1.4 * ts)
	return self


## The drawn object's scale at this text size.
func obj_scale() -> float:
	return minf(text_scale, OBJECT_MAX_SCALE)


## The height the words under an object and its tag take at text scale `ts` (px).
static func _words_h(ts: float) -> float:
	return (NAME_PX + SMALL_PX) * 1.5 * ts + BuyButton.BUY_HEIGHT * ts + 12.0 * ts


## A wedge of the stock wheel: hub at local `p_hub`, from `r_in` to `r_out`.
func as_wedge(p_hub: Vector2, r_out: float, r_in: float) -> ShopItem:
	hub = p_hub
	radius_out = r_out
	radius_in = r_in
	set_meta(BuyButton.TAG_AT_TOP, true)
	return self


func _has_point(point: Vector2) -> bool:
	if shelf != Shelf.SLICE:
		return Rect2(Vector2.ZERO, size).has_point(point)
	var d := (point - hub).rotated(-wedge_angle)
	var a := absf(atan2(d.x, -d.y))
	return (a <= WEDGE_HALF and d.length() >= radius_in and d.length() <= radius_out) or (buy_button != null and buy_button.get_rect().has_point(point))


func _draw() -> void:
	if shelf == Shelf.CARD:
		super._draw()
		return
	match shelf:
		Shelf.FIRMWARE, Shelf.DAEMON:
			_draw_object()
		Shelf.SLICE:
			_draw_wedge()
		Shelf.BIN:
			_draw_bin()
	if sold_stub:
		_draw_sold()


func _hot() -> bool:
	return _lifted and not disabled and not sold_stub


func _ink() -> Color:
	return Palette.TEXT_LO if (disabled or sold_stub) else Palette.TEXT_HI


## A dimmed object out of reach or sold (the art at reduced value; the tag says why).
func _shade() -> Color:
	return Color(Palette.TEXT_HI, 1.0).darkened(0.45) if (disabled or sold_stub) else Palette.NO_TINT


func _draw_object() -> void:
	var r := object_rect()
	var name := art_name()
	if _hot():
		draw_rect(r.grow(4), Color(Palette.CELL_ACID, 0.25), false, 6.0)
		draw_rect(r.grow(2), Palette.CELL_ACID, false, 2.0)
	var t := MainframeArt.tex(name)
	if t != null:
		draw_texture_rect(t, r, false, _shade())
		if shelf == Shelf.FIRMWARE:
			# the foam lip over the pins (shop_v5: the chip is pushed into the foam)
			var lip := MainframeArt.tex("foam_lip")
			if lip != null:
				var lw := r.size.x * 0.86
				var lh := lip.get_size().y * MainframeArt.SCALE * obj_scale()
				draw_texture_rect(lip, Rect2(Vector2(r.get_center().x - lw * 0.5, r.position.y + r.size.y * CHIP_PIN_LINE - lh * 0.5), Vector2(lw, lh)), false)
	elif glyph == null:
		StatIcon.draw(self, r.get_center(), r.size.x * 0.3, StatIcon.FIRMWARE if shelf == Shelf.FIRMWARE else StatIcon.DAEMON, _ink())
	_caption(_caption_top())


## The name on label-maker tape and the small line under an object, from `y` (returns the y under).
func _caption(y: float) -> float:
	var c := _caption_layout(y)
	var tape: Rect2 = c["tape"]
	draw_rect(tape, Palette.LABEL_TAPE)
	draw_rect(Rect2(tape.position + Vector2(0, 2), Vector2(tape.size.x, 1.5)), Color(Palette.TEXT_HI, 0.12))
	var f := Palette.display()
	var tr0: Rect2 = c["title"]
	var fs := int(c["fs"])
	draw_string(f, Vector2(0, tr0.position.y + f.get_ascent(fs)) + Vector2(1, 1), card_title.to_upper(), HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, Palette.INK)
	draw_string(f, Vector2(0, tr0.position.y + f.get_ascent(fs)), card_title.to_upper(), HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, _ink())
	if kind_line != "":
		var kr: Rect2 = c["kind"]
		var m := Palette.mono()
		var ms := int(c["ms"])
		draw_string_outline(m, Vector2(0, kr.position.y + m.get_ascent(ms)), kind_line, HORIZONTAL_ALIGNMENT_CENTER, size.x, ms, 3, Palette.INK)
		draw_string(m, Vector2(0, kr.position.y + m.get_ascent(ms)), kind_line, HORIZONTAL_ALIGNMENT_CENTER, size.x, ms, Color(RARITY_COLOURS[clampi(rarity, 0, 3)], 0.95 if not disabled else 0.5))
	return float(c["end"])


## The words under an object from `y`: the name on its tape in Anton and the kind line in mono,
## each shrunk to the item's width (rects as drawn, their sizes, and the y under them).
func _caption_layout(y: float) -> Dictionary:
	var s := text_scale
	var f := Palette.display()
	var fs := roundi(NAME_PX * s)
	var title := card_title.to_upper()
	while fs > FIT_MIN_TEXT and f.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > size.x - TAPE_PAD.x * 2.0 * s:
		fs -= 1
	var tw := minf(size.x - 2.0, f.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	var tape := Rect2((size.x - tw) * 0.5 - TAPE_PAD.x * s, y, tw + TAPE_PAD.x * 2.0 * s, f.get_height(fs) + TAPE_PAD.y * 2.0 * s)
	tape.position.x = maxf(0.0, tape.position.x)
	tape.size.x = minf(size.x, tape.size.x)
	var out := {"fs": fs, "tape": tape, "title": Rect2((size.x - tw) * 0.5, y + TAPE_PAD.y * s, tw, f.get_height(fs)), "ms": 0}
	y = tape.end.y + 2.0 * s
	if kind_line != "":
		var m := Palette.mono()
		var ms := roundi(SMALL_PX * s)
		while ms > FIT_MIN_TEXT and m.get_string_size(kind_line, HORIZONTAL_ALIGNMENT_LEFT, -1, ms).x > size.x - 2.0:
			ms -= 1
		var kw := minf(size.x - 2.0, m.get_string_size(kind_line, HORIZONTAL_ALIGNMENT_LEFT, -1, ms).x)
		out["ms"] = ms
		out["kind"] = Rect2((size.x - kw) * 0.5, y, kw, m.get_height(ms))
		y += m.get_height(ms)
	out["end"] = y
	return out


## Where the words start under this shelf's object (local y).
func _caption_top() -> float:
	return object_rect().end.y + GLYPH_GAP


## The parts as drawn (tests: words, the object and the tag never overlap). Cards keep ZineCard's;
## an object's whole text is its tip and the info strip, so it has no description rows.
func tile_parts() -> Dictionary:
	if shelf == Shelf.CARD:
		return super.tile_parts()
	var names: Array[Rect2] = []
	var icon := Rect2()
	match shelf:
		Shelf.FIRMWARE, Shelf.DAEMON:
			var c := _caption_layout(_caption_top())
			names.append(c["tape"])
			if c.has("kind"):
				names.append(c["kind"])
			icon = object_rect()
		Shelf.SLICE:
			var g := glyph_spot()
			icon = Rect2(g.position - g.size * 0.5, g.size)
		Shelf.BIN:
			names.append(_tape_rect())
			icon = object_rect()
	var out := {"k": 1.0, "centre": icon.get_center(), "fs": roundi(NAME_PX * text_scale), "dfs": roundi(CHIP_TEXT_SIZE * text_scale),
		"rows": 0, "lines": PackedStringArray([card_title.to_upper()]), "desc_lines": PackedStringArray(), "icon": icon, "names": names,
		"desc": [] as Array[Rect2]}
	if buy_button != null:
		out["buy"] = Rect2(buy_button.position, buy_button.size)
	return out


## The bin's label-maker tape (RECYCLE BIN; the concept's own tape in English) at its top (local).
func _tape_rect() -> Rect2:
	var t := MainframeArt.dymo("RECYCLE BIN") if card_title == TranslationServer.translate("RECYCLE BIN") else null
	if t != null:
		var k := minf(1.0, size.x / (t.get_size().x * MainframeArt.SCALE * text_scale))
		var sz := t.get_size() * MainframeArt.SCALE * text_scale * k
		return Rect2((size.x - sz.x) * 0.5, 0.0, sz.x, sz.y)
	var f := Palette.display()
	var fs := roundi(NAME_PX * 1.2 * text_scale)
	var word := card_title.to_upper()
	while fs > FIT_MIN_TEXT and f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > size.x - 12.0:
		fs -= 1
	var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 12.0
	return Rect2((size.x - w) * 0.5, 0.0, w, f.get_height(fs) + 4.0)


func _draw_bin() -> void:
	var tape := _tape_rect()
	var dy := MainframeArt.dymo("RECYCLE BIN") if card_title == TranslationServer.translate("RECYCLE BIN") else null
	if dy != null:
		draw_texture_rect(dy, tape, false)
	else:
		draw_rect(tape, Palette.LABEL_TAPE)
		var f := Palette.display()
		var fs := roundi(NAME_PX * 1.2 * text_scale)
		while fs > FIT_MIN_TEXT and f.get_string_size(card_title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > size.x - 12.0:
			fs -= 1
		draw_string(f, Vector2(tape.position.x, tape.position.y + 2.0 + f.get_ascent(fs)), card_title.to_upper(), HORIZONTAL_ALIGNMENT_CENTER, tape.size.x, fs, Palette.TEXT_HI)
	var r := object_rect()
	var name := art_name()
	var t := MainframeArt.tex(name)
	if t != null:
		# the open bin's lid rises above the shut one's box (same anchor: the bin's foot)
		var k := r.size.x / MainframeArt.tex("bin_shut").get_size().x
		var at := r.position + MainframeArt.anchor("bin_shut") * k
		draw_texture_rect(t, Rect2(at - MainframeArt.anchor(name) * k, t.get_size() * k), false, _shade())
	if _hot():
		draw_rect(r.grow(2), Color(Palette.CELL_ACID, 0.6), false, 2.0)


## The wedge's outline (annular sector about `hub`, `grow` px out).
func wedge_points(grow: float = 0.0) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var steps := 10
	for i in steps + 1:
		var a := wedge_angle - WEDGE_HALF + 2.0 * WEDGE_HALF * i / steps
		pts.append(hub + Vector2(sin(a), -cos(a)) * (radius_out + grow))
	for i in steps + 1:
		var a := wedge_angle + WEDGE_HALF - 2.0 * WEDGE_HALF * i / steps
		pts.append(hub + Vector2(sin(a), -cos(a)) * (radius_in - grow))
	return pts


## Draws wedge art `name` about the hub `c` at angle `a`, the concept wheel's radius mapped to
## `r_out` (the wedge's rim band ends a little past it).
static func draw_wedge_art(ci: CanvasItem, name: String, c: Vector2, a: float, r_out: float, modulate: Color = Palette.NO_TINT) -> bool:
	var t := MainframeArt.tex(name)
	if t == null:
		return false
	var k := r_out / float(MainframeArt.meta().get("wedge_radius", 470))
	ci.draw_set_transform(c, a, Vector2(k, k))
	ci.draw_texture_rect(t, Rect2(-MainframeArt.anchor(name), t.get_size()), false, modulate)
	ci.draw_set_transform(Vector2.ZERO)
	return true


func _draw_wedge() -> void:
	var live := not disabled and not sold_stub
	if not draw_wedge_art(self, art_name(), hub, 0.0, radius_out, _shade()):
		draw_colored_polygon(wedge_points(), Palette.CHIP_EPOXY)
	# for sale: the yellow arc on the rim (shop_layout); focus: the acid edge
	var rim := PackedVector2Array()
	for i in 13:
		var a := wedge_angle - WEDGE_HALF + 2.0 * WEDGE_HALF * i / 12.0
		rim.append(hub + Vector2(sin(a), -cos(a)) * (radius_out + 4.0))
	draw_polyline(rim, Palette.STICKER_SAFE if live else Palette.CARTRIDGE_EDGE, 5.0 if live else 2.0, true)
	if _hot():
		var edge := wedge_points(4.0)
		edge.append(edge[0])
		draw_polyline(edge, Palette.CELL_ACID, 3.0, true)


func _draw_sold() -> void:
	var fs := roundi(SOLD_FONT * text_scale)
	var c := size * 0.5 if shelf != Shelf.SLICE else hub + Vector2(0, -(radius_in + radius_out) * 0.5).rotated(wedge_angle)
	draw_set_transform(c, SOLD_TILT, Vector2.ONE)
	var word := tr(SOLD_WORD)
	var w := Palette.display().get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Rect2(Vector2(-w * 0.5 - 6.0, -fs * 0.7), Vector2(w + 12.0, fs * 1.3))
	draw_rect(box, Palette.KRAFT_RED, false, 3.0)
	draw_string(Palette.display(), Vector2(-w * 0.5, fs * 0.36), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.KRAFT_RED)
	draw_set_transform(Vector2.ZERO)


## The rarity in words (a key, translated where drawn).
static func rarity_word(r: int) -> String:
	return RARITY_WORDS[clampi(r, 0, RARITY_WORDS.size() - 1)]
