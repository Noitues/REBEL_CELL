// ART-5 5a: the network ground decal (see city_network.gdshaderinc), drawn where the ground is
// seen and into the ground pass under see-through buildings.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/city/city_network.gdshaderinc"
