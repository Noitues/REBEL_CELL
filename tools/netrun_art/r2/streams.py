"""Art streams of the street r2 rules (art-pass `r2_rules.fnv64 / art_seed / rng`, spec 3.5): one Mersenne Twister stream per
(art seed, stream name, content ids). The key text is `json.dumps([seed, "art/<stream>", *keys])` with float keys rounded to 4
decimals, FNV-1a 64 of its UTF-8 bytes seeds `random.Random`. This is NOT the NA-02 splitmix stream of `netrun_art.seeds`: the
r2 rules reproduce the plate, which used these. The GDScript twin (`street_r2_rng.gd`) implements the same Mersenne Twister."""
import json
import random
from typing import Any

FNV_OFF = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
M64 = (1 << 64) - 1


def fnv64(s: str) -> int:
    """FNV-1a 64-bit of the UTF-8 bytes of `s`."""
    h = FNV_OFF
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * FNV_PRIME) & M64
    return h


def key_text(seed: Any, stream: str, *keys: Any) -> str:
    """The text that is hashed: float keys rounded to 4 decimals, Python json default separators."""
    return json.dumps([seed, "art/" + stream] + [round(k, 4) if isinstance(k, float) else k for k in keys])


def art_seed(seed: Any, stream: str, *keys: Any) -> int:
    """u64 art seed of a stream."""
    return fnv64(key_text(seed, stream, *keys))


def rng(seed: Any, stream: str, *keys: Any) -> random.Random:
    """The stream's generator."""
    return random.Random(art_seed(seed, stream, *keys))
