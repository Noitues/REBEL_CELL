class_name MapLegend
extends TerminalWindow
## The map key for the city map views (Settings.map_legend): what the highlight colours,
## line styles and badge glyphs mean. Follows the setting live.

const ROWS := [["■", "#FF3DA8", "claimed (yours)"], ["■", "#5CE1FF", "cleared"], ["■", "", "corporate"], ["■", "#FFD24D", "seized"],
	["━", "#FF3DA8", "your network link"], ["- -", "", "threat route"], ["◈", "#F2EEE4", "exploit"], ["❄", "#F2EEE4", "heat reduction"],
	["✦", "#F2EEE4", "boss"], ["⌂", "#F2EEE4", "home / CORE"]]


func _init(corporation_id: StringName = &"") -> void:
	super("MAP LEGEND")
	name = "MapLegend"
	custom_minimum_size.x = 230
	var corp := Palette.corp_color(corporation_id).to_html(false)
	for r in ROWS:
		var l := RichTextLabel.new()
		l.bbcode_enabled = true
		l.fit_content = true
		l.scroll_active = false
		l.custom_minimum_size.x = 200
		l.text = "[color=#%s]%s[/color]  %s" % [r[1].trim_prefix("#") if r[1] != "" else corp, r[0], r[2]]
		body.add_child(l)
	visible = Settings.map_legend
	Settings.changed.connect(func() -> void: visible = Settings.map_legend)
