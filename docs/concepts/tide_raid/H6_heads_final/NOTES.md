# H6 beam heads, final family (D worm / N thorn claw / E sea-mine / 4th beetle)

Designer picks from H5 round 3: D = T2 worm (blue 4690FF), N = T5 thorn claw (magenta FF40D6), E = T4 sea-mine / virion (yellow FFEE3A, about 15 % smaller than N), 4th = T2 beetle (neutral grey B0B6C8). In-game look = the "family test" row: heads 40-48 px in the 1920 raid view, scaled for 1280, shared rim light, core dot and outline. Nothing committed. P1_* folders untouched.

## Files
- `heads_final.png` construction sheet: each head at 256 px, vertices (green = silhouette, red = ink), footprint box, hex palette (fill / rim light / rim dark / ink / dot), build geometry, metrics, weight-by-solidity bars.
- `in_game.png` 40 / 44 / 48 px on the plan_placed city plate: normal, deutan, tritan, 4 px blur, leading a ribbon (plus ribbon blur), card-tab glyph, 1280 scale rows (heads 27 / 29 / 32 px, plus a 1280 ribbon).
- `crowd_test.png` three beams (D = cand1, N = cand2, E = cand0, lanes +-14 px, ribbon 11 px) with heads converging at HOME, and heads sitting on the t1 Sites, at 40 / 44 / 48.
- `motion.png` 4-frame idle (35 % amplitude) and travel (100 %) cycle per head, at 128 px and at game size 44 px on the city.
- `heads/D.svg N.svg E.svg X4.svg` vector source (pose f=0), plus `*_256.png` reference renders with the rim.
- `scripts/`: `heads6.py` (geometry, family contract, renderer), `common.py`, `build_final.py`, `build_ingame.py`, `build_crowd.py`, `build_motion.py`, `export_svg.py`, `metrics6.py` (`python metrics6.py metrics.json [sizes]`), `metrics.json`, `crowd_metrics.json`. Rebuild: run each `build_*.py` / `export_svg.py` by path (the crowd build takes a few minutes).

## Chosen size: 44 px at 1920 (N and D footprint), 29 px at 1280
Footprints are N = D = 2.10 u, E = beetle = 1.79 u (0.852 x N), so at 44 px: N / D 44 px, E / beetle about 37-38 px. Test range 40 / 44 / 48 all pass the overlap target; 44 is the smallest size where every part of the family contract is crisp (dot ring >= 3 px, claw tips 3 px, E armour ring and beetle split still drawn at the nominal-size >= 40 rule) while Sites stay readable. 40 is the fallback if the designer wants more air (hex hide 9 % vs 12 %); 48 is too much for the T1 cluster (see crowd).

## The family contract (in code, `heads6.py`)
- outline 7.5 % of size, ink 0E081C; corner radius .10 u applied AFTER the footprint scale (so the small E keeps the same radius); core dot ink r .18 u on every head, always in a round node (worm head, claw hub, mine body, beetle head); rim light screen-space, top-left lighter (+38 % toward white), bottom-right darker (x .66).
- Mass ramp by SOLIDITY, not size (E is smaller). Fill area at 44 px (colour fill, no outline) D 337 < beetle 518 < N 546 < E 584 px, and hull-fill ratio D .68 / beetle .69 / N .46 (open) / E .80 (solid). E gets density from: full ball, 8 short spikes with no gaps, an ink armour ring round its dot. N reads light through gaps (3 prongs). D is a single thin stroke.
- Direction: D round head + eye-dot ahead of the body (wave runs back). N hub trails, all three prongs open forward. E has a longer, fatter lead spike (reach 1.10 u, knob r .30) and the dot sits forward of centre (+.12 u); it is still the weakest forward cue, the ribbon (chevrons) carries it. Beetle head + antennae lead.

## Metrics (silhouette incl. outline, worst IoU over 24 rotations at identical centre; target <= .55)
| size | D/N | D/E | N/E | max | pieces D/N/E/4th |
|---|---|---|---|---|---|
| 40 / 44 / 48 px | .43 | .54 | .53 | **.54** | 1 / 1 / 1 / 1 |
| 27 / 29 / 32 px (1280) | .43 | .54 | .53 | .54 | 1 / 1 / 1 / 1 |
(H5 round 3 best triad: .61, N/E .61-.76.) 4th unit vs main: X/D .58, X/N .51, X/E .64 (beetle vs enforcer is the closest pair; they differ by hue and by the beetle being an oval plus antennae, flagged below). Piece counts (primitives): D 3 + dot, N 5 + dot, E 17 + dot + ring, beetle 6 + dot + split. Frame delta travel (frame 0 vs 1, 44 px): D .40, N .34, E .24, beetle .12. Full numbers in `scripts/metrics.json`.

## Crowd test (t1 cluster by HOME, default_forecast)
- Hex discs hidden by heads (worst head type parked on any T1 / T2 route anchor, any of 4 headings): 40 px 9 %, 44 px 12 %, 48 px 16 % (worst is N, the widest head). In the "head on its site" scene only t1_c is touched (4 / 6 / 9 %).
- The tier pip strip under each hex is the weak spot: a head parked on a route anchor hides 81 / 90 / 91 % of it, because the anchor sits 36 px below the hex centre and a 44 px head reaches into the pips. This is a layering issue, not a size issue (it barely changes between 40 and 48): draw Site tags and pips above the beam layer (or let heads fade under them), and the size does not swamp the Sites.
- Heads at 44 px are about the Site hex size (hex about 40-42 px wide). Three heads in one tile (HOME stretch) overlap each other when staggered under about 50 px along the same street, so the raid layer should keep a minimum head spacing of about 1 head length on shared streets.
- Recommendation: 44 px at 1920 (29 px at 1280), heads under the Site tags.

## Weak points
1. N claw still reads as a bracket / pincer at 1-2 px stroke weight in the 4 px blur (only a magenta wedge survives); it also reads a little like a Euro sign when horizontal at the earlier crescent form (fixed by the V-shaped hooked horns, still watch it at heading 180 where it reads as a "3").
2. Claw tips are now .16 u = about 3 px at 44 px (was .08 u = 1.5 px): meets the 3 px rule at game size, but at 1280 (29 px) they are 2 px; the outline (1.5-2 px) keeps them visible.
3. E direction is subtle (lead spike + forward dot); at the 4 px blur it is a round yellow blob, as every E in rounds 1-3. Armour ring and beetle split are only drawn at nominal size >= 40, so at 1280 (27-32 px) the E loses its density mark and is just a spiked ball with a dot. Option: draw the ring at all sizes with a thinner width (.09 u).
4. Beetle vs enforcer is the closest pair (.64) among all six pairs; the beetle is grey and oval so the colour channel carries it. Beetle is not part of the three main pairs.
5. Worm D is the thinnest head (hull .68, fill 337 px): at 40 px it is easy to lose against dense city ribbon-colour; its dot has only a 3 px fill ring.
6. The mine E is smaller than N by design (.852 x), so in a tile E reads the smallest of the three even though it is the heaviest: the cue is its solid yellow mass and the chevron ribbon.
7. The SVGs have no rim light (nanosvg has no clip or filter): add it in Godot as a screen-space shader (offset the alpha by 0.055 x size x .75 px, top-left lite +38 %, bottom-right x .66) or use the 256 px PNGs. The outline is a stroke of .37 u (2 x .185 u dilation) under the body, linejoin round.
8. Motion: travel cycles are procedural (S-wave phase, pincer snap, alternating spike pulse, antenna sweep), not hand-keyed; the E motion (.24 frame delta) is deliberately small so the heavy unit does not jitter.
