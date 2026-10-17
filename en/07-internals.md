# Part VII — Engine internals

Every item carries its provenance: **[measured]** our instruments · **[shipped]** proven by a
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
