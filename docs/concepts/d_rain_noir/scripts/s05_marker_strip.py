"""Still 05 (raw frames): the marker's life in three beats (feedback 6).
1 write-on stroke by stroke (nib visible), 2 drips form and hold while the game waits,
3 on press the page leaves and the drips keep running down the screen.
Renders three 1920x1080 frames; strip_layout.py crops and lays them out."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rn_lib import *  # noqa
from rn_parts import *  # noqa

BASE = out_arg(os.path.join(STILLS, "_raw_05"))
reset(samples=int(os.environ.get("RN_SAMPLES", "32")))
world("#010203", 1.0, vol_density=0.0025, vol_color="#8494ab", aniso=0.5)
sun((math.radians(-62), 0, math.radians(8)), "#9fb2d0", 0.35, name="backlight")
front_camera(50, fstop=0.12)
rng = random.Random(5)

# static: blurred skyline, wet street, rain, the enemy wheel glow off to the upper left (spill on the button)
wm = [mat_windows("cw%d" % i, wall="#0a0d13", lit=("#8fa3bd", "#b9aa92"), density=0.2 + 0.05 * i, strength=1.0, scale=2.0 + i * 0.4, seed=i * 3.1) for i in range(3)]


def skyline_h(x, y, r):
    half = 5.4 * (CAM_D + y) / CAM_D
    return max(3.0, r.uniform(-0.3, 0.75) * half + 5.8)


city_blocks(13, (-95, 95), (40, 260), 170, 0, 0, 5, 16, wm, z0=-5.8, hfn=skyline_h)
sky_glow("sky", (0, 330, 124), 900, 260, low="#3a4e6c", strength=2.0)
area((0, -14, 9), (math.radians(55), 0, 0), "#b9c9e4", 700, size=18, size_y=4, name="fill")
gp_back = GP("gp_back")
rain(gp_back, 2600, 1, (-60, 60), (4, 120), (-6, 30), length=(2.0, 6.0), radius=(0.006, 0.018), alpha=(0.08, 0.3))
# a slice of the operative wheel peeking in from above-left (context + light spill onto the button)
spinner("op", 560, 170, 178, [("atk", 5, 6), ("def", 4, 5), ("atk", 5, 6), ("crit", 3, 12), ("atk", 5, 8), ("def", 4, 6), ("evd", 4, 2)],
        "pink", "rivets", "BREAKER", "breaker core", tilt=(13, 7), spill=260, hp=(60, 60))

STAGES = [
    dict(progress=0.58, drips=None, page=0.0),
    dict(progress=1.0, drips={"stage": "forming", "count": 4}, page=0.0),
    dict(progress=1.0, drips={"stage": "running", "count": 4, "run_px": 470}, page=1.0),
]
BX, BY, BW, BH = 690, 470, 540, 150

for si, st in enumerate(STAGES):
    before = set(o.name for o in bpy.data.objects)
    gp_ui = GP("gp_ui%d" % si)
    gp_mk = GP("gp_mk%d" % si)
    dy = 230 * st["page"]                       # the page slides down and away on press
    alpha = 0.86 * (1 - 0.6 * st["page"])
    glass_panel(gp_ui, "p_exec%d" % si, BX, BY + dy, BW, BH, depth=0.15, edge="#3a5a70", alpha=alpha)
    ui_text("EXECUTE", BX + BW / 2, BY + dy + 72, 84, "#8aa4bf", 0.9 * (1 - 0.6 * st["page"]), MONO, "CENTER", depth=0.1)
    ui_text("[SPACE]", BX + BW - 16, BY + dy + BH - 18, 16, "text_lo", 1.0, MONO, "RIGHT", depth=0.1)
    if si == 1:
        # the game waits: a slow caret + prompt (glass voice), the drips hang
        ui_text("> waiting on you_", BX + 12, BY + BH + 40, 18, "text_mid", 1.6, MONO, depth=0.1)
    if st["page"] > 0:
        ml = gp_ui.mat("speed", "#b9c9e4", 0.5)
        for k in range(14):
            x = BX + rng.uniform(0, BW)
            y0 = BY + dy - rng.uniform(20, 160)
            gp_ui.stroke("speed", [P(x, y0, 0.05), P(x, y0 + rng.uniform(60, 180), 0.05)], [S(0.3), S(1.6)], ml, 0.5)
        ui_text("> jack: resolving...", BX + 12, BY + dy + BH + 40, 18, "text_lo", 1.2, MONO, depth=0.1)
    marker(gp_mk, "SEND IT", BX + 8, BY + 118, 92, depth=-0.3, seed=11, angle_deg=-4, progress=st["progress"], drips=st["drips"])
    render("%s_stage%d.png" % (BASE, si + 1))
    # remove this stage's dynamic objects
    for o in list(bpy.data.objects):
        if o.name not in before:
            bpy.data.objects.remove(o, do_unlink=True)
