# REST / WORKSHOP / CACHE in Godot (nodes rounds 2 and 3, designer picks)

Branch `art/look-nodes` (worktree D:/rc_art/godot_look_nodes, rebased by the coordinator onto main c68fe831). Sheet: `impl_sheet.jpg` (then = main c68fe831, now = art/look-nodes;
1920x1080, `--reduce-effects`). Frames: `frames/then_*.png`, `frames/now_*.png` (`frames/r2_now_*.png` = round 2's, the dark CACHE crimson). Captures:
`tools/design_lab/nodes_capture.tscn` through `tools/run_windowed.py` from detached worktrees of each tree (imported first, removed after), under the GPU lock helper
(ME `solace_nodes`); `scripts/cap_run.py`, `scripts/impl_sheet.py`, `scripts/measure.py`.

## Round 3 (art-pass review of round 2)

1. **CACHE colour: a brighter, hotter brick red, `#D22C40`** (`Palette.ROUTE_CACHE`; the CACHE room glow in `street_route.tres` follows: 0.8235, 0.1725, 0.251; the sticker's
   bricks are that red, the loose brick and its lit hole a lighter coral). Held by `test_route_node_icons`: dE76 >= 30 against every kind hue, room colour and state ring under
   **normal, protan and deutan**. **Tritan drops** (reported, not held): least 9, against the elite room glow `#FF591F` (the ELITE ring and RACK are at 32 to 43; Cell pink 25).
   Only a dark red kept tritan above 30; the bright reds cannot (the elite orange sits beside them), so outline carries CACHE vs ELITE there (starburst disc vs brick stack).

   | vs | normal | protan | deutan | tritan |
   |---|---|---|---|---|
   | FIGHT ring (#6CF7FF) | 117 | 62 | 66 | 142 |
   | ELITE ring (#FF8C1A) | 54 | 58 | 41 | 32 |
   | EVENT ring (#4EFF9E) | 136 | 62 | 37 | 142 |
   | SHOP ring (#62A9FF) | 102 | 69 | 91 | 126 |
   | RACK ring (#FFA02A) | 60 | 63 | 42 | 43 |
   | REST (#BF73FF) | 91 | 81 | 95 | 76 |
   | WORKSHOP (#FFD14D) | 81 | 72 | 47 | 69 |
   | room router (#389EFF) | 107 | 73 | 98 | 124 |
   | room terminal (#4DF280) | 136 | 63 | 32 | 139 |
   | room mainframe (#6673FF) | 106 | 86 | 111 | 117 |
   | room server_rack (#FF9433) | 52 | 54 | 37 | 37 |
   | room elite (#FF591F) | 35 | 40 | 32 | **9** |
   | ring walked (#D4FF00) | 128 | 95 | 63 | 101 |
   | ring next (#FF8C1A) | 54 | 58 | 41 | 32 |
   | ring not yet (#F2F6FF) | 88 | 63 | 61 | 100 |
   | Cell pink (#FF3DA8) | 48 | 47 | 43 | 25 |
   | **least** | **35** | **40** | **32** | **9** |

   The search (sRGB grid, step 4, hues 352 to 16 degrees, saturation >= 0.7, the same set) found the brightest red that keeps normal, protan and deutan >= 30 at value 0.82 to 0.84;
   `#D22C40` is the one with the most deutan margin (31.5 against the terminal room). It is a crimson-leaning hot brick, a little pinker than the dark one.
   **Squint** (sheet, "CACHE as a red dot"): the map at 320 px wide, the two CACHE stickers of the overview, before (`#88081C`) and after: the dot's centre colour goes from
   (93,36,47) and (89,45,57) to (121,55,62) and (113,59,70), and its dE76 against the ring of pixels round it from 34 / 27 to 41 / 35. At 4 px blur the dots are red against the
   dark street in both, redder and lighter after.
2. **RUN column dropped** on REST and WORKSHOP (`_node_side` keeps the title sticker and the kind icon); the page test asserts there is no `EventRun`.
3. **Page backdrop at the event page's level.** The pages sat on the neon-wireframe city (saturation 0.77, chroma 0.099, twice the event's). They now stand on the run's Site
   close-up under the same dim as the event page: `SITE_DIM_SCREENS = ["event", "rest", "workshop"]` in `_show_site_backdrop` (the same `SiteBackdrop` and `SiteDim`, the corp tint
   at the event's share; no new numbers). Measured on the strip y 900 to 1070 of each 1920x1080 frame (no UI there), `scripts/measure.py`:

   | page | linear luma | mean sRGB | HSV saturation | chroma (S x V) |
   |---|---|---|---|---|
   | event (reference) | 0.0139 | 0.095 | 0.365 | 0.047 |
   | REST, now | 0.0154 | 0.101 | 0.383 | 0.052 |
   | WORKSHOP, now | 0.0153 | 0.101 | 0.383 | 0.052 |
   | REST / WORKSHOP, then | 0.0132 / 0.0130 | 0.079 | 0.774 / 0.773 | 0.099 |

   Within 11 % of the event's luma and 5 % of its saturation (the rest is the page's own Site still); saturation and chroma halved against then. Squint row in the sheet: REST,
   WORKSHOP and event side by side at 320 px and at a 4 px blur: the terminal windows lead.
4. **Decision-view map shot fixed.** The harness had started the run through the scene (`start_run`), which left the transit page; the HQ way (start the run, set the kinds, then open the
   scene, so the street entry is pending) lands on the street decision view. Both views are in the sheet (the decision view shows REST and WORKSHOP as the numbered rooms).

## Picks, as built (round 2, unchanged)

1. **Icons: C "Slap-tag".** Each of REST / WORKSHOP / CACHE is a die-cut sticker texture in the family's own path (`assets/netrun/route/node_<kind>.png`, 130 x 130, plus
   `_past` cut-off looks at greyscale 0.7), wired through `RouteOverlay.STICKER_ART` (the key and the HQ-run compound) and `StreetRouteOverlay.ART_OF` (the live map). The
   provisional `_draw_d4` shapes and corner badges are no longer reached for these kinds. Vector sources: `tools/art_pipeline/route_nodes/svg/C_*.svg`, exporter
   `export_route_nodes.py`. `NetrunMapView` (the old wireframe map with the placeholder glyphs) is built but hidden, so it is not touched.
2. **Pages: A's event layout.** The window is the kind's CRT in its hue (violet REST, gold WORKSHOP), the slots and offers are the event page's choice stickers in a grid (number on
   the tab), PATCH / CONFIRM REWIRE / BUY / UNDO are vinyl verb stickers, LEAVE the holo sticker; the side column holds the title sticker and the kind's sticker stamped under it.
   Every element, node name, signal and string of `node_page.gd` is kept (the leading number of a row moved onto its tab).
3. **Pencil dropped.** No plan arrows on the pages.
4. **CACHE header, header art only.** The cache sticker sits on the LOOT title's corner (`LootKindStamp`); the title stays LOOT. The strip says `CACHE n OF N`: `NODE_WORDS` had
   no REST / WORKSHOP / CACHE entries (the strip and node info said `?`).

## Size checks (round 2; the glyphs are unchanged, only CACHE's red moved)

- Map sticker, 41.6 px (1080p): the white contour, the ink keyline and all three glyphs survive.
- Legend swatch, 16.8 px: the full brick stack mushed to a slab, so the key uses `node_cache_legend.png` (fewer, fatter bricks); the white contour survives in all three.
- Silhouette soft IoU at 17 px against the shipped five: REST 0.75, WORKSHOP 0.53, CACHE 0.70 (cap in the test 0.80).

## Files outside art's usual set (look lines only unless noted)

- `scripts/ui/netrun_scene.gd`: `_show_node_page` split and `_node_side` (look); `SAFE_MARGIN_SCREENS` rest and workshop (look); `SITE_DIM_SCREENS` (look: the pages' backdrop);
  `_loot_kind_stamp` (look); **`NODE_WORDS` Rest / Workshop / Cache (a string fix; new `# TR` keys "Workshop" and "Cache": build should rerun `tools/export_text.gd`).**
- `scripts/ui/kit/node_page.gd`: look only. `content/config/street_route.tres`: the CACHE room glow. `tests/test_manifest.json`, `tests/unit/test_rg_node_pages_ui.gd` (look tests).
- Art's own: `palette.gd`, `route_ink.gd`, `route_overlay.gd`, `route_legend.gd`, `street_route_overlay.gd`, assets, tools, `tools/design_lab/nodes_capture`.

## Tests (each alone, `-gconfig=`; round 3)

test_route_node_icons 6 | test_rg_node_pages_ui 6 | test_visual_lint_static 7 | test_suite_integrity 8 | test_w3_route 5 | test_parity_route 3 | test_art7_netrun 14 | test_hq_ladder_ui 3 |
test_na23_route_view 15 | test_m14_12q_words 8 | test_parity_hq_run 13 | test_b1b_wax_pencil 22 | test_art2_attachments 15 | test_b5_netrun_pages 9 (the last two read the site backdrop).
Not run: the full suite (build's gate).
