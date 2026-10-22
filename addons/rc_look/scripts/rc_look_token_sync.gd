class_name RcLookTokenSync
extends RefCounted
## LOOK-TOOLBOX module 1: the text edit behind sync_tokens.gd, pure so the test can run it on a string. Rewrites the
## [shader_globals] section of a project.godot text: entries whose name starts with RcLookTokens.PREFIX are replaced by
## `globals` (name -> Color, written in the order given), every other entry and every other section stay byte for byte.

const HEADER := "[shader_globals]"


## `text` with its [shader_globals] section holding `globals` as color entries (the section is added at the end when
## missing). Other globals keep their text and order and come first.
static func with_globals(text: String, globals: Dictionary) -> String:
	var lines := text.split("\n")
	var start := lines.find(HEADER)
	var end := lines.size()
	if start >= 0:
		for i in range(start + 1, lines.size()):
			if lines[i].begins_with("[") and lines[i].ends_with("]"):
				end = i
				break
	var kept := PackedStringArray()
	if start >= 0:
		var i := start + 1
		while i < end:
			var ln := lines[i]
			if ln.contains("={"):
				var block := PackedStringArray([ln])
				var j := i + 1
				while j < end and lines[j] != "}":
					block.append(lines[j])
					j += 1
				block.append("}")
				if not ln.begins_with(RcLookTokens.PREFIX):
					kept.append("\n".join(block))
				i = j + 1
			else:
				i += 1
	var blocks := kept.duplicate()
	for n: String in globals:
		blocks.append("%s={\n\"type\": \"color\",\n\"value\": %s\n}" % [n, var_to_str(globals[n])])
	var section := HEADER + "\n\n" + "\n".join(blocks) + "\n"
	if start < 0:
		return text.rstrip("\n") + "\n\n" + section
	var before := "\n".join(lines.slice(0, start))
	var after := "\n".join(lines.slice(end)) if end < lines.size() else ""
	return before + "\n" + section + ("\n" + after if after != "" else "")
