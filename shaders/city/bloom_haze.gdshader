shader_type fog;
// LOOK Solace THE BLOOM A "Necrosis" (HQ): the faint pink spore haze just above the front (bloom3d_hq.haze): an emissive volume box
// round the helix about three floors tall, fading upward and outward, speckled by a noise (rev 3: r 34, 38 tall, k 0.004, emission 0.07). Art-owned; only the Solace HQ page carries it. A box in the
// compound's plate units: `centre` the compound's origin (world), `unit_k` city BU per plate unit.
#include "res://addons/rc_look/shaders/rc_hash.gdshaderinc"

uniform vec3 pink = vec3(1.0, 0.0612, 0.305);
uniform vec3 centre = vec3(0.0);
uniform float unit_k = 1.0;
uniform float z0 = 0.0;          // the box's floor (plate units, over the compound's ground)
uniform float h = 45.0;          // its height
uniform float k = 0.02;          // density
uniform float emission = 1.4;    // emission per unit density
uniform float noise_scale = 9.0; // the speckle's frequency over the box (cells across it)
uniform float strength = 0.0;

void fog() {
	vec3 p = (WORLD_POSITION - centre) / unit_k;
	float gz = clamp((p.y - z0) / h, 0.0, 1.0);
	float fade = pow(1.0 - gz, 1.6);
	float ramp_in = smoothstep(0.0, 0.08, gz);
	vec3 g = vec3(p.x / 68.0 + 0.5, p.z / 68.0 + 0.5, gz);
	float spec = smoothstep(0.50, 0.66, rcl_vnoise3(g * noise_scale));
	float rr = length(g.xy - vec2(0.5));
	float radial = 1.0 - smoothstep(0.10, 0.48, rr);  // the cylinder's radial fade (rev 3)
	float dens = fade * ramp_in * radial * (0.25 + spec) * strength;
	DENSITY = dens * k / unit_k;
	ALBEDO = pink;
	EMISSION = pink * dens * emission;
}
