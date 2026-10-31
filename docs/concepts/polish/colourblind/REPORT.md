# Colour-blind check of the corp hues (2026-10-30)

- **Method:** Machado 2009 matrices at severity 1.0 in linear RGB, with CIE ΔE2000 between every pair.
  - 21 pairs were checked; a pair under ΔE 10 is a risk.
  - **Caveat:** the head and tail colours were estimated as hue x 0.55 and x 0.38. The game's real traffic values may differ, so recheck them after the final values are fixed.
- **Sheet:** `sheet.jpg`. Script and numbers: `scripts/cb_check.py` and `scripts/results.json`.

## Risky pairs (7 of 21)
| Pair | Deficiency | ΔE2000 |
|---|---|---|
| Solace lime #96FF46 vs Cell lime #D4FF00 | protan | 1.47 |
| Solace lime vs Cell lime | deutan | 4.64 |
| Solace lime vs Cell lime | normal vision | 10.17 (borderline) |
| Solace tail vs Meridian tail | deutan | 6.10 |
| Solace head vs Meridian head | deutan | 9.96 |
| Solace tail vs Aurelian tail | tritan | 7.03 |
| Solace head vs Aurelian head | tritan | 9.00 |
| Solace head vs Orbital head | tritan | 8.87 |
| Solace tail vs Orbital tail | tritan | 7.51 |

**The worst case** is Solace lime against Cell lime under protanopia (ΔE 1.47). They are nearly the same colour.

## Suggested fixes (colour and cue only, no rule changes)
1. **Solace and Cell lime:** separate them by a value step (one darker or lighter), and add a non-colour cue: a shape, stripe or icon wherever both appear on one screen.
2. **Solace and Meridian (deutan):** separate by value.
3. **Solace against Aurelian and Orbital (tritan):** separate by value or saturation.
4. Where the traffic head and tail are the only carrier of corp identity, building colour and signs still carry the corp, so the risk is limited to the cars.
