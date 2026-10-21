# Solace HQ in Art Nouveau (single-HQ style exploration, 2026-10-21)
`solace_nouveau.png` (1920x1080, golden plate overview camera), `solace_nouveau_sbs.jpg` = golden plate | art deco | nouveau.
Nothing outside this folder was edited: `scripts/nouveau_run_hq.py` patches the base `hq_solace` pipeline at run time (hook in
`nouveau_blender_hq.py`), `deco_restyle.py` helpers are imported read-only.

## What the style changes
- Helix keeps its canonical silhouette, lime / pink identity and oval windows, re-ornamented: rippling verdigris floor ribs, two whiplash
  bronze vines per strand (lime on strand A, pink on B) with leaf pairs, tendril coils and glowing berries, a leaded stained-glass rosette
  (came bars, glowing petals, iridescent ring) in every route oval, curled finials, Guimard arch hoops and vine rails on each skybridge.
- Crown: dragonfly-wing lobes with glowing cells, a ribbed bud dome, a Mucha halo of leaded rings and branching tree-columns.
  Plaza: scalloped terraces and 18 Guimard stalk lamps. Neighbour towers get onion-dome caps with whiplash spires.
- City fill: black-teal lacquer, verdigris mullions, cool pale windows, blue-green mist (fog 0.30/0.55/0.72), cool glow lights, cool grade:
  no brown, so the lit helix wins.

## Timings / values (RX 6700 XT, HIP, OIDN)
Final: 1920x1080, 52 spp, 549 s build + render (586 s under the lock), median 0.161. CPU look-dev previews 960x540 / 1280x720, 8 spp, ~2-4 min.
GPU lock waited ~23 min (the shared gpu_lock helper deadlocked when four agents waited at once; my copy defers only to older waiting files).

## Rebuild
```
S=docs/concepts/hq_styles/solace_nouveau/scripts
bash $S/prev.sh <tag>                                    # CPU preview -> D:/rc_scratch/hq_styles/solace_nouveau/solace/<tag>/plate.png
DECO_SPP=52 python $S/nouveau_gpu.py art_nouveau <log> -- python $S/nouveau_run_hq.py solace art g1
python $S/nouveau_sbs.py                                 # after copying plate.png to solace_nouveau.png
```
Scratch: `D:/rc_scratch/hq_styles/solace_nouveau/`.

## References (pages read only, nothing downloaded) and the trait taken
- Guimard, Paris Metro entrances: https://en.wikipedia.org/wiki/Paris_Metro_entrances_by_Hector_Guimard and https://www.moma.org/collection/works/2393
  - dark-green "weathered brass" cast iron (verdigris is the dominant metal, not brown), lamp stems like tropical flowers/vines, a sinuous arch joining twin stems, standardised repeated parts (the 18 plaza lamps, arch hoops on bridges).
- Gaudí, Casa Batlló: https://architectuul.com/architecture/casa-batllo
  - bone-like pillars, dragon-back crest and a trencadís gradient from warm to blue-green: iridescent glass that shifts teal / violet / lime with height; ribbed bud dome.
- Gaudí, Sagrada Família: https://blog.sagradafamilia.org/en/?p=4765
  - double-twist, tree-like branching columns (crown canopy of forked ribs), cool blue-green and warm red-pink light split (lime strand vs pink strand).
- Horta, Hôtel Tassel: https://focusonbelgium.be/en/culture/hotel-tassel-first-art-nouveau-house
  - one unbroken whiplash line running through rail, floor and exposed green iron columns whose heads spread into tendrils (rippling ribs, vines, tendril-capped spires).
- Tiffany Dragonfly lamp / Favrile glass: https://brooklynmuseum.org/objects/1308
  - leaded glass cells with filigree wings and iridescent metallic-lustre glass (stained-glass rosettes, wing veins).
- Lalique Dragonfly-Woman: https://gulbenkian.pt/museu/en/works_museu/dragonfly-broach/
  - plique-a-jour translucent enamel in open metal cells for the glowing wing cells of the crown.
- Mucha: https://grandpalais-immersif.fr/en/actualite/de-lart-nouveau-au-style-mucha
  - the halo circle as a recurring leitmotif: concentric rings with beads behind the crown.

## Weakest points
Ornament is small at overview distance (vines and rosettes read as glowing green texture, the leaded windows barely resolve); tower caps read
as green bead clusters round the plaza; the crown dome is a bright pink-yellow blob with the halo rings faint; skybridges are still plain white bars from the base.
