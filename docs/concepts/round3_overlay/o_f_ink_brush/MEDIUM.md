# o_f_ink_brush: sumi ink and watercolour

**The medium.** The overlay is brushwork painted onto the screen glass. It uses three layers, and each one has a single job:
- **Sumi black (dry-brush) on a hot-pink watercolour wash** carries the verbs: SEND IT, BUY, HIT THIS, OURS.
- **Pink ink lines** carry the annotations: ensō circles, routes, NOW, THEM!, LEAVE.
- **Torn washi with tape** holds notes, the portrait, the Heat poster and price tags.

Red carved **hanko seals** are the stamp vocabulary (VICTORY, FLAGGED, RAIDED, OK, SOLD, and the CELL signature). The faceted Cv2 world never has a brush edge, paper fibre or pigment granulation, so the overlay always reads as a different material.

**Palette.**
- Sumi: #0B090E (dense), #2C262E (dry).
- Pink wash: #D6106C to #FF70B2.
- Pink ink: #EC187A.
- Seal vermilion: #D42C22.
- Washi: #ECE5D4.
- Usumi grey: used only for shading on paper.
- Acid #F0F478: reserved as the rare second wash touch. It isn't used in these frames.

**Lettering.** I wrote a stroke-skeleton alphabet in which stroke order and direction are part of the data. Each stroke is painted by a bristle simulation:
- an angled pressed entry
- pressure and direction-dependent width (horizontal strokes are thinner)
- bristles that run dry in streaks
- flick tails that split and spray, and ink that pools at hard stops

Annotations are thin brush lines. Notes use a handwriting face, inked with soak and dry-edge texture.

**Why it reads as AAA.** Every mark is one confident stroke. There are about five marks per screen, with a strict colour role for each layer and real material response: edge-darkened washes, granulation, fibre edges, wet sheen and seal wear.

**Godot 2D build.**
- **Verb and label shapes:** each one is a baked stroke list (polyline, width and pressure per point). At runtime a `Line2D`/mesh is drawn per stroke and grows along its arc length.
- **Ink fragment shader:** a bristle-streak noise texture is mapped along the stroke UV (u = arc length). A dry-out threshold rises toward the tail. A pool mask darkens the stroke and adds a specular sheen while `wet > 0`.
- **Washes:** a `SubViewport` mask is run through a wash shader that does noise-displaced edges, edge darkening and a granulation texture.
- **Washi, tape and seals:** pre-baked textures, with seal wear done as an alpha texture.
- **Appear:** wash reveal over 0.07 s, then strokes in writing order with an ease-out per stroke. About 0.55 s in total.
- **Idle:** the halo (a blurred mask) creeps outward and the sheen fades over about 4 s, then holds.
- **Leave:** a slanted wipe mask with directional smear samples, drip particles and a bead line. About 0.35 s.

**Risks.**
- Black ink is unreadable straight onto the dark Cv2 base, so every sumi word needs a pink wash or paper behind it. Pink ink alone is the only mark that can sit directly on the base.
- The washes can turn into "amoeba" blobs if the noise displacement is too strong, so the wash shapes need art direction per word.
- The procedural portrait is only passable. A hand-painted portrait texture per operative would be needed.
- The bristle simulation should be baked to textures or meshes rather than simulated live.
- Its pink is close to the base's pink nodes and billboards on the city map.
