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
