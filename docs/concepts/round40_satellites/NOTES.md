# Round 40: satellites v3 and the parasite ring v2

This round builds on round 39, which is untouched. The pieces the designer liked are kept as they were: icon and number size, the destroyed bit explosion, the spin, the bodyguard state, and the parasite ring's colours.

## Files
| File | What it shows |
|---|---|
| `satellites_v3.png` | Botnet and Care Swarm at r = 220 and r = 60, a close-up of the dock, and the replace sequence as 5 stills. |
| `replace.gif` | The replace sequence animated: 15 frames, about 2 MB. |
| `parasite_needle_options.png` | Three layouts for how the parasite ring sits against the needle, on the player's wheel. Below them: layout A on the wheel at r = 220 and r = 60, and the rules. |
| `parasite_trigger.gif` | Layout A in play: 16 frames, about 2.4 MB. The parasite rides the slice through a spin, the needle lands on the host slice, and the parasite's in-line sub-slice fires. |
| `scripts/` | `sat3.py` holds the dock, the replace effects and the parasite ring. `make_r40.py sheet`, `replace`, `options` and `trigger` build the outputs. |

## Satellites
1. **Docking.**
   - The struts and the cradle are gone. The docked slice's own outline (its program-colour hairline) swells out of the host rim in one smooth curved lobe that wraps the satellite.
   - The lobe has one dark fill and one outline. It is built as a metaball of three shapes: a rim arc over the slice, a waisted neck, and a collar round the satellite.
   - **Godot:** one shader-drawn shape per dock, or a pre-baked 9-patch-style arc sprite tinted with `type_color`.
2. **Replace** has four beats:
   1. The NEW satellite arrives and hovers just outside, with a dashed amber "waiting" ring.
   2. The CURRENT satellite undocks. It breaks into blocks and streams back to the host core as green 0/1 bits.
   3. The core pulses green as the bits arrive.
   4. The new satellite glides in and installs, and the dock lobe lights again.

   Nothing reads as rejected or killed. Red bits are kept for "destroyed" only.

## Parasite ring v2
- **It goes on either wheel.** Mostly it is the boss putting it on the player's wheel, as shown here on Breaker.
- **It is thinner.** It is about 90 master units deep, against 150 in round 39. Each of its slices uses the drone layout: a big glyph and a big value spread along the slice, the glyph tinted the same faded red as its number.
- **Its slices reuse real slice effects, including ones that help the boss:**

  | Slice | Effect |
  |---|---|
  | EXPLOIT 4 | hits you |
  | PATCH 6 | heals the boss 6 |
  | DOSE | corrupts your slice |

  Its screens use the Solace corp skin.
- **It only acts when the needle lands on the host slice.** Then the sub-slice in line with the tick fires, as well as the player's own slice. Example: you resolve EXPLOIT 6, and the parasite's PATCH 6 heals the boss 6.
- **Three needle layouts:**

  | Layout | Placement | How it plays with the needle |
  |---|---|---|
  | A, beyond the tip | outside the blade | They never overlap; all 3 sub-slices stay visible; a beam links the blade to the sub-slice in line. It costs height above the wheel. |
  | B, under the blade | in the blade band, with the needle passing over it | Compact, but the blade hides exactly the sub-slice in line, which is the one that triggers. |
  | C, at the slice root | an anti-inner band inside the host slice, joined to the needle by a dashed tick line | Reads most like an anti-inner-ring, but it is small and crowds the host slice and hub. |
- **Recommendation: A.** It is the only layout where the trigger is unambiguous and nothing hides the in-line sub-slice.
- **Rules (proposal):**
  - It rides its slice through spins and flips.
  - It lasts 3 turns, shown as pips, then drops off. It can be cleansed.
  - **Open question:** what happens when the slice it sits on is the one the player is aiming at?

## Weakest parts
- **At r = 60** the parasite slices read only as colour and glyph. The values belong on the forecast tag.
- **Layout A needs about 100 master units of headroom** above the player's wheel. It can clash with the forecast tag when the parasite is on the top slice.
