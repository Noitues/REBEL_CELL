# Round 8: pitch round (one paragraph each, scored before anything is built)

This round exists because six rounds of placement-puzzle raids all scored 31–36, whatever mechanics we tried. These
pitches change what a raid **is**. Each one says:
- the loop;
- the decision;
- what plays hands-off (execution stays zero-input);
- what it reuses from REBEL_CELL;
- the rulings it would challenge (all **designer decisions**).

Pitches 1 and 2 come from the designer (2026-10-22), sharpened here.

---

**1. RING SIEGE: the raid is a wheel (designer).**
- **The board.** Your HQ is the hub of a raid wheel. Concentric rings around it are defense layers, outer to inner.
  Each ring has the locked anatomy (30 ticks, 6 slices of 5), and you stock its slices from your run: SHIM and
  OVERFLOW damage, DEFRAG and SANDBOX absorb, DETOUR shunts the threat to the next spoke, NULL is a hole.
- **The threats.** Each corp entry is a **spoke**, a fixed path into HQ, and its threats queue on the rim at that
  spoke's pointer.
- **The playout (hands-off).** Every tick the rings turn at their own speeds and directions, like inner rings today.
  A threat on a ring is struck by whatever slice is under its spoke. When it breaks that slice, it bores inward to the
  next ring. The wheel spins until the threats are gone or one reaches the hub.
- **The decision.** What to stock on which ring, and each ring's speed and phase: the core combat's timing literacy
  turned into a siege. The forecast is exact, because it is the game's own tick math: "spoke 2 meets OVERFLOW on
  ring 1 at tick 7".
- **Reuses:** wheel anatomy, slice types, pointers, inner rings, the tick resolution math.
- **Challenges:** the City Grid raid map is replaced by the wheel for the fight (the Grid stays the campaign
  map). D26 pacing becomes ticks.

**2. PURSUIT: the corp fleet hunts the cell (designer; FTL's rebel fleet).**
- **The front.** The raid is a **front**, not an event. Solace's net advances across the City Grid and the netrun map
  each netrun, at a speed set by your Heat (cobalt fill crawling node by node, always on screen).
- **The decision is your route.** Run toward high-value targets with the front at your heels, or detour to "cover
  tracks" (a Heat sink) and buy distance. Nodes the front swallows are lost or become corp ground. If it catches your
  current node, you fight an ambush wheel combat there. If it reaches HQ while you are home, the HQ siege resolves
  (with any defense model).
- **The goal.** Hack your way to the corp's core before the front closes. That is the game's premise: hackers on the
  run, striking back.
- **Hands-off part:** the front's advance is automatic and telegraphed each netrun, FTL-style.
- **Reuses:** the netrun map, Heat, the City Grid, wheel combat.
- **Challenges:** raids at fixed Heat thresholds (GDD 4.4); D27 and D28.

**3. RING PURSUIT (1 + 2 merged).**
- **The campaign layer** is pursuit: the front crawls toward you across the map.
- **The fight** is a ring siege. When the front reaches HQ, the threats it gathered on the way (each node it swallowed
  adds one) come down the spokes of your raid wheel.
- **The decision:** where you lead the front (which threats it collects, which spokes they arrive on) and how you stock
  the rings.
- **Hands-off:** the siege.
- **Challenges:** as 1 and 2.

**4. MIRROR NETRUN: the corp runs YOUR network.**
- **The loop.** The raid is the corp doing to you what you do to them. Your network becomes a netrun map, and a corp
  "runner" (a boss wheel) walks it node by node. At each node it fights the defenses you seeded there, as a short
  auto-resolved wheel fight.
- **The decision:** which encounters to plant where, and where to leave bait (it takes loot nodes first).
- **Hands-off:** the runner's path and every fight.
- **Reuses:** the netrun structure, wheel combat, enemy wheels.
- **Challenges:** placement-on-grid raids.

**5. DECK FORTRESS: defense is part of your deck.**
- **The deck.** Defense pieces are cards in your run deck. They take a draw slot in netrun combat (they are dead weight
  there) but form your fortress in a raid.
- **The raid.** It deals your deck onto your nodes in deck order, and you choose the order (a pre-raid "stack the
  deck" step).
- **The decision:** building the deck becomes building the fortress, and every reward pick is a trade between offense
  now and safety later.
- **Hands-off:** the deal and the resolution.
- **Reuses:** cards, reward picks.
- **Challenges:** the separate Armory.

**6. THE OFFER: negotiation, no placement.**
- **The demand.** When the raid lands, Solace presents a demand: three priced offers drawn from your state, such as
  "give us the Vault", "hand over 20 Schematics", or "let us tag your operative (DOSE for 2 netruns)".
- **The decision.** Refuse and the raid resolves against your standing defenses (any model). Pay and it is averted. The
  whole decision is what you can afford to lose, given the run you are building.
- **Hands-off:** the refusal's raid.
- **Reuses:** Stakes' node jobs, statuses.
- **Challenges:** D28 (a paid-off raid has a third outcome).

**7. COUNTERSTRIKE: defend AND hit back.**
- **The window.** A raid opens a window: while the corp's units are inside your network, its core is exposed.
- **The decision:** split your crew and pieces between holding nodes and a counter-hack of the corp's core, a parallel
  auto-run on a corp wheel. The result is a net position: what you lost against what you took.
- **The incentive.** A strong counterstrike can break the next raid or win corp territory, so defending perfectly is
  not always right.
- **Hands-off:** both sides at once, split screen.
- **Reuses:** corp wheels, the crew.
- **Challenges:** D27; the raid as pure defense.

**8. HONEYPOT FARM: raids are harvest.**
- **The lure.** You can deliberately raise a raid's size (a bigger lure) to farm salvage and corp tech from it.
  Honeypot nodes (content: honeypot_node) let threats in on purpose and trap them.
- **The decision:** how much threat you can digest. Greed against safety, Balatro-style risk scaling.
- **Hands-off:** the raid.
- **Reuses:** honeypot_node, salvage.
- **Challenges:** Heat as pure punishment.

**9. SIGNAL WAR: territory, not damage.**
- **The pressure.** Raids push corp influence across the City Grid like Go stones. Your nodes and pieces project
  influence, and so do the corp's.
- **The resolution.** Influence flows tick by tick, and a node flips when the corp's influence there exceeds yours.
- **The decision:** where to project, where to concede, and where to cut the corp's lines.
- **Hands-off:** the flow.
- **Reuses:** the City Grid.
- **Challenges:** HP-based integrity.

**10. THE RACK: an inventory auto-battler (Backpack Battles).**
- **The rack.** Your HQ is a server rack, a small grid you fill with modules (firewalls, ICE, turrets, cooling) of
  different shapes. Adjacency matters: cooling next to a turret means it fires faster; ICE next to a firewall chains a
  freeze.
- **The raid.** It is an auto-battle of your rack against the corp's rack, both visible beforehand.
- **The decision:** spatial packing plus synergy; the rack persists and grows.
- **Hands-off:** the battle.
- **Reuses:** firmware and daemons as modules.
- **Challenges:** the City Grid raid.

**11. GHOST PROTOCOL: stealth, not defense.**
- **The search.** Heat is how visible you are. A raid is a corp search sweep across your network, with deterministic
  sweep patterns shown in advance.
- **The decision:** hide assets in ghost nodes, plant false signatures (decoys), and go dark on nodes. Whatever the
  sweep finds is lost.
- **Hands-off:** watching the sweep pass, tense near-misses included.
- **Reuses:** decoys, Heat.
- **Challenges:** combat-based raids.

**12. BASTION (H7, the round-7 baseline).**
- **The rules.** The persistent fortress with node jobs: survivors rejoin, the corp adapts to your top piece, TAKEN
  nodes become footholds.
- **Measured.** Planning the leg beats one-raid-at-a-time play.
- **Status.** A playable Godot lab is being built now.
