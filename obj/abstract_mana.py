"""Abstract Mana: the tall octahedron that stands for mana when it is used, after vids/Mana.png
(modl SPEC.md).

The spec is `# Modl Abstract Mana` in docs/models/Abstract Mana.md; its tweakvars hold the size.
Readings (Claude, 2026-11-09):
- A four-sided bipyramid: points at the top and bottom, four corners round its equator, half way
  up. Its base point is the origin, as the Mana shader (modl/shaders/Mana.surf) measures its stripe
  up the mesh's own Y: base at 0, equator at half the height.
- Flat faces, each its own normal (the sample's edges are sharp). Eight triangles: one level, no
  LOD group.
- No texture: the look (mottling, glow, stripe) is the shader's, material ModlMana, which
  modl/tools/shaders.js writes from the .surf. The UVs are a plain projection, unused.
- Its prefab is AbstractMana, the docs asset's name, under Assets/Modl/AbstractMana; it replaces
  layout's placeholder of the same name (Assets/Placeholder/AbstractMana).

  python3 obj/abstract_mana.py           writes obj/AbstractMana.obj and AbstractMana.mtl
  python3 obj/abstract_mana.py --write   also installs it into Canopy's Assets/Modl/AbstractMana
"""

import os
import sys

import modl

FAMILY = "AbstractMana"
MATERIAL = "ModlMana"
MATERIAL_PATH = "Assets/Shaders/Modl/ModlMana.mat"  # modl/tools/shaders.js's, from Mana.surf
OBJ_META = "Assets/Meshes/Drill/mesh_Cone_5sided.obj.meta"  # an OBJ's import settings, as install_assets takes them
DOC = os.path.join(modl.DOCS, "models", "Abstract Mana.md")
HEADING = "Modl Abstract Mana"
VARS = {
    "manaHeight": modl.Var(geometry=True, min=0.05, max=10),
    "manaWidth": modl.Var(geometry=True, min=0.02, max=10),
}


def tags():
    modl.check_sources(DOC, HEADING, ["Mana.png"])
    return modl.read_tags(DOC, HEADING, VARS)


def values(overrides=None):
    """The vars in meters, from the doc's tags, with overrides {name: value in the tag's unit},
    each held within its limits."""
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


def bipyramid(v):
    """The mesh: eight flat faces, each a triangle from a point to two neighboring equator corners."""
    h, r = v["manaHeight"], v["manaWidth"] / 2
    mid = h / 2
    corners = [(r, mid, 0.0), (0.0, mid, r), (-r, mid, 0.0), (0.0, mid, -r)]
    top, bottom = (0.0, h, 0.0), (0.0, 0.0, 0.0)
    uv = lambda p: ((p[0] + p[2]) / (2 * v["manaWidth"]) + 0.5, p[1] / h)
    mesh = modl.Mesh(FAMILY)
    for k in range(4):
        a, b = corners[k], corners[(k + 1) % 4]
        for tip in (top, bottom):
            # the face's outward normal: from the bipyramid's axis through the face's middle
            e1 = [a[i] - tip[i] for i in range(3)]
            e2 = [b[i] - tip[i] for i in range(3)]
            n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
            middle = [(a[i] + b[i] + tip[i]) / 3 for i in range(3)]
            out = [middle[0], middle[1] - mid, middle[2]]
            if sum(n[i] * out[i] for i in range(3)) < 0:
                n = [-x for x in n]
            length = sum(x * x for x in n) ** 0.5
            n = tuple(x / length for x in n)
            mesh.face([(tip, uv(tip)), (a, uv(a)), (b, uv(b))], n)
    return mesh


def build(v, install_too=False, report=print):
    """Writes the model into obj/ (and with install_too into Canopy). Returns Canopy's changed files."""
    mesh = bipyramid(v)
    modl.write_obj(os.path.join(modl.HERE, FAMILY + ".obj"), mesh, FAMILY + ".mtl", MATERIAL)
    with open(os.path.join(modl.HERE, FAMILY + ".mtl"), "w") as f:
        f.write(f"newmtl {MATERIAL}\nKd 0.3 0.86 0.93\n")  # the preview's cyan; the game draws the Mana shader
    report(f"{FAMILY}: {v['manaHeight']:g} m tall, {v['manaWidth']:g} m across, {len(mesh.tris)} triangles")
    return install(mesh) if install_too else []


def install(mesh):
    base = f"Assets/Modl/{FAMILY}"
    # the material is modl/tools/shaders.js's, in the working tree (not yet committed)
    material = open(os.path.join(modl.CANOPY, MATERIAL_PATH + ".meta"), encoding="utf-8").read()
    material_guid = next(line.split()[1] for line in material.splitlines() if line.startswith("guid:"))
    obj_meta = modl.canopy_file(OBJ_META).decode().replace("materialImportMode: 2", "materialImportMode: 0")
    obj = f"{base}/{FAMILY}.obj"
    files = {
        obj: open(os.path.join(modl.HERE, FAMILY + ".obj"), "rb").read(),
        obj + ".meta": modl.meta_with_guid(obj_meta, modl.guid_of(obj)),
    }
    prefab = f"{base}/{FAMILY}.prefab"
    files[prefab] = modl.prefab_yaml(FAMILY, [(FAMILY, modl.guid_of(obj))], material_guid)
    files[prefab + ".meta"] = f"fileFormatVersion: 2\nguid: {modl.guid_of(prefab)}\nPrefabImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    return modl.install(FAMILY, files)


def main():
    unused = modl.unused_tags(tags(), VARS)
    if unused:
        print(f"note: tags not used yet: {', '.join(unused)}")
    written = build(values(), "--write" in sys.argv)
    if "--write" in sys.argv:
        print(f"Canopy Assets/Modl/{FAMILY}: {len(written)} files changed" + (": " + ", ".join(p.split('/')[-1] for p in written) if written else ""))


if __name__ == "__main__":
    main()
