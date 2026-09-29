class_name PlanningPicker
extends TilePicker
## The new campaign's planning-table pickers (ART_BIBLE §11 New campaign, §6.5; critique 03,
## 04): W2's TilePicker (states, keys, pad, locked tiles refused) with tiles sized for their
## words and a swatch on each tile's left:
## - a corporation dossier (`"corp": id`): its hue stripe, a block of its CorpPattern and its
##   landmark mark (`landmark_icon`: a seam for the baked landmark glyphs; StatIcon until
##   then), so the five read apart in greyscale;
## - an operative class (`"class": id`): the class's portrait, a Polaroid in small;
## - anything else: the tile's StatIcon (`"icon"`).
## A tile's name wraps at spaces to two lines and steps down the type scale before it would
## be cut (§4.3: never truncated, never mid-word); its meta line (or a locked tile's unlock)
## the same at `caption`. Locked tiles keep W2's DISABLED look, their lock and 4.5:1 words.
## View only: `value` / `tile_chosen` say what was picked; the screen decides what it means.

## The tile size at text scale 1.0 (px): wider than W2's default so a corporation's name
## fits on two lines; the swatch's width, the stripe's and the pattern block's share.
var tile_size: Vector2 = Vector2(208, 84)
const SWATCH_W := 44.0
## The swatch grows with the text only up to this scale (the words need the room).
const SWATCH_GROW_MAX := 1.3
const STRIPE_W := 6.0
const PORTRAIT_PAD := 4.0
## The name's type steps (§4.2), largest first, and the most lines it may take.
const PLAN_NAME_STEPS: Array[int] = [UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]
const PLAN_NAME_LINES := 2
## The landmark mark's radius as a share of the swatch width.
const MARK_SHARE := 0.28
## A tile's width grows with the text only up to this scale (its words wrap and step down
## beyond it), so a row keeps three dossiers at 2.0 (§5.3: 3 -> 2 -> 1 columns).
const WIDTH_GROW_MAX := 1.6


## The tile size at text scale `s` for a tile of `base` size at 1.0.
static func tile_at_scale(base: Vector2, s: float) -> Vector2:
	return Vector2(base.x * minf(s, WIDTH_GROW_MAX), base.y * s)


func _init(p_tiles: Array[Dictionary] = [], p_columns: int = 0, p_tile_size: Vector2 = Vector2(208, 84)) -> void:
	tile_size = p_tile_size
	super(p_tiles, p_columns)


func _tile_size() -> Vector2:
	return tile_at_scale(tile_size, Settings.text_scale)


## §3.6 seam: a corporation's landmark mark (the helix, the crane, the clock tower, the
## dish, the inverted hexagon). The baked landmark glyphs (W8a, assets/art/landmarks/) are
## not in yet; until then each corp shows the map pin with its CorpPattern ring round it.
static func landmark_icon(_corp_id: StringName) -> StringName:
	return StatIcon.MAP


## The corporation's baked landmark glyph (W8a, assets/art/landmarks/) at `height` px, or
## null when there is none (the StatIcon seam then).
static func landmark_texture(corp_id: StringName, height: float) -> Texture2D:
	var path := SvgArt.landmark_path(corp_id)
	return SvgArt.texture(path, height) if path != "" else null


## Tile `i`'s name as drawn: its lines and their size (px) for `width` px, never larger
## than `max_px` (0: no cap).
func plan_name_layout(i: int, width: float, max_px: int = 0) -> Array:
	var f := Palette.mono()
	var text := String(tiles[i].get("name", ""))
	var px := UiTheme.font_px(PLAN_NAME_STEPS[PLAN_NAME_STEPS.size() - 1])
	var lines := PackedStringArray([text])
	for step in PLAN_NAME_STEPS:
		px = UiTheme.font_px(step)
		if max_px > 0 and px > max_px:
			continue
		lines = _plan_wrap(text, f, px, width)
		if lines.size() <= PLAN_NAME_LINES:
			break
	return [lines, px]


## The room tile `i`'s name has (px): beside the swatch, clear of a locked tile's lock.
func plan_name_width(i: int) -> float:
	var s := Settings.text_scale
	var r := tile_rect(i)
	return r.size.x - PAD * 3.0 - SWATCH_W * minf(s, SWATCH_GROW_MAX) - (ICON_R * s * 1.4 + PAD if is_locked(i) else 0.0)


## The one name size every tile of the picker uses (px): the largest step at which each
## name fits its two lines, so the row reads as a set.
func common_name_px() -> int:
	var px := UiTheme.font_px(PLAN_NAME_STEPS[0])
	for i in tiles.size():
		px = mini(px, int(plan_name_layout(i, plan_name_width(i))[1]))
	return px


## `text` broken at spaces into lines no wider than `width` at `px` (a word wider than a
## line stays whole on its own line: the caller steps the size down).
static func _plan_wrap(text: String, f: Font, px: int, width: float) -> PackedStringArray:
	var out := PackedStringArray()
	var cur := ""
	for word in text.split(" ", false):
		var trial := word if cur == "" else cur + " " + word
		if cur != "" and f.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
			out.append(cur)
			cur = word
		else:
			cur = trial
	if cur != "":
		out.append(cur)
	for line in out:
		if f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
			return PackedStringArray(["", "", ""])  # a word too wide: never fits at this size
	return out


func _draw() -> void:
	var f := Palette.mono()
	var s := Settings.text_scale
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	var name_px := common_name_px()
	for i in tiles.size():
		var t: Dictionary = tiles[i]
		var st := tile_state(i)
		var r := tile_rect(i)
		r.position.y += KitState.lift(st)
		var chosen := i == selected() and not is_locked(i)
		KitState.draw_box(self, r, st, Palette.TERMINAL_BG_HOT if chosen and st != KitState.DISABLED else Palette.TERMINAL_BG)
		if chosen and st != KitState.DISABLED:
			draw_rect(r, Palette.CELL_PINK, false, CHOSEN_EDGE)
		var ink := KitState.label_color(st)
		var sw := Rect2(r.position + Vector2(PAD, PAD), Vector2(SWATCH_W * minf(s, SWATCH_GROW_MAX), r.size.y - PAD * 2.0))
		_draw_swatch(t, sw, st)
		var x := sw.end.x + PAD
		# The name keeps clear of a locked tile's lock in the top right corner.
		var w := plan_name_width(i)
		var lay := plan_name_layout(i, w, name_px)
		var y := r.position.y + PAD
		for line in (lay[0] as PackedStringArray):
			draw_string(f, Vector2(x, y + f.get_ascent(int(lay[1]))), line, HORIZONTAL_ALIGNMENT_LEFT, -1, int(lay[1]), ink)
			y += f.get_height(int(lay[1]))
		var meta := String(t.get("unlock", "")) if is_locked(i) else String(t.get("meta", ""))
		if meta != "":
			var mpx := meta_px
			while mpx > UiTheme.CAPTION and f.get_string_size(meta, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx).x > w:
				mpx -= 1
			draw_string(f, Vector2(x, r.end.y - PAD - f.get_descent(mpx)), meta, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx, Palette.TEXT_MID)
		if is_locked(i):
			StatIcon.draw(self, Vector2(r.end.x - PAD - ICON_R * s * 0.7, r.position.y + PAD + ICON_R * s * 0.7), ICON_R * s * 0.7, StatIcon.LOCK, Palette.TEXT_MID)
		KitState.draw_frame(self, r, st if st != KitState.DISABLED or not is_locked(i) else KitState.IDLE)


## The tile's swatch: a corp's stripe, pattern and landmark; a class portrait; or its icon.
func _draw_swatch(t: Dictionary, sw: Rect2, st: StringName) -> void:
	var s := Settings.text_scale
	var dim := st == KitState.DISABLED
	if t.has("corp"):
		var corp := StringName(t["corp"])
		var hue := Palette.corp_color(corp) if not dim else Palette.DISABLED
		draw_rect(Rect2(sw.position, Vector2(STRIPE_W * s, sw.size.y)), hue)
		var block := Rect2(sw.position + Vector2(STRIPE_W * s + PAD * 0.5, 0), Vector2(sw.size.x - STRIPE_W * s - PAD * 0.5, sw.size.y))
		draw_rect(block, Palette.NIGHT_SKY)
		CorpPattern.fill_rect(self, block, Palette.corp_pattern_id(corp), Color(hue, 0.8), s)
		var c := block.get_center()
		var mr := block.size.x * MARK_SHARE * 1.6
		draw_circle(c, mr, Palette.NIGHT_SKY)
		var tex := landmark_texture(corp, mr * 1.6)
		if tex != null:
			var sz := tex.get_size() * (mr * 1.6 / maxf(1.0, tex.get_size().y))
			draw_texture_rect(tex, Rect2(c - sz * 0.5, sz), false, hue)
		else:
			StatIcon.draw(self, c, mr * 0.8, landmark_icon(corp), hue)
	elif t.has("class"):
		var side := minf(sw.size.x, sw.size.y)
		var photo := Rect2(sw.position + Vector2(0, (sw.size.y - side) * 0.5), Vector2(side, side))
		draw_rect(photo, Palette.PAPER)
		var inner := photo.grow(-PORTRAIT_PAD * s)
		PortraitArt.draw(self, inner, PortraitArt.operative_subject(StringName(t["class"]), &"", ""))
		if dim:
			draw_rect(inner, Color(Palette.NIGHT_SKY, 0.6))
	else:
		var icon: StringName = t.get("icon", &"")
		if icon != &"":
			var r := ICON_R * s
			StatIcon.draw(self, sw.position + Vector2(sw.size.x * 0.5, r + PAD * 0.5), r, icon, KitState.label_color(st) if dim else StatIcon.color_of(icon))
