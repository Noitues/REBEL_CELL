# Takeover actions: inspiration board and new concepts, 2026-11-14

Art-pass research for the Takeover fight screen. The question: how should the runner's actions look so that the screen reads as
hacking and netrunning, not as a card game? Concept documents and rough wireframes only. No Godot work, no rule changes.

Inputs: `../NOTES.md` (B-086 plates, B-088 forecast, designer rulings) and `../alternatives/ALTERNATIVES.md` (nine directions,
all rejected: "None of those ideas feel right").

## Why the nine fell flat (diagnosis)
All nine keep the same loop: **a panel of objects beside the wheel → pick one → point it at the wheel**. Only the object's
costume changed (chip, command line, cartridge, token, jack, radial menu). Three habits sink them:
1. **Props, not process.** A terminal, a cartridge or a cable is a *picture of* hacking equipment. Fiction and real tools show
   hacking as **interfering with a system that is already running**: a signal, a schedule, a sequence, a lock. The wheel
   is that running system, yet the actions never touch its language.
2. **The action lives in a menu, the effect lives on the wheel.** The two halves do not share a visual grammar, so the hand
   still reads as a hand of cards in a new frame.
3. **The flanks hold containers, not meaning.** The rejected layouts filled the side space with boxes (rig, daemon panel),
   not with something that explains the fight (who acts, when, in what order).

So a native answer should (a) draw the action **in the same medium as the target** (the wheel's geometry, its signal, its
order of play), (b) make the flanks **part of the system's logic**, and (c) reuse the B-088 numbered arrows, which the
designer has already approved, rather than adding a second language.

---

## Reference board
Paraphrased. "Lends" is what the reference could give this screen. URLs are where the idea was checked; a few entries are
from general knowledge and point at the canonical page.

### A. Hacking and netrunning games
| # | Source | Interaction or visual idea | Lends |
|---|---|---|---|
| 1 | Cyberpunk 2077, Breach Protocol ([wiki](https://cyberpunk.fandom.com/wiki/Breach_Protocol), [solver write-up](https://timiskhakov.github.io/posts/breaching-breach-protocol)) | You build a code sequence in a limited buffer by alternating rows and columns of a matrix; hovering a target code highlights every place it occurs. | A hack is a **sequence that fits a constraint**, and hover shows every legal place at once. |
| 2 | Cyberpunk 2077, quickhacks ([wiki](https://cyberpunk.fandom.com/wiki/Quickhacking)) | Target first: scan a thing, then a short list of hacks for that target with RAM cost; an upload bar shows the hack travelling. | RAM cost words; the travel time of an upload as the "aim" beat. (Target-first was tried in A2; avoid the radial.) |
| 3 | Android: Netrunner, ICE and icebreakers ([Stimhack primer](https://stimhack.com/ice-and-icebreakers/), [NISEI rules](https://nullsignal.games/wp-content/uploads/2021/10/NISEI-Comprehensive-Rules-v1.5-clean.pdf)) | Breakers have a subtype (Fracter / Decoder / Killer) that matches one ICE type, plus strength you pump. | The **type word as a key that fits a lock type**. Matching shape = legal target. |
| 4 | Transistor, Functions ([GamesBeat guide](https://gamesbeat.com/master-transistors-complex-skills-and-possible-combos-with-this-function-guide/)) | Each Function is used Active, as an Upgrade on another, or Passive; the build is a ring of slots. | One object, several readings depending on **where it is socketed**. |
| 5 | Exapunks ([Wikipedia](https://en.wikipedia.org/wiki/Exapunks), [PC Gamer review](https://www.pcgamer.com/au/exapunks-review)) | Little agents walk a network of hosts carrying files; the fiction is printed zines. | Agents (tried as A3 daemons, rejected) but also the **zine print** as the hacker's own material, which our punk layer already is. |
| 6 | Hacknet ([Wikipedia](https://en.wikipedia.org/wiki/Hacknet), [Steam thread on ports](https://steamcommunity.com/app/365450/discussions/0/530649887203170214)) | Each port needs its own cracker; open enough ports and the final hack becomes possible. Terminal plus a graphical map. | Locks that need a **matching tool per lock**; progress shown as ports opening. |
| 7 | Deus Ex: Human Revolution hacking ([StrategyWiki](https://www.strategywiki.org/wiki/Deus_Ex:_Human_Revolution/Hacking)) | Capture nodes from the I/O port toward the registry; fortify captured nodes; Stop worm freezes the trace. | Capture / fortify / stall as **colour moving along a graph**; a visible trace clock. |
| 8 | Invisible Inc, Incognita ([wiki](https://invisibleinc.gamepedia.com/File:Incognita_Programs.png)) | Programs strip firewall pips from devices for PWR; daemons are hidden traps revealed when you break in. | **Integrity as pips you strip**, not a number that changes. |
| 9 | Midnight Protocol ([Third Coast Review](https://thirdcoastreview.com/2021/10/12/review-midnight-protocol), [ModDB reviews](https://www.moddb.com/games/midnight-protocol/reviews)) | Keyboard-only tactical hacking; reviewers say the control scheme itself sells the fantasy. | Hotkeys as a first-class path (1-5, Tab through targets). |
| 10 | Duskers ([Wired review](https://wirednews.pages.dev/2016/05/duskers-review), [feedme.design](https://feedme.design/duskers-a-gaming-masterclass-in-immersive-storytelling)) | Diegetic command line; the player and the character use the same interface; distance creates tension. | Warning: a literal prompt is slow under pressure (that is what sank A1 and B). |
| 11 | Uplink (Introversion, general knowledge; [Wikipedia](https://en.wikipedia.org/wiki/Uplink_(video_game))) | A world map with your bounce route drawn as lines; a trace creeps back along it. | **Lines between hosts as the core picture** of a hack; the trace as a moving front. |
| 12 | Gunpoint, Crosslink ([Wikipedia](https://en.wikipedia.org/wiki/Gunpoint_(video_game)), [dev blog](https://www.pentadact.com/?p=2636)) | Flip to a wiring view and drag new links between devices; the joke is the system turning on its owner. | Hacking as **re-routing the system's own wiring**, not adding props. |
| 13 | Shadowrun: Hong Kong Matrix ([GamePressure guide](https://www.gamepressure.com/shadowrunhongkong/hacking-matrix/z27aee), [RPG Codex update](https://rpgcodex.net/article.php?id=10022)) | Patrol ICE with sight cones, a rising system trace, a pattern minigame at data cores. | A **trace meter** as the corp's clock; each server has its own look (our corp skins). |
| 14 | NieR: Automata hacking ([pattern analysis](https://saschb2b.github.io/game-mechanics/games/nier-automata/genre-shifting-combat)) | Hacking cuts to a minimal shmup in a different visual register; it reuses the game's UI palette. | Cyberspace can be a **different register of the same palette**: our cyan system layer. |
| 15 | Quadrilateral Cowboy ([Wikipedia](https://en.wikipedia.org/wiki/Quadrilateral_Cowboy)) | Typing commands into a physical deck, made to feel physical (slamming Enter). | The commit beat must feel physical: one heavy confirm, not a menu click. |
| 16 | Watch Dogs 2 PC hacking panel ([Game Developer, designing controls](https://gamedeveloper.com/design/designing-game-controls)) | Hack options laid out to mirror the keyboard so hands find them without looking. | Hotkey layout = screen layout (keys 1-5 top to bottom on the flank). |

### B. Film, anime, comics and prose
| # | Source | Idea | Lends |
|---|---|---|---|
| 17 | Gibson, *Neuromancer* ICE and icebreakers ([LitCharts terms](https://www.litcharts.com/lit/neuromancer/terms), [ICE article](https://ipfs.ssi.eecc.de/ipns/en.wikipedia-on-ipfs.org/wiki/Intrusion_Countermeasures_Electronics)) | Corporate data as geometry walled by ICE; the Kuang virus is a slow, patient penetration program you ride. | Attack as something that **grows into the target over time**, not a hit. |
| 18 | *Ghost in the Shell* (1995) ([sci-fi interfaces report card](https://scifiinterfaces.com/2013/08), [Envisioning](https://www.envisioning.com/research/origins/ghost-in-the-shell)) | Network intrusion shown as diagrams, wireframe overlays and text, cool green, often over the real world. | Overlay the hack **on** the object (the wedge), not beside it. |
| 19 | *Serial Experiments Lain* ([archania analysis](https://archania.org/p/the-symbolic-world/symbolic-works/film/serial-experiments-lain)) | The Wired is an atmosphere: power lines, hum, overexposed space; meaning carried by form. | Mood over gadgets: lines and signal, not boxes. |
| 20 | *Hackers* (1995) ([Inverse](https://inverse.com/entertainment/hackers-movie-anniversary), [cybercultural](https://cybercultural.com/p/cyberspace-movies-1995/)) | Cyberspace as a neon city of text; "beautifully wrong"; hacker graffiti and style as identity. | Permission to be stylised; the hacker's **mark** on the system. |
| 21 | *The Matrix* digital rain ([befores & afters](https://beforesandafters.com/2019/03/27/secrets-of-the-matrix-code/)) | A custom glyph set (mirrored kana and numerals) falling in columns, unreadable but unmistakable. | A **private glyph set** for system text: our type words could carry a signal glyph. |
| 22 | *Cyberpunk: Edgerunners* ([AWN](https://awn.com/animationworld/cyberpunk-edgerunners-vibrant-ode-retro-anime), [Gizmodo](https://gizmodo.com/cyberpunk-edgerunners-netflix-trigger-review-spoilers-1849529423/2)) | Netrunners shown in the net with red line art over flat colour; bold, retro, graphic. | Graphic line work as the cyberspace register, which our linocut key line already is. |
| 23 | *Mr. Robot* ([Paste, Kor Adana](https://pastemagazine.com/tech/mr-robot/kor-adana-is-mr-robots-mr-robot), [Syracuse interview](https://onlinegrad.syracuse.edu/blog/Mr-Robot-Cybersecurity-Expert/)) | Real tools on screen; if it can't be done, it isn't shown. Hacking is quiet text in real software. | Credibility comes from **real tool conventions** (flow graphs, logs, packet fields). |
| 24 | *Tron* (1982) and *Johnny Mnemonic* (1995) (general knowledge; [Tron](https://en.wikipedia.org/wiki/Tron), [Johnny Mnemonic](https://en.wikipedia.org/wiki/Johnny_Mnemonic_(film))) | Programs as glowing lines and vehicles inside the machine; a data-glove gesture world. | Light **trails** as the program's path through the system. |

### C. Real security and ops tools
| # | Source | Idea | Lends |
|---|---|---|---|
| 25 | Wireshark Flow Graph ([user guide](https://www.wireshark.org/docs/wsug_html_chunked/ChStatFlowGraph.html), [TechRepublic](https://www.techrepublic.com/article/using-the-flow-graph-feature-on-wireshark/)) | Each host is a vertical line; each packet is a horizontal arrow between them, in time order, with ports and flags. | **Two hosts as two flanks, packets as numbered arrows.** The strongest structural match. |
| 26 | MITRE ATT&CK matrix and Navigator ([Navigator intro](https://medium.com/mitre-attack/the-att-ck-navigator-a-new-open-source-project-a73ae500f361)) | Tactics as ordered columns, techniques as cells, colour layers laid over the matrix. | Ordered steps as a **ladder** you can read left to right; overlays as layers. |
| 27 | Packet headers (TCP flags, length, destination) (general knowledge; [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293)) | A packet is a header of fields: length, flags, destination; a reset (RST) refuses a connection. | Cost = length, type word = flag, target rule = dst field, can't-use = RST with a reason. |
| 28 | Oscilloscope and logic analyser channels (general knowledge; [Wikipedia](https://en.wikipedia.org/wiki/Logic_analyzer)) | Stacked labelled channels, each a trace; a probe clipped to a pin; cursors measure time. | **The hand as five channels**, each a waveform; aim = probe. |
| 29 | SDR waterfall ([sdr-radio](https://sdr-radio.com/SpectrumAndWaterfall), [PySDR](https://github.com/MLAB-project/pysdr)) | Spectrum over time: the current line on top, history scrolling down and fading; brightness = strength. | The corp's **plan as a waterfall**: NOW bright at the edge, the future (or the past) fading. |
| 30 | Radar PPI ([NEETS module](https://rfcafe.com/references/electrical/neets-modules/NEETS-Module-18-3-1-3-10.htm)) | A rotating sweep refreshes a polar display; long-persistence phosphor keeps echoes glowing between sweeps. | The wheel already is a polar display; **persistence** for lasting effects (afterglow on a wedge). |

### D. UI design, FUI and game readability
| # | Source | Idea | Lends |
|---|---|---|---|
| 31 | Territory Studio on FUI ([Pushing Pixels interview](https://www.pushing-pixels.org/2014/08/07/the-craft-of-screen-graphics-and-movie-user-interfaces-interview-with-david-sheldon-hicks-of-territory-studio.html), [Medium: sci-fi interfaces](https://medium.com/territory-film/sci-fi-interfaces-and-emerging-technology-d8390b1c1b33), [AWN on BR2049](https://awn.com/vfxworld/communicating-abstract-user-interfaces-blade-runner-2049)) | Screens reveal character and story; start from emotion; bespoke over genre clichés; in games, design for use first. | Test: does the screen **say who is doing what to whom**? Avoid stock "hacker" props. |
| 32 | Into the Breach telegraphing ([Game Developer: clarity](https://gamedeveloper.com/design/-i-into-the-breach-i-dev-on-ui-design-sacrifice-cool-ideas-for-the-sake-of-clarity-every-time-), [Road to the IGF](https://gamedeveloper.com/game-platforms/road-to-the-igf-subset-games-i-into-the-breach-i-)) | Every enemy action is drawn on the board before it happens, with attack templates; clarity beats cool ideas. | Our forecast already does this. **Make the player's actions use the same drawing as the corp's.** |
| 33 | Patterning circular drum machine ([Ethan Hein UI case study](https://ethanhein.com/wp/2015/user-interface-case-study-patterning/)) | Concentric rings of steps; each ring has its own length and rotation; a playhead sweeps. | A wheel is a **running sequencer**; the fixed pointers are playheads. |
| 34 | Elektron parameter locks ([Elektronauts](https://www.elektronauts.com/t/p-locks-vs-trig-conditions/42492)) | You lock a change onto one step of a sequence that keeps running; trig conditions decide if a step fires. | An action = **a lock placed on one step** of the corp's running loop. |

### E. Tabletop alternatives to a hand of cards
| # | Source | Idea | Lends |
|---|---|---|---|
| 35 | Robo Rally registers ([rules](https://rules.dized.com/game/-35QGfadQpKOT0xvvgNZnQ/_JLhzYwfRk2UB2WUXvv84A/2-the-programming-phase)) | You program five registers, then they resolve left to right with board elements between. | Visible **resolution order** as a physical row. |
| 36 | Dicey Dungeons ([Game Developer: Witch design](https://gamedeveloper.com/design/witch-craft-how-i-dicey-dungeons-i-balances-chance-and-predictability)) | Equipment slots with conditions (odd, below 4); dice drop into slots. | The **slot's shape states the rule**; an illegal drop simply does not fit. |
| 37 | Mac Gerdts rondels ([Navegador rules](https://www.riograndegames.com/wp-content/uploads/2013/02/Navegador-Rules.pdf)) | Actions live on a wheel; you move a marker round it; going further costs more. | Cost as **distance travelled on a circle**. |
| 38 | Gloomhaven area templates (general knowledge; [Wikipedia](https://en.wikipedia.org/wiki/Gloomhaven)) | An action's area is printed as a small hex diagram on the card. | The **target rule drawn as a footprint shape**. |

### F. Locks, ciphers and dials
| # | Source | Idea | Lends |
|---|---|---|---|
| 39 | Enigma rotors ([Crypto Museum](https://cryptomuseum.com/crypto/enigma/working.htm), [rotor details](https://en.wikipedia.org/wiki/Enigma_rotor_details)) | Rotors step like an odometer; a notch carries the next rotor; the ring setting offsets the wiring. | NUDGE is literally a rotor step; **rings with notches** as actions. |
| 40 | Jefferson disk / M-94 ([Wikipedia](https://en.wikipedia.org/wiki/Jefferson_disk)) | A stack of lettered disks on an axle; turn each disk to line up a row. | The **deck as a cylinder of disks**; hand = the disks you can turn now. |
| 41 | Safe manipulation and lock-picking minigames (general knowledge; [Wikipedia: safe-cracking](https://en.wikipedia.org/wiki/Safe-cracking)) | Feel for contact points; a pick binds on the wrong pin; the right one gives a click. | Aim by **detents**: legal targets click, illegal ones bind and say why. |
| 42 | Key bitting and pin tumblers (general knowledge; [Wikipedia: pin tumbler](https://en.wikipedia.org/wiki/Pin_tumbler_lock)) | A key's tooth profile matches a lock's pin stack. | Action identity = **its footprint**, the shape of what it can touch. |

### G. Street and print culture (the runner's own layer)
| # | Source | Idea | Lends |
|---|---|---|---|
| 43 | Web defacement culture (general knowledge; [Wikipedia: website defacement](https://en.wikipedia.org/wiki/Website_defacement)) | Hacktivists replace a corporate page with their own crude, loud mark. | Taking a segment = **overprinting corp enamel with punk print**, which the locked style already does. |
| 44 | Stencil graffiti and zines (general knowledge; [Wikipedia: stencil graffiti](https://en.wikipedia.org/wiki/Stencil_graffiti)) | A cut stencil shows exactly where paint will land before you spray. | The stencil **is** the preview: hold it over a wedge, see the cut-out. |

44 references across seven fields.

---

## Concepts
Every concept keeps: energy cost, the target rule, the type word (CONTROL, VIRUS, FIRE, BLOCK, DELAY), draw / discard /
exhaust, the red "can't use" reason, the B-088 wedge forecast at rest and the numbered hover arrows with the HUD step list,
UNDO, END TURN and the corp plan (NOW, T+1, T+2). The wheel, pointers, walls and seals are unchanged unless stated. All five
use the wheel centred with both flanks working. The netrun words (RAM, QUEUED, SENT...) are dress; a `DECISIONS.md` entry is
owed if the designer takes any of them.

### 1. PACKET LADDER (recommended) — `insp_1_packet_ladder.png`
**Pitch.** The screen is a packet-capture flow graph. Your host's lifeline runs down the left flank, the corp's down the
right; the wheel is the wire between them. An action is a packet you send; the corp's plan is packets it sends back.

**From:** Wireshark Flow Graph (25), packet headers (27), Uplink lines (11), Mr. Robot's real-tool credibility (23), Into the
Breach's "same drawing for both sides" (32), MITRE's ordered ladder (26), B-088 itself.

**How it uses the flanks.** Left: the punk-print host header (health, RAM, statuses), the OUTBOX of packets on the lifeline
(keys 1-5 top to bottom), QUEUED / SENT / DROPPED (draw / discard / exhaust), ROLLBACK. Right: the enamel corp host, INBOUND
plan packets on its lifeline (NOW, T+1, T+2), the armed list, a log of the last END TURN in step numbers, SEND (END TURN).

**Mechanics mapping.**
- Packet header fields: **len** = energy cost, **flag** = the type word, **dst** = the target rule (YOURS, THEIRS, 3x THEIRS,
  HUB for no target).
- Can't use: the packet takes a red **RST** tab with the reason ("RST: needs 4").
- The forecast is the same picture: hover a wedge and the B-088 numbered arrows are drawn, now visibly leaving a lifeline
  (yours from your port, corp plan steps from the corp lifeline via the hub, counterattacks from the wedge).

**One play.**
1. Pick: press 3 or click BREACH. Its port on the lifeline lights; its dst field lights every legal wedge (pink outline).
2. Aim: move to a wedge; a dashed packet arrow runs from the port to it, labelled "P1 BREACH CORE 7 -> 4", and the wedge's
   B-088 outcome mark updates.
3. Confirm: click or Enter. The arrow goes solid and fires; the packet leaves the outbox and drops to SENT.
4. Result: the wedge updates; in the replay at END TURN the corp's packets fire from the right lifeline in step order, in the
   same arrow language.

**Style.** Keeps all three layers: your lifeline and packets are punk print (bone, pink key line), the corp's are enamel with
the teal edge, arrows and numbers are cyan glass.

**Why more native than the nine.** The action is not a prop; it is the **same numbered arrow** the game already uses to explain
what happens. The flanks are not containers; they are the two parties of a conversation, in time order. It looks like a real
analysis tool, not a deck.

**Risks.** Packets are still rectangles in a list; their header form must stay thin (one strip, no art) or they slide back
into cards. Long arrows from the left flank to right-side wedges cross the wheel (route them round the rim, or start the arrow
at the rim point nearest the lifeline). Arrows from both sides at once can clutter: draw only the aimed packet and the hovered
wedge's trace.

**Effort.** S-M. Lines, labels and the existing wheel; the arrow renderer is shared with B-088. Godot: Line2D plus a label
auto-placer (already owed).

### 2. SPLICE — `insp_2_splice.png`
**Pitch.** The hand is five signal channels on a logic analyser. The type word is a waveform (CONTROL square, VIRUS noise,
FIRE spike, BLOCK clamped flatline, DELAY a gap then a pulse). Playing an action splices that waveform into the outer band of
a wedge, where lasting effects stay visible as a signal.

**From:** oscilloscope and logic analyser (28), SDR waterfall (29), radar persistence (30), Elektron parameter locks (34),
Ghost in the Shell overlays (18), the Matrix's private glyph set (21), NieR's palette-true hacking register (14).

**Flanks.** Left: PAYLOAD CH1-CH5, each a punk-print label chip (name, cost, type word, target glyph) plus its trace; BUFFER /
LOGGED / BURNT counts. Right: the corp CARRIER as a waterfall: T+2 and T+1 fall toward NOW, past turns scroll down and fade;
armed list; TRANSMIT.

**One play.** Pick a channel (its trace brightens) → a probe line follows the pointer; legal wedges show a tuned band →
over CORE, the spike waveform previews in CORE's rim band and the outcome mark reads "7 -> 4" → click: the splice is drawn in.
GUARD stays as a blue clamp on your ICE; a virus stays as noise on RELAY; TIME BOMB as a gap with a waiting pulse.

**Style.** **Bends it slightly.** The system layer grows: five waveform traces in cyan-glass panels. The punk print keeps the
label chips; the waveforms take the type colours.

**Why native.** The wheel already turns like a scope; the type word becomes a shape you learn once and then read everywhere,
on the hand and on the wedge.

**Risks.** Five waveforms are a new vocabulary to learn; colour-blind safety must rest on shape (it does). The rim band
competes with the HARM armed arc and the status tags (B-088 moved them to the outer edge). Motion and shader work in Godot.
**Effort.** M.

### 3. ROTOR — `insp_3_rotor.png`
**Pitch.** Your deck is a cipher cylinder of disks. Pick one and it rises as a thin ring around the wheel; turn the ring and
its notch clicks only into legal detents; confirm and the notch engraves the wedge.

**From:** Enigma (39), Jefferson disk (40), safe manipulation and lock-picking binds (41), Patterning's concentric rings (33),
Mac Gerdts rondels (37), Netrunner's breaker-fits-ICE (3).

**Flanks.** Left: the cylinder seen edge-on; the top five disks are the hand (cost as notches cut in the edge, name, type
word); the remaining stack is STACK (draw); spent disks drop to SPENT. Right: the KEY SHEET (plan as rotor settings, the spin
schedule, armed list), TURN KEY (END TURN).

**One play.** Press 3: the BREACH ring appears round the rim with detent ticks (cyan = legal, dim red = binds). Aim with the
mouse angle, Q/E or Tab: the notch walks wedge to wedge; a bind says why ("binds: not next to yours"). Confirm: click, the
ring locks and the wedge takes the stamp. NUDGE has no target: it steps the hub ring +1 / -1, which is exactly a rotor step.

**Style.** Keeps the three layers; the ring is runner pink line work, the detents are cyan glass.

**Why native.** It is the only concept whose action has **the wheel's own shape**; aiming by turning makes the corp's spin and
your play one gesture.

**Risks.** The ring sits where the pointers and the rim are, so it fights the pointers for space. Turning to aim is slower
than clicking; click-to-snap must also work. It can drift toward the rejected Platter Deck (hardware) if drawn as metal: keep
it ink and glass. WORM (three targets) needs three notches. **Effort.** M.

### 4. FOOTPRINT (text only)
**Pitch.** Each action is drawn as its target shape, like a key's bitting: a short arc of 12 ticks showing which wedges it
touches relative to yours (BREACH: one tick next to a pink tick; WORM: three corp ticks; GUARD: one pink tick; NUDGE: the
hub). Drag the footprint round the wheel; it snaps only where it fits.
**From:** key bitting (42), Gloomhaven templates (38), Dicey Dungeons slots (36), Netrunner breakers (3), Into the Breach
templates (32).
**Flanks:** the key ring of five footprints on the left (cost, type word, footprint); corp plan as its own footprints on the
right (the plan step "both sides of CORE" drawn as a shape too).
**Why native / risks:** makes the target rule visible at a glance and illegal moves impossible; but it is abstract, and
rules that depend on state ("weakest segment") have no fixed shape. **Effort:** M.

### 5. DEFACE (text only)
**Pitch.** Hacking as defacement. Actions are cut stencils in the runner's linocut style; hold one over a wedge and the cut-out
shows the result; confirm and it sprays the pink overprint. Lasting effects stay as tags.
**From:** web defacement (43), stencil graffiti and zines (44), Hackers (20), Edgerunners line art (22), Exapunks zines (5).
**Flanks:** a pasted wall of stencils left (hand; draw = the uncut roll, discard = peeled posters, exhaust = burnt); the corp's
clean compliance board right.
**Why native / risks:** the closest fit to the locked style (punk print versus enamel is already the fight), but it reads as
street art more than netrunning, and needs the cyan system layer to frame it as a payload. **Effort:** M.

## Comparison
| | 1 Packet Ladder | 2 Splice | 3 Rotor | 4 Footprint | 5 Deface |
|---|---|---|---|---|---|
| Netrun read | strong (real tool) | strong (signal) | good (cipher) | fair | fair (hacktivist) |
| Native to the wheel | via arrows | via rim band | best (its own shape) | good | good |
| Shares the B-088 grammar | **yes, identical** | partly | no | partly | no |
| Uses both flanks for meaning | **yes (two hosts)** | yes (channels / waterfall) | partly (cylinder / sheet) | partly | partly |
| Locked style | keeps | bends (more system) | keeps | keeps | keeps (leans punk) |
| Readability risk | low-medium (arrow clutter) | medium (new glyphs) | medium (ring vs pointers) | medium (abstract) | low |
| Learn cost | low | medium | low-medium | medium | low |
| Effort | S-M | M | M | M | M |

## Recommendation: 1, PACKET LADDER
1. It answers the critique at the root: the action, the forecast and the replay become **one language** (numbered packets
   between two hosts), so nothing on screen reads as a card being played.
2. It turns the wasted flanks into the two parties of the fight, in time order, which is what a hacker's tools actually show.
3. It keeps the three locked layers and the approved B-088 arrows, and it is the cheapest in Godot.

Borrow from the others:
- From **Splice**, the type-word waveform as a small glyph on each packet's flag field, and on lasting effects on the wedge.
- From **Rotor**, NUDGE as a hub step (+1 / -1 arrows on the hub), and Tab to walk legal wedges with a "binds" reason on
  illegal ones.

If the designer wants the boldest break, paper-test **Splice** next; if they want the most wheel-native feel, **Rotor**.

## Open questions for the designer
1. Is a packet header strip (no card art) acceptable for the hand, or must each action keep an illustration?
2. Take the network words (OUTBOX, QUEUED / SENT / DROPPED, SEND), or keep DRAW / DISCARD / END TURN?
3. Should the corp's plan arrows leave the right lifeline at rest (always on), or only when a wedge is hovered (B-088 now)?
4. For Splice: is a fourth visual vocabulary (waveforms per type word) worth learning?

## Files
- `insp_1_packet_ladder.png`, `insp_2_splice.png`, `insp_3_rotor.png`: 1920x1080 wireframes (flat blocks; yellow text is
  annotation; type colours are placeholders for the locked type-plate colours).
- `inspiration_sheet.jpg`: the three wireframes plus the ranking.
- Source: `D:/rc_scratch/takeover/inspiration/insp_wireframes.py` (`python insp_wireframes.py`; imports the helpers in
  `D:/rc_scratch/takeover/alternatives/alt_wireframes.py`).
- Known wireframe limits: the Rotor ring crosses the pointers; arrows are hand-placed, not auto-routed.
