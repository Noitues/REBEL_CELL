extends SceneTree
## Prints the nodes, meshes, surfaces, materials and vertex-colour presence of the Solace compound glb.
func _init() -> void:
	var sc := load("res://assets/city/hq_compounds/solace/solace_compound.glb") as PackedScene
	var n := sc.instantiate() as Node3D
	_walk(n, 0)
	quit(0)


func _walk(n: Node, d: int) -> void:
	var s := "  ".repeat(d) + n.name + " (" + n.get_class() + ")"
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		s += " aabb=" + str(mi.get_aabb())
		for k in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(k)
			var arr := mi.mesh.surface_get_arrays(k)
			s += "\n" + "  ".repeat(d + 1) + "surf%d mat=%s verts=%d color=%s uv=%s" % [k, m.resource_name if m != null else "-", (arr[Mesh.ARRAY_VERTEX] as PackedVector3Array).size(), str(arr[Mesh.ARRAY_COLOR] != null), str(arr[Mesh.ARRAY_TEX_UV] != null)]
	print("GLB ", s)
	for c in n.get_children():
		_walk(c, d + 1)
