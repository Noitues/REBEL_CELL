class_name CardFace
extends RefCounted
## The card face on the art pass's own sticker (M14 asset parity; ART_BIBLE v2 §3.18, the hand of
## `combat_typical_v4` and `card_play_v2_storyboard`, the loot of `reward_screen_v2`, the CARDS of
## `shop_v5`). S-CARDFACE (designer group ruling 2026-10-05): the one face of every card view (hand,
## loot, Mainframe, deck viewer, card detail, loadout, ghosts and flights). The art layer is the round 31 C-C sticker card,
## `assets/cards/face_<kind>_<rarity>.png`, exported by `tools/art/export_card_faces.py` from
## `r31lib.card_face` + `card_sticker` on art-concepts-r43 (dark faceted body and art panel in the kind
## colour, the kind band, rarity pips, the yellow cost dot, the white die-cut vinyl with its rim and gloss,
## the holo die-cut on Rare). Over it the view draws only what is live, where the generator puts it: the
## RAM cost, the title, the art glyph and the pictograms (1C's atlas glyphs), the kind word, the rules text,
## the key hint and the states (short RAM, refusal pulse, focus halo, disabled). Drawing only.

## The kinds of the C-C card (the generator's KIND_COL): spin / nudge / flip cards are WHEEL, harm HACK,
## the rest SYSTEM.
const KINDS := ["wheel", "hack", "system"]
const KIND_WORDS := {"wheel": "WHEEL", "hack": "HACK", "system": "SYSTEM"} # TR
## S-CARDFACE: a loot offer that is not a card wears the SYSTEM face; its band names what it is.
const OFFER_WORDS := {"firmware": "FIRMWARE", "daemon": "DAEMON"} # TR
## The offer's art inside the art panel (share of the panel, aspect kept).
const OFFER_ART := 0.9
const RARITY_NAMES := ["common", "uncommon", "rare", "boss"]
const FACE_PATH := "res://assets/cards/face_%s_%s.png"
## The exported image (px) and the face inside it (`manifest.json`: face_rect, at the generator's 2x).
const IMAGE := Vector2(504, 644)
const FACE_AT := Vector2(42, 42)
const FACE := Vector2(420, 560)
## The generator's layout, in px of its 210 x 280 face (`r31lib.card_face`).
const UNIT := Vector2(210, 280)
const COST_AT := Vector2(31, 29)
const COST_R := 21.0
const COST_PX := 30.0
const TITLE_AT := Vector2(127, 30)
const TITLE_W := 126.0
const TITLE_PX := 23.0
const ART := Rect2(14, 52, 182, 102)
const ART_GLYPH := 0.74
const BAND := Rect2(14, 154, 182, 24)
const BAND_PX := 15.0
const PIC_AT := Vector2(22, 186)
const PIC_PX := 30.0
const VALUE_PX := 34.0
const TAG_PX := 20.0
const TEXT_TOP := 228.0
const TEXT_BOTTOM := 266.0
const TEXT_PX := 13.0
const TEXT_LINE := 1.3
const TEXT_W := 170.0
const KEY_PX := 11.0
## The key hint's chip: its inset from the art panel's corner, its side padding (px at scale 1) and its
## height (share of the lettering); the chip's ink alpha.
const KEY_INSET := 2.0
const KEY_PAD := 2.0
const KEY_H := 1.25
const KEY_CHIP_ALPHA := 0.7
## The shadow under the sticker (the asset itself, darkened) and its alpha.
const SHADOW_ALPHA := 0.45

static var _faces: Dictionary = {}


## The kind of a card from its pictograms (what it does first).
static func kind_of(card: ZineCard) -> String:
	var kind := String(card.pictos[0].get("kind", "")) if not card.pictos.is_empty() else ""
	var type := int(card.pictos[0].get("type", -1)) if not card.pictos.is_empty() else -1
	if kind in ["spin", "nudge", "flip", "respin"]:
		return "wheel"
	if type in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW, RC.SliceType.INFECT] or kind in ["damage", "status"]:
		return "hack"
	return "system"


## The art layer for `kind` and `rarity` (RC.Rarity).
static func face(kind: String, rarity: int) -> Texture2D:
	var key := "%s_%s" % [kind, RARITY_NAMES[clampi(rarity, 0, RARITY_NAMES.size() - 1)]]
	if not _faces.has(key):
		_faces[key] = load(FACE_PATH % [kind, RARITY_NAMES[clampi(rarity, 0, RARITY_NAMES.size() - 1)]]) as Texture2D
	return _faces[key]


## The atlas glyph key of a pictogram (1C's glyph table), or &"".
static func glyph_of(p: Dictionary) -> StringName:
	match String(p.get("kind", "")):
		"spin":
			return GlyphTableData.key_for_effect(RC.EffectType.SPIN) if int(p.get("amount", 0)) >= 0 else &"effect_spin_ccw"
		"slice":
			var st := int(p.get("status", RC.Status.NONE))
			return GlyphTableData.key_for_status(st) if st != RC.Status.NONE else GlyphTableData.key_for_slice_type(int(p["type"]))
		"nudge":
			return &"effect_nudge_inner" if bool(p.get("inner", false)) else GlyphTableData.key_for_effect(RC.EffectType.NUDGE)
	if p.has("effect"):
		return GlyphTableData.key_for_effect(int(p["effect"]))
	return &""


## Where the face's own px `at` lands on the card (local).
static func at_px(card: ZineCard, at: Vector2) -> Vector2:
	return at * card.size / UNIT


## The font px of a generator size `px` on this card.
static func font_px(card: ZineCard, px: float) -> int:
	return maxi(1, roundi(px * card.size.y / UNIT.y))


## S-CARDFACE: when the generator's own text block (TEXT_TOP, TEXT_W, TEXT_LINE) does not hold the
## whole rules text, it closes up under the pictogram row (PIC_GAP, TEXT_LINE_TIGHT) on the face's full
## inner width (TEXT_W_WIDE) down to TEXT_FOOT, then takes the pictogram row's room too (PIC_AT.y; the art
## glyph still says what the card does). A line that reaches the rarity pips (PIPS_TOP, from PIPS_LEFT
## rightwards, face px of the 3-pip Rare) keeps to the pips' left, centred (PIPS_LEFT about the middle).
const TEXT_W_WIDE := 186.0
const TEXT_LINE_TIGHT := 1.15
const PIC_GAP := 2.0
const TEXT_FOOT := 272.0
const PIPS_TOP := 254.0
const PIPS_LEFT := 150.0
## A rules line's ink (share of its lettering): its baseline under the row's top, and its whole height
## (capitals to descenders; the type's own line metrics carry a gap the face has no room for).
const TEXT_BASE := 0.9
## The rules text's ink outline (px) and its alpha.
const TEXT_OUTLINE := 2
const TEXT_OUTLINE_ALPHA := 0.7
const TEXT_INK := 1.15


## The rules text as drawn: {"fs", "line", "rows", "lines", "w", "widths" (per row), "top" (local px),
## "pictos" (the pictogram row shows)}. Never under the card's body floor on screen (a card growing under
## the pointer letters at floor / hover_scale). With `fit_whole` each layout steps down to the floor
## before the next is tried: the generator's block, the block closed up under the pictograms, then the
## pictogram row's room (at rest only where the card lets its pictograms give way; always while it grows
## under the pointer). What still does not fit ends in an ellipsis (the whole text is the tooltip, the
## inspect and the grown card).
static func text_fit(card: ZineCard) -> Dictionary:
	var ky := card.size.y / UNIT.y
	var kx := card.size.x / UNIT.x
	var grown := card.hover_scale > 1.0
	var grown_px := card.grown_floor if card.grown_floor > 0 else card.body_floor
	var floor_px := maxi(1, ceili(grown_px / card.hover_scale)) if grown else card.body_floor
	var gen := font_px(card, TEXT_PX)
	var foot := card.size.y - card.buy_room() if card.buy_button != null else INF
	# [top, width, line share, bottom, pictograms shown] in face px
	var tries: Array = [[TEXT_TOP, TEXT_W, TEXT_LINE, TEXT_BOTTOM, true]]
	if card.fit_whole:
		tries.append([PIC_AT.y + PIC_PX + PIC_GAP, TEXT_W_WIDE, TEXT_LINE_TIGHT, TEXT_FOOT, true])
		if card.pictos_give_way or grown:
			tries.append([PIC_AT.y, TEXT_W_WIDE, TEXT_LINE_TIGHT, TEXT_FOOT, false])
	# what is drawn when nothing shows the whole text: the layout with the most rows (the later, roomier one on a tie), at the floor
	var fallback := {}
	for t: Array in tries:
		var fs := maxi(floor_px, gen)
		while true:
			var fit := _fit_at(card, fs, float(t[0]) * ky, float(t[1]) * kx, fs * float(t[2]), minf(float(t[3]) * ky, foot), bool(t[4]))
			if (fit["lines"] as PackedStringArray).size() <= int(fit["rows"]):
				return fit
			if fallback.is_empty() or int(fit["rows"]) >= int(fallback["rows"]):
				fallback = fit
			if not card.fit_whole or fs <= floor_px:
				break
			fs -= 1
	return fallback


static func _fit_at(card: ZineCard, fs: int, top: float, w: float, line: float, bottom: float, pictos: bool) -> Dictionary:
	# the last row needs only its lettering, not a whole line step
	var h := fs * TEXT_INK
	var rows := maxi(1, 1 + int((bottom - top - h) / line))
	var pips_y := PIPS_TOP * card.size.y / UNIT.y
	var narrow := minf(w, (PIPS_LEFT - UNIT.x * 0.5) * 2.0 * card.size.x / UNIT.x)
	var widths := PackedFloat32Array()
	for i in rows:
		widths.append(narrow if top + i * line + h > pips_y else w)
	var lines := wrap_body(card.description, widths, fs)
	return {"fs": fs, "line": line, "rows": rows, "lines": lines, "w": w, "widths": widths, "top": top, "pictos": pictos}


## Word-wraps `text` in the face's body type (Plex Sans Condensed) at `font_size`: line i to `widths[i]`
## px (the last width for any line past them).
static func wrap_body(text: String, widths: PackedFloat32Array, font_size: int) -> PackedStringArray:
	var out := PackedStringArray()
	var font := Palette.body()
	var line := ""
	for word in text.split(" ", false):
		var trial := word if line == "" else line + " " + word
		var width := widths[mini(out.size(), widths.size() - 1)]
		if line != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > width:
			out.append(line)
			line = word
		else:
			line = trial
	if line != "":
		out.append(line)
	return out


## The face's parts as drawn (local rects; tests: none overlaps another, all inside the card): "body"
## (a rect per rules line shown), "pictos" (the pictogram row, when it shows), "key" (the key hint).
static func parts(card: ZineCard) -> Dictionary:
	var fit := text_fit(card)
	var body := Palette.body()
	var fs: int = fit["fs"]
	var rows: Array[Rect2] = []
	var lines: PackedStringArray = fit["lines"]
	for i in mini(lines.size(), int(fit["rows"])):
		var w := minf((fit["widths"] as PackedFloat32Array)[i], body.get_string_size(lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
		rows.append(Rect2((card.size.x - w) * 0.5, float(fit["top"]) + i * float(fit["line"]), w, fs * TEXT_INK))
	var out := {"body": rows, "fs": fs}
	if bool(fit["pictos"]) and not card.pictos.is_empty():
		var pic := PIC_PX * card.size.y / UNIT.y
		out["pictos"] = Rect2(at_px(card, PIC_AT), Vector2(card.size.x - at_px(card, PIC_AT).x * 2.0, pic))
	var key := key_rect(card)
	if key.has_area():
		out["key"] = key
	return out


## The key hint's chip (local; empty without a key): on the art panel's top right corner, clear of the
## rules text and the pictograms (it sat on the text's last line at the face's foot).
static func key_rect(card: ZineCard) -> Rect2:
	var key := key_text(card)
	if key == "":
		return Rect2()
	var fs := maxi(1, roundi(KEY_PX * card.text_scale))
	var w := Palette.marker().get_string_size(key, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + KEY_PAD * 2.0 * card.text_scale
	var inset := KEY_INSET * card.text_scale
	return Rect2(Vector2(at_px(card, ART.end).x - w - inset, at_px(card, ART.position).y + inset), Vector2(w, fs * KEY_H))


## The key hint's words ("" without one): the pad button on the focused card, else the hotkey.
static func key_text(card: ZineCard) -> String:
	var key := card.pad_hint if card.pad_hint != "" and card.has_focus() else card.hotkey
	return "[%s]" % key if key != "" else ""


## Draws the card's face (the caller has set the hover / lift transform).
static func draw(card: ZineCard) -> void:
	var s := card.text_scale
	var size := card.size
	var k := size / FACE
	var dest := Rect2(-FACE_AT * k, IMAGE * k)
	var tex := face(kind_of(card), card.card_rarity)
	if card._lifted:
		card.draw_style_box(card._cc_style(Color(Palette.CELL_ACID, 0.5), ZineCard.CC_EDGE * s + 4.0, ZineCard.CC_CORNER * s + 4.0), Rect2(Vector2.ZERO, size))
	if tex != null:
		card.draw_texture_rect(tex, Rect2(dest.position + ZineCard.CC_SHADOW * s, dest.size), false, Color(Palette.SHADOW, SHADOW_ALPHA))
		card.draw_texture_rect(tex, dest, false)
	# The peel curl at the foot corner (it lifts on hover: a moving fold the still can't hold).
	var edge := ZineCard.CC_EDGE * s
	var curl := (ZineCard.CC_CURL_HOVER if card._lifted else ZineCard.CC_CURL) * s
	var corner := Vector2(size.x + edge, size.y + edge)
	card.draw_colored_polygon(PackedVector2Array([corner - Vector2(curl, 0), corner - Vector2(0, curl), corner - Vector2(curl, curl) * 0.92]), Palette.PAPER_ALT)
	card.draw_colored_polygon(PackedVector2Array([corner - Vector2(curl, 0), corner, corner - Vector2(0, curl)]), Palette.NIGHT_SKY)
	var display := Palette.display()
	# The RAM cost on the generator's yellow dot (grey when short, pulsing red on a refusal).
	var cc := at_px(card, COST_AT)
	var cr := COST_R * size.x / UNIT.x
	if card.cost >= 0:
		if card.short_ram or card.cost_alarm > 0.0:
			var fill := Palette.DISABLED if card.short_ram else Palette.STICKER_SAFE
			fill = fill.lerp(ZineCard.REFUSED_COLOR, card.cost_alarm)
			card.draw_circle(cc, cr, fill)
			card.draw_arc(cc, cr, 0.0, TAU, 24, Palette.INK, maxf(1.0, cr * 0.14), true)
		if card.cost_alarm > 0.0:
			card.draw_arc(cc, cr + 2.0 + cr * ZineCard.COST_PULSE_GROW * card.cost_alarm, 0, TAU, 24, Color(ZineCard.REFUSED_COLOR, card.cost_alarm), 3.0, true)
		var cfs := font_px(card, COST_PX * (0.8 if card.cost >= 10 else 1.0))
		_centred(card, display, cc, str(card.cost), cfs, Palette.INK)
	# The title, centred right of the cost dot, shrinking to fit.
	var title := card.card_title.to_upper()
	var tw := TITLE_W * size.x / UNIT.x
	var tfs := font_px(card, TITLE_PX)
	while tfs > 9 and display.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, tfs).x > tw:
		tfs -= 1
	_centred(card, display, at_px(card, TITLE_AT), title, tfs, Palette.PAPER)
	# The art: the first pictogram's glyph, big in the panel.
	var art := Rect2(at_px(card, ART.position), ART.size * size / UNIT)
	var offer := MainframeArt.tex(card.offer_art) if card.offer_art != "" else null
	if offer != null:
		var ok := minf(art.size.x / offer.get_size().x, art.size.y / offer.get_size().y) * OFFER_ART
		card.draw_texture_rect(offer, Rect2(art.get_center() - offer.get_size() * ok * 0.5, offer.get_size() * ok), false)
	elif not card.pictos.is_empty():
		WheelGlyphs.draw(card, glyph_of(card.pictos[0]), art.get_center(), art.size.y * ART_GLYPH, Palette.TEXT_HI)
	# The kind word on the band (an offer's own word).
	var band := Rect2(at_px(card, BAND.position), BAND.size * size / UNIT)
	var band_word: String = OFFER_WORDS.get(card.offer_kind, KIND_WORDS[kind_of(card)])
	_centred(card, Palette.body_medium(), band.get_center(), card.tr(band_word), font_px(card, BAND_PX), Palette.INK)
	var fit := text_fit(card)
	# The pictograms: glyph + value, left to right (unless the rules text took their row).
	var x := at_px(card, PIC_AT).x if bool(fit["pictos"]) else size.x
	var pic := PIC_PX * size.y / UNIT.y
	var py := at_px(card, PIC_AT).y + pic * 0.5
	var vfs := font_px(card, VALUE_PX)
	var gfs := font_px(card, TAG_PX)
	for p in (card.pictos if bool(fit["pictos"]) else []):
		var g := glyph_of(p)
		if g != &"" and WheelGlyphs.draw(card, g, Vector2(x + pic * 0.5, py), pic, Palette.TEXT_HI):
			x += pic + 2.0 * s
		var label := _label(p)
		if label != "":
			var fs := vfs if String(p.get("kind", "")) != "tag" else gfs
			var lw := display.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			if x + lw > size.x - 4.0:
				break
			card.draw_string_outline(display, Vector2(x, py + fs * 0.36), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(2, roundi(fs * 0.12)), Palette.INK)
			card.draw_string(display, Vector2(x, py + fs * 0.36), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.PAPER)
			x += lw + 6.0 * s
		if x > size.x - pic:
			break
	# The rules text under it, centred; what does not fit ends in an ellipsis.
	var lines: PackedStringArray = fit["lines"]
	var rows: int = fit["rows"]
	var body := Palette.body()
	var bfs: int = fit["fs"]
	for i in mini(lines.size(), rows):
		var t := lines[i]
		if i == rows - 1 and lines.size() > rows:
			t = t.substr(0, maxi(0, t.length() - 1)) + "…"
		var y := float(fit["top"]) + i * float(fit["line"]) + bfs * TEXT_BASE
		var rw: float = (fit["widths"] as PackedFloat32Array)[i]
		# S-CARDFACE b: an ink outline keeps small words legible where the face's gloss streak crosses them
		card.draw_string_outline(body, Vector2((size.x - rw) * 0.5, y), t, HORIZONTAL_ALIGNMENT_CENTER, rw, bfs, TEXT_OUTLINE, Color(Palette.INK, TEXT_OUTLINE_ALPHA))
		card.draw_string(body, Vector2((size.x - rw) * 0.5, y), t, HORIZONTAL_ALIGNMENT_CENTER, rw, bfs, Palette.TEXT_HI)
	# The key hint on a dark chip at the art panel's corner.
	var kr := key_rect(card)
	if kr.has_area():
		var kfs := maxi(1, roundi(KEY_PX * s))
		card.draw_rect(kr, Color(Palette.INK, KEY_CHIP_ALPHA))
		card.draw_string(Palette.marker(), Vector2(kr.position.x + KEY_PAD * s, kr.position.y + (kr.size.y + Palette.marker().get_ascent(kfs) - Palette.marker().get_descent(kfs)) * 0.5),
			key_text(card), HORIZONTAL_ALIGNMENT_LEFT, -1, kfs, Palette.TEXT_HI)
	if card.disabled:
		card.draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.SHADOW, 0.5))
	if card.short_ram and card.cost >= 0:
		# Can't afford: the dot greys and a NEED tag says what is missing (under the dot).
		var nfs := roundi(ZineCard.NEED_FONT * s)
		var word := card.tr(ZineCard.NEED_WORD) % card.cost
		var nw := display.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, nfs).x
		var tag := Rect2(Vector2(cc.x - cr, cc.y + cr + 3.0), Vector2(nw + ZineCard.NEED_PAD * 2.0, nfs * 1.3))
		card.draw_rect(tag.grow(2.0), Palette.PAPER)
		card.draw_rect(tag, Palette.HARM)
		card.draw_string(display, tag.position + Vector2(ZineCard.NEED_PAD, nfs * 1.0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, nfs, Palette.PAPER)


## A pictogram's value as drawn next to its glyph.
static func _label(p: Dictionary) -> String:
	match String(p.get("kind", "")):
		"spin":
			return str(absi(int(p["amount"])))
		"respin":
			return "?"
		"nudge":
			return "×%d" % int(p["amount"])
		"slice":
			return str(int(p["amount"])) if int(p["amount"]) > 0 else ""
		"tag":
			return String(p["text"])
	return ""


static func _centred(ci: CanvasItem, font: Font, at: Vector2, text: String, fs: int, col: Color) -> void:
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	ci.draw_string(font, Vector2(at.x - w * 0.5, at.y + (font.get_ascent(fs) - font.get_descent(fs)) * 0.5), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
