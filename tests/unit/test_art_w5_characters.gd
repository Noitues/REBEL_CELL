extends GutTest
## Art pass W5 (ART_BIBLE 7.1, 7.2, 12; STYLE_GUIDE 7): characters. The eight classes have
## distinct silhouettes and accents; per-operative variation stays inside the class; four
## expressions exist and default to neutral; enemies carry their corp hue and pattern.

## Least silhouette difference between any two classes (cells in one mask only over
## cells in either).
const MIN_CLASS_DIFFERENCE := 0.12
## Operatives sampled per class for the variation checks.
const OPS_PER_CLASS := 10


func _mask(subj: Dictionary) -> PackedByteArray:
	return PortraitArt.silhouette_mask(subj)


# --- Item 1: eight class silhouettes and accents ------------------------------------------

func test_the_eight_classes_are_the_content_classes() -> void:
	for c in PortraitArt.CLASS_IDS:
		assert_true(ResourceLoader.exists("res://content/classes/%s.tres" % c), "content class %s" % c)
		assert_true(Palette.CLASS_ACCENTS.has(c), "%s has a §7.1 accent" % c)
	assert_eq(PortraitArt.CLASS_IDS.size(), 8)


func test_no_two_classes_share_a_silhouette() -> void:
	var masks := {}
	for c in PortraitArt.CLASS_IDS:
		masks[c] = _mask(PortraitArt.operative_subject(c))
	var lowest := 1.0
	var pair := ""
	for i in PortraitArt.CLASS_IDS.size():
		for j in range(i + 1, PortraitArt.CLASS_IDS.size()):
			var a: StringName = PortraitArt.CLASS_IDS[i]
			var b: StringName = PortraitArt.CLASS_IDS[j]
			var d := PortraitArt.mask_difference(masks[a], masks[b])
			if d < lowest:
				lowest = d
				pair = "%s/%s" % [a, b]
			assert_gt(d, MIN_CLASS_DIFFERENCE, "%s and %s silhouettes differ (%.3f)" % [a, b, d])
	gut.p("closest classes: %s %.3f" % [pair, lowest])


func test_no_two_classes_share_a_tint() -> void:
	var seen := {}
	for c in PortraitArt.CLASS_IDS:
		var accent := Palette.class_accent(c)
		assert_false(seen.has(accent.to_html()), "%s has its own accent" % c)
		seen[accent.to_html()] = c
		assert_eq(PortraitArt.operative_subject(c)["accent"], accent, "%s portrait uses Palette.class_accent" % c)


func test_operative_variation_stays_within_the_class() -> void:
	for c in PortraitArt.CLASS_IDS:
		var base := _mask(PortraitArt.operative_subject(c))
		var looks := {}
		for k in OPS_PER_CLASS:
			var subj := PortraitArt.operative_subject(c, StringName("op_%d" % k))
			looks["%d/%d/%s" % [subj["hair"], subj["visor"], subj["tint"].to_html()]] = true
			# The tint is a shade of this class's accent: nearer it than any other accent.
			var tint: Color = subj["tint"]
			var own := _dist(tint, Palette.class_accent(c))
			for other in PortraitArt.CLASS_IDS:
				if other != c:
					assert_lt(own, _dist(tint, Palette.class_accent(other)), "%s op_%d tint stays nearest its accent (not %s)" % [c, k, other])
			# The silhouette stays nearest its own class's.
			var m := _mask(subj)
			var d_own := PortraitArt.mask_difference(m, base)
			for other in PortraitArt.CLASS_IDS:
				if other != c:
					assert_lt(d_own, PortraitArt.mask_difference(m, _mask(PortraitArt.operative_subject(other))), "%s op_%d reads as its class, not %s" % [c, k, other])
		assert_gt(looks.size(), 1, "%s operatives vary" % c)


func _dist(a: Color, b: Color) -> float:
	return Vector3(a.r - b.r, a.g - b.g, a.b - b.b).length()


func test_every_look_draws_every_class_and_expression() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(120, 120)
	var was := PortraitArt.style
	for st in PortraitArt.STYLE_NAMES.size():
		PortraitArt.style = st
		for c in PortraitArt.CLASS_IDS:
			for e in PortraitArt.EXPRESSION_NAMES.size():
				var subj := PortraitArt.operative_subject(c, &"op_1", "", e)
				holder.draw.connect(PortraitArt.draw.bind(holder, Rect2(0, 0, 120, 120), subj), CONNECT_ONE_SHOT)
				holder.queue_redraw()
				await get_tree().process_frame
	PortraitArt.style = was
	assert_true(true, "four looks x eight classes x four expressions drew without errors")


# --- Item 2: four expressions --------------------------------------------------------------

func test_four_expressions_exist_and_default_to_neutral() -> void:
	assert_eq(PortraitArt.EXPRESSION_NAMES, ["NEUTRAL", "HURT", "TRIUMPHANT", "FLATLINED"] as Array[String])
	assert_eq(PortraitArt.operative_subject(&"ghost", &"op_1")["expression"], PortraitArt.Expr.NEUTRAL, "subjects default to neutral")
	var p := Polaroid.new("Vex", "[GHOST PORTRAIT]")
	add_child_autofree(p)
	assert_eq(p.expression, PortraitArt.Expr.NEUTRAL, "a Polaroid defaults to neutral")
	p.set_operative(&"ghost", &"op_1")
	assert_eq(p.subject["expression"], PortraitArt.Expr.NEUTRAL)
	for e in [PortraitArt.Expr.HURT, PortraitArt.Expr.TRIUMPHANT, PortraitArt.Expr.FLATLINED]:
		p.set_expression(e)
		assert_eq(p._subject()["expression"], e, "set_expression shows %s" % PortraitArt.EXPRESSION_NAMES[e])


func test_expressions_change_the_face() -> void:
	var r := Rect2(0, 0, 100, 100)
	for c in PortraitArt.CLASS_IDS:
		var n := PortraitArt.shapes(r, PortraitArt.operative_subject(c))
		var hurt := PortraitArt.shapes(r, PortraitArt.operative_subject(c, &"", "", PortraitArt.Expr.HURT))
		var up := PortraitArt.shapes(r, PortraitArt.operative_subject(c, &"", "", PortraitArt.Expr.TRIUMPHANT))
		var flat := PortraitArt.shapes(r, PortraitArt.operative_subject(c, &"", "", PortraitArt.Expr.FLATLINED))
		assert_ne(hurt["head"], n["head"], "%s hurt turns the head" % c)
		assert_ne(hurt["mouth"], n["mouth"], "%s hurt grimaces" % c)
		assert_true((hurt.get("hurt", []) as Array).size() > 0, "%s hurt shows scratches" % c)
		assert_true(up.get("glow", false), "%s triumphant eyes glow" % c)
		assert_gt((up["props"] as Array).size(), (n["props"] as Array).size(), "%s triumphant raises a fist" % c)
		assert_eq((flat["eyes"] as Array).size(), 0, "%s flatlined: no lit eyes" % c)
		assert_eq((flat.get("cross", []) as Array).size(), 4, "%s flatlined: crossed-out eyes" % c)


func test_flatlined_is_grey() -> void:
	var subj := PortraitArt.operative_subject(&"breaker", &"", "", PortraitArt.Expr.FLATLINED)
	var g := PortraitArt._k(subj, Palette.CELL_PINK)
	assert_almost_eq(g.r, g.g, 0.001, "grey")
	assert_almost_eq(g.g, g.b, 0.001, "grey")
	assert_eq(PortraitArt._k(PortraitArt.operative_subject(&"breaker"), Palette.CELL_PINK), Palette.CELL_PINK, "neutral keeps colour")


# --- Item 3: enemies and bosses ---------------------------------------------------------------

func _enemies() -> Array[EnemyData]:
	var out: Array[EnemyData] = []
	for f in DirAccess.get_files_at("res://content/enemies"):
		if f.ends_with(".tres"):
			out.append(load("res://content/enemies/" + f) as EnemyData)
	return out


func test_enemies_use_their_corp_hue_and_pattern() -> void:
	var corps := [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
	var seen_corps := {}
	for e in _enemies():
		var subj := PortraitArt.enemy_data_subject(e)
		assert_eq(subj["tint"], Palette.corp_color(e.corporation_id), "%s in its corp hue" % e.id)
		assert_eq(PortraitArt.pattern_of(subj), Palette.corp_pattern_id(e.corporation_id), "%s in its corp pattern" % e.id)
		if corps.has(e.corporation_id):
			assert_ne(PortraitArt.pattern_of(subj), CorpPattern.Kind.NONE, "%s carries a pattern" % e.id)
			seen_corps[e.corporation_id] = true
		if e.is_boss:
			assert_eq(subj["kind"], PortraitArt.Kind.BOSS, "%s is a boss" % e.id)
		var h := Hologram.for_enemy(e)
		assert_eq(h.mode, Hologram.Mode.BOSS if e.is_boss else Hologram.Mode.BUST, "%s hologram mode" % e.id)
		h.free()
	assert_eq(seen_corps.size(), corps.size(), "every corp has enemies")


func test_machines_agents_and_bosses_stay_distinct_kinds() -> void:
	var drone := PortraitArt.enemy_subject(&"courier_drone", "Courier Drone", &"meridian", false)
	var agent := PortraitArt.enemy_subject(&"account_manager", "Account Manager", &"solace", false)
	var boss := PortraitArt.enemy_subject(&"the_manifest", "The Manifest", &"meridian", true)
	assert_eq(drone["kind"], PortraitArt.Kind.MACHINE)
	assert_eq(agent["kind"], PortraitArt.Kind.AGENT)
	assert_eq(boss["kind"], PortraitArt.Kind.BOSS)
	var r := Rect2(0, 0, 100, 100)
	assert_gt(PortraitArt.shapes(r, drone)["lens"], 0.0, "a machine has a lens")
	assert_gt((PortraitArt.shapes(r, agent)["tie"] as PackedVector2Array).size(), 0, "an agent wears a tie")
	assert_eq((PortraitArt.shapes(r, boss)["extras"] as Array).size(), 5, "a boss wears a crown")


func test_the_boss_hologram_is_sized_to_forty_percent_and_dimmed() -> void:
	assert_eq(Hologram.boss_size(720.0), Vector2(288, 288))
	var boss := Hologram.new(PortraitArt.enemy_subject(&"the_manifest", "The Manifest", &"meridian", true), Hologram.Mode.BOSS)
	add_child_autofree(boss)
	assert_lt(boss.dim, 1.0, "the boss is dimmed behind its wheel")
	assert_eq(boss.mouse_filter, Control.MOUSE_FILTER_IGNORE, "it never takes input")


func test_the_hologram_is_static_under_reduce_effects() -> void:
	var was := Settings.reduce_effects
	Motion.force_live = true
	Settings.set_reduce_effects(false)
	var h := Hologram.new(PortraitArt.enemy_subject(&"civic_drone", "Civic Drone", &"halcyon", false))
	h.size = Vector2(96, 96)
	add_child_autofree(h)
	await get_tree().process_frame
	await get_tree().process_frame
	assert_true(h.is_processing(), "effects on: the idle plays")
	assert_gt(h.phase, 0.0, "the idle clock runs")
	Settings.set_reduce_effects(true)
	await get_tree().process_frame
	var still := h.phase
	for i in 4:
		await get_tree().process_frame
	assert_false(h.is_processing(), "reduce effects: no idle")
	assert_eq(h.phase, still, "the clock stays")
	assert_eq(h.phase, 0.0, "at rest")
	assert_eq(h.shimmer(), 1.0, "no shimmer")
	# The intro is a cross-fade: fully projected at once, alpha rising.
	h.play_intro()
	assert_eq(h.reveal, 1.0, "no projection sweep under reduce effects")
	assert_true(h.intro_running(), "the cross-fade runs")
	assert_eq(h.modulate.a, 0.0, "fades in from clear")
	var done := [false]
	h.intro_finished.connect(func() -> void: done[0] = true)
	h.finish_intro()
	assert_true(done[0], "finish_intro ends it and says so")
	assert_eq(h.modulate.a, 1.0)
	Settings.set_reduce_effects(was)
	Motion.force_live = false


func test_the_intro_reveals_live_and_ends_at_once_headless() -> void:
	var was := Settings.reduce_effects
	Settings.set_reduce_effects(false)
	var h := Hologram.new(PortraitArt.enemy_subject(&"the_manifest", "The Manifest", &"meridian", true), Hologram.Mode.BOSS)
	add_child_autofree(h)
	var done := [false]
	h.intro_finished.connect(func() -> void: done[0] = true)
	h.play_intro()
	assert_true(done[0], "headless: the end state at once")
	assert_eq(h.reveal, 1.0)
	Motion.force_live = true
	done[0] = false
	h.play_intro()
	assert_true(h.intro_running(), "live: the reveal plays")
	assert_lt(h.reveal, 1.0, "it starts unprojected")
	assert_eq(VfxTier.of(Hologram.INTRO_ID), VfxTier.T4, "the intro is T4")
	assert_eq(VfxTier.of(Hologram.IDLE_ID), VfxTier.T0, "the idle is T0")
	assert_true(Motion.seconds(Hologram.IDLE_ID) >= VfxTier.T0_MIN_PERIOD, "T0 period")
	h.finish_intro()
	assert_true(done[0])
	assert_eq(h.reveal, 1.0)
	Motion.force_live = false
	Settings.set_reduce_effects(was)


# --- Item 4: Polaroid and dossier ----------------------------------------------------------------

func _card(op_name: String = "Breaker 1") -> CrewCard:
	var card := CrewCard.new(op_name, "Breaker", 0, 60, 60, "HP 60/60, DECK 10, DAEMONS 0")
	add_child_autofree(card)
	card.set_stats(60, 60, 10, 0)
	return card


func test_the_polaroid_caption_never_repeats_the_name() -> void:
	for scale in [1.0, 1.6]:
		Settings.set_text_scale(scale)
		var card := _card("Breaker 1")
		assert_false(card.polaroid.caption.to_lower().contains("breaker 1"), "caption '%s' is not the name" % card.polaroid.caption)
		assert_ne(card.polaroid.caption, "", "the Polaroid still has a caption (the rank)")
	Settings.set_text_scale(1.0)


func test_the_dossier_shows_stats_as_icon_and_number() -> void:
	var card := _card()
	for k in [StatIcon.HP, StatIcon.CARDS, StatIcon.DAEMON]:
		var f := card.stat_field(k)
		assert_not_null(f, "field %s" % k)
		assert_true(f.value_label.text.is_valid_int() or f.value_label.text.contains("/"), "%s holds only a number: %s" % [k, f.value_label.text])
	assert_eq(card.stat_field(StatIcon.HP).value_label.text, "60/60")
	for l in card.text_labels():
		assert_false(l.text.contains("DECK"), "no stat sentence: %s" % l.text)


func test_dossier_text_meets_the_caption_floor_at_every_scale() -> void:
	for scale in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		var card := _card()
		await get_tree().process_frame
		await get_tree().process_frame
		var floor_px := roundi(UiTheme.CAPTION * scale)
		var labels := card.text_labels()
		assert_gt(labels.size(), 3)
		var steps := []
		for st in UiTheme.STEPS:
			steps.append(UiTheme.font_px_at(st, scale))
		for l in labels:
			var fs := l.get_theme_font_size(&"font_size")
			assert_true(fs >= floor_px, "%s at %.1f: %d px >= %d" % [l.text, scale, fs, floor_px])
			assert_true(steps.has(fs), "%s at %.1f: %d px is a type step" % [l.text, scale, fs])
		for i in labels.size():
			for j in range(i + 1, labels.size()):
				var a := labels[i].get_global_rect().grow(-1.0)
				var b := labels[j].get_global_rect().grow(-1.0)
				assert_false(a.intersects(b), "'%s' and '%s' overlap at %.1f" % [labels[i].text, labels[j].text, scale])
		assert_true(card.polaroid.caption_font_size() >= floor_px, "the Polaroid caption at %.1f" % scale)
	Settings.set_text_scale(1.0)


func test_dossier_text_contrast_and_high_contrast() -> void:
	var card := _card()
	for l in card.text_labels():
		assert_gt(Palette.contrast(l.get_theme_color(&"font_color"), Palette.NOTE_PAPER), 4.5, "%s on paper" % l.text)
	var was := Settings.high_contrast
	Settings.set_high_contrast(true)
	var hc := _card()
	var box := hc.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_eq(box.bg_color.a, 1.0, "opaque panel")
	for l in hc.text_labels():
		assert_gt(Palette.contrast(l.get_theme_color(&"font_color"), box.bg_color), HighContrast.HC_MIN_CONTRAST, "%s at 7:1" % l.text)
	Settings.set_high_contrast(was)


func test_a_downed_operative_is_flatlined() -> void:
	var card := _card()
	card.set_operative(&"breaker", &"op_x")
	card.dead = true
	assert_eq(card.polaroid._subject()["expression"], PortraitArt.Expr.FLATLINED)
	assert_eq(card.class_id, &"breaker")
