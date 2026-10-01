p = "scripts/programs.py"
s = open(p, encoding="utf-8").read()
a = """    if o.get("mascot"):
        import mascots
        im = mascots.apply(ctx, im)
    return im"""
assert s.count(a) == 1
s = s.replace(a, """    if o.get("art"):
        import icons8
        im = icons8.screen(ctx, im)
    elif o.get("mascot"):
        import mascots
        im = mascots.apply(ctx, im)
    return im""")
open(p, "w", encoding="utf-8").write(s)
print("ok")
