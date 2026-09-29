class_name PseudoLoc
extends RefCounted
## Test helper (ANIM-R6 A18): pseudolocalisation on for a test, then the project's own
## values back. `on()` keeps the pseudolocalisation ProjectSettings and the
## TranslationServer switch as they were before; `off()` puts exactly those back (the old
## helpers set them to false, whatever the project had).

const KEYS: Array[String] = ["internationalization/pseudolocalization/replace_with_accents",
	"internationalization/pseudolocalization/double_vowels", "internationalization/pseudolocalization/override"]

## The values before the first `on()` since the last `off()` ({} when none are kept).
static var _saved: Dictionary = {}


## Scrambles every translated string (accents, doubled vowels), keeping the prior values.
static func on() -> void:
	if _saved.is_empty():
		for k in KEYS:
			_saved[k] = ProjectSettings.get_setting(k)
		_saved["enabled"] = TranslationServer.pseudolocalization_enabled
	ProjectSettings.set_setting(KEYS[0], true)
	ProjectSettings.set_setting(KEYS[1], true)
	ProjectSettings.set_setting(KEYS[2], false)
	TranslationServer.pseudolocalization_enabled = true
	TranslationServer.reload_pseudolocalization()


## Puts back what `on()` found (nothing to do when it wasn't called).
static func off() -> void:
	if _saved.is_empty():
		return
	for k in KEYS:
		ProjectSettings.set_setting(k, _saved[k])
	TranslationServer.pseudolocalization_enabled = bool(_saved["enabled"])
	TranslationServer.reload_pseudolocalization()
	_saved = {}


## The value a pseudolocalisation setting had before `on()` (its current one when none kept).
static func saved(key: String) -> Variant:
	return _saved.get(key, ProjectSettings.get_setting(key))
