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
`bloxdFaceBlock(surface.position, surface.normal)`.

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
