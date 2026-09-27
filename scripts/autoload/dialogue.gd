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
## Where the bar sits outside combat when no screen has registered a SubtitleStrip (H20;
## 1280x720 canvas): the top band over the screen title and the stat tags. H21: the HQ,
## netrun and title screens register their own strip (default_rect), which covers no
## stat tag; this band is only the fallback. Long lines page to the lines that fit.
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
	# H22 #7: lines are translated once (shown_text) and paged as shown; the label must not
	# translate a page again (a pseudolocalised page would grow twice).
	text_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	text_label.scroll_active = false
	text_label.clip_contents = true
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

## The subtitle bar in its place outside combat: the screen's SubtitleStrip (H21 #11: a
## band of its own under the top bar that no control and no stat tag sits in; the H20 top
## band hid the stats, the money in the Modem), else DEFAULT_DOCK. The speaker's name
## inline, paged to the lines that fit (H20: the old bottom bar covered raid asset cards,
## LEAVE THE MODEM, crew Loadout buttons, Grid rows and menu buttons).
func dock_default() -> void:
	dock_at(default_rect, lines_fitting(default_rect))
	# The label's own minimum must not stretch the bar past a one-line strip.
	text_label.custom_minimum_size.y = 0.0
	inline_speaker = true
	_default_dock = true


## Where dock_default puts the bar: the rect a SubtitleStrip registered, else DEFAULT_DOCK.
var default_rect: Rect2 = DEFAULT_DOCK
var _default_owner: Object = null
## Room a subtitle band needs beyond its lines (px).
const BAND_SLACK := 2.0


## A screen's subtitle band (`owner` releases it); the bar moves there when docked by default.
func set_default_rect(rect: Rect2, owner: Object) -> void:
	default_rect = rect
	_default_owner = owner
	if _default_dock:
		dock_default()


## Who holds the default dock now (null: DEFAULT_DOCK).
func default_owner() -> Object:
	return _default_owner if is_instance_valid(_default_owner) else null


## Gives the default dock back (DEFAULT_DOCK) when `owner` still holds it.
func release_default_rect(owner: Object) -> void:
	if _default_owner != owner:
		return
	_default_owner = null
	default_rect = DEFAULT_DOCK
	if _default_dock:
		dock_default()


## Height of a subtitle band that holds `lines` lines at the current text size (px).
func band_height(lines: int = 1) -> float:
	var scale := 1.0
	if has_node("/root/Settings"):
		scale = float(get_node("/root/Settings").text_scale)
	return BAR_PADDING + Palette.mono().get_height(roundi(TEXT_FONT_SIZE * scale)) * maxi(1, lines) + BAND_SLACK


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
	_dock_rect = rect
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
	var wrapped := _wrap(text, width * PAGE_FILL, font, fs)
	var lines: PackedStringArray = wrapped[0]
	var glue: PackedStringArray = wrapped[1]
	for i in range(0, lines.size(), dock_lines):
		var page := ""
		for k in range(i, mini(i + dock_lines, lines.size())):
			page += lines[k] if k == i else glue[k - 1] + lines[k]
		out.append(page)
	return out


## Wraps `text` into lines at most `limit` px wide (H22 #7): at spaces, and by characters
## inside a word wider than a line (Japanese / Chinese have no spaces; a pseudolocalised or
## German word can outgrow a narrow dock). Returns [lines, glue]: glue[k] joins line k to
## line k + 1 (" " at a space, "" inside a word).
func _wrap(text: String, limit: float, font: Font, fs: int) -> Array:
	var lines := PackedStringArray()
	var glue := PackedStringArray()
	var cur := ""
	for word in text.split(" ", false):
		var trial := word if cur == "" else cur + " " + word
		if _text_width(trial, font, fs) <= limit:
			cur = trial
			continue
		if _text_width(word, font, fs) <= limit:
			lines.append(cur)
			glue.append(" ")
			cur = word
			continue
		# A word wider than a line: its characters fill the current line, then new ones.
		var head := "" if cur == "" else cur + " "
		for i in word.length():
			var ch := word[i]
			if head.strip_edges() == "" or _text_width(head + ch, font, fs) <= limit:
				head += ch
				continue
			if head.ends_with(" "):
				lines.append(head.substr(0, head.length() - 1))
				glue.append(" ")
			else:
				lines.append(head)
				glue.append("")
			head = ch
		cur = head
	if cur != "":
		lines.append(cur)
	return [lines, glue]


func _text_width(s: String, font: Font, fs: int) -> float:
	return font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x


## `text` as the player reads it (H22 #7): translated once here (TextDb content is already
## translated; tr of a translated line returns it), pseudolocalised when that is on. The
## label shows it untouched, so paging measures the text on screen.
func shown_text(text: String) -> String:
	return tr(text)


## The wrapped line count of `page` in the bar and the height those lines take (px): at
## least the subtitle font's line height, taller for a fallback font's glyphs (CJK).
func _page_height(page: String) -> float:
	var font := Palette.mono()
	var fs := text_label.get_theme_font_size("normal_font_size")
	var sb := bar.get_theme_stylebox("panel")
	var width := (bar.offset_right - bar.offset_left) - (sb.get_margin(SIDE_LEFT) + sb.get_margin(SIDE_RIGHT) if sb != null else 0.0)
	var lines: PackedStringArray = _wrap(page, width * PAGE_FILL, font, fs)[0]
	var h := 0.0
	for l in lines:
		h += maxf(font.get_height(fs), font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).y)
	return maxf(h, font.get_height(fs))


## The text's height the dock's rect leaves (px): the rect less the bar's padding and a
## speaker row (a docked page is clipped to it as a last resort, H22 #7).
func _dock_text_room() -> float:
	var room := _dock_rect.size.y - BAR_PADDING
	if speaker_label.visible:
		var box := speaker_label.get_parent() as BoxContainer
		room -= speaker_label.get_combined_minimum_size().y + (box.get_theme_constant("separation") if box != null else 0)
	return maxf(Palette.mono().get_height(text_label.get_theme_font_size("normal_font_size")), room)


## Escapes BBCode in shown words (pseudolocalisation wraps a line in brackets).
static func _escape(s: String) -> String:
	return s.replace("[", "[lb]")


## The rect of the last dock (a paged page is clipped to its height).
var _dock_rect: Rect2 = DEFAULT_DOCK


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
	# H22 #7: page the words as shown (translated once; a continued page already is).
	var words := String(line["text"]) if bool(line.get("continued", false)) else shown_text(String(line["text"]))
	var shown_name := shown_text(name)
	var body := ("%s: %s" % [shown_name, words]) if inline else words
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
	var shown := _escape(pages[0])
	_shown = pages[0]
	if inline and pages[0].begins_with(shown_name + ":"):
		_shown = pages[0].substr(shown_name.length() + 1).strip_edges()
		shown = "[color=#%s]%s:[/color] %s" % [speaker_label.get_theme_color("font_color").to_html(false), _escape(shown_name), _escape(_shown)]
	text_label.text = shown
	_fit_page(pages[0])
	bar.visible = _subtitles_on()
	_timer = get_tree().create_timer(float(line["seconds"]))
	var t := _timer
	_timer.timeout.connect(func() -> void:
		if _timer == t:
			_next())


## A paged dock holds the page's own lines and no more (H22 #7): the label is as tall as
## the page's wrapped lines, capped at the dock's room and clipped there as a last resort
## (a font's line taller than planned, the label wrapping differently from the measure).
func _fit_page(page: String) -> void:
	if dock_lines <= 0:
		text_label.fit_content = true
		return
	text_label.fit_content = false
	var room := _dock_text_room()
	var h := _page_height(page)
	if h > room + 0.5:
		# Before clipping: this page a size smaller (accents stacked by pseudolocalisation, a
		# taller fallback font); the next page starts at the text size again.
		var fs := text_label.get_theme_font_size("normal_font_size")
		text_label.add_theme_font_size_override("normal_font_size", maxi(1, floori(fs * room / h)))
		h = _page_height(page)
	text_label.custom_minimum_size.y = minf(h, room)


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
		dock_lines = lines_fitting(default_rect)


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
