"""One-off: push Halcyon (violet / amber civic) and Orbital (cold cyan / white space) apart."""
import os
import re

H = os.path.dirname(os.path.abspath(__file__))


def sub(fn, pairs, within=None):
    p = os.path.join(H, fn)
    s = open(p, encoding="utf-8").read()
    if within:
        a = s.index(within[0])
        b = s.index(within[1], a)
        body = s[a:b]
        for x, y in pairs:
            assert x in body, (fn, x)
            body = body.replace(x, y)
        s = s[:a] + body + s[b:]
    else:
        for x, y in pairs:
            assert x in s, (fn, x)
            s = s.replace(x, y)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


# corp base colours
sub("slicelib.py", [('"halcyon": dict(name="HALCYON CIVIC", col=(140, 123, 255), bezel=(0.12, 0.11, 0.20))',
                     '"halcyon": dict(name="HALCYON CIVIC", col=(176, 110, 255), bezel=(0.16, 0.09, 0.24))'),
                    ('"orbital": dict(name="ORBITAL COMMONS", col=(127, 168, 255), bezel=(0.13, 0.14, 0.17))',
                     '"orbital": dict(name="ORBITAL COMMONS", col=(110, 235, 255), bezel=(0.20, 0.25, 0.28))')])
sub("motifs.py", [('"halcyon": dict(a=(150, 135, 255), dim=(60, 64, 160), hot=(255, 50, 70), paper=(212, 218, 255), ink=(14, 16, 54),\n                    gold=(255, 200, 90))',
                   '"halcyon": dict(a=(176, 110, 255), dim=(78, 40, 140), hot=(255, 50, 70), paper=(238, 224, 255), ink=(24, 10, 44),\n                    gold=(255, 170, 40))'),
                  ('"orbital": dict(a=(140, 192, 255), dim=(60, 90, 170), hot=(255, 226, 150), paper=(236, 244, 255), ink=(8, 14, 40),\n                    gold=(255, 215, 120))',
                   '"orbital": dict(a=(110, 235, 255), dim=(30, 110, 140), hot=(255, 255, 255), paper=(236, 252, 255), ink=(4, 16, 28),\n                    gold=(255, 215, 120))')])
sub("scenes.py", [('"halcyon": dict(a=(150, 135, 255), dim=(60, 64, 160), hot=(255, 50, 70), paper=(222, 226, 255), ink=(14, 16, 54),\n                    gold=(255, 200, 90), steel=(196, 200, 220), blue=(60, 120, 255)),',
                   '"halcyon": dict(a=(176, 110, 255), dim=(78, 40, 140), hot=(255, 50, 70), paper=(238, 224, 255), ink=(24, 10, 44),\n                    gold=(255, 170, 40), steel=(206, 196, 226), blue=(60, 120, 255)),'),
                  ('"orbital": dict(a=(140, 192, 255), dim=(60, 90, 170), hot=(255, 226, 150), paper=(236, 244, 255), ink=(8, 14, 40),\n                    gold=(255, 215, 120), rock=(150, 120, 100), planet=(60, 110, 200)),',
                   '"orbital": dict(a=(110, 235, 255), dim=(30, 110, 140), hot=(255, 255, 255), paper=(236, 252, 255), ink=(4, 16, 28),\n                    gold=(255, 215, 120), rock=(150, 120, 100), planet=(30, 120, 150)),')])
sub("d4corp.py", [('"halcyon": dict(base=(0.22, 0.19, 0.46), name="HALCYON CIVIC")', '"halcyon": dict(base=(0.30, 0.15, 0.46), name="HALCYON CIVIC")'),
                  ('"orbital": dict(base=(0.34, 0.40, 0.52), name="ORBITAL COMMONS")', '"orbital": dict(base=(0.62, 0.72, 0.76), name="ORBITAL COMMONS")'),
                  ('"halcyon": (44, 40, 92), "orbital": (60, 70, 92)', '"halcyon": (60, 30, 96), "orbital": (120, 140, 150)')])
# Halcyon material: deep violet blueprint, amber annotations + pulses
sub("skins.py", [('im = Image.new("RGB", (W, H), (16, 18, 64))', 'im = Image.new("RGB", (W, H), (30, 12, 54))'),
                 ('fill=(30, 36, 100), width=1)\n    for y in range(0, H, int(12 * ss)):\n        d.line([(0, y), (W, y)], fill=(30, 36, 100), width=1)',
                  'fill=(52, 26, 92), width=1)\n    for y in range(0, H, int(12 * ss)):\n        d.line([(0, y), (W, y)], fill=(52, 26, 92), width=1)'),
                 ('fill=(58, 70, 170), width=max(1, ss))\n    # concentric', 'fill=(96, 50, 160), width=max(1, ss))\n    # concentric'),
                 ('d.line([(0, y), (W, y)], fill=(90, 100, 230), width=max(1, ss))', 'd.line([(0, y), (W, y)], fill=(150, 90, 230), width=max(1, ss))'),
                 ('d.line([(x, y), (x + 16 * ss, y)], fill=(210, 220, 255), width=int(2 * ss))', 'd.line([(x, y), (x + 16 * ss, y)], fill=(255, 176, 60), width=int(2 * ss))'),
                 ('outline=(70, 80, 190), width=1)', 'outline=(110, 60, 170), width=1)'),
                 ('font=fm, fill=(150, 160, 255))', 'font=fm, fill=(255, 176, 60))'),
                 ('fill=(150, 160, 255), width=1)\n    for xx', 'fill=(255, 176, 60), width=1)\n    for xx'),
                 ('d.line([(xx, y + 10 * ss), (xx, y + 16 * ss)], fill=(150, 160, 255), width=1)', 'd.line([(xx, y + 10 * ss), (xx, y + 16 * ss)], fill=(255, 176, 60), width=1)')],
    within=("def halcyon(", "def orbital("))
# Orbital material: cold cyan / white
sub("skins.py", [('arr[:] = np.array([10, 16, 44], np.float32) / 255', 'arr[:] = np.array([3, 14, 24], np.float32) / 255'),
                 ('c = [(60, 70, 190), (120, 60, 170), (40, 120, 200), (80, 50, 140)][k]', 'c = [(20, 120, 150), (40, 160, 190), (150, 215, 235), (20, 90, 120)][k]'),
                 ('d.line([(x, y), (x + 5 * ss, y)], fill=(70, 100, 180), width=1)', 'd.line([(x, y), (x + 5 * ss, y)], fill=(60, 140, 170), width=1)'),
                 ('d.line([(x, y), (x, y + 5 * ss)], fill=(70, 100, 180), width=1)', 'd.line([(x, y), (x, y + 5 * ss)], fill=(60, 140, 170), width=1)'),
                 ('outline=(130, 170, 255), width=max(1, ss))\n    d.ellipse([W * 0.1, -H * 0.2, W * 1.3, H * 0.45], outline=(100, 140, 230), width=max(1, ss))',
                  'outline=(140, 235, 255), width=max(1, ss))\n    d.ellipse([W * 0.1, -H * 0.2, W * 1.3, H * 0.45], outline=(110, 200, 230), width=max(1, ss))'),
                 ('c = mix((150, 180, 255), (255, 255, 255), b)', 'c = mix((170, 235, 250), (255, 255, 255), b)'),
                 ('d.line(st, fill=(170, 200, 255), width=max(1, int(1.2 * ss)))', 'd.line(st, fill=(200, 245, 255), width=max(1, int(1.2 * ss)))'),
                 ('d.rectangle([sx - 14 * ss, sy - 2 * ss, sx - 5 * ss, sy + 2 * ss], fill=(90, 140, 255))', 'd.rectangle([sx - 14 * ss, sy - 2 * ss, sx - 5 * ss, sy + 2 * ss], fill=(90, 220, 255))'),
                 ('d.rectangle([sx + 5 * ss, sy - 2 * ss, sx + 14 * ss, sy + 2 * ss], fill=(90, 140, 255))', 'd.rectangle([sx + 5 * ss, sy - 2 * ss, sx + 14 * ss, sy + 2 * ss], fill=(90, 220, 255))'),
                 ('fill=(28, 50, 140), outline=(170, 180, 200))', 'fill=(16, 70, 96), outline=(190, 230, 240))')],
    within=("def orbital(", "PLAYER_RGB"))
print("palette patched")
