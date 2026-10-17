# Part II — The API contract

Everything below is either proven in a shipped pack (label **[shipped]**) or exercised by our
own validated packs (**[ours]**). If it is not in this file, treat it as unknown until proven.

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
| `bloxdFaceBlock(position, normal)` | the block id of the face you are on — for surface-hook per-block work **[shipped]** |
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
