extends Node
## ContentRegistry autoload: scans res://content, maps id -> Resource and validates
## every resource on load (TECH_SPEC §3). Content is read-only at runtime.
##
## Ids are collected from every .tres/.res file under the root and from resources
## nested inside them (a wheel's Hub Core, a class's starting cards, ...). The same
## instance reached twice is fine; two different instances sharing an id is a
## duplicate and fails validation.

const CONTENT_ROOT := "res://content"
const CONFIG_PATH := "res://content/config/campaign_config.tres"
const RESOURCE_EXTENSIONS: PackedStringArray = ["tres", "res"]
const CONFIG_KEY := &"__config__"

## The single global tuning resource, or null until scan_directory() finds it.
var config: CampaignConfigData = null

var _by_id: Dictionary = {}          # StringName -> Resource
var _source_of: Dictionary = {}      # StringName -> String (file path)
var _resources: Array[Resource] = [] # every distinct resource seen, scan order
var _seen_instances: Dictionary = {} # instance id -> true
var _errors: PackedStringArray = PackedStringArray()


func _ready() -> void:
	if Engine.is_editor_hint():
		return
	var errors := scan_directory(CONTENT_ROOT)
	errors.append_array(validate())
	if OS.is_debug_build():
		for e in errors:
			push_error("ContentRegistry: " + e)
	# Resolved by path, not by name: tools/validate_content.gd preloads this script from a
	# `-s` SceneTree script, which compiles before autoload singletons exist.
	var bus: Node = get_tree().root.get_node_or_null(^"SignalBus")
	if bus != null:
		bus.content_loaded.emit(_by_id.size(), errors.size())


## Forgets everything scanned or registered so far.
func clear() -> void:
	config = null
	_by_id.clear()
	_source_of.clear()
	_resources.clear()
	_seen_instances.clear()
	_errors.clear()


## Loads every resource file under `root` (recursively) and registers it and its
## nested resources. Returns the load and duplicate-id errors found while scanning.
## Files are visited in sorted path order so results never depend on OS listing order.
func scan_directory(root: String) -> PackedStringArray:
	var errors := PackedStringArray()
	var paths := _collect_resource_paths(root)
	if paths.is_empty():
		errors.append("No content resources found under %s." % root)
	for path in paths:
		var res: Resource = ResourceLoader.load(path)
		if res == null:
			errors.append("Failed to load %s." % path)
			continue
		if res is CampaignConfigData:
			if config != null and config != res:
				errors.append("More than one CampaignConfigData: %s and %s." % [_source_of.get(CONFIG_KEY, "?"), path])
			config = res
			_source_of[CONFIG_KEY] = path
		errors.append_array(register(res, path))
	_errors.append_array(errors)
	return errors


## Registers `res` and every resource nested in its exported properties. Returns the
## duplicate-id errors, if any, and records them for validate(). `source` names the
## file for error messages.
func register(res: Resource, source: String = "") -> PackedStringArray:
	var errors := PackedStringArray()
	_walk(res, source, errors)
	if source == "":
		_errors.append_array(errors)
	return errors


## The resource with content id `id`, or null (with an error) when unknown.
func get_content(id: StringName) -> Resource:
	if not _by_id.has(id):
		push_error("ContentRegistry: no content with id '%s'." % id)
		return null
	return _by_id[id]


## True when `id` is registered.
func has_content(id: StringName) -> bool:
	return _by_id.has(id)


## Every registered id, sorted for deterministic iteration.
func all_ids() -> Array[StringName]:
	var ids: Array[StringName] = []
	for id in _by_id.keys():
		ids.append(id)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return ids


## Number of distinct resources seen (files and nested resources).
func resource_count() -> int:
	return _resources.size()


## Runs validate() on every registered resource and on the config. Returns all
## problems found, including duplicate ids recorded during scanning/registration.
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	errors.append_array(_errors)
	if config == null:
		errors.append("No CampaignConfigData found (expected %s)." % CONFIG_PATH)
	for res in _resources:
		if not res.has_method("validate"):
			continue
		var problems: Variant = res.validate()
		for p in problems:
			errors.append("%s: %s" % [_describe(res), String(p)])
	return errors


func _describe(res: Resource) -> String:
	if "id" in res:
		var id: Variant = res.get("id")
		if id is StringName and id != &"":
			return "%s '%s'" % [_class_of(res), String(id)]
	if res.resource_path != "":
		return "%s (%s)" % [_class_of(res), res.resource_path]
	return _class_of(res)


func _class_of(res: Resource) -> String:
	var script: Script = res.get_script()
	if script != null and script.get_global_name() != &"":
		return String(script.get_global_name())
	return res.get_class()


func _walk(res: Resource, source: String, errors: PackedStringArray) -> void:
	if res == null:
		return
	var instance_id := res.get_instance_id()
	if _seen_instances.has(instance_id):
		return
	_seen_instances[instance_id] = true
	_resources.append(res)
	if res.get_script() == null:
		return  # Engine resources (textures, fonts...) carry no content id.
	if "id" in res:
		var id: Variant = res.get("id")
		if id is StringName and id != &"":
			if _by_id.has(id):
				errors.append("Duplicate content id '%s' in %s (first seen in %s)." % [id, _where(res, source), _source_of[id]])
			else:
				_by_id[id] = res
				_source_of[id] = _where(res, source)
	for prop in res.get_property_list():
		if (prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE) == 0:
			continue
		var value: Variant = res.get(prop.name)
		if value is Resource:
			_walk(value, source, errors)
		elif value is Array:
			for item in value:
				if item is Resource:
					_walk(item, source, errors)


func _where(res: Resource, source: String) -> String:
	if res.resource_path != "":
		return res.resource_path
	return source if source != "" else "<memory>"


func _collect_resource_paths(root: String) -> PackedStringArray:
	var paths := PackedStringArray()
	var dir := DirAccess.open(root)
	if dir == null:
		return paths
	dir.include_hidden = false
	dir.include_navigational = false
	dir.list_dir_begin()
	var name := dir.get_next()
	while name != "":
		var full := root.path_join(name)
		if dir.current_is_dir():
			paths.append_array(_collect_resource_paths(full))
		elif RESOURCE_EXTENSIONS.has(name.get_extension()):
			paths.append(full)
		name = dir.get_next()
	dir.list_dir_end()
	paths.sort()
	return paths
