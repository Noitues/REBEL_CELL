import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
a = '''        fr = full_jobs(w, D)
        print(w, "frames", len(fr), flush=True)
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=32 if w != "fc_dyn" else 24), w)'''
b = '''        fr = full_jobs(w, D)
        tag = w
        if len(sys.argv) > 3:            # v3-r3: a frame range [f0, f1) so a long job fits one GPU lock block
            f0, f1 = int(sys.argv[2]), int(sys.argv[3])
            fr = [x for x in fr if not x["name"][2:6].isdigit() or f0 <= int(x["name"][2:6]) < f1]
            tag = "%s_%d" % (w, f0)
        print(w, "frames", len(fr), flush=True)
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=32 if w != "fc_dyn" else 24), tag)'''
assert a in s
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
