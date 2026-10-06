class_name RaidTerminal
extends TerminalWindow
## ART-6 3A: the Cell's own raid screens as CRT terminals (ART_BIBLE v2 §1.2 "CRT terminal",
## §4.8 YOUR NETWORK, IF PLACED, the LIVE RAID FEED and its Speed / Skip strip), on 1B's
## CrtTerminalPanel: navy glass, the accent edge and glow, 3 px scanlines, the faint
## scrolling hex dump, the `> TITLE` prompt and its blinking caret. Still a TerminalWindow
## (its `body`, `title`, `tag_label`, the pad and every terminal-window check hold): the
## CRT panel is its backdrop and the window's own frame steps aside.

## The accents of 1B's terminal by colour: the Cell's cyan, DISPATCH red, the rest the corp's.
var crt: CrtTerminalPanel


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN) -> void:
	super._init(p_title, p_accent)
	material = null
	var box := StyleBoxEmpty.new()
	box.content_margin_left = CrtTerminalPanel.PAD.x
	box.content_margin_right = CrtTerminalPanel.PAD.x
	box.content_margin_top = CrtTerminalPanel.PAD.y
	box.content_margin_bottom = CrtTerminalPanel.PAD.y
	add_theme_stylebox_override("panel", box)
	crt = CrtTerminalPanel.new()
	crt.name = "Crt"
	crt.mouse_filter = Control.MOUSE_FILTER_IGNORE
	crt.text = p_title.to_upper()
	crt.seed = absi(p_title.hash()) % 997 + 1
	if p_accent == Palette.NET_CYAN:
		crt.accent_kind = CrtTerminalPanel.Accent.CELL
	elif p_accent == Palette.HARM:
		crt.accent_kind = CrtTerminalPanel.Accent.DISPATCH
	else:
		crt.accent_kind = CrtTerminalPanel.Accent.CORP
		crt.corp_color = p_accent
	add_child(crt, false, Node.INTERNAL_MODE_FRONT)
	# The window's own title keeps its room (and its words for the pad and the tests); the
	# CRT's prompt line shows it.
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.add_theme_color_override("font_color", Palette.AUTO)
		head.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
	var outer := get_child(0) if get_child_count() > 0 else null
	if outer != null and outer.get_child_count() > 1 and outer.get_child(1) is ColorRect:
		(outer.get_child(1) as ColorRect).color = Palette.AUTO


## The title and rule stay clear (the CRT's prompt shows the title); the CRT panel binds its own
## skin, so a pick only redraws the frame. ART-12 12s-b.
func _apply_skin() -> void:
	queue_redraw()


func _notification(what: int) -> void:
	if (what == NOTIFICATION_RESIZED or what == NOTIFICATION_SORT_CHILDREN) and crt != null:  # after the container fitted it
		crt.position = Vector2.ZERO
		crt.size = size


func _draw() -> void:
	pass  # the CRT panel is the frame
