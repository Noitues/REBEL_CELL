// ART-5 5c: see city_pool.gdshaderinc (depth-tested: buildings hide what is behind them).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/city/city_pool.gdshaderinc"
