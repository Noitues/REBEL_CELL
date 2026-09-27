class_name DaemonRow
extends Control
## The operative's installed Daemons as a row of sigils under the Polaroid (H20: replaces
## the DAEMONS text note). Hover a sigil for what it does. View only.

## Sigil radius and spacing at text scale 1.0 (px).
const SIGIL_RADIUS := 11.0
const SPACING := 28.0
const HEIGHT := 30.0

var daemon_ids: Array[StringName] = []
var lookup: ContentLookup = null


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = " "
	custom_minimum_size = Vector2(0, HEIGHT)


func set_daemons(ids: Array[StringName], p_lookup: ContentLookup) -> void:
	daemon_ids = ids.duplicate()
	lookup = p_lookup
	custom_minimum_size = Vector2(0, HEIGHT * Settings.text_scale)
	queue_redraw()


func _step() -> float:
	return SPACING * Settings.text_scale


## Daemon under a local point, or &"".
func daemon_at(local: Vector2) -> StringName:
	var i := int(floor(local.x / _step()))
	return daemon_ids[i] if i >= 0 and i < daemon_ids.size() else &""


## Every Daemon's text (the pad inspect and the tests read it).
func describe_all() -> String:
	var parts := PackedStringArray()
	for id in daemon_ids:
		var d := lookup.get_content(id) as DaemonData if lookup != null else null
		parts.append(Codex.describe(d) if d != null else String(id))
	return "\n\n".join(parts) if not parts.is_empty() else "No Daemons installed."


func _get_tooltip(at_position: Vector2) -> String:
	var id := daemon_at(at_position)
	if id == &"":
		return "Daemons: permanent programs of this operative (none installed)." if daemon_ids.is_empty() else ""
	var d := lookup.get_content(id) as DaemonData if lookup != null else null
	return Codex.describe(d) if d != null else String(id)


func _draw() -> void:
	var s := _step()
	var r := SIGIL_RADIUS * Settings.text_scale
	for i in daemon_ids.size():
		var d := lookup.get_content(daemon_ids[i]) as DaemonData if lookup != null else null
		DaemonSigil.draw_sigil(self, Vector2(s * (i + 0.5), size.y * 0.5), r, daemon_ids[i], d.rarity if d != null else RC.Rarity.UNCOMMON)
