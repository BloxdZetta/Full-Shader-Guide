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
