// LOOK-TOOLBOX module 6: the screen bloom pass for any 2D layer (a ColorRect over what it blooms). Reads the screen's
// mips, bright-passes them in linear light (rcl_bright) and adds them back weighted under the soft ceiling
// (rcl_light_add). Static: nothing animates. Filled by RcLookLight.apply_bloom.
shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_light.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float strength = 1.0;
uniform float threshold = 0.6;
uniform float knee = 0.3;
uniform int key = 1;
uniform vec3 lods = vec3(2.0, 4.0, 6.0);
uniform vec3 weights = vec3(0.5, 0.35, 0.25);

void fragment() {
	vec3 base = textureLod(screen_tex, SCREEN_UV, 0.0).rgb;
	vec3 b = vec3(0.0);
	b += weights.x * rcl_bright(rcl_to_lin(textureLod(screen_tex, SCREEN_UV, lods.x).rgb), threshold, knee, key);
	b += weights.y * rcl_bright(rcl_to_lin(textureLod(screen_tex, SCREEN_UV, lods.y).rgb), threshold, knee, key);
	b += weights.z * rcl_bright(rcl_to_lin(textureLod(screen_tex, SCREEN_UV, lods.z).rgb), threshold, knee, key);
	COLOR = vec4(rcl_light_add(base, b * strength), 1.0);
}
