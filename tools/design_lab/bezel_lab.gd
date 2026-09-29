extends Control
## Art pass W3 bezel lab (ART_BIBLE §6.1, §7.1): the eight operative classes' wheels side by
## side at turn 1 (their bezel ornament, hub pattern, Polaroid inset and glyph), or with
## `--enemies` one enemy per corporation plus a boss (notched corp bezels, patterns,
## portrait badges, the boss at 120%). Each wheel is a real WheelView fed by a real
## CombatEngine fight (seed 1); nothing here changes a rule.
## Run windowed through tools/run_windowed.py:
##   python tools/run_windowed.py --log lab.log -- res://tools/design_lab/bezel_lab.tscn -- --out=C:/path/classes.png
## Add `--scale=1.6` for a text scale, `--enemies` for the corp sheet.

const SHEET := Vector2i(1280, 720)
const CLASSES: Array[StringName] = [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]
## One enemy of each corporation, then a boss (content ids).
const ENEMIES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]
const COLUMNS := 4
const SAVE_AFTER_FRAMES := 8
const LABEL_H := 22.0

var _engines: Array[CombatEngine] = []


func _ready() -> void:
	var enemies := false
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--scale="):
			Settings.text_scale = float(a.trim_prefix("--scale="))
		elif a == "--enemies":
			enemies = true
	UiTheme.apply(self)
	var bg := ColorRect.new()
	bg.color = Palette.NET_BG_OUTER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var ids: Array = CLASSES if not enemies else _enemy_ids()
	var rows := ceili(float(ids.size()) / COLUMNS)
	var cell := Vector2(SHEET.x / float(COLUMNS), SHEET.y / float(rows))
	for i in ids.size():
		var engine := CombatEngine.new()
		add_child(engine)
		_engines.append(engine)
		var enemy: StringName = ENEMIES[0] if not enemies else ids[i]
		engine.start_fight(ids[i] if not enemies else &"breaker", [enemy], 1, &"rank:1")
		var s := engine.state()
		var c: CombatantState = s.player if not enemies else s.enemies[0]
		var v := WheelView.new()
		v.position = Vector2((i % COLUMNS) * cell.x, (i / COLUMNS) * cell.y + LABEL_H)
		v.size = cell - Vector2(0, LABEL_H)
		v.show_arrows = false
		add_child(v)
		v.show_combatant(c, s.satellites_of(c.id), engine.readouts(c), engine.resolver.lookup)
		var l := Label.new()
		l.text = String(ids[i]).to_upper() + (" (BOSS)" if v.is_boss() else "")
		l.position = Vector2((i % COLUMNS) * cell.x + 8.0, (i / COLUMNS) * cell.y)
		add_child(l)
	if out != "":
		for k in SAVE_AFTER_FRAMES:
			await RenderingServer.frame_post_draw
		var err := get_viewport().get_texture().get_image().save_png(out)
		print("bezel_lab: saved %s (%s)" % [out, error_string(err)])
		get_tree().quit(0 if err == OK else 1)


## The corp sheet's enemies: the first enemy of each corporation in the content, then its
## first boss (content order; deterministic).
func _enemy_ids() -> Array:
	var out: Array = []
	var corps := {}
	var boss: StringName = &""
	var ids: Array = ContentRegistry.all_ids()
	ids.sort()
	for id in ids:
		var e := ContentRegistry.get_content(id) as EnemyData
		if e == null:
			continue
		if e.is_boss and boss == &"":
			boss = id
		elif not e.is_boss and not e.is_mini_boss and not corps.has(e.corporation_id) and e.corporation_id != &"":
			corps[e.corporation_id] = id
	for k in corps.keys():
		out.append(corps[k])
	if boss != &"":
		out.append(boss)
	return out.slice(0, COLUMNS * 2)
