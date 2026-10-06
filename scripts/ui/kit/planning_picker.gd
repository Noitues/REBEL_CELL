class_name PlanningPicker
extends TilePicker
## Parity NEWC-01 (designer 2026-10-05): the new campaign's pickers, ported from art-m13-final
## scripts/ui/kit/planning_picker.gd (art pass W8b, `PlanningPicker`) and reworked in the v2
## kit: TilePicker's terminal tiles (states, keys, pad, locked tiles refused) with a swatch on
## each tile's left:
## - a corporation (`"corp": id`): its hue stripe and its crest (ART_BIBLE v2 §2.4: crane-A,
##   helix, EYE, ringed planet, FIST; the concept's own crests, `assets/wheel/glyphs_interim/
##   crest_<corp>.png`, as the Site markers wear them) on night glass, tinted in its hue, so
##   the five read apart by shape as well as colour (§5.1). `"redacted": true` hides a corp
##   that must stay a secret while locked (REBEL_CELL: no spoiler) behind a grey `?`;
## - an operative class (`"class": id`): the class's v2 bust (§4.12, PortraitBust: the
##   pre-rendered cel bust, rookie 0, eyes open) in a square with its class-accent rim;
## - anything else: the tile's StatIcon (`"icon"`).
## Locked tiles grey their swatch (stripe and crest in DISABLED, the bust dimmed). View only:
## `value` / `tile_chosen` say what was picked; the screen decides what it means.

## The swatch's width at text scale 1.0 (px) and the scale it stops growing at (the words
## need the room).
const SWATCH_W := 48.0
const SWATCH_GROW_MAX := 1.3
## The corp stripe's width at 1.0 (px) and the crest's share of the swatch block's width.
const STRIPE_W := 6.0
const CREST_SHARE := 0.78
## The portrait's rim (px) and the dim over a locked one.
const RIM := 2.0
const LOCKED_DIM := 0.6
## A locked bust's grey (DISABLED lightened by this share, so the face still reads).
const LOCKED_LIGHTEN := 0.3
## The concept's crests (round 15 / 18 recipes, `tools/art/bake_wheel_glyphs.py`): white
## masks tinted at draw time.
const CREST_DIR := "res://assets/wheel/glyphs_interim/crest_%s.png"
## The redacted corp's mark.
const REDACTED_MARK := "?"

## The swatch width at 1.0 for this picker (px; a crew picker shows bigger portraits).
var swatch_base: float = SWATCH_W
static var _crests: Dictionary = {}


func _init(p_tiles: Array[Dictionary] = [], p_columns: int = 0, p_tile_size: Vector2 = Vector2(176, 64), p_swatch: float = SWATCH_W) -> void:
	swatch_base = p_swatch
	super(p_tiles, p_columns, p_tile_size)
	# B5 (review section f, round 44 `new_campaign.png`): the chosen tile is the cyan edge and its SELECTED tab
	# (with the lime brackets on the pad's focus), never a solid fill.
	fill_selected = false


## B5 (review section c / f: "The corp tiles may show each corp's crest on a small holo chip (intel on the
## target)"): each corp tile's crest sits on the kit's decrypted HOLO material (DecryptedHoloPanel: its corp tint,
## scanlines, slow bands and RGB-split edge; no seal, no stamp, no scrim on a chip this small), by tile index.
var _chips: Dictionary = {}
## The crest's share of the chip and its glow (alpha, and how much bigger the glow copy is).
const CHIP_CREST := 0.68
const CHIP_GLOW_ALPHA := 0.45
const CHIP_GLOW_GROW := 1.25


## Tile `i`'s holo chip (made the first time it is drawn), placed over `box`.
func _chip(i: int, corp: StringName, box: Rect2) -> DecryptedHoloPanel:
	var chip: DecryptedHoloPanel = _chips.get(i)
	if chip == null or not is_instance_valid(chip):
		chip = DecryptedHoloPanel.new()
		chip.name = "HoloChip%d" % i
		chip.scrim = false
		chip.backing = false
		chip.seal = false
		chip.corp_color = Palette.corp_color(corp)
		chip.corporation = corp
		chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
		chip.stamp_slot.visible = false
		var crest_c := Control.new()
		crest_c.name = "Crest"
		crest_c.mouse_filter = Control.MOUSE_FILTER_IGNORE
		chip.content.add_child(crest_c)
		crest_c.set_anchors_preset(Control.PRESET_FULL_RECT)
		crest_c.draw.connect(_draw_chip_crest.bind(crest_c, corp))
		add_child(chip)
		_chips[i] = chip
	if chip.position != box.position or chip.size != box.size:
		chip.position = box.position
		chip.size = box.size
	return chip


func _draw_chip_crest(c: Control, corp: StringName) -> void:
	var tex := crest(corp)
	var tint := Palette.corp_color(corp)
	var side := minf(c.size.x, c.size.y) * CHIP_CREST
	var box := Rect2((c.size - Vector2(side, side)) * 0.5, Vector2(side, side))
	if tex == null:
		StatIcon.draw(c, c.size * 0.5, side * 0.5, StatIcon.MAP, DecryptedHoloPanel.ink(tint))
		return
	c.draw_texture_rect(tex, box.grow(side * (CHIP_GLOW_GROW - 1.0) * 0.5), false, Color(tint, CHIP_GLOW_ALPHA))
	c.draw_texture_rect(tex, box, false, DecryptedHoloPanel.ink(tint))


## Corporation `corp_id`'s crest mask (white), loaded once; null when it has none.
static func crest(corp_id: StringName) -> Texture2D:
	if not _crests.has(corp_id):
		var path := CREST_DIR % String(corp_id)
		_crests[corp_id] = load(path) as Texture2D if ResourceLoader.exists(path) else null
	return _crests[corp_id]


## Lets the cached crests go (exit).
static func release_crests() -> void:
	_crests.clear()


func swatch_width(i: int) -> float:
	var t: Dictionary = tiles[i]
	if t.has("corp") or t.has("class"):
		return swatch_base * minf(Settings.text_scale, SWATCH_GROW_MAX)
	return super(i)


func _draw_swatch(i: int, sw: Rect2, st: StringName, chosen: bool, locked: bool) -> void:
	var t: Dictionary = tiles[i]
	var s := Settings.text_scale
	if t.has("corp"):
		var corp := StringName(t["corp"])
		var redacted := bool(t.get("redacted", false))
		var hue := Palette.DISABLED if locked or redacted else Palette.corp_color(corp)
		var block := Rect2(sw.position, sw.size)
		var side := minf(block.size.x, block.size.y) * CREST_SHARE
		var box := Rect2(block.get_center() - Vector2(side, side) * 0.5, Vector2(side, side))
		if not (locked or redacted):
			# B5: an open corporation's crest on its holo chip (the intel the Cell holds on the target).
			var sq := minf(block.size.x, block.size.y)
			_chip(i, corp, Rect2(block.position + Vector2(0.0, (block.size.y - sq) * 0.5), Vector2(sq, sq))).visible = true
			return
		if _chips.has(i) and is_instance_valid(_chips[i]):
			(_chips[i] as Control).visible = false
		draw_rect(block, Palette.NIGHT_SKY)
		if redacted:
			var f := Palette.display()
			var px := roundi(side)
			var w := f.get_string_size(REDACTED_MARK, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
			draw_string(f, Vector2(block.get_center().x - w * 0.5, block.get_center().y + (f.get_ascent(px) - f.get_descent(px)) * 0.5), REDACTED_MARK, HORIZONTAL_ALIGNMENT_LEFT, -1, px, hue)
			return
		var tex := crest(corp)
		if tex != null:
			draw_texture_rect(tex, box, false, hue)
		else:
			StatIcon.draw(self, block.get_center(), side * 0.5, StatIcon.MAP, hue)
	elif t.has("class"):
		var cls := StringName(t["class"])
		var side := minf(sw.size.x, sw.size.y)
		var photo := Rect2(sw.position + Vector2(0.0, (sw.size.y - side) * 0.5), Vector2(side, side))
		draw_rect(photo, Palette.NIGHT_SKY)
		var tex := PortraitBust.texture(cls, 0, 0) as AtlasTexture
		var inner := photo.grow(-RIM)
		if tex != null:
			if locked:
				draw_texture_rect_region(tex.atlas, inner, PortraitBust.square_region(tex.region), Palette.DISABLED.lightened(LOCKED_LIGHTEN))
			else:
				draw_texture_rect_region(tex.atlas, inner, PortraitBust.square_region(tex.region))
		else:
			PortraitArt.draw(self, inner, PortraitArt.operative_subject(cls))
		if locked:
			draw_rect(inner, Color(Palette.NIGHT_SKY, LOCKED_DIM))
		draw_rect(photo.grow(-RIM * 0.5), Palette.DISABLED if locked else (Palette.GLYPH_INK if chosen else Palette.class_accent(cls)), false, RIM)
	else:
		super(i, sw, st, chosen, locked)
