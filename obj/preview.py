"""Preview: draws a model's OBJ, textured with its family's atlas, to a PNG, so a model can be
checked without Unity or layout (Claude, 2026-11-02). Unity's axes (the OBJ's X negated back),
seen from yaw degrees round +Y (0 looks along -Z at its front) and pitch degrees down, framed to
fit; depth-tested, each corner lit by its normal (a sun over the viewer's left shoulder plus
ambient, as Lambert, both sides alike), smooth between; the normal map is left out.

  python3 obj/preview.py <Name>_LOD0.obj [--yaw 30] [--pitch 20] [--size 400] [--out file.png]
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


def render(obj, atlas, yaw=30.0, pitch=20.0, size=400):
    vs, vts, vns, tris = read_obj(obj)
    tex = modl.read_png(open(atlas, "rb").read()) if atlas and os.path.exists(atlas) else None
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
        # each corner lit by its own normal (smooth, as Unity shades), both sides alike
        lights = [0.35 + 0.75 * abs(sum(view(vns[nk])[q] * sun[q] for q in range(3))) if nk is not None else 1.0 for _, _, nk in tri]
        uv = [vts[j] if j is not None and vts else (0.5, 0.5) for _, j, _ in tri]
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
                light = w0 * lights[0] + w1 * lights[1] + w2 * lights[2]
                img.set(x, y, tuple(min(1.0, col[q] * light) for q in range(3)) + (1.0,))
    return img


def main():
    args = sys.argv[1:]
    obj = args[0]
    opt = lambda name, d: type(d)(args[args.index(name) + 1]) if name in args else d
    family = open(obj).read().split("mtllib ", 1)[1].split()[0].rsplit(".", 1)[0] if "mtllib " in open(obj).read() else None
    atlas = os.path.join(os.path.dirname(obj) or ".", family + "_tx.png") if family else None
    out = opt("--out", os.path.splitext(obj)[0] + "_preview.png")
    modl.write_png(out, render(obj, atlas, opt("--yaw", 30.0), opt("--pitch", 20.0), opt("--size", 400)))
    print(out)


if __name__ == "__main__":
    main()
