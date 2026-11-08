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
- Detail (Ken, 2026-11-03: as the harvesters and ruins have, at every LOD): ModlHut's detail
  texture is Hut_detail.png, a seamless DETAIL_PX tile of fine fiber, tiled so a tile is
  detailTile where the atlas is at woodDensity (so the floor's is twice as coarse, carvings' and
  the cocoon's twice as fine, and it breaks at island seams; faint, it doesn't show). Canopy
  multiplies in linear light, so the tile is made there and stored sRGB, and the atlas is
  lightened by its mean. The hammock and the robe are silk, on ModlHutSilk (Ken: a second draw
  call is worth it, for now): glossy, its own 1024 px atlases HutSilk_tx and
  HutSilk_normal (the swatches in the same cells, so the sash, bars and cords map as before; the
  robe beside them at silkDensity, the bed below at bedDensity), and HutSilk_detail.png, a 2/2
  twill of WEAVE_THREADS threads each way, silkThread apart where the atlas is at silkDensity.
  The hammock's ModlHutHammock and the disc's ModlHutDisc are their own. Each material's
  Canopy/General properties are live vars (SHADERS groups them in Tweak's list): its normal
  strength, gloss and brightness (ModlHut's normalStrength, gloss, brightness; the others'
  prefixed silk (the robe's), hammock and disc).
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
- Painted island by island in parallel and cached (modl.paint_islands; WOOD_TASKS, SILK_TASKS),
  each painter on numpy arrays, its results the same to the bit as the per-pixel painters were
  (Claude, 2026-11-04: checked against the last build's atlases).
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
  1210 a radian); the errors are kept and only measured again with --measure (Ken, 2026-11-04:
  let them drift until I notice), or for a model never measured. A model is culled where it
  is cullPixels tall, at most cullDistance, except the disc, roof, posts and perches, drawn to
  farCullDistance. A level's lowest screen height is size / (2 d) at the next level's distance
  (the last at the cull distance), size the model's largest extent, as Unity's LODGroup and
  layout measure it.

  python3 obj/hut.py           writes obj/<Name>_LOD*.obj, Hut.mtl and the Hut atlases
  python3 obj/hut.py --write   also installs them into Canopy's Assets/Modl/Hut
Layout's Tweak drives it through obj/serve.py.
"""

import json
import math
from array import array
import os
import subprocess
import sys

import numpy as np

import modl
from normals import chamfer

FAMILY = "Hut"
MATERIAL = "ModlHut"
SILK_ATLAS, SILK_MATERIAL = "HutSilk", "ModlHutSilk"  # the silk's own atlases and material
SILK_MODELS = {"Hammock", "RobeFemale"}
HAMMOCK_DETAIL, HAMMOCK_MATERIAL = "HutHammock", "ModlHutHammock"  # the hammock's own detail texture, so its own material
DISC_MATERIAL = "ModlHutDisc"  # the disc's: the family's atlases, Amber's detail texture (DETAIL_META's own)
# Each material's live vars, grouped in Tweak's list under one row, <name>Shaders (serve.py's shaders)
SHADERS = {MATERIAL: "hut", SILK_MATERIAL: "robe", HAMMOCK_MATERIAL: "hammock", DISC_MATERIAL: "disc"}
DOC = os.path.join(modl.DOCS, "models", "Hut Models.md")
HEADING = "Modl Hut"
G = dict(geometry=True)
S = dict(live=True, step=0.01)  # a shader's property: live, in hundredths
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
    "perchPoke": modl.Var(**G, min=0, max=0.3),
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
    "robeLength": modl.Var(**G, min=0.1, max=2), "robeDepth": modl.Var(**G, min=0.02, max=0.5),
    "sashTop": modl.Var(**G, min=0.02, max=2), "pleatDepth": modl.Var(**G, min=0, max=0.05),
    "robeTrim": modl.Var(geometry=True, textures=True, min=0.002, max=0.2),
    "pegLength": modl.Var(**G, min=0.02, max=0.5), "pegRadius": modl.Var(**G, min=0.005, max=0.2),
    "pegKnob": modl.Var(**G, min=0.005, max=0.3),
    "cocoonLength": modl.Var(**G, min=0.01, max=1), "cocoonWidth": modl.Var(**G, min=0.01, max=1),
    "woodTile": modl.Var(geometry=True, textures=True, min=0.1, max=10),
    "woodDensity": modl.Var(geometry=True, textures=True, min=32, max=1024),
    "floorDensity": modl.Var(geometry=True, textures=True, min=16, max=1024),
    "carveDensity": modl.Var(geometry=True, textures=True, min=32, max=2048),
    "cocoonDensity": modl.Var(geometry=True, textures=True, min=32, max=2048),
    "cocoonLump": modl.Var(textures=True, min=0.002, max=0.2),
    "ovenStone": modl.Var(textures=True, min=0.03, max=1), "ovenBlock": modl.Var(textures=True, min=0.03, max=1),
    "stoneRelief": modl.Var(textures=True, min=0, max=10), "stoneRough": modl.Var(textures=True, min=0, max=5),
    "floorRough": modl.Var(textures=True, min=0, max=5), "discDetailTile": modl.Var(live=True, min=0.01, max=4),
    "gloss": modl.Var(**S, min=0, max=1), "discGloss": modl.Var(**S, min=0, max=1), "hammockGloss": modl.Var(**S, min=0, max=1),
    "brightness": modl.Var(**S, min=0, max=10), "discBrightness": modl.Var(**S, min=0, max=10),
    "silkBrightness": modl.Var(**S, min=0, max=10), "hammockBrightness": modl.Var(**S, min=0, max=10),
    "hammockNormalStrength": modl.Var(**S, min=0, max=10),
    "staveWidth": modl.Var(textures=True, min=0.02, max=1),
    "detailStrength": modl.Var(**S, min=0, max=0.5), "detailTile": modl.Var(live=True, min=0.01, max=4),
    "silkGloss": modl.Var(**S, min=0, max=1),
    "normalStrength": modl.Var(**S, min=0, max=10), "discNormalStrength": modl.Var(**S, min=0, max=10),
    "silkNormalStrength": modl.Var(**S, min=0, max=10),
    "silkDensity": modl.Var(geometry=True, textures=True, min=64, max=4096),
    "bedDensity": modl.Var(geometry=True, textures=True, min=64, max=4096),
    "silkThread": modl.Var(live=True, min=0.0002, max=0.01), "silkStrength": modl.Var(**S, min=0, max=0.5),
    "slubRelief": modl.Var(textures=True, min=0, max=10), "slubScale": modl.Var(textures=True, min=0.05, max=4),
    "robeTile": modl.Var(textures=True, min=0.02, max=2),
    "ghichaTile": modl.Var(rebuild=True, min=0.005, max=0.5), "ghichaStrength": modl.Var(**S, min=0, max=1),
    "ghichaRelief": modl.Var(textures=True, min=0, max=10),
    "roundSides": modl.Var(**G, min=4, max=64), "minSides": modl.Var(**G, min=3, max=16),
    "lodError": modl.Var(**G, min=0.25, max=20), "cullPixels": modl.Var(**G, min=1, max=100),
    "cullDistance": modl.Var(**G, min=1, max=1000), "farCullDistance": modl.Var(**G, min=1, max=2000),
}
SOURCE_MATERIAL = "Assets/Materials/StructBases.mat"
COLOR_META, NORMAL_META = "Assets/Texture/StructBases_color.png", "Assets/Texture/StructBases_nmap.png"
WOOD_SOURCE = "Assets/Active/Hut Shehroze v3 126/WoodDesatD.jpg"
LEAF_SOURCE = "Assets/Texture/LeafBeech.png"
DETAIL_META = "Assets/Texture/RockDetailFaint.png"  # a detail texture's import settings
VIDS = os.path.join(os.path.dirname(modl.DOCS), "vids")  # gptviz's images
BED_FABRIC, ROBE_FABRIC, ROBE_IMAGE, SASH_IMAGE = "HammockFabric.png", "RobeFemaleFabric.png", "RobeFemale.png", "RobeFemaleSash.png"
# RobeFemaleFabric.png's parts, (x, y, w, h) as fractions of it: its left panel is the robe's and
# its right the sash's (Ken, 2026-11-04); each panel has a band across its middle
ROBE_BROCADE, ROBE_BAND = (0.0, 0.093, 0.49, 0.333), (0.0, 0.431, 0.49, 0.139)
SASH_BROCADE, SASH_BAND = (0.5, 0.09, 0.5, 0.335), (0.5, 0.433, 0.5, 0.137)
# Sample Ghicha.jpg's left fold, (x, y, w, h) as fractions of it: flat, its streaks upright; its
# tile in pixels (as the part is shaped, four times as tall as wide)
GHICHA, GHICHA_CROP, GHICHA_PX = "Sample Ghicha.jpg", (0.007, 0.225, 0.264, 0.694), (256, 1024)
DETAIL_PX, WEAVE_THREADS = 256, 16  # the fiber's tile in pixels; the weave's threads across its tile
SWATCHES = ["#c08a50", "#8a5a30", "#9a5f30", "#b98a55",   # wood light, dark, mid; leaf
            "#a07040", "#3a3a3c", "#141414", "#d8cfae",   # leaf dark; stone; black; silk
            "#6f8a4a", "#a07a48", "#6b5a3a", "#5d6b3a",   # silk green; cord; robe brown, green
            "#4aa0b0", "#f2f0ea", "#c09a60", "#8a6a40"]   # sash blue; cocoon; straw, straw dark
(WOOD, WOOD_DARK, WOOD_MID, LEAF, LEAF_DARK, STONE, BLACK, SILK, SILK_GREEN, CORD,
 ROBE, ROBE_GREEN, SASH, COCOON, STRAW, STRAW_DARK) = range(16)
ATLAS, CELL, PAD = 1024, 64, 8
RIM_REPS = 8  # the disc's rim wraps its island this many times around


def tags():
    modl.check_sources(DOC, HEADING, ["Canopy " + p for p in (SOURCE_MATERIAL, COLOR_META, NORMAL_META, WOOD_SOURCE, LEAF_SOURCE, DETAIL_META)] + [BED_FABRIC, ROBE_FABRIC, ROBE_IMAGE, SASH_IMAGE, GHICHA])
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


def tube(path, radii, sides, swatch, caps=True, uvs=None, cap_uvs=None, domes=(0.0, 0.0)):
    """A tube along path (points), radius radii[i] at path[i], smooth around, capped; with uvs,
    uvs(along, around) (each 0 to 1, along by length from the path's start) maps its sides, and
    with cap_uvs, cap_uvs(end, around) (end 0 its start, 1 its end) its caps' rims (their middles
    cap_uvs(end, None)). A cap whose domes[end] isn't 0 is a fan, its middle standing out that far."""
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
            end = 0 if sign < 0 else 1
            rim = [(q, n) + ((cap_uvs(end, j / sides),) if cap_uvs else ()) for j, (q, _) in enumerate(ring)]
            if not domes[end]:
                part.faces.append((rim, swatch))
                continue
            tip = tuple(p[q] + n[q] * domes[end] for q in range(3))
            for j in range(sides):
                a, b = rim[j], rim[(j + 1) % sides]
                fn = unit(cross(sub(a[0], tip), sub(b[0], tip)))
                fn = fn if sum(fn[q] * n[q] for q in range(3)) > 0 else tuple(-x for x in fn)
                corners = [(tip, fn) + ((cap_uvs(end, None),) if cap_uvs else ()), (a[0], fn) + a[2:], (b[0], fn) + b[2:]]
                part.faces.append((corners if sign > 0 else corners[::-1], swatch))
    return part


def box(center, size, swatch, bottom=None, top=None, uvs=None):
    """A box (or with bottom and top (w, d) a frustum) centered at center; with uvs, uvs(p, n)
    maps each corner (n its face's outward normal)."""
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
        part.faces.append(([(p, n) + ((uvs(p, n),) if uvs else ()) for p in f], swatch))
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
    isl = islands(v)
    px, py, pw, ph = isl["perch"]
    # its ends the floor's end grain (Ken, 2026-11-04: reuse the disc there): a circle round the
    # floor's middle, PERCH_RINGS of its radius, rings and all, each end turned its own way
    fx, fy, fw, fh = isl["floor"]

    def cap(end, around):
        a = 2 * math.pi * (around or 0) + 1.7 * end
        k = PERCH_RINGS * radii[-end] / max(radii) * (around is not None)
        return ((fx + fw * (0.5 + 0.5 * k * math.cos(a))) / ATLAS, 1 - (fy + fh * (0.5 + 0.5 * k * math.sin(a))) / ATLAS)
    return tube(path, radii, (8, 6, 4)[level], WOOD_MID,
                uvs=lambda along, around: ((px + around * pw) / ATLAS, 1 - (py + along * ph) / ATLAS), cap_uvs=cap,
                domes=(0.0, v["perchPoke"]))


PERCH_RINGS = 0.5  # the share of the floor's radius a perch's end shows


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
    bx, by, bw, bh = silk_islands(v)["bed"]
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


OVEN_REPS, SHELF_THICK = 4, 0.08  # the oven's stone wraps its islands four times around (twice, the atlas drops to 230 px/m); the shelf's thickness


def oven_profile(v, level):
    """The oven's lathe profile and how many segments its dome has (segment 1 is its base's wall,
    2 on its dome, then the smoke ring's wall, rim, inside and floor)."""
    R, base, dome, fr, fh = v["ovenRadius"], v["ovenBaseHeight"], v["domeHeight"], v["flueRadius"], v["flueHeight"]
    n = max(2, 6 >> level)
    prof = [(0, 0), (R, 0), (R, base)]
    for i in range(1, n + 1):
        a = math.pi / 2 * i / n
        r = max(fr, R * math.cos(a))
        prof.append((r, base + dome * math.sin(a)))
        if r <= fr:
            break
    domes = len(prof) - 3
    top = prof[-1][1]
    prof += [(fr, top + fh), (fr * 0.6, top + fh), (fr * 0.6, top + fh * 0.5), (0, top + fh * 0.5)]
    return prof, domes


def profile_length(prof, k0, k1):
    """Segments k0 to k1 of a profile: their length and r(f), the radius f of the way up them by
    length."""
    seg = [(prof[k], prof[k + 1], math.hypot(prof[k + 1][0] - prof[k][0], prof[k + 1][1] - prof[k][1])) for k in range(k0, k1 + 1)]
    total = sum(m for _, _, m in seg)

    def r(f):
        left = f * total
        for n, (a, b, m) in enumerate(seg):
            if left <= m or n == len(seg) - 1:
                t = min(1.0, left / m) if m else 0.0
                return a[0] + (b[0] - a[0]) * t
            left -= m
    return total, r


def oven(v, level):
    """As Oven.png: a dark stone dome on a base, its smoke ring on top, mapped round in islands of
    stone (paint_oven); its mouth and the storage space below its hearth shelf black; the shelf
    of slabs and the bench of wood mapped by their faces."""
    R, base = v["ovenRadius"], v["ovenBaseHeight"]
    prof, domes = oven_profile(v, level)
    isl = islands(v)
    kf = 2 + domes  # the smoke ring's wall
    maps = {1: ("wrap", isl["ovenBase"], OVEN_REPS, 1, 1)}
    maps.update({k: ("wrap", isl["ovenDome"], OVEN_REPS, 2, kf - 1) for k in range(2, kf)})
    maps.update({k: ("wrap", isl["ovenFlue"], OVEN_REPS, kf, kf + 2) for k in range(kf, kf + 3)})
    part = lathe(prof, sides_at(v, level), [STONE] * (kf + 3) + [BLACK], band(prof, maps))
    mw, mh = v["mouthWidth"], v["mouthHeight"]
    part.add(box((0, base + 0.04 + mh / 2, R * 0.93), (mw, mh, 0.12), BLACK))
    sw, sd, sz = v["shelfWidth"], v["shelfDepth"], R * 0.95
    part.add(box((0, base, sz), (sw, SHELF_THICK, sd), STONE, uvs=faces_onto(isl["shelf"], (-sw / 2, base + SHELF_THICK / 2, sz + sd / 2), sw, SHELF_THICK)))
    part.add(box((0, base * 0.45, R * 0.93), (mw, base * 0.5, 0.1), BLACK))
    bw, bd, bt, bh = v["benchWidth"], v["benchDepth"], v["benchThickness"], v["benchHeight"]
    bz = R + bd / 2
    bench = faces_onto(isl["bench"], (-bw / 2, bh, bz + bd / 2), bw, bt)
    part.add(box((0, bh - bt / 2, bz), (bw, bt, bd), WOOD_DARK, uvs=bench))
    for sx in (-1, 1):
        part.add(box((sx * (bw / 2 - 0.08), (bh - bt) / 2, bz), (0.05, bh - bt, 0.05), WOOD_DARK, uvs=bench))
    return part


def faces_onto(rect, corner, width, thick):
    """A box's uvs (box's uvs(p, n)) into an island width across, its front face's strip thick
    tall on top, below it the top face going back (corner: the front's top left, x least, z
    most): the front and back faces by x and height, the top and bottom by x and depth, the ends
    by height and depth, at the island's left; so a slab's joints run on over its front and top."""
    x0, y0, w, h = rect
    k = w / width  # pixels a meter
    cx, cy, cz = corner

    def uvs(p, n):
        if abs(n[1]) > 0.5:  # top or bottom
            i, j = p[0] - cx, thick + cz - p[2]
        elif abs(n[2]) > 0.5:  # front or back
            i, j = p[0] - cx, cy - p[1]
        else:  # an end
            i, j = cy - p[1], thick + cz - p[2]
        return ((x0 + min(w, max(0.0, i * k))) / ATLAS, 1 - (y0 + min(h, max(0.0, j * k))) / ATLAS)
    return uvs


def stave_count(v):
    """The barrel's staves, staveWidth wide around its widest (an even number)."""
    n = max(4, round(2 * math.pi * (v["barrelRadius"] + v["barrelBulge"]) / v["staveWidth"]))
    return n + n % 2


_outlines = {}  # robeLength -> robe_outline's, and sash_outline's by ("sash", its inputs), read once per run or worker


def image_rows(name, solid, high=400):
    """An image from vids/, high pixels high: each row's runs (x0, x1) of pixels where
    solid((r, g, b), 0 to 1), each over 2 pixels."""
    img = modl.read_png(subprocess.run(["magick", os.path.join(VIDS, name), "-resize", f"x{high}", "PNG24:-"], check=True, capture_output=True).stdout)
    px, u, w = img.px, img.unit, img.w
    rows = []
    for y in range(img.h):
        filled = [solid((px[i] * u, px[i + 1] * u, px[i + 2] * u)) for i in range(y * w * 4, (y + 1) * w * 4, 4)]
        runs, x = [], 0
        while x < w:
            if filled[x]:
                a = x
                while x < w and filled[x]:
                    x += 1
                if x - a > 2:
                    runs.append((a, x))
            x += 1
        rows.append(runs)
    return rows


def robe_outline(v):
    """RobeFemale.png's outline, the robe's pattern (Ken, 2026-11-04), in meters from the middle
    of its hem, its two sides averaged, robeLength from its hem (its widest row near the bottom;
    below that is the hem's near side, seen from above) to the top of its neck: "body", (height,
    half width) up its body, the sleeves left out (above the gap under them the body is held to
    its width there); "shoulder" and "armpit", where the right sleeve's top and bottom meet the
    body; "tip" and "low", its cuff's outermost and lowest points (each (x, height)); "span",
    its width across."""
    L = v["robeLength"]
    if L in _outlines:
        return _outlines[L]
    rows = image_rows(ROBE_IMAGE, lambda c: sum(c) < 2.7)  # not the white background
    lower = [r[0] for r in rows[len(rows) // 2:] if len(r) == 1]
    cx = sum(a + b for a, b in lower) / 2 / len(lower)
    middle = lambda y: next(((i, r) for i, r in enumerate(rows[y]) if r[0] <= cx < r[1]), (None, None))
    filled = [y for y in range(len(rows)) if middle(y)[1]]
    top, bottom = filled[0], filled[-1]
    half = lambda y: (middle(y)[1][1] - middle(y)[1][0]) / 2
    hem = max(range(bottom - (bottom - top) // 4, bottom + 1), key=half)
    gap = [y for y in range(top, hem) if middle(y)[0] and len(rows[y]) > middle(y)[0] + 1]
    if not gap:
        raise ValueError(f"{ROBE_IMAGE}: no gap under its sleeves, so they can't be told from its body")
    armpit, low = gap[0], gap[-1]
    chest = half(armpit)
    tip = max(range(top, armpit), key=half)
    shoulder = next(y for y in range(tip, top - 1, -1) if half(y) <= chest)
    i, _ = middle(low)
    centers = [(a + b) / 2 for a, b in rows[low]]
    sleeve = ((centers[i + 1] - cx) + (cx - centers[i - 1])) / 2 if i else centers[i + 1] - cx
    k = L / (hem - top)
    at = lambda x, y: (x * k, (hem - y) * k)
    _outlines[L] = {"body": [at(min(half(y), chest) if y < armpit else half(y), y)[::-1] for y in range(hem, top - 1, -1)],
                    "shoulder": at(chest, shoulder), "armpit": at(chest, armpit), "tip": at(half(tip), tip),
                    "low": at(sleeve, low), "span": 2 * k * max(half(y) for y in range(top, hem + 1))}
    return _outlines[L]


def sash_outline(v):
    """RobeFemaleSash.png's outline (Ken, 2026-11-04), the sash from the front, sized so its band
    (its rows near the top as wide as its widest there) is a little wider than the robe under
    it, its top sashTop above the hem: "rows", (height, [(x0, x1)]) down it, in meters from the
    robe's middle; "band", the band's height; "box", (x0, x1, bottom, top)."""
    key = ("sash", v["robeLength"], v["sashTop"])
    if key in _outlines:
        return _outlines[key]
    rows = image_rows(SASH_IMAGE, lambda c: not (min(c) > 0.67 and max(c) - min(c) < 0.1))  # not its checkerboard
    filled = [y for y, r in enumerate(rows) if r]
    top, bottom = filled[0], filled[-1]
    wide = lambda y: max(b for _, b in rows[y]) - min(a for a, _ in rows[y]) if rows[y] else 0
    widest = max(range(top, top + (bottom - top) // 6), key=wide)
    span = wide(widest)
    foot = next(y for y in range(widest, bottom) if wide(y) < 0.8 * span)
    cx = (min(a for a, _ in rows[widest]) + max(b for _, b in rows[widest])) / 2
    body, k = robe_outline(v)["body"], 0.0
    for _ in range(3):  # the band's height depends on the size, which depends on the robe under it
        band = (foot - top) * k
        k = 2 * 1.06 * max(robe_half(body, v["sashTop"] - band * f) for f in (0, 0.5, 1)) / span
    out = {"rows": [(v["sashTop"] - (y - top) * k, [((a - cx) * k, (b - cx) * k) for a, b in rows[y]]) for y in range(top, bottom + 1)],
           "band": (foot - top) * k}
    xs = [x for _, runs in out["rows"] for run in runs for x in run]
    out["box"] = (min(xs), max(xs), out["rows"][-1][0], v["sashTop"])
    _outlines[key] = out
    return out


def robe_half(body, y):
    """The robe's half width at height y, from its outline's body."""
    for (y0, a0), (y1, a1) in zip(body, body[1:]):
        if y <= y1:
            return a0 + (a1 - a0) * max(0.0, (y - y0) / ((y1 - y0) or 1))
    return body[-1][1]


def simplify(points, tolerance):
    """A polyline's points (2D) less those it can lose straying under tolerance
    (Douglas-Peucker)."""
    if len(points) < 3:
        return list(points)
    (ax, ay), (bx, by) = points[0], points[-1]
    n = math.hypot(bx - ax, by - ay) or 1
    far, k = max((abs((p[0] - ax) * (by - ay) - (p[1] - ay) * (bx - ax)) / n, i) for i, p in enumerate(points[1:-1], 1))
    if far <= tolerance:
        return [points[0], points[-1]]
    return simplify(points[:k + 1], tolerance)[:-1] + simplify(points[k:], tolerance)


def pack(want, tallest_first=True):
    """Islands want [(name, w, h)] in an atlas, (x, y, w, h) in pixels from the top left, by
    name, or None if they don't fit: the swatches' cells in the top left, then the islands,
    tallest first (or in want's order), each padded PAD, each as high as it fits on the skyline
    of those before (its lowest place, then its leftmost)."""
    sky = [[0, 4 * CELL, 4 * CELL], [4 * CELL, ATLAS - 4 * CELL, 0]]  # [x, width, top] spans
    out = {}
    for name, w, h in sorted(want, key=lambda e: -e[2]) if tallest_first else want:
        ww, hh = w + 2 * PAD, h + 2 * PAD
        spots = [(max(t[2] for t in sky if t[0] < x + ww and t[0] + t[1] > x), x) for x, _, _ in sky if x + ww <= ATLAS]
        if not spots:
            return None
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
        if y + hh > ATLAS:
            return None
    return out


def silk_islands(v):
    """pack_silk's, its reads no part's own (modl.quiet)."""
    with modl.quiet(v):
        return pack_silk(v)


def pack_silk(v):
    """The silk atlas's islands (pack's), at silkDensity the robe beside the swatches, the sash
    from the front, the hem's band (the cuffs' too) and the sash's band round the robe, then the
    hammock's bed at bedDensity below, and those densities ("silkDensity", "bedDensity"),
    lowered until they fit: the robe's first, to half, then both."""
    hem, band = (ring_length(r) / BAND_FOLDS for r in (hem_rings(v, 64, True)[0][1], sash_rings(v, 64)[0]))
    sx0, sx1, sy0, sy1 = sash_outline(v)["box"]
    scale = bed = 1.0
    while True:
        sd, bd = v["silkDensity"] * scale, v["bedDensity"] * bed
        px = lambda m, k=sd: max(4, round(m * k))
        out = pack([("robe", px(robe_outline(v)["span"]), px(v["robeLength"])), ("sash", px(sx1 - sx0), px(sy1 - sy0)),
                    ("trim", px(hem), px(v["robeTrim"])), ("sashBand", px(band), px(sash_outline(v)["band"])),
                    ("bed", px(v["bedLength"], bd), px(v["bedWidth"], bd))], tallest_first=False)
        if out:
            out.update(silkDensity=sd, bedDensity=bd)
            return out
        scale *= 0.95
        if scale < 0.5:
            bed *= 0.95


def islands(v):
    """pack_islands', its reads no part's own (modl.quiet): it reads every part's sizes."""
    with modl.quiet(v):
        return pack_islands(v)


def pack_islands(v):
    """The atlas's islands (pack's), by name, and the densities they were sized at ("density",
    "floorDensity", "carveDensity", "cocoonDensity"), lowered until they fit. The hammock's bed
    and the robe are in the silk's atlas (silk_islands)."""
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
    oven_prof, domes = oven_profile(v, 0)
    lengths["dome"] = profile_length(oven_prof, 2, 1 + domes)[0]
    lengths["flue"] = profile_length(oven_prof, 2 + domes, 4 + domes)[0]
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
                ("perch", px(2 * math.pi * v["perchRadius"]), px(v["perchLength"] + v["perchUpturn"])),
                ("ovenBase", px(2 * math.pi * v["ovenRadius"] / OVEN_REPS), px(v["ovenBaseHeight"])),
                ("ovenDome", px(2 * math.pi * v["ovenRadius"] / OVEN_REPS), px(lengths["dome"])),
                ("ovenFlue", px(2 * math.pi * v["flueRadius"] / OVEN_REPS), px(lengths["flue"])),
                ("shelf", px(v["shelfWidth"]), px(SHELF_THICK + v["shelfDepth"])),
                ("bench", px(v["benchWidth"]), px(v["benchThickness"] + v["benchDepth"]))]
        out = pack(want)
        if out:
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

    def raw(i, j):
        around = sub(rings[i][(j + 1) % n], rings[i][(j - 1) % n])
        along = sub(rings[min(i + 1, m - 1)][j], rings[max(i - 1, 0)][j])
        return unit(cross(along, around))
    # all to the side most face out on: a pleat's flank on a flat ring can face its middle
    side = 1 if sum(sum(raw(i, j)[q] * (rings[i][j][q] - mid[i][q]) for q in range(3)) for i in range(m) for j in range(n)) >= 0 else -1
    normal = lambda i, j: tuple(side * x for x in raw(i, j))
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


def robe_deep(v, a):
    """The robe's half depth where it is a wide (half its width): oval, no deeper than robeDepth."""
    return min(v["robeDepth"] / 2, 0.8 * a)


PLEATS, BAND_FOLDS = 16, 4  # the skirt's pleats round it; the turns of the hem's and sash's bands round their islands


def pleat(v, y):
    """How far the skirt's pleats stand out and in at height y: pleatDepth at the hem, none from
    the foot of the sash's band up."""
    start = v["sashTop"] - sash_outline(v)["band"]
    return v["pleatDepth"] * max(0.0, 1 - y / start) ** 0.8 if start > 0 else 0.0


def robe_ring(v, y, a, sides, out=0.0, pleats=True):
    """The body's section at height y, a wide: an oval of sides points, out further all round,
    its pleats (with pleats) standing out and in along its normals, on its front and back."""
    b, p = robe_deep(v, a), pleat(v, y) if pleats else 0.0
    ring = []
    for k in range(sides):
        t = 2 * math.pi * k / sides
        c, s_ = math.cos(t), math.sin(t)
        n = unit((c / a, 0, s_ / b))
        d = out + p * math.cos(PLEATS * t) * abs(s_)  # none at its sides, too sharp to fold in
        ring.append((a * c + n[0] * d, y, b * s_ + n[2] * d))
    return ring


def ring_length(ring):
    return sum(math.dist(p, q) for p, q in zip(ring, ring[1:] + ring[:1]))


HEM_OUT, LIP = 0.0025, 0.002  # how far the hem's and cuffs' bands stand out, and tuck in past their tops


def hem_rings(v, sides, pleats):
    """The hem's band, a ring of its own round the bottom of the skirt: (rings, their vs)."""
    body, trim = robe_outline(v)["body"], v["robeTrim"]
    at = ((0, 0.0, 1), (0, HEM_OUT, 1), (trim, HEM_OUT, 0), (trim + LIP, 0.0, 0))
    return [robe_ring(v, y, robe_half(body, y), sides, out, pleats) for y, out, _ in at], [vv for _, _, vv in at]


def sash_rings(v, sides):
    """The sash's band round the robe, straight, as wide as the robe under it is at its widest."""
    body, top = robe_outline(v)["body"], v["sashTop"]
    ys = (top - sash_outline(v)["band"], top)
    a = max(robe_half(body, y) for y in ys)
    return [robe_ring(v, y, a, sides, 0.003, False) for y in ys]


def densify(points, step):
    """A profile's (height, width) points with more between, none further than step apart up it."""
    out = [points[0]]
    for p, q in zip(points, points[1:]):
        n = max(1, math.ceil((q[0] - p[0]) / step))
        out += [(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n) for i in range(1, n + 1)]
    return out


def wrapped(rings, swatch, rect, vs, reach=1.0):
    """A loft (loft's) mapped round into rect: round it reach of its width, there and back (as
    mirror's tiles, so its pattern meets itself where it turns), ring i at vs[i] down it (0 its
    top, 1 its bottom). Its points should fall where it turns (reach a whole number dividing
    their count)."""
    part = loft(rings, swatch)
    n = len(rings[0])
    x, y, w, h = rect
    fold = lambda u: u % 2 if u % 2 <= 1 else 2 - u % 2
    t = lambda u, vv: ((x + fold(u * reach) * w) / ATLAS, 1 - (y + vv * h) / ATLAS)
    part.faces = [([c + (t((j + dj) / n, vs[i + di]),) for c, (di, dj) in zip(corners, ((0, 0), (1, 0), (1, 1), (0, 1)))], sw)
                  for f, (corners, sw) in enumerate(part.faces) for i, j in [divmod(f, n)]]
    return part


def sash_sheet(v, level, rect):
    """The sash from the front, its outline sash_outline's, a cloth both sides 1.5 mm thick,
    lying over the robe 5 mm off it and its pleats, swelling 4% of robeLength at its knot (where
    RobeFemaleSash.png has it, low in the middle of the band); rows step apart (a fraction of robeLength), each run of
    them split as finely, joined to the runs below that they overlap. Mapped from the front."""
    so, body = sash_outline(v), robe_outline(v)["body"]
    top, band = v["sashTop"], so["band"]
    x0, x1, y0, y1 = so["box"]
    rx, ry, rw, rh = rect

    def z(x, y):
        a = robe_half(body, y)
        d2 = (x / (band * 0.9)) ** 2 + ((y - (top - band * 0.6)) / (band * 0.9)) ** 2
        return robe_deep(v, a) * math.sqrt(max(0.0, 1 - (x / a) ** 2)) + pleat(v, y) + 0.005 + 0.04 * v["robeLength"] * max(0.0, 1 - d2)

    def corner(x, y, side):
        e = 0.0005
        n = unit((-(z(x + e, y) - z(x - e, y)) / (2 * e), -(z(x, y + e) - z(x, y - e)) / (2 * e), 1))
        t = ((rx + (x - x0) / (x1 - x0) * rw) / ATLAS, 1 - (ry + (y1 - y) / (y1 - y0) * rh) / ATLAS)
        return ((x, y, z(x, y) - (0 if side > 0 else 0.0015)), n if side > 0 else tuple(-q for q in n), t)
    step = v["robeLength"] * (0.024, 0.048, 0.096)[level]
    rows = [r for r in so["rows"] if r[1]]
    picked = [rows[0]]
    for r in rows[1:]:
        if picked[-1][0] - r[0] >= step:
            picked.append(r)
    if picked[-1] is not rows[-1]:
        picked.append(rows[-1])
    part = Part()
    clip = lambda p, q: (max(p[0], q[0]), min(p[1], q[1]))
    for (ya, ra), (yb, rb) in zip(picked, picked[1:]):
        for A in ra:
            over = [B for B in rb if B[0] < A[1] and B[1] > A[0]]
            for B in over:
                back = [C for C in ra if C[0] < B[1] and C[1] > B[0]]
                a, b = A if len(over) == 1 else clip(A, B), B if len(back) == 1 else clip(B, A)
                n = max(1, round(max(a[1] - a[0], b[1] - b[0]) / step))
                xa = [a[0] + (a[1] - a[0]) * c / n for c in range(n + 1)]
                xb = [b[0] + (b[1] - b[0]) * c / n for c in range(n + 1)]
                for c in range(n):
                    for side in (1, -1):
                        part.faces.append(([corner(xa[c], ya, side), corner(xa[c + 1], ya, side), corner(xb[c + 1], yb, side), corner(xb[c], yb, side)], SASH))
    return part


def robe(v, level):
    """As RobeFemale.png hangs, its outline the pattern (robe_outline): a cloth body, oval in
    section, as wide as the outline up it, its skirt pleated (but far off); short wide sleeves
    of flat cloth (a rounded rectangle in section) from inside the body out to the outline's
    cuffs, open there (dark inside); its hem and cuffs bands of their own, standing out a
    little and tucked in at their tops; the sash a band round it, and in front its outline in
    RobeFemaleSash.png (sash_sheet). The body's color and collar are the front view's
    (paint_robe), back and front alike; the bands are mapped round them (paint_trim,
    paint_sash), and the sash's front from the front (paint_sash_front)."""
    L, sides, trim = v["robeLength"], (64, 24, 12)[level], v["robeTrim"]
    o, isl = robe_outline(v), silk_islands(v)
    rx, ry, rw, rh = isl["robe"]
    span = o["span"]
    # seen from the front, held to its island
    front = lambda p: ((rx + min(1.0, max(0.0, p[0] / span + 0.5)) * rw) / ATLAS, 1 - (ry + min(1.0, max(0.0, 1 - p[1] / L)) * rh) / ATLAS)
    # how far its outline may stray, and its rings be apart, as fractions of its length
    tol, most = (L * f for f in ((0.0024, 0.093), (0.007, 0.19), (0.024, 2.0))[level])
    body = densify(simplify(o["body"], tol), most)
    part = loft([robe_ring(v, y, a, sides, 0.0, level == 0) for y, a in body], ROBE, front, (STONE, ROBE))
    rings, vs = hem_rings(v, sides, level == 0)
    hem_length = ring_length(rings[1]) / BAND_FOLDS  # the island's
    part.add(wrapped(rings, ROBE, isl["trim"], vs, BAND_FOLDS))
    (chest, shoulder), (_, armpit) = o["shoulder"], o["armpit"]
    thick, around = robe_deep(v, chest) * 0.6, (16, 10, 6)[level]
    for sx in (-1, 1):
        root = [(sx * chest * 0.6, y, 0) for y in (shoulder, armpit)]  # inside the body, so no gap shows
        cuff = [(sx * x, y, 0) for x, y in (o["tip"], o["low"])]
        ends = [(tuple((p[q] + r[q]) / 2 for q in range(3)), math.dist(p, r) / 2, unit(sub(p, r))) for p, r in (root, cuff)]
        ring_of = lambda e: ellipse(e[0], e[1], thick, (e[2], (0, 0, 1)), around, 0.5)
        inner, outer = ring_of(ends[0]), ring_of(ends[1])
        part.add(loft([inner, outer], ROBE, front, (None, STONE if level < 2 else None)))
        reach = math.dist(ends[0][0], ends[1][0])

        def along(f, out):
            """The sleeve's section f of the way from its root to its cuff, out further."""
            c = tuple(ends[0][0][q] + (ends[1][0][q] - ends[0][0][q]) * f for q in range(3))
            return [tuple(c[q] + (p[q] + (r[q] - p[q]) * f - c[q]) * (1 + out / thick) for q in range(3)) for p, r in zip(inner, outer)]
        cuff_rings = [along(1 - (trim + LIP) / reach, 0.0), along(1 - trim / reach, HEM_OUT), along(1.0, HEM_OUT), along(1.0, 0.0)]
        part.add(wrapped(cuff_rings, ROBE, isl["trim"], (0, 0, 1, 1), max(1, round(ring_length(cuff_rings[1]) / hem_length))))
    part.add(wrapped(sash_rings(v, sides), SASH, isl["sashBand"], (1, 0), BAND_FOLDS))
    part.add(sash_sheet(v, level, isl["sash"]))
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
LOD_ERRORS = os.path.join(modl.CACHE, FAMILY + "_lod_errors.json")  # each model's [LOD1, LOD2] error, as last measured
try:
    _lod_errors = json.load(open(LOD_ERRORS))
except (OSError, ValueError):
    _lod_errors = {}


def lod_error(lods, k):
    """How far level k strays from LOD0: the farthest of LOD0's vertices from its surface (each
    point's nearest triangle: its plane where the point falls over it, else its nearest edge),
    in numpy, a few hundred triangles at a time."""
    pts = np.unique(np.round(np.array([p for p, _, _ in lods[0].verts]), 5), axis=0)[:, None, :]
    verts = np.array([p for p, _, _ in lods[k].verts])
    tris = np.array(lods[k].tris)
    dot = lambda u, w: (u * w).sum(-1)

    def edge(a, b):
        ab = b - a
        t = np.clip(dot(pts - a, ab) / np.maximum(dot(ab, ab), 1e-30), 0, 1)
        return np.linalg.norm(pts - (a + t[..., None] * ab), axis=-1)
    best = np.full(len(pts), np.inf)
    for s in range(0, len(tris), 256):
        a, b, c = (verts[tris[s:s + 256, q]][None] for q in range(3))
        n = np.cross(b - a, c - a)
        nn = np.maximum(dot(n, n), 1e-30)
        inside = (dot(np.cross(b - a, pts - a), n) >= 0) & (dot(np.cross(c - b, pts - b), n) >= 0) & (dot(np.cross(a - c, pts - c), n) >= 0)
        plane = np.abs(dot(pts - a, n)) / np.sqrt(nn)
        d = np.where(inside, plane, np.minimum(np.minimum(edge(a, b), edge(b, c)), edge(c, a)))
        best = np.minimum(best, d.min(axis=1))
    return float(best.max())


def assets(v, measure=False):
    """The models, each level starting where its error is lodError pixels (errors measured when
    measure, or for a model never measured; otherwise the last measured, kept in LOD_ERRORS, so
    they drift as the models change until measured again: Ken, 2026-11-04, `hut.py --measure`),
    culled where cullPixels tall."""
    out = []
    for name, make, far in MODELS:
        lods = modl.made(name, lambda r, make=make, name=name: [(make or roof_leaf(r))(r, k).mesh(f"{name}_LOD{k}") for k in range(3)], v)
        ps = [p for p, _, _ in lods[0].verts]
        size = max(max(p[q] for p in ps) - min(p[q] for p in ps) for q in range(3))
        if measure or name not in _lod_errors:
            _lod_errors[name] = [lod_error(lods, k) for k in (1, 2)]
            os.makedirs(modl.CACHE, exist_ok=True)
            with open(LOD_ERRORS, "w") as f:
                json.dump(_lod_errors, f)
        cull = v["farCullDistance"] if far else min(v["cullDistance"], size * PX_PER_RADIAN / v["cullPixels"])
        d1, d2 = (max(0.5, e * PX_PER_RADIAN / v["lodError"]) for e in _lod_errors[name])
        d2 = min(max(d2, d1 * 1.01), cull / 1.01)
        d1 = min(d1, d2 / 1.01)
        a = Asset(name, lods, size, [size / (2 * d) for d in (d1, d2, cull)])
        a.errors, a.distances = _lod_errors[name], (d1, d2, cull)
        if name in SILK_MODELS:
            a.material = modl.material_guid(FAMILY, HAMMOCK_MATERIAL if name == "Hammock" else SILK_MATERIAL)
        elif name == "HutDisc":
            a.material = modl.material_guid(FAMILY, DISC_MATERIAL)
        out.append(a)
    return out


_wood = {}  # the grain source, read once per run or worker


def wood_source(size=None):
    """WoodDesatD as an Image, and its mean gray; with size, shrunk to size pixels square (once
    per size), so copying it at a lower density averages its pixels rather than aliasing."""
    if "img" not in _wood:
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
LID_BUMP = 3.0  # the barrel's lid's relief, times the staves'


def paint_wood(color, normal, rect, along_of, across_of, swatch, tile, density, seed=0, boards_of=None, board_px=0, relief=None, bump=1.0):
    """Fills an island (its padding too, wrapped across its width, clamped down its height) with
    grain tinted swatch's color: along_of(i, j) and across_of(i, j) give a pixel's meters along
    and across the grain. With boards_of (a pixel's board position across; a whole number is a
    seam) and board_px (a board's width in pixels), boards shaded apart with dark seams. The
    normal map is the gradient of a height field in pixels: the grain, each board's crown, and
    its seams grooved 2 px deep; with relief(i, j), a carving's (height in pixels, light), its
    height added and its color times its light; all of it bump times as high. density, the
    island's pixels per meter, sizes the source."""
    img, mean = wood_source(max(8, round(tile * density)))
    x0, y0, w, h = rect
    tint = np.array([int(SWATCHES[swatch][1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)])
    # every pixel at once (numpy): its padding wrapped across, clamped down
    i, j = np.meshgrid(np.arange(-PAD, w + PAD) % w, np.clip(np.arange(-PAD, h + PAD), 0, h - 1))
    src = img.np()[:, :, :3].astype(np.int64).sum(-1)  # the source's grays, times 3 / unit
    along, across = np.broadcast_to(along_of(i, j), i.shape), np.broadcast_to(across_of(i, j), i.shape)
    g = src[np.floor((across / tile) % 1.0 * img.h).astype(np.int64) % img.h,
            np.floor((along / tile) % 1.0 * img.w).astype(np.int64) % img.w] / 3 * img.unit
    shade, dark, height = 1.0, 1.0, GRAIN_BUMP * (g / mean - 1)
    if boards_of:
        b = boards_of(i, j)
        board = _ints(b)
        f = b - board
        shade = 1 + 0.06 * (((board * 2654435761 + seed) % 1000) / 500.0 - 1)
        seam = np.minimum(f, 1 - f) * board_px  # pixels to the nearer seam
        dark = np.where(seam < 1, 0.45, np.where(seam < 2, 0.75, 1.0))
        height = height + CROWN * board_px * 4 * f * (1 - f) - GROOVE * np.maximum(0.0, 2 - seam)
    if relief:
        lift, light = relief.np(i, j)
        height, dark = height + lift, dark * light
    height = (height * bump).astype(np.float32)
    each = lambda x: np.broadcast_to(np.asarray(x, np.float64), i.shape)[..., None]
    col = np.minimum(1.0, (0.5 + 0.5 * g / mean)[..., None] * tint * each(shade) * each(dark))  # as the scalar order had it
    put(color, x0 - PAD, y0 - PAD, np.concatenate([col, np.ones(i.shape + (1,))], -1))
    write_normals(normal, rect, height)


def write_normals(normal, rect, height):
    """An island's normal map, its padding too, from height (pixels, the padded island's rows:
    a flat sequence or an array), in numpy."""
    x0, y0, w, h = rect
    W, H = w + 2 * PAD, h + 2 * PAD
    p = np.pad(np.asarray(height, np.float32).reshape(H, W).astype(np.float64), 1, mode="edge")
    # tangent space: +x along u, +y along v, which is up the image
    nx, ny = -(p[1:-1, 2:] - p[1:-1, :-2]) / 2, (p[2:, 1:-1] - p[:-2, 1:-1]) / 2
    ln = np.sqrt(nx * nx + ny * ny + 1)
    out = np.stack([nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, 1 / ln * 0.5 + 0.5, np.ones_like(ln)], -1)
    put(normal, x0 - PAD, y0 - PAD, out)


def put(img, x, y, pixels):
    """pixels (rows by columns by 4) into img with their top left at (x, y), clipped to it."""
    h, w = pixels.shape[:2]
    xa, ya, xb, yb = max(0, x), max(0, y), min(img.w, x + w), min(img.h, y + h)
    if xa < xb and ya < yb:
        img.np()[ya:yb, xa:xb] = pixels[ya - y:yb - y, xa - x:xb - x]


def _rnd(a, b, k, seed):
    """A repeatable number in 0..1 for cell (a, b), channel k (numbers, or int64 arrays)."""
    return (((a * 73856093) ^ (b * 19349663) ^ (k * 83492791) ^ seed) % 10007) / 10007.0


def _ints(x):
    """x's floor as int64 (an array's), as math.floor gives."""
    return np.floor(x).astype(np.int64)


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
    grid = np.array(lines)

    def arrays(i, j):
        inside = (top <= j) & (j < bottom)
        r = np.clip(((j - top) / band * rows).astype(np.int64), 0, rows - 1)
        c = np.minimum(cols - 1, (i % period / period * cols).astype(np.int64))
        h = np.where(inside, grid[r, c], 0.0)
        return np.where(inside, CARVE_DEPTH * h, 0.0), np.where(inside, CARVE_LIGHT + (1 - CARVE_LIGHT) * h, 1.0)
    relief.np = arrays
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

    def arrays(i, j):
        ci, cj = _ints(i // cw), _ints(j // ch)
        best = None
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                a, b = ci + da, cj + db
                aa = a % nx
                px, py = (a + 0.2 + 0.6 * rnd(aa, b, 1)) * cw, (b + 0.2 + 0.6 * rnd(aa, b, 2)) * ch
                d = ((i - px) / cw) ** 2 + ((j - py) / ch) ** 2
                if best is None:
                    best = [d, aa, b, px, py]
                else:  # the first nearest wins ties, as above
                    closer = d < best[0]
                    best = [np.where(closer, x, y) for x, y in zip((d, aa, b, px, py), best)]
        _, a, b, px, py = best
        return (rnd(a, b, 3) * 2 - 1) * tilt * (i - px) + (rnd(a, b, 4) * 2 - 1) * tilt * (j - py), np.ones(np.shape(i))
    relief.np = arrays
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

    def arrays(x, y):
        a, b = _ints(x), _ints(y)
        fx, fy = x - a, y - b
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        g = lambda i, j: _rnd(i % nx, j, 7, seed)
        top = g(a, b) * (1 - sx) + g(a + 1, b) * sx
        return top * (1 - sy) + (g(a, b + 1) * (1 - sx) + g(a + 1, b + 1) * sx) * sy
    f.np = arrays
    return f


def combine(*reliefs):
    """Reliefs together: their heights added, their lights multiplied."""
    def relief(i, j):
        lift, light = 0.0, 1.0
        for r in reliefs:
            a, b = r(i, j)
            lift, light = lift + a, light * b
        return lift, light

    def arrays(i, j):
        lift, light = 0.0, 1.0
        for r in reliefs:
            a, b = r.np(i, j)
            lift, light = lift + a, light * b
        return lift, light
    relief.np = arrays
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

    def arrays(i, j):
        n = 0.7 * big.np(i * k, j * k) + 0.3 * small.np(2 * i * k, 2 * j * k)
        return height * n, 1 + tone * (2 * n - 1)
    relief.np = arrays
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

    def arrays(i, j):
        if "grid" not in cache:
            grid = np.zeros((max([y for _, y in mask] + [0]) + 2, w))
            for (x, y), m in mask.items():
                if y >= 0:
                    grid[y, x] = m
            cache["grid"] = grid
        grid = cache["grid"]
        m = np.where(j < grid.shape[0], grid[np.clip(j, 0, grid.shape[0] - 1), i], 0.0)
        return -depth * m, 1 - dark * m
    cache = {}
    relief.np = arrays
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


JOINT, BEVEL = 0.006, 0.035  # the oven's stones: half a joint's width, and how far in they round up to their top


def courses(height, length, period_at, seed):
    """Stones laid in courses height tall, each stone about length long, every course set half a
    stone on (and a little more or less): stones(u, y) -> (stone, meters in from its edge), u
    round a repeat period_at(y) meters long (0 to 1), y meters up."""
    def stones(u, y):
        c = math.floor(y / height)
        n = max(1, round(period_at(y) / length))
        x = u * n + 0.5 * c + 0.4 * _rnd(c, 0, 8, seed)
        b = math.floor(x)
        f = x - b
        return (c, b % n), min(min(f, 1 - f) * period_at(y) / n, y - c * height, (c + 1) * height - y)

    def arrays(u, y):  # the same over a grid (its rows each one y)
        period = by_row(period_at, y)
        c = _ints(y / height)
        n = np.maximum(1, np.round(period / length)).astype(np.int64)
        x = u * n + 0.5 * c + 0.4 * _rnd(c, 0, 8, seed)
        b = _ints(x)
        f = x - b
        return (c, b % n), np.minimum(np.minimum(np.minimum(f, 1 - f) * period / n, y - c * height), (c + 1) * height - y)
    stones.np = arrays
    return stones


def by_row(fn, y):
    """fn(y) for each row of a grid whose rows each hold one y, as a column."""
    return np.array([fn(float(t)) for t in y[:, 0]])[:, None]


def flagstones(size, period_at, top, seed):
    """Rounded flagstones about size across, as on Oven.png's dome: the cells of seeds jittered in
    rows size apart, each row as many round a repeat as fit there (period_at(y), up to top), so
    they stay their size as the dome narrows: stones(u, y) as courses'."""
    def row(r):
        return max(1, round(period_at(min(max((r + 0.5) * size, 0.0), top)) / size))

    def stones(u, y):
        period, r0 = period_at(y), math.floor(y / size)
        seeds = []
        for r in (r0 - 1, r0, r0 + 1):
            n = row(r)
            s0 = math.floor(u * n)
            for s in (s0 - 1, s0, s0 + 1):
                su = (s + 0.2 + 0.6 * _rnd(r, s % n, 1, seed)) / n
                sy = (r + 0.15 + 0.7 * _rnd(r, s % n, 2, seed)) * size
                seeds.append(((r, s % n), (u - su) * period, y - sy))
        seeds.sort(key=lambda t: t[1] * t[1] + t[2] * t[2])
        a, ax, ay = seeds[0]
        da = ax * ax + ay * ay
        edge = 9.0
        for b, bx, by in seeds[1:]:
            gap = math.hypot(ax - bx, ay - by)
            if gap > 1e-9 and b != a:
                edge = min(edge, (bx * bx + by * by - da) / (2 * gap))
        return a, edge

    def arrays(u, y):  # the same over a grid (its rows each one y), nearest first in the loop's order
        period, r0 = by_row(period_at, y), _ints(y / size)
        ids_r, ids_s, dxs, dys = [], [], [], []
        for dr in (-1, 0, 1):
            r = r0 + dr
            n = by_row(lambda t: row(math.floor(t / size) + dr), y).astype(np.int64)
            s0 = _ints(u * n)
            for ds in (-1, 0, 1):
                s = s0 + ds
                su = (s + 0.2 + 0.6 * _rnd(r, s % n, 1, seed)) / n
                sy = (r + 0.15 + 0.7 * _rnd(r, s % n, 2, seed)) * size
                ids_r.append(np.broadcast_to(r, u.shape))
                ids_s.append(s % n)
                dxs.append((u - su) * period)
                dys.append(y - sy)
        ids_r, ids_s, dxs, dys = (np.stack(x) for x in (ids_r, ids_s, dxs, dys))
        d2 = dxs * dxs + dys * dys
        k = np.argmin(d2, axis=0)[None]  # the first nearest, as a stable sort finds
        take = lambda x: np.take_along_axis(x, k, 0)[0]
        ar, as_, ax, ay, da = take(ids_r), take(ids_s), take(dxs), take(dys), take(d2)
        gap = np.hypot(ax - dxs, ay - dys)
        other = (gap > 1e-9) & ((ids_r != ar) | (ids_s != as_))
        edge = np.where(other, (d2 - da) / (2 * np.where(other, gap, 1.0)), 9.0).min(axis=0)
        return (ar, as_), np.minimum(edge, 9.0)
    stones.np = arrays
    return stones


def paint_stone(color, normal, rect, place, stones, relief, seed, wrap=True, rough_px=0.0):
    """An island of the oven's dark stone (Oven.png): place(i, j) -> (u, y), a pixel's stones'
    place (stones'); each stone the STONE swatch, a little lighter or darker than the next and
    mottled, rising over BEVEL from its edge to relief pixels, lighter at its worn edges; the
    joints between, JOINT each side, sunk and darker; its face rough_px rough all over."""
    rgb = np.array([int(SWATCHES[STONE][1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)])
    mottle, grit = value_noise(12, seed), value_noise(96, seed + 1)
    i, j = np.meshgrid(np.arange(rect[2]), np.arange(rect[3]))
    u, y = (np.broadcast_to(x, i.shape).astype(np.float64) for x in place(i, j))
    (sa, sb), e = stones.np(u, y)
    m = mottle.np(u * 12, y * 20)  # about 5 cm across, up
    joint = e < JOINT
    f = np.minimum(1.0, (np.where(joint, JOINT, e) - JOINT) / BEVEL)
    tone = (0.82 + 0.36 * _rnd(sa, sb, 3, seed)) * (0.9 + 0.2 * m) * (1 + 0.18 * (1 - f))
    # rough (Ken, 2026-11-04): grit about 7 mm across, and a speck a pixel
    rough = rough_px * (0.7 * grit.np(u * 96, y * 150) + 0.3 * _rnd(i, j, 9, seed))
    col = np.where(joint[..., None], rgb * 0.5, rgb * tone[..., None])
    lift = np.where(joint, 0.0, relief * (0.25 + 0.75 * np.sqrt(f)) * (0.9 + 0.2 * m) + rough)
    fill_arrays(color, normal, rect, col, lift, wrap)


def paint_oven(color, normal, isl, v, density):
    """The oven's islands, as Oven.png: its base two courses of blocks ovenBlock long, its dome
    rounded flagstones ovenStone across, its smoke ring a course of blocks round its wall and
    another over its rim and inside, its shelf slabs across, all raised stoneRelief over their
    joints (paint_stone); its bench wood, along it."""
    R, relief = v["ovenRadius"], v["stoneRelief"]
    prof, domes = oven_profile(v, 0)
    round_ = lambda r: 2 * math.pi * r / OVEN_REPS  # a repeat's meters round, at radius r
    wrapped = lambda rect, length: lambda i, j: ((i + 0.5) / rect[2], length * (1 - (j + 0.5) / rect[3]))
    rect = isl["ovenBase"]
    paint_stone(color, normal, rect, wrapped(rect, v["ovenBaseHeight"]),
                courses(v["ovenBaseHeight"] / 2, v["ovenBlock"], lambda y: round_(R), 21), relief, 21, rough_px=v["stoneRough"])
    rect = isl["ovenDome"]
    length, r = profile_length(prof, 2, 1 + domes)
    paint_stone(color, normal, rect, wrapped(rect, length),
                flagstones(v["ovenStone"], lambda y: round_(r(min(1.0, max(0.0, y / length)))), length, 23), relief, 23, rough_px=v["stoneRough"])
    rect = isl["ovenFlue"]
    length, r = profile_length(prof, 2 + domes, 4 + domes)
    paint_stone(color, normal, rect, wrapped(rect, length),
                courses(v["flueHeight"], v["ovenBlock"] / 2, lambda y: round_(v["flueRadius"]), 25), relief, 25, rough_px=v["stoneRough"])
    rect = isl["shelf"]
    sw = v["shelfWidth"]
    k = rect[2] / sw
    paint_stone(color, normal, rect, lambda i, j: ((i + 0.5) / rect[2], (rect[3] - j - 0.5) / k),
                courses(rect[3] / k + 1.0, v["ovenBlock"] / 2, lambda y: sw, 27), relief, 27, wrap=False, rough_px=v["stoneRough"])
    bench = isl["bench"]
    paint_wood(color, normal, bench, lambda i, j: i / density, lambda i, j: j / density, WOOD_DARK, v["woodTile"], density, 31,
               relief=unevenness(bench, 0.05 * density, 1.0, 33))


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


_fabrics = {}  # (name, w, h, turn, crop) -> Image, and name -> its size, read once per run or worker


def fabric(name, w, h, turn=False, crop=None):
    """A fabric image from vids/, or with crop (x, y, w, h, fractions of it) a part of it, w by h
    pixels (stretched to fit), turned a quarter first if turn, read through ImageMagick."""
    key = (name, w, h, turn, crop)
    if key not in _fabrics:
        cut = []
        if crop:
            W, H = fabric_size(name)
            cut = ["-crop", f"{round(crop[2] * W)}x{round(crop[3] * H)}+{round(crop[0] * W)}+{round(crop[1] * H)}", "+repage"]
        args = ["magick", os.path.join(VIDS, name)] + cut + (["-rotate", "90"] if turn else []) + ["-resize", f"{w}x{h}!", "PNG24:-"]
        _fabrics[key] = modl.kept(["fabric", args, os.path.getmtime(os.path.join(VIDS, name))],
                                  lambda: modl.read_png(subprocess.run(args, check=True, capture_output=True).stdout))
    return _fabrics[key]


def fabric_size(name):
    if name not in _fabrics:
        out = subprocess.run(["magick", "identify", "-format", "%w %h", os.path.join(VIDS, name)], check=True, capture_output=True, text=True).stdout
        _fabrics[name] = tuple(int(n) for n in out.split())
    return _fabrics[name]


def ground_of(img, whole=False):
    """A fabric's plain ground: the median color round its edge, or with whole, of all of it."""
    if whole:
        edge = [img.get(x, y) for x in range(0, img.w, 3) for y in range(0, img.h, 3)]
    else:
        edge = [img.get(x, y) for x in range(0, img.w, 4) for y in (0, img.h - 1)] + [img.get(x, y) for y in range(0, img.h, 4) for x in (0, img.w - 1)]
    return [sorted(c[q] for c in edge)[len(edge) // 2] * img.unit for q in range(3)]


def strip(name, crop, w=None, h=None):
    """Part of a fabric image (fabric's crop) w or h pixels, the other as its shape has it."""
    W, H = fabric_size(name)
    aspect = crop[2] * W / (crop[3] * H)
    w, h = w or max(4, round(h * aspect)), h or max(4, round(w / aspect))
    return fabric(name, w, h, crop=crop)


SLUBS = 2500  # dupioni's slubs a square meter, at scale 1


def slubs(w, h, k, seed, scale=1.0):
    """Dupioni silk's look for an island w by h pixels at k pixels a meter (Ken, 2026-11-04:
    like dupioni.jpeg; the robe's pattern needs no relief, only the silk's weave), scale times
    as large (as many more slubs as cover the same share of it): its weft rows, 1.5 mm apart,
    each a little higher and lighter or lower and darker, changing slowly along it; and its
    slubs, thick weft threads 1 to 6 cm long and 1 to 3 mm thick, swelling and tapering, raised
    and lighter. Returns (height 0 to 1, tone about 1), rows of the island."""
    k *= scale  # its pixels a meter of the dupioni at scale 1
    rib = max(1, round(0.0015 * k))
    cell = 0.08 * k  # the rows' slow changes, about this many pixels long
    along = value_noise(max(1, round(w / cell)), seed)
    i, j = np.meshgrid(np.arange(w), np.arange(h))
    r = j // rib
    f = _rnd(r, 0, 1, seed) * (0.6 + 0.4 * along.np(i / cell, r * 0.37))
    height, tone = 0.3 * f, 0.96 + 0.06 * f
    # the slubs, all at once: each column of each, then each pixel of those, kept where highest
    n = np.arange(round(SLUBS * (w / k) * (h / k)))  # w / k: its meters across at scale 1
    x, y = _rnd(n, 1, 2, seed) * w, _rnd(n, 2, 2, seed) * h
    half = (0.005 + 0.025 * _rnd(n, 3, 2, seed) ** 2) * k
    thick = np.maximum(0.6, (0.0005 + 0.001 * _rnd(n, 4, 2, seed)) * k)  # half its thickness, in pixels
    bright = 0.04 + 0.08 * _rnd(n, 5, 2, seed)
    start, end = (x - half).astype(np.int64), (x + half).astype(np.int64) + 1  # int(), toward 0
    sl = np.repeat(np.arange(len(n)), end - start)
    col = np.arange(len(sl)) - np.repeat(np.cumsum(end - start) - (end - start), end - start) + start[sl]
    swell = np.sqrt(np.maximum(0.0, 1 - ((col - x[sl]) / half[sl]) ** 2))
    hw = thick[sl] * swell
    top, bottom = np.maximum(0, (y[sl] - hw).astype(np.int64)), np.minimum(h, (y[sl] + hw).astype(np.int64) + 2)
    count = np.maximum(0, bottom - top)
    px = np.repeat(np.arange(len(sl)), count)
    row = np.arange(len(px)) - np.repeat(np.cumsum(count) - count, count) + top[px]
    hwp = hw[px]
    d = np.where(hwp != 0, np.abs(row - y[sl][px]) / np.where(hwp != 0, hwp, 1.0), 1.0)
    keep = d < 1
    c = np.sqrt(1 - d[keep] ** 2) * swell[px][keep]
    rows, cols = row[keep], col[px][keep] % w
    np.maximum.at(height, (rows, cols), 0.3 + 0.7 * c)
    np.maximum.at(tone, (rows, cols), 1 + bright[sl][px][keep] * c)
    return height, tone


def mirror(i, n):
    """i into 0 to n - 1, there and back, so a tile repeats without seams (numbers or arrays)."""
    k = i % (2 * n)
    return np.where(k < n, k, 2 * n - 1 - k) if isinstance(k, np.ndarray) else k if k < n else 2 * n - 1 - k


def fill_arrays(color, normal, rect, col, lift, wrap=False):
    """fill's, from arrays over the island: col (rows by columns by 3) and lift (heights in
    pixels); the padding from the nearest, or with wrap from round its width."""
    x0, y0, w, h = rect
    pad = lambda a: np.pad(a, ((PAD, PAD), (PAD, PAD)) + ((0, 0),) * (a.ndim - 2), mode="edge") if not wrap else \
        np.pad(np.pad(a, ((0, 0), (PAD, PAD)) + ((0, 0),) * (a.ndim - 2), mode="wrap"), ((PAD, PAD), (0, 0)) + ((0, 0),) * (a.ndim - 2), mode="edge")
    c = np.clip(pad(np.asarray(col, np.float64)), None, 1.0)
    put(color, x0 - PAD, y0 - PAD, np.concatenate([c, np.ones(c.shape[:2] + (1,))], -1))
    write_normals(normal, rect, pad(np.asarray(lift, np.float64)))


def fill(color, normal, rect, at, wrap=False):
    """An island painted from at(i, j) -> (color, height in pixels) at its pixels (and its
    padding, from the nearest, or with wrap from round its width), its normals from the heights."""
    x0, y0, w, h = rect
    W, H = w + 2 * PAD, h + 2 * PAD
    height = array("f", [0.0]) * (W * H)
    for j in range(-PAD, h + PAD):
        for i in range(-PAD, w + PAD):
            col, lift = at(i % w if wrap else min(max(i, 0), w - 1), min(max(j, 0), h - 1))
            height[(j + PAD) * W + i + PAD] = lift
            xx, yy = x0 + i, y0 + j
            if 0 <= xx < ATLAS and 0 <= yy < ATLAS:
                color.set(xx, yy, tuple(min(1.0, col[q]) for q in range(3)) + (1.0,))
    write_normals(normal, rect, height)


def ghicha():
    """Sample Ghicha.jpg's flat left fold (GHICHA_CROP) as a seamless tile GHICHA_PX, how dark
    each pixel is (0 to 1): its brightness against the blur around it, in linear light (so the
    photo's light and shade go), cross-faded near its edges with itself half a tile round, so it
    wraps. Rows."""
    if GHICHA not in _ghicha:
        W, H = fabric_size(GHICHA)
        x, y, w, h = GHICHA_CROP
        tw, th = GHICHA_PX
        read = ["magick", os.path.join(VIDS, GHICHA), "-crop", f"{round(w * W)}x{round(h * H)}+{round(x * W)}+{round(y * H)}", "+repage",
                "-colorspace", "Gray", "-resize", f"{tw}x{th}!"]
        def make():
            lum, soft = (modl.read_png(subprocess.run(read + more + ["PNG24:-"], check=True, capture_output=True).stdout) for more in ([], ["-blur", "0x40"]))
            linear = lambda img: (lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4))(img.np()[:, :, 0] * img.unit)
            r = linear(lum) / np.maximum(0.02, linear(soft))
            fade = lambda d, band: np.minimum(1.0, (d + 0.5) / band)
            i, j = np.arange(tw), np.arange(th)
            fi, fj = fade(np.minimum(i, tw - 1 - i), tw / 4)[None], fade(np.minimum(j, th - 1 - j), th / 8)[:, None]
            r = r * fi + r[:, (i + tw // 2) % tw] * (1 - fi)
            r = r * fj + r[(j + th // 2) % th] * (1 - fj)
            return np.minimum(1.0, np.maximum(0.0, (GHICHA_LIGHT - r) / GHICHA_RANGE))
        source = os.path.join(VIDS, GHICHA)
        _ghicha[GHICHA] = modl.kept(["ghicha", source, os.path.getmtime(source), read, GHICHA_LIGHT, GHICHA_RANGE], make)
    return _ghicha[GHICHA]


_ghicha = {}
GHICHA_LIGHT, GHICHA_RANGE = 1.4, 1.2  # the brightness (against its blur) that is not dark at all, and how much less is darkest


def ghicha_detail(v):
    """The hammock's detail texture (Ken, 2026-11-04: Sample Ghicha's, as its normal map is):
    ghicha's tile, darkening by up to ghichaStrength (made in linear light, stored sRGB, as
    weave_detail). Returns it and its mean (linear)."""
    return detail_image(np.array(ghicha()), v["ghichaStrength"])


def hammock_tiling(v, density):
    """The hammock's detail texture's tiling, its tiles across the atlas's UVs (u, v): a tile
    ghichaTile wide, as tall as its part of the photo is, where the atlas is at density."""
    W, H = fabric_size(GHICHA)
    tall = v["ghichaTile"] * GHICHA_CROP[3] * H / (GHICHA_CROP[2] * W)
    return ATLAS / density / v["ghichaTile"], ATLAS / density / tall


def paint_bed(color, normal, rect, v, tiling):
    """The hammock's bed, its length across the island: HammockFabric.png (Ken, 2026-11-04: the
    fabric is the source), turned to lie along it; in the normal map Sample Ghicha's weave (Ken,
    2026-11-04: both for the detail texture and the normal map; the pillowed brocade before it
    is normals.py's raised), its light threads raised ghichaRelief over its dark streaks, lying
    just where the detail texture's tiles do (tiling, the material's), so their streaks meet;
    the tile averaged down to the atlas's pixels (it can't show the threads, only the streaks)."""
    x0, y0, w, h = rect
    img = fabric(BED_FABRIC, w, h, turn=True)
    dark = np.array(ghicha(), np.float64)
    tw, th = GHICHA_PX
    nw, nh = max(1, round(ATLAS / tiling[0])), max(1, round(ATLAS / tiling[1]))  # a tile's atlas pixels
    # the tile averaged into its atlas pixels
    sums, counts = np.zeros((nh, nw)), np.zeros((nh, nw))
    rows, cols = (np.arange(th) * nh // th)[:, None], (np.arange(tw) * nw // tw)[None, :]
    np.add.at(sums, (np.broadcast_to(rows, (th, tw)), np.broadcast_to(cols, (th, tw))), dark)
    np.add.at(counts, (np.broadcast_to(rows, (th, tw)), np.broadcast_to(cols, (th, tw))), 1)
    small = sums / np.maximum(1, counts)
    # sampled as the detail texture is (its tiles from the atlas's UV origin, v up), between the small tile's pixels
    i, j = np.meshgrid(np.arange(w), np.arange(h))
    s_ = ((x0 + i + 0.5) / ATLAS * tiling[0]) % 1.0
    t = 1 - ((1 - (y0 + j + 0.5) / ATLAS) * tiling[1]) % 1.0  # down the tile
    a_, b_ = s_ * nw - 0.5, t * nh - 0.5
    ia, ib = np.floor(a_).astype(int), np.floor(b_).astype(int)
    fa, fb = a_ - ia, b_ - ib
    g = lambda p, q: small[q % nh, p % nw]
    d = (g(ia, ib) * (1 - fa) + g(ia + 1, ib) * fa) * (1 - fb) + (g(ia, ib + 1) * (1 - fa) + g(ia + 1, ib + 1) * fa) * fb
    fill_arrays(color, normal, rect, img.np()[:, :, :3] * img.unit, v["ghichaRelief"] * (1 - d))


def paint_robe(color, normal, rect, v):
    """The robe from the front (its back the same), in RobeFemaleFabric.png's left panel (Ken,
    2026-11-04: the robe's): its brocade repeated every robeTile, mirrored so it has no seams;
    and the sash panel's band robeTrim wide for the collar, from the sides of the neck down to
    the sash, crossing as in RobeFemale.png; its weave dupioni's (slubs), raised slubRelief."""
    _, _, w, h = rect
    o = robe_outline(v)
    L, span, trim, relief = v["robeLength"], o["span"], v["robeTrim"], v["slubRelief"]
    k = w / span  # pixels a meter
    cloth = strip(ROBE_FABRIC, ROBE_BROCADE, w=max(4, round(v["robeTile"] * k)))
    img = strip(ROBE_FABRIC, SASH_BAND, h=max(4, round(trim * k)))
    height, tone = slubs(w, h, k, 11, v["slubScale"])
    neck, waist = o["body"][-1][1] * 0.8, v["sashTop"] - 0.005
    # the collar's two sides: (start, end, length), each a band trim wide along start to end
    trims = [((sx * neck, L), (-sx * o["shoulder"][0] * 0.3, waist)) for sx in (-1, 1)]
    trims = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in trims]

    i, j = np.meshgrid(np.arange(w), np.arange(h))
    x, y = (i + 0.5) / k - span / 2, L * (1 - (j + 0.5) / h)
    col = cloth.np()[mirror(j, cloth.h), mirror(i, cloth.w), :3] * cloth.unit
    band = img.np()[:, :, :3]
    for (ax, ay), (bx, by), ll in trims:
        s_ = ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ll
        d = ((bx - ax) * (y - ay) - (by - ay) * (x - ax)) / ll  # to the left of its way
        on = (0 <= s_) & (s_ <= ll) & (np.abs(d) < trim / 2)
        bi = mirror((s_ * k).astype(np.int64), img.w)
        bj = np.clip(np.minimum(img.h - 1, ((0.5 - d / trim) * img.h).astype(np.int64)), 0, img.h - 1)
        col = np.where(on[..., None], band[bj, bi] * img.unit, col)
    fill_arrays(color, normal, rect, col * tone[..., None], relief * height)


def paint_band(color, normal, rect, crop, v, k):
    """A band round the robe, at k pixels a meter: a band of RobeFemaleFabric.png (crop) as high
    as the island, repeated along it, mirrored (as the band's mapping turns, wrapped's), its
    weave the robe's (slubs)."""
    _, _, w, h = rect
    img = strip(ROBE_FABRIC, crop, h=h)
    height, tone = slubs(w, h, k, 12, v["slubScale"])
    i, j = np.meshgrid(np.arange(w), np.arange(h))
    fill_arrays(color, normal, rect, img.np()[j, mirror(i, img.w), :3] * img.unit * tone[..., None], v["slubRelief"] * height)


def paint_sash_front(color, normal, rect, v):
    """The sash from the front, in RobeFemaleFabric.png's right panel (Ken, 2026-11-04: the
    sash's): its band the panel's band; below it the panel's brocade repeated every robeTile,
    mirrored, edged with the band's border robeTrim wide, as RobeFemaleSash.png's ends are; its
    weave the robe's (slubs)."""
    _, _, w, h = rect
    so = sash_outline(v)
    x0, x1, y0, y1 = so["box"]
    k, band, trim, relief = w / (x1 - x0), so["band"], v["robeTrim"], v["slubRelief"]
    rows = so["rows"]
    dy = (rows[0][0] - rows[-1][0]) / max(1, len(rows) - 1)
    xs = x0 + (np.arange(w) + 0.5) / k
    inside = [np.any([(a <= xs) & (xs <= b) for a, b in rows[min(len(rows) - 1, round((j + 0.5) / k / dy))][1]] or [np.zeros(w, bool)], axis=0) for j in range(h)]
    far = np.array(chamfer(inside, w, h))
    cloth = strip(ROBE_FABRIC, SASH_BROCADE, w=max(4, round(v["robeTile"] * k)))
    edge = strip(ROBE_FABRIC, SASH_BAND, h=max(4, round(band * k)))
    border = trim * k / 2
    height, tone = slubs(w, h, k, 13, v["slubScale"])

    i, j = np.meshgrid(np.arange(w), np.arange(h))
    e, c = edge.np()[:, :, :3], cloth.np()[:, :, :3]
    c = np.where((j < band * k)[..., None], e[np.minimum(edge.h - 1, j), mirror(i, edge.w)],  # the band
                 np.where((far < border)[..., None],  # its edge, the band's border inward
                          e[np.clip((far / border * edge.h / 2).astype(np.int64), 0, edge.h - 1), mirror(i + j, edge.w)],
                          c[mirror(j, cloth.h), mirror(i, cloth.w)]))
    fill_arrays(color, normal, rect, c * cloth.unit * tone[..., None], relief * height)


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
    def worleys(i, j, nx, ny, s):  # worley's over arrays, its candidates in its order
        cw, ch = w / nx, h / ny
        ci, cj = _ints(i // cw), _ints(j // ch)
        f1 = f2 = np.full(i.shape, 9.0)
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                a, b = ci + da, cj + db
                aa = a % nx
                d = np.hypot(i / cw - a - _rnd(aa, b, 1, s), j / ch - b - _rnd(aa, b, 2, s))
                nearer = d < f1
                f1, f2 = np.where(nearer, d, f1), np.where(nearer, f1, np.where(d < f2, d, f2))
        e = np.minimum(1.0, (f2 - f1) * 1.5)
        return 1 - (1 - e) * (1 - e)
    nx, ny = max(1, round(w / cell)), max(1, round(h / cell))
    ii, jj = np.meshgrid(np.arange(-PAD, w + PAD) % w, np.clip(np.arange(-PAD, h + PAD), 0, h - 1))
    lump = worleys(ii + 0.5, jj + 0.5, nx, ny, seed) + 0.25 * worleys(ii + 0.5, jj + 0.5, 2 * nx, 2 * ny, seed + 1)
    height = LUMP_HEIGHT * lump + FUZZ * (_rnd(ii, jj, 5, seed) * 2 - 1)
    put(color, x0 - PAD, y0 - PAD, np.broadcast_to(np.array(rgb, np.float32), ii.shape + (4,)))
    write_normals(normal, rect, height)


def swatches():
    """An atlas with the swatches in its top left, a little grain in each, and a flat normal
    (made once, copied after)."""
    if "swatches" not in _wood:
        _wood["swatches"] = make_swatches()
    return tuple(img.copy() for img in _wood["swatches"])


def make_swatches():
    color, normal = modl.Image(ATLAS, ATLAS), modl.Image(ATLAS, ATLAS, (0.5, 0.5, 1.0, 1.0))
    for i, hexcolor in enumerate(SWATCHES):
        rgb = [int(hexcolor[1 + 2 * q:3 + 2 * q], 16) / 255 for q in range(3)]
        x0, y0 = (i % 4) * CELL, (i // 4) * CELL
        for y in range(y0, y0 + CELL):
            for x in range(x0, x0 + CELL):
                g = 0.96 + 0.08 * (((x * 73856093) ^ (y * 19349663)) % 1000 / 1000.0)
                color.set(x, y, (rgb[0] * g, rgb[1] * g, rgb[2] * g, 1.0))
    return color, normal


# Canopy draws in linear color: a texture's stored sRGB values are decoded before they multiply.
to_linear = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
to_srgb = lambda c: c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def tile_noise(n, seed):
    """Smooth noise 0 to 1, f(x, y) in cells of a grid n by n, wrapping both ways (a tile)."""
    def f(x, y):
        a, b = math.floor(x), math.floor(y)
        fx, fy = x - a, y - b
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        g = lambda i, j: _rnd(i % n, j % n, 5, seed)
        top = g(a, b) * (1 - sx) + g(a + 1, b) * sx
        return top * (1 - sy) + (g(a, b + 1) * (1 - sx) + g(a + 1, b + 1) * sx) * sy
    return f


def fiber_detail(v):
    """The family's detail texture (Canopy/General multiplies the color by it, at every LOD): a
    seamless tile of fine fiber, smooth noise at three scales and a per-pixel speck, darkening
    by up to detailStrength (in linear light, as Canopy multiplies; stored sRGB, as its detail
    textures are imported). Returns it and its mean (linear), which the atlas is lightened by."""
    if "fiber" not in _wood:
        n = DETAIL_PX
        big, mid, fine = tile_noise(8, 91), tile_noise(32, 92), tile_noise(96, 93)
        _wood["fiber"] = np.array([[0.3 * big(x / n * 8, y / n * 8) + 0.3 * mid(x / n * 32, y / n * 32) + 0.25 * fine(x / n * 96, y / n * 96)
                                    + 0.15 * _rnd(x, y, 3, 94) for x in range(n)] for y in range(n)])
    return detail_image(_wood["fiber"], v["detailStrength"])


def detail_image(dark, strength):
    """A detail texture darkening by up to strength where dark (0 to 1, rows), made in linear
    light and stored sRGB; and its mean (linear, summed in order, as a loop would)."""
    d = 1 - strength * dark
    srgb = np.where(d <= 0.0031308, d * 12.92, 1.055 * d ** (1 / 2.4) - 0.055)
    img = modl.Image(d.shape[1], d.shape[0])
    img.np()[:, :, :3] = srgb[:, :, None]
    return img, float(np.cumsum(d.ravel())[-1]) / d.size


def weave_detail(v):
    """The silk's detail texture: a seamless tile of WEAVE_THREADS threads each way in a 2/2
    twill (each thread over two, under two, a step along each row, so the ribs run diagonally),
    each float crowned across its thread, the gaps between threads darker, the threads a little
    uneven in tone (rough silk's slubs); darkening by up to silkStrength. Returns it and its mean."""
    if "weave" not in _wood:
        n, t = DETAIL_PX, WEAVE_THREADS
        p = n / t
        slub = tile_noise(t, 95)

        def dark(x, y):
            tx, ty = int(x // p), int(y // p)
            fx, fy = (x + 0.5) / p - tx, (y + 0.5) / p - ty
            warp = (tx - ty) % 4 < 2  # the thread along y is on top
            across, index = (fx, tx) if warp else (fy, ty + t)
            crown = math.sin(math.pi * across)
            tone = 0.85 + 0.3 * (slub(x / p, y / p) if warp else slub(y / p + 7, x / p + 3))
            return min(1.0, (1 - crown) * 0.8 + 0.2 * (1 - tone) + 0.1 * _rnd(index, 0, 4, 96))
        _wood["weave"] = np.array([[dark(x, y) for x in range(n)] for y in range(n)])
    return detail_image(_wood["weave"], v["silkStrength"])


def rock_detail():
    """Amber's detail texture (Canopy's RockDetailFaint.png, DETAIL_META), which the disc takes
    (Ken, 2026-11-04): its guid and its mean (linear)."""
    if "rock" not in _wood:
        meta = modl.canopy_file(DETAIL_META + ".meta").decode()
        img = modl.read_png(modl.canopy_file(DETAIL_META))
        px, u = img.px, img.unit
        total = sum(to_linear(px[i] * u) for i in range(0, len(px), 4))
        _wood["rock"] = (meta.split("guid: ", 1)[1].split()[0], total / (img.w * img.h))
    return _wood["rock"]


def lighten(color, mean, where=None):
    """The atlas's colors over mean (in linear light), so the detail texture leaves them as they
    were on average; with where (a mask, rows by columns), only there (where another detail
    texture lies)."""
    steps = 4096  # finer than the 8 bits the atlas is written in
    table = np.array([to_srgb(min(1.0, to_linear(k / (steps - 1)) / mean)) for k in range(steps)], np.float32)
    px = color.np()
    rgb = np.clip(px[:, :, :3], 0.0, 1.0)
    out = table[np.floor(rgb.astype(np.float64) * (steps - 1) + 0.5).astype(np.int64)]
    if where is None:
        px[:, :, :3] = out
    else:
        px[:, :, :3] = np.where(where[:, :, None], out, px[:, :, :3])


def wood(v):
    """The family atlas's islands, its densities (wood's, the floor's, carvings'), the grain's
    tile, and around(rect, density): meters across per pixel along a wrapped island's width,
    stretched so whole tiles go round."""
    isl = islands(v)
    d, fd, cd, tile = isl["density"], isl["floorDensity"], isl["carveDensity"], v["woodTile"]

    def around(rect, density):
        m = rect[2] / density
        return max(1, round(m / tile)) * tile / m / density
    return isl, d, fd, cd, tile, around


def paint_barrel(color, normal, v):
    isl, d, _, _, tile, around = wood(v)
    staves, count = isl["staves"], stave_count(v)
    k = around(staves, d)
    paint_wood(color, normal, staves, lambda i, j: (staves[3] - j) / d, lambda i, j: i * k, WOOD_MID, tile, d, 17,
               lambda i, j: i / staves[2] * count, staves[2] / count)
    lid = isl["lid"]
    lid_boards = max(2, round(lid[3] / d / v["staveWidth"]))
    # three times the staves' relief: lit from above, as a lid mostly is, relief hardly shows
    # (Ken, 2026-11-04: the lid is missing its normal map)
    paint_wood(color, normal, lid, lambda i, j: i / d, lambda i, j: j / d, WOOD_DARK, tile, d, 29,
               lambda i, j: j / lid[3] * lid_boards, lid[3] / lid_boards, bump=LID_BUMP)
    return [staves, lid]


def paint_floor(color, normal, v):
    """The floor's end grain: the grain laid round in rings (whole tiles around), wobbling a little."""
    isl, _, fd, _, tile, _ = wood(v)
    floor, R = isl["floor"], v["discDiameter"] / 2

    def polar(i, j):
        x, z = (i + 0.5) / floor[2] * 2 * R - R, (j + 0.5) / floor[3] * 2 * R - R
        a = np.arctan2(z, x)
        r = np.hypot(x, z)
        return a, r + 0.02 * np.sin(3 * a + 5 * r) + 0.012 * np.sin(7 * a - 3 * r)
    paint_wood(color, normal, floor, lambda i, j: polar(i, j)[0] / (2 * math.pi) * 16 * tile,
               lambda i, j: polar(i, j)[1], WOOD, tile, fd,
               relief=combine(unevenness(floor, 0.4 * fd, 2.0, 61), cracks(floor, checks(floor, 9, 0.55, 67)),
                              unevenness(floor, 2.5, v["floorRough"], 69, 0.03)))  # rough (Ken, 2026-11-04: not too perfect)
    return [floor]


def paint_rim(color, normal, v):
    """The rim: grain around, its side carved (its bevels plain)."""
    isl, _, _, cd, tile, around = wood(v)
    rim = isl["rim"]
    t, inset = v["discThickness"], min(v["rimInset"], v["discThickness"] / 2)
    bevel = round(inset * math.sqrt(2) / (2 * inset * math.sqrt(2) + t - 2 * inset) * rim[3])
    rim_repeat = rim[2] / cd
    k = around(rim, cd)
    paint_wood(color, normal, rim, lambda i, j: i * k, lambda i, j: j / cd, WOOD_DARK, tile, cd,
               relief=combine(band_relief(rim, max(1, round(rim_repeat / (2 * (t - 2 * inset)))), bevel, rim[3] - bevel, DISC_MOTIF),
                              unevenness(rim, 0.15 * cd, 2.0, 71)))
    return [rim]


def paint_stool(color, normal, v):
    """The stool: its edge carved all over; its seat and legs faceted."""
    isl, d, _, cd, tile, around = wood(v)
    edge = isl["seatEdge"]
    k = around(edge, cd)
    paint_wood(color, normal, edge, lambda i, j: i * k, lambda i, j: j / cd, WOOD_DARK, tile, cd,
               relief=combine(band_relief(edge, max(1, round(edge[2] / edge[3] / 2)), 0, edge[3], STOOL_MOTIF),
                              unevenness(edge, 0.08 * cd, 1.5, 73)))
    seat = isl["seat"]
    paint_wood(color, normal, seat, lambda i, j: i / d, lambda i, j: j / d, WOOD_MID, tile, d,
               relief=combine(facets(seat, 0.035 * d, 0.035 * d, 0.25, 5), cracks(seat, checks(seat, 3, 0.4, 79, 1.5), 1.2, 2.0)))
    leg = isl["leg"]
    k = around(leg, d)
    paint_wood(color, normal, leg, lambda i, j, h=leg[3]: (h - j) / d, lambda i, j, k=k: i * k, WOOD_MID, tile, d,
               relief=facets(leg, 0.03 * d, 0.08 * d, 0.25, 11))
    return [edge, seat, leg]


def paint_post(color, normal, v):
    """The post: its grain along it."""
    isl, d, _, _, tile, around = wood(v)
    post = isl["post"]
    k = around(post, d)
    paint_wood(color, normal, post, lambda i, j, h=post[3]: (h - j) / d, lambda i, j, k=k: i * k, WOOD_DARK, tile, d)
    return [post]


def paint_perch(color, normal, v):
    isl, d, _, _, tile, around = wood(v)
    perch_rect = isl["perch"]
    k = around(perch_rect, d)
    knot = (round(perch_rect[3] * 0.84), round(perch_rect[3] * 0.96))
    paint_wood(color, normal, perch_rect, lambda i, j: j / d, lambda i, j: i * k, WOOD_MID, tile, d,
               relief=combine(unevenness(perch_rect, 0.05 * d, 1.2, 83), band_relief(perch_rect, 3, knot[0], knot[1], STOOL_MOTIF)))
    return [perch_rect]


def paint_roof_leaf(color, normal, v):
    rect = islands(v)["leaf"]
    paint_leaf(color, normal, rect)
    return [rect]


def paint_cocoon(color, normal, v):
    isl = islands(v)
    paint_lumps(color, normal, isl["cocoon"], COCOON, v["cocoonLump"] * isl["cocoonDensity"], 41)
    return [isl["cocoon"]]


def paint_the_mat(color, normal, v):
    isl = islands(v)
    paint_mat(color, normal, isl["mat"], v, isl["floorDensity"])
    return [isl["mat"]]


def paint_the_oven(color, normal, v):
    isl = islands(v)
    paint_oven(color, normal, isl, v, isl["density"])
    return [isl[k] for k in ("ovenBase", "ovenDome", "ovenFlue", "shelf", "bench")]


# the family atlas's painters (modl.paint_islands): (name, asset, painter)
WOOD_TASKS = [("barrel", "Barrel", paint_barrel), ("floor", "HutDisc", paint_floor), ("rim", "HutDisc", paint_rim),
              ("stool", "Stool", paint_stool), ("post", "HutPost", paint_post), ("perch", "Perch", paint_perch),
              ("leaf", "RoofLeaf", paint_roof_leaf), ("cocoon", "Cocoon", paint_cocoon), ("mat", "Mat", paint_the_mat),
              ("oven", "Oven", paint_the_oven)]


def textures(v):
    """The swatches; the wood islands; the leaf; a flat normal elsewhere; lightened for the
    detail texture. Each island is painted again only when a var it reads has changed, on all
    cores (modl.paint_islands)."""
    color, normal = swatches()
    # what the painters share, read once before they fork: the grain at each density
    isl = islands(v)
    for density in (isl["density"], isl["floorDensity"], isl["carveDensity"]):
        wood_source(max(8, round(v["woodTile"] * density)))
    leaf_source()
    by = modl.paint_islands(color, normal, WOOD_TASKS, v, PAD)
    v = modl.Reads(v)  # the reads outside any island's, every asset's
    lighten(color, fiber_detail(v)[1])
    by.setdefault("", set()).update(v.by.get("", set()))
    modl.note_texture_uses(FAMILY, FAMILY, by)
    return modl.TrimSheet(ATLAS, ATLAS, islands(v)["density"]), color, normal


def paint_the_bed(color, normal, v):
    isl = silk_islands(v)
    paint_bed(color, normal, isl["bed"], v, hammock_tiling(v, isl["bedDensity"]))
    return [isl["bed"]]


def paint_the_robe(color, normal, v):
    isl = silk_islands(v)
    paint_robe(color, normal, isl["robe"], v)
    return [isl["robe"]]


def paint_trim(color, normal, v):
    isl = silk_islands(v)
    paint_band(color, normal, isl["trim"], ROBE_BAND, v, isl["silkDensity"])
    return [isl["trim"]]


def paint_sash_band(color, normal, v):
    isl = silk_islands(v)
    paint_band(color, normal, isl["sashBand"], SASH_BAND, v, isl["silkDensity"])
    return [isl["sashBand"]]


def paint_sash(color, normal, v):
    isl = silk_islands(v)
    paint_sash_front(color, normal, isl["sash"], v)
    return [isl["sash"]]


SILK_TASKS = [("bed", "Hammock", paint_the_bed), ("robe", "RobeFemale", paint_the_robe), ("trim", "RobeFemale", paint_trim),
              ("sashBand", "RobeFemale", paint_sash_band), ("sash", "RobeFemale", paint_sash)]


def silk_textures(v):
    """The silk's atlas: the swatches (the bars and cords take theirs), the hammock's bed, the
    robe and its sash (modl.paint_islands, as textures'); lightened for their detail textures,
    the hammock's (its bed and its swatches) for ghicha's, the rest for the weave."""
    color, normal = swatches()
    ghicha()  # shared by the bed and its detail texture: made before the painters fork
    by = modl.paint_islands(color, normal, SILK_TASKS, v, PAD)
    v = modl.Reads(v)
    isl = silk_islands(v)
    bx, by_, bw, bh = isl["bed"]
    hammock = np.zeros((ATLAS, ATLAS), bool)
    hammock[max(0, by_ - PAD):by_ + bh + PAD, max(0, bx - PAD):bx + bw + PAD] = True
    for s in (SILK, SILK_GREEN, CORD):
        hammock[(s // 4) * CELL:(s // 4 + 1) * CELL, (s % 4) * CELL:(s % 4 + 1) * CELL] = True
    v.asset = "RobeFemale"
    lighten(color, weave_detail(v)[1], ~hammock)
    v.asset = "Hammock"
    lighten(color, ghicha_detail(v)[1], hammock)
    for k, x in v.by.items():
        by.setdefault(k, set()).update(x)
    modl.note_texture_uses(FAMILY, SILK_ATLAS, by)
    return color, normal


def more_textures(v):
    """The family's other atlases, for Tweak's previews: [(assets, color, normal)]."""
    return [(sorted(SILK_MODELS), *silk_textures(v))]


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
    f32 = lambda x: np.asarray(x, np.float32).astype(np.float64)  # as stored in a float array
    j = np.arange(-PAD, ih + PAD)
    ty = np.minimum(np.maximum(y0 + (j + 0.5) / ih * (y1 - y0), y0 + 0.5), y1 - 0.5)
    ab = np.array([leaf_edges(float(t)) for t in ty])
    a, b = ab[:, :1], ab[:, 1:]
    tx = np.minimum(np.maximum(x0 + (np.arange(-PAD, iw + PAD)[None] + 0.5) / iw * (x1 - x0), a + 0.5), b - 0.5)
    ty = np.broadcast_to(ty[:, None], tx.shape)
    # img.sample's bilinear, over arrays
    sx, sy = np.minimum(np.maximum(tx - 0.5, 0.0), img.w - 1.0), np.minimum(np.maximum(ty - 0.5, 0.0), img.h - 1.0)
    xa, ya = sx.astype(np.int64), sy.astype(np.int64)
    xb, yb = np.minimum(xa + 1, img.w - 1), np.minimum(ya + 1, img.h - 1)
    fx, fy = sx - xa, sy - ya
    p, u = img.np().astype(np.float64), img.unit
    ch = lambda k: ((p[ya, xa, k] * (1 - fx) + p[ya, xb, k] * fx) * (1 - fy) + (p[yb, xa, k] * (1 - fx) + p[yb, xb, k] * fx) * fy) * u
    bright = f32((ch(0) + ch(1) + ch(2)) / 3)
    # how far in from its edge, as a share of the leaf's widest
    edge = f32(np.minimum(tx - a, b - tx) / (x1 - x0))
    # the blur: a box 11 px wide, by rows then columns, each sum left to right as a loop's
    R_ = 5

    def box(x, axis):
        n = x.shape[axis]
        total, count = np.zeros(x.shape), np.zeros(x.shape)
        for off in range(-R_, R_ + 1):
            idx = np.arange(n) + off
            ok = (idx >= 0) & (idx < n)
            shifted = np.take(x, np.clip(idx, 0, n - 1), axis=axis)
            okb = ok[:, None] if axis == 0 else ok[None, :]
            total = total + np.where(okb, shifted, 0.0)
            count = count + okb
        return total / count
    rows = f32(box(bright, 1))
    blur = box(rows, 0)
    crinkle = unevenness(rect, 24, CRINKLE, 89, 0.0)
    jj, ii = np.meshgrid(np.arange(H) - PAD, np.arange(W) - PAD, indexing="ij")
    vein = bright - blur
    height = VEIN * vein + crinkle.np(ii, jj)[0]
    f = np.minimum(np.maximum(0.5 + LEAF_CONTRAST * (bright / mean - 1), 0.0), 1.2)
    c = [(lo[q] + (hi[q] - lo[q]) * f) * (1 + VEIN_TONE * vein) for q in range(3)]
    e = np.maximum(0.0, 1 - edge / LEAF_EDGE[1]) ** 2 * LEAF_EDGE[2]
    col = np.stack([np.minimum(1.0, np.maximum(0.0, c[q] * (1 - e) + brown[q] * e)) for q in range(3)] + [np.ones(e.shape)], -1)
    put(color, ix - PAD, iy - PAD, col)
    write_normals(normal, rect, height)


def build(v, install_too=False, report=print):
    out = modl.HERE
    bs = assets(v, measure="--measure" in sys.argv)
    names = set()
    for a in bs:
        silk = a.name in SILK_MODELS
        for mesh in a.lods:
            modl.write_obj(os.path.join(out, mesh.name + ".obj"), mesh, (SILK_ATLAS if silk else FAMILY) + ".mtl", SILK_MATERIAL if silk else MATERIAL)
            names.add(mesh.name)
        report(f"{a.name}: {a.size:.2f} m; " + ", ".join(f"LOD{k} {len(m.tris)} triangles" for k, m in enumerate(a.lods))
               + "; LOD1 from {:.0f} m ({:.1f} cm off), LOD2 from {:.0f} m ({:.1f} cm), culled at {:.0f} m".format(
                   a.distances[0], a.errors[0] * 100, a.distances[1], a.errors[1] * 100, a.distances[2]))
    modl.write_mtl(os.path.join(out, FAMILY + ".mtl"), MATERIAL, FAMILY)
    modl.write_mtl(os.path.join(out, SILK_ATLAS + ".mtl"), SILK_MATERIAL, SILK_ATLAS)
    _, color, normal = textures(v)
    silk_color, silk_normal = silk_textures(v)
    for atlas, images in ((FAMILY, (color, normal, fiber_detail(v)[0])), (SILK_ATLAS, (silk_color, silk_normal, weave_detail(v)[0]))):
        for kind, img in zip(("tx", "normal", "detail"), images):
            modl.write_png(os.path.join(out, f"{atlas}_{kind}.png"), img)
    modl.write_png(os.path.join(out, f"{HAMMOCK_DETAIL}_detail.png"), ghicha_detail(v)[0])
    isl, sil = islands(v), silk_islands(v)
    report(f"{FAMILY}_tx.png, {FAMILY}_normal.png: {ATLAS}x{ATLAS}, {len(SWATCHES)} swatches, wood at {isl['density']:.0f} px/m, the floor at {isl['floorDensity']:.0f}; "
           f"{SILK_ATLAS}: the robe at {sil['silkDensity']:.0f} px/m, the bed at {sil['bedDensity']:.0f}")
    if not install_too:
        return []
    # the detail textures' tiling: atlas UVs to tiles, a tile its meters where the atlas has that density
    tiling = lambda density, meters: (ATLAS / density / meters,) * 2
    source = modl.canopy_file(SOURCE_MATERIAL).decode()
    material = lambda tex, nrm, det: modl.material_yaml(source, MATERIAL, tex, nrm, tiling(isl["density"], v["detailTile"]), det,
                                                        {"_NormalStrength": v["normalStrength"], "_Glossiness": v["gloss"], "_Brightness": v["brightness"]})
    silk = lambda tex, nrm, det: modl.material_yaml(source, SILK_MATERIAL, tex, nrm, tiling(sil["silkDensity"], WEAVE_THREADS * v["silkThread"]), det,
                                                    {"_Glossiness": v["silkGloss"], "_NormalStrength": v["silkNormalStrength"], "_Brightness": v["silkBrightness"]})
    # the hammock: the silk's atlases, its detail texture ghicha's
    bed = lambda tex, nrm, det: modl.material_yaml(source, HAMMOCK_MATERIAL, tex, nrm, hammock_tiling(v, sil["bedDensity"]), det,
                                                   {"_Glossiness": v["hammockGloss"], "_NormalStrength": v["hammockNormalStrength"], "_Brightness": v["hammockBrightness"]})
    # the disc: the family's atlases, Amber's detail texture, a tile discDetailTile where the atlas is at floorDensity
    # (brighter than discBrightness, as Amber's darkens more than the fiber the atlas was lightened for: over half)
    bright = v["discBrightness"] * disc_brightening(v)
    disc = lambda tex, nrm: modl.material_yaml(source, DISC_MATERIAL, tex, nrm, tiling(isl["floorDensity"], v["discDetailTile"]), rock_detail()[0],
                                               {"_Brightness": bright, "_NormalStrength": v["discNormalStrength"], "_Glossiness": v["discGloss"]})
    return modl.install_assets(FAMILY, MATERIAL, bs, material, COLOR_META, NORMAL_META, DETAIL_META,
                               [(FAMILY, DISC_MATERIAL, disc, COLOR_META, NORMAL_META),
                                (SILK_ATLAS, SILK_MATERIAL, silk, COLOR_META, NORMAL_META, DETAIL_META),
                                (SILK_ATLAS, HAMMOCK_MATERIAL, bed, COLOR_META, NORMAL_META, DETAIL_META, HAMMOCK_DETAIL)])


def disc_brightening(v):
    """How much brighter than discBrightness the disc's material is: as much as Amber's detail
    darkens more on average than the fiber the family's atlas was lightened for."""
    return fiber_detail(v)[1] / rock_detail()[1]


def live(v):
    """Tweak's live vars (modl.Var's live; serve.py says the form): what each sets on which
    materials, so layout shows them as the drag goes and the server only builds them when
    Tweak is left (Ken, 2026-11-04: shader properties should move in real time)."""
    isl, sil = islands(v), silk_islands(v)
    guid = lambda material: modl.material_guid(FAMILY, material)
    # a detail texture's tiling k / value: a tile value (in the tag's unit) where the atlas is at density
    tiling = lambda name, density, per=1.0: ATLAS / density / (per * modl.UNITS[tags()[name][1]])
    strength = lambda material, name, mean: {"material": guid(material), "strength": v[name], "mean": mean}
    return {
        "normalStrength": [{"material": guid(MATERIAL), "property": "_NormalStrength"}],
        "discNormalStrength": [{"material": guid(DISC_MATERIAL), "property": "_NormalStrength"}],
        "silkNormalStrength": [{"material": guid(SILK_MATERIAL), "property": "_NormalStrength"}],
        "hammockNormalStrength": [{"material": guid(HAMMOCK_MATERIAL), "property": "_NormalStrength"}],
        "gloss": [{"material": guid(MATERIAL), "property": "_Glossiness"}],
        "discGloss": [{"material": guid(DISC_MATERIAL), "property": "_Glossiness"}],
        "silkGloss": [{"material": guid(SILK_MATERIAL), "property": "_Glossiness"}],
        "hammockGloss": [{"material": guid(HAMMOCK_MATERIAL), "property": "_Glossiness"}],
        "brightness": [{"material": guid(MATERIAL), "property": "_Brightness"}],
        "discBrightness": [{"material": guid(DISC_MATERIAL), "property": "_Brightness", "scale": disc_brightening(v)}],
        "silkBrightness": [{"material": guid(SILK_MATERIAL), "property": "_Brightness"}],
        "hammockBrightness": [{"material": guid(HAMMOCK_MATERIAL), "property": "_Brightness"}],
        "detailTile": [{"material": guid(MATERIAL), "tiling": tiling("detailTile", isl["density"])}],
        "discDetailTile": [{"material": guid(DISC_MATERIAL), "tiling": tiling("discDetailTile", isl["floorDensity"])}],
        "silkThread": [{"material": guid(SILK_MATERIAL), "tiling": tiling("silkThread", sil["silkDensity"], WEAVE_THREADS)}],
        # the disc's brightness follows the fiber's mean, as the atlas is lightened by it: unchanged
        "detailStrength": [strength(MATERIAL, "detailStrength", fiber_detail(v)[1])],
        "silkStrength": [strength(SILK_MATERIAL, "silkStrength", weave_detail(v)[1])],
        "ghichaStrength": [strength(HAMMOCK_MATERIAL, "ghichaStrength", ghicha_detail(v)[1])],
    }


def uses(v, live_vars):
    """Each asset's vars, for Tweak's list while it is carried: those its models read themselves
    (modl.model_uses; packing islands aside), its textures' (the last textures run's, and those
    its atlas's painting read for every asset), and its material's live ones (live_vars, live's)."""
    saved = modl.texture_uses(FAMILY)
    out = {}
    for name, _, _ in MODELS:
        own = modl.model_uses(name) or set()
        atlas = saved.get(SILK_ATLAS if name in SILK_MODELS else FAMILY, {})
        material = modl.material_guid(FAMILY, HAMMOCK_MATERIAL if name == "Hammock" else SILK_MATERIAL if name in SILK_MODELS
                                      else DISC_MATERIAL if name == "HutDisc" else MATERIAL)
        mine = {n for n, sets in live_vars.items() if any(x["material"] == material for x in sets)}
        out[name] = sorted(set(own) | set(atlas.get(name, [])) | set(atlas.get("", [])) | mine)
    return out


def main():
    unused = modl.unused_tags(tags(), VARS)
    if unused:
        print(f"note: tags not used yet: {', '.join(unused)}")
    written = build(values(), "--write" in sys.argv)
    if "--write" in sys.argv:
        print(f"Canopy Assets/Modl/{FAMILY}: {len(written)} files changed")


if __name__ == "__main__":
    main()
