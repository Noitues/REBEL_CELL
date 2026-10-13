# PT-002a — designer feedback (verbatim, 2026-10-13)

```
PLAYTEST: PT-002a
STATUS: PASS | FAIL | PARTIAL
STEPS: 6 FAIL, 9 PARTIAL (unsure of "STEP N:"), 11 PARTIAL (See notes below), 12 FAIL (what is the enemy precision tag?), 13 PARTIAL (text reduction works, but ESC key press crashes game, see below)
LOGS: 
 1. Error: E 1:20:02:067   SettingsPanel._unhandled_input: Cannot call method 'set_input_as_handled' on a null value.
  <GDScript Source>settings_panel.gd:572 @ SettingsPanel._unhandled_input()
  <Stack Trace> settings_panel.gd:572 @ _unhandled_input()
      a. Occurred when in options menu and hit ESC key
NOTES: 
 - General:
   1. We show the controller buttons and keybinds always.  I would prefer it only shows if that input method is chosen, otherwise we show the mouse/keyboard options only.  And if we are gamepad, then we supress the mouse/keyboard options.  
   2. Along the same lines, the gamepad options and mouse/keyboard optiosn should be the same just "[ESC]" vs "[B]", not whole separate buttons and looks
   3. Grease Pen random line glitch notches look bad.  We can use those notches but need to make them not just gray squares but rather a smear texture with some alpha transparency.  Needs to look more blended
   4. No Menu button, recommend we put to the top left to the left of heat widget
 - Tutorial:
   1. Centre to Center
   2. page 7/7 says next when button says FINISH
   3. All animations for SEND IT seem to be skipped so action happens immediately
   4. Similarly, winning the tutorial combat skips straight to continue
 - Main Menu:
   1. QUIT:
      a. none of the quit menu buttons are clickable or interactable
      b. keyboard ESC brought me back to main menu, A did not work to quit and CONTINUE had not keybind so not sure what to use there
      c. for all menuing clicking away from the menu should close the menu (not dialog boxes or events or gameplay items)
   2. BREACH and "> CONTINUE" buttons do not animate like the SIMULATE OVERTHROW TUTORIAL and NEW CAMPAIGN buttons do
   3. Choosing New Campaign just sort of hung for a second before bringing up the new campaign screen.  We should at least add a loading bar overlay or some indication that we are working int he background
 - COMBAT:
   1. Winning the combat showed the loot button, but before I could click it, just on mouseover, the loot sheet window popped up
   2. Inner ring is near impossible to read
   3. CONTINUE: No sticker fold appears at all
   4. SKIP: Appears to have ">>" on the S of the sticker
   5. Loot screen had the HARDENED firmware, and the tooltip did not tell us what ENCRYPTED means.
   6. Loot screen, when hovering the current slice options, we should explain what each slice does and what the firmware installed there does
   7. Freeze doesn't work on the player spinner, but it should
   8. The bottom part of the loot reward screen is cut off.  Can only see top half of SKIP, CONTINUE, Deck buttons.
   9. Unsure, but if I hit skip in combat rewards I think it is skipping ALL reward options, not just the initial card selection.  Likely we should have a single rewards screen that shows all the reward types we gain (like slay the spire) and clicking each brings up the reward options for that reward.
   10. In compliance officer fight, starts showing the medical building in the center background, then hovering the enemy wheel causes background to chagne to the city.
   11. Hovering enemy nudge buttons does not show preview
 - NETRUN:
   1. Zooming out via mouse wheel or panning the map, but then hovering the map key/legend then un-hovering it causes an automatic re-zoom in and snap to current location.  It should maintain the zoom level and pan position
   2. Hovering the map legend doesn't show all the map nodes as I want it to.  Actually nothing seems to happen on hovering it
   3. The map nodes and the route is quite difficult to understand intuitively.  I think we need to not have the nodes draw off the route paths (i.e. in the buildings) until we hover over that specific node, then we indicate the node is selected but then animate the node moving along the off-route path to the true location in the building we are targetting.  De-hovering would de animate the off-route node and path back to the on-route node.
   4. GRID VIEW: 
     a. Doesn't show what is the active netrun path and target node
     b. Why do we have options to choose the next netrun node in the grid view?  Remove this.  Netrun route view is the only place to choose that.
 - Event:
   1. We start selected to option 1 and that sticker shows bigger and wider yellow band, but using arrow keys to change focus or mouseover's does not change this indication at all
   2. Scrolling over the icons to the right of the sticker should give the tooltip similar to the tooltip when hovering the sticker
   3. Nothing tells you what the Daemon reward will be...suggest we change the tooltip to include the daemon tooltip, and change the right icon to the daemon's icon and have the daemon's tooltip.
 - HQ:
   1. Market number underneath for the schematic count is redundant with schematics showing on top bar.  Remove the number.  Similar for the CREW 2/2 number, remove it.
   2. CREW -> Select BREAKER 1 (completed a netrun so have daemons and cards) -> VIEW LOADOUT -> NEXT OPERATIVE -> CLOSE: BREAKER 1 is selected on the polaroids at the bottom, but the top bar shows the 0 daemons next to the loadout like its selected on BREAKER 2
 - Raid Setup:
   1. Dropping a defence card into a node uses the card, but their is no indication the node changed visually, only in the "> YOUR NETWORK" window
   2. START DEFENSE: Seem to skip all of the raid and just went straight to the Raid Report screen
   3. Raid Report screen:
     a. Grease pen is covering a bit too much of the words so not easy to read all the fields.  Recommend we add some more space between lines. 
     b. CELL HOLDS is a sticker, which makes me think I can click it.  Need to make it grease pen if it is not a button.
     c. remove all the current grease pen words, circles, and check marks.  Let's only have the CELL HOLDS now.
 - Text 2.0:
   1. Hovering cards in card rewards makes cards get clipped.  Likely reduce card size up on hover
```
