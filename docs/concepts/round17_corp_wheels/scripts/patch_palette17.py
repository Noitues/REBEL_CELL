"""One-off (kept as a record): push Solace (lime / leaf green, warm) and Orbital (ice white + steel blue on near-black) apart.
Halcyon (violet + amber) is unchanged."""
import os

H = os.path.dirname(os.path.abspath(__file__))


def sub(fn, pairs, within=None):
    p = os.path.join(H, fn)
    s = open(p, encoding="utf-8").read()
    a, b = (s.index(within[0]), s.index(within[1], s.index(within[0]))) if within else (0, len(s))
    body = s[a:b]
    for x, y in pairs:
        assert x in body, (fn, x[:70])
        body = body.replace(x, y)
    open(p, "w", encoding="utf-8", newline="\n").write(s[:a] + body + s[b:])


SOL = (150, 255, 70)       # lime / leaf green
SOL_DIM = (50, 110, 20)
ORB = (170, 205, 255)      # ice blue-white
ORB_DIM = (60, 80, 130)

sub("slicelib.py", [('"solace": dict(name="SOLACE BIOSYSTEMS", col=(61, 255, 139), bezel=(0.20, 0.22, 0.22))',
                     '"solace": dict(name="SOLACE BIOSYSTEMS", col=%s, bezel=(0.22, 0.24, 0.18))' % (SOL,)),
                    ('"orbital": dict(name="ORBITAL COMMONS", col=(110, 235, 255), bezel=(0.20, 0.25, 0.28))',
                     '"orbital": dict(name="ORBITAL COMMONS", col=%s, bezel=(0.20, 0.22, 0.28))' % (ORB,))])
sub("motifs.py", [('"solace": dict(a=(61, 255, 139), dim=(20, 110, 80), hot=(255, 70, 150), paper=(226, 244, 238), ink=(8, 34, 30)),',
                   '"solace": dict(a=%s, dim=%s, hot=(255, 70, 150), paper=(240, 250, 226), ink=(16, 34, 8)),' % (SOL, SOL_DIM)),
                  ('"orbital": dict(a=(110, 235, 255), dim=(30, 110, 140), hot=(255, 255, 255), paper=(236, 252, 255), ink=(4, 16, 28),',
                   '"orbital": dict(a=%s, dim=%s, hot=(255, 255, 255), paper=(244, 248, 255), ink=(4, 6, 18),' % (ORB, ORB_DIM))])
sub("scenes.py", [('"solace": dict(a=(61, 255, 139), dim=(20, 110, 80), hot=(255, 70, 150), paper=(226, 244, 238), ink=(8, 34, 30),\n                   glass=(170, 255, 225)),',
                   '"solace": dict(a=%s, dim=%s, hot=(255, 70, 150), paper=(240, 250, 226), ink=(16, 34, 8),\n                   glass=(220, 255, 190)),' % (SOL, SOL_DIM)),
                  ('"orbital": dict(a=(110, 235, 255), dim=(30, 110, 140), hot=(255, 255, 255), paper=(236, 252, 255), ink=(4, 16, 28),\n                    gold=(255, 215, 120), rock=(150, 120, 100), planet=(30, 120, 150)),',
                   '"orbital": dict(a=%s, dim=%s, hot=(255, 255, 255), paper=(244, 248, 255), ink=(4, 6, 18),\n                    gold=(255, 215, 120), rock=(150, 120, 100), planet=(70, 100, 190)),' % (ORB, ORB_DIM))])
sub("tiles.py", [('"solace": ((61, 255, 139), (255, 70, 150)),', '"solace": (%s, (255, 70, 150)),' % (SOL,)),
                 ('"orbital": ((110, 235, 255), (236, 252, 255)),', '"orbital": (%s, (255, 255, 255)),' % (ORB,))])
sub("d4corp.py", [('"solace": dict(base=(0.74, 0.77, 0.75), name="SOLACE BIOSYSTEMS")', '"solace": dict(base=(0.78, 0.80, 0.70), name="SOLACE BIOSYSTEMS")'),
                  ('"orbital": dict(base=(0.62, 0.72, 0.76), name="ORBITAL COMMONS")', '"orbital": dict(base=(0.30, 0.33, 0.42), name="ORBITAL COMMONS")')])
# Solace material: leaf-green glass (was teal)
sub("skins.py", [('top = np.array([12, 48, 44], np.float32) / 255\n    bot = np.array([6, 26, 26], np.float32) / 255',
                  'top = np.array([24, 52, 12], np.float32) / 255\n    bot = np.array([10, 26, 6], np.float32) / 255'),
                 ('fill=(200, 255, 235, 18)', 'fill=(230, 255, 190, 18)'),
                 ('fill=(30, 110, 80, 70)', 'fill=(70, 120, 20, 70)'),
                 ('fill=(20, 70, 50, 220)', 'fill=(40, 80, 12, 220)')], within=("def solace(", "def halcyon("))
# Orbital material: near-black space, white stars, steel-blue nebula
sub("skins.py", [('arr[:] = np.array([3, 14, 24], np.float32) / 255', 'arr[:] = np.array([4, 5, 14], np.float32) / 255'),
                 ('c = [(20, 120, 150), (40, 160, 190), (150, 215, 235), (20, 90, 120)][k]', 'c = [(40, 60, 130), (70, 90, 170), (150, 160, 200), (30, 40, 90)][k]'),
                 ('fill=(60, 140, 170), width=1)\n    for x', 'fill=(70, 90, 140), width=1)\n    for x'),
                 ('d.line([(x, y), (x, y + 5 * ss)], fill=(60, 140, 170), width=1)', 'd.line([(x, y), (x, y + 5 * ss)], fill=(70, 90, 140), width=1)'),
                 ('outline=(140, 235, 255), width=max(1, ss))\n    d.ellipse([W * 0.1, -H * 0.2, W * 1.3, H * 0.45], outline=(110, 200, 230), width=max(1, ss))',
                  'outline=(200, 215, 255), width=max(1, ss))\n    d.ellipse([W * 0.1, -H * 0.2, W * 1.3, H * 0.45], outline=(150, 170, 230), width=max(1, ss))'),
                 ('c = mix((170, 235, 250), (255, 255, 255), b)', 'c = mix((200, 210, 255), (255, 255, 255), b)'),
                 ('d.line(st, fill=(200, 245, 255), width=max(1, int(1.2 * ss)))', 'd.line(st, fill=(230, 236, 255), width=max(1, int(1.2 * ss)))'),
                 ('fill=(16, 70, 96), outline=(190, 230, 240))', 'fill=(30, 40, 96), outline=(210, 216, 240))')], within=("def orbital(", "PLAYER_RGB"))
print("palette 17 patched")
