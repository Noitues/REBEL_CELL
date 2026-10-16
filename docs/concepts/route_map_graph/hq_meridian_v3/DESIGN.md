# Meridian HQ v3: THE GATEHOUSE GANTRY (design pass, 2026-10-16)

The designer's brief: *"build a shipping company with a giant crane that resembles a medieval castle, with trucks
picking up and dropping containers on 3 sides of the building and a high speed train bordering the 4th side. The crane
will move containers around from the train, wall, and trucks."*

Status: design, test 1 (overview) and **test 2 (overview + decision)**. No final renders. Nothing committed.
`hq_meridian/` (v2) is reference only. Concept A was chosen by the coordinator and the designer.

> **Round 2 supersedes sections 1–13 wherever they differ.** It changes the camera, the paint, the bastions, the rail,
> the keep, the ring road and the train. See **section 14** first.

## 1. Why v2 failed, in one line

v2 was a fort *with* a crane in it: two competing objects (a container ring and a slewing crane), a 360° ring route
round low walls, and no single shape. Halcyon is "a pyramid with an eye", Orbital "a ring with a rocket", Solace "a
twin helix". Meridian needs one shape that you can name at a glance.

## 2. The concept

**The crane is the castle.** Meridian's HQ is a goliath gantry crane built as a castle gatehouse: two crenellated
tower-legs joined by a battlemented bridge, with the keep riding on top. The whole thing reads as one shape, a giant
**Π gatehouse**, standing over a walled container yard.

- **Gatehouse = the gantry.** The legs are the gate towers. The span is the bridge over the gate. The spreader hanging
  under the span is the portcullis.
- **Curtain wall = the container store.** The walls are stacked containers that the crane works from.
- **Wall walk = the crane runway.** The legs ride rails on top of the E and W walls.
- **Keep = the crane's trolley.** The machinery house that rides the span is a crenellated keep with corner turrets.
  The server sits in its open crown.
- **Moat = the railway.** The high-speed line runs along the N side and passes under the E and W walls through two
  arched **rail gates**.

## 3. Massing (HQ kit units: 1 storey = 8 BU; north = +y; the lot is 240 × 240 BU and the HQ fills it)

| Element | Size / position | Notes |
|---|---|---|
| Curtain walls (W, S, E) | outer face on the lot edge, 14 thick, 4 courses (36 high) + 4.6 merlons | Containers laid **crosswise**, so their door ends form the outer face and read as "containers" at every zoom. The E and W walls run S→N and carry the runway. |
| S corner towers | 28 × 28, 56 high | Dark cast concrete with lit slits, a beacon and an orange lit cornice. |
| Gatehouses (W, S, E) | twin towers 14 × 24 / 52 high; arch 18 wide × 15 high | Half-raised portcullis, red gate lamps, machicolation corbels. The S gate chamber over the arch is a room slot. |
| Rail gates (NW, NE) | the runway wall continues over both tracks as an arched bridge (arch 18 high), with two drum turrets outside | The gantry can roll out over the train on them. |
| The rail (N edge) | two tracks at y 100 / 112 with catenary, running E-W through the whole city | A sleek high-speed freight set (pale livery with a cold blue light line, wedge noses) carries containers. Beside it is the quay. |
| The bailey (yard) | container stacks 1–4 high in blocks, with cross aisles | |
| Truck lanes | a lane inside each gate (S: E-W; W, E: N-S) with trucks parked at the bays; queues on the street outside each gate | |
| **Gantry legs** | 16 × 24, from the runway (36) to 108 + bartizans to 120; on bogies | Meridian-orange panelled steel, crenellated, with a beacon. Room slots are cut into the S face. |
| **Span** | 210 long, 14 deep, z 84–100, battlements on both edges, machicolations below | A lit **MERIDIAN** stencil and gallery room slots on the S face. Down floods under the span light the yard. |
| **Keep** (the trolley) | 28 × 24, z 101–134, 4 corner turrets to 142 | Tall narrow lit windows. The open crown on the roof holds **THE MASTER MANIFEST**, with a beam straight up. |
| Cab, hoist, spreader | the cab under the span, 4 ropes, the spreader + a container at z 45 | |

Height ladder: city near ring 16–44 BU, walls 36–41, towers 52–56, legs 108–120, keep 134–146. The gantry is the
tallest thing for three blocks in every direction, and the walls sit at street-block height, so the gate silhouette
rises out of a low ring.

## 4. How the castle reads

| Castle part | Built as |
|---|---|
| Gatehouse (two towers + the bridge over the gate) | The gantry: two legs and the span. This is the silhouette. |
| Portcullis | The spreader and container hanging under the span. Also a real half-raised portcullis in each truck gate. |
| Keep | The trolley house on the span: crenellated, corner turrets, the crown. |
| Curtain wall + battlements | Container walls with half-container merlons. |
| Wall walk | The runway (rails on the E / W wall tops). |
| Towers / bartizans | The S corner towers, the gate towers, the leg bartizans and the rail-gate drum turrets. |
| Machicolations | The corbels under the span and over each gate. |
| Moat + water gate | The rail line + the arched rail gates. |
| Bailey | The container yard. |

## 5. The logistics flow (what the crane does)

```
          TRAIN (N)  <---- high-speed line, E-W, through the city to the port ---->
             ^  ^        (the span rolls out over it on the rail-gate bridges)
             |  |
    W BAYS <-+--+-> GANTRY travels N-S on the wall runways; the KEEP (trolley) travels E-W on the span
             |        => reach = the whole rectangle: train, quay, bailey, the three bay lanes, the wall tops
    WALL  <--+--> E BAYS
             |
          S BAYS
```

- **Trucks**, three sides: trucks enter the W, S and E gatehouses and park in the inner bay lanes, all under the
  crane's reach. Queues wait on the street outside each gate. The crane lifts boxes off a truck or drops boxes onto it.
- **Train**, fourth side: the gantry rolls to its N stop, with its legs on the rail-gate bridges and the span over the
  inner track. The keep runs along the span to the car.
- **Wall**: the top courses of the curtain wall are working stock. The crane takes boxes out of the wall and puts them
  back.
- **Bailey**: the stacks are buffer storage between all three.

## 6. Where route nodes / rooms can sit (slots only; the game graph decides the topology)

Every slot is a box or window that can be cut open with the kit's cutaway room:

| Slot type | Where | Count in the test |
|---|---|---|
| Gatehouse chamber | over each gate arch, outer face | 1 (S); W and E available |
| Wall, outer face | a cut-open container in courses 1–3 | 4 |
| Wall, inner face | a yard-side container, seen over the wall | 1 |
| Corner tower | the S faces of the S corner towers | 2 |
| Truck box | a container on a parked truck in a bay lane | 1 |
| Train box | a container on a train car | 1 |
| Gantry leg | stacked floors in each leg's S face | 4 |
| Span gallery | windows in the span's S face | 2 |
| Keep crown | the server | 1 |

**How the illustrative run threads the logistics.** It plays out like a siege. The player enters at a truck gate,
goes along the walls to a corner tower, then takes one of two sides:
- the outer W wall and the train;
- the E bay lane (a truck's box) and the inner E wall.

Both sides climb a gantry leg, cross the span and go up into the keep. The test uses 18 nodes over 9 layers. A GDD
layer of 2–4 nodes fits naturally on paired slots (W/E leg, W/E span, gate W/S/E).

Places where the logistics could carry a link (presented as **places only**; any rule belongs to the game sessions):
- a truck box that moves between bay lanes;
- a train box under the span;
- the spreader's container (the "portcullis") between the bailey and the span;
- the wall's top course.

## 7. The Central Server

**THE MASTER MANIFEST** sits in the keep's open crown, on top of the trolley. It is the highest lit point on the
landmark, open on all four sides so the TARGET reads from any orbit, with a beam straight up for city zoom. Because
the keep is the trolley, the server physically rides the crane; whether that matters in play is a question for the
designer (Q3). For the overview it is parked left of centre on the span, over the bailey.

## 8. Landmark lighting (the landmark ≈ 2× its local background)

The light is carried by the landmark itself, not by raising exposure:
- **Gantry**: warm uplights from the bogie sills up each leg's S and outer faces; orange lit edges on the span (the
  lower edge and under the battlements), the bartizan cornices and the keep's cornice. The MERIDIAN stencil is the
  brightest flat element.
- **Keep**: two side washes from the span ends (orange / sodium), a soft front key, and tall narrow warm windows. The
  red-orange server core and a beam sit in the crown.
- **The yard**: five down floods under the span, alternating sodium and white, so the bailey reads in a pool of light
  framed by the Π.
- **Walls and towers**: street-level wall washers grazing the container door ends; an orange wall-walk line; lit
  slits, red beacons and red gate lamps.
- **The rail**: a cold blue light line on the train and on the rail-gate arches, a sodium glint along the tracks and
  a headlight beam. This is the one cold accent in the HQ, so the 4th side reads as different.
- **Rim**: two area lights behind, light-linked to the landmark only (as in v2).

## 9. Reading at a glance

- **City zoom** (the all-corps map, where the HQ is about 60 px): the **Π** silhouette with a lit block on top. No
  other HQ has an arch:
  - Halcyon is a pyramid;
  - Orbital is a ring and a needle;
  - Solace is a helix;
  - Aurelian is a round colosseum;
  - Tethys is a pier city.

  A cold blue line (the rail) runs off to the port. The orange is Meridian's district colour, and the beam from the
  crown marks it.
- **Netrun zoom** (the overview and decisions): the castle vocabulary does the work. Gates, towers and battlements
  read as "fortress". The crosswise container walls read as "shipping". The trucks in the bays and the train under
  the span read as "logistics". The route climbs one obvious shape (wall → leg → span → keep), so the layout explains
  itself.

## 10. The three concepts (`concepts_sheet.png`) and the recommendation

| | Concept | Verdict |
|---|---|---|
| **A** | **Gatehouse Gantry**: the gantry is the gatehouse and the trolley is the keep | **Recommended.** |
| B | **Slewing Donjon**: a round keep slews a long jib with a castellated counterweight | A strong tower, but the jib reads as "a crane on a tower" (v2's problem again), and a round keep inside a wall echoes Aurelian's colosseum at city zoom. A slewing jib also hides its reach and fights the camera. |
| C | **Quayside Keep**: a ship-to-shore crane straddles the rail as a gatehouse, its boom lowered over the bailey | Reads as "port crane" before "castle". The boom is a long thin diagonal that is lost at city zoom, and the castle stays a separate fort. |

**Why A:**
1. The brief's own sentence is "a giant crane that resembles a medieval castle". Only A makes the crane *be* the
   castle, rather than sit in it or next to it.
2. One unique silhouette, the Π arch, distinct from every other HQ.
3. Its reach is honest and readable: gantry travel × trolley travel covers a rectangle that contains the train, the
   three bay lanes and the walls. That is exactly the brief's flow, and the plan shows it in one hatch.
4. The route has an obvious climb (wall → leg → span → keep) with the server at the top, front and centre.
5. Every castle term maps to a working part (section 4), so nothing is decoration.

## 11. Test render (`H_overview_test.png`, 1280 × 720, Cycles 32 spp, AAA-2)

| median | under 0.10 | over 0.85 | landmark / local background | render |
|---|---|---|---|---|
| 0.130 (target ~0.14) | 36.6 % (25–40) | 1.0 % (≤ 2.5) | 0.207 / 0.112 = **1.85** (target ~2) | 15 s (frame), 25 s (with the build) |

The occlusion rule as in v2 (`hq_kit/section.py`): 85 city buildings flattened to stubs and 28 ghosted. Two v3
changes make it work for an HQ that fills its lot:
- a tighter vertical margin (`downtown.occ`);
- ground-level rooms hidden inside the walls are left out of the target volume (`hq_graph.OCC_HIDDEN`).

Without those, the whole foreground ghosted.

Known weaknesses of the test:
- the train behind the span reads only as a light band (Q4);
- the rail-gate arches are too small to read at this distance;
- the trucks are lost at overview scale (they need lit cabs or a bay-lane light).

## 12. Files

| File | What |
|---|---|
| `DESIGN.md` | This document |
| `concepts_sheet.png` | The three Workbench massing thumbnails, side by side |
| `plan.png` | The orthographic plan: trucks, train, crane (legs, runways, span, keep, reach), walls, gates, the server, the route slots |
| `H_overview_test.png` / `H_overview_test_plate.png` | The Cycles overview test with and without the route UI |
| `scripts/` | The kit copied from `hq_meridian/scripts` + the v3 corp plugin: `hq_preset.py`, `hq_graph.py`, `hq_build.py`, `hq_mechui.py` (neutral), `thumbs.py`, `concepts_sheet.py`, `plan.py`, `locked.py` (GPU lock wrapper) |

Rebuild (from `scripts/`):
- thumbnails: `python locked.py thumbs -- blender -b --factory-startup --python thumbs.py -- D:/rc_scratch/meridian_v3/thumbs`
  then `python concepts_sheet.py D:/rc_scratch/meridian_v3/thumbs`;
- the plan: `python plan.py`;
- the test: `python locked.py test -- python hq_test.py H_overview test`, with the output in `../scratch/test/`.

## 13. Open questions for the designer

1. **The all-corps city render** still shows the v2 container fort. Since the city landmark is canonical, it needs the
   Π gantry when this is approved. Should that be a separate task for the city session?
2. **The freight viaduct.** v2's elevated line led north to the port. Here the line runs E-W along the N edge at
   grade, through the rail gates. Should it still turn to the port (a curve off-lot), or should the lot be rotated so
   the N side faces the coast?
3. **A server that moves.** The keep is the trolley, so the server rides the crane. Keep it as flavour only (parked
   for every shot), or offer it to the game sessions as a mechanic hook? (Art makes no rule here.)
4. **Overview camera.** With the train on the N side and the camera from the SSW, the train sits behind the span and
   reads only through its blue light line. Alternatives: rotate the overview to the SE (the train recedes on the
   right, the Π seen at an angle) or keep the gate face-on (recommended).
5. **Orange.** The gantry is Meridian orange and so are the lit edges, which is close to the route's "next" orange
   (v2 Q1, still open). A darker rust-orange paint with sodium-white edges is the fallback.
6. **Scale.** The towers and turrets stand up to 13 BU outside the lot line (bastions). Should the walls be pulled
   in instead, so everything stays inside the lot?

## 14. Round 2 (coordinator answers + designer notes, test 2)

### 14.1 What changed

| # | Change | Where |
|---|---|---|
| Q1 | The landmark build is an **importable module**: `scripts/meridian_landmark.py`, entry point `build(K, rooms=True, rail=True) -> hooks`. `place(K, origin, k=0.2375)` moves and scales every face, light and beam into the one-city map. Its docstring documents the K namespace it needs. `hq_build.py` is now a 3-line shim. | `meridian_landmark.py` |
| Q2 | The freight line follows the **city polyline** (`D:\rc_scratch\city_all_corps\meridian_rail.json`). Local = (world − hq_centre) / 0.2375. In the lot it runs at grade along the N edge, through both rail gates. Out of the W rail gate it eases N onto the city's westbound leg (local y 138.9). It climbs on the city's ramp to the **deck at 73.7 kit = 17.5 city BU** at the city corner (−117, 255), then follows the city polyline corner for corner to the seawall terminal. To the E it continues at grade into the city. | `meridian_rail.py` (pure python) |
| Q3 | The keep (trolley) is **parked** for every shot. That it rides the crane is flavour only; see 14.4 for the possible game hook. | preset `gantry.keep_x` |
| Q4 | The overview looks from the **SE** (yaw −32°, pitch 36°). The Π is seen at an angle, the E rail gate and the train sit beside the span, and the server is front and centre: the keep is parked so its crown projects on the frame's usable centre line. | preset `cam` |
| Q5 | The gantry is **rust-orange paint** (albedo 0.30 / 0.075 / 0.022). All lit edges and the MERIDIAN stencil are **sodium-white** (1.0 / 0.80 / 0.52). Meridian's "next" orange is no longer used on the HQ. | palette `gantry`, `edge` |
| Q6 | **Everything is inside the lot.** The S corner towers fill the lot corners, the gatehouses' outer faces sit on the lot line, and the rail-gate drum turrets stand on the wall's inner side. | `meridian_landmark` towers |
| D1 | **The TARGET is the keep.** It is a distinct silhouette: <br>- a body with a corbelled battlement; <br>- four corner turrets with **spires**; <br>- an **open lantern crown**, posts and mullions only, lit from inside; <br>- THE MASTER MANIFEST visible inside: the server core with glowing rings and two racks; <br>- a crenellated cap and a spire with a beacon and the beam. <br>Lit by: two side washes, a front key, and an interior lantern light. | keep block |
| D2 | **The train reads.** It is a full high-speed set: a long wedge nose at each end, a lit windscreen and headlamps, graphite carriages with a **bright pane-by-pane window band** and a cold-blue skirt line, and one carriage cut open as the route's slot. It stands in the **bay beside the gantry**, which is parked at y 70 just S of the tracks. There is a second lit set on the ramp to the port. **Platform lights**: a lamp every 11 BU, a lit canopy line and spots. The span's down floods now aim at the train, not the wet yard floor. | rail block |
| D3 | **Truck ring road** all round the lot: 6 lanes (36 kit BU), a lit median, mast lamps. Queues sit bumper to bumper in the two inbound lanes at each truck gate, with **lit cabs** (windscreen, side windows, an amber roof marker, head and tail lamps). Moving traffic is light streaks only (the route-map rule: no car geometry). There are three highway on-ramps and elevated highways (see 14.2). The rail crosses the ring's W and E sides at grade, with red signals. | ring block |
| fix | Bigger rail-gate arches: one stepped arch, 26 high × 25 wide, lit in the rail's cold blue. Lit truck cabs and bay-lane lights: amber lane edges, a lamp post every 22 BU and a sodium area light per lane. | |

### 14.2 Ring-road exits (for the city agent's highway hub)

The ring road is a square band from |x| or |y| = 122 to 158 kit BU (29.0–37.5 city BU) around the HQ centre. Each
exit leaves the ring's **outer kerb** and becomes an on-ramp:
- the ramp climbs to a **deck at 40 kit = 9.5 city BU** over 170 kit (40.4 city) BU on a cosine ease;
- the highway then runs straight out to 1150 kit (273 city) BU;
- the deck is 26 kit (6.2 city) BU wide, with two lanes each way.

The city coordinates use `hq_centre` = (18.0, 222.0) from `meridian_rail.json`, with x east, y north.

| Exit | Kit local (x, y) | City world (x, y) | Heading (deg from N, clockwise) | Serves |
|---|---|---|---|---|
| S | (0.0, −158.0) | (18.00, 184.47) | 180 (south) | the S truck gate |
| W | (−158.0, −30.0) | (−19.52, 214.88) | 270 (west) | the W truck gate |
| E | (158.0, −30.0) | (55.52, 214.88) | 90 (east) | the E truck gate |

No exit is on the N side: that is the rail. The data lives in `meridian_rail.exits(cp)` and
`meridian_rail.highways(cp)` (polylines with z), and the city corridors already keep buildings off them.

### 14.3 Test 2 values

See the report / section 14.5 for the measured numbers.

### 14.4 A possible hook for the game sessions (art makes no rule)

The keep is the crane's trolley and the server sits in it, so the target could physically **move along the span**:
the keep could be over the train one turn and over a bay lane the next. Art parks it for every shot. If the game
sessions want a moving-target mechanic, the art already supports it as a mover (the kit's `mover()` and
`MOVER_POS`). Other places the logistics could carry a link (places only, no rules):
- the spreader's container;
- a train carriage;
- a queued truck's box.

### 14.5 Test 2d (camera round)

Previews (Eevee, `scratch/cam/yaw35.png`, `yaw62.png`, `yaw85.png`) against the SE view of test 2c, where the Π
read as a walled box. The overview is now a **high 3/4 from the SW**: `cam.ov_yaw` = +35, `pitch_o` = 38. At +35 the
gantry's W leg and the keep stand at the left, the span and the lit train band run across the north side, and the
Π reads. At +62 the train is foreshortened behind the leg; at +85 it is edge-on and the Π is lost.
The keep, train, ring road and rust-orange paint are as in 14.1. The exits in 14.2 are unchanged and still apply.

Cycles test (1280 x 720, 32 spp): `scratch/test/H_overview.png`, `H_decision.png`.

| shot | median | under 0.10 | over 0.85 | landmark / local bg |
|---|---|---|---|---|
| H_overview | 0.148 (0.14 +-0.03) | 34.4 % (25-40) | 2.3 % | 0.245 / 0.116 = 2.12 |
| H_decision | 0.134 | 37.7 % | 2.6 % | 1.05 (the keep is not framed here) |

### 14.6 Test 2e (AD review: massing)

2d still read as a walled box, so the gantry was raised, not the camera moved (yaw +35 kept; the framing follows
`hq_graph.OV_POINTS`). Changes: span underside 84 -> **104 BU (2.5x the 41 BU wall)**, span top 122, legs to 142
(was 108) and 20 deep N-S (was 12; E-W is held at the wall's 14 so everything stays in the lot), keep top 148 (was
128) so the lantern crowns at about 163 BU. Rim light: sodium-white vertical edges on all four leg corners and on
both top edges of the span. Bailey and walls darkened about 30 % (`steel`, `steel_alt`), span down floods 4.0e4 ->
2.8e4. Ring-road light streaks halved (`streak_k` 6 -> 3).

| shot | median | under 0.10 | over 0.85 | landmark / local bg |
|---|---|---|---|---|
| H_overview | 0.126 | 41.6 % | 1.8 % | 0.223 / 0.101 = 2.21 |
| H_decision | 0.120 | 42.3 % | 2.5 % | 1.03 |

Slightly dark (under-0.10 just over 40 %); a +0.1 stop of exposure would fix it if wanted.
