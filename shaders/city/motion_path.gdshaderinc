// ART-5 5c: the baked lane paths of the city's motion layers (ART_BIBLE §6.1: "cars in a
// MultiMesh moved in the vertex shader along a baked position texture"). One texel row per
// lane row (CitySkyLanes.bake): xyz = world position, uniform in arc length; a = the row's
// length (BU). Read with texelFetch and interpolated by hand (float textures need not
// filter), exactly as CitySkyLanes.sample does on the CPU.

uniform sampler2D path_tex : filter_nearest, repeat_disable;

vec3 path_at(int row, float s) {
	int w = textureSize(path_tex, 0).x;
	float f = clamp(s, 0.0, 1.0) * float(w - 1);
	int i = min(int(floor(f)), w - 2);
	vec3 a = texelFetch(path_tex, ivec2(i, row), 0).xyz;
	vec3 b = texelFetch(path_tex, ivec2(i + 1, row), 0).xyz;
	return mix(a, b, f - float(i));
}

float path_length(int row) {
	return texelFetch(path_tex, ivec2(0, row), 0).a;
}
