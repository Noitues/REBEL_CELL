import io, re, sys

ROOT = "C:/Users/noitu/Documents/Godot/rebel_cell/"
HUNK = re.compile(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n", re.S)


def rd(p):
    with io.open(ROOT + p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    assert "<<<<<<<" not in s and ">>>>>>>" not in s, p
    with io.open(ROOT + p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def union(p):
    s = rd(p)
    wr(p, HUNK.sub(lambda m: m.group(1) + m.group(2), s))


for p in ["assets/text/strings.csv", "docs/DECISIONS.md", "scripts/data/ui_motion_data.gd",
          "tools/design_lab/motion_lab.gd"]:
    union(p)


def manifest(m):
    ours, theirs = m.group(1), m.group(2)
    indent = re.match(r"[ \t]*", ours).group(0)
    closing = indent + '\t"tier": "full"\n' + indent + "},\n"
    return ours + closing + theirs


s = rd("tests/test_manifest.json")
wr("tests/test_manifest.json", HUNK.sub(manifest, s))


def tres(m):
    ours, theirs = m.group(1), m.group(2)
    theirs_sub = theirs.split("[resource]")[0]
    head, tail = ours.split("[resource]")
    tail = tail.replace('SubResource("m_defeat_stamp")])',
                        'SubResource("m_defeat_stamp"), SubResource("m_flight_land_pulse")])')
    assert "m_flight_land_pulse" in tail
    return head + theirs_sub + "[resource]" + tail


s = rd("content/config/ui_motion.tres")
s = HUNK.sub(tres, s)
n = s.count('[sub_resource type="Resource"') + s.count("[ext_resource") + 1
s = re.sub(r"load_steps=\d+", "load_steps=%d" % n, s, count=1)
wr("content/config/ui_motion.tres", s)
print("load_steps", n)
