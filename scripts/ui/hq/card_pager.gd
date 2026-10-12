class_name CardPager
extends RefCounted
## M14 12Q-HQ (QA matrix L31, L32, L33, L34, L43; ART-5 acceptance): the HQ's selected card (the
## Site's decrypted file, a node's terminal, the CLAIM terminal with its build tiles) and the Heat
## terminal page their rows instead of being cut by their room. The card keeps its header (and
## what sits under its rows) on every page; its body rows (TYPE, LINK, IF CLEARED, INTEGRITY,
## DEFENCES, ... the actions) are dealt into pages in order, each page no taller than the room; a
## MORE tab (BACK on the last page) turns them. The text stays the player's size: never clipped,
## never scaled. A row with the WITH_NEXT meta (a caption over its tiles or its action) goes with
## the row after it; an empty row rides on any page. A row taller than a page by itself is dealt
## in its own parts when it has them: a wrapped Label by whole lines (`lines_skipped` /
## `max_lines_visible`: the Exploit Site's explanation at 2.0), a GridContainer by its rows of
## cells (the CLAIM terminal's build tiles), a FlowContainer by its lines (IF CLEARED's badges at
## 2.0), so each line, tile and badge shows whole on one page.
## `split` and `units` are pure (tests); `apply` is the view glue (it measures the rows once per
## width and text scale, all shown, then pages).

## The meta on a body row that stays on the page of the row after it.
const WITH_NEXT := &"card_page_with_next"
## The card's metas: the measure's key, its rows' heights and parts, the header's share, the rows
## the builder hid itself (never shown by the pager).
const META_KEY := &"card_page_key"
const META_HEIGHTS := &"card_page_heights"
const META_PARTS := &"card_page_parts"
const META_HEAD := &"card_page_head"
const META_HIDDEN := &"card_page_hidden"
## A paged Label's own clip and least height (restored when it shows whole).
const META_LABEL := &"card_page_label"
## A paged flow row's items' lines as measured.
const META_FLOW_LINES := &"card_page_flow_lines"
## The card's least width with every row shown (its column keeps it on every page).
const META_WIDTH := &"card_page_width"


## Deals body rows of `heights` (px, in order) into pages whose rows take at most `room` px with
## `sep` between rows; `with_next[i]` keeps row i on row i + 1's page; an empty row (height 0)
## costs nothing. Returns each row's page. A row taller than `room` alone takes a page of its own.
static func split(heights: Array[float], with_next: Array[bool], sep: float, room: float) -> Array[int]:
	var out: Array[int] = []
	var page := 0
	var used := -1.0  # < 0: the page is empty
	var i := 0
	while i < heights.size():
		# Row i and every row it holds on to.
		var j := i
		var h := heights[i]
		while j < with_next.size() and with_next[j] and j + 1 < heights.size():
			j += 1
			h += (sep if heights[j] > 0.5 else 0.0) + heights[j]
		if h > 0.5:
			var need := h if used < 0.0 else used + sep + h
			if used >= 0.0 and need > room + 0.5:
				page += 1
				need = h
			used = need
		for k in range(i, j + 1):
			out.append(page)
		i = j + 1
	return out


## The units `split` deals for rows of `heights` with `parts[i]` (each row's parts' heights, in
## order; one part for a row that has none): a row that cannot stand on a page with what holds on
## to it (taller than `room`) and has more than one part is dealt part by part (a caption holding
## on to it goes with its first part). Returns {"heights", "with_next", "row" (each unit's row),
## "part" (its first part in its row)}.
static func units(heights: Array[float], parts: Array, with_next: Array[bool], sep: float, room: float) -> Dictionary:
	var uh: Array[float] = []
	var un: Array[bool] = []
	var ur: Array[int] = []
	var up: Array[int] = []
	for i in heights.size():
		var ps: Array = parts[i] if i < parts.size() else []
		# What holds on to this row before it (a caption) shares its page.
		var lead := 0.0
		var k := i - 1
		while k >= 0 and with_next[k]:
			lead += heights[k] + sep
			k -= 1
		if heights[i] + lead > room + 0.5 and ps.size() > 1:
			for p in ps.size():
				uh.append(float(ps[p]))
				un.append(false)
				ur.append(i)
				up.append(p)
			un[un.size() - 1] = with_next[i]
		else:
			uh.append(heights[i])
			un.append(with_next[i])
			ur.append(i)
			up.append(0)
	return {"heights": uh, "with_next": un, "row": ur, "part": up}


## Pages `card` (a TerminalWindow or a RaidHolo: anything with a `body` VBoxContainer) at
## `width` into `room` px of height, page `page` shown (clamped), with `tab` turning them; `tab_h`
## is the room the tab takes when shown (0 when it stands in room the card keeps anyway);
## `rows_box` pages that box's rows instead of the body's (the Heat terminal's rows over its
## SCRUB). Returns {pages, page, changed}.
static func apply(card: Control, width: float, room: float, page: int, tab: MenuChip, tab_h: float,
		more_word: String, back_word: String, rows_box: VBoxContainer = null) -> Dictionary:
	var body := rows_box if rows_box != null else (card.get("body") as VBoxContainer if card != null else null)
	if body == null:
		return {"pages": 1, "page": 0, "changed": false}
	var rows: Array[Control] = []
	for k in body.get_children():
		if k is Control:
			rows.append(k)
	var key := "%d|%.3f|%d" % [roundi(width), Settings.text_scale, rows.size()]
	if card.get_meta(META_KEY, "") != key or _stale(card, body, rows):
		_measure(card, body, rows, width, key)
	var heights: Array[float] = []
	heights.assign(card.get_meta(META_HEIGHTS, []))
	var parts: Array = card.get_meta(META_PARTS, [])
	var hidden: Array = card.get_meta(META_HIDDEN, [])
	var with_next: Array[bool] = []
	for i in rows.size():
		if hidden.has(rows[i]):
			heights[i] = 0.0  # the builder hid it: it counts for nothing
		with_next.append(bool(rows[i].get_meta(WITH_NEXT, false)) and i + 1 < rows.size())
	var sep := float(body.get_theme_constant("separation"))
	var head: float = card.get_meta(META_HEAD, 0.0)
	var u := units(heights, parts, with_next, sep, room - head)
	var pages_of := split(u["heights"], u["with_next"], sep, room - head)
	var n: int = (int(pages_of.max()) + 1) if not pages_of.is_empty() else 1
	if n > 1 and tab_h > 0.0:
		u = units(heights, parts, with_next, sep, room - head - tab_h)
		pages_of = split(u["heights"], u["with_next"], sep, room - head - tab_h)
		n = int(pages_of.max()) + 1
	var p := clampi(page, 0, n - 1)
	var unit_rows: Array[int] = u["row"]
	var unit_parts: Array[int] = u["part"]
	# Each row's parts on page p (a row dealt whole has the one part 0).
	var on_page := {}
	var dealt := {}
	for k in unit_rows.size():
		var r := unit_rows[k]
		dealt[r] = int(dealt.get(r, 0)) + 1
		if pages_of[k] == p:
			if not on_page.has(r):
				on_page[r] = []
			(on_page[r] as Array).append(unit_parts[k])
	var changed := false
	for i in rows.size():
		var on := on_page.has(i) and not hidden.has(rows[i])
		if rows[i].visible != on:
			rows[i].visible = on
			changed = true
		var shown_parts: Array = on_page.get(i, [])
		if _show_parts(rows[i], shown_parts if int(dealt.get(i, 1)) > 1 else [], parts[i] if i < parts.size() else []):
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


## Shows only parts `shown` of `row` (empty: all of it) of heights `heights`: a Label's lines, a
## GridContainer's rows of cells. Returns true when something changed.
static func _show_parts(row: Control, shown: Array, heights: Array = []) -> bool:
	var changed := false
	if row is Label:
		var l := row as Label
		var skip := int(shown.min()) if not shown.is_empty() else 0
		var most := shown.size() if not shown.is_empty() else -1
		if not l.has_meta(META_LABEL):
			l.set_meta(META_LABEL, [l.clip_text, l.custom_minimum_size.y])
		var own: Array = l.get_meta(META_LABEL)
		# A wrapped label keeps its whole height whatever lines it draws: a part of it is as tall
		# as its lines (and draws only them: the others are on the other pages).
		var tall := float(own[1])
		if not shown.is_empty():
			tall = 0.0
			for p in shown:
				tall += float(heights[int(p)]) if int(p) < heights.size() else 0.0
		var clip := bool(own[0]) or not shown.is_empty()
		if l.lines_skipped != skip or l.max_lines_visible != most or l.clip_text != clip or not is_equal_approx(l.custom_minimum_size.y, tall):
			l.lines_skipped = skip
			l.max_lines_visible = most
			l.clip_text = clip
			l.custom_minimum_size.y = tall
			changed = true
	elif row is GridContainer:
		var g := row as GridContainer
		var cols := maxi(g.columns, 1)
		var i := 0
		for c in g.get_children():
			if not c is Control:
				continue
			var on := shown.is_empty() or shown.has(i / cols)
			if (c as Control).visible != on:
				(c as Control).visible = on
				changed = true
			i += 1
	elif row is FlowContainer:
		# Each item's line as measured (the items of a line shown together reflow onto it).
		var lines: Array = row.get_meta(META_FLOW_LINES, [])
		var i := 0
		for c in row.get_children():
			if not c is Control:
				continue
			var on := shown.is_empty() or (i < lines.size() and shown.has(int(lines[i])))
			if (c as Control).visible != on:
				(c as Control).visible = on
				changed = true
			i += 1
	return changed


## True when the last measure no longer holds: a shown row (whole) or the header is another
## height now (a label's words wrapped once it was in the tree, a frame after the measure).
static func _stale(card: Control, body: VBoxContainer, rows: Array[Control]) -> bool:
	var heights: Array = card.get_meta(META_HEIGHTS, [])
	if heights.size() != rows.size():
		return true
	var sum := 0.0
	var shown := 0
	for i in rows.size():
		var r := rows[i]
		if not r.visible:
			continue
		var h := r.get_combined_minimum_size().y
		sum += h
		shown += 1
		if not _partial(r) and absf(h - float(heights[i])) > 1.0:
			return true
	var head := card.get_combined_minimum_size().y - sum - float(body.get_theme_constant("separation")) * maxi(shown - 1, 0)
	return absf(head - float(card.get_meta(META_HEAD, 0.0))) > 1.0


## True when `r` shows only some of its parts now (a Label's lines, a grid's rows).
static func _partial(r: Control) -> bool:
	if r is Label:
		return (r as Label).max_lines_visible >= 0
	if r is GridContainer or r is FlowContainer:
		for c in r.get_children():
			if c is Control and not (c as Control).visible:
				return true
	return false


## Measures the card's rows at `width` with every row the builder showed shown, all of each (each
## row's height and parts, and what the header and frame take besides), keyed by `key`.
static func _measure(card: Control, body: VBoxContainer, rows: Array[Control], width: float, key: String) -> void:
	var hidden: Array = card.get_meta(META_HIDDEN, [])
	if not card.has_meta(META_HIDDEN):
		for r in rows:
			if not r.visible:
				hidden.append(r)
		card.set_meta(META_HIDDEN, hidden)
	for r in rows:
		r.visible = not hidden.has(r)
		_show_parts(r, [])
	var total := FitBuildBox.settle(card, width)
	var heights: Array[float] = []
	var parts: Array = []
	var sum := 0.0
	var shown := 0
	for r in rows:
		var h := r.get_combined_minimum_size().y if r.visible else 0.0
		heights.append(h)
		parts.append(_parts_of(r, h))
		if r.visible:
			sum += h
			shown += 1
	var sep := float(body.get_theme_constant("separation"))
	card.set_meta(META_KEY, key)
	card.set_meta(META_HEIGHTS, heights)
	card.set_meta(META_PARTS, parts)
	card.set_meta(META_HEAD, maxf(0.0, total - sum - sep * maxi(shown - 1, 0)))
	card.set_meta(META_WIDTH, card.get_combined_minimum_size().x)


## The least width `card` needs with every row shown (as measured; its own minimum before the
## first measure, when the builder shows them all): a page never narrows its column.
static func full_width(card: Control) -> float:
	if card == null:
		return 0.0
	return maxf(card.get_combined_minimum_size().x, float(card.get_meta(META_WIDTH, 0.0)))


## A measured row's parts' heights (adding up to `h`): a wrapped Label's lines, a GridContainer's
## rows of cells (each with the gap above it), else the row whole.
static func _parts_of(r: Control, h: float) -> Array[float]:
	var out: Array[float] = []
	if not r.visible or h <= 0.5:
		return out
	if r is Label and (r as Label).get_line_count() > 1:
		var n := (r as Label).get_line_count()
		var lh := floorf(h / n)
		for l in n:
			out.append(lh + (h - lh * n if l == 0 else 0.0))
	elif r is GridContainer:
		var g := r as GridContainer
		var cols := maxi(g.columns, 1)
		var gap := float(g.get_theme_constant("v_separation"))
		var row_h: Array[float] = []
		var i := 0
		for c in g.get_children():
			if c is Control:
				var gr := i / cols
				if gr >= row_h.size():
					row_h.append(0.0)
				row_h[gr] = maxf(row_h[gr], (c as Control).get_combined_minimum_size().y)
				i += 1
		for k in row_h.size():
			out.append(row_h[k] + (gap if k > 0 else 0.0))
	elif r is FlowContainer:
		# Its lines as laid out at the measure (items by their top), each with the gap above it.
		var gap := float(r.get_theme_constant("v_separation"))
		var tops: Array[float] = []
		var line_h: Array[float] = []
		var of_item: Array[int] = []
		for c in r.get_children():
			if not c is Control:
				continue
			var y := (c as Control).position.y
			var at := -1
			for k in tops.size():
				if absf(tops[k] - y) < 1.0:
					at = k
			if at < 0:
				tops.append(y)
				line_h.append(0.0)
				at = tops.size() - 1
			line_h[at] = maxf(line_h[at], (c as Control).get_combined_minimum_size().y)
			of_item.append(at)
		r.set_meta(META_FLOW_LINES, of_item)
		for k in line_h.size():
			out.append(line_h[k] + (gap if k > 0 else 0.0))
	if out.size() <= 1:
		out = [h] as Array[float]
	return out
