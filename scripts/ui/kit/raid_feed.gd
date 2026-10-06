class_name RaidFeed
extends ZineNote
## ART-6 3A: the LIVE RAID FEED's lines as the Cell's terminal text (ART_BIBLE v2 §1.2: the
## Cell's systems are CRT terminals, never paper): the RaidPlayoutPanel's log, a ZineNote
## without its torn paper (the RaidTerminal round it is the glass), in the terminal face.


func _init(p_title: String = "", min_size: Vector2 = Vector2(240, 120)) -> void:
	super._init("", min_size)
	title = p_title
	name = "RaidFeed"
	paper_color = Palette.AUTO
	label.offset_top = 2
	label.offset_left = 2
	label.offset_right = -2
	label.offset_bottom = -2
	label.add_theme_color_override("default_color", Palette.TERMINAL_TEXT)
	label.add_theme_font_size_override("normal_font_size", UiTheme.font_px(UiTheme.CAPTION))


func _draw() -> void:
	pass
