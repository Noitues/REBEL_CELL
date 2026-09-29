"""W10 colour-vision post filters for review packs (Pillow path).

The same maths as tools/visual_qa/cvd_filter.gdshader: greyscale (Rec. 709 luminance)
and deuteranopia (Machado, Oliveira and Fernandes 2009, severity 1.0), both in linear
light. Channels go through 12-bit linear lookup tables, so dark tones keep their detail.
"""

from __future__ import annotations

from PIL import Image

LIN_BITS = 4096
GREY = ((0.2126, 0.7152, 0.0722),) * 3
DEUTAN = (
    (0.367322, 0.860646, -0.227968),
    (0.280085, 0.672501, 0.047413),
    (-0.011820, 0.042940, 0.968881),
)
MATRICES = {"grey": GREY, "deutan": DEUTAN}


def _to_lin(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _to_srgb(v: float) -> float:
    v = min(max(v, 0.0), 1.0)
    return v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055


_LIN = [_to_lin(i / 255.0) for i in range(256)]
_SRGB = [round(_to_srgb(i / (LIN_BITS - 1)) * 255) for i in range(LIN_BITS)]


def apply(img: Image.Image, name: str) -> Image.Image:
    """Returns `img` (RGB) through the named filter ("none", "grey" or "deutan")."""
    img = img.convert("RGB")
    if name == "none":
        return img
    m = MATRICES[name]
    src = img.tobytes()
    out = bytearray(len(src))
    lin = _LIN
    srgb = _SRGB
    top = LIN_BITS - 1
    cache: dict[int, bytes] = {}
    for i in range(0, len(src), 3):
        key = src[i] << 16 | src[i + 1] << 8 | src[i + 2]
        px = cache.get(key)
        if px is None:
            r, g, b = lin[src[i]], lin[src[i + 1]], lin[src[i + 2]]
            vals = []
            for row in m:
                v = row[0] * r + row[1] * g + row[2] * b
                vals.append(srgb[min(max(int(v * top + 0.5), 0), top)])
            px = bytes(vals)
            cache[key] = px
        out[i:i + 3] = px
    return Image.frombytes("RGB", img.size, bytes(out))
