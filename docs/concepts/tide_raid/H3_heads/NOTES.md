# H3 beam head families (exploration, not polish)

Question: the heads (D drone blue 4690FF, N netrunner magenta FF40D6, E enforcer yellow FFEE3A) were not settled in H2. This round draws three new families plus the current one, all as solid fill + ink outline, same footprint (silhouette bbox 2.1 units = 24 / 32 px at game size), hues unchanged.

Files: `heads_board.jpg` (4 families side by side), `family_0_current.png`, `family_A_frames.png`, `family_B_daemons.png`, `family_C_hacker_glyphs.png` (each: construction, 24/32 px on the real plate crop in normal / deutan / tritan, 4 px blur, leading a ribbon (also blurred), card-tab glyph). `scripts/`: `shapes.py` (all polygons), `render.py`, `metrics.py` (+ `metrics.json`), `build.py`, `cb.py` (Machado 2009 sims, copied from H2). Rebuild: `python metrics.py metrics.json` then `python build.py <outdir>`. Plate: `plates/clean/default/plan_placed.png`, panels are real game px, shown 2x nearest.

## Research (quick, from memory of the games; no screenshots fetched or reproduced, only principles taken)
- **Into the Breach**: unit/enemy icons are 1-colour silhouettes with a dark outline, identity by outline shape and a few big internal cuts, never by hue. Taken: ink outline + 1-2 big ink cuts max.
- **Mini Metro**: stations are circle / triangle / square / diamond / pentagon... one primitive per category, distinct at tiny size and under rotation. Taken: family A (side count as the channel).
- **APP-6 / NATO frames**: shape = affiliation (rectangle friendly, diamond hostile, square neutral, quatrefoil unknown), a fill/inner mark = unit type. Taken: the diamond for the hacker, an inner mark for weight.
- **Cyberpunk 2077 quickhacks**: hacks are drawn as a bold simple glyph in a frame; daemons / breach protocol use code-glyph hex tiles. Taken: bold-glyph-on-ink; keyhole / prompt vocabulary (family C).
- **Watch Dogs DedSec**: pointer, skull, cursor and prompt text as the hacker vocabulary; masks and fox/animal ID tags. Taken: the pointer and `>_` (C), the idea of an animal-as-intrusion (B).

## The families (concept per head)
| | D drone | N netrunner | E enforcer |
|---|---|---|---|
| 0 current | dart, swallow-tail | block in four selection brackets | bull-horn C |
| A frames | triangle (3 sides, lightest) | diamond (APP-6 hostile) + data-node dot | hexagon with ink armour ring (heaviest) |
| B daemons | wasp, from above | serpent: hood, jaws, S tail | bull from above: skull, muzzle, two horns |
| C hacker glyphs | mouse pointer, tip leads | `>_` prompt: chevron leads, block cursor trails | badge shield with keyhole (lock-breaker) |

All heads travel along +x, so each has a forward point or leading mass (pointer tip, chevron, shield point, hex vertex, jaws, muzzle/horns). Silhouette numbers at 24 px (worst-case IoU over rotations between types, lower = more distinct; the outline inflates all of them): current D/N 0.45, D/E 0.50, N/E 0.66; A 0.58 / 0.57 / 0.74; B 0.79 / 0.72 / 0.71; C 0.51 / 0.54 / 0.70. Only C's N breaks into 2 pieces at 24 px (chevron + block); every other head is one piece. Areas at 24 px (px): cur 247/416/460, A 309/288/384, B 304/296/398, C 221/292/404.

## What reads at 24 px (squint and colour-blind checks on the boards)
- **A**: best. All three are one clean solid with at most one cut 3 px+ wide. D triangle, N diamond, E hexagon keep their identity at 24 px, at both headings, in deutan and in tritan (tritan makes E near-white and N red-pink, yet the shapes stay unmistakable; the current N brackets and E notch are the ones that get busy). On the ribbon the head reads as a clear terminal, the card-tab glyphs are the cleanest of all four. Blur 4 px: every family collapses to a hue blob; A's E hexagon is the largest solid and still the most visible.
- **C**: very good semantics (pointer, `>_`, keyhole shield say "hacker / ICE-breaker" instantly, and shield+keyhole is the best "armoured lock-breaker" of the lot). At 24 px the E shield and N chevron are clear; D pointer is the smallest/thinnest (area 221) and its shaft is only ~3 px, and D vs N are both arrows (IoU 0.51 is still fine thanks to the block, but the pair is the weakest at a squint).
- **B**: best concept, worst reading. At 24 px wasp and serpent are both a winged smudge (D/N IoU 0.79, highest of any pair), details (stripes, hood chevron, horn gap) are below 2 px. The bull horns survive at 32 px only. Not recommended as a type glyph on cards and locks.
- **0 current**: good D, E; the N brackets fragment into five pieces at 24 px (it only holds because the centre block is large) and read as noise on the busy city.

## Ranking
1. **A frames** (recommended). Most robust: simplest silhouettes, clear weight ramp (3 / 4 / 6 sides) that works with no hue, one family by construction, equal footprint. Fits the grammar rule "weight = severity" and the card tab. Upgrade candidates before polish: give N a slightly bolder dot or a notch so the diamond is not "just a square" at 24 px.
2. **C hacker glyphs.** Most on-theme and readable as a static glyph. If the designer wants the metaphor to win over robustness, take C. A hybrid is also possible: A's triangle for D plus C's `>_` for N plus C's keyhole shield for E.
3. **0 current**, keep as the baseline: fine except N.
4. **B daemons**, only as large decorative art (HQ / hunter), not as the 24 px head.

## Weak points and collisions (decide before polish)
- A's hexagon E collides with the hex tier plates and hex padlock / locked-route marks in the grammar (hex is already the severity container); the ink ring helps but at a squint it is "a hex plate". Fallback: pentagon or an octagon for E.
- C's shield E collides with the teal HOLDS shield-check tier glyph (different hue and keyhole, but the same shape word). C's pointer is also the generic UI cursor, so it can read as "hover" in a mouse game.
- A's triangle D and the existing arrow-like route chevrons / traffic chevrons are close cousins.
- Colour alone cannot carry the type: in tritan E becomes cream and N red-pink (same collision as the DAMAGED / BREACHED / N note in DIRECTION_REVIEW), so these shapes, not hue, have to separate N from E and DAMAGED/BREACHED plates.
- Heads at 24 px are only ~12 px per unit radius; any inner detail must be >= 3 px wide. B and the N-prompt gap break that.
- All numbers are silhouettes with an outline on a flat footprint, rendered at fixed headings 154 and -26 degrees plus the ribbon bends; no motion test (a rotating head, a head at a street turn) was done in this round.
- Not committed.
