# Decision sheets for the art-pipeline spec (2026-10-16)

Answers to the designer's review of round 1 (DIRECTION_REVIEW, "Spec answers" Q4, Q6, Q9). Each sheet is a labelled
2400 px image in this folder. The numbers behind it are in the `.json` next to it. Scripts are in `scripts/` and run on
the CPU only (PIL / numpy): no renders and no GPU. If the designer rules, PIPELINE_SPEC sections 12.1, 9.4 and 3.5
take the chosen values.

## Q4: value tolerance (`Q4_value_tolerance.png`)

**Question.** The look targets a median luma of 0.14 (Rec.709, on the final plate without UI). How far may a frame
drift before the check fails?

**What the sheet shows.** Three approved frames are re-exposed on the PNG (a linear-light exposure, no re-render) to
medians of 0.10, 0.12, 0.14, 0.16 and 0.18:
- the street overview (storyboard f_0400);
- the Halcyon HQ overview (H_overview_v2 plate);
- the night city.

Each cell gives the median, the share under 0.10 and the share over 0.85.
- At 0.10 every frame reads as black with lights.
- At 0.18 the fog greys and the neon stops popping.
- 0.12 to 0.16 reads as the same night.

The approved work already spreads: these overviews measure 0.109 (HQ), 0.120 (street) and 0.140 (city), and the
storyboard's DECISION hold (with UI) measures 0.182.

**Options.**
- **±0.02 (0.12–0.16).** Tight. It would already fail the approved HQ overview and sits on the street's edge.
- **±0.03 (0.11–0.17).** This is the spec's provisional 0.12–0.17 made symmetric.

**Recommendation.**
- **Pass:** 0.14 ±0.03 (0.11–0.17).
- **Warn:** 0.09–0.11 and 0.17–0.19. A warning is reported and never blocks.
- **Fail:** below 0.09 or above 0.19.

Keep R-VAL-2 (25–40 % under 0.10) and R-VAL-3 (≤ 2.5 % over 0.85) as separate checks. Of the three numbers, the share
under 0.10 moves fastest, so it is the real guard against crushed or washed-out frames. The note "the night city feels
too dark" is answered by the daytime version and the city grade, not by a wider band.

## Q6: hover power-cut level (`Q6_power_cut.png`)

**Question.** When the player hovers an option, everything outside the hovered branch dims. How strong should that
dimming be, and should the street and the HQ use one value?

**What "current" really is.** Spec 9.4 quotes V3 dynamic's 32 % with 40 % desaturation, and the HQ's 3D cut to 22 %
plus a 2D x0.62. The approved one-city storyboard renders no 3D cut. Its whole cut is the 2D grade in
`sb_ui.route_grade`:
- the world outside the branch goes to x0.62 with 25 % desaturation;
- the branch rooms keep their value and get a 0.5 type-colour glow.

The re-composed CURRENT cells give a frame median of 0.123–0.125, the same as the storyboard NOTES (0.125 / 0.129), so
the re-composition is faithful.

**Options shown.** The approved hover holds (frames 530 and 600) are re-composed with the same plates and UI. Only the
cut changes:
- **NO CUT:** reference.
- **CURRENT:** the branch reads about 3x brighter than the rest of the frame.
- **ALTERNATIVE, blackout with the route glowing:** the world outside goes to x0.20 with 70 % desaturation; the branch
  is lit x1.35 with a type glow of 1.0. The branch reads about 6x brighter than the rest.

**Why the blackout.** The current cut is already the gentle end. A "keep the colour, desaturate only the city" option
would land almost on top of it and would not help the decision.

**Recommendation.** Take the ALTERNATIVE level as one value for the street and the HQ, applied as a single 2D grade in
Godot. That drops the separate 3D 22 % cut at the HQ, so both pages match.
- The cost is short: the cut lasts only while the cursor rests and eases out in 0.35 s.
- Expose the level as preset values (`hover.cut_level`, `hover.cut_desat`, `hover.branch_boost`), so playtest can ease
  it toward x0.35 if it feels harsh.
- Hover frames stay exempt from the value band.

## Q9: art randomness (`Q9_art_randomness.png`)

**Question.** "What do you mean by art randomness? Can you show me examples of various randomness settings?"

**In plain words.** Art randomness is the per-game variation in how the city looks, kept apart from gameplay
randomness.
- **The game's seed decides the rules side:** the lots, the streets, the route and its rooms.
- **Separate art seeds decide only the dressing:** which building type stands on each lot, how tall it is, where the
  signs go and in what style, which windows are lit, how much the colours mix, and the roof clutter. The game derives
  these seeds from its own seed.

Under the new direction the city itself is procedural per game seed, so the same seed always rebuilds the same city.
Art never reads or advances the game's `RngService` streams, so a look can never change a fight, a reward or a route.

**How the sheet makes it.** The sheet is drawn on a small one-city block as an isometric massing in Python. The lots,
streets and three route buildings are held fixed; the route buildings are outlined in lime.
- **(a)** The same MEDIUM settings with seeds 40417, 77231 and 91002: three different-looking blocks.
- **(b)** Seed 40417 at LOW, MEDIUM and HIGH variance.

Each lot draws a fixed list of numbers from its own stream, `art/building:(i, j)`. The stream uses FNV-1a 64 over
`[layout_seed, "art/<stream>", keys...]` (spec 3.5), expanded with splitmix64 so GDScript can match it. Because the
settings only reshape those numbers, LOW, MEDIUM and HIGH show the same city, calmer or wilder. Rendering seed 40417
twice gives byte-identical images.

**Settings and presets.**

| Setting | LOW | MEDIUM (today's rules) | HIGH |
|---|---|---|---|
| `height_var` | 0.08 | 0.30 | 0.65 |
| `type_mix` | 0.15 | 0.60 | 1.0 |
| `sign_density` (x 16 % blade, 55 % shop band, 16 % roof holo) | 0.45 | 1.0 | 2.2 |
| `colour_mix` | 0.05 | 0.25 | 0.65 |
| `window_var` (around 30 % lit) | 0.03 | 0.12 | 0.30 |
| `clutter` | 0.4 | 1.0 | 2.2 |

- LOW reads as a model kit.
- HIGH loses the district identity and buries the route columns among towers and signs.

**Recommendation.**
- **Default:** MEDIUM.
- **Per-district values in the art preset:** the Sprawl leans toward HIGH (`sign_density` 1.4, `colour_mix` 0.4), and
  corp districts lean toward LOW near their HQ. This fits "colour by proximity to the nearest HQ".
- **Approve the spec's Q9 proposal:** the game derives the art seeds from an `RngService`-derived seed and exports them
  in `derive_<run>.json`, and the tools never invent a seed. This needs a TECH_SPEC / DECISIONS entry by the build
  session.
- **One caveat:** a building that carries route rooms keeps the height the game's derivation needs. `height_var`
  applies only to the non-route lots, and the derivation runs before the art pass.
