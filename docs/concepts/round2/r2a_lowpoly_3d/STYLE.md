# R2A: low-poly 3D ("carved toy city")

**Reference translation.** The reference is a chunky, flat-shaded low-poly figure: large triangle
planes, one soft key light so every facet takes a single tone, muted warm colours, a soft ground
shadow and a vignette. I kept all of that and swapped the subject. The city is a **diorama slab on a
cream floor**, with faceted rock sides and a soft shadow underneath. Buildings are ring-stacked prisms.
Their vertices are jittered with a seeded random, then triangulated, so each wall breaks into two-tone
facets. Window bands, spinner wedges, card faces and UI plates are all built the same way: a raised
centre vertex makes each flat face break into 4–8 facets that catch the light differently. Neon is
**emissive facets**, not glows painted on top: lit windows, sign blades, path ribbons and node inserts.
A light bloom lets them read through the matte world.

**Palette.**
- Day: cream ground `#d6c3ad`, sand/rose/lavender/slate bodies (`#d0b397 #bc8d84 #9d93aa #7d8797`),
  teal water `#6f9aa0`.
- Night: plum ambient `#2a2140`, a blue moon key, neon cyan `#40f0ff`, magenta `#ff3fa4` and amber
  `#ffb040`.
- Suspicion: crimson ambient `#3a1626`, red-shifted windows and signs, pale searchlight cones.
- Node code: amber = you, cyan = target, lime = site, rose = boss.
- UI accents are the same neons on dark plum plates `#2b2436`.

**Technique.** Blender 5.2 EEVEE, all geometry is scripted (`lp_lib.PB`: verts + faces +
per-face material + per-vertex jitter). Text is extruded curves with low curve resolution, so the letters
are faceted too. The UI is real 3D in camera space. In combat a light-linked sun lights only the UI, so
the city keeps its night lighting. Depth of field and a haze plane push the city back. Pillow adds the
post-pass: −10% saturation, a warm cast, a slight softening, a tinted vignette and seeded grain.
Everything is seeded. Rebuild with `python scripts/build_all.py`.

**In Godot (2D/2.5D).** Pre-render the city diorama per lighting state (day/night/alert) as layered
sprites. Or use real low-poly meshes in a `SubViewport` with `SHADING_MODE_UNSHADED` off, flat normals,
one `DirectionalLight3D` and no specular. The nodes and paths go in a separate overlay pass, so they can
animate. Spinners work well as actual 3D meshes (a wedge = fan + apex vertex, rotated in code) in a small
viewport. Cards and plates can be pre-baked 9-slice textures with the facet shading painted in, plus
emissive accent layers for the neon.
