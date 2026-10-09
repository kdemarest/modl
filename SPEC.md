## Overview

modl: Obsidian plugin for procedural 3D assets.
- Today: a Three.js test view (`Modl: test`) rendering `obj/cube.obj`.
- Planned: a modeling language that generates assets in the format below. See `PLAN.md`.
- Three.js: vendor unminified `build/three.js`.

## Asset format

- Per asset `<name>`, in `obj/`: `<name>.obj`, `<name>.mtl`, `<name>_tx.png` (color atlas), `<name>_normal.png` (normal atlas). One material per asset. No FBX.
- OBJ holds positions, triangles, normals, UVs only. No tangents; Unity regenerates them.
- Unified vertex (position, normal, uv). Duplicate a vertex wherever faces need different normals or UVs, so `f` indices are `i/i/i`.
- OBJ: 1-based, triangulated, order `v`, `vt`, `vn`, `usemtl`, `f`.
- MTL: `Kd 1 1 1`, `map_Kd <name>_tx.png`, `map_Bump <name>_normal.png`. Map paths are relative to the `.mtl`, so atlases sit beside it. Unity may override the material.
- Atlases: color and normal share one layout. Padding ≥ 8 px between islands and at borders at 1024² (scale with size), with edge dilation.
- UVs: final atlas coordinates; `u` right, `v` up, origin bottom-left; exported unflipped.
- Normal maps: tangent space, R = X+, G = Y+ (up), B = out. Convert Y- sources at import, never in the exporter.
- The exporter only serializes a finished mesh: no packing, UV layout, or repetition logic.
