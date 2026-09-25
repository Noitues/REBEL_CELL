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
			if c.focus_mode != Control.FOCUS_NONE and not (c is BaseButton and (c as BaseButton).disabled) and (c is BaseButton or c is LineEdit or c is Range):
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


## D-pad neighbours for a whole panel: controls in a horizontal container form one row,
## a lone control is a row of its own; left/right walk a row, up/down move to the same
## column (clamped) of the row above/below. Tilted stickers, SpinBoxes and long lists
## defeat Godot's geometric search, so panels link explicitly (horizontal pass 6).
static func link_layout(root: Node) -> void:
	var rows: Array = []
	_collect_rows(root, rows)
	# Start clean: a relink (settings sections swap their controls) must not leave paths to
	# controls that are no longer in the tree.
	for row in rows:
		for c in row:
			c.focus_neighbor_left = NodePath()
			c.focus_neighbor_right = NodePath()
			c.focus_neighbor_top = NodePath()
			c.focus_neighbor_bottom = NodePath()
	for r in rows.size():
		var row: Array = rows[r]
		for i in row.size():
			var c: Control = row[i]
			if i > 0:
				c.focus_neighbor_left = c.get_path_to(row[i - 1])
			if i + 1 < row.size():
				c.focus_neighbor_right = c.get_path_to(row[i + 1])
			if r > 0:
				var up: Array = rows[r - 1]
				c.focus_neighbor_top = c.get_path_to(up[mini(i, up.size() - 1)])
			if r + 1 < rows.size():
				var down: Array = rows[r + 1]
				c.focus_neighbor_bottom = c.get_path_to(down[mini(i, down.size() - 1)])


static func _usable(c: Node) -> bool:
	if not (c is Control):
		return false
	var ctl := c as Control
	if not ctl.is_visible_in_tree() or ctl.is_queued_for_deletion() or ctl.focus_mode == Control.FOCUS_NONE:
		return false
	if ctl is BaseButton:
		return not (ctl as BaseButton).disabled
	if ctl is Range:
		return not (ctl is SpinBox) and not (ctl is ScrollBar)  # sliders yes; scrollbars belong to their owner
	if ctl is RichTextLabel:
		return true  # a reference note made focusable (ZineNote.make_reference)
	return ctl is LineEdit and not (ctl.get_parent() is SpinBox)


static func _collect_rows(node: Node, rows: Array) -> void:
	for child in node.get_children():
		if not (child is Control) or child.is_queued_for_deletion() or not (child as Control).is_visible_in_tree():
			continue
		if child is SpinBox:
			continue  # use the -/+ buttons beside it
		if _usable(child):
			rows.append([child])
			continue
		if child is HBoxContainer or child is HFlowContainer:
			var row: Array = []
			for g in child.get_children():
				if g is SpinBox:
					continue
				if _usable(g):
					row.append(g)
				else:
					var inner := _first_usable(g)
					if inner != null:
						row.append(inner)
			if not row.is_empty():
				rows.append(row)
			continue
		_collect_rows(child, rows)


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


## Links `root` like link_layout, then points every open edge back at the control itself,
## so the D-pad can't leave a modal (pause menu, confirm dialog) for the screen behind it.
static func trap(root) -> void:
	if root == null or not is_instance_valid(root) or not (root is Node) or (root as Node).is_queued_for_deletion():
		return  # deferred call after the modal closed
	link_layout(root)
	var rows: Array = []
	_collect_rows(root, rows)
	for row in rows:
		for c in row:
			var ctl: Control = c
			for side in ["focus_neighbor_left", "focus_neighbor_right", "focus_neighbor_top", "focus_neighbor_bottom"]:
				if (ctl.get(side) as NodePath).is_empty():
					ctl.set(side, NodePath("."))
