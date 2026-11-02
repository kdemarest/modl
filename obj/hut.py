"""Hut: a Swyng hut's furnishings, one family sharing one material (modl SPEC.md).

The spec is `# Modl Hut` in docs/models/Hut Models.md; its tweakvars ({name value unit} tags) hold
every size, read on each run. Readings (Claude, 2026-11-01):
- Most parts are one flat color, a swatch of the 1024 px atlas (4 x 4 swatches of 64 px in its
  top left, a little grain in each); colors are the images', set here (SWATCHES), not yet tweakvars.
- The barrel, disc, posts and stool are wood grain (Ken, 2026-11-01: map a grain rather than pay
  for triplanar): Canopy's WoodDesatD.jpg, a gray seamless grain, tinted the part's wood swatch
  (its mean gray made that color, the grain's contrast halved), copied into islands of the atlas
  at woodDensity (the floor at floorDensity), packed in shelves beside the swatches, tallest
  first, the densities lowered until they fit. Bands of a turned part are mapped around and
  along its profile (by length), caps from above; a band's grain repeats a whole number of
  woodTile tiles around, so its seam doesn't show. The barrel's staves run up it (one face of
  its body per stave, so the lid has as many sides) and its lid's boards across; the disc's rim
  wraps its island four times around (its sides a multiple of four); the posts' and the stool's
  legs' grain runs along them. The floor is end grain (Ken, 2026-11-01: the disc's image): the
  grain laid round in rings, wobbling a little. The normal map comes from a height field: the
  grain a little; each board of the barrel crowned and grooved 2 px deep at its seams, which are
  dark and each board shaded up to 6% apart; the carved bands of the disc's rim (key frets and
  crossed diamonds, between frame lines) and the stool's edge (key frets and rings), raised
  lines on dark recesses, copied at carveDensity; and the stool's adze facets, each tilted its
  own way (long ones down its legs). The cocoon keeps its flat color, its silk lumpy in the
  normal map (Ken, 2026-11-01: only a normal map, made by an algorithm; a photo of a real one):
  rounded lumps cocoonLump across with creases between (from a cellular noise's F2 - F1),
  half-size lumps over them a little and a fine fuzz, copied at cocoonDensity. The disc and
  the stool's seat are a little uneven (a smooth noise) and checked (Ken, 2026-11-02: too
  perfect): cracks running in from their edges, thinning as they go, dark and grooved.
- The mat, the hammock's bed and the robe are their images' (Ken, 2026-11-02): the mat a plain
  weave of matStrip strips over and under, its border a dark herringbone braid, at the floor's
  density; the bed cream silk with green edges and its hexagons and diamonds in brown and green,
  a fine weave in the normal map; the robe brown with green swirls, a green collar and cuffs and
  a gray hem band, soft folds toward its hem. The robe's boxes are mapped from the front.
- The perch's grain runs along it, a knot band carved round it near its tip. The beech leaf's
  normal map embosses its veins (its brightness less its blur) and crinkles it a little.
- Polygons: see modl SPEC.md, Budgets. Ropes are 3-sided tubes, uncapped, one segment a straight
  run, four to a loop.
- A JPEG source is read through ImageMagick (`magick`, a workspace tool). Islands are padded
  8 px with their own wrapped content.
- The roof is five Roof Leaf models and a Roof Finial, placed by the Hut (Ken, 2026-11-01: five
  objects, so the leaf can roof other buildings). A leaf is Canopy's beech leaf, LeafBeech.png
  (Ken: the simplest profile), stem and all for now: its outline, traced from the texture's
  alpha, is the leaf's, stretched to leafLength by leafWidth, and its picture, tinted the dried
  leaf's colors by its brightness, is copied into an island, mapped as it lies in the texture
  (its stem at the pivot, its tip along +X).
- Built in Unity's axes (+X right, +Y up, +Z forward), then mirrored into OBJ's (X negated,
  winding reversed), as Unity's import negates X again.
- Lathed parts are smooth around and hard between profile segments; boxes and leaves are flat.
  Proportions the spec doesn't give, set here: the disc's rim is its sides; a post's flare
  rises two flare radii; the perch is full radius from a quarter of its length and swells 15%
  at the tip, turning up over its last 40%; the stool's legs start at 60% of the seat's radius
  and thicken 20% to the floor, the seat's top and bottom edges rounded over 30% of its
  thickness; a roof leaf falls as 1 - (1 - u)^1.5 along its length and curls up over its
  last 20%, its edges drooping most at its middle; the
  oven's dome is a quarter ellipse, its storage space a dark box half the base's height,
  its bench on two legs 5 cm square; the barrel's lid is 92% of its top, 2 cm proud, with a
  knob; the robe's sash ends are 6 by 15 cm; the peg
  flares 15% at its base and its knob rounds off over 60% of its radius; the cocoon is smooth along
  its length too.
- LODs: level k has the spec's sides halved k times (at least minSides) and rows likewise; the
  hammock drops to three cords at LOD1 and to its bed and a cord each end at LOD2; the robe
  loses its sash ends at LOD2; the peg has 6, 4 and 3 sides; the perch has 8, 6 and 4 sides, its points where it
  flares and turns up; a roof leaf has 12 even rows at LOD0, and each level below keeps the 8,
  then 4, whose loss strays least, so each level's rows are among the one above's. Where
  each level starts is measured (Ken, 2026-11-02: make LODs from each thing's shape): a full
  build finds how far each level strays from LOD0 (the farthest of LOD0's vertices from the
  level's surface) and starts it where that is lodError pixels (a pixel 90 degrees over 1900, so
  1210 a radian); Tweak's live changes keep the last build's errors. A model is culled where it
  is cullPixels tall, at most cullDistance, except the disc, roof, posts and perches, drawn to
  farCullDistance. A level's lowest screen height is size / (2 d) at the next level's distance
  (the last at the cull distance), size the model's largest extent, as Unity's LODGroup and
  layout measure it.

  python3 obj/hut.py           writes obj/<Name>_LOD*.obj, Hut.mtl and the Hut atlases
  python3 obj/hut.py --write   also installs them into Canopy's Assets/Modl/Hut
Layout's Tweak drives it through obj/serve.py.
"""

import math
from array import array
import os
import subprocess
import sys

import modl

FAMILY = "Hut"
MATERIAL = "ModlHut"
DOC = os.path.join(modl.DOCS, "models", "Hut Models.md")
HEADING = "Modl Hut"
G = dict(geometry=True)
VARS = {
    "discDiameter": modl.Var(**G, min=0.5, max=10), "discThickness": modl.Var(**G, min=0.02, max=2),
    "rimInset": modl.Var(**G, min=0, max=0.3),
    "leafLength": modl.Var(**G, min=0.2, max=12), "leafFall": modl.Var(**G, min=0, max=5),
    "leafWidth": modl.Var(**G, min=0.1, max=8),
    "leafDroop": modl.Var(**G, min=0, max=1), "leafCurl": modl.Var(**G, min=0, max=1),
    "leafThickness": modl.Var(**G, min=0.002, max=0.2),
    "finialHeight": modl.Var(**G, min=0.02, max=2), "finialRadius": modl.Var(**G, min=0.01, max=1),
    "postHeight": modl.Var(**G, min=0.2, max=6), "postRadius": modl.Var(**G, min=0.01, max=0.5),
    "postFlare": modl.Var(**G, min=0.01, max=0.8),
    "perchLength": modl.Var(**G, min=0.1, max=3), "perchRadius": modl.Var(**G, min=0.01, max=0.5),
    "perchFlare": modl.Var(**G, min=0.01, max=0.8), "perchUpturn": modl.Var(**G, min=0, max=1),
    "seatHeight": modl.Var(**G, min=0.1, max=1.5), "seatRadius": modl.Var(**G, min=0.05, max=1),
    "seatThickness": modl.Var(**G, min=0.01, max=0.4), "legRadius": modl.Var(**G, min=0.005, max=0.2),
    "legSplay": modl.Var(**G, min=0, max=0.5),
    "matDiameter": modl.Var(**G, min=0.2, max=5), "matThickness": modl.Var(**G, min=0.002, max=0.2),
    "matBorder": modl.Var(**G, min=0, max=1), "matStrip": modl.Var(textures=True, min=0.01, max=0.3),
    "hammockSpan": modl.Var(**G, min=0.5, max=5), "bedLength": modl.Var(**G, min=0.3, max=4),
    "bedWidth": modl.Var(**G, min=0.1, max=2), "silkThickness": modl.Var(**G, min=0.002, max=0.1),
    "bedSag": modl.Var(**G, min=0, max=1), "bedClearance": modl.Var(**G, min=0, max=2),
    "barRadius": modl.Var(**G, min=0.005, max=0.1), "cordCount": modl.Var(**G, min=1, max=12),
    "cordRadius": modl.Var(**G, min=0.001, max=0.05), "cordRise": modl.Var(**G, min=0, max=1),
    "loopRadius": modl.Var(**G, min=0.01, max=0.3),
    "ovenRadius": modl.Var(**G, min=0.1, max=2), "ovenBaseHeight": modl.Var(**G, min=0.05, max=2),
    "domeHeight": modl.Var(**G, min=0.05, max=2), "flueRadius": modl.Var(**G, min=0.02, max=1),
    "flueHeight": modl.Var(**G, min=0.01, max=1), "mouthWidth": modl.Var(**G, min=0.05, max=2),
    "mouthHeight": modl.Var(**G, min=0.05, max=2), "shelfWidth": modl.Var(**G, min=0.05, max=3),
    "shelfDepth": modl.Var(**G, min=0.02, max=1), "benchWidth": modl.Var(**G, min=0.1, max=3),
    "benchDepth": modl.Var(**G, min=0.05, max=1), "benchThickness": modl.Var(**G, min=0.01, max=0.3),
    "benchHeight": modl.Var(**G, min=0.03, max=1),
    "barrelHeight": modl.Var(**G, min=0.1, max=3), "barrelRadius": modl.Var(**G, min=0.05, max=2),
    "barrelBulge": modl.Var(**G, min=0, max=0.5),
    "robeLength": modl.Var(**G, min=0.1, max=2), "robeWidth": modl.Var(**G, min=0.1, max=2),
    "robeHem": modl.Var(**G, min=0.1, max=2), "robeDepth": modl.Var(**G, min=0.02, max=0.5),
    "sleeveSpan": modl.Var(**G, min=0.1, max=3), "sleeveHeight": modl.Var(**G, min=0.02, max=1),
    "sashHeight": modl.Var(**G, min=0.01, max=0.5), "sashAbove": modl.Var(**G, min=0, max=2),
    "pegLength": modl.Var(**G, min=0.02, max=0.5), "pegRadius": modl.Var(**G, min=0.005, max=0.2),
    "pegKnob": modl.Var(**G, min=0.005, max=0.3),
    "cocoonLength": modl.Var(**G, min=0.01, max=1), "cocoonWidth": modl.Var(**G, min=0.01, max=1),
    "woodTile": modl.Var(geometry=True, textures=True, min=0.1, max=10),
    "woodDensity": modl.Var(geometry=True, textures=True, min=32, max=1024),
    "floorDensity": modl.Var(geometry=True, textures=True, min=16, max=1024),
    "carveDensity": modl.Var(geometry=True, textures=True, min=32, max=2048),
    "cocoonDensity": modl.Var(geometry=True, textures=True, min=32, max=2048),
    "cocoonLump": modl.Var(textures=True, min=0.002, max=0.2),
    "staveWidth": modl.Var(textures=True, min=0.02, max=1),
    "roundSides": modl.Var(**G, min=4, max=64), "minSides": modl.Var(**G, min=3, max=16),
    "lodError": modl.Var(**G, min=0.25, max=20), "cullPixels": modl.Var(**G, min=1, max=100),
    "cullDistance": modl.Var(**G, min=1, max=1000), "farCullDistance": modl.Var(**G, min=1, max=2000),
}
SOURCE_MATERIAL = "Assets/Materials/StructBases.mat"
COLOR_META, NORMAL_META = "Assets/Texture/StructBases_color.png", "Assets/Texture/StructBases_nmap.png"
WOOD_SOURCE = "Assets/Active/Hut Shehroze v3 126/WoodDesatD.jpg"
LEAF_SOURCE = "Assets/Texture/LeafBeech.png"
SWATCHES = ["#c08a50", "#8a5a30", "#9a5f30", "#b98a55",   # wood light, dark, mid; leaf
            "#a07040", "#3a3a3c", "#141414", "#d8cfae",   # leaf dark; stone; black; silk
            "#6f8a4a", "#a07a48", "#6b5a3a", "#5d6b3a",   # silk green; cord; robe brown, green
            "#4aa0b0", "#f2f0ea", "#c09a60", "#8a6a40"]   # sash blue; cocoon; straw, straw dark
(WOOD, WOOD_DARK, WOOD_MID, LEAF, LEAF_DARK, STONE, BLACK, SILK, SILK_GREEN, CORD,
 ROBE, ROBE_GREEN, SASH, COCOON, STRAW, STRAW_DARK) = range(16)
ATLAS, CELL, PAD = 1024, 64, 8
RIM_REPS = 8  # the disc's rim wraps its island this many times around


def tags():
    modl.check_sources(DOC, HEADING, ["Canopy " + p for p in (SOURCE_MATERIAL, COLOR_META, NORMAL_META, WOOD_SOURCE, LEAF_SOURCE)])
    return modl.read_tags(DOC, HEADING, VARS)


def values(overrides=None):
    """The vars in the script's units (meters, counts), from the doc's tags, with overrides
    {name: value in the tag's unit}, each held within its limits."""
    t = tags()
    out = {}
    for name, var in VARS.items():
        value, unit = t[name]
        if overrides and name in overrides:
            value = float(overrides[name])
        value *= modl.UNITS[unit]
        if var.min is not None:
            value = max(var.min, value)
        if var.max is not None:
            value = min(var.max, value)
        out[name] = value
    return out


def uv(swatch):
    """The middle of a swatch, v up from the bottom."""
    col, row = swatch % 4, swatch // 4
    return ((col * CELL + CELL / 2) / ATLAS, 1 - (row * CELL + CELL / 2) / ATLAS)


# ---------- building in Unity's axes ----------

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    n = math.sqrt(sum(x * x for x in a)) or 1.0
    return tuple(x / n for x in a)


class Part:
    """Faces in Unity's axes: each a list of (position, normal) corners and a swatch."""

    def __init__(self):
        self.faces = []

    def add(self, other, move=(0, 0, 0), yaw=0.0):
        """Another part, turned yaw degrees about +Y (Unity's: +X toward -Z) and moved."""
        c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        turn = lambda p: (p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c)
        for corners, swatch in other.faces:
            self.faces.append(([(tuple(a + b for a, b in zip(turn(k[0]), move)), turn(k[1])) + tuple(k[2:]) for k in corners], swatch))
        return self

    def mesh(self, name):
        """The part as an OBJ mesh: X negated, each face wound to face along its normal."""
        m = modl.Mesh(name)
        for corners, swatch in self.faces:
            t = uv(swatch)
            # a corner (position, normal) takes its swatch's middle; (position, normal, uv) its own
            ids = [m.vertex((-k[0][0], k[0][1], k[0][2]), (-k[1][0], k[1][1], k[1][2]), k[2] if len(k) > 2 else t) for k in corners]
            a, b, c = (m.verts[i][0] for i in ids[:3])
            want = m.verts[ids[0]][1]
            fn = cross(sub(b, a), sub(c, a))
            flip = sum(fn[i] * want[i] for i in range(3)) < 0
            for k in range(1, len(ids) - 1):
                m.tris.append((ids[0], ids[k + 1], ids[k]) if flip else (ids[0], ids[k], ids[k + 1]))
        return m


def lathe(profile, sides, swatches, uvs=None, smooth=False):
    """Revolves (radius, y) points about +Y, bottom middle to top middle on the outside; segment k
    takes swatches[k] (or the one swatch), or with uvs, uvs(k, around, r, y, start) where it gives
    one (around 0 to 1 from +X; start, the face's first around). Smooth around, and hard between
    segments unless smooth (then each profile point's normal is its segments' average, straight
    up or down at a pole)."""
    part = Part()
    sides = max(3, int(sides))
    angles = [2 * math.pi * j / sides for j in range(sides + 1)]
    seg = [unit((yb - ya, -(rb - ra), 0))[:2] if (ra, ya) != (rb, yb) else None
           for (ra, ya), (rb, yb) in zip(profile, profile[1:])]

    def point_normal(i):
        near = [n for n in (seg[i - 1] if i > 0 else None, seg[i] if i < len(seg) else None) if n]
        if profile[i][0] == 0:
            return (0.0, 1.0 if sum(n[1] for n in near) > 0 else -1.0)
        return unit((sum(n[0] for n in near), sum(n[1] for n in near), 0))[:2]
    for k in range(len(profile) - 1):
        (ra, ya), (rb, yb) = profile[k], profile[k + 1]
        if ra == rb == 0 or (ra, ya) == (rb, yb):
            continue
        nr, ny = seg[k]
        sw = swatches[k] if isinstance(swatches, list) else swatches
        for j in range(sides):
            corners = []
            for jj, r, y, at in ((j, ra, ya, k), (j, rb, yb, k + 1), (j + 1, rb, yb, k + 1), (j + 1, ra, ya, k)):
                phi = angles[jj]
                pr, py = point_normal(at) if smooth else (nr, ny)
                corner = ((r * math.cos(phi), y, r * math.sin(phi)), (pr * math.cos(phi), py, pr * math.sin(phi)))
                t = uvs(k, jj / sides, r, y, j / sides) if uvs else None
                corners.append(corner + (t,) if t else corner)
            if ra == 0:
                corners = corners[1:3] + corners[:1]
            elif rb == 0:
                corners = [corners[0], corners[1], corners[3]]
            part.faces.append((corners, sw))
    return part


def tube(path, radii, sides, swatch, caps=True, uvs=None):
    """A tube along path (points), radius radii[i] at path[i], smooth around, capped; with uvs,
    uvs(along, around) (each 0 to 1, along by length from the path's start) maps its sides."""
    part = Part()
    sides = max(3, int(sides))
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + math.sqrt(sum((b[q] - a[q]) ** 2 for q in range(3))))
    along = [x / (lengths[-1] or 1) for x in lengths]
    rings = []
    for i, p in enumerate(path):
        t = unit(sub(path[min(i + 1, len(path) - 1)], path[max(i - 1, 0)]))
        ref = (0, 1, 0) if abs(t[1]) < 0.9 else (1, 0, 0)
        a = unit(cross(t, ref))
        b = cross(t, a)
        ring = []
        for j in range(sides):
            phi = 2 * math.pi * j / sides
            n = tuple(a[q] * math.cos(phi) + b[q] * math.sin(phi) for q in range(3))
            ring.append((tuple(p[q] + n[q] * radii[i] for q in range(3)), n))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for j in range(sides):
            k = (j + 1) % sides
            corners = [rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]]
            if uvs:
                at = ((along[i], j), (along[i + 1], j), (along[i + 1], j + 1), (along[i], j + 1))
                corners = [c + (uvs(a, jj / sides),) for c, (a, jj) in zip(corners, at)]
            part.faces.append((corners, swatch))
    if caps:
        for ring, p, sign in ((rings[0], path[0], -1), (rings[-1], path[-1], 1)):
            t = unit(sub(path[1], path[0]) if sign < 0 else sub(path[-1], path[-2]))
            n = tuple(sign * x for x in t)
            part.faces.append(([(q, n) for q, _ in ring], swatch))
    return part


def box(center, size, swatch, bottom=None, top=None, uvs=None):
    """A box (or with bottom and top (w, d) a frustum) centered at center; with uvs, uvs(p)
    maps each corner."""
    part = Part()
    cx, cy, cz = center
    w, h, d = size
    bw, bd = bottom or (w, d)
    tw, td = top or (w, d)
    lo = [(cx + sx * bw / 2, cy - h / 2, cz + sz * bd / 2) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    hi = [(cx + sx * tw / 2, cy + h / 2, cz + sz * td / 2) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    faces = [lo[::-1], hi] + [[lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]] for i in range(4)]
    for f in faces:
        n = unit(cross(sub(f[1], f[0]), sub(f[2], f[0])))
        mid = tuple(sum(p[q] for p in f) / 4 for q in range(3))
        if sum(n[q] * (mid[q] - center[q]) for q in range(3)) < 0:
            n = tuple(-x for x in n)
        part.faces.append(([(p, n) + ((uvs(p),) if uvs else ()) for p in f], swatch))
    return part


def sheet(points, swatch, thickness, normal_up=True, uvs=None):
    """A surface of rows of points (a grid), both sides, its back thickness below; flat faces,
    each its swatch or, with uvs (a grid like points), mapped. A face's normal is from its
    diagonals, so a row of one point (a leaf's tip) still has one."""
    part = Part()
    for i in range(len(points) - 1):
        for j in range(len(points[i]) - 1):
            at = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            q = [points[a][b] for a, b in at]
            n = unit(cross(sub(q[2], q[0]), sub(q[3], q[1])))
            if (n[1] < 0) == normal_up:
                n = tuple(-x for x in n)
            t = [(uvs[a][b],) for a, b in at] if uvs else [()] * 4
            part.faces.append(([(p, n) + k for p, k in zip(q, t)], swatch))
            back = [(p[0], p[1] - thickness, p[2]) for p in q]
            part.faces.append(([(p, tuple(-x for x in n)) + k for p, k in zip(back, t)], swatch))
    return part


def band(prof, maps):
    """A lathe's uvs from maps {segment: mapping}: ("cap", rect, R), seen from above, radius R
    filling the island; ("wrap", rect, reps, k0, k1), around the island's width reps times (whole
    faces to a repeat) and down its height from the top of segment k1 to the bottom of k0, by
    length along the profile. rect is an island (x, y, w, h)."""
    lengths = [0.0]
    for (ra, ya), (rb, yb) in zip(prof, prof[1:]):
        lengths.append(lengths[-1] + math.hypot(rb - ra, yb - ya))

    def uvs(k, around, r, y, start):
        m = maps.get(k)
        if not m:
            return None
        if m[0] == "cap":
            _, (x0, y0, w, h), R = m
            a = 2 * math.pi * around
            return ((x0 + (r * math.cos(a) / (2 * R) + 0.5) * w) / ATLAS, 1 - (y0 + (r * math.sin(a) / (2 * R) + 0.5) * h) / ATLAS)
        _, (x0, y0, w, h), reps, k0, k1 = m
        at = lengths[k] if (r, y) == tuple(prof[k]) else lengths[k + 1]
        s = (at - lengths[k0]) / ((lengths[k1 + 1] - lengths[k0]) or 1)
        u = around * reps - math.floor(start * reps + 1e-9)
        return ((x0 + u * w) / ATLAS, 1 - (y0 + (1 - s) * h) / ATLAS)
    return uvs


# ---------- the models ----------

def sides_at(v, level, big=False):
    base = v["roundSides"] * (2 if big else 1)
    return max(int(v["minSides"]), int(round(base)) >> level)


def disc(v, level):
    r, t, i = v["discDiameter"] / 2, v["discThickness"], min(v["rimInset"], v["discThickness"] / 2)
    prof = [(0, 0), (r - i, 0), (r, i), (r, t - i), (r - i, t), (0, t)]
    isl = islands(v)
    maps = {0: ("cap", isl["floor"], r), 4: ("cap", isl["floor"], r)}
    maps.update({k: ("wrap", isl["rim"], RIM_REPS, 1, 3) for k in (1, 2, 3)})
    sides = -(-sides_at(v, level, True) // RIM_REPS) * RIM_REPS
    return lathe(prof, sides, [WOOD_DARK, WOOD_DARK, WOOD_DARK, WOOD_DARK, WOOD], band(prof, maps))


_leaf = {}  # the beech leaf, read once per run or worker


def leaf_source():
    """LeafBeech as an Image; its outline, {row: (left, right)} in pixels where alpha is over
    half, rows top (tip) to bottom (stem); its box (x0, y0, x1, y1), the stem's middle x, and
    the mean brightness inside it."""
    if not _leaf:
        img = modl.read_png(modl.canopy_file(LEAF_SOURCE))
        rows = {}
        for y in range(img.h):
            xs = [x for x in range(img.w) if img.get(x, y)[3] * img.unit > 0.5]
            if xs:
                rows[y] = (xs[0], xs[-1] + 1)
        y0, y1 = min(rows), max(rows) + 1
        box = (min(a for a, _ in rows.values()), y0, max(b for _, b in rows.values()), y1)
        bright = [sum(img.get(x, y)[:3]) / 3 * img.unit for y, (a, b) in rows.items() for x in range(a, b, 3)]
        _leaf.update(img=img, rows=rows, box=box, stem=sum(rows[y1 - 1]) / 2, mean=sum(bright) / len(bright))
    return _leaf


def leaf_edges(y):
    """The outline's left and right at a fractional row, between its rows' edges."""
    rows, (_, y0, _, y1) = leaf_source()["rows"], leaf_source()["box"]
    y = min(max(y - 0.5, y0), y1 - 1)
    a, b = rows[int(y)], rows[min(int(y) + 1, y1 - 1)]
    f = y - int(y)
    return a[0] * (1 - f) + b[0] * f, a[1] * (1 - f) + b[1] * f


def roof_leaf(v):
    """One roof leaf, its stem at the pivot and its tip leafLength along +X, falling leafFall."""
    def make(_, level):
        L, W, fall = v["leafLength"], v["leafWidth"], v["leafFall"]
        x0, y0, x1, y1 = leaf_source()["box"]
        stem = leaf_source()["stem"]
        ix, iy, iw, ih = islands(v)["leaf"]
        widest = max(b - a for a, b in leaf_source()["rows"].values())
        def point(u, f):
            """The leaf's surface at u along it and f across (0 to 1), with its uv."""
            ty = y1 - u * (y1 - y0)  # the texture's row, the stem at its bottom
            a, b = leaf_edges(ty)
            tx = a + (b - a) * f
            z = -(tx - stem) / widest * W  # the texture's right is the leaf's -Z, seen from above
            s = z / (W / 2)
            curl = v["leafCurl"] * max(0.0, (u - 0.8) / 0.2) ** 2
            y = fall * ((1 - u) ** 1.5 - 1) + curl - v["leafDroop"] * s * s * math.sin(math.pi * u)
            return (u * L, y, z), ((ix + (tx - x0) / (x1 - x0) * iw) / ATLAS, 1 - (iy + (ty - y0) / (y1 - y0) * ih) / ATLAS)
        us = [i / LEAF_ROWS for i in range(LEAF_ROWS + 1)]  # even: its widest part bulges as much as its ends bend
        cols = 4 if level == 0 else 2
        keep = leaf_rows(us, point, level)
        grid = [[point(us[i], j / cols)[0] for j in range(cols + 1)] for i in keep]
        uvs = [[point(us[i], j / cols)[1] for j in range(cols + 1)] for i in keep]
        return sheet(grid, LEAF, v["leafThickness"], uvs=uvs)
    return make


LEAF_ROWS, LEAF_KEEP = 12, (12, 8, 4)  # a roof leaf's rows at LOD0, and how many each level keeps


def leaf_rows(us, point, level):
    """Which of a leaf's rows level keeps: all at LOD0; below, rows dropped one at a time, each
    time the one whose loss strays least (the dropped rows' edges and middle from the straight
    line between the rows kept either side), so each level's rows are among the one above's."""
    pts = [[point(u, f)[0] for f in (0, 0.5, 1)] for u in us]

    def cost(a, b):
        worst = 0.0
        for i in range(a + 1, b):
            t = (us[i] - us[a]) / (us[b] - us[a])
            for j in range(3):
                worst = max(worst, math.dist(pts[i][j], tuple(pts[a][j][q] + (pts[b][j][q] - pts[a][j][q]) * t for q in range(3))))
        return worst
    keep = list(range(len(us)))
    for level_ in range(1, level + 1):
        while len(keep) > LEAF_KEEP[level_] + 1:
            k = min(range(1, len(keep) - 1), key=lambda k: cost(keep[k - 1], keep[k + 1]))
            del keep[k]
    return keep


def finial(v, level):
    fr, fh = v["finialRadius"], v["finialHeight"]
    return lathe([(0, 0), (fr, 0), (fr * 0.8, fh * 0.6), (fr * 0.5, fh), (0, fh)], sides_at(v, level), LEAF_DARK)


def post(v, level):
    r, f, h = v["postRadius"], v["postFlare"], v["postHeight"]
    prof = [(0, 0), (f, 0), (f, f), (r, 2 * f), (r * 0.9, h), (0, h)]
    maps = {k: ("wrap", islands(v)["post"], 1, 1, 3) for k in (1, 2, 3)}
    return lathe(prof, sides_at(v, level), WOOD_DARK, band(prof, maps))


def perch(v, level):
    L, r, f, up = v["perchLength"], v["perchRadius"], v["perchFlare"], v["perchUpturn"]
    # points where it changes: the flare's end (a quarter along), the upturn's start (0.6) and the
    # swell (0.85); each level's among the one above's
    path, radii = [], []
    for t in ((0, 0.12, 0.25, 0.6, 0.73, 0.85, 1), (0, 0.25, 0.6, 0.85, 1), (0, 0.25, 0.6, 1))[level]:
        x = L * t
        path.append((x, f + up * max(0.0, (x / L - 0.6) / 0.4) ** 2, 0))
        t = x / L
        radii.append(f + (r - f) * min(1.0, t / 0.25) if t < 0.25 else r * (1 + 0.15 * max(0.0, (t - 0.85) / 0.15)))
    px, py, pw, ph = islands(v)["perch"]
    return tube(path, radii, (8, 6, 4)[level], WOOD_MID,
                uvs=lambda along, around: ((px + around * pw) / ATLAS, 1 - (py + along * ph) / ATLAS))


def stool(v, level):
    r, t, top = v["seatRadius"], v["seatThickness"], v["seatHeight"]
    y0 = top - t
    prof = [(0, y0), (r * 0.9, y0), (r, y0 + t * 0.3), (r, y0 + t * 0.7), (r * 0.9, top), (0, top)]
    isl = islands(v)
    maps = {0: ("cap", isl["seat"], r), 4: ("cap", isl["seat"], r)}
    maps.update({k: ("wrap", isl["seatEdge"], 1, 1, 3) for k in (1, 2, 3)})
    seat = lathe(prof, sides_at(v, level), [WOOD_MID, WOOD_DARK, WOOD_DARK, WOOD_DARK, WOOD_MID], band(prof, maps))
    lx, ly, lw, lh = isl["leg"]
    leg_uvs = lambda along, around: ((lx + around * lw) / ATLAS, 1 - (ly + along * lh) / ATLAS)
    for k in range(3):
        a = 2 * math.pi * k / 3
        d = (math.cos(a), 0, math.sin(a))
        start, end = r * 0.6, r * 0.6 + v["legSplay"]
        path = [(d[0] * start, y0 + 0.01, d[2] * start), (d[0] * (start + end) / 2, y0 / 2, d[2] * (start + end) / 2), (d[0] * end, 0, d[2] * end)]
        lr = v["legRadius"]
        seat.add(tube(path, [lr, lr * 1.1, lr * 1.2], max(3, sides_at(v, level) // 2), WOOD_MID, uvs=leg_uvs))
    return seat


def mat(v, level):
    R, t, b = v["matDiameter"] / 2, v["matThickness"], min(v["matBorder"], v["matDiameter"] / 2)
    prof = [(R, 0), (R, t), (R - b, t), (0, t)]  # no underside: it lies on the floor
    maps = {k: ("cap", islands(v)["mat"], R) for k in (1, 2)}
    return lathe(prof, sides_at(v, level, True), [STRAW_DARK, STRAW_DARK, STRAW], band(prof, maps))


def hammock(v, level):
    part = Part()
    L, W, sag, clear = v["bedLength"], v["bedWidth"], v["bedSag"], v["bedClearance"]
    nx, nz = max(2, 8 >> level), max(1, 2 >> level)  # it sags only along its length
    grid = [[(-L / 2 + L * i / nx, clear + sag * (2 * (-L / 2 + L * i / nx) / L) ** 2, -W / 2 + W * j / nz) for j in range(nz + 1)] for i in range(nx + 1)]
    bx, by, bw, bh = islands(v)["bed"]
    uvs = [[((bx + i / nx * bw) / ATLAS, 1 - (by + j / nz * bh) / ATLAS) for j in range(nz + 1)] for i in range(nx + 1)]
    part.add(sheet(grid, SILK, v["silkThickness"], uvs=uvs))
    end_y, span = clear + sag, v["hammockSpan"] / 2
    loop_y = end_y + v["cordRise"]
    cords = int(round(v["cordCount"])) if level == 0 else (min(3, int(round(v["cordCount"]))) if level == 1 else 1)
    cs = max(3, 6 >> level)
    for sx in (-1, 1):
        x = sx * L / 2
        lx = sx * (span - 2 * v["loopRadius"])
        if level == 2:  # far off: the bed and a cord to where each loop was
            part.add(tube([(x, end_y, 0), (sx * span, loop_y, 0)], [v["cordRadius"] * 1.5] * 2, 3, CORD, caps=False))
            continue
        part.add(tube([(x, end_y, -W / 2), (x, end_y, W / 2)], [v["barRadius"]] * 2, cs, SILK_GREEN))
        for c in range(cords):
            z = 0.0 if cords == 1 else -W / 2 + W * c / (cords - 1)
            part.add(tube([(x, end_y, z), (lx, loop_y, 0)], [v["cordRadius"]] * 2, 3, CORD, caps=False))
        lr = v["loopRadius"]
        ring = [(lx + sx * lr - sx * lr * math.cos(2 * math.pi * k / 4), loop_y + lr * math.sin(2 * math.pi * k / 4), 0) for k in range(5)]
        part.add(tube(ring, [v["cordRadius"] * 1.5] * 5, 3, CORD, caps=False))
    return part


def oven(v, level):
    R, base, dome, fr, fh = v["ovenRadius"], v["ovenBaseHeight"], v["domeHeight"], v["flueRadius"], v["flueHeight"]
    n = max(2, 6 >> level)
    prof = [(0, 0), (R, 0), (R, base)]
    for i in range(1, n + 1):
        a = math.pi / 2 * i / n
        r = max(fr, R * math.cos(a))
        prof.append((r, base + dome * math.sin(a)))
        if r <= fr:
            break
    top = prof[-1][1]
    prof += [(fr, top + fh), (fr * 0.6, top + fh), (fr * 0.6, top + fh * 0.5), (0, top + fh * 0.5)]
    part = lathe(prof, sides_at(v, level), STONE)
    mw, mh = v["mouthWidth"], v["mouthHeight"]
    part.add(box((0, base + 0.04 + mh / 2, R * 0.93), (mw, mh, 0.12), BLACK))
    part.add(box((0, base, R * 0.95), (v["shelfWidth"], 0.08, v["shelfDepth"]), STONE))
    part.add(box((0, base * 0.45, R * 0.93), (mw, base * 0.5, 0.1), BLACK))
    bw, bd, bt, bh = v["benchWidth"], v["benchDepth"], v["benchThickness"], v["benchHeight"]
    bz = R + bd / 2
    part.add(box((0, bh - bt / 2, bz), (bw, bt, bd), WOOD_DARK))
    for sx in (-1, 1):
        part.add(box((sx * (bw / 2 - 0.08), (bh - bt) / 2, bz), (0.05, bh - bt, 0.05), WOOD_DARK))
    return part


def stave_count(v):
    """The barrel's staves, staveWidth wide around its widest (an even number)."""
    n = max(4, round(2 * math.pi * (v["barrelRadius"] + v["barrelBulge"]) / v["staveWidth"]))
    return n + n % 2


def robe_span(v):
    """The robe's width across its sleeves or hem, whichever is wider: its island's width."""
    return max(v["sleeveSpan"], v["robeHem"], v["robeWidth"])


def islands(v):
    """The atlas's islands, (x, y, w, h) in pixels from the top left, by name, and the densities
    they were sized at ("density", "floorDensity", "carveDensity", "cocoonDensity"): the
    swatches' cells in the top left, then the rest, tallest first, each padded PAD, each as high
    as it fits on the skyline of those before (its lowest place, then its leftmost); the
    densities lowered until they fit."""
    lx0, ly0, lx1, ly1 = leaf_source()["box"]
    H, lid = v["barrelHeight"], 2 * v["barrelRadius"] * 0.92
    r, t, i = v["discDiameter"] / 2, v["discThickness"], min(v["rimInset"], v["discThickness"] / 2)
    f, pr, ph = v["postFlare"], v["postRadius"], v["postHeight"]
    sr, st = v["seatRadius"], v["seatThickness"]
    lengths = {
        "rim": 2 * i * math.sqrt(2) + t - 2 * i,
        "post": f + math.hypot(pr - f, f) + math.hypot(pr * 0.1, ph - 2 * f),
        "seatEdge": 2 * math.hypot(sr * 0.1, st * 0.3) + st * 0.4,
        "leg": math.hypot(v["legSplay"], v["seatHeight"] - st + 0.01),
        "cocoon": sum(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(cocoon_profile(v, 32), cocoon_profile(v, 32)[1:])),
    }
    scale = 1.0
    while True:
        d, fd, cd = v["woodDensity"] * scale, v["floorDensity"] * scale, v["carveDensity"] * scale
        cod = v["cocoonDensity"] * scale
        px = lambda m, k=d: max(4, round(m * k))
        want = [("leaf", px(lx1 - lx0, scale), px(ly1 - ly0, scale)),
                ("staves", px(2 * math.pi * (v["barrelRadius"] + v["barrelBulge"])), px(H)),
                ("lid", px(lid), px(lid)), ("floor", px(2 * r, fd), px(2 * r, fd)),
                ("rim", px(2 * math.pi * r / RIM_REPS, cd), px(lengths["rim"], cd)),
                ("post", px(2 * math.pi * pr), px(lengths["post"])),
                ("seat", px(2 * sr), px(2 * sr)), ("seatEdge", px(2 * math.pi * sr, cd), px(lengths["seatEdge"], cd)),
                ("leg", px(2 * math.pi * v["legRadius"] * 1.1), px(lengths["leg"])),
                ("cocoon", px(math.pi * v["cocoonWidth"], cod), px(lengths["cocoon"], cod)),
                ("mat", px(v["matDiameter"], fd), px(v["matDiameter"], fd)),
                ("bed", px(v["bedLength"]), px(v["bedWidth"])),
                ("robe", px(robe_span(v)), px(v["robeLength"])),
                ("perch", px(2 * math.pi * v["perchRadius"]), px(v["perchLength"] + v["perchUpturn"]))]
        sky = [[0, 4 * CELL, 4 * CELL], [4 * CELL, ATLAS - 4 * CELL, 0]]  # [x, width, top] spans
        out, fits = {}, True
        for name, w, h in sorted(want, key=lambda e: -e[2]):
            ww, hh = w + 2 * PAD, h + 2 * PAD
            spots = [(max(t[2] for t in sky if t[0] < x + ww and t[0] + t[1] > x), x) for x, _, _ in sky if x + ww <= ATLAS]
            if not spots:
                fits = False
                break
            y, x = min(spots)
            rest = []
            for a, width, top in sky:
                b = a + width
                if b <= x or a >= x + ww:
                    rest.append([a, width, top])
                    continue
                if a < x:
                    rest.append([a, x - a, top])
                if b > x + ww:
                    rest.append([x + ww, b - x - ww, top])
            sky = sorted(rest + [[x, ww, y + hh]])
            out[name] = (x + PAD, y + PAD, w, h)
            fits = fits and y + hh <= ATLAS
        if fits:
            out.update(density=d, floorDensity=fd, carveDensity=cd, cocoonDensity=cod)
            return out
        scale *= 0.9


def barrel(v, level):
    H, R, bulge = v["barrelHeight"], v["barrelRadius"], v["barrelBulge"]
    n = max(2, 4 >> level)
    prof = [(0, 0)] + [(R + bulge * math.sin(math.pi * i / n), H * i / n) for i in range(n + 1)]
    lid = R * 0.92
    prof += [(lid, H), (lid, H + 0.02), (0, H + 0.02)]
    isl = islands(v)
    maps = {k: ("wrap", isl["staves"], 1, 1, n) for k in range(1, n + 1)}
    maps.update({k: ("cap", isl["lid"], lid) for k in range(n + 1, n + 4)})
    # a face of its body per stave, so the seams are edges and the lid has as many sides
    sides = max(int(v["minSides"]), stave_count(v) >> level)
    part = lathe(prof, sides, [WOOD_MID] * (n + 2) + [WOOD_DARK, WOOD_DARK], band(prof, maps))
    part.add(lathe([(0, 0), (0.03, 0), (0.03, 0.03), (0, 0.04)], max(3, sides_at(v, level) // 2), WOOD_DARK), (0, H + 0.02, 0))
    return part


def loft(rings, swatch, uvs=None, caps=(None, None)):
    """A tube through rings (closed loops of points, all the same count), smooth around and
    along; uvs(p) maps each corner. caps: the swatch to close its first and last ring with, or
    None to leave it open."""
    part = Part()
    m, n = len(rings), len(rings[0])
    mid = [tuple(sum(p[q] for p in r) / n for q in range(3)) for r in rings]

    def normal(i, j):
        around = sub(rings[i][(j + 1) % n], rings[i][(j - 1) % n])
        along = sub(rings[min(i + 1, m - 1)][j], rings[max(i - 1, 0)][j])
        nm = unit(cross(along, around))
        out = sub(rings[i][j], mid[i])
        return nm if sum(nm[q] * out[q] for q in range(3)) >= 0 else tuple(-x for x in nm)
    corner = lambda i, j: (rings[i][j], normal(i, j)) + ((uvs(rings[i][j]),) if uvs else ())
    for i in range(m - 1):
        for j in range(n):
            k = (j + 1) % n
            part.faces.append(([corner(i, j), corner(i + 1, j), corner(i + 1, k), corner(i, k)], swatch))
    for end, cap in ((0, caps[0]), (m - 1, caps[1])):
        if cap is None:
            continue
        nm = unit(sub(mid[end], mid[1 if end == 0 else m - 2]))
        part.faces.append(([(p, nm) + ((uvs(p),) if uvs else ()) for p in rings[end]], cap))
    return part


def ellipse(center, a, b, axes, sides, square=1.0):
    """A loop of sides points round center: a along axes[0], b along axes[1]; square under 1
    squares it off toward a rounded rectangle (a superellipse's exponent)."""
    u, w = axes
    out = []
    for k in range(sides):
        c, s_ = math.cos(2 * math.pi * k / sides), math.sin(2 * math.pi * k / sides)
        c, s_ = math.copysign(abs(c) ** square, c), math.copysign(abs(s_) ** square, s_)
        out.append(tuple(center[q] + a * c * u[q] + b * s_ * w[q] for q in range(3)))
    return out


def robe(v, level):
    """As RobeFemale.png hangs: a cloth body, oval in section, from its hem up to broad, square
    shoulders and in to a wide neck; short wide sleeves of flat cloth (a rounded rectangle in
    section) angled down from its shoulders, open at their cuffs (dark inside); the sash a band round it, knotted in front, its two ends hanging past the hem.
    Its color, collar and trim are the front view's (paint_robe), back and front alike."""
    L, W, hem, D = v["robeLength"], v["robeWidth"], v["robeHem"], v["robeDepth"]
    rx, ry, rw, rh = islands(v)["robe"]
    span = robe_span(v)
    # seen from the front, held to its island (a tilted cuff reaches a little past its span)
    front = lambda p: ((rx + min(1.0, max(0.0, p[0] / span + 0.5)) * rw) / ATLAS, 1 - (ry + min(1.0, max(0.0, 1 - p[1] / L)) * rh) / ATLAS)
    flat = ((1, 0, 0), (0, 0, 1))
    sides = (12, 8, 6)[level]
    # its outline up the body: (height, half width, half depth); square shoulders, a wide neck
    body = [(0, hem / 2, D / 2), (0.3 * L, W / 2 * 0.98, D / 2), (0.75 * L, W / 2, D / 2 * 0.95), (L - 0.025, W / 2 * 0.97, D / 2 * 0.85), (L, 0.1, D * 0.3)]
    body = [body[i] for i in ((0, 1, 2, 3, 4), (0, 2, 3, 4), (0, 3, 4))[level]]
    part = loft([ellipse((0, y, 0), a, b, flat, sides) for y, a, b in body], ROBE, front, (STONE, ROBE))
    sh = v["sleeveHeight"]
    for sx in (-1, 1):
        start, end = (sx * (W / 2 - 0.04), L - sh / 2 - 0.01, 0), (sx * v["sleeveSpan"] / 2, L - sh / 2 - 0.05, 0)
        axis = unit(sub(end, start))
        upward = unit(cross((0, 0, 1), axis))
        # flat cloth: a rounded rectangle its height by a little over half the body's depth
        rings = [ellipse(c, sh / 2, D * 0.3, (upward, (0, 0, 1)), (8, 6, 4)[level], 0.5) for c in (start, end)]
        part.add(loft(rings, ROBE_GREEN, front, (None, STONE if level < 2 else None)))
    sa, sw = v["sashAbove"], v["sashHeight"]
    t = sa / L  # where up the body the sash is, for its width there
    a = (hem / 2) * (1 - t) + (W / 2) * t
    part.add(loft([ellipse((0, y, 0), a * 1.06, D / 2 * 1.12, flat, sides) for y in (sa - sw / 2, sa + sw / 2)], SASH))
    if level < 2:  # far off, without its knot and ends
        z = D / 2 * 1.12
        part.add(box((0, sa, z + 0.012), (0.07, sw * 1.2, 0.025), SASH))
        for sx in (-1, 1):
            part.add(box((sx * 0.025, sa - sw / 2 - 0.1, z + 0.01), (0.055, 0.2, 0.01), SASH))
    return part


def peg(v, level):
    """Along +Z from its base: flared a little where it grows, turning up toward its knob, its
    grain the stool's legs' (their island)."""
    pl, r, k = v["pegLength"], v["pegRadius"], v["pegKnob"]
    up = 0.3 * r
    pts = [((0, 0, 0), r * 1.15), ((0, 0, 0.65 * pl), r), ((0, up * 0.4, 0.88 * pl), r),
           ((0, up, pl), k), ((0, up, pl + 0.6 * k), 0.55 * k)]
    keep = ((0, 1, 2, 3, 4), (0, 1, 3, 4), (0, 3, 4))[level]
    lx, ly, lw, lh = islands(v)["leg"]
    return tube([pts[i][0] for i in keep], [pts[i][1] for i in keep], (6, 4, 3)[level], WOOD_DARK,
                uvs=lambda along, around: ((lx + around * lw) / ATLAS, 1 - (ly + along * lh) / ATLAS))


def cocoon_profile(v, n):
    L, W = v["cocoonLength"], v["cocoonWidth"]
    return [(W / 2 * math.sin(math.pi * i / n), L / 2 * (1 - math.cos(math.pi * i / n))) for i in range(n + 1)]


def cocoon(v, level):
    L, W = v["cocoonLength"], v["cocoonWidth"]
    n = max(3, 6 >> level)
    prof = cocoon_profile(v, n)
    maps = {k: ("wrap", islands(v)["cocoon"], 1, 0, n - 1) for k in range(n)}
    upright = lathe(prof, max(int(v["minSides"]), sides_at(v, level) * 5 // 8), COCOON, band(prof, maps), smooth=True)
    lying = Part()
    for corners, sw in upright.faces:
        # long axis from +Y onto +X, resting on the floor
        lying.faces.append(([((k[0][1] - L / 2, k[0][0] + W / 2, k[0][2]), (k[1][1], k[1][0], k[1][2])) + tuple(k[2:]) for k in corners], sw))
    return lying


MODELS = [("HutDisc", disc, True), ("RoofLeaf", None, True), ("RoofFinial", finial, True), ("HutPost", post, True), ("Perch", perch, True),
          ("Stool", stool, False), ("Mat", mat, False), ("Hammock", hammock, False), ("Oven", oven, False),
          ("Barrel", barrel, False), ("RobeFemale", robe, False), ("Peg", peg, False), ("Cocoon", cocoon, False)]


class Asset:
    def __init__(self, name, lods, size, heights):
        self.name, self.lods, self.size, self.heights = name, lods, size, heights


PX_PER_RADIAN = 1900 / (math.pi / 2)  # the Quest 2's: 90 degrees over 1900 px
_lod_errors = {}  # each model's [LOD1, LOD2] error, from the last full build (or the first use)


def point_triangle(p, a, b, c):
    """The distance from p to triangle abc (Ericson's closest point by regions)."""
    ab, ac, ap = sub(b, a), sub(c, a), sub(p, a)
    dot = lambda u, w: u[0] * w[0] + u[1] * w[1] + u[2] * w[2]
    d1, d2 = dot(ab, ap), dot(ac, ap)
    if d1 <= 0 and d2 <= 0:
        return math.dist(p, a)
    bp = sub(p, b)
    d3, d4 = dot(ab, bp), dot(ac, bp)
    if d3 >= 0 and d4 <= d3:
        return math.dist(p, b)
    vc = d1 * d4 - d3 * d2
    if vc <= 0 and d1 >= 0 and d3 <= 0:
        t = d1 / (d1 - d3)
        return math.dist(p, tuple(a[i] + t * ab[i] for i in range(3)))
    cp = sub(p, c)
    d5, d6 = dot(ab, cp), dot(ac, cp)
    if d6 >= 0 and d5 <= d6:
        return math.dist(p, c)
    vb = d5 * d2 - d1 * d6
    if vb <= 0 and d2 >= 0 and d6 <= 0:
        t = d2 / (d2 - d6)
        return math.dist(p, tuple(a[i] + t * ac[i] for i in range(3)))
    va = d3 * d6 - d5 * d4
    if va <= 0 and d4 - d3 >= 0 and d5 - d6 >= 0:
        t = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return math.dist(p, tuple(b[i] + t * (c[i] - b[i]) for i in range(3)))
    den = 1 / (va + vb + vc)
    return math.dist(p, tuple(a[i] + ab[i] * vb * den + ac[i] * vc * den for i in range(3)))


def lod_error(lods, k):
    """How far level k strays from LOD0: the farthest of LOD0's vertices from its surface."""
    pts = {tuple(round(c, 5) for c in p) for p, _, _ in lods[0].verts}
    tris = [[lods[k].verts[i][0] for i in t] for t in lods[k].tris]
    return max(min(point_triangle(p, *t) for t in tris) for p in pts)


def assets(v, measure=False):
    """The models, each level starting where its error is lodError pixels (errors measured when
    measure, or on first use; otherwise the last measured), culled where cullPixels tall."""
    out = []
    for name, make, far in MODELS:
        make = make or roof_leaf(v)
        lods = [make(v, k).mesh(f"{name}_LOD{k}") for k in range(3)]
        ps = [p for p, _, _ in lods[0].verts]
        size = max(max(p[q] for p in ps) - min(p[q] for p in ps) for q in range(3))
        if measure or name not in _lod_errors:
            _lod_errors[name] = [lod_error(lods, k) for k in (1, 2)]
        cull = v["farCullDistance"] if far else min(v["cullDistance"], size * PX_PER_RADIAN / v["cullPixels"])
        d1, d2 = (max(0.5, e * PX_PER_RADIAN / v["lodError"]) for e in _lod_errors[name])
        d2 = min(max(d2, d1 * 1.01), cull / 1.01)
        d1 = min(d1, d2 / 1.01)
        a = Asset(name, lods, size, [size / (2 * d) for d in (d1, d2, cull)])
        a.errors, a.distances = _lod_errors[name], (d1, d2, cull)
        out.append(a)
    return out


_wood = {}  # the grain source, read once per run or worker


def wood_source(size=None):
    """WoodDesatD as an Image, and its mean gray; with size, shrunk to size pixels square (once
    per size), so copying it at a lower density averages its pixels rather than aliasing."""
    if not _wood:
        data = modl.canopy_file(WOOD_SOURCE)
        if not data.startswith(b"\x89PNG"):
            data = subprocess.run(["magick", "-", "PNG24:-"], input=data, check=True, capture_output=True).stdout
        img = modl.read_png(data)
        step = max(1, img.w // 64)
        grays = [sum(img.get(x, y)[:3]) / 3 * img.unit for y in range(0, img.h, step) for x in range(0, img.w, step)]
        _wood.update(data=data, img=img, mean=sum(grays) / len(grays), sizes={})
    img = _wood["img"]
    if size and size < img.w:
        if size not in _wood["sizes"]:
            small = subprocess.run(["magick", "-", "-resize", f"{size}x{size}!", "PNG24:-"], input=_wood["data"], check=True, capture_output=True).stdout
            _wood["sizes"][size] = modl.read_png(small)
        img = _wood["sizes"][size]
    return img, _wood["mean"]


def wood_gray(img, along, across, tile):
    """The source's gray at (along, across) meters, along the grain, wrapping every tile."""
    x = (along / tile) % 1.0 * img.w
    y = (across / tile) % 1.0 * img.h
    return sum(img.get(int(x) % img.w, int(y) % img.h)[:3]) / 3 * img.unit


GRAIN_BUMP, CROWN, GROOVE = 1.5, 0.06, 0.8  # the height field's grain, board crown and seam groove


def paint_wood(color, normal, rect, along_of, across_of, swatch, tile, density, seed=0, boards_of=None, board_px=0, relief=None):
    """Fills an island (its padding too, wrapped across its width, clamped down its height) with
    grain tinted swatch's color: along_of(i, j) and across_of(i, j) give a pixel's meters along
    and across the grain. With boards_of (a pixel's board position across; a whole number is a
    seam) and board_px (a board's width in pixels), boards shaded apart with dark seams. The
    normal map is the gradient of a height field in pixels: the grain, each board's crown, and
    its seams grooved 2 px deep; with relief(i, j), a carving's (height in pixels, light), its
    height added and its color times its light. density, the island's pixels per meter, sizes
    the source."""
    img, mean = wood_source(max(8, round(tile * density)))
    x0, y0, w, h = rect
    tint = [int(SWATCHES[swatch][1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)]
    W, H = w + 2 * PAD, h + 2 * PAD
    height = array("f", [0.0]) * (W * H)
    for j in range(-PAD, h + PAD):
        for i in range(-PAD, w + PAD):
            ii, jj = i % w, min(max(j, 0), h - 1)
            g = wood_gray(img, along_of(ii, jj), across_of(ii, jj), tile)
            shade, dark, bump = 1.0, 1.0, GRAIN_BUMP * (g / mean - 1)
            if boards_of:
                b = boards_of(ii, jj)
                board = int(math.floor(b))
                f = b - board
                shade = 1 + 0.06 * (((board * 2654435761 + seed) % 1000) / 500.0 - 1)
                seam = min(f, 1 - f) * board_px  # pixels to the nearer seam
                dark = 0.45 if seam < 1 else 0.75 if seam < 2 else 1.0
                bump += CROWN * board_px * 4 * f * (1 - f) - GROOVE * max(0.0, 2 - seam)
            if relief:
                lift, light = relief(ii, jj)
                bump, dark = bump + lift, dark * light
            height[(j + PAD) * W + i + PAD] = bump
            x, y = x0 + i, y0 + j
            if 0 <= x < ATLAS and 0 <= y < ATLAS:
                color.set(x, y, tuple(min(1.0, (0.5 + 0.5 * g / mean) * tint[q] * shade * dark) for q in range(3)) + (1.0,))
    write_normals(normal, rect, height)


def write_normals(normal, rect, height):
    """An island's normal map, its padding too, from height (pixels, the padded island's rows)."""
    x0, y0, w, h = rect
    W, H = w + 2 * PAD, h + 2 * PAD
    at = lambda a, b: height[min(max(b, 0), H - 1) * W + min(max(a, 0), W - 1)]
    for j in range(H):
        for i in range(W):
            x, y = x0 - PAD + i, y0 - PAD + j
            if not (0 <= x < ATLAS and 0 <= y < ATLAS):
                continue
            # tangent space: +x along u, +y along v, which is up the image
            nx, ny = -(at(i + 1, j) - at(i - 1, j)) / 2, (at(i, j + 1) - at(i, j - 1)) / 2
            ln = math.sqrt(nx * nx + ny * ny + 1)
            normal.set(x, y, (nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, 1 / ln * 0.5 + 0.5, 1.0))


def _rnd(a, b, k, seed):
    """A repeatable number in 0..1 for cell (a, b), channel k."""
    return (((a * 73856093) ^ (b * 19349663) ^ (k * 83492791) ^ seed) % 10007) / 10007.0


# Carved bands: raised lines, polylines in a cell 2 wide and 1 tall (the band's height), between
# frame lines along its edges, repeated around.
def _ring(cx, cy, r):
    return [(cx + r * math.cos(math.pi * k / 8), cy + r * math.sin(math.pi * k / 8)) for k in range(17)]


KEY = [(0.1, 0.16), (0.9, 0.16), (0.9, 0.84), (0.1, 0.84), (0.1, 0.34), (0.7, 0.34), (0.7, 0.66), (0.3, 0.66), (0.3, 0.5), (0.5, 0.5)]
DISC_MOTIF = [KEY, [(1.08, 0.16), (1.92, 0.84)], [(1.08, 0.84), (1.92, 0.16)],
              [(1.5, 0.26), (1.74, 0.5), (1.5, 0.74), (1.26, 0.5), (1.5, 0.26)]]
STOOL_MOTIF = [KEY, _ring(1.5, 0.5, 0.34), _ring(1.5, 0.5, 0.16)]
FRAME = [[(-0.1, 0.04), (2.1, 0.04)], [(-0.1, 0.96), (2.1, 0.96)]]
CARVE_DEPTH, CARVE_LIGHT = 4.0, 0.55  # a carving's lines' height in pixels; its recesses' light


def carving(motif, cols, rows, width=0.055, soft=0.035):
    """A motif's raised lines over one repeat, rows x cols heights 0 to 1, edges softened."""
    return line_mask(motif + FRAME, cols, rows, 2.0, width, soft)


def band_relief(rect, repeats, top, bottom, motif):
    """A carving for paint_wood: motif repeated across the island's width, between its rows top
    and bottom."""
    w, band = rect[2], bottom - top
    period = w / repeats
    cols, rows = max(4, round(period)), max(4, round(band))
    lines = carving(motif, cols, rows)

    def relief(i, j):
        if not top <= j < bottom:
            return 0.0, 1.0
        h = lines[min(rows - 1, int((j - top) / band * rows))][min(cols - 1, int(i % period / period * cols))]
        return CARVE_DEPTH * h, CARVE_LIGHT + (1 - CARVE_LIGHT) * h
    return relief


def facets(rect, cw, ch, tilt, seed):
    """Adze facets for paint_wood: cells about cw by ch pixels (a whole number across, so they
    wrap), each a plane tilted up to tilt (pixels of height a pixel) its own way."""
    w, h = rect[2], rect[3]
    nx, ny = max(1, round(w / cw)), max(1, round(h / ch))
    cw, ch = w / nx, h / ny
    rnd = lambda a, b, k: _rnd(a, b, k, seed)

    def relief(i, j):
        ci, cj = int(i // cw), int(j // ch)
        best = None
        for a in (ci - 1, ci, ci + 1):
            for b in (cj - 1, cj, cj + 1):
                aa = a % nx
                px, py = (a + 0.2 + 0.6 * rnd(aa, b, 1)) * cw, (b + 0.2 + 0.6 * rnd(aa, b, 2)) * ch
                d = ((i - px) / cw) ** 2 + ((j - py) / ch) ** 2
                if best is None or d < best[0]:
                    best = (d, aa, b, px, py)
        _, a, b, px, py = best
        return (rnd(a, b, 3) * 2 - 1) * tilt * (i - px) + (rnd(a, b, 4) * 2 - 1) * tilt * (j - py), 1.0
    return relief


def value_noise(nx, seed):
    """Smooth noise 0 to 1, f(x, y) in cells of a grid nx cells across (wrapping across)."""
    def f(x, y):
        a, b = math.floor(x), math.floor(y)
        fx, fy = x - a, y - b
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        g = lambda i, j: _rnd(i % nx, j, 7, seed)
        top = g(a, b) * (1 - sx) + g(a + 1, b) * sx
        return top * (1 - sy) + (g(a, b + 1) * (1 - sx) + g(a + 1, b + 1) * sx) * sy
    return f


def combine(*reliefs):
    """Reliefs together: their heights added, their lights multiplied."""
    def relief(i, j):
        lift, light = 0.0, 1.0
        for r in reliefs:
            a, b = r(i, j)
            lift, light = lift + a, light * b
        return lift, light
    return relief


def unevenness(rect, cell, height, seed, tone=0.08):
    """A relief: gentle unevenness, smooth noise about cell pixels across (and half that, a
    little) up to height pixels, the color up to tone lighter or darker with it."""
    w = rect[2]
    nx = max(1, round(w / cell))
    big, small = value_noise(nx, seed), value_noise(2 * nx, seed + 1)
    k = nx / w

    def relief(i, j):
        n = 0.7 * big(i * k, j * k) + 0.3 * small(2 * i * k, 2 * j * k)
        return height * n, 1 + tone * (2 * n - 1)
    return relief


def walk(x, y, angle, length, step, wiggle, seed):
    """A crack's path: from (x, y) length pixels, turning up to wiggle radians each step."""
    pts = [(x, y)]
    for k in range(max(1, int(length / step))):
        angle += (_rnd(k, 3, 9, seed) * 2 - 1) * wiggle
        x, y = x + math.cos(angle) * step, y + math.sin(angle) * step
        pts.append((x, y))
    return pts


def cracks(rect, lines, width=1.6, depth=2.5, dark=0.5):
    """A relief: cracks along lines (polylines in the island's pixels, wrapping across), widest
    at their starts and thinning to their ends, depth pixels deep and dark times darker."""
    w = rect[2]
    mask = {}
    for line in lines:
        total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line, line[1:])) or 1
        done = 0.0
        for a, b in zip(line, line[1:]):
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            steps = max(1, int(seg * 2))
            for k in range(steps + 1):
                t = k / steps
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                r = width / 2 * max(0.2, 1 - (done + seg * t) / total)
                for jj in range(int(y - r - 1), int(y + r + 2)):
                    for ii in range(int(x - r - 1), int(x + r + 2)):
                        m = min(1.0, max(0.0, r + 0.5 - math.hypot(ii + 0.5 - x, jj + 0.5 - y)))
                        key = (ii % w, jj)
                        if m > mask.get(key, 0.0):
                            mask[key] = m
            done += seg

    def relief(i, j):
        m = mask.get((i, j), 0.0)
        return -depth * m, 1 - dark * m
    return relief


def checks(rect, count, reach, seed, step=2.0):
    """Cracks running in from a round island's edge toward its middle, count of them, each
    reaching up to reach of the way in."""
    w, h = rect[2], rect[3]
    cx, cy, R = w / 2, h / 2, min(w, h) / 2
    out = []
    for k in range(count):
        a = 2 * math.pi * (k + _rnd(k, 1, 11, seed)) / count
        length = R * reach * (0.5 + 0.5 * _rnd(k, 2, 11, seed))
        out.append(walk(cx + math.cos(a) * R * 0.97, cy + math.sin(a) * R * 0.97, a + math.pi, length, step, 0.3, seed + k))
    return out


def line_mask(motif, cols, rows, span, width, soft):
    """Polylines (x 0 to span, y 0 to 1 down) as rows x cols coverage 0 to 1, edges softened;
    each segment drawn only over its own box."""
    out = [[0.0] * cols for _ in range(rows)]
    sx, sy = cols / span, rows  # pixels per unit
    reach = width + soft
    for line in motif:
        for a, b in zip(line, line[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ll = (dx * dx + dy * dy) or 1
            for j in range(max(0, int((min(a[1], b[1]) - reach) * sy)), min(rows, int((max(a[1], b[1]) + reach) * sy) + 1)):
                y = (j + 0.5) / sy
                row = out[j]
                for i in range(max(0, int((min(a[0], b[0]) - reach) * sx)), min(cols, int((max(a[0], b[0]) + reach) * sx) + 1)):
                    x = (i + 0.5) / sx
                    t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / ll))
                    m = (width - math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)) / soft + 0.5
                    if m > row[i]:
                        row[i] = min(1.0, m)
    return out


def hexcolor(c):
    return [int(c[1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)]


def paint_mat(color, normal, rect, v, density):
    """The mat seen from above: a plain weave of matStrip strips, each over one and under the
    next, toned a little apart, crowned, with dark gaps; its border a herringbone braid of the
    dark straw, two rows leaning apart, bound dark at its outer edge."""
    x0, y0, w, h = rect
    R, b = v["matDiameter"] / 2, min(v["matBorder"], v["matDiameter"] / 2)
    strip = v["matStrip"]
    light, darkc = hexcolor(SWATCHES[STRAW]), hexcolor(SWATCHES[STRAW_DARK])
    braids = max(8, round(2 * math.pi * (R - b / 2) / strip))
    W, H = w + 2 * PAD, h + 2 * PAD
    height = array("f", [0.0]) * (W * H)
    for j in range(-PAD, h + PAD):
        for i in range(-PAD, w + PAD):
            x = (min(max(i, 0), w - 1) + 0.5) / w * 2 * R - R
            z = (min(max(j, 0), h - 1) + 0.5) / h * 2 * R - R
            r = math.hypot(x, z)
            if r < R - b:
                a, c = x / strip, z / strip
                ia, ic = math.floor(a), math.floor(c)
                over = (ia + ic) % 2 == 0  # the strip along x is on top
                across, along, index = (c - ic, a - ia, ic) if over else (a - ia, c - ic, ia + 1000)
                base, gap = light, min(across, 1 - across) < 0.07
            else:
                q = (R - r) / b  # 0 at the edge, 1 inside
                u = math.atan2(z, x) / (2 * math.pi) * braids + (q * b / strip if q < 0.5 else -q * b / strip)
                across, along, index = u - math.floor(u), 0.5, math.floor(u) + (5000 if q < 0.5 else 7000)
                base, gap = darkc, min(across, 1 - across) < 0.08 or abs(q - 0.5) < 0.03 or q < 0.08
            crown = 1 - (2 * across - 1) ** 2
            tone = 1 + 0.08 * (_rnd(index, 0, 13, 3) * 2 - 1)
            fiber = 0.96 + 0.04 * math.sin(across * 2 * math.pi * 3)
            shade = tone * fiber * (0.6 if gap else 0.85 + 0.15 * crown) * (0.9 + 0.1 * math.sin(math.pi * along))
            height[(j + PAD) * W + i + PAD] = 0.0 if gap else 1.8 * crown * (0.7 + 0.3 * math.sin(math.pi * along))
            xx, yy = x0 + i, y0 + j
            if 0 <= xx < ATLAS and 0 <= yy < ATLAS:
                color.set(xx, yy, tuple(min(1.0, base[q] * shade) for q in range(3)) + (1.0,))
    write_normals(normal, rect, height)


BED_BROWN, BED_GREEN = "#7a4a32", "#6f8a4a"


def paint_bed(color, normal, rect, v):
    """The hammock's bed, its length across the island: cream silk, green along its long edges,
    a brown hexagon round a green one in its middle, diamonds either side; a fine weave."""
    x0, y0, w, h = rect
    span = v["bedLength"] / v["bedWidth"]  # the island's width in bed widths
    c = span / 2
    hexagon = lambda s: [(c - 0.55 * s, 0.5), (c - 0.3 * s, 0.5 - 0.3 * s), (c + 0.3 * s, 0.5 - 0.3 * s), (c + 0.55 * s, 0.5),
                         (c + 0.3 * s, 0.5 + 0.3 * s), (c - 0.3 * s, 0.5 + 0.3 * s), (c - 0.55 * s, 0.5)]
    diamond = lambda x, y, s: [(x - s, y), (x, y - s), (x + s, y), (x, y + s), (x - s, y)]
    brown = [hexagon(1.0), diamond(c, 0.5, 0.07), diamond(c - 0.85, 0.5, 0.08), diamond(c + 0.85, 0.5, 0.08)]
    green = [hexagon(0.6), [(0, 0.15), (span, 0.15)], [(0, 0.85), (span, 0.85)]] + \
        [diamond(c + sx * 0.8, y, 0.05) for sx in (-1, 1) for y in (0.3, 0.7)] + [diamond(c + sx * 1.0, 0.5, 0.05) for sx in (-1, 1)]
    mb, mg = (line_mask(m, w, h, span, 0.025, 0.02) for m in (brown, green))
    cream, br, gr = hexcolor(SWATCHES[SILK]), hexcolor(BED_BROWN), hexcolor(BED_GREEN)
    W, H = w + 2 * PAD, h + 2 * PAD
    height = array("f", [0.0]) * (W * H)
    for j in range(-PAD, h + PAD):
        for i in range(-PAD, w + PAD):
            ii, jj = min(max(i, 0), w - 1), min(max(j, 0), h - 1)
            edge = 1.0 if min(jj + 0.5, h - jj - 0.5) / h < 0.07 else 0.0
            g, b_ = max(mg[jj][ii], edge), mb[jj][ii]
            col = [cream[q] * (1 - g) + gr[q] * g for q in range(3)]
            col = [col[q] * (1 - b_) + br[q] * b_ for q in range(3)]
            weave = math.sin(i * math.pi * 2 / 3) * math.sin(j * math.pi * 2 / 3)
            height[(j + PAD) * W + i + PAD] = 0.35 * weave
            xx, yy = x0 + i, y0 + j
            if 0 <= xx < ATLAS and 0 <= yy < ATLAS:
                color.set(xx, yy, tuple(min(1.0, col[q] * (0.97 + 0.03 * weave)) for q in range(3)) + (1.0,))
    write_normals(normal, rect, height)


def paint_robe(color, normal, rect, v):
    """The robe from the front (its back the same): brown, green swirls on its chest, lower body
    and sleeves, a green collar down to its sash, green cuffs, a gray band at its hem; fine
    cloth, and soft folds deepening toward the hem."""
    x0, y0, w, h = rect
    L, span = v["robeLength"], robe_span(v)
    wide = span / L  # the island's width in robe lengths

    def spiral(cx, cy, r, turns=1.6):
        # cx in meters from the middle, cy in meters up; to the mask's units (robe lengths, down)
        return [((cx + r * (1 - t) * math.cos(2 * math.pi * turns * t)) / L + wide / 2,
                 1 - (cy + r * (1 - t) * math.sin(2 * math.pi * turns * t)) / L) for t in (k / 24 for k in range(25))]
    swirls = [spiral(sx * 0.09, 0.30, 0.045) for sx in (-1, 1)] + [spiral(sx * 0.12, 0.12, 0.04) for sx in (-1, 1)] + \
        [spiral(sx * (span / 2 - 0.07), L - v["sleeveHeight"] / 2, 0.03) for sx in (-1, 1)]
    collar = [[(wide / 2 - 0.07 / L, 0), (wide / 2, 0.45)], [(wide / 2 + 0.07 / L, 0), (wide / 2, 0.45)]]
    ms, mc = line_mask(swirls, w, h, wide, 0.02, 0.015), line_mask(collar, w, h, wide, 0.04, 0.015)
    base, green, trim, gray = hexcolor(SWATCHES[ROBE]), hexcolor(SWATCHES[ROBE_GREEN]), hexcolor("#4f6a3a"), hexcolor("#7d7f76")
    W, H = w + 2 * PAD, h + 2 * PAD
    height = array("f", [0.0]) * (W * H)
    for j in range(-PAD, h + PAD):
        for i in range(-PAD, w + PAD):
            ii, jj = min(max(i, 0), w - 1), min(max(j, 0), h - 1)
            x, y = (ii + 0.5) / w * span - span / 2, L * (1 - (jj + 0.5) / h)
            col = base
            for m, c in ((ms[jj][ii], green), (mc[jj][ii], trim)):
                col = [col[q] * (1 - m) + c[q] * m for q in range(3)]
            if abs(x) > span / 2 - 0.03:
                col = trim
            if y < 0.05:
                col = gray
            elif y < 0.062:
                col = trim
            cloth = 0.25 * math.sin(i * math.pi * 2 / 3) * math.sin(j * math.pi * 2 / 3)
            fold = 0.8 * math.sin(x * 2 * math.pi / 0.09 + 2 * math.sin(x * 23)) * max(0.0, 1 - y / (0.7 * L))
            height[(j + PAD) * W + i + PAD] = cloth + fold
            xx, yy = x0 + i, y0 + j
            if 0 <= xx < ATLAS and 0 <= yy < ATLAS:
                color.set(xx, yy, tuple(min(1.0, col[q] * (0.95 + 0.2 * cloth)) for q in range(3)) + (1.0,))
    write_normals(normal, rect, height)


LUMP_HEIGHT, FUZZ = 2.5, 0.15  # the cocoon's lumps' height and its fuzz's, in pixels


def paint_lumps(color, normal, rect, swatch, cell, seed):
    """The cocoon's silk: the island its swatch's flat color, and in the normal map rounded lumps
    about cell pixels across, rounded on top with creases between (F2 - F1 of a jittered grid of
    cells, a whole number across, so they wrap), half-size lumps over them at 25%, and a fine
    fuzz."""
    x0, y0, w, h = rect
    rgb = tuple(int(SWATCHES[swatch][1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)) + (1.0,)

    def worley(i, j, nx, ny, s):
        cw, ch = w / nx, h / ny
        ci, cj = int(i // cw), int(j // ch)
        f1 = f2 = 9.0
        for a in (ci - 1, ci, ci + 1):
            for b in (cj - 1, cj, cj + 1):
                aa = a % nx
                d = math.hypot(i / cw - a - _rnd(aa, b, 1, s), j / ch - b - _rnd(aa, b, 2, s))
                if d < f1:
                    f1, f2 = d, f1
                elif d < f2:
                    f2 = d
        e = min(1.0, (f2 - f1) * 1.5)
        return 1 - (1 - e) * (1 - e)  # rounded on top, creased between
    nx, ny = max(1, round(w / cell)), max(1, round(h / cell))
    W, H = w + 2 * PAD, h + 2 * PAD
    height = array("f", [0.0]) * (W * H)
    for j in range(-PAD, h + PAD):
        for i in range(-PAD, w + PAD):
            ii, jj = i % w, min(max(j, 0), h - 1)
            lump = worley(ii + 0.5, jj + 0.5, nx, ny, seed) + 0.25 * worley(ii + 0.5, jj + 0.5, 2 * nx, 2 * ny, seed + 1)
            height[(j + PAD) * W + i + PAD] = LUMP_HEIGHT * lump + FUZZ * (_rnd(ii, jj, 5, seed) * 2 - 1)
            x, y = x0 + i, y0 + j
            if 0 <= x < ATLAS and 0 <= y < ATLAS:
                color.set(x, y, rgb)
    write_normals(normal, rect, height)


def textures(v):
    """The swatches, a little grain in each; the wood islands; the leaf; a flat normal elsewhere."""
    color, normal = modl.Image(ATLAS, ATLAS), modl.Image(ATLAS, ATLAS, (0.5, 0.5, 1.0, 1.0))
    for i, hexcolor in enumerate(SWATCHES):
        rgb = [int(hexcolor[1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)]
        x0, y0 = (i % 4) * CELL, (i // 4) * CELL
        for y in range(y0, y0 + CELL):
            for x in range(x0, x0 + CELL):
                g = 0.96 + 0.08 * (((x * 73856093) ^ (y * 19349663)) % 1000 / 1000.0)
                color.set(x, y, (rgb[0] * g, rgb[1] * g, rgb[2] * g, 1.0))
    isl = islands(v)
    d, fd, cd, tile = isl["density"], isl["floorDensity"], isl["carveDensity"], v["woodTile"]

    def around(rect, density):
        """Meters across per pixel along an island's width, stretched so whole tiles go round."""
        m = rect[2] / density
        return max(1, round(m / tile)) * tile / m / density

    staves, count = isl["staves"], stave_count(v)
    k = around(staves, d)
    paint_wood(color, normal, staves, lambda i, j: (staves[3] - j) / d, lambda i, j: i * k, WOOD_MID, tile, d, 17,
               lambda i, j: i / staves[2] * count, staves[2] / count)
    lid = isl["lid"]
    lid_boards = max(2, round(lid[3] / d / v["staveWidth"]))
    paint_wood(color, normal, lid, lambda i, j: i / d, lambda i, j: j / d, WOOD_DARK, tile, d, 29,
               lambda i, j: j / lid[3] * lid_boards, lid[3] / lid_boards)
    # the floor's end grain: the grain laid round in rings (whole tiles around), wobbling a little
    floor, R = isl["floor"], v["discDiameter"] / 2

    def polar(i, j):
        x, z = (i + 0.5) / floor[2] * 2 * R - R, (j + 0.5) / floor[3] * 2 * R - R
        a = math.atan2(z, x)
        r = math.hypot(x, z)
        return a, r + 0.02 * math.sin(3 * a + 5 * r) + 0.012 * math.sin(7 * a - 3 * r)
    paint_wood(color, normal, floor, lambda i, j: polar(i, j)[0] / (2 * math.pi) * 16 * tile,
               lambda i, j: polar(i, j)[1], WOOD, tile, fd,
               relief=combine(unevenness(floor, 0.4 * fd, 2.0, 61), cracks(floor, checks(floor, 9, 0.55, 67))))
    # the rim: grain around, its side carved (its bevels plain)
    rim = isl["rim"]
    t, inset = v["discThickness"], min(v["rimInset"], v["discThickness"] / 2)
    bevel = round(inset * math.sqrt(2) / (2 * inset * math.sqrt(2) + t - 2 * inset) * rim[3])
    rim_repeat = rim[2] / cd
    k = around(rim, cd)
    paint_wood(color, normal, rim, lambda i, j: i * k, lambda i, j: j / cd, WOOD_DARK, tile, cd,
               relief=combine(band_relief(rim, max(1, round(rim_repeat / (2 * (t - 2 * inset)))), bevel, rim[3] - bevel, DISC_MOTIF),
                              unevenness(rim, 0.15 * cd, 2.0, 71)))
    # the stool: its edge carved all over; its seat and legs faceted
    edge = isl["seatEdge"]
    k = around(edge, cd)
    paint_wood(color, normal, edge, lambda i, j: i * k, lambda i, j: j / cd, WOOD_DARK, tile, cd,
               relief=combine(band_relief(edge, max(1, round(edge[2] / edge[3] / 2)), 0, edge[3], STOOL_MOTIF),
                              unevenness(edge, 0.08 * cd, 1.5, 73)))
    seat = isl["seat"]
    paint_wood(color, normal, seat, lambda i, j: i / d, lambda i, j: j / d, WOOD_MID, tile, d,
               relief=combine(facets(seat, 0.035 * d, 0.035 * d, 0.25, 5), cracks(seat, checks(seat, 3, 0.4, 79, 1.5), 1.2, 2.0)))
    for name, swatch in (("post", WOOD_DARK), ("leg", WOOD_MID)):  # grain along
        rect = isl[name]
        k = around(rect, d)
        paint_wood(color, normal, rect, lambda i, j, h=rect[3]: (h - j) / d, lambda i, j, k=k: i * k, swatch, tile, d,
                   relief=facets(rect, 0.03 * d, 0.08 * d, 0.25, 11) if name == "leg" else None)
    perch_rect = isl["perch"]
    k = around(perch_rect, d)
    knot = (round(perch_rect[3] * 0.84), round(perch_rect[3] * 0.96))
    paint_wood(color, normal, perch_rect, lambda i, j: j / d, lambda i, j: i * k, WOOD_MID, tile, d,
               relief=combine(unevenness(perch_rect, 0.05 * d, 1.2, 83), band_relief(perch_rect, 3, knot[0], knot[1], STOOL_MOTIF)))
    paint_leaf(color, normal, isl["leaf"])
    paint_lumps(color, normal, isl["cocoon"], COCOON, v["cocoonLump"] * isl["cocoonDensity"], 41)
    paint_mat(color, normal, isl["mat"], v, fd)
    paint_bed(color, normal, isl["bed"], v)
    paint_robe(color, normal, isl["robe"], v)
    return modl.TrimSheet(ATLAS, ATLAS, d), color, normal


VEIN, CRINKLE = 6.0, 1.5  # the leaf's veins' emboss (pixels per unit of brightness) and crinkle
VEIN_TONE, LEAF_CONTRAST, LEAF_EDGE = 3.0, 1.6, ("#7a5230", 0.18, 0.6)  # the edge: its brown, width, strength


def paint_leaf(color, normal, rect):
    """The beech leaf into its island, padding included: its brightness, against its mean,
    between the dark and light dried leaf swatches, LEAF_CONTRAST times as far apart; its veins
    (its brightness less its blur over 5 px) lighter by VEIN_TONE times them; browned toward its
    edges, as HutWeaver.png's leaves are (Ken, 2026-11-02: the leaf showed no texture). Outside
    its outline a pixel takes the nearest inside along its row, so the padding and edges carry
    no background. Its normal map embosses the veins (light, so raised) and crinkles it a little
    (smooth noise)."""
    src = leaf_source()
    img, (x0, y0, x1, y1), mean = src["img"], src["box"], src["mean"]
    lo, hi = ([int(SWATCHES[s][1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)] for s in (LEAF_DARK, LEAF))
    brown = hexcolor(LEAF_EDGE[0])
    ix, iy, iw, ih = rect
    W, H = iw + 2 * PAD, ih + 2 * PAD
    bright, edge = array("f", [0.0]) * (W * H), array("f", [0.0]) * (W * H)
    for j in range(-PAD, ih + PAD):
        ty = min(max(y0 + (j + 0.5) / ih * (y1 - y0), y0 + 0.5), y1 - 0.5)
        a, b = leaf_edges(ty)
        for i in range(-PAD, iw + PAD):
            tx = min(max(x0 + (i + 0.5) / iw * (x1 - x0), a + 0.5), b - 0.5)
            bright[(j + PAD) * W + i + PAD] = sum(img.sample(tx, ty)[:3]) / 3
            # how far in from its edge, as a share of the leaf's widest
            edge[(j + PAD) * W + i + PAD] = min(tx - a, b - tx) / (x1 - x0)
    # the blur: a box 11 px wide, by rows then columns
    R = 5
    rows = array("f", [0.0]) * (W * H)
    for j in range(H):
        for i in range(W):
            lo_, hi_ = max(0, i - R), min(W - 1, i + R)
            rows[j * W + i] = sum(bright[j * W + lo_:j * W + hi_ + 1]) / (hi_ - lo_ + 1)
    crinkle = unevenness(rect, 24, CRINKLE, 89, 0.0)
    height = array("f", [0.0]) * (W * H)
    for j in range(H):
        lo_, hi_ = max(0, j - R), min(H - 1, j + R)
        for i in range(W):
            blur = sum(rows[jj * W + i] for jj in range(lo_, hi_ + 1)) / (hi_ - lo_ + 1)
            g, vein = bright[j * W + i], bright[j * W + i] - blur
            height[j * W + i] = VEIN * vein + crinkle(i - PAD, j - PAD)[0]
            x, y = ix + i - PAD, iy + j - PAD
            if not (0 <= x < ATLAS and 0 <= y < ATLAS):
                continue
            f = min(max(0.5 + LEAF_CONTRAST * (g / mean - 1), 0.0), 1.2)
            c = [(lo[q] + (hi[q] - lo[q]) * f) * (1 + VEIN_TONE * vein) for q in range(3)]
            e = max(0.0, 1 - edge[j * W + i] / LEAF_EDGE[1]) ** 2 * LEAF_EDGE[2]
            color.set(x, y, tuple(min(1.0, max(0.0, c[q] * (1 - e) + brown[q] * e)) for q in range(3)) + (1.0,))
    write_normals(normal, rect, height)


def build(v, install_too=False, report=print):
    out = modl.HERE
    bs = assets(v, measure=True)
    names = set()
    for a in bs:
        for mesh in a.lods:
            modl.write_obj(os.path.join(out, mesh.name + ".obj"), mesh, FAMILY + ".mtl", MATERIAL)
            names.add(mesh.name)
        report(f"{a.name}: {a.size:.2f} m; " + ", ".join(f"LOD{k} {len(m.tris)} triangles" for k, m in enumerate(a.lods))
               + "; LOD1 from {:.0f} m ({:.1f} cm off), LOD2 from {:.0f} m ({:.1f} cm), culled at {:.0f} m".format(
                   a.distances[0], a.errors[0] * 100, a.distances[1], a.errors[1] * 100, a.distances[2]))
    modl.write_mtl(os.path.join(out, FAMILY + ".mtl"), MATERIAL, FAMILY)
    _, color, normal = textures(v)
    modl.write_png(os.path.join(out, FAMILY + "_tx.png"), color)
    modl.write_png(os.path.join(out, FAMILY + "_normal.png"), normal)
    report(f"{FAMILY}_tx.png, {FAMILY}_normal.png: {ATLAS}x{ATLAS}, {len(SWATCHES)} swatches, wood at {islands(v)['density']:.0f} px/m, the floor at {islands(v)['floorDensity']:.0f}")
    if not install_too:
        return []
    material = lambda tex, nrm: modl.material_yaml(modl.canopy_file(SOURCE_MATERIAL).decode(), MATERIAL, tex, nrm)
    return modl.install_assets(FAMILY, MATERIAL, bs, material, COLOR_META, NORMAL_META)


def main():
    unused = modl.unused_tags(tags(), VARS)
    if unused:
        print(f"note: tags not used yet: {', '.join(unused)}")
    written = build(values(), "--write" in sys.argv)
    if "--write" in sys.argv:
        print(f"Canopy Assets/Modl/{FAMILY}: {len(written)} files changed")


if __name__ == "__main__":
    main()
