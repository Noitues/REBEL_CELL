class_name NetrunMapView
extends Control
## The netrun map as a wireframe graph (GDD 9.1, STYLE_GUIDE 1): layers left to right,
## edges in net_cyan, nodes as glowing wireframe shapes with a glyph per type (Router
## ring, Elite Router double ring, Terminal square, Modem diamond, Server Rack hexagon),
## the current node in cell_pink, reachable nodes in cell_acid, visited nodes dimmed,
## Heat cost labelled. Emits node_clicked; the scene decides what a click means.

signal node_clicked(node_id: StringName)

const NODE_RADIUS := 18.0
const TYPE_NAMES := {RC.InfilNodeType.ROUTER: "Router", RC.InfilNodeType.TERMINAL: "Terminal",
	RC.InfilNodeType.MODEM: "Modem", RC.InfilNodeType.SERVER_RACK: "Server Rack"}

var map: MapGraph = null
var current_id: StringName = &""
var visited: Array[StringName] = []
var available: Array[StringName] = []
var corp_color: Color = Palette.CORP_SOLACE
var _positions: Dictionary = {}


func _init() -> void:
	custom_minimum_size = Vector2(900, 360)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(queue_redraw)


func show_map(p_map: MapGraph, p_current: StringName, p_visited: Array[StringName], p_available: Array[StringName]) -> void:
	map = p_map
	current_id = p_current
	visited = p_visited
	available = p_available
	queue_redraw()


func _layout() -> void:
	_positions.clear()
	if map == null:
		return
	var layers := map.layer_count()
	for li in layers:
		var layer: Array = map.layers[li]
		var x := 50.0 + (size.x - 100.0) * float(li) / maxf(1.0, layers - 1)
		for ni in layer.size():
			var y := size.y * (float(ni) + 1.0) / (layer.size() + 1.0)
			_positions[layer[ni]["id"]] = Vector2(x, y)


func node_at(point: Vector2) -> StringName:
	for id in _positions:
		if point.distance_to(_positions[id]) <= NODE_RADIUS + 6:
			return id
	return &""


func position_of(node_id: StringName) -> Vector2:
	_layout()
	return _positions.get(node_id, Vector2.ZERO)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var id := node_at(event.position)
		if id != &"":
			node_clicked.emit(id)


func _draw() -> void:
	if map == null:
		return
	_layout()
	# Edges.
	for node in map.all_nodes():
		var a: Vector2 = _positions[node["id"]]
		for n in node["next"]:
			var b: Vector2 = _positions[n]
			var on_path: bool = (visited.has(node["id"]) and (visited.has(n) or available.has(n))) or node["id"] == current_id
			draw_line(a, b, Color(Palette.NET_CYAN, 0.55 if on_path else 0.25), 2.0 if on_path else 1.0)
	# Nodes.
	for node in map.all_nodes():
		var id: StringName = node["id"]
		var p: Vector2 = _positions[id]
		var col := Palette.NET_CYAN
		if id == current_id:
			col = Palette.CELL_PINK
		elif available.has(id):
			col = Palette.CELL_ACID
		elif visited.has(id):
			col = Color(Palette.NET_CYAN, 0.35)
		elif node["type"] == RC.InfilNodeType.SERVER_RACK or node["elite"]:
			col = corp_color
		if id == current_id or available.has(id):
			draw_arc(p, NODE_RADIUS + 8, 0, TAU, 32, Color(col, 0.25), 8.0)
		match int(node["type"]):
			RC.InfilNodeType.ROUTER:
				draw_arc(p, NODE_RADIUS, 0, TAU, 32, col, 1.5)
				if node["elite"]:
					draw_arc(p, NODE_RADIUS - 6, 0, TAU, 32, col, 1.5)
			RC.InfilNodeType.TERMINAL:
				draw_rect(Rect2(p - Vector2(NODE_RADIUS, NODE_RADIUS), Vector2(NODE_RADIUS * 2, NODE_RADIUS * 2)), col, false, 1.5)
			RC.InfilNodeType.MODEM:
				draw_polyline(PackedVector2Array([p + Vector2(0, -NODE_RADIUS), p + Vector2(NODE_RADIUS, 0), p + Vector2(0, NODE_RADIUS), p + Vector2(-NODE_RADIUS, 0), p + Vector2(0, -NODE_RADIUS)]), col, 1.5)
			RC.InfilNodeType.SERVER_RACK:
				var pts := PackedVector2Array()
				for k in 7:
					var a := TAU * k / 6.0
					pts.append(p + Vector2(cos(a), sin(a)) * NODE_RADIUS)
				draw_polyline(pts, col, 2.0)
		var glyph := ""
		match int(node["type"]):
			RC.InfilNodeType.ROUTER:
				glyph = "◈" if node["elite"] else "○"
			RC.InfilNodeType.TERMINAL:
				glyph = "▭"
			RC.InfilNodeType.MODEM:
				glyph = "◇"
			RC.InfilNodeType.SERVER_RACK:
				glyph = "⬢"
		draw_string(Palette.display(), p + Vector2(-7, 7), glyph, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.PAPER)
		var label: String = TYPE_NAMES.get(int(node["type"]), "?")
		if node["elite"] and node["type"] == RC.InfilNodeType.ROUTER:
			label = "Elite " + label
		if int(node["heat"]) != 0:
			label += " +%d Heat" % int(node["heat"])
		if visited.has(id) and id != current_id:
			label = "done"
		draw_string(Palette.mono(), p + Vector2(-40, NODE_RADIUS + 16), label, HORIZONTAL_ALIGNMENT_CENTER, 80, 10, Color(Palette.PAPER, 0.5 if visited.has(id) and id != current_id else 1.0))
	# Layer labels.
	for li in map.layer_count():
		var x := 50.0 + (size.x - 100.0) * float(li) / maxf(1.0, map.layer_count() - 1)
		draw_string(Palette.mono(), Vector2(x - 20, 14), "L%d" % (li + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(Palette.NET_CYAN, 0.6))
