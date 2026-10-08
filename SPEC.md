# Procedural Modeling Design Outline

## Core Principles

* Small set of reusable geometric primitives.
* Higher-level semantic primitives for common industrial forms.
* Geometry, materials, UVs, and transforms generated together.
* Prefer parameterization over manual mesh editing.
* Reuse generalized operations such as extrusion, sweep, loft, revolve, arrays, and booleans.

---

## Basic Primitives

### Box

```text
Box(
    sizeX,
    sizeY,
    sizeZ,
    bevel,
    bevelSegments,
    faceMaterials
)
```

### Cylinder

```text
Cylinder(
    radius,
    height,
    numSides,
    cappedTop,
    cappedBottom,
    bevelTop,
    bevelBottom
)
```

### Sphere

```text
Sphere(
    radius,
    segments,
    rings,
    mode,
    scaleX,
    scaleY,
    scaleZ
)
```

### Dome

```text
Dome(
    radius,
    height,
    numSides,
    rings,
    cutoff,
    baseCap,
    edgeBevel
)
```

### Cone

```text
Cone(
    radius,
    height,
    numSides,
    capped
)
```

### Frustum

```text
Frustum(
    bottomRadius,
    topRadius,
    height,
    numSides,
    cappedTop,
    cappedBottom
)
```

### Capsule

```text
Capsule(
    radius,
    length,
    numSides,
    rings
)
```

### Ring / Annulus

```text
Ring(
    outerRadius,
    innerRadius,
    thickness,
    numSides,
    bevel
)
```

### Torus

```text
Torus(
    majorRadius,
    minorRadius,
    majorSegments,
    minorSegments,
    arc
)
```

### Wedge

```text
Wedge(
    width,
    depth,
    height,
    slope
)
```

### Prism

```text
Prism(
    numSides,
    radius,
    length,
    rotation,
    capped
)
```

### Plate

```text
Plate(
    width,
    height,
    thickness,
    bevel,
    cornerRadius
)
```

---

## Compound Industrial Primitives

### Pipe

```text
Pipe(
    length,

    crossSection = RegularPolygon(
        sides,
        outerRadius,
        innerRadius | wallThickness,
        rotation
    ),

    longitudinalBevel,
    innerBevel,

    leftEnd = PipeEnd(
        capped,
        bevel,
        collar,
        collarWidth,
        collarDepth
    ),

    rightEnd = PipeEnd(...),

    bands = [
        Band(position, width, depth)
    ],

    lengthSegments,

    materials = {
        outer,
        inner,
        ends,
        trim
    }
)
```

### Elbow

```text
Elbow(
    bendRadius,
    bendAngle,
    crossSection,
    bendSegments,
    endTreatment
)
```

### Junction

```text
Junction(
    type,           # T, Y, cross
    mainRadius,
    branchRadius,
    branchAngle,
    wallThickness,
    endTreatment
)
```

### Tank

```text
Tank(
    radius,
    height,
    numSides,

    top = Dome(...),
    bottom = Dome(...),

    bands = [
        Band(position, width, depth)
    ],

    feet = {
        count,
        width,
        height,
        radialOffset
    },

    topPort,
    bottomPort,

    materials
)
```

### Shoebox

```text
Shoebox(
    width,
    depth,
    height,
    wallThickness,
    bevel,
    lidHeight,
    lidOverlap,
    baseThickness
)
```

### Beam

```text
Beam(
    profileType,    # I, H, C, T, L, box
    length,
    width,
    height,
    flangeThickness,
    webThickness,
    bevel
)
```

### Flange

```text
Flange(
    outerRadius,
    innerRadius,
    thickness,
    numSides,
    bevel,

    bolts = {
        count,
        radius,
        circleRadius
    }
)
```

### Collar

```text
Collar(
    radius,
    width,
    depth,
    numSides,
    bevel
)
```

### Duct

```text
Duct(
    width,
    height,
    length,
    wallThickness,
    cornerBevel,
    endTreatment
)
```

### Vent

```text
Vent(
    width,
    height,
    depth,
    frameWidth,
    insetDepth,
    grilleType,
    grilleCount
)
```

### Panel

```text
Panel(
    width,
    height,
    depth,
    borderWidth,
    insetDepth,
    bevel,
    cornerRadius
)
```

### Grating

```text
Grating(
    width,
    length,
    thickness,
    cellWidth,
    cellLength,
    barWidth
)
```

### Catwalk

```text
Catwalk(
    width,
    length,
    floorType,
    thickness,

    railingLeft,
    railingRight,

    supportSpacing
)
```

### Railing

```text
Railing(
    path,
    height,
    postSpacing,
    railCount,
    postRadius,
    railRadius
)
```

### Ladder

```text
Ladder(
    width,
    height,
    rungSpacing,
    railRadius,
    rungRadius
)
```

### Stairs

```text
Stairs(
    width,
    rise,
    run,
    stepCount,
    treadThickness,
    railing
)
```

### Truss

```text
Truss(
    length,
    height,
    width,
    segmentCount,
    memberRadius,
    pattern
)
```

---

## Generalized Geometry Operations

### Profile

```text
Profile(
    points,
    closed,
    holes,
    bevel
)
```

Common profile constructors:

```text
RegularPolygon(...)
Rectangle(...)
RoundedRectangle(...)
Circle(...)
IProfile(...)
CProfile(...)
LProfile(...)
```

### Extrude

```text
Extrude(
    profile,
    length,
    capStart,
    capEnd
)
```

### Sweep

```text
Sweep(
    profile,
    path,
    pathSegments,
    twist,
    scaleAlongPath
)
```

### Loft

```text
Loft(
    profiles,
    positions,
    interpolation
)
```

### Revolve

```text
Revolve(
    profile,
    angle,
    segments,
    axis
)
```

### Shell

```text
Shell(
    shape,
    thickness,
    direction
)
```

---

## Geometry Operators

```text
Translate(...)
Rotate(...)
Scale(...)

Bevel(...)
Chamfer(...)

Union(...)
Difference(...)
Intersect(...)

Mirror(...)
Array(...)
RadialArray(...)
RepeatAlongPath(...)

Subdivide(...)
Triangulate(...)
Weld(...)
```

---

## Placement and Composition

```text
Transform(
    position,
    rotation,
    scale
)

Attach(
    child,
    parent,
    anchor,
    orientation
)

Group(...)
Instance(...)
```

---

## Surface / UV Assignment

```text
MaterialRegion(
    name,
    textureRegion,
    normalRegion,
    roughnessRegion
)

UVMode(
    planar,
    cylindrical,
    radial,
    perFace,
    explicit
)
```

Generated primitives should support assigning different material regions to logical surfaces:

```text
outer
inner
top
bottom
ends
trim
bands
feet
```

---

## Design Rule

Use low-level primitives and generalized operators as the foundation.

Add semantic primitives such as `Pipe`, `Tank`, `Beam`, and `Catwalk` when they remove repeated boilerplate or encode useful modeling conventions.


# OBJ Export Format

## Purpose

Use **Wavefront OBJ** as the generated mesh format for procedural assets.

OBJ is sufficient because assets currently require only:

- positions
- triangles
- normals
- UVs
- one color texture atlas
- one normal-map atlas

Do not generate FBX.

---

## Output Files

For an asset named `stronghold`:

```text
stronghold.obj
stronghold.mtl
stronghold_tx.png
stronghold_normal.png
```

Use one material per exported asset unless explicitly required otherwise.

---

## Internal Mesh Representation

Prefer a unified vertex representation:

```text
Vertex {
    position: vec3
    normal: vec3
    uv: vec2
}

Mesh {
    vertices[]
    triangles[]
}
```

If two faces need different normals or UVs at the same geometric position, duplicate the vertex.

This allows OBJ position, UV, and normal indices to remain identical.

---

## OBJ Layout

```obj
mtllib stronghold.mtl
o Stronghold

v x y z
v x y z
...

vt u v
vt u v
...

vn x y z
vn x y z
...

usemtl StrongholdMaterial

f 1/1/1 2/2/2 3/3/3
...
```

Rules:

* OBJ indices are **1-based**.
* Triangulate all geometry before export.
* Emit vertices first, then UVs, then normals, then faces.
* Use `positionIndex/uvIndex/normalIndex`.
* With unified vertices, all three indices should normally be identical.

Example:

```text
vertex index 17
→ OBJ index 18
→ 18/18/18
```

---

## MTL Layout

```mtl
newmtl StrongholdMaterial

Kd 1.0 1.0 1.0
map_Kd stronghold_tx.png
map_Bump stronghold_normal.png
```

`map_Kd` references the color texture.

`map_Bump` may reference the normal map for compatibility naming, but do not rely on MTL normal-map semantics for Unity shader configuration.

Unity-side material/shader setup may override the imported material.

---

## Texture Rules

Use exactly two generated texture atlases unless requirements change:

```text
*_tx.png
*_normal.png
```

Both must use identical atlas layouts.

Example:

```text
tank_side
tank_top
pipe_side
pipe_end
beam_side
...
```

The same atlas rectangle must correspond between color and normal maps.

Atlas seam safety rules (for mipmaps in Unity and three.js):

* Keep padding between UV islands.
* Keep outer border padding around atlas edges.
* Dilate (edge-bleed) each island color/normal texels outward into padding.

Minimum padding guideline:

* At 1024x1024 atlas size, use at least 8 px island padding and 8 px outer border.
* Scale proportionally for other resolutions (for example 4 px at 512, 16 px at 2048).

---

## UV Rules

UVs must already reference final atlas coordinates before OBJ export.

UV coordinate convention is explicit:

* Use standard OBJ UV orientation: `(u, v)` where `u` increases to the right and `v` increases upward.
* Treat `(0,0)` as the lower-left of the texture address space and `(1,1)` as upper-right.
* Export UVs exactly as authored; the OBJ exporter must not flip `v`.
* Runtime importers should preserve this convention (Unity default UV handling; three.js with normal `TextureLoader` flow).

The OBJ writer must not:

* pack textures
* understand model components
* generate UV layouts
* perform texture repetition logic

Those belong to the procedural geometry / atlas-generation layer.

If a texture repeats once per polygon, emit the same atlas UV rectangle for each polygon.

If multiple repetitions are required across a surface, subdivide the surface at repetition boundaries.

---

## Normal Maps

OBJ does not store tangents.

Do not export tangent data.

Tangents should be generated later by Unity from:

```text
positions
normals
UVs
```

Normal maps must use a single explicit tangent-space convention:

* `R` = `X+` (right)
* `G` = `Y+` (up)
* `B` = `Z+` (out of surface)

This matches Unity's default Y+ expectation and is directly compatible with three.js tangent-space normal mapping.

If external assets use opposite green-channel convention (`Y-`), convert at import time (for example, Flip Green in Unity) rather than changing exporter semantics.

---

## Exporter Responsibility

The OBJ exporter should only serialize an already-complete mesh:

```text
Procedural geometry
        ↓
positions
normals
UVs
triangles
        ↓
OBJ exporter
```

Keep the exporter simple and deterministic.

````markdown
# Procedural UV Mapping Design

## Goal

UV mapping must be generated automatically from procedural geometry.

Do not require AI image generation to understand mesh topology or UV layouts.

AI-generated textures should normally be simple flat seamless material tiles. Procedural geometry is responsible for:

- surface classification
- projection direction
- texel density
- repetition
- mirrored repetition
- UV seams
- atlas placement

---

## Core Principle

Every primitive knows its own semantic surface regions.

Examples:

```text
Box:
  top
  bottom
  front
  back
  left
  right

Cylinder:
  side
  top
  bottom

Pipe:
  outer
  inner
  leftEnd
  rightEnd
  collars
  bands

Beam:
  web
  flanges
  ends
````

Each region receives an explicit UV mapping policy.

---

## Mapping Definition

Conceptually:

```text
UVMapping {
    projection
    texture
    tileSize
    repeatU
    repeatV
    orientation
}
```

Example:

```text
outer:
    projection = cylindrical
    texture = rusty_metal
    tileSize = 0.40m
    repeatU = mirror
    repeatV = repeat
```

---

## UV Coordinate Space

Generate UVs first in logical/local texture space.

Prefer physical scale:

```text
u = surfaceDistanceU / tileSizeU
v = surfaceDistanceV / tileSizeV
```

This gives consistent texel density automatically.

A 1-meter surface should receive approximately the same texture density regardless of which object owns it.

Do not generate final atlas UV coordinates during the first mapping step.

---

## Supported Projection Modes

```text
Planar
Cylindrical
Radial
PerFace
Explicit
```

Possible later additions:

```text
BoxProjection
Triplanar
Spherical
```

---

## Texture Repeat Modes

Support at minimum:

```text
Repeat
MirrorRepeat
Clamp
Stretch
Fit
```

### Repeat

```text
tile 0: 0 → 1
tile 1: 0 → 1
tile 2: 0 → 1
```

### MirrorRepeat

```text
tile 0: 0 → 1
tile 1: 1 → 0
tile 2: 0 → 1
tile 3: 1 → 0
```

Mirror repetition is useful for reducing obvious visual repetition.

---

## Atlas Interaction

Source textures remain independent during authoring.

Example:

```text
rusty_metal.png
bronze.png
pipe_inner.png
rock.png
```

The build stage packs them into:

```text
stronghold_tx.png
stronghold_normal.png
```

Both atlases must use identical layouts.

Each source texture receives an atlas rectangle:

```text
AtlasRegion {
    u0
    v0
    u1
    v1
}
```

Logical UVs are converted into atlas UVs only during the final build.

---

## Repetition Inside an Atlas

Do not depend on GPU texture wrapping across the full atlas.

If a surface requires multiple repetitions, divide the geometry at texture repetition boundaries.

Example:

```text
Bad:

+-------------------------+
| one polygon, 5 repeats  |
+-------------------------+

Preferred:

+----+----+----+----+----+
| t  | t  | t  | t  | t  |
+----+----+----+----+----+
```

Each polygon references the same atlas rectangle.

For mirrored repetition, reverse the U or V direction on alternating tiles.

---

## UV Seams

UVs belong to face corners, not uniquely to geometric positions.

If adjacent faces need different:

* UV coordinates
* projection directions
* normal directions

duplicate the exported vertex as needed.

Unified exported vertex:

```text
Vertex {
    position
    normal
    uv
}
```

---

## Primitive Responsibilities

Each primitive should define sensible default mappings.

Example:

```text
Cylinder.side:
    cylindrical
    repeat according to physical circumference and height

Cylinder.top:
    planar/radial
    normally fit or clamp

Pipe.outer:
    cylindrical
    repeat

Pipe.inner:
    cylindrical
    repeat

Pipe.ends:
    planar/radial
    usually fit
```

Defaults should be overridable.

---

## Orientation

Procedural primitives must preserve semantic orientation.

Examples:

* Box top texture should know which direction is "forward".
* Pipe side mapping should know axial and circumferential directions.
* Beam web and flange textures should align consistently along beam length.

Expose optional rotation/orientation controls:

```text
uvRotation
flipU
flipV
swapUV
```

---

## Texel Density

Prefer world-space texture scale over arbitrary UV scaling.

Example:

```text
tileSize = 0.5m
```

means one full texture tile covers approximately 0.5 meters.

Allow separate axes when needed:

```text
tileSizeU
tileSizeV
```

---

## Normal Maps

Color and normal atlases must use exactly the same UV mapping.

Mirrored UVs can change tangent handedness.

Do not store tangents in OBJ.

Unity should regenerate tangents from:

```text
positions
normals
UVs
```

The pipeline must use one consistent tangent-space normal-map convention.

---

## Atlas Padding

Every atlas region must include padding to prevent texture bleeding under:

* bilinear filtering
* trilinear filtering
* mipmaps

Padding generation belongs to the atlas builder.

---

## AI Texture Generation

AI should primarily generate:

* seamless square material textures
* matching normal maps or height-derived normal maps
* flat reusable surface materials

Examples:

```text
painted rusty steel
dark oxidized bronze
scratched industrial steel
weathered rock
```

AI should not be expected to:

* understand final UV topology
* paint directly onto arbitrary meshes
* determine projection directions
* manage atlas placement

---

## Recommended Processing Pipeline

```text
Procedural geometry
        ↓
Semantic surface regions
        ↓
Logical UV generation
        ↓
Physical-scale repeat / mirror-repeat
        ↓
Subdivision at repetition boundaries
        ↓
Texture atlas packing
        ↓
Logical UV → atlas UV conversion
        ↓
OBJ export
```

---

## Design Requirement

UV generation must be deterministic and independent of the renderer.

The same generated mesh and UVs must work in:

* WebView / Three.js preview
* OBJ export
* Unity
