class_name ContentLookup
extends RefCounted
## Id -> Resource map handed to the combat core so it can resolve content ids without
## touching the ContentRegistry autoload (keeps the core pure and testable).

var _by_id: Dictionary = {}


## Registers `res` and every resource nested in it that carries a non-empty `id`.
func add(res: Resource) -> ContentLookup:
	_walk(res, {})
	return self


## Registers every id of a registry-like object exposing all_ids() / get_content().
func add_registry(registry: Object) -> ContentLookup:
	for id in registry.all_ids():
		_by_id[id] = registry.get_content(id)
	return self


func has(id: StringName) -> bool:
	return _by_id.has(id)


## Every known id, sorted (deterministic pools).
func ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in _by_id.keys():
		out.append(id)
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out


## Sorted ids of every resource whose script class is `class_name_`.
func ids_of_class(class_name_: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for id in ids():
		var script: Script = _by_id[id].get_script()
		if script != null and script.get_global_name() == class_name_:
			out.append(id)
	return out


## Resource for `id`; pushes an error and returns null when unknown.
func get_content(id: StringName) -> Resource:
	if not _by_id.has(id):
		push_error("ContentLookup: unknown content id '%s'." % id)
		return null
	return _by_id[id]


func _walk(res: Resource, seen: Dictionary) -> void:
	if res == null or seen.has(res.get_instance_id()):
		return
	seen[res.get_instance_id()] = true
	if res.get_script() == null:
		return
	if "id" in res:
		var id: Variant = res.get("id")
		if id is StringName and id != &"":
			_by_id[id] = res
	for prop in res.get_property_list():
		if (prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE) == 0:
			continue
		var value: Variant = res.get(prop.name)
		if value is Resource:
			_walk(value, seen)
		elif value is Array:
			for item in value:
				if item is Resource:
					_walk(item, seen)
