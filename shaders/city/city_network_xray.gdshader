// ART-5 5a: the network decal's x-ray (bible §4.1, §6.1): the same decal drawn only where a
// building hides the ground (depth test inverted), so a hidden link shows through solid at the
// City Grid zoom and at full strength through see-through buildings.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_inverted, shadows_disabled, fog_disabled;
#include "res://shaders/city/city_network.gdshaderinc"
