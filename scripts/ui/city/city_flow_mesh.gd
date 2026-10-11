class_name CityFlowMesh
extends RefCounted
## M14 perf slice (HQ idle CPU): the city map's crawling dashes and threat chevrons
## (CityMapOverlay's flow layer) as ONE still mesh, laid only when the routes on screen change;
## shaders/city/city_flow.gdshader slides each dash and chevron along its track by the frame's
## phase. The CPU path laid every dash and every chevron again on every frame (~1-5 ms of the
## HQ idle's frame with its threat routes). Same picture: the same quads and polyline strips at
## the same places, in the same order (the CPU's: per edge its dashes, then its chevrons, each
## chevron's keyline before its colour).
##
## A track is one segment of one edge for one kind (its dashes, or its chevrons); its row in the
## track texture: (origin.xy, dir.xy), (length, period, base, flow), (kind, 0, 0, 0). A dash
## track's base is 0; a chevron track's base is minus the edge's length before the segment (the
## CPU carried the chevrons' spacing on round the corners: carry = (phase - before) mod step).

const SHADER := preload("res://shaders/city/city_flow.gdshader")
const KIND_DASH := 0
const KIND_CHEVRON := 1
## Rows the track texture may hold (a texture's height limit); a plan past it stays on the CPU.
const MAX_TRACKS := 16384
## The chevrons' keyline width and their colour's width per unit of the map's scale k:
## CityMapOverlay._chevrons' values (its keyline colour comes in with build()).
const CHEVRON_INK_W := 4.5
const CHEVRON_W := 2.2

var mesh: ArrayMesh = null
var tracks: ImageTexture = null
var material: ShaderMaterial = null
## Track rows of the last build (tests, the probe).
var track_count: int = 0

var _rows := PackedFloat32Array()
var _verts := PackedVector2Array()
var _uvs := PackedVector2Array()
var _cols := PackedColorArray()
var _idx := PackedInt32Array()


## Lays edges `edges` (each {"pts": PackedVector2Array (local px), "color", "width", "flow",
## "dashed", "arrows"}) at phase 0: dashes of `dash_on` px every `dash_period` px, chevrons of
## half-size `chevron_size` every `chevron_step` px (both already scaled to the map), the map's
## scale `k` for the chevrons' widths, their keyline `chevron_ink`, at most `max_per_segment` of
## each per segment. False
## (nothing built) when the plan does not fit the track texture.
func build(edges: Array[Dictionary], dash_on: float, dash_period: float, chevron_step: float, chevron_size: float, k: float, max_per_segment: int, chevron_ink: Color) -> bool:
	_rows = PackedFloat32Array()
	_verts = PackedVector2Array()
	_uvs = PackedVector2Array()
	_cols = PackedColorArray()
	_idx = PackedInt32Array()
	track_count = 0
	for e: Dictionary in edges:
		var pts: PackedVector2Array = e["pts"]
		var col: Color = e["color"]
		var w: float = e["width"]
		var flow := 1.0 if bool(e["flow"]) else 0.0
		if bool(e["dashed"]):
			for q in pts.size() - 1:
				var a := pts[q]
				var length := a.distance_to(pts[q + 1])
				if not is_finite(length) or length <= 0.0:
					continue
				var row := _track(a, (pts[q + 1] - a) / length, length, dash_period, 0.0, flow, KIND_DASH)
				for i in mini(max_per_segment, ceili(length / dash_period)):
					var t := i * dash_period
					_quad(row, t, t + dash_on, w, col)
		if bool(e["arrows"]):
			var before := 0.0
			for q in pts.size() - 1:
				var a := pts[q]
				var length := a.distance_to(pts[q + 1])
				if not is_finite(length) or length <= 0.0:
					continue
				var row := _track(a, (pts[q + 1] - a) / length, length, chevron_step, -before, flow, KIND_CHEVRON)
				before += length
				for i in mini(max_per_segment, ceili(length / chevron_step)):
					var c := i * chevron_step
					var wing := PackedVector2Array([Vector2(c - chevron_size, chevron_size), Vector2(c + chevron_size, 0.0), Vector2(c - chevron_size, -chevron_size)])
					_strip(row, c, polyline_strip(wing, CHEVRON_INK_W * k, -1.0), chevron_ink)
					_strip(row, c, polyline_strip(wing, CHEVRON_W * k, -1.0), col)
	if track_count > MAX_TRACKS:
		return false
	mesh = null
	if _idx.is_empty():
		return true
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = _verts
	arrays[Mesh.ARRAY_TEX_UV] = _uvs
	arrays[Mesh.ARRAY_COLOR] = _cols
	arrays[Mesh.ARRAY_INDEX] = _idx
	mesh = ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, Mesh.ARRAY_FLAG_USE_2D_VERTICES)
	var img := Image.create_from_data(3, track_count, false, Image.FORMAT_RGBAF, _rows.to_byte_array())
	if tracks == null or tracks.get_size() != Vector2(img.get_size()):
		tracks = ImageTexture.create_from_image(img)
	else:
		tracks.update(img)
	if material == null:
		material = ShaderMaterial.new()
		material.shader = SHADER
	material.set_shader_parameter(&"tracks", tracks)
	return true


## Sets the frame's phases (px): the dashes' fmod(travel, dash period), the chevrons'
## fmod(travel, chevron step).
func set_phase(dash_phase: float, chevron_phase: float) -> void:
	if material == null:
		return
	material.set_shader_parameter(&"dash_phase", dash_phase)
	material.set_shader_parameter(&"chevron_phase", chevron_phase)


## The shift (px along its track) a track of `period`, `base` and `flow` (0 or 1) gives its
## elements at phase `phase`: the shader's mod(phase * flow + base, period).
static func shift_of(phase: float, period: float, base: float, flow: float) -> float:
	var x := phase * flow + base
	return x - period * floorf(x / period)


## The triangle strip (2 vertices per point) Godot lays for a polyline of `width` through `pts`
## (no antialiasing): the ends square to their segment, a corner mitred on the bisector of its
## two segments' normals. `frame_sign` -1: `pts` are in a track's frame (x along the track, y
## along its dir.orthogonal(): a mirror of the canvas), so the canvas' normals are negated and
## the strip's vertices come in Godot's order.
static func polyline_strip(pts: PackedVector2Array, width: float, frame_sign: float = 1.0) -> PackedVector2Array:
	var out := PackedVector2Array()
	var hw := width * 0.5 * frame_sign
	var n := pts.size()
	for i in n:
		var off: Vector2
		if i == 0:
			off = (pts[1] - pts[0]).normalized().orthogonal()
		elif i == n - 1:
			off = (pts[i] - pts[i - 1]).normalized().orthogonal()
		else:
			var n0 := (pts[i] - pts[i - 1]).normalized().orthogonal()
			var n1 := (pts[i + 1] - pts[i]).normalized().orthogonal()
			var bis := (n0 + n1).normalized()
			off = bis / maxf(bis.dot(n0), 0.001)
		out.append(pts[i] + off * hw)
		out.append(pts[i] - off * hw)
	return out


func _track(a: Vector2, dir: Vector2, length: float, period: float, base: float, flow: float, kind: int) -> int:
	_rows.append_array(PackedFloat32Array([a.x, a.y, dir.x, dir.y, length, period, base, flow, float(kind), 0.0, 0.0, 0.0]))
	track_count += 1
	return track_count - 1


## A dash from `t0` to `t1` along track `row`, `w` px wide (draw_multiline's quad).
func _quad(row: int, t0: float, t1: float, w: float, col: Color) -> void:
	var hw := w * 0.5
	var b := _verts.size()
	for p: Vector2 in [Vector2(t0, hw), Vector2(t1, hw), Vector2(t1, -hw), Vector2(t0, -hw)]:
		_verts.append(p)
		_uvs.append(Vector2(row, t0))
		_cols.append(col)
	_idx.append_array(PackedInt32Array([b, b + 1, b + 2, b, b + 2, b + 3]))


## Triangle strip `strip` (track-frame px) on track `row`, anchored at `anchor`.
func _strip(row: int, anchor: float, strip: PackedVector2Array, col: Color) -> void:
	var b := _verts.size()
	for p in strip:
		_verts.append(p)
		_uvs.append(Vector2(row, anchor))
		_cols.append(col)
	for i in strip.size() - 2:
		if i % 2 == 0:
			_idx.append_array(PackedInt32Array([b + i, b + i + 1, b + i + 2]))
		else:
			_idx.append_array(PackedInt32Array([b + i + 1, b + i, b + i + 2]))
