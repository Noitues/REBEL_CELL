class_name TilePicker
extends Range
## ART_BIBLE §6.5 picker: a row (or a grid of `columns`) of tiles, each an icon, a name and a
## meta line, never an OS-style dropdown (replaces OptionButton: corporations, home server,
## Modem sockets, ...). Locked tiles show greyed with a lock and their unlock condition, and
## choosing one is refused (HARM flash, no-entry mark; `refused(index)`). One focus stop:
## the arrow keys / D-pad move a cursor between tiles (at the edge focus moves on to the
## next control), accept or a click chooses. `value` is the chosen tile's index (Range;
## `value_changed` fires) and `tile_chosen` names it. The six §6 states apply to the tile
## under the pointer or cursor, and to the whole picker when disabled or forced. GLASS.
## View only.

## A tile was chosen (not locked).
signal tile_chosen(index: int)
## A locked tile was chosen, or anything while disabled.
signal refused(index: int)

## Tile size at text scale 1.0 (px), the gap between tiles, the padding inside, the icon's
## radius.
const TILE_W := 144.0
const TILE_H := 76.0
const TILE_GAP := UiTheme.SP_S
const PAD := UiTheme.SP_S
const ICON_R := 10.0
## The chosen tile's edge (px).
const CHOSEN_EDGE := 2.0
## Art pass WF (§4.3 rule 3): a name wraps at word boundaries, never mid-word, on up to
## NAME_LINES lines; when a word or the lines don't fit it steps down through NAME_STEPS to
## the caption floor, and past that the tile grows (taller for lines, wider for a word).
const NAME_STEPS: Array[int] = [UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]
const NAME_LINES := 2
## The lock badge's radius as a share of the icon's.
const LOCK_SHARE := 0.7

## Tiles: {name: String, meta: String, icon: StringName, locked: bool, unlock: String} (all
## words translated by the caller).
var tiles: Array[Dictionary] = []
## Tiles per row (0 = all in one row).
var columns: int = 0:
	set(v):
		columns = maxi(0, v)
		update_minimum_size()
## Unavailable: nothing can be chosen.
var disabled: bool = false:
	set(v):
		disabled = v
		queue_redraw()
## The tile the keys / pad point at.
var cursor: int = 0
var _hover: int = -1
## The tile last refused (drawn in the refused state while KitState says so).
var _refused_tile: int = -1


func _init(p_tiles: Array[Dictionary] = [], p_columns: int = 0) -> void:
	min_value = 0
	step = 1
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_STOP
	columns = p_columns
	KitState.track(self)
	mouse_exited.connect(func() -> void: _hover = -1; queue_redraw())
	value_changed.connect(func(_v: float) -> void: queue_redraw())
	set_tiles(p_tiles)


## Replaces the tiles (the chosen index is kept when still valid).
func set_tiles(p_tiles: Array[Dictionary]) -> void:
	tiles = p_tiles
	max_value = maxf(0.0, tiles.size() - 1)
	cursor = clampi(cursor, 0, maxi(0, tiles.size() - 1))
	update_minimum_size()
	queue_redraw()


## The chosen tile's index.
func selected() -> int:
	return int(value)


## True when tile `i` is locked.
func is_locked(i: int) -> bool:
	return i >= 0 and i < tiles.size() and bool(tiles[i].get("locked", false))


## Chooses tile `i`: refused when locked or disabled, else it becomes the value.
func choose(i: int) -> void:
	if i < 0 or i >= tiles.size():
		return
	cursor = i
	if disabled or is_locked(i):
		_refused_tile = i
		KitState.refuse(self)
		refused.emit(i)
		return
	value = i
	tile_chosen.emit(i)
	queue_redraw()


func _cols() -> int:
	return tiles.size() if columns <= 0 else mini(columns, maxi(1, tiles.size()))


func _tile_size() -> Vector2:
	_layout()
	return _size_cache


## Art pass WF: tile `i`'s name as drawn: {px: the type size, lines: the words per line
## (whole words only), line_h: px per line}.
func name_layout(i: int) -> Dictionary:
	_layout()
	return _names[i] if i >= 0 and i < _names.size() else {}


## Art pass WF: tile `i`'s meta (or unlock) line as drawn: {px, lines, line_h}; it wraps at
## word boundaries at caption, the floor.
func meta_layout(i: int) -> Dictionary:
	_layout()
	return _metas[i] if i >= 0 and i < _metas.size() else {}


## The width tile names wrap to in a tile of width `tile_w` (px): the tile less its
## padding and the icon's room.
func name_width(tile_w: float, with_icon: bool = true) -> float:
	var s := Settings.text_scale
	return tile_w - PAD * 2.0 - ((ICON_R * s * 2.0 + PAD) if with_icon else 0.0)


## `text` wrapped to `width` at `px`, at word boundaries only (a word wider than `width`
## sits alone on its line; the caller checks for it).
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


## The widest line of `lines` at `px` (px).
static func widest(lines: PackedStringArray, font: Font, px: int) -> float:
	var w := 0.0
	for l in lines:
		w = maxf(w, font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return w


var _layout_key: Array = []
var _size_cache := Vector2.ZERO
var _names: Array[Dictionary] = []
var _metas: Array[Dictionary] = []


## Lays every tile's words out (cached per tiles and text scale): each name takes the largest
## NAME_STEPS size whose whole words fit NAME_LINES lines; the tiles (all one size, so the
## grid stays even) grow to hold the tallest words and the widest word.
func _layout() -> void:
	var s := Settings.text_scale
	var key := [s, tiles.hash()]
	if key == _layout_key:
		return
	_layout_key = key
	var f := Palette.mono()
	var tile := Vector2(TILE_W, TILE_H) * s
	_names.clear()
	_metas.clear()
	var need_w := 0.0
	var need_h := 0.0
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	var meta_lh := meta_px * UiTheme.line_height(UiTheme.CAPTION)
	for t in tiles:
		var has_icon: bool = t.get("icon", &"") != &""
		var w := name_width(tile.x, has_icon)
		if bool(t.get("locked", false)):
			w -= ICON_R * s * LOCK_SHARE * 2.0  # the lock badge's corner
		var words := String(t.get("name", ""))
		var chosen := {}
		for step in NAME_STEPS:
			var px := UiTheme.font_px(step)
			var lines := wrap_words(words, f, px, w)
			chosen = {"px": px, "lines": lines, "line_h": px * UiTheme.line_height(step)}
			if lines.size() <= NAME_LINES and widest(lines, f, px) <= w:
				break
		_names.append(chosen)
		var lines_n: PackedStringArray = chosen["lines"]
		need_w = maxf(need_w, widest(lines_n, f, int(chosen["px"])) + tile.x - w)
		var meta := String(t.get("unlock", "")) if bool(t.get("locked", false)) else String(t.get("meta", ""))
		var meta_w := tile.x - PAD * 2.0
		var meta_lines := wrap_words(meta, f, meta_px, meta_w) if meta != "" else PackedStringArray()
		_metas.append({"px": meta_px, "lines": meta_lines, "line_h": meta_lh})
		need_w = maxf(need_w, widest(meta_lines, f, meta_px) + PAD * 2.0)
		var name_h := maxf(lines_n.size() * float(chosen["line_h"]), ICON_R * s * 2.0 if has_icon else 0.0)
		need_h = maxf(need_h, PAD * 2.0 + name_h + meta_lines.size() * meta_lh)
	_size_cache = Vector2(ceilf(maxf(tile.x, need_w)), ceilf(maxf(tile.y, need_h)))


## Tile `i`'s rect (local, at rest).
func tile_rect(i: int) -> Rect2:
	var cols := maxi(1, _cols())
	var ts := _tile_size()
	return Rect2(Vector2((i % cols) * (ts.x + TILE_GAP), (i / cols) * (ts.y + TILE_GAP)), ts)


## The tile under local point `p` (-1 when none).
func tile_at(p: Vector2) -> int:
	for i in tiles.size():
		if tile_rect(i).has_point(p):
			return i
	return -1


func _get_minimum_size() -> Vector2:
	if tiles.is_empty():
		return Vector2.ZERO
	var cols := maxi(1, _cols())
	var rows := ceili(tiles.size() / float(cols))
	var ts := _tile_size()
	return Vector2(cols * ts.x + (cols - 1) * TILE_GAP, rows * ts.y + (rows - 1) * TILE_GAP)


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
		var cols := maxi(1, _cols())
		var to := cursor
		if event.is_action_pressed(&"ui_left", true) and cursor % cols > 0:
			to = cursor - 1
		elif event.is_action_pressed(&"ui_right", true) and cursor % cols < cols - 1 and cursor + 1 < tiles.size():
			to = cursor + 1
		elif event.is_action_pressed(&"ui_up", true) and cursor - cols >= 0:
			to = cursor - cols
		elif event.is_action_pressed(&"ui_down", true) and cursor + cols < tiles.size():
			to = cursor + cols
		if to != cursor:
			cursor = to
			queue_redraw()
			accept_event()
		# At an edge the move isn't taken: focus goes on to the neighbouring control.


## The state tile `i` is drawn in (§6): the picker's forced / disabled state for all, the
## refused tile while refused, pressed / hover under the pointer, focus at the cursor.
func tile_state(i: int) -> StringName:
	var st := KitState.of(self)
	if has_meta(KitState.META_FORCED):
		return st
	if st == KitState.DISABLED:
		return st
	if st == KitState.REFUSED:
		return KitState.REFUSED if i == _refused_tile else KitState.IDLE
	if is_locked(i):
		return KitState.DISABLED
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


func _draw() -> void:
	var f := Palette.mono()
	var s := Settings.text_scale
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
		var icon: StringName = t.get("icon", &"")
		var x := r.position.x + PAD
		if icon != &"":
			var ic := Vector2(x + ICON_R * s, r.position.y + PAD + ICON_R * s)
			StatIcon.draw(self, ic, ICON_R * s, icon, ink if st == KitState.DISABLED else StatIcon.color_of(icon))
			x += ICON_R * s * 2.0 + PAD
		# Art pass WF (§4.3 rule 3): whole words on up to NAME_LINES lines (see _layout).
		var nl := name_layout(i)
		var name_px: int = nl["px"]
		var base := r.position.y + PAD + f.get_ascent(name_px)
		for line in nl["lines"] as PackedStringArray:
			draw_string(f, Vector2(x, base), line, HORIZONTAL_ALIGNMENT_LEFT, -1, name_px, ink)
			base += float(nl["line_h"])
		var ml := meta_layout(i)
		var meta_lines: PackedStringArray = ml["lines"]
		var meta_px: int = ml["px"]
		var mbase := r.end.y - PAD - f.get_descent(meta_px) - (meta_lines.size() - 1) * float(ml["line_h"])
		for line in meta_lines:
			draw_string(f, Vector2(r.position.x + PAD, mbase), line, HORIZONTAL_ALIGNMENT_LEFT, -1, meta_px, Palette.TEXT_MID)
			mbase += float(ml["line_h"])
		if is_locked(i):
			StatIcon.draw(self, Vector2(r.end.x - PAD - ICON_R * s * LOCK_SHARE, r.position.y + PAD + ICON_R * s * LOCK_SHARE), ICON_R * s * LOCK_SHARE, StatIcon.LOCK, Palette.TEXT_MID)
		KitState.draw_frame(self, r, st if st != KitState.DISABLED or not is_locked(i) else KitState.IDLE)
