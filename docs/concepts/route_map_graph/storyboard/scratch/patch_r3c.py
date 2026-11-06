import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
a = '''        print(w, "frames", len(fr), flush=True)
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=32 if w != "fc_dyn" else 24), tag)'''
b = '''        print(w, "frames", len(fr), flush=True)
        mark = os.path.join(SCR, "r3_done_%s" % tag)      # v3-r3: a batch already rendered with the current LOOK is skipped
        if os.path.exists(mark):
            print("skip", tag, "(already rendered)", flush=True)
            sys.exit(0)
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=32 if w != "fc_dyn" else 24), tag)
        open(mark, "w").write(json.dumps(LOOK))'''
assert a in s
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
