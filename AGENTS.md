{#include ../canvid/SharedProjects.md}

Asset workspace:
- obj/ holds Wavefront OBJ/MTL outputs, their texture/normal PNG atlases, and the procedural generation scripts used to produce them.
- Keep each atlas next to its .mtl; MTL map_Kd/map_Bump paths resolve relative to the .mtl file.
- Do not scaffold further subfolders under obj/ unless explicitly requested by the user.

Quick context (always load):
- {#include SPEC.md#Overview}

Full-read policy for editing modl:
- Read full ARCH.md for architecture, plugin-load behavior, candidate-view lifecycle, runtime boundaries, or generation/review flow changes.
- Read full SPEC.md for required behavior, tool contracts, failure policy, test/validation expectations, or Implemented tracking changes.
- If scope is unclear or quick context is insufficient, read both full files before editing.

Core rules:
- Make only the requested change.
- Preserve behavior unless the request requires change.
- Keep implementation minimal and practical.
- Keep code Android-compatible with Obsidian mobile.
- Use Obsidian APIs, not Node/Electron APIs.
- Never expose, log, or store API keys outside Obsidian SecretStorage.
- Dependency graph creation must have exactly one implementation path in gptviz; all dependency features must query that shared graph instead of rebuilding parallel graph logic.
- Update SPEC.md Implemented as needed; do not edit Planned unless explicitly requested.

Scripts and build workflow:
- Assume all .sh scripts run from cwd = modl/.
- let's the user run build.sh, not you

Vault visibility constraint:
- The vault has a plugin that allows opening/editing arbitrary extensions.
- It is impossible for you to access anything under .obsidian/

Editing hygiene:
- Prefer narrow replacements/insertions and re-read affected files after multi-step edits.
- Keep declarations/usages consistent and patterns simple/verified.