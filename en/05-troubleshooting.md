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
