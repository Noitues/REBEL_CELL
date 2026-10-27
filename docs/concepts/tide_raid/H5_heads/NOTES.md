# H5 beam heads, round 3: six family systems (exploration, not polish)

Brief: designer liked the mix across round-2 families but not the icons themselves: wants distinct icons per type, a cohesive theme across the three, and an identity for each. So each candidate here is a SYSTEM: one theme, one construction language, three characters, plus a proof that it extends to a 4th unit.

Files: `heads_board.jpg` (6 triads at 2x: construction, family test row, 24/32 px normal/deutan/tritan, 4 px blur, ribbon normal/deutan/blur, card tab normal/tritan, 2-frame motion), `triad_T*_*.png` (detail sheet per triad, H4 layout plus theme/motif header, family test row, mass-ramp areas), `character_T1_immune.png` and `character_T6_silicon.png` (128 px idle x3, travel x3, hit/recoil/burst x3, plus all 27 states at 32 px on the city), `scripts/`. Rebuild: `python metrics.py metrics.json`, `python build5.py <outdir> [board|detail|char|all]` (`H5_TOP2=T1,T3` picks sheets). `mfast.py T3` = 24 px IoU only. Nothing committed.

## The shared construction language (the "family contract", enforced in code)
- **Silhouette classes:** D = LONG, N = BRANCHED (reaches, intrudes), E = ROUND-MASSIVE. Same footprint (2.1 u = 24 / 32 px), hues unchanged (4690FF / FF40D6 / FFEE3A).
- **One corner radius** (`R = .1 u`, `rnd()` is applied to every silhouette polygon) and **one outline weight** (renderer, 7.5 % of size).
- **One core dot** in ink (r .16-.26 u = 3 px or more at 24 px) on every head, set in a round node (hub, turret, head, capsid). This replaces H4's "a cut somewhere" with a single repeatable mark, so the three read as siblings.
- **One light treatment, new in this round:** screen-space rim light (lighter top-left rim, darker bottom-right rim, about 1.4 px at 24 px), shape-agnostic, so it can never drift between heads. Not shown on card-tab glyphs.
- **Mass ramp:** D thin, N open (gaps), E solid. Area at 24 px, D/N/E: T1 206/260/360, T6 247/344/472, T5 180/344/390, T4 205/377/408; T3 336/282/414 and T2 198/380/327 break the ramp (see weak points).
- Each triad adds one partner to the dot (knob tips, eye on the lead, port in a hub, via nodes, calyx cap).

## Research (principles only)
- Reused H4 research (APP-6 redundancy, Into the Breach flat silhouette plus 2-frame idle, Mini Metro one primitive per class, phage / virion iconography). New this round: the "family" requirement is about shared constants, not shared subject, so the constants (radius, dot, light) are in code once instead of being re-drawn per head. Web lookups for the new subjects (diatom / jellyfish / samara / chip pin-1 dot) were done from memory only, nothing copied.

## The six triads
| id | theme | D (long) | N (branched) | E (round-massive) | shared motif | mystery 4th |
|---|---|---|---|---|---|---|
| T1 immune | Solace's own immune system, weaponised | swarm cell: fat rod, knob tail flicks | programmed antibody Y, bulb ends, hub dot, arms flex | armoured phage: octagon capsid, base plate, 2 thick legs | core dot + knob on every extremity | macrophage (round cell, 3 knob pseudopods) |
| T2 zoo | black-ICE daemons caged as lab specimens | worm, round head leads | ghost: dome leads, scalloped hem, one eye-dot | logic bomb: ball, fuse, spark | one eye-dot on the lead of every beast | beetle |
| T3 robots | Solace security as sterile service robots | quad drone, 4 rotors on an X | swab probe: hub, 3 bulb-tipped prongs, cable stub | tank: chamfer hull, round turret, barrel | hub / turret with an ink port dot | sentry dome |
| T4 tide | the Tide itself, plankton drifting in | darter: round head, curving tail | jelly: dome leads, 3 knob-tipped tendrils | sea-mine / virion: ball, 8 knobbed spikes | round knob on every tip + core dot | crab |
| T5 garden | Solace's greenhouse gone feral | samara: seed leads, one long wing | thorn claw: hub, two horns, centre thorn | burr: round pod, 7 thorns, calyx cap | seed dot in a round body + trailing flat cap | mushroom |
| T6 silicon | the ICE as printed circuitry | trace bolt: staircase trace, via head leads | trace fork: node, cross trace, 2 via prongs | die: heavy square, 4 pin tabs, via dot | via dot in a round node, right-angle traces | diode |

## Metrics (silhouette incl. outline, frame 0; IoU = worst case over 24 rotations; target every pair <= .55; every head is 1 piece at 24 px)
| triad | D/N | D/E | N/E | max | 32 px max | frame delta 24 px D/N/E |
|---|---|---|---|---|---|---|
| T1 immune | .61 | .55 | .64 | .64 | see json | .21 / .23 / .07 |
| T2 zoo | .52 | .61 | .76 | .76 | | .41 / .09 / .04 |
| T3 robots | .50 | .58 | .67 | .67 | | .38 / .11 / .05 |
| T4 tide | .51 | .49 | .72 | .72 | | .15 / .16 / .17 |
| T5 garden | .42 | .46 | .63 | .63 | | .09 / .25 / .09 |
| T6 silicon | .47 | .51 | .61 | .61 | | .11 / .10 / .00 |
(Round 2 for comparison: B1 .66, H1 .67, M2 .82, H2 had .35-.58.) Full numbers in `scripts/metrics.json`.

**Target not met.** D/N and D/E are <= .55 almost everywhere (only T1 D/E = .55 borderline, T2 D/E .61, T3 D/E .58 miss). N/E is .61-.76 in every triad. Cause: the footprint is fixed at 2.1 u, so N and E both fill the same box and, with centres aligned, a branched head nests inside a round-massive one; IoU then approaches area(N)/area(E). To pass .55 the N must be at most about 0.55 of E's area (E max is about 450 px at 24 px), which means N strokes under 2 px fill or a smaller E. I stopped at the point where shrinking N started to cost legibility (the sub-3 px rule). Options for the designer: allow N/E up to .65 (T1, T5, T6 pass), or let E be a different footprint class (smaller bbox than N). Note also that the IoU test is a worst case over all rotations at identical centres; in play the colour channel adds separation.

## Ranking and recommendation
1. **T6 silicon** (recommended on shape-system strength). Best numbers of the round (max .61, ramp 247/344/472 is clean), the most unmistakable family at a squint and in the family-test row (round via nodes plus right-angle traces make D, N, E obviously one drawing hand), strongest 4th-unit extension (diode, chip, relay, all fit without new rules), and every head is a bold single piece. Weakness: it says "circuit board", not Solace or virus; and the die is a rounded square, close in spirit to a hex tier plate (it is square, with pin tabs, so no collision, but watch it next to plates).
2. **T1 immune weapon** (recommended on story). The only triad whose theme is exactly Solace-spreads-a-virus plus the heads the designer liked (antibody Y, phage). Clean ramp (206/260/360), highest D/E overlap but acceptable. Weak: phage E at 24 px is an octagon with two small brackets, the legs get lost; consider a bigger capsid with a single tail. The rod D is near the round-2 bacillus, fine but unexciting.
3. **T4 tide drifters.** Strongest single E (the sea-mine / virion) and the tidiest knob language; jelly N is a good silhouette (dome plus 3 tendrils). N/E .72 is the worst of the top group, and the darter reads as a sperm, which is both on-theme for a virus and a possible misread.
4. **T3 robots.** Quad plus tank are the readable pair the designer liked, but quad (336) is heavier than the probe (282): the ramp inverts, and the probe / quad / tank do not obviously share a body plan beyond the hub dot.
5. **T5 garden.** Good numbers (.63), but the pod burr reads close to a virion/mine and the claw looks like a bracket "E"; theme is new content (Solace garden) rather than the existing story.
6. **T2 zoo.** Ghost is the heaviest head (380 > bomb 327, inverted ramp) and reads Pac-Man-ish; N/E .76. Best "personality", worst system.

## Weak points
- N/E overlap above target in all six (above).
- Dot sizes: dots are 3.0-3.5 px at 24 px (r .16-.18); on the worm head and rod it leaves only a 1.5 px ring of fill around it. Tritan and the 4 px blur lose the dot completely (blur shows just the hue blob, same as rounds 1-2); the dot is an identity-at-close-range mark, the silhouette class carries distinctness.
- The "no sub-3 px details" rule: thin tapers (T5 claw tips, samara wing edge, T2 spark, T4 tendrils at .24 u = 2.3 px fill) are close to the limit; T3 treads, rotor blades and the T6 pin-1 marker only draw at 40 px+ on purpose.
- Direction: D, N lead clearly in T2, T3, T4, T5, T6, but T1 N and T4 E / T5 E / T3 quad are rotationally ambiguous; the ribbon carries direction.
- Light treatment is rim shading in screen space, so on an upside-down head the highlight stays top-left (intended), but at 24 px the 1 px rim lightens the outline edge on thin parts and can look like jitter on tendrils.
- Collisions checked: no hex plate (T1 phage capsid is an octagon; die is a square), no padlock, no shield, no skull, no HUNTER eye (a single ink dot on a solid body is not a ringed eye; T2 N ghost with one dot is the closest, flag if designer thinks it is), no lime halo, no cursor shape, no cross anywhere (T3 quad is an X, which is not a cross; antibody is a Y). T5 claw looks like a trident / lyre; T3 probe is a three-prong fork (jack-in grammar has a plug; not the same shape).
- Character sheets: hit / recoil / burst are generated by squash, recolour and bursting the live polygons, not hand-drawn frames, so they prove the identity survives breakup (T6 pieces stay readable, T1 antibody falls into knobs) but are not the final animation. Dark burst frames are low contrast on purpose.
- Numbers are 24 / 32 px silhouettes at heading 0 with the 24-rotation sweep; no real rotating head at a street turn. The family-test 4th unit uses a neutral hue and is hypothetical, no hue is proposed.
