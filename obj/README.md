## obj directory

This folder is the 3D asset workspace for the Modl pipeline.

Store these artifact types here:

- Wavefront OBJ meshes (`*.obj`)
- Material files (`*.mtl`)
- Texture atlases (`*_tx.png`)
- Normal-map atlases (`*_normal.png`)
- Procedural generation scripts that describe how to build geometry and maps

Purpose:

- Keep generated/model artifacts separate from plugin code projects.
- Keep 3D build inputs and outputs together in one predictable location.
- Support procedural regeneration of objects, textures, and normals from scripts.

Layout:

- Keep OBJ, MTL, PNG atlases, and the scripts that generate them together in obj/.
- MTL `map_Kd`/`map_Bump` paths resolve relative to the .mtl, so atlases sit beside it.
