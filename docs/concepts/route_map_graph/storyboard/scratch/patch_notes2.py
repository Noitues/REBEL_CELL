import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "NOTES.md")
s = open(p, encoding="utf-8").read()
r = [("Only a faint cool edge stays, in the top 0.05 BU under the cut plane.", "There is no top-edge line (round 2b: it read as UI frames), so the wet street's reflections are the only light down there."),
     ("`plinth` (albedo 0.012, edge 0.05, edge_k 0.05;", "`plinth` (albedo 0.012, edge_k 0;"),
     ("Each rig is a soft 3° cone plus a 0.9° core (r3 hero soft/core), light-linked to the fog only.", "Each rig is one soft 6° cone with a fully soft edge (blend 1.0), light-linked to the fog only. It widens with distance and fades from the source by the inverse square, so it shows where it crosses fog. Round 2b dropped the 0.9° core: it read as a stage laser."),
     ("`beams` 6, `beam` 2e7, `beam_rise` 1.35, `fog_peak` 0.03,", "`beams` 6, `beam` 2e7 (× 1.5), `beam_cone` 6, `beam_rise` 1.35, `fog_peak` 0.039 (round 2b: 1.3× so the layering reads),")]
for a, b in r:
    assert a in s, a
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
