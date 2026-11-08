"""modl: the library modl's model scripts build on (SPEC.md; the primitives follow PLAN.md).
Python stdlib only.

- Images: PNG read and write (8-bit RGB/RGBA), float images, bilinear sampling.
- Textures: stone synthesized from patches of an existing Canopy texture (color and normal
  together), trim-sheet bands, normal detail from height profiles (slots, bevels).
- Geometry: a profile of edges swept along an arc (Revolve), with flat caps, each edge its own
  region with hard edges between; UVs at physical scale on a trim sheet.
- Export: OBJ and MTL (SPEC.md's format).
- Canopy: a family installed into the Canopy working tree (models, textures, material, prefabs,
  with their .meta files), guids from paths so reruns keep references.
- Tweakvars: values read from, and written back to, the `{name value unit}` tags of a model's
  `# Modl` section in the docs (SPEC.md).
"""

import contextlib
import hashlib
import json
import math
import os
import random
import re
import struct
import subprocess
import zlib
from array import array

import numpy as np

CANOPY = os.environ.get("CANOPY", "/sdcard/Canopy")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")


# ---------- tweakvars ----------

DOCS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs"))
# A tag's unit and how many of it make the script's own unit (meters, degrees, px/m, counts).
UNITS = {"m": 1.0, "cm": 0.01, "mm": 0.001, "deg": 1.0, "px/m": 1.0, "px": 1.0, "": 1.0}
TAG = re.compile(r"\{([A-Za-z]\w*) (-?\d+(?:\.\d+)?)(?: ([^{}\s]+))?\}")


class Var:
    """How a script uses a tweakvar: whether a change reshapes the geometry, redoes the
    textures, needs a full rebuild (new assets or a new stone), or is live: it sets only its
    materials' properties, which layout shows at once (the family's live(values) says how); its
    limits in the tag's unit; its step, where step_of's (a unit's, or 1 for none) is too coarse:
    a shader's property, such as a normal strength of 1, wants hundredths."""

    def __init__(self, geometry=False, textures=False, rebuild=False, live=False, min=None, max=None, step=None):
        self.geometry, self.textures, self.rebuild, self.live, self.min, self.max = geometry, textures, rebuild, live, min, max
        self.step = step


def section(doc, heading):
    """The text of `# <heading>` in a docs file, and its start and end offsets."""
    text = open(doc, encoding="utf-8").read()
    m = re.search(r"^# " + re.escape(heading) + r"\n(.*?)(?=^# |\Z)", text, re.S | re.M)
    if not m:
        raise ValueError(f"no '# {heading}' in {doc}")
    return text, m.start(1), m.end(1)


def read_tags(doc, heading, declared):
    """The section's tweakvars: {name: (value, unit)} in the tags' own units, checked against the
    script's declared vars: every declared one tagged, each tagged the same everywhere."""
    text, a, b = section(doc, heading)
    found = {}
    for m in TAG.finditer(text, a, b):
        name, value, unit = m.group(1), float(m.group(2)), m.group(3) or ""
        if unit not in UNITS:
            raise ValueError(f"{{{name}}}: unknown unit '{unit}' (use {', '.join(u or 'none' for u in UNITS)})")
        if name in found and found[name] != (value, unit):
            raise ValueError(f"{{{name}}} is tagged twice with different values: {found[name]} and {(value, unit)}")
        found[name] = (value, unit)
    missing = [n for n in declared if n not in found]
    if missing:
        raise ValueError(f"'# {heading}' in {os.path.relpath(doc, DOCS)} has no tag for: {', '.join(missing)}")
    return found


def sources(doc, heading):
    """The section's `Source:` lines (as gptviz's # Extract has them): a bare name is an image in
    vids/ (gptviz's output), "Canopy <path>" a file in the Canopy repo."""
    text, a, b = section(doc, heading)
    return [m.strip() for m in re.findall(r"^Source:(.*)$", text[a:b], re.M)]


def check_sources(doc, heading, used):
    """Every input a script reads must be declared by a Source line, so what a model is built from
    can be seen (and checked for staleness) from the docs alone."""
    missing = [u for u in used if u not in sources(doc, heading)]
    if missing:
        raise ValueError(f"'# {heading}' in {os.path.relpath(doc, DOCS)} needs Source lines for: {', '.join(missing)}")


class Reads(dict):
    """A family's values (a dict) that notes which of them are read, so a model made from them
    can be cached by the values it used (made); and which it reads itself (own: not while quiet,
    as packing islands reads every part's sizes), by asset while asset is set (a texture's
    painter's), for Tweak's list of a carried piece's vars."""
    def __init__(self, values):
        super().__init__(values)
        self.read, self.own, self.by, self.quiet, self.asset = set(), set(), {}, 0, None

    def __getitem__(self, name):
        self.read.add(name)
        if not self.quiet:
            self.own.add(name)
            self.by.setdefault(self.asset or "", set()).add(name)
        return super().__getitem__(name)


@contextlib.contextmanager
def quiet(values):
    """Reads of values (if a Reads) in it aren't the reader's own (see Reads)."""
    if isinstance(values, Reads):
        values.quiet += 1
    try:
        yield
    finally:
        if isinstance(values, Reads):
            values.quiet -= 1


def kept(key, make):
    """make(), kept on disk (.cache/kept/) by key, a JSON-able description of everything it
    depends on (its sources' paths with their modification times, its settings), so slow reads
    (ImageMagick's, a photo's tile) are made once across runs and workers."""
    import pickle
    name = hashlib.sha1(json.dumps(key, sort_keys=True, default=str).encode()).hexdigest()
    path = os.path.join(CACHE, "kept", name + ".pkl")
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except (OSError, EOFError, pickle.UnpicklingError):
        pass
    value = make()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}"
    with open(tmp, "wb") as f:
        pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp, path)
    return value


def note_texture_uses(family, atlas, by):
    """Keeps which vars each asset's textures read (by: {asset or "": vars}, "" for reads outside
    any asset's), in .cache/<family>_uses.json by atlas, for Tweak's vars (texture_uses)."""
    path = os.path.join(CACHE, f"{family}_uses.json")
    try:
        saved = json.load(open(path))
    except (OSError, ValueError):
        saved = {}
    saved[atlas] = {k: sorted(x) for k, x in by.items()}
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w") as f:
        json.dump(saved, f)


def texture_uses(family):
    """note_texture_uses' record, {atlas: {asset or "": [vars]}} ({} before any textures run)."""
    try:
        return json.load(open(os.path.join(CACHE, f"{family}_uses.json")))
    except (OSError, ValueError):
        return {}


def model_uses(name):
    """The vars a model read itself when last made (made's), or None."""
    hit = _made.get(name)
    return hit[2] if hit else None


_painted = {}  # an island painter's name -> (the values it read, as (name, value) pairs, its regions, its own reads)
_tasks = []  # the painters a paint_islands is running, for its forked workers


def _region(img, rect, pad):
    """The pixels of rect and its padding (clipped to img): (x, y, numpy copy)."""
    x0, y0, w, h = rect
    xa, ya, xb, yb = max(0, x0 - pad), max(0, y0 - pad), min(img.w, x0 + w + pad), min(img.h, y0 + h + pad)
    return xa, ya, img.np()[ya:yb, xa:xb].copy()


def _paint(i, color, normal, values, pad):
    """Runs painter i of _tasks on color and normal: (the values it read as pairs, its own reads,
    its regions [(x, y, color pixels, normal pixels)])."""
    name, asset, fn = _tasks[i]
    reads = Reads(values)
    reads.asset = asset
    rects = fn(color, normal, reads)
    regions = [(x, y, c, _region(normal, rect, pad)[2]) for rect in rects for x, y, c in [_region(color, rect, pad)]]
    return tuple((k, dict.__getitem__(values, k)) for k in reads.read), {k: set(x) for k, x in reads.by.items()}, regions


def _paint_forked(i):
    return _paint(i, *_forked)


def forked(fn, items, workers=None):
    """[fn(item) for item in items], each in a forked child (one a core at a time), its result
    pickled back through a pipe. (multiprocessing's Pool took seconds to shut down here.)"""
    import pickle
    import select
    workers = workers or os.cpu_count() or 1
    results, running, todo = [None] * len(items), {}, list(enumerate(items))
    while todo or running:
        while todo and len(running) < workers:
            k, item = todo.pop(0)
            r, w = os.pipe()
            pid = os.fork()
            if pid == 0:  # the child
                os.close(r)
                try:
                    data = pickle.dumps((True, fn(item)), protocol=pickle.HIGHEST_PROTOCOL)
                except BaseException as error:  # noqa: BLE001 - sent back, raised in the parent
                    data = pickle.dumps((False, f"{type(error).__name__}: {error}"))
                with os.fdopen(w, "wb") as out:
                    out.write(data)
                os._exit(0)
            os.close(w)
            running[r] = (k, pid, [])
        ready, _, _ = select.select(list(running), [], [])
        for r in ready:
            chunk = os.read(r, 1 << 20)
            if chunk:
                running[r][2].append(chunk)
                continue
            k, pid, chunks = running.pop(r)
            os.close(r)
            os.waitpid(pid, 0)
            ok, value = pickle.loads(b"".join(chunks))
            if not ok:
                raise RuntimeError(f"a forked painter failed: {value}")
            results[k] = value
    return results


def paint_islands(color, normal, tasks, values, pad=8):
    """Paints an atlas's islands (Ken, 2026-11-04: the toolchain's speed is the game's): tasks
    [(name, asset, painter)], each painter(color, normal, values) painting its islands, only
    within them and their pad, and returning their rects; its reads are asset's (Reads). A
    painter is run again only when a value it read has changed (else its last regions are put
    back), and those that run do so in forked workers, one a core. Returns the reads by asset
    ({asset: vars}, for note_texture_uses)."""
    global _tasks, _forked
    misses = [i for i, (name, _, _) in enumerate(tasks)
              if not (name in _painted and all(k in values and values[k] == x for k, x in _painted[name][0]))]
    _tasks, _forked = tasks, (color, normal, values, pad)
    if len(misses) > 1:
        done = forked(_paint_forked, misses)
    else:
        done = [_paint(i, color, normal, values, pad) for i in misses]
    _tasks, _forked = [], None
    for i, result in zip(misses, done):
        _painted[tasks[i][0]] = result
    by = {}
    for name, _, _ in tasks:
        _, own, regions = _painted[name]
        for x, y, c, n in regions:
            color.np()[y:y + c.shape[0], x:x + c.shape[1]] = c
            normal.np()[y:y + n.shape[0], x:x + n.shape[1]] = n
        for k, x in own.items():
            by.setdefault(k, set()).update(x)
    return by


_forked = None
_made = {}  # a model's name -> (the values it read, as (name, value) pairs, what made it, those it read itself)


def made(name, make, values):
    """make(values) for a model, again only when a value it read last time has changed, so
    Tweak's drag on one var remakes only the models that use it (Ken, 2026-11-04: leaf curl
    should move in near real time; remaking every model took about a second)."""
    hit = _made.get(name)
    if hit and all(k in values and values[k] == x for k, x in hit[0]):
        return hit[1]
    reads = Reads(values)
    out = make(reads)
    _made[name] = (tuple((k, dict.__getitem__(values, k)) for k in reads.read), out, set(reads.own))
    return out


def unused_tags(tags, declared):
    return [n for n in tags if n not in declared]


def number(value, step):
    """A value rounded to its step and written without trailing zeros."""
    places = max(0, -math.floor(math.log10(step) + 1e-9)) if step < 1 else 0
    text = f"{round(value / step) * step:.{places}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def write_tags(doc, heading, values, steps):
    """Rewrites the numbers of the section's tags for these vars ({name: value in the tag's
    unit}); the prose around them is untouched. Returns whether the file changed."""
    text, a, b = section(doc, heading)

    def sub(m):
        name = m.group(1)
        if name not in values:
            return m.group(0)
        unit = m.group(3)
        return "{" + name + " " + number(values[name], steps[name]) + (" " + unit if unit else "") + "}"

    new = text[:a] + TAG.sub(sub, text[a:b]) + text[b:]
    if new != text:
        with open(doc, "w", encoding="utf-8") as f:
            f.write(new)
    return new != text


def step_of(value, unit):
    """A drag's step for a value in a unit: a centimeter, a tenth of a millimeter-scale unit,
    half a degree, a pixel, one; but never coarser than a hundredth of the value's own size (two
    figures), so a small value (a strength of 0.12, a thread of 1.5 mm) isn't rounded away when
    it is written (Ken, 2026-11-04: Tweak had written them as 0 and 2 mm)."""
    step = {"m": 0.01, "cm": 0.1, "mm": 1, "deg": 0.5, "px/m": 1, "px": 0.1, "": 1}.get(unit, 0.01)
    if value and float(value) != int(value):
        step = min(step, 10.0 ** (math.floor(math.log10(abs(value))) - 1))
    return step


def mesh_json(mesh):
    """A mesh for layout's live tweaks: flat positions, normals, uvs and triangle indices."""
    return {
        "v": [round(x, 5) for p, _, _ in mesh.verts for x in p],
        "n": [round(x, 4) for _, n, _ in mesh.verts for x in n],
        "uv": [round(x, 5) for _, _, uv in mesh.verts for x in uv],
        "f": [i for t in mesh.tris for i in t],
    }


# ---------- images ----------

class Image:
    """A 4-channel image, rows top to bottom: floats (0..1 as stored), or bytes read from a PNG
    (unit 1/255) to save converting them."""

    def __init__(self, w, h, fill=(0.0, 0.0, 0.0, 1.0)):
        self.w, self.h = w, h
        self.px = array("f")
        self.px.frombytes(np.tile(np.array(fill, np.float32), w * h).tobytes())
        self.unit = 1.0

    def copy(self):
        out = Image(1, 1)
        out.w, out.h, out.px, out.unit = self.w, self.h, array(self.px.typecode, self.px), self.unit
        return out

    def np(self):
        """Its pixels as a numpy array, rows by columns by 4, sharing them (float32, or uint8 as
        read from a PNG: times unit)."""
        return np.asarray(memoryview(self.px)).reshape(self.h, self.w, 4)

    def get(self, x, y):
        i = (y * self.w + x) * 4
        return self.px[i:i + 4]

    def set(self, x, y, c):
        i = (y * self.w + x) * 4
        self.px[i:i + 4] = array("f", c)

    def sample(self, x, y):
        """Bilinear, at pixel-center coordinates (x, y), clamped to the image."""
        x = min(max(x - 0.5, 0.0), self.w - 1.0)
        y = min(max(y - 0.5, 0.0), self.h - 1.0)
        x0, y0 = int(x), int(y)
        x1, y1 = min(x0 + 1, self.w - 1), min(y0 + 1, self.h - 1)
        fx, fy = x - x0, y - y0
        p, u = self.px, self.unit
        a, b = (y0 * self.w + x0) * 4, (y0 * self.w + x1) * 4
        c, d = (y1 * self.w + x0) * 4, (y1 * self.w + x1) * 4
        return [((p[a + k] * (1 - fx) + p[b + k] * fx) * (1 - fy) + (p[c + k] * (1 - fx) + p[d + k] * fx) * fy) * u for k in range(4)]


def read_png(data):
    """8-bit RGB or RGBA, not interlaced, to an Image."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, idat = 8, []
    while pos < len(data):
        n, = struct.unpack(">I", data[pos:pos + 4])
        tag, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat.append(body)
    if depth != 8 or interlace or ctype not in (2, 6):
        raise ValueError("only 8-bit RGB or RGBA, not interlaced")
    bpp = 4 if ctype == 6 else 3
    try:  # ImageMagick unfilters far faster than Python
        rows = bytearray(subprocess.run(["magick", "png:-", "-depth", "8", "RGBA:-"], input=data, check=True, capture_output=True).stdout)
        if len(rows) == w * h * 4:
            img = Image(1, 1)
            img.w, img.h, img.px, img.unit = w, h, array("B", rows), 1 / 255
            return img
    except (OSError, subprocess.CalledProcessError):
        pass
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    rows, prev = bytearray(h * stride), bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            line = bytearray((a + b) & 255 for a, b in zip(line, prev))
        elif f == 3:
            for i in range(stride):
                line[i] = (line[i] + ((line[i - bpp] if i >= bpp else 0) + prev[i]) // 2) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b, c = prev[i], prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows[y * stride:(y + 1) * stride] = line
        prev = line
    if bpp == 3:
        rgba = bytearray(w * h * 4)
        rgba[0::4], rgba[1::4], rgba[2::4] = rows[0::3], rows[1::3], rows[2::3]
        rgba[3::4] = b"\xff" * (w * h)
        rows = rgba
    img = Image(1, 1)
    img.w, img.h, img.px, img.unit = w, h, array("B", rows), 1 / 255
    return img


def write_png(path, img, alpha=False, level=6):
    """img as a PNG, its values rounded to bytes, zlib level 6 (9 took far longer for a few
    percent: Ken, 2026-11-04, lighter compression)."""
    bpp = 4 if alpha else 3
    v = img.np()[:, :, :bpp].astype(np.float64) * img.unit
    rows = np.clip(np.floor(v * 255 + 0.5), 0, 255).astype(np.uint8).reshape(img.h, img.w * bpp)
    raw = np.concatenate([np.zeros((img.h, 1), np.uint8), rows], axis=1).tobytes()

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", img.w, img.h, 8, 6 if alpha else 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), level)))
        f.write(chunk(b"IEND", b""))


def save_cache(name, imgs):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, name), "wb") as f:
        for img in imgs:
            f.write(struct.pack("<II", img.w, img.h))
            img.px.tofile(f)


def load_cache(name, count):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        return None
    out = []
    with open(p, "rb") as f:
        for _ in range(count):
            w, h = struct.unpack("<II", f.read(8))
            img = Image(w, h)
            img.px = array("f")
            img.px.fromfile(f, w * h * 4)
            out.append(img)
    return out


# ---------- Canopy files ----------

def read_unity_mesh(text):
    """A text-serialized Unity Mesh .asset (one triangle submesh, one vertex stream, float, half
    or 8-bit channels): {positions, normals, uvs, triangles}, in Unity's own (left-handed) axes.
    As layout/tools/unity-mesh.js reads them."""
    num = lambda k: int((re.search(r"\b" + k + r": (-?\d+)", text) or [0, 0])[1])
    if num("m_MeshCompression"):
        raise ValueError("compressed mesh not supported")
    count = num("m_VertexCount")
    block = text.split("m_Channels:")[1].split("m_DataSize:")[0]
    channels = [dict(stream=int(m[0]), offset=int(m[1]), format=int(m[2]), dim=int(m[3]) & 0xF)
                for m in re.findall(r"- stream: (\d+)\s+offset: (\d+)\s+format: (\d+)\s+dimension: (\d+)", block)]
    size = {0: 4, 1: 2, 2: 1, 3: 1}
    stride = max(c["offset"] + c["dim"] * size[c["format"]] for c in channels if c["dim"])
    data = bytes.fromhex(re.search(r"_typelessdata: ([0-9a-f]*)", text)[1])

    def channel(ci):
        c = channels[ci]
        if not c["dim"]:
            return None
        out = []
        for v in range(count):
            row = []
            for d in range(c["dim"]):
                o = v * stride + c["offset"] + d * size[c["format"]]
                if c["format"] == 0:
                    row.append(struct.unpack_from("<f", data, o)[0])
                elif c["format"] == 1:
                    row.append(struct.unpack_from("<e", data, o)[0])
                elif c["format"] == 2:
                    row.append(data[o] / 255)
                else:
                    row.append(struct.unpack_from("<b", data, o)[0] / 127)
            out.append(row)
        return out

    sub = re.search(r"firstByte: (\d+)\r?\n\s+indexCount: (\d+)\r?\n\s+topology: (\d+)", text)
    if not sub or int(sub[3]) != 0:
        raise ValueError("only one triangle submesh is supported")
    wide = num("m_IndexFormat") == 1
    ib = bytes.fromhex(re.search(r"m_IndexBuffer: ([0-9a-f]*)", text)[1])
    tris = [struct.unpack_from("<I" if wide else "<H", ib, i * (4 if wide else 2))[0] for i in range(int(sub[2]))]
    return {"positions": channel(0), "normals": channel(1), "uvs": channel(4), "triangles": tris}

def canopy_file(path):
    """A file's committed content from the Canopy repo (fetched if the checkout is sparse)."""
    return subprocess.run(["git", "-C", CANOPY, "show", "HEAD:" + path], check=True, capture_output=True).stdout


# ---------- textures ----------

def synthesize(color, normal, rects, w, h, scale, patch=104, feather=40, seed=1, even=0.8):
    """Color and normal images w x h, seamless left to right, made of patches of the source
    images' rects (x0, y0, x1, y1: plain areas, away from their islands' edges), each sampled
    at `scale` source pixels per output pixel, randomly flipped, laid on a jittered grid and
    blended over feathered edges. Each patch keeps only its detail: its average color moves
    `even` of the way to the sources' average, and its average tilt is removed (the source's
    large-scale tilts, flipped with the patches, showed as squares). Normals are unpacked to
    -1..1, flipped with their patch, blended and renormalized."""
    rng = random.Random(seed)
    # the sources' average color, from a sample of their rects
    mean = [0.0, 0.0, 0.0]
    for _ in range(3000):
        r = rects[rng.randrange(len(rects))]
        c = color.sample(rng.uniform(r[0], r[2]), rng.uniform(r[1], r[3]))
        for k in range(3):
            mean[k] += c[k] / 3000
    acc_c, acc_n = array("f", [0.0] * (w * h * 3)), array("f", [0.0] * (w * h * 3))
    acc_a = array("f", [0.0] * (w * h))
    step = patch - feather
    cols = max(1, round(w / step))
    step_x = w / cols
    weight = [min(1.0, (i + 0.5) / feather, (patch - i - 0.5) / feather) for i in range(patch)]
    weight = [0.5 - 0.5 * math.cos(math.pi * x) for x in weight]
    # two layers: a grid jittered little enough to cover everything, then one half a step off
    # with more jitter over it, to break up the grid
    spots = []
    for layer, jitter in ((0, feather * 0.3), (0.5, step * 0.35)):
        y = -feather + layer * step
        while y < h:
            for col in range(cols):
                spots.append((int((col + layer) * step_x + rng.uniform(-jitter, jitter)), int(y + rng.uniform(-jitter, jitter))))
            y += step
    for x0, y0 in spots:
        r = rects[rng.randrange(len(rects))]
        sw, sh = patch * scale, patch * scale
        sx = rng.uniform(r[0], r[2] - sw)
        sy = rng.uniform(r[1], r[3] - sh)
        fx, fy = rng.random() < 0.5, rng.random() < 0.5
        samples = []
        for j in range(patch):
            py = sy + ((patch - 1 - j) if fy else j) * scale + 0.5 * scale
            for i in range(patch):
                px = sx + ((patch - 1 - i) if fx else i) * scale + 0.5 * scale
                c = color.sample(px, py)
                n = normal.sample(px, py)
                nx, ny = n[0] * 2 - 1, n[1] * 2 - 1
                samples.append((c, -nx if fx else nx, -ny if fy else ny, n[2] * 2 - 1))
        cnt = len(samples)
        pm = [sum(sm[0][k] for sm in samples) / cnt for k in range(3)]
        shift = [(mean[k] - pm[k]) * even for k in range(3)]
        tx_, ty_ = sum(sm[1] for sm in samples) / cnt, sum(sm[2] for sm in samples) / cnt
        for j in range(patch):
            ty = y0 + j
            if ty < 0 or ty >= h:
                continue
            wy = weight[j]
            for i in range(patch):
                a = weight[i] * wy
                tx = (x0 + i) % w
                c, nx, ny, nz = samples[j * patch + i]
                c = (c[0] + shift[0], c[1] + shift[1], c[2] + shift[2])
                nx, ny = nx - tx_, ny - ty_
                o = ty * w + tx
                k = 1 - a
                acc_a[o] = acc_a[o] * k + a
                o3 = o * 3
                acc_c[o3] = acc_c[o3] * k + c[0] * a
                acc_c[o3 + 1] = acc_c[o3 + 1] * k + c[1] * a
                acc_c[o3 + 2] = acc_c[o3 + 2] * k + c[2] * a
                acc_n[o3] = acc_n[o3] * k + nx * a
                acc_n[o3 + 1] = acc_n[o3 + 1] * k + ny * a
                acc_n[o3 + 2] = acc_n[o3 + 2] * k + nz * a
    out_c, out_n = Image(w, h), Image(w, h)
    for o in range(w * h):
        a = acc_a[o] or 1.0
        o3 = o * 3
        out_c.px[o * 4:o * 4 + 3] = array("f", [acc_c[o3] / a, acc_c[o3 + 1] / a, acc_c[o3 + 2] / a])
        nx, ny, nz = acc_n[o3], acc_n[o3 + 1], max(acc_n[o3 + 2], 1e-4)
        ln = math.sqrt(nx * nx + ny * ny + nz * nz)
        out_n.px[o * 4:o * 4 + 3] = array("f", [nx / ln * 0.5 + 0.5, ny / ln * 0.5 + 0.5, nz / ln * 0.5 + 0.5])
    return out_c, out_n


class Band:
    """A trim-sheet band: rows [top, top + rows) of the sheet, `meters` tall at the sheet's
    density, with v measured in meters from its bottom edge (v up, SPEC.md)."""

    def __init__(self, name, meters, sheet):
        self.name, self.meters, self.sheet = name, meters, sheet
        self.rows = round(meters * sheet.density)

    def uv(self, along, across):
        """UV of a point `along` meters (u, wrapping) and `across` meters from the band's
        bottom edge (v)."""
        s = self.sheet
        return (along * s.density / s.w, (s.h - self.top - self.rows + across * s.density) / s.h)


class TrimSheet:
    """Bands stacked from the top of a w x h sheet at `density` px/m, `pad` px apart."""

    def __init__(self, w, h, density, pad=8):
        self.w, self.h, self.density, self.pad = w, h, density, pad
        self.bands = {}
        self.next = pad

    def band(self, name, meters):
        b = Band(name, meters, self)
        b.top = self.next
        self.next += b.rows + self.pad
        if self.next > self.h:
            raise ValueError(f"bands overflow the {self.w}x{self.h} sheet at band {name}")
        self.bands[name] = b
        return b

    def tile_meters(self):
        return self.w / self.density


def apply_profile(color, normal, band, profile):
    """Bends a band's normals by a height profile across it, and darkens its color: profile(m)
    gives (slope dh/dv, shade) at m meters across from the band's bottom edge (v up). Normals
    combine by the whiteout blend."""
    s = band.sheet
    for row in range(band.rows):
        y = band.top + row
        across = (band.rows - row - 0.5) / s.density
        slope, shade = profile(across)
        if slope == 0 and shade == 1:
            continue
        # detail normal: (0, -dh/dv, 1), unnormalized; G is +v
        dl = math.sqrt(slope * slope + 1)
        dx, dy, dz = 0.0, -slope / dl, 1.0 / dl
        for x in range(s.w):
            i = (y * s.w + x) * 4
            nx, ny, nz = normal.px[i] * 2 - 1, normal.px[i + 1] * 2 - 1, normal.px[i + 2] * 2 - 1
            rx, ry, rz = nx + dx, ny + dy, nz * dz
            ln = math.sqrt(rx * rx + ry * ry + rz * rz)
            normal.px[i], normal.px[i + 1], normal.px[i + 2] = rx / ln * 0.5 + 0.5, ry / ln * 0.5 + 0.5, rz / ln * 0.5 + 0.5
            if shade != 1:
                color.px[i] *= shade
                color.px[i + 1] *= shade
                color.px[i + 2] *= shade


def bevel(width, meters, max_angle=55.0):
    """A faked rounded bevel `width` wide along both edges of a face `meters` across: (slope,
    shade) at a distance across, the surface falling toward the nearer edge, steepest at it;
    None away from the edges."""
    def at(across):
        for d, sign in ((across, 1.0), (meters - across, -1.0)):
            if d < width:
                t = 1 - d / width
                return sign * math.tan(math.radians(max_angle * t * t)), 1.0
        return None
    return at


def profile_of(*parts):
    """Profiles (slot, bevel, ...) as one: the first that applies at each distance across."""
    def at(across):
        for p in parts:
            r = p(across)
            if r is not None:
                return r
        return 0.0, 1.0
    return at


def slot(start, width, depth, shade=0.8):
    """A rounded groove `width` wide and `depth` deep whose near side is `start` meters across:
    (slope, shade) inside it, else None. The groove's color darkens toward its middle."""
    def at(across):
        t = (across - start) / width
        if 0 <= t <= 1:
            return -depth * math.pi / width * math.cos(math.pi * t), 1 - (1 - shade) * math.sin(math.pi * t)
        return None
    return at


# ---------- geometry ----------

class Mesh:
    """Unified vertices (position, normal, uv) and triangles, OBJ-style right-handed."""

    def __init__(self, name):
        self.name = name
        self.verts, self.index, self.tris = [], {}, []

    def vertex(self, p, n, uv):
        key = tuple(round(x, 6) for x in (*p, *n, *uv))
        if key not in self.index:
            self.index[key] = len(self.verts)
            self.verts.append((p, n, uv))
        return self.index[key]

    def face(self, corners, normal):
        """A convex polygon of (position, uv) corners with one normal, fanned; wound so its
        front faces along the normal."""
        ids = [self.vertex(p, normal, uv) for p, uv in corners]
        for k in range(1, len(ids) - 1):
            a, b, c = corners[0][0], corners[k][0], corners[k + 1][0]
            e1 = [b[i] - a[i] for i in range(3)]
            e2 = [c[i] - a[i] for i in range(3)]
            fn = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
            if sum(fn[i] * normal[i] for i in range(3)) >= 0:
                self.tris.append((ids[0], ids[k], ids[k + 1]))
            else:
                self.tris.append((ids[0], ids[k + 1], ids[k]))


    def face_ids(self, ids, normal):
        """A convex polygon of existing vertices, fanned, wound to face along `normal`."""
        for k in range(1, len(ids) - 1):
            a, b, c = (self.verts[i][0] for i in (ids[0], ids[k], ids[k + 1]))
            e1 = [b[i] - a[i] for i in range(3)]
            e2 = [c[i] - a[i] for i in range(3)]
            fn = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
            tri = (ids[0], ids[k], ids[k + 1])
            self.tris.append(tri if sum(fn[i] * normal[i] for i in range(3)) >= 0 else (tri[0], tri[2], tri[1]))


class Edge:
    """A profile edge from a to b, (radial, y) meters from the profile's center, its face
    textured by `band` with v running from a to b."""

    def __init__(self, a, b, band):
        self.a, self.b, self.band = a, b, band


def arc_segments(angle, outer, max_error):
    """Segments that keep a chord within max_error of an arc of `angle` degrees at radius
    `outer`."""
    seg = 2 * math.acos(max(-1.0, 1 - max_error / outer))
    return max(1, math.ceil(math.radians(angle) / seg))


def nested_segments(angle, outer, errors):
    """Segment counts for LOD levels, most detailed first, each within its level's error and each
    a multiple of the next, so a lower level's vertices are a subset of the one above."""
    counts = [arc_segments(angle, outer, e) for e in errors]
    for k in range(len(counts) - 2, -1, -1):
        counts[k] = counts[k + 1] * math.ceil(counts[k] / counts[k + 1])
    return counts


def revolve(name, edges, radius, angle, max_error=0.005, cap_band=None, segments=None):
    """Sweeps a closed profile (edges, in order around it) around the vertical axis, its center
    `radius` meters from the axis, through `angle` degrees centered on +Z, as one mesh whose
    pivot is the profile's center at the arc's middle: the axis is at (0, 0, -radius). Each edge
    is a face with hard edges; along the arc normals are smooth. Segments keep the chord within
    max_error of the arc at the profile's outermost radius (or are `segments`). Edge faces map u to the arc length
    at each point's own radius and v along the edge; the end caps (cap_band) map u to the
    radial distance from the profile's inner side and v to height."""
    outer = radius + max(max(e.a[0], e.b[0]) for e in edges)
    n = segments or arc_segments(angle, outer, max_error)
    phis = [math.radians(-angle / 2 + angle * k / n) for k in range(n + 1)]
    points = list(dict.fromkeys(p for e in edges for p in (e.a, e.b)))
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    # the profile's corners in order around its center (it is convex)
    points.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    def place(r, y, phi):
        return (r * math.sin(phi), y, r * math.cos(phi) - radius)

    mesh = Mesh(name)
    for e in edges:
        (ra, ya), (rb, yb) = e.a, e.b
        length = math.hypot(rb - ra, yb - ya)
        # the edge's outward normal in the profile plane: perpendicular, away from the center
        nr, ny = (yb - ya) / length, -(rb - ra) / length
        if nr * ((ra + rb) / 2 - cx) + ny * ((ya + yb) / 2 - cy) < 0:
            nr, ny = -nr, -ny
        for k in range(n):
            corners = []
            for phi, (r, y, t) in ((phis[k], (ra, ya, 0)), (phis[k], (rb, yb, length)), (phis[k + 1], (rb, yb, length)), (phis[k + 1], (ra, ya, 0))):
                corners.append((place(radius + r, y, phi), e.band.uv((radius + r) * phi, t)))
            mid = (phis[k] + phis[k + 1]) / 2
            # one normal per vertex: radial at the vertex's own angle, so the arc shades smoothly
            ids = []
            for (p, uv), phi in zip(corners, (phis[k], phis[k], phis[k + 1], phis[k + 1])):
                ids.append((p, (nr * math.sin(phi), ny, nr * math.cos(phi)), uv))
            vids = [mesh.vertex(p, nn, uv) for p, nn, uv in ids]
            want = (nr * math.sin(mid), ny, nr * math.cos(mid))
            a, b, c = ids[0][0], ids[1][0], ids[2][0]
            e1 = [b[i] - a[i] for i in range(3)]
            e2 = [c[i] - a[i] for i in range(3)]
            fn = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
            if sum(fn[i] * want[i] for i in range(3)) >= 0:
                mesh.tris += [(vids[0], vids[1], vids[2]), (vids[0], vids[2], vids[3])]
            else:
                mesh.tris += [(vids[0], vids[2], vids[1]), (vids[0], vids[3], vids[2])]
    if cap_band:
        inner = min(min(e.a[0], e.b[0]) for e in edges)
        bottom = min(min(e.a[1], e.b[1]) for e in edges)
        for phi, sign in ((phis[0], -1), (phis[-1], 1)):
            normal = (sign * math.cos(phi), 0.0, -sign * math.sin(phi))
            corners = [(place(radius + r, y, phi), cap_band.uv(r - inner, y - bottom)) for r, y in points]
            mesh.face(corners, normal)
    mesh.segments = n
    return mesh


# ---------- export ----------

def write_obj(path, mesh, mtl, material):
    lines = [f"# {mesh.name}: modl (obj/modl.py)", f"mtllib {mtl}", f"o {mesh.name}"]
    lines += [f"v {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}" for p, _, _ in mesh.verts]
    lines += [f"vt {uv[0]:.6f} {uv[1]:.6f}" for _, _, uv in mesh.verts]
    lines += [f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}" for _, n, _ in mesh.verts]
    lines.append(f"usemtl {material}")
    lines += ["f " + " ".join(f"{i + 1}/{i + 1}/{i + 1}" for i in t) for t in mesh.tris]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_mtl(path, material, family):
    with open(path, "w") as f:
        f.write(f"newmtl {material}\nKd 1 1 1\nmap_Kd {family}_tx.png\nmap_Bump {family}_normal.png\n")


# ---------- installing into Canopy ----------

# A model file with one object: Unity collapses it into its root, with these fixed ids
# (as layout/tools/make-shapes.js's placeholder prefabs use them).
MODEL = {"t": "-8679921383154817045", "go": "919132149155446097", "renderer": "-7635826562936255635"}
ROOT = {"go": "1000000000000000001", "t": "1000000000000000002"}


def guid_of(path):
    return hashlib.md5(("modl:" + path).encode()).hexdigest()


def id_of(*parts):
    return str(int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:15], 16) + 1)


def meta_with_guid(template, guid):
    lines = template.split("\n")
    return "\n".join(f"guid: {guid}" if l.startswith("guid: ") else l for l in lines)


def folder_meta(path):
    return f"fileFormatVersion: 2\nguid: {guid_of(path)}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"


def prefab_yaml(name, models, material_guid, lods=None):
    """A prefab: an empty root holding each model (a list of (object name, model guid)) nested at
    its origin with the material. With lods ({size, heights}: the LODGroup's size and each
    level's lowest screen height, a fraction), the root's LODGroup draws model k as level k."""
    insts, mods_by, stripped_t, renderers = [], [], [], []
    for order, (obj, guid) in enumerate(models):
        inst = id_of(name, order, guid)
        st = str((int(inst) ^ int(MODEL["t"])) & ((1 << 63) - 1))
        sr = str((int(inst) ^ int(MODEL["renderer"])) & ((1 << 63) - 1))
        mods = []

        def mod(target, prop, value, ref="{fileID: 0}", guid=guid):
            mods.append(f"    - target: {{fileID: {target}, guid: {guid}, type: 3}}\n      propertyPath: {prop}\n      value: {value}\n      objectReference: {ref}")

        mod(MODEL["t"], "m_RootOrder", order)
        for k in "xyz":
            mod(MODEL["t"], f"m_LocalPosition.{k}", 0)
        for k, v in zip("wxyz", (1, 0, 0, 0)):
            mod(MODEL["t"], f"m_LocalRotation.{k}", v)
        for k in "xyz":
            mod(MODEL["t"], f"m_LocalEulerAnglesHint.{k}", 0)
        mod(MODEL["go"], "m_Name", obj)
        mod(MODEL["renderer"], "m_Materials.Array.data[0]", "", f"{{fileID: 2100000, guid: {material_guid}, type: 2}}")
        insts.append(f"""--- !u!1001 &{inst}
PrefabInstance:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Modification:
    m_TransformParent: {{fileID: {ROOT['t']}}}
    m_Modifications:
""" + "\n".join(mods) + f"""
    m_RemovedComponents: []
  m_SourcePrefab: {{fileID: 100100000, guid: {guid}, type: 3}}
--- !u!4 &{st} stripped
Transform:
  m_CorrespondingSourceObject: {{fileID: {MODEL['t']}, guid: {guid}, type: 3}}
  m_PrefabInstance: {{fileID: {inst}}}
  m_PrefabAsset: {{fileID: 0}}
""" + (f"""--- !u!23 &{sr} stripped
MeshRenderer:
  m_CorrespondingSourceObject: {{fileID: {MODEL['renderer']}, guid: {guid}, type: 3}}
  m_PrefabInstance: {{fileID: {inst}}}
  m_PrefabAsset: {{fileID: 0}}
""" if lods else ""))
        stripped_t.append(st)
        renderers.append(sr)
    lod_id = id_of(name, "lodgroup")
    components = f"  - component: {{fileID: {ROOT['t']}}}\n" + (f"  - component: {{fileID: {lod_id}}}\n" if lods else "")
    lod_doc = ""
    if lods:
        levels = "".join(f"""  - screenRelativeHeight: {h:.6f}
    fadeTransitionWidth: 0
    renderers:
    - renderer: {{fileID: {r}}}
""" for h, r in zip(lods["heights"], renderers))
        lod_doc = f"""--- !u!205 &{lod_id}
LODGroup:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {ROOT['go']}}}
  serializedVersion: 2
  m_LocalReferencePoint: {{x: 0, y: 0, z: 0}}
  m_Size: {lods['size']:.6f}
  m_FadeMode: 0
  m_AnimateCrossFading: 0
  m_LastLODIsBillboard: 0
  m_LODs:
{levels}  m_Enabled: 1
"""
    children = "\n".join(f"  - {{fileID: {st}}}" for st in stripped_t)
    return f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &{ROOT['go']}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
{components}  m_Layer: 0
  m_Name: {name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{ROOT['t']}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {ROOT['go']}}}
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children:
{children}
  m_Father: {{fileID: 0}}
  m_RootOrder: 0
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
{lod_doc}""" + "".join(insts)


def material_yaml(template, name, tex_guid, normal_guid, detail_scale=None, detail_guid=None, floats=None):
    """A Canopy material from another's text: its name, color and normal textures replaced,
    its detail textures' tiling set (u, v), or with no detail_scale its detail textures dropped
    (cloth wants no rock grain); with detail_guid, its detail texture that one (a family's own);
    floats ({property: value}, e.g. _Glossiness) set."""
    out, prop = [], None
    for line in template.split("\n"):
        s = line.strip()
        if detail_scale is None and s == "- _DETAIL_MULX2":
            continue
        if s.startswith("m_Name: "):
            line = line[:line.index("m_Name: ")] + "m_Name: " + name
        key = s[2:s.index(":")] if s.startswith("- _") and ": " in s else None
        if floats and key in floats:
            line = line[:line.index("- _")] + f"- {key}: {floats[key]:g}"
        if s.startswith("- _"):
            prop = s[2:].rstrip(":")
        elif prop and prop.startswith("_Detail") and s.startswith("m_Texture: ") and detail_scale is None:
            # before the texture swap below, which would keep a detail texture unchanged
            line = line[:line.index("m_Texture:")] + "m_Texture: {fileID: 0}"
        elif prop and s.startswith("m_Texture: {fileID: 2800000"):
            g = tex_guid if prop == "_MainTex" else normal_guid if prop in ("_BumpMap", "_NormalMap") else detail_guid if prop == "_DetailTex" else None
            if g:
                line = line[:line.index("m_Texture:")] + f"m_Texture: {{fileID: 2800000, guid: {g}, type: 3}}"
        elif prop and prop.startswith("_Detail") and s.startswith("m_Scale: ") and detail_scale is not None:
            line = line[:line.index("m_Scale:")] + f"m_Scale: {{x: {detail_scale[0]:.4f}, y: {detail_scale[1]:.4f}}}"
        out.append(line)
    return "\n".join(out)


def material_guid(family, material):
    """The guid of a family's installed material, for an asset that has one of its own."""
    return guid_of(f"Assets/Modl/{family}/{material}.mat")


def material_files(family, atlas, material, material_text, color_meta_from, normal_meta_from, detail_meta_from=None, detail=None):
    """One material's files in Assets/Modl/<family>/: the atlases <atlas>_tx.png and
    <atlas>_normal.png from obj/ (and, with detail_meta_from, its detail texture
    <detail>_detail.png, detail atlas unless given, so materials can share an atlas but not
    their detail), their metas copied from Canopy textures of the same kind, and
    <material>.mat: material_text(color guid, normal guid[, detail guid])."""
    base = f"Assets/Modl/{family}"
    tex, nrm, det = (f"{base}/{n}_{k}.png" for n, k in ((atlas, "tx"), (atlas, "normal"), (detail or atlas, "detail")))
    mat = f"{base}/{material}.mat"
    read = lambda name: open(os.path.join(HERE, name), "rb").read()
    files = {
        tex: read(atlas + "_tx.png"),
        tex + ".meta": meta_with_guid(canopy_file(color_meta_from + ".meta").decode(), guid_of(tex)),
        nrm: read(atlas + "_normal.png"),
        nrm + ".meta": meta_with_guid(canopy_file(normal_meta_from + ".meta").decode(), guid_of(nrm)),
        mat: material_text(guid_of(tex), guid_of(nrm), *([guid_of(det)] if detail_meta_from else [])),
        mat + ".meta": f"fileFormatVersion: 2\nguid: {guid_of(mat)}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    }
    if detail_meta_from:
        files[det] = read((detail or atlas) + "_detail.png")
        files[det + ".meta"] = meta_with_guid(canopy_file(detail_meta_from + ".meta").decode(), guid_of(det))
    return files


def install_assets(family, material, assets, material_text, color_meta_from, normal_meta_from, detail_meta_from=None, more=()):
    """Installs a family into Canopy's Assets/Modl/<family>/: its atlases from obj/ (with texture
    metas copied from Canopy textures of the same kind), its material (material_text, made with
    material_yaml; see material_files), and each asset's LOD models and prefab. assets: objects
    with name, lods (Meshes), size, heights and optionally material (a guid of its own, e.g.
    material_guid's). more: further materials, each a tuple of material_files' arguments after
    family. Returns the paths changed."""
    base = f"Assets/Modl/{family}"
    mat = f"{base}/{material}.mat"
    obj_meta = canopy_file("Assets/Meshes/Drill/mesh_Cone_5sided.obj.meta").decode()
    # the prefab sets the material; the model brings none of its own
    obj_meta = obj_meta.replace("materialImportMode: 2", "materialImportMode: 0")
    read = lambda name: open(os.path.join(HERE, name), "rb").read()
    files = material_files(family, family, material, material_text, color_meta_from, normal_meta_from, detail_meta_from)
    for m in more:
        files.update(material_files(family, *m))
    for a in assets:
        models = []
        for mesh in a.lods:
            obj = f"{base}/{mesh.name}.obj"
            files[obj] = read(mesh.name + ".obj")
            files[obj + ".meta"] = meta_with_guid(obj_meta, guid_of(obj))
            models.append((mesh.name, guid_of(obj)))
        prefab = f"{base}/{a.name}.prefab"
        files[prefab] = prefab_yaml(a.name, models, getattr(a, "material", None) or guid_of(mat), {"size": a.size, "heights": a.heights})
        files[prefab + ".meta"] = f"fileFormatVersion: 2\nguid: {guid_of(prefab)}\nPrefabImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
    return install(family, files)


def install(family, files):
    """Writes files {relative path: bytes or str} into Assets/Modl/<family>/ in the Canopy
    working tree with folder metas, removing what an earlier run left there that this one did
    not write. Returns the paths written."""
    base = f"Assets/Modl/{family}"
    want = dict(files)
    want["Assets/Modl.meta"] = folder_meta("Assets/Modl")
    want[f"{base}.meta"] = folder_meta(base)
    written = []
    for rel, data in want.items():
        full = os.path.join(CANOPY, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        data = data.encode() if isinstance(data, str) else data
        if not os.path.exists(full) or open(full, "rb").read() != data:
            with open(full, "wb") as f:
                f.write(data)
            written.append(rel)
    folder = os.path.join(CANOPY, base)
    for n in os.listdir(folder):
        if f"{base}/{n}" not in want:
            os.remove(os.path.join(folder, n))
            written.append(f"{base}/{n} (removed)")
    return written
