{#include ../canvid/SharedProjects.md}

Asset workspace:
- obj/ holds Wavefront OBJ/MTL outputs, their texture/normal PNG atlases, and the procedural generation scripts used to produce them.
- Keep each atlas next to its .mtl; MTL map_Kd/map_Bump paths resolve relative to the .mtl file.
- Do not scaffold further subfolders under obj/ unless explicitly requested by the user.

Quick context (always load):
- {#include SPEC.md#Overview}

Full-read policy for editing modl:
- Read full SPEC.md for scope and asset format; PLAN.md for the planned modeling language.

Core rules:
- Make only the requested change.
- Preserve behavior unless the request requires change.
- Keep implementation minimal and practical.
- Keep code Android-compatible with Obsidian mobile.
- Use Obsidian APIs, not Node/Electron APIs.
- Never expose, log, or store API keys outside Obsidian SecretStorage.
- Code is the source of truth for implemented behavior; do not describe it in docs. Edit PLAN.md only when asked.

Scripts and build workflow:
- Assume all .sh scripts run from cwd = modl/.
- Run build.sh after code changes so the user can test.

Vault visibility constraint:
- The vault has a plugin that allows opening/editing arbitrary extensions.
- It is impossible for you to access anything under .obsidian/

Editing hygiene:
- Prefer narrow replacements/insertions and re-read affected files after multi-step edits.
- Keep declarations/usages consistent and patterns simple/verified.