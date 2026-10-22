# Solace HQ as a modern-art sculpture (v2 exploration, 2026-10-21) and two variants
Files: `solace_modernart.png` (v1), `solace_modernart_sbs.jpg` (golden plate | art nouveau | modern art), `solace_warm.png` (A),
`solace_solarpunk.png` (B), `solace_variants.jpg` (v1 | warm | solarpunk). All 1920x1080, golden-plate overview camera, Cycles GPU.
Nothing outside this folder was edited: `scripts/modernart_run_hq.py` patches the base `hq_solace` pipeline at run time
(`modernart_blender_hq.py` hook; `deco_restyle.py` helpers imported read-only). The base landmark geometry is emptied at run time and replaced.

## What it is
Two broad ribbon backbones (56 BU wide, 2.6 thick, shallow bow, full 360 deg turn, same radius and pitch as the canonical helix) with one
base-pair slab per floor spanning them; route floors are thicker slabs with a room block; a ball (v1/warm) or sun-orb (solarpunk) on top;
a plinth in the plaza. Reflection-only softboxes (invisible to camera and fog) and two spots give the surfaces highlights.
- **v1 modern art**: lime / pink lacquer ribbons with edge light, Mondrian red / yellow / blue / white / black split slabs, mirror ball,
  white gallery plinth, cool teal-black city.
- **A warm**: ribbon A burnished copper (metal), ribbon B honey lacquer, slabs ochre / rust / cream / olive / umber (route floors honey | terracotta),
  lime / pink only as 0.9 BU edge lights, copper ball, cream plinth, warm-neutral dark city (neutral-grey mullions, warm windows, grey-brown mist).
- **B solarpunk**: ribbon A laminated-timber tone, ribbon B copper; hedges on both edges, hanging gardens (vines with leaf lumps) from the lower edge,
  vertical garden columns on the faces; slabs are cream terraces with lawns, plants and amber glowing greenhouses (bronze frames), thin aqua water
  cascades down between levels; glowing sun-orb crowned with planting; plinth = stone with lawn and a planted rim; same warm-neutral city.

## Timings / values (RX 6700 XT, HIP, OIDN; contended queue, so times vary a lot)
| Image | spp | build + render | median |
|---|---|---|---|
| v1 modern art | 40 | 645 s | 0.161 |
| A warm | 40 | 1057 s | 0.169 |
| B solarpunk | 28 | 292 s (an earlier 40 spp run was stopped by me at 26 min, with the GPU shared; foliage halved, 28 spp, then 292 s alone) | 0.161 |
CPU look-dev previews 960x540, 8 spp, 1.5-4 min each (11 runs). The shared GPU lock helper let other agents take the lock ahead of an older waiter several
times; waits were 52 min and 85 min.

## Critique (squint test, every preview and each final)
- m1: ribbons rendered as a zero-area curve (azimuth was a function of z only); fixed by giving each ribbon row its own azimuth. m2: ribbons grey: base
  geometry still drawn, then the ribbon bug above. m4/m5: reads at once as a DNA ribbon sculpture; ribbons too flat (emission high), slabs hidden
  behind 92 BU-wide ribbons, so ribbons narrowed to 56-62, emission lowered, slabs enlarged. m6: plinth now a tall white block; passes.
- **v1 final**: passes the squint test: lime and pink ribbons, colour-blocked slabs, white plinth, dark teal city, sculpture brightest by far.
  Weak: the ribbon's far-side/inner face shows as grey translucent bands (reads as glass segments, not a clean ribbon); gloss is mostly flat colour
  because the world is dark; the plinth is a plain white block with no reflection; the city windows are still busy speckle behind the thin top of the helix.
- **A warm final**: reads as a copper/honey ribbon sculpture with earthy slabs; warm and gentle, no toy primaries. Weak: value separation is lower
  (sculpture and city are both amber/brown, so the helix pops less than v1; the city is still a brown speckle field, nearer to the deco "mud" than I want);
  copper ribbon looks the same orange as the honey one at distance; the grey bands again.
- **B solarpunk final**: the most "Solace": green-edged helix, glowing amber greenhouses on every few floors, lawn plinth and sun-orb, still a clear
  silhouette. Weak: the greenery reads as green lumps (low-poly foliage), not as hanging gardens; water cascades are almost invisible at this distance;
  the timber ribbon reads as flat orange; the lawn on the plinth is a flat green slab; same busy brown city as A.
- Designer's doubt (is this the right style): the shape works in all three; the sculpture reads best in v1 (maximum value contrast); B carries the Solace
  brand idea best; A is the safest. A hybrid of B (greenery, greenhouses) on a dark cool-neutral city would likely give the strongest value hierarchy.

## Rebuild
```
S=docs/concepts/hq_styles/solace_modernart/scripts
bash $S/prev.sh <tag>            # v1 CPU preview;  bash $S/prev2.sh warm|solar <tag>  for the variants (D:/rc_scratch/hq_styles/solace_modernart/solace/<tag>/plate.png)
R="python $S/modernart_run_hq.py solace art"
DECO_SPP=40 python $S/modernart_gpu.py art_modernart <log> -- $R v1 ';;' $R warm 'd.variant="warm"' 'post={"shadow_tint":[0.50,0.48,0.47],"sat":0.9}' \
   ';;' $R solar 'd.variant="solar"' 'post={"shadow_tint":[0.50,0.48,0.46],"sat":0.95}'      # solar final used DECO_SPP=28
python $S/modernart_sbs.py ; python $S/modernart_variants.py     # after copying plates to the PNG names above
```

## References (pages read only, nothing downloaded)
- Jencks DNA sculptures (Clare College Cambridge, Newcastle DNA Spiral): https://www.cam.ac.uk/node/22183 , https://co-curate.ncl.ac.uk/dna-spiral-times-square-newcastle
  - the double helix as pure public sculpture: continuous strands, rungs as separate bars, readable from far away.
- Kapoor, Cloud Gate: https://rapidwelding.com/blog/articles/the-bean - polished plates, mirror finish (mirror ball, softbox highlights, smooth ribbon shading).
- Koons, Balloon Dog: https://www.dimensions.com/element/balloon-dog - mirror-polished steel under a transparent colour coat (saturated clear-coated lacquer).
- Serra, The Matter of Time: https://en.wikipedia.org/wiki/The_Matter_of_Time - huge sweeping curved walls (broad ribbons, not tubes).
- Calder / Mondrian: https://buffaloakg.org/artworks/k196124-cone , https://christies.com.cn/lot/lot-5621981 - fat primaries plus black and white, a stabile rooted on a plinth.
- CapitaSpring and Bosco Verticale: https://www.studiomatrx.org/guides/capitaspring , https://domusweb.it/en/city/milano/2018/07/24/vertical-forest.html
  - planting as the facade, sun-loving plants on the perimeter, sky terraces (hedges on the ribbon edges, lawns and planted terraces on the slabs).
- Gardens by the Bay Supertrees and Jewel Changi Rain Vortex: https://VisitSingapore.com/travel-guide-tips/about-singapore/city-in-nature/sustainable-architecture/
  and https://www.businesstraveller.com/city-guides/four-hours-in-singapore-2023/
  - vertical gardens on a tall sculptural frame; a 40 m waterfall through terraced planting (water cascades between levels). Kampung Admiralty: search
    returned nothing usable, so no trait was taken from it.

# Solarpunk v2 (concrete ribbons + neon trim, cool city) - `solace_solarpunk_v2.png`, `solace_solarpunk_v1_v2.jpg`
Designer brief: B solarpunk with muted grey-green architectural concrete ribbons, lime only as thin neon trim, a little pink, cool-neutral dark city,
draped foliage and potted trees as fewer bigger masses, no water cascades, amber greenhouses and sun-orb kept, inner faces opaque.
Built by `variant solar2` in `scripts/modernart_restyle.py` (`apply_solar2`).

## What changed from v1
- Ribbons: one procedural precast-concrete material (celadon grey noise mix, faint board-form lines every 4 BU, roughness 0.85, low emission), the
  same on both faces of both strands; lime neon trim 0.55 BU wide on each ribbon edge, on the slab edges and the plinth edge; pink only on the
  crown halo ring and every sixth greenhouse (amber elsewhere); no water.
- Foliage: draped curtain meshes (5 x ~108 columns, ragged bottoms, bulging out) hang from the lower edge of each ribbon and shorter ones from the top lip;
  about 24 big hedge masses on the top lips; potted trees (planter, trunk, one big 8-sided canopy) at slab ends and on the plinth; about 3.3k foliage faces in all.
- City: v1's dark teal-black fill and cool blue mist again; warm key spot (amber, 170k W) and cool fill on the sculpture only.
- Root cause of the "grey translucent bands" (they were in v1, warm and solarpunk v1 as well): 32 frosted window-glass meshes (`frost_*`, `frostf_*`)
  from the base pipeline's mover objects, still drawn at the route floors, plus `strand` and `imap`. v2 hides and empties them. The ribbon inner face was fine.

## Timings
CPU previews 960x540 8 spp, 13 runs. Final: 1920x1080, 36 spp, 2215 s wall (37 min; the scene took 292 s alone earlier, so the GPU was shared), median 0.161,
lock held 21:41 to 22:19 (38 min), wait 58 min. Watchdog (15 min no CPU progress on the blender child, 45 min cap) never fired.

## Critique (squint test)
- Previews: v2a ribbons black and white zebra (the frost glass), concrete too dark; v2b/c ribbons blown out by the key lights, fixed with more emission and
  less key; v2k bands gone; v2l concrete reads grey-green, neon trim thin; v2m draped curtains visible. Final matches v2m.
- Squint: at thumbnail size it reads as a twisted double-ribbon tower with glowing floors on a lime-edged plinth in a dark cool city. Value separation is
  now by both value and temperature (warm amber and pale concrete against teal-black). Better than v1 on every point of the brief.
- Weak: (1) the ribbons are pale cream-grey, not the muted sage the brief asked for (the lit concrete is near white, so the "green concrete" only shows in the shadow
  side and under the foliage); a lower key and a darker base would fix it. (2) The curtains and hedges glow as large saturated lime-green masses, so the green reads
  louder than the neon trim, and their silhouettes are still blobby; they look like moss on the ribbons rather than hanging gardens. (3) Potted trees are small grey-green
  blobs at this distance. (4) The plinth lawn and the lime outline are strong and flat. (5) The sun-orb is a plain bright disc.
