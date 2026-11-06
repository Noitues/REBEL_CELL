"""Colour-blind simulation (Machado, Oliveira, Fernandes 2009, severity 1.0, applied in linear RGB)."""
import numpy as np
from PIL import Image

DEUT = np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]])
TRIT = np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])


def lin(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)


def unlin(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055)


def sim(im, M):
    a = lin(np.asarray(im.convert('RGB'), np.float32) / 255)
    o = a @ M.T
    return Image.fromarray((unlin(o) * 255 + .5).astype(np.uint8))
