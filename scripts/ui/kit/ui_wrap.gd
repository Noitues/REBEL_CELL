class_name UiWrap
extends RefCounted
## Keeps menu panels inside the fixed 1280-wide screen (H9/H12 width rule): long Labels and
## Buttons wrap instead of widening their panel. Views call fit() after a panel enters the tree.

## Widest a single Label or Button in a row may grow before it wraps.
const MAX_ITEM_WIDTH := 560.0


## Wraps every Label stacked in a vertical box, and any Label or Button in a row that is
## wider than MAX_ITEM_WIDTH (text scale included).
static func fit(root: Node) -> void:
	if root == null:
		return
	for n in root.find_children("*", "Label", true, false):
		var l := n as Label
		if l.autowrap_mode != TextServer.AUTOWRAP_OFF:
			continue
		if l.get_parent() is VBoxContainer:
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		elif l.get_minimum_size().x > MAX_ITEM_WIDTH:
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.custom_minimum_size.x = MAX_ITEM_WIDTH
	for n in root.find_children("*", "Button", true, false):
		var b := n as Button
		if b.autowrap_mode == TextServer.AUTOWRAP_OFF and b.get_minimum_size().x > MAX_ITEM_WIDTH:
			b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			b.custom_minimum_size.x = MAX_ITEM_WIDTH
