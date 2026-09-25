extends CanvasLayer
## Dialogue autoload: the subtitle bar (GDD 9.6: speaker names, honours
## Settings.subtitles) and the line database (GDD 8.2, 8.6): DISPATCH briefings, raid
## warnings, threshold lines, operative barks and the pirate-radio DJ, all read from
## LineSetData content. Line choice is deterministic (hash of the campaign seed and the
## key), never global RNG. DISPATCH text is clean system text (Share Tech Mono on a dark
## strip); other speakers get the paper strip. Views call say(); nothing here changes
## game state.

signal line_spoken(speaker: int, text: String)

const SPEAKER_NAMES := {RC.Voice.NARRATOR: "", RC.Voice.STREET_MERC: "OPERATIVE", RC.Voice.CORPO: "CORPORATE",
	RC.Voice.AI_OBSERVER: "OBSERVER", RC.Voice.DISPATCH: "DISPATCH"}
const SECONDS_PER_CHAR := 0.045
const MIN_SECONDS := 1.6
const MAX_QUEUE := 6

var bar: PanelContainer
var speaker_label: Label
var text_label: RichTextLabel
## Lines shown so far this session (tests and the codex read it).
var history: Array[Dictionary] = []
var _queue: Array[Dictionary] = []
var _timer: SceneTreeTimer = null
var _sets: Array[LineSetData] = []


## Class alternative id -> base class id (barks are shared with the base class).
var _class_base: Dictionary = {}

func _ready() -> void:
	layer = 90
	bar = PanelContainer.new()
	bar.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	bar.offset_left = -440
	bar.offset_right = 440
	bar.offset_top = -92
	bar.offset_bottom = -20
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.visible = false
	add_child(bar)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.add_child(box)
	speaker_label = Label.new()
	speaker_label.add_theme_font_override("font", Palette.mono())
	speaker_label.add_theme_font_size_override("font_size", 12)
	box.add_child(speaker_label)
	text_label = RichTextLabel.new()
	text_label.bbcode_enabled = true
	text_label.fit_content = true
	text_label.custom_minimum_size = Vector2(860, 40)
	text_label.add_theme_font_override("normal_font", Palette.mono())
	text_label.add_theme_font_size_override("normal_font_size", 15)
	text_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(text_label)
	_style(RC.Voice.DISPATCH)
	_collect_sets()
	if has_node("/root/Settings"):
		get_node("/root/Settings").changed.connect(_on_settings_changed)


func _collect_sets() -> void:
	_sets.clear()
	_class_base.clear()
	var registry: Node = get_tree().root.get_node_or_null(^"ContentRegistry")
	if registry == null:
		return
	for id in registry.all_ids():
		var res: Resource = registry.get_content(id)
		if res is LineSetData:
			_sets.append(res)
		elif res is ClassData and (res as ClassData).alternative_of != &"":
			_class_base[id] = (res as ClassData).alternative_of


## Registers extra line sets (tests).
func add_set(set: LineSetData) -> void:
	if not _sets.has(set):
		_sets.append(set)


# --- Speaking -----------------------------------------------------------------------------

## Shows a subtitle (queued behind any line still on screen). Emits line_spoken at once
## so voice-over and logs can follow even with subtitles switched off.
func say(speaker: int, text: String, seconds: float = 0.0, corporation_id: StringName = &"") -> void:
	if text == "":
		return
	history.append({"speaker": speaker, "text": text, "corporation": corporation_id})
	line_spoken.emit(speaker, text)
	if _queue.size() >= MAX_QUEUE:
		_queue.pop_front()
	_queue.append({"speaker": speaker, "text": text, "corporation": corporation_id,
		"seconds": seconds if seconds > 0.0 else maxf(MIN_SECONDS, text.length() * SECONDS_PER_CHAR)})
	if _timer == null:
		_next()


## Clears the queue and hides the bar (scene changes).
func clear() -> void:
	_queue.clear()
	_timer = null
	bar.visible = false


func is_showing() -> bool:
	return bar.visible


func current_text() -> String:
	return text_label.get_parsed_text() if bar.visible else ""


func _next() -> void:
	if _queue.is_empty():
		_timer = null
		bar.visible = false
		return
	var line: Dictionary = _queue.pop_front()
	var corp_id := StringName(String(line.get("corporation", "")))
	_style(int(line["speaker"]), corp_id)
	var name := speaker_name(int(line["speaker"]), corp_id)
	speaker_label.text = name
	speaker_label.visible = name != ""
	text_label.text = String(line["text"])
	bar.visible = _subtitles_on()
	_timer = get_tree().create_timer(float(line["seconds"]))
	var t := _timer
	_timer.timeout.connect(func() -> void:
		if _timer == t:
			_next())


func _subtitles_on() -> bool:
	var s: Node = get_node_or_null("/root/Settings")
	return s == null or bool(s.subtitles)


func _on_settings_changed() -> void:
	if not _subtitles_on():
		bar.visible = false


## The subtitle label: corporate lines carry their corporation's short name.
func speaker_name(speaker: int, corporation_id: StringName = &"") -> String:
	if speaker == RC.Voice.CORPO and corporation_id != &"":
		var registry: Node = get_tree().root.get_node_or_null(^"ContentRegistry") if is_inside_tree() else null
		var corp := registry.get_content(corporation_id) as CorporationData if registry != null else null
		if corp != null:
			return corp.display_name.split(" ")[0].to_upper()
	return SPEAKER_NAMES.get(speaker, "")


## DISPATCH: clean dark strip with amber system text; everyone else: paper strip, ink.
func _style(speaker: int, corporation_id: StringName = &"") -> void:
	var style := StyleBoxFlat.new()
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	if speaker == RC.Voice.DISPATCH or speaker == RC.Voice.CORPO:
		style.bg_color = Color(Palette.DESK_DARK, 0.92)
		var corp_color := Palette.corp_color(corporation_id) if corporation_id != &"" else Palette.CORP_SOLACE
		style.border_color = Palette.CRT_AMBER if speaker == RC.Voice.DISPATCH else corp_color
		style.set_border_width_all(1)
		speaker_label.add_theme_color_override("font_color", style.border_color)
		text_label.add_theme_color_override("default_color", Palette.CRT_AMBER if speaker == RC.Voice.DISPATCH else Palette.PAPER)
	else:
		style.bg_color = Color(Palette.PAPER, 0.94)
		style.border_color = Palette.INK
		style.set_border_width_all(1)
		speaker_label.add_theme_color_override("font_color", Palette.CELL_PINK)
		text_label.add_theme_color_override("default_color", Palette.INK)
	bar.add_theme_stylebox_override("panel", style)


# --- Line database ---------------------------------------------------------------------------

## DISPATCH voice drift stage for the profile (GDD 8.2): 0 for the first campaigns, 1 after
## two campaigns, 2 after five. Reads the RunManager profile when present.
func drift_stage() -> int:
	var rm: Node = get_node_or_null("/root/RunManager")
	if rm == null or rm.profile == null:
		return 0
	var played: int = rm.profile.campaigns_started
	if played >= 6:
		return 2
	if played >= 3:
		return 1
	return 0


## A line for `key` from sets matching `speaker`, `corporation_id` and `class_id`
## (empty = any). Lines above the current drift stage are hidden; among the rest the
## highest stage wins; ties are broken by `salt` (campaign seed, turn...) so the choice is
## stable for a save. Returns null when nothing matches.
func line(key: String, speaker: int = -1, corporation_id: StringName = &"", class_id: StringName = &"", salt: int = 0) -> VoiceLineData:
	var stage := drift_stage()
	var best: Array[VoiceLineData] = []
	var best_stage := -1
	for set in _sets:
		if speaker >= 0 and set.speaker != speaker:
			continue
		if corporation_id != &"" and set.corporation_id != &"" and set.corporation_id != corporation_id:
			continue
		if class_id != &"" and set.class_id != &"" and set.class_id != class_id:
			continue
		for l in set.lines_for(key):
			if l.drift_stage > stage:
				continue
			if l.drift_stage > best_stage:
				best_stage = l.drift_stage
				best = [l]
			elif l.drift_stage == best_stage:
				best.append(l)
	if best.is_empty():
		return null
	best.sort_custom(func(a: VoiceLineData, b: VoiceLineData) -> bool: return a.text < b.text)
	return best[posmod(hash([key, salt]), best.size())]


## Speaks the line for `key` if any. Returns the text spoken ("" when none).
func speak(key: String, speaker: int = -1, corporation_id: StringName = &"", class_id: StringName = &"", salt: int = 0) -> String:
	var l := line(key, speaker, corporation_id, class_id, salt)
	if l == null:
		return ""
	var voice := speaker
	if voice < 0:
		for set in _sets:
			if set.lines.has(l):
				voice = set.speaker
	say(voice, l.text, 0.0, corporation_id)
	return l.text


func briefing(corporation_id: StringName, site_id: StringName, salt: int = 0) -> String:
	return speak("site:%s" % site_id, RC.Voice.DISPATCH, corporation_id, &"", salt)


func raid_warning(corporation_id: StringName, raid_id: StringName, salt: int = 0) -> String:
	var text := speak("raid:%s" % raid_id, -1, corporation_id, &"", salt)
	if text == "":
		text = speak("raid:any", -1, corporation_id, &"", salt)
	return text


func threshold_line(corporation_id: StringName, heat: int, salt: int = 0) -> String:
	return speak("threshold:%d" % heat, -1, corporation_id, &"", salt)


func bark(class_id: StringName, trigger: String, salt: int = 0) -> String:
	# Class alternatives speak with their base class's barks.
	return speak("bark:%s" % trigger, RC.Voice.STREET_MERC, &"", _class_base.get(class_id, class_id), salt)


func dj(salt: int = 0, corporation_id: StringName = &"") -> String:
	return speak("dj", RC.Voice.NARRATOR, corporation_id, &"", salt)
