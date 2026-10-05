class_name PencilLint
extends RefCounted
## The grease pencil's standing rules as a check (ART-1 1B; ART_BIBLE v2 §1.2 "No UI ever
## covers grease pencil" (round 40), §6.4 layer order "... damage numbers -> grease pencil ->
## cursor. Pencil is above all UI"):
## - **cover**: no UI node that draws (a Control other than a bare layout Control or
##   Container) is drawn above a pencil mark where its rect meets a stroke;
## - **layer**: every pencil mark is on a CanvasLayer at or above every UI layer that shows
##   (the cursor's layer, `CURSOR_LAYER_MIN` and up, is the one exception).
## The visual QA harness exports these (tools/visual_qa/review_pack.gd, lint key "pencil")
## and tests call `violations` on a built screen. Reads the tree; changes nothing.

## CanvasLayers from this order up hold only the cursor (allowed above pencil).
const CURSOR_LAYER_MIN := 128
## Controls of these classes only lay out their children; they draw nothing of their own.
const LAYOUT_CLASSES: Array[String] = ["Control", "Container", "BoxContainer", "VBoxContainer", "HBoxContainer",
	"GridContainer", "MarginContainer", "CenterContainer", "AspectRatioContainer", "FlowContainer", "HFlowContainer",
	"VFlowContainer", "ScrollContainer", "SubViewportContainer", "SplitContainer", "HSplitContainer", "VSplitContainer"]


## Every pencil mark (GreasePencilMark / GreasePencilWord) visible under `root`.
static func marks(root: Node) -> Array[Node2D]:
	var out: Array[Node2D] = []
	if root == null or not root.is_inside_tree():
		return out
	for n in root.get_tree().get_nodes_in_group(GreasePencilMark.GROUP):
		var m := n as Node2D
		if m != null and m.is_visible_in_tree() and (m == root or root.is_ancestor_of(m)):
			out.append(m)
	return out


## The rects a mark's strokes cover (global).
static func stroke_rects(m: Node2D) -> Array[Rect2]:
	if m is GreasePencilMark:
		return (m as GreasePencilMark).segment_rects()
	if m is GreasePencilWord:
		return [(m as GreasePencilWord).global_rect()]
	return []


## The CanvasLayer order a node draws on (0: the root canvas).
static func layer_of(n: Node) -> int:
	var p := n.get_parent()
	while p != null:
		if p is CanvasLayer:
			return (p as CanvasLayer).layer
		p = p.get_parent()
	return 0


## True when `c` draws something of its own (not a bare layout node).
static func draws(c: Control) -> bool:
	if c.get_script() != null:
		return true
	return not LAYOUT_CLASSES.has(c.get_class())


## Every rule broken under `root`: [{rule, mark, node, why}].
static func violations(root: Node) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var ms := marks(root)
	if ms.is_empty():
		return out
	var order := {}
	_walk(root, order, [0])
	for m in ms:
		var ml := layer_of(m)
		var mkey := _key(ml, int(order.get(m.get_instance_id(), 0)))
		var rects := stroke_rects(m)
		for id in order:
			var n := instance_from_id(id) as Control
			if n == null or not n.is_visible_in_tree() or not draws(n) or m.is_ancestor_of(n) or n.is_ancestor_of(m):
				continue
			var nl := layer_of(n)
			if nl >= CURSOR_LAYER_MIN:
				continue
			if nl > ml:
				out.append({"rule": "layer", "mark": str(m.get_path()), "node": str(n.get_path()),
					"why": "UI on layer %d above the pencil's layer %d" % [nl, ml]})
				continue
			if _key(nl, int(order[id])) <= mkey:
				continue
			var nr := n.get_global_rect()
			for r in rects:
				if nr.intersects(r):
					out.append({"rule": "cover", "mark": str(m.get_path()), "node": str(n.get_path()),
						"why": "drawn over a stroke at %s" % [r.position.round()]})
					break
	return out


static func _key(layer: int, index: int) -> int:
	return layer * 1000000 + index


static func _walk(n: Node, order: Dictionary, counter: Array) -> void:
	if n is CanvasItem:
		order[n.get_instance_id()] = counter[0]
		counter[0] += 1
	for c in n.get_children():
		_walk(c, order, counter)
