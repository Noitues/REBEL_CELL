p='lw_install.py'
s=open(p).read()
s=s.replace("""    s = SK[0]
    _orig_paint(L, f, beat, which=which, with_base=with_base)
""","""    s = SK[0]
    import corp_kinds as CK
    restore = CK.use(getattr(s, 'kind_gain', None))
    try:
        _orig_paint(L, f, beat, which=which, with_base=with_base)
    finally:
        restore()
""")
open(p,'w').write(s)
