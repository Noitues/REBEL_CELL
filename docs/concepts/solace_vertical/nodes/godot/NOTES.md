# REST / WORKSHOP / CACHE in Godot (nodes round 2, designer picks)

Branch `art/look-nodes` (worktree D:/rc_art/godot_look_nodes, on main 63364307). Sheet: `impl_sheet.jpg` (then = main 63364307, now = art/look-nodes; 1920x1080,
`--reduce-effects`). Frames: `frames/then_*.png`, `frames/now_*.png`. Captures: `tools/design_lab/nodes_capture.tscn` through `tools/run_windowed.py` from
detached worktrees of each commit (imported first, removed after), under the GPU lock helper (ME `solace_nodes`); `scripts/cap_run.py`, `scripts/impl_sheet.py`.

## Picks, as built

1. **Icons: C "Slap-tag".** Each of REST / WORKSHOP / CACHE is a die-cut sticker texture in the family's own path (`assets/netrun/route/node_<kind>.png`, 130 x 130, plus
   `_past` cut-off looks at greyscale 0.7), wired through `RouteOverlay.STICKER_ART` (the key and the HQ-run compound) and `StreetRouteOverlay.ART_OF` (the live map). The
   provisional `_draw_d4` shapes and corner badges are no longer reached for these kinds. Vector sources: `tools/art_pipeline/route_nodes/svg/C_*.svg`, exporter
   `export_route_nodes.py`. `NetrunMapView` (the old wireframe map with the placeholder glyphs) is built but hidden (`map_view.visible = false`, "the route model"), so it is not touched.
2. **Pages: A's event layout.** The window is the kind's CRT in its hue (violet REST, gold WORKSHOP), the slots and offers are the event page's choice stickers in a grid (number on
   the tab), PATCH / CONFIRM REWIRE / BUY / UNDO are vinyl verb stickers, LEAVE the holo sticker; the side column holds the RUN terminal (the existing `_event_run_window`), the title
   sticker and the kind's sticker stamped under it. Every element, node name, signal and string of `node_page.gd` is kept (the leading number of a row moved onto its tab).
3. **Pencil dropped.** No plan arrows on the pages.
4. **CACHE header, header art only.** The cache sticker sits on the LOOT title's corner (`LootKindStamp`); the title stays LOOT. The strip says `CACHE n OF N`: `NODE_WORDS` had
   no REST / WORKSHOP / CACHE entries, so the strip and the node info said `?` (see "then" in the sheet); they now read Rest / Workshop / Cache.
5. **CACHE hue.** Brick crimson `#88081C` (`Palette.ROUTE_CACHE`, also the CACHE room glow in `street_route.tres`), off FIGHT's cyan.

## CACHE hue and its distances (dE76; sRGB to linear RGB, Machado 2009 severity 1 for protan / deutan / tritan; `scripts/table.py`)

The set a kind hue is measured against: the five shipped sticker ring colours, REST and WORKSHOP, the five street room glow colours (router, terminal, mainframe, server_rack, elite),
the three state ring colours and the Cell pink. Required: >= 30 against every one, under all four visions. Result (least over the set): **normal 50, protan 49, deutan 48, tritan 34.**

| vs | normal | protan | deutan | tritan |
|---|---|---|---|---|
| FIGHT ring (#6CF7FF) | 113 | 77 | 75 | 129 |
| ELITE ring (#FF8C1A) | 62 | 68 | 58 | 37 |
| EVENT ring (#4EFF9E) | 131 | 78 | 55 | 129 |
| SHOP ring (#62A9FF) | 98 | 79 | 91 | 111 |
| RACK ring (#FFA02A) | 67 | 73 | 59 | 44 |
| REST (#BF73FF) | 92 | 87 | 94 | 67 |
| WORKSHOP (#FFD14D) | 85 | 85 | 66 | 66 |
| room router (#389EFF) | 102 | 81 | 97 | 109 |
| room terminal (#4DF280) | 130 | 78 | 52 | 125 |
| room mainframe (#6673FF) | 103 | 91 | 108 | 101 |
| room server_rack (#FF9433) | 60 | 65 | 55 | 40 |
| room elite (#FF591F) | 50 | 49 | 48 | 34 |
| ring walked (#D4FF00) | 127 | 106 | 81 | 93 |
| ring next (#FF8C1A) | 62 | 68 | 58 | 37 |
| ring not yet (#F2F6FF) | 90 | 79 | 74 | 95 |
| Cell pink (#FF3DA8) | 59 | 54 | 49 | 40 |

How it was found: a grid over sRGB (step 8) against the same set. The bright hues are all taken (every bright cyan, green, blue, violet, pink, orange and yellow is within 30 of a kind),
so the free axis is lightness: only dark saturated colours clear 30 under all four visions (dark blue, oxblood). Brick crimson is the one that is also a stash (bricks). The darker
the hue the farther it is (#780018 reaches 40 under tritan); #88081C keeps the glyph readable beside its ink outline. `test_route_node_icons` holds the numbers.
Honest limit: the *sticker fills* (ELITE's dark red-brown disc `HARM_INK`, RACK's brown) are not in the set; CACHE crimson is near ELITE's fill (about dE 20). Outline separates them
(starburst disc vs brick stack), not hue.

## Size checks

- Map sticker, 41.6 px (1080p): the white contour, the ink keyline and all three glyphs survive; the house's door and moon, the spanner's jaw and the bricks' gaps read (sheet, "ICON CROPS").
- Legend swatch, 16.8 px: house and spanner read at 1x; the full brick stack mushed to a red slab, so the key uses `node_cache_legend.png` (fewer, fatter bricks, wider mortar,
  a bigger loose brick), via `RouteOverlay.draw_sticker(..., small)` / `LEGEND_ART`. The white contour survives at 16.8 px in all three.
- Silhouette soft IoU at 17 px against the shipped five: REST 0.75, WORKSHOP 0.53, CACHE 0.70 (the shipped discs score 0.98 against each other). The test caps it at 0.80.
- 320 px squint and 4 px blur: in the sheet's squint row (colour and greyscale) the three read as non-discs among the discs, ring states unchanged.

## Files outside art's usual set (look lines only unless noted)

- `scripts/ui/netrun_scene.gd`: `_show_node_page` wraps the page in a split with a new `_node_side` (look); `SAFE_MARGIN_SCREENS` gains rest and workshop (look);
  `_show_reward_page` adds the CACHE stamp via `_loot_kind_stamp` (look); **`NODE_WORDS` gains Rest / Workshop / Cache (a string fix: they said `?`; new `# TR` keys
  "Workshop" and "Cache", "Rest" already exists: `tools/export_text.gd` should be rerun by build).**
- `scripts/ui/kit/node_page.gd`: look only (see above). No signal, name or session call changed.
- `content/config/street_route.tres`: the CACHE room glow colour (look config).
- `tests/test_manifest.json`: one new fast-tier script; `tests/unit/test_rg_node_pages_ui.gd`: three look tests added (build's flow tests unchanged and green).
- Art's own: `scripts/ui/kit/palette.gd` (ROUTE_* tokens), `route_ink.gd` (`accent_of`), `route_overlay.gd`, `route_legend.gd`, `street_route_overlay.gd`, assets, tools.

## Tests (each alone, `-gconfig=`)

test_route_node_icons (new, fast): 6 pass | test_rg_node_pages_ui: 6 pass (3 new) | test_visual_lint_static: 7 pass | test_suite_integrity: 8 pass | test_w3_route 5 | test_parity_route 3 |
test_art7_netrun 14 | test_hq_ladder_ui 3 | test_na23_route_view 15 | test_m14_12q_words 8 | test_parity_hq_run 13 | test_b1b_wax_pencil 21. Not run: the full suite (build's gate).

## Known, for the designer

- The RUN terminal repeats HP / Cycles that the top bar already shows (the shipped event page dropped its RUN terminal for that reason, B5); it is in because the pick named the RUN
  column. One line to remove (`side.add_child(_event_run_window(s))`).
- The title sticker on the pages is the white word sticker (the event page's TERMINAL); the kind hue lives in the window and the stamp.
- The decision-view (zoomed) map shot is not in the sheet: the capture harness's second toggle landed on the transit page; the overview shows the numbered choices.
