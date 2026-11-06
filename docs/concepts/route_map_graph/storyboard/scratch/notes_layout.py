P = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\NOTES.md"
s = open(P, encoding="utf-8").read()
SEC = r'''### Mainline layout changes (designer-approved 2026-10-15) for the hand-off

These change the CITY LAYOUT that main's HQ map is built from, not only the storyboard.
- **Keys:** `sb_onecity.LAYOUT_RULES`.
- **Applied by:** `sb_onecity.apply_layout_rules()`, which writes `unified_v3.json` from the base layout.
- **Who uses it:** both looks, the HQ map and the netrun street, so the whole sequence stays one city.
- **Mainline mapping:** the counterparts belong in `content/config/city_config.tres` and the city layout builder.

| Key | Value | Rule |
|---|---|---|
| `frontage_min_floors` | 6 | Every street-level building fronting a **border-link street** rises to at least 6 floors (6 × 1.9 = 11.4 BU), plus 0–2 more floors by its key so the front is not a flat wall. A building's height counts its stacked parts. On this map 605 frontage buildings qualify, and 471 were raised. |
| `border_street_width` | 8.0 BU | Border-link streets widen from the 6 BU base tile to 8 BU: the street faces of their frontage step back 1 BU each side. The ground tiles are unchanged. |
| `hero_sign_rule` | blade + band, district pair | Every route column carries a blade sign at its street-face corner on the start side, from the 2nd floor to just under the roof, in stacked panels. It also carries a lit band under its roof. The colours alternate between the district pair along the street. Built in `onecity_build.py` from the derived columns: content follows the route, so this is not mainline layout data. |

**Scope.**
- "Border-link street" means every straight leg of every border link in the network, extended along the same street
  line by the netrun extension (60 BU). This is the street a netrun can be derived on.
- The rule changes the HQ map wherever the Cell can jack in. It is the same city at every zoom, so the HQ map shows the
  taller street fronts too.

**Effect on this run:**
- All 8 route columns now take double-height rooms (all 19 rooms span 2 floors).
- The street OVERVIEW comes 20 % closer (distance 114.5, was 140.5), because the frontage is taller relative to its
  length.

'''
s = s.replace("### Godot mapping\n", SEC + "### Godot mapping\n", 1)
open(P, "w", encoding="utf-8").write(s)
print("ok")
