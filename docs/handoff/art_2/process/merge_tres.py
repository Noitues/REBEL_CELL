"""Structural union merge of a Godot .tres (ui_motion.tres style) from two full versions.
usage: python merge_tres.py OURS_FILE THEIRS_FILE OUT_FILE
Keeps ours' header, ext_resources and sub_resources in order; appends theirs' sub_resources whose id is
new (with any comment lines directly above them); entries = ours' order + theirs' new refs; load_steps fixed."""
import io, re, sys

def blocks(text):
    # split into: header line, then chunks starting at each [ext_resource|sub_resource|resource] line,
    # carrying preceding comment/blank lines with the chunk they precede
    lines = text.split("\n")
    head = lines[0]
    chunks, pending, cur = [], [], None
    for l in lines[1:]:
        if l.startswith("[ext_resource") or l.startswith("[sub_resource") or l.startswith("[resource]"):
            if cur is not None:
                chunks.append(cur)
            cur = {"pre": pending, "lines": [l]}
            pending = []
        elif cur is None:
            pending.append(l)
        elif l.startswith(";") or (l.strip() == "" and cur is not None and cur["lines"][0].startswith("[sub")):
            pending.append(l) if l.startswith(";") else cur["lines"].append(l)
        else:
            if pending:
                cur["lines"].extend(pending); pending = []
            cur["lines"].append(l)
    if cur is not None:
        cur["lines"].extend(pending)
        chunks.append(cur)
    return head, chunks

def cid(c):
    m = re.search(r'id="([^"]+)"', c["lines"][0])
    return (c["lines"][0].split()[0], m.group(1) if m else None)

ours = io.open(sys.argv[1], encoding="utf-8", newline="").read()
theirs = io.open(sys.argv[2], encoding="utf-8", newline="").read()
oh, oc = blocks(ours)
th, tc = blocks(theirs)
have = {cid(c) for c in oc}
res_o = [c for c in oc if c["lines"][0].startswith("[resource]")][0]
res_t = [c for c in tc if c["lines"][0].startswith("[resource]")][0]
new = [c for c in tc if not c["lines"][0].startswith("[resource]") and cid(c) not in have]
body = [c for c in oc if not c["lines"][0].startswith("[resource]")]
out_chunks = body + new
def entries(c):
    for l in c["lines"]:
        if l.startswith("entries = "):
            return re.findall(r'SubResource\("([^"]+)"\)', l)
    return []
eo, et = entries(res_o), entries(res_t)
allref = eo + [x for x in et if x not in eo]
res_lines = []
for l in res_o["lines"]:
    if l.startswith("entries = "):
        l = 'entries = Array[ExtResource("1_entry")]([' + ", ".join('SubResource("%s")' % x for x in allref) + "])"
    res_lines.append(l)
out = [oh]
for c in out_chunks:
    out.extend(c["pre"]); out.extend(c["lines"])
out.extend(res_o["pre"]); out.extend(res_lines)
s = "\n".join(out)
subs = len(re.findall(r"^\[sub_resource ", s, re.M))
exts = len(re.findall(r"^\[ext_resource ", s, re.M))
s = re.sub(r"load_steps=\d+", "load_steps=%d" % (subs + exts + 1), s, count=1)
ids = re.findall(r'^\[sub_resource [^\]]*id="([^"]+)"', s, re.M)
assert len(ids) == len(set(ids)), "dup ids"
missing = [x for x in allref if x not in ids]
assert not missing, missing
assert s.count("[resource]") == 1
assert s.index("[resource]") > s.rindex("[sub_resource")
io.open(sys.argv[3], "w", encoding="utf-8", newline="").write(s)
print("ok subs", subs, "new", len(new), "entries", len(allref))
