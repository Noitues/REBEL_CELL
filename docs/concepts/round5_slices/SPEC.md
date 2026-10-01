# Round 5: spinner slices as programs (shared spec)

## The idea (from the designer)
- Every slice on a spinner is a **program that executes** when the pointer lands on it.
- Each slice is its **own full slice texture**: a wedge tile with its own material and pattern, with the **icon in the middle and the value**.
- The icon and number read like the reference: `docs/concepts/spinner_3d/09_enemy_pair.png` (paths relative to `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\`). That image was very clear: a **bold white glyph** plus a **big white number with a dark outline**, rotated with the slice, readable at a glance.
- Textures: circuit board like the MODEM sign (`docs/concepts/round4_modem_sign/sign_sheet.png`) and other ideas.
- Each program can have its **own shader behaviour** for flavour: glitch, shadowing, scanlines, pulse, and so on.
- **Enemies** use one **cohesive theme** per enemy or corporation, which can borrow from the player's themes.

## The programs (slice types → program names)
| Slice type | Program | Feel | Colour (keep) |
|---|---|---|---|
| ATTACK | **EXPLOIT** | Aggressive, sharp | pink #FF3DA8 |
| CRITICAL | **ZERO-DAY** | Rare, dangerous, flashy | hot pink / white |
| DEFEND | **FIREWALL** | Solid, layered, blocking | cyan #5CE1FF |
| SHIELD | **SANDBOX** | Contained, enclosed | cyan / teal |
| EVADE | **PROXY** | Slippery, rerouting | green #7BE07B |
| HEAL | **PATCH** | Restoring, repairing | green |
| AFFLICT | **VIRUS** | Infectious, spreading | violet #C85AFF |
| DEPLOY | **TROJAN** | Hidden payload, unpacking | lavender #B08CFF |
| MISS | **NULL** | Empty, dead | grey #6A6A6A |

(FILTER can stand in for a resistance or inertia slice if you want a tenth.)

## Geometry (identical for every agent, so the results compare)
- **Wheel:** 30 ticks; outer radius 360 px at master size, inner (hub) radius 130 px.
- **Slice tile:** a wedge spanning **3 ticks (36°)**. Also show one 2-tick (24°) and one 5-tick (60°) slice, to prove the texture and icon adapt.
- **Icon and value:** centred in the tile at about 60% of the radius span, rotated with the slice (as in the reference). The glyph sits above the number, or beside it if the wedge is wide.
  - The glyph is white with a dark outline and is about 34% of the tile's width.
  - The number is bold condensed white with a dark outline, the same size as the glyph or larger.
- **Readability rule:** the glyph and number must stay readable over the texture. Calm the texture under them with a darker plate, a vignette, or texture fading toward the centre.

## Deliverables for each agent, in `docs/concepts/round5_slices/<your_slug>/`
1. `programs_sheet.png` (1920×1080): all 9 programs as individual wedge tiles, laid out in a grid, each labelled with its program name. Also show a 2-tick and a 5-tick variant of one program.
2. `wheel_player.png` (1920×1080): a full assembled player wheel mixing about 8 of your program tiles. Add the pointer at the top, a hub, a bezel, and the HP arc below, in the spirit of the reference.
3. `wheel_enemy.png` (1920×1080): one or more full enemy wheels with a **cohesive theme**. One material family per enemy, all slices sharing it, with type still shown by glyph and colour accent. Follow any enemy instruction in your brief.
4. `shader_fx.gif` (≤ 4 MB) plus `shader_fx_strip.png`: each program's shader behaviour looping (glitch, pulse, scan…). Show 4–6 programs at least.
5. `small_and_grey.png`: your player wheel at radius 60 px, and the same at hero size in greyscale. Both must stay readable.
6. `NOTES.md`: for each program, its texture and its shader behaviour. Also how to build it in Godot 4.7: per-slice `ShaderMaterial` on a wedge mesh or polygon, the texture atlas, uniforms. And your favourite.
7. `scripts/`.

## Tools
- **Blender 5.2 headless** for bevelled, lit, emissive tiles like the reference, Pillow for 2D work, or both:
  - run `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python x.py`;
  - redirect output to a log file;
  - wrap it in `timeout 900`;
  - don't use the Blender MCP.
- **Blender 5.2 tips:**
  - The compositor is `scene.compositing_node_group` with a `NodeGroupOutput`, and the glare Type is a socket.
  - Set `view_transform` to `'Standard'`.
  - Use absolute paths.
  - Under EEVEE, cap light shadows.
- **Python:** write `.py` files and run them. **Never `python -`.** Use seeded randomness, and keep your own scratch subfolder.
- **Limits:** keep your folder under about 25 MB. Make only original designs.

## Report (under 150 words)
- your folder;
- the strongest and weakest programs;
- whether the icon and number still read at r = 60;
- your favourite program look.
