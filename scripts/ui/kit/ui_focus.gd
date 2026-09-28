class_name UiFocus
extends RefCounted
## Controller and keyboard focus (GAP_ANALYSIS P2 11): every panel gives its first usable
## button focus when it opens, so a pad-only player always has something selected and
## ui_accept / the D-pad work from the first frame. UI helper only; no game state.


## The first visible, enabled, focusable control under `root` (depth-first, tree order).
static func first_focusable(root: Node) -> Control:
	if root == null:
		return null
	for child in root.get_children():
		if child is Control:
			var c := child as Control
			if not c.is_visible_in_tree() or c.is_queued_for_deletion():
				continue
			# The effective mode: a modal (hold) switches focus off for the screen behind it.
			if c.get_focus_mode_with_override() != Control.FOCUS_NONE and not (c is BaseButton and (c as BaseButton).disabled) and (c is BaseButton or c is LineEdit or c is Range):
				return c
		if child.is_queued_for_deletion():
			continue
		var deeper := first_focusable(child)
		if deeper != null:
			return deeper
	return null


## Focuses the first usable control under `root` unless something inside it already has
## focus. Deferred, so it works right after the panel is built.
## With `only_if_lost`, it acts only when nothing usable has focus anywhere (the combat hand
## refreshes every action and must not pull focus off a button the player moved to).
static func focus_first(root: Node, only_if_lost: bool = false, fallback: Node = null) -> void:
	if root == null:
		return
	_focus_now.call_deferred(root, only_if_lost, fallback)


## Untyped on purpose: the deferred call can land after the panel was freed.
static func _focus_now(target, only_if_lost: bool = false, fallback = null) -> void:
	if target == null or not is_instance_valid(target) or not (target is Node) or not (target as Node).is_inside_tree():
		return
	var root := target as Node
	var viewport := root.get_viewport()
	var owner := viewport.gui_get_focus_owner() if viewport != null else null
	var usable := owner != null and is_instance_valid(owner) and not owner.is_queued_for_deletion() and owner.is_visible_in_tree() \
		and not (owner is BaseButton and (owner as BaseButton).disabled)
	if usable and (only_if_lost or root.is_ancestor_of(owner)):
		return
	var first := first_focusable(root)
	if first == null and fallback != null and is_instance_valid(fallback) and fallback is Node:
		first = first_focusable(fallback as Node)
	if first != null:
		first.grab_focus()


## Focus to give back when a modal closes (the pause menu restores the hand's focus).
static func owner_of(node: Node) -> Control:
	if node == null or not node.is_inside_tree():
		return null
	return node.get_viewport().gui_get_focus_owner()


## D-pad neighbours for a whole panel. The panel is read as blocks stacked top to bottom:
## a lone control is a block of one; controls in a horizontal container form one row;
## and (ANIM-R4 H1) a horizontal container whose children hold several rows each (the HQ's
## menu column beside the crew and the poster) is a block of columns: up/down walk a
## column item by item, left/right cross to the same row (clamped) of the next column, and
## a column's last item goes down to the block below (its first item up to the block
## above). Tilted stickers, SpinBoxes and long lists defeat Godot's geometric search, so
## panels link explicitly (horizontal pass 6).
static func link_layout(root: Node) -> void:
	var blocks: Array = []
	_collect_blocks(root, blocks)
	# Start clean: a relink (settings sections swap their controls) must not leave paths to
	# controls that are no longer in the tree.
	for c in _controls_of(blocks):
		c.focus_neighbor_left = NodePath()
		c.focus_neighbor_right = NodePath()
		c.focus_neighbor_top = NodePath()
		c.focus_neighbor_bottom = NodePath()
	for b in blocks.size():
		var cols: Array = blocks[b]
		for j in cols.size():
			var col: Array = cols[j]
			for r in col.size():
				var row: Array = col[r]
				for i in row.size():
					var c: Control = row[i]
					# Left / right: along the row, then across to the next column's row.
					if i > 0:
						c.focus_neighbor_left = c.get_path_to(row[i - 1])
					elif j > 0:
						var lrow: Array = _row_at(cols[j - 1], r)
						c.focus_neighbor_left = c.get_path_to(lrow[lrow.size() - 1])
					if i + 1 < row.size():
						c.focus_neighbor_right = c.get_path_to(row[i + 1])
					elif j + 1 < cols.size():
						var rrow: Array = _row_at(cols[j + 1], r)
						c.focus_neighbor_right = c.get_path_to(rrow[0])
					# Up / down: within the column, then out to the block above / below.
					if r > 0:
						var up: Array = col[r - 1]
						c.focus_neighbor_top = c.get_path_to(up[mini(i, up.size() - 1)])
					elif b > 0:
						c.focus_neighbor_top = c.get_path_to(_edge(blocks[b - 1], j if cols.size() > 1 else i, i, false, cols.size() > 1))
					if r + 1 < col.size():
						var down: Array = col[r + 1]
						c.focus_neighbor_bottom = c.get_path_to(down[mini(i, down.size() - 1)])
					elif b + 1 < blocks.size():
						c.focus_neighbor_bottom = c.get_path_to(_edge(blocks[b + 1], j if cols.size() > 1 else i, i, true, cols.size() > 1))


## Row `r` of a column, clamped to its last row.
static func _row_at(col: Array, r: int) -> Array:
	return col[mini(r, col.size() - 1)]


## The control of `block` a neighbour block reaches from position `p` (the column of a
## block of columns, else the place in the row) and place `i` in its row: the top row when
## entering from above (`top`), else the bottom row. A row takes place `p` (clamped); a
## block of columns takes column `p`, and place `i` of its row only from another block of
## columns (`from_cols`).
static func _edge(block: Array, p: int, i: int, top: bool, from_cols: bool) -> Control:
	if block.size() == 1:
		var only: Array = block[0]
		var line: Array = only[0] if top else only[only.size() - 1]
		return line[mini(p, line.size() - 1)]
	var col: Array = block[mini(p, block.size() - 1)]
	var row: Array = col[0] if top else col[col.size() - 1]
	return row[mini(i if from_cols else 0, row.size() - 1)]


## Every control in `blocks`, in order.
static func _controls_of(blocks: Array) -> Array:
	var out: Array = []
	for cols in blocks:
		for col in cols:
			for row in col:
				out.append_array(row)
	return out


static func _usable(c: Node) -> bool:
	if not (c is Control):
		return false
	var ctl := c as Control
	if not ctl.is_visible_in_tree() or ctl.is_queued_for_deletion() or ctl.get_focus_mode_with_override() == Control.FOCUS_NONE:
		return false
	if ctl is BaseButton:
		return not (ctl as BaseButton).disabled
	if ctl is Range:
		return not (ctl is SpinBox) and not (ctl is ScrollBar)  # sliders yes; scrollbars belong to their owner
	if ctl is RichTextLabel:
		return true  # a reference note made focusable (ZineNote.make_reference)
	return ctl is LineEdit and not (ctl.get_parent() is SpinBox)


## Collects `node`'s blocks (see link_layout): each block is an Array of columns, each
## column an Array of rows, each row an Array of Controls.
static func _collect_blocks(node: Node, blocks: Array) -> void:
	for child in node.get_children():
		if not (child is Control) or child.is_queued_for_deletion() or not (child as Control).is_visible_in_tree():
			continue
		if child is SpinBox:
			continue  # use the -/+ buttons beside it
		if _usable(child):
			blocks.append([[[child]]])
			continue
		if child is HBoxContainer or child is HFlowContainer:
			var block := _horizontal_block(child)
			if not block.is_empty():
				blocks.append(block)
			continue
		_collect_blocks(child, blocks)


## A horizontal container's block: one row (a control per child: the child or the first
## usable control inside it), or, when a child holds more than one row (a menu column), a
## column per child.
static func _horizontal_block(box: Node) -> Array:
	var cols: Array = []
	var tall := false
	for g in box.get_children():
		if g is SpinBox or not (g is Control) or g.is_queued_for_deletion() or not (g as Control).is_visible_in_tree():
			continue
		if _usable(g):
			cols.append([[g]])
			continue
		var inner: Array = []
		_collect_blocks(g, inner)
		var col := _as_rows(inner)
		if col.is_empty():
			continue
		tall = tall or col.size() > 1
		cols.append(col)
	if cols.is_empty():
		return []
	if tall:
		return cols
	# A plain row, as before ANIM-R4: a control per child (its first usable one).
	var row: Array = []
	for col in cols:
		row.append(col[0][0])
	return [[row]]


## `blocks` read top to bottom as rows of one column: a block of columns gives its rows
## side by side (row k of every column together).
static func _as_rows(blocks: Array) -> Array:
	var rows: Array = []
	for cols in blocks:
		var depth := 0
		for col in cols:
			depth = maxi(depth, (col as Array).size())
		for k in depth:
			var row: Array = []
			for col in cols:
				if k < (col as Array).size():
					row.append_array(col[k])
			rows.append(row)
	return rows

static func _first_usable(node: Node) -> Control:
	for child in node.get_children():
		if child is SpinBox:
			continue
		if _usable(child):
			return child
		var deeper := _first_usable(child)
		if deeper != null:
			return deeper
	return null


## Makes `view` modal for the keyboard and the pad (H20): while it is open nothing beside
## it can take focus (its siblings' focus is switched off recursively, so the D-pad and
## Tab can't reach the screen behind and A can't press a control there), and when it
## closes the siblings get focus back and so does whoever had it when the view opened.
## Call it once `view` is in the tree (its _ready). The view keeps Godot's geometric
## D-pad search inside itself (card grids, the spinner's pads).
static func hold(view: Control) -> void:
	if view == null or not view.is_inside_tree() or view.get_parent() == null:
		return
	var owner := owner_of(view)
	# Weak: the opener may be freed while the view is open (the panel behind rebuilt).
	var back: WeakRef = weakref(owner) if owner != null and not view.is_ancestor_of(owner) else null
	var blocked: Array = []
	for sib in view.get_parent().get_children():
		if sib == view or not (sib is Control):
			continue
		var ctl := sib as Control
		if ctl.focus_behavior_recursive == Control.FOCUS_BEHAVIOR_DISABLED:
			continue
		blocked.append([ctl, ctl.focus_behavior_recursive])
		ctl.focus_behavior_recursive = Control.FOCUS_BEHAVIOR_DISABLED
	view.tree_exiting.connect(func() -> void:
		for pair in blocked:
			if is_instance_valid(pair[0]):
				(pair[0] as Control).focus_behavior_recursive = pair[1]
		var ctl: Object = back.get_ref() if back != null else null
		if ctl != null and (ctl as Control).is_inside_tree() and not (ctl as Control).is_queued_for_deletion():
			(ctl as Control).grab_focus.call_deferred(), CONNECT_ONE_SHOT)


## Takes `view` (a modal holding focus) out of the tree at once, so the screen behind can
## take focus again before whatever the view's result rebuilds, then frees it.
static func release(view: Control) -> void:
	if view.get_parent() != null:
		view.get_parent().remove_child(view)
	view.queue_free()


## True when `event` is a key or pad input a modal view should keep from the screen
## behind it (number keys entering map nodes, Space, the pad's face buttons).
static func is_device_input(event: InputEvent) -> bool:
	return event is InputEventKey or event is InputEventJoypadButton or event is InputEventJoypadMotion


## Links `root` like link_layout, then points every open edge back at the control itself,
## so the D-pad can't leave a modal (pause menu, confirm dialog) for the screen behind it.
static func trap(root) -> void:
	if root == null or not is_instance_valid(root) or not (root is Node) or (root as Node).is_queued_for_deletion():
		return  # deferred call after the modal closed
	link_layout(root)
	var blocks: Array = []
	_collect_blocks(root, blocks)
	for c in _controls_of(blocks):
		var ctl: Control = c
		for side in ["focus_neighbor_left", "focus_neighbor_right", "focus_neighbor_top", "focus_neighbor_bottom"]:
			if (ctl.get(side) as NodePath).is_empty():
				ctl.set(side, NodePath("."))
