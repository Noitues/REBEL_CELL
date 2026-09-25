# REBEL_CELL — Style Guide (Visual Baseline)

Approved mockups (private canvas; ask the project owner for access):
https://claude.ai/artifact/EyiLTRaqVVwdhSQox1yufP — see the "Blended direction: three
worlds" row (HQ, City Grid, Netrun combat).

## 1. Three Worlds
| World | Style | Used for |
|---|---|---|
| Physical | **Diegetic Cyberdeck**: rain-streaked window, neon, worn metal deck, CRT readouts | HQ, recruitment, stationing, loadout |
| The net | **Wireframe Cyberspace**: glowing line geometry, perspective grid floor, wireframe skyline | City Grid, netrun map, combat arena, raids |
| The Cell's voice | **Punk Zine**: paper, tape, marker, spray paint, drips, halftone | Cards, HUD, notes, menus, story beats, codex |

**The rule:** the room is a cyberdeck, the net is wireframe, and anything the Cell touches
gets zined. Only combat combines two worlds (wireframe arena + zine UI).

Punk energy reference: neon graffiti chaos (spray, drips, scrawled notes, hot pink).
Use original motifs only. Do not copy existing characters, doodles or logos from any IP.
The Cell mascot is an original grinning hexagon "cell".

## 2. Colour Tokens
| Token | Hex | Use |
|---|---|---|
| `cell_pink` | #FF3DA8 | The Cell: player wheel, tags, primary actions |
| `cell_acid` | #D4FF00 | Secondary Cell highlight: previews, scribbles, emphasis |
| `paper` | #F2EEE4 | Zine paper |
| `paper_alt` | #E9E4D6 | Aged paper, posters |
| `ink` | #111111 | Zine ink |
| `net_cyan` | #5CE1FF | Neutral net geometry, grid, links |
| `net_bg` | #02030A → #0D1440 | Cyberspace background (radial) |
| `corp_solace` | #3DFF8B | Solace wheels, Sites, threats, holograms |
| `corp_meridian` | #FF8C1A | Meridian Freight Systems (M8) |
| `corp_halcyon` | #8C7BFF | Halcyon Civic (M9; moved off #4FFFB0, too close to Solace) |
| `corp_orbital` | #DDE3FF | Orbital Commons (M10; starlight, kept clear of resist_gold) |
| `corp_rebel_cell` | #FF2A6D | REBEL_CELL (M11) |
| `crt_amber` | #FFB000 | CRT readouts on the physical deck only |
| `resist_gold` | #FFD24D | Spin resistance, locks |
| `desk_dark` | #1B1D21 / #34383E | Deck metal |

Each corporation gets its own `corp_*` glow colour. Never use colour as the only signal.

## 3. Typography
| Role | Font | Notes |
|---|---|---|
| Handwriting, tags, notes | Permanent Marker | Cell voice only |
| Zine display, numbers | Anton | Card titles, HP, Heat |
| System text | Share Tech Mono | Net labels, logs, CRT, DISPATCH |

All three are on Google Fonts under open licences; confirm each licence before release.
DISPATCH is always Share Tech Mono on clean surfaces, never handwritten or zine-styled.

## 4. Component Rules
- **Wheels:** wireframe with glow; player wheel `cell_pink`, enemy wheels `corp_*`;
  a glyph on every slice (✦ Crit, ▲ Atk, ■ Def, ◈ Afflict, ✕ Miss, plus Shield, Evade,
  Heal, Deploy glyphs); dashed outline for the Miss slice; resistance shown in `resist_gold`.
- **Zine elements never cover the wheels.**
- **Cards:** stickers (black/pink/paper), slight rotation (±4°), tape strips, hovered card
  lifts and glows; cost in marker.
- **HUD:** Polaroid portrait, ransom-note Heat, marker tally RAM, torn-paper log strip,
  circular "SEND IT" stamp for End Turn.
- **Ghost preview:** dashed `cell_acid` arc from current to predicted pointer position.
- **Grid:** isometric wireframe buildings; claimed Sites `cell_pink` with spray circles;
  corporate Sites `corp_*`; threat paths glowing `corp_*` arrows; zine sidebar "THE PLAN".
- **HQ:** graffiti tag with drips, wanted poster (Heat), Polaroid roster, pirate radio,
  deck CRT, "JACK IN" button.

## 5. Motion & Feedback
- Jack in: camera pushes into the deck CRT and dissolves to wireframe; jack out reverses.
- Precision: Perfect = latch + wheel-local inversion + 2-frame freeze; Good = clean click;
  Partial = stutter; Miss slice = static burst.
- Heat: effects pulse on threshold events; they do not stay on. Physical world adds wanted
  posters and searchlights; the net shows corporate wireframe creeping over zine elements.
- REBEL_CELL campaign: the net itself renders in zine style.

## 6. Accessibility
Reduce-effects toggle, flash limiter (≤ 3 flashes/s, on by default), glyphs for every
slice and status, text scaling, subtitles with speaker names.

## 7. Placeholder Art Policy (M0–M3)
- Use simple shapes in the correct colour tokens and fonts; label placeholders in
  brackets, e.g. `[BREAKER PORTRAIT]`.
- Portraits: grey rectangles at final aspect ratio (Polaroid 1:1 image area).
- Keep art behind a thin view layer so final art swaps in without code changes.
- Portrait pipeline (final): painted in full colour with strong value contrast, shown
  through a shader matching the screen's world; glitch variants at low HP and death.
