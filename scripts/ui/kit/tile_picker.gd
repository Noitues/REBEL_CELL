class_name TilePicker
extends Range
## Parity NEWC-01 / NEWC-04 (designer 2026-10-05): a picker that shows every choice at once as
## a grid of terminal tiles, never an OS-style dropdown or popup list. Ported from
## art-m13-final scripts/ui/kit/tile_picker.gd (art pass W2 / WF, `TilePicker`) and reworked
## in the v2 kit (ART_BIBLE v2 §2.10, §4.13; round 31 `settings_menu.jpg` tiles): each tile
## wears the concept's tile plate (`assets/ui/menus/kit/tile_idle` / `tile_selected`, as
## MenuChip and CrtTiles), its name in terminal CAPS and a meta line in the caption step.
## The chosen tile is the cyan-filled plate with ink words and a cyan frame round it (§2.10:
## selected is a cyan fill, never lime); focus is the lime brackets round the tile under the
## cursor; a locked tile is hatched grey with a lock and its unlock words, and choosing it is
## refused (KitState's HARM flash and no-entry mark, `refused(index)`).
## One focus stop: the arrow keys / D-pad move a cursor between tiles (at an edge the move is
## not taken, so focus goes on to the neighbouring control), accept or a click chooses.
## `value` is the chosen tile's index (Range; `value_changed` fires) and `tile_chosen` names
## it. `columns` 0 lays as many tiles a row as the picker's width holds. View only.

## A tile was chosen (not locked).
signal tile_chosen(index: int)
## A locked tile was chosen, or any while disabled.
signal refused(index: int)

## The gap between tiles (px): clear of the neighbour's focus brackets.
const TILE_GAP := UiTheme.SP_M
## Padding inside a tile (px).
const PAD := UiTheme.SP_S
## Room round the tiles inside the picker for the focus brackets (StyleBoxBrackets: offset,
## stroke and keyline outside the tile).
const OUTSET := StyleBoxBrackets.OFFSET + StyleBoxBrackets.THICKNESS + StyleBoxBrackets.KEYLINE
## A tile's icon radius at text scale 1.0 (a tile with an `icon` and no swatch).
const ICON_R := 10.0
## The name's type steps (largest first) and the most lines it may take: whole words only,
## never cut (§4.3); past the caption floor the tiles grow wider.
const NAME_STEPS: Array[int] = [UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]
const NAME_LINES := 2
## The meta (or unlock) line's step and the most lines it may take.
const META_STEP := UiTheme.CAPTION
const META_LINES := 2
## A tile's width grows with the text only up to this scale (its words wrap and step down
## beyond it), so a row keeps more than one tile at 2.0; its least height up to the second
## (past it the tile is as tall as its words).
const WIDTH_GROW_MAX := 1.6
const HEIGHT_GROW_MAX := 1.3
## The selected frame: its stroke and its gap outside the tile (px; inside the brackets).
const SELECTED_FRAME := 2.0
const SELECTED_GAP := 3.0
## The locked hatch: spacing (px) and its alpha.
const HATCH := 7.0
const HATCH_ALPHA := 0.35
## The lock badge's radius at text scale 1.0 (KitState's badge).
const LOCK_R := KitState.BADGE_R
## The concept's tile plates (tools/art/bake_menus_r33.py, settings.py tiles): nine-patches
## drawn at two thirds (board -> game), as MenuChip.
const PLATE_IDLE := "res://assets/ui/menus/kit/tile_idle.png"
const PLATE_SELECTED := "res://assets/ui/menus/kit/tile_selected.png"
const PLATE_MARGIN := 10
const PLATE_SCALE := 2.0 / 3.0

## Tiles: {name, meta, locked, unlock, tip, icon} (+ a subclass's own keys); every word
## already translated by the caller.
var tiles: Array[Dictionary] = []
## B5 (integration review section f, round 44 `new_campaign.png`): false draws the chosen tile as the idle plate with a
## 3 px cyan edge and a SELECTED word tab on its top edge (never a solid fill: it shouted); true keeps the cyan
## filled plate (the Options' tiles, round 31).
var fill_selected: bool = true
## B5: the chosen edge's stroke at 1080p (round 44: 3 px) and the SELECTED tab's words (a key) and step.
const EDGE_SELECTED_1080 := 3.0
const SELECTED_WORD := "SELECTED" # TR
const SELECTED_STEP := UiTheme.CAPTION
## A tile's size at text scale 1.0 (px; it grows to hold its words).
var tile_size: Vector2 = Vector2(176, 64)
## Tiles a row (0 = as many as the width holds).
var columns: int = 0:
	set(v):
		columns = maxi(0, v)
		_relayout()
## Unavailable: nothing can be chosen.
var disabled: bool = false:
	set(v):
		disabled = v
		queue_redraw()
## The tile the keys / pad point at.
var cursor: int = 0
var _hover: int = -1
## The tile last refused (drawn refused while KitState says so).
var _refused_tile: int = -1
var _laid_w: float = -1.0
static var _plates: Dictionary = {}


func _init(p_tiles: Array[Dictionary] = [], p_columns: int = 0, p_tile_size: Vector2 = Vector2(176, 64)) -> void:
	min_value = 0
	step = 1
	tile_size = p_tile_size
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_STOP
	# The picker draws its own focus (brackets round the cursor's tile), so the pad's focus
	# scale must not grow the whole grid.
	set_meta(UiFocus.META_NO_SCALE, true)
	PaletteSkins.watch(self)
	KitState.track(self)
	columns = p_columns
	mouse_exited.connect(func() -> void: _hover = -1; queue_redraw())
	value_changed.connect(func(_v: float) -> void: queue_redraw())
	# The pad lands on the chosen tile.
	focus_entered.connect(func() -> void: cursor = selected(); queue_redraw())
	focus_exited.connect(queue_redraw)
	# Auto columns follow the width (a height change alone lays nothing out again).
	resized.connect(func() -> void:
		if not is_equal_approx(size.x, _laid_w):
			_laid_w = size.x
			_relayout())
	set_tiles(p_tiles)


func _ready() -> void:
	Settings.changed.connect(_relayout)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_relayout):
		Settings.changed.disconnect(_relayout)


## Replaces the tiles (the chosen index is kept when still valid).
func set_tiles(p_tiles: Array[Dictionary]) -> void:
	tiles = p_tiles
	max_value = maxf(0.0, tiles.size() - 1)
	cursor = clampi(cursor, 0, maxi(0, tiles.size() - 1))
	_relayout()


## The chosen tile's index.
func selected() -> int:
	return int(value)


## True when tile `i` is locked.
func is_locked(i: int) -> bool:
	return i >= 0 and i < tiles.size() and bool(tiles[i].get("locked", false))


## Chooses tile `i`: refused when it is locked or the picker is disabled, else it becomes
## the value.
func choose(i: int) -> void:
	if i < 0 or i >= tiles.size():
		return
	cursor = i
	if disabled or is_locked(i):
		_refused_tile = i
		KitState.refuse(self)
		refused.emit(i)
		queue_redraw()
		return
	value = i
	tile_chosen.emit(i)
	queue_redraw()


# --- Layout ---------------------------------------------------------------------------------

var _layout_key: Array = []
var _tile := Vector2.ZERO
var _cols := 1
var _name_px := 0
var _names: Array[PackedStringArray] = []
var _metas: Array[PackedStringArray] = []


func _relayout() -> void:
	_layout_key = []
	update_minimum_size()
	queue_redraw()


## The tile size at text scale `s` for a tile of `base` size at 1.0 (before its words grow it).
static func tile_at_scale(base: Vector2, s: float) -> Vector2:
	return Vector2(base.x * minf(s, WIDTH_GROW_MAX), base.y * minf(s, HEIGHT_GROW_MAX))


## The width of tile `i`'s left swatch (px; 0 = none). A subclass draws its own.
func swatch_width(i: int) -> float:
	return ICON_R * Settings.text_scale * 2.0 if String(tiles[i].get("icon", "")) != "" else 0.0


## The room a tile's name has in a tile `tile_w` wide (px): the tile less its padding and
## the swatch.
func name_room(i: int, tile_w: float) -> float:
	var sw := swatch_width(i)
	return tile_w - PAD * 2.0 - (sw + PAD if sw > 0.0 else 0.0)


## The room a tile's meta line has (px): beside the swatch; a locked tile with no swatch
## keeps its foot's right end for the lock (with a swatch the lock hangs on its corner).
func meta_room(i: int, tile_w: float) -> float:
	var room := name_room(i, tile_w)
	if is_locked(i) and swatch_width(i) <= 0.0:
		room -= LOCK_R * Settings.text_scale * 2.0 + PAD
	return room


## Tile `i`'s swatch rect inside tile rect `r` (zero size when it has none).
func swatch_rect(i: int, r: Rect2) -> Rect2:
	var sw := swatch_width(i)
	if sw <= 0.0:
		return Rect2(r.position + Vector2(PAD, PAD), Vector2.ZERO)
	return Rect2(r.position + Vector2(PAD, PAD), Vector2(sw, r.size.y - PAD * 2.0))


## Tile `i`'s name as shown (CAPS terminal words).
func shown_name(i: int) -> String:
	return String(tiles[i].get("name", "")).to_upper()


## Tile `i`'s second line: its unlock words while locked, else its meta.
func shown_meta(i: int) -> String:
	return String(tiles[i].get("unlock", "")) if is_locked(i) else String(tiles[i].get("meta", ""))


## `text` broken at spaces into lines no wider than `width` at `px` in `font` (a word wider
## than a line stays whole on its own line: the caller checks with `widest`).
static func wrap_words(text: String, font: Font, px: int, width: float) -> PackedStringArray:
	var lines := PackedStringArray()
	var line := ""
	for word in text.split(" ", false):
		var tried := word if line == "" else line + " " + word
		if line != "" and font.get_string_size(tried, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
			lines.append(line)
			line = word
		else:
			line = tried
	if line != "":
		lines.append(line)
	return lines


## The widest of `lines` at `px` in `font` (px).
static func widest(lines: PackedStringArray, font: Font, px: int) -> float:
	var w := 0.0
	for l in lines:
		w = maxf(w, font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return w


## Lays every tile out (cached per tiles, width and text scale): one name size for the whole
## picker (the largest step at which every name fits its lines, so the row reads as a set),
## the tiles all one size (wider for a word that does not fit at the floor, taller for the
## lines), and the columns the width holds.
func _layout() -> void:
	var s := Settings.text_scale
	var key := [s, tiles.hash(), size.x, columns]
	if key == _layout_key:
		return
	_layout_key = key
	var tile := tile_at_scale(tile_size, s)
	# The name size: the largest step every name fits at (whole words, NAME_LINES lines).
	_name_px = UiTheme.font_px(NAME_STEPS[NAME_STEPS.size() - 1])
	for st in NAME_STEPS:
		var px := UiTheme.font_px(st)
		var f := Chrome.caps_font(st)
		var fits := true
		for i in tiles.size():
			var room := name_room(i, tile.x)
			var lines := wrap_words(shown_name(i), f, px, room)
			if lines.size() > NAME_LINES or widest(lines, f, px) > room:
				fits = false
				break
		if fits:
			_name_px = px
			break
	var name_step := _name_step()
	var nf := Chrome.caps_font(name_step)
	var mf := Palette.mono()
	var meta_px := UiTheme.font_px(META_STEP)
	# A word too wide at the floor widens every tile (never cut, never mid-word).
	var need_w := tile.x
	for i in tiles.size():
		var lines := wrap_words(shown_name(i), nf, _name_px, name_room(i, tile.x))
		need_w = maxf(need_w, tile.x + widest(lines, nf, _name_px) - name_room(i, tile.x))
	tile.x = ceilf(need_w)
	_names.clear()
	_metas.clear()
	var name_lh := nf.get_height(_name_px)
	var meta_lh := mf.get_height(meta_px)
	var need_h := tile.y
	for i in tiles.size():
		var lines := wrap_words(shown_name(i), nf, _name_px, name_room(i, tile.x))
		_names.append(lines)
		var meta := shown_meta(i)
		var mlines := wrap_words(meta, mf, meta_px, meta_room(i, tile.x)) if meta != "" else PackedStringArray()
		_metas.append(mlines)
		need_h = maxf(need_h, PAD * 2.0 + lines.size() * name_lh + mlines.size() * meta_lh + (PAD * 0.5 if not mlines.is_empty() else 0.0))
	tile.y = ceilf(need_h)
	_tile = tile
	var n := maxi(1, tiles.size())
	if columns > 0:
		_cols = mini(columns, n)
	elif size.x > 0.0:
		_cols = clampi(floori((size.x - OUTSET * 2.0 + TILE_GAP) / (tile.x + TILE_GAP)), 1, n)
	else:
		_cols = 1


## The type step the shared name size came from.
func _name_step() -> int:
	for st in NAME_STEPS:
		if UiTheme.font_px(st) == _name_px:
			return st
	return NAME_STEPS[NAME_STEPS.size() - 1]


## The face every tile's name is drawn in (terminal CAPS at the shared size's step).
func name_font() -> Font:
	_layout()
	return Chrome.caps_font(_name_step())


## The shared name size (px) every tile's name is drawn at.
func name_px() -> int:
	_layout()
	return _name_px


## Tile `i`'s name lines as drawn (whole words).
func name_lines(i: int) -> PackedStringArray:
	_layout()
	return _names[i] if i >= 0 and i < _names.size() else PackedStringArray()


## Tile `i`'s meta (or unlock) lines as drawn.
func meta_lines(i: int) -> PackedStringArray:
	_layout()
	return _metas[i] if i >= 0 and i < _metas.size() else PackedStringArray()


## Tiles a row now.
func column_count() -> int:
	_layout()
	return _cols


## Every tile's size now (px).
func tile_extent() -> Vector2:
	_layout()
	return _tile


## Tile `i`'s rect (local, at rest).
func tile_rect(i: int) -> Rect2:
	_layout()
	var c := maxi(1, _cols)
	return Rect2(Vector2(OUTSET + (i % c) * (_tile.x + TILE_GAP), OUTSET + (i / c) * (_tile.y + TILE_GAP)), _tile)


## The tile under local point `p` (-1 when none).
func tile_at(p: Vector2) -> int:
	for i in tiles.size():
		if tile_rect(i).has_point(p):
			return i
	return -1


func _get_minimum_size() -> Vector2:
	if tiles.is_empty():
		return Vector2.ZERO
	_layout()
	var c := maxi(1, _cols)
	var rows := ceili(tiles.size() / float(c))
	# Auto columns ask for one tile's width (the row wraps to what the parent gives).
	var w_cols := c if columns > 0 else 1
	return Vector2(w_cols * _tile.x + (w_cols - 1) * TILE_GAP, rows * _tile.y + (rows - 1) * TILE_GAP) + Vector2.ONE * OUTSET * 2.0


func _get_tooltip(at_position: Vector2) -> String:
	var i := tile_at(at_position)
	if i < 0:
		return ""
	return UiTip.fold(String(tiles[i].get("tip", "")))


# --- Input ------------------------------------------------------------------------------------

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var h := tile_at((event as InputEventMouseMotion).position)
		if h != _hover:
			_hover = h
			queue_redraw()
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		var mb := event as InputEventMouseButton
		KitState.set_pressed(self, mb.pressed)
		if mb.pressed:
			choose(tile_at(mb.position))
		accept_event()
	elif event.is_action_pressed(&"ui_accept"):
		choose(cursor)
		accept_event()
	else:
		var to := move_target(cursor, event)
		if to != cursor:
			cursor = to
			queue_redraw()
			accept_event()
		# At an edge the move is not taken: focus goes on to the neighbouring control.


## Where the cursor goes from tile `from` for `event` (the same tile at an edge).
func move_target(from: int, event: InputEvent) -> int:
	var c := maxi(1, column_count())
	if event.is_action_pressed(&"ui_left", true) and from % c > 0:
		return from - 1
	if event.is_action_pressed(&"ui_right", true) and from % c < c - 1 and from + 1 < tiles.size():
		return from + 1
	if event.is_action_pressed(&"ui_up", true) and from - c >= 0:
		return from - c
	if event.is_action_pressed(&"ui_down", true) and from + c < tiles.size():
		return from + c
	return from


# --- Drawing ----------------------------------------------------------------------------------

## The state tile `i` is drawn in (§6): the picker's forced or disabled state for all, the
## refused tile while refused, pressed / hover under the pointer, focus at the cursor (a
## locked tile shows focus too; its lock and hatch come from `is_locked`).
func tile_state(i: int) -> StringName:
	var st := KitState.of(self)
	if has_meta(KitState.META_FORCED):
		return st
	if st == KitState.DISABLED:
		return st
	if st == KitState.REFUSED:
		return KitState.REFUSED if i == _refused_tile else (KitState.FOCUS if has_focus() and i == cursor else KitState.IDLE)
	if st == KitState.PRESSED and i == _hover:
		return KitState.PRESSED
	if has_focus() and i == cursor:
		return KitState.FOCUS
	if i == _hover:
		return KitState.HOVER
	return KitState.IDLE


## The picker's own state (KitState).
func state() -> StringName:
	return KitState.of(self)


## True when tile `i` is drawn as the chosen one.
func is_chosen(i: int) -> bool:
	return i == selected() and not is_locked(i)


static func _plate(path: String) -> StyleBoxTexture:
	if not _plates.has(path):
		var sb := StyleBoxTexture.new()
		sb.texture = load(path) as Texture2D
		sb.texture_margin_left = PLATE_MARGIN
		sb.texture_margin_right = PLATE_MARGIN
		sb.texture_margin_top = PLATE_MARGIN
		sb.texture_margin_bottom = PLATE_MARGIN
		_plates[path] = sb
	return _plates[path]


## Lets the cached plates go (exit).
static func release() -> void:
	_plates.clear()


func _draw() -> void:
	_layout()
	var s := Settings.text_scale
	var nf := Chrome.caps_font(_name_step())
	var mf := Palette.mono()
	var meta_px := UiTheme.font_px(META_STEP)
	for i in tiles.size():
		var st := tile_state(i)
		var r := tile_rect(i)
		r.position.y += KitState.lift(st)
		var chosen := is_chosen(i) and st != KitState.DISABLED
		var locked := is_locked(i) or st == KitState.DISABLED
		var filled := chosen and fill_selected
		draw_set_transform(r.position, 0.0, Vector2.ONE * PLATE_SCALE)
		draw_style_box(_plate(PLATE_SELECTED if filled else PLATE_IDLE), Rect2(Vector2.ZERO, r.size / PLATE_SCALE))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		if not chosen and (st == KitState.HOVER or st == KitState.FOCUS or st == KitState.PRESSED):
			draw_rect(r, Color(KitState.edge_color(st), 0.6), false, 1.0)
		if locked:
			_hatch(r)
		var swr := swatch_rect(i, r)
		var x := r.position.x + PAD
		if swr.size.x > 0.0:
			_draw_swatch(i, swr, st, filled, locked)
			x += swr.size.x + PAD
		var ink := Palette.GLYPH_INK if filled else (Palette.TEXT_MID if locked else (Palette.TEXT_HI if chosen else KitState.label_color(st)))
		var y := r.position.y + PAD
		for line in name_lines(i):
			draw_string(nf, Vector2(x, y + nf.get_ascent(_name_px)), line, HORIZONTAL_ALIGNMENT_LEFT, -1, _name_px, ink)
			y += nf.get_height(_name_px)
		var ml := meta_lines(i)
		var my := r.end.y - PAD - ml.size() * mf.get_height(meta_px)
		for line in ml:
			draw_string(mf, Vector2(x, my + mf.get_ascent(meta_px)), line, HORIZONTAL_ALIGNMENT_LEFT, -1, meta_px, Palette.GLYPH_INK if filled else Palette.TEXT_MID)
			my += mf.get_height(meta_px)
		if is_locked(i):
			var lr := LOCK_R * s
			KitState.draw_lock_badge(self, lock_center(i, r), lr)
		if filled:
			draw_rect(r.grow(SELECTED_GAP), Palette.SELECTED, false, SELECTED_FRAME)
		elif chosen:
			_draw_selected_edge(r)
		# Focus brackets, the refused HARM outline and no-entry (the lock is drawn above).
		KitState.draw_frame(self, r, st if st != KitState.DISABLED else KitState.IDLE)


## B5 (round 44 `new_campaign.png`): the chosen tile's 3 px cyan edge (1080p) and its SELECTED word tab, a small
## cyan plate with ink words hanging on the edge's top right.
func _draw_selected_edge(r: Rect2) -> void:
	var cyan := PaletteSkins.chrome(Palette.SELECTED)
	var w := maxf(1.0, EDGE_SELECTED_1080 * get_viewport_rect().size.y / PaperLie.BOARD_H) if is_inside_tree() else EDGE_SELECTED_1080
	draw_rect(r.grow(-w * 0.5), cyan, false, w)
	var f := Chrome.caps_font(SELECTED_STEP)
	var px := Chrome.px(SELECTED_STEP)
	var word := tr(SELECTED_WORD)
	var tw := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var tab := Rect2(Vector2(r.end.x - tw - PAD * 2.0, r.position.y - f.get_height(px) * 0.5), Vector2(tw + PAD * 1.5, f.get_height(px)))
	draw_rect(tab, cyan)
	draw_string(f, Vector2(tab.position.x + PAD * 0.75, tab.position.y + f.get_ascent(px)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.GLYPH_INK)


## Where tile `i`'s lock sits in its rect `r` while locked: on its swatch's bottom right
## corner (KitState's badge hangs on a corner), or the foot's right end with no swatch.
func lock_center(i: int, r: Rect2) -> Vector2:
	var lr := LOCK_R * Settings.text_scale
	var swr := swatch_rect(i, r)
	if swr.size.x > 0.0:
		return swr.end - Vector2(lr, lr)
	return Vector2(r.end.x - PAD - lr, r.end.y - PAD - lr)


## The grey hatch over a locked tile (MenuChip's disabled hatch), clipped to `r`.
func _hatch(r: Rect2) -> void:
	var h := r.size.y
	var col := Color(Palette.DISABLED, HATCH_ALPHA)
	var x := r.position.x
	while x < r.end.x + h:
		# The line from (x, bottom) up-left to (x - h, top), clipped to the tile's sides.
		var t0 := maxf(0.0, x - r.end.x)
		var t1 := minf(h, x - r.position.x)
		if t1 > t0:
			draw_line(Vector2(x - t0, r.end.y - t0), Vector2(x - t1, r.end.y - t1), col, 1.0)
		x += HATCH


## Draws tile `i`'s swatch into `sw` (the base draws its StatIcon; a subclass its own art).
func _draw_swatch(i: int, sw: Rect2, _st: StringName, chosen: bool, locked: bool) -> void:
	var icon := StringName(tiles[i].get("icon", ""))
	if icon == &"":
		return
	var r := ICON_R * Settings.text_scale
	var col := Palette.GLYPH_INK if chosen else (Palette.DISABLED if locked else PaletteSkins.chrome(Palette.NET_CYAN))
	StatIcon.draw(self, Vector2(sw.get_center().x, sw.position.y + r), r, icon, col)
