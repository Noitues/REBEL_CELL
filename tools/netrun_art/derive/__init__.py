"""derive: the derive_<run>.json producers. `game_partial` is what the game writes (NA02 Ruling O4); `derive.street` and
`hq.slots` fill the rest (version 2)."""
from typing import Any, Dict, Iterable, List

from .. import seeds
from ..io import u64_str

VERSION = 2
# Unkeyed art streams that get a scene-level seed in `art_seeds` (NA02_FIELDS section 7, Ruling O6)
UNKEYED_STREAMS: List[str] = [
    "scene", "cars", "sky", "ground_glow", "street_lanes", "beams", "plumes", "glows", "windows_flicker", "flicker", "glitch",
    "city_fill", "city.zoning", "city.build", "city.ring", "city.streaks", "city.beams", "city.sea", "city.landmark",
    "city.post", "downtown", "ring", "cycles", "variance", "terrain", "fauna.tethys"]
PER_CORP_STREAMS = ("landmark", "key_landmark")


def art_seeds(layout_seed: str, corps: Iterable[str] = ()) -> Dict[str, str]:
    """`{stream: "<u64>"}` for the unkeyed streams plus `landmark.<corp>` and `key_landmark.<corp>` base seeds."""
    names = list(UNKEYED_STREAMS) + [f"{p}.{c}" for c in sorted(corps) for p in PER_CORP_STREAMS]
    return {n: u64_str(seeds.art_seed(layout_seed, n)) for n in sorted(names)}


def game_partial(layout_seed: str, run: str, kind: str, corps: Iterable[str] = ()) -> Dict[str, Any]:
    """The partial derive file the game writes: `version`, `kind`, `layout_seed`, `run`, `art_seeds`."""
    return dict(version=1, kind=kind, layout_seed=str(layout_seed), run=run, art_seeds=art_seeds(layout_seed, corps))
