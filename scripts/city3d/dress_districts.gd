class_name DressDistricts
extends RefCounted
## NA-24: district languages and HQ-distance bands over the exporter's city (`city.json`: buildings with `terr`, `hq`, `parts`).
## The district of a plan point is the territory of the nearest building; its palette set resolves a dress palette id to a colour
## (`DressingConfigData.palettes`; sets named `placeholder_*` stand in until the art-pass district assets land). The HQ band is the
## distance to the nearest corporation HQ building (`DressingConfigData.hq_bands`). Pure: a function of the city only.

const SPRAWL := "sprawl"
## Cell edge (BU) of the nearest-building lookup.
const CELL := 24.0
const MAX_RING := 4

var _cells: Dictionary = {}
var _hqs: Array = []


func _init(city: Dictionary) -> void:
	for b: Dictionary in city["buildings"]:
		var x0 := INF
		var x1 := -INF
		var y0 := INF
		var y1 := -INF
		for pt: Dictionary in b["parts"]:
			for q: Array in pt["poly"]:
				x0 = minf(x0, float(q[0]))
				x1 = maxf(x1, float(q[0]))
				y0 = minf(y0, float(q[1]))
				y1 = maxf(y1, float(q[1]))
		var c := Vector2((x0 + x1) * 0.5, (y0 + y1) * 0.5)
		var terr: String = String(b["terr"]) if String(b["terr"]) != "" else SPRAWL
		var key := Vector2i(floori(c.x / CELL), floori(c.y / CELL))
		if not _cells.has(key):
			_cells[key] = []
		(_cells[key] as Array).append([c, terr])
		if bool(b["hq"]):
			_hqs.append(c)


## The territory (`sprawl` for the neutral city) of the nearest building to plan point (`x`, `y`).
func terr_at(x: float, y: float) -> String:
	var k := Vector2i(floori(x / CELL), floori(y / CELL))
	var best := INF
	var terr := SPRAWL
	for ring in MAX_RING:
		for i in range(k.x - ring, k.x + ring + 1):
			for j in range(k.y - ring, k.y + ring + 1):
				if maxi(absi(i - k.x), absi(j - k.y)) != ring or not _cells.has(Vector2i(i, j)):
					continue
				for e: Array in _cells[Vector2i(i, j)]:
					var d: float = (e[0] as Vector2).distance_squared_to(Vector2(x, y))
					if d < best or (d == best and IdSort.less(e[1], terr)):
						best = d
						terr = e[1]
		if best < INF:
			break
	return terr


## The palette set id of territory `terr`.
static func set_of(terr: String) -> String:
	var d: Dictionary = DressingConfigData.shipped().districts
	return String(d[terr]["palette"]) if d.has(terr) else String(d[SPRAWL]["palette"])


## The colour of palette id `id` in the district of plan point (`x`, `y`): the district set, else the shared `common` ids.
func color(id: String, x: float, y: float) -> Color:
	return color_in(id, set_of(terr_at(x, y)))


## The colour of palette id `id` in palette set `set_id`.
static func color_in(id: String, set_id: String) -> Color:
	var pal: Dictionary = DressingConfigData.shipped().palettes
	var src: Dictionary = pal[set_id] if (pal.has(set_id) and (pal[set_id] as Dictionary).has(id)) else pal["common"]
	var c: Array = src[id]
	return Color(float(c[0]), float(c[1]), float(c[2]))


## Distance (BU) of plan point (`x`, `y`) from the nearest HQ building (INF when the city has none).
func hq_dist(x: float, y: float) -> float:
	var best := INF
	for h: Vector2 in _hqs:
		best = minf(best, h.distance_to(Vector2(x, y)))
	return best


## The HQ band (`{max_bu, sign_mul, emit_mul, plume_mul}`) of plan point (`x`, `y`).
func band_at(x: float, y: float) -> Dictionary:
	var d := hq_dist(x, y)
	var bands: Array = DressingConfigData.shipped().hq_bands
	for b: Dictionary in bands:
		if d <= float(b["max_bu"]):
			return b
	return bands[bands.size() - 1]


## A deterministic 0..1 number of (`cls`, `key`): the FNV-1a 64 of the text through one splitmix64 step. No stream: a pure hash.
static func hash01(cls: String, key: String) -> float:
	var h: int = ArtSeed.fnv1a64((cls + "|" + key).to_utf8_buffer())
	var r: Array[int] = ArtSeed.splitmix64(h)
	return ArtSeed.uniform(r[1])
