class_name BakedTexture
extends Texture2D
## A baked city image kept on the GPU. View only.
##
## ANIM-R5 P1: it shows the bake's own SubViewport, kept after its one render (never updated
## again; its painter and geometry go): the texture drawn is the viewport's render target,
## through `SubViewport.get_texture()` (a ViewportTexture: the only way Godot lets another
## canvas draw a viewport's target; ANIM-R4 H10 wrapped the target in a Texture2DRD, which
## Godot refuses for a viewport's shared texture, so every kept bake drew nothing). Nothing
## is allocated or copied in the landing frame. The viewport lives under
## CityBakeCache's holder and goes with the last reference to this resource (the cache's
## entry, a spread's old image), so a view can never draw a texture whose viewport was freed
## under it.
##
## `rd_copy` is the fallback of ANIM-R1 M2 (the picture copied on the GPU into a texture of
## its own, freed with this resource), used when keeping viewports is switched off.

## The kept bake viewport (null for a copy).
var held: SubViewport = null
## The GPU copy (null for a kept viewport).
var rd_copy: Texture2DRD = null
var _w: int = 0
var _h: int = 0


## A texture showing `vp`'s render target, the viewport kept; null when its target is not a
## valid, non-empty texture.
static func of_viewport(vp: SubViewport) -> BakedTexture:
	if vp == null or not is_instance_valid(vp):
		return null
	var vt := vp.get_texture()
	if vt == null or not vt.get_rid().is_valid() or vp.size.x <= 0 or vp.size.y <= 0:
		return null
	var t := BakedTexture.new()
	t.held = vp
	t._w = vp.size.x
	t._h = vp.size.y
	return t


## A texture owning the RenderingDevice texture `rid` (freed with this resource); null when
## `rid` is not a valid texture of a non-empty size.
static func of_rd(rid: RID) -> BakedTexture:
	var rd := RenderingServer.get_rendering_device()
	if rd == null or not rid.is_valid() or not rd.texture_is_valid(rid):
		return null
	var copy := Texture2DRD.new()
	copy.texture_rd_rid = rid
	if not copy.get_rid().is_valid() or copy.get_width() <= 0 or copy.get_height() <= 0:
		copy.texture_rd_rid = RID()
		rd.free_rid(rid)
		return null
	var t := BakedTexture.new()
	t.rd_copy = copy
	t._w = copy.get_width()
	t._h = copy.get_height()
	return t


## True while the picture can be drawn (its viewport alive, or its copy's texture valid).
func valid() -> bool:
	if held != null:
		return is_instance_valid(held) and held.get_texture().get_rid().is_valid()
	return rd_copy != null and rd_copy.get_rid().is_valid()


func _get_rid() -> RID:
	if held != null:
		return held.get_texture().get_rid() if is_instance_valid(held) else RID()
	return rd_copy.get_rid() if rd_copy != null else RID()


func _get_width() -> int:
	return _w


func _get_height() -> int:
	return _h


func _has_alpha() -> bool:
	return false


## The picture read back to the CPU (tools and tests only: a stall).
func picture() -> Image:
	if held != null and is_instance_valid(held):
		return held.get_texture().get_image()
	if rd_copy != null:
		return rd_copy.get_image()
	return null


func _notification(what: int) -> void:
	if what != NOTIFICATION_PREDELETE:
		return
	if held != null:
		# Freed at the end of the frame (a canvas may still hold this frame's draw of it); at
		# exit the holder goes with the tree.
		if is_instance_valid(held) and not held.is_queued_for_deletion():
			held.queue_free()
		held = null
	if rd_copy != null:
		var rid := rd_copy.texture_rd_rid
		rd_copy.texture_rd_rid = RID()
		rd_copy = null
		var rd := RenderingServer.get_rendering_device()
		if rd != null and rid.is_valid() and rd.texture_is_valid(rid):
			rd.free_rid(rid)
