# Tethys Deep, abyssal bioluminescent style (single-HQ exploration, 2026-10-21)

Same overview camera as `golden_plates/hq_tethys_overview` (t_over), same city, dam, water, caustics, drowned quarter, fish and whales. The pier city is
re-grown as sea life: the main HQ is a great chambered nautilus (nacre, tiger stripes, glowing septa and siphuncle, an anglerfish lure on an arched
stalk, a radiolarian lattice beside it, pale buttress ribs under it); the six inner pods are small nautili; the twelve outer and mid pods are jellyfish
bells (ribbed emissive skin, glass catch, scalloped lappets, trailing tentacles with bead tips, a few red lure tips); the piers are siphonophore chains
(lit spine, paired bells, hanging zooids); stilts, plinths and the breakwater carry coral, barnacle and kelp crust; the lot fence is anglerfish lures.
Cuttlefish-style colour-shift cells run as a frieze round the plinths. The drowned city is a little darker (WET_LIT 0.40) and the dam floods are
about half power so the HQ wins. Nothing in the base pipeline was edited: `abyssal_build.py` substitutes four hooks in `tethys_landmark.py` at run time.

Files: `tethys_abyssal.png` (1920 x 1080), `tethys_abyssal_sbs.jpg` (golden plate | abyssal), `scripts/`.

## Numbers
Cycles GPU (RX 6700 XT, HIP, OIDN), 1920 x 1080, 48 spp: render 148 s, 178 s wall with the build; frame median (luma) 0.160, 28 % under 0.10, 0.5 % over 0.85.
Look-dev: CPU previews 960 x 540 at 4 to 10 spp and a 1.5x crop at 16 spp (about 5 min each). GPU lock wait was 54 min (FIFO queue).

## Rebuild (Windows, Blender 5.2 headless; scratch D:/rc_scratch/hq_styles/tethys_abyssal)
```
S=docs/concepts/hq_styles/tethys_abyssal/scripts
# scratch needs scr/zoned_base.json, scr/meridian_rail.json, scr/mainframe_blade.png (copies of D:/rc_scratch/tethys/)
python $S/run_final.py f1 1.5 48 0.16        # GPU lock, render, then the base post (post_city.aaa) to f1/plate.png
BORDER=0.28,0.38,0.72,0.95 $S/run_prev.sh p3 1.5 16   # CPU crop preview; $S/run_prev.sh p4 0.75 10 for the full frame
python $S/abyssal_sbs.py tethys_abyssal.png tethys_abyssal_sbs.jpg
```

## References (pages read only; no files downloaded, no images copied)
- Haeckel, Kunstformen der Natur, plates index (https://mediamatic.net/nl/page/224288/kunstformen-der-natur-lieferung-2; https://en.wikipedia.org/wiki/Kunstformen_der_Natur):
  the plates' themes are symmetry and level of organisation. Taken: strict radial symmetry on every bell (ribs, scalloped lappets), the spined lattice sphere
  (radiolarian screen), siphonophore chains of repeated bells.
- Chambered nautilus (https://en.wikipedia.org/wiki/Chambered_nautilus, plus general shell-structure sources): a logarithmic spiral, chambers sealed by septa and
  pierced by a siphuncle, lustrous nacre lining, countershaded outer shell. Taken: the planispiral with a tube that grows about 3x per turn, striped matte outer rim,
  pastel iridescent flanks, a glowing septum line and a siphuncle dot per chamber.
- MBARI siphonophore lures (https://www.mbari.org/?p=86345): light is concentrated at the tips of thin stalks, bodies stay pale, and the lure colour is rarely red.
  Taken: tentacles dim at the root and bright at the bead tips, a few red tips, the anglerfish stalk with one bright bulb as the crown light.
- Deep-sea bioluminescence census (https://www.practicalfishkeeping.co.uk/fishkeeping-news/three-quarters-of-deep-sea-animals-make-their-own-light/): jellies and
  siphonophores are the most consistent glowers. Taken: cnidarian forms carry the light, the shell-forms stay mostly lit by the key.
- Oceanographic Museum of Monaco (https://en.wikipedia.org/wiki/Oceanographic_Museum_of_Monaco): a monumental building that seems to grow from the cliff, with a
  frieze band on the sea face. Taken: the heavy stepped reef plinth under the shell, with a frieze of colour-shift cells between pale cornice rings.
- Rougerie's SeaOrbiter (https://www.popsci.com/article/science/spaceship-sea/): slightly more than half of the mass is submerged, with pressurised decks below.
  Taken: the deep stair, lit portholes and coral-crusted columns reading below the waterline (kept from the base station).
- Neri Oxman, Mediated Matter (https://en.wikipedia.org/wiki/Neri_Oxman) and Calatrava's biomorphic ribs (https://parametric-architecture.com/santiago-calatrava-6-notable-projects-and-his-philosophy/):
  property gradients, structure that follows load, a skin that carries light. Taken: seven pale tapered buttress ribs from plinth to shell, and colour gradients
  (crown dim to margin bright) on the bell skins.

## Weakest points
- The nautilus top is still a pale, flat face from this camera; the lit aperture and tentacles face away or are hidden by the bells.
- Bells read as striped umbrellas at full size (rib stripes too regular); a translucent subsurface look is only faked with emission plus a glass catch.
- Coral, kelp and barnacle crust is small against the 1920 px frame; it reads mostly as a sparkle on the breakwater and stilts, not as a reef.
- The siphonophore chains are thin and partly hidden under the bells; the walkway links read weaker than the original glass tubes.
- The dam and dry city keep their warm sodium look (only dimmed); the abyssal style stops at the waterline.

## v2 nautilus biodome (scrapped by the designer, 2026-10-21)
Explored as CPU previews only (no final): one giant glass nautilus (frame mullions, lit septa, tiger-stripe outer rim, a jelly in every chamber, the main jelly amber in the body
chamber), jelly bells around it on siphonophore chains, the dam cooled and dimmed. It read as a spoked wheel more than a shell, so it was dropped; the code stays in `scripts/abyssal.py`
(`biodome`, `landmark_v2`, env `ABY_V2=1`) and feeds the dam cooling used by `../tethys_ideas`. No `tethys_biodome_v2.png` / `tethys_v1_v2.jpg` were made.
