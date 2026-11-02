"""Curved Bench: the War College amphitheater's benches, one per row (modl SPEC.md).

The spec is `# Modl Curved Bench` in docs/models/Curved Benches.md; its tweakvars ({name value
unit} tags) hold every number, read on each run. Readings (Claude, 2026-10-26):
- discDiameter is the central disc's diameter. Row k (1 to extraRows + 1) runs from
  discDiameter / 2 + firstRowGap + (k - 1) * (benchDepth + rowGap) out to benchDepth beyond.
- The pivot is the middle of the bench: half way along the arc, across the seat and up its
  thickness. The ring's center is 0, 0, -radius from it (radius: the row's middle), so a bench
  placed at 0, height, radius under a center object, unrotated, sits in its row, its concave
  side toward the center; turning the parent by benchArc puts the next bench end to end.
- The struct disc is StructPlatformRoundThinLods (material StructBases, its color atlas a baked,
  carved one): its stone is copied from plain islands of StructBases_color and _nmap at
  stoneDensity (the disc's own is 164 px/m at scale 1), and StructBases' detail texture is tiled
  to the same density. The trim sheet is 1024 px wide (a 1024 / stoneDensity m tile along the
  arc) and as tall as its bands need, in powers of two.
- Slots: rounded grooves, darkened a little in the middle. Bevels: rounded, on every edge.
- The central disc is an asset of the family too, AmphitheaterDisc: the struct disc's own meshes
  (StructPlatformRoundThinLods, material StructBases, its carved top kept) rescaled to
  discDiameter across and discThickness tall, its pivot the middle of its bottom (an
  assemblage's Origin). Its LODs are three of the struct disc's six (Lod0, Lod2, Lod4), at the
  family's distances, so its levels line up with the benches'.
- LODs: separate models, CurvedBenchRow<r>_LOD<k>, under the prefab's LODGroup. A pixel is
  90 degrees over 1900 px (the Quest 2; layout's lodFov 90), so an error of lodError pixels at
  distance d is d * PIXEL * lodError meters; each level's segment count is the least within its
  error, made a multiple of the next level's (nested). The LODGroup's size is the bench's
  largest extent; a level's lowest screen height is size / (2 d tan(45 degrees)) at the next
  level's distance (the last at cullDistance), as Unity's LODGroup and layout measure it.

  python3 obj/curved_bench.py           writes obj/CurvedBenchRow*.obj, CurvedBench.mtl and the
                                        CurvedBench atlases
  python3 obj/curved_bench.py --write   also installs them into Canopy's Assets/Modl/CurvedBench
Layout's Tweak drives it through obj/serve.py.
"""

import hashlib
import math
import os
import sys

import modl

FAMILY = "CurvedBench"
MATERIAL = "ModlCurvedBench"
DOC = os.path.join(modl.DOCS, "models", "Curved Benches.md")
HEADING = "Modl Curved Bench"
VARS = {
    "benchArc": modl.Var(geometry=True, min=5, max=180),
    "benchDepth": modl.Var(geometry=True, textures=True, min=0.3, max=3),
    "benchThickness": modl.Var(geometry=True, textures=True, min=0.05, max=0.6),
    "discDiameter": modl.Var(geometry=True, min=0.5, max=20),
    "discThickness": modl.Var(geometry=True, min=0.02, max=2),
    "firstRowGap": modl.Var(geometry=True, min=0, max=10),
    "rowGap": modl.Var(geometry=True, min=0, max=10),
    "extraRows": modl.Var(rebuild=True, min=0, max=12),
    "slotInset": modl.Var(textures=True, min=0, max=1.5),
    "slotWidth": modl.Var(textures=True, min=0.005, max=0.5),
    "slotDepth": modl.Var(textures=True, min=0, max=0.05),
    "bevelWidth": modl.Var(textures=True, min=0, max=0.1),
    "stoneDensity": modl.Var(rebuild=True, min=32, max=512),
    "lod0Error": modl.Var(geometry=True, min=0.0005, max=0.1),
    "lodError": modl.Var(geometry=True, min=0.1, max=20),
    "lod1Distance": modl.Var(geometry=True, min=1, max=400),
    "lod2Distance": modl.Var(geometry=True, min=1, max=400),
    "cullDistance": modl.Var(geometry=True, min=1, max=1000),
}
PIXEL = math.radians(90) / 1900
SHEET_WIDTH = 1024
# The struct disc's stone (StructBases, 2048 px): its own density, plain islands of stone (well
# inside their edges), and its material's detail tiling per meter (6 over 0.0805 UV a meter).
SOURCE_COLOR = "Assets/Texture/StructBases_color.png"
SOURCE_NORMAL = "Assets/Texture/StructBases_nmap.png"
SOURCE_MATERIAL = "Assets/Materials/StructBases.mat"
SOURCE_DENSITY = 164.0
SOURCE_RECTS = [(808, 38, 962, 452), (1358, 658, 1507, 1042), (878, 1348, 992, 1772)]
DETAIL_PER_METER = 6 * 0.0805
# The struct disc: its LOD meshes (level k is _Lod<k>), the three the disc keeps, its material.
DISC_MESH = "Assets/Meshes/StructPlatformRoundThinLodMeshes/StructPlatformRoundThinLod_Lod{}.asset"
DISC_LEVELS = (0, 2, 4)
DISC_MATERIAL = "757bc6a0a4989ba47a06ee643f5509c7"  # Assets/Materials/StructBases.mat


def tags():
    used = [SOURCE_COLOR, SOURCE_NORMAL, SOURCE_MATERIAL] + [DISC_MESH.format(level) for level in DISC_LEVELS]
    modl.check_sources(DOC, HEADING, ["Canopy " + u for u in used])
    return modl.read_tags(DOC, HEADING, VARS)


def values(overrides=None):
    """The vars in the script's units (meters, degrees, px/m, px, counts), from the doc's tags,
    with overrides {name: value in the tag's unit}, each held within its limits (VARS, in the
    script's units)."""
    t = tags()
    out = {}
    for name, var in VARS.items():
        value, unit = t[name]
        if overrides and name in overrides:
            value = float(overrides[name])
        value *= modl.UNITS[unit]
        # limits are in the script's units
        if var.min is not None:
            value = max(var.min, value)
        if var.max is not None:
            value = min(var.max, value)
        out[name] = value
    return out


def sheet_for(v):
    """The trim sheet and its bands: the seat, the bottom (each benchDepth across) and the sides
    (benchThickness), the sheet as tall as they need."""
    density = v["stoneDensity"]
    need = 8 + 2 * (round(v["benchDepth"] * density) + 8) + round(v["benchThickness"] * density) + 8
    h = 512
    while h < need:
        h *= 2
    sheet = modl.TrimSheet(SHEET_WIDTH, h, density)
    return sheet, sheet.band("top", v["benchDepth"]), sheet.band("side", v["benchThickness"]), sheet.band("bottom", v["benchDepth"])


class Bench:
    """One row's bench: its prefab name, its LOD meshes (most detailed first), its inner radius,
    and its LODGroup's size and lowest screen height per level."""

    def __init__(self, name, inner, lods, size, heights, anchor=None, material=None):
        self.name, self.inner, self.lods, self.size, self.heights = name, inner, lods, size, heights
        self.material = material  # a material guid of its own (else the family's)
        # where the pivot sits on its ring: `ring` m out from the ring's center, along the
        # bench's +Z (layout keeps an anchored piece at its angle around a scene's Origin)
        self.anchor = anchor


def benches(v):
    sheet, top, side, bottom = sheet_for(v)
    out = []
    depth, w, h, arc = v["benchDepth"], v["benchDepth"] / 2, v["benchThickness"] / 2, v["benchArc"]
    # each level's distances, kept increasing
    d1 = v["lod1Distance"]
    d2 = max(v["lod2Distance"], d1 * 1.01)
    cull = max(v["cullDistance"], d2 * 1.01)
    errors = [v["lod0Error"], d1 * PIXEL * v["lodError"], d2 * PIXEL * v["lodError"]]
    for row in range(1, int(round(v["extraRows"])) + 2):
        inner = v["discDiameter"] / 2 + v["firstRowGap"] + (row - 1) * (depth + v["rowGap"])
        outer = inner + depth
        edges = [
            modl.Edge((-w, -h), (w, -h), bottom),   # bottom, v from the inner edge
            modl.Edge((w, -h), (w, h), side),       # outer side, v up
            modl.Edge((-w, h), (w, h), top),        # seat, v from the inner edge
            modl.Edge((-w, -h), (-w, h), side),     # inner side, v up
        ]
        counts = modl.nested_segments(arc, outer, errors)
        lods = [modl.revolve(f"{FAMILY}Row{row}_LOD{k}", edges, inner + w, arc, cap_band=side, segments=n) for k, n in enumerate(counts)]
        half = math.radians(min(arc, 180)) / 2
        size = max(2 * outer * math.sin(half), outer - inner * math.cos(half), 2 * h)
        out.append(Bench(f"{FAMILY}Row{row}", inner, lods, size, [size / (2 * d) for d in (d1, d2, cull)], {"ring": inner + w}))
    return out


_disc = {}  # the struct disc's meshes, read once per run or worker


def disc(v):
    """The central disc: the struct disc's meshes rescaled (Unity's axes to OBJ's: X negated,
    winding reversed), its pivot the middle of its bottom."""
    if not _disc:
        for level in DISC_LEVELS:
            _disc[level] = modl.read_unity_mesh(modl.canopy_file(DISC_MESH.format(level)).decode())
    ref = _disc[DISC_LEVELS[0]]["positions"]
    across = max(p[0] for p in ref) - min(p[0] for p in ref)
    bottom = min(p[1] for p in ref)
    tall = max(p[1] for p in ref) - bottom
    sxz, sy = v["discDiameter"] / across, v["discThickness"] / tall
    lods = []
    for k, level in enumerate(DISC_LEVELS):
        src = _disc[level]
        mesh = modl.Mesh(f"AmphitheaterDisc_LOD{k}")
        ids = []
        for p, n, uv in zip(src["positions"], src["normals"], src["uvs"]):
            nn = (-n[0] / sxz, n[1] / sy, n[2] / sxz)
            ln = math.sqrt(sum(x * x for x in nn)) or 1
            ids.append(mesh.vertex((-p[0] * sxz, (p[1] - bottom) * sy, p[2] * sxz), tuple(x / ln for x in nn), tuple(uv)))
        t = src["triangles"]
        mesh.tris = [(ids[t[i]], ids[t[i + 2]], ids[t[i + 1]]) for i in range(0, len(t), 3)]
        mesh.segments = len(mesh.tris)
        lods.append(mesh)
    d1 = v["lod1Distance"]
    d2 = max(v["lod2Distance"], d1 * 1.01)
    cull = max(v["cullDistance"], d2 * 1.01)
    size = max(v["discDiameter"], v["discThickness"])
    return Bench("AmphitheaterDisc", 0, lods, size, [size / (2 * d) for d in (d1, d2, cull)], material=DISC_MATERIAL)


def assets(v):
    """What serve.py asks a family for: the benches and the disc."""
    return benches(v) + [disc(v)]


def stone(density, h):
    """StructBases' stone at this density, SHEET_WIDTH wide and at least h tall: synthesized once
    per density, 1024 px tall or more, and cached in obj/.cache."""
    rows = max(1024, h)
    if (density, rows) in _stone:
        return _stone[density, rows]
    key = hashlib.md5(repr((SHEET_WIDTH, rows, density, SOURCE_DENSITY, SOURCE_RECTS, SOURCE_COLOR, SOURCE_NORMAL)).encode()).hexdigest()[:12]
    cached = modl.load_cache(f"{FAMILY}_stone_{key}.bin", 2)
    if cached:
        _stone[density, rows] = cached
        return cached
    print(f"synthesizing the stone at {density:g} px/m (once; cached in obj/.cache; a minute or two)...", file=sys.stderr)
    src_c = modl.read_png(modl.canopy_file(SOURCE_COLOR))
    src_n = modl.read_png(modl.canopy_file(SOURCE_NORMAL))
    out = modl.synthesize(src_c, src_n, SOURCE_RECTS, SHEET_WIDTH, rows, SOURCE_DENSITY / density)
    modl.save_cache(f"{FAMILY}_stone_{key}.bin", out)
    _stone[density, rows] = out
    return out


_stone = {}  # kept in memory while a tweak worker runs


def textures(v):
    sheet, top, side, bottom = sheet_for(v)
    color, normal = stone(v["stoneDensity"], sheet.h)
    # the sheet's rows of the (taller) stone
    keep = sheet.w * sheet.h * 4
    c, n = modl.Image(sheet.w, sheet.h), modl.Image(sheet.w, sheet.h)
    c.px, n.px = color.px[:keep], normal.px[:keep]
    depth, width, inset = v["benchDepth"], v["slotWidth"], v["slotInset"]
    seat = modl.profile_of(
        modl.slot(inset, width, v["slotDepth"]),
        modl.slot(depth - inset - width, width, v["slotDepth"]),
        modl.bevel(v["bevelWidth"], depth))
    modl.apply_profile(c, n, top, seat)
    modl.apply_profile(c, n, bottom, modl.profile_of(modl.bevel(v["bevelWidth"], depth)))
    modl.apply_profile(c, n, side, modl.profile_of(modl.bevel(v["bevelWidth"], v["benchThickness"])))
    return sheet, c, n


def build(v, install_too=False, report=print):
    """Writes the family into obj/ (and with install_too into Canopy). Returns Canopy's changed
    files."""
    out = modl.HERE
    bs = assets(v)
    for b in bs:
        for mesh in b.lods:
            modl.write_obj(os.path.join(out, mesh.name + ".obj"), mesh, FAMILY + ".mtl", MATERIAL)
        heights = f"screen heights {', '.join(f'{x:.3f}' for x in b.heights)}"
        if b.material:
            report(f"{b.name}: {v['discDiameter']:g} m across, {v['discThickness']:g} m thick; " + ", ".join(f"LOD{k} {len(m.tris)} triangles" for k, m in enumerate(b.lods)) + f"; {heights}")
            continue
        arc = math.radians(v["benchArc"]) * (b.inner + v["benchDepth"] / 2)
        levels = ", ".join(f"LOD{k} {m.segments} segments {len(m.tris)} triangles" for k, m in enumerate(b.lods))
        report(f"{b.name}: radius {b.inner:.2f} to {b.inner + v['benchDepth']:.2f} m, arc {arc:.2f} m; {levels}; {heights}")
    modl.write_mtl(os.path.join(out, FAMILY + ".mtl"), MATERIAL, FAMILY)
    sheet, color, normal = textures(v)
    modl.write_png(os.path.join(out, FAMILY + "_tx.png"), color)
    modl.write_png(os.path.join(out, FAMILY + "_normal.png"), normal)
    report(f"{FAMILY}_tx.png, {FAMILY}_normal.png: {sheet.w}x{sheet.h} at {sheet.density:g} px/m, a {sheet.tile_meters():.2f} m tile along the arc")
    for name in os.listdir(out):
        # models of rows or levels no longer made
        if (name.startswith(FAMILY + "Row") or name.startswith("AmphitheaterDisc")) and name.endswith(".obj") and name[:-4] not in {m.name for b in bs for m in b.lods}:
            os.remove(os.path.join(out, name))
    return install(bs, sheet) if install_too else []


def install(bs, sheet):
    u_per_m, v_per_m = sheet.density / sheet.w, sheet.density / sheet.h
    detail = (DETAIL_PER_METER / u_per_m, DETAIL_PER_METER / v_per_m)
    material = lambda tex, nrm: modl.material_yaml(modl.canopy_file(SOURCE_MATERIAL).decode(), MATERIAL, tex, nrm, detail)
    return modl.install_assets(FAMILY, MATERIAL, bs, material, SOURCE_COLOR, SOURCE_NORMAL)


def main():
    unused = modl.unused_tags(tags(), VARS)
    if unused:
        print(f"note: tags not used yet: {', '.join(unused)}")
    written = build(values(), "--write" in sys.argv)
    if "--write" in sys.argv:
        print(f"Canopy Assets/Modl/{FAMILY}: {len(written)} files changed" + (": " + ", ".join(p.split('/')[-1] for p in written) if written else ""))


if __name__ == "__main__":
    main()
