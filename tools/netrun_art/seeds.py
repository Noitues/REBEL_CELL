"""Art seeds for the NA-02 contract (C3): FNV-1a 64 art seed, splitmix64 draws, uniform.

Standard library only. Reads no gameplay RNG stream. Matches tools/netrun_art/fixtures/na02_vectors.json.
"""
import json
from typing import Iterator, Union

FNV_OFF = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
M64 = (1 << 64) - 1
SM_GAMMA = 0x9E3779B97F4A7C15

Key = Union[int, str]


def fnv1a64(data: bytes) -> int:
    """FNV-1a 64-bit hash of `data` as a u64."""
    h = FNV_OFF
    for b in data:
        h = ((h ^ b) * FNV_PRIME) & M64
    return h


def art_seed(layout_seed: Union[int, str], stream: str, *keys: Key) -> int:
    """u64 art seed for `stream` and `keys`.

    `layout_seed` is the u64 decimal string of the city header (or an int; a signed GDScript seed is taken
    as its two's-complement u64). Keys are int or str only; float, bool and other types raise TypeError.
    """
    for k in keys:
        if isinstance(k, (float, bool)) or not isinstance(k, (int, str)):
            raise TypeError("keys are int or str only")
    seed = int(layout_seed) & M64
    arr = [str(seed), "art/" + stream, *keys]
    return fnv1a64(json.dumps(arr, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def splitmix64(state: int) -> Iterator[int]:
    """Infinite generator of u64 splitmix64 draws seeded with `state`."""
    state &= M64
    while True:
        state = (state + SM_GAMMA) & M64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        yield z ^ (z >> 31)


def uniform(x: int) -> float:
    """Map a u64 draw to a float in [0, 1)."""
    return (x >> 11) * (2.0 ** -53)
