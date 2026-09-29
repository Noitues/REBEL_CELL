# Meridian Freight Systems — machines bust brief

**Family:** enemy machines of Meridian Freight Systems (ART_BIBLE §7.2). **Members:** `cargo_hauler`, `courier_drone`, `customs_scanner`, `drone_dispatcher`, `port_authority`, `route_optimizer`.
**Deliverable:** one bust or hologram portrait per member, 1:1, **768 px master**, shown above its wheel (W3). A shared base per family with per-member props is fine; each member must still read apart at 96 px by one distinctive prop.
**Concepts:** `docs/art_review/W5/concepts/enemy_meridian_machine.png`. Stand-in: `PortraitArt.enemy_subject` / `Hologram` (BUST).

## Corp identity (§3.6)
- Hue: **#FF8C1A** (`Palette.CORP_MERIDIAN`), always paired with the pattern: **shipping-container stripes at 45°** (`CorpPattern`, `Palette.corp_pattern_id(&"meridian")`).
- Landmark glyph: container crane (may appear as a badge or lapel pin).
- Theme: logistics that treats people as cargo.

## Look
Machines and programs: a rounded box head with one big lens (the lens iris in the corp hue), one to three antennae, a narrow chassis neck. The chassis carries the corp pattern as panel print. No face, no mouth.

## Value and light
- Figure mass near black; the corp hue only on the rim, the eyes/lens, the tie and the pattern.
- The pattern must survive greyscale (colour-blind players read the corp by pattern first).
- The in-net version is a hologram: the same art through scan lines, translucent body, a projector cone. Paint the opaque bust; the `Hologram` view adds the projection.

## Distinct kinds
Machines, agents and bosses must never be confused: agents have a head and tie; machines have a lens and no face; bosses are larger with a crown and a patterned halo.

## Do / don't
- Do give each member one prop that reads at 96 px (a clipboard, a scanner arm, a parking boot, a dish).
- Don't use the corp hue for anything but identity (never a §3.3 UI role: no green "heal" read on Solace, no red "harm" read on REBEL_CELL without its glitch bars).
- Don't show real brands or logos.
