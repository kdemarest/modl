## Overview

modl: Obsidian plugin for procedural 3D assets.
- Today: a Three.js test view (`Modl: test`) rendering `obj/cube.obj`, and Python model scripts in `obj/` (stdlib only) built on `obj/modl.py`.
- Planned: a modeling language that generates assets in the format below. See `PLAN.md`.
- Three.js: vendor unminified `build/three.js`.

## Model specs and scripts

- A model family's spec is a `# Modl <Name>` section in its file in `docs/models/` (e.g. `Curved Benches.md`), in Ken's words. It is the source of truth; the script follows it.
- Tweakvars: every number Ken may tweak is written in the prose as `{name value unit}`, e.g. `{benchArc 45 deg}`; units m, cm, mm, deg, px/m, or none for counts. Claude adds the tags and names when a spec is first written, Ken's words around them, and tags numbers Claude chose too. The tags hold the values: the script reads them every run (no numbers of its own), and Tweak rewrites only their numbers. A var tagged twice must agree; a var the script declares but the doc does not tag is an error.
- Inputs: the section opens with `Source:` lines, one per file the script reads, as gptviz's `# Extract` has them: a bare name is an image in `vids/` (`Source: Logo Warrior.png`), `Canopy <path>` a file in the Canopy repo. The script refuses to run when it reads an input no Source line declares, so what a model is built from (and what its staleness depends on) is in the docs.
- The script decides how each var is used (`modl.Var`): geometry (reshaped live), textures (redone when a drag ends), or rebuild (new assets or a new stone: a full build, entered as a number). Its limits are in its own units (meters, degrees).
- A family (e.g. the curved benches, one per amphitheater row) is one script, `obj/<family>.py`, with `FAMILY`, `DOC`, `HEADING`, `VARS`, and `tags()`, `values(overrides)`, `assets(values)` (each asset's name, LOD meshes, LODGroup size and screen heights), `textures(values)`, `build(values, install)`; its docstring holds Claude's readings of the spec.
- LODs: a spec's `## LODs` subsection gives each level's error (in pixels where it starts: a pixel is 90 degrees over 1900 px, the Quest 2) and distances. Each level is its own model, `<Name>_LOD<k>.obj`, generated rather than decimated, so normals, UVs, hard edges and textures match at every level; where a level's detail is segments, each level's count is a multiple of the next, so its vertices are a subset of the one above.
- `python3 obj/preview.py obj/<Name>_LOD0.obj [--yaw 30] [--pitch 20]` draws a written model, textured with its family's atlas and smooth-lit, to `<Name>_LOD0_preview.png`: a look at a model without Unity or layout.
- `python3 obj/<family>.py` writes the family into `obj/`; `--write` also installs it into the Canopy working tree (below), where layout shows it and reloads it when it changes.
- Fine detail the player sees up close (inscriptions, slots, bevels) goes in the normal map, optionally darkened in the color map, not in geometry (Ken, 2026-10-26: players accept inscribed things looking flat close up).
- Each spec states its pivot. Textures state their density in pixels per meter, so stone matches stone across assets.

## Budgets

Claude's proposal (2026-11-02), for Ken to revise. A family's models are placed many times (the Hut: in most biomes, several in view, each with its owner's props), and a Quest frame affords well under a million triangles and a couple of hundred draw calls in all. For scale (Ken, 2026-11-02): a whole tree, most of the terrain a player plays on, is about 20,000 triangles, and its leaves 1000 instances of 6. So:
- Triangles at LOD0 by size: under 25 cm, 120 at most; under 1 m, 300; under 2.5 m, 400; larger, 600. An assembly (a hut with its furnishings, before its owner's props) at most 5000 at LOD0, a third of that at LOD1 and a sixth at LOD2; what is drawn far (a hut's disc, roof, posts and perches) at most 400 at LOD2. Each build prints every model's triangles per level.
- Round sections: 16 sides only for things a meter or more across, 8 to 12 smaller, 4 to 6 for rods and legs, 3 for cords. Rows only where the outline curves.
- Ropes and cords: 3-sided tubes, uncapped, one segment a straight run, at most four to a loop or bend; fewer at LOD1 (at most three of a bundle), one or none at LOD2. Twist, lashings and knots go in the normal map, never in geometry.
- Fine detail (carving, weave, grain, cracks, fuzz) is in the normal map and color, as above; geometry carries only the silhouette.
- No faces nobody sees, but things are placed anywhere, any way up (Ken, 2026-11-02: we use them dynamically), so only what can never show its underside loses it: a mat, which lies flat wherever it goes.
- Wrinkles, folds and other cloth detail are normal map, unless geometry for them is nearly free.
- LODs come from each thing's shape (Ken, 2026-11-02): each level keeps what its silhouette needs (rows where the outline bends, sides where it is round, parts big enough to see) and sheds the rest; a build measures each level's error against LOD0 and starts the level where that error is a family's `lodError` pixels, so a poor level shows as a far start.
- One material per family, so its instances batch; small props cull at the family's cull distance.

## Tweak worker

- `python3 obj/serve.py Assets/Modl/<Family>` serves layout's Tweak (layout `unity.json` `tweakWorkers`): one JSON request per stdin line, one reply per stdout line, values in each tag's own unit. Ops: `vars` (the family's assets and vars with value, unit, step, limits and use), `meshes` (every model for these values, each LOD level its own: flat positions, normals, uvs, triangle indices; each asset's LODGroup; and its anchor, where it has one: `{ring}`, its pivot that far from a ring's center along its +Z, so layout keeps it at its angle around a scene's Origin as the ring changes), `textures` (preview atlases' paths), `write` (the values into the doc's tags, then the full build installed). It reloads the family script and `modl.py` when they change.

## Asset format

- Per family `<family>`, in `obj/`: `<name>.obj` for each asset, and one `<family>.mtl`, `<family>_tx.png` (color atlas) and `<family>_normal.png` (normal atlas) they share: one material per family, so they batch and share texture memory. No FBX.
- OBJ holds positions, triangles, normals, UVs only. No tangents; Unity regenerates them. One object per file.
- Unified vertex (position, normal, uv). Duplicate a vertex wherever faces need different normals or UVs, so `f` indices are `i/i/i`.
- OBJ: 1-based, triangulated, order `v`, `vt`, `vn`, `usemtl`, `f`. Right-handed, Y up, meters; Unity's import negates X.
- MTL: `Kd 1 1 1`, `map_Kd <family>_tx.png`, `map_Bump <family>_normal.png`. Map paths are relative to the `.mtl`, so atlases sit beside it.
- Atlases are one of two kinds; color and normal share one layout either way.
  - Island atlas: unique islands. Padding ≥ 8 px between islands and at borders at 1024² (scale with size), with edge dilation. Never rely on GPU wrap inside it: split geometry at repeat boundaries; every tile maps to the same atlas rect.
  - Trim sheet: horizontal bands, each the full width, seamless left to right, padded and dilated above and below. U repeats by GPU wrap (no splitting); a band's V range is fixed.
- UVs: final atlas coordinates; `u` right, `v` up, origin bottom-left; exported unflipped.
- Normal maps: tangent space, R = X+, G = Y+ (up), B = out. Convert Y- sources at import, never in the exporter.
- The exporter only serializes a finished mesh: no packing, UV layout, or repetition logic.

## In Canopy

- `--write` installs a family into `Assets/Modl/<Family>/` in the Canopy working tree, which modl owns and rewrites: each `<Name>.obj` (Unity's model importer), the two atlases (texture importer; the normal atlas as a normal map, U and V repeat), `Modl<Family>.mat` on Canopy/General made from an existing Canopy material the script names (its textures replaced, its detail tiling scaled to the same density), and `<Name>.prefab`: the models nested under an empty root, with the material, and a LODGroup on the root drawing model k as level k. Guids come from file paths, so reruns keep every reference. Never committed; the folder is logged once in `docs/Canopy Changes.md`.
- Colliders are not written yet.

## Shaders

- An asset may use a surface shader instead of (or as well as) atlases: `shaders/<Name>.surf`, a Unity Properties block plus `void surface(SurfIn s, inout SurfOut o)` in the HLSL that GLSL shares. Format and rules: `tools/shaders.js`.
- `node tools/shaders.js` writes `Assets/Shaders/Modl/<Name>.shader` (Canopy/General's lighting and fog around the function) and `Modl<Name>.mat` into the Canopy working tree; it owns that folder. Log the change in `docs/Canopy Changes.md`.
- layout draws the same function from the `.shader` (between its `MODL SURFACE` markers) with matching lighting, so the shader, not a texture, is the asset's look in both.
- Lighting is Canopy's own (one sun, ambient, gloss, fog from `ShaderVars.cs` globals), not Unity's Standard; emission is a surface output added after lighting.
- Object-space surfaces (`s.objPos`) get `DisableBatching`; such meshes must not be marked Static.
