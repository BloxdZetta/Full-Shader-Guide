# Bloxd Shader Packs — The Complete Guide (English)

🌐 [All languages](README.md) · [Français](GUIDE-FR.md)

**Everything known about Bloxd.io shader packs, explained as simply as possible:**
how the web renderer draws the picture, how shaders work, what a pack can do,
what it cannot do, and how to build one — backed by measured engine data,
a full numeric block-id table, dissected community packs, and local validation
in all 8 engine variants.

**One file, everything inside.** Use the contents below — or GitHub's outline (the ≡ button) — to jump straight to a part.

> **Scope: shader-pack API v2.** This edition describes packs whose manifest says `apiVersion: 2`, running through the current WebGPU/Lite terrain path. A future API version is a new contract until the importer and renderer actually accept it: never change `apiVersion` speculatively, and keep version-dependent code isolated so a migration touches a small surface.

## Contents

- [Part 0 — Start from zero: how rendering and Bloxd shaders work](#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work)
- [Part I — Making a pack](#part-i--making-a-pack)
- [Part II — The API contract](#part-ii--the-api-contract)
- [Part III — Recipes](#part-iii--recipes)
- [Part IV — Measured numbers (realism that survives contact with the game)](#part-iv--measured-numbers-realism-that-survives-contact-with-the-game)
- [Part V — Troubleshooting](#part-v--troubleshooting)
- [Part VI — Implementation & local validation](#part-vi--implementation--local-validation)
- [Part VII — Engine internals](#part-vii--engine-internals)
- [Part VIII — The numeric block-id table](#part-viii--the-numeric-block-id-table)
- [Part IX — Where this knowledge comes from (and what we don't know)](#part-ix--where-this-knowledge-comes-from-and-what-we-dont-know)
- [Part X — The constants register (EN)](#part-x--the-constants-register-en)


---

# Part 0 — Start from zero: how rendering and Bloxd shaders work

**Read this first.** No experience needed. In ten minutes you will know how the game draws
its picture, what a shader is, and exactly what a shader pack can and cannot do.
The deep chapters (Parts I–X) come after.

## 1. The one-minute version

- Bloxd.io is a voxel game: the world is made of cubes (blocks).
- The picture on your screen is drawn by your graphics card (GPU), 60 or more times per second.
- A **shader** is a tiny program that runs on the GPU and decides the colour of pixels.
- A **shader pack** is a folder or small `.zip` with shader code. The game imports it and lets
  your code recolour **blocks, water and lava** while they are drawn — and, only in
  allow-policy games, move their corners.
- You do not change the game. Mostly you change colours and light at the exact moment each
  pixel is drawn; vertex hooks are the one optional, policy-gated exception.

## 2. How the picture is drawn (web rendering, step by step)

Your screen is a grid of tiny dots called **pixels** (for example 1920 × 1080 = about two
million pixels). One full picture is a **frame**. The game draws a new frame again and again —
that is what makes movement look smooth.

Two processors share the work:

| | CPU (main processor) | GPU (graphics card) |
|---|---|---|
| Job | game logic, physics, network | drawing millions of pixels, very fast, in parallel |
| Style | few workers, very smart | thousands of workers, each one simple |

On the web, the chain looks like this:

1. The game runs as JavaScript in your browser (recent Chrome or Edge works best).
2. The game talks to the GPU through **WebGPU**, the modern graphics API of the browser.
3. Inside the browser, **Dawn** (with its compiler **Tint**) translates the shader language
   **WGSL** into instructions your GPU understands (Direct3D / Metal / Vulkan, depending on
   your system).
4. The GPU executes the shaders and puts the finished frame on screen.

Bloxd itself is built with a voxel engine (**noa-engine**) on top of a 3D framework
(**Babylon.js**). For every frame, the drawing pipeline does this:

1. **Chunks.** The world is cut into columns of blocks called chunks. Only chunks near you
   are prepared for drawing.
2. **Meshing.** For each chunk, the engine builds a *mesh*: a skin of triangles covering only
   the block faces you can actually see. Hidden faces are skipped.
3. **Texture atlas.** Every block face gets its picture from one big image, the **atlas**,
   which contains all block textures side by side. Each face knows which small square of the
   atlas to use (its **UV** coordinates).
4. **Vertex step.** The GPU runs a *vertex shader* on every corner (vertex) of every triangle:
   it places the corner at the right position on your screen and passes data along (texture
   coordinates, light values, face direction…). A pack's optional vertex hooks can replace a
   corner's world position here, before projection, in allow-policy games.
5. **Rasterising.** The GPU fills each triangle with pixels. Every covered pixel becomes a
   **fragment**: a candidate pixel with interpolated data.
6. **Fragment step.** The GPU runs a *fragment shader* for every fragment: this is where the
   final colour of the pixel is decided. **This is where a pack's surface and light hooks live.**
7. **Screen.** The finished frame is shown. Then everything repeats for the next frame.

```mermaid
flowchart LR
    A[World of blocks] --> B[Chunks]
    B --> C[Meshes: visible faces only]
    C --> D[Vertex step: place corners<br/>optional pack vertex hooks]
    D --> E[Rasterise: fill pixels]
    E --> F[Fragment step: YOUR PACK<br/>surface + light hooks]
    F --> G[Screen]
```

Key idea: your pack never sees "the world" as a whole. A vertex hook sees **one corner at a
time**; surface and light hooks see **one fragment at a time** — one pixel of one block face —
plus the data the header supplies for that corner or pixel. Everything a pack does must be
computed from that local data.

## 3. What a shader is

A shader is a small function (a small piece of code) that the GPU runs an enormous number of
times in parallel — once per vertex, or once per fragment. It must be fast and self-contained:
no files, no network, no memory of the previous frame.

Bloxd packs are written in **WGSL** (WebGPU Shading Language). You do not write a whole
shader. The engine already has its own shaders; it lets you insert your code at six fixed
points, called **hooks** (Section 5): two programs (terrain and liquid) × three stages
(vertex, surface, light). Think of six doors: at a vertex door the engine asks where a corner
should be; at the surface and light doors it asks how this pixel should finally look.

## 4. What a Bloxd shader pack is

A pack is a `.zip` file with:

```
pack.json     (small metadata file)
*.wgsl        (your WGSL code — one file or many, any folders)
```

`pack.json` only needs:

```json
{ "apiVersion": 2, "name": "My Pack", "author": "you" }
```

- `apiVersion` must be exactly the JSON number **2** (the string `"2"` fails). Old v1 packs
  are rejected by the current importer.
- The importer accepts a folder or one `.zip`. After path normalisation there must be exactly
  one `pack.json`; if every file shares one root folder, that folder is stripped automatically.
- The manifest is a UTF-8 JSON object of at most **65,536 bytes**. `name` must be a non-empty
  string after trimming; `author` is an optional string or `null`; other keys are ignored.
- Sources are **1 to 256** `.wgsl` files (extension case-insensitive), sorted by path and
  joined by the pack analyser. Their total decompressed size is at most **262,144 bytes**;
  duplicate paths and invalid UTF-8 are rejected. Non-WGSL files are ignored.
- A `.zip` may be at most **33,554,432 bytes** with at most **1,024 entries**; only stored or
  deflate entries are read, while Zip64, multi-disk and encrypted archives are rejected.

To install a pack in the game: Bloxd → `O` Settings → Graphics → enable **Use New WebGPU
Renderer** → Shader Pack → choose the folder or `.zip` → **Apply**, then **reload the page**:
an imported or removed pack takes effect after that reload. Without a usable WebGPU device the
pack can be stored but stays blocked instead of becoming active.

A pack only affects **blocks, water and lava** drawn by the WebGPU/Lite terrain path. Some game
modes disable packs completely, and a WebGL fallback runs no pack code.

## 5. The six hooks (your only doors)

| Hook | When it runs | What you control |
|---|---|---|
| `bloxdTerrainVertex` | per vertex, terrain, before projection | the world position of each terrain corner |
| `bloxdTerrainSurface` | per fragment, solid blocks, before lighting | base colour, alpha where present, self-glow (emission) |
| `bloxdTerrainLight` | same fragment, after surface and engine fog | final lit colour of blocks |
| `bloxdLiquidVertex` | per vertex, liquids, before projection | the world position of each liquid corner |
| `bloxdLiquidSurface` | per fragment, water and lava, before lighting | base colour and alpha of liquids |
| `bloxdLiquidLight` | same fragment, after surface and engine fog | final lit colour of liquids |

Rules of the doors:

- A liquid stage falls back to the matching terrain hook when the liquid hook is absent. If a
  surface hook exists without its light hook (or the reverse), the missing fragment stage uses
  the engine default. Vertex hooks are optional.
- Vertex runs first. Its returned position replaces the world position **before** projection,
  interpolated fragment position and fog distance are computed.
- Surface runs **before** light, in the same fragment. You can pass a value from surface to
  light with a module-scope variable (`var<private>`).
- Always start from the engine's default result: `bloxdDefaultVertex(...)`,
  `bloxdDefaultSurface(...)` or `bloxdDefaultLight(...)`, change what you need, then return it.
  Never build the result structs yourself.
- Surface hooks run after texture colour × vertex colour and before the alpha test and
  lighting. Where `out.alpha` exists it drives cut-out discard and liquid blending; it has no
  blending effect on a plain opaque material. The `alpha` output exists only under
  `BLOXD_ALPHA` — everywhere **except terrain+strict** — so guard terrain alpha writes with
  `#ifdef BLOXD_ALPHA`.
- Self-glow (`out.emission`) belongs to the **surface** hooks only.
- A selected vertex hook, or a `discard` reachable from surface/light, does **not** reject the
  pack: the strict variants for that program are switched off and reported as “off in strict”,
  while allow variants keep the code. Strict is the default game policy, so a pack that must
  look right everywhere cannot depend on moved vertices or discards.
- The light hook receives the engine colour before and after fog. Returning
  `bloxdApplyFog(colour, light)` keeps the normal fog; any other returned RGB replaces the
  final RGB and can therefore cancel fog. The light hook does not change alpha.

## 6. What the engine tells you

For every fragment, your hooks receive data. The most useful fields:

| Data | Meaning, in simple words |
|---|---|
| `colour` | the block's texture colour at this pixel (from the atlas), before your changes |
| `blockId` | the **numeric id** of the block (a whole number). This is how you treat one block type differently from another — full table in Part VIII |
| `position` | where this pixel is in the world (x, y, z) |
| `normal` | which way the face points (up, down, north…), as a vector |
| `skyLight` | how much sky light reaches this block, 0 to 1 — but **tone-mapped**: open sky ≈ 1.0, one light level lost under a tree ≈ 0.995 (see Section 7) |
| `blockLight` | light from lamps, torches, lava… as a colour (coloured lamps exist) |
| `heldLight` | light from the item in the player's hand |
| `skyLightColour` | the current tint of the sky (dark blue at night, warm at sunset) |
| `litColour` | the engine's own lit colour for this surface (useful as a base) |
| `engineColour` | the engine-combined colour before pack emission/fog handling in the default light result |
| `directional`, `ambient` | the directional scalar and ambient term the engine used for this fragment |
| `ambientLightColour` | the ambient light tint paired with `skyLightColour` |
| `fogVisibility`, `fogColour` | how fogged this pixel is, and the fog colour (arrives **black** when fog is off — handle that case) |

Engine functions you can call:

| Function | What it gives you |
|---|---|
| `bloxdDefaultVertex(in)` / `bloxdDefaultSurface(in)` / `bloxdDefaultLight(surface, light)` | the engine's normal result — always your starting point |
| `bloxdApplyFog(colour, light)` | blends your colour into the fog correctly |
| `bloxdSunDirection()` | unit vector towards the sun; `(0,0,0)` in worlds without an earth-like sun; the moon is exactly the opposite direction |
| `bloxdTime()` | seconds — **wraps back to 0 every 3600 seconds** (`bloxdTimeWrap`). See Section 7 |
| `bloxdEyePosition()` | the camera position (for distance effects) |
| `bloxdOriginOffset()` | the engine periodically rebases world coordinates; add this offset into any world-position pattern, or your pattern will visibly jump |
| `bloxdFaceBlock(position, normal)` | the block cell (whole-number coordinates) of the face you are drawing — perfect for per-block random variation |
| `bloxdOpaqueBehind()` | liquid surface/light only, under `BLOXD_SCENE_DEPTH`: returns `{found, position, distance}` for the opaque point behind this exact pixel; `distance` is eye→behind, so liquid thickness along the view ray is `distance - distance(eye, fragment position)` |

## 7. The traps everyone falls into

**Time wraps.** `bloxdTime()` counts seconds but restarts at 3600. If your animation uses raw
time, it will jump once per hour. Always animate with whole cycles inside the wrap:

```wgsl
sin(6.2831853 * fract(bloxdTime() / bloxdTimeWrap * cycles + phase))
```

Choose `cycles` as a whole number. Then the value at second 3600 equals the value at second
0: no jump, ever.

**skyLight is tone-mapped.** It is not a linear 0–1 brightness. The engine compresses the
0–15 light levels into a curve: open sky is ≈ 1.0 and losing one level still reads ≈ 0.995.
If you test `skyLight < 0.5` expecting "in shadow", almost nothing will match. Calibrate
thresholds on the real curve (Part IV gives measured values).

**Fog is always there.** Even when you cannot see it, the engine computes fog (sometimes
pushed very far away). If your light hook returns a colour without `bloxdApplyFog`, distant
terrain will look too bright and cut through the fog. Apply fog last, after your colour work.

**Unlit does not mean “fields disappear”.** In an unlit variant the header supplies neutral
light data: `skyLight = 1`, `blockLight = 0`, `heldLight = 0`, `directional = 0`, and white
light colours. Sky-driven logic therefore sees “full sky” unless it is explicitly gated with
`#ifdef BLOXD_LIGHTING`.

**Strict is the default, and imports apply on reload.** A vertex hook or reachable `discard`
silently turns that program off in strict games instead of failing the whole pack. After
importing, replacing or removing a pack, reload the page before judging the result.

## 8. Everything a pack CAN do

- Recolour any block, water or lava — globally or per `blockId`.
- Move terrain or liquid vertices in allow-policy games (wind, waves, wobble) — never as the
  only carrier of an essential look, because strict is the default policy.
- Measure real liquid thickness along the view ray with `bloxdOpaqueBehind().distance`.
- Make things glow (`out.emission` in surface hooks): lava, ores, lamps…
- Animate colour and alpha over time (pulsing, flowing lava, shimmering water) — wrap-safe
  (Section 7).
- React to the day/night cycle through `bloxdSunDirection()` and `skyLightColour` (warm
  sunsets, blue moonlight tints).
- Add world-anchored procedural detail: subtle per-block variation with `bloxdFaceBlock`
  hashes, distance fog tints, underwater darkening with `bloxdOpaqueBehind()` depth.
- Grade the whole image per fragment: contrast, saturation, warm/cold balance — as long as
  fog is applied at the end.
- Paint effects *on* surfaces: sparkles on ore, wet-looking darkening near water level, snow
  on upward faces (`normal.y`), and similar tricks — all computed from the fragment's own data.
- Use distance (`bloxdEyePosition()`) to fade expensive or noisy effects out (cheap
  level-of-detail).

## 9. What a pack CANNOT do (engine limits)

- **Plants, grass and flowers** are drawn by a part of the engine packs cannot reach. You
  cannot recolour or animate them.
- **No post-processing.** You have no access to the finished frame, no screen coordinates, no
  blur/bloom/vignette passes.
- **No general scene depth or behind-colour.** The only “what is behind this” query is
  `bloxdOpaqueBehind()` through a liquid, at the exact pixel, against geometry drawn before
  the liquid snapshot; it returns no colour and cannot see the liquid itself or transparencies
  drawn later.
- **No real shadow maps or ambient occlusion** beyond what the engine's light values already
  encode.
- **No new objects or particles** in the world. You can only paint on surfaces that already
  exist. (Clever packs paint overlay effects onto surfaces — see the recipes — but the
  geometry is always the engine's.)
- **No textures or samplers** of your own, no extra data feeds: your only inputs are the
  hook arguments and the engine functions.
- **Vertex movement is policy-gated.** The vertex hooks are real, but they run only where a
  game explicitly chooses the allow policy; strict is the default and switches that program's
  pack code off. Never make readability or a core effect depend on moved corners.
- **The sky itself** (sun disc, skybox, clouds) is drawn by the engine. Packs receive sky
  *data* (direction, tint) but do not draw the sky.

If an effect needs something from this list, no pack can do it today — this is proven engine
behaviour, not a skill issue.

## 10. Your first pack in five steps

1. Create `pack.json`:

```json
{ "apiVersion": 2, "name": "My First Pack", "author": "you" }
```

2. Create `shader.wgsl` next to it:

```wgsl
fn bloxdTerrainSurface(surface: BloxdSurfaceIn) -> BloxdSurface {
    var out = bloxdDefaultSurface(surface);
    out.colour = out.colour * vec3f(1.05, 1.0, 0.92);
    return out;
}

fn bloxdTerrainLight(surface: BloxdSurface, light: BloxdLightIn) -> BloxdLight {
    var out = bloxdDefaultLight(surface, light);
    _ = surface;
    return out;
}
```

This pack makes every block slightly warmer (more red, less blue) and keeps the engine's
lighting. The `_ = surface;` line tells the compiler "this input is intentionally unused" —
WGSL requires this bare form.

3. Either keep the two files in one folder for folder import, or zip them together. The
   clearest layout keeps `pack.json` beside the WGSL at the top level; a single wrapper folder
   shared by every file is also accepted and stripped by the importer.
4. In the game: Settings → Graphics → **Use New WebGPU Renderer** on → Shader Pack →
   choose the folder or `.zip` → Apply → **reload the page**.
5. Look around: the world should be a little warmer. Change the three numbers and reload to
   experiment.

Then grow step by step: one effect at a time, check it at midday, sunset, night, underwater
and in a cave before adding the next.

## 11. The nine hard rules

Breaking the analyser rules rejects the pack; breaking the policy rules makes it silently
vanish in the default strict games:

1. Never define a `BLOXD_*` macro or any `bloxd*` name other than the six hooks. Pack
   preprocessor directives are only `#define`, `#ifdef`, `#ifndef`, `#else` and `#endif` at
   the start of a line; a pack `#define` is a valueless global flag and may not sit inside a
   conditional.
2. Never build `BloxdVertex`, `BloxdSurface` or `BloxdLight` yourself — start from
   `bloxdDefaultVertex`, `bloxdDefaultSurface` or `bloxdDefaultLight`.
3. `mod` is a reserved word in WGSL — use `%`.
4. No attributes (`@…`), entry points, textures, samplers, `override`, `enable`, `requires`,
   `diagnostic`, extra storage classes, double-underscore identifiers or screen UVs of your own.
5. A vertex hook or reachable `discard` switches that program **off in strict** (the default
   policy) instead of rejecting the pack. For a strict-safe pack, avoid both or gate the effect
   so the strict variant still carries the look.
6. `out.alpha` exists only under `BLOXD_ALPHA` (absent solely in terrain+strict). Liquid alpha
   exists in every variant; terrain alpha writes need the `BLOXD_ALPHA` guard.
7. Unused inputs: write `_ = value;` — the form `let _ =` is rejected.
8. Respect the importer byte caps: manifest ≤ 65,536 bytes; 1–256 WGSL files; total WGSL
   ≤ 262,144 bytes; one zip ≤ 33,554,432 bytes and ≤ 1,024 entries.
9. The engine builds **8 variants**: allow/strict × lit/unlit × terrain/liquid. The only pack
   defines are `BLOXD_STRICT`, `BLOXD_LIGHTING`, `BLOXD_SCENE_DEPTH` (liquid only) and
   `BLOXD_ALPHA` (absent only in terrain+strict). Your code must compile and behave in all of
   them. Parenthesise mixed bitwise/shift expressions for the browser's Tint compiler.

## 12. Mini glossary

| Word | Meaning |
|---|---|
| Frame | one complete picture on the screen |
| Pixel / fragment | one dot of the picture / a candidate pixel being coloured |
| Vertex | a corner of a triangle |
| Mesh | the skin of triangles built from a chunk's visible faces |
| Atlas (texture atlas) | the one big image containing all block textures |
| UV | coordinates that say which part of the atlas a face uses |
| WGSL | the shader language of WebGPU — the language of Bloxd packs |
| Hook | one of the six engine functions your pack may define (vertex/surface/light × terrain/liquid) |
| skyLight / blockLight | light from the sky / light from blocks (lamps, lava) |
| Wrap (3600 s) | `bloxdTime()` restarting at 0 every hour |
| Fog | distant terrain blending into the fog colour |
| Variant | one of the 8 ways the engine compiles your pack |

## 13. Go deeper

| Part | File | Content |
|---|---|---|
| I | [01-making](#part-i--making-a-pack) | pack format, multi-file loading, caps, distribution |
| II | [02-api](#part-ii--the-api-contract) | the complete hook and struct contract |
| III | [03-recipes](#part-iii--recipes) | 12 production recipes with WGSL code |
| IV | [04-realism](#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) | measured numbers: light units, fog, water optics |
| V | [05-troubleshooting](#part-v--troubleshooting) | every known failure mode and its fix |
| VI | [06-implementation](#part-vi--implementation--local-validation) | local validation in all 8 variants, packaging checks |
| VII | [07-internals](#part-vii--engine-internals) | engine internals (time, light pipeline, sky, loader) |
| VIII | [08-block-ids](#part-viii--the-numeric-block-id-table) | the full numeric block-id table |
| IX | [09-sources](#part-ix--where-this-knowledge-comes-from-and-what-we-dont-know) | how every fact in this guide was established |
| X | [10-constants](#part-x--the-constants-register-en) | every constant, with its role |

Other languages: [guide index](README.md).

---

# Part I — Making a pack

## What a pack is

A pack is imported either as a **folder** or as **one `.zip`** containing one manifest and one
or more WGSL sources:

```
pack.json          # metadata, required, exactly one after path normalisation
*.wgsl             # 1–256 WGSL files, any folder layout below the pack root
```

`pack.json`:

```json
{ "apiVersion": 2, "name": "My Pack", "author": "you" }
```

- `apiVersion` **must be exactly the JSON number 2**. The string `"2"` fails, and v1 packs are
  rejected by the current importer.
- `name` must be a string that is non-empty after trimming. `author` is optional and, when
  present and not `null`, must be a string.
- The stored manifest keeps only `apiVersion`, `name` and `author` (`author` becomes a string
  or `null`); every other key is discarded. There is no file list in `pack.json`.
- The manifest must be a strict-UTF-8 JSON object of at most **65,536 bytes** after
  decompression. Zero manifests, or two or more after normalisation, are an import error.
- Paths are normalised (`\` becomes `/`), directory entries and common macOS junk are ignored,
  and a root folder shared by **all** files is stripped automatically. Keeping `pack.json` at
  the top level remains the clearest layout. **[client]**

## Installing (what your users will do)

Bloxd → `O` Settings → Graphics → tick **Use New WebGPU Renderer** → Shader Pack → drag and
drop, choose a folder, or choose one `.zip` → **Apply** → **reload the page**. The import
control is disabled while a pack is loading/checking or until WebGPU is confirmed usable.
Import validates the pack immediately and stores the result; a real pack change is marked
pending and becomes visible only after the reload. If no temporary WebGPU validation device is
available, the pack is stored unvalidated and blocked with a “no WebGPU” state rather than
becoming active. **[client]**

## What a pack can affect

**Blocks, water and lava only**, and only when the WebGPU/Lite renderer draws the terrain.
An active pack can force the game to request WebGPU, but a WebGL fallback runs no pack code.
Plants/grass/flowers are drawn by a part of Bloxd **packs cannot reach** (confirmed by
dissection of a shipped pack). Games choose a pack policy — off, strict or allow; **strict is
the default**, allow is an explicit opt-in, and some portals/games disable packs entirely.
Vertex deformation is therefore an allow-only enhancement, never a baseline. **[client]**

## Single-file vs multi-file — IMPORTANT

The importer collects every `.wgsl` file below the pack root, sorts the normalised paths
lexicographically, and feeds the token streams to the analyser in that order. There is **no
required `shader.wgsl`**: shipped packs use subfolders such as `lib/`, `terrain/` and
`water/` with no root shader file. WGSL module declarations are order-independent, but the
pack preprocessor is sequential and its `#define` flags are global to the whole pack, so file
naming still matters wherever conditional code depends on a flag. Diagnostics are mapped back
to the original file and line. Duplicate exact paths are rejected. **[client + shipped]**

Both layouts are valid:

```
my-pack.zip                    my-pack.zip
├── pack.json                  ├── pack.json
└── shader.wgsl                ├── lib/hash.wgsl
                               ├── terrain/soft.wgsl
                               └── water/liquid.wgsl
```

Multi-file is nicer to maintain; single-file is easier to share. A wrapper folder shared by
every entry is stripped before these paths are interpreted.

## Caps

| Item | Exact current limit |
|---|---:|
| one imported `.zip` file | ≤ **33,554,432 bytes** (32 MiB) |
| entries inside that zip | ≤ **1,024** |
| accepted zip entry methods | **0 stored** or **8 deflate** only; Zip64, multi-disk and encrypted entries rejected |
| `pack.json` after decompression | ≤ **65,536 bytes**, strict UTF-8 JSON object |
| `.wgsl` files | **1–256**, extension case-insensitive, duplicate exact path rejected |
| all `.wgsl` after decompression | ≤ **262,144 bytes** total, strict UTF-8 |
| stored validation errors | first **100** errors plus an overflow count |

Other files in the folder/zip are ignored. CRC values and declared uncompressed sizes are not
the safety gate; decompression is streamed against the byte budget. Per-fragment cost remains
yours to control: gate expensive effects by distance/blockId (see Part III recipes). **[client]**

## Distributing

- **The Bloxdhub workshop** is the de-facto storefront (`bloxdhub.com/workshop?type=shader-packs`).
  Each item page exposes a direct `media.bloxdhub.com/workshop-files/<token>.zip` link.
- Direct `.zip` download links work equally; users just pick the downloaded file or folder in Settings.
- Update cadence is hot: workshop packs update within hours; users must re-download manually.

## Minimal working pack

`pack.json`:

```json
{ "apiVersion": 2, "name": "Starter", "author": "you" }
```

`shader.wgsl`:

```wgsl
fn bloxdTerrainSurface(surface: BloxdSurfaceIn) -> BloxdSurface {
    var out = bloxdDefaultSurface(surface);
    out.colour = out.colour * vec3f(1.02, 1.0, 0.96);
    return out;
}

fn bloxdTerrainLight(surface: BloxdSurface, light: BloxdLightIn) -> BloxdLight {
    var out = bloxdDefaultLight(surface, light);
    _ = surface; // v2 requires the bare underscore form for unused hook params
    return out;
}
```

Import the folder, or zip those two files at the top level (one shared wrapper folder also works), Apply, and reload the page. Now read Part II.

---

# Part II — The API contract

Everything below is proven in a shipped pack (**[shipped]**), exercised by locally validated
packs (**[local]**), or verified against the current public web client's pack pipeline as a
behavioural fact (**[client]**). If it is not in this file, treat it as unknown until proven.

## The six hooks

| Hook | Runs | Purpose |
|---|---|---|
| `bloxdTerrainVertex(BloxdVertexIn) -> BloxdVertex` | per terrain vertex, before projection | move terrain corners in world space |
| `bloxdTerrainSurface(BloxdSurfaceIn) -> BloxdSurface` | per terrain fragment, after texture × vertex colour, before alpha test and lighting | recolour / alpha / emission of blocks |
| `bloxdTerrainLight(BloxdSurface, BloxdLightIn) -> BloxdLight` | same fragment, after surface; engine pre/post-fog colours are both available | final terrain RGB |
| `bloxdLiquidVertex(BloxdVertexIn) -> BloxdVertex` | per liquid vertex, before projection | move liquid corners in world space |
| `bloxdLiquidSurface(BloxdSurfaceIn) -> BloxdSurface` | per liquid fragment, before alpha test and lighting | colour/alpha/emission of water & lava |
| `bloxdLiquidLight(BloxdSurface, BloxdLightIn) -> BloxdLight` | same fragment, after surface | final liquid RGB |

Facts that matter:

- **Fallback is per stage.** A missing liquid vertex/surface/light hook falls back to the
  corresponding terrain hook. If only one of surface/light is selected for a program, the other
  fragment stage is the engine default. Vertex is optional. The generated program keeps only
  declarations reachable from the selected hooks. **[client]**
- **Vertex output is world position.** It replaces the corner's world position before
  projection, before the interpolated fragment position, and before fog distance. A selected
  vertex hook switches that program off in strict variants. **[client]**
- **Surface and light run in the same fragment, surface first.** You can pass data between them
  with a module-scope `var<private>` **[shipped]**. Fragments killed earlier by the engine fade
  or later by the alpha test do not run downstream hooks. **[client]**
- Surface output colour overwrites the sampled base colour; there is no second texture sample.
  `out.alpha`, where the field exists, is applied before the alpha test and is the real liquid
  blend factor. On a plain opaque material it has no blending effect. **[client]**
- **`out.emission` belongs to the surface hook** (self-glow). Do not write it from light hooks.
- The default light result is `engineColour + emission × fogVisibility`, then normal fog is
  `mix(fogColour, colour, fogVisibility)`. A custom light hook's returned RGB replaces the final
  RGB (so it may cancel fog); alpha is unchanged by the light stage. **[client]**
- To opt in to a hook you define it and start from the matching `bloxdDefault*` result; unused
  parameters are dropped with the bare form `_ = param;`.

## Structs (complete API v2 header fields)

```wgsl
BloxdVertexIn  { position: vec3f, normal: vec3f, blockId: u32 }
BloxdVertex    { position: vec3f }
BloxdSurfaceIn { colour: vec3f, alpha: f32, normal: vec3f, position: vec3f,
                 blockId: u32 }
BloxdSurface   { colour: vec3f, alpha: f32 /* only under BLOXD_ALPHA */,
                 emission: vec3f }
BloxdLightIn   { litColour: vec3f, engineColour: vec3f, directional: f32,
                 ambient: vec3f, blockLight: vec3f, skyLight: f32,
                 ambientLightColour: vec3f, skyLightColour: vec3f,
                 heldLight: vec3f, fogColour: vec3f, fogVisibility: f32,
                 position: vec3f, normal: vec3f, blockId: u32 }
BloxdLight     { colour: vec3f }
BloxdOpaqueBehind { found: bool, position: vec3f, distance: f32 }
```

Reading the fields:

- `blockId : u32` — **the numeric block id** (Part VIII table). This is how per-block shading works.
- `skyLight` — the engine sky-light curve applied to the 0–15 level (exact formula in Part IV).
  Open sky = 1; level 14 ≈ 0.9945. Threshold decisions must be calibrated on this curve.
- `blockLight`, `heldLight` — colour channels (can be non-grey: coloured lamps).
- `skyLightColour`, `ambientLightColour` — sky and ambient tints; the sky tint darkens at night.
- `litColour` — the surface's own lit colour. `engineColour` — the engine-combined colour used
  by the default light result before pack emission/fog handling. `directional` and `ambient`
  expose the directional scalar and ambient term behind that result.
- `fogVisibility`, `fogColour` — engine fog inputs. `fogColour` arrives **black** when fog mode is NONE.
- Without `BLOXD_LIGHTING`, the header supplies `skyLight = 1`, `blockLight = 0`,
  `heldLight = 0`, `directional = 0`, and white light colours. **[client]**
- Header structs may be used as parameter/return types and through the `bloxdDefault*` values;
  constructing them directly is rejected. **[client]**

## Engine functions

| Function | Returns / does |
|---|---|
| `bloxdDefaultVertex(in)` / `bloxdDefaultSurface(in)` / `bloxdDefaultLight(surface, light)` | your mandatory starting point — never construct the result structs literally |
| `bloxdApplyFog(colour, light)` | `mix(fogColour, colour, fogVisibility)`; call it when your light hook should keep normal engine fog |
| `bloxdSunDirection()` | unit vector to the sun; **(0,0,0) when the skybox has no earth-type sun**; static in default worlds; the moon is exactly `−bloxdSunDirection()` |
| `bloxdTime()` / `bloxdTimeWrap` | `performance.now()/1000 mod 3600`; animate with **whole cycles**: `sin(TAU * fract(bloxdTime() / bloxdTimeWrap * cycles + phase))` **[client]** |
| `bloxdEyePosition()` | camera position, for distance/LOD and view vectors |
| `bloxdOriginOffset()` | integer floating-origin rebase offset; **add it into any world-space hash** or patterns jump when the engine rebases (it does) |
| `bloxdFaceBlock(position, normal)` | the **cell** (block coordinates) of the face you are on — per-block hash input; the id itself is `surface.blockId` / `light.blockId` **[shipped]** |
| `bloxdOpaqueBehind()` | `{found, position, distance}` for the opaque point behind the current liquid fragment. Liquid surface/light only, under `BLOXD_SCENE_DEPTH`; reachable from vertex is an error, and terrain use without the guard is diagnosed. `distance` is eye→behind; optical thickness is that minus eye→fragment distance. **[client]** |

## Hard rules (violating any = rejected, off in strict, or broken pack)

1. **Never `#define` anything starting with `BLOXD_`**, and never declare a `bloxd*` name other
   than the six hooks. The pack preprocessor accepts only `#define`, `#ifdef`, `#ifndef`,
   `#else` and `#endif`, at the start of a line. A pack `#define` is a valueless flag, global
   to the whole pack, and is forbidden inside a conditional; conditionals may test a `bloxd*`
   name only for the four engine defines in the variant table below. **[client]**
2. **Never construct `BloxdVertex`/`BloxdSurface`/`BloxdLight` literally** — always start from
   `bloxdDefault*`.
3. `mod` is a **reserved word** in WGSL — use the `%` operator.
4. The analyser explicitly rejects `@…` attributes; `enable`, `requires` and `diagnostic`;
   `override`; storage classes other than plain `var`, `var<private>` and `var<function>`;
   `sampler`/`texture_*` types; redeclared built-in or reserved names; identifiers containing a
   double underscore; and direct construction of header structs. **[client]**
5. A selected vertex hook or a `discard` reachable from surface/light **switches the strict
   variants for that program off**; it does not reject the pack, and allow variants keep the
   code. Design the strict look first because strict is the default policy. **[client]**
6. Guard every terrain use of `out.alpha` with `#ifdef BLOXD_ALPHA`. The field is absent only
   in terrain+strict; liquid outputs have alpha in all variants. **[client]**
7. `let _ =` is rejected; use bare `_ = expr;`.
8. Respect the exact importer caps in Part I (manifest, file count, total WGSL bytes, zip size
   and entry count). **[client]**
9. Assume the browser Tint compiler, not just naga: parenthesise mixed bitwise/shift expressions
   even though some shipped packs skip it.

## The 8 variants you must survive

The analyser always builds allow/strict × lit/unlit × terrain/liquid. A game then chooses off,
strict or allow; **strict is the default**, allow is explicit. Exactly four defines are visible
to pack code:

| Define | Defined exactly when |
|---|---|
| `BLOXD_STRICT` | strict variant |
| `BLOXD_LIGHTING` | lit variant |
| `BLOXD_SCENE_DEPTH` | liquid program (both policies, lit or unlit) |
| `BLOXD_ALPHA` | every variant **except terrain+strict** |

Unlit variants still run through the same hook shapes with neutral light inputs (`skyLight=1`,
block/held/directional light zero, white light colours), so gate sky logic with
`#ifdef BLOXD_LIGHTING` when “unlit” must mean “effect off”. Every hook and helper reachable
from it must compile under the define set of all eight variants (Part VI). **[client]**

## Capabilities & boundaries — the definitive matrix

| Packs CAN | Packs CANNOT |
|---|---|
| recolour terrain & liquids **per blockId** (Part VIII) | touch plants/grass/flowers (engine-rendered, unreachable **[shipped]**) |
| set alpha on cutouts and liquids where `BLOXD_ALPHA` provides the field | post-process the frame (no screen-space access, no feedback texture) |
| self-glow via `out.emission` (surface hook) | read general scene depth or the colour behind a surface — only the liquid `bloxdOpaqueBehind()` query exists |
| grade, tint, replace or keep fog in the light hook, sky-driven terms | real shadow-mapping or SSAO beyond what the supplied light values encode |
| world-anchored procedural effects (hash + rebase) | add objects/particles to the world (paint overlays instead, R14) |
| private-var data surface→light per fragment | use textures/samplers/extra binds or persistent GPU state |
| vertex deformation in allow-policy games | depend on vertex deformation or `discard` in the default strict policy |
| measure liquid thickness from `bloxdOpaqueBehind().distance` | see through terrain, see other liquids/transparencies behind the snapshot point, or sample neighbouring pixels |
| react to block/held/directional/ambient light, sun vector and wrapped time | know the held-beam direction; get per-world config UI |

# Part III — Recipes

All snippets are original (constants quoted from dissected packs are credited). They follow the
Part II rules and compile in all 8 variants.

## R1 — Block detection (the foundation)

```wgsl
fn isLeaf(id: u32) -> bool {
    switch id {
        case 100u, 101u, 102u, 103u, 491u, 492u, 493u, 653u, 911u, 1226u: { return true; }
        default: { return false; }
    }
}
```

Id groups live in Part VIII. In the light hook use `light.blockId`; in the surface hook use
`surface.blockId` — `bloxdFaceBlock(surface.position, surface.normal)` gives the block's cell
coordinates, the input per-block hashes want.

## R2 — Canopy shadow (the trick behind “soft tree shadows”)

Under a tree, exactly one skyLight level is lost — but skyLight is tone-mapped, so that level is
≈ 0.995, not 0.93. Count it:

```wgsl
const CANOPY_SPREAD = 0.0035; // skyLight lost that counts as full shade
var covered = clamp((1.0 - light.skyLight) / CANOPY_SPREAD, 0.0, 1.0)
            * smoothstep(0.35, 0.6, light.skyLight); // caves stay open
```

Credit: shipped pack Breeze (Crownix, after Ellie). Pair it with a lamp guard (R4) or lamps
stop working under trees.

## R3 — Directional sun tint by face

```wgsl
let sun = bloxdSunDirection();
let day = smoothstep(0.0, 0.12, sun.y);            // off at night & on sunless skies
let lit = smoothstep(-0.1, 0.35, dot(light.normal, sun));
let strength = day * smoothstep(0.4, 0.9, light.skyLight); // shadows need skyLight
out.colour *= mix(vec3f(0.76, 0.8, 0.88), vec3f(1.1, 1.04, 0.94), lit) * strength;
```

`bloxdSunDirection()` is zero on sunless skyboxes — `day` auto-disables everything.

## R4 — Lamp guard (lights must punch through your shading)

```wgsl
let lamp = 1.0 - smoothstep(0.4, 0.9,
             max(light.blockLight.r, max(light.blockLight.g, light.blockLight.b)));
strength *= lamp;   // every darkening/shadow factor you add must multiply by this
```

## R5 — Brightness lift that never clips (grade before fog)

```wgsl
const BRIGHTEN = 1.45; const VIBRANCE = 0.22;
fn grade(c: vec3f) -> vec3f {
    let l = max(c, vec3f(0.0));
    let b = l * BRIGHTEN / (1.0 + l * (BRIGHTEN - 1.0)); // slope B at black, white stays white
    let grey = dot(b, vec3f(0.2126, 0.7152, 0.0722));
    let chroma = max(b.r, max(b.g, b.b)) - min(b.r, min(b.g, b.b));
    return clamp(mix(vec3f(grey), b, 1.0 + VIBRANCE * (1.0 - chroma)), vec3f(0.0), vec3f(1.0));
}
// usage: out.colour = bloxdApplyFog(grade(lit) + surface.emission, light);
```

Credit: shipped pack Breeze. Grade **before** fog, add emission before fog.

## R6 — Real water depth (Beer–Lambert, engine-approved data)

Use this only in a liquid surface/light path. `behind.distance` is the eye→opaque-point
distance, so the view-ray thickness through the liquid is that value minus eye→surface:

```wgsl
#ifdef BLOXD_SCENE_DEPTH
let behind = bloxdOpaqueBehind();
let eyeDist = distance(bloxdEyePosition(), surface.position);
let thickness = select(64.0, max(behind.distance - eyeDist, 0.0), behind.found);
#else
let thickness = 64.0;
#endif
let depthFade = 1.0 - exp(-thickness * 0.32);   // ~1/3 at 1 block, ~85% at 6 blocks
out.colour = out.colour * mix(SHALLOW_TINT, DEEP_TINT, depthFade);
```

`behind.position.y` is still useful when an effect needs **vertical** depth below a waterline;
do not confuse that with optical thickness along a grazing view ray. `found=false` means no
opaque point in the pre-liquid snapshot for this exact pixel (open sky is the common case).
Credit: shipped pack Breeze for the 0.32 extinction scale.

## R7 — Sky reflection that respects night

```wgsl
let toEye = normalize(bloxdEyePosition() - cellCentre);
let grazing = 1.0 - clamp(dot(toEye, n), 0.0, 1.0);
let fresnel = 0.02 + 0.98 * grazing * grazing * grazing * grazing * grazing; // Schlick, water
let skyExposure = smoothstep(0.45, 0.98, light.skyLight); // cave water must not reflect sky
colour = mix(colour, light.skyLightColour * SKY_TINT, fresnel * 0.45 * skyExposure);
```

Never `normalize(toEye + bloxdSunDirection())` without a length guard — it is exactly zero when
the sun sits opposite the eye (NaN guarantee).

## R8 — World-stable hashing under the floating origin

```wgsl
fn mixBits(v: u32) -> u32 {
    var h = v; h ^= h >> 16u; h *= 0x7feb352du; h ^= h >> 15u; h *= 0x846ca68bu; h ^= h >> 16u;
    return h;
}
fn cellHash(c: vec3i) -> u32 {
    let p = bitcast<vec3u>(c);
    return mixBits((p.x * 0x8da6b343u) ^ (p.y * 0xd8163841u) ^ (p.z * 0xcb1ab31fu));
}
// any world-space pattern must rebase:
let place = light.position + vec3f(bloxdOriginOffset() % vec3i(4096));
```

Credit: shipped pack Breeze. Without the origin term your patterns slide when the engine rebases
the world (it does, periodically).

## R9 — Wrap-safe animation (precision far from spawn)

```wgsl
const TAU = 6.2831853;
let value = 0.5 + 0.5 * sin(TAU * fract(bloxdTime() / bloxdTimeWrap * cycles + phase));
```

`cycles` is a whole number ⇒ seamless at the wrap. This is the only safe way to use `bloxdTime()`
for persistent world-anchored motion.

## R10 — LOD fade so distance costs nothing

```wgsl
let near = 1.0 - smoothstep(FAR * 0.6, FAR, distance(bloxdEyePosition(), position));
if (near > 0.0) { /* expensive detail only here */ }
```

Shipped packs fade per-cell grain at 14 m, ripples at 24–40 m, blotches at 48 m. Every
per-fragment loop you add must be gated.

## R13 — Precision-immortal value noise (rotated integer lattices)

The shipped-pack trick for noise that never loses precision and never jumps at origin rebases:
work on a lattice whose corners are **integers that wrap**, approached through whole-number
strides:

```wgsl
const CELLS = 8;  const PERIOD = 289;             // corner ids wrap here (float-safe)
const STRIDE = 2000;  const SHIFT = vec2i(117, 44); // 0.5 lattice cells/block, rotated 20.6°
fn octave(cell: vec2i) -> vec3f {
    let rest  = ((cell % STRIDE) + STRIDE) % STRIDE;
    let count = ((cell - rest) / STRIDE) % PERIOD;   // keeps base small forever
    let base  = count.x * SHIFT + count.y * vec2i(-SHIFT.y, SHIFT.x);
    // hash corners of base + rotated point; quintic blend; return analytic gradient + value
}
```

Credit: shipped pack Breeze (two rotated octaves; fine octave fades 24→40 m and is skipped past
it). Paired with R8/R9 this gives waves/grain/mist that survive hours far from spawn.

## R14 — Painting overlays: adding “objects” without adding anything

Packs cannot add objects to the world — so **paint them into the colour**. March a few steps
along the view ray in a frame that slides downward (so hashed cells fall), test a hashed quad
per cell, and if one is hit **return its colour instead of the terrain’s**:

```wgsl
for (var i = 0; i < STEPS; i++) {
    let s = (f32(i) + 0.5) * stride;
    let sliding = eye + origin + d * s + vec3f(0.0, t * FALL, 0.0); // falling frame
    let h = cellHash(vec3i(floor(sliding / CELL)) + SALT);
    if (hashUnit(h) > CHANCE) { continue; }
    // position a hashed quad in the cell; if the pixel is on it: return colour * level;
}
```

Gate it (`isLeaf(blockId) || underTree`, range ≤ 10 m) — a 6-step raymarch per pixel is the
workshop’s #1 FPS complaint when unbounded. Credit: shipped pack Breeze (falling leaves), the
technique generalises to any “particle”.

## R11 — Alpha that survives every variant

Liquid `BloxdSurface` has an alpha field in **every** variant, including strict, because
`BLOXD_ALPHA` is absent only for terrain+strict:

```wgsl
var out = bloxdDefaultSurface(surface);
out.alpha = clamp(surface.alpha / REGISTERED_ALPHA * mix(SHALLOW_OP, DEEP_OP, depthFade),
                  0.0, 1.0);
out.alpha = max(out.alpha, foam * 0.95); // overlays push alpha up, never down
```

In a terrain surface hook, the same write must be guarded:

```wgsl
#ifdef BLOXD_ALPHA
out.alpha = surface.alpha;
#endif
```

Rebuild liquid alpha from the registered/input value instead of hardcoding one material's
opacity for every liquid.

## R12 — Per-cell variation without texture repetition

```wgsl
let cell = vec3i(floor(surface.position * CELLS - surface.normal * 0.5))
         + bloxdOriginOffset() * CELLS + vec3i(0, 104729, 0); // offset avoids hash collisions
offset = (f32(cellHash(cell) >> 8u) / 16777216.0 * 2.0 - 1.0) * AMOUNT;
```

The half-cell normal shift keeps side faces from flickering between neighbours.

---

# Part IV — Measured numbers (realism that survives contact with the game)

Labels: **[measured]** from our screenshot/sonde pipelines · **[shipped]** proven in a released
pack · **[3rd-party]** restored from production JS by the community, sanity-check before relying.

## Light units

- Sky light propagates as integer levels 0–15; **open sky = 15**. The value delivered to packs
  uses the exact curve `x = level/15`, `skyLight = 1 − (1 − x/(3 − 2x))³` **[client]**.
  Reference points: level 0→0, 1→0.0682, 4→0.2905, 8→0.6203, 12→0.9213, 14→**0.9945**,
  15→1. One level lost under a canopy is therefore still ≈0.995, not 14/15≈0.933.
- Worked thresholds on the delivered curve: full sky ≈ ≥0.98; cave/night rejection below
  ≈0.45 corresponds roughly to losing the top nine levels. Calibrate against the formula, not
  a linear mental model.
- Vertex light levels are packed as four 4-bit base-16 fields, interpolated, and the sky curve
  is applied in the fragment stage. Packed light colours also floor every channel at **35 % of
  the brightest channel** **[client]** — pure red lifts toward (1.0, 0.35, 0), which is why
  lamps can look washed-out pink.
- `l.ambient` = material.ambient × sceneAmbient; the scene side follows the user's graphics
  setting (default 0.5). Never hardcode its default **[3rd-party]**.

## Sun, moon, sky

- Default worlds: sun direction static ≈ **(−0.56, 0.81, −0.18)** **[3rd-party]**; day/night
  worlds update it; **moon = −sun exactly**; night ⇔ `sun.y < 0`.
- Non-earth skyboxes (gloomy/interstellar/space): `bloxdSunDirection()` = **(0,0,0)** — gate
  every sun effect with a `sun.y`-based day factor and it self-disables **[shipped]**.
- The terrain directional term is a per-vertex Lambert sum over the scene's compiled-in
  directional lights (the Lite path accepts up to four). It does not by itself create a
  time-of-day look; sun-driven colour still comes from `bloxdSunDirection()` and the supplied
  sky/ambient colours. **[client]**

## Fog

- Visibility is a **linear ramp**: `fogVisibility = (fogEnd − dist)/(fogEnd − fogStart)`,
  `fogStart = 32×D`, `fogEnd = 32×(D+1)` (D = player’s distance setting; D=0 ⇒ end 5) — the
  gradient band is only **32 blocks wide** **[3rd-party]**. Our older “EXP2” note came from a
  wiki; trust the production-JS figure, verify with a probe pack if your effect cares.
- Default fog colour `rgb(183, 191, 195)`; world owners can override it; **fog mode 0 (NONE)
  delivers fogColour as black** — hence always `mix(fogColour, col, fogVisibility)` via
  `bloxdApplyFog`, which is safe at visibility 1. Player “showFog off” pushes the band to
  3200–3328 **[3rd-party]**.
- **Open question, labelled honestly**: one community source says the ramp is linear
  (32×D→32×(D+1)); our older wiki note said EXP2. The linear figure comes from production-JS
  restoration and is more credible — but the definitive sonde measurement is pending. Neither
  affects thresholds that test `fogVisibility` directly.
- Fine checker patterns at chunk borders during loading = the engine’s Bayer 4×4 chunk fade,
  **not your bug**.

## Water optics (shipped-pack proven values)

- Beer–Lambert depth darkening `1 − exp(−0.32·d)` (≈⅓ at 1 block) **[shipped]**; the local P0
  plan used 0.45/0.08/0.03 (r/g/b) — both work, the single-scalar is friendlier.
- Schlick Fresnel with F0 = 0.02; broad sheen `0.05·pow(nDotH, 24)·sunUp` **[shipped]**.
- Registered water colour (0.5, 0.5, 0.8) / alpha 0.9 — rebuild alpha from it, don’t hardcode.

## Grading

- Lift curve `c·B/(1+c·(B−1))`: slope **B at black, exactly 1.0 at white** — white never clips.
  Breeze ships B = 1.45 **[shipped]**; our cinematic pack tuned B per-channel after fitting a
  tone curve to real frames.
- Vibrance with a chroma guard (`1 − chroma`) saturates dull pixels without oversaturating
  already-colourful ones.

## Why measure at all

Every shipped pack we dissected tunes by eye. Fitting your curve to actual captured frames
(linear regression on log–log luminance pairs) takes an afternoon and is the difference between
“vibes” and reproducible looks. See Part VI.

---

# Part V — Troubleshooting

## Compile-time

| Symptom | Cause / fix |
|---|---|
| `'mod' is a reserved word in WGSL` | rename or use `%` |
| `no definition in scope: bloxdOpaqueBehind` in your local harness | your harness stub is too narrow, not the pack — the symbol is real (shipped packs use it) |
| rejected `#define BLOXD_…` | engine-owned macros; pick another prefix |
| `direct struct construction` | you wrote `BloxdSurface{…}` — start from `bloxdDefaultSurface(...)` |
| `let _ =` rejected | v2 wants the bare form `_ = expr;` |
| naga passes, game rejects | browser Tint is stricter on precedence: parenthesise `a ^= b >> c`, mixed bitwise chains |
| pack silently ignored or import rejected | check, in order: `apiVersion` is the JSON number `2`; exactly one `pack.json` after the shared-root strip; manifest ≤65,536 bytes with a non-empty `name`; 1–256 `.wgsl` files totalling ≤262,144 UTF-8 bytes; zip ≤33,554,432 bytes/1,024 entries using stored/deflate only. A wrapper folder is fine only when **every** file shares it |
| imported but the world did not change | reload the page — pack changes are pending until reload; also confirm the game policy is not off/strict-off for your vertex/discard path and that the renderer did not fall back to WebGL |
| `alpha` member missing in one local variant | terrain+strict has no `BloxdSurface.alpha`; guard terrain alpha with `#ifdef BLOXD_ALPHA` (liquids always have it) |
| `bloxdOpaqueBehind` rejected outside liquids | call it only from liquid surface/light code under `#ifdef BLOXD_SCENE_DEPTH`; vertex reachability is an error |

## Loads but looks wrong

| Symptom | Cause / fix |
|---|---|
| nothing changes in some games | game policy can be off, strict or allow. Strict is default: a selected vertex hook or reachable `discard` turns that program's pack code off there while allow games keep it |
| plants don’t sway / can’t recolour | plants are drawn by a part of Bloxd packs can’t reach (confirmed by dissection); only block faces are yours |
| shadows/sky effects behave as if the sky were open | an unlit variant supplies `skyLight=1` with block/held/directional light at zero; gate sky logic with `#ifdef BLOXD_LIGHTING` when unlit must disable it |
| lamps stopped working | you darkened without a lamp guard (R4) |
| patterns slide/drift over time | missing `bloxdOriginOffset()` in your hash (R8), or un-wrapped `bloxdTime()` (R9) |
| water looks black in caves | sky-driven terms missing a `skyExposure` gate (R7) — reflections of a sky that isn’t there |
| NaN / black flicker at one camera angle | `normalize(toEye + sunDir)` is exactly zero when sun is opposite the eye — guard the length |
| checker pattern while chunks load | engine Bayer 4×4 fade, not yours |
| white blocks in fog mode 0 worlds | you used fogColour without `bloxdApplyFog` — it arrives black there |
| far-from-spawn textures shimmer/zoom | float precision: work in integer cells + rebase (R8) |

## Performance

- Per-fragment **loops** are the killer: a 6-step raymarch per pixel is fine gated to 10 m near
  trees, ruinous unbounded (this exact complaint is visible in workshop comments of the top pack).
- Fade every detail by distance (R10); skip work entirely when the gate is 0 (`if`, not `mix`).
- Per-cell hashing beats per-pixel noise for anything the eye reads as “texture”.

## Distribution

- Users must re-download the zip after every update — workshop “Updated 2 hours ago” spam is normal.
- Same filename ≠ same content: hash your zips if you care about reproducibility.
- v1 packs: **cannot** be loaded by the current game; migrate to `apiVersion: 2` (Part I).

---

# Part VI — Implementation & local validation

## Layout of a maintainable pack

```
my-pack/
├── pack.json
├── lib/hash.wgsl        # hashing + origin rebase (R8/R9)
├── terrain/*.wgsl       # one concern per file
├── water/*.wgsl
└── effects/*.wgsl
```

The importer sorts normalised `.wgsl` paths lexicographically before analysis. WGSL declarations
can be order-free, but pack `#define` flags are global and sequential: name files so any file
that sets a flag sorts before files that test it, or keep each flag's definition and use inside
one file. Keep `var<private>` state inside one concern, because surface→light is the only
intended fragment-local channel.

## Local pipeline (what to run before every release)

1. **Importer-shape check** — reproduce the pack root after the shared-folder strip; require
   exactly one `pack.json`, parse it as a JSON object, assert `apiVersion` is the number `2`,
   `name` is non-empty after trimming, manifest ≤65,536 UTF-8 bytes, 1–256 `.wgsl` files, no
   duplicate normalised path, and total WGSL ≤262,144 UTF-8 bytes.
2. **Concat check** — sort `.wgsl` paths exactly as the importer does and analyse that ordered
   stream, including the pack preprocessor rules (line-start directives only; valueless global
   `#define` flags; no `#define` inside a conditional).
3. **8-variant compile** — validate with the API v2 header stubbed per variant:
   allow/strict × lit/unlit × terrain/liquid, with `BLOXD_ALPHA` absent only in terrain+strict
   and `BLOXD_SCENE_DEPTH` present only for liquid. Stub every engine symbol you use; if the
   stub is missing one (e.g. `bloxdOpaqueBehind`), fix the stub, not the pack.
4. **Static checks** — reserved words (`mod`), `#define BLOXD_`, non-hook `bloxd*` names,
   literal header-struct construction, banned attributes/storage/texture types, `let _`,
   double-underscore identifiers and TODO markers.
5. **Loop/logic audit** — every per-fragment loop must be bounded AND gated by distance or
   blockId; every darkening factor must multiply by the lamp guard; every terrain alpha access
   sits under `BLOXD_ALPHA`; every depth access sits in liquid code under `BLOXD_SCENE_DEPTH`.
6. **Package** — prefer `pack.json` at the top level. If zipping, use stored/deflate entries
   only, no Zip64/encryption/multi-disk, ≤1,024 entries and ≤33,554,432 bytes. Record the
   zip's sha256; publish the hash with the release.
7. **In-game smoke test** — import, Apply, **reload**, then test day, night, cave, canopy,
   water edge, lava, a lamp, a sunless skybox and an unlit world. Screenshot each and compare
   against the previous release.
8. **Policy matrix** — test a strict/default game and an allow game if the pack uses vertex
   hooks or `discard`; the strict result is the baseline most players will see.

## Measuring instead of guessing

- Capture screenshots at fixed camera/world setups (a “probe world”): same seed, same time band.
- Fit your grade curve on log–log luminance pairs from captures; a handful of points drives a
  one-parameter lift (R5) precisely.
- Probe packs (temporary, never shipped): write engine quantities to colour channels —
  skyLight to red, blockLight to green, etc. — and read them back with a colour picker. This is
  how the tone-mapping thresholds of Part IV were measured.

## Release checklist

- [ ] `apiVersion: 2` as a JSON number; non-empty `name`; manifest ≤65,536 bytes
- [ ] 1–256 `.wgsl` files, sorted-path concat checked, total ≤262,144 UTF-8 bytes
- [ ] compiles 8/8 locally with the exact four-define variant matrix + Tint-paranoid parentheses
- [ ] no `#define BLOXD_`, no non-hook `bloxd*`, no literal header structs, no banned WGSL forms
- [ ] terrain alpha guarded by `BLOXD_ALPHA`; liquid depth guarded by `BLOXD_SCENE_DEPTH`
- [ ] strict baseline looks correct without vertex hooks or reachable `discard`
- [ ] lamp guard on every darkening term; all loops bounded + gated
- [ ] zip (if used): stored/deflate only, ≤1,024 entries, ≤33,554,432 bytes, sha256 published
- [ ] imported, Applied and page-reloaded before screenshots: day, night, cave, canopy, water,
      lava, lamp, sunless skybox, unlit world

# Part VII — Engine internals

Every item carries its provenance: **[measured]** local instruments · **[shipped]** proven by a
released pack in-game · **[client]** verified as a behavioural fact against the current public
web client's pack pipeline · **[3rd-party]** community-restored engine information that should
still be sanity-checked before becoming load-bearing.

## Time and space

- `bloxdTime()` is `performance.now()/1000 mod 3600` (`bloxdTimeWrap = 3600`), rewritten into
  the pack inputs every frame the Lite runtime runs. It is unrelated to any in-game clock
  **[client]**.
- Pack inputs are one 64-byte uniform block: `time` at byte 0, integer `originOffset` at 16,
  `sunDirection` at 32 and `eyePosition` at 48 (group 3, binding 0). Pack code should use the
  header accessors rather than depending on the raw layout. **[client]**
- The engine uses a **floating origin**: `bloxdOriginOffset()` returns the integer world rebase
  offset (the renderer is built on noa-engine). Any world-anchored pattern must add the offset
  into its hash input **[shipped]**.
- Day/night is not, by itself, a terrain-lighting model: directional lighting is a compiled
  per-vertex Lambert sum, while time-of-day colour for packs comes mainly from
  `bloxdSunDirection()`, `skyLightColour` and `ambientLightColour`. **[client]**

## Light pipeline

- Sky light levels run 0–15. For level `L`, let `x=L/15`; packs receive
  `1 − (1 − x/(3 − 2x))³`. The same curve exists on CPU and GPU paths. Level 14 is 0.9945.
  **[client]**
- `aPackedLightLevels` stores four 4-bit levels in base 16 inside a float; the decoded values
  are interpolated and curved per fragment. Each delivered colour channel is floored at
  **35 % of the brightest channel**. **[client]**
- Directional light is summed per vertex as `max(0, dot(N, dir)) × intensity` over the
  compiled directional-light list; the Lite renderer accepts up to four directional lights.
  **[client]**
- `heldLight` is conical: inside the cone it combines an angular falloff built from two
  smoothsteps with distance warped by power **0.75**; outside the cone it uses the plainer
  distance term, then an ambient boost and a final max-combine with sky/block light. **[client]**
- Block light properties (official scripting docs **[3rd-party-official]**): `lightEmission`
  0–15 (feeds the blockLight BFS) and `lightFilter` — 1 air-class / 3 fluid-class / 15 opaque —
  which is why rooms go dark and fluids dim gradients.
- Custom blocks can set `skyLightEmission` (0–15), which **injects into the skyLight channel
  itself**, outside the blockLight BFS — sun/shadow tests keyed on skyLight alone can be fooled
  in such worlds; combine with blockLight for robustness **[3rd-party]**.
- `l.ambient` = material.ambient × sceneAmbient (user setting, default 0.5) **[3rd-party]**.
- In unlit pack variants the header neutralises light inputs (`skyLight=1`, block/held/
  directional zero, white light colours) instead of removing the fields. **[client]**

## Surfaces and hook injection points

- **Vertex:** the hook receives world position, normal and `blockId`; its returned position
  replaces world position before projection, interpolated position and fog distance. Strict
  variants reject this path by switching the program's pack code off. **[client]**
- **Surface:** the hook runs after the atlas sample and vertex colour are combined, and before
  the alpha test and lighting. Its colour overwrites the base colour; no re-sampling is
  possible. Alpha is applied only where `BLOXD_ALPHA` provided the output field. **[client]**
- **Light:** the engine keeps a pre-fog colour, applies fog, then calls the hook before return
  with both engine colours available through the header fields. The hook's RGB replaces the
  final RGB; alpha is left unchanged. **[client]**
- `out.emission` is a surface-hook output; the default light result adds
  `emission × fogVisibility` to `engineColour`. **[client]**
- Fragments discarded by the Bayer chunk-fade before surface, or by the alpha test after
  surface, do not execute later pack stages. `blockId` is delivered to vertices only for
  programs carrying pack code. **[client]**
- Plants/grass/flowers render through a path **packs cannot reach** **[shipped]**.
- Chunk loading fades with the engine's **Bayer 4×4 screen-space dither**; fine checkers during
  load are not your bug **[client]**.

## Liquid depth snapshot

- `bloxdOpaqueBehind()` is the only special depth accessor. It is valid only when reachable
  from liquid surface/light under `BLOXD_SCENE_DEPTH`; vertex reachability is an error and
  terrain use asks for the guard. **[client]**
- The depth subsystem is installed only when the Lite renderer starts with an active pack
  variant requesting scene depth. Otherwise the accessor reports “nothing behind”. **[client]**
- When the current liquid variant requests depth and a visible blended liquid chunk exists,
  rendering is cut **before terrain transparencies**; depth already drawn (opaques, direct
  geometry and earlier transparencies) is converted into an R32Float texture at target size,
  then liquids draw. A liquid therefore cannot see itself, other liquids in that later pass, or
  transparencies drawn after the cut. **[client]**
- Hardware depth `d` is converted to positive view distance with near `n` and far `f` as
  `(f·n/(f−n)) / (2d + n/(f−n))`; `d ≤ 0` becomes 0/nothing. The pack reads the exact screen
  pixel; a positive value reconstructs the behind point along the eye→fragment ray and returns
  eye→behind `distance`. No behind colour is exposed. **[client]**

## IDs

- The render pipeline identifies blocks by **numeric `blockId : u32`** (Part VIII); the scripting
  API uses string ids — two namespaces for the same blocks.
- The id space **grows with updates**: a dump that ended at 2089 already misses shipped-pack ids
  up to 3254. Re-enumerate per release (Part VIII method).

## Sky

- Default worlds: static sun ≈ (−0.56, 0.81, −0.18); **moon = −sun**; sunless skyboxes deliver
  a zero sun vector **[3rd-party]**.
- Fog: linear 32-block band at the load border; default colour rgb(183,191,195); fogColour
  arrives **black** with fog mode NONE **[3rd-party]**. The ramp shape remains the labelled
  open question in Part IV; pack code should consume `fogVisibility` rather than re-derive it.

## Importer, storage, validation and runtime

- Import is the exact folder/zip pipeline in Part I: one manifest, sorted WGSL paths, strict
  UTF-8, byte caps, stored/deflate zip entries only, shared-root stripping, immediate
  validation and a required page reload before a changed pack takes effect. **[client]**
- The stored pack keeps the reduced manifest, a path→source map and the validation result. It
  is considered active only when validation succeeded **and** the stored header fingerprint
  still matches the current API v2 header; otherwise it is blocked (failed validation or no
  WebGPU validation device). **[client]**
- Validation runs the static analyser first. If that passes, a temporary WebGPU device builds
  one synthetic validation module per variant with dummy inputs, maps WGSL errors back to
  pack file/line, stores at most 100 errors plus the strict-off list, then destroys the device.
  Revalidation happens when the header fingerprint is stale and the stored pack has not changed
  underneath the check. **[client]**
- At page/game start the compiled page pack is reclassified and its eight variants regenerated;
  no real render pipeline is built there. The Lite renderer later builds the real material
  pipelines (including packed and unpacked atlas vertex forms), with a 60-second validation
  budget and cancellation polling; failures name the generated program. **[client]**
- Packs require the Lite WebGPU terrain path. An active pack is loaded before renderer creation
  and may force a WebGPU request unless a lost-device state is remembered; if rendering falls
  back to WebGL, no pack hooks run. Game policy then selects off/strict/allow per program. **[client]**
- Generated pack identifiers are prefixed internally, and `dpdy`-family derivatives are
  sign-corrected for the renderer's Y convention; neither detail changes the source-level API
  above. **[client]**

# Part VIII — The numeric block-id table

The render pipeline’s `blockId: u32` is the key to per-block shading. This table is curated for
shading work; regenerate the full list any time in-game:

```
for (i = 2; i < 3400; i++) api.log(i + " = " + api.blockIdToBlockName(i))
```

(paste into a Code Block; the id space grows with updates — a 2026 dump already ends at 2089
while shipped packs target ids up to 3254.)

## Shading-relevant groups (read-verified entries)

| Group | Ids |
|---|---|
| **Natural** | 2 Dirt · 3 Messy Dirt · 4 **Grass Block** · 5 Sand · 6 Clay · 7 Gravel · 8 Snow · 28 Stone · 29 Messy Stone · 31 Smooth Stone · 32-37 Diorite/Andesite/Granite (+smooth) · 38 Sandstone · 39 Yellowstone · 139 Ice · 140 Obsidian · 147 Bedrock · 650 Red Sand · 652 Rocky Dirt · 472 Useless Soil · 1295 Melting Ice |
| **Magma** | 471 **Magma** (the solid lava block) |
| **Ore / metals** | 40 Coal · 41 Iron · 42 Gold · 43 Lapis · 44 Emerald · 45 Diamond · 465 Moonstone Ore · blocks 46-50 · 172 Diamond · 470 Moonstone |
| **Leaves** | 100 Pine · 101 Aspen · 102 Maple · 103 Elm · 491 Plum · 492 Cedar · 493 Palm · 911 Pear · 653 Autumn Maple · 1226 Cherry · canopies 208-211, 494-496, 938, 654, 1259 |
| **Logs** | 9 Maple · 10 Pine · 11 Plum · 12 Cedar · 13 Aspen · 14 Elm · 502 Palm · 909 Pear · 1222 Cherry · stripped 21-26, 1112-1121 |
| **Plants** | **150 Grass** (the plant) · 151-163 flowers · **1109 Tall Grass** · 1110 Tall Grass\|Top · 149 Cactus · 213 Fat Cactus · 219 Vines · 105 Watermelon · 975 Pumpkin · 957 Cobweb |
| **Liquids** | **126 Water** · **1491 Lava** |
| **Light** | 124 Dim Lamp On · 125 Off · 143 Beacon · 164 Furnace · 168 Workbench · 980 Jack o’Lantern · 145 Golden Decoration · 146 Moonstone Explosive |
| **Glass** | 106 Glass · 107-122 the 16 tints · 992-1007 Patterned |
| **Coloured** | 51-66 Wool · 67-83 Baked Clay · 84-99 Concrete · 228-243 Planks · 245-308 Ceramic · 1040-1055 Carpet |
| **Special** | 0 Air · 1 Unloaded · 127 Invisible Solid · 1510 Code Block · 1512 worldedit-ghost |

## Live annex — ids beyond the 2026 dump (proven by a shipped pack)

A released pack (Breeze v1) targets these, none of which exist in the 2089-id dump — the game
grew; exact names pending a fresh dump:

- **Leaves** (their `isLeaf`): **1636 · 1969 · 2019 · 2020 · 2021 · 2022 · 2023 · 2024 · 2025 · 2085**
- **Grass Blocks** (their `isGrassBlock`): **1694 · 1955 · 3071 · 3072 · 3073 · 3253 · 3254**

## Gotchas

- **Two namespaces**: scripting uses string ids (`api.setBlock(...)`) — the shader’s u32 is the
  render id. Map via `api.blockIdToBlockName(i)` loops, never by guessing.
- Prefer **group switches** over equality: new biome variants arrive as new ids in the same
  family (see the annex).
- Id 4 = the grass **block** (top-face effects); 150 = the grass **plant** (unreachable — its
  sway is engine-side). Both have shipped-pack precedent.

---

# Part IX — Where this knowledge comes from (and what we don't know)

Every claim in this guide carries a provenance label. This page is the method behind the labels —
because a guide that tells you *how it knows* is worth ten that just assert.

## The four provenance classes

| Label | Meaning | Trust policy |
|---|---|---|
| **[measured]** | produced by local instruments: probe packs that write engine quantities into colour channels, screenshot pipelines with fixed camera/world setups, curve fitting on captured frames | trust within the measured envelope |
| **[shipped]** | proven by a released community pack running in the live game (e.g. Breeze v1, dissected file-by-file) | trust — the game itself accepted it |
| **[client]** | behavioural facts verified against the current public web client's shader-pack pipeline: importer limits, analyser rules, variant construction, storage/validation states, Lite injection points and liquid-depth semantics | trust for the client generation described; re-check after a client/API update |
| **[3rd-party]** | restored from production JS or community references outside the pack pipeline read above | never load-bearing until measured or promoted to **[client]**; cited because it guided probes |

## The instruments

- **8-variant naga harness** — the engine’s prelude stubbed per variant (strict/allow × lit/unlit
  × terrain/liquid). Every local release compiles 8/8 before it ships; that record has predicted
  in-game acceptance across dozens of releases.
- **42-case WGSL fuzz** — malformed shapes fed through the compiler to map what breaks naga vs
  what breaks the browser Tint (two different compilers; the game uses the browser’s).
- **Probe packs** (never shipped) — skyLight→red, blockLight→green, fog→blue; read back with a
  colour picker in controlled worlds. This is where the tone-mapping thresholds and the shadow
  band (13.6–14.95/15) come from.
- **Curve fitting** — capture frames at known setups, regress log–log luminance pairs, get the
  actual response curve instead of a guessed gamma.
- **Reverse-oracle dissection** — compile a *shipped* pack through our harness: every failure is
  our harness being wrong, not the pack (that is how `bloxdFaceBlock`, `bloxdOpaqueBehind`,
  `skyLightColour`, `litColour` and multi-file loading were confirmed).
- **Client-pipeline verification** — the importer, analyser, validation and Lite runtime facts
  were checked as one chain, from `pack.json` acceptance to the generated terrain/liquid
  programs and the liquid depth snapshot. Only behavioural facts and formulas are reported.
- **Cross-source triangulation** — a fact is only promoted when independent sources agree
  (community manual + shipped packs + client pipeline + probes). Disagreements are kept and
  labelled (see the fog ramp open question in Part IV).

## Honest open questions

1. **Fog ramp shape** — linear 32×D [3rd-party] vs EXP2 (older wiki note). Production-JS figure
   favoured; a dedicated sonde measurement is still the cleanest promotion path. Pack code that
   consumes `fogVisibility` directly is unaffected.
2. **New-id names** — ids up to 3254 are *used* by a shipped pack; official names await a fresh
   `api.blockIdToBlockName` dump.
3. **Future API versions** — until an importer/renderer generation accepts a new `apiVersion`,
   its hooks, structs, defines, caps and migration rules are unknown. This guide's exact numbers
   are API v2 numbers and must be re-verified, not extrapolated.

## Numbers behind this guide

Full numeric id table (0 → 3254+) · the complete six-hook API v2 contract · exact importer
byte caps and eight-variant define matrix · liquid depth semantics from accessor to snapshot ·
dozens of validated releases across two production packs · 2 shipped packs dissected to the
constant · every constant quoted carries its author credit.

---

<!-- CONSTANTS:START — generated by zz.py, do not edit by hand -->

# Part X — The constants register (EN)

## Engine-exposed variables (what the game gives you)

| Variable | Type / value | Meaning |
|---|---|---|
| `vertex.position` | vec3f | incoming world position of the corner (vertex hooks) |
| `vertex.normal` | vec3f | face normal at the corner |
| `vertex.blockId` | u32 | numeric block id at the corner |
| `outVertex.position` | vec3f | returned world position; replaces the corner before projection/fog distance |
| `surface.colour` | vec3f | incoming material colour after texture × vertex colour |
| `surface.alpha` | f32 | incoming alpha |
| `surface.normal` | vec3f | face normal |
| `surface.position` | vec3f | world position of the fragment |
| `surface.blockId` | u32 | numeric block id (Part VIII) |
| `out.alpha` | f32 | output alpha; field exists only under `BLOXD_ALPHA` (absent solely in terrain+strict) |
| `out.emission` | vec3f | self-glow, surface hook only |
| `light.litColour` | vec3f | surface's own lit colour |
| `light.engineColour` | vec3f | engine-combined colour used by the default light result before pack emission/fog handling |
| `light.directional` | f32 | directional-light scalar behind the engine result |
| `light.ambient` | vec3f | ambient term behind the engine result |
| `light.blockLight` | vec3f | block light colour (35% channel floor) |
| `light.skyLight` | f32 0..1 | exact curve `1 − (1 − x/(3 − 2x))³`, `x=level/15` (level 14≈0.9945) |
| `light.ambientLightColour` | vec3f | ambient light tint |
| `light.skyLightColour` | vec3f | sky tint; darkens at night |
| `light.heldLight` | vec3f | handheld light (conical, distance warped ^0.75) |
| `light.fogColour` | vec3f | fog colour; **black when fog mode is NONE** |
| `light.fogVisibility` | f32 | engine fog factor |
| `light.position` | vec3f | world position in the light hook |
| `light.normal` | vec3f | face normal in the light hook |
| `light.blockId` | u32 | numeric block id in the light hook |
| `bloxdTimeWrap` | f32 = **3600** | wrap period of `bloxdTime()` (seconds) |
| `bloxdDefaultVertex(in)` | BloxdVertex | unchanged vertex result — mandatory starting point for vertex hooks |
| `bloxdOriginOffset()` | vec3i | floating-origin rebase; inject into world hashes |
| `bloxdSunDirection()` | vec3f | unit sun vector; zero on sunless skies; moon = −this |
| `bloxdFaceBlock(p,n)` | vec3i | cell (block coordinates) of the current face — per-block hash input; the id itself is `surface.blockId` / `light.blockId` |
| `bloxdOpaqueBehind()` | {found,position,distance} | liquid-only opaque point behind the exact pixel; `distance` is eye→behind |
| `bloxdEyePosition()` | vec3f | camera position |
| `bloxdApplyFog(c,l)` | vec3f | mix(fogColour, c, fogVisibility) |

## Engine-internal figures every pack author needs

| Figure | Value | Provenance |
|---|---|---|
| time source | `performance.now()/1000 mod 3600` | [client] |
| light scale | integer levels 0–15, open sky = 15 | [client + measured] |
| skyLight curve | `x=level/15`; `1 − (1 − x/(3 − 2x))³`; level 14 = 0.9945 | [client] |
| packed-light channel floor | 35 % of max channel | [client] |
| pack defines | `BLOXD_STRICT`; `BLOXD_LIGHTING`; `BLOXD_SCENE_DEPTH` liquid-only; `BLOXD_ALPHA` absent only terrain+strict | [client] |
| manifest cap | 65,536 bytes after decompression; `apiVersion` exactly number 2 | [client] |
| WGSL caps | 1–256 files; 262,144 bytes total after decompression | [client] |
| zip caps | 33,554,432 bytes; 1,024 entries; stored/deflate only | [client] |
| stored validation errors | 100 plus overflow count | [client] |
| fog band | start 32×D, end 32×(D+1) (linear per 3rd-party; EXP2 legacy note — open question) | [3rd-party] |
| default fog colour | rgb(183, 191, 195) | [3rd-party] |
| showFog off | band pushed to 3200–3328 | [3rd-party] |
| scene ambient default | 0.5 (user setting) | [3rd-party] |
| Lite directional lights | up to 4 compiled directional lights; per-vertex Lambert sum | [client] |



## cinematic-v5 (local pack — frozen baseline) — 183 constants

| Constant | Value | Role |
|---|---|---|
| `TR_ALT_HAZE` | 0.15 | altitude haze: veil strength above 55 blocks |
| `TR_AURORA_WATER` | 0.08 | water: night aurora reflection strength (in our reflection only) |
| `TR_BACKLIGHT` | 0.18 | backlight: strength of vegetation against-sun glow |
| `TR_BACKLIGHT_COL` | vec3f(1.0, 0.62, 0.28) | backlight: warm glow colour |
| `TR_BAT_CHANCE` | 0.12 | bats: share of air cells at dusk |
| `TR_BAT_COL` | vec3f(0.10, 0.09, 0.08) | bats: dark silhouette colour |
| `TR_BAT_ROAM` | 0.8 | bats: erratic roaming radius |
| `TR_BAT_SIZE` | 0.09 | bats: body size |
| `TR_BAT_T_WING` | 9.424778 | bats: fast wing-beat speed (wrap-locked) |
| `TR_BFLY_BODY` | 0.012 | butterflies: body sliver half-width |
| `TR_BFLY_CHANCE` | 0.25 | butterflies: share of air cells holding one |
| `TR_BFLY_COL1` | vec3f(0.95, 0.93, 0.85) | butterflies: white variant |
| `TR_BFLY_COL2` | vec3f(0.98, 0.85, 0.30) | butterflies: yellow variant |
| `TR_BFLY_COL3` | vec3f(0.90, 0.55, 0.25) | butterflies: orange variant |
| `TR_BFLY_GAP` | 0.035 | butterflies: half-separation of the two wings |
| `TR_BFLY_ROAM` | 0.4 | butterflies: roaming radius around the cell |
| `TR_BFLY_SIZE` | 0.05 | butterflies: body size |
| `TR_BFLY_TALL` | 1.35 | butterflies: wing-disc height ratio |
| `TR_BFLY_T_WING` | 3.1415927 | butterflies: wing-beat angular speed (wrap-locked) |
| `TR_BUG_COL` | vec3f(0.72, 0.06, 0.05) | ladybugs: shell red |
| `TR_BUG_SHARE` | 0.12 | butterflies: share that are ladybugs instead |
| `TR_CANOPY_HI` | 0.9995 | tree-effect window: skyLight of open sky (fields stay bare) |
| `TR_CANOPY_LO` | 0.90 | tree-effect window: minimum skyLight (caves stay bare) |
| `TR_CINEMA_BOOST` | 1.6 | cinema mode: multiplier on golden mist and backlight |
| `TR_CINEMA_MODE` | false | cinema mode: false = normal, true = boosted atmosphere |
| `TR_EDGE_AO` | 0.92 | edge AO strength (skyLight-weighted by law) |
| `TR_EMBER_CHANCE` | 0.18 | lava: share of cells emitting rising embers |
| `TR_EMBER_HEIGHT` | 2.2 | lava: ember rise height (blocks) |
| `TR_EMBER_SIZE` | 0.03 | lava: ember angular size at 1 block |
| `TR_EMBER_T_RISE` | 4.0 | lava: ember rise period (must divide 3600) |
| `TR_EPSILON` | 0.0001 | generic epsilon guard |
| `TR_FLY_CHANCE` | 0.18 | fireflies: share of air cells holding one |
| `TR_FLY_COLOUR` | vec3f(1.0, 0.85, 0.45) | fireflies: glow colour |
| `TR_FLY_SIZE` | 0.035 | fireflies: glow dot radius |
| `TR_FLY_W_BLINK` | 0.0698132 | fireflies: blink angular speed (wrap-locked) |
| `TR_FLY_W_BOB` | 0.7853981 | fireflies: hover bobbing angular speed (wrap-locked) |
| `TR_GLASS_MIRROR` | 0.30 | glass: sky reflection strength (fresnel) |
| `TR_GLASS_RIM` | 0.22 | glass: grazing-angle edge brightening |
| `TR_GOLDEN_GAIN` | 0.50 | golden-hour gain |
| `TR_GOLDEN_TINT` | vec3f(1.06, 1.005, 0.90) | golden-hour tint |
| `TR_GRAIN` | 0.0 | film grain amount (distance-faded) |
| `TR_HZN_CLOUD_STR` | 0.45 | horizon cloud bank strength |
| `TR_LAMP_FLICKER` | 0.10 | lamp flicker: spill modulation depth (0 = off) |
| `TR_LAMP_SOFT_AO` | 0.55 | lamp softening: edge-AO kept near lamps |
| `TR_LAMP_SOFT_GAIN` | 2.5 | lamp softening: blockLight to wash-factor gain |
| `TR_LAMP_SOFT_GRAIN` | 0.5 | lamp softening: grain kept near lamps |
| `TR_LAVA_FLOW_SCALE` | 0.55 | lava: viscous flow texture scale (much slower than water) |
| `TR_LEAF_AUTUMN` | 0.12 | falling leaves: share of autumn-tinted leaves |
| `TR_LEAF_AUTUMN_GOLD` | vec3f(0.87, 0.60, 0.16) | falling leaves: autumn golden tint |
| `TR_LEAF_AUTUMN_RUST` | vec3f(0.62, 0.28, 0.09) | falling leaves: autumn rust tint |
| `TR_LEAF_BACKLIT` | 0.35 | falling leaves: backlit glow when sun is behind |
| `TR_LEAF_CELL` | 3.0 | falling leaves: air-cell size (one leaf max per cell) |
| `TR_LEAF_CHANCE` | 0.3 | falling leaves: share of cells holding a leaf |
| `TR_LEAF_DRIFT` | 0.06 | falling leaves: downwind drift (cloud direction) |
| `TR_LEAF_FADE_LO` | 5.0 | falling leaves: distance where fading starts |
| `TR_LEAF_FALL` | 0.6 | falling leaves: fall speed (must equal WRAP*CELL/3600 exactly) |
| `TR_LEAF_FLUTTER` | 0.15 | falling leaves: vertical flutter amplitude |
| `TR_LEAF_GUST` | 0.5 | falling leaves: sway boost during gusts |
| `TR_LEAF_LEN` | 1.7 | falling leaves: leaf length/width aspect |
| `TR_LEAF_LOD_SHRINK` | 0.45 | falling leaves: distant shrink share |
| `TR_LEAF_ON` | true | feature toggle: falling leaves |
| `TR_LEAF_RANGE` | 10.0 | falling leaves: draw distance from the eye |
| `TR_LEAF_RIM` | 0.22 | falling leaves: centre rim-light strength |
| `TR_LEAF_SIZE` | 0.09 | falling leaves: leaf half-width |
| `TR_LEAF_SIZE_VAR` | 0.30 | falling leaves: per-leaf size variation (+/-) |
| `TR_LEAF_STEPS` | 6 | falling leaves: ray-march samples along the view line |
| `TR_LEAF_TIP` | 0.55 | falling leaves: pointed-tip taper strength |
| `TR_LEAF_TWOTONE` | 0.18 | falling leaves: per-leaf two-tone variation |
| `TR_LEAF_WRAP` | 720 | falling leaves: y-cell wrap for a seamless 3600 s loop |
| `TR_LEAF_W_FLIP` | 2.199115 | falling leaves: flip angular speed (wrap-locked) |
| `TR_LEAF_W_GUST` | 0.1047197 | falling leaves: gust cycle angular speed (wrap-locked) |
| `TR_LEAF_W_SPIN` | 1.600467 | falling leaves: spin angular speed (wrap-locked) |
| `TR_LEAF_W_SWAY_A` | 1.300270 | falling leaves: sway angular speed x (wrap-locked) |
| `TR_LEAF_W_SWAY_B` | 0.900590 | falling leaves: sway angular speed z (wrap-locked) |
| `TR_LITTER_DENS` | 0.82 | leaf litter: share of cells left bare |
| `TR_LITTER_MIX` | 0.22 | leaf litter: ground blend strength under canopy |
| `TR_LITTER_SCALE` | 3.0 | leaf litter: speckle cells per block |
| `TR_MIST_GOLDEN` | 0.10 | aerial perspective / mist |
| `TR_MIST_GOLDEN_COL` | vec3f(0.93, 0.96, 1.0) | aerial perspective / mist |
| `TR_MIST_GROUND` | 0.12 | ground mist: strength at golden hour |
| `TR_MIST_GROUND_BAND` | 3.5 | ground mist: height band around the eye (blocks) |
| `TR_MIST_GROUND_COL` | vec3f(0.93, 0.96, 1.0) | ground mist: veil colour |
| `TR_MIST_GROUND_HI` | 90.0 | ground mist: distance fade end (blocks) |
| `TR_MIST_GROUND_LO` | 16.0 | ground mist: distance fade start (blocks) |
| `TR_MOONLIGHT` | vec3f(0.30, 0.38, 0.55) | moonlight tint |
| `TR_MOON_COLUMN` | 0.10 | water: moonlight column strength on the river |
| `TR_MOON_GAIN` | 0.30 | moonlight gain |
| `TR_MOTE_CHANCE` | 0.2 | air motes: share of cells holding one (cave spores / day pollen) |
| `TR_MOTE_COL` | vec3f(0.55, 0.75, 1.0) | air motes: cave spore colour |
| `TR_MOTE_SIZE` | 0.035 | air motes: angular size at 1 block |
| `TR_POLLEN_COL` | vec3f(1.0, 0.85, 0.45) | air motes: golden pollen colour |
| `TR_RELIEF_EPS` | 0.30 | relief-mapping step epsilon |
| `TR_RELIEF_GAIN` | 1.6 | relief lighting gain |
| `TR_RELIEF_HEIGHT` | 0.16 | relief heightfield amplitude |
| `TR_RELIEF_SCALE` | 1.7 | relief-mapping height scale |
| `TR_SCOTO` | 0.5 | scotopic (rod-vision) mixing strength |
| `TR_SKY2_BAND_A` | -0.22 | sun elevation: full night below this |
| `TR_SKY2_BAND_B` | -0.04 | sun elevation: twilight begins here |
| `TR_SKY2_BAND_C` | 0.10 | sun elevation: day begins here |
| `TR_SKY2_BAND_D` | 0.30 | sun elevation: full day above this |
| `TR_SKY2_GLOW_DAWN` | vec3f(1.0, 0.70, 0.38) | dawn sun-glow colour |
| `TR_SKY2_GLOW_DUSK` | vec3f(1.0, 0.50, 0.26) | dusk sun-glow colour |
| `TR_SKY2_GLOW_NIGHT` | vec3f(0.50, 0.62, 0.92) | moon-glow colour |
| `TR_SKY2_NIGHT_LOW` | vec3f(0.07, 0.10, 0.20) | night sky horizon colour (deep blue) |
| `TR_SKY2_NIGHT_TOP` | vec3f(0.01, 0.02, 0.06) | night sky zenith colour |
| `TR_SKY2_TWI_LOW` | vec3f(0.98, 0.62, 0.42) | twilight sky horizon colour (peach-gold) |
| `TR_SKY2_TWI_TOP` | vec3f(0.34, 0.34, 0.62) | twilight sky zenith colour (mauve) |
| `TR_SKYF_CURVE` | 1.6 | sky-fog: elevation-curve steepness (Blocky Day proven) |
| `TR_SKYF_FOG_MIX` | 0.9 | sky-fog: share of the engine fog colour replaced by the sky gradient |
| `TR_SKYF_GLOW` | 0.55 | sky-fog: sun-glow strength (Blocky Day HORIZON_GLOW) |
| `TR_SKYF_GLOW_COL` | vec3f(1.00, 0.78, 0.50) | sky-fog: sun-glow colour inside the fake sky |
| `TR_SKYF_HAZE_DESAT` | 0.10 | aerial-haze grey desaturation (lower = bluer sky feel) |
| `TR_SKYF_HORIZON_MIX` | 0.85 | sky-fog: horizon haze blend into the fake sky |
| `TR_SKYF_LOW` | vec3f(0.70, 0.80, 0.96) | sky-fog: fake-sky horizon colour (Blocky Day proven) |
| `TR_SKYF_TOP` | vec3f(0.25, 0.45, 0.85) | sky-fog: fake-sky zenith colour (Blocky Day proven) |
| `TR_SOFTEN_AMOUNT` | 0.0 | face-speckle smoothing strength (anti-seam) |
| `TR_SOFTEN_GRAIN_NEAR` | 14.0 | distance where the fine grain layer stops |
| `TR_SOFTEN_LEVEL` | 0.5 | brightness smoothed faces settle towards |
| `TR_SOFTEN_MIST` | 0.0 | soft cloud-blotch strength on faces |
| `TR_SOFTEN_MIST_FAR` | 48.0 | distance where blotches fade out |
| `TR_SOFTEN_MIST_SIZE` | 5.0 | blotch frequency per block |
| `TR_SPLASH_BRIGHT` | 1.6 | lava: droplet brightness |
| `TR_SPLASH_CHANCE` | 0.35 | lava: share of cells with an active splash source |
| `TR_SPLASH_COL` | vec3f(1.0, 0.55, 0.15) | lava: droplet colour |
| `TR_SPLASH_HEIGHT` | 0.45 | lava: droplet apex height |
| `TR_SPLASH_SIZE` | 0.045 | lava: droplet angular size at 1 block |
| `TR_SPLASH_TRAIL` | 0.05 | lava: trail spacing behind the drop (fraction of cycle) |
| `TR_SPLASH_T_RISE` | 3.0 | lava: rise-and-fall period (must divide 3600) |
| `TR_SWAY_FLOWER_HI` | 163u | flower id range end (sway gate) |
| `TR_SWAY_FLOWER_LO` | 151u | flower id range start (sway gate) |
| `TR_SWAY_VINE_W` | 0.5 | vine sway weight (id 219) |
| `TR_VIBRANCE` | 0.16 | pre-fog grade (lift + chroma-guarded vibrance) |
| `TR_WATER_CLARITY` | 0.82 | water clarity (view-through) |
| `TR_WATER_DAY_TINT` | vec3f(0.34, 0.78, 0.82) | water tint, day band |
| `TR_WATER_DUSK_TINT` | vec3f(0.20, 0.48, 0.66) | water tint, dusk band |
| `TR_WATER_GLINT` | 0.82 | sun glint strength |
| `TR_WATER_MIRROR_CAP` | 1.05 | water optics |
| `TR_WATER_MIRROR_CHROMA` | 0.80 | water optics |
| `TR_WATER_MIRROR_PRESS` | 1.60 | water optics |
| `TR_WATER_MOON_GLINT` | vec3f(0.48, 0.66, 0.88) | water optics |
| `TR_WATER_NIGHT_TINT` | vec3f(0.075, 0.19, 0.34) | water tint, night band |
| `TR_WATER_REFLECTIVITY` | 0.78 | water reflectivity |
| `TR_WATER_RIPPLE` | 0.105 | ripple amplitude |
| `TR_WATER_TINT` | 0.48 | water tint mix strength |
| `TR_WAVE_OMEGA_A` | 0.502655 | wave band A angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_B` | 0.726057 | wave band B angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_C` | 0.949459 | wave band C angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_D` | 1.605703 | wave band D angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_E` | 1.982694 | wave band E angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_F` | 2.415536 | wave band F angular frequency (frozen R17) |
| `TR_WAVE_SWELL_AMP` | 0.15 | water: long swell normal amplitude |
| `TR_WAVE_SWELL_FOAM` | 0.20 | water: foam strength on swell crests |
| `TR_WAVE_SWELL_SCALE` | 0.10 | water: swell spatial frequency (radians per block) |
| `bloom_spill` | 0.5 | bloom bleed amount |
| `cloud_height` | 100.0 | cv5 cloud layer altitude |
| `cloud_scale` | 0.006 | cv5 cloud noise scale |
| `cloud_speed` | vec2f(1.2, 0.7) | cv5 cloud drift speed (x,y) |
| `cloud_strength` | 0.3 | cv5 2D cloud layer strength |
| `grade_contrast` | 0.16 | final contrast offset |
| `grade_saturation` | 1.2 | final saturation multiplier |
| `grass_id` | 150u | the decorative grass PLANT block id (per-block sway gate) |
| `haze_base_height` | 40.0 | fog reference altitude |
| `haze_density` | 0.006 | height-fog density |
| `haze_height_falloff` | 0.012 | fog altitude falloff |
| `haze_strength` | 0.48 | height-fog strength |
| `hot_glow_strength` | 0.2 | lava/hot-emitter glow |
| `leaf_glow` | 0.6 | leaf translucency glow |
| `luma` | vec3f(0.299, 0.587, 0.114) | Rec.709 luminance weights |
| `ray_sky_max` | 0.90 | god-ray sky exposure gate high |
| `ray_sky_min` | 0.60 | god-ray sky exposure gate low |
| `ray_strength` | 0.3 | god-ray strength |
| `shadow_ambient_drop` | 0.55 | ambient loss inside shadow |
| `shadow_softness` | 0.04 | shadow edge softness |
| `shadow_strength` | 0.85 | directional shadow strength |
| `shadow_threshold` | 0.95 | skyLight threshold where shadows start |
| `shadow_tint` | vec3f(0.62, 0.74, 1.0) | shadow cool tint |
| `sun_fallback` | vec3f(0.42, 0.85, 0.0) | sun tint when skyLightColour is unavailable |
| `sway_amount` | 0.3 | sway amplitude factor |
| `sway_mode` | 2 | sway implementation selector; 2 = colour-only (runs everywhere) |
| `sway_speed` | 1.0 | sway time multiplier |
| `tall_grass_id` | 1109u | Tall Grass plant id (same gate) |
| `tall_grass_top_id` | 1110u | Tall Grass top-half block id (sway gate) |
| `underwater_strength` | 0.30 | underwater colour grade strength |

## titan-bsl-ultra-v2 (local pack — sky/cloud/water showcase) — 288 constants

| Constant | Value | Role |
|---|---|---|
| `TR_AERIAL_DESAT` | 0.55 | aerial perspective / mist |
| `TR_AERIAL_SCALE` | 46.0 | aerial perspective / mist |
| `TR_AERIAL_SLANT` | 1.35 | aerial perspective / mist |
| `TR_AERIAL_STRENGTH` | 0.22 | aerial perspective / mist |
| `TR_AIR_SCATTER` | 0.055 | aerial perspective / mist |
| `TR_AMBIENT_HUE_AMOUNT` | 0.45 | bounce/ambient hue shaping |
| `TR_AO_EDGE_MIN` | 0.10 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_EDGE_SOFT` | 2.60 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_LEVEL_HIGH` | 14.60 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_LEVEL_LOW` | 3.00 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_SHADE_FLOOR` | 0.34 | ambient-occlusion system (skyLight-weighted) |
| `TR_AURORA_A` | vec3f(0.22, 0.95, 0.55) | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_B` | vec3f(0.85, 0.30, 0.95) | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_GAIN` | 0.34 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_HIGH` | 0.62 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_LOW` | 0.06 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_BACKLIGHT` | 0.30 | backlight: strength of vegetation against-sun glow |
| `TR_BLOCK_AMBIENT` | 0.55 | block-light ambient & roughness response |
| `TR_BLOCK_ROUGH_SPREAD` | 0.06 | block-light ambient & roughness response |
| `TR_BLOCK_VARIATION` | 0.018 | per-block / per-cell brightness variation |
| `TR_BOUNCE_AMBIENT_HUE` | vec3f(1.05, 0.99, 0.925) | bounce/ambient hue shaping |
| `TR_BUMP_STRENGTH` | 0.85 | micro-detail & terrain normal work |
| `TR_CANOPY_DAPPLE` | 0.55 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_OPEN_HI` | 0.85 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_OPEN_LO` | 0.35 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_SCALE` | 0.36 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_SWIRL` | 0.351111 | tree-canopy shadow (lost skyLight level) |
| `TR_CAUSTIC_COLOUR` | vec3f(0.62, 0.94, 0.86) | water caustics on flooded ground |
| `TR_CAUSTIC_DISP_B` | 0.80 | water caustics on flooded ground |
| `TR_CAUSTIC_DISP_R` | 1.25 | water caustics on flooded ground |
| `TR_CAUSTIC_FALLOFF` | 0.22 | water caustics on flooded ground |
| `TR_CAUSTIC_FAST` | 0.30 | water caustics on flooded ground |
| `TR_CAUSTIC_SCALE` | 0.22 | water caustics on flooded ground |
| `TR_CAUSTIC_SPIN` | 0.508889 | water caustics on flooded ground |
| `TR_CIRRUS_DENSITY` | 0.62 | cirrus layer |
| `TR_CIRRUS_GAIN` | 0.30 | cirrus layer |
| `TR_CIRRUS_HEIGHT` | 420.0 | cirrus layer |
| `TR_CIRRUS_SCALE` | 0.0022 | cirrus layer |
| `TR_CLOUD_AMBIENT_DIM` | 0.22 | ambient dimming under cloud shadow |
| `TR_CLOUD_BOTTOM_COLOUR` | vec3f(0.40, 0.45, 0.58) | volumetric clouds (marching & lighting) |
| `TR_CLOUD_COVERAGE` | 0.46 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_FILL` | vec3f(0.26, 0.33, 0.46) | volumetric clouds (marching & lighting) |
| `TR_CLOUD_HEIGHT` | 190.0 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_MIN_SUN` | 0.06 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_OPACITY` | 0.88 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_POWDER` | 1.60 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_POWDER_GAIN` | 0.35 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_RAY_MAX` | 6000.0 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SCALE` | 0.0086 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SELF_SHADOW` | 0.70 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_DRIFT` | 0.022222 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_GAPS` | 0.85 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_SCALE` | 0.026 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_STEP` | 34.0 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_STRENGTH` | 0.62 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SILVER` | 0.45 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SOFTNESS` | 0.16 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SPEED` | 0.55 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_TOP_COLOUR` | vec3f(1.00, 0.99, 0.96) | volumetric clouds (marching & lighting) |
| `TR_CLOUD_WIND` | vec2f(0.82, 0.57) | volumetric clouds (marching & lighting) |
| `TR_CLUMP_SCALE` | 0.034 | foliage clumping |
| `TR_CLUMP_STRENGTH` | 1.00 | foliage clumping |
| `TR_CLUMP_TINT` | 0.55 | foliage clumping |
| `TR_DEBUG_MODE` | 0 | debug visualisation selector (0 = off) |
| `TR_DETAIL_FAR` | 0.45 | dither & LOD detail fades |
| `TR_DETAIL_NEAR` | 0.06 | dither & LOD detail fades |
| `TR_DITHER` | 0.0035 | dither & LOD detail fades |
| `TR_DIVE_MIRROR` | vec3f(0.020, 0.110, 0.150) | underwater mirror pass strength |
| `TR_EDGE_CREASE` | 0.26 | micro-detail & terrain normal work |
| `TR_EDGE_WIDTH` | 0.18 | micro-detail & terrain normal work |
| `TR_EMISSION_AMBER_HI` | 0.50 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_AMBER_LO` | 0.30 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_BRIGHT` | 0.88 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_DARK_LO` | 0.38 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_DIM` | 0.58 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_FIERY_HI` | 0.85 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_FIERY_LO` | 0.65 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_GOLD_HI` | 2.20 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_GOLD_LO` | 1.40 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_SAT_HI` | 0.80 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_SAT_LO` | 0.30 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_SELF_LIGHT` | 0.45 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_STRENGTH` | 1.25 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_UNCONFIRMED` | 0.15 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_WARM_HI` | 1.62 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_WARM_LO` | 1.16 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EPSILON` | 0.000001 | generic epsilon guard |
| `TR_EXPOSURE` | 0.96 | tone mapping & grade |
| `TR_F0_DIELECTRIC` | 0.04 | PBR material set (GGX F0/roughness/sheen) |
| `TR_FACE_CONTRAST` | 0.30 | per-face variation phases |
| `TR_FACE_PHASE_A` | 0.6180339887 | per-face variation phases |
| `TR_FACE_PHASE_B` | 0.7548776662 | per-face variation phases |
| `TR_FIRE_FLICKER` | 0.16 | fire flicker animation |
| `TR_FIRE_PHASE` | 41.0 | fire flicker animation |
| `TR_FOLIAGE_NORMAL_HIGH` | 0.85 | animated foliage normals |
| `TR_FOLIAGE_NORMAL_LOW` | 0.25 | animated foliage normals |
| `TR_GLARE_DESAT` | 0.70 | bloom glare shaping |
| `TR_GLARE_FULL` | 1.05 | bloom glare shaping |
| `TR_GLARE_KNEE` | 0.55 | bloom glare shaping |
| `TR_GRADE_CONTRAST` | 0.45 | tone mapping & grade |
| `TR_GRADE_FILMIC` | 0.45 | tone mapping & grade |
| `TR_GRADE_HIGHLIGHT_DESAT` | 0.25 | tone mapping & grade |
| `TR_GRADE_NIGHT` | vec3f(0.60, 0.80, 1.14) | tone mapping & grade |
| `TR_GRADE_NIGHT_MIX` | 0.45 | tone mapping & grade |
| `TR_GRADE_SATURATION` | 1.10 | tone mapping & grade |
| `TR_GRADE_SHADOW_RANGE` | 0.38 | tone mapping & grade |
| `TR_GRADE_SHADOW_TINT` | vec3f(0.93, 0.975, 1.08) | tone mapping & grade |
| `TR_GRADE_VIBRANCE` | 0.38 | pre-fog grade (lift + chroma-guarded vibrance) |
| `TR_GRASS_GLINT_F0` | 0.045 | specular glint on grass |
| `TR_GRASS_GLINT_GAIN` | 0.55 | specular glint on grass |
| `TR_GRASS_GLINT_ROUGH` | 0.40 | specular glint on grass |
| `TR_GUST_BREATHE` | 0.675556 | wind gust field |
| `TR_GUST_SCALE` | 0.020 | wind gust field |
| `TR_GUST_SHADE` | 0.26 | wind gust field |
| `TR_GUST_SPEED` | 1.500000 | wind gust field |
| `TR_LAMP_WOBBLE` | 0.05 | lamp light wobble |
| `TR_LEAF_NORMAL_FLUTTER` | 1.240000 | animated foliage normals |
| `TR_LEAF_NORMAL_RATE` | 0.42 | animated foliage normals |
| `TR_LEAF_NORMAL_STRENGTH` | 0.60 | animated foliage normals |
| `TR_LEAF_NORMAL_TIME` | 0.413333 | animated foliage normals |
| `TR_LOCAL_KEEP` | 0.85 | lighting framework (keep/unlit/night/shelter) |
| `TR_LOOP_CELLS` | 8.0 | wrap-lock (time/precision loops) |
| `TR_LOOP_SECONDS` | 3600.0 | wrap-lock (time/precision loops) |
| `TR_MAGMA_CORE` | vec3f(1.000, 0.800, 0.300) | magma/lava material & LOD |
| `TR_MAGMA_CRUST` | vec3f(0.030, 0.006, 0.001) | magma/lava material & LOD |
| `TR_MAGMA_GAIN` | 1.30 | magma/lava material & LOD |
| `TR_MAGMA_HOT` | vec3f(1.000, 0.250, 0.030) | magma/lava material & LOD |
| `TR_MAGMA_LOD_FAR` | 80.0 | magma/lava material & LOD |
| `TR_MAGMA_LOD_NEAR` | 12.0 | magma/lava material & LOD |
| `TR_MAGMA_SCALE` | 0.30 | magma/lava material & LOD |
| `TR_MAGMA_WARP` | 4.00 | magma/lava material & LOD |
| `TR_MAT_GRASS_F0` | 0.042 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_GRASS_ROUGH` | 0.90 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_MOSS_F0` | 0.035 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_MOSS_ROUGH` | 0.92 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SAND_F0` | 0.045 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SAND_ROUGH` | 0.94 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SHEEN` | 0.032 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SHEEN_POWER` | 3.0 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SNOW_F0` | 0.030 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SNOW_ROUGH` | 0.72 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_STONE_F0` | 0.040 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_STONE_ROUGH` | 0.92 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_WET_F0` | 0.055 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_WET_ROUGH` | 0.24 | PBR material set (GGX F0/roughness/sheen) |
| `TR_METEOR_GAIN` | 1.60 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_METEOR_PERIOD` | 48.0 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_METEOR_TRAIL` | 90.0 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_MICRO_DETAIL_SCALE` | 1.35 | micro-detail & terrain normal work |
| `TR_MICRO_DETAIL_STRENGTH` | 0.20 | micro-detail & terrain normal work |
| `TR_MICRO_ROUGHNESS` | 0.14 | micro-detail & terrain normal work |
| `TR_MIE_OPEN_HI` | 0.80 | aerial perspective / mist |
| `TR_MIE_OPEN_LO` | 0.30 | aerial perspective / mist |
| `TR_MIE_STRENGTH` | 0.22 | aerial perspective / mist |
| `TR_MIST_BASE` | 56.0 | aerial perspective / mist |
| `TR_MIST_SCALE` | 9.0 | aerial perspective / mist |
| `TR_MIST_STRENGTH` | 0.10 | aerial perspective / mist |
| `TR_MIST_SUN` | 0.30 | aerial perspective / mist |
| `TR_MOON_COLOUR` | vec3f(0.62, 0.72, 1.00) | night/moon ambient system |
| `TR_MOON_DIFFUSE` | 0.30 | night/moon ambient system |
| `TR_MOON_DISC_GAIN` | 4.20 | moon disc & ring render |
| `TR_MOON_DISC_HI` | 0.99975 | moon disc & ring render |
| `TR_MOON_DISC_LO` | 0.99920 | moon disc & ring render |
| `TR_MOON_OPEN_HI` | 0.70 | night/moon ambient system |
| `TR_MOON_OPEN_LO` | 0.25 | night/moon ambient system |
| `TR_MOON_REDDEN` | 0.80 | night/moon ambient system |
| `TR_MOON_RING_GAIN` | 0.32 | moon disc & ring render |
| `TR_MOON_RING_HI` | 0.99920 | moon disc & ring render |
| `TR_MOON_RING_LO` | 0.99780 | moon disc & ring render |
| `TR_MW_GAIN` | 0.10 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_MW_SCALE` | 2.60 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_MW_TILT` | vec3f(0.42, 0.86, -0.28) | night-sky features (stars/milky way/aurora/meteors) |
| `TR_NIGHT_AMBIENT` | 0.46 | night/moon ambient system |
| `TR_NIGHT_AMBIENT_LIFT` | 1.00 | night/moon ambient system |
| `TR_NIGHT_DIM` | 0.92 | lighting framework (keep/unlit/night/shelter) |
| `TR_NOISE_ORIGIN` | vec2f(31.7, 71.3) | hash origin salt |
| `TR_NOISE_WRAP` | 256.0 | maths/noise plumbing |
| `TR_NOISE_WRAP_INV` | 0.00390625 | maths/noise plumbing |
| `TR_ORE_GLOW` | 0.22 | ore sparkle & spec boost |
| `TR_ORE_ROUGHNESS_DROP` | 0.12 | ore sparkle & spec boost |
| `TR_ORE_SPEC_BOOST` | 0.35 | ore sparkle & spec boost |
| `TR_PI` | 3.14159265359 | maths/noise plumbing |
| `TR_PLANT_ROOT` | 0.10 | plant-root detection tolerance |
| `TR_PLANT_TOL` | 0.045 | plant-root detection tolerance |
| `TR_RELIEF_SHADE` | 0.45 | relief shading |
| `TR_RELIEF_SIGN` | 1.0 | relief shading |
| `TR_RELIEF_STRENGTH` | 0.55 | relief shading |
| `TR_SAND_RIPPLE_AMP` | 0.18 | sand ripples |
| `TR_SAND_RIPPLE_FREQ` | 5.80 | sand ripples |
| `TR_SAND_RIPPLE_WANDER` | 0.14 | sand ripples |
| `TR_SHADE_DUSK` | vec3f(0.58, 0.58, 0.88) | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADE_SKY` | vec3f(0.84, 0.89, 0.98) | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_DUSK_SOFT` | 0.03 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_DUSK_WIDEN` | 0.05 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_SOFTNESS` | 0.040 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_SUN_FLOOR` | 0.10 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_THRESHOLD` | 0.95 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_TINT_COOL` | 0.50 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHELTER_SINK` | 0.26 | lighting framework (keep/unlit/night/shelter) |
| `TR_SHOULDER` | 0.80 | tone mapping & grade |
| `TR_SHOULDER_KNEE` | 0.66 | tone mapping & grade |
| `TR_SKYSPEC_ROUGH_HIGH` | 0.75 | sky specular on water |
| `TR_SKYSPEC_ROUGH_LOW` | 0.35 | sky specular on water |
| `TR_SKYSPEC_STRENGTH` | 0.18 | sky specular on water |
| `TR_SKY_AMBIENT_HUE` | vec3f(0.90, 0.965, 1.07) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK` | vec3f(1.00, 0.45, 0.20) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK_FADE` | 7.0 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK_GAIN` | 0.90 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK_POW` | 3.0 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_HAZE_GAIN` | 0.42 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_HORIZON` | vec3f(0.66, 0.79, 0.93) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_ZENITH` | vec3f(0.16, 0.36, 0.80) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_ZENITH_POW` | 0.45 | sky gradient (zenith/horizon/dusk) |
| `TR_SNELL_HI` | 0.72 | Snell window underwater |
| `TR_SNELL_LO` | 0.58 | Snell window underwater |
| `TR_SNELL_SKY` | 0.85 | Snell window underwater |
| `TR_SNELL_SUN` | 2.20 | Snell window underwater |
| `TR_SPARKLE_DENSITY` | 0.10 | water sparkle glints |
| `TR_SPARKLE_SCALE` | 1.30 | water sparkle glints |
| `TR_SPARKLE_STRENGTH` | 0.26 | water sparkle glints |
| `TR_SPEC_AA` | 0.10 | specular system & anti-aliasing |
| `TR_SPEC_STRENGTH` | 0.55 | specular system & anti-aliasing |
| `TR_SSS_BIAS` | 0.85 | subsurface scattering on foliage |
| `TR_SSS_FLOOR` | 0.18 | subsurface scattering on foliage |
| `TR_SSS_STRENGTH` | 0.42 | subsurface scattering on foliage |
| `TR_STAR_DENSITY` | 0.0022 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_STAR_GAIN` | 1.30 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_STAR_SCALE` | 190.0 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_STAR_TWINKLE` | 0.35 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_SUNSET_BAND` | 0.30 | sun/sunset response |
| `TR_SUN_AIRMASS` | 0.26 | sun airmass reddening (sky model) |
| `TR_SUN_AIRMASS_MAX` | 9.00 | sun airmass reddening (sky model) |
| `TR_SUN_AIRMASS_NORM` | 1.16413 | sun airmass reddening (sky model) |
| `TR_SUN_AIR_RGB` | vec3f(0.34, 0.62, 1.00) | sun airmass reddening (sky model) |
| `TR_SUN_BUDGET_GAIN` | 0.20 | sun/sunset response |
| `TR_SUN_DIRECTION_BLEND` | 0.60 | sun/sunset response |
| `TR_SUN_DISC_GAIN` | 26.0 | sun disc & glow render |
| `TR_SUN_DISC_HI` | 0.99970 | sun disc & glow render |
| `TR_SUN_DISC_LO` | 0.99880 | sun disc & glow render |
| `TR_SUN_GLOW_GAIN` | 0.90 | sun disc & glow render |
| `TR_SUN_GLOW_HI` | 0.9992 | sun disc & glow render |
| `TR_SUN_GLOW_LO` | 0.9920 | sun disc & glow render |
| `TR_SUN_HUE` | vec3f(1.00, 0.98, 0.95) | sun airmass reddening (sky model) |
| `TR_SUN_REDDEN` | 0.85 | sun airmass reddening (sky model) |
| `TR_SUN_STRENGTH` | 0.85 | sun/sunset response |
| `TR_SWAY_ANGLE` | 0.55 | sway angle cap |
| `TR_TAU` | 6.28318530718 | maths/noise plumbing |
| `TR_TERRAIN_ROUGHNESS` | 1.05 | micro-detail & terrain normal work |
| `TR_TONEMAP_STRENGTH` | 1.0 | tone mapping & grade |
| `TR_TORCH_PIERCE_GAIN` | 1.40 | torch warm tint & pierce |
| `TR_TORCH_PIERCE_TINT` | 0.60 | torch warm tint & pierce |
| `TR_TORCH_WARM_TINT` | vec3f(1.10, 0.86, 0.62) | torch warm tint & pierce |
| `TR_UNDERWATER_ABSORB` | vec3f(0.32, 0.055, 0.022) | underwater grade when camera submerged |
| `TR_UNDERWATER_BLUE_HI` | 0.30 | underwater grade when camera submerged |
| `TR_UNDERWATER_BLUE_LO` | 0.10 | underwater grade when camera submerged |
| `TR_UNDERWATER_CAUSTIC` | 0.55 | underwater grade when camera submerged |
| `TR_UNDERWATER_DEEP` | vec3f(0.020, 0.130, 0.190) | underwater grade when camera submerged |
| `TR_UNDERWATER_RATIO` | 1.333 | underwater grade when camera submerged |
| `TR_UNDERWATER_RATIO_HI` | 2.80 | underwater grade when camera submerged |
| `TR_UNDERWATER_RATIO_LO` | 2.00 | underwater grade when camera submerged |
| `TR_UNDERWATER_STRENGTH` | 0.85 | underwater grade when camera submerged |
| `TR_UNLIT_GAIN` | 1.0 | lighting framework (keep/unlit/night/shelter) |
| `TR_VERTEX_GUST` | 0.45 | vertex displacement hooks (few-game feature) |
| `TR_VERTEX_LIFT` | 0.35 | vertex displacement hooks (few-game feature) |
| `TR_VERTEX_ROOT` | 0.15 | vertex displacement hooks (few-game feature) |
| `TR_VERTEX_SWAY` | 0.140 | vertex displacement hooks (few-game feature) |
| `TR_WATER_CLARITY` | 0.82 | water clarity (view-through) |
| `TR_WATER_DAY_TINT` | vec3f(0.34, 0.78, 0.82) | water tint, day band |
| `TR_WATER_DUSK_TINT` | vec3f(0.20, 0.48, 0.66) | water tint, dusk band |
| `TR_WATER_GLINT` | 0.82 | sun glint strength |
| `TR_WATER_MIRROR_CAP` | 1.05 | water optics |
| `TR_WATER_MIRROR_CHROMA` | 0.80 | water optics |
| `TR_WATER_MIRROR_PRESS` | 1.60 | water optics |
| `TR_WATER_MOON_GLINT` | vec3f(0.48, 0.66, 0.88) | water optics |
| `TR_WATER_NIGHT_TINT` | vec3f(0.075, 0.19, 0.34) | water tint, night band |
| `TR_WATER_REFLECTIVITY` | 0.78 | water reflectivity |
| `TR_WATER_RIPPLE` | 0.105 | ripple amplitude |
| `TR_WATER_TINT` | 0.48 | water tint mix strength |
| `TR_WAVE_OMEGA_A` | 0.502655 | wave band A angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_B` | 0.726057 | wave band B angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_C` | 0.949459 | wave band C angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_D` | 1.605703 | wave band D angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_E` | 1.982694 | wave band E angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_F` | 2.415536 | wave band F angular frequency (frozen R17) |
| `TR_WIND_FIELD_BASE` | 0.5 | wind field for foliage |
| `TR_WIND_FIELD_SCALE` | 0.012 | wind field for foliage |
| `TR_WIND_FIELD_SPEED` | 0.551111 | wind field for foliage |
| `TR_WIND_SPEED_STEP` | 0.013889 | wind master settings |

## PROBE-DIAG-v2 (measurement probe, modes 0-15) — 19 constants

| Constant | Value | Role |
|---|---|---|
| `MODE_0_SKYLIGHT_RAW` | 0 | probe mode 0 — raw skyLight to all channels |
| `MODE_10_DIRECTIONAL_GRAY` | 10 | probe mode 10 — terrain directional light as grey |
| `MODE_11_DEPTH_DEFINE` | 11 | probe mode 11 — is BLOXD_SCENE_DEPTH active (green/red) |
| `MODE_12_DEPTH_FOUND` | 12 | probe mode 12 — bloxdOpaqueBehind().found (green/red) |
| `MODE_13_DEPTH_PATH_BANDS` | 13 | probe mode 13 — water path depth colour bands |
| `MODE_14_DEPTH_VERTICAL_BANDS` | 14 | probe mode 14 — vertical depth colour bands |
| `MODE_15_DEPTH_BED_ANCHOR` | 15 | probe mode 15 — bed anchor visualisation (fract bed.y) |
| `MODE_1_SKY_LEVEL_0_15` | 1 | probe mode 1 — skyLight rescaled 0-15 |
| `MODE_2_BLOCKLIGHT_RGB` | 2 | probe mode 2 — blockLight RGB as colour |
| `MODE_3_HELDLIGHT_RGB_X4` | 3 | probe mode 3 — heldLight ×4 (visibility boost) |
| `MODE_4_SKYLIGHTCOLOUR_NORM` | 4 | probe mode 4 — skyLightColour normalised |
| `MODE_5_AMBIENTCOLOUR_NORM` | 5 | probe mode 5 — ambient colour normalised |
| `MODE_6_FOGVISIBILITY_GRAY` | 6 | probe mode 6 — fogVisibility as grey |
| `MODE_7_FOGCOLOUR_RAW` | 7 | probe mode 7 — raw fogColour (reveals black in mode NONE) |
| `MODE_8_SUNDIRECTION_RGB` | 8 | probe mode 8 — sun direction as RGB |
| `MODE_9_SUNLENGTH_GRAY` | 9 | probe mode 9 — |sunDir| as grey (0 on sunless skies) |
| `MODE_SECONDS` | 60.0 | probe seconds-per-mode before rotating |
| `PROBE_MODE` | -1 | probe channel selector; >=0 freezes a measurement mode |
| `TR_EPS` | 0.0001 | probe epsilon |

## Breeze v1 (shipped pack, dissected — Crownix after Ellie) — 61 constants

| Constant | Value | Role |
|---|---|---|
| `BLOCK_VARIATION` | 0.04 | per-block / per-cell brightness variation |
| `BRIGHTEN` | 1.45 | pre-fog grade (lift + chroma-guarded vibrance) |
| `CANOPY_SPREAD` | 0.0035 | tree-canopy shadow (lost skyLight level) |
| `CANOPY_STRENGTH` | 1.0 | tree-canopy shadow (lost skyLight level) |
| `CANOPY_TINT` | vec3f(0.5, 0.56, 0.7) | tree-canopy shadow (lost skyLight level) |
| `CELLS_PER_BLOCK` | 8 | shading-cell lattice plumbing |
| `CELL_FAR` | 40.0 | per-block / per-cell brightness variation |
| `CELL_VARIATION` | 0.06 | per-block / per-cell brightness variation |
| `COARSE_SHIFT` | vec2i(117, 44) | rotated-integer-lattice wave octaves & LOD |
| `COARSE_STRIDE` | 2000 | rotated-integer-lattice wave octaves & LOD |
| `CREST_GAIN` | 0.02 | wave-crest lighting |
| `DEEP_OPACITY` | 0.97 | depth-driven opacity ramp |
| `DEEP_TINT` | vec3f(0.05, 0.18, 0.5) | Beer-Lambert depth colouring |
| `DEPTH_DARKEN` | 0.32 | Beer-Lambert depth colouring |
| `FALLING_LEAVES` | true | painted falling-leaf raymarch |
| `FINE_FAR` | 40.0 | rotated-integer-lattice wave octaves & LOD |
| `FINE_NEAR` | 24.0 | rotated-integer-lattice wave octaves & LOD |
| `FINE_SHIFT` | vec2i(459, 312) | rotated-integer-lattice wave octaves & LOD |
| `FINE_STRIDE` | 3700 | rotated-integer-lattice wave octaves & LOD |
| `FOAM_COLOUR` | vec3f(0.97, 0.99, 1.0) | shoreline foam edge |
| `FOAM_SOLID` | 0.1 | shoreline foam edge |
| `FOAM_WIDTH` | 0.45 | shoreline foam edge |
| `GLINT_COLOUR` | vec3f(1.0, 0.97, 0.88) | broad sun sheen colour |
| `GRAIN_NEAR` | 14.0 | near grain cutoff |
| `GRASS_GUSTS` | 0.16 | wind gusts rolling over grass tops |
| `GUST_DIRECTION` | vec2f(0.92, 0.39) | wind gusts rolling over grass tops |
| `HASH_PERIOD` | 289 | shading-cell lattice plumbing |
| `LANDING_RINGS` | true | feature toggle: leaf-landing rings |
| `LEAF_CELL` | 3.0 | painted falling-leaf raymarch |
| `LEAF_CHANCE` | 0.3 | painted falling-leaf raymarch |
| `LEAF_FALL` | 0.6 | painted falling-leaf raymarch |
| `LEAF_RANGE` | 10.0 | painted falling-leaf raymarch |
| `LEAF_SHIMMER` | 0.3 | gust shimmer on leaves |
| `LEAF_SIZE` | 0.09 | painted falling-leaf raymarch |
| `LEAF_STEPS` | 6 | painted falling-leaf raymarch |
| `MIST` | 0.16 | blotch strength |
| `MIST_FAR` | 48.0 | drifting world-fixed blotches |
| `MIST_SIZE` | 5.0 | drifting world-fixed blotches |
| `REFLECTIVITY` | 0.45 | Schlick sky reflection |
| `RING_CELL` | 4 | leaf-landing rings on water |
| `RING_CHANCE` | 0.45 | leaf-landing rings on water |
| `RING_EVERY` | 5.0 | leaf-landing rings on water |
| `RING_SIZE` | 1.1 | leaf-landing rings on water |
| `RING_STRENGTH` | 0.4 | leaf-landing rings on water |
| `SHADE_FROM` | -0.1 | face-direction sun tint bounds |
| `SHADE_TINT` | vec3f(0.76, 0.8, 0.88) | face-direction sun tint bounds |
| `SHALLOW_OPACITY` | 0.3 | depth-driven opacity ramp |
| `SHALLOW_TINT` | vec3f(0.58, 0.92, 0.92) | Beer-Lambert depth colouring |
| `SKY_REFLECTION_COLOUR` | vec3f(0.68, 0.79, 0.94) | Schlick sky reflection |
| `SOFTEN` | 0.12 | texture speckle smoothing (soft look) |
| `SOFT_LEVEL` | 0.5 | texture speckle smoothing (soft look) |
| `SUNSPOTS` | 0.45 | drifting sunspots through canopy shadow |
| `SUNSPOT_SPEED` | 0.3 | drifting sunspots through canopy shadow |
| `SUN_FROM` | 0.35 | face-direction sun tint bounds |
| `SUN_TINT` | vec3f(1.1, 1.04, 0.94) | face-direction sun tint bounds |
| `TAU` | 6.2831853 | 2π constant |
| `VIBRANCE` | 0.22 | pre-fog grade (lift + chroma-guarded vibrance) |
| `WATER_ALPHA` | 0.9 | water's engine-registered values (rebuilt from) |
| `WATER_COLOUR` | vec3f(0.5, 0.5, 0.8) | water's engine-registered values (rebuilt from) |
| `WIND_SPEED` | 0.8 | wind master settings |
| `WIND_STRENGTH` | 1.0 | wind master settings |

<!-- CONSTANTS:END -->
