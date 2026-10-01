def edit(p, pairs):
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a)
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)

edit("icons8.py", [
    ("    fire(b, 512, 600, 860, 600, t, seed=3)\n    sk, eyes = skull_masks(512, 520, 250)",
     "    fire(b, 512, 720, 760, 860, t, seed=3)\n    sk, eyes = skull_masks(512, 560, 250)"),
    ("    fire(b, 512, 900, 900, 860, t, seed=7)", "    fire(b, 512, 930, 720, 960, t, seed=7)"),
    ("    fire(b, 512, 520, 980, 470, t, seed=11)", "    fire(b, 512, 540, 940, 560, t, seed=11)"),
    ("    d.ellipse([cx - w / 2, base_y - w * 0.18, cx + w / 2, base_y + w * 0.18], fill=255)",
     "    d.ellipse([cx - w / 2, base_y - w * 0.12, cx + w / 2, base_y + w * 0.12], fill=255)"),
])
edit("versions.py", [
    ('        opts["mascot"] = True\n        opts["plate"] = min(opts.get("plate", 0.62), 0.55) if not lod else 0.8',
     '        if spec.get("art", True):  # round 8: bold identity art (icons8) replaces the faint mascots\n'
     '            opts["art"] = True\n            opts["art_map"] = spec.get("art_map", {})\n'
     '            opts["plate"] = 0.55 if not lod else 0.8\n'
     '        else:\n            opts["mascot"] = True\n            opts["plate"] = min(opts.get("plate", 0.62), 0.55) if not lod else 0.8'),
    ('    "the_manifest": "THE MANIFEST // PRIORITY ROUTING +4 SHIELD // PHASE 1 OF 3 // MULTIPLY @66% // ORBIT @33% // ",',
     '    "the_manifest": "THE MANIFEST // PRIORITY ROUTING +4 SHIELD // PHASE 1 OF 3 // MULTIPLY @66% // ORBIT @33% // ",\n'
     '    "ghost": "CELL-9 // GHOST // MESH ONLINE // FIRST NUDGE IGNORES RES // PERFECT: STRIP 2 RES // RING PIERCE . x2 . ECHO // HP 50/50 // ",\n'
     '    "drone_dispatcher": "MERIDIAN FREIGHT // DRONE DISPATCHER // COURIER BAY 2/2 // TARIFF ARMED // PKG 0447 OUTBOUND // ",'),
])
edit("slicelib.py", [
    ('    elif name == "DRONE":  # quad-rotor',
     '''    elif name == "HOOK":  # phishing hook
        d.ellipse([226, 20, 286, 80], outline=255, width=24)
        d.line([(256, 70), (256, 330)], fill=255, width=52)
        d.arc([96, 210, 282, 470], 0, 180, fill=255, width=52)
        d.polygon([(96, 330), (60, 220), (150, 280)], fill=255)
    elif name == "SHIELDG":
        d.polygon([(80, 50), (432, 50), (432, 250), (256, 470), (80, 250)], fill=255)
        d.polygon([(130, 95), (382, 95), (382, 235), (256, 400), (130, 235)], fill=0)
        d.polygon([(165, 130), (347, 130), (347, 225), (256, 345), (165, 225)], fill=255)
    elif name == "LOCK":
        d.arc([136, 30, 376, 290], 180, 360, fill=255, width=56)
        d.rectangle([136, 160, 192, 240], fill=255)
        d.rectangle([320, 160, 376, 240], fill=255)
        d.rounded_rectangle([90, 220, 422, 480], radius=30, fill=255)
        d.ellipse([226, 290, 286, 350], fill=0)
        d.rectangle([242, 330, 270, 420], fill=0)
    elif name == "LENS":
        d.ellipse([40, 40, 340, 340], fill=255)
        d.ellipse([92, 92, 288, 288], fill=0)
        d.line([(300, 300), (470, 470)], fill=255, width=70)
    elif name == "DRONE":  # quad-rotor'''),
])
print("ok")
