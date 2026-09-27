// Blinking city lights (H20): window lights and beacons over the baked city blink on
// the GPU, so their geometry is built once per camera and never redrawn per frame.
// Per vertex: UV.x = phase (0-1), UV.y = +period (seconds; shown while lit) or -period
// (shown while dark). A light is lit for `duty` of its period. `animate` is 0 under
// reduce-effects: every light holds its t = 0 state. Periods are seconds long, far under
// the flash limiter's 3 per second.
shader_type canvas_item;

uniform float duty : hint_range(0.0, 1.0) = 0.5;
uniform float animate = 1.0;

void fragment() {
	float period = max(abs(UV.y), 0.001);
	float lit = 1.0 - step(duty, fract(TIME * animate / period + UV.x));
	float shown = UV.y > 0.0 ? lit : 1.0 - lit;
	COLOR.a *= shown;
}
