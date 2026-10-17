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
