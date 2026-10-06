extends GutTest
## H24 screens (DECISIONS "H24 screens"): the code's words exported for translators; no
## "%+d" in a translated line; every word on the HQ, raid setup, route, Mainframe, event, loot
## and title screens translated, once; the late-campaign raid map framed with its key clear
## of the nodes; B-back only from a pad; the SAVED stamp placed on the page it lands on; the
## subtitle pager's first page carries words; the event's choices inside the screen with a
## mark for "no change"; the Mainframe's text, icons and buy stickers apart; every crew dossier
## reachable at big text; the route's nodes clear of its column, its colours explained and
## its choices told apart; the title's Continue line; the raid setup's defence cards and
## words; screen-tied subtitles ending with their screen; the top bar's captions; the whole
## text of loot and Mainframe items on focus.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const TITLE := "res://scenes/menu/title_scene.tscn"
const SLOT := "gut_s24_screens"
const CANVAS := Vector2(1280, 720)
## Frames the raid map takes to frame its nodes (settled passes, and a key swap).
const RAID_SETTLE := 60
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.3, Settings.TEXT_SCALE_MAX]
## The pseudolocalisation marks the tests use (a translation of a translation shows two).
const PSEUDO_PREFIX := "«"
const PSEUDO_SUFFIX := "»"
const PSEUDO_SETTINGS := ["internationalization/pseudolocalization/prefix", "internationalization/pseudolocalization/suffix",
	"internationalization/pseudolocalization/replace_with_accents", "internationalization/pseudolocalization/double_vowels",
	"internationalization/pseudolocalization/fake_bidi", "internationalization/pseudolocalization/override",
	"internationalization/pseudolocalization/expansion_ratio", "internationalization/pseudolocalization/skip_placeholders"]

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _legend_before: bool = true
var _pseudo_before: bool = false
var _locale_before: String = "en"
var _translation: Translation = null
var _pseudo_settings: Dictionary = {}


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	_pseudo_before = TranslationServer.pseudolocalization_enabled
	_locale_before = TranslationServer.get_locale()
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Fx.saved_screen = Rect2(Vector2.ZERO, CANVAS)


func after_each() -> void:
	if _translation != null:
		TranslationServer.remove_translation(_translation)
		_translation = null
	TranslationServer.set_locale(_locale_before)
	if TranslationServer.pseudolocalization_enabled != _pseudo_before:
		TranslationServer.pseudolocalization_enabled = _pseudo_before
	if not _pseudo_settings.is_empty():
		for k in _pseudo_settings:
			ProjectSettings.set_setting(k, _pseudo_settings[k])
		_pseudo_settings.clear()
		TranslationServer.reload_pseudolocalization()
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
	Fx.saved_screen = Rect2()
	Dialogue.clear()
	Dialogue.enter_screen("")
	Dialogue.dock_default()
	AudioDirector.muted = false
	get_tree().paused = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _open(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


## `c`'s rect clipped to the scroll views above it.
func _shown_rect(c: Control) -> Rect2:
	var r := c.get_global_rect()
	var p := c.get_parent()
	while p != null:
		if p is ScrollContainer:
			r = r.intersection((p as Control).get_global_rect())
		p = p.get_parent()
	return r


## Every visible, usable control under `root`, and the map legends, as far as they show.
func _controls(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		var usable := (n is BaseButton and not (n as BaseButton).disabled and (n as Control).mouse_filter != Control.MOUSE_FILTER_IGNORE) or n is LineEdit or (n is Range and not (n is ScrollBar))
		if usable or n is MapLegend or n is RouteLegend:
			if _shown_rect(n as Control).has_area():
				out.append(n)
	return out


func _translate(pairs: Dictionary) -> void:
	_translation = Translation.new()
	_translation.locale = "xx"
	for k in pairs:
		_translation.add_message(k, pairs[k])
	TranslationServer.add_translation(_translation)
	TranslationServer.set_locale("xx")


## Pseudolocalisation on with its own marks: a word translated once reads «...», one
## translated twice ««...»» (the settings are restored after the test).
func _pseudo() -> void:
	for k in PSEUDO_SETTINGS:
		_pseudo_settings[k] = ProjectSettings.get_setting(k)
	ProjectSettings.set_setting("internationalization/pseudolocalization/prefix", PSEUDO_PREFIX)
	ProjectSettings.set_setting("internationalization/pseudolocalization/suffix", PSEUDO_SUFFIX)
	ProjectSettings.set_setting("internationalization/pseudolocalization/replace_with_accents", true)
	ProjectSettings.set_setting("internationalization/pseudolocalization/double_vowels", false)
	ProjectSettings.set_setting("internationalization/pseudolocalization/fake_bidi", false)
	ProjectSettings.set_setting("internationalization/pseudolocalization/override", false)
	ProjectSettings.set_setting("internationalization/pseudolocalization/expansion_ratio", 0.0)
	ProjectSettings.set_setting("internationalization/pseudolocalization/skip_placeholders", true)
	TranslationServer.reload_pseudolocalization()
	TranslationServer.pseudolocalization_enabled = true


## The words control `c` puts on screen: its text as its auto-translate mode shows it.
func _shown_text(c: Control) -> String:
	var t := ""
	if c is Label:
		t = (c as Label).text
	elif c is Button:
		t = (c as Button).text
	elif c is RichTextLabel:
		t = (c as RichTextLabel).text
	elif c is LineEdit:
		t = (c as LineEdit).placeholder_text
	return c.atr(t) if c.can_auto_translate() else t


## The tooltip control `c` shows, translated as its tooltip mode says.
func _shown_tip(c: Control) -> String:
	var mode := c.tooltip_auto_translate_mode
	var on := c.can_auto_translate() if mode == Node.AUTO_TRANSLATE_MODE_INHERIT else mode == Node.AUTO_TRANSLATE_MODE_ALWAYS
	return String(TranslationServer.translate(c.tooltip_text)) if on and c.tooltip_text != "" else c.tooltip_text


## Whether `t` holds a translation of a translation: a «...» pair whose words are exactly
## one «...» pair (a line built from translated parts, "«%s (x)»" % "«Name»", nests pairs
## too, but never one right inside another).
static func _doubled(t: String) -> bool:
	var open: Array[int] = []
	var pairs := {}
	for i in t.length():
		if t[i] == PSEUDO_PREFIX:
			open.append(i)
		elif t[i] == PSEUDO_SUFFIX and not open.is_empty():
			pairs[open.pop_back()] = i
	for a in pairs:
		if pairs.has(a + 1) and int(pairs[a + 1]) == int(pairs[a]) - 1:
			return true
	return false


## Nothing under `root` is translated twice, in a text or a tooltip.
func _assert_once(root: Node, what: String) -> void:
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		var c := n as Control
		var t := _shown_text(c)
		assert_false(_doubled(t), "%s: '%s' (%s %s) translated twice" % [what, t, c.get_class(), c.name])
		var tip := _shown_tip(c)
		assert_false(_doubled(tip), "%s: the tooltip of %s %s translated twice: '%s'" % [what, c.get_class(), c.name, tip.left(120)])


## Every word under `root` a player reads is translated (carries the pseudo mark): labels
## and buttons with letters, other than names in `names_ok`.
func _assert_translated(root: Node, what: String, names_ok: Array[String] = []) -> void:
	var letters := RegEx.create_from_string("[A-Za-z]{2,}")
	for n in _all(root):
		if not (n is Label or n is Button) or not (n as Control).is_visible_in_tree():
			continue
		var t := _shown_text(n as Control)
		if letters.search(t) == null:
			continue
		var skip := false
		for ok in names_ok:
			if t.contains(ok):
				skip = true
		if skip:
			continue
		assert_true(t.contains(PSEUDO_PREFIX), "%s: '%s' (%s %s) is not translated" % [what, t, n.get_class(), n.name])


## Two claimed nodes beside the home server, an Armory and a pending raid.
func _raid_campaign() -> CampaignState:
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var claimed := 0
	for sd in grid_data.sites:
		if sd.tier == 1 and sd.id != grid_data.home_site_id and sd.objective == RC.SiteObjective.NONE and claimed < 2:
			var s := c.grid.site(sd.id)
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = ["turret"] if claimed == 0 else []
			claimed += 1
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25, "corporation": String(c.corporation_id)})
	return c


## A late campaign (H24 S5): LATE_CLAIMS claimed Sites of the lowest tiers, LATE_TAKEN
## taken ones, an Armory and a pending raid.
const LATE_CLAIMS := 9
const LATE_TAKEN := 2
func _late_campaign() -> CampaignState:
	var c := RunManager.campaign
	var sites: Array = RunManager.corporation.city_grid.sites.filter(func(sd: SiteData) -> bool:
		return sd != null and sd.id != RunManager.corporation.city_grid.home_site_id and sd.objective != RC.SiteObjective.CENTRAL_SERVER)
	sites.sort_custom(func(a: SiteData, b: SiteData) -> bool: return a.tier < b.tier or (a.tier == b.tier and String(a.id) < String(b.id)))
	var claimed := 0
	var taken := 0
	for sd in sites:
		var s := c.grid.site(sd.id)
		if claimed < LATE_CLAIMS:
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = []
			claimed += 1
		elif taken < LATE_TAKEN:
			s["status"] = GridState.SiteStatus.TAKEN
			taken += 1
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25, "corporation": String(c.corporation_id)})
	return c


func _raid(scale: float) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	_raid_campaign()
	var hq := _open(HQ)
	await _frames()
	hq.show_raid()
	await _frames(RAID_SETTLE)
	return hq


func _netrun() -> Control:
	var scene := _open(NETRUN)
	scene.start_run(1)
	return scene


func _shop(scene: Control) -> void:
	var s := RunManager.netrun
	s.run.cycles = 120
	s._open_shop()
	scene._show_current()


func _event(scene: Control, id: StringName = &"ev_leash_on_the_floor") -> void:
	var run := RunManager.netrun.run
	run.event_id = id
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _loot(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()


func _unlock_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


# --- S1 the code's words reach the translators ------------------------------------------------

func test_every_code_key_is_in_the_csv() -> void:
	var keys := TextDb.code_keys(PackedStringArray(["res://scripts/ui", "res://scripts/autoload"]))
	assert_true(keys.size() > 100, "the code translates its words (%d keys)" % keys.size())
	assert_true(keys.has("HITS %s %d") and keys.has("LAST TURN: ") and keys.has("NEXT %d (%s)"), "the combat's drawn words are keys")
	assert_true(keys.has("CYBERDECK HQ") and keys.has("START DEFENSE") and keys.has("PIRATE RADIO"), "and the screens'")
	var csv := {}
	var f := FileAccess.open("res://assets/text/strings.csv", FileAccess.READ)
	f.get_csv_line()
	while not f.eof_reached():
		var line := f.get_csv_line()
		if line.size() > 1:
			csv[line[0]] = line[1]
	var missing := PackedStringArray()
	for k in keys:
		if not csv.has(k):
			missing.append(k)
	assert_eq(missing.size(), 0, "strings.csv lacks %d code keys (run tools/export_text.gd): %s" % [missing.size(), ", ".join(missing.slice(0, 20))])
	for k in TextDb.UI_TEXT:
		assert_true(csv.has(k), "screen sentence %s exported" % k)
	# The key's English is the key itself, and the importer keeps it (spaces included).
	assert_eq(String(csv.get(" AGAIN", "")), " AGAIN")
	assert_eq(String(TranslationServer.get_translation_object("en").get_message("LAST TURN: ")), "LAST TURN: ", "the .translation carries it")


func test_code_keys_read_literals_and_marked_lines() -> void:
	assert_eq(TextDb.unescape("A\\nB \\\"C\\\" \\\\"), "A\nB \"C\" \\")
	var keys := TextDb.code_keys(PackedStringArray(["res://scripts/ui"]))
	assert_true(keys.has("IF THE RAID\nRUNS NOW:"), "a marked constant's words, escapes read")
	assert_true(keys.has("Fight") and keys.has("Elite fight"), "the route's node words")
	assert_false(keys.has(""), "no empty key")


# --- S2 signed numbers ------------------------------------------------------------------------------

func test_signed_numbers_and_no_plus_d_in_translated_lines() -> void:
	assert_eq(TextDb.signed(3), "+3")
	assert_eq(TextDb.signed(-2), "-2")
	assert_eq(TextDb.signed(0), "0")
	var mine := ["res://scripts/ui/hq_scene.gd", "res://scripts/ui/netrun_scene.gd", "res://scripts/ui/title_scene.gd", "res://scripts/autoload/dialogue.gd",
		"res://scripts/autoload/fx.gd"]
	var d := DirAccess.open("res://scripts/ui/kit")
	for f in d.get_files():
		if f.ends_with(".gd") and not f in ["toast.gd", "ram_bar.gd", "drip_button.gd", "heat_poster.gd"]:
			mine.append("res://scripts/ui/kit/" + f)
	var re := RegEx.create_from_string("(?<![A-Za-z0-9_])(?:tr|atr|TranslationServer\\.translate|TextDb\\.mark)\\(\\s*\"([^\"]*)\"")
	for path in mine:
		var src := FileAccess.get_file_as_string(path)
		for m in re.search_all(src):
			assert_false(m.get_string(1).contains("%+"), "%s: translated line '%s' has a %%+ format (use %%s and TextDb.signed)" % [path, m.get_string(1)])
		for line in src.split("\n"):
			if line.strip_edges(false, true).ends_with(TextDb.CODE_MARK):
				assert_false(line.contains("%+"), "%s: a marked line with %%+: %s" % [path, line.strip_edges()])
	# Under pseudolocalisation the numbers survive (the "%+d" format broke).
	_pseudo()
	var card := CardData.new()
	card.id = &"gut_ram"
	var e := EffectData.new()
	e.type = RC.EffectType.GAIN_RAM
	e.amount = 3
	card.effects = [e] as Array[EffectData]
	var tag := String(ZineCard.pictos_of(card)[0]["text"])
	assert_string_contains(tag, "+3", "RAM+3 keeps its number: %s" % tag)
	assert_true(tag.begins_with(PSEUDO_PREFIX), "and its word is translated: %s" % tag)
	var dh := HQ_modifier_text(20)
	assert_string_contains(dh, "+20", "a rule's number: %s" % dh)


func HQ_modifier_text(value: float) -> String:
	var m := RuleModifierData.new()
	m.type = RC.RuleModifierType.RAID_STRENGTH_PCT
	m.value = value
	return load("res://scripts/ui/hq_scene.gd")._modifier_text(m)


# --- S3 / S4 words translated, once -----------------------------------------------------------------

func test_hq_raid_and_grid_words_are_translated_once() -> void:
	_raid_campaign()
	_pseudo()
	var hq := _open(HQ)
	await _frames(4)
	_assert_once(hq, "HQ")
	var names: Array[String] = []
	for op in RunManager.campaign.roster:
		names.append(op.name.to_upper())
		names.append(op.name)
	_assert_translated(hq._panel, "HQ", names)
	assert_true(String(hq.hud._title).begins_with(PSEUDO_PREFIX), "the screen title: %s" % hq.hud._title)
	for i in hq.hud.stats.items.size():
		assert_true(hq.hud.stats.tag_name(i).begins_with(PSEUDO_PREFIX), "top-bar word %s" % hq.hud.stats.tag_name(i))
	var radio := hq._panel.find_child("PirateRadio", true, false) as CrtText  # ART-10 4C: terminal text
	assert_true(radio.title.begins_with(PSEUDO_PREFIX), "PIRATE RADIO's title")
	assert_true(radio.label.get_parsed_text().contains(PSEUDO_PREFIX), "its words")
	for n in _all(hq._panel):
		if n is Badge:
			assert_true((n as Badge).text.contains(PSEUDO_PREFIX) or (n as Badge).text == "" or (n as Badge).asset_id != &"", "badge '%s'" % (n as Badge).text)
		if n is CrewCard:
			assert_true((n as CrewCard).polaroid.caption.contains(PSEUDO_PREFIX), "the rank tag: %s" % (n as CrewCard).polaroid.caption)
	var boosts: Node = hq._panel.find_child("Boosts", true, false)
	for b in boosts.get_children():
		if b is Button:
			assert_false(_shown_text(b).begins_with(PSEUDO_PREFIX + PSEUDO_PREFIX), "boost '%s' once" % _shown_text(b))
	hq.show_grid()
	await _frames(4)
	_assert_once(hq, "Grid")
	hq.show_raid()
	await _frames(8)
	_assert_once(hq, "raid setup")
	for key in ["HomeForecast", "ThreatsStopped", "RaidStrength"]:
		var b := hq._panel.find_child(key, true, false) as Label  # ART-6 3A: the work order's fields
		assert_true(b.text.begins_with(PSEUDO_PREFIX), "%s: '%s'" % [key, b.text])
	assert_true(String(hq.hud._title).begins_with(PSEUDO_PREFIX), "the raid title")
	var run := hq._panel.find_child("RunRaid", true, false) as Button
	assert_true(_shown_text(run).begins_with(PSEUDO_PREFIX), "START DEFENSE translated")
	await _close(hq)


func test_route_shop_event_loot_words_are_translated_once() -> void:
	_pseudo()
	var scene := _netrun()
	await _frames(6)
	_assert_once(scene, "route")
	var b := scene._panel.find_child("Node1", true, false) as Button
	assert_true(_shown_text(b).contains(PSEUDO_PREFIX), "route choice '%s'" % _shown_text(b))
	for n in scene.city_overlay.nodes:
		if String(n.get("label", "")) != "":
			assert_true(String(n["label"]).contains(PSEUDO_PREFIX), "map label '%s'" % n["label"])
	assert_true(String(scene.hud._title).begins_with(PSEUDO_PREFIX), "NETRUN // ROUTE translated")
	_shop(scene)
	await _frames(4)
	_assert_once(scene, "Mainframe")
	var sign := scene._panel.find_child("MainframeSign", true, false) as MainframeSign
	for w in sign.shown_words():
		assert_true(w.begins_with(PSEUDO_PREFIX), "the sign's '%s'" % w)
	var shred := scene._panel.find_child("RemoveCard", true, false) as ZineCard
	assert_true(shred.card_title.begins_with(PSEUDO_PREFIX), "SHRED A CARD")
	assert_true(shred.buy_button.label_text().begins_with(PSEUDO_PREFIX), "its sticker's verb")
	var slices: Node = scene._panel.find_child("Slices", true, false)
	for t in slices.get_children():
		assert_true((t as ZineCard).card_title.begins_with(PSEUDO_PREFIX), "slice '%s'" % (t as ZineCard).card_title)
	assert_true(String(scene.hud._title).begins_with(PSEUDO_PREFIX), "the Mainframe's title")
	_event(scene)
	await _frames(4)
	_assert_once(scene, "event")
	for n in _all(scene._panel):
		if n is GraffitiScrawl:
			assert_true((n as GraffitiScrawl).text.begins_with(PSEUDO_PREFIX), "PLAY IT SAFE?? translated")
	_loot(scene)
	await _frames(4)
	_assert_once(scene, "loot")
	for n in _all(scene._panel):
		if n is GraffitiTag:
			assert_true((n as GraffitiTag).text.begins_with(PSEUDO_PREFIX), "LOOT: pick a card translated")
	assert_true(String(scene.hud._title).begins_with(PSEUDO_PREFIX), "BREACH PAYOUT translated")
	await _close(scene)


func test_title_words_are_translated_once() -> void:
	RunManager.autosave()
	_pseudo()
	var title := _open(TITLE)
	title.continue_slot = SLOT
	title.show_main()
	await _frames(4)
	_assert_once(title, "title")
	_assert_translated(title._panel, "title")
	# ART-10 4C: the plan is the three verb stickers (1. BREACH ...), each translated once.
	for v in title.verbs:
		assert_true(v.shown_text().begins_with(PSEUDO_PREFIX), "the plan: %s" % v.shown_text())
	await _close(title)


func test_the_twice_check_tells_nesting_from_doubling() -> void:
	assert_true(_doubled("««X»»"), "a translation of a translation")
	assert_true(_doubled("a ««X»» b"))
	assert_false(_doubled("««a» x «b»»"), "a line built from translated parts")
	assert_false(_doubled("«Recruit «Breaker» (10)»"))
	assert_false(_doubled("«X» «Y»"))
	_pseudo()
	var l: Label = add_child_autofree(Label.new())
	l.text = TextDb.t(RunManager.lookup().get_content(&"jolt"), "display_name")
	assert_true(_doubled(_shown_text(l)), "a pre-translated word in an auto-translating label is caught")
	TextDb.shown_as_given(l)
	assert_false(_doubled(_shown_text(l)), "shown as given: once")


func test_content_without_a_key_shows_its_own_text_not_the_key() -> void:
	var card := CardData.new()
	card.id = &"gut_mirror_elite_card"
	card.display_name = "Mirror Thing"
	assert_eq(TextDb.t(card, "display_name"), "Mirror Thing")
	_pseudo()
	var shown := TextDb.t(card, "display_name")
	assert_false(shown.contains("CardData"), "not the key: %s" % shown)
	assert_true(shown.begins_with(PSEUDO_PREFIX) and not shown.begins_with(PSEUDO_PREFIX + PSEUDO_PREFIX), "its own text, pseudolocalised once: %s" % shown)
	var jolt := RunManager.lookup().get_content(&"jolt")
	assert_true(TextDb.t(jolt, "display_name").begins_with(PSEUDO_PREFIX), "a catalogued key translates")


func test_translate_once_with_a_translation() -> void:
	var boost: Resource = null
	for b in RunManager.config().netrun_boosts:
		if b != null:
			boost = b
			break
	var key := TextDb.key_for(boost, "display_name")
	var shown := "XX_BOOST"
	# The translated text is itself a key of the catalogue: shown twice it would change again.
	_translate({key: shown, shown: "TWICE", "CYBERDECK HQ": "XX_HQ", "XX_HQ": "TWICE", "DISPATCH": "XX_DISPATCH", "XX_DISPATCH": "TWICE"})
	var hq := _open(HQ)
	await _frames(4)
	var b := hq._panel.find_child("Boost_%s" % boost.id, true, false) as Button
	assert_string_contains(_shown_text(b), "XX_BOOST", "the boost in the player's language")
	assert_false(_shown_text(b).contains("TWICE"), "and translated once: %s" % _shown_text(b))
	assert_eq(String(hq.hud._title), "XX_HQ")
	assert_eq(Dialogue.speaker_name(RC.Voice.DISPATCH), "XX_DISPATCH", "the speaker's name once")
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, "A line.")
	await _frames(2)
	assert_false(Dialogue.text_label.get_parsed_text().contains("TWICE"), "the bar shows it once: %s" % Dialogue.text_label.get_parsed_text())
	assert_false(Dialogue.speaker_label.can_auto_translate(), "the name label shows it as given")
	await _close(hq)


func test_pad_prompts_translate_their_verbs_once() -> void:
	_translate({"Buy": "XX_BUY", "XX_BUY": "TWICE", "Leave": "XX_LEAVE", "Settings": "XX_SETTINGS"})
	var row: PadPrompts = add_child_autofree(PadPrompts.new())
	Settings.set_pad_active(true)
	row.set_prompts([[&"ui_accept", "Buy"], [&"ui_cancel", "Leave"]])
	var texts := row.texts()
	assert_eq(texts[0], "A  XX_BUY")
	for c in row.get_children():
		if c is Label:
			assert_false((c as Label).can_auto_translate(), "shown as given")
			assert_false(_shown_text(c).contains("TWICE"))
	await _frames(1)


# --- S5 the late-campaign raid map -------------------------------------------------------------------

func test_late_campaign_raid_map_fits_with_its_key_clear() -> void:
	_unlock_all()
	for corp in CORPS:
		for scale in SCALES:
			Settings.set_text_scale(scale)
			RunManager.new_campaign(1, corp)
			_late_campaign()
			var hq := _open(HQ)
			await _frames()
			hq.show_raid()
			await _frames(RAID_SETTLE)
			var area_ctl := hq._panel.find_child("RaidMapArea", true, false) as Control
			var area := area_ctl.get_global_rect().intersection(Rect2(Vector2.ZERO, CANVAS)).grow(1.0)
			var rects := LegendSpot.node_rects(hq.city_overlay, false)
			assert_true(rects.size() >= LATE_CLAIMS, "%s: the late network on the map (%d)" % [corp, rects.size()])
			for r in rects:
				assert_true(area.encloses(r), "%s at %.1f: node %s inside the map area %s (strip %s)" % [corp, scale, r, area, hq.raid_legend_is_strip()])
			var legend: MapLegend = hq.raid_legend
			if legend.is_visible_in_tree():
				var lr := Rect2(legend.global_position, legend.size * legend.scale)
				for r in LegendSpot.node_rects(hq.city_overlay, true):
					assert_false(lr.intersects(r), "%s at %.1f: the key %s covers a node or label at %s (strip %s)" % [corp, scale, lr, r, hq.raid_legend_is_strip()])
			await _close(hq)


# --- S6 B-back only from a pad -----------------------------------------------------------------------

func test_a_keyboard_esc_never_leaves_when_settings_is_rebound() -> void:
	var saved := InputMap.action_get_events(&"open_settings").duplicate()
	InputMap.action_erase_events(&"open_settings")
	var f10 := InputEventKey.new()
	f10.physical_keycode = KEY_F10
	InputMap.action_add_event(&"open_settings", f10)
	var esc := InputEventKey.new()
	esc.physical_keycode = KEY_ESCAPE
	esc.keycode = KEY_ESCAPE
	esc.pressed = true
	assert_true(esc.is_action_pressed("ui_cancel"), "Esc is ui_cancel")
	var pad := InputEventJoypadButton.new()
	pad.button_index = JOY_BUTTON_B
	pad.pressed = true
	var scene := _netrun()
	await _frames()
	_shop(scene)
	await _frames()
	scene._unhandled_input(esc)
	await _frames()
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.SHOP, "a keyboard's Esc stays in the Mainframe")
	scene._unhandled_input(pad)
	await _frames()
	assert_ne(RunManager.netrun.run.phase, RunState.Phase.SHOP, "a pad's B leaves it")
	await _close(scene)
	RunManager.new_campaign(1)
	_raid_campaign()
	var hq := _open(HQ)
	await _frames()
	hq.show_grid()
	await _frames()
	hq._unhandled_input(esc)
	await _frames()
	assert_eq(hq.panel_name, "grid", "a keyboard's Esc stays on the Grid")
	hq._unhandled_input(pad)
	await _frames()
	assert_eq(hq.panel_name, "hq", "a pad's B goes back to the HQ")
	await _close(hq)
	InputMap.action_erase_events(&"open_settings")
	for ev in saved:
		InputMap.action_add_event(&"open_settings", ev)


# --- S7 the SAVED stamp ------------------------------------------------------------------------------

func _assert_saved_clear(root: Node, what: String) -> void:
	var saved_at := Engine.get_process_frames()
	await _frames(2)
	# Placed after the save, on the new page (it may have faded already on a slow frame).
	assert_true(Fx.saved_placed_frame > saved_at, "%s: SAVED placed after the save (frame %d > %d)" % [what, Fx.saved_placed_frame, saved_at])
	var r := Rect2(Fx.saved_label.position, Fx.saved_label.size)
	assert_true(Rect2(Vector2.ZERO, CANVAS).encloses(r), "%s: SAVED on screen %s" % [what, r])
	for c in _controls(root):
		assert_false(r.intersects(_shown_rect(c)), "%s: SAVED %s covers %s '%s' at %s (text %.1f, pad %s)" % [what, r, c.get_class(), c.get("text"), _shown_rect(c), Settings.text_scale, Settings.pad_active])


func test_the_saved_stamp_is_placed_on_the_page_it_lands_on() -> void:
	for pad in [false, true]:
		for scale in [1.0, Settings.TEXT_SCALE_MAX]:
			Settings.set_text_scale(scale)
			Settings.set_pad_active(pad)
			var hq := _open(HQ)
			await _frames()
			hq.new_campaign(1)  # saves before its page is built
			await _assert_saved_clear(hq, "HQ new campaign")
			_raid_campaign()
			hq.show_raid()
			await _frames(RAID_SETTLE)
			RunManager.autosave()
			await _assert_saved_clear(hq, "raid setup")
			await _close(hq)
			RunManager.new_campaign(1)
			var scene := _netrun()
			await _frames(8)
			RunManager.autosave()
			await _assert_saved_clear(scene, "route")
			_shop(scene)
			await _frames()
			RunManager.autosave()
			await _assert_saved_clear(scene, "Mainframe")
			await _close(scene)
	Settings.set_pad_active(false)


# --- S8 the pager's first page ------------------------------------------------------------------------

func test_the_first_page_always_carries_words() -> void:
	var hq := _open(HQ)
	await _frames()
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		await _frames(2)
		var width := Dialogue.default_rect.size.x
		var font := Palette.mono()
		var fs := Dialogue.text_label.get_theme_font_size("normal_font_size")
		# One unbreakable word that fits a line alone but not after the name (a CJK line has
		# no spaces; an override-pseudolocalised word can grow as long).
		var ch := "字"
		var word := ""
		while font.get_string_size(word + ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x < width * 0.8:
			word += ch
		for words in [word, word + " " + word, "ABCDEFGHIJ".repeat(4)]:
			Dialogue.clear()
			Dialogue.say(RC.Voice.DISPATCH, words)
			await _frames(2)
			var first := Dialogue.current_text().replace(Dialogue.CONTINUED_MARK, "").strip_edges()
			assert_ne(first, "", "the first page carries words, not the name alone (text %.1f): '%s'" % [scale, Dialogue.text_label.get_parsed_text()])
			var pages := Dialogue.pages_of("%s: %s" % [Dialogue.speaker_name(RC.Voice.DISPATCH), words], Dialogue.speaker_name(RC.Voice.DISPATCH) + ":")
			assert_true(pages[0].length() > (Dialogue.speaker_name(RC.Voice.DISPATCH) + ": ").length(), "page one: '%s'" % pages[0])
			assert_eq("".join(pages).replace(" ", ""), ("%s: %s" % [Dialogue.speaker_name(RC.Voice.DISPATCH), words]).replace(" ", ""), "nothing lost between pages")
	await _close(hq)


# --- S9 the event's choices ----------------------------------------------------------------------------

func test_event_choices_stay_on_screen_and_no_change_shows_a_mark() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames()
		_event(scene)
		await _frames(4)
		var ev := RunManager.netrun.current_event()
		for i in ev.choices.size():
			var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
			var r := b.get_global_rect()
			assert_true(r.end.x <= CANVAS.x - NetrunScene_EVENT_RIGHT_GAP() * scale + 0.5, "choice %d ends at %.0f, clear of the edge (text %.1f)" % [i, r.end.x, scale])
			var row := b.find_child("OutcomeRow", false, false) as OutcomeRow
			assert_not_null(row, "choice %d shows its outcome as icons" % i)
		await _close(scene)
	var s: NetrunSession = null
	var nothing := EventChoiceData.new()
	RunManager.new_campaign(1)
	var scene2 := _netrun()
	await _frames()
	s = RunManager.netrun
	assert_true(OutcomeRow.shown(OutcomeRow.of_choice(s, nothing)).is_empty(), "a choice that changes nothing")
	var none := OutcomeRow.no_change()
	assert_eq(none.size(), 1)
	assert_eq(StringName(none[0]["kind"]), OutcomeRow.NO_CHANGE, "shows the neutral mark")
	assert_ne(String(none[0]["text"]), "", "and says so")
	await _close(scene2)


func NetrunScene_EVENT_RIGHT_GAP() -> float:
	return load("res://scripts/ui/netrun_scene.gd").EVENT_RIGHT_GAP


# --- S10 the Mainframe's tiles -------------------------------------------------------------------------

func _parts_apart(card: ZineCard, what: String) -> void:
	var inside := Rect2(Vector2.ZERO, card.size).grow(0.5)
	var buy := Rect2(card.buy_button.position, card.buy_button.size) if card.buy_button != null else Rect2()
	if buy.has_area():
		assert_true(inside.encloses(buy), "%s: the buy sticker %s inside its tile %s" % [what, buy, card.size])
	if card.look == ZineCard.Look.STICKER:
		var p := card.sticker_parts()
		for r in p["body"]:
			assert_true(inside.encloses(r), "%s: body line %s inside" % [what, r])
			if buy.has_area():
				assert_false((r as Rect2).intersects(buy), "%s: body line %s under the sticker %s" % [what, r, buy])
		if p.has("pictos") and buy.has_area():
			assert_false((p["pictos"] as Rect2).intersects(buy), "%s: pictograms under the sticker" % what)
		assert_false(p.has("chip") and buy.has_area(), "%s: no chip mark under a buy sticker" % what)
		return
	var t := card.tile_parts()
	var icon: Rect2 = t["icon"]
	assert_true(inside.encloses(icon), "%s: the icon %s inside the tile %s" % [what, icon, card.size])
	var texts: Array[Rect2] = []
	texts.append_array(t["names"])
	texts.append_array(t["desc"])
	for r in texts:
		assert_true(inside.encloses(r), "%s: text %s inside the tile %s" % [what, r, card.size])
		assert_false(r.intersects(icon), "%s: text %s over the icon %s" % [what, r, icon])
		if buy.has_area():
			assert_false(r.intersects(buy), "%s: text %s under the sticker %s" % [what, r, buy])
	if buy.has_area():
		assert_false(icon.intersects(buy), "%s: the icon %s under the sticker %s" % [what, icon, buy])


func test_mainframe_text_icons_and_stickers_never_overlap() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		_shop(scene)
		await _frames(4)
		var items := 0
		for n in _all(scene._panel):
			if n is ZineCard:
				items += 1
				_parts_apart(n as ZineCard, "%s at %.1f" % [(n as ZineCard).card_title, scale])
				var buy := (n as ZineCard).buy_button
				if buy != null:
					var own := (n as ZineCard).text_scale
					assert_true(buy.lettering_px() >= roundi(BuyButton.BUY_FONT * own * BuyButton.TWO_LINES_BELOW) or buy.shown_lines().size() > 1,
						"%s: the sticker's words keep near the text size (%d px at %.1f)" % [(n as ZineCard).card_title, buy.lettering_px(), own])
					assert_true(buy.lettering_px() >= roundi(BuyButton.BUY_FONT * minf(scale, 1.3) * 0.75), "%s: the price scales with the text (%d px at %.1f)" % [(n as ZineCard).card_title, buy.lettering_px(), scale])
		assert_true(items >= 5)
		var shred := scene._panel.find_child("RemoveCard", true, false) as ZineCard
		assert_false(shred.tile_parts()["names"].is_empty(), "SHRED A CARD shows its name")
		await _close(scene)


# --- S11 the crew dossiers --------------------------------------------------------------------------

func test_every_crew_dossier_is_reachable_at_big_text() -> void:
	var c := RunManager.campaign
	while c.roster.size() < 3:
		c.recruit(RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData)
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var hq := _open(HQ)
		await _frames(6)
		var scroll := hq.find_child("PageScroll", true, false) as ScrollContainer
		var view := scroll.get_global_rect()
		var cards: Array[CrewCard] = []
		for n in _all(hq._panel):
			if n is CrewCard:
				cards.append(n)
		assert_eq(cards.size(), c.roster.size(), "a dossier per operative")
		for card in cards:
			assert_true(card.get_combined_minimum_size().y <= view.size.y, "%s fits the page's view (%.0f in %.0f)" % [card.name, card.get_combined_minimum_size().y, view.size.y])
			scroll.ensure_control_visible(card)
			await _frames(2)
			var r := card.get_global_rect()
			assert_true(view.grow(1.0).encloses(r), "%s: whole on screen once scrolled to (%s in %s, text %.1f)" % [card.name, r, view, scale])
			var loadout := card.find_child("Loadout", true, false) as Button
			loadout.grab_focus()
			await _frames(2)
			assert_true(view.grow(1.0).encloses(loadout.get_global_rect()), "%s's Loadout reachable by pad" % card.name)
		if scale > 1.0:
			assert_true(CrewCard.is_compact(), "compact dossiers at big text")
			assert_almost_eq(cards[0].get_global_rect().position.y, cards[1].get_global_rect().position.y, 1.0,
				"the first two dossiers side by side at big text: %s, %s" % [cards[0].get_global_rect(), cards[1].get_global_rect()])
		var radio := hq._panel.find_child("PirateRadio", true, false) as CrtText  # ART-10 4C: terminal text
		assert_false(radio.label.get_parsed_text().contains("RC1-"), "no share code on the lore note")
		assert_string_contains(radio.tooltip_text, "RC1-", "it is in the note's tooltip")
		hq.open_settings()
		await _frames()
		var seed_line := hq._settings_panel.find_child("SeedLine", true, false) as Label
		assert_not_null(seed_line, "Settings has the seed line")
		assert_string_contains(seed_line.text, CampaignCode.of(RunManager.campaign, RunManager.campaign.start_class_id))
		hq.open_settings()
		await _close(hq)


# --- S12 the route ----------------------------------------------------------------------------------

func test_route_nodes_clear_of_the_route_column_and_choices_told_apart() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames(24)
		var col := scene._panel.find_child("RouteColumn", true, false) as Control
		var win := scene._panel.find_child("RouteWindow", true, false) as Control
		for r in LegendSpot.node_rects(scene.city_overlay, false):
			assert_false(win.get_global_rect().intersects(r), "a node %s under the ROUTE window %s (text %.1f)" % [r, win.get_global_rect(), scale])
			assert_false(col.get_global_rect().intersects(r), "a node %s under the route column (text %.1f)" % [r, scale])
			assert_true(Rect2(Vector2.ZERO, CANVAS).encloses(r), "on screen: %s" % r)
		var legend: RouteLegend = scene.route_legend
		for k in RouteLegend.COLOR_KEYS:
			assert_not_null(legend.body.find_child("Color_%s" % k, true, false), "the key says what %s nodes are" % k)
		# Each choice says where it leads; the tooltips of two fights differ.
		var s := RunManager.netrun
		var tips := {}
		for i in s.available_nodes().size():
			var b := scene._panel.find_child("Node%d" % (i + 1), true, false) as Button
			var node := s.run.map.get_node(s.available_nodes()[i])
			var ahead: String = scene.ahead_words(s.run.map, node)
			if ahead != "":
				assert_string_contains(b.text, ahead, "choice %d says where it leads" % (i + 1))
			assert_string_contains(b.tooltip_text, "Cycles" if int(node["type"]) == RC.InfilNodeType.ROUTER else "", "what it pays")
			tips[b.tooltip_text] = true
		await _close(scene)


# --- S13 the title's Continue line ----------------------------------------------------------------------

func test_the_continue_line_reads_as_a_line_of_icons() -> void:
	RunManager.campaign.heat = 14
	RunManager.autosave()
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var title := _open(TITLE)
		title.continue_slot = SLOT
		title.show_main()
		await _frames(4)
		# ART-10 4C (round 33): BREACH's terminal chip reads CONTINUE with the slot line under it
		# ("slot // corp // run N // Heat H"); at big text the line moves into the tooltip.
		var cont := title._panel.find_child("Continue", true, false) as MenuChip
		assert_not_null(cont, "Continue offers the slot")
		assert_eq(cont.text, "Continue", "one word on its own line")
		if scale <= 1.0:
			assert_string_contains(cont.line, TextDb.t(RunManager.corporation, "display_name"), "the saved campaign as a line under it")
			assert_string_contains(cont.line, "Heat 14")
		assert_string_contains(cont.tooltip_text, "Heat 14", "the tooltip says it in words")
		await _close(title)
	var src := FileAccess.get_file_as_string("res://tools/playtest/storyboard.gd")
	assert_string_contains(src, "continue_slot = SLOT", "the storyboard's title shows its own slot")


# --- S14 the raid setup ---------------------------------------------------------------------------------

func test_defence_cards_say_what_they_do_and_the_button_says_defend() -> void:
	for scale in SCALES:
		var hq: Control = await _raid(scale)
		var run := hq._panel.find_child("RunRaid", true, false) as Button
		assert_eq(run.text, "START DEFENSE")
		assert_false(TextDb.ui_text("ui.raid_intro").contains("RUN THE RAID"), "the opening line says it too")
		for n in _all(hq._panel):
			if n is AssetCard:
				var card := n as AssetCard
				assert_ne(card.effect_text, "", "%s says what it does" % card.asset_id)
				assert_ne(card.effect_kind, "", "%s has a pictogram" % card.asset_id)
				var er := card.effect_rect()
				assert_true(Rect2(Vector2.ZERO, card.size).encloses(er), "%s: the effect line on the card at %.1f" % [card.asset_id, scale])
		var loadout := hq._panel.find_child("DefenseLoadout", true, false) as TerminalWindow
		assert_string_contains(loadout.title, hq.armory_words(), "the same ARMORY words as the HQ")
		assert_ne(loadout.tooltip_text, "", "and explained")
		await _close(hq)
	var hq2 := _open(HQ)
	await _frames()
	var badge := hq2._panel.find_child("ArmoryBadge", true, false) as Badge
	assert_eq(badge.text, hq2.armory_words(), "HQ's ARMORY badge: the same count")
	assert_string_contains(badge.tooltip_text.replace("\n", " "), "not counting those deployed")  # ART-0 C: folded narrower at 2.0
	await _close(hq2)
	assert_eq(AssetCard.effect_of(RunManager.lookup().get_content(&"ice_lock"))[0], "hold")
	assert_eq(AssetCard.effect_of(RunManager.lookup().get_content(&"decoy"))[0], "lure")
	assert_eq(AssetCard.effect_of(RunManager.lookup().get_content(&"turret"))[0], "shoot")


# --- S15 screen-tied subtitles ----------------------------------------------------------------------------

func test_a_screen_line_ends_when_its_screen_is_left() -> void:
	var scene := _netrun()
	await _frames(4)
	# start_run spoke the jack-in line on the route.
	Dialogue.clear()
	Dialogue.enter_screen("route")
	Dialogue.speak("run_start", RC.Voice.DISPATCH, RunManager.campaign.corporation_id, &"", 0, "route")
	Dialogue.say(RC.Voice.DISPATCH, "Heat went up.")  # news: no scope
	await _frames()
	assert_eq(Dialogue.shown_scope(), "route", "the jack-in line shows on the route")
	_shop(scene)
	await _frames(2)
	assert_ne(Dialogue.shown_scope(), "route", "gone on the Mainframe")
	assert_string_contains(Dialogue.current_text(), "Heat went up.", "the news line plays on")
	Dialogue.say(RC.Voice.DISPATCH, "On the event.", 0.0, &"", false, "event")
	_event(scene)
	await _frames(2)
	# ANIM-R6 B12: the event's story stays on its paper; a line of the event's screen takes the bar.
	assert_eq(Dialogue.shown_scope(), "event", "the event's own line takes the bar")
	await _close(scene)
	# The briefing said at HQ belongs to the route.
	Dialogue.clear()
	Dialogue.enter_screen("grid")
	Dialogue.say(RC.Voice.DISPATCH, "Briefing.", 0.0, &"", false, "route")
	Dialogue.enter_screen("route")
	assert_eq(Dialogue.shown_scope(), "route", "a line for the next screen survives the switch")


# --- S16 the top bar's captions ---------------------------------------------------------------------------

func test_the_top_bar_says_whose_numbers_it_shows() -> void:
	var hq := _open(HQ)
	await _frames(4)
	var stats: HudStats = hq.hud.stats
	assert_true(stats.captions_shown(), "HQ: a caption")
	assert_eq(String(stats.captions[0][1]), "CAMPAIGN")
	for i in stats.items.size():
		assert_ne(String(stats.items[i][3]), "", "tag %s has a tooltip" % stats.items[i][0])
	var caps := stats.caption_rects()
	var tags := stats.tag_rects()
	for cr in caps:
		for tr in tags:
			assert_false(cr.intersects(tr), "a caption %s on a tag %s" % [cr, tr])
	assert_ne(stats._get_tooltip(caps[0].get_center()), "", "the caption explains itself")
	await _close(hq)
	var scene := _netrun()
	await _frames(4)
	var rs: HudStats = scene.hud.stats
	var words := []
	for cp in rs.captions:
		words.append(cp[1])
	assert_eq(words, ["CAMPAIGN", "THIS RUN"], "a run: the campaign's numbers, then the run's")
	for i in rs.items.size():
		assert_ne(String(rs.items[i][3]), "", "run tag %s has a tooltip" % rs.items[i][0])
	await _close(scene)


# --- S17 the whole text on hover and focus -------------------------------------------------------------------

func test_loot_and_mainframe_cards_show_their_whole_text_on_focus() -> void:
	var scene := _netrun()
	await _frames()
	Settings.set_pad_active(true)
	_loot(scene)
	await _frames()
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	for card in stickers.get_children():
		var zc := card as ZineCard
		var res := RunManager.lookup().get_content(StringName(String(RunManager.netrun.run.pending_rewards[0]["options"][card.get_index()])))
		var desc := TextDb.t(res, "description")
		assert_string_contains(zc.tooltip_text.replace("\n", " "), desc.left(20), "loot %s: the whole text on hover" % zc.card_title)
		zc.grab_focus()
		await _frames(2)
		assert_not_null(FocusTip.tip_of(zc), "loot %s: the whole text on focus" % zc.card_title)
	_shop(scene)
	await _frames()
	var shop_cards: Array[ZineCard] = []
	for n in _all(scene._panel):
		if n is ZineCard:
			shop_cards.append(n)
	for zc in shop_cards:
		if true:
			assert_ne(zc.tooltip_text, "", "%s: a tooltip" % zc.card_title)
			zc.grab_focus()
			await _frames(2)
			assert_not_null(FocusTip.tip_of(zc), "%s: the whole text on focus" % zc.card_title)
	Settings.set_pad_active(false)
	await _close(scene)
