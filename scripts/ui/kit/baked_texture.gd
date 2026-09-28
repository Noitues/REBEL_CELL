class_name BakedTexture
extends Texture2DRD
## A baked city image kept on the GPU (ANIM-R1 M2): CityBakeCache copies a bake's
## viewport into a texture of its own instead of reading it back to the CPU and uploading
## it again (that cost a frame of ~60 ms at the end of a big bake). The texture is freed
## with the last reference to this resource. View only.
##
## ANIM-R4 H10: or it shows the bake's own viewport, kept (never updated again) instead of
## copied: `held` is that viewport, freed with this resource (the copy allocated and filled
## a second texture in the landing frame: ~14 ms of the route's 60-70 ms frame after a jack).
var held: SubViewport = null


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and held != null:
		texture_rd_rid = RID()  # the viewport's own: freed with it
		if is_instance_valid(held):
			held.queue_free()
		held = null
		return
	if what == NOTIFICATION_PREDELETE and texture_rd_rid.is_valid():
		var rid := texture_rd_rid
		texture_rd_rid = RID()
		var rd := RenderingServer.get_rendering_device()
		if rd != null and rid.is_valid():
			rd.free_rid(rid)
