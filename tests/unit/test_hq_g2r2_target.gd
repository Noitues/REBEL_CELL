extends GutTest
## M14 G2R2-1 (standing rule: no UI over grease pencil): on the HQ's Grid the TARGET's pencil never
## sits under a panel (the edge arrow shows instead), and no Site name label sits on the TARGET word,
## arrow or chip. Every corporation at text scale 1.0 / 1.6 / 2.0.

const HQ := "res://scenes/hq/hq_scene.tscn"
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const SETTLE := 14

var _scale0: float = 1.0


func before_each() -> void:
	AudioDirector.muted = true
	_scale0 = Settings.text_scale
	RunManager.save_slot = "gut_hq_g2r2_target"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Settings.set_text_scale(_scale0)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _panel_rects(t: TargetEdgeMarker) -> Array[Rect2]:
	var out: Array[Rect2] = []
	for c in t.panels:
		if c != null and is_instance_valid(c) and c.is_visible_in_tree() and c.size != Vector2.ZERO:
			out.append(c.get_global_rect().grow(-1.0))
	return out


func test_the_target_pencil_is_never_under_a_panel_and_no_label_sits_on_it() -> void:
	for corp in CORPORATIONS:
		for s in SCALES:
			Settings.set_text_scale(s)
			var holder: Control = add_child_autofree(Control.new())
			holder.size = Vector2(1280, 720)
			var hq: Control = load(HQ).instantiate()
			holder.add_child(hq)
			hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
			hq.show_grid()
			for i in SETTLE:
				await get_tree().process_frame
			var where := "%s x%.1f" % [corp, s]
			var t: TargetEdgeMarker = hq.grid_target
			if t == null:
				pending("no 3D city headless: no edge marker")
				return
			var ov: CityMapOverlay = hq.city_overlay
			var panels := _panel_rects(t)
			if t.showing():
				var pencil := t.pencil_rects()
				assert_gt(pencil.size(), 1, "%s: the arrow and its word are placed" % where)
				for p in pencil:
					for b in panels:
						assert_false(p.intersects(b), "%s: the arrow, word and chip clear of every panel" % where)
					for key in ov.label_rects():
						var lr: Rect2 = ov.get_global_transform() * (ov.label_rects()[key] as Rect2)
						assert_false(p.grow(CityMapOverlay.PENCIL_CLEAR).intersects(lr), "%s: label %s keeps %.0f px from the TARGET pencil" % [where, key, CityMapOverlay.PENCIL_CLEAR])
			else:
				for n in ov.nodes:
					if not CityMapOverlay.is_boss(n):
						continue
					var l := ov.boss_layout(n)
					if l.is_empty():
						continue
					var xf := ov.get_global_transform()
					for k in ["circle", "word"]:
						for b in panels:
							assert_false((xf * (l[k] as Rect2)).intersects(b), "%s: the TARGET %s is not under a panel" % [where, k])
					for key in ov.label_rects():
						var lr: Rect2 = xf * (ov.label_rects()[key] as Rect2)
						for r in ov.boss_rects(n):
							assert_false((xf * r).grow(CityMapOverlay.PENCIL_CLEAR).intersects(lr), "%s: label %s keeps %.0f px from the TARGET circle, word and chip" % [where, key, CityMapOverlay.PENCIL_CLEAR])
			hq.get_parent().queue_free()
			await get_tree().process_frame
