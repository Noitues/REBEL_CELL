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

## Subtitle font sizes at text scale 1.0.
const SPEAKER_FONT_SIZE := 12
const TEXT_FONT_SIZE := 15
## Lines per subtitle page in a docked bar (0 = the bar grows to fit the whole line).
var dock_lines: int = 0
## The subtitle text's widest minimum (a narrower dock wraps inside its rect) (px).
const TEXT_MIN_WIDTH := 560.0
## Where the bar sits outside combat (H20; 1280x720 canvas): the top band over the screen
## title and the stat tags. Every control sits below the band (the screens' content starts
## under the HUD strip) or right of it (VIEW LOADOUT, the Daemons icon), so a line never
## covers one; long lines page to the lines that fit at the current text size.
const DEFAULT_DOCK := Rect2(8, 2, 964, 52)
## Vertical padding of the bar's panel (top + bottom content margins, px).
const BAR_PADDING := 12.0
## In the default dock the speaker's name leads the line (no separate name row).
var inline_speaker: bool = false
var _default_dock: bool = false
## The words of the page on screen (without the inline name).
var _shown: String = ""


func _ready() -> void:
	layer = 90
	bar = PanelContainer.new()
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.visible = false
	add_child(bar)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.add_child(box)
	speaker_label = Label.new()
	speaker_label.add_theme_font_override("font", Palette.mono())
	speaker_label.add_theme_font_size_override("font_size", SPEAKER_FONT_SIZE)
	box.add_child(speaker_label)
	text_label = RichTextLabel.new()
	text_label.bbcode_enabled = true
	text_label.fit_content = true
	text_label.custom_minimum_size = Vector2(TEXT_MIN_WIDTH, 40)
	text_label.add_theme_font_override("normal_font", Palette.mono())
	text_label.add_theme_font_size_override("normal_font_size", TEXT_FONT_SIZE)
	text_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(text_label)
	_style(RC.Voice.DISPATCH)
	_collect_sets()
	if has_node("/root/Settings"):
		get_node("/root/Settings").changed.connect(_on_settings_changed)
	_apply_text_scale()
	dock_default()


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

## The subtitle bar in its place outside combat (DEFAULT_DOCK): the top band, the speaker's
## name inline, paged to the lines that fit (H20: the old bottom bar covered raid asset
## cards, LEAVE THE MODEM, crew Loadout buttons, Grid rows and menu buttons).
func dock_default() -> void:
	dock_at(DEFAULT_DOCK, lines_fitting(DEFAULT_DOCK))
	inline_speaker = true
	_default_dock = true


## Kept for callers from before H20 (the combat scene restores the dock on exit): the
## default dock, no longer at the foot of the screen.
func dock_bottom() -> void:
	dock_default()


## How many subtitle lines fit in `rect`'s height at the current text size (at least 1).
func lines_fitting(rect: Rect2) -> int:
	var fs := text_label.get_theme_font_size("normal_font_size")
	return maxi(1, floori((rect.size.y - BAR_PADDING) / Palette.mono().get_height(fs)))


## The subtitle bar in a screen rect (combat puts it at the top, clear of the hand). With
## `max_lines` > 0 a longer line is shown as pages of at most that many lines, one after
## the other, so the bar never grows past the rect's neighbours at any text scale.
func dock_at(rect: Rect2, max_lines: int = 0) -> void:
	bar.set_anchors_preset(Control.PRESET_TOP_LEFT)
	bar.offset_left = rect.position.x
	bar.offset_top = rect.position.y
	bar.offset_right = rect.end.x
	bar.offset_bottom = rect.end.y
	bar.grow_vertical = Control.GROW_DIRECTION_END
	dock_lines = max_lines
	# The text wraps inside the rect (a narrow column dock must not widen the bar).
	var sb := bar.get_theme_stylebox("panel")
	var margins := sb.get_margin(SIDE_LEFT) + sb.get_margin(SIDE_RIGHT) if sb != null else 0.0
	if text_label != null:
		text_label.custom_minimum_size.x = minf(TEXT_MIN_WIDTH, maxf(0.0, rect.size.x - margins))
	inline_speaker = false
	_default_dock = false


## Splits `text` into pages of at most `dock_lines` wrapped lines at the bar's width and
## the current text size (one page when the bar is not paged).
func pages_of(text: String) -> PackedStringArray:
	var out := PackedStringArray()
	if dock_lines <= 0:
		out.append(text)
		return out
	var font := Palette.mono()
	var fs := text_label.get_theme_font_size("normal_font_size")
	var sb := bar.get_theme_stylebox("panel")
	var width := (bar.offset_right - bar.offset_left) - (sb.get_margin(SIDE_LEFT) + sb.get_margin(SIDE_RIGHT) if sb != null else 0.0)
	var lines := PackedStringArray()
	var cur := ""
	for word in text.split(" ", false):
		var trial := word if cur == "" else cur + " " + word
		if cur != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width * PAGE_FILL:
			lines.append(cur)
			cur = word
		else:
			cur = trial
	if cur != "":
		lines.append(cur)
	for i in range(0, lines.size(), dock_lines):
		out.append(" ".join(lines.slice(i, i + dock_lines)))
	return out


## Share of the bar width a paged line may fill (RichTextLabel wraps a little earlier than
## the plain measurement).
const PAGE_FILL := 0.95


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


## The words on screen now (the current page, without an inline speaker name).
func current_text() -> String:
	return _shown if bar.visible else ""


func _next() -> void:
	if _queue.is_empty():
		_timer = null
		bar.visible = false
		return
	var line: Dictionary = _queue.pop_front()
	# Page at the text size in force now (a settings change without a signal can't leave
	# the bar paging for another size).
	_apply_text_scale()
	var corp_id := StringName(String(line.get("corporation", "")))
	var name := speaker_name(int(line["speaker"]), corp_id)
	# Default dock: the name leads the first page ("DISPATCH: ..."), not a row of its own.
	var inline := inline_speaker and name != "" and not bool(line.get("continued", false))
	var body := ("%s: %s" % [name, String(line["text"])]) if inline else String(line["text"])
	var pages := pages_of(body)
	if pages.size() > 1:
		# The rest of a long line waits at the front of the queue, time shared by length.
		var whole := maxf(1.0, body.length())
		var seconds := float(line["seconds"])
		for k in range(pages.size() - 1, 0, -1):
			var rest := line.duplicate()
			rest["text"] = pages[k]
			rest["continued"] = true
			rest["seconds"] = maxf(MIN_SECONDS, seconds * pages[k].length() / whole)
			_queue.push_front(rest)
		line["seconds"] = maxf(MIN_SECONDS, seconds * pages[0].length() / whole)
	_style(int(line["speaker"]), corp_id)
	speaker_label.text = name
	speaker_label.visible = name != "" and not inline_speaker
	var shown := pages[0]
	_shown = shown
	if inline and shown.begins_with(name + ":"):
		_shown = shown.substr(name.length() + 1).strip_edges()
		shown = "[color=#%s]%s:[/color] %s" % [speaker_label.get_theme_color("font_color").to_html(false), name, _shown]
	text_label.text = shown
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
	_apply_text_scale()


## Subtitle font sizes follow Settings.text_scale (GDD 9.6).
func _apply_text_scale() -> void:
	var scale := 1.0
	if has_node("/root/Settings"):
		scale = float(get_node("/root/Settings").text_scale)
	speaker_label.add_theme_font_size_override("font_size", roundi(SPEAKER_FONT_SIZE * scale))
	text_label.add_theme_font_size_override("normal_font_size", roundi(TEXT_FONT_SIZE * scale))
	if _default_dock:
		dock_lines = lines_fitting(DEFAULT_DOCK)


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
		style.bg_color = Color(0.02, 0.03, 0.08, 0.95)
		var corp_color := Palette.corp_color(corporation_id) if corporation_id != &"" else Palette.CORP_SOLACE
		style.border_color = Palette.CRT_AMBER if speaker == RC.Voice.DISPATCH else corp_color
		style.set_border_width_all(1)
		style.border_width_left = 4
		style.shadow_color = Color(0, 0, 0, 0.5)
		style.shadow_size = 8
		speaker_label.add_theme_color_override("font_color", style.border_color)
		text_label.add_theme_color_override("default_color", Palette.CRT_AMBER if speaker == RC.Voice.DISPATCH else Palette.PAPER)
	else:
		style.bg_color = Color(Palette.NOTE_PAPER, 0.97)
		style.border_color = Palette.INK
		style.set_border_width_all(1)
		style.border_width_left = 4
		style.border_color = Palette.CELL_PINK
		style.shadow_color = Color(0, 0, 0, 0.5)
		style.shadow_size = 8
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
	var cfg: CampaignConfigData = rm.config()
	if played >= cfg.dispatch_drift_late:
		return 2
	if played >= cfg.dispatch_drift_mid:
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
