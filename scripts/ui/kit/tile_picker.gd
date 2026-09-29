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
	var s := Settings.text_scale
	return Vector2(TILE_W, TILE_H) * s


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
	var name_px := UiTheme.font_px(UiTheme.LABEL)
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
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
		var w := r.end.x - PAD - x
		var name_base := r.position.y + PAD + f.get_ascent(name_px)
		draw_string(f, Vector2(x, name_base), String(t.get("name", "")), HORIZONTAL_ALIGNMENT_LEFT, w, name_px, ink)
		var meta := String(t.get("unlock", "")) if is_locked(i) else String(t.get("meta", ""))
		if meta != "":
			draw_string(f, Vector2(r.position.x + PAD, r.end.y - PAD - f.get_descent(meta_px)), meta, HORIZONTAL_ALIGNMENT_LEFT,
				r.size.x - PAD * 2.0, meta_px, Palette.TEXT_MID)
		if is_locked(i):
			StatIcon.draw(self, Vector2(r.end.x - PAD - ICON_R * s * 0.7, r.position.y + PAD + ICON_R * s * 0.7), ICON_R * s * 0.7, StatIcon.LOCK, Palette.TEXT_MID)
		KitState.draw_frame(self, r, st if st != KitState.DISABLED or not is_locked(i) else KitState.IDLE)
