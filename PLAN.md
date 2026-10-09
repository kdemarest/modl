## Principles

- Small set of parameterized primitives plus semantic industrial primitives; geometry, materials, UVs, and transforms generated together.
- Prefer parameters over mesh editing. Reuse general ops (extrude, sweep, loft, revolve, arrays, booleans).
- Add a semantic primitive only when it removes boilerplate or encodes a modeling convention.

## Basic primitives

- `Box(sizeX, sizeY, sizeZ, bevel, bevelSegments, faceMaterials)`
- `Cylinder(radius, height, numSides, cappedTop, cappedBottom, bevelTop, bevelBottom)`
- `Sphere(radius, segments, rings, mode, scaleX, scaleY, scaleZ)`
- `Dome(radius, height, numSides, rings, cutoff, baseCap, edgeBevel)`
- `Cone(radius, height, numSides, capped)`
- `Frustum(bottomRadius, topRadius, height, numSides, cappedTop, cappedBottom)`
- `Capsule(radius, length, numSides, rings)`
- `Ring(outerRadius, innerRadius, thickness, numSides, bevel)`
- `Torus(majorRadius, minorRadius, majorSegments, minorSegments, arc)`
- `Wedge(width, depth, height, slope)`
- `Prism(numSides, radius, length, rotation, capped)`
- `Plate(width, height, thickness, bevel, cornerRadius)`

## Industrial primitives

- `Pipe(length, crossSection = RegularPolygon(sides, outerRadius, innerRadius | wallThickness, rotation), longitudinalBevel, innerBevel, leftEnd = PipeEnd(capped, bevel, collar, collarWidth, collarDepth), rightEnd = PipeEnd(...), bands = [Band(position, width, depth)], lengthSegments, materials = {outer, inner, ends, trim})`
- `Elbow(bendRadius, bendAngle, crossSection, bendSegments, endTreatment)`
- `Junction(type: T|Y|cross, mainRadius, branchRadius, branchAngle, wallThickness, endTreatment)`
- `Tank(radius, height, numSides, top = Dome(...), bottom = Dome(...), bands = [Band(...)], feet = {count, width, height, radialOffset}, topPort, bottomPort, materials)`
- `Shoebox(width, depth, height, wallThickness, bevel, lidHeight, lidOverlap, baseThickness)`
- `Beam(profileType: I|H|C|T|L|box, length, width, height, flangeThickness, webThickness, bevel)`
- `Flange(outerRadius, innerRadius, thickness, numSides, bevel, bolts = {count, radius, circleRadius})`
- `Collar(radius, width, depth, numSides, bevel)`
- `Duct(width, height, length, wallThickness, cornerBevel, endTreatment)`
- `Vent(width, height, depth, frameWidth, insetDepth, grilleType, grilleCount)`
- `Panel(width, height, depth, borderWidth, insetDepth, bevel, cornerRadius)`
- `Grating(width, length, thickness, cellWidth, cellLength, barWidth)`
- `Catwalk(width, length, floorType, thickness, railingLeft, railingRight, supportSpacing)`
- `Railing(path, height, postSpacing, railCount, postRadius, railRadius)`
- `Ladder(width, height, rungSpacing, railRadius, rungRadius)`
- `Stairs(width, rise, run, stepCount, treadThickness, railing)`
- `Truss(length, height, width, segmentCount, memberRadius, pattern)`

## Geometry operations

- `Profile(points, closed, holes, bevel)`; constructors `RegularPolygon`, `Rectangle`, `RoundedRectangle`, `Circle`, `IProfile`, `CProfile`, `LProfile`.
- `Extrude(profile, length, capStart, capEnd)`, `Sweep(profile, path, pathSegments, twist, scaleAlongPath)`, `Loft(profiles, positions, interpolation)`, `Revolve(profile, angle, segments, axis)`, `Shell(shape, thickness, direction)`.
- Operators: `Translate`, `Rotate`, `Scale`, `Bevel`, `Chamfer`, `Union`, `Difference`, `Intersect`, `Mirror`, `Array`, `RadialArray`, `RepeatAlongPath`, `Subdivide`, `Triangulate`, `Weld`.
- Composition: `Transform(position, rotation, scale)`, `Attach(child, parent, anchor, orientation)`, `Group`, `Instance`.

## Surfaces and UV mapping

- UVs are generated from geometry, never from AI. AI makes flat seamless material tiles (+ normal or height maps) only; it never sees topology, projections, or atlases.
- Each primitive names its surface regions (Box: top/bottom/front/back/left/right; Cylinder: side/top/bottom; Pipe: outer/inner/leftEnd/rightEnd/collars/bands; Beam: web/flanges/ends). Common names: outer, inner, top, bottom, ends, trim, bands, feet.
- Per region: `MaterialRegion(name, textureRegion, normalRegion, roughnessRegion)` and `UVMapping {projection, texture, tileSize, repeatU, repeatV, orientation}`, e.g. Pipe.outer = cylindrical, rusty_metal, 0.40 m, mirror U, repeat V.
- Projections: Planar, Cylindrical, Radial, PerFace, Explicit. Later: Box, Triplanar, Spherical.
- Repeat modes: Repeat, MirrorRepeat (alternate tiles reversed, hides repetition), Clamp, Stretch, Fit.
- Physical scale: `u = distanceU / tileSizeU`, `v = distanceV / tileSizeV`, giving uniform texel density across objects. Separate U/V tile sizes allowed.
- Primitives ship overridable defaults (Cylinder.side cylindrical repeat by circumference/height; caps planar/radial fit; Pipe inner/outer cylindrical repeat; ends planar/radial fit).
- Primitives keep semantic orientation (Box forward, Pipe axial vs. circumferential, Beam along length). Controls: `uvRotation`, `flipU`, `flipV`, `swapUV`.
- Never rely on GPU wrap inside an atlas: split geometry at repeat boundaries; every tile maps to the same atlas rect (mirror = reversed U/V on alternate tiles).
- UVs belong to face corners; duplicate vertices where UV, projection, or normal differ.
- Mirrored UVs can flip tangent handedness; color and normal atlases always share UVs.
- Atlas builder: packs source textures (e.g. rusty_metal, bronze) into `<name>_tx.png` / `<name>_normal.png`, assigns `AtlasRegion {u0, v0, u1, v1}`, owns padding. Logical UVs convert to atlas UVs only at final build.

## Pipeline

geometry → surface regions → logical UVs → physical-scale repeat/mirror → split at repeat boundaries → atlas packing → logical-to-atlas UVs → OBJ export.

Deterministic and renderer-independent: the same mesh and UVs must work in the Three.js preview, OBJ export, and Unity.
