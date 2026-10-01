p = "programs.py"
s = open(p, encoding="utf-8").read()
a = "def texture(ctx):\n    import skins\n"
assert s.count(a) == 1
s = s.replace(a, """def texture(ctx):
    im = _texture(ctx)
    o = getattr(ctx, "opts", {}) or {}
    if o.get("mascot"):
        import mascots
        im = mascots.apply(ctx, im)
    return im


def _texture(ctx):
    import skins
""")
open(p, "w", encoding="utf-8").write(s)
print("ok")
