# Round 38: operative portraits

Built on the locked dialogue option A: every portrait is a low-poly cel bust (Cv2 triangulated facets, E toon bands, inverted-hull ink) shown on the Cell's CRT comms feed. Class colours follow `round22_raid_world/class_colours_v2.png`.

## Files

| File | What it shows |
|---|---|
| `portraits_classes.png` | 8 classes × 3 procedural rookies (one large, two small), each on the feed. Shows callsigns, base / alternative class, role line and gear notes. |
| `portrait_states.png` | One rookie (RIGGER // SPROCKET) in every state: idle, talking, hurt, stationed, flatlined, recruit. |
| `portrait_contexts.png` | Crew roster terminal (CRT), Meridian corp dossier (paper photo print, paper clip, red pencil ring), campaign audit polaroids (KIA crossed out, auditor post-it), and the contacts: fixer, street merc, DISPATCH (voice only). |

## Class gear (silhouette first; colour = class)

| Class | Gear | Accent |
|---|---|---|
| Breaker | Hood + glowing visor bar, chest stripe | `#FF3DA8` pink |
| Wrecker (alt of Breaker) | Respirator with glowing filters, shoulder pads, optional glasses bar | `#FF6E32` orange |
| Ghost | Hood (or none), lower-face mask, glowing eye slits, optional mask stripe | `#5BE0FF` cyan |
| Phantom (alt of Ghost) | White half face-mask with a lilac seam: the "afterimage" | `#DBC1FF` lilac |
| Rigger | Headset + mic, goggles up on the forehead or down over the eyes | `#7AE07A` green |
| Overclocker (alt of Rigger) | Slot goggles, heat-sink fins on the temple, often a mohawk | `#FFB040` amber |
| Botnet | Antenna, monocle (alternate seeds), 2–3 hovering ico-drones with LEDs | `#6072FF` indigo |
| Hivemind (alt of Botnet) | Hex circlet with 6 nodes, glowing neural jack | `#C659FF` violet |

## Procedural rookies (`bust_rig.py`)

The seed picks:
- skin (5 tones);
- hair style (buzz, crop, mohawk, bald, long) and colour (natural or dyed);
- jaw taper and head width;
- a beard (30 %, always a natural colour);
- one gear swap per class (hood colour, goggles up or down, monocle, drone count, mask stripe, glasses).

Class gear and colour never change, so the class reads at chip size. In game, generate the seed from the run's roster RNG stream (deterministic) and store it on the operative state. Bake one portrait set per seed (offline Blender or an in-engine 3D viewport, see below).

## States

| State | Feed treatment | LED |
|---|---|---|
| Idle | Live: scanlines, slight RGB split, a rolling bar, a slow blink (eyes-shut render every 4–6 s) | green |
| Talking | Mouth-open render alternating with closed at speech rate, plus voice-level bars | green |
| Hurt (HP ≤ 25 %, art_asset B1) | Grimace + squint render, red wash, torn scan bands, wider RGB split, cracked glass, an HP chip | red |
| Stationed | Class-colour monochrome at 12 fps, an "ON <SITE>" bar | class colour |
| Flatlined (permanent) | Static noise over greyscale, a NO SIGNAL bar, a red grease-pencil X, a FLATLINED stamp | off |
| Recruit (unhired) | Greyscale and a "HIRE: 15 SCHEMATICS" stamp (GDD 5.4) | amber |

Triumphant (art_asset B1) is deferred to the dedicated portrait pass. The proposal: the talking render, a gold rim and a bloom pulse.

## Contexts

- **Crew roster (HQ):** CRT rows with a small feed per operative. A stationed operative keeps the tinted feed and shows its site in the class colour. A flatlined operative keeps its row: static, the name struck in red, FLATLINED. This makes permadeath visible.
- **Corp dossier:** the bust as a flat, desaturated photo print, paper-clipped to the corp file and ringed in red pencil. This is the corp's view of the operative, used for Heat/WANTED and the HQ mugshot.
- **Campaign audit:** polaroids with a handwritten callsign and rank. A KIA polaroid is greyscale and crossed out in red. An auditor post-it sits on the page.
- **Contacts:** the fixer and the street merc use the same feed with their own accent (cyan, amber). **DISPATCH never gets a face.** Its feed is a red voice trace on black in REBEL_CELL red, with a red bezel and the line "VOICE ONLY // NO FEED". Its waveform is driven by the voice line's amplitude.

## Godot build notes

- **Portrait renders.** Each operative is a small set of renders (idle, blink, talk, hurt, dead-eyes), at 600×666 with a transparent background.
  - These can be pre-rendered from `bust_rig.py` for a pool of seeds (8 classes × N seeds).
  - Alternatively, ship the parts as low-poly meshes and assemble them in a SubViewport with a toon shader. This removes the seed limit and costs one 3D viewport per visible feed.
- **The feed** is one `ColorRect` with a CanvasItem shader on top of the portrait `TextureRect`. Its uniforms:
  - `mode`: idle / talk / hurt / stationed / dead / recruit;
  - `tint`: the class colour;
  - `split`, `tear`, `noise` and `fps_hold` (the last for stationed).
- **Overlays** are separate nodes: the LED, the label strip, the HP chip, the X and the stamps.
- **Paper contexts** reuse the render through a "print" shader: desaturate, warm the colour, add grain, then apply a flat backdrop.

## Scripts (`scripts/`)

| Script | What it does |
|---|---|
| `render_busts.py` | Writes the job list and runs `bust_rig.py` once in headless Blender. It renders 30 busts in about 20 s. |
| `bust_rig.py` | The parametric bust: class gear, seed variants, mouth and eye states. |
| `portraits.py` (`classes\|states\|contexts`) | Builds the three sheets: the feed and DISPATCH feed, the roster, dossier, polaroid and audit. |
| Copied from round 31 | `bust_blender.py` (the original two busts), `r31lib.py`, `sticker_lib19.py`, `dialogue.py`, `lib17/`, `assets.py`. |
| `clear_scratch.py` | Clears the scratch folder (the renders are regenerated from scratch). |

All randomness is seeded.
