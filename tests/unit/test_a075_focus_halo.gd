extends GutTest
## A-075 (ART_BIBLE §2.10): a focused vinyl sticker shows a lime (`Palette.FOCUS`) die-cut halo, an unfocused one
## does not, kit-wide (VinylSticker watches its owning control's focus), and the halo moves with focus between
## the two stickers of a ConfirmDialog. Hover without focus does not show it.


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _halo_px(v: VinylSticker) -> float:
	return float((v.material as ShaderMaterial).get_shader_parameter(&"halo_px"))


func _holder() -> Control:
	var h := Control.new()
	h.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child_autofree(h)
	return h


func test_a_focused_sticker_draws_the_halo_and_an_unfocused_one_does_not() -> void:
	var h := _holder()
	var a := SendItSticker.new("KEEP", "", HudSkin.VINYL_YELLOW, 40)
	var b := SendItSticker.new("GO", "", HudSkin.VINYL_PINK, 40)
	h.add_child(a)
	h.add_child(b)
	await _frames()
	assert_false(a.art.focus_halo)
	assert_eq(_halo_px(a.art), 0.0, "no halo at rest")
	a.grab_focus()
	await _frames()
	assert_true(a.art.focus_halo)
	assert_eq(_halo_px(a.art), VinylSticker.FOCUS_HALO_PX, "the focused sticker's halo")
	assert_eq(_halo_px(b.art), 0.0, "the other stays plain")
	assert_eq((a.art.material as ShaderMaterial).get_shader_parameter(&"halo_color"), Palette.FOCUS, "lime from the palette")
	assert_eq(Palette.FOCUS.to_html(false).to_upper(), "D4FF00")
	b.grab_focus()
	await _frames()
	assert_eq(_halo_px(a.art), 0.0, "gone on focus loss")
	assert_eq(_halo_px(b.art), VinylSticker.FOCUS_HALO_PX)


func test_hover_without_focus_shows_no_halo() -> void:
	var h := _holder()
	var a := SendItSticker.new("KEEP", "", HudSkin.VINYL_YELLOW, 40)
	h.add_child(a)
	await _frames()
	a.mouse_entered.emit()
	await _frames()
	assert_eq(_halo_px(a.art), 0.0, "hover alone leaves the die-cut plain")


func test_the_halo_follows_focus_between_the_two_buttons_of_a_confirm_dialog() -> void:
	var h := _holder()
	var d := ConfirmDialog.new("Respin?", "RESPIN", "KEEP PLANNING")
	h.add_child(d)
	await _frames(4)
	var no := d.no_button as SendItSticker
	var yes := d.yes_button as SendItSticker
	assert_eq(get_viewport().gui_get_focus_owner(), no, "the safe answer starts focused")
	assert_eq(_halo_px(no.art), VinylSticker.FOCUS_HALO_PX)
	assert_eq(_halo_px(yes.art), 0.0)
	yes.grab_focus()
	await _frames()
	assert_eq(_halo_px(no.art), 0.0)
	assert_eq(_halo_px(yes.art), VinylSticker.FOCUS_HALO_PX)


## The rect a focused sticker's drawn die-cut covers, halo included (its body through the art's grown, tilted transform).
func _focused_rect(b: SendItSticker) -> Rect2:
	var t := b.art.get_global_transform()
	var r := b.art.body_rect
	var pts := [t * r.position, t * Vector2(r.end.x, r.position.y), t * r.end, t * Vector2(r.position.x, r.end.y)]
	var box := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		box = box.expand(p)
	return box.grow(VinylSticker.FOCUS_HALO_PX)


func test_both_focused_stickers_and_the_words_sit_inside_the_dialogs_inner_frame() -> void:
	var h := _holder()
	var d := ConfirmDialog.new("Respin?", "RESPIN", "KEEP PLANNING", "RESPIN", "A body line that is long enough to show where the words start.", false, "go on [A]", "keep going [B]")
	h.add_child(d)
	await _frames(6)
	var frame := d.panel.body.get_global_rect()
	for b in [d.no_button, d.yes_button]:
		b.grab_focus()
		await _frames(3)
		var r := _focused_rect(b as SendItSticker)
		assert_true(frame.encloses(r), "%s focused %s inside the frame %s" % [b.name, r, frame])
		var sb := b as SendItSticker
		var hp := float(sb._hint_px())
		var cap := Rect2(sb.get_global_position() + Vector2(SendItSticker.LINE_INSET_X, sb.size.y - SendItSticker.LINE_INSET_BOTTOM - hp), Vector2(sb._line_w(), hp))
		assert_false(cap.intersects(r), "%s caption %s clear of the focused sticker and halo %s" % [b.name, cap, r])
	var q := d.find_child("Question", true, false) as Label
	assert_gte(q.get_global_rect().position.x - frame.position.x, HudDialogPanel.PAD * 0.5 - 1.0, "the words sit in from the frame by the title's inset")
