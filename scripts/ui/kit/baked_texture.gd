class_name BakedTexture
extends Texture2DRD
## A baked city image kept on the GPU (ANIM-R1 M2): CityBakeCache copies a bake's
## viewport into a texture of its own instead of reading it back to the CPU and uploading
## it again (that cost a frame of ~60 ms at the end of a big bake). The texture is freed
## with the last reference to this resource. View only.


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and texture_rd_rid.is_valid():
		var rid := texture_rd_rid
		texture_rd_rid = RID()
		var rd := RenderingServer.get_rendering_device()
		if rd != null and rid.is_valid():
			rd.free_rid(rid)
