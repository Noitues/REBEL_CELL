class_name JackInputGate
extends Node
## ANIM-R2 R3: the jack's input blocker. `_input` reaches the nodes of the tree in reverse
## tree order, so the Fx autoload (an early child of the root) saw a press only after the
## scene's own `_input` handlers had acted on it: a Space then Enter under the opaque cover
## could carry and drop an operative nobody saw. While a jack runs Fx keeps this node the
## LAST child of the root (the new scene is added after it, so it moves back behind it at
## once), so it sees every event first and stops each one but pointer motion (hover only)
## before any scene handler, GUI control or shortcut gets it. View only.

## Stops events while true (Fx sets it with the jack).
var blocking: bool = false
## Events stopped so far (tests read it).
var stopped: int = 0


func _init() -> void:
	name = "JackInputGate"
	process_mode = Node.PROCESS_MODE_ALWAYS


func _enter_tree() -> void:
	var root := get_tree().root
	if not root.child_entered_tree.is_connected(_on_root_child):
		root.child_entered_tree.connect(_on_root_child)


func _exit_tree() -> void:
	var root := get_tree().root
	if root.child_entered_tree.is_connected(_on_root_child):
		root.child_entered_tree.disconnect(_on_root_child)


## A node joined the root (the arriving scene): stay behind it, so this gate stays first
## in the input order.
func _on_root_child(node: Node) -> void:
	if node != self:
		stay_last.call_deferred()


## Moves this gate to the end of the root's children (first to receive `_input`).
func stay_last() -> void:
	if not is_inside_tree():
		return
	var root := get_parent()
	if root != null and get_index() != root.get_child_count() - 1:
		root.move_child(self, -1)


func _input(event: InputEvent) -> void:
	if blocking and not (event is InputEventMouseMotion):
		stopped += 1
		get_viewport().set_input_as_handled()
