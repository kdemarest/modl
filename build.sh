#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEST="../.obsidian/plugins/modl"
BUNDLE_PATH="$DEST/main.js"
STAGING_BUNDLE_PATH="assembled-plugin.js"
MAP_PATH="runtime-code-map.json"
BUILD_LOG="${MODL_BUILD_LOG:-build.log}"

: > "$BUILD_LOG"
exec > >(tee -a "$BUILD_LOG") 2>&1
echo "Writing build output to $BUILD_LOG"

THREE_VERSION="0.160.0"
THREE_VENDOR_DIR="./vendor"
THREE_VENDOR_PATH="$THREE_VENDOR_DIR/three.min.js"
THREE_LICENSE_PATH="$THREE_VENDOR_DIR/LICENSE-three.txt"
THREE_MIN_URL="https://unpkg.com/three@${THREE_VERSION}/build/three.min.js"
THREE_LICENSE_URL="https://unpkg.com/three@${THREE_VERSION}/LICENSE"

if ! command -v node >/dev/null 2>&1; then
  echo "Build failed: node not found in PATH." >&2
  exit 1
fi

mkdir -p "$DEST"
mkdir -p "$THREE_VENDOR_DIR"

fetch_file() {
  local URL="$1"
  local OUTPUT_PATH="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" -o "$OUTPUT_PATH"
    return
  fi

  if command -v wget >/dev/null 2>&1; then
    wget -qO "$OUTPUT_PATH" "$URL"
    return
  fi

  echo "Build failed: need curl or wget to fetch $URL" >&2
  exit 1
}

if [ ! -s "$THREE_VENDOR_PATH" ]; then
  echo "Vendoring Three.js r$THREE_VERSION ..."
  fetch_file "$THREE_MIN_URL" "$THREE_VENDOR_PATH"
fi

if [ ! -s "$THREE_LICENSE_PATH" ]; then
  fetch_file "$THREE_LICENSE_URL" "$THREE_LICENSE_PATH"
fi

mapfile -t ROOT_JS_FILES < <(
  find . -maxdepth 1 -type f -name '*.js' \
    ! -name "$(basename "$STAGING_BUNDLE_PATH")" \
    | sort
)

if [ "${#ROOT_JS_FILES[@]}" -eq 0 ]; then
  echo "Build failed: no source .js files found in $(pwd)" >&2
  exit 1
fi

JS_FILES=("$THREE_VENDOR_PATH" "${ROOT_JS_FILES[@]}")

: > "$STAGING_BUNDLE_PATH"
CURRENT_LINE=1
MAP_ENTRIES=""

for FILE in "${JS_FILES[@]}"; do
  SOURCE_LINES=$(awk 'END { print NR + 0 }' "$FILE")
  START_LINE=$CURRENT_LINE

  cat "$FILE" >> "$STAGING_BUNDLE_PATH"
  printf '\n' >> "$STAGING_BUNDLE_PATH"

  if [ "$SOURCE_LINES" -gt 0 ]; then
    END_LINE=$((START_LINE + SOURCE_LINES - 1))
  else
    END_LINE=$START_LINE
  fi

  RELATIVE_FILE=${FILE#./}
  SOURCE_PATH="modl/$RELATIVE_FILE"
  ESCAPED_SOURCE_PATH=$(printf '%s' "$SOURCE_PATH" | sed 's/\\/\\\\/g; s/"/\\"/g')

  ENTRY=$(cat <<EOF
    {
      "sourcePath": "$ESCAPED_SOURCE_PATH",
      "sourceStartLine": 1,
      "bundleStartLine": $START_LINE,
      "bundleEndLine": $END_LINE
    }
EOF
)

  if [ -n "$MAP_ENTRIES" ]; then
    MAP_ENTRIES+=$',\n'
    MAP_ENTRIES+="$ENTRY"
  else
    MAP_ENTRIES="$ENTRY"
  fi

  CURRENT_LINE=$((CURRENT_LINE + SOURCE_LINES + 1))
done

GENERATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$MAP_PATH" <<EOF
{
  "project": "modl",
  "generatedAt": "$GENERATED_AT",
  "bundlePath": ".obsidian/plugins/modl/main.js",
  "entries": [
$MAP_ENTRIES
  ]
}
EOF

if ! node --check "$STAGING_BUNDLE_PATH" >/dev/null; then
  echo "Build failed: syntax check failed for bundled output." >&2
  exit 1
fi

echo "Fast syntax check passed."

SMOKE_SCRIPT="${MODL_SMOKE_SCRIPT:-./smoke.sh}"
if [[ ! -f "$SMOKE_SCRIPT" ]]; then
  echo "Build failed: smoke script not found at $SMOKE_SCRIPT" >&2
  exit 1
fi
bash "$SMOKE_SCRIPT" "$STAGING_BUNDLE_PATH"

echo "Smoke test passed."

cp "$STAGING_BUNDLE_PATH" "$BUNDLE_PATH"

cp manifest.json "$DEST/manifest.json"

# Tell Obsidian Hot Reload to watch this plugin.
touch "$DEST/.hotreload"

echo "Built Modl and wrote $MAP_PATH"