# Partie III — Recettes (FR)

Snippets originaux ; constantes citées créditées. Conformes aux règles de la Partie II.

## R1 — Détection de bloc (la fondation)

```wgsl
fn isLeaf(id: u32) -> bool {
    switch id {
        case 100u, 101u, 102u, 103u, 491u, 492u, 493u, 653u, 911u, 1226u: { return true; }
        default: { return false; }
    }
}
```

Groupes d'ids en Partie VIII. Hook light → `light.blockId` ; hook surface →
`surface.blockId` — `bloxdFaceBlock(surface.position, surface.normal)` donne les coordonnées
du bloc, l'entrée que veulent les hashs par bloc.

## R2 — Ombre de canopée (l'astuce des « soft tree shadows »)

Sous un arbre, exactement un niveau de skyLight est perdu — mais skyLight est tone-mappé :
ce niveau ≈ 0.995, pas 0.93. On le compte :

```wgsl
const CANOPY_SPREAD = 0.0035;
var covered = clamp((1.0 - light.skyLight) / CANOPY_SPREAD, 0.0, 1.0)
            * smoothstep(0.35, 0.6, light.skyLight); // les grottes restent ouvertes
```

Crédit : pack publié Breeze (Crownix, d'après Ellie). À combiner avec la garde lampes (R4).

## R3 — Teinte directionnelle soleil par face

```wgsl
let sun = bloxdSunDirection();
let day = smoothstep(0.0, 0.12, sun.y);            // off la nuit & sans ciel soleil
let lit = smoothstep(-0.1, 0.35, dot(light.normal, sun));
let strength = day * smoothstep(0.4, 0.9, light.skyLight);
out.colour *= mix(vec3f(0.76, 0.8, 0.88), vec3f(1.1, 1.04, 0.94), lit) * strength;
```

## R4 — Garde lampes (la lumière doit percer ton shading)

```wgsl
let lamp = 1.0 - smoothstep(0.4, 0.9,
             max(light.blockLight.r, max(light.blockLight.g, light.blockLight.b)));
strength *= lamp;   // tout facteur d'assombrissement multiplie par ceci
```

## R5 — Lift de luminosité sans clipping (grade avant fog)

```wgsl
const BRIGHTEN = 1.45; const VIBRANCE = 0.22;
fn grade(c: vec3f) -> vec3f {
    let l = max(c, vec3f(0.0));
    let b = l * BRIGHTEN / (1.0 + l * (BRIGHTEN - 1.0)); // pente B au noir, blanc = blanc
    let grey = dot(b, vec3f(0.2126, 0.7152, 0.0722));
    let chroma = max(b.r, max(b.g, b.b)) - min(b.r, min(b.g, b.b));
    return clamp(mix(vec3f(grey), b, 1.0 + VIBRANCE * (1.0 - chroma)), vec3f(0.0), vec3f(1.0));
}
// usage : out.colour = bloxdApplyFog(grade(lit) + surface.emission, light);
```

Crédit : Breeze. Grade **avant** fog ; emission ajoutée avant fog.

## R6 — Profondeur d'eau réelle (Beer-Lambert, données moteur)

```wgsl
let behind = bloxdOpaqueBehind();
let depth = select(64.0, max(surface.position.y - behind.position.y, 0.0), behind.found);
let depthFade = 1.0 - exp(-depth * 0.32);   // ~1/3 à 1 bloc
```

Crédit : Breeze. `depth = 64` si rien d'opaque derrière (ciel ouvert = profond).

## R7 — Réflexion ciel respectueuse de la nuit

```wgsl
let grazing = 1.0 - clamp(dot(toEye, n), 0.0, 1.0);
let fresnel = 0.02 + 0.98 * grazing * grazing * grazing * grazing * grazing; // Schlick, eau
let skyExposure = smoothstep(0.45, 0.98, light.skyLight); // l'eau de grotte ne reflète pas
colour = mix(colour, light.skyLightColour * TEINTE, fresnel * 0.45 * skyExposure);
```

Jamais `normalize(toEye + bloxdSunDirection())` sans garde de longueur — somme exactement nulle
quand le soleil est opposé à la vue (NaN garanti).

## R8 — Hash stable monde sous floating origin

```wgsl
fn mixBits(v: u32) -> u32 {
    var h = v; h ^= h >> 16u; h *= 0x7feb352du; h ^= h >> 15u; h *= 0x846ca68bu; h ^= h >> 16u;
    return h;
}
let place = light.position + vec3f(bloxdOriginOffset() % vec3i(4096)); // OBLIGATOIRE
```

Crédit : Breeze. Sans le terme d'origine, tes motifs glissent quand le moteur rebasse le monde.

## R9 — Animation wrap-sûre (précision loin du spawn)

```wgsl
let value = 0.5 + 0.5 * sin(6.2831853 * fract(bloxdTime() / bloxdTimeWrap * cycles + phase));
```

`cycles` entier ⇒ sans couture au wrap. La seule façon sûre d'animer ancré monde.

## R10 — Fondu LOD pour que la distance ne coûte rien

```wgsl
let near = 1.0 - smoothstep(FAR * 0.6, FAR, distance(bloxdEyePosition(), position));
if (near > 0.0) { /* détail coûteux uniquement ici */ }
```

Packs publiés : grain 14 m, rides 24-40 m, taches 48 m. Toute boucle par fragment doit être gated.

## R13 — Bruit value-noise immortel (réseaux entiers tournés)

L'astuce des packs publiés pour un bruit qui ne perd jamais la précision et ne saute jamais au
rebase : un réseau dont les coins sont des **entiers qui wrappent**, approché par strides entiers :

```wgsl
const CELLULES = 8;  const PERIODE = 289;          // wrap des coins (sûr en float)
const STRIDE = 2000;  const DECAL = vec2i(117, 44); // 0,5 cellule réseau/bloc, tourné 20,6°
fn octave(cellule: vec2i) -> vec3f {
    let reste  = ((cellule % STRIDE) + STRIDE) % STRIDE;
    let compte = ((cellule - reste) / STRIDE) % PERIODE;   // base petite pour toujours
    let base   = compte.x * DECAL + compte.y * vec2i(-DECAL.y, DECAL.x);
    // hash des coins de base + point tourné ; blend quintique ; gradient analytique + valeur
}
```

Crédit : pack publié Breeze (deux octaves tournées ; octave fine fondue 24→40 m et sautée au-delà).
Combiné à R8/R9 : vagues/grain/brume qui survivent des heures loin du spawn.

## R14 — Peindre des surmontes : ajouter des « objets » sans rien ajouter

Les packs ne peuvent pas ajouter d'objets au monde — alors **peignez-les dans la couleur**.
Marchez quelques pas le long du rayon de vue dans un repère qui glisse vers le bas (les cellules
hashées tombent), testez un quad hashé par cellule, et si touché **retournez sa couleur à la
place de celle du terrain** :

```wgsl
for (var i = 0; i < PAS; i++) {
    let s = (f32(i) + 0.5) * pas;
    let glissant = oeil + origine + d * s + vec3f(0.0, t * CHUTE, 0.0); // repère tombant
    let h = hashCellule(vec3i(floor(glissant / CELLULE)) + SEL);
    if (hashUnit(h) > CHANCE) { continue; }
    // placer un quad hashé dans la cellule ; si le pixel est dessus : return couleur * niveau;
}
```

Gater (`isLeaf(blockId) ∥ sousCanopee`, portée ≤ 10 m) — le raymarch 6 pas non-borné est la
plainte FPS n°1 du workshop. Crédit : pack publié Breeze (feuilles tombantes), technique
généralisable à toute « particule ».

## R11 — Alpha liquide strict-sûr

```wgsl
var out = bloxdDefaultSurface(surface);
out.alpha = clamp(surface.alpha / ALPHA_ENREGISTRE * mix(OP_PEUP, OP_PROF, depthFade), 0.0, 1.0);
out.alpha = max(out.alpha, ecume * 0.95); // les surmontes poussent l'alpha vers le haut
```

## R12 — Variation par cellule sans répétition de texture

```wgsl
let cell = vec3i(floor(surface.position * CELLULES - surface.normal * 0.5))
         + bloxdOriginOffset() * CELLULES + vec3i(0, 104729, 0); // décalage anti-collision
```

Le demi-cellule par la normale évite le scintillement des faces latérales.
