"""Preview: draws a model's OBJ, textured with its family's atlas, to a PNG, so a model can be
checked without Unity or layout (Claude, 2026-11-02). Unity's axes (the OBJ's X negated back),
seen from yaw degrees round +Y (0 looks along -Z at its front) and pitch degrees down, framed to
fit; depth-tested, lit by its normals (a sun over the viewer's left shoulder plus ambient, as
Lambert, both sides alike), smooth between, bent by its family's normal map (<family>_normal.png,
tangent space: +x along u, +y along v, each triangle's tangents from its uvs) unless --flat.

  python3 obj/preview.py <Name>_LOD0.obj [--yaw 30] [--pitch 20] [--size 400] [--flat] [--out file.png]
"""

import math
import os
import sys

import modl


def read_obj(path):
    """Positions and normals (Unity's axes), uvs, and triangles as (position, uv, normal) index
    corners."""
    vs, vts, vns, tris = [], [], [], []
    for line in open(path):
        t = line.split()
        if not t:
            continue
        if t[0] == "v":
            vs.append((-float(t[1]), float(t[2]), float(t[3])))
        elif t[0] == "vt":
            vts.append((float(t[1]), float(t[2])))
        elif t[0] == "vn":
            vns.append((-float(t[1]), float(t[2]), float(t[3])))
        elif t[0] == "f":
            corners = []
            for k in t[1:]:
                parts = k.split("/")
                corners.append((int(parts[0]) - 1, int(parts[1]) - 1 if len(parts) > 1 and parts[1] else None,
                                int(parts[2]) - 1 if len(parts) > 2 and parts[2] else None))
            for i in range(1, len(corners) - 1):
                tris.append((corners[0], corners[i], corners[i + 1]))
    return vs, vts, vns, tris


def render(obj, atlas, yaw=30.0, pitch=20.0, size=400, normals=None):
    vs, vts, vns, tris = read_obj(obj)
    read = lambda path: modl.read_png(open(path, "rb").read()) if path and os.path.exists(path) else None
    tex, bumps = read(atlas), read(normals)
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(p):
        # turn by yaw about +Y, then tilt by pitch; the camera looks along -Z of the result
        x, y, z = p[0] * cy - p[2] * sy, p[1], p[0] * sy + p[2] * cy
        return x, y * cp - z * sp, y * sp + z * cp
    pts = [view(p) for p in vs]
    lo = [min(p[q] for p in pts) for q in range(3)]
    hi = [max(p[q] for p in pts) for q in range(3)]
    span = max(hi[0] - lo[0], hi[1] - lo[1]) or 1
    k = size * 0.9 / span
    screen = [((p[0] - (lo[0] + hi[0]) / 2) * k + size / 2, size / 2 - (p[1] - (lo[1] + hi[1]) / 2) * k, p[2]) for p in pts]
    img = modl.Image(size, size, (1.0, 1.0, 1.0, 1.0))
    depth = [-1e9] * (size * size)
    sun = [-0.4, 0.6, 0.7]
    ln = math.sqrt(sum(c * c for c in sun))
    sun = [c / ln for c in sun]
    for tri in tris:
        a, b, c = (screen[i] for i, _, _ in tri)
        # each corner's normal (smooth, as Unity shades), in view space
        ns = [view(vns[nk]) if nk is not None else None for _, _, nk in tri]
        uv = [vts[j] if j is not None and vts else (0.5, 0.5) for _, j, _ in tri]
        frame = tangents([view(vs[i]) for i, _, _ in tri], uv) if bumps and None not in ns else None
        area = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(area) < 1e-9:
            continue
        x0, x1 = max(0, int(min(a[0], b[0], c[0]))), min(size - 1, int(max(a[0], b[0], c[0])) + 1)
        y0, y1 = max(0, int(min(a[1], b[1], c[1]))), min(size - 1, int(max(a[1], b[1], c[1])) + 1)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px, py = x + 0.5, y + 0.5
                w0 = ((b[0] - px) * (c[1] - py) - (c[0] - px) * (b[1] - py)) / area
                w1 = ((c[0] - px) * (a[1] - py) - (a[0] - px) * (c[1] - py)) / area
                w2 = 1 - w0 - w1
                if w0 < 0 or w1 < 0 or w2 < 0:
                    continue
                z = w0 * a[2] + w1 * b[2] + w2 * c[2]
                if z <= depth[y * size + x]:
                    continue
                depth[y * size + x] = z
                if tex:
                    u = w0 * uv[0][0] + w1 * uv[1][0] + w2 * uv[2][0]
                    v = w0 * uv[0][1] + w1 * uv[1][1] + w2 * uv[2][1]
                    col = tex.sample(u * tex.w, (1 - v) * tex.h)[:3]
                else:
                    col = (0.8, 0.8, 0.8)
                n = [w0 * ns[0][q] + w1 * ns[1][q] + w2 * ns[2][q] for q in range(3)] if None not in ns else None
                if n and frame:
                    t = bumps.sample(u * bumps.w, (1 - v) * bumps.h)
                    m = [t[q] * 2 - 1 for q in range(3)]
                    n = [frame[0][q] * m[0] + frame[1][q] * m[1] + n[q] * m[2] for q in range(3)]
                light = 0.35 + 0.75 * abs(sum(n[q] * sun[q] for q in range(3))) / math.sqrt(sum(c * c for c in n) or 1) if n else 1.0
                img.set(x, y, tuple(min(1.0, col[q] * light) for q in range(3)) + (1.0,))
    return img


def tangents(ps, uv):
    """A triangle's directions of +u and +v (unit), from its corners' points and uvs."""
    e1, e2 = [[p[q] - ps[0][q] for q in range(3)] for p in ps[1:]]
    (du1, dv1), (du2, dv2) = [(t[0] - uv[0][0], t[1] - uv[0][1]) for t in uv[1:]]
    det = du1 * dv2 - du2 * dv1
    if abs(det) < 1e-12:
        return None
    unit = lambda a: [c / (math.sqrt(sum(x * x for x in a)) or 1) for c in a]
    return unit([(e1[q] * dv2 - e2[q] * dv1) / det for q in range(3)]), unit([(e2[q] * du1 - e1[q] * du2) / det for q in range(3)])


def main():
    args = sys.argv[1:]
    obj = args[0]
    opt = lambda name, d: type(d)(args[args.index(name) + 1]) if name in args else d
    family = open(obj).read().split("mtllib ", 1)[1].split()[0].rsplit(".", 1)[0] if "mtllib " in open(obj).read() else None
    atlas = os.path.join(os.path.dirname(obj) or ".", family + "_tx.png") if family else None
    out = opt("--out", os.path.splitext(obj)[0] + "_preview.png")
    normals = None if "--flat" in args or not atlas else atlas.replace("_tx.png", "_normal.png")
    modl.write_png(out, render(obj, atlas, opt("--yaw", 30.0), opt("--pitch", 20.0), opt("--size", 400), normals))
    print(out)


if __name__ == "__main__":
    main()
