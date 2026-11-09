// Makes Unity shaders from modl's surface shaders (shaders/*.surf) and writes them into the Canopy
// working tree:
//   node tools/shaders.js          writes Assets/Shaders/Modl (cwd = modl/)
//   node tools/shaders.js --dry    checks every .surf and lists what it would write
// For each <Name>.surf: <Name>.shader (the surface function lit by Canopy's CanopyLighting.cginc) and
// Modl<Name>.mat (the shader with its default property values; prefixed, as Canopy already has
// materials such as Obsidian.mat, and Shape lines name materials by file), each with a .meta whose guid comes
// from its path, so rerunning keeps references. This script owns the folder: files it no longer
// makes are removed, and a material's values come from the .surf, so tune them there.
//
// A .surf file: // comments, Shader "<name>", a Unity Properties block (Color, Vector, Float,
// Range, Int), then HLSL helper functions and
//   void surface(SurfIn s, inout SurfOut o)
// SurfIn: objPos, objNormal (the mesh's own space, as Unity imported it), worldPos, worldNormal,
// viewDir (surface to camera, normalized), uv, time (seconds). SurfOut, with its defaults:
// albedo (1, 1, 1), emission (0, added after lighting), gloss (0, Canopy/General's _Glossiness:
// how tight the sun's highlight is), specular (0.2, General's: how bright it is), normal
// (s.worldNormal; lighting uses it), alpha (1). ObjectToWorldNormal(n) turns an object-space
// normal into a world one, e.g. a sphere's normal from s.objPos to round off a faceted mesh.
// layout (layout/web/surface.js) draws the same function as GLSL, read from the .shader between
// the MODL SURFACE markers, so it keeps to what both languages share: write float literals with a
// point (1.0, never 1), no mul(), textures, semantics, static or #directives. Each shader is
// compiled (glslangValidator, pkg glslang) against stand-ins for UnityCG.cginc, with the Canopy
// tree's CanopyLighting.cginc, before anything is written; layout's tools/shader-check.js checks
// them against Unity's own include files.
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const SOURCES = path.join(__dirname, '..', 'shaders');
const REPO = '/sdcard/Canopy';
const DIR = 'Assets/Shaders/Modl';

const guidOf = file => crypto.createHash('md5').update('canopy-modl:' + file).digest('hex');
const uniformType = { Color: 'float4', Vector: 'float4', Float: 'float', Range: 'float', Int: 'float' };

// "<text>" of a .surf -> { name, comments, properties: [{ name, label, type, range, value, line }], code }.
function parse(text, file) {
  text = text.replace(/\r\n/g, '\n');
  const fail = message => { throw new Error(`${file}: ${message}`); };
  const comments = (/^(?:\s*\/\/.*\n)*/.exec(text)[0]).trim();
  const name = (/^\s*Shader\s+"([^"]+)"/m.exec(text) || fail('needs Shader "<name>"'))[1];
  const open = /^\s*Properties\s*\{/m.exec(text) || fail('needs a Properties { } block');
  const close = text.indexOf('}', open.index + open[0].length);
  if (close < 0) fail('Properties block is not closed');
  const properties = [];
  for (const raw of text.slice(open.index + open[0].length, close).split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('//')) continue;
    const m = /^(_\w+)\s*\(\s*"([^"]*)"\s*,\s*(Color|Vector|Float|Int|Range\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\))\s*\)\s*=\s*(.+)$/.exec(line);
    if (!m) fail(`can't read property "${line}"; use _Name ("Label", Color|Vector|Float|Range(a, b)|Int) = value`);
    const type = m[3].startsWith('Range') ? 'Range' : m[3];
    const value = /^\(.*\)$/.test(m[6]) ? m[6].slice(1, -1).split(',').map(Number) : [Number(m[6])];
    if (value.some(v => !Number.isFinite(v)) || value.length !== (uniformType[type] === 'float4' ? 4 : 1)) fail(`${m[1]}: bad default ${m[6]}`);
    properties.push({ name: m[1], label: m[2], type, range: type === 'Range' ? [+m[4], +m[5]] : null, value, line });
  }
  const code = text.slice(close + 1).replace(/^\s*\n/, '').replace(/\s+$/, '') + '\n';
  lint(code, fail);
  return { name, comments, properties, code };
}

// The rules that keep surface code valid as both HLSL and GLSL (see the header).
function lint(code, fail) {
  if (!/\bvoid\s+surface\s*\(\s*SurfIn\s+s\s*,\s*inout\s+SurfOut\s+o\s*\)/.test(code)) fail('needs void surface(SurfIn s, inout SurfOut o)');
  code.replace(/\/\*[\s\S]*?\*\//g, '').split('\n').forEach((raw, i) => {
    const line = raw.replace(/\/\/.*/, '');
    const bad = [
      [/(?<![\w.])\d+(?![\w.])/, 'an integer literal; write it with a point (1.0), GLSL never converts'],
      [/\bmul\s*\(/, 'mul()'],
      [/\btex\w*\s*\(|\bsampler/, 'a texture'],
      [/\bstatic\b/, 'static'],
      [/^\s*#/, 'a # directive'],
      [/:\s*(SV_\w+|TEXCOORD\d*|POSITION|NORMAL|COLOR\d*)\b/, 'a semantic']
    ].find(([re]) => re.test(line));
    if (bad) fail(`surface code line ${i + 1}: ${bad[1]}: ${raw.trim()}`);
  });
}

function shader(s, source) {
  const tabs = (n, text) => text.replace(/^(?=.)/gm, '\t'.repeat(n));
  // Object space doesn't survive batching (it bakes vertices into world space).
  const objectSpace = /\bs\.obj(Pos|Normal)\b/.test(s.code);
  const tags = `"RenderType"="Opaque" "Queue"="Geometry"${objectSpace ? ' "DisableBatching"="True"' : ''}`;
  return `// Generated by modl/tools/shaders.js from modl/shaders/${source}; edit that and rerun it.
${s.comments}
Shader "${s.name}"
{
	Properties
	{
${s.properties.map(p => '\t\t' + p.line).join('\n')}
	}

	SubShader
	{
		Tags { ${tags} }
		LOD 100
		Cull Back
		ZWrite On
		// no ShadowCaster pass => won't cast shadows

		Pass
		{
			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#pragma target 3.0

			#include "UnityCG.cginc"
			#include "../CanopyLighting.cginc"

${s.properties.map(p => `\t\t\t${uniformType[p.type]} ${p.name};`).join('\n')}

			struct SurfIn
			{
				float3 objPos;
				float3 objNormal;
				float3 worldPos;
				float3 worldNormal;
				float3 viewDir;
				float2 uv;
				float  time;
			};
			struct SurfOut
			{
				float3 albedo;
				float3 emission;
				float  gloss;
				float  specular;
				float3 normal;
				float  alpha;
			};
			float3 ObjectToWorldNormal(float3 n) { return UnityObjectToWorldNormal(n); }

			// MODL SURFACE BEGIN
${tabs(3, s.code)}			// MODL SURFACE END

			// Canopy's lighting (CanopyLighting.cginc: one sun, ambient, General's highlight, the
			// darkening below the sea before it, exp2 fog after), plus the surface's emission, which the
			// sun and darkening leave alone. layout/web/surface.js has the same in GLSL.
			float4 ModlLight(SurfIn s, SurfOut o)
			{
				CanopySurface c;
				c.albedo = CanopyDim(o.albedo, s.worldPos);
				c.normal = normalize(o.normal);
				c.gloss = o.gloss;
				c.specular = o.specular;
				c.emission = o.emission;
				c.worldPos = s.worldPos;
				float3 d = _WorldSpaceCameraPos - s.worldPos;
				return float4(CanopyFog(CanopyLight(c), s.worldPos, dot(d, d), 1), o.alpha);
			}

			struct appdata
			{
				float4 vertex : POSITION;
				float3 normal : NORMAL;
				float2 uv     : TEXCOORD0;
				UNITY_VERTEX_INPUT_INSTANCE_ID
			};

			struct v2f
			{
				float4 pos       : SV_POSITION;
				float3 objPos    : TEXCOORD0;
				float3 objNormal : TEXCOORD1;
				float3 wPos      : TEXCOORD2;
				float3 wNormal   : TEXCOORD3;
				float2 uv        : TEXCOORD4;
				UNITY_VERTEX_OUTPUT_STEREO // Multiview: both eyes in one pass
			};

			v2f vert(appdata v)
			{
				v2f o;
				UNITY_SETUP_INSTANCE_ID(v);
				UNITY_INITIALIZE_OUTPUT(v2f, o);
				UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
				o.pos = UnityObjectToClipPos(v.vertex);
				o.objPos = v.vertex.xyz;
				o.objNormal = v.normal;
				o.wPos = mul(unity_ObjectToWorld, v.vertex).xyz;
				o.wNormal = UnityObjectToWorldNormal(v.normal);
				o.uv = v.uv;
				return o;
			}

			float4 frag(v2f i) : SV_Target
			{
				SurfIn s;
				s.objPos = i.objPos;
				s.objNormal = normalize(i.objNormal);
				s.worldPos = i.wPos;
				s.worldNormal = normalize(i.wNormal);
				s.viewDir = normalize(_WorldSpaceCameraPos - i.wPos);
				s.uv = i.uv;
				s.time = _Time.y;
				SurfOut o;
				o.albedo = float3(1, 1, 1);
				o.emission = float3(0, 0, 0);
				o.gloss = 0;
				o.specular = 0.2;
				o.normal = s.worldNormal;
				o.alpha = 1;
				surface(s, o);
				return ModlLight(s, o);
			}
			ENDCG
		}
	}

	// no fallback (keep it lean)
}
`;
}

// Compiles a generated shader's vertex and fragment programs as HLSL; throws with the errors.
const UNITY_CG = `float4x4 unity_ObjectToWorld; float4x4 UNITY_MATRIX_VP; float3 _WorldSpaceCameraPos; float4 _Time; float4 UNITY_LIGHTMODEL_AMBIENT;
float4 UnityObjectToClipPos(float4 v) { return mul(UNITY_MATRIX_VP, mul(unity_ObjectToWorld, v)); }
float3 UnityObjectToWorldNormal(float3 n) { return normalize(mul((float3x3)unity_ObjectToWorld, n)); }
#define UNITY_VERTEX_INPUT_INSTANCE_ID
#define UNITY_VERTEX_OUTPUT_STEREO
#define UNITY_SETUP_INSTANCE_ID(v)
#define UNITY_INITIALIZE_OUTPUT(type, o) o = (type)0;
#define UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o)
// instancing (Canopy's lights keep each renderer's slots in an instanced property: CanopyLighting.cginc;
// Claude, 2026-11-09: without these every modl shader stopped compiling here)
#define UNITY_INSTANCING_BUFFER_START(name) cbuffer name {
#define UNITY_DEFINE_INSTANCED_PROP(type, var) type var;
#define UNITY_INSTANCING_BUFFER_END(name) };
#define UNITY_ACCESS_INSTANCED_PROP(buffer, var) var`;
function compile(text, label) {
  const program = /CGPROGRAM([\s\S]*?)ENDCG/.exec(text)[1].replace(/^\s*#pragma.*$/gm, '').replace('#include "UnityCG.cginc"', UNITY_CG);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'modl-shader-'));
  try {
    fs.writeFileSync(path.join(dir, 'shader.hlsl'), program);
    for (const stage of ['vert', 'frag']) {
      try {
        execFileSync('glslangValidator', ['-V', '-D', '-e', stage, '-S', stage, '-I' + path.join(REPO, 'Assets', 'Shaders', 'Modl'), 'shader.hlsl', '-o', stage + '.spv'], { cwd: dir, stdio: 'pipe' });
      } catch (error) {
        const out = String(error.stdout || '') + String(error.stderr || '') || error.message;
        throw new Error(`${label} (${stage}) doesn't compile:\n${out.split('\n').filter(l => /ERROR|error/.test(l)).join('\n') || out}`, { cause: error });
      }
    }
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

const n6 = x => +(+x).toFixed(6) || 0;
function material(name, shaderGuid, properties) {
  const sorted = list => [...list].sort((a, b) => (a.name < b.name ? -1 : 1));
  const floats = sorted(properties.filter(p => uniformType[p.type] === 'float')).map(p => `    - ${p.name}: ${n6(p.value[0])}`);
  const colors = sorted(properties.filter(p => uniformType[p.type] === 'float4')).map(p => `    - ${p.name}: {r: ${n6(p.value[0])}, g: ${n6(p.value[1])}, b: ${n6(p.value[2])}, a: ${n6(p.value[3])}}`);
  const list = lines => (lines.length ? '\n' + lines.join('\n') : ' []');
  return `%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!21 &2100000
Material:
  serializedVersion: 6
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: ${name}
  m_Shader: {fileID: 4800000, guid: ${shaderGuid}, type: 3}
  m_ShaderKeywords:
  m_LightmapFlags: 4
  m_EnableInstancingVariants: 0
  m_DoubleSidedGI: 0
  m_CustomRenderQueue: -1
  stringTagMap: {}
  disabledShaderPasses: []
  m_SavedProperties:
    serializedVersion: 3
    m_TexEnvs: []
    m_Floats:${list(floats)}
    m_Colors:${list(colors)}
`;
}

const tail = '  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n';
const meta = (file, importer) => `fileFormatVersion: 2\nguid: ${guidOf(file)}\n${importer}\n${tail}`;

// Every file to write, by path under the Unity project.
function plan() {
  const files = {};
  files[DIR + '.meta'] = meta(DIR, 'folderAsset: yes\nDefaultImporter:');
  for (const source of fs.readdirSync(SOURCES).filter(f => f.endsWith('.surf')).sort()) {
    const s = parse(fs.readFileSync(path.join(SOURCES, source), 'utf8'), source);
    const base = path.basename(source, '.surf');
    const shaderFile = `${DIR}/${base}.shader`, matFile = `${DIR}/Modl${base}.mat`;
    files[shaderFile] = shader(s, source);
    compile(files[shaderFile], source);
    files[shaderFile + '.meta'] = meta(shaderFile, 'ShaderImporter:\n  defaultTextures: []\n  nonModifiableTextures: []');
    files[matFile] = material('Modl' + base, guidOf(shaderFile), s.properties);
    files[matFile + '.meta'] = meta(matFile, 'NativeFormatImporter:\n  mainObjectFileID: 2100000');
  }
  return files;
}

if (require.main === module) {
  const files = plan();
  if (process.argv.includes('--dry')) {
    for (const f of Object.keys(files)) console.log(f);
    process.exit(0);
  }
  const keep = new Set(Object.keys(files));
  const dir = path.join(REPO, DIR);
  fs.mkdirSync(dir, { recursive: true });
  for (const f of fs.readdirSync(dir)) {
    if (!keep.has(`${DIR}/${f}`)) {
      fs.rmSync(path.join(dir, f), { recursive: true });
      console.log('removed ' + `${DIR}/${f}`);
    }
  }
  let changed = 0;
  for (const [file, text] of Object.entries(files)) {
    const full = path.join(REPO, file);
    if (fs.existsSync(full) && fs.readFileSync(full, 'utf8') === text) continue;
    fs.writeFileSync(full, text);
    console.log('wrote ' + file);
    changed++;
  }
  console.log(`${keep.size} files in ${path.join(REPO, DIR)}, ${changed} changed`);
}

module.exports = { parse, shader, compile, plan };
