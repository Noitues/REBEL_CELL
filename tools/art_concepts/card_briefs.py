"""Card illustration briefs (W4, ART_BIBLE 7.3; designer ruling Q1).

Writes docs/art_briefs/cards/: one brief per effect family (the ~30 shared base
illustrations, tinted per card type), one brief per rare or class card that gets unique
art, and an index README. The card list comes from tools/art_concepts/cards.psv
(regenerate it with `godot --headless --path . -s tools/art_concepts/dump_cards.gd`).

    python tools/art_concepts/card_briefs.py

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art_briefs" / "cards"
CARDS = ROOT / "tools" / "art_concepts" / "cards.psv"

STOCK = {"WHEEL CARD": ("paper", "`PAPER_ALT` #E9E4D6"), "SYSTEM CARD": ("black", "`INK` #111111"),
         "HACK CARD": ("pink", "`STICKER_PINK` #F5AFCB")}

PRINT_SPEC = """- **Master:** 768 x 512 px (3:2), flat RGB, no transparency. Keep the subject inside the
  centre 540 x 460 px: the hand card shows a centre crop about 1.17:1 (the full 3:2 shows
  only in the detail view), and the top-right 60 px corner carries the rarity tab.
- **Two inks** (riso passes), each its own halftone screen:
  - key pass: `INK` #111111 (printed `PAPER` #F2EEE4 on black-stock cards), screen 45°;
  - spot pass: `CELL_PINK` #FF3DA8, screen 15°, multiplied over the stock.
- **Halftone:** round dots, cell about 10 px at the master (about 1/50 of the height);
  solids above 92% tone. No gradients left unscreened.
- **Misregistration:** the spot pass sits 4-7 px off the key pass, diagonally, the same
  direction across the whole print. Never more than 8 px (it must still read at 100 px).
- **Stock:** photocopy grain, a few toner specks, one faint copier streak, a slightly burnt
  edge. The stock colour is the card type's (see "Inks by type")."""

INKS_BY_TYPE = """| Card type | Stock (window) | Key ink | Spot ink |
|---|---|---|---|
| WHEEL (paper) | `PAPER_ALT` #E9E4D6 | `INK` | `CELL_PINK` |
| SYSTEM (black) | `INK` #111111 | `PAPER` (light ink) | `CELL_PINK` |
| HACK (pink) | `STICKER_PINK` #F5AFCB | `INK` | `CELL_PINK` |"""

COMMON_DO = ["one subject, read in half a second at 100 px wide", "hand-cut, stamped, photocopied feel (ART_BIBLE 1, 2)",
             "silhouette first: it must read in greyscale (ART_BIBLE 12)"]
COMMON_DONT = ["no text, numbers or UI glyphs in the art (the band and rules carry them)", "no third ink, no gradients, no glow",
               "no chrome-and-hologram cyberpunk, no characters or logos from any IP (ART_BIBLE 1)"]

# family -> (title, subject, composition, do, dont)
FAMILIES = {
    "spin": ("Spin", "A spinner wheel mid-turn, a hand-drawn clockwise arrow sweeping round it.",
             "Wheel left of centre (about 40% of the height across), arrow arcing over its top to the right; speed lines trail left. One slice flooded pink.",
             ["motion reads clockwise"], ["no numbers on the slices"]),
    "spin_heavy": ("Heavy spin", "The same wheel thrown hard: a double arrow, heavy speed lines.",
                   "Wheel centred and larger; a key arrow and a pink arrow wrap it in two rings; streaks both sides.",
                   ["more force than Spin: thicker arrows, more lines"], ["don't blur the wheel (riso has no blur)"]),
    "backspin": ("Backspin", "The wheel pulled counter-clockwise.", "Mirror of Spin: wheel right of centre, arrow sweeping left over its top.",
                 ["the arrow unmistakably counter-clockwise"], ["don't reuse the Spin plate flipped (the pointer stays on top)"]),
    "gear": ("Gear mesh", "Two gears biting into each other, one driving the other.", "Large gear low-left, small gear high-right, teeth interlocked at the centre; a curved arrow on the big one.",
             ["the mesh point is the focal point"], ["no more than two gears"]),
    "nudge": ("Nudge", "A close-up of a wheel's rim under its pointer, two small chevrons either side.",
              "Wheel cropped by the bottom edge, pointer at top centre, chevrons left and right of it (the pink pair offset outward).",
              ["tiny, precise movement"], ["no big rotation arrows (that is Spin)"]),
    "jam": ("Jam", "A crowbar wedged into an enemy wheel's spokes, sparks at the bite.", "Wheel right, bar entering from the bottom-left corner, pink spark burst where metal meets metal.",
            ["violence to machinery, not to people"], ["no hands or arms"]),
    "inner_ring": ("Inner ring", "Two concentric rings, the inner one turning on its own.", "Rings centred; the inner disc flooded pink, a short arrow riding the gap between rings.",
                   ["the inner ring clearly the moving part"], ["no slices on the outer ring"]),
    "snap": ("Snap", "A crosshair snapping onto the centre of a slice.", "Wheel centred, crosshair and a pink target ring on the top slice.",
             ["precision, click"], ["no motion lines"]),
    "flip": ("Flip", "A wheel split down the middle, its halves swapping sides.", "A vertical fold line at centre; left half flooded pink, right half hatched; two arrows crossing over and under.",
             ["mirror symmetry"], ["no rotation arrows"]),
    "respin": ("Respin", "Two dice mid-throw with a loose arrow over them.", "Dice low-left and centre-right at different angles, pips in key ink, faces tinted pink.",
               ["chance, a gamble"], ["no casino imagery beyond dice"]),
    "freeze": ("Freeze", "A frost crystal over a stalled wheel.", "Six-armed snowflake centred, a pink cold halo behind it.",
               ["cold, still"], ["no blue (two inks only)"]),
    "strip": ("Strip", "Armour plates peeling off in layers.", "A stack of offset plates falling to the lower right, the top one in key outline, the rest pink tints; an arrow flicking away.",
              ["layers coming off"], ["no shield shapes (that is Shield)"]),
    "breach": ("Breach", "A hexagonal hub core cracked open, fractures running out.", "Hex centred with a pink core; five crack lines radiating to the frame.",
               ["the hub is the target"], ["no explosion fire"]),
    "damage": ("Damage", "A bolt striking a target ring.", "Target right of centre, zigzag bolt from the top-left corner, pink impact burst behind the target.",
               ["one clean hit"], ["no blood, no bodies"]),
    "arc": ("Arc", "Lightning chaining between three nodes.", "Three nodes in a triangle, bolts linking them left to right, each node haloed pink.",
            ["the chain reads as hitting every enemy"], ["no single big bolt (that is Damage)"]),
    "overload": ("Overload", "A battery bursting its casing, feedback arcing back to its owner.", "Upright cell centred, flooded pink, a crack bolt inside, a curved arrow looping back underneath.",
                 ["power with a cost"], ["no flames"]),
    "block": ("Block", "A firewall of bricks.", "Four staggered rows of bricks filling the centre; each brick outlined, pink tones varying brick to brick.",
              ["solid, stacked"], ["no fire (the name is the pun)"]),
    "shield": ("Shield", "A hexagonal energy plate.", "Hex centred, pink fill, three struts across it; an incoming arrow glancing off the left.",
               ["protective, lasting"], ["no medieval shields"]),
    "evade": ("Evade", "A figure sidestepping, leaving two afterimages.", "Three silhouettes left to right, the two ghosts in pink tints, the last solid in key.",
              ["speed, a dodge"], ["no faces; silhouettes stay generic"]),
    "heal": ("Heal", "A patch with a plus sign, small pluses rising off it.", "Bandage strip turned slightly, cross centred on it, three pink pluses floating up-right.",
             ["care, relief"], ["no hearts (the HP glyph owns the heart)"]),
    "cleanse": ("Cleanse", "A spray bottle wiping a slice clean.", "Bottle top-right spraying droplets to the left over a pink clean stripe.",
                ["a fresh, cleared strip"], ["no bubbles or sparkles"]),
    "corrupt": ("Corrupt", "Glitch bars tearing through a skull-shaped mask of code.", "Horizontal torn bars across the frame (mostly pink, some key), a small blocky skull at centre.",
                ["the scan-glitch language of the net"], ["don't use the REBEL_CELL corp's glitch-bar pattern exactly (ART_BIBLE 3.6)"]),
    "overclock": ("Overclock", "A microchip giving off heat waves.", "Chip low-centre, three wavy heat lines rising in pink.",
                  ["hot, over the limit"], ["no flames, no thermometer"]),
    "encrypt": ("Encrypt", "A padlock over a field of data blocks.", "Lock centred, pink body; scattered pink squares behind it like packets.",
                ["closed, safe"], ["no keys (it's a lock you can't open)"]),
    "parasite": ("Parasite", "A worm latched onto a slice, feeding.", "A sinuous worm across the centre, its head at the right; a pink slice arc under it.",
                 ["creepy but graphic"], ["no gore"]),
    "ram": ("RAM", "A memory stick being filled.", "Long module across the centre, pink chips on it, a down arrow feeding it from the top.",
            ["full, charged"], ["no numbers on the chips"]),
    "drain": ("Drain", "A memory stick leaking a drop.", "Module high-centre with chips fading out left to right, a pink drop falling below.",
              ["loss, a leak"], ["no skulls (that is Corrupt)"]),
    "draw": ("Draw", "Three cards fanning up from the pile.", "Three tilted cards centre, each tinted a step more pink, an up arrow to the right.",
             ["the game's own card shape"], ["no playing-card suits"]),
    "drone": ("Drone", "A quad drone seen from above.", "Body centred, four arms, rotors as pink discs with key rims.",
              ["the Botnet's small helpers"], ["no weapons on the drone"]),
    "calibrate": ("Calibrate", "A ruler's tick marks under a marker and a small wrench.", "Ruler along the lower third, pink marker triangle above it, wrench top-right.",
                  ["fine adjustment, free nudges"], ["no measuring numbers"]),
    "ring_lock": ("Ring lock", "A ring chained shut.", "Ring left of centre with a pink band, a short chain to a padlock on the right.",
                  ["the inner ring held still"], ["no more than three chain links"]),
    "steady": ("Steady hand", "A reticle over a spirit level.", "Crosshair centred with a pink dot at its heart, a level bar along the bottom with its bubble dead centre.",
               ["calm precision, a Perfect"], ["no hands"]),
    "undock": ("Undock", "A satellite leaving its orbit.", "Planet-like hub lower-left, pink orbit ring, a small satellite breaking off to the upper right with an arrow.",
               ["movement between slices"], ["no space backdrop stars"]),
    "amplify": ("Amplify", "Echoing chevrons, the last one solid.", "Three play-style chevrons left to right, two pink echoes then the key one; sound-wave arcs ahead.",
                ["doubling, again"], ["no 'x2' text"]),
    "chip": ("Chip (fallback)", "A microchip (Firmware and Daemon stickers without card data).", "Chip centred, pins all round, pink die.",
             ["generic hardware"], ["no brand marks"]),
}

# unique card -> (subject, how it varies its family's base)
UNIQUE = {
    "blind_spot": ("Ghost class. A frost crystal half-hidden behind a sliding mask of static.", "Freeze base mirrored; a pink vertical scan band hides the left third (the Ghost's face-mesh cue)."),
    "ghost_step": ("Ghost class. A crowbar that passes through the wheel like a ghost.", "Jam base; the bar drawn in pink only where it crosses the rim, as if phasing through."),
    "hot_swap": ("Rigger class. A snap crosshair with a cable plugged into the hub.", "Snap base; a coiled cable (Rigger's harness) runs from the hub to the frame edge."),
    "leech_worm": ("Rare. A fat worm coiled round a slice, two smaller ones following.", "Parasite base with three worms of falling size; the slice arc fuller; foil card."),
    "overclock_nudges": ("Rare. Nudge chevrons echoing twice over a wheel rim.", "Amplify base over a cropped Nudge rim; the echo chevrons in pink; foil card."),
    "overdrive": ("Breaker class. A chip with a crowbar-antenna, heat pouring off it.", "Overclock base; one heat line becomes the Breaker's crowbar-antenna."),
    "parasite_pulse": ("Botnet class. A worm carried by a tiny drone.", "Parasite base; a small quad drone (the Botnet halo cue) holds the worm's tail."),
    "shatter": ("Breaker class. A hub core smashed by a riveted crowbar.", "Breach base; a riveted bar (Breaker's riveted plates) through the hex."),
    "short_circuit": ("Rare. A hub core with fractures and a fried wire looping out of it.", "Breach base; a pink looped wire sparks from one crack; foil card."),
    "spawn_drone": ("Botnet class. A drone lifting off a wheel slice.", "Drone base; a slice wedge below it, rotor rings doubled (the orbiting dot ring)."),
    "stim_patch": ("Rare. A stim injector over a bandage, pluses rising.", "Heal base; an injector crosses the patch diagonally; foil card."),
    "torque_wrench": ("Rigger class. A wrench turning the big gear.", "Gear base; a wrench bites the big gear's hub, a cable wrapped round its handle (Rigger)."),
}


def read_cards() -> list[dict]:
    out = []
    for line in CARDS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        cid, fam, unique, typ, rarity, cls, name = line.split("|")
        out.append({"id": cid, "family": fam, "unique": unique == "true", "type": typ, "rarity": rarity, "class": cls, "name": name})
    return out


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {i}" for i in items)


def family_brief(fam: str, cards: list[dict]) -> str:
    title, subject, comp, do, dont = FAMILIES[fam]
    users = [c for c in cards if c["family"] == fam]
    base = [c for c in users if not c["unique"]]
    uniq = [c for c in users if c["unique"]]
    types = sorted({c["type"] for c in base})
    rows = "\n".join(f"| `{c['id']}` | {c['name']} | {c['type'].split()[0]} ({STOCK[c['type']][0]}) | {c['rarity']} |" for c in base) or "| – | – | – | – |"
    uniq_line = ", ".join(f"[`{c['id']}`](unique/{c['id']}.md)" for c in uniq) or "none"
    concept = f"../../art_review/W4/concepts/{fam}.png"
    return f"""# {title} (family `{fam}`)

Base illustration, shared by every non-unique card of this family and **tinted per card
type** (ART_BIBLE 7.3, designer ruling Q1). Stand-in: `CardArt` family `{fam}`. Concept:
[`{fam}.png`]({concept}) (pixel-art concept only, Q6).

## Subject
{subject}

## Composition (3:2, 768 x 512 master)
{comp}

## Inks
Tints needed for this family: {", ".join(f"{t.split()[0]} ({STOCK[t][0]})" for t in types) or "none yet"}.

{INKS_BY_TYPE}

## Print spec
{PRINT_SPEC}

## Do
{bullets(do + COMMON_DO)}

## Don't
{bullets(dont + COMMON_DONT)}

## Cards using this base
| Card id | Name | Type | Rarity |
|---|---|---|---|
{rows}

Unique variations of this family: {uniq_line}.
"""


def unique_brief(c: dict) -> str:
    subject, variation = UNIQUE[c["id"]]
    title, _, comp, do, dont = FAMILIES[c["family"]]
    stock = STOCK[c["type"]]
    return f"""# {c['name']} (`{c['id']}`), unique art

{c['rarity']}{" · class " + c['class'] if c['class'] else ""} · {c['type']} on {stock[0]} stock. Family base:
[{title}](../{c['family']}.md). Stand-in: `CardArt` seeded from the card id (a mirrored or
shifted variation of the family plate plus pink accents).{" Printed on holographic foil stock in game (the foil is the card's, not the art's: don't paint a sheen)." if c['rarity'] in ("RARE", "BOSS") else ""}

## Subject
{subject}

## Composition (3:2, 768 x 512 master)
{variation} Base layout: {comp}

## Inks
Stock {stock[1]}; key `{"PAPER" if c['type'] == "SYSTEM CARD" else "INK"}`, spot `CELL_PINK`.{" Class accents stay off the art (ART_BIBLE 7.1: accents live on portraits, bezels and dossier stripes); the class reads through its prop cue only." if c['class'] else ""}

## Print spec
{PRINT_SPEC}

## Do
{bullets(do + COMMON_DO + ["keep the family's silhouette recognisable: this card must still read as its family"])}

## Don't
{bullets(dont + COMMON_DONT)}
"""


def main() -> int:
    cards = read_cards()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "unique").mkdir(exist_ok=True)
    for fam in FAMILIES:
        (OUT / f"{fam}.md").write_text(family_brief(fam, cards), encoding="utf-8", newline="\n")
    uniq = [c for c in cards if c["unique"]]
    for c in uniq:
        (OUT / "unique" / f"{c['id']}.md").write_text(unique_brief(c), encoding="utf-8", newline="\n")
    fam_rows = "\n".join(
        f"| [{FAMILIES[f][0]}]({f}.md) | `{f}` | {sum(1 for c in cards if c['family'] == f and not c['unique'])} | "
        f"{', '.join('`' + c['id'] + '`' for c in cards if c['family'] == f and c['unique']) or '–'} | [concept](../../art_review/W4/concepts/{f}.png) |"
        for f in FAMILIES)
    uniq_rows = "\n".join(f"| [`{c['id']}`](unique/{c['id']}.md) | {c['name']} | {c['rarity']} | {c['class'] or '–'} | {c['family']} |" for c in uniq)
    readme = f"""# Card illustration briefs (W4)

ART_BIBLE 7.3 and designer ruling Q1: about 30 **base illustrations**, one per effect
family, shared by the family's cards and tinted per card type; **unique art** for every
rare and class card. Every final is a two-colour risograph print (INK + CELL_PINK) at
768 x 512 (3:2). Until the finals land, `scripts/ui/kit/card_art.gd` (`CardArt`) draws a
procedural stand-in in the same style; a final drops in by setting the card's `art`
texture (`CardData.art`) with no code change.

- {len(FAMILIES)} family briefs (34 used by content, plus the `chip` fallback for Firmware and Daemon stickers).
- {len(uniq)} unique-art briefs (rares and class cards), listed below by id.
- Pixel-art concepts, one per family: [`docs/art_review/W4/concepts/`](../../art_review/W4/concepts/contact_sheet.png)
  (script-drawn, Q6; never shipped).

Regenerate: `godot --headless --path . -s tools/art_concepts/dump_cards.gd`, then
`python tools/art_concepts/card_briefs.py` and `python tools/art_concepts/card_concepts.py`.

## Inks by card type
{INKS_BY_TYPE}

## Families
| Brief | Family | Base cards | Unique variations | Concept |
|---|---|---|---|---|
{fam_rows}

## Unique art (rares and class cards)
| Brief | Name | Rarity | Class | Family |
|---|---|---|---|---|
{uniq_rows}

## Delivery
- 768 x 512 PNG, sRGB, named `<family>_<type>.png` for bases (`spin_paper.png`) and
  `<card_id>.png` for unique art, into `assets/art/cards/`; the importer sets each card's
  `art`. The window crops the centre about 1.17:1 on hand cards and shows the whole 3:2
  in the card detail.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    print(f"card_briefs: {len(FAMILIES)} family briefs, {len(uniq)} unique briefs, README in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
