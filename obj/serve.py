"""A model family's tweak worker, for layout's Tweak (modl SPEC.md, Tweakvars).

  python3 obj/serve.py Assets/Modl/<Family>

Finds the script in obj/ whose FAMILY is <Family>, then answers one JSON request per stdin line
with one JSON reply per stdout line (anything the script prints goes to stderr). The script and
modl.py are reloaded when they change, so edits to them apply to the next request. Values are in
each tag's own unit ({benchDepth 1.5 m}: 1.5).
  {"op": "vars"}                -> {"family", "assets": [names], "vars": [{name, value, unit,
                                    step, min, max, geometry, textures, rebuild, live}], "uses": {asset:
                                    [the vars it uses, for a carried piece's list]}, "shaders":
                                    [{"material": guid, "name"}: the family's SHADERS, each
                                    material's live vars grouped in layout's list under one row,
                                    <name>Shaders], "watch": [the
                                    spec doc, the script, modl.py: a change to one calls for a
                                    write with no values, a rebuild from the doc]}
  {"op": "meshes", "values"}    -> {"meshes": {model name: {v, n, uv, f}}, "lods": {asset:
                                    {size, heights}}}: every model (each LOD level is one, named
                                    as its .obj) with positions, normals and uvs flat and f
                                    triangle indices (OBJ's right-handed axes), each asset's
                                    LODGroup, and "anchors": {asset: {ring}} for assets whose
                                    pivot sits `ring` m from a ring's center along their +Z
  {"op": "textures", "values"}  -> {"map": png path, "normal": png path, "more": [{"assets",
                                    "map", "normal"}]}: preview atlases (more: the atlases of
                                    those assets that have their own, the family's more_textures)
  {"op": "write", "values"}     -> {"doc": changed, "written": [Canopy paths]}: the values into
                                    the doc's tags, then the full build installed into Canopy
A live var's "live" lists what it sets, on materials by guid (layout applies them as the drag
goes, asking nothing): [{"material", "property": "_NormalStrength", "_Glossiness" or
"_Brightness", "scale"?} (the value itself, or times scale), {"material", "tiling": k} (the detail texture's tiling k / value), {"material",
"strength": s, "mean": m} (the detail texture baked at strength s, its linear mean m: at value
v it is 1 + v / s (d - 1), and the color m / (1 - v / s (1 - m)) brighter)].
Errors reply {"error": message}.
"""

import contextlib
import importlib
import json
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modl  # noqa: E402


def script_for(family):
    for name in sorted(os.listdir(HERE)):
        if name.endswith(".py") and name not in ("modl.py", "serve.py"):
            text = open(os.path.join(HERE, name), encoding="utf-8").read()
            if re.search(r'^FAMILY = "' + re.escape(family) + '"', text, re.M):
                return name[:-3]
    raise SystemExit(f"serve.py: no script in obj/ has FAMILY = \"{family}\"")


class Family:
    def __init__(self, family):
        self.name = script_for(family)
        self.module, self.stamp = None, None

    def get(self):
        files = [os.path.join(HERE, self.name + ".py"), os.path.join(HERE, "modl.py")]
        stamp = tuple(os.path.getmtime(f) for f in files)
        if stamp != self.stamp:
            importlib.reload(modl)
            self.module = importlib.reload(self.module) if self.module else importlib.import_module(self.name)
            self.stamp = stamp
        return self.module


def step(m, name, t):
    """A var's drag step: its own (modl.Var's step), else its tag's (modl.step_of)."""
    return min(getattr(m.VARS.get(name), "step", None) or 1e9, modl.step_of(t[name][0], t[name][1]))


def vars_reply(m):
    t = m.tags()
    live = m.live(m.values()) if hasattr(m, "live") else {}
    out = []
    for name, var in sorted(m.VARS.items()):
        value, unit = t[name]
        per = modl.UNITS[unit]
        out.append({
            "name": name, "value": value, "unit": unit, "step": step(m, name, t),
            "min": None if var.min is None else var.min / per, "max": None if var.max is None else var.max / per,
            "geometry": var.geometry, "textures": var.textures, "rebuild": var.rebuild,
            "live": live.get(name) if getattr(var, "live", False) else None,
        })
    watch = [os.path.abspath(m.DOC), os.path.abspath(m.__file__), os.path.join(HERE, "modl.py")]
    names = [b.name for b in m.assets(m.values())]
    uses = m.uses(m.values(), live) if hasattr(m, "uses") else {}
    shaders = [{"material": modl.material_guid(m.FAMILY, k), "name": n} for k, n in getattr(m, "SHADERS", {}).items()]
    return {"family": m.FAMILY, "assets": names, "vars": out, "watch": watch, "uses": uses, "shaders": shaders}


def handle(fam, req):
    m = fam.get()
    op, values = req.get("op"), req.get("values") or {}
    if op == "vars":
        return vars_reply(m)
    if op == "meshes":
        bs = m.assets(m.values(values))
        return {"meshes": {x.name: modl.mesh_json(x) for b in bs for x in b.lods}, "lods": {b.name: {"size": b.size, "heights": b.heights} for b in bs},
                "anchors": {b.name: b.anchor for b in bs if getattr(b, "anchor", None)}}
    if op == "textures":
        _, color, normal = m.textures(m.values(values))
        out = os.path.join(modl.CACHE, "preview")
        os.makedirs(out, exist_ok=True)
        paths = {"map": os.path.join(out, m.FAMILY + "_tx.png"), "normal": os.path.join(out, m.FAMILY + "_normal.png")}
        modl.write_png(paths["map"], color, level=1)
        modl.write_png(paths["normal"], normal, level=1)
        paths["more"] = []
        for k, (assets, c, n) in enumerate(m.more_textures(m.values(values)) if hasattr(m, "more_textures") else []):
            more = {"assets": assets, "map": os.path.join(out, f"{m.FAMILY}_more{k}_tx.png"), "normal": os.path.join(out, f"{m.FAMILY}_more{k}_normal.png")}
            modl.write_png(more["map"], c, level=1)
            modl.write_png(more["normal"], n, level=1)
            paths["more"].append(more)
        return paths
    if op == "write":
        t = m.tags()
        steps = {n: step(m, n, t) for n in values if n in t}
        changed = modl.write_tags(m.DOC, m.HEADING, {n: float(x) for n, x in values.items() if n in t}, steps)
        written = m.build(m.values(), True, report=lambda s: print(s, file=sys.stderr))
        return {"doc": changed, "written": written}
    raise ValueError(f"unknown op {op!r}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 obj/serve.py Assets/Modl/<Family>")
    fam = Family(sys.argv[1].rstrip("/").split("/")[-1])
    reply = sys.stdout
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            with contextlib.redirect_stdout(sys.stderr):
                out = handle(fam, json.loads(line))
        except Exception as error:  # every failure is a reply, so layout can show it
            traceback.print_exc(file=sys.stderr)
            out = {"error": f"{type(error).__name__}: {error}"}
        reply.write(json.dumps(out, separators=(",", ":")) + "\n")
        reply.flush()


if __name__ == "__main__":
    main()
