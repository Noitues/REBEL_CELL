class_name RcLookMaterialAudit
extends RefCounted
## LOOK-TOOLBOX dev tool: lists, for every ShaderMaterial under a node (material overrides, surface overrides, mesh
## surfaces, next passes, CanvasItem materials), each shader parameter that is set and how it compares with the
## shader's own text default. Labs call it behind `--dump-materials=<file>` so a "true defaults" pass reads the values
## the game really draws with. Appends lines "AUDIT|<shader file>|<name>|<text default>|<value>" (one per distinct
## value). Not shipped behaviour: tools only.

const UNIFORM_RE := "uniform\\s+\\w+\\s+(\\w+)(?:\\s*:\\s*[^=;]+)?(?:\\s*=\\s*([^;]+))?;"


## Appends the audit of every ShaderMaterial under `root` to `path`.
static func dump(root: Node, path: String) -> void:
	var seen := {}
	var mats: Array[ShaderMaterial] = []
	_collect(root, mats, seen)
	var lines := {}
	for m in mats:
		if m.shader == null or m.shader.resource_path == "":
			continue
		var defaults := text_defaults(m.shader.code)
		for u: Dictionary in m.shader.get_shader_uniform_list():
			var n: String = u["name"]
			var v: Variant = m.get_shader_parameter(StringName(n))
			if v == null or v is Texture or v is Object:
				continue
			lines["AUDIT|%s|%s|%s|%s" % [m.shader.resource_path.get_file(), n, defaults.get(n, "<none>"), _fmt(v)]] = true
	var f := FileAccess.open(path, FileAccess.READ_WRITE if FileAccess.file_exists(path) else FileAccess.WRITE)
	if f == null:
		push_error("material_audit: cannot write %s" % path)
		return
	f.seek_end()
	var keys := lines.keys()
	keys.sort()
	for k: String in keys:
		f.store_line(k)
	f.close()


## Uniform name -> its default as written in the shader ("<none>" when it has none).
static func text_defaults(code: String) -> Dictionary:
	var out := {}
	var re := RegEx.create_from_string(UNIFORM_RE)
	for m in re.search_all(code):
		out[m.get_string(1)] = m.get_string(2).strip_edges() if m.get_string(2) != "" else "<none>"
	return out


static func _collect(n: Node, mats: Array[ShaderMaterial], seen: Dictionary) -> void:
	if n is GeometryInstance3D:
		_add((n as GeometryInstance3D).material_override, mats, seen)
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		for s in mi.get_surface_override_material_count():
			_add(mi.get_surface_override_material(s), mats, seen)
		if mi.mesh != null:
			for s in mi.mesh.get_surface_count():
				_add(mi.mesh.surface_get_material(s), mats, seen)
	if n is MultiMeshInstance3D:
		var mm := (n as MultiMeshInstance3D).multimesh
		if mm != null and mm.mesh != null:
			for s in mm.mesh.get_surface_count():
				_add(mm.mesh.surface_get_material(s), mats, seen)
	if n is CanvasItem:
		_add((n as CanvasItem).material, mats, seen)
	for c in n.get_children(true):
		_collect(c, mats, seen)


static func _add(m: Material, mats: Array[ShaderMaterial], seen: Dictionary) -> void:
	while m != null:
		if seen.has(m.get_instance_id()):
			return
		seen[m.get_instance_id()] = true
		if m is ShaderMaterial:
			mats.append(m as ShaderMaterial)
		m = m.next_pass


static func _fmt(v: Variant) -> String:
	if v is Vector2:
		return "vec2(%s, %s)" % [v.x, v.y]
	if v is Vector3:
		return "vec3(%s, %s, %s)" % [v.x, v.y, v.z]
	if v is Vector4 or v is Color or v is Quaternion:
		return "vec4(%s, %s, %s, %s)" % [v[0], v[1], v[2], v[3]]
	return str(v)
