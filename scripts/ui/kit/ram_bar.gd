class_name RamBar
extends Control
## RAM as a bare row of cyan chips (lit = available), nothing else (combat pass).

var ram: int = 0
var max_ram: int = 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(200, 14)


func set_ram(value: int, maximum: int) -> void:
	ram = value
	max_ram = maximum
	tooltip_text = "RAM %d/%d" % [value, maximum]
	queue_redraw()


func _draw() -> void:
	var step := 16.0
	var x0 := (size.x - max_ram * step) * 0.5
	for k in max_ram:
		var rc := Rect2(x0 + k * step, 1, 12, 12)
		draw_rect(rc, Palette.NET_CYAN if k < ram else Color(1, 1, 1, 0.1))
		draw_rect(rc, Color(Palette.NET_CYAN, 0.6), false, 1.0)
