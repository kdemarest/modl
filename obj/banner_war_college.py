"""Banner War College: the War College's banner, a navy cloth with the gold dagger hanging from a
wooden crossbar, as in the concept image wc-amphitheater.png (modl SPEC.md).

The spec is `# Modl Banner War College` in docs/models/Banner War College.md; its tweakvars hold
every number. Readings (Claude, 2026-10-27):
- The War College logo is the spec's Source image, vids/Logo Warrior.png (the dagger, green
  #226622 on blue #77bbff; no Logo War College exists): cut out by its colors, recolored gold on navy as the concept
  shows. Navy #1b2a5e, gold #d9a53a and wood #6b4a2b are set here, not yet tweakvars.
- The pivot is the middle of the crossbar. The bar runs along X; the cloth hangs below it in the
  XY plane, its top hidden in the bar (wrapped round it), its front facing +Z and its back -Z,
  each a face of its own (Canopy culls back faces) with the dagger the right way round.
- Folds are a sine across the cloth, deeper toward the bottom; the point is the cloth's last
  pointDepth narrowing straight to the middle.
- Texture: 512 x 1024; the cloth fills the left 440 px from top to bottom (the whole cloth,
  point included, stretched to it), the wood a strip on the right. The normal map raises the
  embroidered dagger slightly and gives the cloth a fine weave.
- LODs: the folds deepen linearly down the cloth, so one row of cells holds them exactly, and one
  more row makes the point: LOD0 12 x 3 cloth cells (four across each fold) and a barSides-sided
  bar and knobs, LOD1 6 x 2 and a side fewer (at least 3), LOD2 a flat cloth 2 x 2 and the same; switch heights size / (2 d) at the spec's distances (layout's lodFov 90).

  python3 obj/banner_war_college.py           writes obj/BannerWarCollege_LOD*.obj and atlases
  python3 obj/banner_war_college.py --write   also installs them into Canopy's Assets/Modl/BannerWarCollege
Layout's Tweak drives it through obj/serve.py.
"""

import math
import os
import sys

import modl

FAMILY = "BannerWarCollege"
MATERIAL = "ModlBannerWarCollege"
DOC = os.path.join(modl.DOCS, "models", "Banner War College.md")
HEADING = "Modl Banner War College"
VARS = {
    "bannerWidth": modl.Var(geometry=True, textures=True, min=0.2, max=5),
    "bannerLength": modl.Var(geometry=True, textures=True, min=0.3, max=10),
    "pointDepth": modl.Var(geometry=True, min=0, max=3),
    "foldDepth": modl.Var(geometry=True, min=0, max=0.3),
    "foldSpacing": modl.Var(geometry=True, min=0.05, max=3),
    "logoHeight": modl.Var(textures=True, min=0.1, max=10),
    "logoTop": modl.Var(textures=True, min=0, max=10),
    "barLength": modl.Var(geometry=True, min=0.2, max=6),
    "barRadius": modl.Var(geometry=True, min=0.005, max=0.3),
    "barSides": modl.Var(geometry=True, min=3, max=24),
    "lod1Distance": modl.Var(geometry=True, min=1, max=400),
    "lod2Distance": modl.Var(geometry=True, min=1, max=400),
    "cullDistance": modl.Var(geometry=True, min=1, max=1000),
}
VIDS = os.path.join(modl.DOCS, "..", "vids")
LOGO_INK, LOGO_PAPER = (0x22 / 255, 0x66 / 255, 0x22 / 255), (0x77 / 255, 0xbb / 255, 0xff / 255)
NAVY, GOLD, WOOD = (0x1b / 255, 0x2a / 255, 0x5e / 255), (0xd9 / 255, 0xa5 / 255, 0x3a / 255), (0x6b / 255, 0x4a / 255, 0x2b / 255)
SHEET = (512, 1024)
CLOTH_U = (0, 440 / 512)            # the cloth's columns
WOOD_U = (456 / 512, 504 / 512)     # the wood strip's
V_PAD = 4 / 1024
LEVELS = [(12, 3, 0, True), (6, 2, 1, True), (2, 2, 1, False)]  # cloth columns, rows, bar sides fewer than barSides, folds
COLOR_META, NORMAL_META = "Assets/Texture/StructBases_color.png", "Assets/Texture/StructBases_nmap.png"
SOURCE_MATERIAL = "Assets/Materials/StructBases.mat"


class Asset:
    def __init__(self, name, lods, size, heights):
        self.name, self.lods, self.size, self.heights = name, lods, size, heights


def logo_name():
    """The logo: the spec's one Source line naming an image in vids/."""
    images = [s for s in modl.sources(DOC, HEADING) if not s.startswith("Canopy ")]
    if len(images) != 1:
        raise ValueError(f"'# {HEADING}' needs one Source line naming the logo image, found {images}")
    return images[0]


def tags():
    modl.check_sources(DOC, HEADING, ["Canopy " + SOURCE_MATERIAL])
    logo_name()
    return modl.read_tags(DOC, HEADING, VARS)


def values(overrides=None):
    """The vars in the script's units (meters), from the doc's tags with overrides (in the tags'
    units), each held within its limits."""
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


def cloth(mesh, v, cols, rows, folds):
    """Both faces of the cloth: a grid down from the bar, narrowing to the point."""
    W, H, P = v["bannerWidth"], v["bannerLength"], min(v["pointDepth"], v["bannerLength"])
    depth = v["foldDepth"] if folds else 0.0

    def z(x, down):
        return depth * (0.35 + 0.65 * down / H) * math.sin(2 * math.pi * x / v["foldSpacing"] + 0.7)

    def normal(x, down):
        e = 1e-3
        dzdx = (z(x + e, down) - z(x - e, down)) / (2 * e)
        dzdy = -(z(x, down + e) - z(x, down - e)) / (2 * e)  # y is up, down is -y
        ln = math.sqrt(dzdx * dzdx + dzdy * dzdy + 1)
        return (-dzdx / ln, -dzdy / ln, 1 / ln)

    point_rows = max(1, round(rows * P / H)) if P > 0 else 0
    downs = [(H - P) * k / (rows - point_rows) for k in range(rows - point_rows + 1)]
    downs += [H - P + P * k / point_rows for k in range(1, point_rows + 1)]
    grid = []
    for down in downs:
        half = W / 2 * (min(1.0, (H - down) / P) if P > 0 else 1.0)
        grid.append([(-half + 2 * half * c / cols, down) for c in range(cols + 1)])
    for side in (1, -1):
        ids = []
        for row in grid:
            r = []
            for x, down in row:
                n = normal(x, down)
                u = (x + W / 2) / W
                if side < 0:
                    u = 1 - u  # the back reads the right way round
                uv = (CLOTH_U[0] + u * (CLOTH_U[1] - CLOTH_U[0]), 1 - V_PAD - down / H * (1 - 2 * V_PAD))
                r.append(mesh.vertex((x, -down, z(x, down)), tuple(side * c for c in n), uv))
            ids.append(r)
        for k in range(len(grid) - 1):
            for c in range(cols):
                quad = [ids[k][c], ids[k][c + 1], ids[k + 1][c + 1], ids[k + 1][c]]
                for tri in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
                    a, b, cc = (mesh.verts[i][0] for i in tri)
                    e1 = [b[i] - a[i] for i in range(3)]
                    e2 = [cc[i] - a[i] for i in range(3)]
                    fn = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
                    if math.sqrt(sum(x * x for x in fn)) < 1e-9:
                        continue  # the point's collapsed cells
                    mesh.tris.append(tri if fn[2] * side >= 0 else (tri[0], tri[2], tri[1]))


def rod(mesh, x0, x1, radius, sides):
    """A cylinder along X from x0 to x1 with flat caps, in the wood strip."""
    L = abs(x1 - x0) or 1
    ring = lambda x, k: (x, radius * math.cos(2 * math.pi * k / sides), radius * math.sin(2 * math.pi * k / sides))
    for k in range(sides):
        a0, a1 = 2 * math.pi * k / sides, 2 * math.pi * (k + 1) / sides
        n0, n1 = (0, math.cos(a0), math.sin(a0)), (0, math.cos(a1), math.sin(a1))
        u0 = WOOD_U[0] + (WOOD_U[1] - WOOD_U[0]) * k / sides
        u1 = WOOD_U[0] + (WOOD_U[1] - WOOD_U[0]) * (k + 1) / sides
        v0, v1 = 0.1, 0.1 + 0.8 * min(1.0, L / 2)
        ids = [mesh.vertex(ring(x0, k), n0, (u0, v0)), mesh.vertex(ring(x1, k), n0, (u0, v1)),
               mesh.vertex(ring(x1, k + 1), n1, (u1, v1)), mesh.vertex(ring(x0, k + 1), n1, (u1, v0))]
        mesh.face_ids(ids, ((n0[0] + n1[0]) / 2, (n0[1] + n1[1]) / 2, (n0[2] + n1[2]) / 2))
    mid = ((WOOD_U[0] + WOOD_U[1]) / 2, 0.95)
    for x, nx in ((x0, -1.0 if x0 < x1 else 1.0), (x1, 1.0 if x0 < x1 else -1.0)):
        mesh.face([(ring(x, k), mid) for k in range(sides)], (nx, 0.0, 0.0))


def assets(v):
    out = []
    lods = []
    L, r = v["barLength"], v["barRadius"]
    for k, (cols, rows, fewer, folds) in enumerate(LEVELS):
        sides = max(3, int(round(v["barSides"])) - fewer)
        mesh = modl.Mesh(f"{FAMILY}_LOD{k}")
        cloth(mesh, v, cols, rows, folds)
        rod(mesh, -L / 2, L / 2, r, sides)
        for end in (-1, 1):  # the knobs
            rod(mesh, end * L / 2, end * (L / 2 + 2.2 * r), 1.7 * r, sides)
        mesh.segments = cols
        lods.append(mesh)
    d1 = v["lod1Distance"]
    d2 = max(v["lod2Distance"], d1 * 1.01)
    cull = max(v["cullDistance"], d2 * 1.01)
    size = max(L + 4.4 * r, v["bannerLength"])
    out.append(Asset(FAMILY, lods, size, [size / (2 * d) for d in (d1, d2, cull)]))
    return out


_logo = {}  # the logo image and its dagger's box, read once per run or worker


def logo():
    if not _logo:
        img = modl.read_png(open(os.path.join(VIDS, logo_name()), "rb").read())
        ink = lambda c: ink_of(c)
        xs, ys = [], []
        for y in range(0, img.h, 4):
            for x in range(0, img.w, 4):
                if ink(img.sample(x + 0.5, y + 0.5)) > 0.5:
                    xs.append(x)
                    ys.append(y)
        _logo.update(img=img, box=(min(xs) - 4, min(ys) - 4, max(xs) + 8, max(ys) + 8))
    return _logo


def ink_of(c):
    """How much of the logo's ink (vs its paper) a color is, 0 to 1."""
    di = sum((c[k] - LOGO_INK[k]) ** 2 for k in range(3))
    dp = sum((c[k] - LOGO_PAPER[k]) ** 2 for k in range(3))
    return dp / (di + dp) if di + dp else 0.0


def textures(v):
    W, H = v["bannerWidth"], v["bannerLength"]
    w, h = SHEET
    color, normal = modl.Image(w, h, (0, 0, 0, 1)), modl.Image(w, h, (0.5, 0.5, 1, 1))
    lg = logo()
    x0, y0, x1, y1 = lg["box"]
    lh = v["logoHeight"]
    lw = lh * (x1 - x0) / (y1 - y0)
    cols = round(CLOTH_U[1] * w)
    # the dagger's ink per cloth pixel (0 outside it)
    ink = [[0.0] * cols for _ in range(h)]
    for j in range(h):
        down = ((j + 0.5) / h - V_PAD) / (1 - 2 * V_PAD) * H
        ly = (down - v["logoTop"]) / lh
        if not 0 <= ly <= 1:
            continue
        for i in range(cols):
            x = (i + 0.5) / cols * W - W / 2
            lx = (x + lw / 2) / lw
            if 0 <= lx <= 1:
                ink[j][i] = ink_of(lg["img"].sample(x0 + lx * (x1 - x0), y0 + ly * (y1 - y0)))
    seed = lambda i, j: ((i * 73856093) ^ (j * 19349663)) % 1000 / 1000.0
    for j in range(h):
        for i in range(w):
            k = (j * w + i) * 4
            if i < cols:
                m = ink[j][i]
                weave = 0.96 + 0.08 * seed(i, j) + 0.03 * math.sin(i * 1.7) * math.sin(j * 1.7)
                c = [(NAVY[q] * (1 - m) + GOLD[q] * m) * weave for q in range(3)]
                # the embroidery stands a little proud: its edges tilt outward
                dx = (ink[j][min(i + 1, cols - 1)] - ink[j][max(i - 1, 0)]) * 1.5
                dy = (ink[max(j - 1, 0)][i] - ink[min(j + 1, h - 1)][i]) * 1.5  # v is up
                wx, wy = 0.06 * math.sin(i * 2.1), 0.06 * math.sin(j * 2.1)
                nx, ny = -dx + wx, -dy + wy
            else:
                grain = 0.8 + 0.2 * math.sin(i * 0.9 + 6 * math.sin(j * 0.013)) + 0.05 * seed(i, j)
                c = [WOOD[q] * grain for q in range(3)]
                nx, ny = 0.15 * math.cos(i * 0.9 + 6 * math.sin(j * 0.013)), 0.0
            ln = math.sqrt(nx * nx + ny * ny + 1)
            color.px[k:k + 3] = modl.array("f", c)
            normal.px[k:k + 3] = modl.array("f", [nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, 1 / ln * 0.5 + 0.5])
    sheet = modl.TrimSheet(w, h, cols / W)
    return sheet, color, normal


def build(v, install_too=False, report=print):
    out = modl.HERE
    a = assets(v)[0]
    for mesh in a.lods:
        modl.write_obj(os.path.join(out, mesh.name + ".obj"), mesh, FAMILY + ".mtl", MATERIAL)
    report(f"{a.name}: cloth {v['bannerWidth']:g} x {v['bannerLength']:g} m, bar {v['barLength']:g} m; " + ", ".join(f"LOD{k} {len(m.tris)} triangles" for k, m in enumerate(a.lods)) + "; screen heights " + ", ".join(f"{x:.3f}" for x in a.heights))
    modl.write_mtl(os.path.join(out, FAMILY + ".mtl"), MATERIAL, FAMILY)
    _, color, normal = textures(v)
    modl.write_png(os.path.join(out, FAMILY + "_tx.png"), color)
    modl.write_png(os.path.join(out, FAMILY + "_normal.png"), normal)
    report(f"{FAMILY}_tx.png, {FAMILY}_normal.png: {SHEET[0]}x{SHEET[1]}")
    if not install_too:
        return []
    material = lambda tex, nrm: modl.material_yaml(modl.canopy_file(SOURCE_MATERIAL).decode(), MATERIAL, tex, nrm)
    return modl.install_assets(FAMILY, MATERIAL, [a], material, COLOR_META, NORMAL_META)


def main():
    unused = modl.unused_tags(tags(), VARS)
    if unused:
        print(f"note: tags not used yet: {', '.join(unused)}")
    written = build(values(), "--write" in sys.argv)
    if "--write" in sys.argv:
        print(f"Canopy Assets/Modl/{FAMILY}: {len(written)} files changed")


if __name__ == "__main__":
    main()
