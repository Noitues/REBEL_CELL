extends Logger
## Review-pack harness (ART-0 D, ported from art-pass W10): collects the errors Godot logs while one screen is reached, so
## its status file can name them (tools/visual_qa/review_pack.gd). Engine threads may log,
## so the list is guarded.

var _mutex := Mutex.new()
var _errors: Array[String] = []
var _script_error := false


## Starts a new screen: forgets earlier errors.
func begin() -> void:
	_mutex.lock()
	_errors.clear()
	_script_error = false
	_mutex.unlock()


## Whether a script error was logged since `begin`.
func has_script_error() -> bool:
	_mutex.lock()
	var v := _script_error
	_mutex.unlock()
	return v


## The errors logged since `begin` (and forgets them).
func take() -> Array[String]:
	_mutex.lock()
	var out := _errors.duplicate()
	_errors.clear()
	_mutex.unlock()
	return out


func _log_error(function: String, file: String, line: int, code: String, rationale: String, _editor_notify: bool,
		error_type: int, _script_backtraces: Array[ScriptBacktrace]) -> void:
	var what := rationale if rationale != "" else code
	var kind := "SCRIPT ERROR" if error_type == ERROR_TYPE_SCRIPT else ("WARNING" if error_type == ERROR_TYPE_WARNING else "ERROR")
	if error_type == ERROR_TYPE_WARNING:
		return
	_mutex.lock()
	_errors.append("%s: %s (%s:%d %s)" % [kind, what, file, line, function])
	if error_type == ERROR_TYPE_SCRIPT:
		_script_error = true
	_mutex.unlock()


func _log_message(_message: String, _error: bool) -> void:
	pass
