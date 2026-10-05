extends RefCounted
## Static visual lint (ART-0 D, ported from art-pass W10; ART_BIBLE v1 §4.3 rule 1, §13
## "Lint", §14 "no literal colours or sizes in the view"). Reads `scripts/ui/**/*.gd` as text (no scene is instanced) and
## counts, per file and rule, the lines that carry a literal colour or a literal font size.
## `tests/unit/test_visual_lint_static.gd` compares the counts with the committed baseline
## `tools/visual_qa/lint_baseline.json`: a count may only go down.
## `tools/visual_qa/lint_static_cli.gd` (run by `update_lint_baseline.py`) writes it.
##
## Rules (keys of the per-file dictionaries):
## - `color`: `Color(` whose first argument is a number or a string literal, `Color8(`,
##   `Color.html(`, `Color.hex(`. `palette.gd` (the token file) is exempt.
## - `font_override`: `add_theme_font_size_override(<name>, <int literal>)`.
## - `draw_size`: `draw_string` / `draw_multiline_string` (and their `_outline` forms) whose
##   font-size argument is an integer literal.
## - `font_const`: a constant or variable whose name holds `FONT` set to an integer literal
##   below `FLOOR_PX` (the §4.2 `caption` floor).
## - `font_size_assign`: `font_size = <int literal>` (a property or a local).

const ROOT := "res://scripts/ui"
const BASELINE := "res://tools/visual_qa/lint_baseline.json"
## Files that hold the colour tokens themselves (§3): their literals are the definition.
const COLOR_EXEMPT: Array[String] = ["res://scripts/ui/kit/palette.gd"]
## ART_BIBLE §4.2 `caption`: nothing the player reads is smaller.
const FLOOR_PX := 12
const RULES: Array[String] = ["color", "font_override", "draw_size", "font_const", "font_size_assign"]
## Argument index of the font size: CanvasItem.draw_string(font, pos, text, align, width, SIZE)
## and Font.draw_string(canvas_item, pos, text, align, width, SIZE) alike.
const SIZE_ARG := 5

static var _re_color: RegEx
static var _re_override: RegEx
static var _re_const: RegEx
static var _re_assign: RegEx
static var _re_draw: RegEx
static var _re_int: RegEx


static func _init_res() -> void:
	if _re_color != null:
		return
	_re_color = RegEx.create_from_string("\\bColor\\s*\\(\\s*[-+]?[0-9.\"']|\\bColor8\\s*\\(|\\bColor\\.html\\s*\\(|\\bColor\\.hex(64)?\\s*\\(")
	_re_override = RegEx.create_from_string("add_theme_font_size_override\\s*\\([^,()]+,\\s*[0-9]+\\s*\\)")
	_re_const = RegEx.create_from_string("^\\s*(?:static\\s+)?(?:const|var)\\s+([A-Za-z0-9_]*FONT[A-Za-z0-9_]*)\\s*(?::\\s*int\\s*)?:?=\\s*([0-9]+)\\s*$")
	_re_assign = RegEx.create_from_string("(?<![A-Za-z0-9_])font_size\\s*(?::\\s*int\\s*)?:?=\\s*[0-9]+\\s*$")
	_re_draw = RegEx.create_from_string("\\b(draw_string|draw_multiline_string|draw_string_outline|draw_multiline_string_outline)\\s*\\(")
	_re_int = RegEx.create_from_string("^[0-9]+$")


## Every `.gd` file under `root`, sorted.
static func ui_files(root: String = ROOT) -> Array[String]:
	var out: Array[String] = []
	_collect(root, out)
	out.sort()
	return out


static func _collect(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_collect(dir.path_join(d), out)


## The line with its comment removed (a `#` inside a string literal is kept).
static func strip_comment(line: String) -> String:
	var quote := ""
	var i := 0
	while i < line.length():
		var ch := line[i]
		if quote != "":
			if ch == "\\":
				i += 2
				continue
			if ch == quote:
				quote = ""
		elif ch == "\"" or ch == "'":
			quote = ch
		elif ch == "#":
			return line.substr(0, i)
		i += 1
	return line


## Findings of one file's text: {rule: [line numbers (1-based), ...]}. `path` decides the
## palette exemption.
static func scan_text(path: String, text: String) -> Dictionary:
	_init_res()
	var out := {}
	for r in RULES:
		out[r] = []
	var raw := text.split("\n")
	var lines: PackedStringArray = []
	for l in raw:
		lines.append(strip_comment(l))
	var color_exempt := COLOR_EXEMPT.has(path)
	for i in lines.size():
		var l := lines[i]
		if l.strip_edges() == "":
			continue
		if not color_exempt and _re_color.search(l) != null:
			(out["color"] as Array).append(i + 1)
		if _re_override.search(l) != null:
			(out["font_override"] as Array).append(i + 1)
		var m := _re_const.search(l)
		if m != null and int(m.get_string(2)) < FLOOR_PX:
			(out["font_const"] as Array).append(i + 1)
		if _re_assign.search(l) != null:
			(out["font_size_assign"] as Array).append(i + 1)
	# draw_string calls can span lines: scan the joined text.
	var joined := "\n".join(lines)
	for m in _re_draw.search_all(joined):
		var args := _call_args(joined, m.get_end())
		if args.size() > SIZE_ARG and _re_int.search(args[SIZE_ARG].strip_edges()) != null:
			var line_no := joined.substr(0, m.get_start()).count("\n") + 1
			(out["draw_size"] as Array).append(line_no)
	return out


## Top-level arguments of the call whose `(` ends just before `from`.
static func _call_args(text: String, from: int) -> PackedStringArray:
	var args: PackedStringArray = []
	var depth := 0
	var quote := ""
	var cur := ""
	var i := from
	while i < text.length():
		var ch := text[i]
		if quote != "":
			cur += ch
			if ch == "\\" and i + 1 < text.length():
				cur += text[i + 1]
				i += 2
				continue
			if ch == quote:
				quote = ""
		elif ch == "\"" or ch == "'":
			quote = ch
			cur += ch
		elif ch == "(" or ch == "[" or ch == "{":
			depth += 1
			cur += ch
		elif ch == ")" or ch == "]" or ch == "}":
			if depth == 0:
				args.append(cur.strip_edges())
				return args
			depth -= 1
			cur += ch
		elif ch == "," and depth == 0:
			args.append(cur.strip_edges())
			cur = ""
		else:
			cur += ch
		i += 1
	return args


## Findings for every UI file: {path: {rule: [lines]}} (files with none are left out).
static func scan_all(root: String = ROOT) -> Dictionary:
	var out := {}
	for p in ui_files(root):
		var found := scan_text(p, FileAccess.get_file_as_string(p))
		var any := false
		for r in RULES:
			if not (found[r] as Array).is_empty():
				any = true
		if any:
			out[p] = found
	return out


## {path: {rule: count}} of `scan_all` (only non-zero counts).
static func counts(findings: Dictionary) -> Dictionary:
	var out := {}
	for p in findings:
		var per := {}
		for r in RULES:
			var n := ((findings[p] as Dictionary)[r] as Array).size()
			if n > 0:
				per[r] = n
		if not per.is_empty():
			out[p] = per
	return out


## The committed baseline's counts ({path: {rule: count}}); empty when missing.
static func load_baseline(path: String = BASELINE) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed is Dictionary and (parsed as Dictionary).get("files") is Dictionary:
		return (parsed as Dictionary)["files"]
	return {}


## Compares current findings with a baseline. Returns {"up": [lines of text], "down":
## [lines of text]}: a file-rule count above its baseline (a new file starts at 0) is "up",
## below it is "down".
static func compare(findings: Dictionary, baseline: Dictionary) -> Dictionary:
	var up: Array[String] = []
	var down: Array[String] = []
	var now := counts(findings)
	var paths := {}
	for p in now:
		paths[p] = true
	for p in baseline:
		paths[p] = true
	var sorted := paths.keys()
	sorted.sort()
	for p in sorted:
		for r in RULES:
			var was := int((baseline.get(p, {}) as Dictionary).get(r, 0))
			var is_n := int((now.get(p, {}) as Dictionary).get(r, 0))
			if is_n > was:
				var lines: Array = (findings[p] as Dictionary)[r]
				up.append("%s [%s] %d > baseline %d, lines %s" % [p, r, is_n, was, str(lines)])
			elif is_n < was:
				down.append("%s [%s] %d < baseline %d" % [p, r, is_n, was])
	return {"up": up, "down": down}
