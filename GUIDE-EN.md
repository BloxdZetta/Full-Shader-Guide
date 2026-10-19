# Bloxd Shader Packs — The Complete Guide (English)

🌐 [All languages](README.md) · [Français](GUIDE-FR.md)

**Everything known about Bloxd.io shader packs, explained as simply as possible:**
how the web renderer draws the picture, how shaders work, what a pack can do,
what it cannot do, and how to build one — backed by measured engine data,
a full numeric block-id table, dissected community packs, and local validation
in all 8 engine variants.

**One file, everything inside.** Use the contents below — or GitHub's outline (the ≡ button) — to jump straight to a part.

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
- A **shader pack** is a small `.zip` with shader code. The game loads it and lets your code
  recolour **blocks, water and lava** while they are drawn.
- You do not change the game. You only change colours and light, at the exact moment each
  pixel is drawn.

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
   coordinates, light values, face direction…).
5. **Rasterising.** The GPU fills each triangle with pixels. Every covered pixel becomes a
   **fragment**: a candidate pixel with interpolated data.
6. **Fragment step.** The GPU runs a *fragment shader* for every fragment: this is where the
   final colour of the pixel is decided. **This is where Bloxd shader packs live.**
7. **Screen.** The finished frame is shown. Then everything repeats for the next frame.

```mermaid
flowchart LR
    A[World of blocks] --> B[Chunks]
    B --> C[Meshes: visible faces only]
    C --> D[Vertex step: place corners]
    D --> E[Rasterise: fill pixels]
    E --> F[Fragment step: YOUR PACK recolours]
    F --> G[Screen]
```

Key idea: your pack never sees "the world". It sees **one fragment at a time** — one pixel of
one block face — plus some data about that pixel. Everything a pack does must be computed
from that local data.

## 3. What a shader is

A shader is a small function (a small piece of code) that the GPU runs an enormous number of
times in parallel — once per vertex, or once per fragment. It must be fast and self-contained:
no files, no network, no memory of the previous frame.

Bloxd packs are written in **WGSL** (WebGPU Shading Language). You do not write a whole
shader. The engine already has its own shaders; it lets you insert your code at four fixed
points, called **hooks** (Section 5). Think of it as four doors: the engine walks through its
drawing code, and at each door it asks your function: "here is this pixel's data — do you want
to change the colour?"

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

- `apiVersion` must be the number **2**. Old v1 packs are rejected.
- The loader finds **every** `*.wgsl` file in the zip and joins them together. File order and
  folders do not matter.
- Total WGSL size limit: **256 KB**.

To install a pack in the game: Bloxd → `O` Settings → Graphics → enable **Use New WebGPU
Renderer** → Shader Pack → **Choose .zip** → **Apply**.

A pack only affects **blocks, water and lava**. Some game modes disable packs completely.

## 5. The four hooks (your only doors)

| Hook | When it runs | What you control |
|---|---|---|
| `bloxdTerrainSurface` | per fragment, solid blocks, first | base colour, transparency (alpha), self-glow (emission) |
| `bloxdTerrainLight` | same fragment, right after | final lit colour of blocks |
| `bloxdLiquidSurface` | per fragment, water and lava, first | base colour and alpha of liquids |
| `bloxdLiquidLight` | same fragment, right after | final lit colour of liquids |

Rules of the doors:

- Surface runs **before** light, in the same fragment. You can pass a value from surface to
  light with a module-scope variable (`var<private>`).
- Always start from the engine's default result: `bloxdDefaultSurface(...)` or
  `bloxdDefaultLight(...)`, change what you need, then return it. Never build the result
  structs yourself.
- Surface hooks run before the engine's transparency cut-out test: on leaves and cut-out
  blocks, `out.alpha` decides if the pixel is kept or discarded; on liquids it is the real
  blend factor; on plain solid blocks alpha does nothing.
- Self-glow (`out.emission`) belongs to the **surface** hooks only.
- If you write your own final colour in a light hook, apply the fog yourself at the end with
  `bloxdApplyFog(colour, light)` — the engine's fog is always present in the scene, and
  skipping it makes distant blocks shine through the fog.

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
| `fogVisibility`, `fogColour` | how fogged this pixel is, and the fog colour (arrives **black** when fog is off — handle that case) |

Engine functions you can call:

| Function | What it gives you |
|---|---|
| `bloxdDefaultSurface(in)` / `bloxdDefaultLight(surface, light)` | the engine's normal result — always your starting point |
| `bloxdApplyFog(colour, light)` | blends your colour into the fog correctly |
| `bloxdSunDirection()` | unit vector towards the sun; `(0,0,0)` in worlds without an earth-like sun; the moon is exactly the opposite direction |
| `bloxdTime()` | seconds — **wraps back to 0 every 3600 seconds** (`bloxdTimeWrap`). See Section 7 |
| `bloxdEyePosition()` | the camera position (for distance effects) |
| `bloxdOriginOffset()` | the engine periodically rebases world coordinates; add this offset into any world-position pattern, or your pattern will visibly jump |
| `bloxdFaceBlock(position, normal)` | the block cell (whole-number coordinates) of the face you are drawing — perfect for per-block random variation |
| `bloxdOpaqueBehind()` | liquids only: finds the first solid block behind the liquid surface — used to measure water depth |

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

**Lighting can be off.** If a game or setting disables lighting, `skyLight` may not be sent
at all and sky-driven effects silently do nothing. Write effects so the pack still looks fine
without them.

## 8. Everything a pack CAN do

- Recolour any block, water or lava — globally or per `blockId`.
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
- **No scene depth.** The only "what is behind this" query is `bloxdOpaqueBehind()` through
  a liquid.
- **No real shadow maps or ambient occlusion** beyond what the engine's light values already
  encode.
- **No new objects or particles** in the world. You can only paint on surfaces that already
  exist. (Clever packs paint overlay effects onto surfaces — see the recipes — but the
  geometry is always the engine's.)
- **No textures or samplers** of your own, no extra data feeds: your only inputs are the
  hook arguments and the engine functions.
- **Vertex movement** (bending geometry, waves that move corners) exists in the engine but
  **only runs in a few games** — never depend on it; fake movement with colour/alpha
  animation instead.
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

3. Zip the two files together, with `pack.json` at the root of the zip (not inside a
   subfolder).
4. In the game: Settings → Graphics → **Use New WebGPU Renderer** on → Shader Pack →
   Choose .zip → Apply.
5. Look around: the world should be a little warmer. Change the three numbers and reload to
   experiment.

Then grow step by step: one effect at a time, check it at midday, sunset, night, underwater
and in a cave before adding the next.

## 11. The nine hard rules

Breaking any of these breaks or rejects the pack:

1. Never define anything whose name starts with `BLOXD_` — those belong to the engine.
2. Never build `BloxdSurface` / `BloxdLight` yourself — start from `bloxdDefaultSurface` /
   `bloxdDefaultLight`.
3. `mod` is a reserved word in WGSL — use `%`.
4. No textures, no samplers, no entry points or attributes of your own, no screen UVs.
5. Avoid `discard` (rejected in strict mode) — use `out.alpha` instead.
6. Liquid hooks must always output a valid alpha, in every variant.
7. Unused inputs: write `_ = value;` — the form `let _ =` is rejected.
8. Total WGSL ≤ 256 KB.
9. The engine compiles your code in **8 variants** (strict/permissive × lit/unlit ×
   terrain/liquid). Your code must compile and behave in all of them. Parenthesise mixed
   bitwise/shift expressions for the browser's Tint compiler.

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
| Hook | one of the four engine functions your pack may define |
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

A **.zip** containing:

```
pack.json          # metadata, required
*.wgsl             # one or more WGSL files, any folder layout
```

`pack.json` (the only required keys):

```json
{ "apiVersion": 2, "name": "My Pack", "author": "you" }
```

- `apiVersion` **must be the number 2**. v1 packs are rejected by the current game.
- There is no file list in `pack.json` — see multi-file below.

## Installing (what your users will do)

Bloxd → `O` Settings → Graphics → tick **Use New WebGPU Renderer** → Shader Pack →
**Choose .zip** → **Apply** (or refresh). Packs need a WebGPU browser (recent Chrome/Edge on
desktop) and only take effect where allowed.

## What a pack can affect

**Blocks, water and lava only** — plus a few colour paths (fog input, sky light colour) exposed
through the light hook. Plants/grass/flowers are drawn by a part of Bloxd **packs cannot reach**
(confirmed by dissection of a shipped pack). Some games disable packs entirely. Vertex-level
deformation exists but **only runs in a few games** — never depend on it.

## Single-file vs multi-file — IMPORTANT (proven in the wild)

The loader **globs every `*.wgsl` under the zip root and concatenates them**. There is **no
required `shader.wgsl`**: the #1 workshop pack ships 10 files in subfolders
(`lib/hash.wgsl`, `terrain/sunShade.wgsl`, `water/liquid.wgsl`, …) with no root shader file.
WGSL module scope is order-independent, so file order does not matter.

Both layouts are valid:

```
my-pack.zip                    my-pack.zip
├── pack.json                  ├── pack.json
└── shader.wgsl                ├── lib/hash.wgsl
                               ├── terrain/soft.wgsl
                               └── water/liquid.wgsl
```

Multi-file is nicer to maintain; single-file is easier to share. Same bytes at load time.

## Caps

- **256 KB** total `.wgsl` after concatenation (loader cap; a 28 KB pack is comfortable).
- One source file, one language: WGSL only. No `#include`, no preprocessor of your own.
- Per-fragment cost is yours to control: gate expensive effects by distance/blockId
  (see Part III recipes).

## Distributing

- **The Bloxdhub workshop** is the de-facto storefront (`bloxdhub.com/workshop?type=shader-packs`).
  Each item page exposes a direct `media.bloxdhub.com/workshop-files/<token>.zip` link.
- Direct zip links (Drive, GitHub releases) work equally; users just pick the file in Settings.
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

Zip those two files (pack.json at zip root) and it loads. Now read Part II.

---

# Part II — The API contract

Everything below is either proven in a shipped pack (label **[shipped]**) or exercised by
locally validated packs (**[local]**). If it is not in this file, treat it as unknown until proven.

## The four hooks

| Hook | Runs | Purpose |
|---|---|---|
| `bloxdTerrainSurface(BloxdSurfaceIn) -> BloxdSurface` | per fragment, opaque terrain | recolour / alpha of blocks |
| `bloxdTerrainLight(BloxdSurface, BloxdLightIn) -> BloxdLight` | same fragment, after surface | final lit colour, **before engine fog if you call `bloxdApplyFog` yourself** |
| `bloxdLiquidSurface(BloxdSurfaceIn) -> BloxdSurface` | per fragment, liquids | colour/alpha of water & lava |
| `bloxdLiquidLight(BloxdSurface, BloxdLightIn) -> BloxdLight` | same fragment, after surface | liquid final colour |

Facts that matter:

- **Surface and light run in the same fragment, surface first.** You can pass data between them
  with a module-scope `var<private>` **[shipped]**.
- Surface hooks run **before alphaTest**: `out.alpha` drives the discard on cutouts (grass plant,
  leaves) and is the real blend factor on liquids. It does nothing on plain opaque blocks.
- **`out.emission` belongs to the surface hook** (self-glow). Do not write it from light hooks.
- To opt in to a hook you must define it and **return `bloxdDefault*`** when you have nothing to
  do; unused parameters are dropped with the bare form `_ = param;`.

## Structs (fields proven in use)

```wgsl
BloxdSurfaceIn { colour: vec3f, alpha: f32, position: vec3f, normal: vec3f,
                 blockId: u32 /* ... */ }
BloxdSurface   { colour: vec3f, alpha: f32, emission: vec3f /* ... */ }
BloxdLightIn   { position: vec3f, normal: vec3f, blockId: u32,
                 skyLight: f32, blockLight: vec3f, heldLight: vec3f,
                 skyLightColour: vec3f, litColour: vec3f,
                 fogVisibility: f32, fogColour: vec3f /* ... */ }
BloxdLight     { colour: vec3f /* ... */ }
```

Reading the fields:

- `blockId : u32` — **the numeric block id** (Part VIII table). This is how per-block shading works.
- `skyLight` — **tone-mapped** 0..1 (see Part IV). Open sky ≈ 1; one lost light level under a
  canopy ≈ 0.995. Threshold decisions must be calibrated on this curve.
- `blockLight`, `heldLight` — colour channels (can be non-grey: coloured lamps).
- `skyLightColour` — the sky's tint; darkens at night. Use it to tint sky-driven terms **[shipped]**.
- `litColour` — the surface's own lit colour (material light + corner shading) **[shipped]**.
- `fogVisibility`, `fogColour` — engine fog. `fogColour` arrives **black** when fog mode is NONE.

## Engine functions

| Function | Returns / does |
|---|---|
| `bloxdDefaultSurface(in)` / `bloxdDefaultLight(surface, light)` | your mandatory starting point — never construct the structs literally |
| `bloxdApplyFog(colour, light)` | mix(fogColour, colour, fogVisibility); call it last, after your grade, before overlays |
| `bloxdSunDirection()` | unit vector to the sun; **(0,0,0) when the skybox has no earth-type sun**; static in default worlds; the moon is exactly `−bloxdSunDirection()` |
| `bloxdTime()` / `bloxdTimeWrap` | seconds, wraps at `bloxdTimeWrap` (3600). Animate with **whole cycles**: `sin(TAU * fract(bloxdTime() / bloxdTimeWrap * cycles + phase))` |
| `bloxdEyePosition()` | camera position, for distance/LOD and view vectors |
| `bloxdOriginOffset()` | floating-origin rebase offset; **add it into any world-space hash** or patterns jump when the engine rebases (it does) |
| `bloxdFaceBlock(position, normal)` | the **cell** (block coordinates) of the face you are on — per-block hash input; the id itself is `surface.blockId` / `light.blockId` **[shipped]** |
| `bloxdOpaqueBehind()` | `{found, position}` of the first opaque block behind a liquid fragment — vertical water depth, refraction approximations **[shipped]** |

## Hard rules (violating any = broken or rejected pack)

1. **Never `#define` anything starting with `BLOXD_`** — the engine owns those macros per variant.
2. **Never construct `BloxdSurface`/`BloxdLight` literally** — always start from `bloxdDefault*`.
3. `mod` is a **reserved word** in WGSL — use the `%` operator.
4. No textures, no samplers, no builtins/entry-point attributes of your own, no screen UVs.
5. `discard` breaks strict-mode packs; prefer `out.alpha` semantics.
6. Liquids keep alpha in every engine variant — your liquid hook must always write a sane alpha.
7. `let _ =` is rejected; use bare `_ = expr;`.
8. Total `.wgsl` ≤ 256 KB.
9. Assume the browser Tint compiler, not just naga: parenthesise mixed bitwise/shift expressions
   even though some shipped packs skip it.

## The 8 variants you must survive

Engine compiles your file in: **strict × lit × {terrain, liquid}** and **allow × lit ×
{terrain, liquid}** (unlit variants exist too). “Strict” = hardened game servers: no discard, no
extra features; “allow” = everything on. When “Lighting” is **off**, the game sends **no skyLight
at all** — sky-driven logic silently no-ops (proven by a shipped pack). Whether light hooks run
at all in unlit builds is **not yet measured**; write them so it doesn’t matter. Every hook must
compile in all variants (Part VI).

## Capabilities & boundaries — the definitive matrix

| Packs CAN | Packs CANNOT |
|---|---|
| recolour terrain & liquids **per blockId** (Part VIII) | touch plants/grass/flowers (engine-rendered, unreachable **[shipped]**) |
| set alpha on cutouts (discard) and liquids (blend) | post-process the frame (no screen-space access) |
| self-glow via `out.emission` (surface hook) | read scene depth — except `bloxdOpaqueBehind()` through a liquid |
| grade, tint, fog-before, sky-driven terms | real shadow-mapping or SSAO beyond what skyLight encodes |
| world-anchored procedural effects (hash + rebase) | add objects/particles to the world (paint overlays instead, R14) |
| private-var data surface→light per fragment | use textures/samplers/extra binds |
| vertex deformation | depend on it — **only a few games run it** **[shipped]** |
| react to block/held light, sun vector, time | know the held-beam direction; get per-world config UI |

---

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

```wgsl
let behind = bloxdOpaqueBehind();
let depth = select(64.0, max(surface.position.y - behind.position.y, 0.0), behind.found);
let depthFade = 1.0 - exp(-depth * 0.32);   // ~1/3 at 1 block, ~85% at 6 blocks
out.colour = light.litColour * mix(SHALLOW_TINT, DEEP_TINT, depthFade);
```

Credit: shipped pack Breeze. `depth = 64` when nothing opaque is behind (open sky = deep).

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

## R11 — Strict-safe liquid alpha

```wgsl
var out = bloxdDefaultSurface(surface);
out.alpha = clamp(surface.alpha / REGISTERED_ALPHA * mix(SHALLOW_OP, DEEP_OP, depthFade),
                  0.0, 1.0);
out.alpha = max(out.alpha, foam * 0.95); // overlays push alpha up, never down
```

Liquids keep alpha in every variant; rebuild from the registered value instead of hardcoding.

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

- Sky light propagates 0–15 (flood fill); **open sky = 15**. One level lost under a canopy is
  still ≈ **0.995 after tone-mapping** — a “lost level” is visible, darkness is not linear.
- skyLight arrives **tone-mapped** to packs. Worked thresholds: full sky ≈ ≥0.98; cave/night
  rejection below ≈ 0.45; a canopy’s one lost level ≈ 0.995 **[shipped]**.
- Packed light colours have a **35 % per-channel floor** relative to the brightest channel
  **[3rd-party]** — pure red lifts to (1.0, 0.35, 0). This is why lamps look washed-out pink.
- `l.ambient` = material.ambient × sceneAmbient; the scene side follows the user’s graphics
  setting (default 0.5). Never hardcode its default **[3rd-party]**.

## Sun, moon, sky

- Default worlds: sun direction static ≈ **(−0.56, 0.81, −0.18)** **[3rd-party]**; day/night
  worlds update it; **moon = −sun exactly**; night ⇔ `sun.y < 0`.
- Non-earth skyboxes (gloomy/interstellar/space): `bloxdSunDirection()` = **(0,0,0)** — gate
  every sun effect with a `sun.y`-based day factor and it self-disables **[shipped]**.
- Terrain directional light is two lamps with fixed direction/intensity — **terrain brightness
  does not follow the sun by itself**; time-of-day looks are 100 % your job.

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
| pack silently ignored | `apiVersion` not the number 2, pack.json invalid JSON, or zip nests a folder instead of files |

## Loads but looks wrong

| Symptom | Cause / fix |
|---|---|
| nothing changes in some games | those games disable packs — nothing to do |
| plants don’t sway / can’t recolour | plants are drawn by a part of Bloxd packs can’t reach (confirmed by dissection); only block faces are yours |
| shadows disappeared | “Lighting” is off in that world → the game sends **no skyLight**; your `smoothstep(0.4, 0.9, skyLight)` gate correctly no-ops |
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

The loader concatenates — keep cross-file dependencies order-free (pure functions only at module
scope, `var<private>` only inside one concern).

## Local pipeline (what we run before every release)

1. **Concat check** — build the concatenation the loader will make; compile *that* file too.
2. **8-variant compile** — validate against a local naga with the engine’s prelude stubbed per
   variant: strict/allow × lit/unlit × terrain/liquid. A pack that compiles in 8/8 locally has
   never failed in-game for us. Stub every engine symbol you use; if your stub is missing one
   (e.g. `bloxdOpaqueBehind`), fix the stub, not the pack.
3. **Static checks** — reserved words (`mod`), `#define BLOXD_`, literal struct construction,
   `let _`, TODO markers, total size ≤ 256 KB.
4. **Loop/logic audit** — every per-fragment loop must be bounded AND gated by a distance or
   blockId condition; every darkening factor must multiply by the lamp guard.
5. **Package** — zip with `pack.json` at the **zip root** (not inside a folder). Record the
   zip’s sha256; publish the hash with the release.
6. **In-game smoke test** — day world, night world, cave, one tree, water edge, a lamp, a
   “strict”-style server if available; screenshot each; compare against the previous release.
7. **Stress matrix via world-owner options** — worlds can override what packs receive, which
   makes free test environments: `fogColour` override, skyLight / ambient-light overrides,
   `lightingOverride`, skybox types (`earth`, gloomy, interstellar/space ⇒ **zero sun vector**),
   day/night-cycle worlds, plus lighting-off worlds. A pack that survives this matrix (sun
   effects auto-off, fog-safe, cave-correct) is release-grade.

## Measuring instead of guessing

- Capture screenshots at fixed camera/world setups (a “probe world”): same seed, same time band.
- Fit your grade curve on log–log luminance pairs from captures; a handful of points drives a
  one-parameter lift (R5) precisely.
- Probe packs (temporary, never shipped): write engine quantities to colour channels —
  skyLight to red, blockLight to green, etc. — and read them back with a colour picker. This is
  how the tone-mapping thresholds of Part IV were measured.

## Release checklist

- [ ] `apiVersion: 2` as a number
- [ ] compiles 8/8 locally (naga) + Tint-paranoid parentheses pass
- [ ] no `#define BLOXD_`, no literal structs, no `let _`, no `mod`, no discard in strict paths
- [ ] liquid alpha written in every branch
- [ ] lamp guard on every darkening term
- [ ] all loops bounded + gated
- [ ] size ≤ 256 KB
- [ ] zip sha256 published alongside
- [ ] smoke-tested in: day, night, cave, canopy, water edge, lamp, sunless-skybox world

---

# Part VII — Engine internals

Every item carries its provenance: **[measured]** local instruments · **[shipped]** proven by a
released pack in-game · **[3rd-party]** restored from production JS by community analysis
(sanity-check anything load-bearing).

## Time and space

- `bloxdTime()` is the **browser uptime wrapped at 1 hour** (`bloxdTimeWrap` = 3600). It is
  unrelated to any in-game clock **[3rd-party + shipped usage]**.
- The engine uses a **floating origin**: `bloxdOriginOffset()` rebases world coordinates
  periodically (the renderer is built on noa-engine). Any world-anchored pattern must add the
  offset into its hash input **[shipped]** — “doesn’t jump when noa rebases its origin”.
- Day/night is **not** a terrain lighting change: two directional lamps are created at scene
  start with fixed direction/intensity; only the skybox and `bloxdSunDirection()` carry time
  **[3rd-party]**.

## Light pipeline

- Sky light 0–15 flood-fill; open sky = 15; **tone-mapped before packs see it** (one lost level
  ≈ 0.995 post-curve) **[shipped thresholds]**.
- `aPackedLightLevels` decode floors each channel at **35 % of the brightest** **[3rd-party]**.
- `heldLight` (hand torch): range = brightest channel, ≤ 15 blocks, distance pre-warped `^0.75`,
  value arrives pre-ambient-boost **[3rd-party]**.
- Block light properties (official scripting docs **[3rd-party-official]**): `lightEmission`
  0–15 (feeds the blockLight BFS) and `lightFilter` — 1 air-class / 3 fluid-class / 15 opaque —
  which is why rooms go dark and fluids dim gradients.
- Custom blocks can set `skyLightEmission` (0–15), which **injects into the skyLight channel
  itself**, outside the blockLight BFS — sun/shadow tests keyed on skyLight alone can be fooled
  in such worlds; combine with blockLight for robustness **[3rd-party]**.
- `l.ambient` = material.ambient × sceneAmbient (user setting, default 0.5) **[3rd-party]**.

## Surfaces

- Surface hooks run **before alphaTest**: `out.alpha` drives cutout discard (grass plants,
  leaves) and is the true blend factor for liquids; no effect on plain opaques **[3rd-party]**.
- `out.emission` is a surface-hook output; adding it in light hooks still works if you sum it
  into the colour yourself before fog **[shipped]**.
- Plants/grass/flowers render through a path **packs cannot reach** **[shipped]**; vertex-level
  deformation exists but **only some games run it** **[shipped]** — hence “shading-only” wind.
- Chunk loading fades with the engine’s **Bayer 4×4 screen-space dither**; fine checkers during
  load are not your bug **[3rd-party]**.

## IDs

- The render pipeline identifies blocks by **numeric `blockId : u32`** (Part VIII); the scripting
  API uses string ids — two namespaces for the same blocks.
- The id space **grows with updates**: a dump that ended at 2089 already misses shipped-pack ids
  up to 3254. Re-enumerate per release (Part VIII method).

## Sky

- Default worlds: static sun ≈ (−0.56, 0.81, −0.18); **moon = −sun**; sunless skyboxes deliver
  a zero sun vector **[3rd-party]**.
- Fog: linear 32-block band at the load border; default colour rgb(183,191,195); fogColour
  arrives **black** with fog mode NONE **[3rd-party]**.

## Loader

- Globs `**/*.wgsl` and concatenates; no root file required; order-independent module scope
  **[shipped]**.
- Cap: 256 KB total WGSL; v1 `apiVersion` values are rejected outright **[3rd-party]**.

---

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

## The three provenance classes

| Label | Meaning | Trust policy |
|---|---|---|
| **[measured]** | produced by local instruments: probe packs that write engine quantities into colour channels, screenshot pipelines with fixed camera/world setups, curve fitting on captured frames | trust within the measured envelope |
| **[shipped]** | proven by a released community pack running in the live game (e.g. Breeze v1, dissected file-by-file) | trust — the game itself accepted it |
| **[3rd-party]** | restored from production JS by community analysis (the imu31465 internals, npm type dumps, wiki) | never load-bearing until measured; cited because they guided our probes |

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
- **Cross-source triangulation** — a fact is only promoted when independent sources agree
  (community manual + wiki + client dumps + our probes). Disagreements are kept and labelled
  (see the fog ramp open question in Part IV).

## Honest open questions

1. **Fog ramp shape** — linear 32×D [3rd-party] vs EXP2 (older wiki note). Production-JS figure
   favoured; sonde measurement pending.
2. **Light hooks in unlit builds** — do they run at all? Not yet measured; write hooks that don’t care.
3. **Loader hygiene details** — exact error messages and recovery paths of the in-game loader
   (the client bundle exists in public archives; a dedicated read is planned).
4. **New-id names** — ids up to 3254 are *used* by a shipped pack; official names await a fresh
   `api.blockIdToBlockName` dump.

## Numbers behind this guide

Full numeric id table (0 → 3254+) · dozens of validated releases across two production packs ·
4 engine APIs first documented here from shipped-pack usage · 2 shipped packs dissected to the
constant · every constant quoted carries its author credit.

---

<!-- CONSTANTS:START — generated by guide/tools/gen_var_registry.py, do not edit by hand -->

# Part X — The constants register (EN)

## Engine-exposed variables (what the game gives you)

| Variable | Type / value | Meaning |
|---|---|---|
| `surface.colour` | vec3f | incoming material colour (pre-shading) |
| `surface.alpha` | f32 | incoming alpha; drives cutout discard & liquid blend |
| `surface.position` | vec3f | world position of the fragment |
| `surface.normal` | vec3f | face normal |
| `surface.blockId` | u32 | numeric block id (Part VIII) |
| `out.emission` | vec3f | self-glow, surface hook only |
| `light.skyLight` | f32 0..1 | sky light, **tone-mapped** (open sky ≈1, one lost canopy level ≈0.995) |
| `light.blockLight` | vec3f | block light colour (35% channel floor) |
| `light.heldLight` | vec3f | handheld light (≤15 blocks, dist^0.75) |
| `light.skyLightColour` | vec3f | sky tint; darkens at night |
| `light.litColour` | vec3f | surface's own lit colour |
| `light.fogVisibility` | f32 | engine fog factor (linear band 32×D per 3rd-party) |
| `light.fogColour` | vec3f | fog colour; **black when fog mode is NONE** |
| `light.blockId` | u32 | numeric block id in the light hook |
| `bloxdTimeWrap` | f32 = **3600** | the wrap period of `bloxdTime()` (seconds) |
| `bloxdOriginOffset()` | vec3i | floating-origin rebase; inject into world hashes |
| `bloxdSunDirection()` | vec3f | unit sun vector; zero on sunless skies; moon = −this |
| `bloxdFaceBlock(p,n)` | vec3i | cell (block coordinates) of the current face — per-block hash input; the id itself is `surface.blockId` / `light.blockId` |
| `bloxdOpaqueBehind()` | {found,position} | first opaque block behind a liquid fragment |
| `bloxdEyePosition()` | vec3f | camera position |
| `bloxdApplyFog(c,l)` | vec3f | mix(fogColour, c, fogVisibility) |

## Engine-internal figures every pack author needs

| Figure | Value | Provenance |
|---|---|---|
| time wrap | 3600 s | [3rd-party + shipped usage] |
| light scale | 0–15, open sky = 15 | [3rd-party + measured] |
| tone curve family | ≈ 45·b/(1+2b) (saturating) | [measured] |
| terrain shadow band | skyLight 13.6–14.95 / 15 | [measured] |
| packed-light channel floor | 35 % of max channel | [3rd-party] |
| fog band | start 32×D, end 32×(D+1) (linear per 3rd-party; EXP2 legacy note — open question) | [3rd-party] |
| default fog colour | rgb(183, 191, 195) | [3rd-party] |
| showFog off | band pushed to 3200–3328 | [3rd-party] |
| scene ambient default | 0.5 (user setting) | [3rd-party] |
| loader cap | 256 KB total .wgsl | [3rd-party] |
| scene directional lamps | 2, fixed direction/intensity | [3rd-party] |



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
