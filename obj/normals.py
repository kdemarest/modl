"""A library of normal-map generators: each one a model stopped using, kept for later (Ken,
2026-11-04: any time we stop using one, keep its code here; if only its parameters changed,
keep those). Each says where it was used, with what parameters, and why it was let go. A
generator returns heights (0 to 1, rows of pixels), which a family's painter scales to pixels
and turns into normals (hut.py's fill and write_normals)."""

import math

import numpy as np


def chamfer(inside, w, h):
    """How far in each pixel of inside (rows of booleans) is from its edge, in pixels (a chamfer
    distance: 1 across, 1.4 diagonally); 0 outside. Two sweeps, a row at a time in numpy: the
    row before's three neighbors, then along the row a running minimum (a pixel's left neighbor
    plus 1, as far as it reaches)."""
    far = np.where(np.array(inside, bool).reshape(h, w), 9e9, 0.0)
    at = np.arange(w, dtype=np.float64)
    for order in (1, -1):
        for j in (range(h) if order > 0 else range(h - 1, -1, -1)):
            row = far[j].copy()
            if 0 <= j - order < h:
                prev = far[j - order]
                row = np.minimum(row, prev + 1.0)
                side = np.full(w, np.inf)
                side[1:], diag = prev[:-1] + 1.4, np.full(w, np.inf)
                diag[:-1] = prev[1:] + 1.4
                row = np.minimum(row, np.minimum(side, diag))
            if order > 0:
                row = np.minimum.accumulate(row - at) + at
            else:
                row = (np.minimum.accumulate((row + at)[::-1]) - at[::-1])[::-1]
            far[j] = row
    return far


# ---------- pillowed brocade ----------
# The Hut's hammock bed, 2026-11-04 (Ken: make it pop, overdo it): HammockFabric.png turned along
# the bed, raised 4 px (brocadeRelief) at 768 px/m. Let go the same day for Sample Ghicha.jpg's
# weave (Ken: both for the detail texture and the normal map).
PILLOW = 8  # the pixels a raised shape takes to rise from its edge to its top


def raised(img, ground):
    """How high each pixel of a fabric (a modl.Image) stands (0 to 1), rows of the image: its
    pattern (where its color is far from ground's, an RGB 0 to 1) raised, each shape a pillow
    rounding up from its edge over PILLOW pixels, its lighter parts higher, so even a wide plain
    fill catches the light; softened over a pixel each way."""
    w, h, u = img.w, img.h, img.unit
    px = img.px
    m = [[min(1.0, math.sqrt(sum((px[(y * w + x) * 4 + q] * u - ground[q]) ** 2 for q in range(3))) / 0.25) for x in range(w)] for y in range(h)]
    far = chamfer([[c > 0.5 for c in row] for row in m], w, h)
    lum = lambda x, y: (px[(y * w + x) * 4] + px[(y * w + x) * 4 + 1] + px[(y * w + x) * 4 + 2]) * u / 3
    m = [[m[y][x] * math.sqrt(min(1.0, far[y][x] / PILLOW + 0.15)) * (0.6 + 0.4 * lum(x, y)) for x in range(w)] for y in range(h)]
    return [[(m[y][x] * 4 + m[y][max(x - 1, 0)] + m[y][min(x + 1, w - 1)] + m[max(y - 1, 0)][x] + m[min(y + 1, h - 1)][x]) / 8 for x in range(w)] for y in range(h)]


# ---------- dupioni slubs: parameters let go ----------
# hut.py's slubs (still in use, for the robe and its sash), at slubScale 1 (2026-11-04, after
# dupioni.jpeg): weft rows 1.5 mm apart, slubs 1 to 6 cm long and 1 to 3 mm thick, 2500 a
# square meter, raised 2 px (slubRelief) at 679 px/m. Let go the same day for slubScale 0.2
# (Ken: 20% as large, repeating more often).
DUPIONI_FIRST = {"slubScale": 1.0, "slubRelief": 2.0}
# Then at slubScale 0.2, raised 2 px; let go the same day for 0.4 px (Ken: 20% as raised).
DUPIONI_SMALL = {"slubScale": 0.2, "slubRelief": 2.0}
# Then raised 0.4 px; let go the same day for 0.2 px (Ken: half as raised).
DUPIONI_LOW = {"slubScale": 0.2, "slubRelief": 0.4}
# Then 0.2 px, the same day; let go for 0.4 again (Ken: go back to 0.4).
DUPIONI_LOWER = {"slubScale": 0.2, "slubRelief": 0.2}
