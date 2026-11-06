"""Easing curves (t in 0..1 -> 0..1) used by the storyboards, the motion tests and the timing table.
Each name maps 1:1 to a Godot Tween trans/ease pair in tide_look.tres (see EASE_GODOT)."""
import math

FPS = 30.0


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(f, f0, f1):
    """0..1 progress of frame f through [f0, f1]."""
    if f1 <= f0:
        return 1.0 if f >= f0 else 0.0
    return clamp((f - f0) / float(f1 - f0))


def linear(t): return t
def step(t): return 1.0 if t >= 1.0 else 0.0
def in_quad(t): return t * t
def out_quad(t): return 1 - (1 - t) ** 2
def in_out_quad(t): return 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2
def in_cubic(t): return t ** 3
def out_cubic(t): return 1 - (1 - t) ** 3
def in_out_cubic(t): return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def out_expo(t): return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)
def out_back(t, s=1.70158):
    t -= 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2
def out_back_soft(t): return out_back(t, 0.9)
def hold(t): return 0.0


EASE = {
    'LINEAR': linear, 'STEP': step, 'IN_QUAD': in_quad, 'OUT_QUAD': out_quad, 'IN_OUT_QUAD': in_out_quad,
    'IN_CUBIC': in_cubic, 'OUT_CUBIC': out_cubic, 'IN_OUT_CUBIC': in_out_cubic, 'OUT_EXPO': out_expo,
    'OUT_BACK': out_back, 'OUT_BACK_SOFT': out_back_soft, 'HOLD': hold,
}

# Godot 4 Tween mapping for build (trans, ease)
EASE_GODOT = {
    'LINEAR': 'TRANS_LINEAR / EASE_IN_OUT', 'STEP': 'set value on frame (no tween)',
    'IN_QUAD': 'TRANS_QUAD / EASE_IN', 'OUT_QUAD': 'TRANS_QUAD / EASE_OUT', 'IN_OUT_QUAD': 'TRANS_QUAD / EASE_IN_OUT',
    'IN_CUBIC': 'TRANS_CUBIC / EASE_IN', 'OUT_CUBIC': 'TRANS_CUBIC / EASE_OUT', 'IN_OUT_CUBIC': 'TRANS_CUBIC / EASE_IN_OUT',
    'OUT_EXPO': 'TRANS_EXPO / EASE_OUT', 'OUT_BACK': 'TRANS_BACK / EASE_OUT (overshoot 1.70)',
    'OUT_BACK_SOFT': 'TRANS_BACK / EASE_OUT (overshoot 0.9, custom curve)', 'HOLD': 'no tween: value held',
}


def e(name, f, f0, f1):
    """eased progress of frame f in [f0,f1] using curve `name`."""
    return EASE[name](prog(f, f0, f1))
