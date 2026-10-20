// LOOK L5 (whole-city plate parity): the A2 road glow lines at the whole-city night, unshaded: the vertex colour (the class
// glow, CityA2Features) times `tint` and `gain`, so the ring roads and motorways bloom as the plate's lit peach skeleton.
shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;

#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float gain = 1.0;
uniform vec3 tint = vec3(1.0);

void fragment() {
	ALBEDO = COLOR.rgb * tint * gain;
}
