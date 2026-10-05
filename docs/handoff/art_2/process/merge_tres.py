"""Structural three-way union merge of a Godot .tres (ui_motion.tres style).
usage: python merge_tres.py BASE_FILE OURS_FILE THEIRS_FILE OUT_FILE
  (get them with: git show $(git merge-base HEAD MERGE_HEAD):<path> > base; git show HEAD:<path> > ours;
   git show MERGE_HEAD:<path> > theirs)
- A sub_resource / ext_resource present on both sides: if one side left it as in BASE, the other side's
  edit wins; if both edited it differently, OURS wins and it is listed as a CONFLICT to check by hand.
- New blocks from THEIRS are appended (with the comment lines just above them).
- entries = ours' order + theirs' new refs (refs either side removed relative to base stay removed).
- load_steps = sub_resources + ext_resources + 1."""
import io, re, sys


def blocks(text):
    lines = text.split("\n")
    head = lines[0]
    chunks, pending, cur = [], [], None
    for l in lines[1:]:
        if l.startswith("[ext_resource") or l.startswith("[sub_resource") or l.startswith("[resource]"):
            if cur is not None:
                chunks.append(cur)
            cur = {"pre": pending, "lines": [l]}
            pending = []
        elif cur is None or l.startswith(";"):
            pending.append(l)
        else:
            if pending:
                cur["lines"].extend(pending)
                pending = []
            cur["lines"].append(l)
    if cur is not None:
        cur["lines"].extend(pending)
        chunks.append(cur)
    return head, chunks


def key(c):
    m = re.search(r'id="([^"]+)"', c["lines"][0])
    return (c["lines"][0].split()[0], m.group(1) if m else "[resource]")


def body(c):
    return "\n".join(l for l in c["lines"]).strip()


def entries(c):
    for l in c["lines"]:
        if l.startswith("entries = "):
            return re.findall(r'SubResource\("([^"]+)"\)', l)
    return []


base_t, ours_t, theirs_t = (io.open(p, encoding="utf-8", newline="").read() for p in sys.argv[1:4])
_, bc = blocks(base_t)
oh, oc = blocks(ours_t)
_, tc = blocks(theirs_t)
B = {key(c): c for c in bc}
T = {key(c): c for c in tc}
O = {key(c): c for c in oc}
conflicts = []
out_chunks = []
for c in oc:
    k = key(c)
    if k[1] == "[resource]":
        continue
    if k in T:
        b, t = B.get(k), T[k]
        if body(c) == body(t):
            out_chunks.append(c)
        elif b is not None and body(c) == body(b):
            out_chunks.append(t)  # only theirs edited it
        elif b is not None and body(t) == body(b):
            out_chunks.append(c)  # only ours edited it
        else:
            out_chunks.append(c)
            conflicts.append(k[1])
    elif k in B:
        continue  # theirs deleted it and ours left it unchanged? keep ours only if ours edited it
    else:
        out_chunks.append(c)
for c in tc:
    k = key(c)
    if k[1] == "[resource]" or k in O:
        continue
    if k in B:
        continue  # ours deleted it
    out_chunks.append(c)
ro = [c for c in oc if key(c)[1] == "[resource]"][0]
rt = [c for c in tc if key(c)[1] == "[resource]"][0]
rb = [c for c in bc if key(c)[1] == "[resource]"]
eb = set(entries(rb[0])) if rb else set()
eo, et = entries(ro), entries(rt)
removed = (eb - set(eo)) | (eb - set(et))
allref = [x for x in eo if x not in removed] + [x for x in et if x not in eo and x not in removed]
res_lines = []
for l in ro["lines"]:
    if l.startswith("entries = "):
        l = 'entries = Array[ExtResource("1_entry")]([' + ", ".join('SubResource("%s")' % x for x in allref) + "])"
    res_lines.append(l)
out = [oh]
for c in out_chunks:
    out.extend(c["pre"])
    out.extend(c["lines"])
out.extend(ro["pre"])
out.extend(res_lines)
s = "\n".join(out)
subs = len(re.findall(r"^\[sub_resource ", s, re.M))
exts = len(re.findall(r"^\[ext_resource ", s, re.M))
s = re.sub(r"load_steps=\d+", "load_steps=%d" % (subs + exts + 1), s, count=1)
ids = re.findall(r'^\[sub_resource [^\]]*id="([^"]+)"', s, re.M)
assert len(ids) == len(set(ids)), "duplicate sub_resource ids"
missing = [x for x in allref if x not in ids]
assert not missing, missing
assert s.count("[resource]") == 1 and s.index("[resource]") > s.rindex("[sub_resource")
io.open(sys.argv[4], "w", encoding="utf-8", newline="").write(s)
print("ok subs", subs, "entries", len(allref), "both-edited (ours kept, CHECK):", conflicts)
