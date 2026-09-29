# Art pass: designer feedback, round 2 (2026-09-29)

**Verdict on round 1:** underwhelming. It polished some places and regressed in others, but it didn't give the game the facelift it needs to go from indie to AAA. The next step is a **concept round**:
- 5 agents each write one page of art direction and game concept;
- each renders a set of concept stills (Blender Grease Pencil), in a deliberately different style;
- then the designer and the orchestrator compare them and choose a visual direction.

Every item below is a constraint the concepts must show, and the backlog for implementation after the direction is picked.

1. **Concept round:** as above. The results live in `docs/concepts/`.
2. **Modem sign:** keep the **original** Modem sign (restore the pre-W8c neon look). Drop the paper BUY/SHRED stickers.
3. **Combat backdrop:** the city behind fights is too saturated and washes out the details that matter, the spinners. It needs to recede.
4. **Spinners:** find ways to make them feel 3D or layered. Proposals are to be discussed.
5. **Damage:** hits shoot off small pieces of binary code (0/1 shards) from the hit point.
6. **Marker font as live ink.** The pink marker is someone writing on the screen, with the ink dripping down:
   - words **write on** stroke by stroke;
   - drips slowly form, then pause while the game waits for the player;
   - on press, as the page transitions, the drips **continue down the screen**.
7. **City life:**
   1. The bare-grid / no-buildings view looks flat and bad, and it cuts off the big HQ building art. Add a **night** version.
   2. The fog layers are too uniform and too blurry. Use **patches** of fog with **varying** blur.
   3. Add a 3D orthographic **tilt-shift**: distance gets blurrier.
   4. Raid grid nodes are rooftops with lines from the street up to them, which looks bad. Put the **lines and nodes on the same plane**.
   5. Give the Grid's roads **elevation**, especially highways, with several levels of traffic, flying vehicles, and a busy real-city feel.
   6. Add **projected hologram billboards** and ad banners through the city. The text doesn't need to be legible.
   7. Step up the escalation with **Heat or HQ incursions**: helicopters, searchlights, drones.
   8. More life in the virtual city generally.
8. **Stickered cards:** whenever cards come up, animate them being **slapped on as stickers** over whatever is on the display, as if placing stickers on the screen.
9. **Marker over digital:** the marker "SEND IT" is written **over a washed-out digital "EXECUTE"**, as if scrawled over it. The theme carries through: marker verbs over system words.
10. **Light spill:** glowing elements cast **ambient light** onto the elements around them. Marker and stickers are excluded.
11. **Heat glitch:** screen-wide glitch shaders show the Heat level through minor flickers or distortions. It can be switched off in Options.
