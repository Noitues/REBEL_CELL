// ART-5 5c: see city_pool.gdshaderinc. The x-ray variant: drawn through buildings, as the
// network decal is (bible 4.1, 4.3: the hardened nodes' rings and lights are node markers).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled, depth_test_disabled;
#include "res://shaders/city/city_pool.gdshaderinc"
