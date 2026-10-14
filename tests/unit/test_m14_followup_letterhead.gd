extends GutTest
## M14 FOLLOW-UP (art director, 2026-10-11): every corporation letters its paper with its own
## letterhead name (CorporationData.letterhead_name, "MERIDIAN FREIGHT"), routed through TextDb.
## At text scale 1.0 / 1.6 / 2.0 every corp-paper letterhead (the raid work order and report, the
## corp memo, the operative dossier, the audit dossier) shows it whole, left of the seal, with no
## ellipsis; the full legal name stays in the bodies. A corp with no letterhead name keeps the old
## fit (its display name, the ellipsis as the fallback). Views never change state.

const SCALES: Array[float] = [1.0, 1.6, 2.0]
## The corp memo's width on the event screen (NetrunScene.EVENT_MEMO_W).
const MEMO_W := 470.0

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_letterhead"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 1) -> void:
	for i in n:
		await get_tree().process_frame


func _corp(id: StringName) -> CorporationData:
	return RunManager.lookup().get_content(id) as CorporationData


## `lh`'s letterhead lettered whole: its name, every line in the room, no ellipsis, never under 1.0.
func _assert_whole(lh: CorpPaperPanel, want: String, tag: String) -> void:
	var fit := lh.letterhead_fit()
	var lines: PackedStringArray = fit["lines"]
	assert_eq(lh.letterhead_text(), want, "%s: the letterhead letters the letterhead name" % tag)
	assert_eq(" ".join(lines), want, "%s: whole (%s)" % [tag, lines])
	for line in lines:
		assert_false(line.contains(CorpPaperPanel.ELLIPSIS), "%s: no ellipsis in '%s'" % [tag, line])
		var w := Palette.body_medium().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, int(fit["px"])).x
		assert_lte(w, lh.name_width() + 0.5, "%s: '%s' in its room (%.0f in %.0f)" % [tag, line, w, lh.name_width()])
	assert_gte(int(fit["px"]), UiTheme.font_px_at(UiTheme.LABEL, 1.0), "%s: never smaller than at 1.0" % tag)
	# On the sheet: the first line's top stays below the sheet's top (the memo's rose over it at 2.0).
	var f := Palette.body_medium()
	var px := int(fit["px"])
	var top := lh.top_pad + lh.head_h - UiTheme.SP_M - f.get_height(px) * float(lines.size() - 1) - f.get_ascent(px)
	assert_gte(top, 0.0, "%s: the name stands on the sheet (top %.1f)" % [tag, top])


func test_every_corp_has_a_short_letterhead_name_through_textdb() -> void:
	for id: StringName in RaidSkin.CORPS:
		var corp := _corp(id)
		assert_not_null(corp, "%s: in content" % id)
		assert_ne(corp.letterhead_name, "", "%s: has a letterhead name" % id)
		assert_eq(corp.letterhead_errors().size(), 0, "%s: in capitals, a short form" % id)
		assert_true(TextDb.has_message(TextDb.key_for(corp, "letterhead_name")), "%s: a TextDb key in strings.csv" % id)
		assert_eq(CorpPaperPanel.letterhead_of(corp), TextDb.t(corp, "letterhead_name").to_upper(), "%s: read through TextDb" % id)
	assert_eq(_corp(&"meridian").letterhead_name, "MERIDIAN FREIGHT", "the art director's own example")
	assert_eq(CorpPaperPanel.letterhead_of(null), "", "no corp: no letterhead name")


func test_the_raid_papers_letter_the_letterhead_name_whole_left_of_the_seal() -> void:
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		for id: StringName in RaidSkin.CORPS:
			for stamp in [RaidPaper.STAMP_INTERCEPTED, RaidPaper.STAMP_CLASSIFIED]:
				var sheet := RaidPaper.new(id, "COLLECTIONS: FIRST NOTICE", stamp, "WO 25-SB-452")
				add_child_autofree(sheet)
				sheet.size = Vector2(HqLayout.ORDER_WIDTH * HqLayout.words_scale(scale), 400.0)
				await _frames()
				var tag := "x%.1f %s %s" % [scale, id, stamp]
				_assert_whole(sheet.paper, _corp(id).letterhead_name, tag)
				assert_lte(UiTheme.SP_L + sheet.paper.name_width(), sheet.size.x - sheet.seal_reserve() + 0.5, "%s: left of the seal" % tag)
				assert_eq(sheet.paper.corp_name, TextDb.t(_corp(id), "display_name").to_upper(), "%s: the full name stays for the footer" % tag)
				sheet.queue_free()


func test_the_memo_and_the_operative_dossier_letter_it_whole() -> void:
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		for id: StringName in RaidSkin.CORPS:
			var corp := _corp(id)
			var tag := "x%.1f %s" % [scale, id]
			var memo := CorpMemo.new(TextDb.t(corp, "display_name"), Palette.corp_color(id), scale, CorpPaperPanel.letterhead_of(corp))
			add_child_autofree(memo)
			memo.custom_minimum_size = Vector2(MEMO_W, 0)
			memo.size = Vector2(MEMO_W, 300.0)
			await _frames()
			_assert_whole(memo.sheet, corp.letterhead_name, "%s memo" % tag)
			assert_eq(memo.corp_name, TextDb.t(corp, "display_name"), "%s memo: the routing line keeps the full name" % tag)
			var d := OperativeDossier.new()
			add_child_autofree(d)
			d.show_file({"corp": TextDb.t(corp, "display_name"), "letterhead": CorpPaperPanel.letterhead_of(corp), "corp_color": Palette.corp_color(id),
				"subject": "Vex", "class_word": "Runner", "class_id": "runner", "operative_id": "op_vex", "rank": 2, "hp": 20, "max_hp": 24,
				"ram": 4, "wheel": ["A", "B"], "hub": "Core", "deck": 12, "station": ["+1 ICE"]})
			d.size = d.custom_minimum_size
			await _frames()
			_assert_whole(d.paper, corp.letterhead_name, "%s dossier" % tag)
			memo.queue_free()
			d.queue_free()


func test_the_audit_dossier_letterhead_shows_the_letterhead_name() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	c.outcome = CampaignState.Outcome.LOST
	var facts := DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), func(id: StringName) -> String: return String(id),
		func(id: StringName) -> String: return String(id), [] as Array[Dictionary], 3)
	assert_eq(facts.corporation_letterhead, CorpPaperPanel.letterhead_of(RunManager.corporation), "the facts carry the letterhead name")
	for id: StringName in RaidSkin.CORPS:
		facts.corporation_id = id
		facts.corporation_name = TextDb.t(_corp(id), "display_name")
		facts.corporation_letterhead = CorpPaperPanel.letterhead_of(_corp(id))
		var dossier: AuditDossier = add_child_autofree(AuditDossier.new(facts))
		var style := CorpHouseStyle.of(id)
		var want := style.name_shown("").to_upper() if style.house_name != "" else _corp(id).letterhead_name
		var shown := dossier.find_child("LetterheadName", true, false) as Label
		assert_eq(shown.text, want, "%s: the house's own signature, else its letterhead name" % id)
		assert_false(shown.text.contains(CorpPaperPanel.ELLIPSIS), "%s: whole" % id)
		dossier.queue_free()


func test_a_corp_without_a_letterhead_name_keeps_the_ellipsis_fallback() -> void:
	var f := Palette.body_medium()
	var panel := CorpPaperPanel.new()
	add_child_autofree(panel)
	panel.corp_name = "SUPERCALIFRAGILISTIC EXPIALIDOCIOUS HOLDINGS"
	panel.size = Vector2(160.0, 200.0)
	await _frames()
	assert_eq(panel.letterhead_text(), panel.corp_name, "no letterhead name: the display name")
	var cut: PackedStringArray = panel.letterhead_fit()["lines"]
	assert_true(cut[-1].ends_with(CorpPaperPanel.ELLIPSIS), "too long: cut with an ellipsis (%s)" % [cut])
	# The pure whole fit: a name that fit_name would cut stands whole at a smaller size.
	var whole := CorpPaperPanel.fit_whole(f, "SUPERCALIFRAGILISTIC", 36, 18, 60.0, 80.0)
	assert_eq(Array(whole["lines"]), ["SUPERCALIFRAGILISTIC"], "whole, never cut")
	assert_lt(int(whole["px"]), 18, "below the 1.0 size only when nothing else fits")
	assert_lte(f.get_string_size("SUPERCALIFRAGILISTIC", HORIZONTAL_ALIGNMENT_LEFT, -1, int(whole["px"])).x, 60.0, "in its room")
	var roomy := CorpPaperPanel.fit_whole(f, "MERIDIAN FREIGHT", 36, 18, 2000.0, 80.0)
	assert_eq(roomy, CorpPaperPanel.fit_name(f, "MERIDIAN FREIGHT", 36, 18, 2000.0, 80.0), "the same as fit_name when it fits")
