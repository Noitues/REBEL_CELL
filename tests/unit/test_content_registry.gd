extends GutTest
## ContentRegistry resolves every content id; duplicate ids fail validation (M0 acceptance).

const RegistryScript := preload("res://scripts/autoload/content_registry.gd")
const TEMP_DIR := "user://test_content_registry"

var _registry: Node


func before_each() -> void:
	# Not added to the tree, so _ready() does not scan res://content.
	_registry = autofree(RegistryScript.new())


func after_each() -> void:
	_remove_temp_dir()


func _slice(id: StringName) -> SliceData:
	var s := SliceData.new()
	s.id = id
	s.slice_type = RC.SliceType.ATTACK
	s.base_output = 6
	return s


func _remove_temp_dir() -> void:
	var dir := DirAccess.open(TEMP_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		dir.remove(f)
	DirAccess.remove_absolute(TEMP_DIR)


func _save_temp(res: Resource, file_name: String) -> String:
	DirAccess.make_dir_recursive_absolute(TEMP_DIR)
	var path := TEMP_DIR.path_join(file_name)
	assert_eq(ResourceSaver.save(res, path), OK, "saved " + path)
	return path


func test_registers_resource_by_id_and_resolves_it() -> void:
	var slice := _slice(&"atk")
	assert_eq(_registry.register(slice).size(), 0)
	assert_true(_registry.has_content(&"atk"))
	assert_same(_registry.get_content(&"atk"), slice)


func test_all_ids_is_sorted() -> void:
	_registry.register(_slice(&"zeta"))
	_registry.register(_slice(&"alpha"))
	_registry.register(_slice(&"mid"))
	assert_eq(_registry.all_ids(), [&"alpha", &"mid", &"zeta"])


func test_duplicate_ids_fail_validation() -> void:
	_registry.register(_slice(&"atk"))
	var errors: PackedStringArray = _registry.register(_slice(&"atk"))
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "Duplicate content id 'atk'")
	var problems: PackedStringArray = _registry.validate()
	var found := false
	for p in problems:
		if p.contains("Duplicate content id 'atk'"):
			found = true
	assert_true(found, "validate() reports the duplicate")



func test_same_instance_registered_twice_is_not_a_duplicate() -> void:
	var slice := _slice(&"atk")
	_registry.register(slice)
	assert_eq(_registry.register(slice).size(), 0)
	assert_eq(_registry.resource_count(), 1)


func test_nested_resources_are_registered_by_id() -> void:
	var hub := HubCoreData.new()
	hub.id = &"breaker_core"
	var wheel := WheelData.new()
	wheel.hub = hub
	var slots: Array[WheelSlotData] = []
	for s in [_slice(&"crit"), _slice(&"atk"), _slice(&"atk2"), _slice(&"atk3"), _slice(&"def"), _slice(&"miss")]:
		var slot := WheelSlotData.new()
		slot.slice = s
		slots.append(slot)
	wheel.slots = slots
	assert_eq(_registry.register(wheel).size(), 0)
	assert_same(_registry.get_content(&"breaker_core"), hub)
	assert_true(_registry.has_content(&"crit"))
	assert_true(_registry.has_content(&"miss"))


func test_nested_duplicate_across_parents_is_reported() -> void:
	var a := WheelSlotData.new()
	a.slice = _slice(&"atk")
	var b := WheelSlotData.new()
	b.slice = _slice(&"atk")
	_registry.register(a)
	assert_eq(_registry.register(b).size(), 1)


func test_validate_surfaces_resource_validate_errors() -> void:
	var site := SiteData.new()
	site.id = &"bad_site"
	site.objective = RC.SiteObjective.HEAT_REDUCTION
	site.heat_change = 5  # must be negative
	_registry.register(site)
	var problems: PackedStringArray = _registry.validate()
	var found := false
	for p in problems:
		if p.begins_with("SiteData 'bad_site':"):
			found = true
	assert_true(found, "site validate() error is reported with its id: %s" % [problems])


func test_validate_reports_missing_config() -> void:
	var problems: PackedStringArray = _registry.validate()
	assert_eq(problems.size(), 1)
	assert_string_contains(problems[0], "No CampaignConfigData")


func test_scan_directory_loads_files_and_reports_duplicates() -> void:
	_save_temp(_slice(&"scan_a"), "a.tres")
	_save_temp(_slice(&"scan_b"), "b.tres")
	_save_temp(_slice(&"scan_a"), "c_dup.tres")
	var errors: PackedStringArray = _registry.scan_directory(TEMP_DIR)
	assert_eq(errors.size(), 1, str(errors))
	assert_string_contains(errors[0], "Duplicate content id 'scan_a'")
	assert_string_contains(errors[0], "c_dup.tres")
	assert_true(_registry.has_content(&"scan_a"))
	assert_true(_registry.has_content(&"scan_b"))
	assert_eq(_registry.all_ids(), [&"scan_a", &"scan_b"])


func test_scan_of_empty_directory_is_an_error() -> void:
	DirAccess.make_dir_recursive_absolute(TEMP_DIR)
	var errors: PackedStringArray = _registry.scan_directory(TEMP_DIR)
	assert_eq(errors.size(), 1)
	assert_string_contains(errors[0], "No content resources found")


func test_real_content_scans_cleanly_and_every_id_resolves() -> void:
	var errors: PackedStringArray = _registry.scan_directory(RegistryScript.CONTENT_ROOT)
	assert_eq(errors.size(), 0, str(errors))
	assert_not_null(_registry.config, "campaign config found")
	for id in _registry.all_ids():
		assert_not_null(_registry.get_content(id), "id %s resolves" % id)
	var problems: PackedStringArray = _registry.validate()
	assert_eq(problems.size(), 0, str(problems))


func test_autoload_scanned_real_content_at_startup() -> void:
	assert_not_null(ContentRegistry.config, "autoload found the campaign config")
	assert_eq(ContentRegistry.validate().size(), 0)
