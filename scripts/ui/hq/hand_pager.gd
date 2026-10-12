class_name HandPager
extends RefCounted
## M14 12Q-HQ (QA matrix L30, L53): the HQ hand pages instead of running past its box. A hand
## (the CREW polaroids, the MARKET's recruit cards, boost stickers and Profile unlock columns) is
## a row of units, plain or in captioned groups (a market group: a VBox with its `Caption` and
## its `Items` row). When the row is wider than the hand's box, the units are dealt into pages in
## order, each as wide as the box less the MORE tab; the tab (MORE, BACK on the last page) turns
## them. Nothing is clipped or scaled: the text stays the player's size, and every offer and
## operative is one press away. A group's caption shows on every page it has units on. A unit with the GLUE meta (the queued boosts line, a RECALL chip)
## stays on its neighbour's page. `split` is pure (tests); `apply` is the view glue.

## The meta on a unit that stays on the page of the unit before it.
const GLUE := &"hand_page_glue"
## The tab's name in the hand row.
const TAB_NAME := "HandMore"


## Deals units of `widths` (px, in order) into pages no wider than `room`; `groups[i]` is the
## unit's group (-1 for a plain unit), `captions[g]` the group's caption width, `item_sep` the
## gap between a group's units and `block_sep` the gap between the row's blocks (groups and
## plain units); `glue[i]` keeps unit i on unit i - 1's page. Returns each unit's page (0..).
## A unit wider than `room` alone takes a page of its own.
static func split(widths: Array[float], groups: Array[int], captions: Dictionary, item_sep: float, block_sep: float,
		glue: Array[bool], room: float) -> Array[int]:
	var out: Array[int] = []
	var page := 0
	var on_page: Array[int] = []
	for i in widths.size():
		var glued := i > 0 and i < glue.size() and glue[i]
		if not glued and not on_page.is_empty():
			var trial := on_page.duplicate()
			# The unit and every unit glued after it go together.
			trial.append(i)
			var j := i + 1
			while j < widths.size() and j < glue.size() and glue[j]:
				trial.append(j)
				j += 1
			if page_width(trial, widths, groups, captions, item_sep, block_sep) > room + 0.5:
				page += 1
				on_page.clear()
		on_page.append(i)
		out.append(page)
	return out


## The width of a page holding units `idx` (in order): its blocks side by side, a group as wide
## as its caption or its units, whichever is wider.
static func page_width(idx: Array, widths: Array[float], groups: Array[int], captions: Dictionary, item_sep: float,
		block_sep: float) -> float:
	var total := 0.0
	var blocks := 0
	var k := 0
	while k < idx.size():
		var g: int = groups[idx[k]]
		var w: float = widths[idx[k]]
		k += 1
		if g >= 0:
			while k < idx.size() and groups[idx[k]] == g:
				w += item_sep + widths[idx[k]]
				k += 1
			w = maxf(w, float(captions.get(g, 0.0)))
		total += w
		blocks += 1
	return total + block_sep * maxi(blocks - 1, 0)


## Pages hand row `cards` into `room` px with `tab` (a MenuChip: the row's last child, or beside the
## row) turning them; shows page `page` (clamped) and returns {pages, page, changed}. The tab shows
## only when the row pages; its word is MORE, BACK on the last page.
static func apply(cards: HBoxContainer, room: float, page: int, tab: MenuChip, more_word: String, back_word: String) -> Dictionary:
	var units: Array[Control] = []
	var holders: Array[Control] = []  # each unit's group block (null for a plain unit)
	var widths: Array[float] = []
	var groups: Array[int] = []
	var glue: Array[bool] = []
	var captions := {}
	var item_sep := 0.0
	var g := 0
	for k in cards.get_children():
		var block := k as Control
		if block == null or block == tab:
			continue
		var items := block.get_node_or_null("Items") as Container
		if items != null:
			item_sep = float(items.get_theme_constant("separation"))
			var cap := block.get_node_or_null("Caption") as Control
			captions[g] = cap.get_combined_minimum_size().x if cap != null else 0.0
			for u in items.get_children():
				if u is Control:
					units.append(u)
					holders.append(block)
					widths.append((u as Control).get_combined_minimum_size().x)
					groups.append(g)
					glue.append(bool((u as Control).get_meta(GLUE, false)))
			g += 1
		else:
			units.append(block)
			holders.append(null)
			widths.append(block.get_combined_minimum_size().x)
			groups.append(-1)
			glue.append(bool(block.get_meta(GLUE, false)))
	var block_sep := float(cards.get_theme_constant("separation"))
	var pages_of := split(widths, groups, captions, item_sep, block_sep, glue, room)
	var n: int = (int(pages_of.max()) + 1) if not pages_of.is_empty() else 1
	if n > 1 and tab != null and tab.get_parent() == cards:
		# A tab in the row takes its room at the row's end on every page (one beside the row, none).
		pages_of = split(widths, groups, captions, item_sep, block_sep, glue, room - block_sep - tab.get_combined_minimum_size().x)
		n = int(pages_of.max()) + 1
	var p := clampi(page, 0, n - 1)
	var changed := false
	var shown_groups := {}
	for i in units.size():
		var on := pages_of[i] == p
		if units[i].visible != on:
			units[i].visible = on
			changed = true
		if holders[i] != null:
			shown_groups[holders[i]] = bool(shown_groups.get(holders[i], false)) or on
	for h: Control in shown_groups:
		if h.visible != bool(shown_groups[h]):
			h.visible = bool(shown_groups[h])
			changed = true
	if tab != null:
		var paged := n > 1
		if tab.visible != paged:
			tab.visible = paged
			changed = true
		var word := back_word if p >= n - 1 else more_word
		if paged and tab.text != word:
			tab.text = word
			tab.refit()
	return {"pages": n, "page": p, "changed": changed}
