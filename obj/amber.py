"""Amber: the game's money, a melted nodule of resin after vids/Sample Amber (modl SPEC.md).

The spec is `# Modl Amber` in docs/models/Amber.md; its tweakvars hold every number. Readings
(Claude, 2026-11-07):
- The shape is a smooth union of ellipsoids, a body and lobes round its rim: smooth where it bulges,
  creased where lobes meet, as the samples are. Every direction from the middle meets it once, so
  it is a radius per direction.
- That makes the mesh an octahedral grid: the sphere of directions unfolded into the unit square,
  its poles on the thin axis (X). The grid is the UV layout, one island at nearly even density with
  no atlas packing, and each triangle stays in one face of the octahedron, so the fold's corners
  are simply vertices twice. The maps are functions of the point in space, so nothing shows there.
- Opaque, seeming translucent (Canopy/Amber, Assets/Shaders/Amber.shader, does the rest): the color
  map is what lies inside, the same all the way round, read twice, once shifted by the view so it
  sits behind the surface. Nothing view-dependent is baked: a rim is wherever the edge is from
  here, so it is the shader's (Ken, 2026-11-07: a map of thickness along one axis painted a stripe
  round the stone).
- Installed as .asset meshes, not the OBJs other families use: Canopy's prefabs name the mesh itself,
  and an .asset's id is always 4300000, where an OBJ's can't be worked out here. The OBJs still
  go in obj/ (the preview, Tweak).

  python3 obj/amber.py           writes obj/Amber_LOD*.obj and atlases
  python3 obj/amber.py --write   also installs them into Canopy's Assets/Modl/Amber
  python3 obj/amber.py --write --rewire   and points Canopy's amber at them, from the committed files
Layout's Tweak drives it through obj/serve.py.
"""

import math
import os
import re
import subprocess
import sys

import numpy as np

import modl

FAMILY = "Amber"
MATERIAL = "ModlAmber"
PREFAB = "AmberModel"  # not Amber: layout finds prefabs by name, and Items/Amber.prefab is the game's
LAYERED, CORE_MATERIAL, SHELL_MATERIAL = "AmberLayered", "ModlAmberCore", "ModlAmberShell"
BRIGHT, BRIGHT_MATERIAL = "AmberBright", "ModlAmberBright"
GAME_MATERIAL = BRIGHT_MATERIAL  # what --rewire puts on Canopy's amber (Ken, 2026-11-07: enough for now)
GENERAL = "70f970fb0365c514d978918d4586c7ae"  # Canopy/General
DOC = os.path.join(modl.DOCS, "models", "Amber.md")
HEADING = "Modl Amber"
VARS = {
    "amberLength": modl.Var(geometry=True, textures=True, min=0.02, max=0.5),
    "amberWidth": modl.Var(geometry=True, textures=True, min=0.02, max=0.5),
    "amberThickness": modl.Var(geometry=True, textures=True, min=0.01, max=0.5),
    "lobeCount": modl.Var(geometry=True, textures=True, min=3, max=12),
    "lobeSize": modl.Var(geometry=True, textures=True, min=0.1, max=0.8),
    "creaseSoftness": modl.Var(geometry=True, textures=True, min=1, max=40),
    "seed": modl.Var(rebuild=True, min=0, max=9999),
    "cloudCount": modl.Var(textures=True, min=0, max=5),
    "atlasPixels": modl.Var(rebuild=True, min=128, max=2048),
    "lod0Grid": modl.Var(geometry=True, min=4, max=48),
    "lod1Grid": modl.Var(geometry=True, min=4, max=48),
    "lod2Grid": modl.Var(geometry=True, min=2, max=48),
    "lod1Distance": modl.Var(geometry=True, min=0.2, max=100),
    "lod2Distance": modl.Var(geometry=True, min=0.2, max=100),
    "cullDistance": modl.Var(geometry=True, min=1, max=200),
}
# sampled from the photographs, as sRGB
HONEY, GOLD, ORANGE, RED, DEEP, GREEN = (np.array(c) / 255 for c in ((255, 208, 40), (255, 160, 16), (250, 104, 6), (226, 40, 6), (140, 22, 4), (136, 150, 36)))
SHADER, SHELL_SHADER = "Assets/Shaders/Amber.shader", "Assets/Shaders/AmberShell.shader"
TEMPLATE_MESH = "Assets/Meshes/GridObsidianDagger/GridObsidianDagger_part000_L0.asset"
COLOR_META, NORMAL_META = "Assets/Texture/Amber0.png", "Assets/Texture/OD_Mat_normal.jpg"
OLD_MESH, OLD_MATERIAL = "d9bd2234763aaa744a0c895610d18513", "35cd039054957af4ba994447b1125570"
# the prefabs with the old amber's LODGroup, which gain levels, and those that only draw it
LOD_PREFABS = ["Assets/Prefabs/Items/Amber.prefab", "Assets/Prefabs/Items/AmberFromResin.prefab", "Assets/Prefabs/Items/AmberObject.prefab"]
PLAIN_FILES = ["Assets/Prefabs/Hand/Hand.prefab", "Assets/Prefabs/Idols/SeekerIdol.prefab", "Assets/Prefabs/Items/Payment10Amber.prefab", "Assets/Scenes/Game.unity"]


class Asset:
    def __init__(self, name, lods, size, heights):
        self.name, self.lods, self.size, self.heights = name, lods, size, heights


def tags():
    modl.check_sources(DOC, HEADING, ["Canopy Assets/Prefabs/Items/Amber.prefab"])
    return modl.read_tags(DOC, HEADING, VARS)


def values(overrides=None):
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


# ---------- the shape ----------
def lobes(v):
    """Ellipsoids in unit space (thin x, y its length, z its width): centers and radii."""
    r = np.random.default_rng(int(v["seed"]))
    centers, radii = [(0.0, 0.0, 0.0)], [(0.5, 0.86, 0.8)]
    n = int(round(v["lobeCount"]))
    start = r.uniform(0, 2 * math.pi)
    for k in range(n):
        a = start + 2 * math.pi * (k + r.uniform(-0.42, 0.42)) / n
        size = v["lobeSize"] * r.uniform(0.55, 1.45)
        out = r.uniform(0.86, 1.0) - size * 0.82
        centers.append((r.uniform(-0.2, 0.2), out * math.cos(a), out * math.sin(a)))
        radii.append((size * r.uniform(1.0, 1.3), size, size * r.uniform(0.85, 1.1)))
    return np.array(centers), np.array(radii)


def undulation(d):
    """A slow swell over it all, as melted resin has, by direction."""
    return 1 + 0.1 * (fbm(d, 1.7, 61, 2) - 0.5)


def field(p, centers, radii, soft):
    """A smooth minimum of the ellipsoids' distances at points p (n, 3): negative inside."""
    d = np.stack([(np.linalg.norm((p - c) / r, axis=1) - 1) * r.mean() for c, r in zip(centers, radii)])
    least = d.min(axis=0)
    return least - soft * np.log(np.exp(-(d - least) / soft).sum(axis=0))


def radius(dirs, shape):
    """Where each direction leaves the shape (bisection from the middle, which is inside)."""
    lo, hi = np.zeros(len(dirs)), np.full(len(dirs), 2.0)
    for _ in range(18):
        mid = (lo + hi) / 2
        out = field(dirs * mid[:, None], *shape) > 0
        hi = np.where(out, mid, hi)
        lo = np.where(out, lo, mid)
    return (lo + hi) / 2


def gradient(p, shape):
    """The swollen shape's outward normal at points on it."""
    e = 2e-3
    swollen = lambda q: field(q / undulation(q / np.linalg.norm(q, axis=1, keepdims=True))[:, None], *shape)
    g = np.stack([swollen(p + o) - swollen(p - o) for o in np.eye(3) * e], axis=1)
    return g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-12)


def unfold(u, w):
    """The octahedral map: u, w in 0..1 to unit directions, the poles on x."""
    a, b = 2 * u - 1, 2 * w - 1
    z = 1 - np.abs(a) - np.abs(b)
    fold = z < 0
    y = np.where(fold, (1 - np.abs(b)) * np.sign(a + 1e-12), a)
    x = np.where(fold, (1 - np.abs(a)) * np.sign(b + 1e-12), b)
    d = np.stack([z, y, x], axis=1)
    return d / np.linalg.norm(d, axis=1, keepdims=True)


def surface(u, w, v):
    """Points on the amber, and normals, in meters (Unity's axes), for uvs."""
    shape = (*lobes(v), v["creaseSoftness"] / 400)
    s = scale(v, shape)
    d = unfold(u, w)
    plain = d * radius(d, shape)[:, None]  # on the field, before the swell
    unit = plain * undulation(d)[:, None]
    p = (unit - s[0]) * s[1]
    n = gradient(unit, shape) / s[1]
    return p, n / np.linalg.norm(n, axis=1, keepdims=True), unit, shape, plain


_scales = {}


def scale(v, shape):
    """The unit shape's middle and the scale that fits it to the spec's sizes."""
    key = (v["seed"], v["lobeCount"], v["lobeSize"], v["creaseSoftness"], v["amberLength"], v["amberWidth"], v["amberThickness"])
    if key not in _scales:
        g = np.linspace(0, 1, 97)
        u, w = (a.ravel() for a in np.meshgrid(g, g))
        d = unfold(u, w)
        p = d * (radius(d, shape) * undulation(d))[:, None]
        lo, hi = p.min(axis=0), p.max(axis=0)
        _scales[key] = ((lo + hi) / 2, np.array([v["amberThickness"], v["amberLength"], v["amberWidth"]]) / (hi - lo))
    return _scales[key]


# ---------- meshes ----------
def grid_mesh(name, cells, v, inset=0.0):
    """An octahedral grid, right-handed for the OBJ (x negated from Unity's), each triangle in one
    face of the octahedron: a cell's diagonal runs along the fold."""
    n = int(round(cells / 2)) * 2
    g = np.arange(n + 1) / n
    u, w = (a.ravel() for a in np.meshgrid(g, g))
    p, nrm = surface(u, w, v)[:2]
    p = p - nrm * inset
    mesh = modl.Mesh(name)
    flip = np.array([-1.0, 1.0, 1.0])
    ids = [mesh.vertex(tuple(float(x) for x in a * flip), tuple(float(x) for x in b * flip), (float(s), float(t))) for a, b, s, t in zip(p, nrm, u, w)]
    at = lambda i, j: ids[j * (n + 1) + i]
    for j in range(n):
        for i in range(n):
            q = [at(i, j), at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)]
            same = (i < n // 2) == (j < n // 2)  # which way the fold's diagonal runs here
            for tri in ((q[0], q[1], q[3]), (q[1], q[2], q[3])) if same else ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
                a, b, c = (np.array(mesh.verts[k][0]) for k in tri)
                outward = np.cross(b - a, c - a) @ np.array(mesh.verts[tri[0]][1])
                mesh.tris.append(tri if outward >= 0 else (tri[0], tri[2], tri[1]))
    mesh.segments = n
    return mesh


def assets(v):
    meshes = [grid_mesh(f"{FAMILY}_LOD{k}", v[f"lod{k}Grid"], v) for k in range(3)]
    d1 = v["lod1Distance"]
    d2 = max(v["lod2Distance"], d1 * 1.01)
    cull = max(v["cullDistance"], d2 * 1.01)
    size = max(v["amberLength"], v["amberWidth"], v["amberThickness"])
    return [Asset(PREFAB, meshes, size, [size / (2 * d) for d in (d1, d2, cull)])]


def asset_text(mesh):
    """A Unity Mesh .asset of a modl mesh: Unity's axes, tangents from the uvs."""
    p = np.array([m[0] for m in mesh.verts]) * [-1, 1, 1]
    n = np.array([m[1] for m in mesh.verts]) * [-1, 1, 1]
    uv = np.array([m[2] for m in mesh.verts])
    tris = np.array([(t[0], t[2], t[1]) for t in mesh.tris])  # back to Unity's winding
    t, b = np.zeros_like(p), np.zeros_like(p)
    e1, e2 = p[tris[:, 1]] - p[tris[:, 0]], p[tris[:, 2]] - p[tris[:, 0]]
    d1, d2 = uv[tris[:, 1]] - uv[tris[:, 0]], uv[tris[:, 2]] - uv[tris[:, 0]]
    det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(det) > 1e-12, 1 / np.where(det == 0, 1, det), 0)[:, None]
    ft, fb = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) * r, (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) * r
    for k in range(3):
        np.add.at(t, tris[:, k], ft)
        np.add.at(b, tris[:, k], fb)
    t -= n * (t * n).sum(axis=1, keepdims=True)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
    w = np.where((np.cross(n, t) * b).sum(axis=1) < 0, -1.0, 1.0)
    data = np.concatenate([p, n, t, w[:, None], uv], axis=1).astype("<f4")
    vec = lambda a: f"{{x: {a[0]:.7g}, y: {a[1]:.7g}, z: {a[2]:.7g}}}"
    box = lambda q: (vec((q.min(axis=0) + q.max(axis=0)) / 2), vec((q.max(axis=0) - q.min(axis=0)) / 2))
    c, e = box(p)
    sub, at = "  m_SubMeshes:\n", 0
    for count in getattr(mesh, "submeshes", [len(tris)]):
        part = tris[at:at + count]
        first, last = int(part.min()), int(part.max())
        sc, se = box(p[first:last + 1])
        sub += f"  - serializedVersion: 2\n    firstByte: {at * 6}\n    indexCount: {count * 3}\n    topology: 0\n    baseVertex: 0\n    firstVertex: {first}\n    vertexCount: {last - first + 1}\n    localAABB:\n      m_Center: {sc}\n      m_Extent: {se}\n"
        at += count
    text = modl.canopy_file(TEMPLATE_MESH).decode().replace("\r\n", "\n")
    text = re.sub(r"m_Name: .*", f"m_Name: {mesh.name}", text, count=1)
    text = re.sub(r" {2}m_SubMeshes:\n[\s\S]*?(?= {2}m_Shapes:)", lambda m: sub, text, count=1)
    text = re.sub(r"m_IndexBuffer: [0-9a-f]*", "m_IndexBuffer: " + tris.astype("<u2").tobytes().hex(), text, count=1)
    text = re.sub(r"m_VertexCount: \d+", f"m_VertexCount: {len(p)}", text, count=1)
    text = re.sub(r"m_DataSize: \d+", f"m_DataSize: {data.nbytes}", text, count=1)
    text = re.sub(r"_typelessdata: [0-9a-f]*", "_typelessdata: " + data.tobytes().hex(), text, count=1)
    text = re.sub(r"( {2}m_LocalAABB:\n {4}m_Center: ).*\n( {4}m_Extent: ).*", lambda m: f"{m[1]}{c}\n{m[2]}{e}", text, count=1)
    return text.replace("\n", "\r\n")


# ---------- the maps ----------
def noise(p, f, seed):
    """Value noise of points, 0..1: smooth, from a hashed lattice."""
    q = p * f + seed * 17.13
    i = np.floor(q).astype(np.int64)
    t = q - i
    t = t * t * (3 - 2 * t)
    def h(a, b, c):
        x = (i[:, 0] + a).astype(np.uint64) * np.uint64(0x9E3779B97F4A7C15) + (i[:, 1] + b).astype(np.uint64) * np.uint64(0xC2B2AE3D27D4EB4F) + (i[:, 2] + c).astype(np.uint64) * np.uint64(0x165667B19E3779F9)
        x ^= x >> np.uint64(29)
        x *= np.uint64(0xBF58476D1CE4E5B9)
        x ^= x >> np.uint64(32)
        return (x >> np.uint64(40)).astype(np.float64) / 16777215.0
    x00 = h(0, 0, 0) * (1 - t[:, 0]) + h(1, 0, 0) * t[:, 0]
    x10 = h(0, 1, 0) * (1 - t[:, 0]) + h(1, 1, 0) * t[:, 0]
    x01 = h(0, 0, 1) * (1 - t[:, 0]) + h(1, 0, 1) * t[:, 0]
    x11 = h(0, 1, 1) * (1 - t[:, 0]) + h(1, 1, 1) * t[:, 0]
    y0, y1 = x00 * (1 - t[:, 1]) + x10 * t[:, 1], x01 * (1 - t[:, 1]) + x11 * t[:, 1]
    return y0 * (1 - t[:, 2]) + y1 * t[:, 2]


def fbm(p, f, seed, octaves=4):
    total, amp, out = 0.0, 1.0, np.zeros(len(p))
    for k in range(octaves):
        out += amp * noise(p, f * 2 ** k, seed + k)
        total += amp
        amp *= 0.5
    return out / total


def blend(a, b, t):
    return a + (b - a) * np.clip(t, 0, 1)[:, None]


def textures(v):
    size = int(round(v["atlasPixels"]))
    g = (np.arange(size) + 0.5) / size
    u, w = (a.ravel() for a in np.meshgrid(g, 1 - g))
    p, nrm, unit, shape, plain = surface(u, w, v)
    # what lies inside, the same all the way round: nothing here knows where the eye is, or which
    # way the stone faces. Its rims are the shader's, where the view makes them.
    r = np.random.default_rng(int(v["seed"]) + 1)
    warped = unit + 0.22 * (np.stack([fbm(unit, 2.1, s, 3) for s in (11, 12, 13)], axis=1) - 0.5)
    body = fbm(warped, 3.0, 1)
    color = blend(np.tile(GOLD, (len(p), 1)), ORANGE, (body - 0.36) * 3.4)
    # the red clouds, scattered round the stone, broken by the noise
    cloud = np.zeros(len(p))
    for _ in range(int(round(v["cloudCount"]))):
        d = r.normal(size=3)
        c = d / np.linalg.norm(d) * 0.55
        cloud = np.maximum(cloud, 1 - np.linalg.norm(warped - c, axis=1) / 0.62)
    cloud = np.clip(cloud * 2.6 + (fbm(warped, 7.0, 5) - 0.5) * 2.2, 0, 1)
    color = blend(color, RED, cloud * 1.15)
    color = blend(color, DEEP, (cloud - 0.72) * 2.6)
    # bright veils of honey through the body, as light caught inside
    veil = np.clip((fbm(warped, 3.6, 71) - 0.5) * 6.5, 0, 1) * (1 - np.clip(cloud * 1.6, 0, 1))
    color = blend(color, HONEY, veil * 0.85)
    # green pockets
    pocket = np.clip((fbm(warped, 2.6, 21) - 0.62) * 9, 0, 1)
    color = blend(color, GREEN, pocket * 0.4)
    # fine crazing, light threads, and dark specks
    craze = np.clip(1 - np.abs(fbm(warped, 11.0, 31, 3) - 0.5) * 34, 0, 1)
    color = blend(color, HONEY, craze * 0.32)
    speck = np.clip((noise(unit, 46.0, 41) - 0.87) * 22, 0, 1) * np.clip(fbm(unit, 3.2, 42, 2) * 2.4 - 0.9, 0, 1)
    color = blend(color, DEEP * 0.55, speck * 0.8)
    out = modl.Image(size, size, (0, 0, 0, 1))
    px = out.np()
    px[:, :, :3] = color.reshape(size, size, 3)
    # the bright amber's: the same, its colors pushed, on Canopy/General
    gray = color.mean(axis=1, keepdims=True)
    out.bright = modl.Image(size, size, (0, 0, 0, 1))
    out.bright.np()[:, :, :3] = np.clip((gray + (color - gray) * 1.3) * 1.1, 0, 1).reshape(size, size, 3)
    # the layered amber's core: dark and mottled, seen through the shell
    mottle = fbm(warped, 4.2, 81)
    dark = blend(np.tile(DEEP * 0.5, (len(p), 1)), RED * 0.72, (mottle - 0.42) * 3.2)
    dark = blend(dark, ORANGE * 0.85, np.clip(1 - np.abs(fbm(warped, 6.0, 82, 3) - 0.5) * 22, 0, 1) * 0.55)
    dark = blend(dark, DEEP * 0.16, (fbm(warped, 9.0, 83) - 0.58) * 7)
    out.core = modl.Image(size, size, (0, 0, 0, 1))
    cx = out.core.np()
    cx[:, :, :3] = dark.reshape(size, size, 3)
    # the surface's own fine relief: dimples, and a little of the crazing
    e = 1.2 / (size * 0.33)
    bump = lambda q: 0.55 * fbm(q, 9.0, 51, 3) + 0.2 * fbm(q, 26.0, 52, 2) 
    h0 = bump(unit)
    grad = np.stack([bump(unit + o) - h0 for o in np.eye(3) * e], axis=1) / e
    grad -= nrm * (grad * nrm).sum(axis=1, keepdims=True)
    t, b = surface_frame(p, size)
    tipped = nrm - grad * 0.018
    tipped /= np.linalg.norm(tipped, axis=1, keepdims=True)
    tn = np.stack([(tipped * t).sum(axis=1), (tipped * b).sum(axis=1), (tipped * nrm).sum(axis=1)], axis=1)
    normal = modl.Image(size, size, (0.5, 0.5, 1, 1))
    normal.np()[:, :, :3] = (tn * 0.5 + 0.5).reshape(size, size, 3)
    return None, out, normal


def surface_frame(p, size):
    """Unit tangents along +u and +v at each texel, from the points of the texel grid (rows run
    down, so v's the other way)."""
    grid = p.reshape(size, size, 3)
    unit = lambda a: (a / (np.linalg.norm(a, axis=2, keepdims=True) + 1e-12)).reshape(-1, 3)
    return unit(np.gradient(grid, axis=1)), unit(-np.gradient(grid, axis=0))


# ---------- installing ----------
LOOKS = {  # each material's shader, values, and color map
    MATERIAL: (SHADER, {"_NormalStrength": 1, "_Brightness": 1, "_Glossiness": 0.97, "_HighlightStrength": 2, "_Depth": 0.04, "_Glow": 0.9, "_Through": 1.6, "_Reflect": 0.12, "_RimReach": 1}, -1),
    CORE_MATERIAL: (SHADER, {"_NormalStrength": 1, "_Brightness": 1, "_Glossiness": 0, "_HighlightStrength": 0, "_Depth": 0.04, "_Glow": 0.75, "_Through": 0.9, "_Reflect": 0, "_RimReach": 1}, -1),
    BRIGHT_MATERIAL: (GENERAL, {"_NormalStrength": 1, "_Brightness": 1.5, "_Glossiness": 0.97, "_HighlightStrength": 2}, -1),
    SHELL_MATERIAL: (SHELL_SHADER, {"_NormalStrength": 1, "_Brightness": 1, "_Glossiness": 0.97, "_HighlightStrength": 2, "_Body": 0.5, "_Glow": 0.9, "_Through": 1.6, "_Reflect": 0.12}, 2970),
}


def material_text(name, tex, nrm):
    shader_file, floats, queue = LOOKS[name]
    shader = shader_file if shader_file == GENERAL else modl.guid_of(shader_file)
    colors = {"_Tint": (1, 1, 1, 1)} if shader_file == GENERAL else {"_RimColor": (1, 0.77, 0.16, 1)}
    env = lambda k, g: f"    - {k}:\n        m_Texture: {{fileID: 2800000, guid: {g}, type: 3}}\n        m_Scale: {{x: 1, y: 1}}\n        m_Offset: {{x: 0, y: 0}}\n"
    return (f"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n  serializedVersion: 8\n  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {{fileID: 0}}\n  m_PrefabInstance: {{fileID: 0}}\n  m_PrefabAsset: {{fileID: 0}}\n  m_Name: {name}\n  m_Shader: {{fileID: 4800000, guid: {shader}, type: 3}}\n  m_ValidKeywords: []\n  m_InvalidKeywords: []\n  m_LightmapFlags: 4\n  m_EnableInstancingVariants: 1\n  m_DoubleSidedGI: 0\n  m_CustomRenderQueue: {queue}\n  stringTagMap: {{}}\n  disabledShaderPasses: []\n  m_SavedProperties:\n    serializedVersion: 3\n    m_TexEnvs:\n"
            + env("_MainTex", tex) + env("_NormalMap", nrm) + "    m_Ints: []\n    m_Floats:\n"
            + "".join(f"    - {k}: {x}\n" for k, x in floats.items()) + "    m_Colors:\n"
            + "".join(f"    - {k}: {{r: {c[0]}, g: {c[1]}, b: {c[2]}, a: {c[3]}}}\n" for k, c in colors.items()) + "  m_BuildTextureStacks: []\n")


def sized_meta(meta, size):
    """A texture's meta at this size, clamped: the octahedral map's edges don't meet."""
    meta = re.sub(r"(\bwrap[UVW]: )-?\d+", r"\g<1>1", meta)
    return re.sub(r"(\bmaxTextureSize: )\d+", rf"\g<1>{size}", meta)


def prefab_text(a, base, materials):
    """A prefab of a root with a LODGroup, its levels plain objects (AmberModel for layout's Tweak,
    AmberLayered to compare). materials: each level's material guids."""
    root, rt, lod = "1000000000000000001", "1000000000000000002", modl.id_of(a.name, "lodgroup")
    shell = "  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {fileID: 0}\n  m_PrefabInstance: {fileID: 0}\n  m_PrefabAsset: {fileID: 0}\n"
    kids, docs, levels = [], "", ""
    for k, mesh in enumerate(a.lods):
        go, t, f, r = (modl.id_of(a.name, k, x) for x in "gtfr")
        kids.append(t)
        levels += f"  - screenRelativeHeight: {a.heights[k]:.6f}\n    fadeTransitionWidth: 0\n    renderers:\n    - renderer: {{fileID: {r}}}\n"
        docs += f"--- !u!1 &{go}\nGameObject:\n{shell}  serializedVersion: 6\n  m_Component:\n  - component: {{fileID: {t}}}\n  - component: {{fileID: {f}}}\n  - component: {{fileID: {r}}}\n  m_Layer: 0\n  m_Name: {mesh.name}\n  m_TagString: Untagged\n  m_Icon: {{fileID: 0}}\n  m_NavMeshLayer: 0\n  m_StaticEditorFlags: 0\n  m_IsActive: 1\n"
        docs += f"--- !u!4 &{t}\nTransform:\n{shell}  m_GameObject: {{fileID: {go}}}\n  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}\n  m_LocalPosition: {{x: 0, y: 0, z: 0}}\n  m_LocalScale: {{x: 1, y: 1, z: 1}}\n  m_ConstrainProportionsScale: 0\n  m_Children: []\n  m_Father: {{fileID: {rt}}}\n  m_RootOrder: {k}\n  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}\n"
        docs += f"--- !u!33 &{f}\nMeshFilter:\n{shell}  m_GameObject: {{fileID: {go}}}\n  m_Mesh: {{fileID: 4300000, guid: {modl.guid_of(base + '/' + mesh.name + '.asset')}, type: 2}}\n"
        docs += renderer_doc(r, go, materials[k], shell)
    children = "\n".join(f"  - {{fileID: {t}}}" for t in kids)
    return (f"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!1 &{root}\nGameObject:\n{shell}  serializedVersion: 6\n  m_Component:\n  - component: {{fileID: {rt}}}\n  - component: {{fileID: {lod}}}\n  m_Layer: 0\n  m_Name: {a.name}\n  m_TagString: Untagged\n  m_Icon: {{fileID: 0}}\n  m_NavMeshLayer: 0\n  m_StaticEditorFlags: 0\n  m_IsActive: 1\n"
            f"--- !u!4 &{rt}\nTransform:\n{shell}  m_GameObject: {{fileID: {root}}}\n  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}\n  m_LocalPosition: {{x: 0, y: 0, z: 0}}\n  m_LocalScale: {{x: 1, y: 1, z: 1}}\n  m_ConstrainProportionsScale: 0\n  m_Children:\n{children}\n  m_Father: {{fileID: 0}}\n  m_RootOrder: 0\n  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}\n"
            f"--- !u!205 &{lod}\nLODGroup:\n{shell}  m_GameObject: {{fileID: {root}}}\n  serializedVersion: 2\n  m_LocalReferencePoint: {{x: 0, y: 0, z: 0}}\n  m_Size: {a.size:.6f}\n  m_FadeMode: 0\n  m_AnimateCrossFading: 0\n  m_LastLODIsBillboard: 0\n  m_LODs:\n{levels}  m_Enabled: 1\n") + docs


def renderer_doc(r, go, materials, shell):
    slots = "".join(f"  - {{fileID: 2100000, guid: {m}, type: 2}}\n" for m in materials)
    return (f"--- !u!23 &{r}\nMeshRenderer:\n{shell}  m_GameObject: {{fileID: {go}}}\n  m_Enabled: 1\n  m_CastShadows: 0\n  m_ReceiveShadows: 0\n  m_DynamicOccludee: 1\n  m_MotionVectors: 1\n  m_LightProbeUsage: 0\n  m_ReflectionProbeUsage: 0\n  m_RayTracingMode: 2\n  m_RayTraceProcedural: 0\n  m_RenderingLayerMask: 1\n  m_RendererPriority: 0\n  m_Materials:\n{slots}"
            "  m_StaticBatchInfo:\n    firstSubMesh: 0\n    subMeshCount: 0\n  m_StaticBatchRoot: {fileID: 0}\n  m_ProbeAnchor: {fileID: 0}\n  m_LightProbeVolumeOverride: {fileID: 0}\n  m_ScaleInLightmap: 1\n  m_ReceiveGI: 1\n  m_PreserveUVs: 0\n  m_IgnoreNormalsForChartDetection: 0\n  m_ImportantGI: 0\n  m_StitchLightmapSeams: 1\n  m_SelectedEditorRenderState: 3\n  m_MinimumChartSize: 4\n  m_AutoUVMaxDistance: 0.5\n  m_AutoUVMaxAngle: 89\n  m_LightmapParameters: {fileID: 0}\n  m_SortingLayerID: 0\n  m_SortingLayer: 0\n  m_SortingOrder: 0\n  m_AdditionalVertexStreams: {fileID: 0}\n")


def install_family(a, layered, size):
    base = f"Assets/Modl/{FAMILY}"
    read = lambda name: open(os.path.join(modl.HERE, name), "rb").read()
    tex, core, nrm, prefab = f"{base}/{FAMILY}_tx.png", f"{base}/{FAMILY}Core_tx.png", f"{base}/{FAMILY}_normal.png", f"{base}/{PREFAB}.prefab"
    bright = f"{base}/{FAMILY}Bright_tx.png"
    mats = {m: f"{base}/{m}.mat" for m in LOOKS}
    guid = {m: modl.guid_of(p) for m, p in mats.items()}
    native = lambda path, main: f"fileFormatVersion: 2\nguid: {modl.guid_of(path)}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: {main}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    files = {
        tex: read(FAMILY + "_tx.png"),
        tex + ".meta": sized_meta(modl.meta_with_guid(modl.canopy_file(COLOR_META + ".meta").decode(), modl.guid_of(tex)), size),
        nrm: read(FAMILY + "_normal.png"),
        nrm + ".meta": sized_meta(modl.meta_with_guid(modl.canopy_file(NORMAL_META + ".meta").decode(), modl.guid_of(nrm)), size),
        core: read(FAMILY + "Core_tx.png"),
        core + ".meta": sized_meta(modl.meta_with_guid(modl.canopy_file(COLOR_META + ".meta").decode(), modl.guid_of(core)), size),
        bright: read(FAMILY + "Bright_tx.png"),
        bright + ".meta": sized_meta(modl.meta_with_guid(modl.canopy_file(COLOR_META + ".meta").decode(), modl.guid_of(bright)), size),
        prefab: prefab_text(a, base, [[guid[MATERIAL]]] * 3),
        prefab + ".meta": f"fileFormatVersion: 2\nguid: {modl.guid_of(prefab)}\nPrefabImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    }
    for m, path in mats.items():
        files[path] = material_text(m, modl.guid_of({CORE_MATERIAL: core, BRIGHT_MATERIAL: bright}.get(m, tex)), modl.guid_of(nrm))
        files[path + ".meta"] = native(path, 2100000)
    for mesh in a.lods:
        path = f"{base}/{mesh.name}.asset"
        files[path] = asset_text(mesh)
        files[path + ".meta"] = native(path, 4300000)
    both = [guid[CORE_MATERIAL], guid[SHELL_MATERIAL]]
    second = f"{base}/{LAYERED}.prefab"
    files[second] = prefab_text(layered, base, [both, both, [guid[MATERIAL]]])
    files[second + ".meta"] = f"fileFormatVersion: 2\nguid: {modl.guid_of(second)}\nPrefabImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    third = f"{base}/{BRIGHT}.prefab"
    files[third] = prefab_text(Asset(BRIGHT, a.lods, a.size, a.heights), base, [[guid[BRIGHT_MATERIAL]]] * 3)
    files[third + ".meta"] = f"fileFormatVersion: 2\nguid: {modl.guid_of(third)}\nPrefabImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    return modl.install(FAMILY, files)


def committed(path):
    return subprocess.run(["git", "-C", modl.CANOPY, "show", "HEAD:" + path], capture_output=True, check=True).stdout.decode("latin1")


def rewired(text, mesh_guid, material_guid):
    """A prefab or scene's amber on the new mesh and material. Mesh colliders keep the old mesh, a
    simple hull."""
    text = text.replace(f"guid: {OLD_MATERIAL}, type: 2", f"guid: {material_guid}, type: 2")
    new = f"{{fileID: 4300000, guid: {mesh_guid}, type: 2}}"
    old = f"{{fileID: 4300000, guid: {OLD_MESH}, type: 3}}"
    parts = re.split(r"(?=^--- )", text, flags=re.M)
    for i, doc in enumerate(parts):
        if old in doc and (re.match(r"--- !u!33 ", doc) or re.search(r"propertyPath: m_Mesh\r?\n\s+value: ?\r?\n\s+objectReference: " + re.escape(old), doc)):
            parts[i] = doc.replace(old, new) if re.match(r"--- !u!33 ", doc) else re.sub(r"(propertyPath: m_Mesh\r?\n\s+value: ?\r?\n\s+objectReference: )" + re.escape(old), lambda m: m[1] + new, doc)
    return "".join(parts)


def with_levels(text, file, a, guids):
    """The old amber's LODGroup given the family's levels: LOD0 its renderer, the others new objects
    under it, so whatever scales it scales them."""
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    docs = re.split(r"(?=^--- )", text, flags=re.M)
    filt = next(d for d in docs if d.startswith("--- !u!33 ") and guids[0] in d)
    go = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", filt)[1]
    rend = next(d for d in docs if d.startswith("--- !u!23 ") and f"m_GameObject: {{fileID: {go}}}" in d)
    rid = re.match(r"--- !u!23 &(-?\d+)", rend)[1]
    tdoc = next(d for d in docs if re.match(r"--- !u!4 &-?\d+\n", d) and f"m_GameObject: {{fileID: {go}}}" in d)
    tid = re.match(r"--- !u!4 &(-?\d+)", tdoc)[1]
    group = next(d for d in docs if d.startswith("--- !u!205 ") and f"renderer: {{fileID: {rid}}}" in d)
    shell = "  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {fileID: 0}\n  m_PrefabInstance: {fileID: 0}\n  m_PrefabAsset: {fileID: 0}\n"
    layer = re.search(r"m_Layer: (\d+)", next(d for d in docs if re.match(rf"--- !u!1 &{go}\n", d)))[1]
    added, kids, levels = [], [], [f"  - screenRelativeHeight: {a.heights[0]:.6f}\n    fadeTransitionWidth: 0\n    renderers:\n    - renderer: {{fileID: {rid}}}\n"]
    for k in (1, 2):
        g, t, f, r = (modl.id_of(file, k, x) for x in "gtfr")
        kids.append(t)
        added.append(f"--- !u!1 &{g}\nGameObject:\n{shell}  serializedVersion: 6\n  m_Component:\n  - component: {{fileID: {t}}}\n  - component: {{fileID: {f}}}\n  - component: {{fileID: {r}}}\n  m_Layer: {layer}\n  m_Name: AmberLod{k}\n  m_TagString: Child\n  m_Icon: {{fileID: 0}}\n  m_NavMeshLayer: 0\n  m_StaticEditorFlags: 0\n  m_IsActive: 1\n")
        added.append(f"--- !u!4 &{t}\nTransform:\n{shell}  m_GameObject: {{fileID: {g}}}\n  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}\n  m_LocalPosition: {{x: 0, y: 0, z: 0}}\n  m_LocalScale: {{x: 1, y: 1, z: 1}}\n  m_ConstrainProportionsScale: 0\n  m_Children: []\n  m_Father: {{fileID: {tid}}}\n  m_RootOrder: {k - 1}\n  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}\n")
        added.append(f"--- !u!33 &{f}\nMeshFilter:\n{shell}  m_GameObject: {{fileID: {g}}}\n  m_Mesh: {{fileID: 4300000, guid: {guids[k]}, type: 2}}\n")
        added.append(re.sub(r"m_GameObject: \{fileID: -?\d+\}", f"m_GameObject: {{fileID: {g}}}", rend.replace(f"&{rid}", f"&{r}", 1)))
        levels.append(f"  - screenRelativeHeight: {a.heights[k]:.6f}\n    fadeTransitionWidth: 0\n    renderers:\n    - renderer: {{fileID: {r}}}\n")
    new_t = tdoc.replace("  m_Children: []\n", "  m_Children:\n" + "".join(f"  - {{fileID: {t}}}\n" for t in kids) + "")
    new_g = re.sub(r"  m_LODs:\n[\s\S]*?(?=  m_Enabled:)", lambda m: "  m_LODs:\n" + "".join(levels), group)
    out = "".join(new_t if d is tdoc else new_g if d is group else d for d in docs)
    out = out.rstrip("\n") + "\n" + "".join(added)
    return out.replace("\n", "\r\n") if crlf else out


def rewire(a):
    """Canopy's amber onto the family, each file from its committed text."""
    base = f"Assets/Modl/{FAMILY}"
    guids = [modl.guid_of(f"{base}/{m.name}.asset") for m in a.lods]
    material = modl.guid_of(f"{base}/{GAME_MATERIAL}.mat")
    for file in LOD_PREFABS + PLAIN_FILES:
        text = rewired(committed(file), guids[0], material)
        if file in LOD_PREFABS:
            text = with_levels(text, file, a, guids)
        with open(os.path.join(modl.CANOPY, file), "w", encoding="latin1", newline="") as f:
            f.write(text)
        print(f"rewired {file}")


def build(v, install_too=False, report=print):
    out = modl.HERE
    a = assets(v)[0]
    for mesh in a.lods:
        modl.write_obj(os.path.join(out, mesh.name + ".obj"), mesh, FAMILY + ".mtl", MATERIAL)
    report(f"{a.name}: {v['amberLength'] * 100:g} x {v['amberWidth'] * 100:g} x {v['amberThickness'] * 100:g} cm; " + ", ".join(f"LOD{k} {len(m.tris)} triangles" for k, m in enumerate(a.lods)))
    modl.write_mtl(os.path.join(out, FAMILY + ".mtl"), MATERIAL, FAMILY)
    _, color, normal = textures(v)
    modl.write_png(os.path.join(out, FAMILY + "_tx.png"), color)
    modl.write_png(os.path.join(out, FAMILY + "Core_tx.png"), color.core)
    modl.write_png(os.path.join(out, FAMILY + "Bright_tx.png"), color.bright)
    modl.write_png(os.path.join(out, FAMILY + "_normal.png"), normal)
    size = int(round(v["atlasPixels"]))
    report(f"{FAMILY}_tx.png, {FAMILY}_normal.png: {size}x{size}")
    if not install_too:
        return []
    layered = Asset(LAYERED, a.lods, a.size, a.heights)
    written = install_family(a, layered, size)
    if "--rewire" in sys.argv:
        rewire(a)
    return written


def main():
    unused = modl.unused_tags(tags(), VARS)
    if unused:
        print(f"note: tags not used yet: {', '.join(unused)}")
    written = build(values(), "--write" in sys.argv)
    if "--write" in sys.argv:
        print(f"Canopy Assets/Modl/{FAMILY}: {len(written)} files changed")


if __name__ == "__main__":
    main()
